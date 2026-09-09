# Mora, huecos y corrección de la historia laboral - Bloque H del kit

> **Última actualización:** 2026-07-26. Se agregó el **cuarto estado** de la sección 1 (aporte reportado sin semanas acreditadas, con su guion de conversación) y la sección **1 ter** sobre huecos y lagunas, que fija cómo se responde "¿dónde están mis huecos?" ahora que existe `calculadora/lagunas.py`.
> **Última actualización anterior:** 2026-07-21. **Estado:** destilado inicial. Verificado contra Ley 100 de 1993 y Ley 797 de 2003 (texto vigente en el Gestor Normativo de Función Pública), Decreto 1833 de 2016 (compilatorio), Ley 1066 de 2006 y jurisprudencia de unificación de la Corte Constitucional. Marcas `[VERIFICAR]` para el abogado pensional antes del piloto.
> **Convención:** cada regla cita su fuente legal.
> **Por qué existe este documento:** el router de la calculadora ya detecta moras y el agente las reporta como hallazgo. Detectar un problema y no saber decir qué hacer con él es peor que no detectarlo. Este documento tiene que ser **accionable**: pasos concretos, ante quién, con qué papeles, en qué orden.

## 1. Los cuatro estados distintos que la gente confunde

Antes que nada, el agente tiene que clasificar. Los cuatro se ven parecidos en el reporte y tienen consecuencias muy distintas.

| Estado | Qué pasó | ¿La semana cuenta? | Quién lo resuelve |
|---|---|---|---|
| **Mora patronal** | Hubo afiliación y vínculo laboral vigente, pero el empleador no consignó el aporte | **Sí.** No se le puede oponer al afiliado | La administradora, cobrando al empleador |
| **Deuda presunta** | El sistema presume que hubo cotización porque la afiliación sigue activa y no se reportó la novedad de retiro | **Sí, sujeta a verificación** del vínculo real | La administradora, tras verificar el vínculo |
| **Periodo no reportado** | No hay ningún registro: nunca hubo afiliación, o el empleador nunca lo reportó | **No, hasta que se pruebe y se pague el cálculo actuarial** | El trabajador probando el vínculo, y el empleador pagando |
| **Aporte reportado sin semanas acreditadas** (ver 1 bis) | Hay aportante identificado y salario reportado, pero el reporte acredita **cero semanas**, y la columna de simultáneas también está en cero | **Depende de la causa, que el documento no dice.** Hoy no cuentan | Primero el afiliado, averiguando qué pasó; después, según la causa, la administradora o el aportante |

**La diferencia práctica que hay que decirle al usuario:** en mora y deuda presunta la carga de resolver es de la administradora. En un periodo no reportado, el primer paso lo tiene que dar la persona, aportando la prueba de que trabajó ahí. En el cuarto estado no se sabe todavía de quién es la carga, y por eso el primer movimiento es averiguar, no reclamar.

## 1 bis. El cuarto estado: salario reportado y cero semanas acreditadas

**Cómo se ve.** Una fila del reporte de Colpensiones con aportante identificado, NIT, salario reportado, y **0,00 en semanas cotizadas, 0,00 en semanas simultáneas y 0,00 en semanas válidas**. Lo que la vuelve sospechosa es el contraste interno: cuando esa misma persona tuvo dos aportantes en otro periodo, el reporte **sí** marcó las semanas en la columna de simultáneas. Aquí no marcó nada, y aun así el salario está impreso.

**Caso real que lo destapó** (sesión de role-play del 2026-07-26, hombre de 59 años que además cotiza como independiente sobre $3.600.000):

| Aportante | Periodo | Salario reportado | Semanas | Simultáneas |
|---|---|---|---|---|
| Empresa de servicios temporales | 03/2026 | $641.999 | 0,00 | 0,00 |
| Empresa de servicios temporales | 04/2026 | $1.750.905 | 0,00 | 0,00 |
| Empresa de servicios temporales | 05/2026 | $1.750.905 | 0,00 | 0,00 |

**No es un caso de borde.** Aparece en **los dos** reportes de Colpensiones del set dorado, y en los dos el aportante es una empresa de servicios temporales o de servicios especiales. La sospecha de patrón es concreta: **vinculaciones cortas por empresas temporales sobre gente que además cotiza por su cuenta.**

`[VERIFICAR]` **Respuesta operativa: el agente dice que esa fila NO le está sumando semanas y que hay que averiguar por qué antes de reclamar, porque las cuatro causas posibles se resuelven en puertas distintas.** No promete que sean recuperables ni las descarta.

