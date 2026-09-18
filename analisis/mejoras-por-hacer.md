# Mejoras de Júbilo: lo que sale del primer feedback real

> **Origen:** las cinco primeras conversaciones reales del bot, la noche del 16 de septiembre de 2026, más la nota de voz de uno de los usuarios de prueba.
> **Escrito el:** 2026-09-18. **Ejecutado el:** 2026-09-18, en la misma sesión.
> **Estado:** casi todo hecho. Lo que queda son dos cosas que dependen de decisiones o de documentos que hoy no están, y quedan marcadas abajo.
> **Nada desplegado todavía.** Todo está en el repo, con las pruebas en verde, pero el servidor sigue con la versión anterior: desplegar es una decisión aparte, y no se hace con gente conversando.

---

## Estado de cada bloque

| Bloque | De qué es | Estado |
|---|---|---|
| 1 | Que la gente llegue con el documento | **Hecho**, menos una verificación que necesita una historia laboral partida real |
| 2 | Que no parezca caído | **Hecho**, las cuatro cosas, con pruebas |
| 3 | El diagnóstico: convergencia de multifondos y perfil | **Hecho.** Norma verificada en texto primario y modelada en la calculadora. El 3.2 no entra, por decisión de Santiago |
| 4 | Medir si sirvió | **Diseñado y bloqueado:** Santiago lo quiere como pregunta abierta después del reporte de cierre, así que espera al bloque 6 |
| 5 | Pedir el documento a Colpensiones | **Hecho.** La prueba de acceso salió bien y el módulo quedó construido |
| 6 | El reporte de cierre | **No se construye todavía:** Santiago pidió validar la estructura primero. La propuesta está abajo, lista para su visto bueno |
| 7 | Llevarlo a WhatsApp | **Análisis hecho.** Informe en `analisis/whatsapp-viabilidad.md` |
| 8 | Bajar el costo | **Primer paso hecho** (separar caché de tokens frescos y sacarlo en el reporte). El resto sigue siendo análisis |

**Lo que Santiago decidió el 2026-09-18, y por eso ya no está pendiente:**

- **Bloque 3.2, el techo legal en el diagnóstico: NO entra.** Júbilo lo sigue manejando en conversación cuando aparece.
- **Bloque 4, el micro-feedback:** entra, pero **no como escala de 1 a 5**: como una **pregunta abierta**, al final de todo, después de mandar el reporte de cierre.
- **Bloque 6, el formato:** todavía no se decide. Primero se valida la estructura.

**Las dos únicas cosas que quedan abiertas:**

1. **El reporte de cierre (bloque 6).** Falta que Santiago valide la estructura propuesta y escoja formato.
2. ~~Si el reporte de un fondo trae los periodos de los fondos anteriores con salario.~~ **RESUELTO el 2026-09-18**, con siete historias laborales reales de la carpeta de ejemplos. La respuesta es la opción (a) de las tres que planteaba este archivo: **sí los trae, y con IBC y fechas completas.** Así que **con un solo documento alcanza**, incluso con historia partida, y el system prompt ya no pide dos. El detalle y sus límites están en `kit-contexto/tramites-y-consultas.md`.

---

## Cómo usar este archivo

Es un prompt. Ábrelo en una sesión limpia de Claude Code, en el repo de Júbilo, y pídele que empiece por el bloque que quieras atacar. Lee antes el `AGENTS.md` del repo: manda sobre todo lo que está aquí.

**El orden recomendado** (del original, se conserva porque explica por qué se atacó en ese orden): los bloques 1 y 2 son los que mueven el embudo y son los más baratos de hacer. El 3 arregla un error de precisión que hoy afecta a quien está cerca de pensionarse. El 5 empieza y puede terminar en una sola prueba. El 6 es producto nuevo. El 7 y el 8 son decisiones grandes que hoy solo necesitan análisis.

---

## Lo que pasó, en una página

El bot se compartió con cinco personas. Tres recibieron diagnóstico, dos nunca mandaron el documento. Había tres bugs que cortaban el flujo del documento y se arreglaron esa misma noche, así que estos números están medidos con el bot roto durante buena parte del rato.

**Los números de esa noche**

| Dato | Valor |
|---|---|
| Vieron el aviso | 4 personas |
| Escribieron algo | 5 personas |
| Mandaron su historia laboral | 3 personas |
| Recibieron diagnóstico | 3 personas |
| Turnos totales | 51 |
| Respuesta típica (p50) | 8,6 s |
| Respuesta lenta (p95) | **319,9 s** |
| Espera en fila (p95) | 0,0 s (nadie coincidió nunca) |
| Costo total | US$ 8,22 |
| Costo por persona | **US$ 1,64** |

**Los cuatro hechos que importan**

- Donde se cae la gente es en conseguir y mandar el documento. Ninguna de las tres que llegó lo hizo sola.
- Una persona mandó un pantallazo del saldo de su fondo creyendo que era la historia laboral.
- La conversación más larga (29 turnos) tardó 57 minutos en llegar al diagnóstico, 47 de ellos atascada en el bug.
- Mientras esperaba, esa persona probó `/restart`, `/refresh`, `/clear` y `/start`, convencida de que el bot estaba caído. Y recibió un mensaje del CLI en inglés.

El reporte completo, con las cinco conversaciones textuales, está en `analisis/datos/` (la carpeta está en el `.gitignore`; si no está, se regenera con `analisis/traer_datos.sh`).

---

## Bloque 1. Que la gente llegue con el documento: HECHO el 2026-09-18

Es el cuello de botella del embudo. Dos de cinco no pasaron de aquí.

**Qué quedó hecho, resumido:**

| Punto | Estado |
|---|---|
| 1.1 Qué es y qué no es la historia laboral | **Hecho.** Documento nuevo del kit: `kit-contexto/que-es-la-historia-laboral.md`, con la tabla de los cinco documentos que la gente manda por error y qué es cada uno. Registrado en el mapa del kit del system prompt |
| 1.2 Abrir preguntando el fondo | **Hecho.** La bienvenida (`bienvenida-y-aviso.txt`, versión 1.2) ya pregunta el fondo y ya dice qué es y qué no es el documento. El system prompt le prohíbe volver a preguntarlo |
| 1.3 El PDF de instrucciones | **Resuelto, pero no como decía este archivo.** Ver la nota de abajo: el PDF de `~/Downloads` no era de Colpensiones |
| 1.4 Feature 1, el rendimiento por AFP | **Investigación hecha** (`kit-contexto/rendimiento-por-administradora.md`). El feature **no se activa**: el paso 2 es una decisión de Santiago |
| 1.4 Feature 2, historia partida | **Investigado y parcialmente resuelto.** Ver la nota en el punto 1.4 |
| 1.5 Vacíos de trámite por fondo | **Hecho.** Investigación en `kit-contexto/fuentes-tramites/descarga-historia-laboral-por-fondo.md` y el vacío de Skandia cerrado en `tramites-y-consultas.md` |

### 1.1 Explicar qué es la historia laboral, y sobre todo qué no es

El feedback textual del usuario de la conversación de 29 turnos: **no sabía qué era el documento que le estaban pidiendo.** La persona del común no distingue la historia laboral de otros papeles pensionales.

Lo que hay que añadir al kit (`kit-contexto/`):

- **Qué es:** el reporte que emite el fondo con todas las semanas cotizadas de toda la vida laboral, empleador por empleador.
- **Cómo reconocerlo:** en Colpensiones se titula "REPORTE DE SEMANAS COTIZADAS EN PENSIONES", trae un total de semanas y un detalle por empleador con fechas, y suele tener cinco páginas.
- **Qué NO es**, con nombres propios, porque es lo que la gente manda por error:
  - El saldo o extracto de la cuenta individual (pasó de verdad: alguien mandó el pantallazo del saldo).
  - El extracto de cesantías.
  - El certificado laboral que da el empleador.
  - El certificado de afiliación.
  - La proyección de pensión que a veces ofrece el propio fondo.

