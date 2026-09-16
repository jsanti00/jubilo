# Datos personales y alcance de Júbilo - Documento 13 del kit

> **Última actualización:** 2026-07-27. **Estado:** parte 1 (norma) verificada contra fuentes oficiales. Parte 2 (respuestas al usuario): **todas las marcas `[DECISIÓN DE SANTIAGO]` quedaron cerradas el 2026-07-27** y hoy son respuestas utilizables. Siguen abiertas tres marcas `[VERIFICAR]` (Ley 2300 de 2023, lista de países con nivel adecuado según la SIC, y el detalle del RNBD y las sanciones), que no bloquean el piloto porque cada una trae respuesta operativa.
> **Por qué existe:** el usuario entrega su historia laboral completa, que es información reservada por ley, y va a preguntar qué se hace con ella. Además destraba el pendiente abierto del `system-prompt.md` ("Política de datos y consentimiento").
> **Regla de honestidad:** ya no hay puntos sin definir en este documento. Si aparece uno nuevo, el agente **no improvisa**: dice que aún no está definido y que no quiere prometer algo que no sabe.
> **Documentos derivados:** el texto que ve el usuario está en `aviso-de-privacidad.md`. Los documentos internos (manual de políticas y procedimientos, procedimiento ante incidentes) están en `../cumplimiento/`.

---

# Parte 1. Datos personales: la norma

## 1. Qué régimen aplica

**Ley 1581 de 2012** (ley estatutaria de protección de datos personales) y su reglamento, el **Decreto 1377 de 2013** (compilado en el Decreto Único 1074 de 2015 del sector Comercio). La autoridad es la **Superintendencia de Industria y Comercio (SIC)**. *Fuente: Ley 1581 de 2012, art. 19.*

**No aplica la Ley 1266 de 2008** (hábeas data financiero y crediticio): esa regula centrales de riesgo y comportamiento crediticio, que no es lo que Júbilo trata. Su valor aquí es solo que de ella sale la clasificación de datos en públicos, semiprivados y privados. *Fuente: Ley 1266 de 2008, art. 3, lits. e a h.*

`[VERIFICAR]` **Reforma en trámite.** En agosto de 2025 el Gobierno radicó un proyecto de ley estatutaria (Proyecto 247 de 2025, acumulado con el 214 de 2025) para modernizar la Ley 1581, con cambios en bases de legitimación (interés legítimo, ejecución contractual) y en datos de menores. **Hasta que no sea ley, rige la Ley 1581 tal como está aquí.** Verificar el estado del trámite antes del piloto.

## 2. Cómo se clasifica la historia laboral (esto cambia el nivel de exigencia)

**Primera capa: es información reservada.** La ley clasifica expresamente como reservados "los que involucren derechos a la privacidad e intimidad de las personas, incluidas en las **hojas de vida, la historia laboral y los expedientes pensionales** y demás registros de personal que obren en los archivos de las instituciones públicas o privadas, así como la historia clínica". Y añade que esa información **solo puede ser solicitada por el titular, sus apoderados o personas autorizadas con facultad expresa**. *Fuente: Ley 1755 de 2015, art. 24, num. 3 y parágrafo.*

**Segunda capa: como dato personal, la historia laboral es semiprivada, no sensible por sí misma.** Semiprivado es el dato que no es íntimo, ni reservado, ni público, y cuyo conocimiento interesa no solo al titular sino a cierto sector (aquí, al Sistema General de Seguridad Social). *Fuente: Ley 1266 de 2008, art. 3 lit. g; criterio confirmado en conceptos oficiales sobre historia laboral.* No aparece en el listado de datos sensibles del art. 5 de la Ley 1581.

**Tercera capa, y es la que importa: la historia laboral puede contener datos que sí son sensibles.** Son sensibles los que afectan la intimidad o cuyo uso indebido puede generar discriminación, entre ellos **los datos relativos a la salud** y **la pertenencia a sindicatos**. *Fuente: Ley 1581 de 2012, art. 5.*

Ejemplos concretos que aparecen en historias laborales reales:
- Novedades por **incapacidad** o licencia de maternidad: revelan salud.
- Aportes o descuentos a **sindicato**: revelan pertenencia sindical.
- Cotización bajo **régimen de alto riesgo** o mención de calificación de invalidez: revelan salud u ocupación.

