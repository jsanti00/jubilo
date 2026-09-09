# Casos de RPM liquidados a mano

> **Creado:** 2026-07-28. **Última actualización:** 2026-07-28, después de que se corrigieran los tres defectos que este documento detectó. **Autor:** agente C del batch de construcción del 2026-07-27 (decisión 6 de Santiago).
> **Qué es:** cuatro casos de Régimen de Prima Media liquidados paso a paso **desde la norma**, sin usar `rpm.py`, para que exista por primera vez un número esperado que alguien pueda auditar. La prueba `probar_casos_liquidados.py` compara estas cifras contra lo que devuelve el módulo y termina en código de salida 1 si alguna se mueve.
> **Por qué existe:** el bug del IBL sobrevivió a cinco pruebas y al set dorado porque todas verificaban que el flujo corriera y que las semanas cuadraran, ninguna que el resultado fuera correcto (ver `ESTADO.md`, pendiente 2 de la sesión del 26).
> **Alcance:** SOLO RPM. Los casos de RAIS quedan pendientes porque la banda del factor de conversión está cambiando sus cifras en paralelo.

---

## 0. Cómo leer este documento

Cada caso trae cinco cosas, en el mismo orden en que las exige la ley:

1. **El afiliado y su historia**, en un formato que se puede reconstruir a mano.
2. **Las semanas**, contadas con la regla del día exacto.
3. **El IBL**, con la tabla de indexación año por año.
4. **La tasa de reemplazo**, con la fórmula y sus límites.
5. **La mesada**, con los topes aplicados.

Todas las cifras están en **pesos de 2026** (la calculadora no proyecta inflación en ningún punto). La fecha de cálculo de los cuatro casos es **2026-06-30**, fija para que la prueba sea reproducible.

Los cuatro casos son **sintéticos**: se diseñaron con historias de un renglón por año para que la aritmética se pueda seguir sin computador, y cada uno ejercita reglas distintas. No son personas reales ni salen del set dorado de `casos/`, que no se toca.

| Caso | Perfil | Qué regla pone a prueba |
|---|---|---|
| **L1** | Hombre de 64 años, ya cumple edad y semanas | IBL indexado por IPC, ventana de 10 años, fórmula base, un bloque de 50 semanas |
| **L2** | Mujer de 54 años, se pensiona en 2029 | Ventana anclada al **año de pensión** (el bug del IBL), requisito de semanas de la C-197, bloques contados desde el requisito reducido |
| **L3** | Hombre de alto ingreso con historia partida en el tiempo | Piso del 55% de la tasa base, cero bloques adicionales, tope de IBC de 25 SMLMV |
| **L4** | Hombre que ganó bien hace veinte años y poco en la última década | `elegir_ibl`: la alternativa de **toda la vida laboral** del art. 21 y la elección del mayor de los dos |

> **L4 se agregó el 2026-07-28**, cuando se corrigió el hallazgo 1 de la sección 7. La elección del mayor de los dos IBL es la regla más nueva del módulo y era la única sin liquidación manual que la respaldara, que es exactamente el hueco que este documento existe para tapar.

---

## 1. Las reglas que se aplican, con su fuente

Todo lo que sigue sale de estas siete reglas. Ninguna otra se usa.

| # | Regla | Fuente | Confianza |
|---|---|---|---|
| R1 | **Semanas:** 1 semana = 7 días. El total se reconstruye fila por fila desde los días exactos, no sumando semanas redondeadas | Nota del reporte de Colpensiones, verificada contra 2 reportes reales (`casos/README.md`) | ALTA |
| R2 | **IBL:** promedio de los IBC de los **10 años anteriores a la pensión**, cada uno actualizado con el IPC hasta la fecha de liquidación. Cada mes pesa por sus días cotizados | Ley 100 de 1993 art. 21 | ALTA (fuente primaria, Secretaría del Senado) |
| R2b | **Alternativa del IBL:** quien cotizó **1.250 semanas o más** puede liquidar con el promedio de **toda la vida laboral**, también indexado, si ese promedio le resulta superior. Manda el mayor de los dos | Ley 100 art. 21, inciso final | ALTA. Implementada en `elegir_ibl` desde el 2026-07-28 (ver hallazgo 1 de la sección 7); el caso L4 la liquida a mano |
| R3 | **Tasa base:** `r = 65,5% - 0,5 x s`, con `s = IBL / SMLMV`. La tasa base **no baja del 55% ni sube del 65%** | Ley 100 art. 34, mod. Ley 797 de 2003 art. 10. Texto literal: *"un porcentaje que oscilará entre el 65 y el 55% del ingreso base de liquidación"* | ALTA (verificado 2026-07-27 contra Secretaría del Senado y Diario Oficial 45.079) |
| R4 | **Semanas adicionales:** +1,5% por cada bloque **completo** de 50 semanas por encima de las mínimas requeridas **del año de la pensión** | Ley 100 art. 34, mod. Ley 797 de 2003 art. 10 (*"adicionales a las mínimas requeridas"*) | MEDIA. La aplicación del requisito reducido de la C-197 como base del conteo **no está confirmada con Colpensiones**: es la zona más gris del kit (ver `reglas-rpm.md` s.5) |
| R5 | **Techo y pisos:** el total nunca pasa del 80% del IBL; la mesada nunca baja de 1 SMLMV ni sube de 25 SMLMV | Ley 100 art. 34; tope de 25 SMLMV del Acto Legislativo 01 de 2005 | ALTA |
| R6 | **Requisitos:** edad 57 mujer / 62 hombre. Semanas: hombre 1.300 fijas; mujer según el año (1.250 en 2026, 1.175 en 2029) | Ley 100 art. 33 mod. Ley 797/2003 art. 9; Sentencia C-197 de 2023 | ALTA en edad. MEDIA en la tabla de la mujer: el resolutivo literal de la C-197 no se ha podido abrir, la tabla se reconstruyó de comunicados de Colpensiones y Presidencia que coinciden (ver `reglas-rpm.md` s.3) |