Ojo con el nombre: en la conversación se usó "certificado laboral" para referirse a esto, y **certificado laboral es otra cosa** (lo expide el empleador). El documento se llama **historia laboral**. Esa confusión de nombre es parte del problema a resolver, no algo que el kit deba heredar.

### 1.2 Abrir preguntando el fondo, sin dar por hecho que sabe el nombre del documento

Hoy Júbilo pregunta el fondo y da el paso a paso, pero solo después de que la persona dice que no sabe. En tres de cinco conversaciones se gastó un turno en eso. La bienvenida debería llevar ya la pregunta del fondo.

### 1.3 Entregar el PDF de instrucciones del propio fondo

**OJO, este punto partía de un dato equivocado y hay que dejarlo escrito.** El archivo `~/Downloads/como-consultar-tu-historia-laboral.pdf` **no es de Colpensiones: es la guía de Skandia**, y ya estaba en el repo desde el 2026-07-21, en `kit-contexto/fuentes-tramites/skandia-guia-historia-laboral.pdf` (mismo archivo, se comprobó por huella). No había nada que mover, y sus pasos ya estaban incorporados en texto en `tramites-y-consultas.md`.

**Lo que sí salió de volver a leerlo, y es el hallazgo útil:** esa guía dice que la pantalla de historia laboral de Skandia muestra el desglose de semanas separado en Skandia, otros fondos y Colpensiones. Eso es evidencia directa para la pregunta abierta del punto 1.4, y está recogida en la sección nueva de `tramites-y-consultas.md` sobre historia partida.

**Lo que sigue pendiente de este punto:** conseguir guía oficial de Protección, Porvenir y Colfondos. La ruta de cada uno ya está documentada en texto, que es lo que se lee en el chat, así que el PDF es un lujo y no un bloqueo.

<details>
<summary>El texto original del punto, para historial</summary>

Hay un PDF de Colpensiones que explica cómo consultar la historia laboral: `~/Downloads/como-consultar-tu-historia-laboral.pdf` (3,4 MB).

Pendiente de hacer:

- Moverlo al repo, a `kit-contexto/guias/`, para que viaje con el despliegue.
- Leerlo e incorporar los pasos al kit en texto, porque el texto se lee en el chat y el PDF hay que abrirlo.
- **Decidir si además se envía el PDF por Telegram.** El bot puede mandar archivos. A favor: es material oficial del fondo y da confianza. En contra: 3,4 MB, y quien está perdido probablemente no abra un PDF. Recomendación: los pasos en texto primero, y ofrecer el PDF solo si la persona lo pide o se atasca.
- Conseguir el equivalente de Protección, Porvenir, Colfondos y Skandia, o escribirlo si el fondo no lo publica.

</details>

### 1.4 Saber en qué fondo está: hoy se usa para una sola cosa, y habilita dos más

**Cómo pasó, textual.** La bienvenida dice "envíame tu historia laboral, si no la tienes te digo cómo descargarla". La persona respondió "No sé cómo descargarla" (19:21). **Júbilo fue el que preguntó el fondo**, no la persona: "¿En qué fondo estás afiliado: Colpensiones, Protección, Porvenir, Colfondos o Skandia?". La persona tardó **cinco minutos** en contestar "Colpensiones" (19:26), lo cual sugiere que fue a averiguarlo. Mucha gente no sabe en qué fondo está.

**El único uso que se le da hoy:** saber qué ruta de descarga darle. Nada más.

**Para el cálculo no hace falta preguntarlo:** el fondo define el régimen (Colpensiones es RPM, los privados son RAIS) y eso sale del propio documento; lo resuelve `router.py`. Preguntarlo antes solo sirve para la descarga.

**Los dos features que sí habilita, y ninguno está aprovechado:**

#### Feature 1: decirle si su administradora está en el extremo bueno o malo del rango

**De dónde sale.** Los rangos de `RENDIMIENTO_REAL_OBSERVADO` en `datos_sistema.py` **no son incertidumbre de mercado: son la dispersión entre administradoras** para el mismo perfil, medida por la Superfinanciera entre marzo de 2011 y octubre de 2024. En el perfil moderado van de 1,97% a 3,15% real. El propio código lo dice: "la distancia entre los dos extremos NO es riesgo de mercado: es con cuál AFP está el usuario. Es una palanca accionable, no una incertidumbre que le toque aguantar. Aun así la calculadora no recomienda administradora".

**Cuánto pesa.** Cuenta ilustrativa (no una cifra pensional), aportando cada año y comparando el extremo alto contra el bajo del perfil moderado:

| Años cotizando | Diferencia en el saldo final |
|---|---|
| 20 | +13% |
| 30 | +21% |
| 40 | +30% |

En RAIS la mesada sale del saldo, así que eso se traduce casi directo en la pensión. Y es una palanca que la persona sí puede mover: cambiar de administradora dentro del RAIS es libre, no tiene la ventana de diez años que sí tiene el cambio de régimen.

**El bloqueo, y es el paso previo obligatorio.** En el repo está el rango agregado, no la serie por administradora con nombre propio. Hoy se sabe que alguien rindió 1,97% y alguien 3,15%, pero no quién es quién. **Sin ese dato el feature no se puede hacer**, aunque se sepa el fondo de la persona.

Lo que hay que hacer, en orden:

**PASO 1: investigación profunda del desempeño de cada administradora.** Es un frente de investigación en sí mismo, no un dato que se busca de paso. El encargo:

- **Las cinco administradoras, una por una:** Colpensiones (para el contraste), Protección, Porvenir, Colfondos y Skandia.
- **Qué sacar de cada una:** rentabilidad real (descontada la inflación) por cada uno de los tres portafolios, para el periodo más largo que publique la Superfinanciera, y también los últimos cinco años por separado. El desempeño histórico largo y el reciente pueden contar historias distintas, y eso importa para alguien que va a cotizar veinte años más.
- **De dónde:** la fuente primaria es la Superintendencia Financiera. El `FUENTE_RENDIMIENTO` de hoy advierte que el dato crudo vive en un tablero de Power BI que no se pudo extraer, y que por eso la confianza es MEDIA (viene de una nota de prensa de El Colombiano que cita a la SFC). Hay que ir al portal de la SFC, a sus informes de rentabilidad de los fondos de pensiones obligatorias, que son periódicos y públicos. Asofondos también publica cifras agregadas.
- **Lo que hay que anotar sin excepción:** la fecha de corte de cada cifra, si es nominal o real, si es la rentabilidad del portafolio o la del afiliado (no son lo mismo, las comisiones se descuentan distinto), y el nivel de confianza. Sin eso el dato no sirve para este proyecto.
- **Lo que también hay que mirar, porque pesa igual que el rendimiento:** la comisión de administración de cada AFP. Un rendimiento mayor con una comisión mayor puede terminar peor.
- **Entregable:** un archivo nuevo en `kit-contexto/`, algo como `rendimiento-por-administradora.md`, con la tabla, las fuentes y las advertencias. Y los números que la calculadora vaya a usar, a `datos_sistema.py`, con su fuente escrita como el resto del archivo.

**PASO 1: HECHO el 2026-09-18, y mejor de lo que este archivo pedía.** La investigación por web quedó en prensa, que es lo mismo que ya había. Así que se fue al **dato primario diario de la Superfinanciera**, publicado en datos.gov.co (dataset `hds9-4524`), y se calculó la rentabilidad real por AFP y por portafolio desde cero. El informe está en `kit-contexto/rendimiento-por-administradora.md` y el script reejecutable en `analisis/rendimiento_afp.py`.