**Consecuencia operativa.** El tratamiento de datos sensibles está prohibido salvo excepciones, y la principal es la **autorización explícita** del titular. *Fuente: Ley 1581 de 2012, art. 6 lit. a.* Además, cuando hay datos sensibles hay que:
1. **Informar al titular que, por ser sensibles, no está obligado a autorizar su tratamiento.**
2. **Decirle explícita y previamente cuáles de los datos son sensibles y para qué se van a usar**, y obtener consentimiento expreso.
3. **Nunca condicionar el servicio a que entregue datos sensibles.** *Fuente: Decreto 1377 de 2013, art. 6.*

**Traducción para el diseño de Júbilo:** aunque el objetivo del producto son semanas, IBC y fechas (semiprivados), el documento que llega puede traer datos sensibles adheridos. El estándar de exigencia se fija sobre el peor caso, no sobre el promedio.

## 3. Qué autorización se requiere

| Requisito | Regla | Fuente |
|---|---|---|
| Naturaleza | **Previa, expresa e informada** | Ley 1581, art. 3 lit. a y art. 9 |
| Momento | A más tardar **al momento de recolectar** los datos | Decreto 1377, art. 5 |
| Forma válida | (i) por escrito, (ii) oral, o (iii) por **conductas inequívocas** del titular que permitan concluir razonablemente que autorizó | Decreto 1377, art. 7 |
| Lo que nunca vale | **El silencio.** En ningún caso se asimila a conducta inequívoca | Decreto 1377, art. 7 |
| Prueba | El responsable debe **conservar prueba** de la autorización y entregar copia si el titular la pide | Ley 1581, art. 12 par.; Decreto 1377, art. 8 |
| Si cambia la finalidad | Hay que obtener **nueva autorización** | Decreto 1377, art. 5 |
| Datos sensibles | Consentimiento **explícito**, con las tres advertencias de la sección 2 | Ley 1581, art. 6 lit. a; Decreto 1377, art. 6 |

**Qué hay que informarle al titular al pedirle la autorización** (contenido mínimo): el tratamiento y su finalidad; el carácter facultativo de responder preguntas sobre datos sensibles; los derechos que le asisten; y la identificación, dirección y teléfono del responsable. *Fuente: Ley 1581 de 2012, art. 12.*

**Recolección limitada.** Solo se pueden pedir los datos **pertinentes y adecuados para la finalidad**, y está prohibido usar medios engañosos o fraudulentos para obtenerlos. *Fuente: Decreto 1377 de 2013, art. 4.*

## 4. Derechos del titular

*Fuente: Ley 1581 de 2012, art. 8, salvo indicación distinta.*

| Derecho | Qué significa en la práctica |
|---|---|
| **Conocer** | Pedir toda la información suya que esté en la base de datos, gratis (lit. a y f) |
| **Actualizar y rectificar** | Corregir datos parciales, inexactos, incompletos, fraccionados o que induzcan a error (lit. a) |
| **Suprimir** | Pedir que se borren sus datos (lit. e) |
| **Revocar la autorización** | Retirar el permiso en cualquier momento (lit. e) |
| **Pedir prueba de la autorización** | Exigir que le muestren con qué permiso lo están tratando (lit. b) |
| **Saber el uso dado a sus datos** | Preguntar qué han hecho con ellos (lit. c) |
| **Quejarse ante la SIC** | Por infracciones a la ley (lit. d) |

**Límite honesto de la supresión y la revocatoria:** no proceden cuando el titular tiene un **deber legal o contractual de permanecer** en la base de datos. *Fuente: Decreto 1377 de 2013, art. 9.* Y el responsable debe poner mecanismos **gratuitos y de fácil acceso** para pedirlas. *Misma fuente.*

**Términos para responder:**

| Solicitud | Término | Prórroga | Fuente |
|---|---|---|---|
| **Consulta** (quiero ver mis datos) | 10 días hábiles | 5 días hábiles más, avisando motivos y fecha | Ley 1581, art. 14 |
| **Reclamo** (corregir, actualizar, suprimir, revocar) | 15 días hábiles | 8 días hábiles más, avisando motivos y fecha | Ley 1581, art. 15 |

Detalles del reclamo que conviene tener presentes: si llega incompleto, hay 5 días para requerir al titular, y si pasan 2 meses sin respuesta se entiende desistido; si quien lo recibe no es competente, traslada en máximo 2 días hábiles; y mientras se decide, el registro debe llevar la leyenda "reclamo en trámite". *Fuente: Ley 1581 de 2012, art. 15.*

