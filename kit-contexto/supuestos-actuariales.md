# Supuestos actuariales - Documento 7 del kit

> **Última actualización:** 2026-07-16. **Estado:** series clave verificadas contra fuentes oficiales o contra los casos reales del set dorado; marcas `[VERIFICAR]` para lo pendiente de confirmar antes del piloto.
> **Principio rector:** toda proyección muestra sus supuestos y entrega **rangos**, nunca un número mágico ("tu pensión estaría entre $A y $B").

## 1. Serie histórica: SMLMV (salario mínimo)

Necesaria para: expresar el IBL en salarios mínimos (tasa de reemplazo), validar IBC contra el mínimo, y proyectar pensión mínima.

| Año | SMLMV | Año | SMLMV |
|---|---|---|---|
| 2010 | $515.000 | 2019 | $828.116 |
| 2011 | $535.600 | 2020 | $877.803 |
| 2012 | $566.700 | 2021 | $908.526 |
| 2013 | $589.500 | 2022 | $1.000.000 |
| 2014 | $616.000 | 2023 | $1.160.000 |
| 2015 | $644.350 | 2024 | $1.300.000 |
| 2016 | $689.455 | 2025 | $1.423.500 |
| 2017 | $737.717 | 2026 | $1.750.905 |
| 2018 | $781.242 | | |

*Fuentes: decretos anuales de salario mínimo; 2026 confirmado por Decretos 1469 y 1470 de 2025 (+23% nominal). Chequeo cruzado con los casos reales: los IBC de salario mínimo de 2021 ($908.526), 2025 ($1.423.500) y 2026 ($1.750.905) en las historias laborales coinciden con la serie.*

**Serie 1992-2009 ya cargada en la calculadora** (`datos_sistema.py`), cotejada en dos fuentes secundarias que citan los decretos.

`[VERIFICAR]` **Respuesta operativa:** la calculadora usa la serie tal como está y el agente entrega las cifras sin advertencia especial, porque **la serie ya tiene una verificación cruzada mejor que una fuente secundaria**: los IBC de salario mínimo que aparecen en las historias laborales reales del set dorado (2021, 2025 y 2026) coinciden con ella. Un error en la serie se habría visto ahí. **Falta confirmar:** el cotejo formal año por año de 1992 a 2009 contra el archivo del Banco de la República o los decretos originales. **Si cambia:** un salario mínimo mal cargado de un año viejo desplaza el IBL indexado de quien cotizó ese año. El efecto es acotado (un año dentro de una ventana de diez) salvo error grande. **Prioridad:** baja frente a las marcas del actuario, pero **es tarea de una tarde y no necesita abogado**: la agrupamos con el cotejo del IPC de abajo.

## 2. Serie histórica: IPC anual (diciembre a diciembre)

Necesaria para: indexar los IBC al calcular el IBL (Ley 100 art. 21) y actualizar la indemnización sustitutiva.

| Año | IPC | Año | IPC |
|---|---|---|---|
| 2015 | 6,77% | 2021 | 5,62% |
| 2016 | 5,75% | 2022 | 13,12% |
| 2017 | 4,09% | 2023 | 9,28% |
| 2018 | 3,18% | 2024 | 5,20% |
| 2019 | 3,80% | 2025 | 5,10% |
| 2020 | 1,61% | | |

*Fuente: DANE (2025 confirmado: boletín IPC diciembre 2025, publicado enero 2026).*

**Serie 1993-2014 ya cargada en la calculadora** (`datos_sistema.py`), cotejada en dos fuentes secundarias que citan al DANE. Con ella el IBL de "toda la vida" ya calcula para historias desde 1993 (verificado con caso-04).

`[VERIFICAR]` **Respuesta operativa:** igual que con el salario mínimo, la calculadora usa la serie y entrega cifras. Los años 2015 a 2025 de la tabla de arriba **sí** están contra boletín del DANE; lo que falta cotejar es el tramo 1993-2014, cargado desde fuentes secundarias que citan al DANE. **Falta confirmar:** ese tramo contra el archivo oficial del DANE. **Si cambia:** el IPC solo entra en el IBL de Colpensiones, para indexar salarios viejos a pesos de hoy. Un error acumulado en años lejanos afecta sobre todo el cálculo de "toda la vida laboral" de quien tiene 1.250 semanas o más, que es justo la gente cerca de pensionarse. **Regla dura que ya está implementada y no depende de esta marca:** si falta el IPC de un año, `calcular_ibl` **devuelve error en vez de inventar el dato**. Es decir, el riesgo aquí es de dato equivocado, nunca de dato inventado. **Se agrupa con el cotejo del salario mínimo: misma tarde, mismo responsable, sin abogado.**

## 3. Supuestos de proyección (escenario base y rango)

