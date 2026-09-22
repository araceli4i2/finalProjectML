# Módulo de Modelado y MLOps (`models/`)

Este directorio contiene el pipeline de entrenamiento, evaluación comparativa, calibración estadística y monitoreo continuo de deriva de datos (*Data Drift*) para el proyecto **AprendizajeSupervisadoML**.

---

## 1. Estructura del Directorio `models/`

```text
models/
├── README.md                 -> Esta guía técnica de arquitectura y modelos
├── train.py                  -> Script de entrenamiento, validación cruzada (5-Fold CV) y exportación MLOps
├── drift.py                  -> Detector de Data Drift (Prueba de Kolmogorov-Smirnov y distancia de Wasserstein)
└── reference_stats.json      -> Distribuciones empíricas base (percentiles y proporciones de ceros)
```

---

## 2. Flujo de Trabajo del Módulo

```text
data/processed/dataset_procesado.csv
                 │
                 ▼
┌────────────────────────────────────────────────────────┐
│ models/train.py                                        │
│ 1. Carga de predictores numéricos (log1p) y categoricos │
│ 2. Partición estratificada Train (80%) / Test (20%)    │
│ 3. Preprocesamiento: ColumnTransformer                 │
│    - StandardScaler -> 11 variables log1p              │
│    - OneHotEncoder  -> depto y sector_macro            │
│ 4. Evaluación 5-Fold Cross Validation (CV R²)          │
│ 5. Cálculo del Smearing Factor de Duan en escala Bs    │
│ 6. Selección de modelo campeón (Random Forest)        │
└───────────────┬────────────────────────────────────────┘
                │
                ├───────────────────────────────────────────────────────┐
                ▼                                                       ▼
  dashboard/artifacts/                                         models/reference_stats.json
  ├── best_model.joblib          (Pipeline serializado)        (Estadísticas empíricas de
  ├── registry.json              (Gobernanza MLOps)             entrenamiento para drift)
  ├── feature_importance.json    (Importancia de variables)             │
  └── test_predictions.csv       (Residuos y diagnósticos)              ▼
                                                               ┌───────────────────────────┐
                                                               │ models/drift.py           │
                                                               │ KS-test + Wasserstein     │
                                                               │ con ajuste de Bonferroni  │
                                                               └───────────────────────────┘
```

---

## 3. Metodología de Modelado y Calibración

### A. Variable Objetivo y Transformación
- **Target original:** `S00_01_A` (Ingreso Operativo Anual en Bolivianos, idéntico a `S05_04`).
- **Espacio de optimización:** Se modela $y_{\log} = \ln(1 + y)$.
- **Problema de re-transformación:** El operador exponencial simple $\exp(\hat{y}_{\log})$ subestima sistemáticamente la media esperada debido a la desigualdad de Jensen:
  $$\mathbb{E}[\exp(\varepsilon)] \ge \exp(\mathbb{E}[\varepsilon]) = 1$$
- **Solución implementada:** Se aplica el **Estimador de Smearing no paramétrico de Duan**:
  $$s = \frac{1}{n} \sum_{i=1}^n \exp(y_i - \hat{y}_i)$$
  $$\hat{y}_{\text{Bs}} = \max\left(0, \exp(\hat{y}_{\log}) \cdot s - 1\right)$$
  *(Factor de Duan para Random Forest: $s \approx 1.0401$)*.

### B. Predictores Utilizados
1. **11 Variables Numéricas:** `log_S01_05_A` (personal), `log_S01_03_C` (sueldos básicos), `log_S01_14` (otras remuneraciones), `log_S02_09` (energía y agua), `log_S07_09_E` (activos fijos), `log_S06_06_B` (inventarios finales), `log_S12_01_B` (almacén materias primas), `log_S12_02_B` (almacén producto terminado), `log_n_insumos` (variedad de insumos), `log_total_valor_co` (compras de insumos), `log_total_valor_uti` (consumo productivo de insumos).
2. **2 Variables Categóricas:** `depto` (9 departamentos) y `sector_macro` (14 macrosectores CAEB).

