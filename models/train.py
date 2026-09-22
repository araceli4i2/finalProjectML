"""
Script de Entrenamiento y Validación de Modelos de Regresión.
Proyecto: AprendizajeSupervisadoML (EAIMCS - INE Bolivia).

Evalúa Ridge, Random Forest y Boosting regularizado (LightGBM / XGBoost) con 5-Fold Cross Validation.
Optimiza la función de pérdida robusta (Huber / MAE) para reducir el MedAPE y mitigar el impacto de atípicos financieros.
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

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor
from sklearn.metrics import r2_score, mean_absolute_error, root_mean_squared_error, median_absolute_error
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

import lightgbm as lgb

try:
    import xgboost as xgb
except ImportError:
    xgb = None

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

    # Estratificación en split inicial basada en cuantiles del target
    y_quantiles = pd.qcut(y_log, q=5, labels=False, duplicates="drop")
    X_train, X_test, y_train_log, y_test_log, y_train_raw, y_test_raw = train_test_split(
        X, y_log, y_raw, test_size=0.2, random_state=RANDOM_STATE_SEED, stratify=y_quantiles
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
        # LightGBM configurado con función de pérdida robusta (Huber), tasa baja y regularización L1/L2
        "LightGBM": lgb.LGBMRegressor(
            objective="huber",          # Pérdida de Huber: cuadrática en errores pequeños, lineal en atípicos
            learning_rate=0.03,         # Tasa de aprendizaje baja (0.01 - 0.05) para convergencia estable
            n_estimators=600,           # Estimadores suficientes para compensar la tasa baja sin sobreajustar
            num_leaves=31,              # Complejidad de árbol equilibrada
            max_depth=6,                # Profundidad máxima controlada para acotar varianza
            reg_alpha=1.0,              # Regularización L1 (Lasso) para inducir esparcidad y mitigar sobreajuste
            reg_lambda=5.0,             # Regularización L2 (Ridge) sobre las ponderaciones de hojas
            subsample=0.8,              # Submuestreo estocástico de filas (bagging fraction)
            colsample_bytree=0.8,       # Submuestreo estocástico de columnas por árbol
            importance_type="gain",     # Importancia basada en ganancia de reducción de pérdida
            random_state=RANDOM_STATE_SEED,
            verbose=-1,
            n_jobs=1
        )
        # Nota: Si se prefiere XGBoost como alternativa directa de Boosting:
        # "XGBoost": xgb.XGBRegressor(
        #     objective="reg:pseudohubererror", # o "reg:absoluteerror" para optimización pura de MAE
        #     learning_rate=0.03,
        #     n_estimators=700,
        #     max_depth=6,
        #     reg_alpha=1.5,
        #     reg_lambda=5.0,
        #     subsample=0.8,
        #     colsample_bytree=0.8,
        #     random_state=RANDOM_STATE_SEED,
        #     n_jobs=1
        # )
    }

    results: Dict[str, Any] = {}
    fitted_pipelines: Dict[str, Pipeline] = {}
    smearing_factors: Dict[str, float] = {}

    # Validación cruzada estratificada por cuantiles
    train_quantiles = pd.qcut(y_train_log, q=5, labels=False, duplicates="drop")
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE_SEED)

    logger.info("Iniciando validación cruzada estratificada (5 Folds) y ajuste de modelos...")
    for name, model in models.items():
        pipe = Pipeline([
            ("prep", preprocessor),
            ("reg", model)
        ])

        # CV en escala logarítmica con pliegues estratificados
        cv_scores = cross_val_score(
            pipe, X_train, y_train_log, 
            cv=cv.split(X_train, train_quantiles), 
            scoring="r2", n_jobs=1
        )

        # Ajuste en train completo
        pipe.fit(X_train, y_train_log)
        fitted_pipelines[name] = pipe

        # Cálculo del Factor de Retransformación de Duan (Smearing Factor)
        train_pred_log = pipe.predict(X_train)
        residuals_train = y_train_log - train_pred_log
        smearing_factor = float(np.mean(np.exp(residuals_train)))
        smearing_factors[name] = smearing_factor

        # Evaluación en Test aplicando corrección de Duan
        y_pred_log = pipe.predict(X_test)
        y_pred_raw = np.maximum(0.0, np.exp(y_pred_log) * smearing_factor - 1.0)

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
            "medape_percent": medape,
            "smearing_factor": smearing_factor
        }

        logger.info(
            "[%s] CV R2: %.4f | Test R2 (Log): %.4f | Test R2 (Bs): %.4f | MedAPE: %.2f%% | Duan Smearing: %.4f",
            name, results[name]["cv_r2_mean"], r2_log, r2_bs, medape, smearing_factor
        )

    # Selección dinámica del mejor modelo para producción (mayor R² log y menor MedAPE entre ensambles)
    ensemble_candidates = [m for m in models.keys() if m != "Ridge"]
    best_name = max(
        ensemble_candidates,
        key=lambda m: (results[m]["r2_log"], -results[m]["medape_percent"])
    )
    best_pipe = fitted_pipelines[best_name]
    logger.info("Modelo seleccionado para producción: %s (Smearing Factor: %.4f)", best_name, smearing_factors[best_name])

    # Importancia de variables dinámica para cualquier modelo con feature_importances_ o coef_
    feature_importance_list = []
    reg_step = best_pipe.named_steps["reg"]
    encoder = best_pipe.named_steps["prep"].named_transformers_["cat"]
    cat_features = list(encoder.get_feature_names_out(cat_cols))
    all_features = log_num_cols + cat_features

    if hasattr(reg_step, "feature_importances_"):
        importances = reg_step.feature_importances_
        fi_df = pd.DataFrame({"feature": all_features, "importance": importances})
        fi_df = fi_df.sort_values(by="importance", ascending=False)
        feature_importance_list = fi_df.head(15).to_dict(orient="records")
    elif hasattr(reg_step, "coef_"):
        importances = np.abs(reg_step.coef_)
        fi_df = pd.DataFrame({"feature": all_features, "importance": importances})
        fi_df = fi_df.sort_values(by="importance", ascending=False)
        feature_importance_list = fi_df.head(15).to_dict(orient="records")

    # Guardar modelo de producción en dashboard/artifacts/
    model_artifact_path = artifacts_dir / "best_model.joblib"
    joblib.dump(best_pipe, model_artifact_path)
    logger.info("Artefacto serializado guardado en: %s", model_artifact_path)

    # Guardar predicciones diagnósticas tabulares en formato CSV (100% DE OBSERVACIONES DE TEST)
    y_test_pred_log_best = best_pipe.predict(X_test)
    y_test_pred_best = np.maximum(0.0, np.exp(y_test_pred_log_best) * smearing_factors[best_name] - 1.0)
    test_diagnostics_df = pd.DataFrame({
        "real_bs": [float(v) for v in y_test_raw],
        "pred_bs": [float(v) for v in y_test_pred_best],
        "real_log": [float(v) for v in y_test_log],
        "pred_log": [float(v) for v in y_test_pred_log_best],
        "residuals_log": [float(r) for r in (y_test_log - y_test_pred_log_best)]
    })
    test_diag_csv = artifacts_dir / "test_predictions.csv"
    test_diagnostics_df.to_csv(test_diag_csv, index=False)
    logger.info("Predicciones de prueba completas (%d filas) guardadas en CSV: %s", len(test_diagnostics_df), test_diag_csv)

    # Guardar estadísticas de referencia no paramétricas para Drift en models/reference_stats.json
    reference_stats = {}
    for c in PREDICTOR_NUM_COLS:
        vals = df[c].values
        reference_stats[c] = {
            "mean": float(np.mean(vals)),
            "std": float(np.std(vals)),
            "median": float(np.median(vals)),
            "q25": float(np.percentile(vals, 25)),
            "q75": float(np.percentile(vals, 75)),
            "p01": float(np.percentile(vals, 1)),
            "p05": float(np.percentile(vals, 5)),
            "p10": float(np.percentile(vals, 10)),
            "p90": float(np.percentile(vals, 90)),
            "p95": float(np.percentile(vals, 95)),
            "p99": float(np.percentile(vals, 99)),
            "min": float(np.min(vals)),
            "max": float(np.max(vals)),
            "zero_fraction": float(np.mean(vals == 0))
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

    framework = (
        "lightgbm" if "LightGBM" in best_name
        else "xgboost" if "XGB" in best_name
        else "scikit-learn"
    )

    version_entry = {
        "version": version_id,
        "model_type": best_name,
        "timestamp": datetime.now().isoformat(),
        "dataset_rows": len(df),
        "metrics": results[best_name],
        "all_models_metrics": results,
        "smearing_factor": smearing_factors[best_name],
        "status": "ACTIVE",
        "framework": framework,
        "python_version": sys.version.split()[0]
    }
    history.insert(0, version_entry)

    registry_data = {
        "active_version": version_id,
        "last_updated": datetime.now().isoformat(),
        "smearing_factor": smearing_factors[best_name],
        "rmse_log": results[best_name]["rmse_log"],
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
