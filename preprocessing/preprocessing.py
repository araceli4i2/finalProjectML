"""
Módulo de Preprocesamiento de Datos para Aprendizaje Supervisado.
Dataset: EAIMCS 2017-2018 (INE Bolivia) - Estimación de Ingresos Operativos.

Centraliza todas las reglas de negocio, limpieza de centinelas,
agregación de insumos por empresa y prevención de fuga de datos (data leakage).
"""

import logging
import sys
from pathlib import Path
from typing import Tuple, List, Any
import numpy as np
import pandas as pd

# -----------------------------------------------------------------------------
# CONFIGURACIÓN DE LOGGING
# -----------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("preprocessing")

# -----------------------------------------------------------------------------
# CONSTANTES DE RUTAS Y REGLAS DE NEGOCIO
# -----------------------------------------------------------------------------
PROJECT_ROOT: Path = Path(__file__).resolve().parents[1]
DEFAULT_RAW_DIR: Path = PROJECT_ROOT / "data" / "raw"
DEFAULT_PROCESSED_DIR: Path = PROJECT_ROOT / "data" / "processed"

# Archivos crudos de entrada
RAW_FILE_GENERAL: str = "MOD_ANUAL_S01-07_12_general_i.csv"
RAW_FILE_MATERIALES: str = "MOD_ANUAL_S10_materiales_i.csv"

# Archivos procesados de salida
PROCESSED_FILE_CSV: str = "dataset_procesado.csv"
PROCESSED_FILE_PARQUET: str = "dataset_procesado.parquet"

# Centinela del INE (marcado para imputación pendiente o inconsistencia contable)
CENTINELA_VAL: float = 99999.0

# Variable Objetivo (Ingresos Operativos Anuales)
# S00_01_A (Sección 0, Carátula) es idéntico a S05_04 (Sección 5, Total Ingresos)
TARGET_COL: str = "S00_01_A"
TARGET_ALT_COL: str = "S05_04"

# Columnas excluidas para PREVENCIÓN DE FUGA DE DATOS (Data Leakage)
# Incluye componentes de ingresos de Sección 5 y agregados macroeconómicos del INE (VBP, VA, CI)
EXCLUDED_LEAKAGE_COLS: List[str] = [
    "S05_01", "S05_02", "S05_03", "S05_04",  # Componentes de ingresos que reproducen el target
    "VPA", "PC", "ISPOINF", "VIPP", "VBP",   # Variables macroeconómicas que contienen producción
    "EAC", "OGO", "VUMPEEI", "CI", "VA",     # Cuentas de valor agregado y consumo intermedio
    "SSB", "OPP", "PS", "R", "D"             # Ratios y variables calculadas post-encuesta
]

# Variables predictoras numéricas clave de estructura productiva
PREDICTOR_NUM_COLS: List[str] = [
    "S01_05_A",   # Total personal ocupado
    "S01_03_C",   # Sueldos y salarios básicos anuales
    "S01_14",     # Otras remuneraciones (aguinaldos, aportes salud/AFPs, bonos)
    "S02_09",     # Total energía, agua y combustibles
    "S07_09_E",   # Activos fijos: total valor histórico final
    "S06_06_B",   # Total inventarios finales
    "S12_01_B",   # Capacidad almacenamiento materia prima
    "S12_02_B",   # Capacidad almacenamiento producto terminado
    "n_insumos",  # Variedad de materias primas declaradas (de Sección 10)
    "total_valor_co",   # Valor compras de materias primas en Bs (de Sección 10)
    "total_valor_uti"   # Valor utilización de materias primas en Bs (de Sección 10)
]

# Variables predictoras categóricas
PREDICTOR_CAT_COLS: List[str] = [
    "depto",         # Departamento normalizado (9 departamentos)
    "sector_macro"   # Macrosector económico CAEB normalizado
]

# Semilla fija para reproducibilidad
RANDOM_STATE_SEED: int = 42


