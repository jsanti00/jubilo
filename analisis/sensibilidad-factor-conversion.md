# Sensibilidad del factor de conversion de capital a mesada (RAIS)

> Generado por `analisis/sensibilidad_factor_conversion.py` el 2026-09-19. Fecha de calculo de todos los casos: 2026-07-18. Perfil de fondo: moderado. Este documento se regenera corriendo el script; no se edita a mano.

## 1. Que se esta midiendo y por que importa

En el RAIS la mesada no sale de una formula sobre el salario: sale de dividir el capital ahorrado entre un **factor de conversion**, que es el valor presente de 13 mesadas al ano durante la expectativa de vida. Ese factor depende por completo de una tasa de descuento, y esa tasa es hoy el supuesto mas fragil de toda la calculadora.

- La calculadora usa hoy **4,00%** como extremo optimista. No es el precio de una renta vitalicia: es la tasa de **reserva** que la norma le exige al sistema (Decreto 2555).
- El extremo conservador se despeja del precio observado: **0,28%** para hombres y **0,63%** para mujeres en 2026.
- Desde 2027, con el Decreto 1485, el mismo despeje da **-0,90%** para hombres y **-0,31%** para mujeres, o sea tasa negativa: la renta es tan cara que el capital pierde valor al convertirse.

**Correccion al rango del barrido.** El encargo sugeria barrer de 3,0% a 6,0%. Ese rango es el equivocado: el 4% es el techo practico y el piso real esta cerca de cero, incluso en negativo. Todo lo que pase de 4% es zona teorica (ninguna aseguradora vende por debajo de la reserva matematica). El barrido se corre de 0,25% a 6,00% en pasos de 0,25 para no perder la sugerencia, pero la lectura util esta entre 0,25% y 4%.

## 2. Los casos medidos

| Caso | Tipo | Edad hoy | Edad legal | Saldo usado | Supuesto declarado |
|---|---|---|---|---|---|
| `caso-01-porvenir-rais` | RAIS | 27 | 62 | $22.026.542 | el documento trae sexo y nacimiento |
| `caso-02-skandia-rais` | RAIS | 27 | 62 | $13.969.133 (estimado) | sin saldo en el documento: se usa el piso estimado desde aportes |
| `caso-03-proteccion-rais` | RAIS | 26 | 62 | $130.478.992 | sexo simulado (el documento no lo trae) |
| `caso-06-colfondos-rais` | RAIS | 35 | 62 | $14.553.930 (estimado) | sexo Y edad simulados (el documento no trae ninguno de los dos) |
| `caso-04-colpensiones-rpm` | RPM (contrafactual) | 48 | 62 | $187.990.990 | esta en Colpensiones: el saldo RAIS se simula desde sus salarios |
| `caso-05-colpensiones-rpm` | RPM (contrafactual) | 59 | 62 | $138.074.988 | esta en Colpensiones: el saldo RAIS se simula desde sus salarios |

Los dos casos de Colpensiones se miden como **contrafactual**: se les simula el saldo que tendrian en un fondo privado, con la misma funcion que usa `comparador.py` para responder la pregunta del traslado. Entran porque el factor no solo mueve su mesada hipotetica: mueve el **veredicto de traslado de regimen**, que es una recomendacion con consecuencias legales.

## 3. Linea base: lo que la calculadora dice hoy, sin tocar nada

Antes del barrido, esto es lo que ya entrega `rais.py` con sus dos extremos vigentes: el 4% de la norma y el precio de mercado que corresponde al sexo y al ano de pension de cada caso.

| Caso | Mesada al 4% | Mesada a precio de mercado | Edad anticipada al 4% | Edad a precio de mercado |
|---|---|---|---|---|
| `caso-01-porvenir-rais` | $2.090.605 | $1.750.905 | 61 | no alcanza |
| `caso-02-skandia-rais` | $1.750.905 | $1.750.905 | no alcanza | no alcanza |
| `caso-03-proteccion-rais` | $13.200.055 | $7.921.248 | 36 | 46 |
| `caso-06-colfondos-rais` | $223.943 | $134.386 | no alcanza | no alcanza |
| `caso-04-colpensiones-rpm` | $1.750.905 | $1.750.905 | no alcanza | no alcanza |
| `caso-05-colpensiones-rpm` | $1.750.905 | $1.750.905 | no alcanza | no alcanza |

