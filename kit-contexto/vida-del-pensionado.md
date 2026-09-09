# La vida después de pensionarse (bloque A del plan de corpus)

> **Última actualización:** 2026-07-21. **Estado:** destilado inicial verificado contra texto vigente en Secretaría del Senado (compilación actualizada al 15 de julio de 2026), Función Pública y Corte Constitucional. Marcas `[VERIFICAR]` para el abogado pensional antes del piloto.
> **Por qué existe:** el kit cubría cómo se calcula la pensión, no qué pasa después. El hueco apareció en role-play con el escenario estrella del producto: alguien que se pensiona anticipadamente en RAIS a los 35-40 años y sigue trabajando décadas.
> **Convención:** cada regla cita su fuente legal. Toda cifra que cambia cada año (SMLMV, IPC) es dato de la calculadora, no texto de este documento.

## 1. La regla madre: qué cambia y qué no el día que te pensionas

| Obligación | ¿Sigue después de pensionarse? | Fuente |
|---|---|---|
| Cotizar a **pensión** | **No.** La obligación cesa | Ley 100 art. 17, mod. Ley 797/2003 art. 4 |
| Cotizar a **salud** sobre la mesada | **Sí**, siempre, y se descuenta de la mesada | Ley 100 arts. 143 y 204 par. 5 |
| Cotizar a **salud** sobre el salario si sigue trabajando | **Sí**, además de lo anterior | Decreto 780/2016 art. 2.2.1.1.2.1 |
| Afiliación a **riesgos laborales (ARL)** si sigue trabajando como dependiente | **Sí**, obligatoria y a cargo del empleador | Ley 1562/2012 art. 2, num. 3 del lit. a) |

**El titular para el usuario:** pensionarse apaga el aporte a pensión, no apaga el aporte a salud. Y si sigue trabajando, la seguridad social del trabajo (salud y ARL) se mantiene completa.

## 2. Cotización a pensión: cuándo cesa exactamente

Texto vigente: *"La obligación de cotizar cesa al momento en que el afiliado reúna los requisitos para acceder a la pensión mínima de vejez, o cuando el afiliado se pensione por invalidez o anticipadamente."* *Fuente: Ley 100 art. 17, modificado por Ley 797 de 2003 art. 4.*

Tres consecuencias que hay que decir con precisión:

1. **Cesa la obligación, no la posibilidad.** El mismo artículo agrega que lo anterior es "sin perjuicio de los aportes voluntarios que decida continuar efectuando el afiliado o el empleador en los dos regímenes".
2. **Si el trabajador decide seguir cotizando, el empleador está obligado a acompañarlo.** La Corte Constitucional lo fijó: la decisión del afiliado de continuar cotizando voluntariamente es vinculante para su empleador, que debe seguir haciendo los aportes a su cargo. *Fuente: Sentencia C-529 de 2010 (M.P. Mauricio González Cuervo).*
3. **Nadie puede obligar al trabajador a seguir cotizando** (salvo el caso público de la sección 8).

**Aterrizaje:** "Ya pensionado, el descuento del 4% de pensión sobre tu sueldo desaparece y tu empleador se ahorra su 12%. Si tú decides seguir aportando, él está obligado a seguir poniendo su parte."

## 3. El caso estrella: pensión anticipada en RAIS y seguir trabajando 25 años más

En el RAIS se puede pensionar a cualquier edad si el saldo financia una mesada superior al 110% del SMLMV. *Fuente: Ley 100 art. 64 inciso 1.* Detalle del cálculo en `reglas-rais.md` sección 3.

**Qué le queda a esa persona si sigue trabajando:**

- **Pensión: nada obligatorio.** El art. 17 nombra expresamente el caso ("o cuando el afiliado se pensione ... anticipadamente"). Quien ya tomó la pensión anticipada no tiene obligación de cotizar a pensión por el resto de su vida laboral.
- **Salud: todo.** Paga sobre la mesada (sección 4) y, además, la cotización de trabajador dependiente o independiente sobre su ingreso laboral (sección 5).
- **ARL: sí, si trabaja como dependiente.** La ley nombra a los pensionados que se reincorporan a la fuerza laboral como afiliados obligatorios. *Fuente: Ley 1562 de 2012 art. 2, que modificó el art. 13 del Decreto-ley 1295 de 1994, lit. a) num. 3.*

