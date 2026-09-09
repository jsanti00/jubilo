# Manual interno de políticas y procedimientos de tratamiento de datos personales

> **Documento interno. No se muestra al usuario.** Lo que el usuario ve es `../kit-contexto/aviso-de-privacidad.md`.
> **Versión:** 1.0. **Fecha de entrada en vigencia:** 2026-07-27. **Estado:** borrador operativo, pendiente de revisión de abogado de protección de datos (ver sección 5).
> **Por qué existe:** el responsable está obligado a adoptar un manual interno de políticas y procedimientos para garantizar el cumplimiento de la ley y, en especial, para la atención de consultas y reclamos. *Fuente: Ley 1581 de 2012, art. 17 lit. k.* Confianza alta.
> **Qué recoge además:** el contenido mínimo de la política de tratamiento de la información del *Decreto 1377 de 2013, art. 13*. Confianza alta.
> **Documentos hermanos:** `procedimiento-incidentes-seguridad.md` (mismo folder) y `../kit-contexto/datos-y-alcance.md` (sustento normativo detallado).
> **Regla de coherencia:** este manual **no puede prometer menos ni distinto** que el aviso de privacidad. Si alguna vez difieren, manda el aviso, porque es el texto que vio el titular, y este manual se corrige.
> **Nota sobre el orden:** la sección 5 es la lista de puntos que requieren revisión del abogado. Está en ese número porque el aviso de privacidad la referencia así; no se renumera.

---

## 1. Identificación del responsable y alcance

**Responsable del tratamiento.** Jose Santiago Sierra Garcia, persona natural. No hay sociedad detrás del piloto y no se representa que la haya. *Decisión de Santiago del 2026-07-27.*

- Ser persona natural no atenúa ninguna obligación: la ley aplica al tratamiento hecho por personas naturales y jurídicas por igual. *Fuente: Ley 1581 de 2012, art. 2.* Confianza alta.
- **Datos de contacto publicados:** correo electrónico `[POR DEFINIR]`. Es el contenido mínimo del *Decreto 1377 de 2013, art. 15 num. 1*, y sin él el aviso de privacidad no se puede publicar. Es un dato operativo pendiente, no una decisión abierta.
- **Persona que atiende peticiones:** el propio responsable. No hay área ni delegado. Cumple el requisito de identificar al área o persona encargada del *Decreto 1377 de 2013, art. 13 num. 4*. Confianza alta.

**Alcance.** Aplica a todo el tratamiento de datos personales que ocurre en el piloto de Júbilo: el canal de Telegram, los archivos que el usuario envía, los datos extraídos de ellos y las conversaciones anonimizadas.

**Arquitectura real, porque define el riesgo.** El piloto corre en un canal de Telegram con Claude Code como motor de razonamiento, **sin servidor propio ni base de datos administrada**. El agente lee la historia laboral (PDF o imagen), extrae un JSON con los datos del caso y **borra el archivo original apenas termina la extracción** (*decisión de Santiago del 2026-07-21, opción B*). El procesamiento ocurre **fuera de Colombia**. Los datos que se conservan viven en el equipo del responsable y en la infraestructura del proveedor del modelo y del canal de mensajería.

**Consecuencia honesta de esa arquitectura:** el responsable **no controla directamente** la infraestructura donde se procesan los datos. Los controles reales están enumerados en la sección 6 y los que faltan están marcados ahí como faltantes, no descritos como si existieran.

**Quién más interviene.** No hay empleados, contratistas ni encargados contratados por el responsable para tratar datos. Los proveedores de infraestructura (mensajería y modelo) actúan de hecho como encargados del tratamiento, sin contrato de transmisión de datos suscrito para este fin. Ver sección 5, punto 2.

---

## 2. Datos que se tratan y finalidades

**Datos recolectados.**

