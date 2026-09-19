# Calculadora de Júbilo (V0)

> **Última actualización:** 2026-07-27 (módulo `costo_y_retorno.py` nuevo). La regla de arquitectura: **la IA nunca calcula**; todo número sale de este código fijo, que implementa las reglas del kit (`../kit-contexto/`) tal cual están escritas.

## Archivos

| Archivo | Qué hace |
|---|---|
| `datos_sistema.py` | Datos verificados: SMLMV 1992-2026, IPC 1993-2025, tabla C-197, parámetros RPM y RAIS |
| `rpm.py` | Diagnóstico Colpensiones: semanas, requisitos, IBL indexado, tasa de reemplazo, escenarios |
| `rais.py` | Diagnóstico fondos privados: proyección de saldo, 3 salidas (capital / GPM / devolución), pensión anticipada |
| `comparador.py` | El mismo caso por ambos módulos con supuestos iguales + ventana de traslado |
| `lagunas.py` | Dónde están los huecos: vacíos (meses que nadie reportó), déficit por tramo (semanas que faltaron dentro de un rango) y filas con salario y cero semanas |
| `recuperacion.py` | Qué le pasa al número si esas semanas se recuperan. Separa lo que ya está contado, lo estimable y lo que no se puede estimar |
| `costo_y_retorno.py` | Cuánto cuesta cotizar y en cuánto tiempo se recupera: aporte mensual, costo total, mesada neta, breakeven y ganancia neta, como tabla de escenarios etiquetados |
| `router.py` | Primera capa: qué módulo corre, señales de exceptuados, datos faltantes, alertas |
| **`diagnosticar.py`** | **La puerta de entrada. Encadena todo: verificación cruzada -> router -> rpm/rais -> comparador. Es lo que corre el agente; los demás módulos no se llaman sueltos** |
| `probar_*.py` | Pruebas de cada pieza contra el set dorado (`../casos/`) |

## Cómo correr las pruebas

```bash
python3 probar_diagnosticar.py  # El flujo completo + los 2 casos negativos
python3 probar_rpm.py         # Casos 04 y 05 (Colpensiones)
python3 probar_rais.py        # Casos 01, 02 y 03 (fondos privados)
python3 probar_comparador.py  # Los 5 casos por ambos regímenes
python3 probar_router.py      # Clasificación y alertas de los 5 + 1 sintético
python3 probar_lagunas.py     # Huecos: set dorado + números esperados a mano
python3 probar_recuperacion.py # Qué se puede recuperar y qué no se estima
python3 probar_costo_y_retorno.py # Costo de cotizar, breakeven y el caso de validación a mano
```

Correr las ocho después de cualquier cambio. Las semanas de cada caso deben CUADRAR contra el total impreso del documento (tolerancia 0,15).

**`probar_lagunas.py`, `probar_recuperacion.py`, `probar_costo_y_retorno.py` y la sección de regresión de `probar_rais.py` terminan en código de salida 1 si algo falla**, así que sirven para automatizar. Las otras cuatro imprimen para lectura humana. `probar_lagunas.py` es además la primera prueba con **números esperados calculados a mano sobre el documento** (pendiente 2 de la sesión del 2026-07-26): una prueba que solo verifica que el flujo corre no detecta un cálculo malo.

## El módulo de lagunas

Responde "¿dónde están mis huecos?", que hasta el 2026-07-26 el agente contestaba comparando rangos a mano. Devuelve tres bloques que no se solapan:

| Bloque | Qué es | Precisión |
|---|---|---|
| `vacios` | Meses que **ningún** aportante reportó | Fecha exacta de inicio y fin |
| `tramos_con_deficit` | Dentro de un rango sí reportado, cuántas semanas faltaron frente a las que cabían | **Cuántos** meses faltan, no **cuáles** |
| `filas_ibc_sin_semanas` | Aportante con salario reportado y cero semanas acreditadas, sin marca de simultaneidad | Lista de filas |

**Dos decisiones de diseño que no se deben revertir:**

1. **Un mes completo son 30 días, no los días calendario.** Es la convención del sistema pensional y la del resto de la calculadora. Un tramo de 13 meses "cabe" 390 días (55,71 semanas), no 396. Con días calendario el déficit del caso real daba 9,43 semanas; con la convención correcta da 8,57, que son exactamente 2 meses.
2. **El déficit total NO es la suma de los tramos.** Dos filas pueden cubrir el mismo mes (dos aportantes, un pago partido) y ese mes se contaría dos veces. `deficit_de_tramos_semanas` lo mide una sola vez por mes, sobre el mapa mensual, que ya topa los días en 30 por simultaneidad. Sin eso, el módulo inventaría déficits donde hubo simultaneidad legítima.

**Límite del formato que el módulo respeta:** Colpensiones agrupa por tramos con el mismo salario, así que el detalle mes a mes no existe en el documento. El módulo dice cuántos meses faltan; el mes exacto está en PILA. Regla de comportamiento correspondiente en `../kit-contexto/system-prompt.md` > "Los huecos y su recuperación salen de la calculadora".

### Cuándo alerta el router (no hay umbral de tamaño)

La primera versión alertaba a partir de 26 semanas perdidas, un número elegido a ojo. Un umbral absoluto trata igual dos casos opuestos: 30 semanas repartidas en 20 años (ruido) y 30 semanas en alguien a quien le faltan 20 para pensionarse (decisivo). Ahora son dos pruebas de relevancia, independientes entre sí:

| Alerta | Cuándo se levanta | Por qué importa |
|---|---|---|
| `lagunas_recientes` | Se perdió al menos un mes dentro de los últimos 3 años cubiertos por el documento | Es la ventana con la que `rpm.py` y `rais.py` proyectan **toda** la pensión. Un hueco ahí no es historia, es un supuesto vivo |
| `lagunas_decisivas` | Lo perdido en huecos alcanza o supera lo que le falta para su requisito | Recuperar deja de ser un detalle y pasa a ser su palanca más grande |
| `ibc_sin_semanas` | Siempre que aparezca una fila del cuarto estado | No depende de tamaños: es un estado sin clasificar |

