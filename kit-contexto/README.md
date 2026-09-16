# Kit de contexto de Júbilo: arquitectura y estado

> **Última actualización:** 2026-07-21. Validado con Santiago.

## Principio rector: cero internet en producción

El agente en producción **no tiene acceso a internet**. Todo lo que sabe viene de esta carpeta y de la calculadora. Objetivo: llevar al mínimo la posibilidad de alucinación.

- **Los números** los produce la calculadora en código fijo. La IA nunca calcula.
- **Las reglas y respuestas** salen solo del corpus local. Si algo no está en el corpus, el agente dice que no lo sabe.
- **Los datos variables** (SMLMV, IPC, rendimientos) viven como archivos de datos de la calculadora, no como "conocimiento" del modelo.
- **El internet se usa solo en laboratorio**: para construir y actualizar este corpus, con verificación contra fuentes oficiales y revisión del abogado pensional. Lo verificado queda congelado como contexto.
- **Ingesta multi-formato (2026-07-21):** el agente acepta la historia laboral como PDF **o como imagen/screenshot**, con la misma verificación cruzada. Se evaluó y **descartó** que el agente automatizara el trámite de descarga: los portales bloquean el acceso automatizado (Colpensiones por firewall, Porvenir por reCAPTCHA Enterprise). El *cerebro* del agente sigue sin internet. Detalle en `system-prompt.md` > "Formatos de ingesta: PDF o imagen".

## Arquitectura del corpus: 3 capas

| Capa | Qué es | Quién la usa | Estado |
|---|---|---|---|
| **1. Operativa** | Los 21 destilados de este kit. Cada regla cita su fuente legal. Resuelve ~95% de las conversaciones | El agente, siempre | En construcción (ver tabla abajo) |
| **2. Referencia** | Textos completos oficiales (leyes, decretos, sentencias) descargados en laboratorio. Consulta por búsqueda local cuando la pregunta excede el destilado o hay que citar textualmente | El agente, por excepción | Pendiente (checklist abajo) |
| **3. Casos** | Set dorado (`V0/casos/`) + casos hipotéticos por escenario. Crece con cada conversación del piloto | Extracción (few-shot) y pruebas de la calculadora | 6 casos: los 4 formatos RAIS + Colpensiones cubiertos (caso-06 con discrepancia interna documentada) |

**Regla de precedencia:** si el destilado (capa 1) y el texto crudo (capa 2) parecen contradecirse, el agente responde con el destilado y marca la duda para revisión. La capa 2 alimenta la capa 1 en laboratorio, nunca la salta.

## Estado de los documentos (capa 1)

> **Ampliación del 2026-07-21:** el kit pasó de 11 a 21 documentos. Los 10 nuevos (filas 12 a 21) cubren el **contexto adyacente**: lo que la gente pregunta alrededor del cálculo, no sobre el cálculo. Se construyeron a partir de `../plan-corpus-adyacente.md`, tras detectar en role-play que el agente calculaba bien pero no sabía responder si un pensionado a los 35 seguía cotizando. **Estado de todos: borrador verificado contra fuente oficial, pendiente de revisión del abogado pensional** (78 marcas `[VERIFICAR]` **al 2026-07-26**: las 77 migradas más la del cuarto estado, que no va al abogado sino a Colpensiones). **Ese número quedó viejo, ver el recuento de abajo.**

> **Recuento de marcas del 2026-07-28 (contado en disco, no heredado): 99 marcas vivas.** El 78 era el corte del 26 y no alcanzó a incluir los documentos y ampliaciones del 26 y el 27. Desglose de los archivos con más carga: `reclamacion-y-defensa.md` 11, `bonos-tiempos-publicos-y-exterior.md` 9, `mora-y-correccion-historia-laboral.md` 8, `sin-pension-alternativas.md` 8, `modalidades-de-pension.md` 6, `reglas-rpm.md` 6, `rentista-de-capital.md` 5. No cuenta `README.md` ni `system-prompt.md`, que mencionan las marcas pero no las contienen.
>
> **Movimiento de la ronda del 2026-07-28:** una **cerrada** en fuente primaria (el techo de 45 SMLMV, `independientes.md` s.4), una **trasladada y no borrada** (el fundamento de la obligación del rentista anterior a 2023, que pasó de `independientes.md` s.3 a `rentista-de-capital.md` s.11, con nota en el origen para que no se cuente dos veces) y **cinco nuevas** en el documento nuevo. Neto: más 4.
>
> **Dos marcas siguen en formato viejo** (texto dentro del corchete, sin respuesta operativa) y no entran en las 99: la fecha de sanción de la Ley 2103 de 2021 en `bonos-tiempos-publicos-y-exterior.md` s.10, y las sentencias clave de traslados en el checklist de la capa 2 de este mismo archivo. Son las únicas dos que quedan del formato anterior a la migración.

