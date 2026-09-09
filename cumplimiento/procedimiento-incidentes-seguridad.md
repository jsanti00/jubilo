# Procedimiento ante incidentes de seguridad de datos personales

> **Documento interno. No se muestra al usuario.**
> **Versión:** 1.0. **Fecha de entrada en vigencia:** 2026-07-27. **Estado:** borrador operativo, pendiente de revisión de abogado de protección de datos.
> **Por qué existe:** el responsable debe informar a la Superintendencia de Industria y Comercio cuando se presenten violaciones a los códigos de seguridad y existan riesgos en la administración de la información de los titulares. *Fuente: Ley 1581 de 2012, art. 17 lit. n.* Confianza alta.
> **Documento hermano:** `manual-interno-tratamiento-datos.md`, que define responsable, datos tratados, arquitectura y controles. Este procedimiento no los repite.
> **Regla de coherencia:** este procedimiento no puede prometerle al titular menos de lo que dice `../kit-contexto/aviso-de-privacidad.md`.

---

## 1. Qué cuenta como incidente

**Definición operativa.** Cualquier evento, confirmado o razonablemente sospechado, que comprometa la confidencialidad, la integridad o la disponibilidad de datos personales tratados por Júbilo, o que genere riesgo en su administración.

**La sospecha razonable ya activa el procedimiento.** No se espera a la confirmación para contener: se espera a la confirmación para reportar.

**Catálogo de incidentes plausibles en la arquitectura real del piloto.** El piloto corre en un canal de Telegram con Claude Code como motor, sin servidor propio, con procesamiento fuera de Colombia y con los JSON conservados en el equipo del responsable.

| Escenario | Qué se compromete | Severidad base |
|---|---|---|
| Compromiso del token del bot de Telegram | Un tercero puede leer y escribir como Júbilo, incluidos documentos en tránsito | **Crítica** |
| Compromiso de la cuenta de Telegram del responsable | Acceso al histórico de conversaciones | **Crítica** |
| Acceso no autorizado al equipo donde viven los JSON (robo, pérdida, malware, equipo desbloqueado) | Datos del caso de varios titulares | **Crítica** |
| Incidente reportado por el proveedor del modelo o del canal | Datos en procesamiento, alcance no controlado por el responsable | **Alta** |
| Falla del borrado del archivo original tras la extracción | Persistencia de un documento que se prometió borrar, con posibles datos sensibles adheridos | **Alta** |
| Envío del diagnóstico o de datos a la persona equivocada | Un titular expuesto | **Alta** |
| Fuga de datos sensibles de salud o sindicato dentro de una conversación conservada sin anonimizar bien | Datos sensibles, agravante legal | **Alta** |
| Pérdida de los JSON sin copia (disponibilidad) | Continuidad del servicio, no confidencialidad | **Media** |
| Procesamiento de datos de un menor de 18 años detectado tarde | Tratamiento proscrito | **Media** |
| Publicación accidental de un dato personal en un archivo del repositorio o en un material compartido | Uno o pocos titulares | **Media** |

**Lo que no es incidente:** que el usuario mande un documento sin haber visto el aviso (eso se resuelve con la regla del manual, sección 3.1), o que el agente se equivoque en un cálculo.

**Agravantes que suben cualquier severidad un nivel:** que haya datos sensibles de salud o sindicales involucrados (*Ley 1581 de 2012, arts. 5 y 6*), que afecte a más de un titular, o que el evento sea deliberado y no accidental.

---

## 2. Roles

No hay equipo. Todos los roles recaen hoy en **Jose Santiago Sierra Garcia**, responsable del tratamiento. Se enumeran igual porque son funciones distintas, deben ejecutarse en orden, y el día que haya una segunda persona el reparto ya está escrito.

| Rol | Función | Hoy lo ejerce |
|---|---|---|
| **Detector** | Quien nota el evento. Puede ser el responsable, un usuario o un proveedor | Cualquiera |
| **Coordinador del incidente** | Decide severidad, ordena la contención, lleva la bitácora y decide si se reporta | Santiago |
| **Contención técnica** | Ejecuta las medidas de la sección 3.2: revocar tokens, cerrar sesiones, aislar el equipo | Santiago |
| **Comunicación con titulares** | Redacta y envía el aviso a los afectados | Santiago |
| **Reporte a la autoridad** | Prepara y radica el reporte ante la SIC | Santiago |
| **Cierre y lecciones** | Actualiza controles y el manual interno | Santiago |

**Regla de escalamiento hacia afuera:** si el incidente involucra posible responsabilidad legal, datos sensibles de varios titulares, o duda sobre si hay que reportar, se contacta al abogado de protección de datos **antes** de radicar cualquier cosa ante la SIC.

---

## 3. Fases y plazos