La ventana reciente se recorta contra el documento **por los dos lados**: quien se afilió hace un mes no tiene tres años de huecos, tiene un mes de historia. Sin ese recorte el módulo le inventaría un problema a todo afiliado nuevo.

`lagunas_decisivas` necesita el requisito de semanas, que el router calcula según el régimen (vejez en RPM, garantía de pensión mínima en RAIS). **Si no se conoce, la prueba no corre y no se inventa un resultado.**

## El módulo de recuperación

Responde la pregunta que sigue siempre a "¿dónde están mis huecos?": **"¿y cuánto me sube la pensión si los recupero?"**. No usa fórmulas nuevas: arma una copia del caso con las semanas acreditadas y vuelve a correr el mismo módulo del régimen, así el efecto sobre el IBL, sobre los bloques de 50 semanas y sobre la fecha sale de código ya probado.

**La tabla que organiza todo,** y que existe porque la intuición falla en las tres filas:

| Grupo | ¿Ya está contado? | ¿Se puede estimar la mesada? |
|---|---|---|
| Mora o deuda presunta que el documento acredita | **Sí, ya está en el total impreso** | No hay nada que ganar. Lo que hay es un **riesgo a la baja** si no se la convalidan |
| Filas con salario reportado y cero semanas | No | **Sí**: hay salario y hay periodo |
| Vacíos y déficit de tramos | No | **No**: sin salario reportado no hay con qué calcular |

**Tres cosas que el módulo hace y una suma a ojo no haría:**

1. **Solo promete los días LIBRES del mes.** En el caso real, de las 3 filas pendientes solo una agrega semanas: en abril y mayo el afiliado ya había cotizado 30 días por su cuenta, así que acreditar la fila de la temporal no le suma nada. Eran simultaneidad. A ojo se habrían prometido 12,86 semanas en vez de 4,29.
2. **Detecta cuando recuperar BAJA la mesada.** El mes recuperable se cotizó sobre $641.999, muy por debajo de su IBL de $3.001.446. Acreditarlo sube el conteo y **baja la mesada un 0,65%**. El módulo levanta una `advertencia` explícita: sirve para llegar al requisito de semanas, no para subir el monto.
3. **Se niega a estimar lo que no puede.** Las 516,86 semanas de vacíos se reportan en semanas y sin ningún monto.

**Precisión declarada:** en documentos que agrupan por tramos, saber cuántos días tiene libres un mes concreto depende de en qué meses del rango se cotizó, y eso el documento no lo dice. El campo `precision_de_los_dias_libres` lo declara como aproximado. El total de semanas no cambia; su reparto entre meses sí.

## Cómo se corre un diagnóstico

```bash
python3 diagnosticar.py ../casos/caso-03-proteccion-rais.json --sexo M --edad 26
python3 diagnosticar.py caso.json --json    # salida completa para máquina
python3 diagnosticar.py caso.json --ibc-futuro 8000000 --densidad-futura 1.0
```

`--sexo` y `--edad` solo si el documento no los trae. **Si la verificación cruzada falla, el programa se detiene, no imprime diagnóstico y termina con código 1**: es la regla dura 4 del kit, no un error a rodear.

## Análisis de sensibilidad: `--ibc-futuro` y `--densidad-futura`

Son los dos supuestos del escenario "sigue cotizando" y **funcionan en los dos regímenes y en el comparador** (RAIS quedó cubierto el 2026-07-26; antes solo aplicaban a RPM).

| Flag | Qué cambia | Dónde pega |
|---|---|---|
| `--ibc-futuro` | Salario sobre el que cotizaría de aquí en adelante, **en pesos de hoy** | RPM: entra al IBL de los 10 años anteriores a la pensión. RAIS: sube el aporte mensual del 11,5% a la cuenta |
| `--densidad-futura` | Ritmo de cotización futuro, de 0 a 1 (1 = todos los meses) | RPM: fecha en que completa semanas + IBL. RAIS: aporte mensual + semanas para la garantía de pensión mínima |

En RAIS mueven también la **edad de pensión anticipada**, que es el mensaje estrella del producto: en el caso-01 pasa de los 58 a los 51 años al subir el IBC a $8.000.000 con densidad 1,0.

Sin los flags, cada supuesto sale del propio historial: el salario del último mes con cotización real y el ritmo de los últimos 3 años. Los dos valores usados quedan en la salida (`ibc_futuro_supuesto`, `densidad_futura_supuesta`), para que ninguna cifra viaje sin sus supuestos al lado.

## El módulo de costo y retorno (2026-07-27)

Responde la pregunta que el diagnóstico deja abierta. El diagnóstico dice **cuánta pensión te queda**; la decisión real del usuario es **si vale la pena pagar eso**. Hasta el 2026-07-27 ese número se calculaba en scripts temporales fuera del repositorio y sin pruebas (pendiente 4 de `../ESTADO.md`): la regla dura 1 se cumplía en la letra y se rompía en el espíritu, porque la mitad de la tabla que veía el usuario no la verificaba nadie.

**Qué calcula, con su norma:**

| Componente | Tasa | Fuente |
|---|---|---|
| Aporte a pensión | 16% del IBC | Ley 100 art. 20, mod. Ley 797 de 2003 art. 7 |
| Salud del cotizante | 12,5% del IBC | Ley 100 art. 204, mod. Ley 1122 de 2007 art. 10 |
| Fondo de Solidaridad, subcuenta de solidaridad | +1% desde 4 SMLMV | Ley 100 art. 27, mod. Ley 797 de 2003 art. 8 |
| Fondo de Solidaridad, subcuenta de subsistencia | +0,2% por tramo de 16 a 20 SMLMV, plano en 1% por encima de 20 | Ley 100 art. 27, mod. Ley 797 de 2003 art. 8 |
| Salud del pensionado | 4 / 10 / 12% por tramo de mesada | `../kit-contexto/vida-del-pensionado.md` s.4 |