**Dato del sistema usado en los cuatro casos:** SMLMV de 2026 = **$1.750.905** (Decretos 1469 y 1470 de 2025, verificado). Serie de IPC diciembre a diciembre del DANE, la que está cargada en `datos_sistema.py`.

**Factores de indexación** (inflación acumulada desde el año indicado hasta pesos de 2026), calculados como el producto de `(1 + IPC del año / 100)` desde el año de la cotización hasta 2025 inclusive:

| Año | Factor | Año | Factor |
|---|---|---|---|
| 2016 | 1,729272 | 2022 | 1,366780 |
| 2017 | 1,635246 | 2023 | 1,208257 |
| 2018 | 1,570992 | 2024 | 1,105652 |
| 2019 | 1,522574 | 2025 | 1,051000 |
| 2020 | 1,466835 | 2026 y posteriores | 1,000000 |
| 2021 | 1,443593 | | |

> **Convención declarada:** el factor de un año incluye la inflación **de ese mismo año**. Es decir, un salario de 2016 se trata como pesos de comienzos de 2016 y se lleva a pesos de comienzos de 2026. Los años futuros no se indexan porque ya vienen expresados en pesos de hoy. Los dos sesgos que esto introduce (media inflación de más en la punta vieja, media inflación de menos en la punta nueva) van en direcciones opuestas y se compensan en buena parte. **No es la fórmula exacta de Colpensiones**, que indexa mes a mes con el índice de precios; es la aproximación anual que usa el proyecto y hay que declararla al usuario.

---

## 2. Caso L1: hombre que ya cumple edad y semanas

**Para qué sirve:** es el caso base. Verifica el IBL indexado, la ventana de 10 años y la fórmula sin que ningún límite muerda.

### 2.1 El afiliado

| Dato | Valor |
|---|---|
| Sexo | Hombre |
| Fecha de nacimiento | 1962-02-20 |
| Edad a la fecha de cálculo | 64 años |
| Cumplió 62 años el | 2024-02-20 |
| Historia | Cotización continua de enero de 2000 a junio de 2026, un solo empleador |

Salarios (IBC nominal de cada año, el mismo los 12 meses):

| Periodo | IBC mensual |
|---|---|
| 2000 a 2015 | de $800.000 a $1.700.000, subiendo $60.000 por año |
| 2016 | $2.000.000 |
| 2017 | $2.100.000 |
| 2018 | $2.200.000 |
| 2019 | $2.300.000 |
| 2020 | $2.400.000 |
| 2021 | $2.500.000 |
| 2022 | $2.700.000 |
| 2023 | $3.000.000 |
| 2024 | $3.200.000 |
| 2025 | $3.400.000 |
| 2026 (enero a junio) | $3.600.000 |

### 2.2 Paso 1, las semanas (regla R1)

- 26 años completos (2000 a 2025) x 12 meses x 30 días = **9.360 días**
- 6 meses de 2026 x 30 días = **180 días**
- Total = **9.540 días**
- Semanas = 9.540 / 7 = **1.362,86 semanas**

Requisito del hombre: **1.300 semanas** (R6). Ya las tiene. Ya tiene la edad. **Se puede pensionar hoy: 2026-06-30.**

### 2.3 Paso 2, el IBL (regla R2)

La ventana son los 10 años anteriores a la pensión, o sea de 2016 en adelante. Cada año aporta sus días como peso.

| Año | Meses | Días | IBC nominal | Factor | IBC en pesos de 2026 |
|---|---|---|---|---|---|
| 2016 | 12 | 360 | $2.000.000 | 1,729272 | $3.458.545 |
| 2017 | 12 | 360 | $2.100.000 | 1,635246 | $3.434.016 |
| 2018 | 12 | 360 | $2.200.000 | 1,570992 | $3.456.183 |
| 2019 | 12 | 360 | $2.300.000 | 1,522574 | $3.501.921 |
| 2020 | 12 | 360 | $2.400.000 | 1,466835 | $3.520.403 |
| 2021 | 12 | 360 | $2.500.000 | 1,443593 | $3.608.982 |
| 2022 | 12 | 360 | $2.700.000 | 1,366780 | $3.690.305 |
| 2023 | 12 | 360 | $3.000.000 | 1,208257 | $3.624.770 |
| 2024 | 12 | 360 | $3.200.000 | 1,105652 | $3.538.086 |
| 2025 | 12 | 360 | $3.400.000 | 1,051000 | $3.573.400 |
| 2026 | 6 | 180 | $3.600.000 | 1,000000 | $3.600.000 |
| **Total** | | **3.780** | | | |

Numerador (suma de IBC indexado x días):

- Los diez años completos suman $35.406.611 de IBC indexado. Por 360 días cada uno: 35.406.611 x 360 = **$12.746.379.960**
- 2026: 3.600.000 x 180 = **$648.000.000**
- Numerador total = **$13.394.379.960**

**IBL = 13.394.379.960 / 3.780 = $3.543.487** (valor exacto 3.543.486,776)

### 2.4 Paso 3, la tasa de reemplazo (reglas R3 y R4)

- `s` = 3.543.487 / 1.750.905 = **2,02** salarios mínimos
- Tasa base = 65,5 - 0,5 x 2,023803 = **64,49%** (dentro de la banda 55 a 65, ningún límite muerde)
- Semanas por encima del mínimo: 1.362,9 - 1.300 = 62,9 -> **1 bloque completo** de 50
- Premio: 1 x 1,5% = **+1,5%**
- **Tasa total = 64,49 + 1,5 = 65,99%**
- Techo del 80%: no muerde