| Categoría | Ejemplos | Clasificación | Fuente |
|---|---|---|---|
| Datos del caso pensional | Semanas cotizadas, IBC históricos, fechas de afiliación y de novedades, sexo, fecha de nacimiento | Semiprivado | Ley 1266 de 2008, art. 3 lit. g |
| Identificadores | Nombre, cédula, identificador de Telegram | Semiprivado | Ley 1581 de 2012, art. 3 |
| Datos que pueden venir adheridos | Incapacidades, licencias, calificación de invalidez, aportes a sindicato, régimen de alto riesgo | **Sensibles** | Ley 1581 de 2012, art. 5 |
| Contenido de la conversación | Preguntas del usuario y respuestas del agente | Semiprivado hasta la anonimización | Ley 1581 de 2012, art. 3 |

La historia laboral es además **información reservada** que solo puede solicitar el titular, su apoderado o quien tenga facultad expresa. *Fuente: Ley 1755 de 2015, art. 24 num. 3 y parágrafo.* Confianza alta. Operativamente esto significa que Júbilo **solo recibe el documento de manos del propio titular**, nunca de un tercero.

**Finalidades declaradas. Son dos y se declaran por separado.** *Decisión de Santiago del 2026-07-27.*

1. **Calcular el diagnóstico pensional del titular.** Es la finalidad principal.
2. **Conservar la conversación anonimizada para mejorar el producto.** Es una finalidad distinta, así que se informa y autoriza aparte, no escondida dentro de la primera. *Fuente: Decreto 1377 de 2013, art. 5.* Confianza alta.

**Anonimizar significa** eliminar cédula, nombre, fecha de nacimiento e identificador de Telegram, dejando los números del caso y el texto despersonalizado. **Límite reconocido:** la anonimización de texto libre nunca es perfecta, así que ese material se sigue tratando bajo el régimen completo de la Ley 1581 en lugar de declararlo fuera de la ley por anónimo.

**Usos prohibidos, sin excepción.**

- **No hay comisiones por referir a fondos de pensiones, aseguradoras ni abogados. Nunca.** No es política del piloto: es restricción del modelo de negocio. *Decisión de Santiago del 2026-07-27.* Además de lo comercial, cierra de raíz el riesgo de que Júbilo deje de ser un tercero informativo (ver sección 5, punto 6).
- No se vende, publica ni cede la información a terceros. La información solo puede suministrarse al titular, a sus causahabientes o representantes, a autoridades en ejercicio de funciones legales u orden judicial, y a terceros autorizados por el titular o por la ley. *Fuente: Ley 1581 de 2012, art. 13.* Confianza alta.
- No se envían mensajes proactivos ni comerciales de ningún tipo. El agente solo responde.
- No se usan los datos para perfilar ni para contactar a nadie.
- **Recolección limitada:** solo se piden datos pertinentes y adecuados para la finalidad, y está prohibido usar medios engañosos para obtenerlos. *Fuente: Decreto 1377 de 2013, art. 4.* Confianza alta.

**Menores de 18 años: no se atienden.** *Decisión de Santiago del 2026-07-27.* El tratamiento de datos de niños, niñas y adolescentes está proscrito salvo los de naturaleza pública, y una historia laboral no lo es. *Fuente: Ley 1581 de 2012, art. 7; Decreto 1377 de 2013, art. 12.* Confianza alta. Si la fecha de nacimiento o algo que diga el usuario indica menos de 18 años, el agente **no procesa** el documento, lo dice con amabilidad, **borra el archivo y no guarda el JSON**.

---

## 3. Ciclo de vida del dato: autorización, conservación y supresión

### 3.1 Autorización

**Forma adoptada: conducta inequívoca del titular, con aviso previo.** Adjuntar la historia laboral después de haber visto el aviso de privacidad es la conducta que constituye la autorización. Es una forma expresamente válida. *Fuente: Decreto 1377 de 2013, art. 7.* Confianza alta.

**Procedimiento obligatorio, en este orden:**

