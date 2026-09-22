"""
Servidor Web Flask para el Dashboard de Predicción de Ingresos Operativos.
Proyecto: AprendizajeSupervisadoML (EAIMCS - INE Bolivia).

Provee rutas web Jinja2 y una API REST completa para visualizaciones interactivas
con Plotly, exploración de datos, diagnóstico de modelos, inferencia predictiva y MLOps.
"""

import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import numpy as np
import pandas as pd
import joblib
from flask import Flask, render_template, jsonify, request

# Ajuste de ruta raíz del proyecto para importar módulos hermanos
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dashboard.data_loader import DashboardDataLoader
from models.drift import DriftDetector

# Inicialización de Flask
app = Flask(
    __name__,
    static_folder="static",
    template_folder="templates"
)

# Configuración de logs
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("dashboard.app")

# Inicializar cargador de datos (Singleton)
data_loader = DashboardDataLoader()

# Directorio de artefactos del dashboard
ARTIFACTS_DIR = Path(__file__).resolve().parent / "artifacts"

# Cargar artefactos de Machine Learning
MODEL = None
REGISTRY = None
FEATURE_IMPORTANCE = None
TEST_DIAGNOSTICS = None

def load_dashboard_artifacts() -> None:
    """Carga los artefactos serializados desde dashboard/artifacts/."""
    global MODEL, REGISTRY, FEATURE_IMPORTANCE, TEST_DIAGNOSTICS
    
    model_path = ARTIFACTS_DIR / "best_model.joblib"
    if model_path.exists():
        try:
            MODEL = joblib.load(model_path)
            logger.info("Modelo cargado exitosamente desde: %s", model_path)
        except Exception as e:
            logger.error("Error al cargar best_model.joblib: %s", e)

    registry_path = ARTIFACTS_DIR / "registry.json"
    if registry_path.exists():
        try:
            with open(registry_path, "r", encoding="utf-8") as f:
                REGISTRY = json.load(f)
        except Exception as e:
            logger.warning("No se pudo cargar registry.json: %s", e)

    fi_path = ARTIFACTS_DIR / "feature_importance.json"
    if fi_path.exists():
        try:
            with open(fi_path, "r", encoding="utf-8") as f:
                FEATURE_IMPORTANCE = json.load(f)
        except Exception as e:
            logger.warning("No se pudo cargar feature_importance.json: %s", e)

    test_pred_path = ARTIFACTS_DIR / "test_predictions.csv"
    if test_pred_path.exists():
        try:
            df_diag = pd.read_csv(test_pred_path)
            TEST_DIAGNOSTICS = df_diag.to_dict(orient="list")
            logger.info("Predicciones de prueba cargadas desde: %s", test_pred_path)
        except Exception as e:
            logger.warning("No se pudo cargar test_predictions.csv: %s", e)

load_dashboard_artifacts()
drift_detector = DriftDetector()


# -------------------------------------------------------------
# RUTAS DE INTERFAZ DE USUARIO (JINJA2)
# -------------------------------------------------------------
@app.route("/")
def index():
    """Ruta principal: renderiza el cascarón SPA del dashboard corporativo."""
    kpis = data_loader.get_kpis()
    active_version = REGISTRY.get("active_version", "v1.0.0") if REGISTRY else "v1.0.0-baseline"
    return render_template("index.html", kpis=kpis, active_version=active_version)


# -------------------------------------------------------------
# API: SECCIÓN 1 - RESUMEN EJECUTIVO & KPIS
# -------------------------------------------------------------
@app.route("/api/kpis")
def get_kpis():
    """Retorna los indicadores macroeconómicos y dimensiones generales del estudio."""
    return jsonify(data_loader.get_kpis())


# -------------------------------------------------------------
# API: SECCIÓN 2 - DICCIONARIO DE DATOS NAVEGABLE
# -------------------------------------------------------------
@app.route("/api/dictionary")
def get_dictionary():
    """Retorna la lista estructurada de variables documentadas en docs/02_diccionario_datos_EAIMCS.md."""
    query = request.args.get("q", "").lower().strip()
    section = request.args.get("section", "").strip()

    entries = data_loader.get_dictionary()
    if section:
        entries = [e for e in entries if e["section"].lower() == section.lower()]
    if query:
        entries = [
            e for e in entries
            if query in e["name"].lower() or query in e["desc"].lower() or query in e["section"].lower()
        ]
    return jsonify({
        "total": len(entries),
        "entries": entries
    })