- **Confianza ALTA**, y verificada de forma independiente: el valor de la unidad, el nominal anualizado de una AFP y las dos cifras de inflación se recalcularon aparte y cuadran.
- **140 cierres mensuales, el mismo periodo exacto para las cuatro AFP** (ene-2015 a ago-2026), así que **sí son comparables entre sí**, que es lo que la investigación de prensa nunca pudo garantizar.
- El IPC sale del índice DANE publicado por el Banco de la República. Ninguna cifra de inflación es estimada.
- **Lo que sigue faltando, y es el hueco real:** esto es rentabilidad **del fondo**, no **del afiliado**. No descuenta la comisión de administración ni el seguro previsional, que se cobran antes de que la plata entre al fondo. Ese dato no sale de este dataset, y las comisiones por AFP siguen en confianza BAJA, con cifras de 2022.

**LO QUE ESTO DESTAPA, Y ES UNA DECISIÓN DE SANTIAGO QUE NO ESTABA PREVISTA EN ESTE ARCHIVO.** Los números primarios no coinciden con los que hoy usa la calculadora, y en un punto que está documentado como decisión suya:

| Perfil | Hoy en `datos_sistema.py` (prensa, 2011-2024, MEDIA) | Dato primario SFC (2015-2026, ALTA) |
|---|---|---|
| Conservador | 2,53% a 2,69% (central 2,61%) | 1,93% a 2,11% (central **2,02%**) |
| Moderado | 1,97% a 3,15% (central 2,56%) | 2,27% a 3,25% (central **2,76%**) |
| Mayor riesgo | 2,88% a 4,25% (central 3,56%) | 3,31% a 4,13% (central **3,72%**) |

**Lo importante no es que los números se muevan un poco: es que se cae la contradicción.** Con el dato de prensa, el moderado rendía **menos** que el conservador, y eso está escrito en el código con nombre propio (`MODERADO_NO_SUPERA_A_CONSERVADOR`) y es la razón por la que el supuesto prospectivo se construyó a mano, importando una prima de renta variable de una serie mundial. **Con el dato primario, el moderado sí le gana al conservador**, en el orden que el supuesto ya asumía.

Si eso se confirma, el supuesto prospectivo construido a mano deja de hacer falta: se podría anclar la proyección en evidencia colombiana en vez de en una prima importada de otro mercado. **No se cambió nada**, porque eso mueve todas las proyecciones y la decisión de usar el prospectivo es de Santiago y está marcada como "no se reabre".

**PASO 2: decidir hasta dónde se puede afirmar.** Decirle a alguien "tu AFP es de las que menos rinde" es, en la práctica, recomendarle un traslado de administradora. Hay que mirarlo contra `datos-y-alcance.md`, donde ya está definido que Júbilo no se presenta como asesor autorizado. Es decisión de Santiago, no técnica.

**PASO 3:** solo entonces, usar el fondo de la persona para ubicarla en el rango.

#### Feature 2: detectar a quien tiene semanas en los dos regímenes

Ya está construido y sin usar. `diagnosticar.py` tiene `diagnosticar_historias()`, que el propio código llama "la puerta de entrada del caso de historia partida": verifica cada documento contra su total impreso, consolida las semanas **sin doble conteo**, y decide el régimen por la afiliación de hoy y no por el documento con más semanas. El kit tiene `reglas-traslados.md` y el comparador está probado con cinco casos de traslado.

**Tres razones para detectarlo, de la más grave a la más valiosa:**

1. **Sin las dos historias, el diagnóstico sale mal, no incompleto.** Si alguien cotizó en Colpensiones, se trasladó a un privado y solo manda la historia del privado, su total de semanas queda corto. Las semanas son lo que define si cumple el requisito y en qué fecha. El bot le diría "te faltan X semanas" cuando le faltan menos, o "no alcanzas" cuando sí alcanza. Es un número equivocado con cara de número cierto, que es justo lo que la regla dura del proyecto trata de evitar.
2. **La decisión de traslado tiene fecha de vencimiento.** La ventana se cierra diez años antes de la edad de pensión. Es la decisión de plata más grande de su vida pensional y, pasada la ventana, no se puede volver atrás.
3. **Hay jurisprudencia de ineficacia del traslado** (el README apunta a la SU-140 de 2019 y la línea posterior, marcada como pendiente de verificar con abogado). Quien se trasladó mal asesorado puede tener camino de vuelta, y eso no lo sabe casi nadie.

**El límite que no se cruza:** `datos-y-alcance.md` dice que Júbilo no puede sustituir la doble asesoría obligatoria para trasladarse de régimen. Así que el feature es **detectar y advertir**, con los números de ambos escenarios, no recomendar el traslado.

**Lo que falta para activarlo:** que en algún punto se le pregunte "¿estuviste antes en otro fondo?" y, si dice que sí, se le pidan las dos historias. Saber el fondo actual es lo que abre esa pregunta.

**Pregunta abierta, y hay que resolverla antes de decidir si se piden dos documentos: ¿la historia laboral del fondo actual ya trae los periodos anteriores?**

Hay un indicio fuerte de que sí, al menos en parte. El `casos/esquema-datos.md` distingue dos campos: `administradora_emisora` ("quién emite el reporte") y, **dentro de cada periodo**, `administradora` con el comentario "dónde quedó ese aporte (puede diferir de la emisora)". Quien diseñó ese esquema lo hizo con documentos reales en la mano y previó que un reporte emitido por una administradora contenga periodos que quedaron en otra.

Lo que falta por saber es el **nivel de detalle**, y eso decide el feature:

- Si el reporte del fondo actual trae los periodos anteriores **con salario base (IBC) y fechas completas**, no hace falta pedir el segundo documento: el diagnóstico se puede hacer con uno solo.
- Si los trae **solo como un total de semanas**, sin IBC, alcanza para no equivocarse con el requisito de semanas, pero no para calcular el IBL del RPM, que necesita los salarios. Ahí el segundo documento sí hace falta, y solo para quien esté evaluando traslado.
- Si no los trae, el segundo documento es obligatorio para cualquiera con historia partida.

**Cómo verificarlo sin usar documentos de los usuarios de prueba:** con la historia laboral de Santiago, que puede descargar de los dos lados si tuvo historia partida, y con el PDF guía de Colpensiones. Los documentos de la gente que probó el bot no se usan para esto.

### 1.5 Llenar los vacíos de trámite por fondo: HECHO

Se revisaron los cinco fondos. El informe completo, con nivel de confianza por dato, quedó en `kit-contexto/fuentes-tramites/descarga-historia-laboral-por-fondo.md`.

**El vacío concreto que disparó este punto (la clave de la app de Skandia en la web) sigue sin confirmar, y así quedó escrito.** Lo que hay: una fuente secundaria dice que es la misma clave, y Skandia lo documenta oficialmente así para México, pero **no existe la afirmación en ninguna página oficial colombiana citable**. Confianza MEDIA.

Eso no es un fracaso de la investigación: es la respuesta honesta, y es exactamente lo que la regla de honestidad del kit manda hacer con un dato así. Lo que cambió es que ahora Júbilo, además de decir que no lo tiene confirmado, da el camino corto para resolverlo en el momento: la línea nacional de Skandia, 01 8000 517 526. Quedó escrito en la sección de Skandia de `tramites-y-consultas.md`, junto con los demás canales de atención que faltaban.

**Dos hallazgos de paso que valen más que el vacío original:**

1. **Porvenir tiene una vía sin iniciar sesión** que solo pide tipo y número de documento y manda el reporte al correo. No estaba documentada así. (Aun así **no se automatiza**: Porvenir usa reCAPTCHA Enterprise, y eso no se evade.)
2. **Colfondos entrega el reporte en Excel, no solo en PDF.** Es el único que lo hace, y un Excel es más fácil de leer sin errores que un PDF.

---

## Bloque 2. Que no parezca caído: HECHO el 2026-09-18

**Las cuatro cosas quedaron en `bot/bot.py`, y hay una prueba nueva que las cubre: `bot/probar_bot.py`.** El script de despliegue la corre y se detiene si falla.