### 2.5 Paso 4, la mesada (regla R5)

- Mesada = 3.543.487 x 65,99% = **$2.338.280** mensuales, en pesos de hoy
- Piso de 1 SMLMV ($1.750.905): no muerde. Tope de 25 SMLMV: no muerde
- **Al año, con 13 mesadas: $30.397.640**

### 2.6 Cifras esperadas del caso L1

| Concepto | Valor esperado |
|---|---|
| Semanas hoy | 1.362,86 |
| Fecha de pensión | 2026-06-30 |
| IBL (10 años) | $3.543.487 |
| s (en salarios mínimos) | 2,02 |
| Tasa base | 64,49% |
| Bloques de 50 semanas | 1 |
| Tasa total | 65,99% |
| **Mesada** | **$2.338.280** |
| IBL de toda la vida (informativo) | $3.232.467 |

**Contraste con `rpm.py`: coincide en las nueve cifras, peso por peso.**

---

## 3. Caso L2: mujer que se pensiona en 2029

**Para qué sirve:** es el caso que habría atrapado el bug del IBL. La ventana de 10 años se ancla al **año de la pensión (2029)**, no al año de hoy, así que los 33 meses que todavía le faltan por cotizar entran al promedio salarial. Verifica además el requisito de semanas de la C-197 y el conteo de bloques desde el requisito reducido.

### 3.1 La afiliada

| Dato | Valor |
|---|---|
| Sexo | Mujer |
| Fecha de nacimiento | 1972-03-10 |
| Edad a la fecha de cálculo | 54 años |
| Cumple 57 años el | 2029-03-10 |
| Historia | Cotización continua de enero de 2004 a junio de 2026 |

Salarios: de 2004 a 2015 sube de $700.000 a $1.470.000 ($70.000 por año). De ahí en adelante:

| Año | IBC | Año | IBC |
|---|---|---|---|
| 2016 | $1.900.000 | 2022 | $2.900.000 |
| 2017 | $2.000.000 | 2023 | $3.200.000 |
| 2018 | $2.100.000 | 2024 | $3.500.000 |
| 2019 | $2.300.000 | 2025 | $3.800.000 |
| 2020 | $2.400.000 | 2026 (enero a junio) | $4.000.000 |
| 2021 | $2.600.000 | | |

### 3.2 Paso 1, las semanas de hoy (regla R1)

- 22 años completos (2004 a 2025) x 360 días = 7.920 días
- 6 meses de 2026 = 180 días
- Total = **8.100 días = 1.157,14 semanas**

Requisito de 2026 para mujer: **1.250 semanas** (R6). **No las tiene todavía.**

### 3.3 Paso 2, cuándo se pensiona

Son dos requisitos y manda el que llegue más tarde.

- **Edad:** cumple 57 el **2029-03-10**.
- **Semanas:** cotizando al ritmo actual (densidad 100%, 30 días por mes), le faltan 1.250 x 7 - 8.100 = 650 días, o sea 21,7 meses. Los alcanza hacia **abril de 2028**.

Manda la edad. **Fecha de pensión: 2029-03-10.** Año de pensión: 2029, en el que el requisito de la mujer es **1.175 semanas**.

### 3.4 Paso 3, las semanas que tendrá al pensionarse

- Meses entre la fecha de cálculo (junio de 2026) y la pensión (marzo de 2029) = **33 meses**
- Días futuros = 33 x 30 x 100% de densidad = **990 días**
- Total = 8.100 + 990 = 9.090 días = **1.298,6 semanas**

### 3.5 Paso 4, el IBL anclado al año de pensión (regla R2)

**Este es el punto que importa.** La ventana son los 10 años anteriores a **2029**, o sea de 2019 en adelante. Los años 2026 a 2029 son proyección: cotiza sobre su salario actual de $4.000.000, que ya está en pesos de hoy y por eso no se indexa.

| Año | Meses | Días | IBC | Factor | IBC en pesos de 2026 | Origen |
|---|---|---|---|---|---|---|
| 2019 | 12 | 360 | $2.300.000 | 1,522574 | $3.501.921 | historia |
| 2020 | 12 | 360 | $2.400.000 | 1,466835 | $3.520.403 | historia |
| 2021 | 12 | 360 | $2.600.000 | 1,443593 | $3.753.341 | historia |
| 2022 | 12 | 360 | $2.900.000 | 1,366780 | $3.963.661 | historia |
| 2023 | 12 | 360 | $3.200.000 | 1,208257 | $3.866.421 | historia |
| 2024 | 12 | 360 | $3.500.000 | 1,105652 | $3.869.782 | historia |
| 2025 | 12 | 360 | $3.800.000 | 1,051000 | $3.993.800 | historia |
| 2026 | 12 | 360 | $4.000.000 | 1,000000 | $4.000.000 | 6 meses de historia + 6 proyectados |
| 2027 | 12 | 360 | $4.000.000 | 1,000000 | $4.000.000 | proyectado |
| 2028 | 12 | 360 | $4.000.000 | 1,000000 | $4.000.000 | proyectado |
| 2029 | 3 | 90 | $4.000.000 | 1,000000 | $4.000.000 | proyectado |
| **Total** | | **3.690** | | | | |

Numerador:

- Los diez años completos suman $38.469.329 de IBC indexado. Por 360 días: **$13.848.958.440**
- 2029: 4.000.000 x 90 = **$360.000.000**
- Numerador total = **$14.208.958.440**

**IBL = 14.208.958.440 / 3.690 = $3.850.666** (valor exacto 3.850.666,287)

