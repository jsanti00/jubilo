# Aportes voluntarios y sobrecotización - Documento 22 del kit

> **Última actualización:** 2026-07-26. **Estado:** nuevo. Construido con investigación en fuentes oficiales tras una sesión de role-play (2026-07-26) donde el agente no supo responder la pregunta más natural de un usuario con dinero: "¿puedo meterle más plata a mi pensión?".
> **Por qué existe:** el kit cubría cómo se calcula la pensión y qué pasa si no alcanza, pero no **cómo mejorarla deliberadamente**. Es la pregunta del usuario con mayor disposición a pagar por la asesoría.

## 1. La pregunta y la respuesta corta

**"Tengo con qué. ¿Puedo poner más plata y pensionarme mejor?"**

La respuesta depende del régimen, y es asimétrica:

| Régimen | ¿Se puede aportar más? | Cómo |
|---|---|---|
| **RAIS** (fondos privados) | **Sí, directamente** | Aportes voluntarios a la cuenta individual: entran al saldo y capitalizan |
| **RPM** (Colpensiones) | **No hay vehículo de aporte voluntario** | La única vía es un IBC más alto (con límites) y más semanas |

**La razón de la asimetría:** en RAIS la pensión sale de un saldo propio, así que meter plata al saldo mejora la pensión de forma mecánica. En RPM la pensión sale de una fórmula (IBL por tasa de reemplazo) que no mira cuánto capital se aportó: mira el promedio salarial y las semanas. Plata suelta no tiene por dónde entrar a esa fórmula.

**Consecuencia de asesoría:** a un afiliado a Colpensiones que quiere "invertir" en su pensión hay que decirle que no existe ese producto dentro del régimen, y llevarlo a las dos palancas que sí existen (sección 2) más los vehículos de ahorro por fuera del sistema.

## 2. RPM: las dos únicas palancas

1. **Subir el IBC** dentro de lo que permite su situación (sección 3). Mueve el IBL, que es el número sobre el que se liquida.
2. **Sumar semanas por encima del mínimo:** cada bloque completo de 50 semanas adicionales sube la tasa de reemplazo **1,5 puntos**, con techo del 80% del IBL. *Fuente: Ley 100 art. 34, mod. Ley 797 de 2003 art. 10; detalle en `reglas-rpm.md` sección 5.*

Nada más. No hay cuenta individual, no hay rendimientos, no hay aporte extra que capitalice.

## 3. Sobrecotizar: lo que la ley permite y lo que no resuelve

**Lo que dice la ley:** el 40% del artículo 89 de la Ley 2277 de 2022 es una **base mínima**, y el techo del sistema es 25 SMLMV (Ley 100 art. 18). Entre esos dos límites, **la ley no prohíbe cotizar sobre una base mayor a la que resultaría de los ingresos**.

**Lo que la ley no resuelve, y es el riesgo real:** subir mucho la base justo en los años que entran a la liquidación del IBL (los últimos 10) es exactamente el patrón que las entidades revisan. El IBL se calcula sobre el promedio de los últimos 10 años **o de toda la vida laboral si resulta superior** (Ley 100 art. 21), y esa regla del promedio largo es, en sí misma, la principal defensa del sistema contra los aumentos de última hora: subir la base tres años no mueve tanto un promedio de diez.

`[VERIFICAR]` **La marca más importante de este documento. Respuesta operativa del agente:** cotizar por encima del mínimo no está prohibido, pero **un salto abrupto en los últimos años antes de pensionarse es una zona gris que el agente no resuelve y deriva a abogado pensional**, sobre todo si el aumento no corresponde a un aumento real de ingresos. **Falta confirmar:** no se ubicó jurisprudencia de la Corte Suprema, Sala Laboral, sobre independientes que inflan su IBC al final. Lo que sí existe es doctrina análoga sobre servidores públicos que aumentaron su IBL con **encargos de corta duración** al final de la carrera, invalidados por fraude a la ley y abuso del derecho en protección del erario. Es extrapolable en principio, no hay fallo puntual que lo aplique a un independiente. **Si cambia:** si aparece jurisprudencia que lo valida, esto pasa de zona gris a palanca legítima y es una de las recomendaciones más valiosas que puede dar Júbilo; si aparece jurisprudencia que lo castiga, pasa a advertencia dura.

