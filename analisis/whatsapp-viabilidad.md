# WhatsApp Cloud API para Júbilo: viabilidad para persona natural en Colombia

Fecha de investigación: 18-sep-2026.

## 1. Persona natural y verificación de negocio

- Meta exige: cuenta de Meta Business Manager, Business Verification completada, número dedicado (no puede tener WhatsApp normal activo al mismo tiempo), nombre de negocio conforme a sus políticas, y autenticación de dos factores obligatoria desde 2024 (Meta for Developers, WATI, consulta 18-sep-2026).
- La Business Verification pide documentos que muestren el nombre del negocio (no de una persona) junto a un número de identificación tributaria. Para Colombia, proveedores mencionan RUT y certificado de Cámara de Comercio como los documentos típicos (liveconnect.chat, macsoft.com.co, consulta 18-sep-2026). No encontré confirmación oficial de Meta de que un RUT de persona natural sin registro mercantil sea suficiente: es el punto más incierto de todo este análisis.
- Existe la figura de "sole proprietor" pero es específica de Twilio para el registro A2P 10DLC de SMS en EEUU/Canadá (usa número de seguridad social, no Tax ID); no aplica a WhatsApp ni a Colombia. No hay un equivalente documentado de "persona natural" para la Business Verification de Meta fuera de EEUU/Canadá.
- Límites de mensajería sin verificar: 250 conversaciones iniciadas por el negocio cada 24h; tras verificar sube a 1.000 y luego escala según calidad y volumen (Meta for Developers, consulta 18-sep-2026).
- No encontré una figura intermedia oficial para emprendedor individual sin sociedad constituida.

## 2. Precios vigentes

- Desde el 1 de julio de 2025 Meta cobra por mensaje entregado, no por conversación de 24h como antes (Twilio changelog, YCloud, Meta for Developers, consulta 18-sep-2026).
- Categorías: marketing, utilidad, autenticación y servicio (no plantilla). Los mensajes de servicio dentro de la ventana de 24h son gratis hoy, pero eso cambia el 1 de octubre de 2026.
- Cifras para Colombia (fuentes secundarias, sin confirmar contra la tabla oficial de Meta): utilidad y autenticación cerca de 0.0008 USD por mensaje (de las más bajas del mundo); marketing entre 0.0125 y 0.02 USD por mensaje según la fuente. Hay discrepancia entre blogs sobre el valor exacto de marketing: tratar como estimación, no como dato duro.
- No hay cupo gratis mensual fijo. Lo gratis depende del contexto: mensajes de servicio dentro de la ventana de 24h (gratis hasta 30-sep-2026), plantillas de utilidad dentro de esa ventana (gratis hasta 30-sep-2026), y ventanas de "Free Entry Point" de 72h cuando el usuario llega desde un anuncio de clic a WhatsApp.
- **Cambio relevante:** a partir del 1 de octubre de 2026 Meta empieza a cobrar también los mensajes de servicio y utilidad enviados dentro de la ventana de 24h, a las mismas tarifas de sus categorías, sin descuento por volumen (confirmado en página oficial de Meta for Developers, consulta 18-sep-2026). Esto sube el costo de un bot conversacional tipo Júbilo, que hoy vive casi enteramente dentro de esa ventana gratis.

## 3. Ventana de 24 horas y plantillas

- Cuando el usuario escribe primero, se abre una ventana de servicio de 24h: dentro de ella se puede mandar cualquier mensaje de formato libre (texto, PDF, audio, etc.) sin plantilla.
- Fuera de esa ventana, solo se puede iniciar contacto con una plantilla pre-aprobada por Meta.
- Aprobación de plantillas: no encontré un plazo oficial exacto de Meta en esta búsqueda; fuentes de BSPs hablan de minutos a 24-48h en la práctica, pero no es un dato oficial confirmado.
- Una plantilla de categoría "utilidad" sí sirve para mandar al día siguiente un aviso tipo "tu reporte está listo" (es el caso de uso típico de utility), pero después de octubre de 2026 esa plantilla ya no será gratis aunque el usuario responda dentro de la ventana: se cobrará igual que cualquier utility fuera de ventana.

## 4. Webhooks

