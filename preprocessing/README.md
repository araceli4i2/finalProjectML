# Módulo de Preprocesamiento de Datos (`preprocessing/`)

Este módulo implementa el pipeline de ingeniería de características, limpieza de datos y transformación reproducible para el proyecto **AprendizajeSupervisadoML**, basado en los microdatos de la **EAIMCS 2017-2018** (Instituto Nacional de Estadística de Bolivia).

---

## 1. Entradas y Salidas del Pipeline

### Archivos de Entrada (`data/raw/`)
1. **`MOD_ANUAL_S01-07_12_general_i.csv`**:
   - Estructura: 3,153 filas × 167 columnas.
   - Granularidad: 1 fila = 1 empresa.
   - Llave primaria: `ID`.
   - Contenido: Carátula (departamento `C2_01`, actividad económica `actividad_pricipal_codigo_V1`), Sección 0 (`S00_01_A`), Sección 1 (Personal y salarios), Sección 2 (Energía), Sección 6 (Inventarios), Sección 7 (Activos fijos) y Sección 12 (Almacenamiento).
2. **`MOD_ANUAL_S10_materiales_i.csv`**:
   - Estructura: 6,428 filas × 8 columnas.
   - Granularidad: Multi-registro (N materias primas/materiales declarados por empresa).
   - Llave de unión: `ID`.
   - Variables clave: `materia`, `valor_co` (valor de compras en Bs) y `valor_uti` (valor de utilización en proceso productivo).

### Archivos de Salida (`data/processed/`)
1. **`dataset_procesado.csv`**:
   - Dimensiones: **3,153 filas × 185 columnas**.
   - Incluye variables originales limpias, variables agregadas de insumos, macrosectores homogéneos y columnas transformadas `log_*`.
2. **`dataset_procesado.parquet`** *(si el motor Parquet está disponible)*.

---

## 2. Diagrama de Flujo del Pipeline