| Supuesto | Base | Rango | Justificación |
|---|---|---|---|
| Inflación futura | 3,5% | 3,0% - 5,0% | Meta del Banco de la República 3%; promedio reciente por encima |
| Crecimiento real del SMLMV | +1,5% anual | +0,5% - +2,5% | Promedio histórico de largo plazo. Nota: 2026 fue atípico (+17% real); usarlo como tendencia inflaría las proyecciones |
| Crecimiento salarial individual | IPC (0% real) | 0% - +1,5% real | Conservador; el usuario puede ajustarlo en el chat ("¿y si me suben el sueldo?") |
| Rendimiento real fondos RAIS: conservador | +2,0% | +1% - +3% | Ver la marca de abajo |
| Rendimiento real fondos RAIS: moderado | +4,0% | +2,5% - +5,5% | Ver la marca de abajo |
| Rendimiento real fondos RAIS: mayor riesgo | +5,0% | +3% - +7% | Ver la marca de abajo |
| Densidad de cotización futura | La observada en los últimos 3 años del usuario | Ajustable | Se calcula del propio historial; el usuario puede cambiarla en el chat |

`[VERIFICAR]` **Rendimientos reales por tipo de fondo. Respuesta operativa:** el agente sigue usando 2% / 4% / 5% real, **siempre como rango y nunca como punto**, y explicando que el rendimiento es un supuesto y no una promesa. Son cifras de largo plazo, que es el horizonte correcto: una proyección a 30 años no se calibra con el último trimestre. **Falta confirmar:** la serie histórica **real** (deflactada por IPC) por tipo de fondo desde que existen los multifondos. La investigación del 2026-07-26 no pudo abrirla: la Superfinanciera la publica en un tablero de Power BI que las herramientas automatizadas no leen. Lo único que se obtuvo son rentabilidades **nominales** puntuales a marzo de 2025 (conservador 5,87%, moderado 4,16%, mayor riesgo 7,25%), que con inflación de ~5% dejarían rendimientos reales bastante más bajos ese trimestre, y una comparación OCDE citada por prensa con 3,8% a 15 años y 4,8% a 20 años. **Si cambia:** es el supuesto que más mueve las cifras del RAIS. Bajar el moderado de 4% a 3% real recorta la mesada proyectada de un joven de forma sustancial. **Cómo se cierra:** alguien con navegador tiene que entrar al tablero de la Superfinanciera y bajar la serie por tipo de fondo. Es la tarea más barata y de mayor impacto de esta lista, y no necesita abogado: necesita 20 minutos.

## 4. Parámetros del sistema (para la calculadora)

| Parámetro | Valor | Fuente / estado |
|---|---|---|
| Distribución del 16% en RAIS | 11,5% cuenta individual + 1,5% Fondo de Garantía de Pensión Mínima + 3,0% comisión y seguros | Ley 797/2003 art. 7 y reglamentación posterior; ver marca 1 |
| Distribución del 16% en RPM | 13% fondo común + 3% administración | Ley 797/2003 art. 7 y reglamentación posterior; ver marca 1 |
| Mesadas al año | 13 | Acto Legislativo 01 de 2005 |
| Interés técnico renta vitalicia | 4% real | Circular Básica Jurídica de la SFC; ver marca 2 |
| Tablas de mortalidad | Rentistas RV08 (Res. 1555/2010 SFC): expectativa residual **exacta**, mujer 57: **29,7 años**; hombre 62: **21,3 años** | Verificado 2026-07-27, ver marca 3 |
| Conversión capital a mesada (V1) | Factor actuarial simplificado por edad y sexo, documentado y visible | Aproximación V1; se refina con el actuario |

**Marca 1.** `[VERIFICAR]` **Distribución del 16%. Respuesta operativa:** el agente usa el desglose de la tabla (RAIS 11,5 / 1,5 / 3,0; RPM 13 / 3) y así lo explica cuando el usuario pregunta "¿a dónde se va mi plata?". Es el desglose que publican las AFP y el que usa la calculadora. **Falta confirmar:** el **decreto reglamentario exacto** que fija hoy ese reparto. El art. 7 de la Ley 797 de 2003 no lo trae literal: fija la tasa base en 13,5% (RAIS: 10% cuenta, 0,5% Fondo de Garantía, 3% administración), ordena los incrementos de 2004 a 2006 y un punto más desde 2008 **condicionado a que el PIB creciera 4% o más en promedio los dos años anteriores**, y **delega en el Gobierno la redistribución quinquenal** entre el Fondo de Garantía y la cuenta individual. La condición del PIB sí se cumplió y la cotización llegó al 16% en 2008 (Decreto 4982 de 2007), pero el decreto que fija el reparto final 11,5 / 1,5 / 3 no se leyó en fuente primaria. **Si cambia:** cada décima que se mueva entre la cuenta individual y el Fondo de Garantía cambia el saldo proyectado de **todos** los diagnósticos RAIS. Es el parámetro con más alcance de esta tabla, aunque el rango de error plausible sea estrecho.