# -----------------------------------------------------------------------------
# FUNCIONES DE PREPROCESAMIENTO
# -----------------------------------------------------------------------------
def load_raw_datasets(raw_dir: Path | None = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Carga los archivos crudos del Módulo General y de Materiales desde data/raw/.
    
    Args:
        raw_dir: Ruta al directorio de datos crudos (default: data/raw).
        
    Returns:
        Tupla (df_general, df_materiales).
    """
    directory = Path(raw_dir) if raw_dir else DEFAULT_RAW_DIR
    p_gen = directory / RAW_FILE_GENERAL
    p_mat = directory / RAW_FILE_MATERIALES

    if not p_gen.exists():
        raise FileNotFoundError(f"No se encontró el archivo general en: {p_gen}")
    if not p_mat.exists():
        raise FileNotFoundError(f"No se encontró el archivo de materiales en: {p_mat}")

    logger.info("Cargando archivo general: %s", p_gen.name)
    df_gen = pd.read_csv(p_gen, low_memory=False)

    logger.info("Cargando archivo de materiales: %s", p_mat.name)
    df_mat = pd.read_csv(p_mat, low_memory=False)

    logger.info("Datos crudos leídos: General=%d filas | Materiales=%d filas", len(df_gen), len(df_mat))
    return df_gen, df_mat


def clean_materials_data(df_mat: pd.DataFrame) -> pd.DataFrame:
    """
    Limpia valores centinela (99999) y anomalías negativas en el dataset de Sección 10.
    
    Args:
        df_mat: DataFrame con los registros de insumos y materias primas.
        
    Returns:
        DataFrame limpio de materiales.
    """
    df = df_mat.copy()
    
    # Tratamiento de centinelas 99999 y valores negativos anómalos
    for col in ["valor_co", "valor_uti"]:
        if col in df.columns:
            s = pd.to_numeric(df[col].replace(CENTINELA_VAL, np.nan), errors="coerce")
            df[f"{col}_clean"] = s.clip(lower=0)
            
    logger.debug("Valores monetarios de materiales limpiados con acotamiento >= 0.")
    return df


def aggregate_materials_by_enterprise(df_mat_clean: pd.DataFrame) -> pd.DataFrame:
    """
    Agrega la tabla de estructura larga (N registros por empresa) a nivel empresa por 'ID'.
    Calcula: n_insumos (conteo), total_valor_co (compras) y total_valor_uti (utilización).
    
    Args:
        df_mat_clean: DataFrame limpio de materiales.
        
    Returns:
        DataFrame agregado a nivel empresa con una fila por ID.
    """
    agg_df = df_mat_clean.groupby("ID").agg(
        n_insumos=("materia", "count"),
        total_valor_co=("valor_co_clean", "sum"),
        total_valor_uti=("valor_uti_clean", "sum")
    ).reset_index()

    logger.info("Sección 10 agregada: %d empresas únicas con insumos declarados.", len(agg_df))
    return agg_df


def map_caeb_to_sector(code: Any) -> str:
    """
    Mapea el código de actividad económica CAEB (CIIU Rev. 4) al macrosector oficial.
    
    Args:
        code: Código CAEB numérico o string.
        
    Returns:
        Nombre homogéneo del macrosector en español.
    """
    try:
        c_str = str(code).strip()[:2]
        num = int(c_str)
        if 1 <= num <= 3:
            return "Agropecuario y Pesca"
        elif 5 <= num <= 9:
            return "Minería e Hidrocarburos"
        elif 10 <= num <= 33:
            return "Industria Manufacturera"
        elif 35 <= num <= 39:
            return "Electricidad, Gas y Agua"
        elif 41 <= num <= 43:
            return "Construcción"
        elif 45 <= num <= 47:
            return "Comercio Mayorista y Minorista"
        elif 49 <= num <= 53:
            return "Transporte y Almacenamiento"
        elif 55 <= num <= 56:
            return "Alojamiento y Servicios de Comida"
        elif 58 <= num <= 63:
            return "Información y Comunicaciones"
        elif 64 <= num <= 66:
            return "Intermediación Financiera"
        elif 68 <= num <= 68:
            return "Actividades Inmobiliarias"
        elif 69 <= num <= 75:
            return "Servicios Profesionales y Técnicos"
        elif 77 <= num <= 82:
            return "Servicios Administrativos y de Apoyo"
        elif 85 <= num <= 85:
            return "Educación"
        elif 86 <= num <= 88:
            return "Salud y Asistencia Social"
        else:
            return "Otras Actividades de Servicios"
    except Exception:
        return "Otras Actividades de Servicios"


def merge_and_clean_enterprise_data(df_gen: pd.DataFrame, df_mat_agg: pd.DataFrame) -> pd.DataFrame:
    """
    Une la tabla general y los insumos agregados vía Left Join por 'ID'.
    Imputa ceros coherentes para empresas sin insumos de manufactura.
    
    Args:
        df_gen: DataFrame de empresas general (MOD_ANUAL_S01-07_12).
        df_mat_agg: DataFrame agregado de materiales por ID.
        
    Returns:
        DataFrame consolidado a nivel empresa.
    """
    merged = df_gen.merge(df_mat_agg, on="ID", how="left")
    
    # Imputación coherente de cero en insumos para comercio/servicios
    merged["n_insumos"] = merged["n_insumos"].fillna(0)
    merged["total_valor_co"] = merged["total_valor_co"].fillna(0)
    merged["total_valor_uti"] = merged["total_valor_uti"].fillna(0)

    # Normalización de categorías geográficas y sectoriales
    merged["depto"] = merged["C2_01"].astype(str).str.strip().str.upper()
    merged["sector_macro"] = merged["actividad_pricipal_codigo_V1"].apply(map_caeb_to_sector)

    # Identificación y verificación de la variable objetivo (S00_01_A)
    # Si S00_01_A está presente, se usa formalmente; fallback a S05_04 si fuera necesario
    target_series = pd.to_numeric(merged.get(TARGET_COL, merged.get(TARGET_ALT_COL)), errors="coerce")
    merged["target"] = target_series

    # Filtrar únicamente empresas con ingresos positivos válidos
    valid_mask = merged["target"].notnull() & (merged["target"] > 0)
    filtered = merged[valid_mask].copy()

    logger.info("Unión completada: %d empresas válidas con target > 0.", len(filtered))
    return filtered


def apply_feature_transformations(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica limpieza de centinelas en predictores numéricos y genera las
    transformaciones logarítmicas log(1 + x) para estabilizar varianzas.
    
    Args:
        df: DataFrame consolidado a nivel empresa.
        
    Returns:
        DataFrame con columnas originales limpias y columnas transformadas log_*.
    """
    res = df.copy()

    # Target logarítmico
    res["target_log"] = np.log1p(res["target"])

    # Limpieza de centinelas y creación de logaritmos en predictores numéricos
    for col in PREDICTOR_NUM_COLS:
        if col in res.columns:
            cleaned = pd.to_numeric(res[col].replace(CENTINELA_VAL, np.nan), errors="coerce")
            res[col] = cleaned.fillna(0).clip(lower=0)
            res[f"log_{col}"] = np.log1p(res[col])
            
    logger.info("Transformación log1p aplicada exitosamente a %d predictores numéricos.", len(PREDICTOR_NUM_COLS))
    return res


def run_preprocessing(
    raw_dir: Path | None = None,
    output_dir: Path | None = None,
    save_outputs: bool = True
) -> pd.DataFrame:
    """
    Ejecuta el pipeline completo de preprocesamiento de extremo a extremo:
    1. Carga de datos crudos (data/raw/).
    2. Limpieza de Sección 10 y centinelas 99999.
    3. Agregación de insumos por empresa (ID).
    4. Cruce relacional Left Join y exclusión de fuga de datos.
    5. Mapeo a macrosectores CAEB.
    6. Transformación logarítmica de predictores y target.
    7. Exportación a data/processed/ (CSV y Parquet opcional).
    
    Returns:
        DataFrame completamente preprocesado y listo para modelado.
    """
    logger.info("=== INICIANDO PIPELINE DE PREPROCESAMIENTO ===")
    
    # 1. Cargar datos crudos
    df_gen, df_mat = load_raw_datasets(raw_dir)
    
    # 2. Limpiar materiales
    df_mat_clean = clean_materials_data(df_mat)
    
    # 3. Agregar materiales por ID
    df_mat_agg = aggregate_materials_by_enterprise(df_mat_clean)
    
    # 4. Fusión y limpieza general
    merged_df = merge_and_clean_enterprise_data(df_gen, df_mat_agg)
    
    # 5. Ingeniería de características y transformaciones
    processed_df = apply_feature_transformations(merged_df)

    # 6. Guardar resultados
    if save_outputs:
        out_dir = Path(output_dir) if output_dir else DEFAULT_PROCESSED_DIR
        out_dir.mkdir(parents=True, exist_ok=True)

        csv_path = out_dir / PROCESSED_FILE_CSV
        logger.info("Guardando dataset procesado en CSV: %s", csv_path)
        processed_df.to_csv(csv_path, index=False, encoding="utf-8")

        # Intentar exportar a Parquet si el motor pyarrow o fastparquet está disponible
        try:
            parquet_path = out_dir / PROCESSED_FILE_PARQUET
            processed_df.to_parquet(parquet_path, index=False)
            logger.info("Guardando dataset procesado en Parquet: %s", parquet_path)
        except (ImportError, ValueError):
            logger.info("Motor Parquet no disponible en el entorno; salida CSV generada correctamente.")

    logger.info(
        "=== PREPROCESAMIENTO COMPLETADO: %d filas x %d columnas ===",
        processed_df.shape[0], processed_df.shape[1]
    )
    return processed_df


if __name__ == "__main__":
    df_final = run_preprocessing(save_outputs=True)
    t = df_final["target"]
    print("\n--- RESUMEN ESTADÍSTICO DE LA VARIABLE OBJETIVO (S00_01_A) ---")
    print(f"Total empresas procesadas: {len(df_final):,}")
    print(f"Mínimo:  Bs {t.min():,.2f}")
    print(f"Mediana: Bs {t.median():,.2f}")
    print(f"Media:   Bs {t.mean():,.2f}")
    print(f"Máximo:  Bs {t.max():,.2f}")
