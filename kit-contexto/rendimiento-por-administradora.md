# Rendimiento y comisiones de AFP en Colombia

Investigacion para el proyecto Jubilo. Fecha de consulta: 18 de septiembre de 2026.

## Serie oficial de la Superfinanciera (calculada el 2026-09-18)

Esta seccion reemplaza en la practica a la investigacion de prensa que aparece mas abajo. Se construyo desde el dato primario diario de la Superintendencia Financiera de Colombia (SFC), publicado en datos.gov.co, para los 4 portafolios de pensiones obligatorias de las 4 AFP privadas.

### Tabla: rentabilidad anualizada del fondo, nominal y real

| Portafolio | AFP | Nominal periodo completo | Real periodo completo | Nominal 5 anos | Real 5 anos | Desde | Hasta | Obs. mensuales |
|---|---|---|---|---|---|---|---|---|
| Conservador | Colfondos | 8,02% | 2,04% | 8,78% | 0,80% | 2015-01-31 | 2026-08-31 | 140 |
| Conservador | Porvenir | 8,09% | 2,11% | 8,87% | 0,88% | 2015-01-31 | 2026-08-31 | 140 |
| Conservador | Proteccion | 7,89% | 1,93% | 8,58% | 0,62% | 2015-01-31 | 2026-08-31 | 140 |
| Conservador | Skandia | 7,96% | 1,99% | 8,34% | 0,39% | 2015-01-31 | 2026-08-31 | 140 |
| Moderado | Colfondos | 8,25% | 2,27% | 7,40% | -0,47% | 2015-01-31 | 2026-08-31 | 140 |
| Moderado | Porvenir | 9,30% | 3,25% | 8,87% | 0,88% | 2015-01-31 | 2026-08-31 | 140 |
| Moderado | Proteccion | 8,99% | 2,96% | 9,04% | 1,04% | 2015-01-31 | 2026-08-31 | 140 |
| Moderado | Skandia | 8,87% | 2,85% | 8,09% | 0,16% | 2015-01-31 | 2026-08-31 | 140 |
| Mayor riesgo | Colfondos | 10,23% | 4,13% | 10,07% | 2,00% | 2015-01-31 | 2026-08-31 | 140 |
| Mayor riesgo | Porvenir | 9,39% | 3,34% | 10,34% | 2,25% | 2015-01-31 | 2026-08-31 | 140 |
| Mayor riesgo | Proteccion | 9,36% | 3,31% | 10,29% | 2,20% | 2015-01-31 | 2026-08-31 | 140 |
| Mayor riesgo | Skandia | 9,77% | 3,70% | 10,47% | 2,37% | 2015-01-31 | 2026-08-31 | 140 |
| Retiro programado | Colfondos | 8,35% | 2,36% | 8,56% | 0,60% | 2015-01-31 | 2026-08-31 | 140 |
| Retiro programado | Porvenir | 8,95% | 2,92% | 9,93% | 1,87% | 2015-01-31 | 2026-08-31 | 140 |
| Retiro programado | Proteccion | 8,50% | 2,50% | 9,09% | 1,09% | 2015-01-31 | 2026-08-31 | 140 |
| Retiro programado | Skandia | 8,42% | 2,42% | 8,73% | 0,76% | 2015-01-31 | 2026-08-31 | 140 |
| Alternativo (solo Skandia) | Skandia | 8,33% | 2,34% | 6,88% | -0,95% | 2015-01-31 | 2026-08-31 | 140 |

Inflacion usada como referencia, anualizada sobre los mismos periodos: **5,85%** para el periodo completo (ene-2015 a ago-2026) y **7,91%** para los ultimos 5 anos (ago-2021 a ago-2026).

El renglon "Alternativo (solo Skandia)" es el Fondo Alternativo de Skandia, que existe dentro de los recursos de seguridad social administrados por esa AFP pero no tiene equivalente en las otras tres. No es comparable de forma horizontal, se deja solo por completitud.

### Metodologia exacta

**Fuente.** Dataset `hds9-4524` de datos.gov.co, "Valoracion de los Tipos de Fondos de Pensiones Obligatorias y Cesantias", de la SFC. Cobertura diaria del 2015-01-01 al 2026-09-16.

**Campo usado.** El dataset **no publica el valor de la unidad** como un renglon propio. Lo que hay es el renglon `cod_renglon = 300` ("valor del fondo al cierre del dia") en dos columnas: `NUMERO DE UNIDADES` y `VALOR EN PESOS $`. El valor de la unidad se derivo como:

```
valor_unidad = (valor del fondo en pesos al cierre) / (numero de unidades al cierre)
```

Ejemplo de control: Porvenir Moderado pasa de 33.149,39 pesos por unidad el 2015-01-31 a 92.798,83 el 2026-08-31.

Existe un renglon alterno `305`, que es una segunda variante del mismo cierre del dia. La diferencia contra el `300` es del orden de 0,02% del valor del fondo, es decir irrelevante para una rentabilidad anualizada. Se uso el `300`.

**Frecuencia.** De la serie diaria se tomo el **ultimo dia disponible de cada mes**. Se trabaja a cierre de mes porque el IPC es mensual: asi la rentabilidad nominal y la real cubren exactamente el mismo periodo, sin desfases.

**Anualizacion.** Geometrica, punto a punto, con dias calendario:

```
nominal_anual = (unidad_final / unidad_inicial) ^ (365,25 / dias) - 1
```

Para los ultimos 5 anos se tomo el cierre de mes 60 meses antes del final (ago-2021 a ago-2026).

**IPC.** Indice de Precios al Consumidor de Colombia, serie mensual, **base diciembre 2018 = 100**, obtenida por API del Banco de la Republica (servicio `estadisticas-economicas-back`, `idMenu=100002`), que publica la serie con fuente DANE. Ultimo dato disponible: ago-2026, indice 160,42. No se consiguio una API abierta del DANE con la serie nacional del IPC: datos.gov.co solo expone IPC de Cali y series municipales viejas. Se uso por tanto la publicacion de Banrep del mismo indice DANE, no una cifra estimada.

**Conversion a real.** Fisher, con la inflacion anualizada del mismo periodo:

```
real = (1 + nominal) / (1 + inflacion_anualizada) - 1
inflacion_anualizada = (IPC_final / IPC_inicial) ^ (365,25 / dias) - 1
```

**Fecha de corte final.** 2026-08-31 y no 2026-09-16, aunque la SFC ya tiene datos de septiembre, porque agosto es el ultimo mes con IPC publicado. Cortar antes evita comparar una rentabilidad nominal de 2026-09 contra una inflacion que todavia no existe.

### Comparabilidad

**Alta, y esto es lo que la investigacion de prensa no lograba.** Los 17 portafolios tienen exactamente el mismo periodo (2015-01-31 a 2026-08-31) y el mismo numero de observaciones (140 cierres mensuales). Las cifras se pueden restar entre AFP directamente.

Tres advertencias sobre que miden estas cifras:

- Es **rentabilidad del fondo**, no del afiliado. No descuenta la comision de administracion sobre la cotizacion (hasta 3% del ingreso base) ni la prima del seguro previsional, que se cobran antes de que la plata entre al fondo. Si descuenta los gastos que se causan dentro del portafolio.
- El portafolio Moderado aparece en el dataset bajo dos nombres distintos (`FONDO DE PENSIONES MODERADO` para Colfondos y Proteccion, `FONDO DE PENSIONES OBLIGATORIO MODERADO` para Porvenir), pero es el mismo portafolio regulatorio en los cuatro casos.
- El nombre de Proteccion aparece con y sin tilde en distintos registros del dataset. Se normalizo a "Proteccion".

### Nivel de confianza

**ALTO.** Es dato primario de la Superintendencia Financiera, el mismo insumo con el que la SFC calcula la rentabilidad minima obligatoria, tomado por API sin intermediarios ni prensa. El unico paso de calculo propio es la division valor sobre unidades, que es la definicion contable del valor de la unidad. El IPC es el indice oficial DANE publicado por Banrep.

Lo que sigue siendo estimacion y no dato: nada en esta seccion. Lo que falta cubrir: la rentabilidad neta al afiliado despues de comisiones, que requiere modelar las comisiones y no sale de este dataset.

### Como reproducirlo

```bash
python3 /Users/jsanti00/Developer/jubilo/analisis/rendimiento_afp.py
```

El script baja el crudo de la SFC y el IPC, los deja en cache (`AFP_DATOS`, por defecto `/tmp/afp_datos`), imprime la tabla en Markdown y guarda `resultados.json`. Para forzar una actualizacion, borrar la carpeta de cache antes de correrlo. La bajada completa son unas 145.000 filas y toma un par de minutos.

---

## Contraste de prensa, confianza menor