**La distinción que más se confunde, y hay que decirla bien:**

El artículo 64 tiene un **segundo inciso** que dice: *"Cuando a pesar de cumplir los requisitos para acceder a la pensión en los términos del inciso anterior, el trabajador opte por continuar cotizando, el empleador estará obligado a efectuar las cotizaciones a su cargo, mientras dure la relación laboral, legal o reglamentaria, y hasta la fecha en la cual el trabajador cumpla sesenta (60) años si es mujer y sesenta y dos (62) años de edad si es hombre."*

- Ese inciso aplica a quien **puede** pensionarse anticipadamente y **decide no hacerlo todavía**: ahí el empleador debe seguir cotizando hasta los 60/62.
- No aplica a quien **ya tomó** la pensión: para ese, rige el art. 17 y la obligación cesó.

`[VERIFICAR]` **Respuesta operativa:** el agente le dice al pensionado del RAIS que **su mesada ya no sube por ahorrar más en el sistema obligatorio**, y que el ahorro nuevo debe ir a un fondo de pensiones **voluntarias**, que es un producto aparte. El razonamiento es de mecánica, no de doctrina: si contrató renta vitalicia, la mesada quedó fija en un contrato con una aseguradora y ningún aporte posterior la mueve (*reglas-rais.md* s.4); si está en retiro programado, su cuenta se recalcula cada año pero la cotización obligatoria ya cesó al pensionarse (*Ley 100 art. 17, texto vigente de la Ley 797 art. 4*). Y el intento de aportar a voluntarias ya pensionado para retirarlo exento tampoco funciona (*Oficio DIAN 3706 de 2018*, ver `tributario-pensional.md` s. 7 bis). **Falta confirmar:** qué hace en la práctica cada AFP si un pensionado insiste en consignar a la cuenta obligatoria (¿lo rechaza, lo devuelve, lo reclasifica?). No se encontró fuente oficial que lo resuelva. **Si cambia:** si alguna AFP sí admitiera aportes que recalculan la mesada del retiro programado, se abriría una palanca real para el pensionado anticipado con capacidad de ahorro, que es un segmento de alto valor. Mientras tanto la **postura conservadora** es la de arriba: no prometer que el ahorro nuevo sube la mesada, porque quien mueva plata sobre esa promesa la deja atrapada en el producto equivocado.

**Riesgo laboral del escenario (no pensional, pero el usuario va a preguntar):** cumplir requisitos de pensión es justa causa de terminación del contrato, y el empleador puede darlo por terminado cuando la pensión sea reconocida o notificada. *Fuente: Ley 100 art. 33 par. 3, mod. Ley 797 de 2003 art. 9 (parágrafo condicionalmente exequible).*

`[VERIFICAR]` **Respuesta operativa:** el agente **advierte el riesgo sin darlo por cierto**: le dice al usuario que pensionarse anticipadamente por el art. 64 y seguir en el mismo empleo lo pone en una zona no resuelta, y que **antes de firmar su pensión hable con su empleador o con un laboralista**. No le dice "te pueden despedir" ni "no te pueden despedir". El argumento a favor de que **no** aplica es de texto: el parágrafo condiciona la justa causa a cumplir los requisitos "establecidos en este artículo", y ese artículo es el 33 (edad y semanas del RPM), que un pensionado anticipado de 38 años no cumple. **Falta confirmar:** con el abogado, si la jurisprudencia laboral ha extendido la justa causa a la pensión del art. 64. **Si cambia:** cambia una decisión grande e irreversible. Alguien puede tomar la pensión anticipada creyendo que conserva su empleo y perder el sueldo el mismo mes. Por eso la **postura conservadora** aquí es advertir del riesgo, no invocar la lectura literal favorable: el costo de equivocarse hacia el optimismo lo paga el usuario con su trabajo.