- El endpoint debe ser HTTPS público con certificado TLS/SSL válido; no se aceptan certificados autofirmados.
- Cada payload viene firmado con HMAC-SHA256 en el header `X-Hub-Signature-256`, calculado con el App Secret de la app de Meta; se debe validar antes de confiar en el contenido.
- Handshake de verificación: Meta manda un GET con `hub.verify_token` y `hub.challenge`; el servidor debe validar el token y devolver el challenge tal cual.
- Dato adicional (fuente secundaria, no oficial, tratar con cautela): el 31 de marzo de 2026 Meta cambiaría la autoridad certificadora de mTLS de DigiCert a su propia Meta CA, relevante solo si en algún momento se usa mTLS.
- No encontré alternativa oficial al endpoint público (no hay opción de polling o conexión persistente sin servidor expuesto).

## 5. Proveedores vs directo con Meta

- **Directo con Meta:** sin costo de plataforma adicional, pero se asume toda la verificación de negocio, gestión de plantillas, infraestructura del webhook y soporte técnico.
- **360dialog:** cuota mensual fija por número (cifra citada: ~49 EUR/mes) más las tarifas de Meta sin markup por mensaje (pass-through). Conviene a partir de cierto volumen (una fuente sugiere el punto de equilibrio cerca de 10.000 mensajes/mes). Cifras de fuentes secundarias, no verificadas contra el pricing page oficial de 360dialog.
- **Twilio:** agrega un fee por mensaje encima de la tarifa de Meta (cifra citada: ~0.005 USD/mensaje), documentado aparte de la tabla de Meta.
- **Infobip:** modelo con cuota por perfil/servicio (cifra citada: 263 USD en cierto plan), posicionado en la gama media.
- Ningún BSP revisado pasa la tarifa de Meta sin algún tipo de margen (monto fijo, porcentaje o fee por mensaje). Todos facilitan la gestión de plantillas y calidad, pero ninguno resuelve el requisito de fondo: la verificación de negocio de Meta subyacente sigue siendo la misma, el BSP no la reemplaza, solo facilita el trámite.
- No encontré evidencia de que algún BSP acepte formalmente "persona natural sin registro mercantil" como cliente en Colombia; habría que confirmarlo directamente con 360dialog o Twilio si el plan avanza.

## 6. Audio (notas de voz)

- Llegan como archivo .ogg codificado en OPUS (Meta for Developers, consulta 18-sep-2026).
- Se descargan vía la Media API de Meta: primero se pide la URL temporal del archivo con el media ID que llega en el webhook, luego se descarga ese archivo con el token de acceso.
- Existe una función nativa de Meta de "transcripción automática" configurable del lado del usuario de WhatsApp, pero no encontré su costo ni si aplica a mensajes recibidos por un negocio vía Cloud API: la documentación revisada la describe desde la perspectiva del usuario final, no confirmé si un bot puede activarla.
- Costo de transcripción: no encontré cifra oficial de Meta. Alternativa habitual: transcribir el .ogg con un servicio externo de speech-to-text (ej. Whisper de OpenAI u otro), cuyo costo depende del proveedor elegido, no de Meta. No tengo cifra confiable para incluir aquí sin inventar un número.

## 7. Número dedicado

- El número registrado en Cloud API queda dedicado al bot: deja de poder usarse como WhatsApp normal o WhatsApp Business App al mismo tiempo.
- Para migrar un número que YA tiene WhatsApp (personal o WhatsApp Business App): hay que eliminar la cuenta de ese número en la app antes de registrarlo en Cloud API, lo que borra el historial de chats de ese número en la app. Alternativa: onboardear a través de un Solution Provider que soporte "coexistence" (mantener el número activo en la app y en la API a la vez), si el proveedor lo ofrece.
- Tras desconectar el número de la app, tarda hasta 3 minutos en quedar disponible para registrarlo en la API.

## Veredicto