Lo que sigue es la investigacion previa, basada en paginas de las AFP y notas de prensa que citan circulares de la SFC. Se conserva como contraste, pero **la seccion de arriba manda**: cubre mas portafolios, con el mismo periodo para todos, y con conversion a real.

## Resumen y limitaciones

No fue posible construir la tabla completa y actualizada (largo plazo y ultimos 5 anos, por AFP y por portafolio, nominal vs. real, fondo vs. afiliado) porque:

- Las paginas oficiales de las AFP (Protección, Colfondos, Skandia) estan renderizadas en JavaScript: el fetch solo captura el encabezado o recibe error 403.
- Los PDF de la Superintendencia Financiera de Colombia (SFC) llegan como binario o grafico vectorial ilegible por las herramientas disponibles.
- El tablero de Power BI de la SFC no es extraible (confirmado, consistente con intentos previos del equipo).

Lo que si se consiguio: series de largo plazo de Porvenir (fuente primaria, su propia pagina), comparativos de prensa que citan circulares oficiales de la SFC (2022, 2023 y 2025), y la estructura regulatoria de comisiones.

## Tabla principal

| AFP | Portafolio | Rentabilidad | Periodo | Tipo | Confianza |
|---|---|---|---|---|---|
| Porvenir | Moderado | 11,22% (minimo 7,18%) | 31-may-2022 a 31-may-2026 (~4 anos) | Nominal, no se especifica fondo/afiliado | ALTA (fuente propia, cita Circular 34/2026 SFC) |
| Porvenir | Conservador | 10,56% (minimo 7,03%) | 31-may-2023 a 31-may-2026 (~3 anos) | Nominal | ALTA |
| Porvenir | Mayor riesgo | 11,43% (minimo 6,65%) | 31-may-2021 a 31-may-2026 (5 anos) | Nominal | ALTA |
| Colfondos | Mayor riesgo | 6,35% | 31-dic-2017 a 31-dic-2022 (5 anos) | Nominal | ALTA (La Republica citando Carta Circular 7/2023 SFC) |
| Proteccion | Mayor riesgo | 5,95% | igual periodo | Nominal | ALTA |
| Skandia | Mayor riesgo | 4,75% | igual periodo | Nominal | ALTA |
| Colfondos | Moderado | 6,85% | 31-dic-2018 a 31-dic-2022 (4 anos) | Nominal | ALTA |
| Proteccion | Moderado | 8,30% | igual periodo | Nominal | ALTA |
| Skandia | Moderado | 6,90% | igual periodo | Nominal | ALTA |
| Colfondos | Conservador | 1,45% | 31-dic-2019 a 31-dic-2022 (3 anos) | Nominal | ALTA |
| Proteccion | Conservador | 1,50% | igual periodo | Nominal | ALTA |
| Skandia | Conservador | 0,70% | igual periodo | Nominal | ALTA |
| Colfondos | No especificado (probable moderado) | 9,84% | 31-mar-2023 a 31-mar-2025 (2 anos) | Nominal, "neto" (probable rentabilidad del afiliado) | MEDIA (La Republica citando SFC, sin PDF original) |
| Proteccion | idem | 9,52% | idem | idem | MEDIA |
| Porvenir | idem | 9,51% | idem | idem | MEDIA |
| Skandia | idem | 8,61% | idem | idem | MEDIA |
| Proteccion | idem | 8,35% | 31-dic-2024 a 31-mar-2025 (trimestre) | idem | MEDIA |
| Porvenir | idem | 8,94% | idem | idem | MEDIA |
| Colfondos | idem | 8,15% | idem | idem | MEDIA |
| Skandia | idem | 7,91% | idem | idem | MEDIA |

No conseguido: rentabilidad real (descontada inflacion) para ninguna AFP; rentabilidad de los ultimos 5 anos exactos a fecha de hoy (2026) por portafolio para Proteccion, Colfondos y Skandia; distincion clara y verificada entre rentabilidad del portafolio y rentabilidad del afiliado en la mayoria de cifras (solo Porvenir aclara metodologia, y no del todo).

## Comisiones de administracion

| AFP | Comision sobre IBC | Fecha/fuente | Confianza |
|---|---|---|---|
| Todas las AFP (regla legal) | Maximo 3% del IBC combinado (administracion + seguro previsional), Ley 100/1993 | Vigente, marco legal | ALTA |
| Skandia | Hasta 2,1% (parte de administracion dentro del tope de 3%) | Prensa, sin fecha exacta reciente | BAJA/MEDIA |
| Porvenir | ~1,0% | La Republica, mar-2022 | BAJA (dato de 2022, no verificado vigente) |
| Colfondos | ~0,85% (0,55% administracion + resto seguro) | La Republica, mar-2022; pagina propia no accesible (403) | BAJA |
| Proteccion | ~0,85% | La Republica, mar-2022 | BAJA |