| Qué | Cómo quedó |
|---|---|
| 2.1 Acuse con tiempo estimado | Solo cuando el mensaje trae adjunto. El de texto normal se queda con "Recibido. Dame un momento", porque anunciarle minutos a algo que tarda nueve segundos es peor |
| 2.2 Fuga del CLI | Las dos capas. Todo mensaje que empiece por barra lo contesta `bot.py` y nunca llega a Claude, y además hay un filtro de salida que intercepta las frases del CLI y anota el caso como evento `fuga_cli` |
| 2.3 Reenvíos | Se calcula la huella del archivo al recibirlo. Si ya llegó antes, se contesta con un texto fijo y **no se llama a Claude** |
| 2.4 `/start` repetido | A quien ya está registrado se le responde retomando, sin repetir el aviso |

**Un detalle del orden que importa para las métricas:** la revisión del archivo repetido va **antes** de anotar `documento_recibido`. Si fuera al revés, cada reenvío contaría como un documento más y el embudo del reporte diría que llegaron más documentos de los que llegaron.

**El filtro de salida solo actúa sobre respuestas de menos de 400 caracteres.** Un diagnóstico largo puede nombrar de casualidad una de esas palabras, y tumbarlo entero sería mucho peor que dejar pasar una frase rara.


### 2.1 Acuse con tiempo estimado, solo cuando de verdad va a tardar

El p95 es de 320 segundos y lo único que la persona ve es "Recibido. Dame un momento".

- **Solo cuando el mensaje trae un adjunto**, que es el caso lento. Para un mensaje de texto normal (8,6 s de mediana) el acuse actual está bien y meter un "espera unos minutos" sería peor.
- Texto en la línea de: "Recibí tu historia laboral. Leerla y hacer las cuentas me toma dos o tres minutos, no te vayas."
- Va en `bot/bot.py`, donde hoy se manda el acuse.

### 2.2 Tapar la fuga de mensajes del CLI

**Un usuario recibió literalmente: "/restart isn't available in this environment."** Un mensaje del CLI que corre por debajo, en inglés, llegó al chat de una persona. Rompe el tono y expone la infraestructura.

Dos capas, y hacen falta las dos:

- **El bot atiende los comandos antes de llamar a Claude.** Todo mensaje que empiece por `/` lo responde el propio `bot.py` con un texto en español. Eso mata la fuga en su origen y además ahorra la cuota de cuatro llamadas inútiles.
- **Un filtro de salida.** Antes de enviar la respuesta de Claude, si coincide con patrones del CLI (frases en inglés tipo "isn't available", "in this environment", "requires approval", "permission"), no se manda: se manda un texto propio y se anota el caso en la bitácora para verlo en el reporte.

### 2.3 No repetir siete veces lo mismo ante reenvíos

Durante el bloqueo, la persona reenvió el PDF dos veces y luego seis capturas. Júbilo respondió siete variaciones de "ya tengo tu documento, no reenvíes más". Después del diagnóstico volvió a mandar el mismo PDF y cinco páginas sueltas, y se gastaron seis turnos más.

- **Calcular el hash del archivo al recibirlo.** Si ya se recibió antes, el bot responde una sola vez con un texto fijo y **no llama a Claude**.
- Eso ahorra cuota real: esos reenvíos costaron cerca de US$ 1 de los US$ 8,22 de la noche.
- El texto debe ser uno solo y estable, no una reformulación distinta cada vez. La gente reenvía porque no está segura de que llegó; decirlo igual dos veces tranquiliza más que decirlo distinto siete.

### 2.4 Que `/start` no repita el aviso legal a quien ya lo vio

Con el `/start`, Júbilo reinició la bienvenida completa, aviso de privacidad incluido, y la repitió dos veces seguidas. Debe reconocer a quien ya está registrado y retomar donde iba.

---

## Bloque 3. El diagnóstico: HECHO el 2026-09-18

**El hallazgo del archivo estaba bien, y era más grave de lo que decía.** La calculadora no modelaba la convergencia, y además `perfil_por_defecto()` daba "conservador" desde los 52 en mujeres y los 56 en hombres, cuando la norma dice que a los 52 una mujer apenas tiene el 20% en conservador. Estaba equivocado en los dos sentidos: de más para unos y de menos para otros.

**Paso 1, la investigación: hecha y verificada en texto primario.** El informe quedó en `kit-contexto/multifondos-y-convergencia.md`. La primera pasada reconstruyó la tabla de fuentes secundarias y quedó en confianza MEDIA, que no alcanza para meter un número a la calculadora. Después se consiguió el texto literal de los dos artículos en el Gestor Normativo de Función Pública y **las dos tablas quedaron confirmadas palabra por palabra**. Confianza ALTA.

**La trampa de la norma, que es el dato que nadie ve:** el cuadro del artículo 2.6.11.1.6 dice 50 años para mujeres y 55 para hombres. Su parágrafo 2 corre esas edades **dos años** desde 2014. Quien lea el cuadro y no el parágrafo se equivoca por dos años en todo el tramo final. La prueba de regresión comprueba justo eso.

**La tabla que quedó en el código** (saldo mínimo obligatorio en el fondo conservador):

| Mujeres | Hombres | En conservador |
|---|---|---|
| 51 o menos | 56 o menos | 0% |
| 52 | 57 | 20% |
| 53 | 58 | 40% |
| 54 | 59 | 60% |
| 55 | 60 | 80% |
| 56 o más | 61 o más | **100%** |

**Pasos 2 y 3, el código: hechos.**

- `calculadora/datos_sistema.py`: funciones nuevas `mezcla_obligatoria()`, `perfiles_que_la_ley_le_permite()` y `rendimiento_de_la_mezcla()`, cada una con su fuente escrita al lado.
- `calculadora/rais.py`: el diagnóstico ahora trae un bloque `convergencia_obligatoria` y un escenario `mezcla_obligatoria_por_edad`, que es el que de verdad le aplica a quien ya está en convergencia. Los perfiles que la ley ya le quitó quedan marcados con `prohibido_por_convergencia` y el system prompt prohíbe ofrecerlos.
- `calculadora/probar_rais.py`: 27 comprobaciones nuevas, incluidas las dos tablas completas edad por edad y una que verifica que las tres partes del saldo siempre sumen 1 entre los 30 y los 80 años.
- El system prompt gana una sección: "El perfil de fondo: no lo preguntas, lo deduces de la ley".

**Tres cosas más que salieron del texto primario y no estaban en este archivo:**

1. **La convergencia al conservador aplica a todo el mundo**, haya elegido portafolio o no. Solo se puede ir a más conservador, nunca a menos.
2. **El cambio de portafolio se puede hacer cada seis meses** (artículo 2.6.11.1.7), y ese plazo es independiente del de cambiar de administradora.
3. **La AFP está obligada a avisarle** entre el cuarto y el tercer mes anteriores a que le arranque la convergencia. Es una palanca: mucha gente no sabe que ese aviso le tiene que llegar.

**La Ley 2381 no toca nada de esto**, y eso quedó verificado: el Decreto 1225 de 2024 dice que las administradoras del componente de ahorro individual siguen cumpliendo las disposiciones vigentes de multifondos.


### 3.1 El perfil de riesgo: no preguntarlo, y arreglar algo más grande que apareció

Júbilo preguntó el perfil dos veces y la persona nunca respondió. Buscando por qué, apareció un problema de cálculo que pesa más que el de conversación.

**Lo que hay hoy en la calculadora**

- `datos_sistema.py` tiene `RENDIMIENTO_REAL_OBSERVADO` con un rango por perfil: conservador (2,53% a 2,69%), moderado (1,97% a 3,15%), mayor riesgo (2,88% a 4,25%). Fuente Superfinanciera vía prensa, confianza MEDIA.
- `rais.py` produce los tres escenarios y `comparador.py` compara contra el moderado, dejando dicho el supuesto.
- Por lo tanto **el perfil nunca fue un insumo obligatorio**: la calculadora no lo necesita para correr.