1. El agente muestra el aviso de privacidad **antes** de pedir la historia laboral, una vez por usuario, en el turno inmediatamente anterior a la solicitud del documento.
2. Se registra la **fecha, la hora y la versión** del aviso mostrado.
3. El usuario envía el documento.
4. Se registra la fecha y hora del envío.

El par (aviso mostrado, documento enviado) es la prueba de la autorización que el responsable debe conservar y entregar al titular si la pide. *Fuente: Ley 1581 de 2012, art. 12 par.; Decreto 1377 de 2013, art. 8.* Confianza alta.

**Reglas duras.**

- **Si el usuario manda el documento sin haber visto el aviso, no se procesa.** Se muestra el aviso y se le pide que lo reenvíe. El silencio nunca equivale a conducta inequívoca. *Fuente: Decreto 1377 de 2013, art. 7.* Confianza alta.
- **El aviso cubre los dos puntos que lo exigen:** que responder sobre datos sensibles es facultativo (*Decreto 1377, art. 15 par. y art. 6*) y que el procesamiento ocurre fuera de Colombia (*Ley 1581, art. 26 lit. f*). Confianza alta.
- **El servicio nunca se condiciona a la entrega de datos sensibles.** Si el usuario tacha las novedades de salud, el diagnóstico se hace igual con lo que quede. *Fuente: Decreto 1377 de 2013, art. 6 num. 3.* Confianza alta.
- **Si cambia la finalidad, se pide autorización nueva.** No se reutiliza la anterior. *Fuente: Decreto 1377 de 2013, art. 5.* Confianza alta.

**Versionado del aviso.** Cada cambio material genera una versión nueva. Debe poder reconstruirse **qué versión vio cada usuario**. Versión vigente: 1.0.

### 3.2 Conservación

**Regla adoptada: la conservación se ata a la finalidad, no al calendario.** *Decisión de Santiago del 2026-07-27.*

| Elemento | Qué pasa con él | Cuándo |
|---|---|---|
| Archivo original (PDF o imagen) | Se **borra** | Apenas termina la extracción, no al cerrar la conversación |
| JSON extraído | Se conserva mientras sirva a la finalidad declarada | Hasta que el titular pida borrarlo o la revisión anual concluya que la finalidad se agotó |
| Conversación anonimizada | Se conserva mientras sirva a la mejora del producto | Igual criterio |
| Registro de aviso mostrado y autorización | Se conserva mientras exista el dato asociado y mientras sea prueba exigible | Ver sección 5, punto 5 |

**Fundamento.** La ley no fija plazo. Manda conservar "durante el tiempo que sea razonable y necesario, de acuerdo con las finalidades que justificaron el tratamiento", suprimir cumplida la finalidad, y **documentar los procedimientos** de tratamiento, conservación y supresión. *Fuente: Decreto 1377 de 2013, art. 11.* Confianza alta. Un plazo de 12 o 24 meses sería una cifra inventada que después habría que defender.

**Revisión anual documentada.** Cada 12 meses, contados desde la entrada en vigencia de este manual, el responsable revisa por escrito, en la sección 7 de este documento:

1. Si la finalidad que justificó conservar los datos sigue viva.
2. Qué se suprimió en el periodo y por qué.
3. Si la arquitectura cambió y con ella el análisis de riesgo.

Sin ese registro, la política de conservación atada a finalidad queda sin sustento. **Primera revisión programada: 2027-07-27.**

### 3.3 Supresión

- **A solicitud del titular: el mismo día, gratis y sin preguntar por qué.** El plazo legal de 15 días hábiles para el reclamo es un techo, no una meta. Así se lo promete el aviso de privacidad y el manual no lo puede rebajar.
- **De oficio:** cuando la revisión anual concluya que la finalidad se agotó.
- **Límite legal reconocido:** la supresión y la revocatoria no proceden cuando el titular tiene deber legal o contractual de permanecer en la base de datos. *Fuente: Decreto 1377 de 2013, art. 9.* Confianza alta. **En Júbilo no existe hoy ningún caso así**, porque no hay contrato ni obligación legal de retención. Si algún día lo hay, se documenta aquí antes de invocarlo.
- **Qué implica borrar, en concreto:** eliminar el JSON del caso, el registro de la conversación asociada y cualquier copia local o respaldo. Ver sección 5, punto 3, sobre la verificación del borrado en infraestructura de terceros.
- **Se deja constancia** de cada supresión en el registro de la sección 7.

