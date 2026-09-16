# Costo de cotizar - Documento 7 del kit

> **Creado:** 2026-07-27. **Por qué existe:** hueco detectado en la demo del 2026-07-26. El kit cubría el aporte a salud del **pensionado** (`vida-del-pensionado.md` sección 4) pero no el del **cotizante activo**, así que el agente no podía responder la pregunta comercial más importante del segmento independiente: "si subo mi base, ¿cuánto me cuesta al mes?". Este documento cierra ese hueco.
> **Alcance:** el costo de cotizar mientras se aporta. Quién puede cotizar, sobre qué base y con qué riesgo está en `independientes.md`, que es el documento vecino y no se duplica aquí.
> **Regla dura del proyecto:** la IA nunca calcula. Todo número de este documento sale de `calculadora/costo_y_retorno.py` y las cifras de abajo son ilustrativas del orden de magnitud, no la respuesta al usuario. La respuesta al usuario la produce el módulo.

## 1. Los tres componentes del costo

Quien cotiza como independiente paga de su bolsillo tres cosas sobre **la misma base**:

| Componente | Tarifa | Desde cuándo aplica | Fuente |
|---|---|---|---|
| Pensión | 16% del IBC | Siempre | Ley 100 de 1993 art. 20, mod. Ley 797 de 2003 art. 7 |
| Fondo de Solidaridad Pensional, subcuenta de solidaridad | +1% del IBC | IBC igual o superior a 4 SMLMV | Ley 100 art. 20, mod. Ley 797 art. 7 (obligación) y art. 27, mod. Ley 797 art. 8 (destino) |
| Fondo de Solidaridad Pensional, subcuenta de subsistencia | +0,2% a +1% del IBC | IBC igual o superior a 16 SMLMV | Ley 100 art. 27, mod. Ley 797 art. 8 num. 2 lit. a) |
| Salud | 12,5% del IBC | Siempre | Ley 100 art. 204 inciso 1, mod. Ley 1122 de 2007 art. 10 |

**Tarifa combinada resultante** (la cifra que el usuario siente):

| Tramo de IBC | Tarifa total |
|---|---|
| De 1 a menos de 4 SMLMV | 28,5% |
| De 4 a menos de 16 SMLMV | 29,5% |
| De 16 a 20 SMLMV | 29,7% a 30,3% según el tramo |
| Más de 20 SMLMV | 30,5% |

**Aterrizaje para el usuario:** "De cada 100 pesos de base que declares, se van cerca de 30: 16 a pensión y 12,5 a salud, más un punto de solidaridad si tu base pasa de cuatro mínimos."

## 2. Salud del cotizante activo: 12,5%

**Texto vigente del art. 204 de la Ley 100 de 1993, inciso 1, modificado por el art. 10 de la Ley 1122 de 2007** (transcripción literal, Secretaría del Senado, `secretariasenado.gov.co/senado/basedoc/ley_0100_1993_pr004.html`):

> "La cotización al Régimen Contributivo de Salud será, a partir del primero (1º) de enero del año 2007, del 12,5% del ingreso o salario base de cotización, el cual no podrá ser inferior al salario mínimo. La cotización a cargo del empleador será del 8.5% y a cargo del empleado del 4%. Uno punto cinco (1,5) de la cotización serán trasladados a la subcuenta de Solidaridad del Fosyga para contribuir a la financiación de los beneficiarios del régimen subsidiado."

**Vigencia confirmada, no solo existencia:** en el texto compilado por la Secretaría del Senado, el inciso 1 aparece con nota de vigencia activa ("Inciso 1o. modificado por el artículo 10 de la Ley 1122 de 2007. El nuevo texto es el siguiente"). Lo que sí está derogado o caído en ese mismo artículo es otra cosa: el inciso 2 es **inexequible**, y el inciso del 12% para pensionados de la Ley 1250 de 2008 quedó **derogado tácitamente** por el parágrafo 5 (ver `vida-del-pensionado.md` sección 4). El 12,5% del cotizante activo sigue en pie. **Confianza: ALTA.**

**El reparto 8,5% empleador / 4% empleado no aplica al independiente.** No hay empleador: los 12,5 puntos son suyos. Es exactamente el mismo salto que en pensión (16% completo en vez de 12% + 4%) y conviene decirlo junto, porque el usuario suele conocer la cifra de "4%" de cuando era empleado y subestima el costo real por un factor de tres.

**Qué NO es este 12,5%:** no es la tarifa del pensionado. El pensionado paga entre 4% y 12% sobre la mesada según su tamaño (`vida-del-pensionado.md` sección 4). Son dos momentos distintos de la vida financiera y el agente no los mezcla: 12,5% mientras aporta, 4% a 12% cuando cobra.