**Lo que NO hay, y es el hallazgo**

La Ley 1328 de 2009 creó el esquema de multifondos, que incluye la asignación por defecto de quien no elige y un **régimen de convergencia**: conforme la persona se acerca a la edad de pensión, la ley obliga a ir pasando el saldo al portafolio conservador.

**La calculadora no modela nada de eso.** Se buscó en `calculadora/` y `kit-contexto/`: no hay convergencia, ni asignación por defecto, ni ninguna regla por edad. La Ley 1328 aparece en el kit, pero por otros temas (BEPS y Defensor del Consumidor).

Consecuencia: a alguien cerca de la edad de pensión hoy se le puede estar mostrando el escenario de "mayor riesgo" cuando la ley ya lo obliga a estar mayoritariamente en conservador. Es una banda optimista de más, y de las que importan, porque es justo el segmento que está a punto de decidir.

**Lo que hay que hacer, en orden**

**PASO 1, y es el primero de todo este frente: investigar la norma y fijar los números.** Nada de lo demás se puede diseñar sin esto, y no se resuelve de memoria. Hay que salir a buscar:

- Desde qué edad arranca la convergencia, y si difiere entre hombres y mujeres.
- Qué porcentaje del saldo tiene que estar en cada portafolio, por rango de edad.
- Qué pasa exactamente con quien nunca eligió portafolio: a cuál queda asignado y con qué norma.
- Si la Ley 2381 (la reforma) cambió algo de esto.

Dónde buscar: Decreto 2555 de 2010 (parte 2.6, que compila el régimen de multifondos), las circulares de la Superfinanciera, y la Ley 1328 de 2009 como norma habilitante. Cada dato entra a `datos_sistema.py` con su fuente escrita y su nivel de confianza, como el resto del archivo. **Este paso es investigación, no código.**

Después, y solo después:

2. **Modelar la convergencia en `rais.py`**, con su caso en `probar_rais.py`.
3. **No mostrar escenarios que la ley le prohíbe** a esa persona por edad.
4. **No preguntar el perfil.** Dos caminos, que no se excluyen:
   - **Supuesto informado (por defecto):** moderado para quien no eligió, corregido por la convergencia según su edad. Sale de la ley, no de la persona.
   - **El extracto, para afinar (opcional):** el extracto trimestral de pensión obligatoria dice en qué portafolio está. Ofrecerlo como "si quieres que lo afine, mándame tu extracto", nunca como requisito. Es un documento más y cada documento que se pide cuesta gente.

Lo que no se hace en ningún caso es preguntar en abstracto "¿cuál es tu perfil de riesgo?": pone a la persona a no saber algo de su propia plata, y eso es lo que la hace abandonar.

### 3.2 Anclar el techo legal en el propio diagnóstico

Un usuario dijo: "para mí el ideal sería terminar con una pensión de al menos 50.000.000 COP mensuales". Persiguió esa meta tres turnos, pidiendo el escenario sin lagunas y después con el IBC máximo, hasta que Júbilo le mostró que ni el techo de Colpensiones ($43.772.625) se acerca.

Júbilo manejó bien la expectativa ("no te la voy a ofrecer como si lo fuera"), pero se gastaron tres turnos largos en bajar a alguien de una meta imposible. Decir el techo legal desde el diagnóstico evitaría esa vuelta.

**Estado: DECIDIDO el 2026-09-18. NO entra.** Júbilo lo sigue manejando en conversación cuando la persona trae una meta imposible, que es lo que ya hacía bien.

### 3.3 Lo que la gente pregunta después del diagnóstico

Sirve para saber hacia dónde crece el producto. Lo que pidieron:

- Cómo recuperar las semanas en mora, y si hacen falta papeles del empleador.
- Cuánta plata representan los meses sin cotizar. **Júbilo no pudo:** esos huecos no tienen salario reportado, así que no hay con qué calcular.
- El escenario con el IBC máximo legal.
- Cómo pensionarse lo antes posible.

---

## Bloque 4. Medir si sirvió: DECIDIDO, y esperando al bloque 6

**Decisión de Santiago (2026-09-18):** entra, pero **no como escala de 1 a 5.** Va como **una pregunta abierta, al final de todo, después de mandar el reporte de cierre.**

**Por qué eso lo deja bloqueado:** si la pregunta va después del reporte, necesita el disparador del reporte, que es el temporizador por inactividad del bloque 6. O sea que este bloque se implementa cuando se implemente el 6, no antes.

**Lo que ya está listo para cuando llegue el momento:**

- La tabla `eventos` acepta cualquier hito sin cambios de esquema, así que la respuesta se anota ahí.
- El texto de la pregunta debe ser una sola, corta y sin escala. Algo como: "Una última cosa, y es para mí, no para ti: ¿esto te sirvió de algo?".
- La respuesta pasa por `registro.redactar()` como cualquier otro texto, porque la gente puede contestar con datos personales dentro.
- **Se pregunta una sola vez por persona.** Volver a preguntarlo es lo que convierte una pregunta honesta en una encuesta.


**En cinco conversaciones no hay una sola señal de satisfacción.** Ningún "gracias, esto me sirvió". Con el bot roto media noche es explicable, pero hoy no hay forma de saber si el diagnóstico le sirvió a alguien.

El micro-feedback de 1 a 5 después del diagnóstico se descartó el 16 de septiembre, antes de tener datos. Con estos datos el cálculo cambia: la tabla `eventos` ya acepta cualquier hito, así que es barato.

**Estado: sin decidir.** Falta que Santiago diga si entra.

---

## Bloque 5. Pedir el documento por el bot: HECHO el 2026-09-18

**Santiago reabrió esta decisión el 2026-09-18**, con este argumento: no es saltarse el control de acceso de un tercero, es automatizarle al propio cliente del fondo su propio acceso, a través de otra interfaz. El argumento es válido y cambia el encuadre: un agente que actúa por el usuario, con su consentimiento y sobre un formulario público, no es lo mismo que atacar un sistema. Queda aprobado con el alcance de abajo. La nota del `AGENTS.md` del 2026-07-21 hay que actualizarla cuando esto se resuelva, en un sentido o en otro.

**Alcance aprobado**

- **Solo los fondos que no exigen iniciar sesión.** Colpensiones es el caso: el formulario pide tipo y número de documento y manda el reporte al correo registrado.
- **Los fondos con login quedan fuera**, y no por dificultad técnica: automatizarlos exigiría que la persona le entregue al bot su usuario y contraseña del fondo. Para esos, lo acordado es explicar qué es el documento y darle la guía de descarga (bloque 1).

**Las dos líneas que no se cruzan**

1. **Nada de evadir protecciones anti-bot.** Si el portal responde a una petición normal, adelante. Si responde 403 por un WAF, la salida es hablar con Colpensiones o desistir, no rotar IPs, ni resolver captchas, ni falsificar señales de navegador para parecer una persona. La diferencia entre automatizar en nombre del usuario y disfrazarse de usuario es exactamente esta.
2. **Nunca se piden ni se guardan credenciales** de la cuenta de nadie en un fondo.

### PASO 0: RESUELTO EL 2026-09-18. Sí se puede entrar, y el trámite se completa

**Resultado de la prueba** (una sola corrida desde el Mac, con una cédula real que dio Santiago, que no se escribe aquí, contra `sede.colpensiones.gov.co/tramite/updInfo/55/`):