```text
┌──────────────────────────────────────┐       ┌──────────────────────────────────────┐
│ MOD_ANUAL_S01-07_12_general_i.csv    │       │ MOD_ANUAL_S10_materiales_i.csv       │
│ (3,153 empresas)                     │       │ (6,428 registros de insumos)         │
└──────────────────┬───────────────────┘       └──────────────────┬───────────────────┘
                   │                                              │
                   │                                              ▼
                   │                               ┌──────────────────────────────────┐
                   │                               │ Paso 1: Limpieza de centinelas   │
                   │                               │ 99999 -> NaN y clip(lower=0)     │
                   │                               └──────────────────┬───────────────┘
                   │                                              │
                   │                                              ▼
                   │                               ┌──────────────────────────────────┐
                   │                               │ Paso 2: Agregación por ID        │
                   │                               │ - n_insumos (conteo)             │
                   │                               │ - total_valor_co (suma compras)  │
                   │                               │ - total_valor_uti (suma uso)     │
                   │                               └──────────────────┬───────────────┘
                   │                                                  │ (1,614 empresas)
                   ▼                                                  ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ Paso 3: Fusión Relacional (Left Join por 'ID')                                      │
│ -> 3,153 empresas conservadas                                                       │
│ -> Imputación coherente: insumos = 0 para empresas no manufactureras                │
└──────────────────────────────────┬──────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ Paso 4: Normalización Categórica                                                    │
│ -> Geografía: depto (C2_01 en mayúsculas, 9 departamentos)                          │
│ -> Actividad: sector_macro (445 códigos CAEB mapeados a 14 macrosectores CIIU)      │
└──────────────────────────────────┬──────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ Paso 5: Tratamiento de la Variable Objetivo (S00_01_A)                              │
│ -> Validación de ingresos positivos (> 0) y cálculo de target_log                   │
│ -> Exclusión de Sección 5 (S05_01 a S05_04) y macro INE para CERO Data Leakage      │
└──────────────────────────────────┬──────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ Paso 6: Transformación Logarítmica log(1 + x)                                       │
│ -> 11 predictores numéricos: personal, sueldos, energía, activos, inventarios, etc. │
└──────────────────────────────────┬──────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ Paso 7: Exportación a data/processed/ (dataset_procesado.csv)                       │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Explicación Detallada Paso a Paso

### Paso 1: Limpieza de Centinelas en Insumos (Sección 10)
- **Qué hace:** En `MOD_ANUAL_S10_materiales_i.csv`, reemplaza el valor centinela **99999** por `NaN` y acota los valores al mínimo cero (`clip(lower=0)`).
- **Por qué:** Según el manual metodológico del INE (`docs/01_analisis_dataset_EAIMCS.md`), el código 99999 indica inconsistencia contable en la identidad de inventarios o imputación pendiente; tratarlo como valor monetario real distorsionaría la media por órdenes de magnitud.
- **Variables afectadas:** `valor_co`, `valor_uti`.

### Paso 2: Agregación de la Sección 10 a Nivel Empresa
- **Qué hace:** Agrupa por `ID` generando tres métricas sintéticas:
  - `n_insumos`: número total de materias primas/materiales declarados por empresa.
  - `total_valor_co`: suma del valor de compra de insumos en Bolivianos (Bs).
  - `total_valor_uti`: suma del valor de utilización de insumos en el ejercicio.
- **Por qué:** La tabla de materiales está en formato largo (una empresa tiene múltiples filas). Para alimentarla a un modelo a nivel empresa (donde 1 fila = 1 empresa), es matemáticamente necesario reducirla a estadísticos agregados por empresa.

### Paso 3: Fusión Relacional (`Left Join`) e Imputación Coherente
- **Qué hace:** Une el módulo anual general con la tabla agregada de materiales mediante un `left_join` por la llave `ID`. Las empresas que no tuvieron registros en la Sección 10 reciben `n_insumos = 0`, `total_valor_co = 0`, `total_valor_uti = 0`.
- **Por qué:** Las empresas de los sectores comercio mayorista/minorista o servicios (que constituyen más del 50% de la muestra) no consumen materias primas de transformación industrial; asignar cero refleja su realidad operativa sin perderlas del análisis.

### Paso 4: Mapeo de Códigos CAEB a Macrosectores
- **Qué hace:** Toma el código de 4 a 5 dígitos `actividad_pricipal_codigo_V1` y lo clasifica según los 2 primeros dígitos en los 14 macrosectores de la Clasificación de Actividades Económicas de Bolivia (CAEB / CIIU Rev. 4).
- **Por qué:** 445 códigos dispersos generan sobreajuste y dispersión dimensional. Agruparlos en macrosectores (Comercio, Manufactura, Construcción, etc.) permite generalizar patrones sectoriales sólidos.

### Paso 5: Variable Objetivo y Prevención de Fuga de Datos (*Data Leakage*)
- **Variable objetivo elegida:** `S00_01_A` (Valor total de ingresos operativos anuales en Bs). Es numéricamente idéntica a `S05_04`.
- **Variables estrictamente excluidas:**
  - `S05_01`, `S05_02`, `S05_03`, `S05_04`: desglose de ventas de la Sección 5. Si se incluyeran, el modelo "memorizaría" la suma de las partes (`Ingresos = S05_01 + S05_02 + S05_03`), causando una fuga de datos artificial con $R^2 = 1.0$ inútil en la práctica.
  - `VBP`, `VA`, `CI`, `VIPP`, etc.: variables macroeconómicas del INE que incorporan directamente el valor bruto de producción.

### Paso 6: Transformación Logarítmica `log(1 + x)`
- **Qué hace:** Aplica $y' = \log(1 + y)$ al ingreso y a los predictores monetarios y de personal.
- **Por qué:** La distribución de ingresos empresariales presenta una asimetría positiva extrema (cola pesada tipo Pareto). La escala logarítmica normaliza los residuos y estabiliza la varianza (homocedasticidad).

---

## 4. Cómo Ejecutar el Preprocesamiento

Desde la terminal en la raíz del proyecto:

```bash
python preprocessing/preprocessing.py
```

### Salida esperada en consola:
```text
[INFO] preprocessing: === INICIANDO PIPELINE DE PREPROCESAMIENTO ===
[INFO] preprocessing: Cargando archivo general: MOD_ANUAL_S01-07_12_general_i.csv
[INFO] preprocessing: Cargando archivo de materiales: MOD_ANUAL_S10_materiales_i.csv
[INFO] preprocessing: Datos crudos leídos: General=3153 filas | Materiales=6428 filas
[INFO] preprocessing: Sección 10 agregada: 1614 empresas únicas con insumos declarados.
[INFO] preprocessing: Unión completada: 3153 empresas válidas con target > 0.
[INFO] preprocessing: Transformación log1p aplicada exitosamente a 11 predictores numéricos.
[INFO] preprocessing: Guardando dataset procesado en CSV: .../data/processed/dataset_procesado.csv
[INFO] preprocessing: === PREPROCESAMIENTO COMPLETADO: 3153 filas x 185 columnas ===

--- RESUMEN ESTADÍSTICO DE LA VARIABLE OBJETIVO (S00_01_A) ---
Total empresas procesadas: 3,153
Mínimo:  Bs 1,285,236.00
Mediana: Bs 15,829,418.00
Media:   Bs 56,892,532.34
Máximo:  Bs 5,292,081,689.00
```