Los plazos de las fases 1 a 3 son **autoimpuestos**, no legales: la ley no fija término para el deber del *art. 17 lit. n*. Se fijan cortos porque la contención tardía es lo que convierte un susto en una violación de datos.

### 3.1 Fase 0. Detección y registro inicial. Plazo: inmediato

1. Se abre una entrada en el registro de incidentes (sección 6) con fecha, hora y descripción de los hechos conocidos.
2. Se anota lo que se sabe y **lo que no se sabe**. La bitácora se escribe en el momento, no después.
3. **No se borra ni se altera evidencia.** Un borrado apresurado destruye la prueba de qué pasó.

### 3.2 Fase 1. Contención. Plazo: dentro de las 24 horas siguientes a la detección

Se ejecuta lo que aplique al escenario:

- **Revocar y regenerar el token del bot de Telegram.** Es la primera medida ante cualquier sospecha sobre el canal.
- **Cerrar sesiones activas y cambiar credenciales** de la cuenta de Telegram y del proveedor del modelo.
- **Aislar el equipo comprometido** de la red y verificar el cifrado de disco.
- **Suspender el servicio** si no se puede garantizar que los datos entrantes estén protegidos. Es preferible un piloto caído a un piloto filtrando.
- **Retirar el dato expuesto** de donde haya quedado publicado.
- **Solicitar al proveedor** la información del incidente, su alcance y qué datos de Júbilo estuvieron involucrados.

### 3.3 Fase 2. Evaluación. Plazo: dentro de los 3 días hábiles siguientes a la detección

Se responde por escrito en la bitácora:

1. **Qué datos se comprometieron**, por categoría (identificadores, datos del caso, datos sensibles) y si el archivo original estaba aún sin borrar.
2. **Cuántos titulares** están afectados y si son identificables.
3. **Causa raíz**, no solo el síntoma.
4. **Ventana temporal** de la exposición.
5. **Si persiste el riesgo** o ya fue contenido.
6. **Severidad final**, aplicando los agravantes de la sección 1.
7. **Decisión de reporte** a la SIC, con su justificación, y **decisión de aviso** a los titulares.

La decisión de no reportar se escribe y se motiva. Es una decisión, no una omisión.

### 3.4 Fase 3. Notificación a los titulares afectados. Plazo: dentro de los 5 días hábiles siguientes a la detección

**Criterio para avisar:** se avisa siempre que el incidente pueda afectar los derechos del titular, y en todo caso cuando haya datos sensibles involucrados o cuando el dato haya salido del control del responsable. Ante duda, se avisa.

**Contenido mínimo del aviso al titular, en el lenguaje directo del producto:**

1. Qué pasó y cuándo, sin eufemismos.
2. Qué datos suyos estuvieron involucrados.
3. Qué se hizo para contenerlo.
4. Qué puede hacer él, incluido pedir la supresión de sus datos, que se ejecuta el mismo día.
5. Que puede quejarse ante la SIC.
6. El correo de contacto del responsable.

**Canal:** el mismo chat, y correo si el titular lo dejó. **No se minimiza el hecho ni se le echa la culpa al proveedor.**

### 3.5 Fase 4. Reporte a la autoridad

Ver sección 4, que es donde queda la marca abierta.

### 3.6 Fase 5. Cierre y lecciones. Plazo: dentro de los 15 días hábiles siguientes al cierre

1. Se completa la entrada del registro de incidentes con causa raíz y medidas adoptadas.
2. Se actualiza la sección 6 de `manual-interno-tratamiento-datos.md` si el incidente reveló un control faltante.
3. Se revisa si el aviso de privacidad prometió algo que la arquitectura no puede sostener y, si es así, se corrige el aviso.

---

## 4. Reporte a la Superintendencia de Industria y Comercio

**El deber, que no está en duda.** El responsable debe informar a la autoridad de protección de datos cuando se presenten violaciones a los códigos de seguridad y existan riesgos en la administración de la información de los titulares. *Fuente: Ley 1581 de 2012, art. 17 lit. n.* Confianza alta. **Este deber no depende de estar inscrito en el Registro Nacional de Bases de Datos.**

`[VERIFICAR]` **Cuál es el canal y el plazo exactos para reportar un incidente cuando el responsable es una persona natural no obligada a inscribirse en el RNBD.**