Sobre eso entrega **costo total** hasta la fecha de pensión, **mesada bruta y neta** con 13 mesadas al año, **breakeven en meses** y **ganancia neta** a un horizonte parametrizable (21 años por defecto).

**Dos reglas que el módulo hace cumplir por construcción:**

1. **La base de salud y la de pensión son la misma.** No se puede cotizar a pensión sobre una base alta y a salud sobre el mínimo (criterio UGPP: el IBC es único para el sistema de seguridad social integral). Quien pregunta "¿cuánto me cuesta subir la base?" está preguntando por 28,5 puntos, no por 16.
2. **El escalonado del Fondo de Solidaridad se suma al 1%, no lo reemplaza**, y no llega a 25 SMLMV: se aplana en 1% adicional por encima de 20. Una versión vieja del kit insinuaba lo contrario.

**Forma de la salida: tabla de escenarios etiquetados** (decisión de producto del 2026-07-27, no reabrir). Cada fila se nombra por la decisión que la produce ("cotizar sobre 7.600.000", "cotizar sobre el mínimo") y trae su costo y su breakeven como **punto único**. La fila "sigues como hoy" es la base y las alternativas se comparan contra ella. **No es una banda de rango:** en RPM la fórmula es determinista, así que lo que varía no es incertidumbre del modelo sino una decisión del usuario, y un rango difuso comunicaría lo contrario.

```bash
python3 costo_y_retorno.py --ibc 7600000 --meses 34 --mesada 2722674
python3 costo_y_retorno.py --ibc 7600000 --meses 34 --mesada 2722674 \
  --alternativa "cotizar sobre el mínimo:1750905:34:1750905" --horizonte 21
```

La mesada bruta de cada fila **no la inventa este módulo**: entra desde `rpm.py` o desde el diagnóstico (`escenario_desde_diagnostico`), que toma el IBC y la mesada sin que nadie los teclee. Si el diagnóstico no trae datos devuelve `None` en vez de estimar, y un diagnóstico con error no produce fila.

**Caso de validación, verificado a mano y fijado en la prueba:** IBC 7.600.000, 34 meses de aporte, mesada bruta 2.722.674, que da aporte mensual 2.242.000, costo total 76.228.000, mesada neta 2.450.407, breakeven 28,7 meses y ganancia neta a 21 años 592.733.002.

**Supuestos que la salida declara siempre** (no se muestran cifras sin ellos): todo en pesos de hoy sin proyectar inflación; base única de salud y pensión; ARL y caja de compensación fuera, por ser voluntarias para el rentista de capital y el independiente por cuenta propia; escalonado del Fondo de Solidaridad aplicado por salto al cruzar el umbral (lectura literal de la tabla, pendiente de confirmar con el abogado si es proporcional dentro del tramo); breakeven nominal y sin descuento; 13 mesadas al año.

## Aproximaciones conocidas de V1 (documentadas también en el kit)

1. **Conversión capital a mesada (RAIS):** renta vitalicia sin beneficiarios de sobrevivencia; las mesadas RAIS altas pueden estar sobreestimadas. Prioridad 1 del actuario.
2. **IBL con rangos de Colpensiones:** el salario del rango es el último reportado (es lo único que trae el resumen).
3. **IBL proyectado para menores de (edad pensión - 10):** se usa el salario actual en términos reales, porque su IBL real se formará con salarios futuros.
4. **Saldo RAIS simulado** (en el comparador, para historias de Colpensiones): aportes del 11,5% capitalizados al rendimiento moderado; ignora bono pensional y comisiones históricas.
5. **Proyecciones en términos reales** (pesos de hoy): la mesada nominal futura será mayor.
6. **Horizonte de proyección RAIS sin fecha de nacimiento:** cuando el documento solo trae la edad en años (ej. Protección), los meses hasta la edad legal se cuentan en años enteros y quedan con un margen de hasta 12 meses. La salida lo declara con `horizonte_exacto: false`. Con la fecha de nacimiento el conteo es de fecha a fecha y el margen desaparece.
7. **Breakeven nominal (`costo_y_retorno.py`):** mide en cuántos meses de mesada se recupera lo aportado, sin descontar el rendimiento que esa misma plata habría dado invertida en otra parte. Es un punto de recuperación de caja, no un análisis de valor presente. Para el independiente con patrimonio, que es justo quien hace esta pregunta, el costo de oportunidad es real y hoy no está modelado.

> **Última revisión de sesgo de proyección:** 2026-07-26 (`rpm.py` el 26 en la mañana, `rais.py` el 26 en la tarde). Ver `../ESTADO.md`.

## La banda del factor de conversión (RAIS), aplicada el 2026-07-27

Cierra el riesgo abierto más serio del proyecto. Implementa las **decisiones 1 y 2 de Santiago** del 2026-07-27, que no se reabren.

**El problema en una frase.** Convertir un saldo en mesada exige un **precio** de renta vitalicia, y ese precio no está fijado por ninguna norma. La calculadora venía estimándolo con el **4% de interés técnico**, que es la tasa de **reserva** que la norma le exige al sistema, no lo que una aseguradora cobra por vender la renta. Son tres tasas distintas y usaba la que no es.

**Qué cambió.** Todo lo que depende del factor sale ahora en **banda de dos extremos**, nunca en punto único: la **mesada** de cada escenario, la **edad de pensión anticipada** y el **capital que exige el umbral del 110% del SMLMV** (Ley 100 art. 64).

| Extremo | Fuente | Confianza |
|---|---|---|
| Optimista, 4,00% real | Circular Básica Jurídica de la Superfinanciera, Parte II, Título III, Cap. I, num. 2 | **ALTA**, norma verificada el 2026-07-21 |
| Conservador, precio de mercado | Infobae, 14 de enero de 2026, citando el Decreto 1485 de 2025: capital que exige una renta vitalicia de un salario mínimo | **BAJA**, fuente secundaria, sin verificación primaria |