**Requisito de procedibilidad:** el titular solo puede quejarse ante la SIC **después** de haber agotado la consulta o el reclamo ante el responsable. *Fuente: Ley 1581 de 2012, art. 16.*

## 5. Obligaciones de quien trata esos datos

Los principios rectores, que son el marco de todo lo demás: **legalidad, finalidad, libertad, veracidad o calidad, transparencia, acceso y circulación restringida, seguridad y confidencialidad**. *Fuente: Ley 1581 de 2012, art. 4.*

Deberes concretos del responsable, en lo que aplica a un producto como Júbilo. *Fuente: Ley 1581 de 2012, art. 17.*

- Garantizar en todo tiempo el ejercicio del hábeas data (lit. a).
- Solicitar y **conservar copia de la autorización** (lit. b).
- Informar la finalidad de la recolección y los derechos del titular (lit. c).
- **Conservar la información con condiciones de seguridad** que impidan adulteración, pérdida, consulta, uso o acceso no autorizado o fraudulento (lit. d).
- Rectificar cuando la información sea incorrecta (lit. g).
- Tramitar consultas y reclamos en los términos de la sección 4 (lit. j).
- **Adoptar un manual interno de políticas y procedimientos**, en especial para atender consultas y reclamos (lit. k).
- Informar a solicitud del titular el uso dado a sus datos (lit. m).
- **Informar a la SIC cuando haya violaciones a los códigos de seguridad** y riesgos en la administración de la información (lit. n).

**Política de tratamiento de la información.** Debe constar por escrito (físico o electrónico), en lenguaje claro y sencillo, y contener al menos: identificación y datos de contacto del responsable; tratamiento y finalidad; derechos del titular; área o persona que atiende peticiones; procedimiento para ejercer los derechos; y fecha de entrada en vigencia y periodo de vigencia de la base de datos. *Fuente: Decreto 1377 de 2013, art. 13.*

**Aviso de privacidad.** Cuando no sea posible poner la política completa a disposición del titular, se usa un aviso de privacidad con contenido mínimo: nombre y contacto del responsable; tratamiento y finalidad; derechos del titular; y cómo consultar la política. Si se recolectan datos sensibles, el aviso debe señalar expresamente que responder es facultativo. *Fuente: Decreto 1377 de 2013, arts. 14 y 15.* **Este es el formato que le sirve a un bot de chat.**

**Retención: no hay un plazo fijo en la ley, y por eso es decisión de producto.** La regla legal es que los datos solo se pueden conservar "durante el tiempo que sea razonable y necesario, de acuerdo con las finalidades que justificaron el tratamiento"; cumplida la finalidad, hay que **suprimirlos**, salvo obligación legal o contractual de conservarlos. Y hay que **documentar los procedimientos** de tratamiento, conservación y supresión. *Fuente: Decreto 1377 de 2013, art. 11.*

**Registro Nacional de Bases de Datos (RNBD).** Solo están obligados a registrar: sociedades y entidades sin ánimo de lucro con **activos totales superiores a 100.000 UVT**, y las personas jurídicas de naturaleza pública. **No** están obligadas las micro y pequeñas empresas ni las personas naturales. *Fuente: Ley 1581 de 2012, art. 25; Decreto 090 de 2018.* `[VERIFICAR]` la numeración exacta del artículo compilado en el Decreto 1074 de 2015 y si el umbral cambió después de 2018.

**Sanciones.** La SIC puede imponer multas, suspender actividades relacionadas con el tratamiento, cerrar temporalmente operaciones y, en casos graves, cerrar inmediata y definitivamente la operación que involucre tratamiento de datos sensibles. *Fuente: Ley 1581 de 2012, art. 23.* `[VERIFICAR]` cuantías vigentes en SMLMV.

## 6. Deberes de información al consumidor financiero: qué le aplica a Júbilo

**Regla de fondo: la Ley 1328 de 2009 no le aplica directamente a Júbilo.** Su ámbito son "las relaciones entre estos [los consumidores financieros] y **las entidades vigiladas por la Superintendencia Financiera de Colombia**". *Fuente: Ley 1328 de 2009, art. 1.* Júbilo no es entidad vigilada, no administra recursos de nadie y no intermedia.

**Consecuencias, y hay que ser explícito con las dos caras:**