## 4. Resultados del barrido

### `caso-01-porvenir-rais` (RAIS)

| Tasa | Mesada proyectada | Edad pension anticipada | Capital umbral 110% |
|---|---|---|---|
| 0,25% | $1.750.905 | no alcanza antes de los 62 | $518.726.508 |
| 0,50% | $1.750.905 | no alcanza antes de los 62 | $504.696.612 |
| 0,75% | $1.750.905 | no alcanza antes de los 62 | $491.194.072 |
| 1,00% | $1.750.905 | no alcanza antes de los 62 | $478.195.687 |
| 1,25% | $1.750.905 | no alcanza antes de los 62 | $465.679.387 |
| 1,50% | $1.750.905 | no alcanza antes de los 62 | $453.624.174 |
| 1,75% | $1.750.905 | no alcanza antes de los 62 | $442.010.063 |
| 2,00% | $1.750.905 | no alcanza antes de los 62 | $430.818.034 |
| 2,25% | $1.764.317 | no alcanza antes de los 62 | $420.029.977 |
| 2,50% | $1.809.117 | no alcanza antes de los 62 | $409.628.646 |
| 2,75% | $1.854.531 | no alcanza antes de los 62 | $399.597.617 |
| 3,00% | $1.900.553 | no alcanza antes de los 62 | $389.921.242 |
| 3,25% | $1.947.178 | 62 | $380.584.611 |
| 3,50% | $1.994.399 | 62 | $371.573.515 |
| 3,75% | $2.042.211 | 62 | $362.874.408 |
| 4,00%  **(el 4% que usa hoy la calculadora)** | $2.090.605 | 61 | $354.474.375 |
| 4,25% | $2.139.576 | 61 | $346.361.101 |
| 4,50% | $2.189.117 | 61 | $338.522.837 |
| 4,75% | $2.239.219 | 60 | $330.948.377 |
| 5,00% | $2.289.877 | 60 | $323.627.026 |
| 5,25% | $2.341.081 | 60 | $316.548.577 |
| 5,50% | $2.392.826 | 59 | $309.703.286 |
| 5,75% | $2.445.102 | 59 | $303.081.849 |
| 6,00% | $2.497.902 | 58 | $296.675.382 |

**Recorrido completo:** mesada de $1.750.905 a $2.497.902 (1,43 veces); la edad anticipada va de 62 a 58 anos; capital del umbral de $296.675.382 a $518.726.508.

**Ojo: la salida del RAIS cambia dentro del barrido** (garantia_pension_minima, pension_por_capital). La tasa no solo mueve la cifra: mueve en que regla cae la persona.

### `caso-02-skandia-rais` (RAIS)