**Aterrizaje:** "Si te pensionas anticipadamente y sigues trabajando, no vuelves a pagar un peso obligatorio a pensión. Salud sí, doble: sobre la mesada y sobre el sueldo. Y tu empleador te debe afiliar a la ARL."

## 4. Salud: cuánto te descuentan de la mesada

La cotización en salud de los pensionados está **en su totalidad a cargo de ellos** y se descuenta de la mesada. *Fuente: Ley 100 art. 143 inciso 2.*

Tarifa vigente por rango de mesada:

| Mesada | Aporte a salud | Fuente |
|---|---|---|
| 1 SMLMV | 4% | Ley 100 art. 204 par. 5, adicionado por Ley 2010 de 2019 art. 142 (tabla "a partir de 2022") |
| Más de 1 y hasta 2 SMLMV | 10% | Misma |
| Más de 2 y hasta 3 SMLMV | 10% | Ley 2294 de 2023 art. 78, que adicionó un inciso al par. 5, con vigencia desde 2024 |
| Más de 3 SMLMV | 12% | Ley 100 art. 204 par. 5 (tabla "a partir de 2022") |

- La tabla original de la Ley 2010 de 2019 para 2020 y 2021 (8% y 10%) **perdió fuerza ejecutoria por cumplimiento del objeto**; no se usa.
- El inciso del 12% para pensionados que traía la Ley 1250 de 2008 art. 1 quedó **derogado tácitamente** por el parágrafo 5. No citarlo como norma vigente.
- La demanda contra el parágrafo 5 terminó en **inhibición**, así que la norma sigue en pie. *Fuente: Sentencia C-409 de 2021.*

`[VERIFICAR]` **Respuesta operativa:** el agente usa el **10%** para el tramo de 2 a 3 SMLMV, es decir, da la rebaja por vigente. La reglamentación que faltaba sí se expidió: la **Resolución 1271 de agosto de 2023** del Ministerio de Salud (vía el Anexo Técnico 1 de la PILA), y la rebaja opera desde la cotización de enero de 2024. Colpensiones lo comunicó públicamente y la está aplicando en 2026. **Falta confirmar:** el texto de esa resolución en fuente primaria (la investigación del 2026-07-26 la corroboró por varias fuentes secundarias más un comunicado de Colpensiones, no leyó el diario oficial); y qué pasa con el beneficio al terminar el cuatrienio, porque la Ley 2294 de 2023 es el Plan Nacional de Desarrollo 2022-2026 y sus normas instrumentales pueden perder vigencia. **Si cambia:** el pensionado de ese tramo pasaría de 10% a 12%, unos $35.000 mensuales menos sobre una mesada de 2 SMLMV. **Regla de revisión:** este es el primer dato del kit que hay que mirar en enero de 2027, junto con el SMLMV.

**Aterrizaje:** "De tu mesada te descuentan salud antes de que te llegue. Cuánto depende del tamaño de la mesada: 4% si es de un mínimo, 10% hasta tres mínimos, 12% de ahí para arriba."

## 5. Salud cuando además hay salario o ingresos: se paga sobre las dos cosas

Regla: *"Para los pensionados las cotizaciones se calcularán con base en la mesada pensional"*, y *"cuando el afiliado perciba salario o pensión de dos o más empleadores u ostente simultáneamente la calidad de asalariado e independiente, las cotizaciones correspondientes serán efectuadas en forma proporcional al salario, ingreso o pensión devengado de cada uno de ellos"*. *Fuente: Decreto 780 de 2016 art. 2.2.1.1.2.1 (compila el art. 65 del Decreto 806 de 1998).*

Traducido a la vida real del pensionado que trabaja:

- **Sobre la mesada:** el porcentaje de la tabla de la sección 4, todo a su cargo.
- **Sobre el salario:** la cotización ordinaria de trabajador dependiente, 4% a su cargo y 8,5% a cargo del empleador. *Fuente: Ley 100 art. 204 inciso 1, mod. Ley 1122 de 2007 art. 10.*
- **Sobre honorarios como independiente:** la cotización que le corresponda como independiente (base del 40% del ingreso mensualizado, ver `independientes.md`).

**Consecuencia contraintuitiva y valiosa:** un pensionado en salud paga más que un trabajador no pensionado con el mismo sueldo, porque paga dos veces sobre bases distintas. Al proyectar ingreso neto en el escenario "me pensiono y sigo trabajando", el modelo debe restar los dos aportes.

**Aterrizaje:** "Salud la pagas dos veces: un porcentaje de tu mesada y el 4% de tu sueldo. No es un error de tu empresa ni de tu fondo, es como está diseñado."

## 6. EPS, beneficiarios y qué cubre el pensionado

- El pensionado es **afiliado cotizante del régimen contributivo**; conserva su EPS y puede trasladarse como cualquier otro afiliado.
- **Sí puede tener beneficiarios.** Núcleo familiar: cónyuge; a falta de cónyuge, compañero o compañera permanente (incluidas parejas del mismo sexo); hijos menores de 25 que dependan económicamente; hijos de cualquier edad con incapacidad permanente que dependan económicamente; hijos del cónyuge o compañero en esas mismas situaciones; y, a falta de cónyuge, compañero e hijos, los padres que **no estén pensionados** y dependan económicamente. *Fuente: Decreto 780 de 2016 art. 2.1.3.6.*
- **Límite importante:** los pensionados cotizantes reciben únicamente la **prestación de servicios de salud** del plan de beneficios. *Fuente: Decreto 780 de 2016 art. 2.1.3.6, inciso final.* Es decir, por su condición de pensionado no genera derecho a prestaciones económicas (incapacidades ni licencias) con cargo a la EPS. Si además es trabajador activo, esas prestaciones se derivan de su vínculo laboral, no de la mesada.

`[VERIFICAR]` **Respuesta operativa:** el agente responde que **el pensionado que además trabaja sí tiene derecho a incapacidades y licencias, pero por su vínculo laboral, no por su mesada.** Es la lectura directa de la norma: el inciso final del art. 2.1.3.6 del Decreto 780 de 2016 limita lo que genera la **condición de pensionado**, no lo que genera un contrato de trabajo vigente sobre el que se cotiza a salud. **Falta confirmar:** con el abogado, si alguna EPS niega la prestación económica alegando esa frase cuando la persona es pensionada y trabajadora a la vez, y con qué resultado. **Si cambia:** si se confirmara que la condición de pensionado bloquea la prestación económica del vínculo laboral, un pensionado anticipado que siga trabajando quedaría sin ingreso durante una incapacidad larga, que es exactamente el escenario en que más lo necesita. El agente lo menciona como punto a verificar con la EPS antes de contar con esa plata.
- **Nadie puede estar afiliado dos veces.** No se puede ser cotizante y beneficiario al mismo tiempo, ni estar en dos EPS. *Fuente: Decreto 780 de 2016 art. 2.1.3.14.* Caso típico: la persona que se pensiona y venía como beneficiaria de su cónyuge pasa a ser cotizante.

**Aterrizaje:** "Sigues con tu EPS y puedes tener a tu pareja y a tus hijos como beneficiarios, igual que ahora. Lo que cambia es que ahora el cotizante eres tú y el descuento sale de tu mesada."

## 7. Riesgos laborales (ARL)

- **Pensionado que vuelve a trabajar como dependiente:** afiliado obligatorio al Sistema General de Riesgos Laborales. *Fuente: Ley 1562 de 2012 art. 2, que modificó el art. 13 del Decreto-ley 1295 de 1994, lit. a) num. 3: "los jubilados o pensionados, que se reincorporen a la fuerza laboral como trabajadores dependientes, vinculados mediante contrato de trabajo o como servidores públicos".*
- **Pensionado contratista:** también es afiliado obligatorio si el contrato formal de prestación de servicios supera un mes. *Fuente: misma norma, lit. a) num. 1.*
- El aporte a ARL de trabajadores dependientes es **100% a cargo del empleador**. La condición de pensionado no lo cambia.

