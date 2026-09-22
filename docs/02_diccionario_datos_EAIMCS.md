# Diccionario de Datos: EAIMCS 2017-2018

Fuente: Catálogo ANDA (INE Bolivia), estudio BOL-INE-EAIMCS-2017-2018.
Diccionario de datos oficial: https://anda.ine.gob.bo/index.php/catalog/252/data-dictionary

Este documento cubre únicamente los dos archivos usados en el proyecto:
1. **MODULO_ANUAL_Secc_1-7_y_12** (`MOD_ANUAL_S1-07_12_general`) — 152 variables, nivel empresa.
2. **M_ANUAL_Sec_10_MATERIAS_PRIMAS** (`MOD_ANUAL_S10_materiales`) — 8 variables, nivel ítem/insumo.

> Nota general de tipo de dato: todas las variables monetarias están expresadas en **Bolivianos (Bs)**, gestión 2017 (o el cierre fiscal correspondiente a la actividad). Las variables `_E` o con sufijo "especifique" son texto libre (abierto) asociado a una opción "otros". Recordar que valores como **99999** pueden representar datos imputados/pendientes según el proceso de consistencia del INE (ver documento de análisis).

---

## 1. Archivo: MODULO_ANUAL_Secc_1-7_y_12

Incluye la carátula (identificación de la empresa) y las secciones 0 a 7 y 12 del Módulo Anual.

### Carátula / Identificación

| Variable | Descripción |
|---|---|
| `ID` | Identificador único de la empresa (llave de unión con otros archivos) |
| `C2_01` | Departamento |
| `actividad_pricipal_codigo_V1` | Código CAEB de la Actividad Principal |
| `actividad1_codigo_v1` | Código CAEB de la Actividad Secundaria |
| `actividad2_codigo_v1` | Código CAEB de Otra Actividad |

### Sección 0 – Ingresos operativos por tipo de cierre contable

| Variable | Descripción |
|---|---|
| `S00_01_A` | Valor TOTAL de Ingresos Operativos, en Bs (año calendario enero–diciembre 2017) |

### Sección 1 – Personal ocupado, sueldos y salarios y otras remuneraciones

| Variable | Descripción |
|---|---|
| `S01_01_A` | N° total de personas (hombres y mujeres) – Personal remunerado permanente |
| `S01_01_B` | N° de mujeres – Personal remunerado permanente |
| `S01_01_C` | Sueldos y salarios básicos anuales – Personal remunerado permanente |
| `S01_02_A` | N° total de personas – Personal temporal o eventual |
| `S01_02_B` | N° de mujeres – Personal temporal o eventual |
| `S01_02_C` | Sueldos y salarios básicos anuales – Personal temporal o eventual |
| `S01_03_A` | N° total de personas – TOTAL Personal Remunerado |
| `S01_03_B` | N° de mujeres – TOTAL Personal Remunerado |
| `S01_03_C` | Sueldos y salarios básicos anuales – TOTAL Personal Remunerado |
| `S01_04_A` | N° total de personas – Personal NO Remunerado |
| `S01_04_B` | N° de mujeres – Personal NO Remunerado |
| `S01_05_A` | N° total de personas – TOTAL Personal Ocupado |
| `S01_05_B` | N° de mujeres – TOTAL Personal Ocupado |
| `S01_06` | Aguinaldo |
| `S01_07` | Pagos en especie (alimentos, prendas de vestir, transporte u otros) |
| `S01_08` | Indemnizaciones o beneficios sociales de la gestión |
| `S01_09` | Bono de producción y horas extras |
| `S01_10` | Otros pagos al personal (bono de antigüedad, primas, comisiones, etc.) |
| `S01_10E` | Especifique (si anotó otros pagos al personal) — texto libre |
| `S01_11` | Aporte Patronal al Seguro de Salud (público o privado) |
| `S01_12` | Aporte Patronal a las AFP's |
| `S01_13` | Otros aportes patronales (pro vivienda, solidario, etc.) |
| `S01_13E` | Especifique (si anotó otros aportes) — texto libre |
| `S01_14` | TOTAL Otras Remuneraciones |

### Sección 2 – Energía, agua y combustible

| Variable | Descripción |
|---|---|
| `S02_01` | Energía eléctrica (incluye tasa de aseo y recojo de basura) |
| `S02_02` | Agua |
| `S02_03` | Gas natural (por tubería) |
| `S02_04` | Diésel oil |
| `S02_05` | Gasolina |
| `S02_06` | Gas licuado de petróleo (GLP) |
| `S02_07` | Gas natural vehicular (GNV) |
| `S02_08` | Otros combustibles y lubricantes (aceites, grasas, otros carburantes) |
| `S02_08E` | Especifique (si anotó otros) — texto libre |
| `S02_09` | TOTAL Energía, agua y combustibles |