| Tasa | Mesada proyectada | Edad pension anticipada | Capital umbral 110% |
|---|---|---|---|
| 0,25% | $1.750.905 | no alcanza antes de los 62 | $518.726.508 |
| 0,50% | $1.750.905 | no alcanza antes de los 62 | $504.696.612 |
| 0,75% | $1.750.905 | no alcanza antes de los 62 | $491.194.072 |
| 1,00% | $1.750.905 | no alcanza antes de los 62 | $478.195.687 |
| 1,25% | $1.750.905 | no alcanza antes de los 62 | $465.679.387 |
| 1,50% | $1.750.905 | no alcanza antes de los 62 | $453.624.174 |
| 1,75% | $1.750.905 | no alcanza antes de los 62 | $442.010.063 |
| 2,00% | $1.750.905 | no alcanza antes de los 62 | $430.818.034 |
| 2,25% | $1.750.905 | no alcanza antes de los 62 | $420.029.977 |
| 2,50% | $1.750.905 | no alcanza antes de los 62 | $409.628.646 |
| 2,75% | $1.750.905 | no alcanza antes de los 62 | $399.597.617 |
| 3,00% | $1.750.905 | no alcanza antes de los 62 | $389.921.242 |
| 3,25% | $1.750.905 | no alcanza antes de los 62 | $380.584.611 |
| 3,50% | $1.750.905 | no alcanza antes de los 62 | $371.573.515 |
| 3,75% | $1.750.905 | no alcanza antes de los 62 | $362.874.408 |
| 4,00%  **(el 4% que usa hoy la calculadora)** | $1.750.905 | no alcanza antes de los 62 | $354.474.375 |
| 4,25% | $1.750.905 | no alcanza antes de los 62 | $346.361.101 |
| 4,50% | $1.750.905 | no alcanza antes de los 62 | $338.522.837 |
| 4,75% | $1.750.905 | no alcanza antes de los 62 | $330.948.377 |
| 5,00% | $1.750.905 | no alcanza antes de los 62 | $323.627.026 |
| 5,25% | $1.750.905 | no alcanza antes de los 62 | $316.548.577 |
| 5,50% | $1.750.905 | no alcanza antes de los 62 | $309.703.286 |
| 5,75% | $1.750.905 | no alcanza antes de los 62 | $303.081.849 |
| 6,00% | $1.750.905 | no alcanza antes de los 62 | $296.675.382 |

**Recorrido completo:** mesada de $1.750.905 a $1.750.905 (1,00 veces); no alcanza la pension anticipada a ninguna tasa; capital del umbral de $296.675.382 a $518.726.508.

### `caso-03-proteccion-rais` (RAIS)

| Tasa | Mesada proyectada | Edad pension anticipada | Capital umbral 110% |
|---|---|---|---|
| 0,25% | $9.020.324 | 44 | $518.726.508 |
| 0,50% | $9.271.077 | 43 | $504.696.612 |
| 0,75% | $9.525.931 | 43 | $491.194.072 |
| 1,00% | $9.784.867 | 42 | $478.195.687 |
| 1,25% | $10.047.860 | 42 | $465.679.387 |
| 1,50% | $10.314.885 | 41 | $453.624.174 |
| 1,75% | $10.585.915 | 40 | $442.010.063 |
| 2,00% | $10.860.922 | 40 | $430.818.034 |
| 2,25% | $11.139.874 | 39 | $420.029.977 |
| 2,50% | $11.422.739 | 39 | $409.628.646 |
| 2,75% | $11.709.482 | 38 | $399.597.617 |
| 3,00% | $12.000.067 | 38 | $389.921.242 |
| 3,25% | $12.294.457 | 37 | $380.584.611 |
| 3,50% | $12.592.612 | 37 | $371.573.515 |
| 3,75% | $12.894.492 | 36 | $362.874.408 |
| 4,00%  **(el 4% que usa hoy la calculadora)** | $13.200.055 | 36 | $354.474.375 |
| 4,25% | $13.509.257 | 36 | $346.361.101 |
| 4,50% | $13.822.054 | 35 | $338.522.837 |
| 4,75% | $14.138.402 | 35 | $330.948.377 |
| 5,00% | $14.458.252 | 34 | $323.627.026 |
| 5,25% | $14.781.558 | 34 | $316.548.577 |
| 5,50% | $15.108.271 | 34 | $309.703.286 |
| 5,75% | $15.438.341 | 33 | $303.081.849 |
| 6,00% | $15.771.720 | 33 | $296.675.382 |

**Recorrido completo:** mesada de $9.020.324 a $15.771.720 (1,75 veces); la edad anticipada va de 44 a 33 anos; capital del umbral de $296.675.382 a $518.726.508.

### `caso-06-colfondos-rais` (RAIS)

