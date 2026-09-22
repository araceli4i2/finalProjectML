# AprendizajeSupervisadoML: Estimación de Ingresos Operativos Anuales (EAIMCS - INE Bolivia)

Sistema integral de Machine Learning supervisado (regresión) y Dashboard Web interactivo desarrollado en **Python (Flask + Scikit-Learn + Jinja2 + Plotly.js)** para predecir y auditar los ingresos operativos anuales de empresas bolivianas medianas y grandes, utilizando como fuente oficial los microdatos de la **Encuesta a la Industria Manufacturera, Comercio y Servicios (EAIMCS 2017-2018)** del Instituto Nacional de Estadística (INE) de Bolivia (Catálogo ANDA: `BOL-INE-EAIMCS-2017-2018`).

---

## 1. Propósito del Proyecto y Objetivo de Predicción

El objetivo central es estimar el **Ingreso Operativo Anual (`S00_01_A` / `S05_04`)** en Bolivianos (Bs) que una empresa formal debería generar a partir de sus variables de estructura productiva:
- **Personal ocupado total (`S01_05_A`)** y composición laboral.
- **Sueldos y salarios básicos anuales (`S01_03_C`)** y otras remuneraciones (`S01_14`).
- **Energía, agua y combustibles (`S02_09`)**.
- **Valor histórico final de activos fijos (`S07_09_E`)** (maquinaria, instalaciones, equipo de transporte).
- **Inventarios finales (`S06_06_B`)**.
- **Capacidad de almacenamiento (`S12_01_B`, `S12_02_B`)**.
- **Materias primas y materiales (`Sección 10`)**, agregadas a nivel empresa por `ID` en compras y utilización.
- **Ubicación geográfica (`C2_01`)** (los 9 departamentos de Bolivia) y **Actividad Económica CAEB (`actividad_pricipal_codigo_V1`)** mapeada a 14 macrosectores homogéneos (Comercio, Industria, Construcción, Servicios).

### Caso de Uso y Marco Lógico
Proveer un **valor esperado técnico e imparcial** que sirva de contraste para detectar discrepancias estadísticas, reportes subvaluados o inconsistencias contables antes de consolidar cuentas nacionales o formular políticas sectoriales.

---

## 2. Estructura Modular del Repositorio

El repositorio sigue una arquitectura estandarizada, limpia y completamente modular, donde cada directorio contiene su propia documentación técnica autónoma:

```text
AprendizajeSupervisadoML/
├── .gitignore                         -> Exclusión de entornos virtuales, temporales y cachés
├── requirements.txt                   -> Dependencias consolidadas del proyecto con versiones fijadas
├── README.md                          -> Guía global del repositorio (este documento)
├── data/                              -> Capa de datos crudos inmutables y procesados
│   ├── README.md                      -> Especificación, gobernanza y origen de microdatos
│   ├── raw/                           -> Microdatos crudos del INE (.sav y exportaciones .csv)
│   │   ├── MOD_ANUAL_S01-07_12_general_i.sav
│   │   ├── MOD_ANUAL_S01-07_12_general_i.csv  (3,153 empresas x 167 variables)
│   │   ├── MOD_ANUAL_S10_materiales_i.sav
│   │   └── MOD_ANUAL_S10_materiales_i.csv     (6,428 registros de insumos x 8 variables)
│   └── processed/                     -> Salida consolidada generada por preprocessing.py
│       └── dataset_procesado.csv      (3,153 empresas x 185 columnas limpias)
├── preprocessing/                     -> Pipeline de limpieza, ingeniería de datos y anti-leakage
│   ├── README.md                      -> Documentación metodológica del pipeline de datos
│   ├── explicacion_preprocesamiento.md -> Guía detallada del tratamiento y transformaciones del dataset
│   └── preprocessing.py               -> Módulo ejecutable de limpieza, agregación relacional y exportación
├── models/                            -> Pipeline de entrenamiento, calibración y MLOps
│   ├── README.md                      -> Arquitectura de modelado, validación cruzada y Data Drift
│   ├── train.py                       -> Pipeline de entrenamiento con 5-Fold CV y selección de modelo
│   ├── drift.py                       -> Detector de Data Drift (Kolmogorov-Smirnov y Wasserstein)
│   └── reference_stats.json           -> Distribuciones empíricas base para auditoría de deriva
├── dashboard/                         -> Aplicación web interactiva y API REST
│   ├── README.md                      -> Arquitectura del dashboard, catálogo API e instrucciones
│   ├── requirements.txt               -> Dependencias específicas del entorno web
│   ├── app.py                         -> Servidor web Flask y API REST (/api/kpis, /api/predict, etc.)
│   ├── data_loader.py                 -> Cargador singleton de datos procesados y cálculo de KPIs
│   ├── run_server.py                  -> Lanzador alternativo en localhost:5055
│   ├── artifacts/                     -> Artefactos serializados generados por models/train.py
│   │   ├── best_model.joblib          -> Pipeline serializado en producción (Random Forest)
│   │   ├── registry.json              -> Metadatos de gobernanza y control de versiones MLOps
│   │   ├── feature_importance.json    -> Importancia de variables normalizada para Plotly.js
│   │   └── test_predictions.csv       -> Predicciones y residuos tabulares del conjunto de prueba
│   ├── static/                        -> Recursos frontend (CSS corporativo y JS Plotly)
│   │   ├── css/styles.css
│   │   └── js/app.js
│   └── templates/
│       └── index.html                 -> Cascarón SPA Jinja2 con las 8 secciones interactivas
├── notebooks/                         -> Cuadernos de conversión y experimentación
│   ├── README.md                      -> Guía de ejecución de cuadernos interactivos
│   └── convertir.ipynb                -> Cuaderno de conversión de archivos SPSS (.sav) a CSV (.csv)
└── docs/                              -> Fundamentación teórica, diccionario y marco lógico
    ├── README.md                      -> Índice central de documentación metodológica
    ├── 01_analisis_dataset_EAIMCS.md  -> Análisis de cobertura, marco muestral y sesgos del INE
    ├── 02_diccionario_datos_EAIMCS.md -> Catálogo exhaustivo de variables y reglas contables
    └── marco_logico_ingresos_operativos.md -> Matriz de marco lógico, árbol de objetivos y metas CCT
```