# -------------------------------------------------------------
# API: SECCIÓN 3 - ANÁLISIS EXPLORATORIO (EDA) INTERACTIVO
# -------------------------------------------------------------
@app.route("/api/eda/distribution")
def get_eda_distribution():
    """
    VISUALIZACIÓN: Histograma de Distribución de Ingresos Operativos.
    POR QUÉ: Permite evidenciar la severa asimetría positiva (cola pesada tipo Pareto)
    en escala normal y demostrar cómo la transformación logarítmica (log1p)
    estabiliza la varianza y aproxima la normalidad requerida por los modelos.
    """
    return jsonify(data_loader.get_distribution_data())


@app.route("/api/eda/boxplot_deptos")
def get_eda_boxplot_deptos():
    """
    VISUALIZACIÓN: Diagramas de Caja (Boxplots) por Departamento.
    POR QUÉ: El boxplot es el gráfico estándar para comparar simultáneamente
    mediana, rango intercuartílico (IQR) y valores extremos/atípicos entre regiones.
    Muestra la gran concentración de ingresos en el eje central (Santa Cruz, La Paz, Cochabamba).
    """
    return jsonify(data_loader.get_boxplot_depto_data())


@app.route("/api/eda/boxplot_sectors")
def get_eda_boxplot_sectors():
    """
    VISUALIZACIÓN: Boxplots de Ingresos por Macrosector Económico CAEB.
    POR QUÉ: Permite contrastar la escala económica y dispersión entre actividades
    (Manufactura, Comercio, Construcción, Servicios), justificando el uso de la actividad
    como variable categórica en el preprocesamiento del modelo.
    """
    return jsonify(data_loader.get_boxplot_sector_data())


@app.route("/api/eda/correlations")
def get_eda_correlations():
    """
    VISUALIZACIÓN: Matriz de Correlación Heatmap.
    POR QUÉ: Un mapa de calor permite identificar rápidamente la fuerza y dirección
    de la asociación lineal entre las variables predictoras (Personal, Sueldos, Energía,
    Activos Fijos, Inventarios, Insumos) y los Ingresos Operativos, detectando también colinealidad.
    """
    return jsonify(data_loader.get_correlation_data())


@app.route("/api/eda/outliers")
def get_eda_outliers():
    """
    VISUALIZACIÓN: Gráfico de Dispersión (Scatter Plot) de Outliers y Ratios Operativos.
    POR QUÉ: Permite visualizar empresas atípicas con alta discrepancia entre
    ingreso declarado y personal/sueldos, además de corroborar la depuración de valores centinela 99999.
    """
    return jsonify(data_loader.get_outliers_data())


# -------------------------------------------------------------
# API: SECCIÓN 4 - RESUMEN DE PREPROCESAMIENTO Y PIPELINE
# -------------------------------------------------------------
@app.route("/api/pipeline")
def get_pipeline():
    """Retorna el detalle metodológico y cuantitativo del pipeline de limpieza y transformación."""
    return jsonify({
        "steps": [
            {
                "step": 1,
                "title": "Carga e Inspección de Tablas Inmutables (data/raw/)",
                "desc": "Lectura de MOD_ANUAL_S01-07_12_general_i (3,153 empresas) y MOD_ANUAL_S10_materiales_i (6,428 registros de insumos).",
                "status": "Completado"
            },
            {
                "step": 2,
                "title": "Tratamiento de Valores Centinela (99999) y Atípicos",
                "desc": "Sustitución de centinelas 99999 (imputación pendiente del INE) por NaN y corrección de valores anómalos negativos mediante acotamiento (clip(lower=0)).",
                "status": "Completado"
            },
            {
                "step": 3,
                "title": "Agregación de Sección 10 a Nivel Empresa",
                "desc": "Agrupación por ID empresarial: cálculo de n_insumos (conteo), total_valor_co (compras) y total_valor_uti (utilización).",
                "status": "Completado"
            },
            {
                "step": 4,
                "title": "Fusión Relacional (Left Join)",
                "desc": "Cruce por ID conservando las 3,153 empresas. Asignación coherente de valor 0 a empresas comerciales o de servicios sin insumos manufactureros.",
                "status": "Completado"
            },
            {
                "step": 5,
                "title": "Prevención de Fuga de Datos (Data Leakage)",
                "desc": "Exclusión deliberada de variables macroeconómicas derivadas calculadas por el INE (VBP, VA, CI, VIPP) y componentes de Sección 5 (S05_01 a S05_04).",
                "status": "Completado"
            },
            {
                "step": 6,
                "title": "Ingeniería de Características y Normalización",
                "desc": "Mapeo de 445 códigos CAEB a 14 macrosectores. Aplicación de transformación logarítmica log(1 + x) a montos monetarios y personal.",
                "status": "Completado"
            },
            {
                "step": 7,
                "title": "Estandarización y Codificación Categórica",
                "desc": "StandardScaler para variables numéricas logarítmicas y OneHotEncoder para departamentos y sectores dentro de un ColumnTransformer.",
                "status": "Completado"
            },
            {
                "step": 8,
                "title": "Partición Train / Test y Validación Cruzada",
                "desc": "División estratificada 80% entrenamiento (2,522 empresas) y 20% prueba (631 empresas) con 5-Fold Cross Validation.",
                "status": "Completado"
            }
        ]
    })