| # | Documento | Estado | Nota |
|---|---|---|---|
| 1 | `system-prompt.md` | **Borrador** | Estructura y reglas duras listas; voz y flujo exacto por iterar con Santiago |
| 2 | `reglas-rpm.md` | **Listo** | Probado con casos 04 y 05 |
| 3 | `reglas-rais.md` | **Listo** | Probado con casos 01, 02 y 03 |
| 4 | `reglas-traslados.md` | **Listo** | Probado con el comparador (5 casos) |
| 5 | `regimenes-especiales.md` | **Listo** | Detección probada en el router |
| 6 | `independientes.md` | **Reescrito 2026-07-26** | Norma vigente confirmada (Ley 2277 de 2022 art. 89 + Decreto 379 de 2026). **El 40% es base mínima, no cifra fija.** Nuevas secciones: rentistas de capital y sanciones de la UGPP |
| 7 | `supuestos-actuariales.md` | **Listo** | Series 1992-2026 cargadas en la calculadora |
| 8 | `faq-y-glosario.md` | **Listo (semilla)** | Crece con las preguntas del piloto |
| 9 | `historias-laborales-ejemplo/` | **Cubierto** | El set dorado en `V0/casos/` cumple ese rol |
| 10 | `reforma-ley-2381.md` | **Listo** | Ambos escenarios; se reescribe el día del fallo |
| 11 | `tramites-y-consultas.md` | **Esqueleto** | Documento nuevo (2026-07-20): el paso a paso real por administradora (perfil de multifondos, descargar historia laboral, saldo). Se llena consultando cada portal |
| 12 | `vida-del-pensionado.md` | **Borrador verificado** | Bloque A. Cierra el hueco que originó la ampliación: quien toma la pensión anticipada del art. 64 **no vuelve a cotizar a pensión** (art. 17, mod. Ley 797 art. 4), pero **sí paga salud dos veces** si sigue trabajando (sobre la mesada y sobre el salario) y entra a ARL |
| 13 | `tributario-pensional.md` | **Borrador verificado** | Bloque B. Renta exenta de 1.000 UVT, retención, aportes voluntarios y AFC, límite del 40% / 1.340 UVT de la Ley 2277 de 2022 |
| 14 | `beneficiarios-y-sobrevivientes.md` | **Borrador verificado** | Bloque C. Incluye la tabla de qué pasa con el saldo al morir según modalidad, que es lo que faltaba para poder asesorar la elección de modalidad |
| 15 | `modalidades-de-pension.md` | **Borrador verificado** | Bloque D. Riesgo de longevidad vs. de mercado, reversibilidad asimétrica, agotamiento del saldo, quiebra de la aseguradora |
| 16 | `invalidez-e-incapacidades.md` | **Borrador verificado** | Bloque E. Convierte la invalidez de "fuera de alcance" a cobertura informativa (sigue sin calcularse mesada ni PCL) |
| 17 | `sin-pension-alternativas.md` | **Borrador verificado** | Bloque F. Compara todas las salidas; trae el PSAP reabierto por el Decreto 543 de 2026 |
| 18 | `bonos-tiempos-publicos-y-exterior.md` | **Borrador verificado** | Bloque G. La causa número uno de historias laborales que "no cuadran"; convenios internacionales con su estado real de vigencia |
| 19 | `mora-y-correccion-historia-laboral.md` | **Ampliado 2026-07-26** | Bloque H. Hace accionables las moras que el router ya detecta. **Cuarto estado nuevo** (s.1 bis: salario reportado con cero semanas, con guion de conversación) y **s.1 ter** sobre huecos y lagunas, que fija cómo se responde "¿dónde están mis huecos?" con `calculadora/lagunas.py` |
| 20 | `reclamacion-y-defensa.md` | **Borrador verificado** | Bloque I. Escrito bajo el **CPTSS nuevo (Ley 2452 de 2025, vigente desde el 2 de abril de 2026)**, que suprimió la única instancia |
| 21 | `datos-y-alcance.md` | **Borrador + decisiones** | Bloque J. Habeas data y alcance de Júbilo. Trae 12 puntos `[DECISIÓN DE SANTIAGO]`, incluida la política de retención de datos |
| 22 | `aportes-voluntarios-y-sobrecotizacion.md` | **Borrador verificado** | Nuevo (2026-07-26). Cómo meterle más plata a la pensión: aportes voluntarios en RAIS, por qué no existen en RPM, sobrecotizar y su zona gris, excedentes de libre disponibilidad |
| 23 | `costo-de-cotizar.md` | **Borrador verificado** | Nuevo (2026-07-27). Cierra el hueco de la demo del 26: el kit cubría la salud del **pensionado** pero no la del **cotizante activo**, así que el agente no podía responder cuánto cuesta subir la base. Salud del independiente (12,5%), Fondo de Solidaridad con su escalonado, qué no aplica (ARL y caja voluntarias, parafiscales no), base única salud-pensión. Las cifras las produce `calculadora/costo_y_retorno.py` |
| 24 | `aviso-de-privacidad.md` | **Borrador, falta abogado** | Nuevo (2026-07-27). Aviso del piloto en lenguaje de usuario, con el contenido mínimo del *Decreto 1377 art. 15* y la línea de autorización por conducta inequívoca que cubre datos sensibles de salud y el procesamiento fuera de Colombia |
| 25 | `rentista-de-capital.md` | **Borrador verificado** | Nuevo (2026-07-28). El segmento de mayor disposición a pagar, que vivía en una sección de `independientes.md`. Qué cuenta como renta de capital, cómo se determina el IBC, presunción de costos, dividendos, patrimonio frente a ingreso, y la frontera con el independiente por cuenta propia. **Hallazgo de fondo:** el rentista no es categoría aparte, es un independiente con contrato distinto a prestación de servicios (*Decreto 780 de 2016 art. 3.2.7.2 lit. b*), y el **Decreto 379 del 7 de abril de 2026** derogó el anexo de coeficientes que sustentaba la regla de dividendos que el kit venía dando |