**Los dos extremos se declaran en la salida**, en la llave `banda_factor`: de dónde sale cada uno, su fuente, su confianza, por qué difieren, si le aplica el Decreto 1485 y qué tiene de inconsistente la fuente. El conservador dice explícitamente que su fuente **no es oficial**. La declaración viaja pegada a las cifras, no en un comentario del código.

### Cómo se construye el extremo conservador

Del capital que exige hoy una renta vitalicia de un salario mínimo se saca el **factor** dividiendo por el salario mínimo, y de ahí se despeja la **tasa real implícita** (`datos_sistema.tasa_implicita`), que es lo que permite aplicarlo a cualquier edad. Hacía falta una tasa y no un factor suelto porque la pensión anticipada compara edades muy distintas.

| Sexo | Capital 2026 | Factor | Capital 2027 (Decreto 1485) | Encarecimiento |
|---|---|---|---|---|
| Hombre | 470.000.000 | 268,4 | 537.000.000 | **14,3%** |
| Mujer | 504.000.000 | 287,9 | 581.000.000 | **15,3%** |

El factor del hombre (268,4) reproduce el ~268 que el proyecto venía citando desde el 2026-07-21. El de la mujer es un **ancla nueva**: antes se extrapolaba con la tasa implícita del hombre, que la castigaba de más.

**El "14%" que circula en prensa no se cita como dato oficial.** No aparece en el decreto ni en ningún documento oficial: es una cifra derivada por el medio a partir de estos capitales. Recalculada desde los capitales da **14,3% en hombres y 15,3% en mujeres**, no un 14% parejo, y así se usa.

**Dos supuestos declarados, no verificados:** la fuente **no dice a qué edad** corresponden esos capitales (se supone la edad legal de pensión de cada sexo, 62 y 57), y son cifras de prensa sobre una **mesada de un salario mínimo**.

### Inconsistencia de la fuente, pregunta para el actuario

Los dos capitales no se dejan reproducir con una sola tasa de descuento sobre las expectativas de vida que usa la calculadora: **la mujer vive 39% más que el hombre (29,7 contra 21,3 años) y su renta cuesta apenas 7% más**. Eso implica tasas implícitas muy distintas por sexo (cerca de 0,3% en hombres y 2,1% en mujeres) y sugiere que la fuente usa supuestos que no conocemos: otras edades, cobertura de beneficiarios u otra tabla de mortalidad. **Se usa el ancla de cada sexo**, que es lo más fiel al dato disponible, y la diferencia se declara en la salida en vez de promediarse en silencio. Va con la pregunta 4 de la lista del actuario.

### Decreto 1485 de 2025, aplicado según su alcance

Publicado el 31 de diciembre de 2025, vigente desde el 1 de enero de 2026, sustituye el Título 17 del Decreto 1833 de 2016. Obliga a las aseguradoras a proyectar el crecimiento anual de la mesada de las rentas vitalicias inmediata y diferida con el mayor valor entre la productividad promedio de los últimos 10 años y el 35% del IPC promedio de los últimos 10 años (datos de la Oficina de Bonos Pensionales del Ministerio de Hacienda), y elimina la cobertura completa del Estado sobre el componente político de los incrementos del salario mínimo. **Confianza: MEDIA**, confirmado en compilación oficial alterna (CER Latam sobre el texto de MinHacienda); el SUIN Juriscol falló por error de certificado, así que el texto literal crudo no se leyó.

**Alcance respetado en el código:** aplica a rentas vitalicias y pólizas **nuevas desde 2027**. Quien se pensione en 2026 compra al precio viejo y la calculadora no le aplica el encarecimiento. Como el año de pensión cambia con la edad, la pensión anticipada evalúa año por año cuál precio le toca.

### Cómo conviven la banda y los perfiles de fondo

Regla nueva, declarada en `rais.REGLA_BANDA_Y_PERFILES`. Son **dos rangos de naturaleza distinta y no se multiplican**. El perfil de fondo es una **decisión** del usuario sobre dónde está su plata; la banda del factor es **incertidumbre del modelo** sobre el precio de la renta. Regla operativa: **el perfil manda las filas y la banda manda las columnas**. Cada perfil trae sus dos extremos, y el rango que el agente comunica como "tu mesada" es el del perfil que le aplica al usuario, no el que va del piso del perfil conservador al techo del de mayor riesgo (eso sería una banda inútil de tan ancha). En la pensión anticipada y el umbral del 110%, donde hoy solo se calcula el perfil moderado, el rango mostrado es **solo** el del factor, y así se dice.

**Dónde muerde y dónde no.** La referencia de mercado se construyó sobre una mesada cercana a **1 SMLMV**, que es donde el precio se dispara porque esa mesada se reajusta con el salario mínimo, que sube más que el IPC. Para mesadas altas la validación contra el simulador de Protección dio +4,9% con el 4% normativo, así que ahí el precio real se parece más al extremo **optimista**. La banda se aplica igual en todas partes (decisión 2: si el factor es incierto, lo es en todas partes), y la asimetría se declara junto a las cifras.

**Compatibilidad, a propósito.** Las llaves sin apellido (`mesada`, `salida`, `edad_pension_anticipada`) siguen siendo el **extremo optimista**, exactamente lo que la calculadora daba antes del cambio. Ninguna cifra histórica del proyecto queda huérfana: todas son ahora el borde superior de la banda. Llaves nuevas: `mesada_conservadora`, `salida_conservadora`, `mesada_banda`, `edad_pension_anticipada_conservadora`, `edad_pension_anticipada_banda`, `capital_umbral_110_pct` y `banda_factor`.

### Efecto sobre el set dorado

Fecha de cálculo 2026-07-18, escenario moderado, pesos de hoy. Los seis casos se pensionan después de 2027, así que a todos les aplica el precio ya encarecido.

