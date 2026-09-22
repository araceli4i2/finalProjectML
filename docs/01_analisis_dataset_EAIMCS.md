# Análisis del Dataset: EAIMCS 2017-2018 (Bolivia)

## Fuente
- **Catálogo ANDA (INE Bolivia):** https://anda.ine.gob.bo/index.php/catalog/252
- **ID del estudio:** BOL-INE-EAIMCS-2017-2018
- **Nombre completo:** Encuesta a la Industria Manufacturera, Comercio y Servicios, 2017-2018
- **Institución productora:** Instituto Nacional de Estadística (INE) de Bolivia, Dirección de Estadísticas e Indicadores Económicos y Sociales (DEIES), Unidad de Estadísticas e Indicadores Económicos (UEIE)
- **Financiador:** Banco Mundial (BM)
- **Fecha de publicación en ANDA:** 30/09/2025 (última modificación registrada: abril 2026)

## 1. Objetivo de la encuesta
La EAIMCS busca generar información estructural y coyuntural para caracterizar y cuantificar la producción de empresas medianas y grandes de los sectores **industria manufacturera, comercio y servicios**, a nivel nacional y departamental, sirviendo de insumo para las Cuentas Nacionales de Bolivia.

Objetivos específicos relevantes para nuestro proyecto:
- Determinar la composición de la producción de bienes y servicios, compra y consumo de materias primas/materiales, ingresos por ventas/servicios, personal ocupado, salarios, activos fijos e inventarios.
- Esta es la razón por la que el dataset contiene, en un mismo módulo, casi todas las variables necesarias para un modelo de predicción de ingresos operativos (personal, sueldos, energía, activos fijos, inventarios, capacidad de almacenamiento, actividad económica).

## 2. Cobertura, universo y unidad de análisis
- **Cobertura geográfica:** Nacional, los 9 departamentos de Bolivia (Chuquisaca, La Paz, Cochabamba, Oruro, Potosí, Tarija, Santa Cruz, Beni, Pando).
- **Universo:** Empresas **medianas y grandes** (no incluye microempresas ni empresas pequeñas).
- **Unidad de observación/análisis:** La Empresa (categorizada como grande o mediana) y el Establecimiento Económico.
- **Nivel mínimo de desagregación:** Departamento × actividad económica.

## 3. Diseño muestral (clave para interpretar el dataset)
- No es una muestra probabilística clásica con factor de expansión; es una **muestra dirigida** basada en un **directorio de empresas** (no aplica factor de expansión).
- El directorio se construyó a partir de:
  1. Base Empresarial Vigente (BEV) 2016 de FUNDEMPRESA (Registro Comercial), usando **ingreso operativo anual** como proxy de tamaño (ya que la BEV no tenía personal ocupado ni patrimonio neto).
  2. Empresas de Cuentas Nacionales no presentes en FUNDEMPRESA (554).
  3. Empresas de la ETIM no presentes en FUNDEMPRESA (128).
  - **Total del directorio:** 10.044 empresas.
- Umbrales de clasificación de tamaño (usados para decidir qué empresas entraron al marco):

| Sector | Mediana empresa (Bs) | Gran empresa (Bs) |
|---|---|---|
| Producción | 2.450.001 – 35.000.000 | ≥ 35.000.001 |
| Servicios | 1.750.001 – 28.000.000 | ≥ 28.000.001 |

- **Distribución del marco por departamento:** La Paz (2.669) y Santa Cruz (3.846) concentran la mayoría de empresas; Pando (109) y Beni (193) las de menor cantidad.

### Tasa de respuesta (importante para el análisis de sesgo del dataset)
- **Módulo Anual:** tasa de no respuesta ≈ 55% en número de empresas, pero solo ≈ 5% en términos de ingresos operativos agregados (las empresas que no respondieron son en su mayoría de menor tamaño relativo). Esto implica que el dataset representa muy bien el ingreso operativo agregado del universo, aunque con menos observaciones (empresas) de las que existen en el directorio.
- **Módulo Trimestral:** de las mismas 10.044 empresas, respondieron 1.808 (26%). Por sector: industria manufacturera 14%, comercio 27%, servicios 28%.
- **Implicación práctica:** el `MODULO_ANUAL_Secc_1-7_y_12` (que usaremos) tiene mejor cobertura que los módulos trimestrales; es la base más sólida para un modelo de regresión de ingresos anuales.

