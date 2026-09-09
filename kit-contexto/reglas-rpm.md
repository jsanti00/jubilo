# Reglas operativas RPM (Colpensiones) - Documento 2 del kit

> **Última actualización:** 2026-07-16. **Estado:** destilado inicial bajo Ley 100 de 1993 vigente. Marcas `[VERIFICAR]` señalan puntos que debe confirmar el abogado pensional o actuario antes del piloto (control de calidad definido en la definición conceptual, sección 4).
> **Convención:** cada regla cita su fuente legal. La calculadora implementa estas reglas tal cual; si una regla cambia, se cambia aquí primero.

## 1. Qué es el RPM

Régimen de Prima Media con Prestación Definida, administrado por Colpensiones. Los aportes van a un fondo común y la pensión se calcula con una **fórmula definida por ley** (no depende de rendimientos ni de saldo individual). *Fuente: Ley 100 de 1993, arts. 31-32.*

## 2. Cotización

| Concepto | Regla | Fuente |
|---|---|---|
| Tasa total | 16% del IBC | Ley 100 art. 20, mod. Ley 797/2003 art. 7 |
| Empleado | 12% empleador + 4% trabajador | Ley 100 art. 20 |
| Independiente | 16% a su cargo; IBC **mínimo** del 40% de los ingresos netos de costos, piso 1 SMLMV (detalle completo en `independientes.md`) | Ley 100 art. 19; Ley 2277 de 2022 art. 89, reglamentado por el Decreto 780 de 2016 art. 3.2.7.5, sustituido por el Decreto 379 de 2026 |
| IBC mínimo / máximo | 1 SMLMV / 25 SMLMV | Ley 100 art. 18 |
| Fondo de Solidaridad Pensional | +1% adicional si IBC >= 4 SMLMV; más un escalonado adicional desde 16 SMLMV (tabla abajo) | Ley 100 art. 27, mod. Ley 797/2003 art. 8 |

### El escalonado del Fondo de Solidaridad, con la tabla completa

Son **dos aportes distintos que se suman**, no uno solo. Quien gana más de 20 SMLMV paga los dos: el 1% de la subcuenta de solidaridad **más** el 1% de la subcuenta de subsistencia, o sea 2 puntos por encima del 16%.

| Ingreso base de cotización | Aporte adicional | Subcuenta |
|---|---|---|
| Desde 4 SMLMV | +1,0% | Solidaridad |
| De 16 a 17 SMLMV | +0,2% | Subsistencia |
| De 17 a 18 SMLMV | +0,4% | Subsistencia |
| De 18 a 19 SMLMV | +0,6% | Subsistencia |
| De 19 a 20 SMLMV | +0,8% | Subsistencia |
| Superiores a 20 SMLMV | +1,0% | Subsistencia |

*Fuente: Ley 100 de 1993 art. 27, modificado por Ley 797 de 2003 art. 8, num. 2 lit. a).*

`[VERIFICAR]` **Respuesta operativa:** el agente ya puede dar la tabla completa de arriba, con las cifras literales de la ley. **Se corrigieron dos cosas de la ficha anterior:** (a) el escalonado **no llega hasta 25 SMLMV**; termina en el tramo "superiores a 20 SMLMV", que es plano en 1%. La redacción anterior ("de 16 a 25 SMLMV") inducía a inventar tramos que la ley no tiene. (b) El aporte del escalonado **se suma** al 1% de la subcuenta de solidaridad, no lo reemplaza. **Falta confirmar:** con el abogado, si hay decreto reglamentario posterior que ajuste estos porcentajes, y cómo se aplica el escalonado dentro de un tramo (proporcional o por salto al cruzar el umbral). **Si cambia:** movería el costo mensual de quien cotiza por encima de 16 SMLMV, un caso poco frecuente pero de alto valor. **Antecedente que esto cierra:** el 2026-07-26, en una sesión de role-play, el agente estimó el tramo alto como "+0,2% por cada salario mínimo por encima de 15", una interpretación propia sin respaldo. Con la tabla arriba, ese cálculo a ojo queda prohibido: se lee la tabla.

**No existe aporte voluntario en RPM.** La única forma de aumentar la mesada es un IBL más alto o más semanas: no hay cuenta individual donde poner plata extra. Es una de las preguntas más frecuentes de quien tiene capacidad de ahorro. Detalle y contraste con RAIS en `aportes-voluntarios-y-sobrecotizacion.md`.

