# Aviso de privacidad del piloto - Documento 23 del kit

> **Última actualización:** 2026-09-16. **Estado:** borrador de producto, pendiente de revisión de abogado de protección de datos.
> **Qué es esto:** el texto exacto que el agente le muestra al usuario **antes** de pedirle la historia laboral. No es la política de tratamiento completa: es el aviso de privacidad, que es el formato que la ley permite cuando no se puede poner la política entera a disposición del titular. *Fuente: Decreto 1377 de 2013, arts. 14 y 15.*
> **De dónde salen las decisiones:** `datos-y-alcance.md`, secciones 7, 8, 9 y 12, cerradas por Santiago el 2026-07-27. El cambio a versión 1.1 (aviso dentro de la bienvenida, texto de 330 a 150 palabras) lo cerró Santiago el 2026-09-16.
> **Documentos hermanos:** el manual interno y el procedimiento ante incidentes están en `../cumplimiento/`. Este es el único de los tres que ve el usuario.

---

## 1. Cuándo se muestra

**Siempre antes de que el usuario mande la historia laboral, y nunca después.** Es la condición de validez de todo el esquema: la autorización es por conducta inequívoca (adjuntar el documento), y una conducta solo es inequívoca si la persona ya sabía a qué estaba diciendo que sí. *Fuente: Decreto 1377 de 2013, art. 7.*

Reglas de uso para el agente:

- El aviso va **dentro del mensaje de bienvenida**, que es el primer mensaje de la conversación. No es un turno aparte: así nadie puede mandar su historia laboral sin haberlo visto.
- Se muestra **una vez por usuario**.
- Si el usuario manda el documento **sin haber visto el aviso**, el agente **no lo procesa**: manda el mensaje de bienvenida (que contiene el aviso) y le pide que lo reenvíe.
- Si el usuario **pregunta por sus datos** en cualquier otro momento, el agente responde con lo de `datos-y-alcance.md` secciones 7 a 9, no repitiendo el aviso completo.
- Se registra qué versión del aviso se mostró y cuándo. Esa es la prueba de la autorización. *Fuente: Ley 1581 de 2012, art. 12 par.; Decreto 1377 de 2013, art. 8.*

---

## 2. El texto

La versión vigente es la **1.1**. La 1.0 queda archivada abajo, no se borra: el manual interno exige (su sección 3.1) poder reconstruir qué versión vio cada usuario.

### 2.1 Versión 1.1 (vigente desde el 2026-09-16)

Es el mensaje de bienvenida completo, con el aviso incorporado. Este es el texto literal que ve el usuario, en bloque de código para que se copie sin alteraciones:

```
Hola 👋 Soy Júbilo. Te digo cuándo y con qué monto te vas a pensionar, y cómo mejorar tu resultado.

Envíame tu historia laboral en el chat. Si no la tienes te digo cómo descargarla.

Antes de que la mandes, lo mínimo sobre tus datos. Detrás de esto hay una persona, no una empresa: Jose Santiago Sierra Garcia (bot.jubilo@gmail.com). Con tu historia laboral hago dos cosas: calculo tu diagnóstico y guardo la conversación sin tu nombre ni tu cédula para mejorar el producto. No la vendo ni se la mando a nadie. El archivo original lo borro apenas saco los números, y el procesamiento ocurre en servidores fuera de Colombia. Si tu historia trae incapacidades, invalidez o sindicatos, esos son datos sensibles y no estás obligado a dármelos: táchalos y te hago el diagnóstico igual.

Escríbeme "mis datos" para ver, corregir o borrar lo tuyo, o quitarme el permiso de usarlo. Si quieres el detalle completo, escríbeme "política de datos". Al mandarme tu historia laboral aceptas esto.
```

### 2.2 Versión 1.0 (histórica, dejó de usarse el 2026-09-16)

Estuvo vigente del 2026-07-27 al 2026-09-16. Se mostraba como un turno aparte, inmediatamente antes de pedir el documento. Se conserva para poder reconstruir qué vio cada usuario que interactuó en ese periodo. **No se muestra a nadie más.**

