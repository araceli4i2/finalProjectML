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

## 2. Estructura Reorganizada del Repositorio

El repositorio sigue una arquitectura estandarizada, limpia y modular:

```text
AprendizajeSupervisadoML/
├── .gitignore                         -> Exclusión de venv/, temporales y cachés
├── requirements.txt                   -> Dependencias con versiones fijadas
├── README.md                          -> Guía global del repositorio
├── data/
│   ├── raw/                           -> Datos crudos inmutables (.sav y exportaciones originales .csv)
│   │   ├── MOD_ANUAL_S01-07_12_general_i.sav
│   │   ├── MOD_ANUAL_S10_materiales_i.sav
│   │   ├── MOD_ANUAL_S01-07_12_general_i.csv
│   │   └── MOD_ANUAL_S10_materiales_i.csv
│   └── processed/                     -> Salida oficial generada por preprocessing.py
│       └── dataset_procesado.csv      (3,153 empresas x 185 columnas limpias)
├── preprocessing/
│   ├── README.md                      -> Documentación metodológica del pipeline de datos
│   └── preprocessing.py               -> Módulo central de preprocesamiento, limpieza y agregación
├── models/
│   ├── train.py                       -> Pipeline de entrenamiento con 5-Fold CV y selección de modelo
│   ├── drift.py                       -> Detector de Data Drift (prueba de Kolmogorov-Smirnov)
│   └── reference_stats.json           -> Estadísticas base de distribución para monitoreo
├── dashboard/
│   ├── README.md                      -> Guía autónoma de ejecución del dashboard
│   ├── app.py                         -> Servidor web Flask y API REST
│   ├── data_loader.py                 -> Cargador singleton de datos procesados y cálculo de KPIs
│   ├── run_server.py                  -> Inicializador del servidor en localhost:5055
│   ├── artifacts/                     -> Artefactos generados por models/ y consumidos por el dashboard
│   │   ├── best_model.joblib          -> Pipeline serializado en producción (Random Forest)
│   │   ├── registry.json              -> Metadatos de gobernanza y versiones MLOps
│   │   ├── feature_importance.json    -> Importancia de variables para Plotly.js
│   │   └── test_predictions.csv       -> Predicciones y residuos tabulares del conjunto de prueba
│   ├── static/
│   │   ├── css/styles.css             -> Diseño corporativo, modo oscuro/claro y tipografía Inter
│   │   └── js/app.js                  -> Navegación SPA y renderizado dinámico con Plotly.js
│   └── templates/
│       └── index.html                 -> Cascarón HTML5 Jinja2 con las 8 secciones
├── notebooks/
│   └── convertir.ipynb                -> Notebook de conversión inicial .sav a .csv
└── docs/
    ├── 01_analisis_dataset_EAIMCS.md  -> Análisis metodológico del dataset del INE
    ├── 02_diccionario_datos_EAIMCS.md -> Catálogo oficial de variables y reglas contables
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

El ciclo de ejecución está organizado en 3 pasos secuenciales:

### Paso 1: Ejecutar Preprocesamiento de Datos
Genera el dataset limpio y consolidado en `data/processed/dataset_procesado.csv` tratando centinelas 99999, agregando la Sección 10 y excluyendo variables de fuga de datos:

```bash
python preprocessing/preprocessing.py
```

### Paso 2: Entrenar Modelos y Generar Artefactos MLOps
Evalúa Ridge, Random Forest e HistGradientBoosting con validación cruzada de 5 particiones y genera los artefactos en `dashboard/artifacts/`:

```bash
python models/train.py
```

#### Métricas Obtenidas en el Conjunto de Prueba (Test Holdout 20%):
| Algoritmo | CV $R^2$ (Log) | Test $R^2$ (Log) | Test $R^2$ (Escala Bs) | MedAPE (% Error Mediano) | Estado |
|---|---|---|---|---|---|
| **Ridge Regression** | 0.5414 | 0.5819 | 0.2692 | 52.73% | Base Lineal |
| **Random Forest Regressor** 🏆 | **0.7675** | **0.8012** | **0.7599** | **31.10%** | **En Producción** |
| **HistGradientBoosting** | 0.7661 | 0.8029 | 0.6148 | 31.13% | Evaluado |

### Paso 3: Levantar el Dashboard Web
Inicia el servidor Flask para explorar las 8 secciones interactivas:

```bash
python dashboard/app.py
```
*(O de forma alternativa: `python dashboard/run_server.py`)*

Abre en tu navegador web:
👉 **`http://127.0.0.1:5055`**

---

## 5. Fuentes y Referencias Técnicas

- **Fuente Oficial:** Instituto Nacional de Estadística (INE), Bolivia.
- **Catálogo ANDA:** [BOL-INE-EAIMCS-2017-2018](https://anda.ine.gob.bo/index.php/catalog/252)
- **Documentación Técnica Local:**
  - `docs/01_analisis_dataset_EAIMCS.md`: Cobertura, universo y diseño muestral.
  - `docs/02_diccionario_datos_EAIMCS.md`: Diccionario de variables y reglas contables.
  - `docs/marco_logico_ingresos_operativos.md`: Árbol de objetivos, supuestos e indicadores CCT.
  - `preprocessing/README.md`: Diagrama de flujo y transformaciones del preprocesamiento.
  - `dashboard/README.md`: Catálogo de endpoints y uso del dashboard.