### Sección 3 – Materias primas, materiales, envases, embalajes y mercaderías (resumen)

| Variable | Descripción |
|---|---|
| `S03_01` | Compra de materias primas, envases y embalajes para industria y materiales para servicios |
| `S03_02` | Compra de mercadería para reventa |
| `S03_03` | TOTAL compras de materias, materiales, envases, embalajes y mercadería |

### Sección 4 – Otros gastos operativos

| Variable | Descripción |
|---|---|
| `S04_01` | Pagos por trabajos de fabricación realizados por terceros |
| `S04_02` | Reparación y mantenimiento (por terceros) |
| `S04_03` | Alquiler de activos fijos (incluye leasing operativo) |
| `S04_04` | Repuestos y accesorios (incluye ferretería) |
| `S04_05` | Ropa de trabajo e indumentaria de seguridad |
| `S04_06` | Honorarios a profesionales independientes |
| `S04_07` | Servicios de internet |
| `S04_08` | Servicios de telefonía y otros servicios de comunicación |
| `S04_09` | Materiales de oficina |
| `S04_10` | Fletes por transporte prestado por terceros (interior del país) |
| `S04_11` | Gastos por representación, pasajes y viáticos |
| `S04_12` | Gastos por exportación (fletes, seguros, estibaje) |
| `S04_13` | Gastos por importación (aranceles, fletes, seguros, estibaje) |
| `S04_14` | Publicidad, propaganda y relaciones públicas |
| `S04_15` | Primas por seguro (excluye seguro de personas) |
| `S04_16` | Comisiones pagadas a terceros por comercialización |
| `S04_17` | Capacitación al personal |
| `S04_18` | Servicio de seguridad por terceros |
| `S04_19` | Otros gastos operativos (excluye financieros, impuestos, depreciaciones) |
| `S04_19E` | Especifique (si anotó otros) — texto libre |
| `S04_20` | TOTAL Otros gastos operativos |
| `S04_21A` | % del gasto en reparación y mantenimiento dirigido a Edificaciones |
| `S04_21B` | % del gasto en reparación y mantenimiento dirigido a Maquinaria y equipo |
| `S04_21C` | % del gasto en reparación y mantenimiento dirigido a Vehículos y equipo de transporte |
| `S04_21D` | % del gasto en reparación y mantenimiento dirigido a Equipos de computación y comunicación |
| `S04_21E` | % del gasto en reparación y mantenimiento dirigido a Otros activos |
| `S04_21F` | TOTAL % del gasto en reparación y mantenimiento |
| `S04_22A` | % del gasto por alquileres dirigido a Edificaciones |
| `S04_22B` | % del gasto por alquileres dirigido a Maquinaria y equipo |
| `S04_22C` | % del gasto por alquileres dirigido a Vehículos y equipo de transporte |
| `S04_22D` | % del gasto por alquileres dirigido a Equipos de computación y comunicación |
| `S04_22E` | % del gasto por alquileres dirigido a Otros activos |
| `S04_22F` | TOTAL % del gasto por alquileres |

### Sección 5 – Ingresos operativos ⭐ (variable objetivo del proyecto)

| Variable | Descripción |
|---|---|
| `S05_01` | Ingresos por venta de productos fabricados |
| `S05_02` | Ingresos por venta de mercadería |
| `S05_03` | Ingresos por servicios prestados y otros ingresos no financieros |
| `S05_04` | **TOTAL Ingresos** (variable objetivo candidata principal para la regresión) |

### Sección 6 – Inventarios

| Variable | Descripción |
|---|---|
| `S06_01_A` | Inventario inicial de productos en proceso (solo industria) |
| `S06_01_B` | Inventario final de productos en proceso (solo industria) |
| `S06_02_A` | Inventario inicial de productos fabricados terminados (solo industria) |
| `S06_02_B` | Inventario final de productos fabricados terminados (solo industria) |
| `S06_03_A` | Inventario inicial de mercadería (sin transformación) |
| `S06_03_B` | Inventario final de mercadería (sin transformación) |
| `S06_04_A` | Inventario inicial de materias primas, materiales auxiliares, envases y embalajes |
| `S06_04_B` | Inventario final de materias primas, materiales auxiliares, envases y embalajes |
| `S06_05_A` | Inventario inicial de materiales para la generación de servicios |
| `S06_05_B` | Inventario final de materiales para la generación de servicios |
| `S06_06_A` | TOTAL inventarios iniciales |
| `S06_06_B` | TOTAL inventarios finales |