| Caso | Mesada, banda | Pensión anticipada | Lectura |
|---|---|---|---|
| caso-01 Porvenir | 1.750.905 a 2.666.551 | 58 años a **nunca** antes de los 62 | El extremo conservador le cambia la **salida**: de pensión por capital a garantía de pensión mínima |
| caso-02 Skandia | 1.750.905 a 1.750.905 | No aplica en ninguno | La banda no lo mueve: la GPM es un piso y absorbe los dos extremos |
| caso-03 Protección | 10.219.319 a 17.029.586 | **35 a 45 años** | El mensaje estrella del producto se vuelve un rango de 10 años |
| caso-04 Colpensiones | No aplica (RPM, sin saldo) | No aplica | El RPM es determinista, la banda no lo toca |
| caso-05 Colpensiones | No aplica (RPM, sin saldo) | No aplica | Igual que el 04 |
| caso-06 Colfondos | 139.789 a 232.945 | No aplica en ninguno | Sin sexo ni edad no es diagnosticable; cifras con supuesto (hombre, 40 años) solo para medir el efecto |

El umbral del 110% del SMLMV a los 62 años pasa de exigir **354.474.375** (norma) a **590.700.000** (mercado desde 2027).

### Regresión, en `probar_rais.py`, con código de salida 1

Fija que la banda existe en las tres salidas que dependen del factor, que el orden de los extremos nunca se invierte, que el extremo optimista coincide peso por peso con lo que la calculadora daba antes, que la declaración trae fuente y confianza en los dos extremos, que el factor de cada sexo sale del capital de la fuente y no de una cifra suelta, que el Decreto 1485 se aplica solo desde 2027, que el encarecimiento no se aplana en un 14% parejo, y que los dos rangos no se multiplican entre sí.

**Lo que sigue abierto:** el extremo conservador necesita fuente primaria y la inconsistencia entre las dos anclas por sexo necesita actuario (preguntas 2, 3 y 4 de la lista); el efecto de los **beneficiarios de sobrevivencia** sigue sin modelarse; y la **pensión anticipada se calcula solo en perfil moderado**, brecha anterior a este cambio.

## Segunda banda: el rendimiento por perfil de fondo, recalibrado a rango el 2026-07-27

Decisión de Santiago del 2026-07-27: los tres supuestos de rendimiento se recalibran **a rango, no a punto**.

**Por qué.** Los tres valores viejos quedaban fuera del rango observado por la Superfinanciera, y ni siquiera en la misma dirección.

| Perfil | Supuesto viejo | Rango observado | Punto central nuevo |
|---|---|---|---|
| Conservador | 2,00% (subestimaba) | 2,53% a 2,69% | **2,61%** |
| Moderado | 4,00% (por encima del techo) | 1,97% a 3,15% | **2,56%** |
| Mayor riesgo | 5,00% (sobreestimaba) | 2,88% a 4,25% | **3,56%** |

**Fuente:** Superintendencia Financiera, periodo marzo 2011 a octubre 2024, vía El Colombiano del 15 de enero de 2025. **Confianza MEDIA**, fuente secundaria que cita a la SFC; el dato crudo vive en un tablero de Power BI que no se puede extraer de forma automatizada, así que no se leyó el original.

**Qué significa este rango, y es lo que más importa:** es un rango **por administradora**, no una banda de riesgo de mercado. La distancia entre extremos no es cómo le puede ir al mercado, es **con cuál AFP está el usuario**. Es una palanca accionable, no una incertidumbre que le toque aguantar, y la salida lo dice con esas palabras. La calculadora aun así no recomienda administradora.

### Hallazgo que rompe un supuesto del producto

Con estos datos el punto central del perfil **moderado (2,56%) queda por debajo del conservador (2,61%)**: en el periodo observado el fondo moderado no le ganó al conservador. La calculadora **ya no asume que a más riesgo va más rendimiento**, y ninguna prueba exige que los tres perfiles vayan en orden creciente. Quien lea la tabla de escenarios verá al moderado por debajo del conservador y eso es el dato, no un error.

### Cómo conviven las dos bandas (la decisión de diseño, medida antes de tomarla)

El RAIS tiene ahora dos fuentes de rango. Multiplicarlas daba esto, medido sobre el caso-03:

| Perfil | Solo factor | Solo administradora | Envolvente de las dos |
|---|---|---|---|
| Conservador | x1,67 | x1,04 | x1,73 |
| Moderado | x1,67 | x1,30 | **x2,17** |
| Mayor riesgo | x1,67 | x1,37 | **x2,29** |

En el perfil moderado la envolvente va de 6,5 a 14,0 millones. **Un rango donde el techo es más del doble del piso no le permite decidir nada a nadie**, así que no se comunica.

**Regla adoptada, declarada en `rais.REGLA_DOS_BANDAS`:** las dos bandas **no se multiplican**.

1. La banda del **factor** es incertidumbre del modelo sobre el precio de la renta vitalicia. El usuario no puede hacer nada al respecto. Es la que se comunica como "tu mesada", y se calcula con el rendimiento **central** del perfil.
2. La banda del **rendimiento** es la diferencia entre administradoras. Va aparte, en `mesada_banda_afp`, presentada como "lo que pesa tu administradora", porque es accionable.
3. La **envolvente** se calcula y se guarda en `mesada_envolvente` para auditoría, marcada como no comunicable.

Es la misma lógica que ya separaba el perfil de fondo del factor: lo que el usuario **decide** va en un eje, lo que el modelo **no sabe** va en el otro.

### Efecto sobre el set dorado

Escenario moderado, fecha 2026-07-18. El "antes" es la banda del factor con el supuesto de rendimiento viejo.

| Caso | Antes | Ahora, banda del factor | Ahora, lo que pesa la AFP |
|---|---|---|---|
| caso-01 Porvenir | 1.750.905 a 2.666.551 | 1.750.905 a **1.945.612** | 1.750.905 a 2.209.514 |
| caso-02 Skandia | 1.750.905 a 1.750.905 | 1.750.905 a 1.750.905 | 1.750.905 a 1.750.905 |
| caso-03 Protección | 10.219.319 a 17.029.586 | **7.347.652** a **12.244.207** | 10.752.602 a 13.986.580 |
| caso-04 Colpensiones | No aplica (RPM) | No aplica | No aplica |
| caso-05 Colpensiones | No aplica (RPM) | No aplica | No aplica |
| caso-06 Colfondos | 139.789 a 232.945 | **105.791** a **176.291** | 157.315 a 197.596 |