- Júbilo **no tiene** Defensor del Consumidor Financiero ni Sistema de Atención al Consumidor Financiero, y **no puede** ofrecerlos ni insinuarlos. Quien sí los tiene es el fondo del usuario (ver `reclamacion-y-defensa.md` sección 7).
- Júbilo **no puede presentarse** como asesor autorizado, ni como sustituto de la **doble asesoría obligatoria** para trasladarse de régimen (`reglas-traslados.md` sección 2).
- El estándar de información del art. 9 de la Ley 1328 (información **cierta, suficiente y oportuna**, que permita y facilite comparar las opciones del mercado) **se adopta voluntariamente como listón de calidad**, aunque no obligue. Es exactamente lo que ya hace el kit: rangos, supuestos visibles y ambos regímenes comparados.

`[VERIFICAR]` Dos puntos con el abogado, porque son los que podrían cambiar el régimen aplicable:
1. Si cobrar por el servicio, o recibir comisión por referir usuarios a una administradora o a un abogado, convierte a Júbilo en algo distinto a un tercero informativo.
2. Qué obligaciones le impone el Estatuto del Consumidor (Ley 1480 de 2011) a Júbilo como proveedor de un servicio digital, en particular en materia de información veraz y suficiente y de publicidad engañosa. No se verificó articulado; no citar artículos hasta confirmarlos.

---

# Parte 2. Alcance de Júbilo: respuestas listas

**Cómo se usan estas respuestas:** son el guion, no un texto para pegar tal cual. Se dicen en el estilo crisp del `system-prompt.md` (un mensaje, una idea) y sin narrar maquinaria interna.

## 7. "¿Qué hacen con mis datos?"

**Respuesta propuesta:** "Uso tu historia laboral para dos cosas: calcular tu diagnóstico pensional y, de forma anónima, mejorar el producto. No la publico, no la vendo y no se la doy a nadie."

- Sustento: principio de finalidad y recolección limitada (*Ley 1581, art. 4 lit. b; Decreto 1377, art. 4*). La segunda finalidad va declarada porque un uso distinto exige informarlo y autorizarlo aparte (*Decreto 1377, art. 5*); ver sección 12 punto 3.
- **Antes de recibir el documento**, el agente debe haber mostrado un **aviso de privacidad** corto (contenido mínimo del *Decreto 1377, art. 15*) y pedir autorización. Adjuntar el documento después de ese aviso es una **conducta inequívoca** válida (*Decreto 1377, art. 7*), pero **el aviso tiene que haber ido primero y quedar registrado**.

**DECIDIDO (Santiago, 2026-07-27): autorización por conducta inequívoca, con aviso previo al envío del documento.** No hay botón de "Acepto". El texto exacto del aviso vive en `aviso-de-privacidad.md` y se muestra siempre antes de pedir la historia laboral.

Reglas que se derivan de la decisión, y que el agente debe cumplir sin excepción:

1. **El aviso va primero, siempre.** Si el usuario manda el documento antes de haberlo visto, el agente no procesa: muestra el aviso y espera a que lo reenvíe. El silencio nunca equivale a autorización (*Decreto 1377, art. 7*).
2. **El aviso documenta los dos puntos que lo exigen.** La historia laboral puede traer datos de salud, que son sensibles (*Ley 1581, art. 6*), y el procesamiento ocurre fuera de Colombia (*Ley 1581, art. 26*). Por eso el aviso dice expresamente que responder sobre datos sensibles es facultativo (*Decreto 1377, art. 15 par.*) y cierra con la línea "al enviarme tu historia laboral aceptas que la procese, incluyendo servidores fuera de Colombia".
3. **Queda prueba.** Se registra la fecha y hora en que se mostró el aviso, su versión, y el envío del documento que siguió. Eso es la prueba de la autorización que el responsable debe conservar y entregar si el titular la pide (*Ley 1581, art. 12 par.; Decreto 1377, art. 8*). El procedimiento está en `../cumplimiento/manual-interno-tratamiento-datos.md`.
4. **El servicio no se condiciona a datos sensibles.** Si el usuario tacha o no envía las novedades de salud de su historia laboral, el diagnóstico se hace igual con lo que haya (*Decreto 1377, art. 6*).

**Por qué conducta inequívoca y no botón:** es una forma de autorización expresamente válida (*Decreto 1377, art. 7*), y el canal del piloto es un chat de Telegram donde un botón añade un turno sin añadir prueba: el registro del aviso previo más el envío del documento prueba lo mismo. **Qué cambiaría si el abogado dice otra cosa:** se agrega un turno con confirmación explícita antes de aceptar el archivo; no cambia nada más del flujo.