---

## 4. Benchmark de Modelos Evaluados

Evaluación sobre el conjunto de prueba independiente (*Test Holdout* 20% = 631 empresas) y validación cruzada de 5 particiones estratificadas:

| Algoritmo | CV $R^2$ (Log) | Test $R^2$ (Log) | Test $R^2$ (Escala Bs) | MedAPE (% Error Mediano) | MAE (Bs) | Smearing Factor | Estado |
|---|---|---|---|---|---|---|---|
| **Ridge Regression** | 0.5476 ± 0.027 | 0.5718 | 0.5171 | 74.07% | 34,309,195 | 1.5352 | Base Lineal |
| **Random Forest Regressor** 🏆 | **0.7724 ± 0.019** | **0.7868** | **0.7529** | **36.20%** | **22,888,317** | **1.0401** | **En Producción** |
| **HistGradientBoosting** | 0.7700 ± 0.014 | 0.7815 | 0.7289 | 36.94% | 23,662,733 | 1.1068 | Alternativa Ensamble |

### Justificación del Modelo Seleccionado:
**Random Forest Regressor** fue seleccionado como el modelo campeón debido a:
- Mayor poder explicativo tanto en escala logarítmica ($R^2 = 0.7868$) como en escala monetaria real ($R^2 = 0.7529$).
- Menor sesgo de re-transformación (factor de Duan más cercano a 1.0: 1.0401 vs 1.1068 de Gradient Boosting).
- Mayor robustez ante relaciones no lineales entre factores productivos (capital y trabajo).
- Capacidad nativa de calcular la dispersión de predicciones entre árboles para estimar intervalos de confianza al 90%.

---

## 5. Sistema de Detección de Data Drift (`models/drift.py`)

El módulo de monitoreo MLOps supervisa la estabilidad temporal de las distribuciones de entrada para alertar si los datos de nuevas empresas difieren significativamente de la base de entrenamiento de la EAIMCS:

1. **Pruebas Estadísticas Aplicadas:**
   - **Prueba de Kolmogorov-Smirnov de 2 Muestras (`ks_2samp`):** Evalúa si la muestra de inferencia proviene de la misma función de distribución acumulada (CDF) continua.
   - **Distancia de Wasserstein (`wasserstein_distance`):** Mide el costo de transporte óptimo (*Earth Mover's Distance*) entre distribuciones.
2. **Corrección por Multiplicidad de Pruebas (Bonferroni):**
   - Al evaluarse simultáneamente 5 variables productivas clave, se ajusta el umbral de significancia:
     $$\alpha_{\text{Bonferroni}} = \frac{\alpha_{\text{base}}}{k} = \frac{0.05}{5} = 0.01$$
3. **Variables Monitoreadas:**
   - Personal Ocupado (`S01_05_A`)
   - Sueldos y Salarios (`S01_03_C`)
   - Energía y Combustibles (`S02_09`)
   - Activos Fijos (`S07_09_E`)
   - Insumos Utilizados (`total_valor_uti`)

---

## 6. Ejecución y Comandos

### Entrenar los Modelos y Generar Artefactos:
```bash
python models/train.py
```

### Ejecutar Verificación del Detector de Drift:
```bash
python models/drift.py
```

---

## 7. Gobernanza y Trazabilidad MLOps

Cada ejecución de `models/train.py`:
1. Genera un identificador de versión único con marca temporal (ej. `v1.20260921.2352`).
2. Actualiza `dashboard/artifacts/registry.json`, archivando la versión anterior y fijando la nueva como `ACTIVE`.
3. Exporta la importancia de variables normalizada a `dashboard/artifacts/feature_importance.json`.
4. Guarda las predicciones detalladas del conjunto de prueba en `dashboard/artifacts/test_predictions.csv` para auditoría y visualización de residuos.
