# Palancas y escenarios: el motor que le falta a Júbilo

> **Escrito el:** 2026-09-18, al cerrar la sesión que ejecutó `mejoras-por-hacer.md`.
> **De dónde sale:** de mirar los dos reportes de cierre de ejemplo. El veredicto de Santiago fue: el formato está bien, el contenido de las secciones 4 y 5 no. Y la frase que enmarca todo el documento: **"este es el verdadero poder del agente que estamos construyendo, y creo que nos falta profundizarlo más allá del reporte. El reporte es solo un síntoma."**
> **Estado: EJECUTADO Y DESPLEGADO el 2026-09-19.** Este archivo se conserva
> porque explica el porqué de cada decisión, pero ya no es una lista de
> pendientes. Lo que se construyó y lo que quedó abierto está abajo, en la
> sección 0.

---

## 0. Qué pasó con esto (cierre del 2026-09-19)

Las dos decisiones de la sección 4 las tomó Santiago y se ejecutaron los seis
pasos de la sección 5. **Todo está desplegado en producción.**

**La decisión A.** Del grupo 3 entraron las palancas 7, 8, 9, 10 y 12. Quedó
fuera la 11 (el momento de reclamar) por segmento chico, y se descartó la idea
de comparar el aporte voluntario contra otros vehículos de ahorro: en
aislamiento funciona bien.

**Lo que se construyó:**

| Pieza | Dónde |
|---|---|
| El director de orquesta | `calculadora/palancas.py` (+ 361 comprobaciones) |
| El detector de la palanca 10 | `calculadora/anomalias.py`, siete tipos con su confianza |
| El aplazamiento de la palanca 7 | `meses_aplazamiento` en `rpm.py` y `rais.py` |
| El detalle por AFP y fondo | `RENDIMIENTO_REAL_POR_AFP` en `datos_sistema.py` |
| Las secciones 4 y 5 del reporte | `reporte/armar_reporte.py`, ya sin redactar nada |
| El envío automático | `bot/bot.py`, a los 30 minutos de silencio |

**Seis cosas que se aprendieron construyéndolo y que no estaban previstas:**

1. **En el RPM aplazar puede BAJAR la mesada.** Cuando la tasa ya está en su
   tope y el IBL que manda es el de toda la vida, cada mes extra cotizando por
   debajo del promedio histórico lo diluye. Caso 04: aplazar 24 meses cuesta
   $30.000 al mes. La palanca sale negativa y no se ofrece.
2. **El traslado de régimen no puede ir en el ranking.** Salió como la palanca
   de mayor impacto y ordenarlo por impacto equivale a recomendarlo.
3. **Hay un segmento al que ninguna palanca le sirve:** quien queda en la
   garantía de pensión mínima. Su reporte salía vacío. Ahora se le dice que lo
   que está en juego no es cuánto recibe, es calificar.
4. **La palanca 9 prometía cinco veces lo posible** entre los 57 y los 60 años,
   porque la marca de convergencia solo aparece al 100%. Ahora se escala por la
   fracción del saldo que la ley deja mover.
5. **Cinco de los seis bugs no fallaban, mentían.** Una mesada de $6.094
   millones, un filtro con sesgo que ocultaba la comparación de régimen justo a
   quien le convenía quedarse, texto del PDF escrito fuera de la hoja, y un bot
   sin `JobQueue` cuyo log decía que todo iba bien.
6. **Al desplegar, el bot encoló cinco reportes retroactivos** para personas que
   habían conversado días antes. No salieron porque faltaba una dependencia.
   Santiago decidió marcarlas como cerradas: la función arranca solo para
   conversaciones nuevas. Queda el rastro en `eventos` como
   `cierre_omitido_retroactivo`.

**Lo que sigue abierto:**

- **Medir el segmento de la garantía mínima.** Es 1 de 6 en el set dorado, que
  no es una muestra representativa. Si en usuarios reales es alto, el producto
  necesita una segunda narrativa completa, no solo un aviso.
- **La palanca 11** (el momento de reclamar), que quedó fuera y sería barata
  ahora que existe el parámetro de aplazamiento.
- **Los datos por AFP se refrescan a mano** con `analisis/rendimiento_afp.py`.
  Nadie lo tiene agendado.

---

## Cómo usar este archivo

Ábrelo en una sesión limpia de Claude Code, en el repo de Júbilo. Lee antes el `AGENTS.md` del repo: manda sobre todo lo que está aquí.

