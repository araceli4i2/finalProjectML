"""
Cargador de Datos y Métricas para el Dashboard de Aprendizaje Supervisado.
EAIMCS (INE Bolivia) - Consume el dataset preprocesado sin duplicar lógica.
"""

import sys
import logging
from pathlib import Path
from typing import Dict, Any, List
import numpy as np
import pandas as pd

# Asegurar importación de preprocessing
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from preprocessing.preprocessing import (
    run_preprocessing,
    map_caeb_to_sector,
    PREDICTOR_NUM_COLS
)

logger = logging.getLogger("dashboard.data_loader")

class DashboardDataLoader:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(DashboardDataLoader, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self):
        if self.initialized:
            return

        self.project_root = PROJECT_ROOT
        self.processed_path = self.project_root / "data" / "processed" / "dataset_procesado.csv"
        self.df = None
        self.kpis: Dict[str, Any] = {}
        self._load_and_prepare()
        self.initialized = True

    def _load_and_prepare(self):
        if not self.processed_path.exists():
            logger.info("Dataset procesado no encontrado. Ejecutando run_preprocessing()...")
            self.df = run_preprocessing(save_outputs=True)
        else:
            logger.info("Cargando dataset procesado desde: %s", self.processed_path)
            self.df = pd.read_csv(self.processed_path, low_memory=False)

        tot_emp = len(self.df)
        med_ing = float(self.df["target"].median())
        mean_ing = float(self.df["target"].mean())
        tot_ing = float(self.df["target"].sum())
        n_deptos = int(self.df["depto"].nunique())
        n_sectores = int(self.df["sector_macro"].nunique())
        top_depto = str(self.df["depto"].value_counts().index[0])
        top_sector = str(self.df["sector_macro"].value_counts().index[0])

        self.kpis = {
            "total_empresas": tot_emp,
            "ingreso_mediano": med_ing,
            "ingreso_promedio": mean_ing,
            "ingreso_total_agregado": tot_ing,
            "num_departamentos": n_deptos,
            "num_macrosectores": n_sectores,
            "top_departamento": top_depto,
            "top_sector": top_sector,
            "fuente": "INE Bolivia - EAIMCS 2017-2018",
            "cobertura": "Nacional (9 departamentos, medianas y grandes empresas)"
        }
        logger.info("Data loader inicializado: %d empresas cargadas.", tot_emp)

    def get_kpis(self) -> Dict[str, Any]:
        return self.kpis

    def get_data(self) -> pd.DataFrame:
        return self.df

    def get_dictionary(self) -> List[Dict[str, str]]:
        """Retorna el catálogo oficial de variables según docs/02_diccionario_datos_EAIMCS.md."""
        entries = [
            {"name": "ID", "section": "Carátula", "desc": "Identificador único de la empresa (llave de unión)", "type": "Numérico / ID", "sample": "10824, 16646"},
            {"name": "C2_01", "section": "Carátula", "desc": "Departamento de ubicación de la empresa (9 departamentos)", "type": "Texto / Categórica", "sample": "SANTA CRUZ, LA PAZ, COCHABAMBA"},
            {"name": "actividad_pricipal_codigo_V1", "section": "Carátula", "desc": "Código CAEB de la Actividad Principal de la empresa", "type": "Código / Categórica", "sample": "41000, 47301, 10104"},
            {"name": "S00_01_A", "section": "Sección 0", "desc": "TOTAL Ingresos Operativos en Bs (VARIABLE OBJETIVO DEL MODELO)", "type": "Monetaria (Bs)", "sample": "Mediana: 15.83M Bs, Min: 1.28M Bs"},
            {"name": "S05_04", "section": "Sección 5", "desc": "TOTAL Ingresos Sección 5 (equivalente exacto a S00_01_A)", "type": "Monetaria (Bs)", "sample": "Mediana: 15.83M Bs"},
            {"name": "S05_01", "section": "Sección 5", "desc": "Ingresos por venta de productos fabricados en Bs (Excluida por fuga)", "type": "Monetaria (Bs)", "sample": "0 a 5.19B Bs"},
            {"name": "S05_02", "section": "Sección 5", "desc": "Ingresos por venta de mercaderías en Bs (Excluida por fuga)", "type": "Monetaria (Bs)", "sample": "0 a 2.05B Bs"},
            {"name": "S05_03", "section": "Sección 5", "desc": "Ingresos por servicios prestados en Bs (Excluida por fuga)", "type": "Monetaria (Bs)", "sample": "0 a 4.68B Bs"},
            {"name": "S01_05_A", "section": "Sección 1", "desc": "TOTAL Personal Ocupado (hombres y mujeres, permanentes y eventuales)", "type": "Conteo / Personas", "sample": "Mediana: 27, Media: 91.5"},
            {"name": "S01_03_C", "section": "Sección 1", "desc": "Sueldos y salarios básicos anuales del personal remunerado en Bs", "type": "Monetaria (Bs)", "sample": "Mediana: 1.20M Bs"},
            {"name": "S01_14", "section": "Sección 1", "desc": "TOTAL Otras Remuneraciones (aguinaldos, aportes a salud y AFPs, bonos)", "type": "Monetaria (Bs)", "sample": "Mediana: 596,106 Bs"},
            {"name": "S02_09", "section": "Sección 2", "desc": "TOTAL Energía eléctrica, agua y combustibles consumidos en Bs", "type": "Monetaria (Bs)", "sample": "Mediana: 131,748 Bs"},
            {"name": "S07_09_E", "section": "Sección 7", "desc": "TOTAL Valor Histórico Final de Activos Fijos (maquinaria, edificios, transporte)", "type": "Monetaria (Bs)", "sample": "Mediana: 5.72M Bs"},
            {"name": "S06_06_B", "section": "Sección 6", "desc": "TOTAL Inventarios Finales (materias primas, productos en proceso y terminados)", "type": "Monetaria (Bs)", "sample": "Mediana: 977,600 Bs"},
            {"name": "S12_01_B", "section": "Sección 12", "desc": "Capacidad máxima de almacenamiento de materia prima", "type": "Cantidad / Capacidad", "sample": "0 a 637M unidades"},
            {"name": "S12_02_B", "section": "Sección 12", "desc": "Capacidad máxima de almacenamiento de producto terminado", "type": "Cantidad / Capacidad", "sample": "0 a 122M unidades"},
            {"name": "n_insumos", "section": "Sección 10", "desc": "Número de materias primas/materiales declarados por empresa (agregado)", "type": "Conteo", "sample": "0 a 67 insumos"},
            {"name": "total_valor_co", "section": "Sección 10", "desc": "Valor total de compras de materias primas e insumos en Bs (agregado)", "type": "Monetaria (Bs)", "sample": "Mediana fabril: 3.22M Bs"},
            {"name": "total_valor_uti", "section": "Sección 10", "desc": "Valor total de utilización de insumos en el proceso productivo en Bs", "type": "Monetaria (Bs)", "sample": "Mediana fabril: 3.20M Bs"}
        ]
        return entries

    def get_distribution_data(self) -> Dict[str, Any]:
        """Prepara datos completos para el histograma interactivo de ingresos operativos."""
        y_raw = self.df["target"].values
        y_log = self.df["target_log"].values
        return {
            "raw_values": [float(v) for v in y_raw],
            "log_values": [float(v) for v in y_log],
            "median_bs": float(np.median(y_raw)),
            "mean_bs": float(np.mean(y_raw)),
            "total_count": len(y_raw),
            "skew_note": "Distribución fuertemente asimétrica a la derecha (Pareto/Log-normal típica de ingresos)."
        }

    def get_boxplot_depto_data(self) -> List[Dict[str, Any]]:
        """Datos de ingresos agrupados por los 9 departamentos sin truncamiento muestral."""
        result = []
        for depto, group in self.df.groupby("depto"):
            vals = group["target"].values
            vals_log = group["target_log"].values
            result.append({
                "depto": depto,
                "count": len(vals),
                "median_bs": float(np.median(vals)),
                "q25_bs": float(np.percentile(vals, 25)),
                "q75_bs": float(np.percentile(vals, 75)),
                "sample_bs": [float(v) for v in vals],
                "sample_log": [float(v) for v in vals_log]
            })
        result = sorted(result, key=lambda x: x["count"], reverse=True)
        return result

    def get_boxplot_sector_data(self) -> List[Dict[str, Any]]:
        """Datos de ingresos agrupados por todos los macrosectores económicos."""
        result = []
        for sector, group in self.df.groupby("sector_macro"):
            if len(group) < 5:
                continue
            vals = group["target"].values
            vals_log = group["target_log"].values
            result.append({
                "sector": sector,
                "count": len(vals),
                "median_bs": float(np.median(vals)),
                "q25_bs": float(np.percentile(vals, 25)),
                "q75_bs": float(np.percentile(vals, 75)),
                "sample_bs": [float(v) for v in vals],
                "sample_log": [float(v) for v in vals_log]
            })
        result = sorted(result, key=lambda x: x["median_bs"], reverse=True)
        return result

    def get_correlation_data(self) -> Dict[str, Any]:
        """Matriz de correlación lineal entre predictores e ingresos en escala logarítmica."""
        vars_dict = {
            "Ingresos (S00_01_A)": "target",
            "Personal (S01_05_A)": "S01_05_A",
            "Sueldos Básicos (S01_03_C)": "S01_03_C",
            "Otras Remun. (S01_14)": "S01_14",
            "Energía/Comb. (S02_09)": "S02_09",
            "Activos Fijos (S07_09_E)": "S07_09_E",
            "Inventarios (S06_06_B)": "S06_06_B",
            "Insumos Utiliz.": "total_valor_uti",
            "Capacidad Almac.": "S12_01_B"
        }
        labels = list(vars_dict.keys())
        cols = list(vars_dict.values())

        sub_df = pd.DataFrame()
        for l, c in zip(labels, cols):
            sub_df[l] = np.log1p(self.df[c])

        corr_matrix = sub_df.corr().round(3).values.tolist()
        return {
            "labels": labels,
            "matrix": corr_matrix,
            "method": "Pearson sobre escala logarítmica log(1 + x)"
        }

    def get_outliers_data(self) -> Dict[str, Any]:
        """Subconjunto de puntos con cálculo de discrepancias bivariadas y ratios operativos."""
        sample = self.df[["ID", "depto", "sector_macro", "S01_05_A", "S01_03_C", "S07_09_E", "target"]].copy()
        
        # Ratio Ingreso / Sueldo (evitando divisiones espurias por cero agregando constante proporcional)
        sample["ratio_ing_sueldo"] = (sample["target"] / (sample["S01_03_C"] + 1000.0)).clip(upper=200)

        # Detección bivariada de anomalías mediante residuo logarítmico respecto a la relación esperada
        log_y = np.log1p(sample["target"])
        log_w = np.log1p(sample["S01_03_C"])
        
        # Regresión ortogonal / tendencia base simple
        residuos = np.abs(log_y - (0.65 * log_w + 6.5))
        q75_res = np.percentile(residuos, 75)
        iqr_res = q75_res - np.percentile(residuos, 25)
        umbral_outlier = q75_res + 1.5 * iqr_res
        sample["is_outlier"] = residuos > umbral_outlier

        data_points = []
        for _, r in sample.sample(n=min(500, len(sample)), random_state=42).iterrows():
            data_points.append({
                "id": int(r["ID"]),
                "depto": str(r["depto"]),
                "sector": str(r["sector_macro"]),
                "personal": float(r["S01_05_A"]),
                "sueldos_bs": float(r["S01_03_C"]),
                "activos_bs": float(r["S07_09_E"]),
                "ingreso_bs": float(r["target"]),
                "ratio": round(float(r["ratio_ing_sueldo"]), 2),
                "is_outlier": bool(r["is_outlier"])
            })
        return {
            "points": data_points,
            "total_outliers_iqr": int(sample["is_outlier"].sum()),
            "outliers_pct": round(float(sample["is_outlier"].mean() * 100), 2)
        }
