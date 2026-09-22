# Documentación Técnica y Metodológica (`docs/`)

Este directorio contiene los fundamentos teóricos, metodológicos, estadísticos y de marco lógico del proyecto **AprendizajeSupervisadoML**, basados en los microdatos oficiales de la **EAIMCS 2017-2018** del Instituto Nacional de Estadística (INE) de Bolivia.

---

## 1. Estructura del Directorio `docs/`

```text
docs/
├── README.md                              -> Esta guía e índice central de documentación
├── 01_analisis_dataset_EAIMCS.md          -> Cobertura, marco muestral, tasas de respuesta y sesgos
├── 02_diccionario_datos_EAIMCS.md         -> Catálogo oficial de variables y reglas contables
└── marco_logico_ingresos_operativos.md    -> Matriz de marco lógico, árbol de objetivos e indicadores CCT
```

---

## 2. Índice de Documentos Metodológicos

### 1. [01_analisis_dataset_EAIMCS.md](file:///c:/Users/RAQUEL%20SERRANO/OneDrive/Documentos/AprendizajeSupervisadoML/docs/01_analisis_dataset_EAIMCS.md)
- **Tema:** Análisis contextual y muestral de la encuesta.
- **Contenido Clave:**
  - Identificación del estudio en el catálogo ANDA (`BOL-INE-EAIMCS-2017-2018`).
  - Cobertura geográfica nacional (9 departamentos) y delimitación al estrato de empresas medianas y grandes.
  - Diseño muestral: muestra dirigida sobre un directorio de 10,044 empresas registradas en FUNDEMPRESA y Cuentas Nacionales.
  - Umbrales de estratificación por tamaño (Bs 2.45M – 35M para medianas de producción, > 35M para grandes).
  - Tasa de cobertura efectiva (41.4%) e implicaciones del sesgo de no respuesta y de formalidad para los modelos predictivos.

### 2. [02_diccionario_datos_EAIMCS.md](file:///c:/Users/RAQUEL%20SERRANO/OneDrive/Documentos/AprendizajeSupervisadoML/docs/02_diccionario_datos_EAIMCS.md)
- **Tema:** Catálogo estructurado de variables y especificación contable.
- **Contenido Clave:**
  - Mapeo columna por columna de los módulos general (`MOD_ANUAL_S01-07_12_general_i`) y de materiales (`MOD_ANUAL_S10_materiales_i`).
  - Identificación de la variable objetivo: `S00_01_A` (Ingreso Operativo Anual) y su equivalencia con `S05_04`.
  - Definición de factores productivos: personal (`S01_05_A`), masa salarial (`S01_03_C`), energía (`S02_09`), activos fijos (`S07_09_E`), inventarios (`S06_06_B`) y almacenamiento (`S12_01_B`, `S12_02_B`).
  - Reglas de depuración de valores centinela (`99999` = imputación pendiente/inconsistencia).
  - Listado exhaustivo de variables excluidas por riesgo de fuga de datos (*data leakage*).

### 3. [marco_logico_ingresos_operativos.md](file:///c:/Users/RAQUEL%20SERRANO/OneDrive/Documentos/AprendizajeSupervisadoML/docs/marco_logico_ingresos_operativos.md)
- **Tema:** Formulación del proyecto mediante la Metodología de Marco Lógico (MML).
- **Contenido Clave:**
  - **Árbol de Problemas:** Causa raíz de la falta de herramientas cuantitativas para detectar inconsistencias y subdeclaración en auditorías económicas.
  - **Árbol de Objetivos:** Medios y fines para disponer de un estimador objetivo del ingreso empresarial basado en insumos productivos.
  - **Matriz de Marco Lógico (MML):**
    - *Fin:* Fortalecer la integridad de las estadísticas económicas y la equidad tributaria.
    - *Propósito:* Desarrollar un sistema de Machine Learning con $R^2 \ge 0.70$ y error mediano porcentual $\le 25\%$ (medido en escala logarítmica).
    - *Componentes:* 1) Dataset integrado y depurado, 2) Análisis exploratorio interactivo, 3) Modelos supervisados validados, 4) API REST de inferencia, 5) Dashboard web MLOps.
    - *Actividades:* Cronograma y recursos requeridos.

---

## 3. Relación con la Arquitectura de Software

Los documentos de este directorio sirven de especificación formal para:
- La lógica de limpieza en [`preprocessing/preprocessing.py`](file:///c:/Users/RAQUEL%20SERRANO/OneDrive/Documentos/AprendizajeSupervisadoML/preprocessing/preprocessing.py).
- La validación del modelo en [`models/train.py`](file:///c:/Users/RAQUEL%20SERRANO/OneDrive/Documentos/AprendizajeSupervisadoML/models/train.py).
- Las secciones informativas y el endpoint `/api/about` en [`dashboard/app.py`](file:///c:/Users/RAQUEL%20SERRANO/OneDrive/Documentos/AprendizajeSupervisadoML/dashboard/app.py).