## 4. Periodo de referencia
- El **Módulo Anual** usa el ejercicio contable **2017**, pero el cierre fiscal varía según actividad:
  - 31 de diciembre de 2017 → Comercio y Servicios.
  - 31 de marzo de 2018 → Industria manufacturera.
  - 30 de junio de 2018 → Agroindustria.
- El **Módulo Trimestral** cubre los 4 trimestres de 2018 (no lo usaremos en este proyecto, salvo mención).
- **Recolección:** boleta virtual (autorelevamiento web) en dos fases: sep-nov 2018 y ene-abr 2019. Fue el primer levantamiento con boleta 100% en línea del INE.

## 5. Procesamiento y calidad del dato (a tener en cuenta antes de modelar)
El INE aplicó reglas de consistencia e imputación que afectan directamente los valores que encontraremos en las variables monetarias:

- **Identidad contable de la Sección 3 (materiales/insumos):**
  `Utilización = Compras + Inventario inicial − Inventario final`
  Si no se cumplía o había dato faltante, el campo se marcó con el código **99999** para imputación posterior. **Recomendación:** al leer `M_ANUAL_Sec_10_MATERIAS_PRIMAS`, tratar el valor 99999 (y valores atípicamente altos similares) como *missing*, no como dato real.
- **Ajuste de la Sección 5 (Ingresos Operativos):** el ingreso operativo de la BEV se usó como "techo" de validación; el nuevo total no podía variar en más de ±20% respecto al de la BEV. Si el detalle sumaba menos que el total declarado, se creó una categoría "otro" para cuadrar. Esto significa que la variable objetivo (ingresos operativos) ya pasó por un proceso de validación cruzada con una fuente administrativa externa, lo cual **aumenta su confiabilidad para usarla como variable dependiente**.
- **Detección de outliers:** se usó rango intercuartílico (IQR) sobre razones macroeconómicas (CI/VBP, R/VBP, Costo de ventas/Ingreso por ventas, etc.), con revisión manual e imputación de los que persistían como atípicos.
- **Codificación:** las variables abiertas (descripciones de materia prima, productos, servicios) fueron codificadas con la Clasificación Central de Productos (CCP) mediante codificación asistida; 110.895 registros codificados en total.

**Conclusión para el proyecto:** los datos ya vienen depurados/validados por el INE, pero aun así conviene revisar valores centinela (99999), outliers residuales y campos vacíos antes de entrenar el modelo.

## 6. Archivos de datos disponibles y cuáles usaremos
La encuesta se distribuye en 10 archivos (tablas) relacionadas por un identificador de empresa (`ID`):

| Archivo | Contenido | Variables | Uso en el proyecto |
|---|---|---|---|
| **MODULO_ANUAL_Secc_1-7_y_12** | Carátula + identificación + Secciones 0 a 7 y 12 del módulo anual (personal, sueldos, energía, materiales, otros gastos, ingresos, inventarios, activos fijos, capacidad de almacenamiento) | 152 | **Sí – tabla principal (nivel empresa)** |
| M_TRIMESTRAL_Sec_5_Productos | Top 10 productos trimestrales | 33 | No |
| MODULO_ANUAL_Secc_8_SERVICIOS | Detalle de servicios prestados | 4 | No |
| MODULO_ANUAL_SecC_9_MERCADERIAS | Detalle de mercaderías comercializadas | 7 | No |
| **M_ANUAL_Sec_10_MATERIAS_PRIMAS** | Detalle de materias primas/materiales/insumos (multi-registro por empresa) | 8 | **Sí – tabla secundaria (nivel ítem/insumo)** |
| M_ANUAL_Sec_11_PRODUCTOS | Detalle de productos y subproductos | 9 | No |
| M_TRIMESTRAL_Sec_1_Energias | Energía/agua/combustibles trimestral | 17 | No |
| M_TRIMESTRAL_Sec_2_Servicios | Servicios trimestrales | 21 | No |
| M_TRIMESTRAL_Sec_3_Mercaderias | Mercaderías trimestrales | 21 | No |
| M_TRIMESTRAL_Sec_4_Materias | Materias primas trimestrales | 33 | No |

> Nota: en el catálogo, el archivo de la Sección 10 aparece nombrado **M_ANUAL_Sec_10_MATERIAS_PRIMAS**, equivalente al `MOD_ANUAL_S10_materiales` mencionado en el proyecto.