Pensión anticipada: el caso-01 pasa de los 58 años a los **62** en el extremo optimista, o sea que deja de existir como mensaje. El caso-03 pasa de 35 a 45 a **36 a 47**.

**Lectura:** la recalibración baja las mesadas cerca de un 28% en los casos con saldo alto, y en el caso-01 borra la pensión anticipada. La calculadora venía siendo optimista por dos vías a la vez (precio de la renta y rendimiento del fondo), y las dos empujaban en la misma dirección.

### Regresión

`probar_rais.py` fija con código de salida 1: que los tres puntos centrales caen dentro del rango observado, que el moderado ya no usa el 4%, que el rango declara fuente, confianza y que es entre administradoras, que cada escenario trae su banda por AFP ordenada, que la envolvente contiene a la banda comunicada pero **no es** la que se comunica, y que la envolvente viene marcada. Se añadió además una comprobación de **compatibilidad del factor independiente del rendimiento** (convertir un saldo patrón al 4% da lo de siempre), para que una recalibración futura del rendimiento no pueda tapar una regresión del factor.

## El vector TMR de la Superfinanciera: fuente primaria para el piso del precio (2026-07-27)

Es la primera pieza de **fuente primaria** que el proyecto consigue sobre el precio de una renta vitalicia. Cambia la calidad del extremo conservador, pero no lo reemplaza, y la razón importa.

### Qué es y qué no es

La TMR es la tasa con que la aseguradora calcula su **reserva matemática** (Decreto 2555 art. 2.31.4.3.2): es la tasa **(b)** de las tres que distingue el proyecto. **No es el precio que le ofrecen al usuario**, que es la **(c)** y sigue sin publicarse porque lo fija cada aseguradora en su nota técnica. Que la TMR venga de fuente primaria no la convierte en precio de venta, y tratarla como tal sería repetir el error original del proyecto en la dirección contraria.

**Para qué sirve entonces: como cota.** Ninguna aseguradora vende una renta más barata que la reserva que debe constituir. Así que el precio real es mayor o igual que el que sale de la TMR. La calculadora la usa como **piso del precio**, y el factor conservador es el **mayor** entre el capital de prensa y el piso de reserva.

**Fuente:** Superintendencia Financiera, Carta Circular 038 del 8 de julio de 2026, corte al 30 de junio de 2026, anexo en Excel con 120 plazos. **Confianza: VERIFICADA EN FUENTE PRIMARIA**, archivo oficial leído. Copia en `../fuentes-datos/`.

### Trampa del anexo, verificada a mano

La columna de inflación implícita **no es dato de mercado en todos los plazos**: se topa en 3,00% desde el plazo 30, y **el plazo 29 ya está en transición** (4,44%). El último plazo limpio es el **28**. Calcular la tasa real más allá da resultados absurdos:

| Plazo | TMR | Inflación implícita | Tasa real |
|---|---|---|---|
| 25 | 6,6232% | 5,9401% | **0,6448%** |
| 28 | 6,6109% | 5,9479% | **0,6257%** |
| 29 | 6,6039% | 4,4378% | 2,0741% (contaminado) |
| 30 | 6,5904% | 3,0000% | 3,4859% (contaminado) |

Importa de verdad porque **la expectativa de vida de la mujer (29,7 años) cae justo en esa zona**. `tmr_real` topa en el plazo 28 en vez de extrapolar, y lo declara. La curva es tan plana ahí (0,64% contra 0,63%) que topar apenas mueve el resultado.

### Lo que la TMR resolvió: el dato de prensa de la mujer no se sostiene

La inconsistencia que había quedado como pregunta abierta para el actuario ya tiene veredicto parcial.

| Sexo | Factor de prensa | Piso de reserva (TMR) | Cuál manda | Lectura |
|---|---|---|---|---|
| Hombre | 268,4 | 257,0 | **Prensa** | Coherente: el precio de venta lleva margen sobre la reserva |
| Mujer | 287,9 | **351,3** | **TMR** | El dato de prensa implicaría vender por debajo de la reserva, que ninguna aseguradora hace |

Sigue sin saberse de dónde salió el capital de 504 millones para la mujer (puede ser otra edad, otra cobertura de beneficiarios u otra tabla). Sigue siendo pregunta para el actuario, pero la calculadora ya no decide a ciegas: manda la cota de fuente primaria.

**Corroboración independiente del orden de magnitud:** la TMR real (0,63% a 0,81%) cae cerca del ancla del hombre (0,28%) y lejísimos del 4% normativo. Confirma que el extremo optimista está muy por encima del precio real.

### Efecto sobre el set dorado: ninguno, y eso es un hallazgo

Los seis casos del set dorado son hombres o se corren con sexo masculino simulado, y en el hombre manda el dato de prensa. **Ninguna cifra del set dorado se movió con este cambio.** El mismo caso-01 corrido como mujer sí se mueve.

**El set dorado no tiene ninguna mujer, así que no puede detectar una regresión en la mitad femenina del modelo.** Es una brecha de cobertura del set, no de la calculadora, y afecta a todo lo que dependa del sexo: edad de pensión, semanas de la C-197, expectativa de vida y ahora el factor. Queda anotado para Santiago.

### Mantenimiento, trimestral y mecánico

La SFC publica una Carta Circular nueva cada trimestre (cortes a 31 de marzo, 30 de junio, 30 de septiembre y 31 de diciembre), entre 7 y 9 días después del cierre. La próxima se espera alrededor del **7 al 9 de octubre de 2026**. Es pública y sin login. Para actualizar: bajar el anexo, recalcular cada plazo como `(1 + TMR) / (1 + inflación implícita) - 1` y reemplazar `TMR_REAL_POR_PLAZO` en `datos_sistema.py`, sin pasar del último plazo con inflación de mercado. El procedimiento está escrito en el propio archivo.