## 3. Requisitos de pensión de vejez

**Edad:** 57 años mujer, 62 años hombre. *Fuente: Ley 100 art. 33, mod. Ley 797/2003 art. 9 (vigente desde 2014).*

**Semanas:**

- **Hombres: 1.300 semanas.**
- **Mujeres: según el año en que cumplen el requisito**, por la Sentencia C-197 de 2023 (la Corte encontró discriminación indirecta de género en exigir las mismas semanas en condiciones laborales desiguales):

| Año | Semanas mujer | Año | Semanas mujer |
|---|---|---|---|
| 2025 | 1.300 | 2031 | 1.125 |
| 2026 | 1.250 | 2032 | 1.100 |
| 2027 | 1.225 | 2033 | 1.075 |
| 2028 | 1.200 | 2034 | 1.050 |
| 2029 | 1.175 | 2035 | 1.025 |
| 2030 | 1.150 | 2036 en adelante | 1.000 |

*Fuente: Corte Constitucional, Sentencia C-197 de 2023: reducción de 50 semanas el 1 de enero de 2026 y de 25 semanas cada año desde 2027 hasta llegar a 1.000.*

`[VERIFICAR]` **Respuesta operativa:** el agente **aplica el calendario de arriba** y se lo dice a la usuaria con seguridad. El razonamiento: la reducción nace de la sentencia, no de la ley, así que opera de forma autónoma mientras la reforma no esté en firme. Y la reforma no lo está: la Ley 2381 de 2024 fue devuelta al Congreso por el **Auto 841 de 2025** de la Corte Constitucional por un vicio de procedimiento; la Cámara repitió el debate el 28 de junio de 2026 y el control de constitucionalidad sigue pendiente. De la Ley 2381 solo producen efecto la elección de administradora y la ventana de traslado. **Falta confirmar:** el texto literal del "RESUELVE" de la C-197 de 2023 con el calendario tal como lo redactó la Corte (la investigación del 2026-07-26 no logró abrir el resolutivo completo y reconstruyó la tabla desde comunicados de Colpensiones y Presidencia, que coinciden entre sí); y si la Corte ya falló de fondo sobre la Ley 2381. **Si cambia:** se mueve la fecha en que una mujer alcanza sus semanas, que es la mitad del diagnóstico. **Regla de vigilancia:** el día que salga el fallo sobre la reforma, esta tabla es lo primero que hay que revisar en todo el kit.

## 4. IBL (Ingreso Base de Liquidación)

El salario sobre el que se calcula la pensión:

1. **Regla general:** promedio de los IBC de los **últimos 10 años** cotizados, actualizando cada IBC anualmente con el IPC hasta la fecha de liquidación. *Fuente: Ley 100 art. 21.*
2. **Alternativa:** promedio de **toda la vida laboral** (también indexado) si el afiliado cotizó al menos 1.250 semanas y ese promedio le resulta superior. *Fuente: Ley 100 art. 21, inciso final.*
3. La calculadora computa ambos cuando aplica y usa el mayor.

## 5. Tasa de reemplazo (porcentaje del IBL que se paga como pensión)

```
r = 65,50% - 0,50 x s        donde s = IBL / SMLMV (número de salarios mínimos)
```

- Esa `r` aplica por las **semanas mínimas requeridas** (numeral 3).
- **+1,5% por cada 50 semanas adicionales** a las mínimas.
- **Techo: 80% del IBL.** **Piso: la pensión nunca es inferior a 1 SMLMV** ni superior a 25 SMLMV.
- Ejemplos de la fórmula base: s=1 -> 65,0%; s=4 -> 63,5%; s=10 -> 60,5%; s=20 -> 55,5%.

*Fuente: Ley 100 art. 34, mod. Ley 797/2003 art. 10; tope de 25 SMLMV: Acto Legislativo 01 de 2005.*