| Tasa | Mesada proyectada | Edad pension anticipada | Capital umbral 110% |
|---|---|---|---|
| 0,25% | $153.033 | no alcanza antes de los 62 | $518.726.508 |
| 0,50% | $157.287 | no alcanza antes de los 62 | $504.696.612 |
| 0,75% | $161.610 | no alcanza antes de los 62 | $491.194.072 |
| 1,00% | $166.003 | no alcanza antes de los 62 | $478.195.687 |
| 1,25% | $170.465 | no alcanza antes de los 62 | $465.679.387 |
| 1,50% | $174.995 | no alcanza antes de los 62 | $453.624.174 |
| 1,75% | $179.593 | no alcanza antes de los 62 | $442.010.063 |
| 2,00% | $184.259 | no alcanza antes de los 62 | $430.818.034 |
| 2,25% | $188.991 | no alcanza antes de los 62 | $420.029.977 |
| 2,50% | $193.790 | no alcanza antes de los 62 | $409.628.646 |
| 2,75% | $198.655 | no alcanza antes de los 62 | $399.597.617 |
| 3,00% | $203.585 | no alcanza antes de los 62 | $389.921.242 |
| 3,25% | $208.579 | no alcanza antes de los 62 | $380.584.611 |
| 3,50% | $213.638 | no alcanza antes de los 62 | $371.573.515 |
| 3,75% | $218.759 | no alcanza antes de los 62 | $362.874.408 |
| 4,00%  **(el 4% que usa hoy la calculadora)** | $223.943 | no alcanza antes de los 62 | $354.474.375 |
| 4,25% | $229.189 | no alcanza antes de los 62 | $346.361.101 |
| 4,50% | $234.495 | no alcanza antes de los 62 | $338.522.837 |
| 4,75% | $239.862 | no alcanza antes de los 62 | $330.948.377 |
| 5,00% | $245.289 | no alcanza antes de los 62 | $323.627.026 |
| 5,25% | $250.774 | no alcanza antes de los 62 | $316.548.577 |
| 5,50% | $256.316 | no alcanza antes de los 62 | $309.703.286 |
| 5,75% | $261.916 | no alcanza antes de los 62 | $303.081.849 |
| 6,00% | $267.572 | no alcanza antes de los 62 | $296.675.382 |

**Recorrido completo:** mesada de $153.033 a $267.572 (1,75 veces); no alcanza la pension anticipada a ninguna tasa; capital del umbral de $296.675.382 a $518.726.508.

### `caso-04-colpensiones-rpm` (RPM (contrafactual))

| Tasa | Mesada proyectada | Edad pension anticipada | Capital umbral 110% |
|---|---|---|---|
| 0,25% | $1.750.905 | no alcanza antes de los 62 | $518.726.508 |
| 0,50% | $1.750.905 | no alcanza antes de los 62 | $504.696.612 |
| 0,75% | $1.750.905 | no alcanza antes de los 62 | $491.194.072 |
| 1,00% | $1.750.905 | no alcanza antes de los 62 | $478.195.687 |
| 1,25% | $1.750.905 | no alcanza antes de los 62 | $465.679.387 |
| 1,50% | $1.750.905 | no alcanza antes de los 62 | $453.624.174 |
| 1,75% | $1.750.905 | no alcanza antes de los 62 | $442.010.063 |
| 2,00% | $1.750.905 | no alcanza antes de los 62 | $430.818.034 |
| 2,25% | $1.750.905 | no alcanza antes de los 62 | $420.029.977 |
| 2,50% | $1.750.905 | no alcanza antes de los 62 | $409.628.646 |
| 2,75% | $1.750.905 | no alcanza antes de los 62 | $399.597.617 |
| 3,00% | $1.750.905 | no alcanza antes de los 62 | $389.921.242 |
| 3,25% | $1.750.905 | no alcanza antes de los 62 | $380.584.611 |
| 3,50% | $1.750.905 | no alcanza antes de los 62 | $371.573.515 |
| 3,75% | $1.750.905 | no alcanza antes de los 62 | $362.874.408 |
| 4,00%  **(el 4% que usa hoy la calculadora)** | $1.750.905 | no alcanza antes de los 62 | $354.474.375 |
| 4,25% | $1.779.015 | no alcanza antes de los 62 | $346.361.101 |
| 4,50% | $1.820.207 | no alcanza antes de los 62 | $338.522.837 |
| 4,75% | $1.861.866 | no alcanza antes de los 62 | $330.948.377 |
| 5,00% | $1.903.987 | no alcanza antes de los 62 | $323.627.026 |
| 5,25% | $1.946.563 | 62 | $316.548.577 |
| 5,50% | $1.989.587 | 62 | $309.703.286 |
| 5,75% | $2.033.054 | 62 | $303.081.849 |
| 6,00% | $2.076.956 | 61 | $296.675.382 |