La causa más respaldada por la evidencia disponible es que **el aporte se reportó en la planilla pero no quedó validado** (mora, pago parcial o pago mal aplicado): el reporte muestra el IBC que el aportante declaró, y las semanas salen de los días **validados**, no de los reportados. Si esa es la causa, el periodo es recuperable y aplica todo lo de las secciones 2 y 3 de este documento: la mora del empleador no se le opone al afiliado.

Las otras tres hipótesis quedaron sin evidencia que las confirme ni las descarte: **simultaneidad real que el sistema no marcó** en la columna correspondiente; **aporte aplicado a otro subsistema** (salud, riesgos laborales) y no a pensión; y **novedad administrativa sin días efectivos** (ingreso y retiro en el mismo mes, suspensión de contrato, licencia no remunerada).

**Falta confirmar:** (a) el glosario oficial de Colpensiones que defina columna por columna qué significan "semanas cotizadas", "semanas en licencia", "semanas simultáneas" y "semanas válidas": **no existe publicado**, y todo lo que hoy explica esas columnas es fuente secundaria; (b) si Colpensiones distingue de alguna forma la mora de la novedad administrativa en este reporte, o si las dos se ven igual; (c) la norma que rige el prorrateo del IBC cuando hay dos aportantes el mismo mes. **Si cambia:** cambiaría la puerta a la que se manda al usuario y si las semanas son recuperables, no la forma de detectarlo (eso ya lo hace `lagunas.py`). **Cómo entra al diagnóstico:** el módulo de lagunas lista estas filas aparte, el router levanta la alerta `ibc_sin_semanas`, y **el agente no las suma al conteo ni las presenta como semanas recuperables** hasta saber la causa.

**Lo que sí es firme y se puede decir sin condicionales:** si resulta ser mora del aportante, el periodo se reconoce aunque la empresa no haya pagado, siempre que se pruebe que la persona efectivamente trabajó ahí. *Fuente: Corte Constitucional, Sentencia T-043 de 2025; Corte Suprema, Sala Laboral, STL14393 de 2025, en la misma línea de la sección 2 de este documento.*

### Guion de conversación cuando aparece esta fila

Existe para que la respuesta no dependa de que el modelo improvise bien la hipótesis en vivo. En la sesión de role-play funcionó, pero funcionó por suerte.

1. **Nombrar el hecho, sin diagnóstico.** "Vi algo raro: [empresa] aparece reportando un salario en [meses], pero con cero semanas acreditadas. Eso no te está sumando."
2. **Las dos preguntas que separan las hipótesis**, una a la vez:
   - "¿Trabajaste con esa empresa en esos meses?"
   - "¿En el desprendible de pago te descontaron pensión?"
3. **Leer la respuesta:**
   - **Trabajó y le descontaron** -> lo más probable es mora del aportante: pasa al guion de mora (sección 7) y a la escalera de la sección 5.
   - **Trabajó y no le descontaron, o fueron pocos días** -> puede ser una novedad sin días efectivos o un aporte que se fue a salud. El paso es pedirle a la empresa el certificado de pago de aportes (planilla PILA) de esos meses.
   - **No trabajó ahí** -> es un reporte que no le corresponde y se pide corrección a Colpensiones (sección 4).
   - **No sabe** -> el paso único es el mismo: pedir la planilla PILA de esos meses a la empresa, o el estado de cuenta a Colpensiones.
4. **Decir el efecto en el número.** Esas semanas **no están** en el conteo, así que el diagnóstico es un piso. Si se resuelven a favor, sube.
5. **No prometer.** Aquí no aplica el "esas semanas son tuyas" de la mora patronal: todavía no se sabe qué son. La frase correcta es "puede que sean recuperables, depende de qué pasó, y eso lo sabemos con un dato".
6. **Cerrar invitando a volver** con lo que averigüe.

**Advertencia para el agente:** el riesgo de esta fila es tratarla como mora patronal por parecido y darle al usuario la tranquilidad que corresponde a otro estado. La mora tiene un responsable claro; esto todavía no.

**Independientes:** la regla se invierte. Si la persona cotizaba como independiente y no pagó un mes, **ese mes no cuenta**: la deuda es propia y no hay tercero contra quien reclamar. *Fuente: la obligación de cotización del independiente está a su cargo, Ley 100 de 1993, art. 19.*

