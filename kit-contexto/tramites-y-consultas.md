# Trámites y consultas por administradora - Documento 11 del kit

> **Última actualización:** 2026-07-21. **Por qué existe:** el kit tenía las reglas del sistema pero no el "cómo se hace". Cuando el usuario pregunta "¿y cómo sé en qué perfil estoy?" o "¿dónde descargo mi historia laboral?", el agente necesita el paso a paso real, no una recomendación vaga de "consulta con tu fondo".
> **Regla de mantenimiento:** las apps y portales cambian. Cada dato aquí lleva la fecha en que se verificó. Si el paso a paso ya no coincide, el agente lo dice y orienta por canal de atención en lugar de insistir con una ruta muerta.
> **Regla de honestidad:** lo que no esté documentado aquí, el agente NO lo inventa. Dice que no tiene el paso a paso exacto y orienta al canal de atención de la administradora.
> **Fuentes oficiales:** las guías o documentos oficiales de cada administradora que respaldan estas rutas se guardan en `fuentes-tramites/`.
> **Ingesta (decidido 2026-07-21):** el usuario descarga su historia laboral siguiendo estas rutas y luego la trae al chat como **PDF o imagen (screenshot)**; el agente acepta ambos por igual. Se evaluó y **descartó** que Júbilo hiciera el trámite por el usuario (automatización): Colpensiones bloquea el acceso automatizado por firewall y Porvenir usa reCAPTCHA Enterprise. Por eso, en todos los fondos, el agente **guía con el paso a paso**; no hace la solicitud por el usuario.

## Estado de documentación

| Administradora | Perfil de multifondos | Descargar historia laboral | Saldo | Cambio de perfil |
|---|---|---|---|---|
| Protección | Por documentar | **Documentado 2026-07-20 (web)** | Por documentar | Por documentar |
| Porvenir | Por documentar | **Documentado 2026-07-21 (web)** | Por documentar | Por documentar |
| Colfondos | Por documentar | **Parcial 2026-07-21 (login/registro; falta dentro del portal)** | Por documentar | Por documentar |
| Skandia | Por documentar | **Documentado 2026-07-21 (web, guía oficial)** | Por documentar | Por documentar |
| Colpensiones | No aplica (RPM no tiene multifondos) | **Documentado 2026-07-21 (web)** | No aplica | No aplica |

## Lo que ya sabemos (verificado)

**Multifondos (aplica solo a fondos privados / RAIS):** existen tres perfiles, conservador, moderado y mayor riesgo (Ley 1328 de 2009). Por ley el afiliado converge obligatoriamente hacia el conservador al acercarse a la edad de pensión, así que un joven que aparezca en conservador probablemente lo está por asignación por defecto y vale la pena que lo revise.

**El perfil NO aparece en la historia laboral.** Verificado contra los 6 documentos del set dorado: ninguno de los cinco formatos (Porvenir, Protección, Skandia, Colpensiones, Colfondos) trae el perfil de fondo. Es siempre una consulta aparte en el portal de la administradora. El agente debe darlo por sentado y no prometer deducirlo del documento.

**Superficie a documentar: solo el navegador (web), no la app nativa** (decisión de Santiago 2026-07-20). Júbilo vive en Telegram y la mayoría lo usará desde el celular, así que se documenta la **página web del fondo**, no su app.
- **Una sola ruta sirve para celular y computador.** La ruta se redacta por **nombres de sección/botón** (ej. "ve a *Certificados* → *Historia laboral*"), no por posición en pantalla, porque esos nombres son iguales en el navegador móvil y en el de escritorio; lo único que cambia es cómo se abre el menú (en móvil suele estar en el ícono ☰). Solo se agrega la aclaración del ☰ si en ese fondo el acceso al menú móvil es confuso.
- **El agente no pregunta "app o web" ni "celular o computador".** No hace falta: la ruta redactada así funciona en ambos.
- **Nota técnica:** el Bot API de Telegram no le informa al bot desde qué cliente escribe el usuario (móvil/escritorio/web); Júbilo no puede detectarlo. Por eso el default es móvil y la ruta se escribe para servir a ambos sin preguntar.

