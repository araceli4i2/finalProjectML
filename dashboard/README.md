# Módulo del Dashboard Web (`dashboard/`)

Este directorio contiene el servidor web, la API REST, la interfaz SPA interactiva (*Single Page Application*), los estilos visuales y los artefactos serializados de Machine Learning para el proyecto **AprendizajeSupervisadoML**.

---

## 1. Estructura del Directorio `dashboard/`

```text
dashboard/
├── README.md                 -> Esta guía de arquitectura y uso del dashboard
├── requirements.txt          -> Dependencias específicas del entorno web
├── app.py                    -> Servidor web Flask y catálogo de rutas API REST
├── data_loader.py            -> Cargador Singleton de datos preprocesados y agregaciones
├── run_server.py             -> Script de inicialización directa en el puerto 5055
├── artifacts/                -> Artefactos de ML consumidos por el dashboard (desde models/)
│   ├── best_model.joblib     -> Pipeline de regresión entrenado (Random Forest Regressor)
│   ├── registry.json         -> Trazabilidad MLOps, histórico de versiones y métricas
│   ├── feature_importance.json -> Importancia relativa de predictores para Plotly.js
│   └── test_predictions.csv  -> Predicciones y residuos tabulares del conjunto de prueba
├── static/                   -> Recursos estáticos del frontend
│   ├── css/
│   │   └── styles.css        -> Sistema de diseño corporativo, soporte dark/light y tipografía Inter
│   └── js/
│       └── app.js            -> Lógica cliente, navegación SPA, llamadas asíncronas y gráficos Plotly.js
└── templates/                -> Plantillas del motor Jinja2
    └── index.html            -> Cascarón HTML5 interactivo con las 8 secciones analíticas
```

---

## 2. Las 8 Secciones del Dashboard Interactivo

El dashboard está concebido para perfiles tanto ejecutivos como técnicos y de auditoría:

1. **Resumen Ejecutivo & KPIs:** Métricas macroeconómicas consolidadas de las 3,153 empresas encuestadas (ingresos medios/medianos, dispersión por departamentos, volumen muestral).
2. **Diccionario de Datos Interactivo:** Buscador en tiempo real de variables oficiales con desglose por secciones, tipos de datos y reglas de consistencia contable del INE.
3. **Análisis Exploratorio (EDA):** Gráficos dinámicos con Plotly.js:
   - Distribución de ingresos (escala natural asimétrica vs. normalizada $\log(1+x)$).
   - Boxplots por los 9 departamentos de Bolivia.
   - Boxplots por los 14 macrosectores económicos CAEB.
   - Mapa de calor de correlaciones lineales de Spearman/Pearson.
   - Gráfico de dispersión de inconsistencias y detección de centinelas 99999.
4. **Pipeline de Preprocesamiento:** Trazabilidad paso a paso del flujo de ingeniería de datos y políticas de prevención de fuga de información (*anti-leakage*).
5. **Diagnóstico de Modelos:** Comparativa de desempeño (Ridge vs. Random Forest vs. HistGradientBoosting), diagrama de dispersión de *Valores Reales vs. Predichos*, distribución de residuos y ranking de importancia de variables.
6. **Simulador Predictivo Interactivo:** Formulario de inferencia operativa en tiempo real con estimación en Bolivianos (Bs), cálculo de intervalos de predicción al 90% y clasificación de tamaño empresarial (Mediana vs. Gran empresa según umbrales de producción/servicios).
7. **MLOps, Versiones y Data Drift:** Auditoría de versiones registradas en `registry.json` y consola interactiva para simular y verificar la prueba de Kolmogorov-Smirnov y distancia de Wasserstein frente a distribuciones base.
8. **Marco Lógico y Metodología:** Justificación técnica, matriz de marco lógico, árbol de objetivos y limitaciones metodológicas de la EAIMCS.

---

## 3. Catálogo de Endpoints de la API REST

| Método | Endpoint | Descripción |
|---|---|---|
| `GET` | `/` | Renderiza la interfaz gráfica SPA Jinja2. |
| `GET` | `/api/kpis` | Retorna los KPIs macroeconómicos calculados por el data loader. |
| `GET` | `/api/dictionary` | Diccionario interactivo filtrable por texto (`?q=`) y sección (`?section=`). |
| `GET` | `/api/eda/distribution` | Histogramas de distribución natural y logarítmica para Plotly. |
| `GET` | `/api/eda/boxplot_deptos` | Datos agregados de cuartiles para los 9 departamentos. |
| `GET` | `/api/eda/boxplot_sectors` | Datos agregados de cuartiles para los 14 macrosectores CAEB. |
| `GET` | `/api/eda/correlations` | Matriz de correlación lineal entre factores de producción e ingresos. |
| `GET` | `/api/eda/outliers` | Relación empírica entre ingreso declarado y salarios/personal. |
| `GET` | `/api/pipeline` | Lista estructurada de las 8 fases del pipeline de preprocesamiento. |
| `GET` | `/api/models` | Métricas de los modelos evaluados, importancia de variables y residuos de prueba. |
| `POST` | `/api/predict` | Inferencia predictiva en escala real (Bs) con corrección de Duan e intervalo de confianza. |
| `GET` | `/api/mlops` | Historial de versiones del registro MLOps y estado actual de deriva estadística. |
| `POST` | `/api/mlops/drift` | Ejecuta la simulación de deriva de datos para una variable específica. |
| `GET` | `/api/about` | Metadatos de la encuesta EAIMCS, marco lógico y limitaciones de muestreo. |

---

## 4. Instrucciones de Ejecución

### Opción A: Desde la raíz del proyecto (Recomendado)
```bash
python dashboard/app.py
```
O bien mediante el script lanzador con configuración de puerto:
```bash
python dashboard/run_server.py
```

### Opción B: Desde dentro de la carpeta `dashboard/`
```bash
cd dashboard
python app.py
```

Una vez iniciado, abre tu navegador en:
👉 **`http://127.0.0.1:5055`**

---

## 5. Dependencias y Requisitos

Las dependencias pueden instalarse desde la raíz (`pip install -r requirements.txt`) o específicamente para el dashboard:
```bash
pip install -r dashboard/requirements.txt
```

---

## 6. Documentación Relacionada

- [models/README.md](file:///c:/Users/RAQUEL%20SERRANO/OneDrive/Documentos/AprendizajeSupervisadoML/models/README.md): Entrenamiento, calibración y generación de los artefactos en `artifacts/`.
- [preprocessing/README.md](file:///c:/Users/RAQUEL%20SERRANO/OneDrive/Documentos/AprendizajeSupervisadoML/preprocessing/README.md): Pipeline de transformación que alimenta el archivo de datos consumido por `data_loader.py`.
- [docs/02_diccionario_datos_EAIMCS.md](file:///c:/Users/RAQUEL%20SERRANO/OneDrive/Documentos/AprendizajeSupervisadoML/docs/02_diccionario_datos_EAIMCS.md): Definición detallada de cada variable expuesta en `/api/dictionary`.