## 8. "¿Los guardan?"

**DECIDIDO (Santiago, 2026-07-21): opción B.** Se guarda **solo el JSON extraído; el archivo original (PDF o imagen) se borra apenas termina la extracción.**

**Respuesta del agente, ya utilizable:** "Del documento me quedo con los números que necesito para tu diagnóstico. El archivo original no lo guardo. Si quieres que borre todo, me dices y lo hago."

Reglas que se derivan de la decisión:
- **El archivo original se suprime al terminar la extracción**, no al cerrar la conversación. Si el usuario vuelve, se le pide de nuevo.
- **Nunca se repite la cédula ni datos personales innecesarios** en la conversación (ya es la regla dura 7 del `system-prompt.md`); con más razón si no se conserva el documento.
- **Borrado a solicitud**, sin fricción y sin preguntar por qué.
- El JSON sigue siendo dato personal: le aplica todo el régimen de la Parte 1 de este documento.

**DECIDIDO (Santiago, 2026-07-27): la conservación se ata a la finalidad, no al calendario.** El JSON y la conversación anonimizada se conservan **mientras sirvan a la finalidad declarada** (dar el diagnóstico y mejorar el producto), con **revisión anual documentada** de si esa finalidad sigue viva, y se borran **cuando el usuario lo pida**, sin plazo mínimo.

- **Por qué no un plazo fijo:** la ley no fija uno. Manda conservar "durante el tiempo que sea razonable y necesario, de acuerdo con las finalidades que justificaron el tratamiento", y suprimir cumplida la finalidad (*Decreto 1377, art. 11*). Un calendario de 12 o 24 meses sería una cifra inventada que después habría que defender.
- **Qué exige a cambio:** que el procedimiento de conservación y supresión esté **documentado** y que la revisión anual deje registro. Ambos están en `../cumplimiento/manual-interno-tratamiento-datos.md`, sección de conservación.
- **Lo que no se conserva en ningún caso:** el PDF o la imagen original, que se borra al terminar la extracción.
- **Respuesta del agente si preguntan cuánto tiempo:** "Los números me los quedo mientras te sirvan a ti y me sirvan para mejorar. No hay un plazo fijo: si me pides que borre, borro ese mismo día."

El análisis que sustentó la decisión se conserva abajo.

**Política de retención: las tres opciones que se evaluaron.**

| Opción | Qué se guarda | A favor | En contra |
|---|---|---|---|
| **A. Cero retención** | Nada. Se procesa el documento y se borra al cerrar la conversación | Es la respuesta más fuerte comercialmente ("no guardo nada"), reduce al mínimo la exposición y el riesgo regulatorio | El usuario debe volver a subir el documento cada vez; se pierde el histórico para mejorar el producto |
| **B. Solo el JSON extraído, sin el documento** | Semanas, IBC, fechas. Se borra el PDF o la imagen original | Permite continuidad de la conversación y análisis agregados; elimina de raíz el riesgo de guardar datos sensibles que venían adheridos al documento | Sigue siendo dato personal y sigue exigiendo todo el régimen de la Parte 1 |
| **C. Documento y JSON, con plazo definido** | Todo, hasta X (por ejemplo 12 meses o hasta que el usuario pida borrarlo) | Máximo valor de producto y de soporte | Máxima exposición; obliga a política formal, medidas de seguridad y procedimiento documentado de supresión (*Decreto 1377, art. 11*) |

**Recomendación:** B como default, con supresión inmediata del archivo original y borrado a solicitud en un clic. Conserva casi todo el valor con una fracción del riesgo, y da una respuesta corta y verdadera: "Del documento me quedo con los números; el archivo original no lo guardo."

**Restricción legal de la que no se escapa ninguna opción:** una vez cumplida la finalidad hay que suprimir, y el procedimiento de conservación y supresión debe estar **documentado** (*Decreto 1377, art. 11*). Elegir la opción C sin escribir esa política es incumplir.

*(La respuesta provisional de "todavía lo estamos definiendo" quedó sin efecto: el punto está cerrado arriba.)*

## 9. "¿Se los dan a mi fondo?"

**Respuesta propuesta:** "No. Yo no hablo con tu fondo ni le mando nada. Tu fondo ya tiene esa información, es él quien te la entregó a ti."