**Empieza por la sección 4, que son las decisiones de Santiago.** Hay dos, y las dos están pendientes. No se construye nada hasta que las responda, porque definen el alcance del módulo entero.

---

## 1. El problema, con nombre propio

El reporte de cierre salió con esta palanca:

| Lo que decía | Por qué está mal |
|---|---|
| "Cotizar sobre un salario base mayor, si puedes" / "cada peso que entra a tu cuenta rinde hasta que te pensiones" | Es genérico, no es accionable, y la parte de la derecha es una obviedad. Palabras de Santiago: "eso es totalmente irrelevante, eso es obvio" |

**Lo que tiene que decir en su lugar:** *"si te suben el sueldo un 10%, tu mesada sube $177.026 al mes"*. Específica, cuantificada, y atada a una acción que la persona puede tomar.

Y la sección de escenarios tenía el mismo problema al revés: ofrecía **"si dejas de cotizar hoy"** a alguien de 27 años. Eso no es un escenario, es una amenaza, y no motiva a nada. Los escenarios existen para mover a la acción, así que tienen que combinar las palancas buenas, no mostrar el peor caso.

---

## 2. Lo que YA existe y no está conectado (verificado el 2026-09-18)

Esto es lo más importante de todo el archivo, porque cambia el tamaño del trabajo: **casi todo el motor está construido y no lo llama nadie.**

### 2.1 El motor de selección: `calculadora/aportes_voluntarios.py`

Son 1.045 líneas. Se comprobó con `grep`: **ninguna otra parte del repo lo importa.** Solo lo ejecutan sus propias pruebas. El orquestador no lo usa, el reporte no lo usa, y el `system-prompt.md` ni lo menciona en el mapa del kit.

Su función `comparar_alternativas_pensionales(regimen, tiene_capacidad_de_pago, es_independiente, ingreso_respalda_ibc_mayor, sisben_1_2_o_3)` ya devuelve, por persona, qué palancas aplican y **cuáles no, con el motivo**. Y ya sabe cosas finas que costaría mucho volver a escribir:

- A un asalariado le descarta sobrecotizar: *"su IBC lo fija su salario, no lo escoge"*.
- Le descarta BEPS a quien tiene capacidad de pago, y lo llama por su nombre: *"es un ERROR DE SEGMENTO. Los BEPS no mejoran una pensión, son para quien no alcanza a cotizar por el mínimo"*.
- Ya trae el matiz del IBL: *"subir la base tres años no mueve tanto el promedio"*, porque el IBL se calcula sobre 10 años o toda la vida laboral si resulta superior (Ley 100 art. 21).
- Cada alternativa trae su norma y su límite de alcance escrito.

### 2.2 El motor de cuantificación: ya responde, hay que llamarlo

`rais.diagnosticar(caso, ibc_futuro=..., densidad_futura=...)` acepta los supuestos como parámetro. Corriendo el caso 01 del set dorado, el 2026-09-18:

| Palanca | Resultado |
|---|---|
| Sueldo +10% | mesada de $2.090.605 a $2.267.631. **$177.026 más al mes, +8%** |
| Sueldo +20% | **$354.052 más al mes, +17%** |
| Sueldo +30% | **$531.078 más al mes, +25%** |
| Cotizar el 90% del tiempo en vez del 80% | **$230.546 más al mes, +11%** |
| Cotizar el 100% del tiempo | **$452.857 más al mes, +22%** |

Esas son exactamente las frases que Santiago pidió. Salen de correr la calculadora, no de estimar.

### 2.3 Las otras piezas que ya existen

| Qué cuantifica | Dónde |
|---|---|
| Aportes voluntarios, con su ahorro tributario y condiciones de permanencia | `aportes_voluntarios.evaluar_aporte_voluntario()` |
| Cuánto cuesta cotizar más y en cuánto tiempo se recupera | `costo_y_retorno.py` (breakeven, ganancia neta, mesada neta de salud) |
| Recuperar semanas en mora | `recuperacion.simular()` |
| Quedarse contra trasladarse de régimen | `comparador.comparar()` |

**Conclusión: no hay que construir el motor. Hay que construir el director de orquesta.**

### 2.4 Un acople frágil que ya se arregló, para que no se repita