| Qué se probó | Resultado |
|---|---|
| ¿Responde el formulario? | Sí. **HTTP 200** en 2,1 segundos. El 403 de julio de 2026 ya no aparece |
| ¿Hay captcha? | No. Ninguna referencia a captcha, reCAPTCHA, hCaptcha ni Turnstile en la página |
| ¿Exige iniciar sesión? | No, mientras se manden los dos campos ocultos del formulario (`tk` y `sxToken`) |
| ¿Se completa el trámite? | Sí, de punta a punta. El portal confirmó: "Tu Historia Laboral fue enviada exitosamente a la cuenta de correo registrada" |
| ¿Se puede capturar el correo de destino? | Sí. El portal lo muestra **ya enmascarado por él mismo**, en la forma `omar*****@hotmail.com`: se ve de qué correo se trata sin que el bot conozca el correo completo |

**Tres cosas que se aprendieron y que estaban mal supuestas:**

1. **El trámite tiene tres pasos, no uno.** Paso 1, abrir el formulario. Paso 2, mandar tipo y número de documento, y ahí el portal responde con el correo enmascarado. Paso 3, confirmar. El envío solo ocurre en el paso 3.
2. **Sin los dos campos ocultos, el portal manda a la pantalla de iniciar sesión.** Son parte del formulario, los manda cualquier navegador sin que la persona los vea, y leerlos de la página no es evasión de nada. Lo que sí hizo falta fue declarar el tamaño del envío: sin eso el portal responde 411.
3. **El correo enmascarado lo enmascara Colpensiones, no nosotros.** Eso resuelve la petición de Santiago (2026-09-18) de mostrarle a la persona a qué correo le va a llegar: se le puede repetir tal cual, sin que el bot conozca el correo completo. Y tiene un uso de producto que no estaba previsto: si la persona no reconoce ese correo, tiene registrado uno viejo en Colpensiones y hay que descubrirlo en ese momento, no media hora después.

**Con un documento que Colpensiones no reconoce**, el portal no explica nada: simplemente devuelve la pantalla sin correo. El módulo lo trata como "no me devolvió ningún correo para ese documento" y no afirma más que eso.

**Lo que quedó construido:** `tramites/pedir_historia.py`, con su prueba `tramites/probar_pedir_historia.py`, que corre sin tocar internet porque trabaja sobre las respuestas reales guardadas del portal.

<details>
<summary>La instrucción original del paso 0, para historial</summary>

**Orden explícito de Santiago (2026-09-18): primero probar si somos capaces de acceder a la página. Nada aguas abajo se cambia antes de eso.** No se toca el kit, ni el aviso de privacidad, ni el flujo de la conversación, ni se escribe el módulo, hasta saber si el acceso funciona.

Cómo probarlo:

- Una sola petición, desde el Mac y no desde el bot, al formulario de Colpensiones (`sede.colpensiones.gov.co/tramite/updInfo/55/`).
- Con los datos de Santiago, no de un usuario.
- Objetivo: saber si responde normalmente o si devuelve el 403 de firewall que devolvió en julio de 2026.

Los tres desenlaces posibles:

1. **Responde y el trámite se puede completar:** se sigue con el resto del bloque.
2. **Devuelve 403 u otro bloqueo:** **el bloque se detiene ahí.** No se busca la vuelta, no se rotan IPs, no se cambian cabeceras para parecer un navegador. La salida es escribirle a Colpensiones o dejar el feature quieto.
3. **Responde pero exige algo nuevo** (captcha, verificación por celular, inicio de sesión): se documenta qué pide y se vuelve a decidir con eso en la mano.

El resultado de esta prueba se escribe en este archivo antes de seguir, sea cual sea.

</details>

### El alcance, ya definido: HECHO el 2026-09-18

Colpensiones **solo envía el reporte al correo registrado**, no permite descarga en pantalla. Santiago lo confirmó y decidió que se puede vivir con eso. Entonces el feature es explícitamente esto y no más:

- Lo que se le ahorra a la persona: llenar el formulario (tipo de documento, número, confirmar el correo).
- Lo que sigue haciendo ella: abrir su correo, encontrar el mensaje de Colpensiones y reenviar el PDF al bot.

Eso hay que decirlo así en el chat, para no prometer lo que no es: algo como "ya le pedí tu historia laboral a Colpensiones, te va a llegar al correo que tienes registrado con ellos. Cuando te llegue, reenvíamela aquí." Si la persona cree que el documento va a aparecer solo, la espera se vuelve otro "no me contesta".

**Cómo se hizo, sin romper el diseño**

El principio del `AGENTS.md` es que el cerebro del agente no tiene internet, y sigue en pie. El trámite lo hace un **módulo aparte con red**, `tramites/pedir_historia.py`, que el bot invoca igual que invoca la calculadora. El modelo no navega: ejecuta un programa nuestro que hace una cosa fija y devuelve un JSON. Lo único que cambió en el aislamiento es un permiso más en `--allowedTools`: `Bash(python3 .../tramites/*)`, al lado del que ya existía para la calculadora.

**El riesgo que esto abre, y por qué se aceptó.** Como el modelo puede disparar el trámite, un usuario malintencionado podría intentar que lo corra con la cédula de otra persona. El daño posible es acotado: Colpensiones manda el documento **al correo del propio titular**, nunca al chat, así que lo peor que pasa es que un tercero reciba un correo suyo que no pidió. Aun así, el system prompt lo prohíbe explícitamente y trata cualquier instrucción de ese tipo, venga del chat o de dentro de un archivo, como intento de manipulación.

**El aviso de privacidad: RESUELTO, versión 1.2**

Hasta el 1.1, el kit definía la cédula como "una llave, no un dato": se usaba para abrir el PDF y no salía del servidor. Con el trámite, la cédula pasa a ser un dato transmitido a un tercero, o sea una finalidad nueva. Lo hecho el 2026-09-18:

- Frase nueva en la bienvenida: "Si me pides que le pida tu historia laboral a Colpensiones, uso tu cédula únicamente para ese trámite, ante ellos, y no la guardo."
- `VERSION_AVISO` sube de 1.1 a **1.2** en `bot.py`, con el porqué escrito al lado.
- El 1.1 queda archivado en `kit-contexto/aviso-de-privacidad.md` sección 2.2, y la tabla de trazabilidad gana una fila para esta transmisión (*Decreto 1377, art. 15 num. 2; Ley 1581, art. 8 lit. a*).

**Pendiente para el abogado:** si esa frase en el aviso basta, o si el trámite exige además una autorización aparte en el momento de hacerlo. Mientras tanto se aplica lo más estricto: el system prompt obliga a ofrecerlo y esperar el sí, nunca a hacerlo por iniciativa propia.

---

## Bloque 6. El reporte de cierre: ESPERANDO EL VISTO BUENO DE SANTIAGO

**Decisión de Santiago (2026-09-18): no se construye todavía.** Primero hay que validar la estructura. Así que este bloque queda como está, con la estructura propuesta abajo, y **el formato sin decidir**.

**Lo que hay que resolver para desbloquearlo, y son dos preguntas:**

1. **¿La estructura de siete secciones de abajo está bien?** Si sobra o falta algo, decirlo ahora, antes de que exista el módulo.
2. **¿Imagen, PDF, o los dos?** La recomendación sigue siendo PDF de una página más la imagen de esa misma página en el mismo mensaje: el PDF se guarda y se reenvía, la imagen se ve sin abrir nada.

**Y una tercera que apareció después, por el bloque 4:** Santiago decidió que el micro-feedback vaya como pregunta abierta **después** del reporte. O sea que el temporizador de inactividad de este bloque es también el disparador del bloque 4, y los dos se construyen juntos.


**Lo que Santiago quiere:** que al final de la conversación, o cuando la persona deje de escribir por unos 30 minutos, le llegue una página con un reporte estandarizado, en imagen o PDF.

**Por qué tiene sentido, más allá de que se vea bien.** Hoy el diagnóstico queda repartido en varios mensajes de chat que se pierden hacia arriba en el scroll. La persona no puede releerlo, ni guardarlo, ni mostrárselo a su pareja o a su contador. Una página es un objeto que se conserva, y además es lo que la gente reenvía, que es el mecanismo de crecimiento más probable de esto.