> **Contraste que muestra el tamaño del bug viejo:** si la ventana se hubiera anclado a 2026 en vez de a 2029, los años 2027 a 2029 (los mejor pagados) no entrarían y entrarían 2019 y 2020 (los peor pagados). El promedio salarial habría quedado más bajo y la mesada con él. Esta es la cifra que ninguna prueba anterior verificaba.

### 3.6 Paso 5, tasa y mesada (reglas R3, R4 y R5)

- `s` = 3.850.666 / 1.750.905 = **2,20** salarios mínimos
- Tasa base = 65,5 - 0,5 x 2,199243 = **64,40%**
- Semanas por encima del mínimo de 2029: 1.298,6 - 1.175 = 123,6 -> **2 bloques completos**
- Premio: 2 x 1,5% = **+3,0%**
- **Tasa total = 67,40%**
- Mesada = 3.850.666 x 67,40% = **$2.595.364** mensuales, en pesos de hoy
- Al año, con 13 mesadas: **$33.739.732**

> **Advertencia que el agente debe repetir con esta cifra:** los 2 bloques adicionales se contaron sobre el requisito reducido de 1.175 semanas de la C-197. Si Colpensiones liquidara contra las 1.300 semanas originales, la afiliada no tendría ningún bloque (1.298,6 está por debajo de 1.300) y la tasa caería del 67,40% al 64,40%, unos **$115.520 mensuales menos**. Es la zona gris de la regla R4 y no se puede presentar como definitiva.

### 3.7 Cifras esperadas del caso L2

| Concepto | Valor esperado |
|---|---|
| Semanas hoy | 1.157,14 |
| Requisito hoy (2026) | 1.250 |
| Fecha en que cumple la edad | 2029-03-10 |
| Fecha de pensión | 2029-03-10 |
| Semanas proyectadas a la pensión | 1.298,6 |
| Requisito del año de pensión (2029) | 1.175 |
| IBL (10 años anteriores a 2029) | $3.850.666 |
| Tasa base | 64,40% |
| Bloques de 50 semanas | 2 |
| Tasa total | 67,40% |
| **Mesada** | **$2.595.364** |
| Escenario "deja de cotizar hoy" | Sin pensión (no alcanza las semanas) |

**Contraste con `rpm.py`: coincide en las doce cifras.**

---

## 4. Caso L3: alto ingreso donde muerde el piso del 55%

**Para qué sirve:** es el único de los tres donde un límite legal cambia el resultado. La fórmula daría 54,63% y la ley la detiene en 55%. Verifica además que el premio por semanas se cuenta bien cuando no hay ningún bloque completo.

### 4.1 El afiliado

| Dato | Valor |
|---|---|
| Sexo | Hombre |
| Fecha de nacimiento | 1962-05-10 |
| Edad a la fecha de cálculo | 64 años |
| Cumplió 62 años el | 2024-05-10 |
| Historia | Enero de 1993 a diciembre de 2015 cotizando sobre 4 SMLMV; **ocho años sin cotizar** (2016 a 2023); regreso en enero de 2024 cotizando sobre el tope legal de 25 SMLMV |

**Por qué esta forma tan particular:** con una historia continua el piso del 55% **no puede morder**. El IBC tope son 25 salarios mínimos del año en que se cotiza, y el salario mínimo ha crecido bastante más rápido que el IPC, así que un salario tope de 2016 traído a pesos de 2026 vale mucho menos de 25 salarios mínimos de hoy. Sobre una historia continua de 10 años al tope, el IBL llega a unos 19 salarios mínimos y la fórmula todavía da más de 55%. Solo con la ventana concentrada en los últimos años se supera el umbral de 21 salarios mínimos donde el piso empieza a operar. Ver el hallazgo 4 de la sección 7.

Salarios del tramo que entra a la ventana:

| Año | IBC (25 SMLMV del año) |
|---|---|
| 2024 | $32.500.000 |
| 2025 | $35.587.500 |
| 2026 (enero a junio) | $43.772.625 |

### 4.2 Paso 1, las semanas (regla R1)

- 1993 a 2015: 23 años x 360 días = 8.280 días
- 2024 y 2025: 720 días. 2026 (6 meses): 180 días
- Total = **9.180 días = 1.311,43 semanas**

Requisito del hombre: 1.300 semanas. Las tiene, por poco. Ya tiene la edad. **Se pensiona hoy: 2026-06-30.**

### 4.3 Paso 2, el IBL (regla R2)

Ventana: 10 años anteriores a 2026, o sea de 2016 en adelante. Los años 2016 a 2023 no tienen cotización y no entran al promedio: **el hueco no cuenta como cero, simplemente no pesa.**

| Año | Meses | Días | IBC | Factor | IBC en pesos de 2026 |
|---|---|---|---|---|---|
| 2024 | 12 | 360 | $32.500.000 | 1,105652 | $35.933.690 |
| 2025 | 12 | 360 | $35.587.500 | 1,051000 | $37.402.462 |
| 2026 | 6 | 180 | $43.772.625 | 1,000000 | $43.772.625 |
| **Total** | | **900** | | | |

Numerador:

- 35.933.690 x 360 = **$12.936.128.400**
- 37.402.462 x 360 = **$13.464.886.320**
- 43.772.625 x 180 = **$7.879.072.500**
- Numerador total = **$34.280.087.220**

**IBL = 34.280.087.220 / 900 = $38.088.986**

### 4.4 Paso 3, la tasa: aquí muerde el piso (regla R3)

- `s` = 38.088.986 / 1.750.905 = **21,75** salarios mínimos
- Fórmula sola: 65,5 - 0,5 x 21,753885 = **54,62%**
- **La ley no deja bajar del 55%.** Tasa base = **55,00%**
- Semanas por encima del mínimo: 1.311,4 - 1.300 = 11,4 -> **0 bloques completos**. No hay premio
- **Tasa total = 55,00%**