> **Ampliación del 2026-07-26:** el kit pasó a 22 documentos. El nuevo y la reescritura de `independientes.md` salieron de una sesión de role-play con un independiente de 59 años con patrimonio, donde el agente falló dos veces seguidas sobre la misma regla. Detalle en `../ESTADO.md`.
>
> **Ampliación del 2026-07-28:** el kit llega a **25 documentos** con `rentista-de-capital.md`, que saca al segmento de la sección 3 de `independientes.md` y la deja como remisión. Salió de la matriz de cobertura: 16 celdas, 46,9% de cobertura, y es el segmento de mayor disposición a pagar. **Corrigió una regla que el agente venía dando mal:** que los dividendos no admiten presunción de costos, que describía un anexo derogado el 7 de abril de 2026.
>

> **Doctrina de las marcas `[VERIFICAR]` (Santiago, 2026-07-26):** una marca **no es un hueco**. Cada una debe traer **respuesta operativa** (lo que el agente responde hoy), **qué falta confirmar** y **qué cambiaría** si el abogado dice otra cosa. El agente siempre tiene respuesta; lo que espera confirmación es el respaldo, no el contenido.
>
> **Migración terminada el 2026-07-26.** Los grupos A (marcas que tocan una cifra de la calculadora o una regla dura) y B (marcas que cambian un consejo al usuario) **están migrados al formato nuevo: cero marcas en formato viejo**. El grupo C se inventarió y **no se migró** por decisión de alcance: son los 6 puntos de `datos-y-alcance.md`, que no son reglas pensionales sino cumplimiento legal del producto, y se deciden con Santiago y el abogado corporativo, no en una conversación con un usuario. Ver la sección "Lo que se lleva el abogado" más abajo.

## Lo que se lleva el abogado, en una sola sesión

Ordenado para que la reunión rinda: **primero lo que mueve una cifra de la calculadora, después lo que cambia un consejo, y al final lo del producto.** Cada punto dice dónde vive la marca completa con su respuesta operativa.

> **Cómo se cierra un punto sin rehacer la sección:** cada fila es independiente. Cuando algo se resuelve, se **tacha el enunciado** y se escribe en la misma fila "CERRADO el AAAA-MM-DD" con la fuente y qué quedó implementado. No se borra la fila: sirve para que nadie la reabra. Ver los puntos 3, 7 y 28 como modelo. Lo mismo aplica a la lista de "lo que NO necesita abogado" de más abajo, donde hay dos puntos que alguien puede estar cerrando en paralelo.

### Bloque 1: para el ACTUARIO, no para el abogado (mueve cifras de todo el producto)

Estos cinco van juntos y en una sola sesión, porque alimentan el mismo factor de conversión de capital a mesada.