`[VERIFICAR]` **Respuesta operativa: sí existe vía de pago retroactivo, y es la buena noticia de esta sección.** El independiente en mora **puede recuperar esas semanas** pagando por PILA las cotizaciones que dejó de pagar más los intereses de mora; al hacerlo, los periodos reportados en mora quedan convalidados en su historia laboral. *Fuente: Decreto 1833 de 2016 (reglas de PILA); Corte Constitucional, Sentencia T-501 de 2018.* Lo que **no** hay es un derecho a que cuenten **antes** de pagar: ahí sigue la diferencia con el trabajador dependiente, cuya protección viene de que la obligación es de un tercero y la administradora tiene deber de cobro. **Falta confirmar:** el texto vigente del decreto que hoy regula ese pago retroactivo (se mencionan el Decreto 1990 de 2016 y el 1296 de 2022, sin verificación primaria), y si hay límite de antigüedad para ponerse al día. **Si cambia:** cambiaría el costo o la ventana para recuperar, no el derecho. **Cómo entra al diagnóstico:** el agente **no suma esas semanas al conteo**. Las muestra aparte, como semanas recuperables, con la advertencia de que hay que pagar intereses. Para alguien a quien le faltan pocas semanas, esto puede ser la palanca más rentable que tiene, y hoy casi nadie se la menciona.

## 1 ter. Huecos y lagunas: qué responde la calculadora y qué no

**"¿Dónde están mis huecos?" es una pregunta de calculadora, no de criterio.** El agente **nunca** la responde comparando rangos del documento por su cuenta: eso rompe la regla dura 1. La responde con la salida del módulo de lagunas, que devuelve tres cosas distintas y no las mezcla:

| Lo que devuelve | Qué significa | Cómo se lo dice al usuario |
|---|---|---|
| **Vacíos** | Meses que **ningún** aportante reportó. Se sabe cuáles son, con fecha exacta | "Entre agosto de 1997 y enero de 2007 no hay ninguna cotización: son 9 años y medio" |
| **Déficit por tramo** | Dentro de un rango sí reportado, cuántas semanas faltaron frente a las que cabían | "En el tramo de marzo de 2025 a marzo de 2026 cotizaste 11 de los 13 meses: faltan unos 2" |
| **Filas con salario y cero semanas** | El cuarto estado de la sección 1 bis | Guion de la sección 1 bis |

**El límite del formato, que es una regla y no una limitación que haya que disculpar.** Colpensiones agrupa las cotizaciones por tramos con el mismo salario, así que **el detalle mes a mes no existe en el documento**. El agente puede decir cuántos meses faltan en un tramo; **no puede decir cuáles**. No los estima por interpolación ni los reparte "por parejo": nombrar un mes que el documento no nombra es inventar un dato.

**A dónde se manda a quien quiera el mes exacto:** a su historial de pagos en PILA, que sí es mes a mes. Es una respuesta útil, no una excusa: "el reporte de Colpensiones agrupa por tramos, así que ahí no está el mes exacto. Si lo necesitas, está en tu historial de pagos de PILA."

**Un hueco no es lo mismo que una mora.** Un vacío puede ser simplemente que la persona no trabajó, o trabajó sin cotizar. No se presenta como un error que alguien deba corregir hasta saber cuál de los dos fue. La pregunta que separa es directa: "¿en esos años estabas trabajando?".

**Un vacío tampoco se lamenta.** El valor de decirlo no es el pasado sino la palanca: cuántas semanas le costó y qué puede hacer hoy con eso (seguir cotizando, recuperar mora, evaluar las alternativas de `sin-pension-alternativas.md`).

## 2. Mi empleador no pagó, ¿pierdo esas semanas?

**No.** Es la respuesta corta y hay que darla primero, sin rodeos.

### El sustento legal

- **El empleador es responsable del pago de su aporte y del aporte del trabajador.** Debe descontarlo del salario al momento del pago y trasladarlo a la entidad elegida por el trabajador. **Responde por la totalidad del aporte aun si no hizo el descuento.** *Fuente: Ley 100 de 1993, art. 22.*
- **Los aportes no consignados a tiempo generan interés moratorio a cargo del empleador**, igual al que rige para el impuesto de renta. Esos intereses se abonan al fondo de reparto o a la cuenta individual del afiliado, es decir, **al bolsillo pensional de la persona, no al de la administradora**. *Fuente: Ley 100 de 1993, art. 23; Decreto 1833 de 2016, art. 2.2.3.3.1.*
- En entidades del sector público, el ordenador del gasto que sin justa causa no consigne a tiempo incurre en **causal de mala conducta** sancionable disciplinariamente. *Fuente: Ley 100 de 1993, art. 23.*

