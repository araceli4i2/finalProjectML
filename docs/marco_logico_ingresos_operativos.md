# Marco Lógico: Estimación de ingresos operativos anuales con aprendizaje supervisado

**Dataset:** Encuesta a la Industria Manufacturera, Comercio y Servicios 2017-2018 (INE Bolivia, catálogo ANDA, BOL-INE-EAIMCS-2017-2018)
**Tipo de proyecto:** Regresión supervisada
**Variable objetivo:** Ingresos operativos anuales (Sección 5 del módulo anual)
**Fecha de elaboración:** 21 de septiembre de 2026
**Horizonte del proyecto:** 21 de septiembre al 30 de noviembre de 2026 (10 semanas)

---

## 1. Introducción

Este documento transforma el **árbol de objetivos** en una ruta estructurada del proyecto de ML mediante la matriz de marco lógico. Cada nivel de la matriz se deriva del árbol:

| Nivel del marco lógico | Origen en el árbol de objetivos |
|---|---|
| **Fin / Impacto** | Fin final (parte superior del árbol) |
| **Propósito / Objetivo** | Objetivo central |
| **Componentes / Productos** | Medios directos |
| **Actividades** | Medios indirectos y acciones necesarias para lograr cada componente |

### Cómo leer las columnas

- **Indicadores objetivamente verificables (IOV):** describen cómo se medirá el logro en términos de **C**antidad, **C**alidad y **T**iempo (CCT).
- **Medios de verificación (MDV):** son las fuentes o documentos donde se comprueba el indicador.
- **Supuestos / siniestros:** condiciones externas que deben cumplirse (supuestos) o eventos adversos que podrían ocurrir (siniestros) y que están fuera del control directo del proyecto.

### Problema y objetivo que originan la matriz

- **Problema central:** los ingresos operativos anuales declarados no cuentan con un valor de referencia derivado de sus variables de estructura productiva (personal, remuneraciones, energía, insumos, inventarios y activos fijos).
- **Objetivo central:** los ingresos operativos anuales declarados cuentan con un valor de referencia derivado de esas variables.

---

## 2. Fin / Impacto

| Nivel | Indicadores (CCT) | Medios de verificación | Supuestos / siniestros |
|---|---|---|---|
| **Fin:** las estadísticas económicas sectoriales se construyen con ingresos declarados contrastados con un valor esperado | **Cantidad:** el 100% de los registros de la muestra de prueba tiene un valor esperado de ingresos y un indicador de discrepancia.<br><br>**Calidad:** los registros atípicos se identifican con un criterio cuantitativo (razón entre ingreso declarado e ingreso estimado).<br><br>**Tiempo:** disponible como prototipo a noviembre de 2026 | Informe final del proyecto<br><br>Listado de registros señalados por el indicador de discrepancia | El INE o los usuarios de los datos consideran el valor de referencia en sus procesos de verificación |

**Explicación:** el fin describe la contribución de largo plazo del proyecto. No se logra solo con este trabajo, pero el proyecto aporta el instrumento (el valor esperado y el indicador de discrepancia) que lo hace posible.

---

## 3. Propósito / Objetivo

| Nivel | Indicadores (CCT) | Medios de verificación | Supuestos / siniestros |
|---|---|---|---|
| **Propósito:** los ingresos operativos anuales declarados cuentan con un valor de referencia derivado de las variables de estructura productiva | **Cantidad:** 1 modelo de regresión seleccionado entre al menos 3 comparados.<br><br>**Calidad:** R² ≥ 0,70 y error porcentual mediano ≤ 25% en el conjunto de prueba.<br><br>**Tiempo:** modelo validado y en funcionamiento (API y dashboard) a noviembre de 2026 | Informe de validación con métricas<br><br>API en funcionamiento<br><br>Repositorio del proyecto | Se obtiene la autorización de acceso a los microdatos<br><br>Las variables de estructura productiva tienen suficiente relación con los ingresos |