- Sustento: la información solo puede suministrarse al titular, a sus causahabientes o representantes, a autoridades en ejercicio de funciones legales u orden judicial, y a **terceros autorizados por el titular o por la ley** (*Ley 1581, art. 13*). Sin autorización específica del usuario, no hay a quién entregarla.
- Complemento útil y verdadero: Júbilo tampoco puede hacer trámites en el portal del fondo. Ya se evaluó y se descartó (`system-prompt.md`, "Formatos de ingesta").
**DECIDIDO (Santiago, 2026-07-27): Júbilo no recibe comisiones por referir, nunca.** Ni de fondos de pensiones, ni de aseguradoras, ni de abogados. No es una política provisional del piloto: es una restricción del modelo de negocio.

- **El agente puede decirlo como diferenciador**, sin esperar a que se lo pregunten, cuando el usuario esté comparando regímenes, evaluando un traslado o eligiendo modalidad de pensión. Frase utilizable: "No me pagan por mandarte a ningún fondo, aseguradora ni abogado. Si te recomiendo algo es porque los números lo dicen."
- **Qué no se hace:** convertirlo en muletilla. Se dice una vez, donde aporta, igual que el disclaimer de la sección 10.
- **Por qué importa legalmente y no solo comercialmente:** cobrar por referir es justo lo que podría sacar a Júbilo de la categoría de tercero informativo (ver la marca `[VERIFICAR]` de la sección 6). Al cerrar la puerta a las comisiones, ese riesgo se elimina de raíz en lugar de gestionarse.
- **Si algún día cambia:** hay que declarar el conflicto de interés de frente, sin que el usuario pregunte, y rehacer el análisis de la sección 6. La credibilidad del comparador de regímenes depende por completo de que no haya un interés escondido.

## 10. "¿Esto es asesoría legal?"

**Respuesta propuesta:** "No. Te explico cómo funciona el sistema y te doy números con supuestos claros. No soy abogado y lo que te digo no es un concepto jurídico ni te sirve como prueba en un proceso."

- Coherente con la regla dura 6 del `system-prompt.md`.
- **Cuándo se dice, sin que lo pregunten:** cuando el usuario menciona demanda, tutela, negativa del fondo, ineficacia de traslado, o pide que Júbilo le redacte algo. El detalle de la frontera está en `reclamacion-y-defensa.md` sección 1.
- **Lo que no se hace:** repetir el disclaimer en cada mensaje. Aparece cuando aporta, no como muletilla.

## 11. "¿Ustedes me tramitan la pensión?"

**Respuesta propuesta:** "No. Te digo exactamente qué pedir, ante quién y en qué orden, y qué plazos tienen para responderte. El trámite lo radicas tú."

- Sustento operativo: `reclamacion-y-defensa.md` secciones 2, 3 y 4.
- Cierre útil, no defensivo: se le entrega el paso siguiente concreto (dónde radicar, qué llevar, cuánto se pueden demorar).

## 12. Otros puntos de producto: decididos el 2026-07-27

Los siete primeros están **cerrados y son aplicables**. Los dos últimos siguen con marca `[VERIFICAR]`: tienen respuesta operativa, y lo que espera confirmación es el respaldo.

**1. Responsable del tratamiento. DECIDIDO: Jose Santiago Sierra Garcia, persona natural.** No hay sociedad detrás del piloto y no se finge que la haya. Se identifica con nombre completo y correo de contacto en el aviso de privacidad, que es el contenido mínimo que exige el *Decreto 1377, art. 15 num. 1* (nombre o razón social **y** datos de contacto del responsable).

- Ser persona natural no atenúa ninguna obligación: la Ley 1581 aplica al tratamiento hecho por personas naturales y jurídicas por igual (*Ley 1581, art. 2*). Lo único que cambia es el RNBD (punto 7).
- **Correo de contacto:** `bot.jubilo@gmail.com`, **definido el 2026-09-16**. Es el buzón que Santiago atiende y el que se publica en el aviso de privacidad y en la política de tratamiento en versión de usuario.
- **Si Júbilo se constituye como sociedad**, cambia el responsable, cambia el aviso y hay que revisar el punto 7.

**2. Canal para ejercer derechos. DECIDIDO: comando dentro del chat más correo, y responde Santiago.**