**Manejo del PDF con clave (regla transversal, Santiago 2026-07-21).** Algunos fondos entregan la historia laboral como PDF protegido con contraseña; cuando la hay, esa clave es **el número de documento del afiliado sin puntos ni comas** (confirmado en Protección). **No hace falta documentar fondo por fondo si el archivo trae clave o no:** si el PDF que manda el usuario está cifrado, Júbilo aplica siempre lo mismo (opción a, decidida) — pide el número de cédula y descifra antes de extraer. Que un fondo entregue el PDF con o sin clave **no cambia el flujo de Júbilo**.

---

## Protección

*Descarga de historia laboral documentada con pantallazos reales del flujo web (2026-07-20). Perfil, saldo y cambio de perfil aún por documentar.*

### Cómo ver en qué perfil estás
- **En el extracto de la cuenta (confirmado):** la sección **"Fondo donde están mis aportes"** muestra el perfil actual (ej. "MAYOR RIESGO") y más abajo el desglose porcentual (ej. "100,00% Mayor riesgo"). Los nombres en pantalla son exactamente "Conservador", "Moderado" y "Mayor riesgo".
- El extracto también trae "a lo largo de mi vida laboral pensional por tipo de fondo": el histórico de en qué fondos ha estado.
- Ruta dentro de la app / web (paso a paso): *pendiente*.

### Cómo cambiar de perfil
- Ruta exacta:
- Requisitos, confirmaciones o tiempos de espera:
- ¿Es inmediato o queda en trámite?

### Cómo descargar la historia laboral

**Ruta verificada (web "Certifácil", 2026-07-20; redacción de Júbilo validada por Santiago 2026-07-21). Ventaja clave: NO pide usuario ni contraseña** ("sin filas y sin clave").

1. Entra a `https://www.proteccion.com/portalafiliados/afiliados/certifacil#/certificados`
2. Toca **"Generar certificados o Historia laboral"**.
3. Escribe tu **tipo y número de documento**, marca **"No soy un robot"** (reCAPTCHA) y dale **"Continuar"**.
4. Elige **"Pensión obligatoria"**.
5. Selecciona **"Constancia de Historia Laboral"** y genera la solicitud.
6. Elige el medio de entrega: **WhatsApp o correo**.
7. Sale el aviso "Solicitud de certificados generada... recibirás una notificación cuando esté listo". **No es descarga inmediata:** el PDF llega por el medio elegido unos minutos después.

- **Nombre exacto del certificado:** "Constancia de Historia Laboral", dentro de la categoría "Pensión obligatoria".
- **Formato:** PDF (~295 KB en el caso real).
- **Clave del PDF (crítico):** el archivo viene **protegido con contraseña**, y la contraseña es **el número de documento sin puntos ni comas** (ej.: cédula 1.234.567.890 -> clave `1234567890`). El mensaje de entrega lo dice: "La clave para abrir tu certificado es tu número de documentos sin puntos ni comas."
- **Si no llega:** el portal sugiere "actualizar tus datos"; alternativa, el chat de la web.

**Implicación para Júbilo (importante):** cuando el usuario mande este PDF, viene **cifrado**. Para leerlo/extraerlo hay que abrirlo con la clave (su número de cédula sin puntos). Por eso, al dar esta ruta, Júbilo debe **avisar de la clave por adelantado** y, cuando reciba el archivo, estar listo para usar ese número. **Decisión tomada (Santiago 2026-07-21): opción (a)** — Júbilo le pide al usuario su número de cédula y descifra el PDF con esa clave antes de extraer (es el dato de menos fricción: el usuario lo da de todos modos).

### Dónde ver el saldo
- Ruta exacta:

### Canales de atención (respaldo cuando la ruta no funciona)
- **Chat web:** widget "Chat" abajo a la derecha en el portal de Certifácil.
- Línea telefónica y oficinas: *por documentar.*

---

## Porvenir

*Descarga de historia laboral documentada con pantallazos reales del flujo web (2026-07-21). Perfil, saldo y cambio de perfil por documentar.*

### Cómo descargar la historia laboral

**Ruta verificada (web, 2026-07-21). No pide usuario ni contraseña; solo documento.**

1. Entra a `https://www.porvenir.com.co/web/certificados-y-extractos/certificado-de-historia-laboral`
2. Selecciona **"Tipo de documento"** y escribe el **"Número de documento"**.
3. Dale **"Enviar a mi correo electrónico"**.
4. Sale la confirmación: el certificado se envía al **correo registrado** en Porvenir (aparece enmascarado). Si es correcto, **"Aceptar"**; si no, **"Actualizar"**.