**Recorrido completo:** mesada de $1.750.905 a $2.076.956 (1,19 veces); la edad anticipada va de 62 a 61 anos; capital del umbral de $296.675.382 a $518.726.508.

**Ojo: la salida del RAIS cambia dentro del barrido** (garantia_pension_minima, pension_por_capital). La tasa no solo mueve la cifra: mueve en que regla cae la persona.

### `caso-05-colpensiones-rpm` (RPM (contrafactual))

| Tasa | Mesada proyectada | Edad pension anticipada | Capital umbral 110% |
|---|---|---|---|
| 0,25% | $1.750.905 | no alcanza antes de los 62 | $518.726.508 |
| 0,50% | $1.750.905 | no alcanza antes de los 62 | $504.696.612 |
| 0,75% | $1.750.905 | no alcanza antes de los 62 | $491.194.072 |
| 1,00% | $1.750.905 | no alcanza antes de los 62 | $478.195.687 |
| 1,25% | $1.750.905 | no alcanza antes de los 62 | $465.679.387 |
| 1,50% | $1.750.905 | no alcanza antes de los 62 | $453.624.174 |
| 1,75% | $1.750.905 | no alcanza antes de los 62 | $442.010.063 |
| 2,00% | $1.750.905 | no alcanza antes de los 62 | $430.818.034 |
| 2,25% | $1.750.905 | no alcanza antes de los 62 | $420.029.977 |
| 2,50% | $1.750.905 | no alcanza antes de los 62 | $409.628.646 |
| 2,75% | $1.750.905 | no alcanza antes de los 62 | $399.597.617 |
| 3,00% | $1.750.905 | no alcanza antes de los 62 | $389.921.242 |
| 3,25% | $1.750.905 | no alcanza antes de los 62 | $380.584.611 |
| 3,50% | $1.750.905 | no alcanza antes de los 62 | $371.573.515 |
| 3,75% | $1.750.905 | no alcanza antes de los 62 | $362.874.408 |
| 4,00%  **(el 4% que usa hoy la calculadora)** | $1.750.905 | no alcanza antes de los 62 | $354.474.375 |
| 4,25% | $1.750.905 | no alcanza antes de los 62 | $346.361.101 |
| 4,50% | $1.750.905 | no alcanza antes de los 62 | $338.522.837 |
| 4,75% | $1.750.905 | no alcanza antes de los 62 | $330.948.377 |
| 5,00% | $1.750.905 | no alcanza antes de los 62 | $323.627.026 |
| 5,25% | $1.750.905 | no alcanza antes de los 62 | $316.548.577 |
| 5,50% | $1.750.905 | no alcanza antes de los 62 | $309.703.286 |
| 5,75% | $1.750.905 | no alcanza antes de los 62 | $303.081.849 |
| 6,00% | $1.750.905 | no alcanza antes de los 62 | $296.675.382 |

**Recorrido completo:** mesada de $1.750.905 a $1.750.905 (1,00 veces); no alcanza la pension anticipada a ninguna tasa; capital del umbral de $296.675.382 a $518.726.508.

## 5. Elasticidad: anios de pension por cada 0,5 puntos de tasa

| Caso | Edad anticipada a 0,25% | Edad a 4% (hoy) | Anios en juego | Anios por cada 0,5 pp (tramo 0,25%-4%) |
|---|---|---|---|---|
| `caso-01-porvenir-rais` | no alcanza | 61 | n/d | 0,67 |
| `caso-02-skandia-rais` | no alcanza | no alcanza | n/d | n/d |
| `caso-03-proteccion-rais` | 44 | 36 | 8 anos | 1,07 |
| `caso-06-colfondos-rais` | no alcanza | no alcanza | n/d | n/d |
| `caso-04-colpensiones-rpm` | no alcanza | no alcanza | n/d | n/d |
| `caso-05-colpensiones-rpm` | no alcanza | no alcanza | n/d | n/d |