### La línea jurisprudencial (esta es la parte que cambia conversaciones)

La Corte Constitucional ha unificado que **la mora del empleador no puede oponerse al afiliado**:

- **SU-226 de 2019:** si están acreditados los requisitos para el reconocimiento pensional, no puede negarse la pensión con el pretexto de una omisión en la afiliación o de la mora. No se le puede trasladar al trabajador, parte débil de la relación laboral, la consecuencia del incumplimiento del empleador ni de la omisión de la administradora en cobrarlo. La administradora tiene el deber de reconocer las semanas no declaradas ni pagadas, quedando habilitada para perseguir el pago del cálculo o título actuarial correspondiente.
- **SU-068 de 2022:** unifica los deberes oficiosos de la administradora y del juez cuando hay dudas serias y fundadas sobre la existencia de la relación laboral.
- **SU-062 de 2023:** reitera la regla y precisa la distinción entre mora patronal y omisión de afiliación, y la carga probatoria del afiliado.
- Reiterada, entre otras, en **T-118 de 2023**.

*Fuente: Corte Constitucional, sentencias SU-226 de 2019, SU-068 de 2022, SU-062 de 2023 y T-118 de 2023.*

`[VERIFICAR]` **Respuesta operativa: la línea está firme y las dos cortes coinciden, así que el agente puede afirmarlo sin condicionales.** La mora del empleador **no es imputable al trabajador** y no puede usarse para negarle semanas ni la pensión, porque la administradora tiene el deber de cobro, incluido el coactivo. En la Corte Constitucional la línea viene de la **C-177 de 1998** y se reafirmó en 2023 y 2024 (**T-551 de 2023**, **T-411 de 2023**, **T-289 de 2024**), con reiteraciones en 2025. En la **Sala Laboral de la Corte Suprema**, que es la que aplica el juez ordinario, la **SL138 de 2024** fue en la misma dirección y sumó algo más: el tiempo efectivamente laborado debe contarse como semana cotizada aun con mora y aun sin cobro coactivo de la administradora. No apareció ninguna sentencia posterior que module la línea a la baja. **Falta confirmar:** el texto de SL138 de 2024 en el sitio de la Corte Suprema (ubicada por prensa jurídica), y si existe una unificación (SU) posterior a 2023 específica sobre mora patronal que reemplace la línea de tutelas caso a caso. **Si cambia:** sería un giro grande y a la baja, y afectaría a mucha gente. Nada indica que vaya en esa dirección. **Cómo entra al diagnóstico:** las semanas en mora del empleador **sí se cuentan** en el conteo del usuario, marcadas como alerta para que reclame, no restadas.

### La distinción que la Corte sí hace, y que el agente no debe borrar

- **Mora patronal:** hay afiliación y vínculo laboral vigente; el empleador no paga a tiempo. La administradora debe contabilizar esos tiempos y asumir las cargas financieras del incumplimiento, cobrando al empleador.
- **Omisión de afiliación:** el empleador nunca afilió. El tiempo también cuenta, **pero se financia con un cálculo actuarial** que el empleador debe trasladar. *Fuente: SU-062 de 2023; Ley 100 de 1993, art. 33, par. 1, lit. d), modificado por la Ley 797 de 2003, art. 9.*

**Carga probatoria del afiliado:** la Corte exige **pruebas razonables o inferencias plausibles sobre la existencia del vínculo laboral**. Si en la historia laboral figura una **novedad de retiro**, el afiliado debe acreditar que la relación continuó después de esa fecha. *Fuente: SU-062 de 2023.*

**Aterrizaje honesto para el usuario:** "esas semanas son tuyas, la deuda es de tu empleador. Pero para que te las cuenten, alguien tiene que probar que trabajaste ahí en esas fechas. Entre más papeles tengas, más rápido."

## 3. ¿Quién está obligado a cobrarle al empleador?

**La administradora, no el trabajador.** Y tiene plazos.

- Corresponde a las entidades administradoras adelantar las acciones de cobro por el incumplimiento del empleador. **La liquidación con la que la administradora determina el valor adeudado presta mérito ejecutivo.** *Fuente: Ley 100 de 1993, art. 24.*
- **Las acciones deben iniciarse de manera extrajudicial a más tardar dentro de los 3 meses siguientes** a la fecha en la que se entró en mora. *Fuente: Decreto 1833 de 2016, art. 2.2.3.3.3 (compila el Decreto 1161 de 1994, art. 13).*
- **Procedimiento para constituir en mora:** la administradora requiere por escrito al empleador moroso; si en **15 días** este no se pronuncia, elabora la liquidación, que presta mérito ejecutivo. *Fuente: Decreto 1833 de 2016, art. 2.2.3.3.5 (compila el Decreto 2633 de 1994, art. 2).*
- **Vía de cobro:** las administradoras del RPM público pueden iniciar **cobro coactivo**; las del RAIS y del RPM privado acuden a la **jurisdicción ordinaria**. *Fuente: Decreto 1833 de 2016, arts. 2.2.3.3.3 y 2.2.3.3.6.*