# -------------------------------------------------------------
# API: SECCIÓN 5 - MODELADO Y RESULTADOS
# -------------------------------------------------------------
@app.route("/api/models")
def get_models_results():
    """
    Retorna la comparativa de modelos (Ridge, RandomForest, HistGradientBoosting),
    gráficos de Real vs. Predicho, análisis de residuos e importancia de variables.
    """
    models_metrics = {}
    if REGISTRY and "versions" in REGISTRY and len(REGISTRY["versions"]) > 0:
        models_metrics = REGISTRY["versions"][0].get("all_models_metrics", {})

    return jsonify({
        "active_model": REGISTRY.get("versions", [{}])[0].get("model_type", "RandomForest") if REGISTRY else "RandomForest",
        "metrics_comparison": models_metrics,
        "feature_importance": FEATURE_IMPORTANCE or [],
        "test_diagnostics": TEST_DIAGNOSTICS or {}
    })


# -------------------------------------------------------------
# API: SECCIÓN 6 - PREDICCIÓN INTERACTIVA
# -------------------------------------------------------------
@app.route("/api/predict", methods=["POST"])
def predict_income():
    """
    Endpoint de Inferencia Predictiva:
    Recibe los datos operativos de una empresa, transforma las variables al espacio logarítmico,
    ejecuta el pipeline de Machine Learning y devuelve el ingreso proyectado en Bolivianos (Bs),
    intervalo de confianza y categoría de tamaño empresarial (Mediana vs. Gran empresa).
    """
    if MODEL is None:
        return jsonify({"error": "El modelo de Machine Learning no está cargado."}), 500

    try:
        data = request.get_json(force=True)

        depto = str(data.get("depto", "SANTA CRUZ")).strip().upper()
        sector_macro = str(data.get("sector_macro", "Industria Manufacturera")).strip()

        personal = float(data.get("personal", 25.0))
        sueldos = float(data.get("sueldos", 1200000.0))
        remuneraciones = float(data.get("remuneraciones", 600000.0))
        energia = float(data.get("energia", 150000.0))
        activos = float(data.get("activos", 5000000.0))
        inventarios = float(data.get("inventarios", 1000000.0))
        capacidad_mp = float(data.get("capacidad_mp", 0.0))
        capacidad_pt = float(data.get("capacidad_pt", 0.0))
        n_insumos = float(data.get("n_insumos", 2.0))
        total_valor_co = float(data.get("total_valor_co", 2500000.0))
        total_valor_uti = float(data.get("total_valor_uti", 2400000.0))

        input_dict = {
            "log_S01_05_A": [np.log1p(max(0, personal))],
            "log_S01_03_C": [np.log1p(max(0, sueldos))],
            "log_S01_14": [np.log1p(max(0, remuneraciones))],
            "log_S02_09": [np.log1p(max(0, energia))],
            "log_S07_09_E": [np.log1p(max(0, activos))],
            "log_S06_06_B": [np.log1p(max(0, inventarios))],
            "log_S12_01_B": [np.log1p(max(0, capacidad_mp))],
            "log_S12_02_B": [np.log1p(max(0, capacidad_pt))],
            "log_n_insumos": [np.log1p(max(0, n_insumos))],
            "log_total_valor_co": [np.log1p(max(0, total_valor_co))],
            "log_total_valor_uti": [np.log1p(max(0, total_valor_uti))],
            "depto": [depto],
            "sector_macro": [sector_macro]
        }

        input_df = pd.DataFrame(input_dict)
        pred_log = float(MODEL.predict(input_df)[0])
        pred_bs = float(np.expm1(pred_log))

        rmse_log = 0.529
        lower_log = pred_log - 1.645 * rmse_log
        upper_log = pred_log + 1.645 * rmse_log
        lower_bs = max(0.0, float(np.expm1(lower_log)))
        upper_bs = float(np.expm1(upper_log))

        is_produccion = "Industria" in sector_macro or "Construcción" in sector_macro or "Minería" in sector_macro
        umbral_gran = 35000000.0 if is_produccion else 28000000.0
        umbral_mediana = 2450000.0 if is_produccion else 1750000.0

        if pred_bs >= umbral_gran:
            categoria_tamano = "Gran Empresa"
            categoria_color = "emerald"
        elif pred_bs >= umbral_mediana:
            categoria_tamano = "Mediana Empresa"
            categoria_color = "indigo"
        else:
            categoria_tamano = "Por debajo del umbral (< Mediana)"
            categoria_color = "amber"

        return jsonify({
            "success": True,
            "prediction_bs": round(pred_bs, 2),
            "prediction_formatted": f"Bs {pred_bs:,.2f}",
            "lower_bound_bs": round(lower_bs, 2),
            "upper_bound_bs": round(upper_bs, 2),
            "interval_formatted": f"Bs {lower_bs:,.2f} – Bs {upper_bs:,.2f}",
            "categoria_tamano": categoria_tamano,
            "categoria_color": categoria_color,
            "log_prediction": round(pred_log, 4)
        })
    except Exception as e:
        logger.error("Error al procesar la predicción: %s", e)
        return jsonify({"error": str(e)}), 400