| # | Pregunta | Dónde |
|---|---|---|
| 1 | **El factor capital a mesada.** El 4% de interés técnico es la tasa de **reserva** del sistema, no el **precio de mercado** de una renta vitalicia. Son tres tasas distintas y la calculadora usa la que no es. Preguntas exactas ya redactadas en `../ESTADO.md` | `supuestos-actuariales.md` marca 2; `modalidades-de-pension.md` s.11 |
| 2 | **Ubicación del interés técnico** en la Circular Básica Jurídica, **reexpedida en 2025** (Circular 6 del 25 de junio) | `modalidades-de-pension.md` s.11 |
| 3 | ~~**Valores exactos de expectativa de vida** de la RV08 a los 57 y 62~~ **CERRADO el 2026-07-27 sin actuario.** Se abrió la tabla oficial de la Resolución 1555 de 2010: mujer 57, **29,7 años**; hombre 62, **21,3 años**. Confirmaron los redondeados. Ya cargados en `datos_sistema.py` | `supuestos-actuariales.md` marca 3; `reglas-rais.md` s.5 |
| 4 | **¿La Superfinanciera va a actualizar la RV08?** Cambia por resolución, no por ley, así que no aparece en el radar del Congreso ni de la Corte | `modalidades-de-pension.md` s.11 |
| 5 | **Efecto de los beneficiarios de sobrevivencia** en la mesada, hoy no modelado (la calculadora sobreestima) | `reglas-rais.md` s.5 |

### Bloque 2: para el ABOGADO PENSIONAL, marcas que tocan una cifra (grupo A)

| # | Pregunta | Dónde |
|---|---|---|
| 6 | **Las "50 semanas adicionales" de una mujer bajo la C-197: ¿desde el requisito reducido del año o desde 1.300?** Es la zona más gris del kit y vale varios puntos de tasa de reemplazo. Sin concepto de Colpensiones ni jurisprudencia | `reglas-rpm.md` s.5 |
| 7 | ~~**El piso del 55% de la tasa de reemplazo.**~~ **CERRADO el 2026-07-27.** Texto literal verificado contra **Secretaría del Senado** ("un porcentaje que oscilará entre el 65 y el 55% del ingreso base de liquidación"). **El piso ya está implementado en `calcular_mesada`**, con 8 comprobaciones de regresión que terminan en código de salida 1 | `reglas-rpm.md` s.5 |
| 8 | **Bono pensional en pensión anticipada:** qué pasa cuando alguien se pensiona antes de la fecha de redención (62 hombre, 60 mujer). Hoy el bono no se suma, o sea que el kit subestima a propósito | `bonos-tiempos-publicos-y-exterior.md` s.5; `reglas-rais.md` s.7 |
| 9 | **Calendarios de la C-197 (RPM) y la C-054 (RAIS):** confirmar que aplican hoy con la reforma en trámite de subsanación, y el resolutivo literal de la C-197 | `reglas-rpm.md` s.3; `sin-pension-alternativas.md` s.4 |
| 10 | **Escalonado del Fondo de Solidaridad:** cómo se aplica dentro de cada tramo (proporcional o por salto). La tabla ya está resuelta y cargada | `reglas-rpm.md` s.2 |
| 11 | **Decreto reglamentario del reparto 11,5 / 1,5 / 3** del 16% en RAIS. La ley delega la redistribución al Gobierno y no se ubicó el decreto vigente | `supuestos-actuariales.md` marca 1 |

### Bloque 3: para el ABOGADO PENSIONAL, marcas que cambian un consejo (grupo B)