`[VERIFICAR]` **Respuesta operativa:** **la fórmula tiene piso y el piso es 55%, no 55,5%.** El mismo art. 34 lo dice después de la fórmula: el monto "oscilará entre el 65 y el 55% del ingreso base de liquidación, en forma decreciente en función de su nivel de ingresos calculado con base en la fórmula señalada". Es decir, la fórmula deja de bajar cuando toca el 55%, que ocurre en s = 21. Para cualquier IBL de 21 salarios mínimos o más, el componente base es 55% y de ahí en adelante solo suben las semanas adicionales. *Fuente: Ley 100 art. 34, modificado por Ley 797 de 2003 art. 10 (texto verificado contra el Diario Oficial 45.079).* **Corrección de la ficha anterior:** el kit traía 55,5% como piso, que era el valor de la fórmula en s = 20, no el piso legal. **MARCA CERRADA el 2026-07-27.** El texto se contrastó contra **Secretaría del Senado**, que es la fuente que este kit prefiere para la Ley 100, y dice literalmente: *"A partir del 2004, el monto mensual de la pensión de vejez será un porcentaje que oscilará entre el 65 y el 55% del ingreso base de liquidación de los afiliados, en forma decreciente en función de su nivel de ingresos calculado con base en la fórmula señalada."* Coincide con lo que ya se había leído en el Diario Oficial 45.079. **Confianza: ALTA, en fuente primaria.**

**Brecha de calculadora, también cerrada el 2026-07-27:** `calcular_mesada` en `rpm.py` aplicaba la fórmula sin límite inferior y subestimaba la tasa base para IBL de más de 21 salarios mínimos. **Ya implementa el piso del 55% y el techo del 65%** sobre la tasa base, con las semanas adicionales sumando por encima y el techo global del 80% intacto. `probar_rpm.py` tiene 8 comprobaciones de regresión que terminan en código de salida 1 si el piso se rompe. **Ninguna cifra del set dorado se movió:** los casos Colpensiones tienen IBL cercanos a 1,7 salarios mínimos, muy lejos de donde el piso muerde.

`[VERIFICAR]` **Respuesta operativa:** se cuentan **desde el requisito reducido del año de la pensión**, que es lo que hace la calculadora. El fundamento es el texto del propio art. 34: "por cada cincuenta (50) semanas adicionales **a las mínimas requeridas**, el porcentaje se incrementará en un 1.5%". La ley ancla el conteo a las mínimas requeridas, no a un número fijo de 1.300, y la C-197 de 2023 redefine cuál es ese mínimo para la mujer beneficiaria en cada año. *Fuente: Ley 100 art. 34, mod. Ley 797 de 2003 art. 10.* **Falta confirmar:** esto es **la zona más gris de todo el documento**. La investigación del 2026-07-26 no encontró concepto de Colpensiones, desarrollo reglamentario ni jurisprudencia que lo resuelva expresamente para las mujeres beneficiadas por la C-197, y hay señales de que en la operación de Colpensiones el punto se discute. **Si cambia:** el impacto es de varios puntos porcentuales de tasa de reemplazo, o sea decenas de miles de pesos mensuales de por vida. **Cómo lo dice el agente:** entrega la cifra con la lectura de arriba **y advierte en la misma frase que ese punto no está cerrado con Colpensiones**, para que la usuaria no tome la cifra como definitiva. Es la excepción declarada a la regla de responder sin condicionales: aquí el condicional es la información honesta.

## 6. Mesadas

**13 mesadas al año** (12 + mesada adicional de diciembre) para pensiones causadas después de julio de 2011. *Fuente: Acto Legislativo 01 de 2005.* La calculadora V1 usa 13 en todos los escenarios futuros.

## 7. Indemnización sustitutiva (si no se alcanza la pensión)

Para quien cumple la edad sin las semanas mínimas y declara la imposibilidad de seguir cotizando: devolución en un solo pago.

```
Indemnización = SBC x semanas cotizadas x promedio ponderado de los porcentajes cotizados
```

donde SBC es el salario base semanal promedio, actualizado con IPC. *Fuente: Ley 100 art. 37; Decreto 1730 de 2001.*

**Regla de asesoría clave:** la indemnización sustitutiva **no reconoce rendimientos** (solo indexa por inflación), mientras la devolución de saldos del RAIS sí incluye los rendimientos de la cuenta. Es una diferencia central en el comparador de regímenes para quien probablemente no se pensione.

## 8. Conteo de semanas (reglas operativas verificadas con casos reales)