**Aterrizaje:** "Sí, te tienen que afiliar a la ARL, y la paga la empresa. Estar pensionado no te quita la cobertura de accidente de trabajo."

## 8. ¿Pensión y sueldo al mismo tiempo? Depende del sector

- **Sector privado: sí, sin restricción pensional.** No hay norma que prohíba recibir mesada y salario privado a la vez.
- **Sector público: no, por regla general.** Nadie puede recibir más de una asignación que provenga del tesoro público, salvo los casos que la ley determine expresamente. *Fuente: Constitución Política art. 128.* En la práctica, las administradoras condicionan la inclusión en nómina de pensionados a la certificación del retiro del servicio.
- **Excepción del servidor público que decide quedarse:** quien accede o está en ejercicio de funciones públicas puede permanecer voluntariamente en el cargo aunque haya completado los requisitos de pensión, **con la obligación de seguir contribuyendo a salud, pensión y riesgos laborales**, y sin que le aplique la justa causa de terminación del par. 3 del art. 9 de la Ley 797 de 2003. *Fuente: Ley 1821 de 2016 art. 2; edad de retiro forzoso de 70 años en su art. 1.* Es la única situación en la que la cotización a pensión **no** cesa al cumplir requisitos.

`[VERIFICAR]` **Respuesta operativa:** el agente responde que **al pensionado del RAIS la prohibición del art. 128 no lo alcanza**, porque esa norma prohíbe recibir más de una asignación **que provenga del Tesoro Público**, y una mesada pagada por una AFP privada con el ahorro propio del afiliado no sale del Tesoro. El caso distinto es el pensionado de **Colpensiones**, cuya mesada sí sale de recursos públicos: ahí la restricción puede operar salvo excepción legal. Las excepciones están en el art. 19 de la Ley 4 de 1992 (entre ellas docentes por horas cátedra y quienes reciben asignación de retiro de la Fuerza Pública). *Fuente: Constitución art. 128; Ley 4 de 1992 art. 19; doctrina reiterada del Departamento Administrativo de la Función Pública.* **Falta confirmar:** el listado literal completo del art. 19 de la Ley 4 de 1992 (la investigación del 2026-07-26 solo verificó los primeros literales) y el número de los conceptos de Función Pública que sostienen la distinción RAIS/RPM. **Si cambia:** si la distinción cayera, un pensionado anticipado del RAIS que planea seguir en el sector público tendría que escoger entre la mesada y el sueldo. Por el tamaño de esa decisión, el agente da la respuesta pero **manda a confirmar con la entidad contratante antes de renunciar a nada**, porque quien decide ahí es el pagador.

**Aterrizaje:** "En una empresa privada puedes tener pensión y sueldo sin problema. En el sector público no: la regla general es que no puedes recibir dos pagos del Estado, y si te quedas en el cargo sigues cotizando a pensión."

## 9. Cómo sube la mesada cada año

*"Se reajustarán anualmente de oficio, el primero de enero de cada año, según la variación porcentual del Índice de Precios al Consumidor, certificado por el DANE para el año inmediatamente anterior. No obstante, las pensiones cuyo monto mensual sea igual al salario mínimo legal mensual vigente, serán reajustadas de oficio cada vez y con el mismo porcentaje en que se incremente dicho salario por el Gobierno."* *Fuente: Ley 100 art. 14.*