> **Antes de que me mandes tu historia laboral, lee esto. Son 30 segundos.**
>
> **Quién soy.** Detrás de Júbilo hay una persona, no una empresa: Jose Santiago Sierra Garcia. Me escribes a `bot.jubilo@gmail.com` para lo que sea de tus datos.
>
> **Qué hago con tu historia laboral.** Dos cosas, y ninguna más:
> 1. Saco tus semanas, tus salarios y tus fechas para calcular tu diagnóstico pensional.
> 2. Guardo la conversación **sin tu nombre ni tu cédula** para ir mejorando el producto.
>
> **Qué no hago.** No la vendo, no la publico y no se la mando a tu fondo ni a nadie más. Tampoco me pagan por recomendarte un fondo, una aseguradora ni un abogado.
>
> **Qué guardo y qué borro.** Del archivo que me mandas saco los números y **borro el archivo original apenas termino**. Me quedo con los números mientras te sirvan a ti y me sirvan para mejorar. No hay plazo fijo: si me pides que borre, borro ese mismo día.
>
> **Ojo con un detalle.** Tu historia laboral puede traer datos de salud (incapacidades, invalidez) o de sindicatos. Esos son datos sensibles y **no estás obligado a dármelos**: si prefieres, táchalos antes de mandarme el documento y hago tu diagnóstico igual con lo que quede.
>
> **Tus derechos.** En cualquier momento me puedes pedir ver tus datos, corregirlos, borrarlos o quitarme el permiso de usarlos. Escríbeme "mis datos" por aquí y te muestro las opciones. Es gratis y no te voy a preguntar por qué. Tengo 10 días hábiles para responderte una consulta y 15 para un reclamo, aunque el borrado lo hago el mismo día. Si crees que no cumplí, puedes quejarte ante la Superintendencia de Industria y Comercio.
>
> **Dónde está la política completa.** Escríbeme "política de datos" y te la paso.
>
> **Al mandarme tu historia laboral aceptas que la procese como te acabo de explicar, incluyendo que el procesamiento ocurre en servidores fuera de Colombia.** Si no estás de acuerdo, no me mandes el documento: igual te puedo explicar cómo funciona el sistema pensional.

---

## 3. Cómo cubre cada requisito legal

Tabla de trazabilidad de la **versión 1.1**, para que el abogado la revise punto por punto. Como el texto 1.1 no tiene párrafos con título, cada fila apunta a la frase concreta.

| Requisito | Fuente | Dónde queda cubierto |
|---|---|---|
| Nombre o razón social y datos de contacto del responsable | Decreto 1377, art. 15 num. 1 | "Detrás de esto hay una persona, no una empresa: Jose Santiago Sierra Garcia (bot.jubilo@gmail.com)" |
| Tratamiento al cual serán sometidos los datos y su finalidad | Decreto 1377, art. 15 num. 2 | "hago dos cosas: calculo tu diagnóstico y guardo la conversación sin tu nombre ni tu cédula para mejorar el producto", con las dos finalidades separadas |
| Derechos que le asisten al titular | Decreto 1377, art. 15 num. 3 | "Escríbeme 'mis datos' para ver, corregir o borrar lo tuyo, o quitarme el permiso de usarlo": acceso, corrección, supresión y revocatoria. **Resuelto el 2026-09-16** devolviendo la revocatoria al aviso corto |
| Mecanismos para conocer la política de tratamiento y sus cambios | Decreto 1377, art. 15 num. 4 | "o 'política de datos' para el detalle completo" |
| Señalar expresamente que responder sobre datos sensibles es facultativo | Decreto 1377, art. 15 par. y art. 6 | "esos son datos sensibles y no estás obligado a dármelos" |
| No condicionar el servicio a la entrega de datos sensibles | Decreto 1377, art. 6 num. 3 | "táchalos y te hago el diagnóstico igual" |
| Carácter previo de la autorización | Ley 1581, art. 9; Decreto 1377, art. 5 | Sección 1 de este documento: el aviso va dentro del mensaje de bienvenida, que es anterior a cualquier envío del documento |
| Conducta inequívoca como forma válida de autorización | Decreto 1377, art. 7 | "Al mandarme tu historia laboral aceptas esto", que nombra el acto concreto que constituye la autorización |
| Autorización para transferencia internacional | Ley 1581, art. 26 lit. f | "el procesamiento ocurre en servidores fuera de Colombia" |
| Términos de respuesta a consultas y reclamos | Ley 1581, arts. 14 y 15 | Ya **no** está en el aviso corto: se cubre en la política de tratamiento en versión de usuario, accesible con el comando "política de datos" |
| Derecho a quejarse ante la SIC | Ley 1581, art. 8 lit. d | Ya **no** está en el aviso corto: se cubre en la política de tratamiento en versión de usuario, accesible con el comando "política de datos" |
| Política de conservación atada a la finalidad | Decreto 1377, art. 11 | El 1.1 dice "El archivo original lo borro apenas saco los números". La conservación de los números atada a la finalidad y el borrado el mismo día **se cubren en la política de tratamiento en versión de usuario**, accesible con "política de datos". **Decisión de Santiago, 2026-09-16:** no vuelven al aviso corto, porque el art. 15 no los lista entre los cuatro contenidos mínimos y porque anunciar el borrado el mismo día antes de automatizarlo sube una promesa que hoy se cumple a mano |