### 4.5 Paso 4, la mesada (regla R5)

- Mesada = 38.088.986 x 55,00% = **$20.948.942** mensuales, en pesos de hoy
- Tope de 25 SMLMV ($43.772.625): no muerde
- Al año, con 13 mesadas: **$272.336.246**

**Cuánto vale el piso:** sin él, la tasa habría sido 54,62% y la mesada $20.805.369. El piso vale **$143.574 mensuales**, unos $1,9 millones al año.

### 4.6 Cifras esperadas del caso L3

| Concepto | Valor esperado |
|---|---|
| Semanas hoy | 1.311,43 |
| Fecha de pensión | 2026-06-30 |
| IBL (10 años) | $38.088.986 |
| s (en salarios mínimos) | 21,75 |
| Tasa base | 55,00% (la fórmula sola daría 54,62%) |
| Bloques de 50 semanas | 0 |
| Tasa total | 55,00% |
| **Mesada** | **$20.948.942** |

**Contraste con `rpm.py`: coincide en las ocho cifras.**

---

## 5. Caso L4: cuando gana el IBL de toda la vida laboral

**Para qué sirve:** es el único caso donde la regla R2b decide el resultado. Respalda a mano la función `elegir_ibl`, que se agregó el 2026-07-28 al corregir el hallazgo 1. Sin este caso, la regla más nueva del módulo sería otra vez una regla sin número esperado que nadie pueda auditar.

### 5.1 El afiliado

| Dato | Valor |
|---|---|
| Sexo | Hombre |
| Fecha de nacimiento | 1962-08-15 |
| Edad a la fecha de cálculo | 63 años |
| Cumplió 62 años el | 2024-08-15 |
| Historia | Cotización continua de enero de 1994 a junio de 2026, sin un solo mes de hueco |
| Salario 1994 a 2015 | **$2.400.000** nominales, constantes (en 1994 eran 24 salarios mínimos: un ejecutivo) |
| Salario 2016 a 2026 | **$1.800.000** nominales, constantes (en 2026 es apenas 1,03 salarios mínimos) |

Es el perfil que el hallazgo 1 dejaba mal liquidado: alguien que ganó muy bien durante veinte años, perdió el empleo formal a mitad de camino y terminó su vida laboral cotizando cerca del mínimo. La ventana de los últimos 10 años le borra exactamente sus mejores años de aportes.

> El salario de 1994 se escogió por debajo del tope legal de ese año (25 SMLMV de 1994 = $2.467.500), para que el tope de IBC del hallazgo 3 no intervenga y el caso pruebe una sola cosa.

### 5.2 Paso 1, las semanas (regla R1)

- 1994 a 2015: 22 años x 360 días = 7.920 días
- 2016 a 2025: 10 años x 360 días = 3.600 días
- 2026 (enero a junio): 180 días
- Total = **11.700 días = 1.671,43 semanas**

Tiene las 1.300 del hombre y, sobre todo, **pasa de las 1.250 que exige la alternativa de toda la vida (R2b)**. Ya tiene la edad. **Se pensiona hoy: 2026-06-30.**

### 5.3 Paso 2, el IBL de los últimos 10 años

Ventana: 2016 en adelante. El salario nominal es constante ($1.800.000), así que el promedio es ese salario por el promedio ponderado de los factores.

| Tramo | Días | Suma de factores | Aporte al numerador |
|---|---|---|---|
| 2016 a 2025 (10 años) | 3.600 | 14,100201 | 1.800.000 x 14,100201 x 360 = **$9.136.930.248** |
| 2026 (6 meses) | 180 | 1,000000 | 1.800.000 x 1,0 x 180 = **$324.000.000** |
| **Total** | **3.780** | | **$9.460.930.248** |

**IBL de 10 años = 9.460.930.248 / 3.780 = $2.502.892**

### 5.4 Paso 3, el IBL de toda la vida laboral (regla R2b)

Ahora entra todo, desde 1994. Los factores del tramo viejo son grandes porque acumulan más de treinta años de inflación:

| Año | Factor | Año | Factor | Año | Factor |
|---|---|---|---|---|---|
| 1994 | 10,226046 | 2002 | 3,269119 | 2010 | 2,138927 |
| 1995 | 8,341664 | 2003 | 3,055537 | 2011 | 2,073206 |
| 1996 | 6,982809 | 2004 | 2,869318 | 2012 | 1,998656 |
| 1997 | 5,741025 | 2005 | 2,719733 | 2013 | 1,951050 |
| 1998 | 4,878506 | 2006 | 2,593927 | 2014 | 1,913920 |
| 1999 | 4,180382 | 2007 | 2,482702 | 2015 | 1,846344 |
| 2000 | 3,827137 | 2008 | 2,349042 | | |
| 2001 | 3,519207 | 2009 | 2,181705 | | |

**Suma de los factores de 1994 a 2015 = 81,139962.** El salario nominal es constante en ese tramo, así que:

| Tramo | Días | Aporte al numerador |
|---|---|---|
| 1994 a 2015 | 7.920 | 2.400.000 x 81,139962 x 360 = **$70.104.927.168** |
| 2016 a 2026 | 3.780 | el mismo de arriba = **$9.460.930.248** |
| **Total** | **11.700** | **$79.565.857.416** |

**IBL de toda la vida = 79.565.857.416 / 11.700 = $6.800.501**

**El de toda la vida es 2,7 veces el de los últimos 10 años. La ley manda usar el mayor: $6.800.501.**

### 5.5 Paso 4, tasa y mesada con cada uno de los dos IBL

El contraste es el punto del caso, así que se liquidan los dos caminos:

| Concepto | Con el IBL de 10 años (lo que hacía el código antes) | Con el IBL de toda la vida (lo correcto) |
|---|---|---|
| IBL | $2.502.892 | $6.800.501 |
| s (en salarios mínimos) | 1,43 | 3,88 |
| Tasa base = 65,5 - 0,5 x s | 64,79% | 63,56% |
| Bloques de 50 semanas (1.671,4 - 1.300 = 371,4) | 7 -> +10,5% | 7 -> +10,5% |
| Tasa total | 75,29% | 74,06% |
| **Mesada** | **$1.884.308** | **$5.036.315** |

Ni el techo del 80% ni el piso de 1 SMLMV muerden en ninguno de los dos, así que la diferencia es limpia: **$3.152.007 al mes, un 167% más.** Es la misma persona con la misma historia; lo único que cambia es cuál de los dos promedios que ofrece la ley se usa.

Nótese que la **tasa** es más baja con el IBL bueno (74,06% contra 75,29%), porque la fórmula castiga el ingreso alto. No importa: 74,06% de un IBL grande es mucho más que 75,29% de uno pequeño. Es un buen recordatorio de que la tasa de reemplazo sola no dice nada.

### 5.6 Cifras esperadas del caso L4

| Concepto | Valor esperado |
|---|---|
| Semanas hoy | 1.671,43 |
| Fecha de pensión | 2026-06-30 |
| IBL de los 10 años | $2.502.892 |
| IBL de toda la vida | $6.800.501 |
| Cuál se usa | `toda_la_vida` |
| s (en salarios mínimos) | 3,88 |
| Tasa base | 63,56% |
| Bloques de 50 semanas | 7 |
| Tasa total | 74,06% |
| **Mesada** | **$5.036.315** |

**Contraste con `rpm.py`: coincide en las diez cifras.**

---

## 6. Los topes, verificados aparte

Los tres casos de arriba no activan el techo del 80%, ni el piso de 1 SMLMV, ni el tope de 25 SMLMV. La prueba los verifica con entradas sintéticas directas a `calcular_mesada`, liquidadas a mano igual que los casos.

| Qué se verifica | Entrada | Cuenta a mano | Resultado esperado |
|---|---|---|---|
| **Techo del 80%** | IBL de 2 SMLMV ($3.501.810), 1.850 semanas, hombre | Tasa base 65,5 - 0,5 x 2 = 64,50%. Bloques: (1.850 - 1.300) / 50 = 11 -> +16,5%. Total 81,00%, **recortado a 80,00%** | Tasa 80,00%, mesada **$2.801.448** |
| **Piso de 1 SMLMV** | IBL de $1.000.000, 1.300 semanas, hombre | s = 0,571. Fórmula: 65,5 - 0,29 = 65,21%, **recortada al techo de la tasa base, 65,00%**. Mesada = $650.000, **subida al piso** | Tasa 65,00%, mesada **$1.750.905** |
| **Tope de 25 SMLMV** | IBL de $100.000.000, 1.300 semanas, hombre | s = 57,1. Fórmula daría 36,9%, **subida al piso del 55%**. Mesada = $55.000.000, **recortada al tope** | Tasa 55,00%, mesada **$43.772.625** |

> El caso del tope de 25 SMLMV usa un IBL imposible en la práctica. Ver el hallazgo 4.

---

## 7. Hallazgos: dónde la cuenta a mano y el código no dijeron lo mismo

Los casos liquidados **cuadran peso por peso** con `rpm.py`. La liquidación manual no encontró ningún error en la fórmula, el IBL ni los límites.

Al armarlos aparecieron cuatro cosas que sí valen. **Tres se corrigieron el 2026-07-28**, en `rpm.py`, después de que Santiago autorizara la primera. La cuarta era informativa desde el principio.

**El diagnóstico original se conserva completo, a propósito.** El valor de este documento no es la lista de defectos vivos: es el rastro de qué estaba mal, cómo se detectó y cuánto costaba. Cada hallazgo lleva ahora su estado al comienzo; lo que sigue debajo es lo que se escribió cuando el defecto estaba abierto y no se reescribe.

| Hallazgo | Estado | Qué lo corrige |
|---|---|---|
| 1. El IBL de toda la vida se calculaba y no se usaba | **CORREGIDO** el 2026-07-28 | `elegir_ibl` en `rpm.py` |
| 2. La fecha de semanas usaba el requisito del año equivocado | **CORREGIDO** el 2026-07-28 | `fecha_en_que_cumple_semanas` en `rpm.py` |
| 3. Sin tope de 25 SMLMV al IBC mensual | **CORREGIDO** el 2026-07-28 | `TOPE_IBC_EN_SMLMV` y `tope_ibc_del_anio` en `rpm.py` |
| 4. El tope de 25 SMLMV de la mesada no puede activarse | Informativo, sigue vigente | No requiere corrección |

### Hallazgo 1 (grave): el IBL de toda la vida se calcula pero no se usa

> **ESTADO: CORREGIDO el 2026-07-28.** Santiago autorizó la corrección. `rpm.py` tiene ahora la función **`elegir_ibl`**, que calcula el de 10 años y, solo con 1.250 semanas o más, calcula también el de toda la vida y **devuelve el mayor**. Cada escenario expone `ibl_10_anios`, `ibl_toda_la_vida` e `ibl_usado`, así que la elección queda a la vista y se puede explicar. **El kit y la norma coincidían en el número: no hubo contradicción que resolver, solo una regla escrita que el código no aplicaba.** La regla quedó liquidada a mano en el **caso L4** de la sección 5, con una diferencia de $3.152.007 al mes sobre ese perfil. Efecto sobre el set dorado: ver la sección 7.5.