Advertencia: estas cifras de comision tienen 4 anos de antiguedad. Se intento verificar en las paginas oficiales de Colfondos y Porvenir (comisiones-de-administracion, PDF de comisiones) y ambas fallaron: la de Colfondos devolvio error 403 y el PDF de Porvenir llego como archivo de diseno grafico (Illustrator) sin texto extraible. No se puede dar por vigente el desglose porcentual sin confirmacion 2026.

## Cifras NO comparables entre si

- Los periodos difieren entre AFP y entre fuentes (2, 3, 4 o 5 anos segun el fondo y la fecha de corte); ninguna comparacion directa entre filas de periodos distintos es valida.
- No se pudo confirmar si las cifras de 2023-2025 y 2025 (La Republica) son por portafolio (conservador, moderado, mayor riesgo) o un promedio ponderado del conjunto de fondos de la AFP; probablemente corresponden al fondo moderado (el de mayor participacion), pero el articulo no lo especifica.
- Ninguna cifra reportada aqui esta confirmada como "rentabilidad del afiliado" (neta de comision) vs. "rentabilidad del portafolio" de forma consistente entre AFP.
- Todo lo reportado es nominal; no hay ninguna cifra real (deflactada) verificada.

## Fuentes

- [Porvenir, Cifras e informacion general de pensiones obligatorias](https://www.porvenir.com.co/pensiones/cifras-e-informacion-general-de-pensiones-obligatorias) (consultado 18-sep-2026)
- [SFC, Informe trimestral de rentabilidad, comision de administracion y seguro previsional](https://www.superfinanciera.gov.co/publicaciones/11084/) (consultado 18-sep-2026; enlaces de descarga por ano, no se pudo leer el contenido del PDF 2026, idFile 1080750)
- [SFC, Rentabilidad minima de fondos de pensiones obligatorias y cesantias (Power BI)](https://www.superfinanciera.gov.co/powerbi/reportes/524/505/) (no extraible, confirmado)
- [La Republica, "Conozca cual es la rentabilidad de los fondos de pension y su nivel minimo regulado"](https://www.larepublica.co/finanzas/rentabilidad-de-los-fondos-de-pension-4115312), 22-abr-2025, citando SFC
- [Valora Analitik, "Estas son las mejores rentabilidades de fondos de pensiones segun cada portafolio"](https://www.valoraanalitik.com/estas-son-las-mejores-rentabilidades-de-fondos-de-pensiones-segun-cada-portafolio/), 8-feb-2023, citando Carta Circular 7/2023 SFC
- [La Republica, "Cuanto cobran los fondos? Comisiones a las pensiones no son de 30% del ingreso"](https://www.larepublica.co/finanzas/cuanto-cobran-los-fondos-las-comisiones-a-las-pensiones-no-llegan-a-30-del-ibc-3322723), mar-2022
- [Colfondos, comisiones de administracion](https://www.colfondos.com.co/dxp/personas/pensiones-obligatorias/comisiones-de-administracion) (error 403, no accesible)
- [Colfondos, indicadores de rentabilidad](https://www.colfondos.com.co/dxp/personas/rentabilidades) (error 403, no accesible)
- [Proteccion, rentabilidades pension obligatoria y cesantias](https://www.proteccion.com/contenidos/persona/cesantias/rentabilidades-pensiones-cesantias) (solo encabezado, contenido JS no capturado)
- [Skandia, portal de rentabilidades](https://portal.skandia.com.co/om.rentabilidades.pl/oldmutual) (pagina con datos de plantilla, no reales)
- [Datos Abiertos Colombia, Valoracion de los Tipos de Fondos de Pensiones Obligatorias y Cesantias](https://www.datos.gov.co/dataset/Valoraci-n-de-los-Tipos-de-Fondos-de-Pensiones-Obl/hds9-4524/data) (dataset identificado, no procesado por limite de alcance)

## Recomendacion para siguiente paso

Las paginas de AFP y la SFC son SPA o PDF no legibles por fetch simple. La via mas confiable seria descargar directamente los Excel/CSV de datos.gov.co (dataset hds9-4524 y similares) con un script y procesarlos localmente, en vez de depender de scraping de paginas.