| # | Pregunta | Dónde |
|---|---|---|
| 12 | **¿La justa causa de despido por cumplir requisitos de pensión alcanza a la pensión anticipada del art. 64?** Alguien puede perder el empleo el mismo mes en que se pensiona | `vida-del-pensionado.md` s.3 |
| 13 | **¿Se pueden recuperar las semanas ya indemnizadas** reintegrando lo recibido? Hoy el agente dice que no cuente con ellas | `sin-pension-alternativas.md` s.3 |
| 14 | **Ventana de traslado de la Ley 2381:** ¿la suspensión revivió el plazo vencido el 16 de julio de 2026? Pregunta frecuente esperable | `reforma-ley-2381.md` s.2 |
| 15 | **Aportes de un pensionado del RAIS a su cuenta obligatoria:** qué hacen las AFP en la práctica | `vida-del-pensionado.md` s.3 |
| 16 | **Art. 128 de la Constitución:** listado literal del art. 19 de la Ley 4 de 1992 y confirmación de que el pensionado del RAIS queda fuera de la prohibición | `vida-del-pensionado.md` s.8 |
| 17 | **Umbral de 150 semanas del bono:** ¿aplica solo al literal a) del art. 115 o también a las demás causales? | `bonos-tiempos-publicos-y-exterior.md` s.2 |
| 18 | **CMISS: ¿el afiliado elige vía o la entidad aplica de oficio la más favorable?** Colpensiones y el art. 8 del convenio parecen decir cosas distintas. Y resolver la discrepancia Honduras / El Salvador en la lista de países | `bonos-tiempos-publicos-y-exterior.md` s.9 |
| 19 | **Honorarios de las Juntas de Calificación:** en qué casos los asume la administradora y no el afiliado. Es una barrera de casi dos millones para apelar | `invalidez-e-incapacidades.md` s.7 |
| 20 | **Condición más beneficiosa:** ¿se eliminó el test de vulnerabilidad para sobrevivientes? ¿Coincide la Sala Laboral con la Corte Constitucional? | `invalidez-e-incapacidades.md` s.5 |
| 21 | **Norma que fija el deber de corrección de historia laboral** de las administradoras. No se encontró ninguna | `mora-y-correccion-historia-laboral.md` s.4 |
| 22 | **Vigilancia de la Superfinanciera sobre Colpensiones:** norma que delimita el alcance, para saber a qué puerta mandar al usuario | `mora-y-correccion-historia-laboral.md` s.5; `reclamacion-y-defensa.md` s.9 |
| 23 | **Prórroga del derecho de petición: ¿tiene tope legal** el nuevo plazo que la entidad se autofija? | `reclamacion-y-defensa.md` s.3 |
| 24 | **¿Queda algún supuesto de intervención directa** en materia pensional bajo la Ley 2452 de 2025? | `reclamacion-y-defensa.md` s.6 |
| 25 | **Intereses de mora del art. 141:** en qué casos los ha negado la jurisprudencia | `reclamacion-y-defensa.md` s.8 |
| 26 | **Circular Externa 018 de 2023** de la Superfinanciera: ¿modifica la 016 de 2016 sobre doble asesoría? | `reglas-traslados.md` s.2 |
| 27 | **Tributario, va a un tributarista y no al pensional:** concepto DIAN expreso sobre pensión exenta como ingreso bruto del art. 592, y texto íntegro del Oficio 905834 de 2022 y el Concepto 6564 de 2023 | `tributario-pensional.md` s.4 y s.8 |
| 28 | ~~**Techo ampliado a 45 SMLMV** y la supuesta condición de crecimiento económico del 4%~~ **CERRADO el 2026-07-28 en fuente primaria.** Los 45 SMLMV sí están en la norma (*Ley 100 art. 18 inciso 4, mod. Ley 797 art. 5*), pero sujetos a reglamentación del gobierno que no se ubicó vigente, así que **el techo aplicable sigue siendo 25 SMLMV**. La condición del 4% en tres vigencias **no aparece en ninguna norma** y el agente no la menciona | `independientes.md` s.4 |
| 29 | **Rentista y ganancia ocasional: ¿vender un inmueble o un paquete de acciones genera base de cotización?** El agente hoy dice que no, apoyado en que la renta de capital es rendimiento y no enajenación, pero **no se ubicó norma ni doctrina de la UGPP que lo diga expresamente**. Es la de mayor monto del segmento: un usuario que vendió un inmueble en el año | `rentista-de-capital.md` s.2 |
| 30 | **Las edades de 50 (mujer) y 55 (hombre) que eximen de cotizar a pensión a quien nunca se afilió.** La UGPP las publica en su ABC de rentistas **sin citar artículo**. Hay que ubicar la norma, porque el error es en la dirección cara: decirle a alguien que no está obligado cuando sí lo estaba lo expone a sanción | `rentista-de-capital.md` s.3 |
| 31 | **Fundamento de la obligación del rentista ANTERIOR a la Ley 2277 de 2022.** Hoy la obligación es clara; lo disputado son los periodos previos a 2023, que es donde están los procesos de fiscalización de monto alto. Dos referencias convergentes sin texto verificado: **Consejo de Estado exp. 28624** (sentencia de febrero de 2025, que habría negado la nulidad apoyándose en los arts. 156 y 157 de la Ley 100) y **Sentencia C-578 de 2009** (que habría incluido al rentista entre los independientes). **Venía de `independientes.md` s.3; se trasladó, no se duplicó** | `rentista-de-capital.md` s.11 |

### Bloque 4: grupo C, inventariado y NO migrado (no es para el abogado pensional)

Los 6 puntos de `datos-y-alcance.md`. Son cumplimiento legal **del producto**, no reglas pensionales, y van al abogado corporativo o de protección de datos junto con los 11 `[DECISIÓN DE SANTIAGO]` que ya tiene ese documento.

| Punto | Tema | Línea |
|---|---|---|
| C1 | Reforma en trámite de la Ley 1581 (Proyecto 247 de 2025) | s.1 |
| C2 | Registro Nacional de Bases de Datos: si Júbilo queda obligado a registrarse | s.7 |
| C3 | Régimen sancionatorio de la SIC aplicable | s.7 |
| C4 | Dos puntos que podrían cambiar el régimen aplicable al producto | s.8 |
| C5 | Si la Ley 2300 de 2023 le aplica a un bot que no es entidad financiera | s.12 |
| C6 | Alojamiento de datos fuera de Colombia y transferencia internacional | s.12 |