- El obstáculo real no es técnico ni de precio: es la Business Verification de Meta, que en la práctica parece pensada para una entidad legal con documentos a su nombre. No encontré confirmación oficial de que un RUT de persona natural sin registro mercantil baste; hay que probarlo directamente en el flujo de Meta o preguntarle a un BSP antes de comprometerse.
- Si la verificación exige una sociedad constituida, la ruta más barata sería usar los datos de Synappse (si aplica) o esperar a constituir una entidad, en vez de forzar el registro como persona natural.
- El costo por mensaje en Colombia es bajo hoy (utilidad/autenticación cerca de 0.0008 USD, marketing entre 0.0125 y 0.02 USD), pero el cambio del 1 de octubre de 2026 que cobra también los mensajes de servicio y utilidad dentro de la ventana de 24h sube el costo real de un bot conversacional tipo Júbilo, que hoy vive gratis en Telegram.
- Los BSPs (360dialog, Twilio, Infobip) facilitan el trámite y la gestión de plantillas, pero ninguno resuelve el requisito de fondo de verificación de negocio de Meta, y no confirmé que acepten persona natural sin empresa en Colombia.
- El envío de PDFs de reportes fuera de la ventana de 24h sí es viable con una plantilla de utilidad aprobada, pero deja de ser gratis a partir de octubre 2026.
- El requisito de HTTPS con certificado válido y verificación de firma es estándar y no representa una barrera real para un desarrollador con experiencia básica en despliegue (Júbilo ya corre en un VPS, por lo que la infraestructura ya existe).
- Migrar un número existente de WhatsApp personal implica borrar su historial de chats salvo que el BSP ofrezca coexistencia; usar un número nuevo dedicado evita ese costo.
- La transcripción de audio no viene resuelta gratis por Meta: si Júbilo quiere seguir recibiendo notas de voz, hay que sumar un proveedor externo de speech-to-text, con un costo adicional que no pude cuantificar en esta búsqueda.
- Camino más barato para una prueba: registrar un número nuevo (no el personal), probar el flujo de Business Verification con los datos disponibles (persona natural o Synappse) antes de invertir en desarrollo, y usar un BSP con plan de bajo costo fijo (360dialog u otro) en vez de ir directo con Meta, para tener soporte si la verificación se traba.

## Fuentes

- [Meta for Developers: Pricing on the WhatsApp Business Platform](https://developers.facebook.com/documentation/business-messaging/whatsapp/pricing)
- [Meta for Developers: pricing updates for service/utility en ventana de 24h](https://developers.facebook.com/documentation/business-messaging/whatsapp/pricing/non-template-messages)
- [Meta for Developers: Messaging Limits](https://developers.facebook.com/documentation/business-messaging/whatsapp/messaging-limits)
- [Meta for Developers: Audio messages](https://developers.facebook.com/documentation/business-messaging/whatsapp/messages/audio-messages)
- [Meta for Developers: Migrate an existing WhatsApp number](https://developers.facebook.com/documentation/business-messaging/whatsapp/solution-providers/migrate-existing-whatsapp-number-to-a-business-account/)
- [Meta: Set up webhooks (Cloud API)](https://developers.facebook.com/docs/whatsapp/cloud-api/guides/set-up-webhooks/)
- [Twilio changelog: Meta updating WhatsApp pricing July 1 2025](https://www.twilio.com/en-us/changelog/meta-is-updating-whatsapp-pricing-on-july-1--2025)
- [YCloud: WhatsApp API pricing update July 1 2025](https://www.ycloud.com/blog/whatsapp-api-pricing-update)
- [Twilio docs: Direct Sole Proprietor Registration (A2P 10DLC, EEUU/Canadá, no aplica a WhatsApp/Colombia)](https://www.twilio.com/docs/messaging/compliance/a2p-10dlc/direct-sole-proprietor-registration-overview)
- [360dialog: WhatsApp API pricing markup vs flat](https://360dialog.com/blog/whatsapp-business-api-pricing-why-markup-on-messages-often-costs-you-more/)
- [macsoft.com.co: WhatsApp Business API Colombia costos y CoExistence](https://www.macsoft.com.co/whatsapp-business-api-colombia/)
- [liveconnect.chat: API WhatsApp Business en Colombia](https://liveconnect.chat/co/whatsapp-business-api-colombia)
- [ominiflow.com: Colombia WhatsApp API pricing](https://ominiflow.com/whatsapp-api-pricing/colombia)
- [formbeep.com: Meta WhatsApp Business API pricing rates by country](https://formbeep.com/whatsapp-api-pricing/)

## Nivel de confianza

Bien establecido: cambio a cobro por mensaje desde jul-2025, cargo de servicio/utilidad en ventana desde oct-2026, formato de audio ogg/opus, requisitos de webhook (HTTPS, firma HMAC), borrado de historial al migrar número existente.

Estimación sin confirmar contra tabla oficial: cifras exactas de Colombia en USD por categoría (varían entre fuentes secundarias, especialmente marketing).

No pude verificar: si una persona natural sin registro mercantil pasa la Business Verification en Colombia; plazo oficial de aprobación de plantillas; costo de transcripción de audio; si algún BSP acepta explícitamente persona natural en Colombia.