---

## 3. Instalación y Requisitos

### Requisitos Previos
- **Python 3.10 o superior**
- Entorno virtual recomendado:

```bash
python -m venv venv

# En Windows:
.\venv\Scripts\activate
# En Linux / macOS:
source venv/bin/activate
```

### Instalación de Dependencias
```bash
pip install -r requirements.txt
```

---

## 4. Orden de Ejecución del Proyecto

El ciclo de ejecución está organizado en pasos secuenciales y reproducibles:

### Paso 1: Ejecutar Preprocesamiento de Datos
Genera el dataset limpio y consolidado en `data/processed/dataset_procesado.csv` tratando centinelas 99999, agregando la Sección 10 y excluyendo variables de fuga de datos:

```bash
python preprocessing/preprocessing.py
```
> Consulta más detalles en [preprocessing/README.md](file:///c:/Users/RAQUEL%20SERRANO/OneDrive/Documentos/AprendizajeSupervisadoML/preprocessing/README.md).

### Paso 2: Entrenar Modelos y Generar Artefactos MLOps
Evalúa Ridge, Random Forest e HistGradientBoosting con validación cruzada estratificada de 5 particiones, calibra con el factor de Duan y genera los artefactos en `dashboard/artifacts/`:

```bash
python models/train.py
```

#### Métricas del Modelo en Producción (Registro MLOps Activo `v1.20260921.2352`):
| Algoritmo | CV $R^2$ (Log) | Test $R^2$ (Log) | Test $R^2$ (Escala Bs) | MedAPE (% Error Mediano) | MAE (Bs) | Smearing Factor | Estado |
|---|---|---|---|---|---|---|---|
| **Ridge Regression** | 0.5476 ± 0.027 | 0.5718 | 0.5171 | 74.07% | 34,309,195 | 1.5352 | Base Lineal |
| **Random Forest Regressor** 🏆 | **0.7724 ± 0.019** | **0.7868** | **0.7529** | **36.20%** | **22,888,317** | **1.0401** | **En Producción** |
| **HistGradientBoosting** | 0.7700 ± 0.014 | 0.7815 | 0.7289 | 36.94% | 23,662,733 | 1.1068 | Alternativa Ensamble |

> Consulta más detalles en [models/README.md](file:///c:/Users/RAQUEL%20SERRANO/OneDrive/Documentos/AprendizajeSupervisadoML/models/README.md).

### Paso 3: (Opcional) Verificar Monitoreo de Data Drift
Verifica la prueba de dos muestras de Kolmogorov-Smirnov y distancia de Wasserstein con corrección de Bonferroni:

```bash
python models/drift.py
```

### Paso 4: Levantar el Dashboard Web
Inicia el servidor Flask para interactuar con las 8 secciones del dashboard:

```bash
python dashboard/app.py
```
*(O de forma alternativa: `python dashboard/run_server.py`)*

Abre en tu navegador web:
👉 **`http://127.0.0.1:5055`**

> Consulta el catálogo completo de rutas y API en [dashboard/README.md](file:///c:/Users/RAQUEL%20SERRANO/OneDrive/Documentos/AprendizajeSupervisadoML/dashboard/README.md).

---

## 5. Documentación y Guías Modulares

Cada módulo del repositorio cuenta con su propia guía técnica detallada:

- 📊 **Capa de Datos:** [data/README.md](file:///c:/Users/RAQUEL%20SERRANO/OneDrive/Documentos/AprendizajeSupervisadoML/data/README.md)
- ⚙️ **Preprocesamiento:** [preprocessing/README.md](file:///c:/Users/RAQUEL%20SERRANO/OneDrive/Documentos/AprendizajeSupervisadoML/preprocessing/README.md) y [explicacion_preprocesamiento.md](file:///c:/Users/RAQUEL%20SERRANO/OneDrive/Documentos/AprendizajeSupervisadoML/preprocessing/explicacion_preprocesamiento.md)
- 🤖 **Modelos y MLOps:** [models/README.md](file:///c:/Users/RAQUEL%20SERRANO/OneDrive/Documentos/AprendizajeSupervisadoML/models/README.md)
- 🖥️ **Dashboard Web y API:** [dashboard/README.md](file:///c:/Users/RAQUEL%20SERRANO/OneDrive/Documentos/AprendizajeSupervisadoML/dashboard/README.md)
- 📓 **Cuadernos de Conversión:** [notebooks/README.md](file:///c:/Users/RAQUEL%20SERRANO/OneDrive/Documentos/AprendizajeSupervisadoML/notebooks/README.md)
- 📚 **Metodología y Marco Lógico:** [docs/README.md](file:///c:/Users/RAQUEL%20SERRANO/OneDrive/Documentos/AprendizajeSupervisadoML/docs/README.md)