**Explicación:** el propósito es el resultado directo que el proyecto debe lograr. Los umbrales de R² y error porcentual son **propuestas iniciales**; conviene reajustarlos después del análisis exploratorio, ya que la concentración de ingresos puede hacer que otra métrica sea más apropiada.

---

## 4. Componentes / Productos

| Componente | Indicadores (CCT) | Medios de verificación | Supuestos / siniestros |
|---|---|---|---|
| **1. Dataset limpio e integrado** (periodo de referencia homologado, ausentes tratados, consistencia verificada) | **Cantidad:** 1 dataset integrado con el 100% de las variables documentadas.<br><br>**Calidad:** sin variables que causen fuga de datos; ausentes tratados y registrados.<br><br>**Tiempo:** hasta el 11 de octubre de 2026 | Carpeta técnica de datos<br><br>Diccionario de variables del dataset<br><br>Script de limpieza | Los microdatos se descargan y autorizan a tiempo<br><br>Proporción de ausentes mayor a la esperada |
| **2. Análisis exploratorio** (correlaciones, ausentes por actividad, distribución de ingresos) | **Cantidad:** 1 informe con al menos 4 análisis (correlaciones, ausentes, distribución, atípicos).<br><br>**Calidad:** los puntos marcados como *(verificar)* en el árbol quedan confirmados o descartados.<br><br>**Tiempo:** hasta el 18 de octubre de 2026 | Informe exploratorio<br><br>Notebook de análisis | Los datos permiten análisis por tipo de actividad |
| **3. Modelos entrenados y validados** | **Cantidad:** al menos 3 modelos (regresión lineal como base, Random Forest, Gradient Boosting).<br><br>**Calidad:** R² ≥ 0,70 en prueba, validación cruzada de 5 particiones, análisis de importancia de variables.<br><br>**Tiempo:** hasta el 15 de noviembre de 2026 | Informe de modelos<br><br>Modelos guardados con versión<br><br>Tabla comparativa de métricas | Volumen de registros suficiente para entrenar y validar<br><br>La concentración de ingresos degrada las métricas |
| **4. API del modelo** | **Cantidad:** 1 API con un servicio de estimación de ingresos.<br><br>**Calidad:** latencia menor a 500 ms por consulta; devuelve valor estimado y razón de discrepancia.<br><br>**Tiempo:** hasta el 22 de noviembre de 2026 | Documentación de la API<br><br>Pruebas de respuesta<br><br>Código en repositorio | Entorno de despliegue disponible<br><br>Restricciones de confidencialidad estadística al exponer el servicio |
| **5. Panel de monitoreo (dashboard)** | **Cantidad:** 1 dashboard con al menos 4 vistas (métricas, error por actividad, atípicos, importancia de variables).<br><br>**Calidad:** actualizado con el modelo vigente.<br><br>**Tiempo:** hasta el 29 de noviembre de 2026 | Dashboard funcionando<br><br>Manual de usuario | Acceso a la herramienta de visualización<br><br>Cambios de alcance durante el desarrollo |

**Explicación:** los componentes son los productos tangibles que el proyecto entrega. Cada uno responde a uno o más medios del árbol de objetivos (ver sección 6).

---

## 5. Actividades

Las duraciones y costos son **referenciales** y deben ajustarse a la realidad del proyecto. Si no hay presupuesto monetario, los costos pueden expresarse en horas de trabajo.