### Lo que NO necesita abogado ni actuario (se cierra solo, y conviene hacerlo antes)

- **Serie real de rentabilidad por tipo de fondo** en el tablero de la Superfinanciera. Requiere un navegador y veinte minutos, y es el supuesto que más mueve las cifras del RAIS (`supuestos-actuariales.md` s.3).
- **Cotejo de las series de salario mínimo (1992-2009) e IPC (1993-2014)** contra fuente oficial. Una tarde (`supuestos-actuariales.md` s.1 y s.2).
- **Monto y criterio de Colombia Mayor** ($225.000 frente a $230.000, y si el corte es a los 80 años o a la edad plena del programa): una resolución de Prosperidad Social (`sin-pension-alternativas.md` s.7).
- **Tope BEPS 2026 y cortes de Sisbén IV**: acto administrativo del Ministerio del Trabajo (`sin-pension-alternativas.md` s.6).
- **[CERRADO el 2026-09-16] Tabla de coeficientes de presunción de costos por actividad CIIU.** No hizo falta derecho de petición: la tabla completa de 24 renglones está embebida en el selector de la calculadora de IBC de la UGPP (`ugpp.gov.co/calculadora-ibc`), con código CIIU y coeficiente, y es de acceso libre. Capturada y archivada con su hash en `verificacion/evidencia/`, transcrita en `independientes.md` s. 2 bis. Cerró dos marcas de un solo golpe: el coeficiente de rentistas (28,08%) y el alcance sobre dividendos, que el renglón vigente **incluye** (`rentista-de-capital.md` s.5 y s.6). Lo que la calculadora **no** da es el texto del acto administrativo: no cita resolución ni decreto, así que la cifra se atribuye a la conducta oficial de la UGPP y no a un artículo. **Lección de método:** antes de escalar una marca a trámite, revisar si la entidad ya aplica el dato en alguna herramienta pública, porque una calculadora web tiene que descargar sus parámetros al navegador para poder calcular.
- **Fecha de publicación en el Diario Oficial del Decreto 379 del 7 de abril de 2026.** Se conoce la fecha de expedición, no la de publicación, y es la que dispara la vigencia del esquema de presunción de costos: el art. 5 de la Resolución 532, en el texto de la Resolución UGPP 566 de 2025, la hace regir "a partir del mes siguiente a la publicación en el Diario Oficial" de ese decreto. De ahí sale la fecha de mayo de 2026 que usa el agente. **Se cierra abriendo el Diario Oficial de abril de 2026** (`rentista-de-capital.md` s.5).
- **Glosario oficial del reporte de semanas de Colpensiones, columna por columna** (qué son "semanas cotizadas", "en licencia", "simultáneas" y "válidas"). **No se encontró publicado**, y todo lo que hoy explica esas columnas es fuente secundaria. Es lo que falta para cerrar el cuarto estado de `mora-y-correccion-historia-laboral.md` s.1 bis (salario reportado con cero semanas). Se cierra pidiéndolo por PQRS a Colpensiones, no con un abogado.

## Checklist de la capa de referencia (capa 2, por descargar y curar)

Descargar la **versión vigente** (no la original) desde fuentes oficiales (Función Pública / SUIN-Juriscol / Corte Constitucional), verificando qué artículos están modificados o derogados:

- [ ] Ley 100 de 1993 (versión actualizada con todas las modificaciones)
- [ ] Ley 797 de 2003
- [ ] Ley 2381 de 2024 (reforma pensional, suspendida en la Corte)
- [ ] Acto Legislativo 01 de 2005
- [ ] Decreto 758 de 1990 (Acuerdo 049, régimen anterior: aplica por transición en casos viejos)
- [ ] Decreto 1833 de 2016 (compilatorio de pensiones)
- [ ] Decreto 2090 de 2003 (actividades de alto riesgo)
- [ ] Decreto 558 de 2020 y Sentencia C-258 de 2021 (meses COVID)
- [ ] Sentencia C-197 de 2023 (semanas mujeres)
- [ ] Jurisprudencia de traslados e ineficacia (SU-140 de 2019 y línea posterior) `[VERIFICAR cuáles son las sentencias clave con el abogado]`
- [ ] Ley 1580 de 2012 (pensión familiar)

**Momento sugerido:** después de probar la calculadora con casos reales; las conversaciones de prueba dicen qué normas se consultan de verdad.

### Ampliación del checklist (2026-07-21, de los 10 bloques nuevos)

Fuentes ya identificadas y verificadas en vigencia durante la construcción de los destilados. La lista completa con URL oficial de descarga, norma por norma, vive en `../plan-corpus-adyacente.md`.