- **Nombre en el portal:** "Descarga tu Historia Laboral (semanas cotizadas)".
- **Entrega:** solo al **correo registrado en Porvenir**. A diferencia de Protección, aquí **NO** se puede elegir WhatsApp ni escribir otro correo, y NO es descarga directa.
- **Fricción a anticipar:** si el correo registrado está desactualizado o el usuario no lo controla, tiene que actualizarlo primero (botón "Actualizar"), lo que puede requerir trámite adicional. Júbilo debe advertirlo por adelantado.
- **¿Trae clave el PDF?** Sin confirmar, pero da igual: si llega cifrado, aplica la **regla transversal** de arriba (clave = número de documento) y Júbilo lo descifra igual. No cambia el flujo.
- **Alcance del documento (importante para completitud):** trae solo periodos en **fondos privados**. Si la persona estuvo en Colpensiones (fondos públicos) o tiene bono pensional en trámite, esas semanas pueden no aparecer aquí; el propio portal invita a consultarlas en la cuenta personal.

### Cómo ver en qué perfil estás
- *Por documentar.*

### Cómo cambiar de perfil
- *Por documentar.*

### Dónde ver el saldo
- *Por documentar.*

### Canales de atención (respaldo cuando la ruta no funciona)
- Botón **"Ayudas"** en la misma página de descarga.
- Línea, chat, oficinas: *por documentar.*

## Colfondos

*Acceso y registro documentados con pantallazos reales (2026-07-21). A diferencia de Protección y Porvenir, Colfondos NO tiene flujo público sin clave: exige iniciar sesión en el Portal Transaccional. Falta el paso a paso DENTRO del portal (Santiago lo captura más adelante).*

### Cómo descargar la historia laboral

**Requiere sí o sí cuenta en el Portal Transaccional (correo registrado + contraseña).** Dos escenarios:

**A. Ya tienes usuario:**
1. Entra a `https://www.colfondos.com.co/dxp/acceso-de-usuarios`
2. Escribe tu **correo** y **contraseña**, marca **"No soy un robot"** y dale **"Acceder"**. (Si olvidaste la clave: **"He olvidado mi contraseña"**.)
3. Dentro del Portal Transaccional, entra a **"Consulta tu historia laboral"**. *(Paso a paso exacto dentro del portal: por documentar.)*

**B. No tienes usuario (crearlo primero):**
1. En la pantalla de acceso, toca **"Créalo ahora"** (o entra a `https://www.colfondos.com.co/dxp/web/guest/registro` y dale **"Empezar"**).
2. En **"Registro de usuarios afiliados"**, elige **tipo** y **número de documento**, marca reCAPTCHA y dale **"Enviar"**.
3. Sigue los pasos: **Datos → Validación → Cuenta → Completa tu cuenta**.
4. **Ojo:** el usuario será el **correo que ya tengas registrado en Colfondos**. Si no está registrado o quieres cambiarlo, hay que llamar al **Contact Center** (fricción real).

- **Nivel de fricción: alto.** Es el único fondo hasta ahora que obliga a login. Júbilo debe advertirlo por adelantado; si el usuario no tiene cuenta, lo orienta con paciencia (y si tiene otro fondo con flujo más simple, puede arrancar por ese, salvo que Colfondos sea su único fondo).
- **Dentro del portal** también se puede: descargar el certificado de afiliación, consultar saldos de productos y hacer el retiro de cesantías (contexto para otros trámites).
- **¿Trae clave el PDF?** Sin confirmar; si llega cifrado, aplica la **regla transversal** (clave = número de documento).

### Cómo ver en qué perfil estás
- *Por documentar (dentro del Portal Transaccional).*

### Cómo cambiar de perfil
- *Por documentar.*

### Dónde ver el saldo
- Dentro del Portal Transaccional: **"Consulta los saldos de tus productos"**. Ruta exacta *por documentar.*

### Canales de atención (respaldo cuando la ruta no funciona)
- **Contact Center** (para temas de correo registrado / usuario). Número *por documentar.*
- Menú superior del sitio: **"Centro de Ayuda"** y **"Canales de servicio"**.

## Skandia

*Documentado a partir de la guía oficial de Skandia "¿Cómo consultar tu historia laboral?" (guardada en `fuentes-tramites/skandia-guia-historia-laboral.pdf`, 2026-07-21). Como Colfondos, exige iniciar sesión.*