### Cómo se genera: la regla que no se puede romper

**El reporte lo arma el código, no el modelo.** Una plantilla fija que se llena con la salida JSON de `diagnosticar.py`. Si el modelo "dibuja" el reporte, cada uno sale distinto y, peor, puede reescribir una cifra. Es la misma regla dura del proyecto: la IA conversa, el código fijo hace los números.

Implicación práctica: se necesita un módulo nuevo, tipo `reporte/armar_reporte.py`, que reciba el JSON del diagnóstico y devuelva el archivo. Con su prueba, que verifique que las cifras del archivo son idénticas a las del JSON.

### Estructura propuesta (a validar con Santiago antes de construir)

Una sola página, en este orden, que es la secuencia real de la pregunta que la persona trae:

1. **Encabezado.** Fecha del diagnóstico, fondo, y el aviso de que es un diagnóstico preliminar y no una liquidación certificada.
2. **Tu situación hoy.** Régimen, edad, semanas cotizadas, semanas que faltan.
3. **Tu resultado proyectado.** Fecha estimada de pensión, mesada como banda (no un número solo), y tasa de reemplazo. La banda es obligatoria: un número solo se lee como promesa.
4. **Tus alertas.** Moras y lagunas, cada una con su impacto concreto en semanas y en fecha. Es lo que mueve a la acción.
5. **Tus palancas.** Qué puede hacer y qué gana con cada cosa, ordenado por impacto.
6. **Supuestos y límites.** Qué se asumió (perfil moderado, densidad futura, etc.) y qué no cubre este diagnóstico.
7. **Tu siguiente paso.** Uno concreto, no tres.

### Lo que hay que resolver

- **Imagen o PDF.** El PDF se guarda y se reenvía mejor, y se ve igual en todos lados. La imagen se ve sin abrir nada, que para mucha gente es la diferencia entre verlo y no verlo. **Recomendación: PDF de una página, y además la primera página como imagen** en el mismo mensaje, para que se vea en la conversación sin abrir el archivo.
- **El disparo por inactividad.** El bot hoy es puramente reactivo: solo actúa cuando llega un mensaje. Para mandar algo a los 30 minutos de silencio hace falta un temporizador. `python-telegram-bot` tiene `JobQueue`, que es el camino natural y no obliga a montar nada nuevo. Hay que decidir qué pasa si la persona vuelve a escribir después: no mandarle un segundo reporte idéntico.
- **Cuándo NO mandarlo.** Si la conversación nunca llegó al diagnóstico, no hay reporte que mandar y un "aquí está tu reporte" vacío sería peor que el silencio. En ese caso, si acaso, un recordatorio de que quedó pendiente mandar el documento.
- **Qué no puede llevar.** Ni nombre, ni cédula, ni número de documento. El reporte se puede reenviar a cualquiera, así que va sin datos que identifiquen a la persona.
- **La marca.** Es la primera pieza de Júbilo que va a circular por fuera del chat. Vale pensar el diseño con ese peso.

---

## Bloque 7. Llevarlo a WhatsApp: ANÁLISIS HECHO

El informe completo, con fuentes y fecha de consulta de cada dato, quedó en `analisis/whatsapp-viabilidad.md`. El análisis de abajo se conserva porque acertó en lo grueso. **Lo que el informe añade o corrige:**

- **El freno es el que este archivo sospechaba, y se confirmó:** la verificación de negocio de Meta está pensada para una entidad legal con documentos a su nombre. **No se pudo confirmar** que un RUT de persona natural sin registro mercantil alcance. Hay que probarlo en el flujo de Meta o preguntárselo a un proveedor antes de invertir en desarrollo.
- **Hay una salida que este archivo no consideraba: usar Synappse.** Si la verificación exige sociedad constituida, la ruta más barata es esa, no forzar el registro como persona natural. Choca con el "detrás de esto hay una persona, no una empresa" del aviso de privacidad, y por eso es una decisión de producto, no de trámite.
- **El precio hoy es bajo y sube pronto.** Los mensajes de utilidad y autenticación en Colombia están cerca de US$ 0,0008. Pero **desde el 1 de octubre de 2026 Meta empieza a cobrar también los mensajes de servicio y utilidad dentro de la ventana de 24 horas**, y eso le pega directo a un bot conversacional como Júbilo, que hoy vive gratis en Telegram.
- **El reporte de cierre del bloque 6 sí se puede mandar al día siguiente**, con una plantilla de utilidad aprobada. Deja de ser gratis en octubre de 2026.
- **La transcripción de audio no viene resuelta.** Meta entrega el audio en ogg/opus y ya: hay que sumar un proveedor de transcripción, con su costo, que no se pudo cuantificar.
- **El webhook no es la barrera.** HTTPS con certificado válido y firma HMAC es estándar, y el VPS ya existe.


**Lo que Santiago quiere:** que Júbilo funcione en WhatsApp. Por ahora solo evaluar viabilidad y dificultad.

**Veredicto corto:** es viable y vale la pena, porque en Colombia WhatsApp es donde está la gente. Pero no es un cambio de librería: es un cambio de arquitectura de red y un trámite con Meta. Lo difícil no es el código.

### Lo que NO cambia

`calculadora/`, `kit-contexto/`, `registro.py` y el flujo entero de la conversación se quedan igual. `bot.py` es un cartero, y solo se cambia el cartero.

### Lo que sí cambia, en orden de dificultad

1. **De polling a webhook.** Telegram deja que el bot pregunte "¿hay mensajes?" desde cualquier parte, sin que nadie lo tenga que alcanzar desde fuera. WhatsApp hace lo contrario: Meta llama a un servidor tuyo. Eso obliga a tener un dominio, un certificado HTTPS válido, un endpoint público y verificación de la firma de cada mensaje. Hoy el VPS no expone nada a internet, y esto lo convierte en un servidor público, con todo lo que implica.
2. **La ventana de 24 horas.** Dentro de las 24 horas del último mensaje de la persona se puede responder libre. Pasadas las 24 horas **solo se puede escribir con plantillas aprobadas previamente por Meta**. Esto afecta directo al bloque 6: un reporte a los 30 minutos entra sin problema, pero cualquier seguimiento al día siguiente necesita plantilla.
3. **La verificación del negocio.** Meta pide una cuenta de Meta Business, un número dedicado (que deja de servir para WhatsApp normal) y, para pasar de los límites iniciales, verificación de la empresa con documentos. **Aquí hay un choque con el producto:** el aviso de privacidad de Júbilo dice hoy "detrás de esto hay una persona, no una empresa". Habría que ver qué exige Meta para una persona natural, y es el punto que más puede frenar todo.
4. **El costo por mensaje.** WhatsApp cobra distinto que Telegram, que es gratis. Meta cambió su modelo de precios y hay que verificar el vigente: qué se cobra dentro de la ventana de servicio y qué se cobra por plantilla. **Ese costo se suma al del modelo**, así que hay que meterlo en la cuenta del bloque 8.
5. **Las notas de voz se vuelven obligatorias.** En Telegram fueron un caso raro que hoy se contesta con un "no puedo escucharlas". En WhatsApp, la gente en Colombia habla por nota de voz por defecto. Habría que transcribir, y eso es un componente más y otro costo.

### Lo que no se va a hacer

Existen librerías que automatizan WhatsApp Web sin pasar por Meta. **No se usan.** Violan los términos de WhatsApp y el desenlace normal es que baneen el número, con los usuarios adentro. Si se va a WhatsApp, se va por la API oficial.

### Lo que hay que averiguar antes de decidir