### ¿Y si la administradora no cobró?

Es exactamente el escenario de la línea SU-226 / SU-068 / SU-062: la negligencia de la administradora en cobrar **no puede trasladarse al afiliado**. La administradora que no cobró debe igualmente contar las semanas y asumir la carga financiera, quedando habilitada para perseguir al empleador. *Fuente: SU-226 de 2019 y SU-062 de 2023.*

**Aterrizaje:** "la ley le da a tu fondo tres meses para salir a cobrar. Si no lo hizo, el problema es del fondo, no tuyo, y la Corte ha sido clara en eso."

## 4. Faltan periodos que yo sí trabajé: cómo se corrigen

### Ante quién

Ante la **administradora que tiene la historia laboral**: Colpensiones si es RPM, la AFP si es RAIS. Es un **trámite gratuito y no requiere abogado**. *Fuente: Ministerio de Justicia, LegalApp, "Corrección de la historia laboral ante Colpensiones".*

Rutas verificadas por administradora en `tramites-y-consultas.md`. Lo verificado hasta hoy:
- **Colpensiones:** en línea por el portal Colpensiones Digital o presencial en un Punto de Atención.
- **Skandia:** desde la propia pantalla de Historia Laboral del portal se puede **editar o agregar periodos** y solicitar la validación; Skandia lo resuelve entre **5 y 60 días** según qué tan fácil sea contactar a los empleadores.
- **Protección, Porvenir y Colfondos:** ruta de corrección **por documentar**. Mientras tanto el agente orienta al canal de atención y no inventa la ruta.

### Con qué papeles

Lo que sirve como prueba del vínculo y del periodo, en orden de fuerza:

1. **Contrato de trabajo** y otrosíes.
2. **Certificación laboral** de la empresa con fechas exactas de ingreso y retiro y salario.
3. **Liquidación de prestaciones sociales** al terminar el contrato.
4. **Comprobantes de pago de nómina o desprendibles** que muestren el descuento del aporte a pensión (son especialmente fuertes: prueban que le descontaron).
5. **Planillas PILA** de esos periodos, si las consigue.
6. **Certificación CETIL**, si el empleador fue una entidad pública (ver `bonos-tiempos-publicos-y-exterior.md`, sección 6).
7. Si la empresa ya no existe: certificado de existencia y representación con la anotación de liquidación, y prueba de a quién pasaron sus obligaciones.

*Fuente: Ministerio de Justicia, LegalApp; Colpensiones, preguntas frecuentes de Historia Laboral.*

**Regla de conversación:** el agente no le pide al usuario "los documentos". Le pregunta por lo que sí sabe que tiene: "¿guardaste el contrato o la carta de liquidación de esa empresa? ¿tienes desprendibles de pago de esa época?".

### Cuánto se demora

- La solicitud de corrección es un **derecho de petición** y, como tal, el término general de respuesta es de **15 días hábiles**. *Fuente: Ley 1755 de 2015, que sustituyó el Título II de la Parte Primera del CPACA.*
- `[VERIFICAR]` **Respuesta operativa: hay que separar dos plazos, y solo uno existe.** **Responder** la petición sí tiene plazo legal: **15 días hábiles** en general y **10 días hábiles** si es solo información o documentos (*Ley 1755 de 2015, art. 14*); si la entidad no alcanza, debe avisarlo antes de que se venza, explicando el motivo y la nueva fecha. **Terminar** la corrección, en cambio, **no tiene plazo legal**, y eso está confirmado, no es un vacío de la investigación: depende de que se ubique al empleador. El único dato por administradora es el de Skandia (5 a 60 días). **Falta confirmar:** si Colpensiones tiene una circular interna con plazos de gestión propios. **Si cambia:** el usuario tendría una fecha exigible en vez de una espera abierta. **Qué le dice el agente, que es lo accionable:** que **la respuesta tiene plazo y la corrección no**. Por eso el consejo es radicar por escrito y **contar los 15 días hábiles**: si no le responden a tiempo, ya tiene una violación del derecho de petición y con eso una tutela. **El agente no promete un tiempo de corrección que no esté documentado aquí.**
- Lo que sí puede decir con base legal: **los términos para reconocer una pensión solo empiezan a correr cuando la información laboral está completa**. *Fuente: Decreto 1833 de 2016, art. 2.2.9.2.2.8, par. 1.* Por eso conviene corregir **antes** de radicar la solicitud de pensión, no después.