# -------------------------------------------------------------
# API: SECCIÓN 7 - MLOPS, REGISTRO DE VERSIONES & DATA DRIFT
# -------------------------------------------------------------
@app.route("/api/mlops")
def get_mlops_info():
    """Retorna el estado de gobernanza, trazabilidad y registro de versiones del modelo."""
    drift_status = drift_detector.simulate_or_test_drift()

    return jsonify({
        "active_version": REGISTRY.get("active_version", "v1.0.0") if REGISTRY else "v1.0.0",
        "last_updated": REGISTRY.get("last_updated", "2026-09-21T15:00:00") if REGISTRY else "",
        "history": REGISTRY.get("versions", []) if REGISTRY else [],
        "drift_metrics": drift_status,
        "pipeline_status": "OPERATIVO",
        "mlflow_integration": {
            "supported": True,
            "instruction": "Para habilitar MLflow local: pip install mlflow && mlflow server --host 127.0.0.1 --port 5000. models/train.py contiene los hooks preparados.",
            "tracking_uri": "http://127.0.0.1:5000 (Opcional local)"
        }
    })


@app.route("/api/mlops/drift", methods=["POST"])
def trigger_drift_simulation():
    """Permite simular o probar la detección de drift en una variable específica para auditoría."""
    data = request.get_json(silent=True) or {}
    feature = data.get("feature", None)
    results = drift_detector.simulate_or_test_drift(simulate_drift_feature=feature)
    return jsonify({
        "status": "success",
        "drift_results": results
    })


# -------------------------------------------------------------
# API: SECCIÓN 8 - MARCO LÓGICO Y ACERCA DEL PROYECTO
# -------------------------------------------------------------
@app.route("/api/about")
def get_about_info():
    """Retorna el resumen del marco lógico y metodológico del estudio."""
    return jsonify({
        "proyecto": "AprendizajeSupervisadoML",
        "objetivo": "Predecir los ingresos operativos anuales de empresas bolivianas a partir de su estructura productiva.",
        "fuente": "Encuesta a la Industria Manufacturera, Comercio y Servicios 2017-2018 (EAIMCS), INE Bolivia.",
        "catalogo_anda": "BOL-INE-EAIMCS-2017-2018",
        "cobertura": "Nacional, 9 departamentos (Santa Cruz, La Paz, Cochabamba, Tarija, Oruro, Chuquisaca, Potosí, Beni, Pando).",
        "universo": "Empresas medianas y grandes del directorio empresarial FUNDEMPRESA + Cuentas Nacionales (10,044 empresas registradas).",
        "limitaciones": [
            "Muestra dirigida sin factor de expansión probabilístico.",
            "Corte transversal (gestión contable 2017/2018), no serie temporal.",
            "Exclusión de micro y pequeñas empresas (MIPYMES).",
            "Microdatos anonimizados según Decreto Ley 1405 de confidencialidad estadística."
        ],
        "marco_logico": {
            "fin": "Proveer un valor de referencia técnico y esperado para auditar la consistencia de estadísticas económicas sectoriales.",
            "proposito": "Desarrollar un modelo de Machine Learning con R² ≥ 0.70 y error porcentual mediano ≤ 25% capaz de estimar ingresos.",
            "componentes": [
                "Componente 1: Dataset limpio e integrado (data/processed/dataset_procesado.csv).",
                "Componente 2: Análisis exploratorio integral.",
                "Componente 3: Modelos entrenados y validados (Ridge, Random Forest, HistGradientBoosting).",
                "Componente 4: API REST del modelo con inferencia en sub-segundo.",
                "Componente 5: Dashboard de monitoreo interactivo y MLOps."
            ]
        }
    })


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5055))
    print(f"\n=======================================================")
    print(f"🚀 DASHBOARD DE MACHINE LEARNING LEVANTADO CON ÉXITO")
    print(f"Accede en tu navegador a: http://127.0.0.1:{port}")
    print(f"=======================================================\n")
    app.run(host="0.0.0.0", port=port, debug=True)