| Vía | Cómo | Para qué |
|---|---|---|
| **Comando en el chat** | El usuario escribe que quiere borrar, ver o corregir sus datos | Es la vía de default: gratuita, inmediata y sin salir del canal |
| **Correo** | La dirección publicada en el aviso de privacidad | Para quien ya no usa el bot, o quiere constancia escrita |

- Cumple el requisito de mecanismos **gratuitos y de fácil acceso** (*Decreto 1377, art. 9*) y el deber de tener un área o persona que atienda peticiones (*Decreto 1377, art. 13*).
- **Quién responde:** Santiago, dentro de los términos legales de **10 días hábiles** para consultas y **15 días hábiles** para reclamos (*Ley 1581, arts. 14 y 15*), con las prórrogas de 5 y 8 días hábiles avisando motivos y fecha.
- **La supresión no espera al término.** Si el usuario pide borrado por el comando del chat, se ejecuta el mismo día. El plazo de 15 días es un techo legal, no una meta.
- El procedimiento completo, con el registro de solicitudes, está en `../cumplimiento/manual-interno-tratamiento-datos.md`.

**3. Uso de conversaciones. DECIDIDO: se guardan anonimizadas, declarado como finalidad aparte.**

- Es una finalidad **distinta** a dar el diagnóstico, así que va informada y autorizada por separado (*Decreto 1377, art. 5*): aparece como segunda finalidad en el aviso de privacidad, no escondida dentro de la primera.
- **Anonimizadas quiere decir** sin cédula, sin nombre, sin fechas de nacimiento y sin el identificador de Telegram. Quedan los números del caso y el texto de la conversación despersonalizado.
- **Para qué sirven:** detectar preguntas que el agente no supo responder, corregir el corpus y ampliar el set dorado. No se usan para perfilar ni contactar a nadie.
- **Honestidad sobre el límite:** un dato realmente anonimizado deja de ser dato personal, pero la anonimización de un texto libre nunca es perfecta. Por eso el tratamiento se sigue manejando bajo el régimen completo de la Parte 1 en lugar de declararlo fuera de la ley por anónimo.

**4. Manual interno de políticas y procedimientos. HECHO.** Obligación del responsable (*Ley 1581, art. 17 lit. k*), en especial para atender consultas y reclamos. Está en `../cumplimiento/manual-interno-tratamiento-datos.md`, y recoge además el contenido mínimo de la política de tratamiento del *Decreto 1377, art. 13*.

**5. Procedimiento ante incidentes de seguridad. HECHO.** Obligación de informar a la SIC las violaciones a los códigos de seguridad y los riesgos en la administración de la información (*Ley 1581, art. 17 lit. n*). Está en `../cumplimiento/procedimiento-incidentes-seguridad.md`.

**6. Menores de edad. DECIDIDO: no se atienden menores de 18 años.**

- **Fundamento:** el tratamiento de datos de niños, niñas y adolescentes está proscrito salvo los de naturaleza pública, y aun esos exigen respetar el interés superior del menor y sus derechos fundamentales (*Ley 1581, art. 7; Decreto 1377, art. 12*). Una historia laboral no es dato público.
- **Cómo lo detecta el agente:** si la fecha de nacimiento de la historia laboral o algo que diga el usuario indica menos de 18 años, no procesa el documento y lo dice.
- **Cómo lo dice, con amabilidad y sin humillar:** "Por ahora solo puedo atender a mayores de 18 años, y por tu fecha de nacimiento todavía no estás en ese grupo. No es un capricho mío: la ley colombiana es especialmente estricta con los datos de menores. Si quieres, esto le sirve a alguien de tu familia."
- **Qué hace con lo ya recibido:** borra el documento y no guarda el JSON.
- **Nota de realidad:** el caso es raro. Un menor de 18 casi nunca tiene historia laboral relevante, y el costo de cubrirlos bien (verificación de edad y autorización del representante legal) es desproporcionado para el piloto.

**7. Registro Nacional de Bases de Datos. DECIDIDO: no se registra en el piloto.** Bajo el umbral vigente solo están obligadas las sociedades y entidades sin ánimo de lucro con activos superiores a 100.000 UVT y las personas jurídicas de naturaleza pública; **las personas naturales no** (*Ley 1581, art. 25; Decreto 090 de 2018*). Como el responsable es persona natural (punto 1), no hay obligación. Ver la marca `[VERIFICAR]` de la sección 5 sobre la numeración compilada y el umbral posterior a 2018. **Se revisa el día en que Júbilo cambie de vehículo jurídico.**