`[VERIFICAR]` **CORREGIDO el 2026-07-26. Respuesta operativa:** el agente **ya no menciona ningún límite del 25% al crecimiento del IBL**, porque esa regla **no existe en el Acto Legislativo 01 de 2005**. La investigación revisó el texto completo del acto legislativo en dos fuentes y la única mención al 25% es otra cosa: el parágrafo transitorio 1 fija que desde el 31 de julio de 2010 no pueden causarse pensiones superiores a **25 salarios mínimos** con cargo a recursos públicos. Es un tope de monto, no un límite de crecimiento. **Cómo se cayó en el error:** se confundió "25 SMLMV" con "25%". Es la misma clase de trampa ya documentada en el README (citar como viva una norma que dice otra cosa), y por eso queda escrita aquí en vez de borrada. **Falta confirmar:** si algún límite de esa naturaleza existe en otra norma (un régimen especial, una circular de Colpensiones). No se encontró en la Ley 100 art. 21 ni en el Decreto 1158 de 1994. **Si cambia:** si apareciera una regla así, sería un argumento adicional para desaconsejar el salto de última hora. **Mientras tanto, la advertencia se sostiene sola** y sin cita inventada: la defensa real del sistema es la que ya está en el párrafo de arriba, el promedio de toda la vida laboral del art. 21, más la doctrina de fraude a la ley de la marca anterior.

**Cómo lo dice el agente, sin asustar ni prometer:**

> "Ponerte al día con lo que realmente ingresas no tiene discusión y te conviene. Cotizar por encima de lo que te corresponde no está prohibido, pero si el salto es grande y justo antes de pensionarte, entra en un terreno que no está resuelto y que prefiero que revises con un abogado pensional antes de mover nada."

## 4. RAIS: aportes voluntarios y excedentes

**Aportes voluntarios a la cuenta individual.** Entran al saldo, capitalizan con el perfil de fondo elegido y aumentan la mesada o adelantan la fecha de pensión. *Fuente: Ley 100 de 1993; compilación en el Decreto 1833 de 2016.* El tratamiento tributario (renta exenta, retiros, el límite del 30% y las 3.800 UVT) está en `tributario-pensional.md`, incluida la trampa del pensionado anticipado que quiere retirar exento (sección 7 bis).

**Excedentes de libre disponibilidad.** Cuando el saldo supera lo necesario para financiar una pensión de referencia (**70% del IBL**, con tope de 15 salarios mínimos), el afiliado puede retirar el excedente. *Fuente: Ley 100 art. 85.* Es la contracara del aporte voluntario: quien sobreahorra en RAIS no pierde la plata, la puede sacar.

**Contraste que el agente debe hacer explícito cuando venga al caso:** el afiliado a un fondo privado que aporta de más puede recuperar el excedente; el afiliado a Colpensiones que cotiza de más **no recupera nada**, porque su aporte va a un fondo común. Es una diferencia de fondo entre regímenes y pesa en la decisión de traslado cuando la ventana sigue abierta (`reglas-traslados.md`).

## 5. Lo que no es un aporte voluntario

- **BEPS:** no es un vehículo para mejorar una pensión, es un mecanismo para quien **no logra** cotizar por salario mínimo (Sisbén 1, 2 y 3), con aporte anual mínimo de 6 salarios mínimos diarios. *Fuente: Ley 1328 de 2009 art. 87.* Detalle en `sin-pension-alternativas.md`. Ofrecerlo a alguien con capacidad de pago es un error de segmento.
- **Ahorro por fuera del sistema** (AFC, voluntarias en fondos, inversiones): puede ser la respuesta correcta para un afiliado a Colpensiones con plata, pero **no es pensión** y no se presenta como tal. El tratamiento tributario está en `tributario-pensional.md`; la decisión de inversión está fuera del alcance de Júbilo.
- **Afiliados voluntarios:** figura para quien no tiene obligación legal de cotizar (estudiantes, colombianos en el exterior) y quiere afiliarse. `[VERIFICAR]` **Respuesta operativa:** existe la figura y permite afiliarse por cuenta propia. **Falta confirmar:** la norma exacta vigente en 2026 (probablemente Decreto 692 de 1994, compilado en el Decreto 1833 de 2016). **Si cambia:** cambia el procedimiento de afiliación, no la existencia de la figura.

## 6. Regla de accionabilidad (por qué este documento existe)

Antes de ofrecer cualquier palanca de este documento, el agente verifica **que el usuario pueda accionarla**:

| Antes de decir... | Verifica que... |
|---|---|
| "sube tu base de cotización" | sea independiente **y** tenga ingreso que lo respalde (o esté subcotizando) |
| "haz aportes voluntarios" | esté en RAIS, no en Colpensiones |
| "acumula más semanas" | le falten semanas y tenga tiempo antes de la edad |
| "trasládate de régimen" | la ventana siga abierta (10 años antes de la edad, `reglas-traslados.md`) |

**Una palanca que el usuario no puede accionar no es un consejo: es ruido, y cuesta más confianza que un "no se puede" dicho a tiempo.** Regla completa en `system-prompt.md`.