| # | Actividad | Duración y costo | Medios de verificación | Supuestos / siniestros |
|---|---|---|---|---|
| 1 | **Gestión y descarga de microdatos** (registro y solicitud en ANDA) | 1 semana (21-27 sep) · $50 | Constancia de autorización<br><br>Archivos descargados (F1 y módulos) | Demora en la autorización<br><br>Cambios en el acceso al catálogo |
| 2 | **Limpieza e integración** (periodo común, ausentes, consistencia entre secciones) | 2 semanas (28 sep-11 oct) · $600 | Script de limpieza<br><br>Dataset integrado<br><br>Registro de decisiones | Alta proporción de valores ausentes<br><br>Inconsistencias entre secciones |
| 3 | **Análisis exploratorio** (correlaciones, ausentes por tipo de actividad, distribución) | 1 semana (12-18 oct) · $300 | Notebook e informe exploratorio | Relaciones más débiles de lo esperado |
| 4 | **Ingeniería de características** (codificación de actividad, transformaciones, escalado, selección de variables) | 1 semana (19-25 oct) · $300 | Script de preprocesamiento<br><br>Lista final de predictores | Riesgo de fuga de datos al elegir predictores |
| 5 | **Entrenamiento y ajuste de modelos** | 2 semanas (26 oct-8 nov) · $600 | Código de entrenamiento<br><br>Modelos versionados | Recursos de cómputo insuficientes<br><br>Sobreajuste por pocos registros |
| 6 | **Validación** (validación cruzada, prueba, análisis de errores) | 1 semana (9-15 nov) · $300 | Informe de validación<br><br>Tabla de métricas | Métricas por debajo del umbral propuesto |
| 7 | **Desarrollo de la API** | 1 semana (16-22 nov) · $300 | Código de la API<br><br>Pruebas de latencia | Fallas en el entorno de despliegue |
| 8 | **Desarrollo del dashboard** | 2 semanas (16-29 nov) · $500 | Dashboard funcionando | Cambios de alcance<br><br>Limitaciones de la herramienta |
| 9 | **MLOps, pruebas y documentación** (versionado, monitoreo, manual) | 1 semana (23-30 nov) · $300 | Repositorio documentado<br><br>Manual de usuario<br><br>Carpetas técnicas | Cambio de personal<br><br>Políticas de privacidad sobre los datos |
| | **Total** | **10 semanas · $3.250** | | |

---

## 6. Trazabilidad: del árbol de objetivos al marco lógico

Esta tabla muestra cómo cada medio del árbol de objetivos se cubre con un componente y actividades del proyecto.

| Medio del árbol de objetivos | Componente | Actividades |
|---|---|---|
| Incorporar el tipo de actividad como característica de cada empresa | 1, 3 | 2, 4 |
| Considerar de forma simultánea las variables asociadas a los ingresos | 2, 3 | 3, 4, 5 |
| Tratar las secciones que aplican solo a ciertos tipos de empresa | 1, 2 | 2, 3 |
| Homologar los ingresos a un periodo de referencia común | 1 | 2 |
| Contrastar los datos autodeclarados con criterios de consistencia | 1, 4, 5 | 2, 6, 7, 8 |
| Considerar la concentración en la distribución de ingresos | 2, 3 | 3, 5, 6 |
| Delimitar el alcance de las variables internas registradas | 3, 5 | 6, 9 |

---

## 7. Consideraciones para ajustar la matriz

1. **Umbrales de los indicadores.** R² ≥ 0,70, error porcentual mediano ≤ 25% y latencia < 500 ms son propuestas. Deben revisarse tras el análisis exploratorio.
2. **Fechas.** Están calculadas desde el 21 de septiembre de 2026, con cierre el 30 de noviembre. Si la fecha de entrega es otra, las duraciones se ajustan proporcionalmente.
3. **Costos.** Son estimaciones en dólares. Pueden reemplazarse por horas de trabajo si no hay presupuesto monetario.
4. **Fuga de datos (*data leakage*).** Los componentes de los ingresos (por ejemplo, los detalles de la Sección 8) no deben usarse como predictores del total de ingresos. Definir el conjunto de predictores es una decisión crítica de la actividad 4.
5. **Tamaño de muestra.** El diccionario de datos muestra 0 casos en todos los archivos; este valor debe confirmarse al obtener los microdatos, porque condiciona la elección de modelos y las métricas alcanzables.
6. **Acceso a los datos.** El INE solicita registro y autorización para descargar los microdatos; esto afecta el cronograma (actividad 1).
7. **Puntos marcados *(verificar)*.** Los enunciados del árbol que dependen de los datos reales (correlaciones, proporción de ausentes, concentración de ingresos) se confirman en el componente 2 y pueden modificar la matriz.