El reporte leía la mesada de `recuperacion.base.mesada_banda`. Ese número **no responde a los supuestos de palanca**: si se pide el diagnóstico con un sueldo futuro distinto, el escenario cambia y `recuperacion.base` no se entera. Daba el mismo número por casualidad en el caso base y se habría roto justo al empezar a mostrar palancas. Ahora lee del escenario del propio diagnóstico. **Al construir palancas, verificar siempre de qué clave sale cada cifra.**

---

## 3. Lo que hay que construir: `calculadora/palancas.py`

Un módulo nuevo que haga cuatro cosas, en este orden. Python puro, sin IA, con su `probar_palancas.py`, como todo lo demás de `calculadora/`.

1. **Elegir.** Qué palancas le aplican a ESTA persona. Se apoya en `comparar_alternativas_pensionales`, que ya segmenta.
2. **Cuantificar.** Cada palanca se corre por la calculadora y devuelve el efecto en pesos de mesada al mes, y en fecha de pensión cuando aplique. **Nunca se estima.**
3. **Ordenar.** Por impacto. Es lo que decide qué va primero en el reporte y qué le ofrece Júbilo en la conversación.
4. **Combinar.** Los escenarios son combinaciones de las mejores palancas, no el peor caso.

**Reglas que este módulo no puede romper**, y todas vienen de decisiones ya tomadas del proyecto:

- **La IA no calcula.** El número sale de aquí, no del modelo.
- **No se recomienda administradora, fondo ni portafolio.** Es asesoría de inversión, actividad regulada. Se muestra el dato y la persona decide.
- **No se recomienda el traslado de régimen.** Se muestran los dos escenarios y se dice que la doble asesoría obligatoria es un requisito de ley que esto no reemplaza.
- **Una palanca que no se puede cuantificar se nombra sin número**, nunca con uno inventado.
- **Ojo con el error de segmento.** Ofrecerle aportes voluntarios a quien no tiene con qué es tan malo como ofrecerle BEPS a quien sí.

---

## 4. LAS DOS DECISIONES DE SANTIAGO (no se construye nada antes)

### 4.1 Decisión A: qué palancas entran al banco

Santiago pidió pensar esto creativamente y escoger de una lista. **Presentarle estas opciones y esperar su respuesta.** Están agrupadas por qué tan listas están.

**Grupo 1: se pueden cuantificar hoy, sin construir nada nuevo.**

| # | Palanca | Cómo se le diría | Qué hace falta |
|---|---|---|---|
| 1 | **Que te suban el sueldo** | "si te suben el sueldo un 10%, tu mesada sube $177.026 al mes" | Nada, ya funciona |
| 2 | **Cerrar las lagunas hacia adelante** | "si cotizas todos los meses en vez del 80% del tiempo, son $452.857 más al mes" | Nada, ya funciona |
| 3 | **Recuperar las semanas en mora** | "tu empleador debe X semanas: recuperarlas te adelanta la pensión N meses" | Nada, `recuperacion.py` ya lo simula |
| 4 | **Quedarte o trasladarte de régimen** | "en Colpensiones tu mesada sería X, en tu fondo entre Y y Z" | Nada, `comparador.py` ya lo hace |

**Grupo 2: el motor existe, falta un dato de la persona.**

| # | Palanca | Cómo se le diría | Qué dato falta |
|---|---|---|---|
| 5 | **Aportes voluntarios** | "$500.000 al mes durante 10 años te suben la mesada $X, y además te ahorran $Y de impuesto de renta este año" | Si le sobra plata, y su ingreso anual para el cálculo tributario |
| 6 | **Sobrecotizar** (solo independientes) | "si cotizas sobre el 60% de tu ingreso en vez del 40%, tu mesada sube $X y te cuesta $Y al mes" | Si es independiente |

**Grupo 3: ideas nuevas, hay que decidir si valen.** Estas son la parte creativa que pidió Santiago.