**Corrección de la norma citada en el plan:** el `plan-corpus-adyacente.md` atribuye la corrección de historia laboral al **art. 46 del Decreto 019 de 2012**. Ese artículo trata de la supresión de la licencia de traducción de obras extranjeras y **el Decreto 019 de 2012 no contiene ninguna disposición sobre corrección de historia laboral** (verificado sobre el texto completo del decreto en el Gestor Normativo). La base real del trámite es el derecho de petición (Ley 1755 de 2015), el deber de las administradoras de mantener correcta la historia laboral, y el procedimiento propio de cada administradora.

`[VERIFICAR]` **Respuesta operativa:** el agente **no cita ninguna norma específica de "deber de corrección", porque no se ha identificado una**, y en su lugar apoya el trámite donde sí hay piso firme: el **derecho de petición** (*Ley 1755 de 2015*), que obliga a responder de fondo en 15 días hábiles, y el **deber de cobro** de la administradora sobre los aportes en mora, que la jurisprudencia da por sentado. Con esos dos el usuario tiene todo lo que necesita para radicar y para reclamar si no le responden. **Falta confirmar:** la norma específica que fija el deber de las administradoras de mantener correcta la historia laboral. **Si cambia:** el reclamo ganaría un fundamento más directo. **Por qué se deja escrito en vez de borrarlo:** este documento nació con una cita equivocada del plan de corpus (el art. 46 del Decreto 019 de 2012, que trata de otra cosa por completo). Dejar visible que **no se encontró la norma**, en vez de sustituir una cita mala por otra que suene bien, es exactamente la disciplina que evita repetir el error.

## 5. ¿Puedo demandar?

Sí, pero es el último escalón y casi nunca es el primero. El orden importa.

### Escalera de escalamiento (de menos a más costo)

1. **Derecho de petición ante la administradora**, pidiendo la corrección o el cobro al empleador. Gratis, sin abogado, respuesta en 15 días hábiles. *Fuente: Ley 1755 de 2015.*
2. **Reclamación ante el Defensor del Consumidor Financiero** de la administradora, si la respuesta no llega o no resuelve. Gratis para el consumidor. *Fuente: Ley 1328 de 2009.*
3. **Queja ante la Superintendencia Financiera de Colombia**, con una precisión que hay que hacer: sirve **frente a las AFP privadas**, que sí son entidades vigiladas por ella. **Frente a Colpensiones no funciona igual.**

`[VERIFICAR]` **Respuesta operativa: la ruta de queja depende de con quién esté la persona, y mandarla a la puerta equivocada le cuesta meses.** Si está en una **AFP privada**, la queja ante la Superfinanciera y ante el Defensor del Consumidor Financiero es la vía. Si está en **Colpensiones**, la Superfinanciera no la vigila de la misma forma (su relación es de instrucciones financieras y actuariales, no de resolver controversias del afiliado): ahí las vías son el **PQRS y el Defensor del Consumidor Financiero de la propia Colpensiones**, y **si hay que decidir el derecho de fondo, el juez laboral**, no una superintendencia. **Falta confirmar:** la norma exacta que delimita el alcance de la vigilancia de la Superfinanciera sobre Colpensiones (posiblemente el decreto de creación, Decreto 2013 de 2012, no verificado). La investigación del 2026-07-26 sostuvo la distinción con fuentes secundarias, no con una norma única. **Si cambia:** se abriría o se cerraría una vía gratuita de presión. **Lo que no cambia:** ninguna superintendencia reconoce una pensión ni ordena pagos. **Ese es el punto que el agente debe dejar claro para que el usuario no pierda tiempo esperando de una queja algo que solo da un juez.**
4. **Denuncia de evasión ante la UGPP**, cuando el empleador no pagó o pagó mal. La UGPP fue creada para el seguimiento y la determinación de la adecuada, completa y oportuna liquidación y pago de los aportes al Sistema de Protección Social, y tiene facultades de cobro coactivo. *Fuente: Ley 1151 de 2007, art. 156.*
   - **Límite duro que hay que advertir:** la competencia de la UGPP cubre los **últimos 5 años** contados desde que debieron hacerse los aportes. Periodos más antiguos no los tramita. *Fuente: UGPP, canal de denuncia de evasión de aportes.*
   - La denuncia puede ser anónima y se hace por el canal de denuncias del portal de la UGPP.
