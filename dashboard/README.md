# Dashboard Web: Estimación de Ingresos Operativos (EAIMCS - INE Bolivia)

Este directorio contiene todo el código fuente, plantillas, estilos y artefactos necesarios para la ejecución del dashboard web corporativo del proyecto **AprendizajeSupervisadoML**.

---

## 1. Estructura de la Carpeta `dashboard/`

```text
dashboard/
├── README.md                 -> Esta guía de ejecución y arquitectura
├── app.py                    -> Servidor web Flask y API REST (/api/kpis, /api/predict, etc.)
├── data_loader.py            -> Cargador singleton de datos procesados y pre-cálculo de KPIs
├── run_server.py             -> Script de inicialización directa en el puerto 5055
├── artifacts/                -> Artefactos serializados generados por el pipeline de models/
│   ├── best_model.joblib     -> Pipeline de regresión entrenado (Random Forest)
│   ├── registry.json         -> Trazabilidad MLOps, versiones y métricas
│   ├── feature_importance.json -> Pesos relativos de predictores para Plotly.js
│   └── test_predictions.csv  -> Datos tabulares de predicciones de prueba y residuos
├── static/
│   ├── css/
│   │   └── styles.css        -> Sistema de diseño con variables CSS, dark/light mode y tipografía Inter
│   └── js/
│       └── app.js            -> Navegación SPA, renderizado dinámico con Plotly y llamadas a la API
└── templates/
    └── index.html            -> Plantilla Jinja2 con las 8 secciones y diseño responsive
```

---

## 2. Cómo Ejecutar el Dashboard

### Opción A: Desde la raíz del proyecto
```bash
python dashboard/app.py
```
O usando el script de inicialización:
```bash
python dashboard/run_server.py
```

### Opción B: Desde dentro de la carpeta `dashboard/`
```bash
cd dashboard
python app.py
```

El servidor iniciará localmente y estará disponible en:
👉 **`http://127.0.0.1:5055`** (o `http://127.0.0.1:5000`)

---

## 3. Catálogo de Endpoints de la API REST

| Método | Endpoint | Descripción |
|---|---|---|
| `GET` | `/` | Renderiza el cascarón SPA del dashboard (Jinja2). |
| `GET` | `/api/kpis` | Retorna los KPIs macroeconómicos de la EAIMCS (empresas, ingresos medianos/promedios). |
| `GET` | `/api/dictionary` | Diccionario interactivo y buscable de variables oficiales. |
| `GET` | `/api/eda/distribution` | Distribución de ingresos (escala natural y logarítmica). |
| `GET` | `/api/eda/boxplot_deptos` | Diagramas de caja por los 9 departamentos de Bolivia. |
| `GET` | `/api/eda/boxplot_sectors` | Diagramas de caja por macrosector económico CAEB. |
| `GET` | `/api/eda/correlations` | Matriz de correlación lineal entre factores productivos e ingresos. |
| `GET` | `/api/eda/outliers` | Gráfico de dispersión de inconsistencias y auditoría de centinelas. |
| `GET` | `/api/pipeline` | Pasos secuenciales del pipeline de preprocesamiento. |
| `GET` | `/api/models` | Comparativa de modelos, residuos e importancia de variables. |
| `POST` | `/api/predict` | Endpoint de inferencia predictiva con intervalos de confianza al 90%. |
| `GET` | `/api/mlops` | Estado de gobernanza, versiones registradas y prueba de Data Drift. |
| `POST` | `/api/mlops/drift` | Simulación y auditoría de la prueba de Kolmogorov-Smirnov. |
| `GET` | `/api/about` | Marco lógico, metodología del INE y limitaciones. |