### Cómo consultar / descargar la historia laboral

**Requiere cuenta (usuario + contraseña) en el Portal de Clientes.**

1. Entra a `www.skandia.com.co` y dale **"Ingresar"** (Portal de Clientes); escribe usuario y contraseña. (Si no la recuerdas: **"Olvidé mi clave"**; si no tienes usuario: **"Obtén tu clave"**.)
2. Selecciona la categoría **"Pensión Obligatoria y Cesantías"**.
3. Selecciona tu contrato de **"Pensión Obligatoria"**.
4. Haz clic en **"Historia Laboral"** (botón "Historial Laboral").
5. Se abre la visualización de tu historia laboral, con: saldo, % que llevas para pensión anticipada, edad, semanas cotizadas, fecha de inicio, y el desglose de semanas (Skandia, otros fondos, Colpensiones) y bono pensional.

- **Descarga en PDF:** la guía documenta la **consulta en pantalla**, no el botón de descarga del certificado. El certificado descargable está en la sección **"Certificados"** del portal. *Ruta exacta del PDF descargable: por confirmar.*
- **Acceso:** requiere login (misma categoría de fricción que Colfondos).
- **Extra útil:** desde esa misma pantalla el usuario puede **editar/agregar periodos** y **solicitar la validación/corrección** de su historia; ese proceso Skandia lo resuelve en **5 a 60 días**, según qué tan fácil sea contactar a los empleadores. Es un trámite aparte de la consulta; relevante si el usuario detecta lagunas o errores.
- **¿Trae clave el PDF?** Sin confirmar; si llega cifrado, aplica la **regla transversal**.

### Cómo ver en qué perfil estás
- *Por documentar.*

### Cómo cambiar de perfil
- La pantalla de Pensiones Obligatorias muestra el botón **"CAMBIAR TIPO DE FONDO"**. Ruta y confirmaciones exactas *por documentar.*

### Dónde ver el saldo
- Visible tras login en **"Pensión Obligatoria y Cesantías"** (saldo total por contrato) y en la propia pantalla de Historia Laboral.

### Canales de atención (respaldo cuando la ruta no funciona)
- Correo de clientes: **cliente@skandia.com.co**.
- Reporte de irregularidades/seguridad: **ciberseguridad@skandia.com.co**.

## Colpensiones

*Descarga de historia laboral documentada con pantallazos reales del flujo web (2026-07-21). No aplica multifondos ni saldo individual (es RPM, régimen público).*

### Cómo descargar la historia laboral

**Ruta verificada (web, 2026-07-21). No pide usuario ni contraseña; solo documento.** Se envía al correo registrado en Colpensiones.

1. Entra a `https://sede.colpensiones.gov.co/tramite/updInfo/55/` (trámite **"Envía tu Historia Laboral a tu correo electrónico"**).
2. Marca el **tipo de documento** (Cédula de ciudadanía / Cédula de extranjería) y escribe el **número de documento**. Dale **"Continuar"**.
3. Aparece el correo registrado (enmascarado). Si es el tuyo, **"Continuar"** para el envío; si no, **"Actualizar tus datos"**.

- **Entrega:** al **correo registrado en Colpensiones** (igual que Porvenir; no se puede elegir otro medio ni escribir otro correo en el momento). No es descarga directa.
- **Fricción a anticipar:** si el correo registrado está desactualizado, hay que actualizar datos primero. Júbilo lo advierte.
- **¿Trae clave el PDF?** Sin confirmar; si llega cifrado, aplica la **regla transversal**.
- **Nota de régimen:** en Colpensiones lo que importa es la historia laboral (semanas); no hay saldo individual ni perfil de multifondos, así que esas secciones no aplican.

### Canales de atención (respaldo cuando la ruta no funciona)
- Sección **"HABLEMOS / Nuestros canales de contacto"** en la misma página del trámite. Línea, chat, puntos de atención: *por documentar.*

---

## Cómo usa esto el agente

1. Cuando el usuario pregunte "cómo sé X", da el paso a paso de **su** administradora (la que emitió el documento que subió), no una respuesta genérica.
2. Si esa administradora aún no está documentada aquí: dilo con honestidad y orienta al canal de atención. Nunca inventes rutas de navegación.
3. Después de dar la ruta, cierra invitando a volver con el dato: "cuando sepas en cuál estás, me dices y afinamos el número". El dato que traiga el usuario mejora la simulación.
