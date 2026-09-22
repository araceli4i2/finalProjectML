# Cuadernos de Exploración y Conversión (`notebooks/`)

Este directorio contiene cuadernos interactivos Jupyter Notebook utilizados para tareas iniciales de exploración de datos, pruebas de concepto y conversión de formatos de microdatos.

---

## 1. Estructura del Directorio `notebooks/`

```text
notebooks/
├── README.md              -> Esta guía de uso de cuadernos
└── convertir.ipynb        -> Conversión automatizada de archivos SPSS (.sav) a CSV (.csv)
```

---

## 2. Descripción de Cuadernos

### [convertir.ipynb](file:///c:/Users/RAQUEL%20SERRANO/OneDrive/Documentos/AprendizajeSupervisadoML/notebooks/convertir.ipynb)
- **Propósito:** Automatizar la extracción y exportación de microdatos provenientes del INE en formato IBM SPSS Statistics (`.sav`) hacia formato texto delimitado por comas (`.csv`, codificación UTF-8), garantizando su lectura eficiente y liviana dentro de los pipelines de Python.
- **Librerías utilizadas:** `pandas`, `pyreadstat`.
- **Flujo de operación:**
  1. Identifica los archivos `.sav` de entrada (`MOD_ANUAL_S01-07_12_general_i.sav` y `MOD_ANUAL_S10_materiales_i.sav`).
  2. Ejecuta `pandas.read_spss()`.
  3. Exporta con `to_csv(index=False, encoding='utf-8')` sin alterar los valores originales ni nombres de columnas.

---

## 3. Instrucciones de Ejecución

Para abrir y ejecutar los cuadernos:

1. Asegúrate de tener activo el entorno virtual del proyecto:
   ```bash
   # En Windows:
   .\venv\Scripts\activate
   # En Linux / macOS:
   source venv/bin/activate
   ```
2. Instala el soporte de Jupyter si no está presente:
   ```bash
   pip install jupyter
   ```
3. Inicia Jupyter Lab o Notebook:
   ```bash
   jupyter notebook
   ```
4. Navega a `notebooks/convertir.ipynb` y ejecuta las celdas en orden.

> ⚠️ **Nota:** Los archivos `.csv` ya se encuentran generados en `data/raw/`, por lo que **no es obligatorio** reejecutar este cuaderno para utilizar el pipeline principal de preprocesamiento, entrenamiento o el dashboard.