### Sección 7 – Activos fijos

Para cada tipo de activo se registran 6 componentes: **A** = valor histórico inicial, **B** = compras, **C** = ventas/retiros, **D** = actualización y ajustes, **E** = valor histórico final, **F** = depreciación de la gestión.

| Tipo de activo | Variables |
|---|---|
| Edificios y construcciones (incluye instalaciones técnicas) | `S07_01_A` … `S07_01_F` |
| Maquinaria y equipo | `S07_02_A` … `S07_02_F` |
| Vehículos y equipo de transporte | `S07_03_A` … `S07_03_F` |
| Muebles y enseres | `S07_04_A` … `S07_04_F` |
| Equipo de computación y comunicación | `S07_05_A` … `S07_05_F` |
| Herramientas | `S07_06_A` … `S07_06_F` |
| Terrenos | `S07_07_A` … `S07_07_E` (sin depreciación, F no aplica) |
| Otros activos fijos (software, franquicias, etc.) | `S07_08_A` … `S07_08_F`, más `S07_08_F1` (descripción texto libre) |
| **TOTALES** | `S07_09_A` (Total valor histórico inicial), `S07_09_B` (Total compras), `S07_09_C` (Total ventas/retiros), `S07_09_D` (Total actualización/ajustes), `S07_09_E` (Total valor histórico final), `S07_09_F` (Total depreciación de la gestión) |

### Sección 12 – Capacidad de almacenamiento

| Variable | Descripción |
|---|---|
| `S12_01_A` | (Automático) Descripción principal Materia Prima |
| `S12_01_B` | Cantidad máxima de MATERIA PRIMA que pudo haber almacenado al 31/dic/2017 |
| `S12_01_C` | Unidad de medida (materia prima) |
| `S12_02_A` | (Automático) Descripción principal Producto |
| `S12_02_B` | Cantidad máxima de PRODUCTO que pudo haber almacenado al 31/dic/2017 |
| `S12_02_C` | Unidad de medida (producto) |

**Total variables en este archivo: 152**

---

## 2. Archivo: M_ANUAL_Sec_10_MATERIAS_PRIMAS

Detalle (multi-registro por empresa) de materias primas, materiales, envases, embalajes e insumos, ordenados por importancia según valor de utilización o compra. **No** incluye desagregación por marca ni tamaño de envase.

| Variable | Descripción |
|---|---|
| `ID` | Identificador de la empresa (llave de unión con MODULO_ANUAL_Secc_1-7_y_12) |
| `materia` | Descripción de la materia prima, material, envase, embalaje o insumo (texto libre) |
| `codigocodif_V1` | Código CCP (Clasificación Central de Productos) asignado |
| `unidad` | Unidad de medida (de compra y de utilización) |
| `cantidad_co` | Cantidad comprada en la gestión (en la unidad de medida indicada) |
| `valor_co` | Valor de compras en Bs (gestión 2017) |
| `cantidad_uti` | Cantidad utilizada en la gestión (en la unidad de medida indicada) |
| `valor_uti` | Valor de utilización en Bs (gestión 2017) |

**Total variables en este archivo: 8**

> Este archivo es de **estructura larga**: cada empresa (`ID`) puede aparecer en varias filas (una por cada insumo declarado, en orden de importancia). Para incorporarlo al modelo a nivel empresa, se recomienda agregarlo por `ID`, por ejemplo:
> - `n_insumos` = conteo de filas por `ID`
> - `valor_compras_total` = suma de `valor_co` por `ID`
> - `valor_utilizacion_total` = suma de `valor_uti` por `ID`
> - `principal_insumo` = descripción/código del insumo con mayor `valor_uti` (primer registro, ya que vienen ordenados por importancia)

---

## 3. Relación entre archivos

```
MODULO_ANUAL_Secc_1-7_y_12 (1 fila = 1 empresa)
        │
        │  ID (llave primaria/foránea)
        ▼
M_ANUAL_Sec_10_MATERIAS_PRIMAS (N filas = N insumos por empresa)
```

## 4. Notas de calidad para el modelado
- Verificar y tratar como *missing* los valores centinela **99999** (usados por el INE cuando la identidad `Utilización = Compras + Inventario inicial − Inventario final` no se cumplía o el dato faltaba).
- Las variables tipo "especifique" (`S01_10E`, `S01_13E`, `S02_08E`, `S04_19E`, `S07_08_F1`) son texto libre; no usar directamente en un modelo numérico sin categorizar.
- Los códigos CAEB (actividad económica) y CCP (productos/insumos) requieren su tabla de equivalencias oficial (no incluida en el diccionario de datos) si se desea decodificarlos a texto legible.