**Prioridad alta (cambiaron o corrigen algo que el kit daba por cierto):**
- [ ] **Ley 2452 de 2025**, nuevo Código Procesal del Trabajo y de la Seguridad Social. **Vigente desde el 2 de abril de 2026**; derogó el Decreto Ley 2158 de 1948, la Ley 712 de 2001 y la Ley 1149 de 2007. Suprimió la única instancia, lo que en la práctica hace necesario abogado para demandar (con amparo de pobreza como contrapeso)
- [ ] **Sentencia C-054 de 2024**: garantía de pensión mínima en RAIS. Ya aplicada al kit y a la calculadora
- [ ] **Decreto 543 de 2026**: reabre y flexibiliza el subsidio al aporte (PSAP), baja el requisito de 650 a 300 semanas
- [ ] Sentencias **SU-226 de 2019**, **SU-068 de 2022** y **SU-062 de 2023**: mora patronal y omisión de afiliación, con la carga probatoria
- [ ] **Ley 2277 de 2022**, arts. 2, 6, 7 y 8: límite del 40% / 1.340 UVT que pega en la mesada neta

**Resto de fuentes por descargar:**
- [ ] Ley 100 de 1993, arts. 14, 17, 46 a 51, 64 a 66, 79 a 89, 115 a 127, 143, 204 (versión de Secretaría del Senado, ver advertencia de fuentes)
- [ ] Ley 797 de 2003, arts. 4, 12 y 13
- [ ] Estatuto Tributario: arts. 55, 56, 126-1, 126-4, 206, 331 a 337, 383, 385, 386, 592
- [ ] Ley 860 de 2003 art. 1 y Sentencia C-428 de 2009 (invalidez)
- [ ] Decreto 1507 de 2014 (manual de calificación de PCL) y Decreto 1352 de 2013, hoy compilado en el Decreto 1072 de 2015
- [ ] Decreto 1833 de 2016: títulos de bonos pensionales, CETIL, mora, sobrevivientes y modalidades
- [ ] Decreto 604 de 2013 y Decreto 2983 de 2013 (BEPS)
- [ ] Ley 1581 de 2012 y Decreto 1377 de 2013 (habeas data)
- [ ] Ley 1328 de 2009, art. 14 lit. d (límite de competencia del Defensor del Consumidor Financiero)
- [ ] Convenio Multilateral Iberoamericano (en vigor para Colombia desde el 1 de agosto de 2023) y bilaterales con España, Chile, Uruguay, Argentina y Ecuador
- [ ] Sentencias C-1035 de 2008, C-336 de 2008, C-556 de 2009 y SU-149 de 2021 (beneficiarios)

### Advertencia de fuentes (2026-07-21)

- **Para la Ley 100, preferir Secretaría del Senado sobre el Gestor Normativo de Función Pública.** Se detectó que el gestor muestra el art. 17 con un texto mezclado que incluye un fragmento que no está en la versión vigente de la Ley 797. Función Pública sirve bien para decretos y para leyes con notas de vigencia.
- **Verificar siempre vigencia, no existencia.** En esta ampliación aparecieron varias normas derogadas o inexequibles que siguen citándose como vigentes en internet: el requisito de fidelidad para sobrevivientes (C-556 de 2009), el art. 84 de la Ley 100 (derogado por la Ley 1955 de 2019), el aporte del 12% en salud de la Ley 1250 de 2008 (derogado tácitamente), el art. 244 de la Ley 1955 de 2019 (inexequible por C-068 de 2020) y el **art. 151 del Código Procesal del Trabajo de 1948** (derogado por la Ley 2452 de 2025, que rige desde abril de 2026; hoy la prescripción de 3 años está en su art. 317).

### Trampas de fuente añadidas el 2026-07-26

- **Una derogatoria se verifica artículo por artículo, no por el número de la ley.** Una fuente secundaria sostenía que el art. 289 de la Ley 100 derogó el **art. 2** de la Ley 33 de 1985; lo que derogó fue el **art. 5**. El art. 2 sigue vivo y es el fundamento de la cuota parte pensional. Estuvo a punto de salir del kit una norma vigente.
- **No confundir una unidad con un porcentaje.** El kit afirmaba que el Acto Legislativo 01 de 2005 limitaba el crecimiento del IBL del último año en un **25%**. No existe tal regla: la única mención al 25 en esa norma es el tope de **25 salarios mínimos** para pensiones con cargo a recursos públicos. Se confundió "25 SMLMV" con "25%".
- **Tampoco confundir el valor de una fórmula con su límite legal.** El kit daba 55,5% como piso de la tasa de reemplazo del RPM; ese era el valor de la fórmula en s = 20. El piso legal es **55%** y lo dice el propio art. 34.
- **El Gestor Normativo también muestra desactualizado el art. 74 de la Ley 100** (beneficiarios de sobrevivientes en RAIS): publica el texto original, de 2 años de convivencia, cuando el art. 13 de la Ley 797 de 2003 lo reemplazó junto con el art. 47. Es el mismo problema ya detectado con el art. 17.
- **Las circulares se mueven de lugar.** La Circular Básica Jurídica de la Superfinanciera fue reexpedida en 2014 y otra vez en 2025. **No citar numerales de circular sin haber abierto el texto vigente:** un numeral mal citado suena preciso y no lo es.