- **Respuesta operativa, lo que se hace hoy:** el reporte se radica ante la SIC por sus canales oficiales de radicación de peticiones, dirigido a la Delegatura para la Protección de Datos Personales, dentro de un plazo autoimpuesto de **15 días hábiles** contados desde la detección del incidente, y antes si la severidad es crítica. El plazo se fija por analogía con el término que la SIC exige a los responsables inscritos en el RNBD para reportar incidentes; **esa analogía no se verificó en fuente primaria y no se cita como norma**.
- **Qué falta confirmar:** (i) si el formulario de reporte de incidentes del RNBD es el único canal habilitado y si un no obligado puede usarlo; (ii) el plazo exacto que la SIC exige y en qué acto administrativo consta; (iii) si existe un umbral de severidad por debajo del cual no hay que reportar.
- **Qué cambiaría:** si el canal formal resulta ser exclusivo del RNBD, hay que radicar por petición ordinaria y dejar constancia del intento por el canal formal. Si el plazo confirmado es más corto que 15 días hábiles, este procedimiento se corrige y las fases 2 y 3 se comprimen. **Si Júbilo se constituye como sociedad y supera el umbral del RNBD, este punto se reescribe entero.**
- **Regla entretanto:** ante un incidente crítico no se espera a cerrar esta marca. Se reporta, aunque sea por el canal ordinario, y se consulta al abogado en paralelo.

**Contenido del reporte a la SIC.** Se prepara con la bitácora ya completa:

1. Identificación del responsable y sus datos de contacto.
2. Fecha y hora de ocurrencia y de detección del incidente.
3. Descripción de los hechos y causa raíz.
4. Categorías y volumen de datos personales comprometidos, señalando expresamente si hubo **datos sensibles**.
5. Número de titulares afectados.
6. Medidas de contención adoptadas y fecha de cada una.
7. Si se notificó a los titulares, cuándo y por qué canal.
8. Medidas correctivas para evitar la repetición.

**Qué no se hace:** no se envían al reporte los datos personales de los afectados más allá de lo necesario para describir el incidente.

**Sanciones que están en juego, para dimensionar.** La SIC puede imponer multas, suspender las actividades relacionadas con el tratamiento, cerrar temporalmente la operación y, en casos graves, cerrar de forma inmediata y definitiva la operación que involucre tratamiento de datos sensibles. *Fuente: Ley 1581 de 2012, art. 23.* Confianza alta en el catálogo de sanciones; `[VERIFICAR]` las cuantías vigentes en SMLMV, pendiente que no cambia nada operativo de este procedimiento.

---

## 5. Incidentes en infraestructura de terceros

Es el escenario más probable y el que menos controla el responsable.

- **Reconocimiento honesto:** el piloto no tiene servidor propio. Si el proveedor del canal o del modelo sufre un incidente, el responsable puede enterarse tarde, por un aviso público, o no enterarse.
- **Lo que sí se hace:** al conocer un incidente de un proveedor, se abre entrada en el registro, se evalúa si hubo datos de Júbilo involucrados y se aplican las fases 2 a 4 con la información disponible.
- **Lo que no se hace:** trasladarle al titular la responsabilidad. Frente al titular, el responsable del tratamiento es Santiago, no el proveedor. *Fuente: Ley 1581 de 2012, art. 17.* Confianza alta.
- **Vínculo con el manual:** la ausencia de contrato de transmisión de datos con esos proveedores es el punto 2 de la sección 5 de `manual-interno-tratamiento-datos.md`, y es también lo que hoy impide exigirles notificación oportuna de incidentes.

---

## 6. Registro de incidentes

Se lleva aquí. Una fila por incidente, y la bitácora detallada como anexo en este mismo folder cuando el caso lo amerite.

| ID | Fecha y hora de ocurrencia | Fecha y hora de detección | Descripción | Datos comprometidos | ¿Sensibles? | Titulares afectados | Severidad | Contención (qué y cuándo) | ¿Se avisó a titulares? | ¿Se reportó a la SIC? | Causa raíz | Medidas correctivas | Fecha de cierre |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| | | | | | | | | | | | | | |

**Conservación del registro:** indefinida mientras exista el piloto. Es evidencia de diligencia y sobrevive al borrado de los datos de los titulares, porque se lleva sin identificadores personales: los afectados se anotan por conteo y por referencia al registro de autorizaciones del manual, no por nombre.

---

## 7. Prueba del procedimiento

Un procedimiento que nunca se ensayó no funciona el día del incidente.

- **Simulacro anual**, junto con la revisión anual de conservación del manual (sección 3.2). Escenario mínimo a ensayar: compromiso del token del bot.
- **Qué se verifica en el simulacro:** que el responsable sabe dónde revocar el token, cuánto tarda en hacerlo, dónde están los JSON que habría que evaluar, y que las plantillas de aviso al titular y de reporte a la SIC existen.
- **Se deja registro** del simulacro en la tabla de la sección 6, marcado como simulacro.
- **Primer simulacro programado: 2027-07-27**, o antes del lanzamiento del piloto si este ocurre primero.

---

## 8. Control de cambios

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0 | 2026-07-27 | Versión inicial. Plazos de fases autoimpuestos. Canal y plazo de reporte a la SIC quedan con marca `[VERIFICAR]` abierta |