- Qué exige hoy Meta para verificar a una persona natural, y si hay alguna figura intermedia.
- El modelo de precios vigente de la Cloud API, con números.
- Si conviene ir directo con Meta o a través de un proveedor (Twilio, 360dialog, Infobip): los proveedores ahorran trámite y cobran margen.
- Si se puede mantener Telegram y WhatsApp en paralelo con el mismo cerebro. Se puede, y probablemente es el camino: el transporte se separa del resto y cada canal es un cartero distinto.

---

## Bloque 8. Bajar el costo: el primer paso HECHO, el resto sigue en análisis

**Lo que este archivo señalaba como "lo primero que hay que hacer en este frente" está hecho:**

- `bot/registro.py`: la tabla `turnos` gana tres columnas, `tokens_frescos`, `tokens_cache` y `tokens_cache_creado`. Las bases que ya existen se actualizan solas al arrancar, sin perder nada, y hay una prueba que simula una base vieja y comprueba justo eso.
- `bot/bot.py`: separa los tres números del JSON que devuelve Claude, en vez de sumarlos en uno.
- `analisis/reporte.py`: sección nueva, "De dónde sale el gasto de entrada", con el reparto en porcentaje y cómo leerlo. El reporte sigue funcionando con las bases viejas, que no tienen esas columnas: la sección simplemente no aparece.

**Por qué esto va primero y no el cambio de modelo:** si casi todo el contexto resulta ser caché, el kit no es el problema y el ahorro está en no llamar al modelo cuando no hace falta, que es lo que ya hacen los bloques 2.2 y 2.3. Si los frescos son altos, entonces sí vale cargar el kit por etapas. Hasta ahora se estaba a punto de optimizar a ciegas.

**Los otros dos ahorros de este bloque ya entraron por el bloque 2, y hay que contarlos aquí:** los comandos y los archivos repetidos ya no llegan al modelo. Esos reenvíos costaron cerca de US$ 1 de los US$ 8,22 de esa noche.

**Lo que sigue pendiente y sin tocar:** cargar el kit por etapas, usar un modelo más pequeño para la conversación, pasar de Pro a API, y cambiar de proveedor. Los cuatro siguen siendo decisiones, no tareas, y el orden del análisis de abajo sigue valiendo.


**El punto de partida, medido:** US$ 0,164 por turno y **US$ 1,64 por persona**. Con la cuenta Pro no hay factura, así que es un costo teórico, pero mide consumo de una cuota que es única y compartida entre todos los usuarios. Con 50 personas, la cuota se agota.

### De dónde sale el costo, en orden de tamaño

**1. El contexto de entrada, y es de lejos el más grande.** Un simple "Hola" consumió **61.792 tokens de entrada**. Eso no es lo que escribió la persona: es el kit que Júbilo lee antes de responder. Para dimensionarlo, `kit-contexto/` son **94.952 palabras** en total (unos 130.000 tokens si se cargara completo) y el `system-prompt.md` solo ya son 9.343 palabras.

Las palancas, de la más barata de implementar a la más profunda:

- **No llamar al modelo cuando no hace falta.** Un `/start`, un comando, un archivo repetido: hoy cada uno cuesta un turno completo. Los reenvíos de esa noche costaron cerca de US$ 1 de los US$ 8,22. Esto ya está en los bloques 2.2 y 2.3, y es el ahorro más fácil que existe.
- **Medir cuánto del contexto es caché y cuánto es fresco.** La bitácora ya guarda `tokens_entrada` sumando lectura de caché y tokens nuevos. Separarlos en dos columnas diría exactamente dónde se va la plata, y es un cambio de una línea. **Hay que hacer esto antes de optimizar cualquier otra cosa**, porque si casi todo es caché, el problema es otro y se estaría apuntando al lugar equivocado.
- **Cargar el kit por etapas.** Hoy el `CLAUDE.md` de cada usuario le dice que lea el system prompt completo antes de responder nada. Quien apenas dijo "hola" no necesita las reglas de tributación pensional ni las de reclamación ante el Defensor del Consumidor. Cargar solo lo de la etapa en la que va la conversación es probablemente el ahorro grande.

**2. El modelo.** Hoy todo corre con el mismo modelo, sin importar la tarea. Pero las tareas son muy distintas: preguntar en qué fondo está la persona es trivial; extraer una historia laboral de cinco páginas sin equivocarse en una cifra es lo más difícil que hace el sistema. Un modelo más pequeño para la conversación y el más capaz solo para la extracción y el diagnóstico es el clásico ahorro de dos dígitos sin pérdida de calidad donde importa. **Pero antes hay que medir el punto 1**, porque si el costo está en el contexto y no en la generación, cambiar de modelo mueve poco.

**3. Pasar de Pro a API.** Hoy el costo es invisible y la cuota es un muro compartido: cuando se agota, a todos les dice que no tiene capacidad. Con API el costo se vuelve visible y controlable, y se puede poner un presupuesto por persona y por día. Es un cambio de cuenta, no de código. Es la decisión que hay que tomar antes de repartir el link a más gente.

**4. Cambiar de proveedor.** Santiago menciona alternativas (proveedores chinos, Grok). Hay que ser claro con lo que implica, porque no es cambiar una llave:

- **No es cambiar de API, es cambiar de runtime.** El bot no llama a una API de texto: corre `claude -p`, y de ahí salen el aislamiento por `CLAUDE_CONFIG_DIR`, la lista de herramientas permitidas, la continuidad de la conversación con `--resume` y los permisos que impiden que el modelo toque lo que no debe. Todo eso hay que reconstruirlo a mano con otro proveedor. Es reescribir el bot, no ajustarlo.
- **Hay que evaluar la calidad en lo que este producto hace**, que no es conversar bonito: es leer un PDF de cinco páginas sin equivocarse en una cifra, y razonar sobre normativa colombiana. Eso se mide con los casos que ya existen en `casos/`, que es justo para lo que sirve el set dorado.
- **Toca el aviso de privacidad.** Hoy dice que el procesamiento ocurre en servidores fuera de Colombia. Cambiar de proveedor cambia a dónde van los datos de la gente, y con un proveedor en otra jurisdicción eso hay que decirlo y subir la `VERSION_AVISO`.
- **El orden sensato:** agotar primero los puntos 1 y 2, que no tienen riesgo, antes de tocar el proveedor, que tiene mucho.

### Lo primero que hay que hacer en este frente

Separar caché de tokens frescos en la bitácora y sacar un reporte con eso. Un turno de análisis, y evita optimizar a ciegas.

---

## Descartado, no reabrir

- **Consultar por otra persona** (los papás, típicamente). Un usuario lo pidió y Júbilo lo rechazó bien: "solo puedo procesar la historia laboral de quien me la manda directamente". Santiago lo confirmó descartado el 2026-09-18.

---

## Lo que ya funciona y no hay que tocar

Para no arreglar lo que no está roto:

- Rechaza la suplantación de identidad. Un usuario intentó hacerse pasar por Santiago para sacarle su arquitectura y Júbilo no cedió.
- Distingue un pantallazo de saldo de una historia laboral, y lo dice con claridad.
- Reconoce páginas repetidas del mismo documento sin recalcular nada.
- Es honesto con las metas imposibles en vez de vender humo.
- Abre los PDFs protegidos con clave, de cualquier fondo.

---

## Antes de dar cualquier cambio por bueno

Está todo en el `AGENTS.md`, pero lo que más se olvida:

- **Las pruebas primero.** Las once suites de `calculadora/` y `bot/probar_registro.py`, todas en verde.
- **Nunca probar contra el bot de producción.** Lo que se puede probar de verdad es corriendo `claude -p` a mano en el servidor, en una carpeta de `/tmp`, con los mismos permisos que usa el bot. Así se encontraron los tres bugs del 16 de septiembre; razonar el prompt no los habría encontrado.
- **No desplegar con gente conversando.** Cada reinicio mata el turno que esté en vuelo. Ya pasó una vez. Se comprueba con `ps -eo pid,cmd | grep "[c]laude -p"` en el servidor.