5. **Acción de tutela**, típicamente por violación del derecho de petición (si no responden) o del mínimo vital y la seguridad social (si la negativa deja a la persona sin pensión). Es la vía por la que se construyó toda la línea SU-226 / SU-068 / SU-062.
6. **Demanda laboral ordinaria** ante la jurisdicción ordinaria laboral, para que se declaren el vínculo y los periodos y se ordene el pago de los aportes con intereses. Aquí sí se necesita abogado.

**Regla de asesoría del agente:** Júbilo llega hasta explicar la escalera y ayudar a preparar el paso 1. **No redacta tutelas ni demandas y no es abogado.** A partir del paso 5 deriva.

## 6. Qué prescribe y qué no

Es la pregunta que produce más miedo innecesario, y la respuesta es tranquilizadora.

| Qué | ¿Prescribe? | Fuente |
|---|---|---|
| **El derecho a la pensión** | **No.** Es imprescriptible | C-230 de 1998, C-298 de 2002, SU-567 de 2015; ver marca A |
| **Las mesadas ya causadas y no cobradas** | **Sí, a 3 años** contados hacia atrás desde la reclamación | Código Sustantivo del Trabajo, art. 488; **Ley 2452 de 2025, art. 317** (nuevo Código Procesal del Trabajo); ver marca B |
| **El recobro de cuotas partes pensionales entre entidades** | Sí, a 3 años desde el pago de la mesada respectiva | Ley 1066 de 2006, art. 4; exequible en C-895 de 2009 |
| **La competencia de la UGPP para perseguir evasión** | Alcance de 5 años hacia atrás | UGPP, canal de denuncia |

**Lo que esto significa en la práctica y hay que decirlo así:** una semana en mora de 1998 **no se pierde por vieja**. Lo que sí se puede perder son mesadas atrasadas si la persona se demora años en reclamar una pensión que ya tenía causada. La consecuencia práctica es: **reclamar la corrección no tiene fecha de vencimiento, pero reclamar la pensión sí conviene hacerlo a tiempo**.

**Marca A.** `[VERIFICAR]` **Respuesta operativa:** el agente afirma la imprescriptibilidad del derecho sin condicionales, y las tres sentencias citadas están verificadas y dicen lo que se les atribuye: la **C-230 de 1998** tumbó la prescripción de 30 años que existía para pedir pensiones; la **C-298 de 2002** separó el derecho (imprescriptible) de las mesadas causadas (prescriptibles); la **SU-567 de 2015** mantiene la posición y suma C-624 de 2006, SU-430 de 1998 y T-274 de 2007. **Falta confirmar:** si hay una unificación posterior a 2015 que sea hoy la cita de cabecera. No se encontró. **Si cambia:** solo cambiaría la cita, no la regla: una línea de casi treinta años no se revierte de un fallo a otro.

**Marca B.** `[VERIFICAR]` **CORREGIDO el 2026-07-26. Respuesta operativa:** la prescripción de 3 años sigue siendo la regla, pero **el artículo que la fija ya no es el art. 151 del Código Procesal del Trabajo de 1948, que quedó derogado**. Hoy es el **art. 317 de la Ley 2452 de 2025**, el nuevo Código Procesal del Trabajo, vigente desde el 2 de abril de 2026: las acciones que emanan de las leyes sociales prescriben en 3 años contados desde que la obligación se hizo exigible. El **art. 488 del Código Sustantivo del Trabajo sigue vigente**, porque la Ley 2452 derogó el código procesal, no el sustantivo. **Sobre la interrupción, que es donde se juega la plata:** la reclamación escrita recibida por el deudor interrumpe la prescripción por un lapso igual al original (*art. 319*), y la presentación de la demanda también, siempre que el auto admisorio se notifique al demandado dentro del año siguiente a su notificación al demandante (*art. 318*). **Falta confirmar:** el texto literal de los arts. 317 a 319 en fuente primaria; la investigación del 2026-07-26 no pudo abrir Secretaría del Senado ni Función Pública. **Si cambia:** cambiaría la cita, no los 3 años. **Trampa que esto cierra:** casi toda la guía que circula en internet sigue citando el art. 151 del código de 1948. **Citarlo hoy es citar una norma muerta.**

## 7. Guion operativo del agente cuando la calculadora reporta mora