1. **1 semana = 7 días; los totales se calculan desde días exactos**, no sumando filas redondeadas del reporte (regla del día exacto, verificada contra 2 reportes reales de Colpensiones; ver `V0/casos/README.md`).
2. **Simultaneidad:** con varios empleadores en el mismo periodo, las semanas se cuentan **una sola vez** y los IBC se **suman** para el promedio (sin exceder 25 SMLMV). *Fuente: nota estándar del reporte de Colpensiones; verificado en casos 03 y 04.*
3. **Meses COVID (abril-mayo 2020, Decreto 558 de 2020):** cuentan para el requisito de 1.300 semanas y para pensión mínima aunque la cotización fue reducida. *Fuente: nota del reporte de Colpensiones; Sentencia C-258 de 2021 ordenó el recálculo.*
4. Periodos **en mora del empleador** no se pierden para el trabajador: se señalan como alerta y suman una vez el empleador paga; los reportes los marcan como "deuda presunta" o mora.

`[VERIFICAR]` **Meses COVID en el IBL. Respuesta operativa:** el agente responde que esos dos meses **cuentan como semanas** (eso está resuelto) y que **el IBC que aparece en el reporte es el que entra al promedio**, que es exactamente lo que hace la calculadora: no inventa un IBC "normalizado" para esos meses. Si el usuario cotizó reducido en abril y mayo de 2020, esos dos meses entran al IBL con el valor reducido. **Falta confirmar:** si Colpensiones al liquidar aplica algún ajuste que reponga el IBC de esos meses. **Si cambia:** el efecto es pequeño (2 meses en una ventana de 120) salvo para quien tenga una historia muy corta. **Postura conservadora:** usar el IBC reportado, que es el dato duro del documento, en vez de suponer un ajuste favorable que nadie ha confirmado.

`[VERIFICAR]` **Mora del independiente. Respuesta operativa:** aquí **la regla se invierte y hay que decirlo claro**: si el moroso es el propio independiente, la deuda es suya y **esas semanas no cuentan hasta que pague**. No hay tercero contra quien reclamar ni deber de cobro que lo proteja, que es lo que sí ampara al trabajador dependiente. La buena noticia es que **sí puede ponerse al día**: paga las cotizaciones dejadas de pagar más los intereses de mora por PILA, y con eso las semanas se convalidan. *Fuente: Decreto 1833 de 2016 (reglas de PILA); Corte Constitucional, Sentencia T-501 de 2018.* **Falta confirmar:** el texto vigente del decreto que regula hoy el pago retroactivo de independientes (se mencionan el Decreto 1990 de 2016 y el 1296 de 2022, sin verificación primaria). **Si cambia:** cambiaría el costo de ponerse al día, no el derecho a hacerlo. **Por qué importa en el diagnóstico:** a un independiente con meses en mora, el agente **no le suma esas semanas** al conteo. Se las muestra aparte, como semanas recuperables si paga, con lo que cuesta recuperarlas.

## 9. Fuera de alcance V1 (el router lo detecta y lo dice)

**Sin cálculo, pero ya con respuesta informativa** (actualizado 2026-07-21: estos temas dejaron de ser "no lo sé" y tienen documento propio; lo que sigue fuera es *calcular* la prestación, no *explicarla*):

- Pensión de invalidez: ver `invalidez-e-incapacidades.md`.
- Pensión de sobrevivientes: ver `beneficiarios-y-sobrevivientes.md`.
- Pensión familiar (Ley 1580 de 2012): ver `beneficiarios-y-sobrevivientes.md`.
- Beneficios Económicos Periódicos (BEPS): ver `sin-pension-alternativas.md`.

**Fuera de alcance del todo:**

- Regímenes exceptuados y especiales (Fuerzas Militares, Policía, magisterio, Ecopetrol) y régimen de transición (terminó el 31 de diciembre de 2014).
- Actividades de alto riesgo (Decreto 2090 de 2003).

## 10. Relación con traslados

Regla que más afecta la asesoría: **a menos de 10 años de la edad de pensión no se permite el traslado de régimen** (Ley 797/2003 art. 2, lit. e). Mujer: bloqueado desde los 47; hombre: desde los 52. El detalle (doble asesoría, ineficacia del traslado) va en `reglas-traslados.md` (pendiente).