## Supuesto prospectivo de rendimiento (decisión de Santiago, 2026-07-28)

Convive con el dato observado de la sección anterior y no lo reemplaza. Son **dos constantes distintas y no se pueden confundir**.

| Constante | Qué es | Se usa para |
|---|---|---|
| `RENDIMIENTO_REAL_OBSERVADO` | **Evidencia.** Lo que rindieron los fondos según la SFC, 2011 a 2024 | Responder qué rindió cada fondo, y medir la dispersión entre AFP |
| `RENDIMIENTO_REAL_PROSPECTIVO` | **Supuesto.** Apuesta sobre el largo plazo | La proyección de la mesada |

**La decisión.** Santiago decidió que la proyección use un supuesto de largo plazo en el que el moderado sí rinde más que el conservador. Su argumento: a horizontes de varias décadas, más exposición a renta variable debe pagar más, y 2011-2024 es una ventana, no el largo plazo.

**La condición innegociable, cumplida:** el dato observado no se borra ni se maquilla. En el periodo medido el moderado rindió menos que el conservador, y eso sigue escrito, visible y con su fuente, tanto en `datos_sistema.py` como en la salida del diagnóstico.

### Cómo se construyó, paso a paso

| Paso | Qué aporta | Valor | Fuente y confianza |
|---|---|---|---|
| 1. Ancla | Punto de partida del conservador | 2,02% | Dato observado colombiano (SFC). Es el perfil donde una ventana de 13 años distorsiona menos, porque su cartera es sobre todo renta fija. **Confianza MEDIA** |
| 2. Prima de renta variable | Cuánto paga el riesgo a largo plazo | 3,5 puntos reales | Dimson, Marsh y Staunton, Global Investment Returns Yearbook 2025 (London Business School, Cambridge Judge y UBS): serie mundial 1900-2024, renta variable 5,2% real contra bonos 1,7% real. **Confianza MEDIA**, resumen público. **Supuesto importado de otro mercado** |
| 3. Exposición adicional a renta variable | Convierte la prima en puntos | Punto medio de la banda legal de cada fondo: conservador 10%, moderado 32,5%, mayor riesgo 57,5% | **Verificado el 2026-09-19** en el Decreto 2555 de 2010, art. 2.6.12.1.4. **Confianza ALTA**, ver abajo |

**Fórmula, y está en el código para que se pueda recalcular sola:** al ancla del conservador se le suma la exposición **adicional** a renta variable de cada perfil respecto de él, multiplicada por la prima.

| Perfil | Banda legal de renta variable | Cálculo | Prospectivo | Observado central |
|---|---|---|---|---|
| Conservador | 0% a 20% | 2,02% + (10% - 10%) x 3,5 | **2,02%** | 2,02% |
| Moderado | 20% a 45% | 2,02% + (32,5% - 10%) x 3,5 | **2,81%** | 2,76% |
| Mayor riesgo | 45% a 70% | 2,02% + (57,5% - 10%) x 3,5 | **3,68%** | 3,72% |

### El eslabón que era débil, ya verificado (2026-09-19)

**Los límites de renta variable por tipo de fondo se leyeron en fuente primaria:** Decreto 2555 de 2010, artículo 2.6.12.1.4 (sustituido por el Decreto 857 de 2011). Las citas textuales están en `fuentes-datos/multifondos-limites-renta-variable.md`.

**Lo que cambió, y es lo importante: no es un techo suelto por fondo, es una banda encadenada.** El numeral 1 fija los máximos (20 / 45 / 70) y el numeral 2 fija los mínimos: el mínimo de cada fondo no puede ser inferior al máximo del fondo anterior. Las bandas reales son conservador 0% a 20%, moderado 20% a 45% y mayor riesgo 45% a 70%.

**Qué se corrigió en el modelo.** Hasta el 2026-09-19 cada perfil entraba a la fórmula con su **techo**, o sea suponiendo que cada fondo usa su límite completo, cosa que ningún fondo hace: el propio código lo declaraba como el borde optimista de la construcción. Ahora entra con el **punto medio** de su banda, que es el supuesto neutral. El conservador no se movió (es el ancla); el moderado bajó de 2,895% a 2,8075% real y el mayor riesgo de 3,77% a 3,6825%.

**Efecto lateral que vale la pena mirar:** el supuesto quedó todavía más pegado a la evidencia. La brecha contra el observado de la SFC pasó de 0,14 a 0,05 puntos en el moderado, y de 0,05 a 0,04 en el mayor riesgo.

**Lo que este rango NO autoriza.** La banda acota el rendimiento **esperado** de largo plazo que implica la mezcla del fondo, no el **realizado**. Un fondo moderado que cumple la ley puede rendir en un periodo por debajo del piso de su banda, y de hecho pasó (la SFC midió moderados en 2,27% real). Por eso la banda legal no se usa para recortar la dispersión observada entre administradoras.

**Supuesto adicional, declarado:** se asume que cada fondo usa su límite completo. Ninguno lo hace, así que estos números son el **borde optimista** de la construcción.

### El nivel es supuesto, la dispersión es dato

La banda entre administradoras (`mesada_banda_afp`) sigue saliendo de la **dispersión observada** por la SFC, aunque el nivel central venga del supuesto. Se toma la distancia de cada extremo observado a su centro y se traslada al nivel prospectivo, así que el ancho de la banda entre AFP sigue midiendo un hecho. Hay prueba que lo verifica perfil por perfil.

### Efecto sobre el set dorado

Escenario moderado, fecha 2026-07-18. El "antes" es con el rendimiento observado central; el "ahora", con el prospectivo.