### Notas de fuente añadidas el 2026-07-28

**1. Que un sitio oficial "no responda" casi nunca significa que esté caído. Significa que hay que cambiar de herramienta.** Es la regla que más tiempo ahorra de esta lista, porque el reflejo equivocado es degradar a fuentes secundarias cuando la fuente oficial sigue ahí.

| Sitio | Cómo falla | Qué funciona |
|---|---|---|
| **Secretaría del Senado** | Rechaza la conexión por HTTPS (`ECONNREFUSED` en 200.7.106.227:443). Cualquier herramienta que fuerce HTTPS queda inservible | **Bajar por HTTP con `curl -skL`** sobre la URL `http://` y limpiar el HTML. Así salieron el art. 89 de la Ley 2277 y los arts. 18, 19 y 20 de la Ley 100 |
| **Función Pública (Gestor Normativo)** | Falla con "unable to verify the first certificate" | **`curl -k`**. Así salieron el Decreto 379 de 2026 completo y el PDF de la Ley 2381 |
| **SUIN-Juriscol** | El mismo error de certificado | **`curl -k`** |
| **UGPP** | Responde bien, pero sus fichas de normas son páginas de índice: publican el título y **no** el texto ni los anexos | Para el articulado, ir a una compilación oficial (Secretaría Jurídica Distrital de Bogotá). Para los anexos, pedirlos por transparencia |

En la sesión del 2026-07-28 no hubo que degradar a fuente secundaria ni una sola vez por esta razón. **Antes de escribir "no se pudo verificar en fuente oficial", agotar el cambio de herramienta.**

**2. El enganche legal de una figura no siempre está donde la intuición dice.** Caso concreto y contraintuitivo: la definición del **rentista de capital** para efectos de cotización **no está en norma tributaria**. El art. 89 de la Ley 2277 de 2022, que es la norma del IBC de los independientes, no lo nombra ni una vez. La frase que lo mete al sistema está en el **Decreto 780 de 2016, que es el Decreto Único Reglamentario del Sector Salud**, art. 3.2.7.2 lit. b, puesto ahí por el Decreto 1601 de 2022 del Ministerio de Salud.

Regla práctica para preguntas de base de cotización: la cadena útil es **Ley 100** (base y techo) más **Ley 2277 art. 89** (el 40%) más **Decreto 780 título 7** (procedimiento y definiciones). El Estatuto Tributario entra solo por remisión, en el art. 107 para costos. Buscar en fuentes DIAN para este tema cuesta tiempo y no rinde.

## Checklist de datos de producto (no son normas, son insumos de UX)

- [ ] **Tabla de benchmark de pares** (semanas y saldo acumulado por edad, fuente pública: Superfinanciera / Asofondos / Colpensiones). Habilita el mensaje "estás en el top X% para tu edad" (idea validada con Santiago 2026-07-20, ver `system-prompt.md`). Sin esta fuente cargada y verificada, el agente NO debe mostrar percentiles.

## Calendario de mantenimiento del corpus (manual, en laboratorio)

| Evento | Qué se actualiza | Cuándo |
|---|---|---|
| Decreto de salario mínimo | SMLMV nuevo en datos de la calculadora | Cada diciembre-enero |
| Boletín IPC del DANE | IPC del año cerrado en datos de la calculadora | Cada enero |
| Fallo de la Corte sobre Ley 2381 | Potencialmente todo el kit (escenarios en `reforma-ley-2381.md`) | El día del fallo |
| Tabla C-197 (semanas mujeres) | Nada: ya está codificada año a año | Automático |
| Jurisprudencia nueva relevante | Destilado afectado + capa 2 | Al detectarla (revisión periódica) |

> **Límite conocido de este calendario (2026-07-21):** cubre lo previsible (salario mínimo, IPC) y **no cubre lo imprevisible**, que es lo que más ha dolido. En un solo día de trabajo aparecieron cuatro normas materiales que el kit no tenía, incluida una que producía una cifra equivocada en la calculadora. La idea de un **agente de vigilancia normativa que levante alertas** (sin editar el kit por su cuenta) quedó planteada como pendiente de futuro en `../ESTADO.md`, para abordarla cuando Júbilo opere comercialmente.