**Sobre lo que se movió del 1.0 al 1.1.** El *art. 15 del Decreto 1377 de 2013* lista cuatro contenidos mínimos del aviso (identidad y contacto del responsable, tratamiento y finalidad, derechos del titular, y mecanismos para conocer la política), y ninguno de los cuatro es de los que se movieron a la política de usuario: los plazos de 10 y 15 días hábiles, la mención de la Superintendencia de Industria y Comercio, el "es gratis y no te voy a preguntar por qué" y el "tampoco me pagan por recomendarte un fondo, una aseguradora ni un abogado". Dicho eso, **no se verificó** si enunciar los plazos de respuesta y la autoridad de vigilancia dentro del aviso corto es exigible por otra vía. Ese punto va a la lista de revisión del abogado.

**Lo que este aviso deliberadamente no dice, y por qué:** no menciona el requisito de procedibilidad ante la SIC (*Ley 1581, art. 16*, hay que reclamar primero al responsable). Es cierto, pero suena a obstáculo puesto por el responsable y el usuario lo descubre igual si llega ahí. Va en la política completa, no en el aviso.

---

## 4. Lo que falta antes de publicarlo

1. ~~**El correo de contacto.** El marcador `[correo de contacto]` tiene que quedar reemplazado por una dirección real que Santiago atienda. Sin eso el aviso incumple el *Decreto 1377, art. 15 num. 1*.~~ **Resuelto el 2026-09-16:** el correo es `bot.jubilo@gmail.com`, ya está en el texto vigente. Se deja el punto por historial de la decisión.
2. **La política de tratamiento completa en versión de usuario.** El aviso promete "escríbeme política de datos y te la paso" y hoy esa versión no existe: existe el manual interno, que es otro documento y otro tono. Hay que derivar de él una versión pública corta. Con el 1.1 esto además es bloqueante, porque cuatro contenidos que estaban en el 1.0 ahora solo viven ahí.
3. **Revisión del abogado de protección de datos.** Ver la lista de la sección 5 de `../cumplimiento/manual-interno-tratamiento-datos.md`.
4. **Versionado.** Cada cambio material al aviso genera versión nueva y hay que poder reconstruir cuál vio cada usuario. Hoy la versión vigente es la 1.1 y la 1.0 queda archivada en la sección 2.2.
5. **Confirmación del recorte del 1.0 al 1.1.** Que el abogado confirme que mover a la política de usuario los plazos de respuesta, la mención de la SIC, la gratuidad del trámite y la ausencia de comisiones no rebaja el contenido mínimo exigible del aviso.
6. ~~**Dos filas parciales de la tabla.**~~ **Resuelto el 2026-09-16.** La revocatoria de la autorización (*art. 15 num. 3*) volvió al texto del aviso corto. La conservación de los números atada a la finalidad (*art. 11*) se queda en la política de usuario y no vuelve al aviso. Lo que sigue abierto para el abogado es solo lo del punto 5: que el recorte del 1.0 al 1.1 no rebaje el contenido mínimo.