| Caso | Antes (observado) | Ahora (prospectivo) | Pensión anticipada |
|---|---|---|---|
| caso-01 Porvenir | 1.750.905 a 1.945.612 | **1.750.905 a 2.377.907** | de 62 a **60** años |
| caso-02 Skandia | 1.750.905 a 1.750.905 | 1.750.905 a 1.750.905 | Sin cambio, sigue en garantía de pensión mínima |
| caso-03 Protección | 7.347.652 a 12.244.207 | **9.063.927 a 15.104.227** | de 36 a 47, pasa a **36 a 46** |
| caso-04 Colpensiones | No aplica (RPM) | No aplica | No aplica |
| caso-05 Colpensiones | No aplica (RPM) | No aplica | No aplica |
| caso-06 Colfondos | 105.791 a 176.291 | **126.519 a 210.832** | Sin cambio |

**Lectura:** el supuesto prospectivo devuelve cerca de un 23% de la mesada en los casos con saldo, y le devuelve al caso-01 dos años de pensión anticipada de los cuatro que la recalibración le había quitado. Sigue muy por debajo de donde estaba antes de todo este trabajo, porque el otro golpe (el precio de la renta vitalicia) no se revierte: ese sí está anclado en fuente primaria.

### Regresión

Fija que las dos constantes existen y son distintas, que el prospectivo es monótono creciente, que **el observado no lo es y sigue sin estarlo** (la prueba que impide maquillar la evidencia), que el conservador prospectivo es exactamente el observado, que la fórmula reproduce los tres números, que la prima cita su fuente y declara que se importa de otro mercado, que la salida declara la contradicción y marca el eslabón sin verificar, y que la dispersión entre AFP sigue siendo la de la SFC mientras el nivel es el prospectivo.

---

## Extracción automática de documentos (añadido el 2026-09-19)

**Qué resuelve.** Hasta ahora la historia laboral la leía el modelo, mirando el
documento y escribiendo el JSON a mano. Eso tarda cerca de **90 segundos** por
documento. Cuando el documento viene de una plantilla que ya conocemos, un
programa hace lo mismo en **menos de 0,3 segundos**, y copia en vez de leer, así
que no puede equivocarse de cifra.

**Cuatro archivos, uno por responsabilidad:**

| Archivo | Qué hace |
|---|---|
| `extraccion_texto.py` | Saca el texto del PDF conservando las columnas (`pdftotext -layout`, y si no está instalado, `pypdf`) |
| `detectar_formato.py` | Mira el texto y dice de qué administradora es. Ante la duda, dice que no sabe |
| `parsers_historia.py` | Un parser por plantilla. Convierte la tabla al esquema de `casos/esquema-datos.md` |
| `extraer.py` | El que se llama desde afuera: junta los tres y decide si el atajo sirve o hay que leer el documento con el modelo |

**Uso:**

```bash
python3 /srv/jubilo/jubilo/calculadora/extraer.py /ruta/del/documento.pdf --salida /ruta/extracciones/2026-07-21-porvenir.json
```

Devuelve un JSON con el estado. Tres respuestas posibles:

- `extraido`: la tabla se leyó y **cuadra contra el total impreso** del
  documento. El JSON ya está escrito y se puede pasar a `diagnosticar.py`.
- `extraido_parcial`: es un extracto de cuenta, no una historia laboral. Sirve
  para el saldo y el total de semanas, no para el detalle de periodos.
- `fallback`: hay que leerlo como siempre, con el modelo. El campo `motivo`
  dice por qué (`sin_capa_de_texto`, `formato_desconocido`, `tabla_ilegible`,
  `no_cuadra_con_el_total_impreso`, ...).

**La regla que manda: esto nunca falla duro.** Cualquier sorpresa termina en
`fallback`. El camino viejo sigue completo y este es solo un atajo.

### Formatos que se leen hoy

| Formato | Muestras reales | Estado |
|---|---|---|
| `colpensiones_reporte_semanas` | 3 | Leído |
| `colfondos_reporte_historia` | 1 | Leído |
| `porvenir_historia_laboral` | 1 | Leído |
| `historia_laboral_consolidada` (Skandia) | 1 | Leído |
| `proteccion_extracto_trimestral` | 1 | Leído, pero es un extracto, no una historia laboral |
| `proteccion_historia_laboral` | 1, **sin capa de texto** | Se identifica y se manda al modelo |

Al final de `parsers_historia.py` está escrito, formato por formato, qué parte
es estructura estable de la plantilla y qué parte podría romperse con otro
documento de la misma administradora. Con una sola muestra por fondo, esa nota
es lo primero que hay que mirar cuando llegue la segunda.

### Cómo se prueba

```bash
python3 -B calculadora/probar_extraer.py                      # detector y fallback
JUBILO_MUESTRAS="/ruta/a/las/muestras" python3 -B calculadora/probar_extraer.py   # además, contra los documentos reales
```

La segunda forma corre los parsers sobre los PDF de verdad y compara el
resultado **campo a campo contra el set dorado de `casos/`**, que es la
extracción que hoy produce el modelo. Las muestras no viven en el repositorio
(son documentos de personas) y por eso la ruta se pasa por variable de entorno:
sin ella la prueba se salta ese nivel y lo dice.

### Conectado a la conversación (2026-09-19)

Ya está enganchado: el **momento 2 del `system-prompt.md`** arranca corriendo
`extraer.py` con `--salida` sobre la carpeta `extracciones/` de la persona. Si
el estado es `extraido`, el agente se salta los pasos de lectura, extracción y
guardado, y pasa directo al orquestador con ese mismo archivo. Con
`extraido_parcial` o `fallback` sigue el camino de siempre, leyendo el documento
él mismo.

Los cuatro motivos de `fallback` están escritos uno por uno en ese paso (PDF sin
capa de texto, plantilla desconocida, plantilla conocida sin filas legibles y
lectura que no cuadra contra el total impreso), con la regla que los cubre a
todos, incluidos los que no están en la lista: si el estado no es `extraido`, el
agente lee el documento. Nunca se queda sin salida.