---

## 4. Procedimiento de atención de consultas y reclamos

Es el núcleo del deber del *art. 17 lit. k* y el que la SIC revisa primero.

### 4.1 Canales

| Vía | Cómo se activa | Para quién |
|---|---|---|
| **Comando en el chat** | El usuario escribe "mis datos" o pide ver, corregir o borrar sus datos | Vía por defecto: gratuita, inmediata, sin salir del canal |
| **Correo electrónico** | La dirección publicada en el aviso de privacidad | Quien ya no usa el bot o quiere constancia escrita |

Ambos son gratuitos y de fácil acceso, como exige el *Decreto 1377 de 2013, art. 9*. Confianza alta. **Quien responde es Santiago**, en persona.

### 4.2 Términos

| Solicitud | Qué es | Término | Prórroga | Fuente |
|---|---|---|---|---|
| **Consulta** | Ver sus datos, saber el uso dado a ellos, pedir prueba de la autorización | 10 días hábiles | 5 días hábiles más, avisando motivos y fecha de respuesta | Ley 1581, art. 14 |
| **Reclamo** | Corregir, actualizar, suprimir o revocar la autorización | 15 días hábiles | 8 días hábiles más, avisando motivos y fecha | Ley 1581, art. 15 |

Confianza alta en ambos. **Excepción autoimpuesta:** el borrado solicitado se ejecuta el mismo día.

### 4.3 Pasos operativos

1. **Recepción.** Se registra en la tabla de la sección 7: fecha, canal, identificador del solicitante, tipo de solicitud.
2. **Clasificación.** Consulta o reclamo, según la tabla de 4.2. Ante duda, se trata como reclamo, que es el término más exigente para el responsable.
3. **Marcación.** Mientras se decide un reclamo, el registro asociado lleva la leyenda **"reclamo en trámite"** y el motivo. *Fuente: Ley 1581 de 2012, art. 15.* Confianza alta.
4. **Reclamo incompleto.** Se requiere al titular dentro de los 5 días siguientes. Si pasan 2 meses sin que responda, se entiende desistido. *Misma fuente.*
5. **Falta de competencia.** Si la solicitud es contra el fondo de pensiones y no contra Júbilo, se traslada o se orienta dentro de los 2 días hábiles siguientes y se le informa al titular. *Misma fuente.*
6. **Respuesta.** Por el mismo canal por el que llegó, salvo que el titular pida otro. Se deja copia en el registro.
7. **Cierre.** Se anota fecha de respuesta y resultado.

### 4.4 Derechos que se garantizan

Conocer, actualizar, rectificar, suprimir, revocar la autorización, pedir prueba de la autorización, saber el uso dado a los datos, y quejarse ante la SIC. *Fuente: Ley 1581 de 2012, art. 8.* Confianza alta.

**Requisito de procedibilidad.** El titular solo puede quejarse ante la SIC después de agotar la consulta o el reclamo ante el responsable. *Fuente: Ley 1581 de 2012, art. 16.* Confianza alta. **El agente no usa esto como barrera**: el aviso deliberadamente no lo menciona, y si el usuario dice que va a la SIC, no se le responde que primero debe reclamar aquí.

### 4.5 Lo que el agente nunca hace

- Preguntar por qué el usuario quiere borrar sus datos.
- Cobrar por una consulta, un reclamo o una copia de la autorización.
- Repetir la cédula o datos personales innecesarios en la conversación.
- Recibir la historia laboral de alguien distinto al titular.

---

## 5. Puntos que requieren revisión del abogado de protección de datos