`[VERIFICAR]` **Respuesta operativa:** el agente responde 12,5% de salud a cargo del independiente, sobre la misma base de pensión. **Falta confirmar:** el texto del art. 18 de la Ley 1122 de 2007 (aseguramiento de los contratistas de prestación de servicios) en fuente primaria; el 2026-07-27 la Secretaría del Senado y el Gestor Normativo no respondieron (conexión rechazada y certificado inválido). El 12,5% queda cerrado igual porque el texto vigente se leyó en el art. 204 compilado, que es la norma sustantiva. **Si cambia:** no cambiaría la tarifa, sí podría afinar la regla de base para el contratista frente al rentista.

## 3. Fondo de Solidaridad Pensional: el 1% y el escalonado

Son **dos aportes distintos que se suman**. Confundirlos es el error clásico y ya se cometió una vez en role-play (`reglas-rpm.md` sección 2).

**Texto literal del art. 8 de la Ley 797 de 2003, que modificó el art. 27 de la Ley 100 de 1993** (Secretaría del Senado, `secretariasenado.gov.co/senado/basedoc/ley_0797_2003.html`):

> "Artículo 27. Recursos. El fondo de solidaridad pensional tendrá las siguientes fuentes de recursos:
> **1. Subcuenta de solidaridad**
> a) El cincuenta por ciento (50%) de la cotización adicional del 1% sobre la base de cotización, a cargo de los afiliados al sistema general de pensiones cuya base de cotización sea igual o superior a cuatro (4) salarios mínimos legales mensuales vigentes; [...]
> **2. Subcuenta de Subsistencia**
> a) Los afiliados con ingreso igual o superior a 16 salarios mínimos mensuales legales vigentes, tendrán un aporte adicional sobre su ingreso base de cotización, así: de 16 a 17 smlmv de un 0.2%, de 17 a 18 smlmv de un 0.4%, de 18 a 19 smlmv de un 0.6%, de 19 a 20 smlmv de un 0.8% y superiores a 20 smlmv de 1% destinado exclusivamente a la subcuenta de subsistencia del Fondo de Solidaridad Pensional de que trata la presente ley;
> b) El cincuenta (50%) de la cotización adicional del 1% sobre la base de cotización, a cargo de los afiliados al sistema general de pensiones cuya base de cotización sea igual o superior a cuatro (4) salarios mínimos legales mensuales vigentes; [...]"

**Precisión de fuente que importa:** el art. 8 (art. 27 de la Ley 100) regula el **destino** de los recursos, y de ahí sale la tabla del escalonado. La **obligación de pagar** el 1% está en el art. 7 de la Ley 797, que modificó el art. 20 de la Ley 100, con este texto:

> "Los afiliados que tengan un ingreso mensual igual o superior a cuatro (4) salarios mínimos mensuales legales vigentes, tendrán a su cargo un aporte adicional de un uno por ciento (1%) sobre el ingreso base de cotización, destinado al fondo de solidaridad pensional, de conformidad con lo previsto en la presente ley en los artículos 25 y siguientes de la Ley 100 de 1993."

El art. 7 repite además, palabra por palabra, la misma tabla escalonada del art. 8. Citar cualquiera de los dos es correcto; citar los dos es más sólido. **Confianza: ALTA en ambos textos.**

**Tres cosas que la ley dice y que se leen mal con frecuencia:**

1. **El escalonado se SUMA al 1%, no lo reemplaza.** Quien cotiza sobre más de 20 SMLMV paga 1% de solidaridad **más** 1% de subsistencia: 2 puntos por encima del 16%.
2. **El escalonado se aplana en 1% por encima de 20 SMLMV.** No llega a 25 SMLMV ni sigue subiendo. El techo de 25 SMLMV es del **IBC**, no del escalonado: 25 SMLMV es una unidad de base, no un porcentaje.
3. **El 50% / 50% del literal a) y del literal b) no cambia lo que paga el usuario.** Es el reparto interno del 1% entre las dos subcuentas del fondo. El afiliado paga 1%, punto. El agente nunca dice "pagas 0,5% y 0,5%".

**Tabla operativa** (idéntica a `reglas-rpm.md` sección 2, misma fuente, no se reinterpreta):

| IBC | Solidaridad | Subsistencia | Total FSP |
|---|---|---|---|
| Menos de 4 SMLMV | 0% | 0% | 0% |
| De 4 a menos de 16 SMLMV | 1,0% | 0% | 1,0% |
| De 16 a 17 SMLMV | 1,0% | 0,2% | 1,2% |
| De 17 a 18 SMLMV | 1,0% | 0,4% | 1,4% |
| De 18 a 19 SMLMV | 1,0% | 0,6% | 1,6% |
| De 19 a 20 SMLMV | 1,0% | 0,8% | 1,8% |
| Más de 20 SMLMV | 1,0% | 1,0% | 2,0% |