El router ya detecta el hallazgo. Esto es lo que el agente hace con él, en orden:

1. **Reportar sin alarmar.** "Vi que hay periodos marcados en mora o como deuda presunta. Es común y no significa que perdiste esas semanas."
2. **Clasificar** con la tabla de la sección 1: ¿era empleado o independiente? ¿hay novedad de retiro en esa fecha? ¿la empresa existe todavía?
3. **Decir el efecto en el número, que depende de si las semanas ya están contadas o no.** `recuperacion.py` lo resuelve y hay que mirarlo antes de hablar, porque la intuición falla:
   - **Mora que el documento ya acredita** (fila con semanas válidas mayores que cero, que es lo normal en el formato de Colpensiones): **esas semanas YA están dentro del total impreso y dentro del conteo**. No son semanas por ganar. Lo que hay ahí es un **riesgo a la baja**: si la administradora no las convalida, el número baja. Verificado sobre un caso real: la fila en deuda presunta traía 4,29 semanas válidas y estaba dentro de las 1.236,57 del total.
   - **Filas con salario reportado y cero semanas** (sección 1 bis): esas **no** están contadas, y son las únicas de las que se puede estimar el efecto en la mesada, porque traen salario.
   - **Vacíos y déficit de tramos:** no están contados y **no se les puede estimar mesada**, porque el documento no reporta salario para ellos.
4. **Dar la regla que tranquiliza,** citando la línea de la Corte en lenguaje llano: la deuda es del empleador, no del trabajador, y el fondo estaba obligado a cobrar.
5. **Dar un solo paso siguiente,** no una lista de seis. Normalmente: pedir la corrección a la administradora con los papeles que tenga.
6. **Preguntar por los papeles** en términos cotidianos (contrato, carta de liquidación, desprendibles).
7. **Cerrar invitando a volver:** "cuando la administradora te responda, me cuentas y recalculamos con esas semanas".
8. **Si el usuario ya está cerca de la edad de pensión,** subir la urgencia: corregir antes de radicar la solicitud, porque los términos de reconocimiento no corren mientras la información esté incompleta.

**Lo que el agente nunca hace:**
- Prometer que las semanas se van a recuperar. Dice que **se pueden** recuperar y explica cómo.
- Estimar a ojo cuánto sube la mesada si se recuperan. **Desde el 2026-07-26 sí se puede estimar, pero solo con `recuperacion.py` y solo cuando el documento reporta salario para ese periodo.** Para vacíos y déficit de tramos sigue sin poderse: sin salario reportado no hay con qué calcular, y se dice cuántas semanas serían, nunca cuánta plata.
- **Prometer que recuperar semanas sube la mesada.** No siempre. En el RPM, semanas cotizadas sobre un salario por debajo del promedio entran al IBL y lo tiran hacia abajo: en el caso real, acreditar el mes pendiente **bajaba** la mesada un 0,65%. Sirve para llegar al requisito de semanas, no necesariamente para subir el monto, y son dos cosas distintas que hay que separar al hablar.
- Dar un plazo de resolución que no esté documentado.
- Sumar por su cuenta las semanas en mora al total del cálculo.

## 8. Fuera de alcance

Lo siguiente **no lo cubre este documento ni V1**. El agente lo dice y deriva:

- **Redactar tutelas, derechos de petición formales o demandas laborales.** Júbilo explica qué hay que pedir y ante quién; no produce el escrito ni actúa como apoderado.
- **Litigio contra el empleador o contra la administradora.** Abogado pensional.
- **Reliquidación de pensiones ya reconocidas** por semanas o IBC mal contados. Ya está fuera de alcance en `faq-y-glosario.md` y sigue estándolo.
- **Cálculo del valor del cálculo actuarial o del título pensional** que debe trasladar un empleador omiso. Lo liquida la administradora.
- **Mora en aportes de salud, riesgos laborales, cesantías o parafiscales.** Júbilo es pensional; se deriva a la UGPP o al Ministerio del Trabajo según el caso.
- **Sanción moratoria laboral del art. 65 del CST** (la de salarios y prestaciones no pagados al terminar el contrato). Es materia laboral, no pensional.
- **Reconstrucción de la historia laboral de una empresa liquidada** sin ninguna prueba documental. El agente explica las vías (certificado de la Cámara de Comercio, entidad sucesora, testigos en juicio) y deriva.
- **Rutas de corrección de Protección, Porvenir y Colfondos**, aún no documentadas en `tramites-y-consultas.md`. El agente lo dice con honestidad y orienta al canal de atención en lugar de inventar una ruta.