Esta es la lista que el aviso de privacidad referencia. Cada punto dice **qué se hace hoy**, **qué falta confirmar** y **qué cambiaría** si la respuesta es distinta. Están ordenados por riesgo, de mayor a menor.

**1. Transferencia y procesamiento fuera de Colombia. Es el punto de mayor riesgo abierto.** `[VERIFICAR]`

- **Hoy:** el sustento es la autorización expresa e inequívoca del titular para la transferencia (*Ley 1581 de 2012, art. 26 lit. f*), obtenida por el aviso previo que menciona expresamente los servidores fuera de Colombia.
- **Falta confirmar:** (i) cuál es el acto administrativo vigente de la SIC con la lista de países declarados con nivel adecuado de protección, y si el país de procesamiento está en ella; (ii) si la autorización del lit. f basta cuando los datos pueden ser sensibles, o si además se exige contrato de transmisión de datos con el encargado (*Decreto 1377 de 2013, arts. 24 y 25*).
- **Qué cambiaría:** si el país está en la lista de adecuados, la autorización deja de ser el sustento y el punto se simplifica. Si se exige contrato de transmisión, hay que suscribirlo con el proveedor de infraestructura antes del piloto, o mover el procesamiento a Colombia.

**2. Calificación de los proveedores de infraestructura como encargados del tratamiento.**

- **Hoy:** el canal de mensajería y el proveedor del modelo procesan datos personales por cuenta del responsable sin contrato específico de tratamiento de datos, más allá de sus términos de servicio estándar.
- **Falta confirmar:** si esa relación configura encargo del tratamiento y qué documento mínimo la debe soportar.
- **Qué cambiaría:** si se requiere contrato, hay que suscribirlo o cambiar de arquitectura antes del piloto. Enlaza con el punto 1.

**3. Suficiencia del borrado del archivo original.**

- **Hoy:** el agente borra el PDF o la imagen apenas termina la extracción.
- **Falta confirmar:** si el borrado local basta cuando el archivo pasó por la infraestructura de un tercero que puede conservar copias o registros temporales, y qué debe decirse al titular sobre eso.
- **Qué cambiaría:** si no basta, el aviso debe matizar la promesa de borrado, que hoy es tajante, y hay que documentar la retención del proveedor.

**4. Validez de la conducta inequívoca para datos sensibles.**

- **Hoy:** la autorización es por conducta inequívoca (*Decreto 1377 de 2013, art. 7*), y los datos sensibles se advierten como facultativos.
- **Falta confirmar:** si el consentimiento **explícito** que exige el *art. 6 lit. a de la Ley 1581* para datos sensibles se satisface con la conducta inequívoca precedida de aviso, o exige un acto afirmativo separado.
- **Qué cambiaría:** se añade un turno de confirmación explícita antes de aceptar el archivo. No cambia nada más del flujo.

**5. Régimen de prueba de la autorización.**

- **Hoy:** se registra versión, fecha y hora del aviso mostrado, más el envío del documento.
- **Falta confirmar:** cuánto tiempo debe conservarse esa prueba después de que se borran los datos del titular, y si conservarla exige a su vez autorización. Hay una tensión real entre el deber de conservar prueba (*Ley 1581, art. 12 par.*) y el derecho de supresión.
- **Qué cambiaría:** si debe conservarse, se define un registro mínimo despersonalizado que sobreviva al borrado.

**6. Estatuto de Júbilo frente al régimen del consumidor financiero.** `[VERIFICAR]`

- **Hoy:** se asume que la *Ley 1328 de 2009* no aplica, porque su ámbito son las entidades vigiladas por la Superintendencia Financiera (*art. 1*), y Júbilo no lo es, no administra recursos ni intermedia. El estándar de información del art. 9 se adopta voluntariamente como listón de calidad.
- **Falta confirmar:** (i) si cobrar por el servicio, o recibir comisión por referir, cambia esa calificación (hoy no aplica: no hay comisiones, por decisión de negocio); (ii) qué le exige el *Estatuto del Consumidor, Ley 1480 de 2011*, a un proveedor de servicio digital en información veraz y publicidad engañosa. No se verificó articulado.
- **Qué cambiaría:** si aplica alguno de los dos regímenes, entran deberes de información y de atención de peticiones adicionales a los de este manual.

