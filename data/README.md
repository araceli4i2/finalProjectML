# Capa de Datos (`data/`): Microdatos y Datasets

Este directorio centraliza el almacenamiento de los datos del proyecto **AprendizajeSupervisadoML**, diferenciando estrictamente entre las fuentes crudas inmutables y el dataset procesado listo para el modelado.

---

## 1. Estructura del Directorio `data/`

```text
data/
├── README.md                          -> Esta guía de gobernanza y especificación de datos
├── raw/                               -> Microdatos originales inmutables (INE Bolivia)
│   ├── MOD_ANUAL_S01-07_12_general_i.sav  (3.65 MB, formato SPSS original)
│   ├── MOD_ANUAL_S01-07_12_general_i.csv  (3.78 MB, exportación tabular)
│   ├── MOD_ANUAL_S10_materiales_i.sav     (634 KB, formato SPSS original)
│   └── MOD_ANUAL_S10_materiales_i.csv     (506 KB, exportación tabular)
└── processed/                         -> Salida generada por preprocessing/preprocessing.py
    └── dataset_procesado.csv          (4.55 MB, 3,153 empresas x 185 columnas)
```

---

## 2. Origen y Especificación de Microdatos Crudos (`data/raw/`)

Los microdatos provienen de la **Encuesta a la Industria Manufacturera, Comercio y Servicios (EAIMCS 2017-2018)** realizada por el Instituto Nacional de Estadística (INE) de Bolivia:
- **Catálogo ANDA:** [BOL-INE-EAIMCS-2017-2018](https://anda.ine.gob.bo/index.php/catalog/252)
- **Marco Muestral:** Directorio de 10,044 empresas medianas y grandes del registro FUNDEMPRESA y Cuentas Nacionales.
- **Universo de Cobertura:** 9 departamentos de Bolivia (La Paz, Santa Cruz, Cochabamba, Tarija, Oruro, Chuquisaca, Potosí, Beni, Pando).

### Tablas Crudas:
1. **Módulo General Anual (`MOD_ANUAL_S01-07_12_general_i`)**:
   - **Dimensiones:** 3,153 filas × 167 columnas.
   - **Granularidad:** 1 fila = 1 empresa.
   - **Llave Primaria:** `ID` (código anonimizado del informante).
   - **Secciones incluidas:**
     - Carátula: Departamento (`C2_01`), Actividad económica CAEB (`actividad_pricipal_codigo_V1`).
     - Sección 0: Carátula económica y valor total de producción (`S00_01_A` = Ingreso Operativo).
     - Sección 1: Personal ocupado (`S01_05_A`), sueldos básicos (`S01_03_C`), aguinaldos y aportes patronales (`S01_14`).
     - Sección 2: Consumo de energía eléctrica, agua y combustibles (`S02_09`).
     - Sección 6: Inventarios iniciales y finales (`S06_06_B`).
     - Sección 7: Activos fijos (maquinaria, edificios, vehículos) y valor histórico (`S07_09_E`).
     - Sección 12: Capacidad de almacenamiento en m² y m³ (`S12_01_B`, `S12_02_B`).

2. **Módulo de Materiales e Insumos (`MOD_ANUAL_S10_materiales_i`)**:
   - **Dimensiones:** 6,428 filas × 8 columnas.
   - **Granularidad:** Relación de 1 a N (una empresa declara múltiples materias primas o insumos).
   - **Llave de Unión:** `ID`.
   - **Variables principales:** `materia` (descripción del material), `valor_co` (valor de compra en Bs), `valor_uti` (valor de utilización en el proceso productivo en Bs).

---

## 3. Dataset Procesado (`data/processed/`)

El archivo **`dataset_procesado.csv`** es el producto del pipeline de limpieza e ingeniería de características implementado en [`preprocessing/preprocessing.py`](file:///c:/Users/RAQUEL%20SERRANO/OneDrive/Documentos/AprendizajeSupervisadoML/preprocessing/preprocessing.py).

### Características Principales:
- **Dimensiones:** 3,153 filas × 185 columnas.
- **Tasa de Retención:** 100% de las empresas del módulo general (se preserva la representatividad muestral completa).
- **Transformaciones Incorporadas:**
  - **Tratamiento de Centinelas:** Sustitución de valores `99999` (código del INE para imputaciones pendientes o inconsistencias) por `NaN` y acotamiento de negativos a cero.
  - **Agregación de Insumos:** Insumos reducidos a nivel empresa (`n_insumos`, `total_valor_co`, `total_valor_uti`) e imputación de ceros para empresas de servicios y comercio.
  - **Normalización Categórica:** 9 departamentos en mayúsculas (`depto`) y 445 actividades CAEB consolidadas en 14 macrosectores (`sector_macro`).
  - **Escala Logarítmica:** Columnas `log_*` generadas mediante $\log(1 + x)$ para corregir la asimetría positiva de Pareto.
  - **Anti-Leakage:** Descarte de componentes de ingresos de Sección 5 (`S05_01` a `S05_04`) y variables de contabilidad nacional del INE (`VBP`, `VA`, `CI`, `VIPP`).

---

## 4. Políticas de Gobernanza y Seguridad de Datos

1. **Inmutabilidad de los Datos Crudos:**
   - Los archivos en `data/raw/` son de solo lectura. Bajo ninguna circunstancia deben ser modificados, sobrescritos o limpiados directamente in situ.
2. **Confidencialidad Estadística:**
   - Conforme al **Decreto Ley Nº 1405** (Ley del Sistema Nacional de Información Estadística de Bolivia), los microdatos se encuentran estrictamente anonimizados. No contienen nombres comerciales, Números de Identificación Tributaria (NIT) ni coordenadas prediales exactas.
3. **Reproducibilidad:**
   - La regeneración completa del dataset procesado a partir de los datos crudos se ejecuta en cualquier momento mediante:
   ```bash
   python preprocessing/preprocessing.py
   ```

---

## 5. Documentación Relacionada

- [preprocessing/README.md](file:///c:/Users/RAQUEL%20SERRANO/OneDrive/Documentos/AprendizajeSupervisadoML/preprocessing/README.md): Metodología y pasos secuenciales del pipeline.
- [docs/01_analisis_dataset_EAIMCS.md](file:///c:/Users/RAQUEL%20SERRANO/OneDrive/Documentos/AprendizajeSupervisadoML/docs/01_analisis_dataset_EAIMCS.md): Cobertura, tasas de respuesta y diseño muestral.
- [docs/02_diccionario_datos_EAIMCS.md](file:///c:/Users/RAQUEL%20SERRANO/OneDrive/Documentos/AprendizajeSupervisadoML/docs/02_diccionario_datos_EAIMCS.md): Catálogo exhaustivo de variables y reglas contables.
