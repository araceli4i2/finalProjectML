# Módulo de Preprocesamiento de Datos (`preprocessing/`)

Este módulo implementa el pipeline integral de ingeniería de características, depuración de centinelas y transformación de datos reproducible para el proyecto **AprendizajeSupervisadoML**, basado en los microdatos de la **EAIMCS 2017-2018** del Instituto Nacional de Estadística (INE) de Bolivia.

> 📘 **Documento Metodológico Detallado:** Para una explicación pormenorizada con justificación teórica, tratamiento de centinelas (99999), agregación relacional, prevención de fuga de datos (*data leakage*) y transformaciones logarítmicas, consulta [explicacion_preprocesamiento.md](file:///c:/Users/RAQUEL%20SERRANO/OneDrive/Documentos/AprendizajeSupervisadoML/preprocessing/explicacion_preprocesamiento.md).

---

## 1. Estructura del Directorio `preprocessing/`

```text
preprocessing/
├── README.md                          -> Esta guía metodológica y de ejecución del pipeline
├── preprocessing.py                   -> Módulo ejecutable de carga, limpieza, agregación y exportación
└── explicacion_preprocesamiento.md    -> Justificación matemática, técnica y contable detallada
```

---

## 2. Entradas y Salidas del Pipeline

### Archivos de Entrada (`data/raw/`)
1. **`MOD_ANUAL_S01-07_12_general_i.csv`**:
   - **Estructura:** 3,153 filas × 167 columnas.
   - **Granularidad:** 1 fila = 1 empresa.
   - **Llave primaria:** `ID`.
   - **Contenido:** Carátula (departamento `C2_01`, actividad económica `actividad_pricipal_codigo_V1`), Sección 0 (`S00_01_A`), Sección 1 (Personal y salarios), Sección 2 (Energía), Sección 6 (Inventarios), Sección 7 (Activos fijos) y Sección 12 (Almacenamiento).
2. **`MOD_ANUAL_S10_materiales_i.csv`**:
   - **Estructura:** 6,428 filas × 8 columnas.
   - **Granularidad:** Multi-registro (N materias primas/materiales declarados por empresa).
   - **Llave de unión:** `ID`.
   - **Variables clave:** `materia`, `valor_co` (compras en Bs) y `valor_uti` (utilización en proceso productivo en Bs).

### Archivos de Salida (`data/processed/`)
1. **`dataset_procesado.csv`**:
   - **Dimensiones:** **3,153 filas × 185 columnas**.
   - Incluye variables originales limpias, variables agregadas de insumos, macrosectores homogéneos y columnas transformadas con $\log(1 + x)$ (`log_*`).

---

## 3. Diagrama de Flujo del Pipeline

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

## 4. Resumen de Etapas de Limpieza y Transformación

### Paso 1: Limpieza de Centinelas en Insumos (Sección 10)
En `MOD_ANUAL_S10_materiales_i.csv`, sustituye el código de control **99999** (imputación pendiente del INE o descuadre contable) por `NaN` y acota los valores al mínimo cero (`clip(lower=0)`).

### Paso 2: Agregación de Insumos a Nivel Empresa
Agrupa la tabla de materiales por `ID` calculando:
- `n_insumos`: conteo de insumos declarados.
- `total_valor_co`: suma del valor de compra en Bolivianos (Bs).
- `total_valor_uti`: suma del valor de utilización productiva en Bolivianos (Bs).

### Paso 3: Fusión Relacional (`Left Join`) e Imputación Coherente
Se fusionan las tablas manteniendo la totalidad de las 3,153 empresas. Aquellas empresas comerciales o de servicios sin insumos manufactureros reciben valor `0`, reflejando fielmente su estructura de costos sin pérdida de registros.

### Paso 4: Mapeo de Códigos CAEB a 14 Macrosectores
Se consolidan 445 códigos específicos de actividad económica en 14 macrosectores agregados (Industria Manufacturera, Comercio Mayorista, Servicios a Empresas, etc.) para evitar sobredispersión categórica.

### Paso 5: Prevención Estricta de Fuga de Datos (*Anti-Leakage*)
Se eliminan del espacio de predictores las variables que reproducen contablemente el target:
- Desglose de ingresos de la Sección 5 (`S05_01`, `S05_02`, `S05_03`, `S05_04`).
- Agregados macroeconómicos calculados por el INE (`VBP`, `VA`, `CI`, `VIPP`, etc.).

### Paso 6: Transformación Logarítmica
Se aplica $\ln(1 + x)$ a las variables de escala monetaria y personal para mitigar el sesgo de asimetría positiva de Pareto y garantizar homocedasticidad.

---

## 5. Cómo Ejecutar el Preprocesamiento

Desde la terminal en la raíz del proyecto:
```bash
python preprocessing/preprocessing.py
```

El script verificará la existencia de los datos crudos en `data/raw/` y escribirá el archivo consolidado en `data/processed/dataset_procesado.csv`.

---

## 6. Documentación Relacionada

- [data/README.md](file:///c:/Users/RAQUEL%20SERRANO/OneDrive/Documentos/AprendizajeSupervisadoML/data/README.md): Especificación de datos crudos y gobernanza.
- [models/README.md](file:///c:/Users/RAQUEL%20SERRANO/OneDrive/Documentos/AprendizajeSupervisadoML/models/README.md): Pipeline de entrenamiento que consume la salida de este módulo.
- [explicacion_preprocesamiento.md](file:///c:/Users/RAQUEL%20SERRANO/OneDrive/Documentos/AprendizajeSupervisadoML/preprocessing/explicacion_preprocesamiento.md): Justificación metodológica detallada paso a paso.