**Marca 2.** `[VERIFICAR]` **Interés técnico del 4%. Respuesta operativa:** la calculadora lo sigue usando y el agente lo declara como supuesto. **Falta confirmar dos cosas distintas, y no hay que mezclarlas:** (a) la ubicación exacta del numeral en la Circular Básica Jurídica, que la Superfinanciera **reexpidió en 2025** y pudo haber reordenado (la referencia del kit, Parte II Título III Capítulo I numeral 2, no se pudo confirmar contra el texto vigente); y (b) algo más de fondo, que **el 4% es la tasa de reserva del sistema, no el precio de mercado de una renta vitalicia**. Ese segundo punto no es una marca de kit sino el riesgo abierto más serio del proyecto y está desarrollado en `ESTADO.md`. **Si cambia:** mueve todas las mesadas RAIS y, sobre todo, la edad de pensión anticipada, que es el mensaje estrella del producto. **Va al actuario, no al abogado.**

**Marca 3. CERRADA el 2026-07-27: valores exactos de la RV08.** Se descargó y leyó la tabla oficial completa de la *Resolución 1555 de 2010 de la Superintendencia Financiera* (rentistas válidos, experiencia 2005-2008), vía el PDF publicado por Fasecolda. **Confianza: ALTA** (tabla oficial abierta y leída directamente, no fuente secundaria).

| Edad | Hombres, expectativa residual | Mujeres, expectativa residual |
|---|---|---|
| 55 | 27,2 años | 31,6 años |
| 57 | 25,5 años | **29,7 años** |
| 60 | 23,0 años | 27,0 años |
| 62 | **21,3 años** | 25,3 años |
| 65 | 19,0 años | 22,7 años |

**Qué cambió frente a lo que el kit traía:** nada material. Los aproximados que se venían usando (mujer 57 ~ 29, hombre 62 ~ 21) resultaron correctos y ahora tienen respaldo exacto y citable. La diferencia (0,7 y 0,3 años) mueve el factor de conversión menos de un 2,5%, dentro del ruido que ya introduce la marca 2.

**Lo que sigue abierto y NO lo cierra este dato:** la Resolución 1555 de 2010 continúa vigente (la investigación no encontró resolución posterior que la reemplace), pero **si la Superfinanciera la actualiza, cambia por resolución y no por ley**, así que no aparece en el radar del Congreso ni de la Corte. Sigue en la lista del actuario como pregunta de vigilancia, no como dato faltante.

**No confundir** esta tabla con la RV08 de inválidos ni con las tablas de mortalidad de la población general del DANE: son poblaciones distintas y usarlas cruzadas daría un factor equivocado.

## 5. Reglas de presentación de resultados

1. Toda cifra proyectada se presenta **en pesos de hoy** (poder adquisitivo actual), con nota de que la mesada nominal futura será mayor.
2. Siempre **rango** (escenario base entre pesimista y optimista variando los supuestos de la sección 3).
3. Los supuestos usados se listan al pie de cada diagnóstico y del informe PDF. **Además (Santiago 2026-07-21), toda cifra proyectada declara junto a ella sus tres supuestos con el valor real del caso**: sobre cuánto cotiza (`ibc_actual`), con qué continuidad (`densidad_ultimos_3_anios`) y hasta cuándo. Un genérico tipo "asumiendo que sigues cotizando como hoy" no cumple: el usuario no puede juzgar ni discutir la cifra. Redacción y ejemplos en `system-prompt.md` > "Supuestos de toda proyección".
4. Ninguna proyección se presenta como promesa: es una estimación bajo la ley vigente y los supuestos declarados.
5. **No imitamos a los simuladores oficiales** (validado con Santiago 2026-07-18): la simulación base es el **valor esperado más realista posible** con supuestos visibles, y después el usuario puede **jugar con sus propios supuestos** en el chat. (Contraste: los simuladores oficiales esconden los suyos; Protección muestra sus rentabilidades "en $0".)
6. **Las preguntas de proyección se hacen en términos de vida real**, no de parámetros: la densidad futura no se pregunta como "¿cotizarás 6 de 12 meses?" sino como "**de los N años que te quedan hasta la edad de pensión, ¿cuántos crees que vas a cotizar?**" (la calculadora la convierte internamente en densidad).
7. **La pensión anticipada (RAIS, art. 64) se muestra siempre que aplique**: la edad en la que el saldo financiaría el 110% del mínimo es de las variables más poderosas y menos conocidas (ya implementada en `rais.py`).

## 6. Pendientes de verificación (antes del piloto)

- [ ] Series IPC y SMLMV completas contra DANE y Banco de la República (cargar como archivo de datos de la calculadora).
- [ ] Rendimientos históricos reales por tipo de fondo (Superfinanciera).
- [ ] Distribución exacta de la cotización del 16% en cada régimen.
- [ ] Interés técnico y tablas de mortalidad vigentes para renta vitalicia.
- [ ] Revisión integral por abogado pensional o actuario (gasto único definido en la definición conceptual).