`reglas-rpm.md` s.4.3 dice: *"la calculadora computa ambos cuando aplica y **usa el mayor**"*. `rpm.py` calcula el IBL de toda la vida y lo devuelve en la llave `ibl_toda_la_vida`, pero la mesada **siempre** se liquida con el IBL de los 10 años. El mayor nunca se elige.

**A quién le pega:** a quien tuvo su mejor ingreso hace más de 10 años. Es exactamente el perfil de quien se quedó sin empleo formal, se volvió independiente o bajó de cargo cerca del final de su vida laboral.

**Cuánto pesa, medido:** caso sintético de un hombre que cotizó sobre 10 salarios mínimos de 1996 a 2012 y sobre 1 salario mínimo de 2013 en adelante, con 1.568,57 semanas.

| Concepto | Valor |
|---|---|
| IBL de los últimos 10 años | $1.339.351 |
| IBL de toda la vida | $6.380.340 |
| Mesada que da `rpm.py` (con el IBL de 10 años, recortada al piso de 1 SMLMV) | $1.750.905 |
| Mesada si usara el mayor, como dice la regla | $4.541.398 |
| **Diferencia** | **$2.790.493 al mes, 2,6 veces la mesada** |

**Qué falta antes de corregirlo:** confirmar la condición del art. 21 inciso final. La alternativa de toda la vida exige haber cotizado **al menos 1.250 semanas** y solo aplica si ese promedio resulta superior. `rpm.py` ya evalúa las 1.250 semanas para decidir si calcula el valor, así que la corrección es elegir el mayor de los dos al liquidar. **Es una decisión de producto y no del agente C:** cambiar esto mueve mesadas del set dorado.

### Hallazgo 2 (medio): la fecha en que alcanza las semanas usa el requisito del año equivocado

> **ESTADO: CORREGIDO el 2026-07-28.** `rpm.py` tiene ahora la función **`fecha_en_que_cumple_semanas`**, que avanza mes a mes comparando las semanas acumuladas contra el requisito **del año de ese mes**, no contra el del año de cálculo.
> **Precisión sobre la medición de abajo:** con la fecha de cálculo del caso, el valor viejo era 2029-06-01 y no 2029-07-01. Un mes de diferencia, por la fecha de cálculo y no por la corrección. La dirección y el tamaño del defecto (alrededor de un año de pensión) son los que se describen.

`rpm.py` línea 305 proyecta cuándo se completan las semanas usando `requisito_hoy`, el requisito del **año de cálculo**. Para las mujeres el requisito baja 25 semanas cada año por la C-197, así que la fecha sale más tarde de lo que corresponde: se le exige a la afiliada un número de semanas que en ese año futuro ya no rige.

**Cuánto pesa, medido:** mujer nacida en 1969 (ya cumplió 57), con 1.097,14 semanas y cotizando al 100%.

| Cálculo | Fecha en que cumple las semanas |
|---|---|
| `rpm.py` (exige 1.250, el requisito de 2026) | 2029-07-01 |
| Correcto (exige 1.200, el requisito de 2028) | 2028-06 |
| **Diferencia** | **13 meses de pensión** |

En los casos L1 y L3 no se nota porque la edad manda. En L2 tampoco, por la misma razón. **Muerde solo cuando las semanas son el requisito que llega más tarde**, que es el perfil de la mujer con historia laboral intermitente: frecuente, y no está cubierto por ninguna prueba.

### Hallazgo 3 (medio): no hay tope de 25 SMLMV al IBC mensual con empleadores simultáneos

> **ESTADO: CORREGIDO el 2026-07-28.** `rpm.py` tiene ahora la constante **`TOPE_IBC_EN_SMLMV = 25`** y la función **`tope_ibc_del_anio(anio)`**, que topa el IBC del mes con el salario mínimo **del año de la cotización**, como corresponde. La regla de reparto de días no se tocó: el defecto era solo del salario, no del conteo de semanas.

`reglas-rpm.md` s.8.2 dice que con varios empleadores los IBC se suman **"sin exceder 25 SMLMV"**. `expandir_a_meses` los suma sin ningún tope.

**Cuánto pesa, medido:** dos empleadores simultáneos, cada uno cotizando sobre 20 SMLMV de 2025.

| Concepto | Valor |
|---|---|
| IBC del mes según `rpm.py` | $56.940.000 (40 SMLMV) |
| Tope legal de 2025 (25 SMLMV) | $35.587.500 |
| **Exceso que entra al IBL** | **60% por encima del tope** |

Es un caso poco frecuente pero de alto valor (dos empleos formales bien pagados), y el efecto va siempre en la dirección de **sobreestimar** la mesada, que es el error caro para la credibilidad del producto. El tope debe aplicarse con el SMLMV del **año de la cotización**, no con el de hoy.

### Hallazgo 4 (informativo): el tope de 25 SMLMV de la mesada no puede activarse

> **ESTADO: sigue vigente y no requiere corrección.** Es una observación sobre la estructura de la norma, no un defecto del código.

El IBC máximo legal son 25 SMLMV (Ley 100 art. 18). Como el IBL es un promedio de IBC, el IBL nunca puede superar 25 SMLMV en pesos de hoy. Y como el techo de la tasa es el 80%, la mesada máxima posible es 80% x 25 = **20 SMLMV**, siempre por debajo del tope de 25.

| Concepto | Valor 2026 |
|---|---|
| Mesada máxima alcanzable (80% de 25 SMLMV) | $35.018.100 |
| Tope de 25 SMLMV | $43.772.625 |

No es un error: la línea del tope está bien como salvaguarda. Vale anotarlo para que nadie invierta tiempo buscando un caso real que la active, y porque si alguna vez esa línea se activa **es señal de que algo aguas arriba está mal** (por ejemplo, el hallazgo 3).