| # | Palanca | Por qué podría valer | El riesgo |
|---|---|---|---|
| 7 | **Trabajar un año más** | Es la palanca más potente y la que menos se piensa: suma semanas, sube el IBL y acorta el tiempo que la pensión tiene que durar. Los tres efectos van en la misma dirección | Ninguno técnico. Puede sonar a "trabaja más", así que el tono importa |
| 8 | **Cambiar de administradora** | Ya tenemos el dato primario por AFP. Dentro del RAIS es libre y no tiene la ventana de diez años | Es el borde de la asesoría de inversión. Santiago ya cerró el lenguaje para esto el 2026-09-18, ver `system-prompt.md` |
| 9 | **Elegir portafolio** | Con el dato primario, la diferencia entre conservador y mayor riesgo son casi 2 puntos reales, que es más que la diferencia entre AFP | Mismo borde que la 8, y la convergencia por edad se lo prohíbe a los mayores |
| 10 | **Corregir la historia laboral** | No es plata nueva: es recuperar semanas que ya se cotizaron y están mal registradas. Suele ser la de mejor relación esfuerzo contra resultado | Solo aplica si hay filas con salario y cero semanas, o inconsistencias |
| 11 | **El momento de reclamar** | Para quien ya cumple requisitos: reclamar hoy contra esperar. Cada mes que espera es un mes de mesada que no cobra, pero también más semanas | Solo aplica a un segmento chico. Hoy el system prompt ya toca el tema |
| 12 | **La densidad del último tramo** | En el RPM el IBL se calcula sobre los últimos 10 años o toda la vida, la que sea mayor. Para alguien a 10 años de pensionarse, lo que cotice ahora pesa muchísimo más | Es fino y muy valioso cerca del retiro. Hay que verificar que la calculadora lo aísle bien |

**La pregunta para Santiago:** cuáles del grupo 3 entran, y si falta alguna que no esté en la lista.

### 4.2 Decisión B: cuándo se preguntan los datos que faltan

**Ya decidido por Santiago el 2026-09-18:** *"me gusta preguntar en medida que se vayan abriendo esas ramas y sea relevante"*.

O sea: **nada de un cuestionario al principio.** La pregunta aparece cuando la palanca se vuelve relevante, y solo entonces. Lo que hay que diseñar es el disparador de cada una:

| Dato | Cuándo se pregunta |
|---|---|
| ¿Asalariado o independiente? | Cuando se va a hablar de subir la base. A un asalariado no se le ofrece sobrecotizar, así que la respuesta cambia la palanca que se muestra |
| ¿Te sobra plata para ahorrar? | Solo antes de ofrecer aportes voluntarios. Nunca antes, porque es una pregunta incómoda y solo sirve para eso |
| ¿Cuál es tu ingreso anual? | Solo si dijo que sí a la anterior, y solo para calcular el ahorro tributario |

**Lo que hay que resolver al construir:** cómo se guarda una respuesta para no volver a preguntarla, y cómo se recalculan las palancas cuando llega un dato nuevo. Hoy el diagnóstico se corre una vez y se acabó.

---

## 5. El orden sugerido de trabajo

1. Presentarle a Santiago la decisión A y esperar respuesta. No arrancar antes.
2. Construir `calculadora/palancas.py` con las palancas del grupo 1, que no necesitan datos nuevos, y su prueba.
3. Conectarlo al reporte: las secciones 4 y 5 salen de ahí y se ordenan por impacto.
4. Conectarlo al `system-prompt.md`, que es lo que Santiago llamó "más allá del reporte": hoy Júbilo improvisa las palancas en la conversación.
5. Después, las palancas del grupo 2 con sus preguntas por rama.
6. Lo del grupo 3 que Santiago haya aprobado.

---

## 6. Lo que quedó pendiente de la sesión anterior y depende de esto

- **El reporte de cierre no está conectado al bot.** El módulo `reporte/armar_reporte.py` existe y funciona, pero nadie lo llama. Falta el disparador por inactividad (`JobQueue` de python-telegram-bot) y mandar el PDF por Telegram.
- **La pregunta abierta de satisfacción (bloque 4 de `mejoras-por-hacer.md`)** va después de mandar el reporte, así que usa el mismo disparador y se construye junto con él.
- **Nada de lo de la sesión anterior está desplegado.** El servidor sigue con la versión previa al commit `76825f7`. Desplegar es una decisión aparte y no se hace con gente conversando.

---

## 7. Antes de dar cualquier cambio por bueno

Está en el `AGENTS.md`, y lo que más se olvida:

- **Las pruebas primero.** Las once suites de `calculadora/`, más `bot/probar_registro.py`, `bot/probar_bot.py`, `tramites/probar_pedir_historia.py` y `reporte/probar_armar_reporte.py`. Quince en total, todas en verde.
- **Si tocas una cifra que usa la proyección, las pruebas se van a poner rojas a propósito.** Eso no es un estorbo: es el sistema avisando. Se revisa una por una y se actualiza el valor fijado solo cuando se entiende por qué cambió.
- **Nunca probar contra el bot de producción.**