## 7. Relación entre las dos tablas que usaremos
- `MODULO_ANUAL_Secc_1-7_y_12` está a **nivel de empresa** (una fila = una empresa), con el `ID` como llave.
- `M_ANUAL_Sec_10_MATERIAS_PRIMAS` está a **nivel de ítem** (una empresa puede tener varias filas, una por cada materia prima/material/insumo declarado, en orden de importancia), y se vincula a la tabla anterior mediante el mismo `ID`.
- Para usar la Sección 10 en un modelo de regresión a nivel empresa, será necesario **agregar** (sumar/contar/promediar) sus variables por `ID` antes de unirla al módulo anual (por ejemplo: número de insumos distintos, valor total de compras, valor total de utilización, principal insumo declarado, etc.).

## 8. Relevancia directa para el proyecto: "Predicción de ingresos operativos anuales de la empresa" (Regresión)

| Insumo requerido por el proyecto | Dónde está en el dataset |
|---|---|
| **Variable objetivo:** Ingresos operativos (Sección 5) | `S05_01` a `S05_04` en MODULO_ANUAL_Secc_1-7_y_12 (ventas de productos, mercadería, servicios y TOTAL ingresos); también `S00_01_A` (ingreso total por tipo de cierre contable, carátula) |
| Personal ocupado | Sección 1: `S01_01_A` a `S01_05_B` |
| Sueldos y salarios | Sección 1: `S01_01_C`, `S01_02_C`, `S01_03_C`, más otras remuneraciones `S01_06`–`S01_14` |
| Energía y combustible | Sección 2: `S02_01` a `S02_09` |
| Activos fijos | Sección 7: `S07_01_*` a `S07_09_*` (por tipo de activo: edificaciones, maquinaria, vehículos, muebles, equipo de cómputo, herramientas, terrenos, otros) |
| Inventarios | Sección 6: `S06_01_*` a `S06_06_*` |
| Capacidad de almacenamiento | Sección 12: `S12_01_*` (materia prima) y `S12_02_*` (producto) |
| Tipo de actividad | Carátula: `actividad_pricipal_codigo_V1`, `actividad1_codigo_v1`, `actividad2_codigo_v1` (códigos CAEB) y `C2_01` (Departamento) |
| Materiales/materias primas (complemento) | Archivo `M_ANUAL_Sec_10_MATERIAS_PRIMAS`: cantidades y valores de compra/utilización de insumos, agregables por empresa |

Con esto, el dataset cubre **todas las categorías de variables predictoras** planteadas en el proyecto, además de la variable objetivo, sin necesidad de fuentes externas adicionales (salvo eventualmente un catálogo CAEB/CCP para decodificar actividades y productos, si se desea usar como texto en vez de código).

## 9. Limitaciones a considerar en el análisis/modelado
1. **Tamaño de muestra reducido y sesgado a empresas grandes/medianas** (no aplica a mipymes ni microempresas).
2. **No hay factor de expansión** → no se pueden generar estimaciones poblacionales oficiales, solo modelos descriptivos/predictivos sobre las empresas encuestadas.
3. **Corte transversal (2017/2018)**: no hay serie temporal por empresa, por lo que el proyecto de regresión debe entenderse como predicción "cross-section" (a partir de las características de la empresa en un año dado), no una serie de tiempo.
4. **Valores centinela (99999)** en variables ajustadas de la Sección 3 y potencialmente en Sección 10: deben tratarse como missing.
5. **Confidencialidad:** los microdatos publicados están anonimizados (Decreto Ley 1405); no contienen razón social, NIT ni datos identificatorios directos.
6. **Condiciones de uso/citación:** los datos son de uso público con fines estadísticos, pero se debe citar al INE como fuente y no se pueden usar con fines tributarios, judiciales o administrativos. Los resultados del análisis no comprometen al INE y son responsabilidad exclusiva del usuario.

## 10. Referencias
- Descripción del estudio: https://anda.ine.gob.bo/index.php/catalog/252/study-description
- Diccionario de datos (catálogo completo de archivos): https://anda.ine.gob.bo/index.php/catalog/252/data-dictionary
- Obtención de microdatos: https://anda.ine.gob.bo/index.php/catalog/252/get-microdata