### 7.5 Qué se movió en el set dorado con las correcciones

Solo una cifra, y es la del hallazgo 1. Verificada por este agente contra `rpm.py` el 2026-07-28, con fecha de cálculo 2026-07-18 (la que usa `probar_rpm.py`).

**caso-04, escenario "sigue cotizando":**

| Concepto | Antes | Ahora |
|---|---|---|
| IBL de los 10 años | $2.107.760 | $2.107.760 |
| IBL de toda la vida | (se calculaba y se ignoraba) | $2.711.151 |
| IBL usado | 10 años | **toda la vida** |
| Tasa base | 64,90% | 64,73% |
| **Mesada** | **$1.750.905** | **$2.168.920** |

**+$418.015 al mes, +23,9%.** La mesada anterior estaba recortada al piso de 1 SMLMV; con el IBL mayor se sostiene sola, que es el cambio cualitativo: deja de ser una pensión de salario mínimo.

**La elección funciona en las dos direcciones**, que es lo que había que comprobar para no cambiar un sesgo por otro. En el **escenario "deja de cotizar" del mismo caso-04** gana el de 10 años ($3.646.803 contra $3.006.182 de toda la vida) y la mesada no se movió. El caso-05 tampoco se movió, y los casos L1, L2 y L3 de este documento siguen cuadrando peso por peso: en los tres gana el IBL de 10 años.

### 7.6 Abierto: el caso-05 no puede evaluar su IBL de toda la vida

El caso-05 tiene un periodo cotizado en **1992** y la serie de IPC de `datos_sistema.py` **arranca en 1993**. `calcular_ibl` no puede indexar ese salario y, fiel a la regla de oro del proyecto, **no inventa el dato**: devuelve el error en vez de un número.

Qué hace `elegir_ibl` con eso, y está bien hecho: liquida con el IBL de los 10 años y **levanta una nota explícita** en la salida, *"No se pudo evaluar el IBL de toda la vida (podría ser el mayor)"*. No falla en silencio ni finge que la alternativa no existía.

**Pero el hueco es real y hay que decirlo:** el caso-05 tiene 1.236,57 semanas hoy y 1.370,1 proyectadas, así que **sí califica** para la alternativa del art. 21. **No sabemos si le convenía.** Dado lo que mostró el caso L4 (una diferencia de $3,1 millones al mes sobre el perfil adecuado), la pregunta no es menor.

| Concepto | Estado |
|---|---|
| Qué falta | El IPC anterior a 1993 de la serie del DANE |
| Cuántos años | Depende de cuánto atrás llegue la historia laboral más vieja que se quiera atender; para el caso-05 basta con 1992 |
| Qué desbloquea | Evaluar la alternativa de toda la vida para cualquier afiliado que empezó a cotizar antes de 1993, o sea buena parte de quien se pensiona hoy |
| Riesgo de no hacerlo | Liquidar por debajo, en silencio, a quien empezó temprano y ganó bien al principio |

**Es la tarea de datos con mejor relación entre esfuerzo y valor que dejó este trabajo.** No requiere abogado ni decisión de producto: es cargar una serie pública.

### Observaciones de convención, que no son errores

1. **La ventana de 10 años tiene granularidad anual.** Entran todos los meses del año calendario, así que en L1 la ventana cubre 10 años y 6 meses (enero de 2016 a junio de 2026) y en L2, 10 años y 3 meses. La ley habla de los 10 años anteriores a la pensión. Con salarios crecientes el sesgo es levemente a la baja (entran meses viejos de más). Efecto de segundo orden, pero hay que declararlo.
2. **La indexación incluye el IPC del propio año** del salario. Ver la nota de la sección 1. Los dos sesgos se compensan en buena parte.
3. **En rangos, el IBC del último mes se aplica a todos los meses del rango.** Es la aproximación V1 documentada en `esquema-datos.md`: el resumen de Colpensiones no trae más. Los casos de este documento están construidos con un renglón por año y salario constante dentro del año, así que la aproximación no los afecta.

---

## 8. Trabajo pendiente: los casos de RAIS

Esta sesión liquidó **solo RPM**, por instrucción explícita: el agente A está reemplazando el factor de conversión de capital a mesada por una banda, así que cualquier número esperado de RAIS fijado hoy nacería desactualizado.

Lo que hay que liquidar a mano después, en orden de valor:

1. **Saldo proyectado con aportes futuros.** Es la pieza equivalente al IBL del RPM: el saldo a la fecha de pensión, con el aporte mensual del 11,5% del IBC, el rendimiento real del perfil y la comisión. Verifica `proyectar_saldo`.
2. **Mesada por los DOS extremos de la banda del factor.** No un número, sino un par ordenado. La prueba debe fijar que el extremo optimista (4% de interés técnico normativo) coincide con lo que la calculadora daba antes del cambio, que es la regresión que pidió el agente A.
3. **Edad de pensión anticipada (art. 64).** El umbral del 110% del salario mínimo, también por los dos extremos. Es el mensaje estrella del producto y el que más se mueve: en el caso-03 pasa de los 35 a los 39 años.
4. **Garantía de Pensión Mínima.** Con las semanas de la Sentencia C-054 de 2024: 1.150 para hombres, 1.135 para mujeres en 2026 bajando 15 por año. Verifica que se evalúa en el año en que cumple la edad legal, no hoy.
5. **Devolución de saldos** para quien no alcanza, contrastada contra la indemnización sustitutiva del RPM. Es la comparación que decide el consejo de traslado para quien probablemente no se pensione.

**Requisito para que sirvan:** igual que aquí, las cifras esperadas tienen que quedar escritas paso a paso en un documento auditable. Una prueba con un número que nadie puede verificar no prueba nada.