**7. Registro Nacional de Bases de Datos.** `[VERIFICAR]`

- **Hoy:** no se registra. Solo están obligadas las sociedades y entidades sin ánimo de lucro con activos superiores a 100.000 UVT y las personas jurídicas de naturaleza pública; las personas naturales no. *Fuente: Ley 1581 de 2012, art. 25; Decreto 090 de 2018.*
- **Falta confirmar:** la numeración exacta del artículo compilado en el *Decreto 1074 de 2015* y si el umbral cambió después de 2018.
- **Qué cambiaría:** si el umbral cambió o si Júbilo se constituye como sociedad, hay que registrar las bases y el canal de reporte de incidentes cambia (ver `procedimiento-incidentes-seguridad.md`, sección 4).

**8. Ley 2300 de 2023 y contactos al consumidor.** `[VERIFICAR]`

- **Hoy:** el agente no envía mensajes proactivos de ningún tipo, así que la pregunta no muerde.
- **Falta confirmar:** si esa ley le aplica a un bot que no es entidad financiera, si cubre canales de mensajería como Telegram, y qué exige para un contacto no comercial de servicio. No se verificó articulado.
- **Qué cambiaría:** si aplica, hay que montar registro de preferencias de contacto y respetar horarios antes de enviar el primer mensaje proactivo. **Regla entretanto: el agente no cita la Ley 2300 al usuario.**

**9. Reforma legislativa en trámite.** `[VERIFICAR]`

- **Hoy:** rige la Ley 1581 tal como está. En agosto de 2025 se radicó un proyecto de ley estatutaria (Proyecto 247 de 2025, acumulado con el 214 de 2025) con cambios en bases de legitimación y datos de menores.
- **Falta confirmar:** el estado del trámite antes de lanzar el piloto.
- **Qué cambiaría:** si se convierte en ley, hay que releer las secciones 2, 3 y 4 de este manual.

**10. Cuantía de las sanciones.** `[VERIFICAR]`

- **Hoy:** se sabe que la SIC puede imponer multas, suspender el tratamiento, cerrar temporalmente y, en casos graves con datos sensibles, cerrar de forma inmediata y definitiva. *Fuente: Ley 1581 de 2012, art. 23.*
- **Falta confirmar:** cuantías vigentes en SMLMV.
- **Qué cambiaría:** nada operativo. Cambia el dimensionamiento del riesgo para decidir cuánto invertir en controles.

**11. Textos legales que faltan y que el abogado debe producir o validar.**

1. La **política de tratamiento completa en versión de usuario**. El aviso promete "escríbeme política de datos y te la paso" y esa versión hoy no existe: existe este manual, que es otro documento y otro tono.
2. El **texto legal definitivo del aviso de privacidad**, hoy en versión 1.0 de producto.
3. Los **términos y condiciones** del servicio, que no existen.
4. La validación de que este manual **cubre el contenido mínimo** del *Decreto 1377 de 2013, art. 13*, incluida la vigencia de la base de datos, que hoy se declara como indefinida atada a finalidad.

---

## 6. Medidas de seguridad: las que existen y las que faltan

El deber es conservar la información con las condiciones de seguridad necesarias para impedir su adulteración, pérdida, consulta, uso o acceso no autorizado o fraudulento. *Fuente: Ley 1581 de 2012, art. 17 lit. d, y principio de seguridad del art. 4 lit. g.* Confianza alta.

**Lo que hoy existe de verdad.**

