"""
Script de Entrenamiento y Validación de Modelos de Regresión.
Proyecto: AprendizajeSupervisadoML (EAIMCS - INE Bolivia).

Evalúa Ridge, Random Forest e HistGradientBoosting con 5-Fold Cross Validation.
Exporta el modelo de producción a dashboard/artifacts/ sin duplicaciones.
"""

import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
import numpy as np
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split, KFold, cross_val_score
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor
from sklearn.metrics import r2_score, mean_absolute_error, root_mean_squared_error, median_absolute_error
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

# Asegurar importación de preprocessing
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from preprocessing.preprocessing import (
    run_preprocessing,
    PREDICTOR_NUM_COLS,
    PREDICTOR_CAT_COLS,
    RANDOM_STATE_SEED
)

# Configuración de Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("models.train")


def train_and_evaluate(
    df: pd.DataFrame,
    artifacts_dir: Path,
    models_dir: Path
) -> Dict[str, Any]:
    """
    Entrena y compara los modelos de regresión, selecciona el mejor ensamble,
    calcula diagnósticos e importancia de variables, y guarda artefactos en dashboard/artifacts/.
    """
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    models_dir.mkdir(parents=True, exist_ok=True)

    log_num_cols: List[str] = [f"log_{c}" for c in PREDICTOR_NUM_COLS]
    cat_cols: List[str] = PREDICTOR_CAT_COLS

    X = df[log_num_cols + cat_cols].copy()
    y_raw = df["target"].values
    y_log = np.log1p(y_raw)

    X_train, X_test, y_train_log, y_test_log, y_train_raw, y_test_raw = train_test_split(
        X, y_log, y_raw, test_size=0.2, random_state=RANDOM_STATE_SEED
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), log_num_cols),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat_cols)
        ]
    )

    models = {
        "Ridge": Ridge(alpha=10.0),
        "RandomForest": RandomForestRegressor(
            n_estimators=120, max_depth=16, min_samples_split=4,
            random_state=RANDOM_STATE_SEED, n_jobs=1
        ),
        "HistGradientBoosting": HistGradientBoostingRegressor(
            max_iter=150, max_depth=6, learning_rate=0.08,
            random_state=RANDOM_STATE_SEED
        )
    }

    results: Dict[str, Any] = {}
    fitted_pipelines: Dict[str, Pipeline] = {}
    cv = KFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE_SEED)

    logger.info("Iniciando validación cruzada (5 Folds) y ajuste de modelos...")
    for name, model in models.items():
        pipe = Pipeline([
            ("prep", preprocessor),
            ("reg", model)
        ])

        # CV en escala logarítmica
        cv_scores = cross_val_score(pipe, X_train, y_train_log, cv=cv, scoring="r2", n_jobs=1)

        # Ajuste en train completo
        pipe.fit(X_train, y_train_log)
        fitted_pipelines[name] = pipe

        # Evaluación en Test
        y_pred_log = pipe.predict(X_test)
        y_pred_raw = np.expm1(y_pred_log)

        # Métricas log y naturales (Bs)
        r2_log = float(r2_score(y_test_log, y_pred_log))
        mae_log = float(mean_absolute_error(y_test_log, y_pred_log))
        rmse_log = float(root_mean_squared_error(y_test_log, y_pred_log))

        r2_bs = float(r2_score(y_test_raw, y_pred_raw))
        mae_bs = float(mean_absolute_error(y_test_raw, y_pred_raw))
        rmse_bs = float(root_mean_squared_error(y_test_raw, y_pred_raw))
        medae_bs = float(median_absolute_error(y_test_raw, y_pred_raw))
        medape = float(np.median(np.abs(y_test_raw - y_pred_raw) / y_test_raw) * 100)

        results[name] = {
            "cv_r2_mean": float(np.mean(cv_scores)),
            "cv_r2_std": float(np.std(cv_scores)),
            "r2_log": r2_log,
            "mae_log": mae_log,
            "rmse_log": rmse_log,
            "r2_bs": r2_bs,
            "mae_bs": mae_bs,
            "rmse_bs": rmse_bs,
            "medae_bs": medae_bs,
            "medape_percent": medape
        }

        logger.info(
            "[%s] CV R2: %.4f | Test R2 (Log): %.4f | Test R2 (Bs): %.4f | MedAPE: %.2f%%",
            name, results[name]["cv_r2_mean"], r2_log, r2_bs, medape
        )

    # Selección del mejor modelo para producción (mayor R² en Bs)
    best_name = "RandomForest" if results["RandomForest"]["r2_bs"] >= results["HistGradientBoosting"]["r2_bs"] else "HistGradientBoosting"
    best_pipe = fitted_pipelines[best_name]
    logger.info("Modelo seleccionado para producción: %s", best_name)

    # Importancia de variables
    feature_importance_list = []
    if best_name == "RandomForest":
        rf_reg = best_pipe.named_steps["reg"]
        encoder = best_pipe.named_steps["prep"].named_transformers_["cat"]
        cat_features = list(encoder.get_feature_names_out(cat_cols))
        all_features = log_num_cols + cat_features
        importances = rf_reg.feature_importances_

        fi_df = pd.DataFrame({"feature": all_features, "importance": importances})
        fi_df = fi_df.sort_values(by="importance", ascending=False)
        feature_importance_list = fi_df.head(15).to_dict(orient="records")

    # Guardar modelo de producción en dashboard/artifacts/
    model_artifact_path = artifacts_dir / "best_model.joblib"
    joblib.dump(best_pipe, model_artifact_path)
    logger.info("Artefacto serializado guardado en: %s", model_artifact_path)

    # Guardar predicciones diagnósticas tabulares en formato CSV
    y_test_pred_best = np.expm1(best_pipe.predict(X_test))
    test_diagnostics_df = pd.DataFrame({
        "real_bs": [float(v) for v in y_test_raw[:300]],
        "pred_bs": [float(v) for v in y_test_pred_best[:300]],
        "real_log": [float(v) for v in y_test_log[:300]],
        "pred_log": [float(v) for v in best_pipe.predict(X_test)[:300]],
        "residuals_log": [float(r) for r in (y_test_log[:300] - best_pipe.predict(X_test)[:300])]
    })
    test_diag_csv = artifacts_dir / "test_predictions.csv"
    test_diagnostics_df.to_csv(test_diag_csv, index=False)
    logger.info("Predicciones de prueba guardadas en formato tabular CSV: %s", test_diag_csv)

    # Guardar estadísticas de referencia para Drift en models/reference_stats.json
    reference_stats = {}
    for c in PREDICTOR_NUM_COLS:
        vals = df[c].values
        reference_stats[c] = {
            "mean": float(np.mean(vals)),
            "std": float(np.std(vals)),
            "median": float(np.median(vals)),
            "q25": float(np.percentile(vals, 25)),
            "q75": float(np.percentile(vals, 75)),
            "min": float(np.min(vals)),
            "max": float(np.max(vals))
        }
    with open(models_dir / "reference_stats.json", "w", encoding="utf-8") as f:
        json.dump(reference_stats, f, indent=2, ensure_ascii=False)

    # Registro MLOps en dashboard/artifacts/registry.json
    version_id = f"v1.{datetime.now().strftime('%Y%m%d.%H%M')}"
    registry_file = artifacts_dir / "registry.json"
    history = []
    if registry_file.exists():
        try:
            with open(registry_file, "r", encoding="utf-8") as f:
                history = json.load(f).get("versions", [])
        except Exception:
            history = []

    for h in history:
        h["status"] = "ARCHIVED"

    version_entry = {
        "version": version_id,
        "model_type": best_name,
        "timestamp": datetime.now().isoformat(),
        "dataset_rows": len(df),
        "metrics": results[best_name],
        "all_models_metrics": results,
        "status": "ACTIVE",
        "framework": "scikit-learn",
        "python_version": sys.version.split()[0]
    }
    history.insert(0, version_entry)

    registry_data = {
        "active_version": version_id,
        "last_updated": datetime.now().isoformat(),
        "versions": history
    }
    with open(registry_file, "w", encoding="utf-8") as f:
        json.dump(registry_data, f, indent=2, ensure_ascii=False)

    with open(artifacts_dir / "feature_importance.json", "w", encoding="utf-8") as f:
        json.dump(feature_importance_list, f, indent=2, ensure_ascii=False)

    logger.info("Metadatos y registros MLOps guardados exitosamente.")
    return version_entry


def run_training() -> Dict[str, Any]:
    """Carga o ejecuta el preprocesamiento y entrena el modelo."""
    processed_csv = PROJECT_ROOT / "data" / "processed" / "dataset_procesado.csv"
    if processed_csv.exists():
        logger.info("Cargando dataset preprocesado desde: %s", processed_csv)
        df = pd.read_csv(processed_csv, low_memory=False)
    else:
        logger.info("Dataset procesado no encontrado, ejecutando pipeline de preprocesamiento...")
        df = run_preprocessing(save_outputs=True)

    artifacts_dir = PROJECT_ROOT / "dashboard" / "artifacts"
    models_dir = PROJECT_ROOT / "models"
    return train_and_evaluate(df, artifacts_dir, models_dir)


if __name__ == "__main__":
    res = run_training()
    print("\n--- RESUMEN FINAL DE ENTRENAMIENTO (models/train.py) ---")
    print(f"Versión: {res['version']} ({res['model_type']})")
    print(f"R² en escala Bs:  {res['metrics']['r2_bs']:.4f}")
    print(f"R² en escala Log: {res['metrics']['r2_log']:.4f}")
    print(f"MedAPE:           {res['metrics']['medape_percent']:.2f}%")