`[VERIFICAR]` **Respuesta operativa:** el agente lee la tabla de arriba tal cual y nunca estima el tramo alto a ojo. **Falta confirmar** (dos preguntas, ambas para el abogado): (a) si dentro de un tramo el escalonado se aplica por salto al cruzar el umbral o de forma proporcional, y (b) qué tarifa aplica **exactamente en 20,00 SMLMV**, porque la ley dice "de 19 a 20" para el 0,8% y "superiores a 20" para el 1%, y el punto exacto cae en los dos bordes. Hoy `costo_y_retorno.py` resuelve las dos así: por salto, y 20,00 SMLMV exacto paga 1%. **Si cambia:** mueve el costo mensual de quien cotiza por encima de 16 SMLMV, caso poco frecuente pero de alta disposición a pagar. En 20 SMLMV la diferencia entre las dos lecturas es de unos $70.000 mensuales.

## 4. Base única para salud y pensión

**No se puede cotizar a pensión sobre una base alta y a salud sobre el mínimo.** Es la pregunta que hace de forma natural quien quiere subir su base pensional sin pagar más salud, y la respuesta es no.

**Sustento normativo, en tres capas:**

1. **La ley habla de un solo sistema.** El art. 89 de la Ley 2277 de 2022 fija la base mínima del 40% para los aportes al **Sistema de Seguridad Social Integral**, que comprende salud y pensiones, no para uno de los dos por separado.
2. **El art. 204 de la Ley 100 remite a la base de pensiones.** Su parágrafo 1 dice, literal: "La base de cotización de las personas vinculadas mediante contrato de trabajo o como servidores públicos, afiliados obligatorios al Sistema General de Seguridad Social en Salud, **será la misma contemplada en el sistema general de pensiones de esta Ley**". La remisión es expresa. *Fuente: Secretaría del Senado, texto compilado del art. 204.*
3. **La UGPP fiscaliza sobre esa base única.** Su competencia es la determinación de aportes al Sistema de la Protección Social como un todo, y una diferencia entre la base de salud y la de pensión de un mismo aportante es precisamente lo que dispara el proceso de determinación (`independientes.md` sección 5).

**Consecuencia práctica que el agente debe decir de entrada:** subir la base pensional cuesta 28,5 centavos por peso, no 16. Quien evalúa la palanca de "subir la base" y solo tiene en la cabeza el 16% subestima el costo casi a la mitad. Es el número que faltaba en la demo.

`[VERIFICAR]` **Respuesta operativa:** base única, sin excepción, y el costo se cotiza al 28,5% o más. **Falta confirmar:** el texto literal del art. 89 de la Ley 2277 de 2022 en Secretaría del Senado (hoy se apoya en el propio `independientes.md` sección 2 y en la remisión expresa del parágrafo 1 del art. 204, que sí se leyó en primaria pero está redactado para trabajadores y servidores públicos, no para independientes); y si el **parágrafo 3 del art. 204** sigue operando, porque dice que "cuando se devenguen mensualmente más de 20 salarios mínimos legales vigentes, la base de cotización podrá ser limitada a dicho monto por el Consejo Nacional de Seguridad Social en Salud", un órgano que ya no existe con esas funciones. **Si cambia:** el techo de salud podría ser 20 SMLMV mientras el de pensión es 25, y entonces la base dejaría de ser única en el tramo más alto. Hoy `costo_y_retorno.py` aplica 12,5% de salud hasta 25 SMLMV, que es el supuesto conservador (cobra de más, no de menos). Afecta solo a quien cotiza por encima de 20 SMLMV.

## 5. Qué NO paga el independiente, y por qué

El usuario suele traer en la cabeza la nómina completa de un empleado. Separar lo que no aplica evita inflar el costo de la decisión y es una fuente barata de credibilidad.

| Concepto | ¿Aplica al independiente? | Por qué |
|---|---|---|
| ARL (riesgos laborales) | **Voluntaria** para el rentista de capital y el independiente por cuenta propia. Obligatoria solo para el contratista cuya actividad sea de riesgo IV o V | La afiliación obligatoria está atada al riesgo de la actividad contratada, no a la condición de independiente |
| Caja de compensación familiar | **Voluntaria** | El independiente puede afiliarse para acceder a subsidio, recreación y crédito, pero no es requisito de la cotización a pensión |
| SENA e ICBF (parafiscales) | **No aplican** | Son aportes **a cargo del empleador** sobre su nómina. Sin nómina no hay hecho generador. El independiente no es empleador de sí mismo |

**Regla de producto:** ARL y caja **quedan fuera del cálculo** de `costo_y_retorno.py` a propósito. Meterlas dentro inflaría el costo de la decisión que el usuario está evaluando, que es cotizar a pensión. Si el producto llega a mostrarlas, van como línea aparte y etiquetada como opcional, nunca dentro del aporte obligatorio.