**8. Mensajes proactivos y marketing.**

`[VERIFICAR]` **si la Ley 2300 de 2023** (protección de la tranquilidad del consumidor frente a contactos comerciales) le aplica a un bot que no es entidad financiera. No se verificó el articulado.

- **Respuesta operativa, lo que se hace hoy:** el agente **no envía mensajes proactivos de ningún tipo**. Solo responde. Si en el futuro se quiere avisar algo (un cambio de norma que afecta al usuario), se pide autorización expresa para ese contacto, con horario y frecuencia, y con salida fácil.
- **Qué falta confirmar:** ámbito de aplicación de la Ley 2300, si cubre canales de mensajería como Telegram, y qué exige exactamente para un contacto no comercial de servicio.
- **Qué cambiaría:** si aplica, hay que montar el registro de preferencias de contacto y respetar los horarios que fije. Si no aplica, la autorización de la Ley 1581 basta. En ninguno de los dos escenarios cambia lo que se hace hoy, que es no contactar a nadie.
- **Regla dura entretanto:** el agente **no cita la Ley 2300 al usuario** hasta confirmarla.

**9. Alojamiento y procesamiento de datos fuera de Colombia.**

`[VERIFICAR]` **la lista vigente de países declarados con nivel adecuado de protección por la SIC.** No se verificó cuál es el acto administrativo vigente ni su contenido actual.

- **El hecho, sin adornos (actualizado el 2026-09-16, cambió el despliegue):** el piloto corre como un **bot de Telegram propio en un VPS que administra Santiago**, con un backend en Python que invoca `claude -p` una vez por mensaje y una base SQLite propia. Es decir: el **almacenamiento** pasó a estar bajo control directo del responsable, y el **procesamiento del modelo** sigue ocurriendo en infraestructura de un tercero y **fuera de Colombia**. Eso último sigue activando el art. 26 de la Ley 1581, que prohíbe la transferencia a países que no acrediten nivel adecuado de protección. La descripción anterior ("sobre Claude Code, sin servidor propio") quedó vencida, y el análisis de riesgo de esta separación en dos capas está anotado para el abogado en `../cumplimiento/manual-interno-tratamiento-datos.md` s.5 punto 1.
- **Respuesta operativa, lo que se hace hoy:** se usa la excepción de la **autorización expresa e inequívoca del titular** para la transferencia (*Ley 1581, art. 26 lit. f*). Por eso el aviso de privacidad dice explícitamente que el procesamiento incluye servidores fuera de Colombia, antes de que el usuario mande el documento. La autorización cubre la transferencia igual que cubre el tratamiento.
- **Qué falta confirmar:** (i) el acto de la SIC vigente con la lista de países adecuados y si Estados Unidos está en ella; (ii) si el abogado considera suficiente la autorización del lit. f para datos que pueden ser sensibles, o exige además contrato de transmisión de datos con el encargado (*Decreto 1377, arts. 24 y 25*).
- **Qué cambiaría:** si el país de procesamiento resulta estar en la lista de adecuados, la autorización deja de ser el sustento y el punto se simplifica. Si el abogado exige contrato de transmisión, hay que suscribirlo con el proveedor de infraestructura antes del piloto, o mover el procesamiento a Colombia. **Es el punto de mayor riesgo regulatorio abierto del producto**, y el primero que debe mirar el abogado.

## 13. Fuera de alcance de este documento

| Tema | A dónde va |
|---|---|
| Quejas sobre la pensión, el fondo o el trámite | `reclamacion-y-defensa.md` sección 7 |
| Doble asesoría obligatoria para traslados | `reglas-traslados.md` sección 2 |
| Cómo se descarga la historia laboral en cada portal | `tramites-y-consultas.md` |
| Reclamos de datos personales contra el **fondo** (no contra Júbilo) | Se orienta el camino (reclamo al responsable y luego SIC, *Ley 1581, arts. 15 y 16*), pero el caso es del usuario con su fondo |
| Redacción del texto legal definitivo (política de tratamiento, términos y condiciones, aviso de privacidad) | **Abogado de protección de datos.** Este documento da el contenido mínimo exigido, no el texto legal |
| Régimen aplicable si Júbilo llega a ser entidad vigilada o a intermediar | Fuera de alcance. Cambia el análisis completo y hay que rehacerlo |