| Control | Cómo opera | Tipo |
|---|---|---|
| Minimización por diseño | Solo se extraen semanas, IBC y fechas; el resto del documento no se transcribe | Técnico, real |
| Supresión del original | El archivo se borra al terminar la extracción | Técnico, real |
| Anonimización de conversaciones | Se eliminan cédula, nombre, fecha de nacimiento e identificador del canal | Procedimental |
| No repetición de identificadores | Regla dura del `system-prompt.md`: el agente no repite la cédula en la conversación | Procedimental |
| Acceso único | Solo el responsable accede a los datos conservados. No hay empleados ni contratistas | Organizativo |
| Rechazo de menores | El agente no procesa y borra lo recibido | Procedimental |
| Registro de autorizaciones y solicitudes | Sección 7 de este manual | Procedimental |

**Lo que falta, dicho sin maquillaje.** Ninguno de estos existe hoy y ninguno debe describirse al usuario como si existiera:

1. **Cifrado en reposo** de los JSON conservados en el equipo del responsable.
2. **Control de acceso documentado** al equipo donde viven los datos (política de bloqueo, contraseña, cifrado de disco verificado).
3. **Custodia del token del bot de Telegram**, que hoy es el punto de compromiso más directo del canal.
4. **Registro de acceso o log de auditoría** que permita saber quién vio qué y cuándo.
5. **Respaldo y plan de recuperación**, hoy inexistentes, con la contrapartida de que un respaldo mal manejado crea copias que después hay que borrar.
6. **Verificación técnica del borrado** en la infraestructura de terceros (ver sección 5, punto 3).
7. **Segregación entre los datos del piloto y el resto del entorno personal** del responsable.

**Criterio de priorización sugerido antes del piloto:** los puntos 2 y 3 son los que convierten un descuido cotidiano en una violación de datos y son baratos. El 1 y el 4 dependen de decidir dónde viven los JSON.

---

## 7. Registros obligatorios

Estos registros son la evidencia de cumplimiento. Sin ellos, las políticas de este manual no son demostrables.

### 7.1 Registro de autorizaciones

| Identificador del titular | Versión del aviso | Fecha y hora del aviso | Fecha y hora del envío del documento | Observaciones |
|---|---|---|---|---|
| | | | | |

### 7.2 Registro de consultas y reclamos

| Fecha de recepción | Canal | Titular | Tipo (consulta o reclamo) | Petición | Fecha de respuesta | Resultado | Prórroga usada |
|---|---|---|---|---|---|---|---|
| | | | | | | | |

### 7.3 Registro de supresiones

| Fecha | Titular | Qué se suprimió | Motivo (solicitud o revisión anual) | Confirmación al titular |
|---|---|---|---|---|
| | | | | |

### 7.4 Registro de la revisión anual de conservación

| Fecha de revisión | Finalidad sigue vigente | Qué se suprimió en el periodo | Cambios de arquitectura | Responsable |
|---|---|---|---|---|
| | | | | |

*Fundamento del registro 7.4: Decreto 1377 de 2013, art. 11, que exige documentar los procedimientos de conservación y supresión. Confianza alta.*

### 7.5 Registro de incidentes

Vive en `procedimiento-incidentes-seguridad.md`, sección 6. No se duplica aquí.

---

## 8. Vigencia, versionado y control de cambios

- **Entrada en vigencia:** 2026-07-27.
- **Vigencia de la base de datos:** indefinida, atada a la finalidad declarada, con revisión anual documentada (sección 3.2). Ver sección 5, punto 11.4, sobre la validación de esta forma de declararla.
- **Versión actual:** 1.0.
- **Cuándo se actualiza obligatoriamente:** al definir el correo de contacto; al recibir la revisión del abogado; al cambiar la arquitectura del piloto; al constituirse una sociedad; al cerrarse cualquier marca `[VERIFICAR]` de la sección 5; y tras cada incidente que deje lecciones.
- **Quién lo actualiza:** el responsable.

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0 | 2026-07-27 | Versión inicial, con las siete decisiones de producto del 2026-07-27 incorporadas |