`[VERIFICAR]` **Respuesta operativa:** el agente dice que ARL y caja son voluntarias para el rentista de capital y el independiente por cuenta propia, y que SENA e ICBF no aplican. **Falta confirmar:** el artículo exacto que fija la obligatoriedad de ARL para contratistas de riesgo IV y V (se atribuye al Decreto 723 de 2013, incorporado al Decreto 1072 de 2015, sin texto leído en primaria) y si un contratista de riesgo bajo puede quedar excluido por la entidad contratante. **Si cambia:** solo afecta al contratista de actividad riesgosa, que hoy queda fuera de alcance; para el rentista de capital, que es el perfil central de este documento, no cambia nada.

## 6. Costo total por tipo de independiente

Los tres tipos están definidos en `independientes.md` sección 1 y no se redefinen aquí. Lo que cambia entre ellos **no es la tarifa, es la base**: los tres pagan 28,5% o más, sobre bases calculadas distinto.

| Tipo | Cómo se llega al IBC | Qué mira el agente antes de dar una cifra |
|---|---|---|
| Contratista de prestación de servicios | 40% del valor mensualizado del contrato, sin IVA | El valor del contrato y si hay IVA incluido |
| Independiente por cuenta propia | 40% de los ingresos **después de costos** | Si usa costos reales (art. 107 ET) o presunción UGPP, porque cambia la base |
| Rentista de capital | 40% de los ingresos **después de costos**, con dividendos y participaciones **incluidos** en la presunción del 28,08% | Si sus costos reales superan el 28,08% del bruto, porque solo entonces le sirve soportarlos |

**Órdenes de magnitud para 2026** (SMLMV de $1.750.905; cifras producidas por `calculadora/costo_y_retorno.py`, no calculadas por el agente):

| IBC | Pensión 16% | FSP | Salud 12,5% | Costo mensual |
|---|---|---|---|---|
| 1 SMLMV ($1.750.905) | $280.145 | $0 | $218.863 | **$499.008** |
| 2 SMLMV ($3.501.810) | $560.290 | $0 | $437.726 | **$998.016** |
| 4 SMLMV ($7.003.620) | $1.120.579 | $70.036 | $875.452 | **$2.066.068** |
| 10 SMLMV ($17.509.050) | $2.801.448 | $175.090 | $2.188.631 | **$5.165.170** |
| 25 SMLMV ($43.772.625) | $7.003.620 | $875.452 | $5.471.578 | **$13.350.651** |

**El salto en 4 SMLMV es visible y hay que anunciarlo.** Pasar de un IBC de 3,9 a 4,0 SMLMV agrega un punto porcentual completo sobre toda la base, no sobre el excedente. Quien está justo debajo del umbral y va a subir su base merece saberlo antes, no después del primer pago.

**Ejemplo encadenado con la regla del 40%**, para un rentista con $12.000.000 mensuales de ingreso neto de costos: IBC = $4.800.000 (2,74 SMLMV), costo mensual = **$1.368.000**. No paga Fondo de Solidaridad porque su IBC, no su ingreso, es lo que se mide contra los 4 SMLMV. Es la confusión más cara del segmento: el umbral se mide sobre la **base**, no sobre lo que la persona gana.

## 7. Cómo entrega esto el agente

1. **Nunca da el 16% solo.** Toda cifra de "cuánto me cuesta cotizar" sale con salud incluida. Dar 16% es subestimar el costo en un 44%.
2. **El número lo produce la calculadora.** El agente pide el ingreso, deja que `costo_y_retorno.py` produzca la tabla de escenarios etiquetados, y explica. No multiplica.
3. **El costo va siempre contra el retorno.** El costo mensual solo, sin la mesada que compra ni el punto de recuperación, es un número que asusta y no decide nada. La tabla de escenarios del módulo trae las dos columnas por diseño.
4. **Los supuestos viajan con la cifra.** Pesos de hoy, sin inflación, base única, ARL y caja fuera, breakeven sin descuento. Están en `SUPUESTOS_DECLARADOS` del módulo.
5. **Verificar accionabilidad antes de ofrecer.** Ofrecer "sube tu base" a quien ya cotiza sobre lo que le corresponde es ruido (`independientes.md` sección 7, punto 5).

## 8. Fuera de alcance V1

- Liquidación exacta de PILA: intereses de mora, planillas, novedades.
- Tarifas de ARL por clase de riesgo y aporte a caja de compensación.
- Independiente con **ingresos simultáneos** de varias fuentes o con relación laboral y contrato a la vez: los IBC se suman hasta el techo de 25 SMLMV, pero la liquidación exacta no está implementada (caso-04 del set dorado).
- Aportes de colombianos residentes en el exterior.
- Tratamiento tributario del aporte (deducibilidad, renta exenta): está en `tributario-pensional.md`, no aquí.
