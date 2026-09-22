"""
Módulo de Detección de Data Drift (Deriva de Datos) para MLOps.
Calcula la prueba de dos muestras de Kolmogorov-Smirnov y distancia de Wasserstein
comparando una muestra de inferencia con la distribución empírica base de entrenamiento.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
import numpy as np
import pandas as pd
from scipy.stats import ks_2samp, wasserstein_distance

logger = logging.getLogger("models.drift")


class DriftDetector:
    """Detector de deriva estadística para monitoreo en producción."""

    def __init__(self, reference_stats_path: Optional[Path] = None) -> None:
        if reference_stats_path is None:
            self.stats_path = Path(__file__).resolve().parent / "reference_stats.json"
        else:
            self.stats_path = Path(reference_stats_path)

        self.reference_stats: Dict[str, Any] = {}
        if self.stats_path.exists():
            try:
                with open(self.stats_path, "r", encoding="utf-8") as f:
                    self.reference_stats = json.load(f)
            except Exception as e:
                logger.warning("No se pudo cargar reference_stats.json: %s", e)
                self.reference_stats = {}

    def _sample_from_reference_distribution(self, ref: Dict[str, Any], n_samples: int = 400) -> np.ndarray:
        """
        Genera una muestra no paramétrica a partir de los percentiles empíricos
        y la proporción de ceros almacenada en las estadísticas de referencia.
        """
        zero_fraction = ref.get("zero_fraction", 0.0)
        p_points = [0.01, 0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99]
        val_points = [
            ref.get("p01", ref.get("min", 0.0)),
            ref.get("p05", ref.get("min", 0.0)),
            ref.get("p10", ref.get("q25", 0.0)),
            ref.get("q25", ref.get("median", 0.0)),
            ref.get("median", ref.get("mean", 1.0)),
            ref.get("q75", ref.get("mean", 2.0)),
            ref.get("p90", ref.get("max", 5.0)),
            ref.get("p95", ref.get("max", 10.0)),
            ref.get("p99", ref.get("max", 20.0))
        ]

        # Asegurar monotonía estricta para interpolación
        val_points = np.maximum.accumulate(np.array(val_points, dtype=float))

        u = np.random.uniform(0.01, 0.99, size=n_samples)
        positive_samples = np.interp(u, p_points, val_points)

        if zero_fraction > 0.02:
            is_zero = np.random.uniform(0, 1, size=n_samples) < zero_fraction
            positive_samples[is_zero] = 0.0

        return np.maximum(0.0, positive_samples)

    def simulate_or_test_drift(
        self,
        sample_df: Any = None,
        simulate_drift_feature: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Ejecuta el test de Kolmogorov-Smirnov y distancia de Wasserstein sobre variables productivas clave.
        Aplica corrección por multiplicidad de pruebas (Bonferroni) sobre las 5 dimensiones.
        """
        results: Dict[str, Any] = {}
        features_to_monitor = [
            ("S01_05_A", "Personal Ocupado"),
            ("S01_03_C", "Sueldos y Salarios"),
            ("S02_09", "Energía y Combustibles"),
            ("S07_09_E", "Activos Fijos"),
            ("total_valor_uti", "Insumos Utilizados")
        ]

        # Nivel de significancia ajustado por Bonferroni (5 variables evaluadas simultáneamente)
        alpha_base = 0.05
        alpha_bonferroni = alpha_base / len(features_to_monitor)

        np.random.seed(42)

        for feat_key, feat_label in features_to_monitor:
            ref = self.reference_stats.get(feat_key, None)
            if not ref:
                results[feat_key] = {
                    "label": feat_label,
                    "status": "SIN DATOS",
                    "ks_stat": 0.0,
                    "p_value": 1.0,
                    "drift_detected": False
                }
                continue

            # Muestra base no paramétrica representativa del entrenamiento
            base_sample = self._sample_from_reference_distribution(ref, n_samples=450)

            # Muestra de producción real o simulada
            if sample_df is not None and isinstance(sample_df, pd.DataFrame) and feat_key in sample_df.columns:
                prod_sample = sample_df[feat_key].dropna().values.astype(float)
            elif simulate_drift_feature == feat_key:
                # Simular desplazamiento severo (+80% en nivel de insumos/costos)
                prod_sample = base_sample * np.random.uniform(1.6, 2.1, size=len(base_sample))
            else:
                # Variación aleatoria natural sin deriva (< 3%)
                prod_sample = base_sample * np.random.uniform(0.98, 1.02, size=len(base_sample))

            ks_res = ks_2samp(base_sample, prod_sample)
            w_dist = float(wasserstein_distance(base_sample, prod_sample))

            p_val = float(ks_res.pvalue)
            ks_stat = float(ks_res.statistic)
            drift_detected = p_val < alpha_bonferroni

            results[feat_key] = {
                "label": feat_label,
                "ks_stat": round(ks_stat, 4),
                "p_value": round(p_val, 4),
                "wasserstein_dist": round(w_dist, 2),
                "alpha_threshold": alpha_bonferroni,
                "drift_detected": drift_detected,
                "status": "DRIFT DETECTADO" if drift_detected else "ESTABLE",
                "severity": "CRÍTICO" if p_val < 0.001 else ("MODERADO" if drift_detected else "NORMAL")
            }

        return results


if __name__ == "__main__":
    detector = DriftDetector()
    print("Test de Drift con detector:")
    res = detector.simulate_or_test_drift(simulate_drift_feature="S02_09")
    print(json.dumps(res, indent=2, ensure_ascii=False))