- Aplica a **los dos regímenes** (el artículo lo dice expresamente) y a pensiones de vejez, invalidez y sobrevivientes.
- **Dos índices distintos:** mesada de 1 SMLMV sube con el salario mínimo; mesada superior sube con el IPC del año anterior.
- **Ninguna pensión puede quedar por debajo del salario mínimo.** *Fuente: Acto Legislativo 01 de 2005 (inciso agregado al art. 48 de la Constitución).*
- El reajuste es **de oficio**: no hay trámite que hacer.
- El parágrafo del art. 14 (mod. Ley 1753 de 2015 art. 138) faculta al Gobierno para crear coberturas que protejan a las aseguradoras de renta vitalicia cuando el salario mínimo sube más que el IPC. Es contexto de por qué la renta vitalicia de mínimo es cara, no una regla que afecte al usuario.

**Implicación para la calculadora:** en proyecciones largas, el mismo capital rinde distinto según si la mesada quedará anclada al SMLMV o al IPC. La serie de ambos índices ya está en `supuestos-actuariales.md`.

**Aterrizaje:** "Tu mesada sube sola cada 1 de enero. Si es de un salario mínimo, sube lo mismo que el mínimo. Si es más alta, sube con la inflación del año pasado."

## 10. Mesada 13 y mesada 14

- **Mesada 13: vigente y universal.** Los pensionados reciben cada año, junto con la mesada de noviembre y en la primera quincena de diciembre, una mensualidad adicional. *Fuente: Ley 100 art. 50.*
- **Mesada 14: eliminada para prácticamente todo el mundo.** Quien cause su derecho a pensión a partir del 25 de julio de 2005 no puede recibir más de **13 mesadas** al año. La pensión se causa cuando se cumplen todos los requisitos, aunque no se haya reconocido. *Fuente: Acto Legislativo 01 de 2005 art. 1 (inciso agregado al art. 48 de la Constitución).*
- **Única excepción viva:** pensión igual o inferior a 3 SMLMV **causada antes del 31 de julio de 2011**, que sí recibe 14 mesadas. *Fuente: Acto Legislativo 01 de 2005, parágrafo transitorio 6.*
- La mesada adicional de junio del art. 142 de la Ley 100 es un beneficio cerrado: solo cobija pensiones causadas y reconocidas **antes del 1 de enero de 1988**.

**Aterrizaje:** "Vas a recibir 13 mesadas al año, la extra llega en diciembre. La mesada 14 se acabó en 2005; solo la conserva quien ya se había pensionado antes de agosto de 2011 con una pensión de hasta tres mínimos."

## 11. Cómo lo usa el agente

1. **Toda proyección de mesada debe presentarse en bruto y en neto.** El neto resta el aporte a salud de la sección 4. Presentar solo la mesada bruta sobreestima el ingreso entre 4% y 12%.
2. **En el escenario de pensión anticipada, decir siempre las tres obligaciones juntas** (pensión no, salud sí y doble, ARL sí). Es la respuesta que faltaba y es corta.
3. **Nunca prometer que la pensión anticipada libera de la seguridad social.** Libera del aporte a pensión, nada más.
4. **Distinguir sector privado y público** antes de responder sobre pensión y sueldo simultáneos.
5. **No congelar cifras anuales.** SMLMV, IPC y los umbrales en salarios mínimos vienen de los datos de la calculadora.

## 12. Fuera de alcance

Estos temas quedan fuera de este documento y el agente los deriva:

- **Sobrevivencia y herencia de la mesada** (qué pasa con la familia al morir el pensionado): bloque C del plan de corpus, aún no construido. Hoy se responde con el "no lo sé" y se deriva a la administradora.
- **Elección entre retiro programado y renta vitalicia** y sus consecuencias sobre el saldo: bloque D. `reglas-rais.md` sección 4 solo las nombra.
- **Reliquidación de la pensión** por aportes posteriores al reconocimiento.
- **Incapacidades, licencias y calificación de invalidez** del pensionado que sigue trabajando: bloque E.
- **Tratamiento tributario de la mesada y de la retención en la fuente:** está en `tributario-pensional.md`, no aquí.
- **Regímenes exceptuados** (fuerza pública, magisterio, Ecopetrol): tienen reglas propias de aportes a salud y de mesadas adicionales. Ver `regimenes-especiales.md`.
- **Liquidación exacta de la PILA** del pensionado que además trabaja.