La elasticidad **no es constante**: la edad de pension anticipada es una variable entera (se mueve a saltos de un ano) y depende de cuando el saldo proyectado cruza el umbral del 110% del salario minimo. En los casos con mucho capital y mucho tiempo por delante, el cruce es plano y la tasa lo mueve varios anos; en los casos que ni siquiera alcanzan el umbral, la tasa no mueve nada porque no hay nada que mover. Cuando un caso solo alcanza el umbral en parte del tramo, la pendiente se mide sobre esa parte y no sobre todo el tramo.

## 6. Que casos son mas fragiles al supuesto

| Caso | Mesada: techo / piso | Anios de pension en juego | Salida del RAIS |
|---|---|---|---|
| `caso-03-proteccion-rais` | 1,75 veces | 11 | pension_por_capital |
| `caso-01-porvenir-rais` | 1,43 veces | 4 | pension_por_capital |
| `caso-04-colpensiones-rpm` | 1,19 veces | 1 | garantia_pension_minima |
| `caso-06-colfondos-rais` | 1,75 veces | 0 | devolucion_de_saldos |
| `caso-02-skandia-rais` | 1,00 veces | 0 | garantia_pension_minima |
| `caso-05-colpensiones-rpm` | 1,00 veces | 0 | garantia_pension_minima |

**Cuatro patrones, y son MECE entre si:**

1. **Fragiles de verdad: los que se pensionan por capital y aun tienen horizonte largo.** Su mesada y su edad de pension dependen enteramente del factor, y como les faltan decadas, cada punto de tasa mueve anos. Es el perfil del caso estrella.
2. **Fragiles en el borde: los que quedan pegados al umbral de la garantia de pension minima.** Su mesada esta clavada en un salario minimo en la parte baja del barrido y se despega en la parte alta, asi que la tasa decide si su cifra la pone su ahorro o la pone el Estado.
3. **Inmunes en la practica: los que terminan en devolucion de saldos.** La mesada que se les calcula se mueve tanto como la del caso estrella en proporcion, pero es una cifra teorica: no alcanzan pension, les devuelven el saldo, y el factor no toca lo que reciben.
4. **Fragiles en el veredicto, no en la cifra: los contrafactuales de Colpensiones.** Lo que el factor mueve ahi no es cuanto reciben, es si el RAIS le gana o le pierde al RPM, que es la comparacion con la que alguien decide trasladarse.

## 7. So whats

1. **El rango de incertidumbre es mas ancho que cualquier palanca que le ofrezcamos a la persona.** En el caso estrella, el factor solo, sin tocar rendimiento ni aportes, ya abre la mesada 1,67 veces entre los dos extremos vigentes ($7.921.248 contra $13.200.055). Eso supera con holgura lo que esa persona gana cambiando de AFP o de perfil de fondo. Mientras el factor sea un supuesto abierto, presentar palancas finas al lado de la mesada le da a la cifra una precision que no tiene.
2. **La edad de pension anticipada no deberia comunicarse como un numero, y el rango real es mas ancho de lo que el proyecto venia asumiendo.** El proyecto trabajaba con la idea de que el caso estrella se movia de los 35 a los 39 anos. Medido, se mueve de los 36 (precio de la norma) a los 46 (precio de mercado), y en el barrido completo cubre once anos. Una persona que oye 'te puedes pensionar a los 36' toma decisiones de vida distintas a la que oye 'entre los 36 y los 46'. La banda ya esta calculada en el codigo (`edad_pension_anticipada_banda`): la decision pendiente es si el agente puede seguir citando el extremo optimista sin apellido.
3. **La forma de cerrar esto no es elegir mejor la tasa, es conseguir el dato.** El precio de la renta vitalicia no esta publicado, pero existe: son las notas tecnicas de las aseguradoras ante la Superfinanciera. Conseguir dos o tres cotizaciones reales convierte el supuesto mas caro del proyecto en un dato, y esta medicion dice exactamente cuanto vale ese esfuerzo.

