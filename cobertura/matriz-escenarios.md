# Matriz de cobertura de escenarios de Júbilo

> Generada el 2026-07-27. Evalúa el estado real de `V0/kit-contexto/`, `V0/calculadora/` y `V0/kit-contexto/system-prompt.md` a esa fecha. Pendiente 3 de `ESTADO.md`.

## 1. Nota metodológica

### 1.1 Discrepancia 64 vs. 128

El prompt original habla de 128 celdas. Las cuatro dimensiones definidas dan **64**: 2 regímenes x 4 situaciones laborales x 4 momentos de vida x 2 niveles de patrimonio = 64. Las 128 solo saldrían agregando una quinta dimensión binaria (sexo, por ejemplo, que sí mueve edad y semanas requeridas, o afiliado con o sin régimen de transición). Esta matriz enumera las **64 reales** y no infla la cuenta. Si Santiago quiere las 128, la quinta dimensión debe decidirse explícitamente; la candidata con más impacto en las cifras es el **sexo**, porque cambia edad de pensión, semanas exigidas bajo la C-197 y expectativa de vida.

### 1.2 Criterio de cubierto / parcial / hueco

Cada celda se evalúa en tres ejes independientes:

| Eje | Pregunta que responde | Fuente de la evaluación |
|---|---|---|
| **Corpus** | ¿Algún documento del kit responde la pregunta, y en qué sección? | Los 22 documentos de `kit-contexto/`, índice en `kit-contexto/README.md` |
| **Cálculo** | ¿La calculadora entrega el número que hace falta? | `rpm.py`, `rais.py`, `comparador.py`, `router.py`, `lagunas.py`, `recuperacion.py`, `diagnosticar.py`, `datos_sistema.py`, `costo_y_retorno.py` |
| **Comportamiento** | ¿El system prompt tiene la regla que ese caso exige? | `kit-contexto/system-prompt.md` |

Escala:

- **Cubierto:** existe la pieza, cita sección concreta y responde la pregunta sin que el agente tenga que improvisar.
- **Parcial:** existe la pieza pero le falta un pedazo necesario para esa celda (una marca `[VERIFICAR]` abierta, una aproximación documentada, una regla que aplica por analogía y no por diseño).
- **Hueco:** no existe pieza, o la que existe contradice lo que esa celda necesita.

El porcentaje pondera cubierto = 100%, parcial = 50%, hueco = 0%. Es una medida de completitud, no de calidad: una celda cubierta puede seguir siendo mala si el dato de fondo está mal.

### 1.3 Códigos

Régimen: **RPM** (Colpensiones), **RAIS** (fondo privado). Situación: **EMP** empleado, **IND** independiente por cuenta propia, **REN** rentista de capital, **MIX** mixto o historia partida. Momento: **M10+** más de 10 años para pensionarse, **M10-** menos de 10 años, **CUM** ya cumple requisitos, **PEN** ya pensionado. Patrimonio: **CA** con capacidad de ahorro, **SC** sin capacidad de ahorro.

---

## 2. La matriz (64 celdas)

### Régimen RPM (Colpensiones)

#### EMP: Empleado

**C01 | RPM · EMP · M10+ · CA**

*Más de 10 años para pensionarse, con capacidad de ahorro.*

> Tengo 38 años, llevo 12 cotizando en Colpensiones y me sobran como $800.000 al mes. ¿Meterle más plata ahí me sirve o mejor invierto por fuera?

- **Corpus: CUBIERTO.** Ref: reglas-rpm.md s.3 y s.5; mora-y-correccion-historia-laboral.md s.1 y s.2; supuestos-actuariales.md s.3 y s.5; aportes-voluntarios-y-sobrecotizacion.md s.2 y s.3.
- **Cálculo: PARCIAL.** Ref: diagnosticar.py -> rpm.py; lagunas.py + recuperacion.py; costo_y_retorno.py (tabla_de_escenarios: cuánto cuesta cada alternativa y en cuántos meses se recupera). Falta: costo_y_retorno.py resuelve el costo y el breakeven de sobrecotizar, pero ningún módulo modela el aporte voluntario propiamente dicho (rendimiento en la cuenta, comisión de la AFP, beneficio tributario del art. 126-1), que es la otra mitad de la decisión de quien tiene excedente.
- **Comportamiento: CUBIERTO.** Ref: Reglas duras (nunca se rompen) 1 a 8; Tu flujo de conversación (los 5 momentos); Plantilla del diagnóstico; Supuestos de toda proyección: explícitos y concretos; Siempre rango, nunca punto medio; Los huecos y su recuperación salen de la calculadora, nunca de tu cuenta; Toda palanca se verifica antes de ofrecerla.

**C02 | RPM · EMP · M10+ · SC**

*Más de 10 años para pensionarse, sin capacidad de ahorro.*

> Tengo 34 años y cotizo por el mínimo en Colpensiones. ¿Con eso cuánto me va a quedar de pensión y a qué edad?

- **Corpus: CUBIERTO.** Ref: reglas-rpm.md s.3 y s.5; mora-y-correccion-historia-laboral.md s.1 y s.2; supuestos-actuariales.md s.3 y s.5; sin-pension-alternativas.md s.2 a s.7.
- **Cálculo: CUBIERTO.** Ref: diagnosticar.py -> rpm.py; lagunas.py + recuperacion.py.
- **Comportamiento: PARCIAL.** Ref: Reglas duras (nunca se rompen) 1 a 8; Tu flujo de conversación (los 5 momentos); Plantilla del diagnóstico; Supuestos de toda proyección: explícitos y concretos; Siempre rango, nunca punto medio; Los huecos y su recuperación salen de la calculadora, nunca de tu cuenta. Falta: la tabla de accionabilidad verifica régimen, edad e ingreso, no capacidad de pago; la regla de segmento de BEPS ('ofrecerlo a alguien con capacidad de pago es un error de segmento') vive en aportes-voluntarios-y-sobrecotizacion.md s.5, no en el system-prompt.

**C03 | RPM · EMP · M10- · CA**

*Menos de 10 años, con capacidad de ahorro.*

> Tengo 55 años, estoy en Colpensiones y acabo de vender un apartamento. ¿Puedo usar esa plata para mejorar mi pensión?

- **Corpus: CUBIERTO.** Ref: reglas-rpm.md s.3 y s.5; mora-y-correccion-historia-laboral.md s.1 y s.2; reglas-traslados.md s.1; aportes-voluntarios-y-sobrecotizacion.md s.2 y s.3.
- **Cálculo: PARCIAL.** Ref: diagnosticar.py -> rpm.py; lagunas.py + recuperacion.py; costo_y_retorno.py (tabla_de_escenarios: cuánto cuesta cada alternativa y en cuántos meses se recupera). Falta: costo_y_retorno.py resuelve el costo y el breakeven de sobrecotizar, pero ningún módulo modela el aporte voluntario propiamente dicho (rendimiento en la cuenta, comisión de la AFP, beneficio tributario del art. 126-1), que es la otra mitad de la decisión de quien tiene excedente.
- **Comportamiento: CUBIERTO.** Ref: Reglas duras (nunca se rompen) 1 a 8; Tu flujo de conversación (los 5 momentos); Plantilla del diagnóstico; Supuestos de toda proyección: explícitos y concretos; Siempre rango, nunca punto medio; Los huecos y su recuperación salen de la calculadora, nunca de tu cuenta; Toda palanca se verifica antes de ofrecerla.

**C04 | RPM · EMP · M10- · SC**

*Menos de 10 años, sin capacidad de ahorro.*

> Me faltan 6 años para los 62 y estoy en Colpensiones. Si me quedo sin trabajo mañana, ¿qué pasa con mi pensión?

- **Corpus: CUBIERTO.** Ref: reglas-rpm.md s.3 y s.5; mora-y-correccion-historia-laboral.md s.1 y s.2; reglas-traslados.md s.1; sin-pension-alternativas.md s.2 a s.7.
- **Cálculo: PARCIAL.** Ref: diagnosticar.py -> rpm.py; lagunas.py + recuperacion.py. Falta: rpm.py nombra la indemnización sustitutiva como camino (línea 332) pero no calcula su monto.
- **Comportamiento: PARCIAL.** Ref: Reglas duras (nunca se rompen) 1 a 8; Tu flujo de conversación (los 5 momentos); Plantilla del diagnóstico; Supuestos de toda proyección: explícitos y concretos; Siempre rango, nunca punto medio; Los huecos y su recuperación salen de la calculadora, nunca de tu cuenta. Falta: la tabla de accionabilidad verifica régimen, edad e ingreso, no capacidad de pago; la regla de segmento de BEPS ('ofrecerlo a alguien con capacidad de pago es un error de segmento') vive en aportes-voluntarios-y-sobrecotizacion.md s.5, no en el system-prompt.

**C05 | RPM · EMP · CUM · CA**

*Ya cumple requisitos, con capacidad de ahorro.*

> Ya tengo la edad y las semanas en Colpensiones, pero me quieren renovar el contrato. ¿Me pensiono ya o sigo trabajando un año más?

- **Corpus: CUBIERTO.** Ref: reglas-rpm.md s.3 y s.5; mora-y-correccion-historia-laboral.md s.1 y s.2; reclamacion-y-defensa.md s.2 y s.3; aportes-voluntarios-y-sobrecotizacion.md s.2 y s.3.
- **Cálculo: PARCIAL.** Ref: diagnosticar.py -> rpm.py; lagunas.py + recuperacion.py; costo_y_retorno.py (breakeven_meses y ganancia_neta: seguir cotizando vs. reclamar ya); costo_y_retorno.py (tabla_de_escenarios: cuánto cuesta cada alternativa y en cuántos meses se recupera). Falta: rpm.py no implementa el piso legal del 55% de tasa de reemplazo (kit-contexto/README.md, bloque 2 punto 7); costo_y_retorno.py resuelve el costo y el breakeven de sobrecotizar, pero ningún módulo modela el aporte voluntario propiamente dicho (rendimiento en la cuenta, comisión de la AFP, beneficio tributario del art. 126-1), que es la otra mitad de la decisión de quien tiene excedente.
- **Comportamiento: PARCIAL.** Ref: Reglas duras (nunca se rompen) 1 a 8; Tu flujo de conversación (los 5 momentos); Plantilla del diagnóstico; Supuestos de toda proyección: explícitos y concretos; Siempre rango, nunca punto medio; Los huecos y su recuperación salen de la calculadora, nunca de tu cuenta; Toda palanca se verifica antes de ofrecerla. Falta: el menú de palancas de 'Toda palanca se verifica antes de ofrecerla' solo contempla 'cerca de cumplir requisitos'; no hay plantilla ni cierre para quien YA cumple, cuyo bloque 2 no es una proyección sino una decisión de cuándo reclamar.

**C06 | RPM · EMP · CUM · SC**

*Ya cumple requisitos, sin capacidad de ahorro.*

> Cumplí requisitos en Colpensiones el mes pasado. ¿Cómo pido la pensión y cuánto se demoran en pagarme?

- **Corpus: CUBIERTO.** Ref: reglas-rpm.md s.3 y s.5; mora-y-correccion-historia-laboral.md s.1 y s.2; reclamacion-y-defensa.md s.2 y s.3; sin-pension-alternativas.md s.2 a s.7.
- **Cálculo: PARCIAL.** Ref: diagnosticar.py -> rpm.py; lagunas.py + recuperacion.py; costo_y_retorno.py (breakeven_meses y ganancia_neta: seguir cotizando vs. reclamar ya). Falta: rpm.py no implementa el piso legal del 55% de tasa de reemplazo (kit-contexto/README.md, bloque 2 punto 7); rpm.py nombra la indemnización sustitutiva como camino (línea 332) pero no calcula su monto.
- **Comportamiento: PARCIAL.** Ref: Reglas duras (nunca se rompen) 1 a 8; Tu flujo de conversación (los 5 momentos); Plantilla del diagnóstico; Supuestos de toda proyección: explícitos y concretos; Siempre rango, nunca punto medio; Los huecos y su recuperación salen de la calculadora, nunca de tu cuenta. Falta: el menú de palancas de 'Toda palanca se verifica antes de ofrecerla' solo contempla 'cerca de cumplir requisitos'; no hay plantilla ni cierre para quien YA cumple, cuyo bloque 2 no es una proyección sino una decisión de cuándo reclamar; la tabla de accionabilidad verifica régimen, edad e ingreso, no capacidad de pago; la regla de segmento de BEPS ('ofrecerlo a alguien con capacidad de pago es un error de segmento') vive en aportes-voluntarios-y-sobrecotizacion.md s.5, no en el system-prompt.

**C07 | RPM · EMP · PEN · CA**

*Ya pensionado, con capacidad de ahorro.*

> Ya estoy pensionado por Colpensiones y sigo trabajando como empleado. ¿Me sirve seguir ahorrando en un fondo voluntario?

- **Corpus: PARCIAL.** Ref: reglas-rpm.md s.3 y s.5; mora-y-correccion-historia-laboral.md s.1 y s.2; vida-del-pensionado.md s.1 a s.5 + tributario-pensional.md s.2 y s.3; aportes-voluntarios-y-sobrecotizacion.md s.2 y s.3. Falta: para el pensionado de Colpensiones con excedente, el corpus solo dice que el ahorro fuera del sistema no es pensión y lo declara fuera de alcance (aportes-voluntarios-y-sobrecotizacion.md s.5).
- **Cálculo: PARCIAL.** Ref: diagnosticar.py -> rpm.py; lagunas.py + recuperacion.py; costo_y_retorno.py (mesada_neta y tarifa_salud_pensionado); costo_y_retorno.py (tabla_de_escenarios: cuánto cuesta cada alternativa y en cuántos meses se recupera). Falta: costo_y_retorno.py ya descuenta salud de la mesada, pero ningún módulo calcula reajuste anual, retención en la fuente, mesada 14 ni excedentes de libre disponibilidad, y diagnosticar.py está construido para proyectar hacia la pensión, no desde ella; costo_y_retorno.py resuelve el costo y el breakeven de sobrecotizar, pero ningún módulo modela el aporte voluntario propiamente dicho (rendimiento en la cuenta, comisión de la AFP, beneficio tributario del art. 126-1), que es la otra mitad de la decisión de quien tiene excedente.
- **Comportamiento: HUECO.** Ref: Reglas duras (nunca se rompen) 1 a 8; Tu flujo de conversación (los 5 momentos); Plantilla del diagnóstico; Supuestos de toda proyección: explícitos y concretos; Siempre rango, nunca punto medio; Los huecos y su recuperación salen de la calculadora, nunca de tu cuenta. Falta: no hay flujo ni plantilla para un usuario ya pensionado; la bienvenida de 'Lo que el usuario nunca ve' (cerrada el 2026-07-20) promete 'cuándo y con qué monto te vas a pensionar', que a él no le aplica.

**C08 | RPM · EMP · PEN · SC**

*Ya pensionado, sin capacidad de ahorro.*

> Me pensionaron con Colpensiones y la mesada me llegó con descuentos. ¿Por qué me descontaron y me la suben el otro año?

- **Corpus: CUBIERTO.** Ref: reglas-rpm.md s.3 y s.5; mora-y-correccion-historia-laboral.md s.1 y s.2; vida-del-pensionado.md s.1 a s.5 + tributario-pensional.md s.2 y s.3; sin-pension-alternativas.md s.2 a s.7.
- **Cálculo: PARCIAL.** Ref: diagnosticar.py -> rpm.py; lagunas.py + recuperacion.py; costo_y_retorno.py (mesada_neta y tarifa_salud_pensionado). Falta: costo_y_retorno.py ya descuenta salud de la mesada, pero ningún módulo calcula reajuste anual, retención en la fuente, mesada 14 ni excedentes de libre disponibilidad, y diagnosticar.py está construido para proyectar hacia la pensión, no desde ella.
- **Comportamiento: HUECO.** Ref: Reglas duras (nunca se rompen) 1 a 8; Tu flujo de conversación (los 5 momentos); Plantilla del diagnóstico; Supuestos de toda proyección: explícitos y concretos; Siempre rango, nunca punto medio; Los huecos y su recuperación salen de la calculadora, nunca de tu cuenta. Falta: no hay flujo ni plantilla para un usuario ya pensionado; la bienvenida de 'Lo que el usuario nunca ve' (cerrada el 2026-07-20) promete 'cuándo y con qué monto te vas a pensionar', que a él no le aplica; la tabla de accionabilidad verifica régimen, edad e ingreso, no capacidad de pago; la regla de segmento de BEPS ('ofrecerlo a alguien con capacidad de pago es un error de segmento') vive en aportes-voluntarios-y-sobrecotizacion.md s.5, no en el system-prompt.

#### IND: Independiente por cuenta propia

**C09 | RPM · IND · M10+ · CA**

*Más de 10 años para pensionarse, con capacidad de ahorro.*

> Soy independiente, facturo $12.000.000 al mes y cotizo en Colpensiones sobre el mínimo. ¿Cuánto me cambia la pensión si cotizo sobre lo que de verdad gano?

- **Corpus: CUBIERTO.** Ref: reglas-rpm.md s.3 y s.5; independientes.md s.2, s.4 y s.7; supuestos-actuariales.md s.3 y s.5; aportes-voluntarios-y-sobrecotizacion.md s.2 y s.3.
- **Cálculo: PARCIAL.** Ref: diagnosticar.py -> rpm.py; rpm/rais con --ibc-futuro y --densidad-futura; costo_y_retorno.py (aporte_mensual y costo_total sobre el IBC real); costo_y_retorno.py (tabla_de_escenarios: cuánto cuesta cada alternativa y en cuántos meses se recupera). Falta: costo_y_retorno.py resuelve el costo y el breakeven de sobrecotizar, pero ningún módulo modela el aporte voluntario propiamente dicho (rendimiento en la cuenta, comisión de la AFP, beneficio tributario del art. 126-1), que es la otra mitad de la decisión de quien tiene excedente.
- **Comportamiento: CUBIERTO.** Ref: Reglas duras (nunca se rompen) 1 a 8; Tu flujo de conversación (los 5 momentos); Plantilla del diagnóstico; Supuestos de toda proyección: explícitos y concretos; Siempre rango, nunca punto medio; Toda palanca se verifica antes de ofrecerla (fila 'sube tu base de cotización'); Toda palanca se verifica antes de ofrecerla.

**C10 | RPM · IND · M10+ · SC**

*Más de 10 años para pensionarse, sin capacidad de ahorro.*

> Soy independiente y hay meses que no alcanzo a pagar la PILA. ¿Cuánto me cuestan esos meses en la pensión?

- **Corpus: CUBIERTO.** Ref: reglas-rpm.md s.3 y s.5; independientes.md s.2, s.4 y s.7; supuestos-actuariales.md s.3 y s.5; sin-pension-alternativas.md s.2 a s.7.
- **Cálculo: CUBIERTO.** Ref: diagnosticar.py -> rpm.py; rpm/rais con --ibc-futuro y --densidad-futura; costo_y_retorno.py (aporte_mensual y costo_total sobre el IBC real).
- **Comportamiento: PARCIAL.** Ref: Reglas duras (nunca se rompen) 1 a 8; Tu flujo de conversación (los 5 momentos); Plantilla del diagnóstico; Supuestos de toda proyección: explícitos y concretos; Siempre rango, nunca punto medio; Toda palanca se verifica antes de ofrecerla (fila 'sube tu base de cotización'). Falta: la tabla de accionabilidad verifica régimen, edad e ingreso, no capacidad de pago; la regla de segmento de BEPS ('ofrecerlo a alguien con capacidad de pago es un error de segmento') vive en aportes-voluntarios-y-sobrecotizacion.md s.5, no en el system-prompt.

**C11 | RPM · IND · M10- · CA**

*Menos de 10 años, con capacidad de ahorro.*

> Tengo 54 años, soy contratista y estoy en Colpensiones. Puedo poner $2.000.000 más al mes: ¿hasta dónde puedo subir mi base sin meterme en problemas?

- **Corpus: CUBIERTO.** Ref: reglas-rpm.md s.3 y s.5; independientes.md s.2, s.4 y s.7; reglas-traslados.md s.1; aportes-voluntarios-y-sobrecotizacion.md s.2 y s.3.
- **Cálculo: PARCIAL.** Ref: diagnosticar.py -> rpm.py; rpm/rais con --ibc-futuro y --densidad-futura; costo_y_retorno.py (aporte_mensual y costo_total sobre el IBC real); costo_y_retorno.py (tabla_de_escenarios: cuánto cuesta cada alternativa y en cuántos meses se recupera). Falta: costo_y_retorno.py resuelve el costo y el breakeven de sobrecotizar, pero ningún módulo modela el aporte voluntario propiamente dicho (rendimiento en la cuenta, comisión de la AFP, beneficio tributario del art. 126-1), que es la otra mitad de la decisión de quien tiene excedente.
- **Comportamiento: CUBIERTO.** Ref: Reglas duras (nunca se rompen) 1 a 8; Tu flujo de conversación (los 5 momentos); Plantilla del diagnóstico; Supuestos de toda proyección: explícitos y concretos; Siempre rango, nunca punto medio; Toda palanca se verifica antes de ofrecerla (fila 'sube tu base de cotización'); Toda palanca se verifica antes de ofrecerla.

**C12 | RPM · IND · M10- · SC**

*Menos de 10 años, sin capacidad de ahorro.*

> Tengo 56 años, soy independiente en Colpensiones y voy en 900 semanas. ¿Alcanzo o mejor me olvido de la pensión?

- **Corpus: CUBIERTO.** Ref: reglas-rpm.md s.3 y s.5; independientes.md s.2, s.4 y s.7; reglas-traslados.md s.1; sin-pension-alternativas.md s.2 a s.7.
- **Cálculo: PARCIAL.** Ref: diagnosticar.py -> rpm.py; rpm/rais con --ibc-futuro y --densidad-futura; costo_y_retorno.py (aporte_mensual y costo_total sobre el IBC real). Falta: rpm.py nombra la indemnización sustitutiva como camino (línea 332) pero no calcula su monto.
- **Comportamiento: PARCIAL.** Ref: Reglas duras (nunca se rompen) 1 a 8; Tu flujo de conversación (los 5 momentos); Plantilla del diagnóstico; Supuestos de toda proyección: explícitos y concretos; Siempre rango, nunca punto medio; Toda palanca se verifica antes de ofrecerla (fila 'sube tu base de cotización'). Falta: la tabla de accionabilidad verifica régimen, edad e ingreso, no capacidad de pago; la regla de segmento de BEPS ('ofrecerlo a alguien con capacidad de pago es un error de segmento') vive en aportes-voluntarios-y-sobrecotizacion.md s.5, no en el system-prompt.

**C13 | RPM · IND · CUM · CA**

*Ya cumple requisitos, con capacidad de ahorro.*

> Ya completé las semanas en Colpensiones y sigo facturando bien. ¿Me conviene dejar de cotizar o seguir un tiempo más?

- **Corpus: CUBIERTO.** Ref: reglas-rpm.md s.3 y s.5; independientes.md s.2, s.4 y s.7; reclamacion-y-defensa.md s.2 y s.3; aportes-voluntarios-y-sobrecotizacion.md s.2 y s.3.
- **Cálculo: PARCIAL.** Ref: diagnosticar.py -> rpm.py; rpm/rais con --ibc-futuro y --densidad-futura; costo_y_retorno.py (aporte_mensual y costo_total sobre el IBC real); costo_y_retorno.py (breakeven_meses y ganancia_neta: seguir cotizando vs. reclamar ya); costo_y_retorno.py (tabla_de_escenarios: cuánto cuesta cada alternativa y en cuántos meses se recupera). Falta: rpm.py no implementa el piso legal del 55% de tasa de reemplazo (kit-contexto/README.md, bloque 2 punto 7); costo_y_retorno.py resuelve el costo y el breakeven de sobrecotizar, pero ningún módulo modela el aporte voluntario propiamente dicho (rendimiento en la cuenta, comisión de la AFP, beneficio tributario del art. 126-1), que es la otra mitad de la decisión de quien tiene excedente.
- **Comportamiento: PARCIAL.** Ref: Reglas duras (nunca se rompen) 1 a 8; Tu flujo de conversación (los 5 momentos); Plantilla del diagnóstico; Supuestos de toda proyección: explícitos y concretos; Siempre rango, nunca punto medio; Toda palanca se verifica antes de ofrecerla (fila 'sube tu base de cotización'); Toda palanca se verifica antes de ofrecerla. Falta: el menú de palancas de 'Toda palanca se verifica antes de ofrecerla' solo contempla 'cerca de cumplir requisitos'; no hay plantilla ni cierre para quien YA cumple, cuyo bloque 2 no es una proyección sino una decisión de cuándo reclamar.

**C14 | RPM · IND · CUM · SC**

*Ya cumple requisitos, sin capacidad de ahorro.*

> Cumplí requisitos en Colpensiones pero llevo dos años sin pagar PILA. ¿Eso me tumba la solicitud?

- **Corpus: CUBIERTO.** Ref: reglas-rpm.md s.3 y s.5; independientes.md s.2, s.4 y s.7; reclamacion-y-defensa.md s.2 y s.3; sin-pension-alternativas.md s.2 a s.7.
- **Cálculo: PARCIAL.** Ref: diagnosticar.py -> rpm.py; rpm/rais con --ibc-futuro y --densidad-futura; costo_y_retorno.py (aporte_mensual y costo_total sobre el IBC real); costo_y_retorno.py (breakeven_meses y ganancia_neta: seguir cotizando vs. reclamar ya). Falta: rpm.py no implementa el piso legal del 55% de tasa de reemplazo (kit-contexto/README.md, bloque 2 punto 7); rpm.py nombra la indemnización sustitutiva como camino (línea 332) pero no calcula su monto.
- **Comportamiento: PARCIAL.** Ref: Reglas duras (nunca se rompen) 1 a 8; Tu flujo de conversación (los 5 momentos); Plantilla del diagnóstico; Supuestos de toda proyección: explícitos y concretos; Siempre rango, nunca punto medio; Toda palanca se verifica antes de ofrecerla (fila 'sube tu base de cotización'). Falta: el menú de palancas de 'Toda palanca se verifica antes de ofrecerla' solo contempla 'cerca de cumplir requisitos'; no hay plantilla ni cierre para quien YA cumple, cuyo bloque 2 no es una proyección sino una decisión de cuándo reclamar; la tabla de accionabilidad verifica régimen, edad e ingreso, no capacidad de pago; la regla de segmento de BEPS ('ofrecerlo a alguien con capacidad de pago es un error de segmento') vive en aportes-voluntarios-y-sobrecotizacion.md s.5, no en el system-prompt.

**C15 | RPM · IND · PEN · CA**

*Ya pensionado, con capacidad de ahorro.*

> Estoy pensionado por Colpensiones y sigo facturando como independiente. ¿Tengo que seguir pagando aportes?

- **Corpus: PARCIAL.** Ref: reglas-rpm.md s.3 y s.5; independientes.md s.2, s.4 y s.7; vida-del-pensionado.md s.1 a s.5 + tributario-pensional.md s.2 y s.3; aportes-voluntarios-y-sobrecotizacion.md s.2 y s.3. Falta: para el pensionado de Colpensiones con excedente, el corpus solo dice que el ahorro fuera del sistema no es pensión y lo declara fuera de alcance (aportes-voluntarios-y-sobrecotizacion.md s.5).
- **Cálculo: PARCIAL.** Ref: diagnosticar.py -> rpm.py; rpm/rais con --ibc-futuro y --densidad-futura; costo_y_retorno.py (aporte_mensual y costo_total sobre el IBC real); costo_y_retorno.py (mesada_neta y tarifa_salud_pensionado); costo_y_retorno.py (tabla_de_escenarios: cuánto cuesta cada alternativa y en cuántos meses se recupera). Falta: costo_y_retorno.py ya descuenta salud de la mesada, pero ningún módulo calcula reajuste anual, retención en la fuente, mesada 14 ni excedentes de libre disponibilidad, y diagnosticar.py está construido para proyectar hacia la pensión, no desde ella; costo_y_retorno.py resuelve el costo y el breakeven de sobrecotizar, pero ningún módulo modela el aporte voluntario propiamente dicho (rendimiento en la cuenta, comisión de la AFP, beneficio tributario del art. 126-1), que es la otra mitad de la decisión de quien tiene excedente.
- **Comportamiento: HUECO.** Ref: Reglas duras (nunca se rompen) 1 a 8; Tu flujo de conversación (los 5 momentos); Plantilla del diagnóstico; Supuestos de toda proyección: explícitos y concretos; Siempre rango, nunca punto medio; Toda palanca se verifica antes de ofrecerla (fila 'sube tu base de cotización'). Falta: no hay flujo ni plantilla para un usuario ya pensionado; la bienvenida de 'Lo que el usuario nunca ve' (cerrada el 2026-07-20) promete 'cuándo y con qué monto te vas a pensionar', que a él no le aplica.

**C16 | RPM · IND · PEN · SC**

*Ya pensionado, sin capacidad de ahorro.*

> Me pensioné con Colpensiones y sigo trabajando por cuenta propia. ¿Me toca pagar salud dos veces?

- **Corpus: CUBIERTO.** Ref: reglas-rpm.md s.3 y s.5; independientes.md s.2, s.4 y s.7; vida-del-pensionado.md s.1 a s.5 + tributario-pensional.md s.2 y s.3; sin-pension-alternativas.md s.2 a s.7.
- **Cálculo: PARCIAL.** Ref: diagnosticar.py -> rpm.py; rpm/rais con --ibc-futuro y --densidad-futura; costo_y_retorno.py (aporte_mensual y costo_total sobre el IBC real); costo_y_retorno.py (mesada_neta y tarifa_salud_pensionado). Falta: costo_y_retorno.py ya descuenta salud de la mesada, pero ningún módulo calcula reajuste anual, retención en la fuente, mesada 14 ni excedentes de libre disponibilidad, y diagnosticar.py está construido para proyectar hacia la pensión, no desde ella.
- **Comportamiento: HUECO.** Ref: Reglas duras (nunca se rompen) 1 a 8; Tu flujo de conversación (los 5 momentos); Plantilla del diagnóstico; Supuestos de toda proyección: explícitos y concretos; Siempre rango, nunca punto medio; Toda palanca se verifica antes de ofrecerla (fila 'sube tu base de cotización'). Falta: no hay flujo ni plantilla para un usuario ya pensionado; la bienvenida de 'Lo que el usuario nunca ve' (cerrada el 2026-07-20) promete 'cuándo y con qué monto te vas a pensionar', que a él no le aplica; la tabla de accionabilidad verifica régimen, edad e ingreso, no capacidad de pago; la regla de segmento de BEPS ('ofrecerlo a alguien con capacidad de pago es un error de segmento') vive en aportes-voluntarios-y-sobrecotizacion.md s.5, no en el system-prompt.

#### REN: Rentista de capital

**C17 | RPM · REN · M10+ · CA**

*Más de 10 años para pensionarse, con capacidad de ahorro.*

> Vivo de arriendos y dividendos, tengo 40 años y nunca he cotizado a Colpensiones. ¿Estoy obligado y sobre cuánto?

- **Corpus: PARCIAL.** Ref: reglas-rpm.md s.3 y s.5; independientes.md s.3; supuestos-actuariales.md s.3 y s.5; aportes-voluntarios-y-sobrecotizacion.md s.2 y s.3. Falta: el rentista tiene una sola sección (independientes.md s.3), con [VERIFICAR] abierto sobre el fundamento y sin tratamiento de rentas mixtas.
- **Cálculo: PARCIAL.** Ref: diagnosticar.py -> rpm.py; router.py (sin regla propia); costo_y_retorno.py (tabla_de_escenarios: cuánto cuesta cada alternativa y en cuántos meses se recupera). Falta: ningún módulo traduce rentas de capital a base de cotización; se aproxima a mano con --ibc-futuro y los coeficientes de presunción están fuera de alcance V1 (independientes.md s.8); costo_y_retorno.py resuelve el costo y el breakeven de sobrecotizar, pero ningún módulo modela el aporte voluntario propiamente dicho (rendimiento en la cuenta, comisión de la AFP, beneficio tributario del art. 126-1), que es la otra mitad de la decisión de quien tiene excedente.
- **Comportamiento: PARCIAL.** Ref: Reglas duras (nunca se rompen) 1 a 8; Tu flujo de conversación (los 5 momentos); Plantilla del diagnóstico; Supuestos de toda proyección: explícitos y concretos; Siempre rango, nunca punto medio; Toda palanca se verifica antes de ofrecerla. Falta: la tabla de accionabilidad de 'Toda palanca se verifica antes de ofrecerla' solo contempla 'sea independiente y tenga ingreso que lo respalde'; la distinción entre patrimonio y renta vive en independientes.md s.3, no en el system-prompt.

**C18 | RPM · REN · M10+ · SC**

*Más de 10 años para pensionarse, sin capacidad de ahorro.*

> No trabajo, vivo de un local que arriendo por $1.800.000. ¿Con eso puedo cotizar a Colpensiones y pensionarme?

- **Corpus: PARCIAL.** Ref: reglas-rpm.md s.3 y s.5; independientes.md s.3; supuestos-actuariales.md s.3 y s.5; sin-pension-alternativas.md s.2 a s.7. Falta: el rentista tiene una sola sección (independientes.md s.3), con [VERIFICAR] abierto sobre el fundamento y sin tratamiento de rentas mixtas.
- **Cálculo: PARCIAL.** Ref: diagnosticar.py -> rpm.py; router.py (sin regla propia). Falta: ningún módulo traduce rentas de capital a base de cotización; se aproxima a mano con --ibc-futuro y los coeficientes de presunción están fuera de alcance V1 (independientes.md s.8).
- **Comportamiento: PARCIAL.** Ref: Reglas duras (nunca se rompen) 1 a 8; Tu flujo de conversación (los 5 momentos); Plantilla del diagnóstico; Supuestos de toda proyección: explícitos y concretos; Siempre rango, nunca punto medio. Falta: la tabla de accionabilidad de 'Toda palanca se verifica antes de ofrecerla' solo contempla 'sea independiente y tenga ingreso que lo respalde'; la distinción entre patrimonio y renta vive en independientes.md s.3, no en el system-prompt; la tabla de accionabilidad verifica régimen, edad e ingreso, no capacidad de pago; la regla de segmento de BEPS ('ofrecerlo a alguien con capacidad de pago es un error de segmento') vive en aportes-voluntarios-y-sobrecotizacion.md s.5, no en el system-prompt.

**C19 | RPM · REN · M10- · CA**

*Menos de 10 años, con capacidad de ahorro.*

> Tengo 53 años y vivo de rentas y de mi patrimonio. ¿Puedo cotizar a Colpensiones sobre lo que tengo ahorrado?

- **Corpus: PARCIAL.** Ref: reglas-rpm.md s.3 y s.5; independientes.md s.3; reglas-traslados.md s.1; aportes-voluntarios-y-sobrecotizacion.md s.2 y s.3. Falta: el rentista tiene una sola sección (independientes.md s.3), con [VERIFICAR] abierto sobre el fundamento y sin tratamiento de rentas mixtas.
- **Cálculo: PARCIAL.** Ref: diagnosticar.py -> rpm.py; router.py (sin regla propia); costo_y_retorno.py (tabla_de_escenarios: cuánto cuesta cada alternativa y en cuántos meses se recupera). Falta: ningún módulo traduce rentas de capital a base de cotización; se aproxima a mano con --ibc-futuro y los coeficientes de presunción están fuera de alcance V1 (independientes.md s.8); costo_y_retorno.py resuelve el costo y el breakeven de sobrecotizar, pero ningún módulo modela el aporte voluntario propiamente dicho (rendimiento en la cuenta, comisión de la AFP, beneficio tributario del art. 126-1), que es la otra mitad de la decisión de quien tiene excedente.
- **Comportamiento: PARCIAL.** Ref: Reglas duras (nunca se rompen) 1 a 8; Tu flujo de conversación (los 5 momentos); Plantilla del diagnóstico; Supuestos de toda proyección: explícitos y concretos; Siempre rango, nunca punto medio; Toda palanca se verifica antes de ofrecerla. Falta: la tabla de accionabilidad de 'Toda palanca se verifica antes de ofrecerla' solo contempla 'sea independiente y tenga ingreso que lo respalde'; la distinción entre patrimonio y renta vive en independientes.md s.3, no en el system-prompt.

**C20 | RPM · REN · M10- · SC**

*Menos de 10 años, sin capacidad de ahorro.*

> Tengo 55 años, mis únicos ingresos son unos arriendos pequeños y tengo 400 semanas en Colpensiones. ¿Me sirve seguir cotizando?

- **Corpus: PARCIAL.** Ref: reglas-rpm.md s.3 y s.5; independientes.md s.3; reglas-traslados.md s.1; sin-pension-alternativas.md s.2 a s.7. Falta: el rentista tiene una sola sección (independientes.md s.3), con [VERIFICAR] abierto sobre el fundamento y sin tratamiento de rentas mixtas.
- **Cálculo: PARCIAL.** Ref: diagnosticar.py -> rpm.py; router.py (sin regla propia). Falta: ningún módulo traduce rentas de capital a base de cotización; se aproxima a mano con --ibc-futuro y los coeficientes de presunción están fuera de alcance V1 (independientes.md s.8); rpm.py nombra la indemnización sustitutiva como camino (línea 332) pero no calcula su monto.
- **Comportamiento: PARCIAL.** Ref: Reglas duras (nunca se rompen) 1 a 8; Tu flujo de conversación (los 5 momentos); Plantilla del diagnóstico; Supuestos de toda proyección: explícitos y concretos; Siempre rango, nunca punto medio. Falta: la tabla de accionabilidad de 'Toda palanca se verifica antes de ofrecerla' solo contempla 'sea independiente y tenga ingreso que lo respalde'; la distinción entre patrimonio y renta vive en independientes.md s.3, no en el system-prompt; la tabla de accionabilidad verifica régimen, edad e ingreso, no capacidad de pago; la regla de segmento de BEPS ('ofrecerlo a alguien con capacidad de pago es un error de segmento') vive en aportes-voluntarios-y-sobrecotizacion.md s.5, no en el system-prompt.
- **Propuesta: FUERA DE ALCANCE.** Rentista de 55 años con 400 semanas y arriendos pequeños: ningún camino del sistema lo lleva a pensión (necesitaría 900 semanas más en 7 años). El valor no está en el diagnóstico sino en indemnización sustitutiva o BEPS, y rpm.py no calcula el monto de la indemnización. Atender la pregunta con la calculadora actual produce un número sin decisión detrás.

**C21 | RPM · REN · CUM · CA**

*Ya cumple requisitos, con capacidad de ahorro.*

> Ya tengo edad y semanas en Colpensiones y vivo de rentas. ¿Pedir la pensión me cambia algo en impuestos?

- **Corpus: PARCIAL.** Ref: reglas-rpm.md s.3 y s.5; independientes.md s.3; reclamacion-y-defensa.md s.2 y s.3; aportes-voluntarios-y-sobrecotizacion.md s.2 y s.3. Falta: el rentista tiene una sola sección (independientes.md s.3), con [VERIFICAR] abierto sobre el fundamento y sin tratamiento de rentas mixtas.
- **Cálculo: PARCIAL.** Ref: diagnosticar.py -> rpm.py; router.py (sin regla propia); costo_y_retorno.py (breakeven_meses y ganancia_neta: seguir cotizando vs. reclamar ya); costo_y_retorno.py (tabla_de_escenarios: cuánto cuesta cada alternativa y en cuántos meses se recupera). Falta: ningún módulo traduce rentas de capital a base de cotización; se aproxima a mano con --ibc-futuro y los coeficientes de presunción están fuera de alcance V1 (independientes.md s.8); rpm.py no implementa el piso legal del 55% de tasa de reemplazo (kit-contexto/README.md, bloque 2 punto 7); costo_y_retorno.py resuelve el costo y el breakeven de sobrecotizar, pero ningún módulo modela el aporte voluntario propiamente dicho (rendimiento en la cuenta, comisión de la AFP, beneficio tributario del art. 126-1), que es la otra mitad de la decisión de quien tiene excedente.
- **Comportamiento: PARCIAL.** Ref: Reglas duras (nunca se rompen) 1 a 8; Tu flujo de conversación (los 5 momentos); Plantilla del diagnóstico; Supuestos de toda proyección: explícitos y concretos; Siempre rango, nunca punto medio; Toda palanca se verifica antes de ofrecerla. Falta: la tabla de accionabilidad de 'Toda palanca se verifica antes de ofrecerla' solo contempla 'sea independiente y tenga ingreso que lo respalde'; la distinción entre patrimonio y renta vive en independientes.md s.3, no en el system-prompt; el menú de palancas de 'Toda palanca se verifica antes de ofrecerla' solo contempla 'cerca de cumplir requisitos'; no hay plantilla ni cierre para quien YA cumple, cuyo bloque 2 no es una proyección sino una decisión de cuándo reclamar.

**C22 | RPM · REN · CUM · SC**

*Ya cumple requisitos, sin capacidad de ahorro.*

> Cumplo requisitos en Colpensiones, vivo de un arriendo y ya no cotizo hace años. ¿Igual me pensiono?

- **Corpus: PARCIAL.** Ref: reglas-rpm.md s.3 y s.5; independientes.md s.3; reclamacion-y-defensa.md s.2 y s.3; sin-pension-alternativas.md s.2 a s.7. Falta: el rentista tiene una sola sección (independientes.md s.3), con [VERIFICAR] abierto sobre el fundamento y sin tratamiento de rentas mixtas.
- **Cálculo: PARCIAL.** Ref: diagnosticar.py -> rpm.py; router.py (sin regla propia); costo_y_retorno.py (breakeven_meses y ganancia_neta: seguir cotizando vs. reclamar ya). Falta: ningún módulo traduce rentas de capital a base de cotización; se aproxima a mano con --ibc-futuro y los coeficientes de presunción están fuera de alcance V1 (independientes.md s.8); rpm.py no implementa el piso legal del 55% de tasa de reemplazo (kit-contexto/README.md, bloque 2 punto 7); rpm.py nombra la indemnización sustitutiva como camino (línea 332) pero no calcula su monto.
- **Comportamiento: PARCIAL.** Ref: Reglas duras (nunca se rompen) 1 a 8; Tu flujo de conversación (los 5 momentos); Plantilla del diagnóstico; Supuestos de toda proyección: explícitos y concretos; Siempre rango, nunca punto medio. Falta: la tabla de accionabilidad de 'Toda palanca se verifica antes de ofrecerla' solo contempla 'sea independiente y tenga ingreso que lo respalde'; la distinción entre patrimonio y renta vive en independientes.md s.3, no en el system-prompt; el menú de palancas de 'Toda palanca se verifica antes de ofrecerla' solo contempla 'cerca de cumplir requisitos'; no hay plantilla ni cierre para quien YA cumple, cuyo bloque 2 no es una proyección sino una decisión de cuándo reclamar; la tabla de accionabilidad verifica régimen, edad e ingreso, no capacidad de pago; la regla de segmento de BEPS ('ofrecerlo a alguien con capacidad de pago es un error de segmento') vive en aportes-voluntarios-y-sobrecotizacion.md s.5, no en el system-prompt.

**C23 | RPM · REN · PEN · CA**

*Ya pensionado, con capacidad de ahorro.*

> Estoy pensionado por Colpensiones y recibo dividendos de una empresa. ¿Tengo que seguir cotizando por esos ingresos?

- **Corpus: PARCIAL.** Ref: reglas-rpm.md s.3 y s.5; independientes.md s.3; vida-del-pensionado.md s.1 a s.5 + tributario-pensional.md s.2 y s.3; aportes-voluntarios-y-sobrecotizacion.md s.2 y s.3; independientes.md s.3 (pensionados entre los no obligados). Falta: para el pensionado de Colpensiones con excedente, el corpus solo dice que el ahorro fuera del sistema no es pensión y lo declara fuera de alcance (aportes-voluntarios-y-sobrecotizacion.md s.5).
- **Cálculo: PARCIAL.** Ref: diagnosticar.py -> rpm.py; router.py (sin regla propia); costo_y_retorno.py (mesada_neta y tarifa_salud_pensionado); costo_y_retorno.py (tabla_de_escenarios: cuánto cuesta cada alternativa y en cuántos meses se recupera). Falta: ningún módulo traduce rentas de capital a base de cotización; se aproxima a mano con --ibc-futuro y los coeficientes de presunción están fuera de alcance V1 (independientes.md s.8); costo_y_retorno.py ya descuenta salud de la mesada, pero ningún módulo calcula reajuste anual, retención en la fuente, mesada 14 ni excedentes de libre disponibilidad, y diagnosticar.py está construido para proyectar hacia la pensión, no desde ella; costo_y_retorno.py resuelve el costo y el breakeven de sobrecotizar, pero ningún módulo modela el aporte voluntario propiamente dicho (rendimiento en la cuenta, comisión de la AFP, beneficio tributario del art. 126-1), que es la otra mitad de la decisión de quien tiene excedente.
- **Comportamiento: HUECO.** Ref: Reglas duras (nunca se rompen) 1 a 8; Tu flujo de conversación (los 5 momentos); Plantilla del diagnóstico; Supuestos de toda proyección: explícitos y concretos; Siempre rango, nunca punto medio. Falta: la tabla de accionabilidad de 'Toda palanca se verifica antes de ofrecerla' solo contempla 'sea independiente y tenga ingreso que lo respalde'; la distinción entre patrimonio y renta vive en independientes.md s.3, no en el system-prompt; no hay flujo ni plantilla para un usuario ya pensionado; la bienvenida de 'Lo que el usuario nunca ve' (cerrada el 2026-07-20) promete 'cuándo y con qué monto te vas a pensionar', que a él no le aplica.

**C24 | RPM · REN · PEN · SC**

*Ya pensionado, sin capacidad de ahorro.*

> Soy pensionado de Colpensiones y arriendo un cuarto de mi casa. ¿Eso me obliga a declarar renta?

- **Corpus: CUBIERTO.** Ref: reglas-rpm.md s.3 y s.5; independientes.md s.3; vida-del-pensionado.md s.1 a s.5 + tributario-pensional.md s.2 y s.3; sin-pension-alternativas.md s.2 a s.7; independientes.md s.3 (pensionados entre los no obligados).
- **Cálculo: PARCIAL.** Ref: diagnosticar.py -> rpm.py; router.py (sin regla propia); costo_y_retorno.py (mesada_neta y tarifa_salud_pensionado). Falta: ningún módulo traduce rentas de capital a base de cotización; se aproxima a mano con --ibc-futuro y los coeficientes de presunción están fuera de alcance V1 (independientes.md s.8); costo_y_retorno.py ya descuenta salud de la mesada, pero ningún módulo calcula reajuste anual, retención en la fuente, mesada 14 ni excedentes de libre disponibilidad, y diagnosticar.py está construido para proyectar hacia la pensión, no desde ella.
- **Comportamiento: HUECO.** Ref: Reglas duras (nunca se rompen) 1 a 8; Tu flujo de conversación (los 5 momentos); Plantilla del diagnóstico; Supuestos de toda proyección: explícitos y concretos; Siempre rango, nunca punto medio. Falta: la tabla de accionabilidad de 'Toda palanca se verifica antes de ofrecerla' solo contempla 'sea independiente y tenga ingreso que lo respalde'; la distinción entre patrimonio y renta vive en independientes.md s.3, no en el system-prompt; no hay flujo ni plantilla para un usuario ya pensionado; la bienvenida de 'Lo que el usuario nunca ve' (cerrada el 2026-07-20) promete 'cuándo y con qué monto te vas a pensionar', que a él no le aplica; la tabla de accionabilidad verifica régimen, edad e ingreso, no capacidad de pago; la regla de segmento de BEPS ('ofrecerlo a alguien con capacidad de pago es un error de segmento') vive en aportes-voluntarios-y-sobrecotizacion.md s.5, no en el system-prompt.
- **Propuesta: FUERA DE ALCANCE.** La pregunta es de obligación de declarar renta, no de pensión. La respuesta depende de patrimonio bruto, consignaciones y compras del año, datos que Júbilo no pide ni debe pedir. tributario-pensional.md s.2 da el marco de la renta exenta, no el test de declarante. Salida correcta: derivar a contador.

#### MIX: Mixto o historia partida

**C25 | RPM · MIX · M10+ · CA**

*Más de 10 años para pensionarse, con capacidad de ahorro.*

> Trabajé 8 años en una alcaldía, luego en Colpensiones y ahora soy independiente. ¿Esos años públicos me cuentan?

- **Corpus: PARCIAL.** Ref: reglas-rpm.md s.3 y s.5; reglas-traslados.md s.5 + bonos-tiempos-publicos-y-exterior.md s.1 y s.8; supuestos-actuariales.md s.3 y s.5; aportes-voluntarios-y-sobrecotizacion.md s.2 y s.3. Falta: no hay documento que ordene la historia partida: las piezas están repartidas en traslados, bonos y reglas-rais s.7.
- **Cálculo: PARCIAL.** Ref: diagnosticar.py -> rpm.py; comparador.py; costo_y_retorno.py (tabla_de_escenarios: cuánto cuesta cada alternativa y en cuántos meses se recupera). Falta: comparador.py simula el saldo RAIS con el 11,5% e ignora bono pensional y comisiones (calculadora/README.md, aprox. 4); no consolida dos historias laborales reales; costo_y_retorno.py resuelve el costo y el breakeven de sobrecotizar, pero ningún módulo modela el aporte voluntario propiamente dicho (rendimiento en la cuenta, comisión de la AFP, beneficio tributario del art. 126-1), que es la otra mitad de la decisión de quien tiene excedente.
- **Comportamiento: HUECO.** Ref: Reglas duras (nunca se rompen) 1 a 8; Tu flujo de conversación (los 5 momentos); Plantilla del diagnóstico; Supuestos de toda proyección: explícitos y concretos; Siempre rango, nunca punto medio; Toda palanca se verifica antes de ofrecerla. Falta: el momento 2 de 'Tu flujo de conversación' asume UN documento y UN total impreso para la verificación cruzada (regla dura 4); no hay regla para dos historias laborales de dos administradoras.

**C26 | RPM · MIX · M10+ · SC**

*Más de 10 años para pensionarse, sin capacidad de ahorro.*

> Estuve en un fondo privado, me pasé a Colpensiones y hay años que no aparecen en ningún lado. ¿Dónde quedaron mis semanas?

- **Corpus: PARCIAL.** Ref: reglas-rpm.md s.3 y s.5; reglas-traslados.md s.5 + bonos-tiempos-publicos-y-exterior.md s.1 y s.8; supuestos-actuariales.md s.3 y s.5; sin-pension-alternativas.md s.2 a s.7. Falta: no hay documento que ordene la historia partida: las piezas están repartidas en traslados, bonos y reglas-rais s.7.
- **Cálculo: PARCIAL.** Ref: diagnosticar.py -> rpm.py; comparador.py. Falta: comparador.py simula el saldo RAIS con el 11,5% e ignora bono pensional y comisiones (calculadora/README.md, aprox. 4); no consolida dos historias laborales reales.
- **Comportamiento: HUECO.** Ref: Reglas duras (nunca se rompen) 1 a 8; Tu flujo de conversación (los 5 momentos); Plantilla del diagnóstico; Supuestos de toda proyección: explícitos y concretos; Siempre rango, nunca punto medio. Falta: el momento 2 de 'Tu flujo de conversación' asume UN documento y UN total impreso para la verificación cruzada (regla dura 4); no hay regla para dos historias laborales de dos administradoras; la tabla de accionabilidad verifica régimen, edad e ingreso, no capacidad de pago; la regla de segmento de BEPS ('ofrecerlo a alguien con capacidad de pago es un error de segmento') vive en aportes-voluntarios-y-sobrecotizacion.md s.5, no en el system-prompt.

**C27 | RPM · MIX · M10- · CA**

*Menos de 10 años, con capacidad de ahorro.*

> Tengo 54 años, coticé 15 años en un fondo privado y 8 en Colpensiones. ¿Me conviene moverme antes de que se cierre la ventana?

- **Corpus: PARCIAL.** Ref: reglas-rpm.md s.3 y s.5; reglas-traslados.md s.5 + bonos-tiempos-publicos-y-exterior.md s.1 y s.8; reglas-traslados.md s.1; aportes-voluntarios-y-sobrecotizacion.md s.2 y s.3. Falta: no hay documento que ordene la historia partida: las piezas están repartidas en traslados, bonos y reglas-rais s.7.
- **Cálculo: PARCIAL.** Ref: diagnosticar.py -> rpm.py; comparador.py; costo_y_retorno.py (tabla_de_escenarios: cuánto cuesta cada alternativa y en cuántos meses se recupera). Falta: comparador.py simula el saldo RAIS con el 11,5% e ignora bono pensional y comisiones (calculadora/README.md, aprox. 4); no consolida dos historias laborales reales; costo_y_retorno.py resuelve el costo y el breakeven de sobrecotizar, pero ningún módulo modela el aporte voluntario propiamente dicho (rendimiento en la cuenta, comisión de la AFP, beneficio tributario del art. 126-1), que es la otra mitad de la decisión de quien tiene excedente.
- **Comportamiento: HUECO.** Ref: Reglas duras (nunca se rompen) 1 a 8; Tu flujo de conversación (los 5 momentos); Plantilla del diagnóstico; Supuestos de toda proyección: explícitos y concretos; Siempre rango, nunca punto medio; Toda palanca se verifica antes de ofrecerla. Falta: el momento 2 de 'Tu flujo de conversación' asume UN documento y UN total impreso para la verificación cruzada (regla dura 4); no hay regla para dos historias laborales de dos administradoras.

**C28 | RPM · MIX · M10- · SC**

*Menos de 10 años, sin capacidad de ahorro.*

> Coticé 6 años en España y el resto en Colpensiones. Tengo 53 años: ¿puedo sumar esas semanas?

- **Corpus: PARCIAL.** Ref: reglas-rpm.md s.3 y s.5; reglas-traslados.md s.5 + bonos-tiempos-publicos-y-exterior.md s.1 y s.8; reglas-traslados.md s.1; sin-pension-alternativas.md s.2 a s.7. Falta: no hay documento que ordene la historia partida: las piezas están repartidas en traslados, bonos y reglas-rais s.7.
- **Cálculo: PARCIAL.** Ref: diagnosticar.py -> rpm.py; comparador.py. Falta: comparador.py simula el saldo RAIS con el 11,5% e ignora bono pensional y comisiones (calculadora/README.md, aprox. 4); no consolida dos historias laborales reales; rpm.py nombra la indemnización sustitutiva como camino (línea 332) pero no calcula su monto.
- **Comportamiento: HUECO.** Ref: Reglas duras (nunca se rompen) 1 a 8; Tu flujo de conversación (los 5 momentos); Plantilla del diagnóstico; Supuestos de toda proyección: explícitos y concretos; Siempre rango, nunca punto medio. Falta: el momento 2 de 'Tu flujo de conversación' asume UN documento y UN total impreso para la verificación cruzada (regla dura 4); no hay regla para dos historias laborales de dos administradoras; la tabla de accionabilidad verifica régimen, edad e ingreso, no capacidad de pago; la regla de segmento de BEPS ('ofrecerlo a alguien con capacidad de pago es un error de segmento') vive en aportes-voluntarios-y-sobrecotizacion.md s.5, no en el system-prompt.
- **Propuesta: FUERA DE ALCANCE.** Historia partida con 6 años cotizados en España. Depende del Convenio Iberoamericano y de la discrepancia CMISS abierta en bonos-tiempos-publicos-y-exterior.md s.9 (¿elige el afiliado o aplica de oficio la entidad?). Sin esa respuesta legal, cualquier cifra es inventada.

**C29 | RPM · MIX · CUM · CA**

*Ya cumple requisitos, con capacidad de ahorro.*

> Tengo semanas en Colpensiones y saldo en otro fondo, y ya tengo la edad. ¿Quién me pensiona y con cuál plata?

- **Corpus: HUECO.** Ref: reglas-rpm.md s.3 y s.5; reglas-traslados.md s.5 + bonos-tiempos-publicos-y-exterior.md s.1 y s.8; reclamacion-y-defensa.md s.2 y s.3; aportes-voluntarios-y-sobrecotizacion.md s.2 y s.3. Falta: ningún documento resuelve quién reconoce la pensión cuando hay semanas en los dos regímenes y falta el bono; bonos-tiempos-publicos-y-exterior.md s.5 lo deja en [VERIFICAR].
- **Cálculo: PARCIAL.** Ref: diagnosticar.py -> rpm.py; comparador.py; costo_y_retorno.py (breakeven_meses y ganancia_neta: seguir cotizando vs. reclamar ya); costo_y_retorno.py (tabla_de_escenarios: cuánto cuesta cada alternativa y en cuántos meses se recupera). Falta: comparador.py simula el saldo RAIS con el 11,5% e ignora bono pensional y comisiones (calculadora/README.md, aprox. 4); no consolida dos historias laborales reales; rpm.py no implementa el piso legal del 55% de tasa de reemplazo (kit-contexto/README.md, bloque 2 punto 7); costo_y_retorno.py resuelve el costo y el breakeven de sobrecotizar, pero ningún módulo modela el aporte voluntario propiamente dicho (rendimiento en la cuenta, comisión de la AFP, beneficio tributario del art. 126-1), que es la otra mitad de la decisión de quien tiene excedente.
- **Comportamiento: HUECO.** Ref: Reglas duras (nunca se rompen) 1 a 8; Tu flujo de conversación (los 5 momentos); Plantilla del diagnóstico; Supuestos de toda proyección: explícitos y concretos; Siempre rango, nunca punto medio; Toda palanca se verifica antes de ofrecerla. Falta: el momento 2 de 'Tu flujo de conversación' asume UN documento y UN total impreso para la verificación cruzada (regla dura 4); no hay regla para dos historias laborales de dos administradoras; el menú de palancas de 'Toda palanca se verifica antes de ofrecerla' solo contempla 'cerca de cumplir requisitos'; no hay plantilla ni cierre para quien YA cumple, cuyo bloque 2 no es una proyección sino una decisión de cuándo reclamar.

**C30 | RPM · MIX · CUM · SC**

*Ya cumple requisitos, sin capacidad de ahorro.*

> Ya tengo 62 y las semanas en Colpensiones, pero me falta el bono pensional de cuando fui empleado público. ¿Puedo pedir la pensión igual?

- **Corpus: HUECO.** Ref: reglas-rpm.md s.3 y s.5; reglas-traslados.md s.5 + bonos-tiempos-publicos-y-exterior.md s.1 y s.8; reclamacion-y-defensa.md s.2 y s.3; sin-pension-alternativas.md s.2 a s.7. Falta: ningún documento resuelve quién reconoce la pensión cuando hay semanas en los dos regímenes y falta el bono; bonos-tiempos-publicos-y-exterior.md s.5 lo deja en [VERIFICAR].
- **Cálculo: PARCIAL.** Ref: diagnosticar.py -> rpm.py; comparador.py; costo_y_retorno.py (breakeven_meses y ganancia_neta: seguir cotizando vs. reclamar ya). Falta: comparador.py simula el saldo RAIS con el 11,5% e ignora bono pensional y comisiones (calculadora/README.md, aprox. 4); no consolida dos historias laborales reales; rpm.py no implementa el piso legal del 55% de tasa de reemplazo (kit-contexto/README.md, bloque 2 punto 7); rpm.py nombra la indemnización sustitutiva como camino (línea 332) pero no calcula su monto.
- **Comportamiento: HUECO.** Ref: Reglas duras (nunca se rompen) 1 a 8; Tu flujo de conversación (los 5 momentos); Plantilla del diagnóstico; Supuestos de toda proyección: explícitos y concretos; Siempre rango, nunca punto medio. Falta: el momento 2 de 'Tu flujo de conversación' asume UN documento y UN total impreso para la verificación cruzada (regla dura 4); no hay regla para dos historias laborales de dos administradoras; el menú de palancas de 'Toda palanca se verifica antes de ofrecerla' solo contempla 'cerca de cumplir requisitos'; no hay plantilla ni cierre para quien YA cumple, cuyo bloque 2 no es una proyección sino una decisión de cuándo reclamar; la tabla de accionabilidad verifica régimen, edad e ingreso, no capacidad de pago; la regla de segmento de BEPS ('ofrecerlo a alguien con capacidad de pago es un error de segmento') vive en aportes-voluntarios-y-sobrecotizacion.md s.5, no en el system-prompt.

**C31 | RPM · MIX · PEN · CA**

*Ya pensionado, con capacidad de ahorro.*

> Me pensioné con Colpensiones pero tengo un saldo viejo en un fondo privado de hace años. ¿Puedo sacar esa plata?

- **Corpus: PARCIAL.** Ref: reglas-rpm.md s.3 y s.5; reglas-traslados.md s.5 + bonos-tiempos-publicos-y-exterior.md s.1 y s.8; vida-del-pensionado.md s.1 a s.5 + tributario-pensional.md s.2 y s.3; aportes-voluntarios-y-sobrecotizacion.md s.2 y s.3. Falta: no hay documento que ordene la historia partida: las piezas están repartidas en traslados, bonos y reglas-rais s.7; para el pensionado de Colpensiones con excedente, el corpus solo dice que el ahorro fuera del sistema no es pensión y lo declara fuera de alcance (aportes-voluntarios-y-sobrecotizacion.md s.5).
- **Cálculo: PARCIAL.** Ref: diagnosticar.py -> rpm.py; comparador.py; costo_y_retorno.py (mesada_neta y tarifa_salud_pensionado); costo_y_retorno.py (tabla_de_escenarios: cuánto cuesta cada alternativa y en cuántos meses se recupera). Falta: comparador.py simula el saldo RAIS con el 11,5% e ignora bono pensional y comisiones (calculadora/README.md, aprox. 4); no consolida dos historias laborales reales; costo_y_retorno.py ya descuenta salud de la mesada, pero ningún módulo calcula reajuste anual, retención en la fuente, mesada 14 ni excedentes de libre disponibilidad, y diagnosticar.py está construido para proyectar hacia la pensión, no desde ella; costo_y_retorno.py resuelve el costo y el breakeven de sobrecotizar, pero ningún módulo modela el aporte voluntario propiamente dicho (rendimiento en la cuenta, comisión de la AFP, beneficio tributario del art. 126-1), que es la otra mitad de la decisión de quien tiene excedente.
- **Comportamiento: HUECO.** Ref: Reglas duras (nunca se rompen) 1 a 8; Tu flujo de conversación (los 5 momentos); Plantilla del diagnóstico; Supuestos de toda proyección: explícitos y concretos; Siempre rango, nunca punto medio. Falta: el momento 2 de 'Tu flujo de conversación' asume UN documento y UN total impreso para la verificación cruzada (regla dura 4); no hay regla para dos historias laborales de dos administradoras; no hay flujo ni plantilla para un usuario ya pensionado; la bienvenida de 'Lo que el usuario nunca ve' (cerrada el 2026-07-20) promete 'cuándo y con qué monto te vas a pensionar', que a él no le aplica.

**C32 | RPM · MIX · PEN · SC**

*Ya pensionado, sin capacidad de ahorro.*

> Estoy pensionado por Colpensiones y me dijeron que falta cobrar una cuota parte de una entidad pública. ¿Eso qué es y me afecta?

- **Corpus: PARCIAL.** Ref: reglas-rpm.md s.3 y s.5; reglas-traslados.md s.5 + bonos-tiempos-publicos-y-exterior.md s.1 y s.8; vida-del-pensionado.md s.1 a s.5 + tributario-pensional.md s.2 y s.3; sin-pension-alternativas.md s.2 a s.7. Falta: no hay documento que ordene la historia partida: las piezas están repartidas en traslados, bonos y reglas-rais s.7.
- **Cálculo: PARCIAL.** Ref: diagnosticar.py -> rpm.py; comparador.py; costo_y_retorno.py (mesada_neta y tarifa_salud_pensionado). Falta: comparador.py simula el saldo RAIS con el 11,5% e ignora bono pensional y comisiones (calculadora/README.md, aprox. 4); no consolida dos historias laborales reales; costo_y_retorno.py ya descuenta salud de la mesada, pero ningún módulo calcula reajuste anual, retención en la fuente, mesada 14 ni excedentes de libre disponibilidad, y diagnosticar.py está construido para proyectar hacia la pensión, no desde ella.
- **Comportamiento: HUECO.** Ref: Reglas duras (nunca se rompen) 1 a 8; Tu flujo de conversación (los 5 momentos); Plantilla del diagnóstico; Supuestos de toda proyección: explícitos y concretos; Siempre rango, nunca punto medio. Falta: el momento 2 de 'Tu flujo de conversación' asume UN documento y UN total impreso para la verificación cruzada (regla dura 4); no hay regla para dos historias laborales de dos administradoras; no hay flujo ni plantilla para un usuario ya pensionado; la bienvenida de 'Lo que el usuario nunca ve' (cerrada el 2026-07-20) promete 'cuándo y con qué monto te vas a pensionar', que a él no le aplica; la tabla de accionabilidad verifica régimen, edad e ingreso, no capacidad de pago; la regla de segmento de BEPS ('ofrecerlo a alguien con capacidad de pago es un error de segmento') vive en aportes-voluntarios-y-sobrecotizacion.md s.5, no en el system-prompt.
- **Propuesta: FUERA DE ALCANCE.** Cuota parte pensional pendiente de una entidad pública: es un trámite de cobro entre entidades que no cambia la mesada del usuario ni admite cálculo. Es asesoría jurídica de trámite, no diagnóstico pensional.

### Régimen RAIS (fondo privado)

#### EMP: Empleado

**C33 | RAIS · EMP · M10+ · CA**

*Más de 10 años para pensionarse, con capacidad de ahorro.*

> Tengo 38 años, llevo 12 cotizando en un fondo privado y me sobran como $800.000 al mes. ¿Meterle más plata ahí me sirve o mejor invierto por fuera?

- **Corpus: CUBIERTO.** Ref: reglas-rais.md s.3 y s.5; mora-y-correccion-historia-laboral.md s.1 y s.2; supuestos-actuariales.md s.3 y s.5; aportes-voluntarios-y-sobrecotizacion.md s.4.
- **Cálculo: PARCIAL.** Ref: diagnosticar.py -> rais.py; lagunas.py + recuperacion.py; costo_y_retorno.py (tabla_de_escenarios: cuánto cuesta cada alternativa y en cuántos meses se recupera). Falta: costo_y_retorno.py resuelve el costo y el breakeven de sobrecotizar, pero ningún módulo modela el aporte voluntario propiamente dicho (rendimiento en la cuenta, comisión de la AFP, beneficio tributario del art. 126-1), que es la otra mitad de la decisión de quien tiene excedente.
- **Comportamiento: CUBIERTO.** Ref: Reglas duras (nunca se rompen) 1 a 8; Tu flujo de conversación (los 5 momentos); Plantilla del diagnóstico; Supuestos de toda proyección: explícitos y concretos; Siempre rango, nunca punto medio; Los huecos y su recuperación salen de la calculadora, nunca de tu cuenta; Toda palanca se verifica antes de ofrecerla.

**C34 | RAIS · EMP · M10+ · SC**

*Más de 10 años para pensionarse, sin capacidad de ahorro.*

> Tengo 34 años y cotizo por el mínimo en un fondo privado. ¿Con eso cuánto me va a quedar de pensión y a qué edad?

- **Corpus: CUBIERTO.** Ref: reglas-rais.md s.3 y s.5; mora-y-correccion-historia-laboral.md s.1 y s.2; supuestos-actuariales.md s.3 y s.5; sin-pension-alternativas.md s.2 a s.7.
- **Cálculo: CUBIERTO.** Ref: diagnosticar.py -> rais.py; lagunas.py + recuperacion.py.
- **Comportamiento: PARCIAL.** Ref: Reglas duras (nunca se rompen) 1 a 8; Tu flujo de conversación (los 5 momentos); Plantilla del diagnóstico; Supuestos de toda proyección: explícitos y concretos; Siempre rango, nunca punto medio; Los huecos y su recuperación salen de la calculadora, nunca de tu cuenta. Falta: la tabla de accionabilidad verifica régimen, edad e ingreso, no capacidad de pago; la regla de segmento de BEPS ('ofrecerlo a alguien con capacidad de pago es un error de segmento') vive en aportes-voluntarios-y-sobrecotizacion.md s.5, no en el system-prompt.

**C35 | RAIS · EMP · M10- · CA**

*Menos de 10 años, con capacidad de ahorro.*

> Tengo 55 años, estoy en un fondo privado y acabo de vender un apartamento. ¿Puedo usar esa plata para mejorar mi pensión?

- **Corpus: CUBIERTO.** Ref: reglas-rais.md s.3 y s.5; mora-y-correccion-historia-laboral.md s.1 y s.2; reglas-traslados.md s.1; aportes-voluntarios-y-sobrecotizacion.md s.4.
- **Cálculo: PARCIAL.** Ref: diagnosticar.py -> rais.py; lagunas.py + recuperacion.py; costo_y_retorno.py (tabla_de_escenarios: cuánto cuesta cada alternativa y en cuántos meses se recupera). Falta: costo_y_retorno.py resuelve el costo y el breakeven de sobrecotizar, pero ningún módulo modela el aporte voluntario propiamente dicho (rendimiento en la cuenta, comisión de la AFP, beneficio tributario del art. 126-1), que es la otra mitad de la decisión de quien tiene excedente.
- **Comportamiento: CUBIERTO.** Ref: Reglas duras (nunca se rompen) 1 a 8; Tu flujo de conversación (los 5 momentos); Plantilla del diagnóstico; Supuestos de toda proyección: explícitos y concretos; Siempre rango, nunca punto medio; Los huecos y su recuperación salen de la calculadora, nunca de tu cuenta; Toda palanca se verifica antes de ofrecerla.

**C36 | RAIS · EMP · M10- · SC**

*Menos de 10 años, sin capacidad de ahorro.*

> Me faltan 6 años para los 62 y estoy en un fondo privado. Si me quedo sin trabajo mañana, ¿qué pasa con mi pensión?

- **Corpus: CUBIERTO.** Ref: reglas-rais.md s.3 y s.5; mora-y-correccion-historia-laboral.md s.1 y s.2; reglas-traslados.md s.1; sin-pension-alternativas.md s.2 a s.7.
- **Cálculo: CUBIERTO.** Ref: diagnosticar.py -> rais.py; lagunas.py + recuperacion.py.
- **Comportamiento: PARCIAL.** Ref: Reglas duras (nunca se rompen) 1 a 8; Tu flujo de conversación (los 5 momentos); Plantilla del diagnóstico; Supuestos de toda proyección: explícitos y concretos; Siempre rango, nunca punto medio; Los huecos y su recuperación salen de la calculadora, nunca de tu cuenta. Falta: la tabla de accionabilidad verifica régimen, edad e ingreso, no capacidad de pago; la regla de segmento de BEPS ('ofrecerlo a alguien con capacidad de pago es un error de segmento') vive en aportes-voluntarios-y-sobrecotizacion.md s.5, no en el system-prompt.

**C37 | RAIS · EMP · CUM · CA**

*Ya cumple requisitos, con capacidad de ahorro.*

> Ya tengo la edad y las semanas en un fondo privado, pero me quieren renovar el contrato. ¿Me pensiono ya o sigo trabajando un año más?

- **Corpus: CUBIERTO.** Ref: reglas-rais.md s.3 y s.5; mora-y-correccion-historia-laboral.md s.1 y s.2; modalidades-de-pension.md s.1, s.7 y s.14; aportes-voluntarios-y-sobrecotizacion.md s.4.
- **Cálculo: HUECO.** Ref: diagnosticar.py -> rais.py; lagunas.py + recuperacion.py; costo_y_retorno.py (breakeven_meses y ganancia_neta: seguir cotizando vs. reclamar ya). Falta: ningún módulo compara modalidades de pensión; rais.py entrega una renta vitalicia sin beneficiarios de sobrevivencia (calculadora/README.md, aprox. 1), que es justo la decisión de esa persona.
- **Comportamiento: PARCIAL.** Ref: Reglas duras (nunca se rompen) 1 a 8; Tu flujo de conversación (los 5 momentos); Plantilla del diagnóstico; Supuestos de toda proyección: explícitos y concretos; Siempre rango, nunca punto medio; Los huecos y su recuperación salen de la calculadora, nunca de tu cuenta; Toda palanca se verifica antes de ofrecerla. Falta: el menú de palancas de 'Toda palanca se verifica antes de ofrecerla' solo contempla 'cerca de cumplir requisitos'; no hay plantilla ni cierre para quien YA cumple, cuyo bloque 2 no es una proyección sino una decisión de cuándo reclamar.

**C38 | RAIS · EMP · CUM · SC**

*Ya cumple requisitos, sin capacidad de ahorro.*

> Cumplí requisitos en un fondo privado el mes pasado. ¿Cómo pido la pensión y cuánto se demoran en pagarme?

- **Corpus: CUBIERTO.** Ref: reglas-rais.md s.3 y s.5; mora-y-correccion-historia-laboral.md s.1 y s.2; modalidades-de-pension.md s.1, s.7 y s.14; sin-pension-alternativas.md s.2 a s.7.
- **Cálculo: HUECO.** Ref: diagnosticar.py -> rais.py; lagunas.py + recuperacion.py; costo_y_retorno.py (breakeven_meses y ganancia_neta: seguir cotizando vs. reclamar ya). Falta: ningún módulo compara modalidades de pensión; rais.py entrega una renta vitalicia sin beneficiarios de sobrevivencia (calculadora/README.md, aprox. 1), que es justo la decisión de esa persona.
- **Comportamiento: PARCIAL.** Ref: Reglas duras (nunca se rompen) 1 a 8; Tu flujo de conversación (los 5 momentos); Plantilla del diagnóstico; Supuestos de toda proyección: explícitos y concretos; Siempre rango, nunca punto medio; Los huecos y su recuperación salen de la calculadora, nunca de tu cuenta. Falta: el menú de palancas de 'Toda palanca se verifica antes de ofrecerla' solo contempla 'cerca de cumplir requisitos'; no hay plantilla ni cierre para quien YA cumple, cuyo bloque 2 no es una proyección sino una decisión de cuándo reclamar; la tabla de accionabilidad verifica régimen, edad e ingreso, no capacidad de pago; la regla de segmento de BEPS ('ofrecerlo a alguien con capacidad de pago es un error de segmento') vive en aportes-voluntarios-y-sobrecotizacion.md s.5, no en el system-prompt.

**C39 | RAIS · EMP · PEN · CA**

*Ya pensionado, con capacidad de ahorro.*

> Ya estoy pensionado por un fondo privado y sigo trabajando como empleado. ¿Me sirve seguir ahorrando en un fondo voluntario?

- **Corpus: CUBIERTO.** Ref: reglas-rais.md s.3 y s.5; mora-y-correccion-historia-laboral.md s.1 y s.2; vida-del-pensionado.md s.1 a s.5 + tributario-pensional.md s.2 y s.3; aportes-voluntarios-y-sobrecotizacion.md s.4.
- **Cálculo: PARCIAL.** Ref: diagnosticar.py -> rais.py; lagunas.py + recuperacion.py; costo_y_retorno.py (mesada_neta y tarifa_salud_pensionado); costo_y_retorno.py (tabla_de_escenarios: cuánto cuesta cada alternativa y en cuántos meses se recupera). Falta: costo_y_retorno.py ya descuenta salud de la mesada, pero ningún módulo calcula reajuste anual, retención en la fuente, mesada 14 ni excedentes de libre disponibilidad, y diagnosticar.py está construido para proyectar hacia la pensión, no desde ella; costo_y_retorno.py resuelve el costo y el breakeven de sobrecotizar, pero ningún módulo modela el aporte voluntario propiamente dicho (rendimiento en la cuenta, comisión de la AFP, beneficio tributario del art. 126-1), que es la otra mitad de la decisión de quien tiene excedente.
- **Comportamiento: HUECO.** Ref: Reglas duras (nunca se rompen) 1 a 8; Tu flujo de conversación (los 5 momentos); Plantilla del diagnóstico; Supuestos de toda proyección: explícitos y concretos; Siempre rango, nunca punto medio; Los huecos y su recuperación salen de la calculadora, nunca de tu cuenta. Falta: no hay flujo ni plantilla para un usuario ya pensionado; la bienvenida de 'Lo que el usuario nunca ve' (cerrada el 2026-07-20) promete 'cuándo y con qué monto te vas a pensionar', que a él no le aplica.

**C40 | RAIS · EMP · PEN · SC**

*Ya pensionado, sin capacidad de ahorro.*

> Me pensionaron con un fondo privado y la mesada me llegó con descuentos. ¿Por qué me descontaron y me la suben el otro año?

- **Corpus: CUBIERTO.** Ref: reglas-rais.md s.3 y s.5; mora-y-correccion-historia-laboral.md s.1 y s.2; vida-del-pensionado.md s.1 a s.5 + tributario-pensional.md s.2 y s.3; sin-pension-alternativas.md s.2 a s.7.
- **Cálculo: PARCIAL.** Ref: diagnosticar.py -> rais.py; lagunas.py + recuperacion.py; costo_y_retorno.py (mesada_neta y tarifa_salud_pensionado). Falta: costo_y_retorno.py ya descuenta salud de la mesada, pero ningún módulo calcula reajuste anual, retención en la fuente, mesada 14 ni excedentes de libre disponibilidad, y diagnosticar.py está construido para proyectar hacia la pensión, no desde ella.
- **Comportamiento: HUECO.** Ref: Reglas duras (nunca se rompen) 1 a 8; Tu flujo de conversación (los 5 momentos); Plantilla del diagnóstico; Supuestos de toda proyección: explícitos y concretos; Siempre rango, nunca punto medio; Los huecos y su recuperación salen de la calculadora, nunca de tu cuenta. Falta: no hay flujo ni plantilla para un usuario ya pensionado; la bienvenida de 'Lo que el usuario nunca ve' (cerrada el 2026-07-20) promete 'cuándo y con qué monto te vas a pensionar', que a él no le aplica; la tabla de accionabilidad verifica régimen, edad e ingreso, no capacidad de pago; la regla de segmento de BEPS ('ofrecerlo a alguien con capacidad de pago es un error de segmento') vive en aportes-voluntarios-y-sobrecotizacion.md s.5, no en el system-prompt.

#### IND: Independiente por cuenta propia

**C41 | RAIS · IND · M10+ · CA**

*Más de 10 años para pensionarse, con capacidad de ahorro.*

> Soy independiente, facturo $12.000.000 al mes y cotizo en un fondo privado sobre el mínimo. ¿Cuánto me cambia la pensión si cotizo sobre lo que de verdad gano?

- **Corpus: CUBIERTO.** Ref: reglas-rais.md s.3 y s.5; independientes.md s.2, s.4 y s.7; supuestos-actuariales.md s.3 y s.5; aportes-voluntarios-y-sobrecotizacion.md s.4.
- **Cálculo: PARCIAL.** Ref: diagnosticar.py -> rais.py; rpm/rais con --ibc-futuro y --densidad-futura; costo_y_retorno.py (aporte_mensual y costo_total sobre el IBC real); costo_y_retorno.py (tabla_de_escenarios: cuánto cuesta cada alternativa y en cuántos meses se recupera). Falta: costo_y_retorno.py resuelve el costo y el breakeven de sobrecotizar, pero ningún módulo modela el aporte voluntario propiamente dicho (rendimiento en la cuenta, comisión de la AFP, beneficio tributario del art. 126-1), que es la otra mitad de la decisión de quien tiene excedente.
- **Comportamiento: CUBIERTO.** Ref: Reglas duras (nunca se rompen) 1 a 8; Tu flujo de conversación (los 5 momentos); Plantilla del diagnóstico; Supuestos de toda proyección: explícitos y concretos; Siempre rango, nunca punto medio; Toda palanca se verifica antes de ofrecerla (fila 'sube tu base de cotización'); Toda palanca se verifica antes de ofrecerla.

**C42 | RAIS · IND · M10+ · SC**

*Más de 10 años para pensionarse, sin capacidad de ahorro.*

> Soy independiente y hay meses que no alcanzo a pagar la PILA. ¿Cuánto me cuestan esos meses en la pensión?

- **Corpus: CUBIERTO.** Ref: reglas-rais.md s.3 y s.5; independientes.md s.2, s.4 y s.7; supuestos-actuariales.md s.3 y s.5; sin-pension-alternativas.md s.2 a s.7.
- **Cálculo: CUBIERTO.** Ref: diagnosticar.py -> rais.py; rpm/rais con --ibc-futuro y --densidad-futura; costo_y_retorno.py (aporte_mensual y costo_total sobre el IBC real).
- **Comportamiento: PARCIAL.** Ref: Reglas duras (nunca se rompen) 1 a 8; Tu flujo de conversación (los 5 momentos); Plantilla del diagnóstico; Supuestos de toda proyección: explícitos y concretos; Siempre rango, nunca punto medio; Toda palanca se verifica antes de ofrecerla (fila 'sube tu base de cotización'). Falta: la tabla de accionabilidad verifica régimen, edad e ingreso, no capacidad de pago; la regla de segmento de BEPS ('ofrecerlo a alguien con capacidad de pago es un error de segmento') vive en aportes-voluntarios-y-sobrecotizacion.md s.5, no en el system-prompt.

**C43 | RAIS · IND · M10- · CA**

*Menos de 10 años, con capacidad de ahorro.*

> Tengo 54 años, soy contratista y estoy en un fondo privado. Puedo poner $2.000.000 más al mes: ¿hasta dónde puedo subir mi base sin meterme en problemas?

- **Corpus: CUBIERTO.** Ref: reglas-rais.md s.3 y s.5; independientes.md s.2, s.4 y s.7; reglas-traslados.md s.1; aportes-voluntarios-y-sobrecotizacion.md s.4.
- **Cálculo: PARCIAL.** Ref: diagnosticar.py -> rais.py; rpm/rais con --ibc-futuro y --densidad-futura; costo_y_retorno.py (aporte_mensual y costo_total sobre el IBC real); costo_y_retorno.py (tabla_de_escenarios: cuánto cuesta cada alternativa y en cuántos meses se recupera). Falta: costo_y_retorno.py resuelve el costo y el breakeven de sobrecotizar, pero ningún módulo modela el aporte voluntario propiamente dicho (rendimiento en la cuenta, comisión de la AFP, beneficio tributario del art. 126-1), que es la otra mitad de la decisión de quien tiene excedente.
- **Comportamiento: CUBIERTO.** Ref: Reglas duras (nunca se rompen) 1 a 8; Tu flujo de conversación (los 5 momentos); Plantilla del diagnóstico; Supuestos de toda proyección: explícitos y concretos; Siempre rango, nunca punto medio; Toda palanca se verifica antes de ofrecerla (fila 'sube tu base de cotización'); Toda palanca se verifica antes de ofrecerla.

**C44 | RAIS · IND · M10- · SC**

*Menos de 10 años, sin capacidad de ahorro.*

> Tengo 56 años, soy independiente en un fondo privado y voy en 900 semanas. ¿Alcanzo o mejor me olvido de la pensión?

- **Corpus: CUBIERTO.** Ref: reglas-rais.md s.3 y s.5; independientes.md s.2, s.4 y s.7; reglas-traslados.md s.1; sin-pension-alternativas.md s.2 a s.7.
- **Cálculo: CUBIERTO.** Ref: diagnosticar.py -> rais.py; rpm/rais con --ibc-futuro y --densidad-futura; costo_y_retorno.py (aporte_mensual y costo_total sobre el IBC real).
- **Comportamiento: PARCIAL.** Ref: Reglas duras (nunca se rompen) 1 a 8; Tu flujo de conversación (los 5 momentos); Plantilla del diagnóstico; Supuestos de toda proyección: explícitos y concretos; Siempre rango, nunca punto medio; Toda palanca se verifica antes de ofrecerla (fila 'sube tu base de cotización'). Falta: la tabla de accionabilidad verifica régimen, edad e ingreso, no capacidad de pago; la regla de segmento de BEPS ('ofrecerlo a alguien con capacidad de pago es un error de segmento') vive en aportes-voluntarios-y-sobrecotizacion.md s.5, no en el system-prompt.

**C45 | RAIS · IND · CUM · CA**

*Ya cumple requisitos, con capacidad de ahorro.*

> Ya completé las semanas en un fondo privado y sigo facturando bien. ¿Me conviene dejar de cotizar o seguir un tiempo más?

- **Corpus: CUBIERTO.** Ref: reglas-rais.md s.3 y s.5; independientes.md s.2, s.4 y s.7; modalidades-de-pension.md s.1, s.7 y s.14; aportes-voluntarios-y-sobrecotizacion.md s.4.
- **Cálculo: HUECO.** Ref: diagnosticar.py -> rais.py; rpm/rais con --ibc-futuro y --densidad-futura; costo_y_retorno.py (aporte_mensual y costo_total sobre el IBC real); costo_y_retorno.py (breakeven_meses y ganancia_neta: seguir cotizando vs. reclamar ya). Falta: ningún módulo compara modalidades de pensión; rais.py entrega una renta vitalicia sin beneficiarios de sobrevivencia (calculadora/README.md, aprox. 1), que es justo la decisión de esa persona.
- **Comportamiento: PARCIAL.** Ref: Reglas duras (nunca se rompen) 1 a 8; Tu flujo de conversación (los 5 momentos); Plantilla del diagnóstico; Supuestos de toda proyección: explícitos y concretos; Siempre rango, nunca punto medio; Toda palanca se verifica antes de ofrecerla (fila 'sube tu base de cotización'); Toda palanca se verifica antes de ofrecerla. Falta: el menú de palancas de 'Toda palanca se verifica antes de ofrecerla' solo contempla 'cerca de cumplir requisitos'; no hay plantilla ni cierre para quien YA cumple, cuyo bloque 2 no es una proyección sino una decisión de cuándo reclamar.

**C46 | RAIS · IND · CUM · SC**

*Ya cumple requisitos, sin capacidad de ahorro.*

> Cumplí requisitos en un fondo privado pero llevo dos años sin pagar PILA. ¿Eso me tumba la solicitud?

- **Corpus: CUBIERTO.** Ref: reglas-rais.md s.3 y s.5; independientes.md s.2, s.4 y s.7; modalidades-de-pension.md s.1, s.7 y s.14; sin-pension-alternativas.md s.2 a s.7.
- **Cálculo: HUECO.** Ref: diagnosticar.py -> rais.py; rpm/rais con --ibc-futuro y --densidad-futura; costo_y_retorno.py (aporte_mensual y costo_total sobre el IBC real); costo_y_retorno.py (breakeven_meses y ganancia_neta: seguir cotizando vs. reclamar ya). Falta: ningún módulo compara modalidades de pensión; rais.py entrega una renta vitalicia sin beneficiarios de sobrevivencia (calculadora/README.md, aprox. 1), que es justo la decisión de esa persona.
- **Comportamiento: PARCIAL.** Ref: Reglas duras (nunca se rompen) 1 a 8; Tu flujo de conversación (los 5 momentos); Plantilla del diagnóstico; Supuestos de toda proyección: explícitos y concretos; Siempre rango, nunca punto medio; Toda palanca se verifica antes de ofrecerla (fila 'sube tu base de cotización'). Falta: el menú de palancas de 'Toda palanca se verifica antes de ofrecerla' solo contempla 'cerca de cumplir requisitos'; no hay plantilla ni cierre para quien YA cumple, cuyo bloque 2 no es una proyección sino una decisión de cuándo reclamar; la tabla de accionabilidad verifica régimen, edad e ingreso, no capacidad de pago; la regla de segmento de BEPS ('ofrecerlo a alguien con capacidad de pago es un error de segmento') vive en aportes-voluntarios-y-sobrecotizacion.md s.5, no en el system-prompt.

**C47 | RAIS · IND · PEN · CA**

*Ya pensionado, con capacidad de ahorro.*

> Estoy pensionado por un fondo privado y sigo facturando como independiente. ¿Tengo que seguir pagando aportes?

- **Corpus: CUBIERTO.** Ref: reglas-rais.md s.3 y s.5; independientes.md s.2, s.4 y s.7; vida-del-pensionado.md s.1 a s.5 + tributario-pensional.md s.2 y s.3; aportes-voluntarios-y-sobrecotizacion.md s.4.
- **Cálculo: PARCIAL.** Ref: diagnosticar.py -> rais.py; rpm/rais con --ibc-futuro y --densidad-futura; costo_y_retorno.py (aporte_mensual y costo_total sobre el IBC real); costo_y_retorno.py (mesada_neta y tarifa_salud_pensionado); costo_y_retorno.py (tabla_de_escenarios: cuánto cuesta cada alternativa y en cuántos meses se recupera). Falta: costo_y_retorno.py ya descuenta salud de la mesada, pero ningún módulo calcula reajuste anual, retención en la fuente, mesada 14 ni excedentes de libre disponibilidad, y diagnosticar.py está construido para proyectar hacia la pensión, no desde ella; costo_y_retorno.py resuelve el costo y el breakeven de sobrecotizar, pero ningún módulo modela el aporte voluntario propiamente dicho (rendimiento en la cuenta, comisión de la AFP, beneficio tributario del art. 126-1), que es la otra mitad de la decisión de quien tiene excedente.
- **Comportamiento: HUECO.** Ref: Reglas duras (nunca se rompen) 1 a 8; Tu flujo de conversación (los 5 momentos); Plantilla del diagnóstico; Supuestos de toda proyección: explícitos y concretos; Siempre rango, nunca punto medio; Toda palanca se verifica antes de ofrecerla (fila 'sube tu base de cotización'). Falta: no hay flujo ni plantilla para un usuario ya pensionado; la bienvenida de 'Lo que el usuario nunca ve' (cerrada el 2026-07-20) promete 'cuándo y con qué monto te vas a pensionar', que a él no le aplica.

**C48 | RAIS · IND · PEN · SC**

*Ya pensionado, sin capacidad de ahorro.*

> Me pensioné con un fondo privado y sigo trabajando por cuenta propia. ¿Me toca pagar salud dos veces?

- **Corpus: CUBIERTO.** Ref: reglas-rais.md s.3 y s.5; independientes.md s.2, s.4 y s.7; vida-del-pensionado.md s.1 a s.5 + tributario-pensional.md s.2 y s.3; sin-pension-alternativas.md s.2 a s.7.
- **Cálculo: PARCIAL.** Ref: diagnosticar.py -> rais.py; rpm/rais con --ibc-futuro y --densidad-futura; costo_y_retorno.py (aporte_mensual y costo_total sobre el IBC real); costo_y_retorno.py (mesada_neta y tarifa_salud_pensionado). Falta: costo_y_retorno.py ya descuenta salud de la mesada, pero ningún módulo calcula reajuste anual, retención en la fuente, mesada 14 ni excedentes de libre disponibilidad, y diagnosticar.py está construido para proyectar hacia la pensión, no desde ella.
- **Comportamiento: HUECO.** Ref: Reglas duras (nunca se rompen) 1 a 8; Tu flujo de conversación (los 5 momentos); Plantilla del diagnóstico; Supuestos de toda proyección: explícitos y concretos; Siempre rango, nunca punto medio; Toda palanca se verifica antes de ofrecerla (fila 'sube tu base de cotización'). Falta: no hay flujo ni plantilla para un usuario ya pensionado; la bienvenida de 'Lo que el usuario nunca ve' (cerrada el 2026-07-20) promete 'cuándo y con qué monto te vas a pensionar', que a él no le aplica; la tabla de accionabilidad verifica régimen, edad e ingreso, no capacidad de pago; la regla de segmento de BEPS ('ofrecerlo a alguien con capacidad de pago es un error de segmento') vive en aportes-voluntarios-y-sobrecotizacion.md s.5, no en el system-prompt.

#### REN: Rentista de capital

**C49 | RAIS · REN · M10+ · CA**

*Más de 10 años para pensionarse, con capacidad de ahorro.*

> Vivo de arriendos y dividendos, tengo 40 años y nunca he cotizado a un fondo privado. ¿Estoy obligado y sobre cuánto?

- **Corpus: PARCIAL.** Ref: reglas-rais.md s.3 y s.5; independientes.md s.3; supuestos-actuariales.md s.3 y s.5; aportes-voluntarios-y-sobrecotizacion.md s.4. Falta: el rentista tiene una sola sección (independientes.md s.3), con [VERIFICAR] abierto sobre el fundamento y sin tratamiento de rentas mixtas.
- **Cálculo: PARCIAL.** Ref: diagnosticar.py -> rais.py; router.py (sin regla propia); costo_y_retorno.py (tabla_de_escenarios: cuánto cuesta cada alternativa y en cuántos meses se recupera). Falta: ningún módulo traduce rentas de capital a base de cotización; se aproxima a mano con --ibc-futuro y los coeficientes de presunción están fuera de alcance V1 (independientes.md s.8); costo_y_retorno.py resuelve el costo y el breakeven de sobrecotizar, pero ningún módulo modela el aporte voluntario propiamente dicho (rendimiento en la cuenta, comisión de la AFP, beneficio tributario del art. 126-1), que es la otra mitad de la decisión de quien tiene excedente.
- **Comportamiento: PARCIAL.** Ref: Reglas duras (nunca se rompen) 1 a 8; Tu flujo de conversación (los 5 momentos); Plantilla del diagnóstico; Supuestos de toda proyección: explícitos y concretos; Siempre rango, nunca punto medio; Toda palanca se verifica antes de ofrecerla. Falta: la tabla de accionabilidad de 'Toda palanca se verifica antes de ofrecerla' solo contempla 'sea independiente y tenga ingreso que lo respalde'; la distinción entre patrimonio y renta vive en independientes.md s.3, no en el system-prompt.

**C50 | RAIS · REN · M10+ · SC**

*Más de 10 años para pensionarse, sin capacidad de ahorro.*

> No trabajo, vivo de un local que arriendo por $1.800.000. ¿Con eso puedo cotizar a un fondo privado y pensionarme?

- **Corpus: PARCIAL.** Ref: reglas-rais.md s.3 y s.5; independientes.md s.3; supuestos-actuariales.md s.3 y s.5; sin-pension-alternativas.md s.2 a s.7. Falta: el rentista tiene una sola sección (independientes.md s.3), con [VERIFICAR] abierto sobre el fundamento y sin tratamiento de rentas mixtas.
- **Cálculo: PARCIAL.** Ref: diagnosticar.py -> rais.py; router.py (sin regla propia). Falta: ningún módulo traduce rentas de capital a base de cotización; se aproxima a mano con --ibc-futuro y los coeficientes de presunción están fuera de alcance V1 (independientes.md s.8).
- **Comportamiento: PARCIAL.** Ref: Reglas duras (nunca se rompen) 1 a 8; Tu flujo de conversación (los 5 momentos); Plantilla del diagnóstico; Supuestos de toda proyección: explícitos y concretos; Siempre rango, nunca punto medio. Falta: la tabla de accionabilidad de 'Toda palanca se verifica antes de ofrecerla' solo contempla 'sea independiente y tenga ingreso que lo respalde'; la distinción entre patrimonio y renta vive en independientes.md s.3, no en el system-prompt; la tabla de accionabilidad verifica régimen, edad e ingreso, no capacidad de pago; la regla de segmento de BEPS ('ofrecerlo a alguien con capacidad de pago es un error de segmento') vive en aportes-voluntarios-y-sobrecotizacion.md s.5, no en el system-prompt.

**C51 | RAIS · REN · M10- · CA**

*Menos de 10 años, con capacidad de ahorro.*

> Tengo 53 años y vivo de rentas y de mi patrimonio. ¿Puedo cotizar a un fondo privado sobre lo que tengo ahorrado?

- **Corpus: PARCIAL.** Ref: reglas-rais.md s.3 y s.5; independientes.md s.3; reglas-traslados.md s.1; aportes-voluntarios-y-sobrecotizacion.md s.4. Falta: el rentista tiene una sola sección (independientes.md s.3), con [VERIFICAR] abierto sobre el fundamento y sin tratamiento de rentas mixtas.
- **Cálculo: PARCIAL.** Ref: diagnosticar.py -> rais.py; router.py (sin regla propia); costo_y_retorno.py (tabla_de_escenarios: cuánto cuesta cada alternativa y en cuántos meses se recupera). Falta: ningún módulo traduce rentas de capital a base de cotización; se aproxima a mano con --ibc-futuro y los coeficientes de presunción están fuera de alcance V1 (independientes.md s.8); costo_y_retorno.py resuelve el costo y el breakeven de sobrecotizar, pero ningún módulo modela el aporte voluntario propiamente dicho (rendimiento en la cuenta, comisión de la AFP, beneficio tributario del art. 126-1), que es la otra mitad de la decisión de quien tiene excedente.
- **Comportamiento: PARCIAL.** Ref: Reglas duras (nunca se rompen) 1 a 8; Tu flujo de conversación (los 5 momentos); Plantilla del diagnóstico; Supuestos de toda proyección: explícitos y concretos; Siempre rango, nunca punto medio; Toda palanca se verifica antes de ofrecerla. Falta: la tabla de accionabilidad de 'Toda palanca se verifica antes de ofrecerla' solo contempla 'sea independiente y tenga ingreso que lo respalde'; la distinción entre patrimonio y renta vive en independientes.md s.3, no en el system-prompt.

**C52 | RAIS · REN · M10- · SC**

*Menos de 10 años, sin capacidad de ahorro.*

> Tengo 55 años, mis únicos ingresos son unos arriendos pequeños y tengo 400 semanas en un fondo privado. ¿Me sirve seguir cotizando?

- **Corpus: PARCIAL.** Ref: reglas-rais.md s.3 y s.5; independientes.md s.3; reglas-traslados.md s.1; sin-pension-alternativas.md s.2 a s.7. Falta: el rentista tiene una sola sección (independientes.md s.3), con [VERIFICAR] abierto sobre el fundamento y sin tratamiento de rentas mixtas.
- **Cálculo: PARCIAL.** Ref: diagnosticar.py -> rais.py; router.py (sin regla propia). Falta: ningún módulo traduce rentas de capital a base de cotización; se aproxima a mano con --ibc-futuro y los coeficientes de presunción están fuera de alcance V1 (independientes.md s.8).
- **Comportamiento: PARCIAL.** Ref: Reglas duras (nunca se rompen) 1 a 8; Tu flujo de conversación (los 5 momentos); Plantilla del diagnóstico; Supuestos de toda proyección: explícitos y concretos; Siempre rango, nunca punto medio. Falta: la tabla de accionabilidad de 'Toda palanca se verifica antes de ofrecerla' solo contempla 'sea independiente y tenga ingreso que lo respalde'; la distinción entre patrimonio y renta vive en independientes.md s.3, no en el system-prompt; la tabla de accionabilidad verifica régimen, edad e ingreso, no capacidad de pago; la regla de segmento de BEPS ('ofrecerlo a alguien con capacidad de pago es un error de segmento') vive en aportes-voluntarios-y-sobrecotizacion.md s.5, no en el system-prompt.
- **Propuesta: FUERA DE ALCANCE.** Rentista de 55 años con 400 semanas y arriendos pequeños: ningún camino del sistema lo lleva a pensión (necesitaría 900 semanas más en 7 años). El valor no está en el diagnóstico sino en indemnización sustitutiva o BEPS, y rpm.py no calcula el monto de la indemnización. Atender la pregunta con la calculadora actual produce un número sin decisión detrás.

**C53 | RAIS · REN · CUM · CA**

*Ya cumple requisitos, con capacidad de ahorro.*

> Ya tengo edad y semanas en un fondo privado y vivo de rentas. ¿Pedir la pensión me cambia algo en impuestos?

- **Corpus: PARCIAL.** Ref: reglas-rais.md s.3 y s.5; independientes.md s.3; modalidades-de-pension.md s.1, s.7 y s.14; aportes-voluntarios-y-sobrecotizacion.md s.4. Falta: el rentista tiene una sola sección (independientes.md s.3), con [VERIFICAR] abierto sobre el fundamento y sin tratamiento de rentas mixtas.
- **Cálculo: HUECO.** Ref: diagnosticar.py -> rais.py; router.py (sin regla propia); costo_y_retorno.py (breakeven_meses y ganancia_neta: seguir cotizando vs. reclamar ya). Falta: ningún módulo traduce rentas de capital a base de cotización; se aproxima a mano con --ibc-futuro y los coeficientes de presunción están fuera de alcance V1 (independientes.md s.8); ningún módulo compara modalidades de pensión; rais.py entrega una renta vitalicia sin beneficiarios de sobrevivencia (calculadora/README.md, aprox. 1), que es justo la decisión de esa persona.
- **Comportamiento: PARCIAL.** Ref: Reglas duras (nunca se rompen) 1 a 8; Tu flujo de conversación (los 5 momentos); Plantilla del diagnóstico; Supuestos de toda proyección: explícitos y concretos; Siempre rango, nunca punto medio; Toda palanca se verifica antes de ofrecerla. Falta: la tabla de accionabilidad de 'Toda palanca se verifica antes de ofrecerla' solo contempla 'sea independiente y tenga ingreso que lo respalde'; la distinción entre patrimonio y renta vive en independientes.md s.3, no en el system-prompt; el menú de palancas de 'Toda palanca se verifica antes de ofrecerla' solo contempla 'cerca de cumplir requisitos'; no hay plantilla ni cierre para quien YA cumple, cuyo bloque 2 no es una proyección sino una decisión de cuándo reclamar.

**C54 | RAIS · REN · CUM · SC**

*Ya cumple requisitos, sin capacidad de ahorro.*

> Cumplo requisitos en un fondo privado, vivo de un arriendo y ya no cotizo hace años. ¿Igual me pensiono?

- **Corpus: PARCIAL.** Ref: reglas-rais.md s.3 y s.5; independientes.md s.3; modalidades-de-pension.md s.1, s.7 y s.14; sin-pension-alternativas.md s.2 a s.7. Falta: el rentista tiene una sola sección (independientes.md s.3), con [VERIFICAR] abierto sobre el fundamento y sin tratamiento de rentas mixtas.
- **Cálculo: HUECO.** Ref: diagnosticar.py -> rais.py; router.py (sin regla propia); costo_y_retorno.py (breakeven_meses y ganancia_neta: seguir cotizando vs. reclamar ya). Falta: ningún módulo traduce rentas de capital a base de cotización; se aproxima a mano con --ibc-futuro y los coeficientes de presunción están fuera de alcance V1 (independientes.md s.8); ningún módulo compara modalidades de pensión; rais.py entrega una renta vitalicia sin beneficiarios de sobrevivencia (calculadora/README.md, aprox. 1), que es justo la decisión de esa persona.
- **Comportamiento: PARCIAL.** Ref: Reglas duras (nunca se rompen) 1 a 8; Tu flujo de conversación (los 5 momentos); Plantilla del diagnóstico; Supuestos de toda proyección: explícitos y concretos; Siempre rango, nunca punto medio. Falta: la tabla de accionabilidad de 'Toda palanca se verifica antes de ofrecerla' solo contempla 'sea independiente y tenga ingreso que lo respalde'; la distinción entre patrimonio y renta vive en independientes.md s.3, no en el system-prompt; el menú de palancas de 'Toda palanca se verifica antes de ofrecerla' solo contempla 'cerca de cumplir requisitos'; no hay plantilla ni cierre para quien YA cumple, cuyo bloque 2 no es una proyección sino una decisión de cuándo reclamar; la tabla de accionabilidad verifica régimen, edad e ingreso, no capacidad de pago; la regla de segmento de BEPS ('ofrecerlo a alguien con capacidad de pago es un error de segmento') vive en aportes-voluntarios-y-sobrecotizacion.md s.5, no en el system-prompt.

**C55 | RAIS · REN · PEN · CA**

*Ya pensionado, con capacidad de ahorro.*

> Estoy pensionado por un fondo privado y recibo dividendos de una empresa. ¿Tengo que seguir cotizando por esos ingresos?

- **Corpus: CUBIERTO.** Ref: reglas-rais.md s.3 y s.5; independientes.md s.3; vida-del-pensionado.md s.1 a s.5 + tributario-pensional.md s.2 y s.3; aportes-voluntarios-y-sobrecotizacion.md s.4; independientes.md s.3 (pensionados entre los no obligados).
- **Cálculo: PARCIAL.** Ref: diagnosticar.py -> rais.py; router.py (sin regla propia); costo_y_retorno.py (mesada_neta y tarifa_salud_pensionado); costo_y_retorno.py (tabla_de_escenarios: cuánto cuesta cada alternativa y en cuántos meses se recupera). Falta: ningún módulo traduce rentas de capital a base de cotización; se aproxima a mano con --ibc-futuro y los coeficientes de presunción están fuera de alcance V1 (independientes.md s.8); costo_y_retorno.py ya descuenta salud de la mesada, pero ningún módulo calcula reajuste anual, retención en la fuente, mesada 14 ni excedentes de libre disponibilidad, y diagnosticar.py está construido para proyectar hacia la pensión, no desde ella; costo_y_retorno.py resuelve el costo y el breakeven de sobrecotizar, pero ningún módulo modela el aporte voluntario propiamente dicho (rendimiento en la cuenta, comisión de la AFP, beneficio tributario del art. 126-1), que es la otra mitad de la decisión de quien tiene excedente.
- **Comportamiento: HUECO.** Ref: Reglas duras (nunca se rompen) 1 a 8; Tu flujo de conversación (los 5 momentos); Plantilla del diagnóstico; Supuestos de toda proyección: explícitos y concretos; Siempre rango, nunca punto medio. Falta: la tabla de accionabilidad de 'Toda palanca se verifica antes de ofrecerla' solo contempla 'sea independiente y tenga ingreso que lo respalde'; la distinción entre patrimonio y renta vive en independientes.md s.3, no en el system-prompt; no hay flujo ni plantilla para un usuario ya pensionado; la bienvenida de 'Lo que el usuario nunca ve' (cerrada el 2026-07-20) promete 'cuándo y con qué monto te vas a pensionar', que a él no le aplica.

**C56 | RAIS · REN · PEN · SC**

*Ya pensionado, sin capacidad de ahorro.*

> Soy pensionado de un fondo privado y arriendo un cuarto de mi casa. ¿Eso me obliga a declarar renta?

- **Corpus: CUBIERTO.** Ref: reglas-rais.md s.3 y s.5; independientes.md s.3; vida-del-pensionado.md s.1 a s.5 + tributario-pensional.md s.2 y s.3; sin-pension-alternativas.md s.2 a s.7; independientes.md s.3 (pensionados entre los no obligados).
- **Cálculo: PARCIAL.** Ref: diagnosticar.py -> rais.py; router.py (sin regla propia); costo_y_retorno.py (mesada_neta y tarifa_salud_pensionado). Falta: ningún módulo traduce rentas de capital a base de cotización; se aproxima a mano con --ibc-futuro y los coeficientes de presunción están fuera de alcance V1 (independientes.md s.8); costo_y_retorno.py ya descuenta salud de la mesada, pero ningún módulo calcula reajuste anual, retención en la fuente, mesada 14 ni excedentes de libre disponibilidad, y diagnosticar.py está construido para proyectar hacia la pensión, no desde ella.
- **Comportamiento: HUECO.** Ref: Reglas duras (nunca se rompen) 1 a 8; Tu flujo de conversación (los 5 momentos); Plantilla del diagnóstico; Supuestos de toda proyección: explícitos y concretos; Siempre rango, nunca punto medio. Falta: la tabla de accionabilidad de 'Toda palanca se verifica antes de ofrecerla' solo contempla 'sea independiente y tenga ingreso que lo respalde'; la distinción entre patrimonio y renta vive en independientes.md s.3, no en el system-prompt; no hay flujo ni plantilla para un usuario ya pensionado; la bienvenida de 'Lo que el usuario nunca ve' (cerrada el 2026-07-20) promete 'cuándo y con qué monto te vas a pensionar', que a él no le aplica; la tabla de accionabilidad verifica régimen, edad e ingreso, no capacidad de pago; la regla de segmento de BEPS ('ofrecerlo a alguien con capacidad de pago es un error de segmento') vive en aportes-voluntarios-y-sobrecotizacion.md s.5, no en el system-prompt.
- **Propuesta: FUERA DE ALCANCE.** La pregunta es de obligación de declarar renta, no de pensión. La respuesta depende de patrimonio bruto, consignaciones y compras del año, datos que Júbilo no pide ni debe pedir. tributario-pensional.md s.2 da el marco de la renta exenta, no el test de declarante. Salida correcta: derivar a contador.

#### MIX: Mixto o historia partida

**C57 | RAIS · MIX · M10+ · CA**

*Más de 10 años para pensionarse, con capacidad de ahorro.*

> Trabajé 8 años en una alcaldía, luego en un fondo privado y ahora soy independiente. ¿Esos años públicos me cuentan?

- **Corpus: PARCIAL.** Ref: reglas-rais.md s.3 y s.5; reglas-traslados.md s.5 + bonos-tiempos-publicos-y-exterior.md s.1 y s.8; supuestos-actuariales.md s.3 y s.5; aportes-voluntarios-y-sobrecotizacion.md s.4. Falta: no hay documento que ordene la historia partida: las piezas están repartidas en traslados, bonos y reglas-rais s.7.
- **Cálculo: PARCIAL.** Ref: diagnosticar.py -> rais.py; comparador.py; costo_y_retorno.py (tabla_de_escenarios: cuánto cuesta cada alternativa y en cuántos meses se recupera). Falta: comparador.py simula el saldo RAIS con el 11,5% e ignora bono pensional y comisiones (calculadora/README.md, aprox. 4); no consolida dos historias laborales reales; costo_y_retorno.py resuelve el costo y el breakeven de sobrecotizar, pero ningún módulo modela el aporte voluntario propiamente dicho (rendimiento en la cuenta, comisión de la AFP, beneficio tributario del art. 126-1), que es la otra mitad de la decisión de quien tiene excedente.
- **Comportamiento: HUECO.** Ref: Reglas duras (nunca se rompen) 1 a 8; Tu flujo de conversación (los 5 momentos); Plantilla del diagnóstico; Supuestos de toda proyección: explícitos y concretos; Siempre rango, nunca punto medio; Toda palanca se verifica antes de ofrecerla. Falta: el momento 2 de 'Tu flujo de conversación' asume UN documento y UN total impreso para la verificación cruzada (regla dura 4); no hay regla para dos historias laborales de dos administradoras.

**C58 | RAIS · MIX · M10+ · SC**

*Más de 10 años para pensionarse, sin capacidad de ahorro.*

> Estuve en un fondo privado, me pasé a un fondo privado y hay años que no aparecen en ningún lado. ¿Dónde quedaron mis semanas?

- **Corpus: PARCIAL.** Ref: reglas-rais.md s.3 y s.5; reglas-traslados.md s.5 + bonos-tiempos-publicos-y-exterior.md s.1 y s.8; supuestos-actuariales.md s.3 y s.5; sin-pension-alternativas.md s.2 a s.7. Falta: no hay documento que ordene la historia partida: las piezas están repartidas en traslados, bonos y reglas-rais s.7.
- **Cálculo: PARCIAL.** Ref: diagnosticar.py -> rais.py; comparador.py. Falta: comparador.py simula el saldo RAIS con el 11,5% e ignora bono pensional y comisiones (calculadora/README.md, aprox. 4); no consolida dos historias laborales reales.
- **Comportamiento: HUECO.** Ref: Reglas duras (nunca se rompen) 1 a 8; Tu flujo de conversación (los 5 momentos); Plantilla del diagnóstico; Supuestos de toda proyección: explícitos y concretos; Siempre rango, nunca punto medio. Falta: el momento 2 de 'Tu flujo de conversación' asume UN documento y UN total impreso para la verificación cruzada (regla dura 4); no hay regla para dos historias laborales de dos administradoras; la tabla de accionabilidad verifica régimen, edad e ingreso, no capacidad de pago; la regla de segmento de BEPS ('ofrecerlo a alguien con capacidad de pago es un error de segmento') vive en aportes-voluntarios-y-sobrecotizacion.md s.5, no en el system-prompt.

**C59 | RAIS · MIX · M10- · CA**

*Menos de 10 años, con capacidad de ahorro.*

> Tengo 54 años, coticé 15 años en un fondo privado y 8 en un fondo privado. ¿Me conviene moverme antes de que se cierre la ventana?

- **Corpus: PARCIAL.** Ref: reglas-rais.md s.3 y s.5; reglas-traslados.md s.5 + bonos-tiempos-publicos-y-exterior.md s.1 y s.8; reglas-traslados.md s.1; aportes-voluntarios-y-sobrecotizacion.md s.4. Falta: no hay documento que ordene la historia partida: las piezas están repartidas en traslados, bonos y reglas-rais s.7.
- **Cálculo: PARCIAL.** Ref: diagnosticar.py -> rais.py; comparador.py; costo_y_retorno.py (tabla_de_escenarios: cuánto cuesta cada alternativa y en cuántos meses se recupera). Falta: comparador.py simula el saldo RAIS con el 11,5% e ignora bono pensional y comisiones (calculadora/README.md, aprox. 4); no consolida dos historias laborales reales; costo_y_retorno.py resuelve el costo y el breakeven de sobrecotizar, pero ningún módulo modela el aporte voluntario propiamente dicho (rendimiento en la cuenta, comisión de la AFP, beneficio tributario del art. 126-1), que es la otra mitad de la decisión de quien tiene excedente.
- **Comportamiento: HUECO.** Ref: Reglas duras (nunca se rompen) 1 a 8; Tu flujo de conversación (los 5 momentos); Plantilla del diagnóstico; Supuestos de toda proyección: explícitos y concretos; Siempre rango, nunca punto medio; Toda palanca se verifica antes de ofrecerla. Falta: el momento 2 de 'Tu flujo de conversación' asume UN documento y UN total impreso para la verificación cruzada (regla dura 4); no hay regla para dos historias laborales de dos administradoras.

**C60 | RAIS · MIX · M10- · SC**

*Menos de 10 años, sin capacidad de ahorro.*

> Coticé 6 años en España y el resto en un fondo privado. Tengo 53 años: ¿puedo sumar esas semanas?

- **Corpus: PARCIAL.** Ref: reglas-rais.md s.3 y s.5; reglas-traslados.md s.5 + bonos-tiempos-publicos-y-exterior.md s.1 y s.8; reglas-traslados.md s.1; sin-pension-alternativas.md s.2 a s.7. Falta: no hay documento que ordene la historia partida: las piezas están repartidas en traslados, bonos y reglas-rais s.7.
- **Cálculo: PARCIAL.** Ref: diagnosticar.py -> rais.py; comparador.py. Falta: comparador.py simula el saldo RAIS con el 11,5% e ignora bono pensional y comisiones (calculadora/README.md, aprox. 4); no consolida dos historias laborales reales.
- **Comportamiento: HUECO.** Ref: Reglas duras (nunca se rompen) 1 a 8; Tu flujo de conversación (los 5 momentos); Plantilla del diagnóstico; Supuestos de toda proyección: explícitos y concretos; Siempre rango, nunca punto medio. Falta: el momento 2 de 'Tu flujo de conversación' asume UN documento y UN total impreso para la verificación cruzada (regla dura 4); no hay regla para dos historias laborales de dos administradoras; la tabla de accionabilidad verifica régimen, edad e ingreso, no capacidad de pago; la regla de segmento de BEPS ('ofrecerlo a alguien con capacidad de pago es un error de segmento') vive en aportes-voluntarios-y-sobrecotizacion.md s.5, no en el system-prompt.
- **Propuesta: FUERA DE ALCANCE.** Historia partida con 6 años cotizados en España. Depende del Convenio Iberoamericano y de la discrepancia CMISS abierta en bonos-tiempos-publicos-y-exterior.md s.9 (¿elige el afiliado o aplica de oficio la entidad?). Sin esa respuesta legal, cualquier cifra es inventada.

**C61 | RAIS · MIX · CUM · CA**

*Ya cumple requisitos, con capacidad de ahorro.*

> Tengo semanas en un fondo privado y saldo en otro fondo, y ya tengo la edad. ¿Quién me pensiona y con cuál plata?

- **Corpus: HUECO.** Ref: reglas-rais.md s.3 y s.5; reglas-traslados.md s.5 + bonos-tiempos-publicos-y-exterior.md s.1 y s.8; modalidades-de-pension.md s.1, s.7 y s.14; aportes-voluntarios-y-sobrecotizacion.md s.4. Falta: ningún documento resuelve quién reconoce la pensión cuando hay semanas en los dos regímenes y falta el bono; bonos-tiempos-publicos-y-exterior.md s.5 lo deja en [VERIFICAR].
- **Cálculo: HUECO.** Ref: diagnosticar.py -> rais.py; comparador.py; costo_y_retorno.py (breakeven_meses y ganancia_neta: seguir cotizando vs. reclamar ya). Falta: comparador.py simula el saldo RAIS con el 11,5% e ignora bono pensional y comisiones (calculadora/README.md, aprox. 4); no consolida dos historias laborales reales; ningún módulo compara modalidades de pensión; rais.py entrega una renta vitalicia sin beneficiarios de sobrevivencia (calculadora/README.md, aprox. 1), que es justo la decisión de esa persona.
- **Comportamiento: HUECO.** Ref: Reglas duras (nunca se rompen) 1 a 8; Tu flujo de conversación (los 5 momentos); Plantilla del diagnóstico; Supuestos de toda proyección: explícitos y concretos; Siempre rango, nunca punto medio; Toda palanca se verifica antes de ofrecerla. Falta: el momento 2 de 'Tu flujo de conversación' asume UN documento y UN total impreso para la verificación cruzada (regla dura 4); no hay regla para dos historias laborales de dos administradoras; el menú de palancas de 'Toda palanca se verifica antes de ofrecerla' solo contempla 'cerca de cumplir requisitos'; no hay plantilla ni cierre para quien YA cumple, cuyo bloque 2 no es una proyección sino una decisión de cuándo reclamar.

**C62 | RAIS · MIX · CUM · SC**

*Ya cumple requisitos, sin capacidad de ahorro.*

> Ya tengo 62 y las semanas en un fondo privado, pero me falta el bono pensional de cuando fui empleado público. ¿Puedo pedir la pensión igual?

- **Corpus: HUECO.** Ref: reglas-rais.md s.3 y s.5; reglas-traslados.md s.5 + bonos-tiempos-publicos-y-exterior.md s.1 y s.8; modalidades-de-pension.md s.1, s.7 y s.14; sin-pension-alternativas.md s.2 a s.7. Falta: ningún documento resuelve quién reconoce la pensión cuando hay semanas en los dos regímenes y falta el bono; bonos-tiempos-publicos-y-exterior.md s.5 lo deja en [VERIFICAR].
- **Cálculo: HUECO.** Ref: diagnosticar.py -> rais.py; comparador.py; costo_y_retorno.py (breakeven_meses y ganancia_neta: seguir cotizando vs. reclamar ya). Falta: comparador.py simula el saldo RAIS con el 11,5% e ignora bono pensional y comisiones (calculadora/README.md, aprox. 4); no consolida dos historias laborales reales; ningún módulo compara modalidades de pensión; rais.py entrega una renta vitalicia sin beneficiarios de sobrevivencia (calculadora/README.md, aprox. 1), que es justo la decisión de esa persona.
- **Comportamiento: HUECO.** Ref: Reglas duras (nunca se rompen) 1 a 8; Tu flujo de conversación (los 5 momentos); Plantilla del diagnóstico; Supuestos de toda proyección: explícitos y concretos; Siempre rango, nunca punto medio. Falta: el momento 2 de 'Tu flujo de conversación' asume UN documento y UN total impreso para la verificación cruzada (regla dura 4); no hay regla para dos historias laborales de dos administradoras; el menú de palancas de 'Toda palanca se verifica antes de ofrecerla' solo contempla 'cerca de cumplir requisitos'; no hay plantilla ni cierre para quien YA cumple, cuyo bloque 2 no es una proyección sino una decisión de cuándo reclamar; la tabla de accionabilidad verifica régimen, edad e ingreso, no capacidad de pago; la regla de segmento de BEPS ('ofrecerlo a alguien con capacidad de pago es un error de segmento') vive en aportes-voluntarios-y-sobrecotizacion.md s.5, no en el system-prompt.

**C63 | RAIS · MIX · PEN · CA**

*Ya pensionado, con capacidad de ahorro.*

> Me pensioné con un fondo privado pero tengo un saldo viejo en un fondo privado de hace años. ¿Puedo sacar esa plata?

- **Corpus: PARCIAL.** Ref: reglas-rais.md s.3 y s.5; reglas-traslados.md s.5 + bonos-tiempos-publicos-y-exterior.md s.1 y s.8; vida-del-pensionado.md s.1 a s.5 + tributario-pensional.md s.2 y s.3; aportes-voluntarios-y-sobrecotizacion.md s.4. Falta: no hay documento que ordene la historia partida: las piezas están repartidas en traslados, bonos y reglas-rais s.7.
- **Cálculo: PARCIAL.** Ref: diagnosticar.py -> rais.py; comparador.py; costo_y_retorno.py (mesada_neta y tarifa_salud_pensionado); costo_y_retorno.py (tabla_de_escenarios: cuánto cuesta cada alternativa y en cuántos meses se recupera). Falta: comparador.py simula el saldo RAIS con el 11,5% e ignora bono pensional y comisiones (calculadora/README.md, aprox. 4); no consolida dos historias laborales reales; costo_y_retorno.py ya descuenta salud de la mesada, pero ningún módulo calcula reajuste anual, retención en la fuente, mesada 14 ni excedentes de libre disponibilidad, y diagnosticar.py está construido para proyectar hacia la pensión, no desde ella; costo_y_retorno.py resuelve el costo y el breakeven de sobrecotizar, pero ningún módulo modela el aporte voluntario propiamente dicho (rendimiento en la cuenta, comisión de la AFP, beneficio tributario del art. 126-1), que es la otra mitad de la decisión de quien tiene excedente.
- **Comportamiento: HUECO.** Ref: Reglas duras (nunca se rompen) 1 a 8; Tu flujo de conversación (los 5 momentos); Plantilla del diagnóstico; Supuestos de toda proyección: explícitos y concretos; Siempre rango, nunca punto medio. Falta: el momento 2 de 'Tu flujo de conversación' asume UN documento y UN total impreso para la verificación cruzada (regla dura 4); no hay regla para dos historias laborales de dos administradoras; no hay flujo ni plantilla para un usuario ya pensionado; la bienvenida de 'Lo que el usuario nunca ve' (cerrada el 2026-07-20) promete 'cuándo y con qué monto te vas a pensionar', que a él no le aplica.

**C64 | RAIS · MIX · PEN · SC**

*Ya pensionado, sin capacidad de ahorro.*

> Estoy pensionado por un fondo privado y me dijeron que falta cobrar una cuota parte de una entidad pública. ¿Eso qué es y me afecta?

- **Corpus: PARCIAL.** Ref: reglas-rais.md s.3 y s.5; reglas-traslados.md s.5 + bonos-tiempos-publicos-y-exterior.md s.1 y s.8; vida-del-pensionado.md s.1 a s.5 + tributario-pensional.md s.2 y s.3; sin-pension-alternativas.md s.2 a s.7. Falta: no hay documento que ordene la historia partida: las piezas están repartidas en traslados, bonos y reglas-rais s.7.
- **Cálculo: PARCIAL.** Ref: diagnosticar.py -> rais.py; comparador.py; costo_y_retorno.py (mesada_neta y tarifa_salud_pensionado). Falta: comparador.py simula el saldo RAIS con el 11,5% e ignora bono pensional y comisiones (calculadora/README.md, aprox. 4); no consolida dos historias laborales reales; costo_y_retorno.py ya descuenta salud de la mesada, pero ningún módulo calcula reajuste anual, retención en la fuente, mesada 14 ni excedentes de libre disponibilidad, y diagnosticar.py está construido para proyectar hacia la pensión, no desde ella.
- **Comportamiento: HUECO.** Ref: Reglas duras (nunca se rompen) 1 a 8; Tu flujo de conversación (los 5 momentos); Plantilla del diagnóstico; Supuestos de toda proyección: explícitos y concretos; Siempre rango, nunca punto medio. Falta: el momento 2 de 'Tu flujo de conversación' asume UN documento y UN total impreso para la verificación cruzada (regla dura 4); no hay regla para dos historias laborales de dos administradoras; no hay flujo ni plantilla para un usuario ya pensionado; la bienvenida de 'Lo que el usuario nunca ve' (cerrada el 2026-07-20) promete 'cuándo y con qué monto te vas a pensionar', que a él no le aplica; la tabla de accionabilidad verifica régimen, edad e ingreso, no capacidad de pago; la regla de segmento de BEPS ('ofrecerlo a alguien con capacidad de pago es un error de segmento') vive en aportes-voluntarios-y-sobrecotizacion.md s.5, no en el system-prompt.
- **Propuesta: FUERA DE ALCANCE.** Cuota parte pensional pendiente de una entidad pública: es un trámite de cobro entre entidades que no cambia la mesada del usuario ni admite cálculo. Es asesoría jurídica de trámite, no diagnóstico pensional.

---

## 3. Porcentaje de cobertura

### 3.1 Global

**Cobertura global: 51,8%** sobre 192 evaluaciones (64 celdas x 3 ejes).

| Estado | Evaluaciones | Peso |
|---|---|---|
| Cubierto | 47 | 24,5% |
| Parcial | 105 | 54,7% |
| Hueco | 40 | 20,8% |

### 3.2 Por eje

| Eje | Cobertura | Cubiertas | Parciales | Huecos |
|---|---|---|---|---|
| Corpus | **72,7%** | 33 | 27 | 4 |
| Cálculo | **48,4%** | 6 | 50 | 8 |
| Comportamiento | **34,4%** | 8 | 28 | 28 |

### 3.3 Por dimensión

**Régimen**

| Valor | Celdas | Cobertura total | Corpus | Cálculo | Comportamiento |
|---|---|---|---|---|---|
| Colpensiones (RPM) | 32 | **52,6%** | 70,3% | 53,1% | 34,4% |
| Fondo privado (RAIS) | 32 | **51,0%** | 75,0% | 43,8% | 34,4% |

**Situación laboral**

| Valor | Celdas | Cobertura total | Corpus | Cálculo | Comportamiento |
|---|---|---|---|---|---|
| Empleado (EMP) | 16 | **66,7%** | 96,9% | 53,1% | 50,0% |
| Independiente por cuenta propia (IND) | 16 | **66,7%** | 96,9% | 53,1% | 50,0% |
| Rentista de capital (REN) | 16 | **46,9%** | 59,4% | 43,8% | 37,5% |
| Mixto o historia partida (MIX) | 16 | **27,1%** | 37,5% | 43,8% | 0,0% |

**Momento de vida**

| Valor | Celdas | Cobertura total | Corpus | Cálculo | Comportamiento |
|---|---|---|---|---|---|
| Más de 10 años para pensionarse (M10+) | 16 | **62,5%** | 75,0% | 62,5% | 50,0% |
| Menos de 10 años (M10-) | 16 | **60,4%** | 75,0% | 56,2% | 50,0% |
| Ya cumple requisitos (CUM) | 16 | **41,7%** | 62,5% | 25,0% | 37,5% |
| Ya pensionado (PEN) | 16 | **42,7%** | 78,1% | 50,0% | 0,0% |

**Patrimonio**

| Valor | Celdas | Cobertura total | Corpus | Cálculo | Comportamiento |
|---|---|---|---|---|---|
| Con capacidad de ahorro (CA) | 32 | **51,6%** | 70,3% | 43,8% | 40,6% |
| Sin capacidad de ahorro (SC) | 32 | **52,1%** | 75,0% | 53,1% | 28,1% |

---

## 4. Huecos, ordenados por celdas afectadas

### 4.1 Huecos de corpus

| # | Celdas | Severidad | Qué falta | Celdas afectadas |
|---|---|---|---|---|
| 1 | **12** | hueco en 0, parcial en 12 | el rentista tiene una sola sección (independientes.md s.3), con [VERIFICAR] abierto sobre el fundamento y sin tratamiento de rentas mixtas | C17, C18, C19, C20, C21, C22, C49, C50, C51, C52, C53, C54 |
| 2 | **12** | hueco en 0, parcial en 12 | no hay documento que ordene la historia partida: las piezas están repartidas en traslados, bonos y reglas-rais s.7 | C25, C26, C27, C28, C31, C32, C57, C58, C59, C60, C63, C64 |
| 3 | **4** | hueco en 0, parcial en 4 | para el pensionado de Colpensiones con excedente, el corpus solo dice que el ahorro fuera del sistema no es pensión y lo declara fuera de alcance (aportes-voluntarios-y-sobrecotizacion.md s.5) | C07, C15, C23, C31 |
| 4 | **4** | hueco en 4, parcial en 0 | ningún documento resuelve quién reconoce la pensión cuando hay semanas en los dos regímenes y falta el bono; bonos-tiempos-publicos-y-exterior.md s.5 lo deja en [VERIFICAR] | C29, C30, C61, C62 |

### 4.2 Huecos de cálculo

| # | Celdas | Severidad | Qué falta | Celdas afectadas |
|---|---|---|---|---|
| 1 | **28** | hueco en 0, parcial en 28 | costo_y_retorno.py resuelve el costo y el breakeven de sobrecotizar, pero ningún módulo modela el aporte voluntario propiamente dicho (rendimiento en la cuenta, comisión de la AFP, beneficio tributario del art. 126-1), que es la otra mitad de la decisión de quien tiene excedente | C01, C03, C05, C07, C09, C11, C13, C15, C17, C19, C21, C23, C25, C27, C29, C31, C33, C35, C39, C41, C43, C47, C49, C51, C55, C57, C59, C63 |
| 2 | **16** | hueco en 0, parcial en 16 | costo_y_retorno.py ya descuenta salud de la mesada, pero ningún módulo calcula reajuste anual, retención en la fuente, mesada 14 ni excedentes de libre disponibilidad, y diagnosticar.py está construido para proyectar hacia la pensión, no desde ella | C07, C08, C15, C16, C23, C24, C31, C32, C39, C40, C47, C48, C55, C56, C63, C64 |
| 3 | **16** | hueco en 2, parcial en 14 | ningún módulo traduce rentas de capital a base de cotización; se aproxima a mano con --ibc-futuro y los coeficientes de presunción están fuera de alcance V1 (independientes.md s.8) | C17, C18, C19, C20, C21, C22, C23, C24, C49, C50, C51, C52, C53, C54, C55, C56 |
| 4 | **16** | hueco en 2, parcial en 14 | comparador.py simula el saldo RAIS con el 11,5% e ignora bono pensional y comisiones (calculadora/README.md, aprox. 4); no consolida dos historias laborales reales | C25, C26, C27, C28, C29, C30, C31, C32, C57, C58, C59, C60, C61, C62, C63, C64 |
| 5 | **8** | hueco en 0, parcial en 8 | rpm.py nombra la indemnización sustitutiva como camino (línea 332) pero no calcula su monto | C04, C06, C12, C14, C20, C22, C28, C30 |
| 6 | **8** | hueco en 0, parcial en 8 | rpm.py no implementa el piso legal del 55% de tasa de reemplazo (kit-contexto/README.md, bloque 2 punto 7) | C05, C06, C13, C14, C21, C22, C29, C30 |
| 7 | **8** | hueco en 8, parcial en 0 | ningún módulo compara modalidades de pensión; rais.py entrega una renta vitalicia sin beneficiarios de sobrevivencia (calculadora/README.md, aprox. 1), que es justo la decisión de esa persona | C37, C38, C45, C46, C53, C54, C61, C62 |

### 4.3 Huecos de comportamiento

| # | Celdas | Severidad | Qué falta | Celdas afectadas |
|---|---|---|---|---|
| 1 | **32** | hueco en 14, parcial en 18 | la tabla de accionabilidad verifica régimen, edad e ingreso, no capacidad de pago; la regla de segmento de BEPS ('ofrecerlo a alguien con capacidad de pago es un error de segmento') vive en aportes-voluntarios-y-sobrecotizacion.md s.5, no en el system-prompt | C02, C04, C06, C08, C10, C12, C14, C16, C18, C20, C22, C24, C26, C28, C30, C32, C34, C36, C38, C40, C42, C44, C46, C48, C50, C52, C54, C56, C58, C60, C62, C64 |
| 2 | **16** | hueco en 4, parcial en 12 | el menú de palancas de 'Toda palanca se verifica antes de ofrecerla' solo contempla 'cerca de cumplir requisitos'; no hay plantilla ni cierre para quien YA cumple, cuyo bloque 2 no es una proyección sino una decisión de cuándo reclamar | C05, C06, C13, C14, C21, C22, C29, C30, C37, C38, C45, C46, C53, C54, C61, C62 |
| 3 | **16** | hueco en 16, parcial en 0 | no hay flujo ni plantilla para un usuario ya pensionado; la bienvenida de 'Lo que el usuario nunca ve' (cerrada el 2026-07-20) promete 'cuándo y con qué monto te vas a pensionar', que a él no le aplica | C07, C08, C15, C16, C23, C24, C31, C32, C39, C40, C47, C48, C55, C56, C63, C64 |
| 4 | **16** | hueco en 4, parcial en 12 | la tabla de accionabilidad de 'Toda palanca se verifica antes de ofrecerla' solo contempla 'sea independiente y tenga ingreso que lo respalde'; la distinción entre patrimonio y renta vive en independientes.md s.3, no en el system-prompt | C17, C18, C19, C20, C21, C22, C23, C24, C49, C50, C51, C52, C53, C54, C55, C56 |
| 5 | **16** | hueco en 16, parcial en 0 | el momento 2 de 'Tu flujo de conversación' asume UN documento y UN total impreso para la verificación cruzada (regla dura 4); no hay regla para dos historias laborales de dos administradoras | C25, C26, C27, C28, C29, C30, C31, C32, C57, C58, C59, C60, C61, C62, C63, C64 |

---

## 5. Celdas propuestas fuera del alcance de Júbilo

Ocho de las 64 celdas se proponen fuera de alcance: cuatro perfiles, cada uno en los dos regímenes. En todas, la respuesta correcta no es un diagnóstico sino una derivación, y forzarlas dentro del producto produce un número sin decisión detrás.

| Celdas | Perfil | Razón para dejarla fuera |
|---|---|---|
| C24 y C56 | REN · PEN · SC | La pregunta es de obligación de declarar renta, no de pensión. La respuesta depende de patrimonio bruto, consignaciones y compras del año, datos que Júbilo no pide ni debe pedir. tributario-pensional.md s.2 da el marco de la renta exenta, no el test de declarante. Salida correcta: derivar a contador. |
| C20 y C52 | REN · M10- · SC | Rentista de 55 años con 400 semanas y arriendos pequeños: ningún camino del sistema lo lleva a pensión (necesitaría 900 semanas más en 7 años). El valor no está en el diagnóstico sino en indemnización sustitutiva o BEPS, y rpm.py no calcula el monto de la indemnización. Atender la pregunta con la calculadora actual produce un número sin decisión detrás. |
| C28 y C60 | MIX · M10- · SC | Historia partida con 6 años cotizados en España. Depende del Convenio Iberoamericano y de la discrepancia CMISS abierta en bonos-tiempos-publicos-y-exterior.md s.9 (¿elige el afiliado o aplica de oficio la entidad?). Sin esa respuesta legal, cualquier cifra es inventada. |
| C32 y C64 | MIX · PEN · SC | Cuota parte pensional pendiente de una entidad pública: es un trámite de cobro entre entidades que no cambia la mesada del usuario ni admite cálculo. Es asesoría jurídica de trámite, no diagnóstico pensional. |

Excluir esas 8 celdas (24 evaluaciones) sube la cobertura de las 56 celdas restantes a **53,3%**.

---

## 6. Lo que exige decisión de Santiago

1. **La quinta dimensión.** Si la matriz debe llegar a 128 celdas, hay que elegirla (recomendación: sexo). Hoy son 64.
2. **El usuario ya pensionado.** 16 de las 64 celdas son de alguien ya pensionado y el comportamiento es hueco en todas: no hay flujo ni plantilla. O se construye ese flujo, o se declara que Júbilo atiende solo hasta el momento de pensionarse.
3. **La historia partida.** 16 celdas. Es el hueco de comportamiento más caro y el corpus tampoco lo ordena en un solo documento.
4. **Los cuatro perfiles fuera de alcance** de la sección 5 (8 celdas contando ambos regímenes): aprobarlos o traerlos de vuelta al producto.

---

## 7. Recuento del 2026-07-28, tras el batch de construcción

> Corte: 2026-07-28, 13:32. Las secciones 1 a 6 son la foto del 2026-07-27 y **no se reescribieron**: esta sección mide contra ellas. Advertencia de vigencia: `kit-contexto/system-prompt.md` estaba siendo editado a las 13:31, un minuto antes del corte. Si crece después, este recuento se queda corto, no largo.

### 7.1 Cómo se contó

El método es el mismo de la sección 1.2 (cubierto = 100%, parcial = 50%, hueco = 0%) y el recuento se hizo así:

1. **Se parsearon las 64 celdas de la sección 2** y sus 192 evaluaciones directamente del archivo, no de memoria. La línea base recalculada desde el texto reprodujo exactamente los cuatro porcentajes publicados (51,8% / 72,7% / 48,4% / 34,4%), así que el punto de partida está verificado.
2. **Cada texto de "Falta:" se mapeó a uno de los 16 huecos de la sección 4.** Las 192 evaluaciones mapearon sin residuo: cero faltas huérfanas. Esto es lo que hace comparables los dos números, porque se mide contra la misma lista de huecos y no contra una nueva.
3. **Un hueco se declaró cerrado solo tras abrir el archivo y leer la pieza.** Lo que el prompt del batch anunciaba y no se encontró en disco no se contó.
4. **Una celda sube a CUBIERTO solo si TODOS sus huecos quedaron cerrados.** Con uno abierto sigue parcial, aunque se hayan cerrado dos. Una celda en hueco con parte cerrada sube a parcial, no a cubierto.

**Lo que este método NO hace, y hay que tenerlo presente al leer el 72,1%:** re-audita las celdas contra la lista de huecos del 2026-07-27, no contra el estado actual de las piezas. Un hueco nuevo que este batch haya abierto (una regla que ahora se contradice con otra, un módulo nuevo sin regla de comportamiento que lo gobierne) no aparece aquí. La cifra mide **cierre de lo que ya sabíamos que faltaba**, no ausencia de defectos.

### 7.2 Los cuatro porcentajes

| Eje | Línea base 2026-07-27 | 2026-07-28 | Delta |
|---|---|---|---|
| **Global** | 51,8% | **72,1%** | **+20,3 pp** |
| Corpus | 72,7% | **72,7%** | **0,0 pp** |
| Cálculo | 48,4% | **56,2%** | **+7,8 pp** |
| Comportamiento | 34,4% | **87,5%** | **+53,1 pp** |

Distribución de las 192 evaluaciones:

| Estado | Antes | Ahora | Delta |
|---|---|---|---|
| Cubierto | 47 | 97 | +50 |
| Parcial | 105 | 83 | -22 |
| Hueco | 40 | 12 | -28 |

**Los 12 huecos que quedan** están concentrados: 8 de cálculo (modalidades de pensión, sección 4.2 hueco 7) y 4 de corpus (quién reconoce la pensión con semanas en los dos regímenes, sección 4.1 hueco 4). **No queda ni un hueco de comportamiento.**

**Lectura conservadora, y por qué la doy.** El salto de comportamiento descansa en cuatro secciones nuevas del system prompt, y una de ellas se estira. La sección "Quien ya cumple los requisitos" está escrita en términos del RPM (su ejemplo es el IBL de Colpensiones): cierra el hueco tal como estaba enunciado, pero a un afiliado de RAIS que ya cumple no le da el cierre real, que no es "reclamar ya contra seguir cotizando" sino qué modalidad escoge. Si se degradan a parcial esas 8 celdas (C37, C38, C45, C46, C53, C54, C61, C62), el resultado es:

| Eje | Lectura mecánica | Lectura conservadora |
|---|---|---|
| Global | 72,1% | **70,6%** |
| Comportamiento | 87,5% | **82,8%** |

El rango honesto del eje de comportamiento es **82,8% a 87,5%**. La diferencia con la línea base no cambia de signo ni de orden de magnitud en ninguna de las dos lecturas.

### 7.3 Qué celdas cambiaron de estado

**54 evaluaciones cambiaron**, en 44 celdas distintas. Ninguna bajó.

**Cálculo, 10 celdas de parcial a cubierto.** Todas son celdas con capacidad de ahorro, que es exactamente el segmento al que le faltaba la mitad de la respuesta.

| Celdas | Qué las desbloqueó |
|---|---|
| C01, C03, C09, C11 (RPM · CA) y C33, C35, C41, C43 (RAIS · CA) | `aportes_voluntarios.py`: proyecta el saldo neto de comisión de administración por AFP y calcula el cupo del beneficio tributario del art. 126-1 con el techo del art. 336. Cierra el hueco 1 de la sección 4.2, el más ancho de cálculo (28 celdas) |
| C05 y C13 (RPM · CUM · CA) | El mismo módulo **más** el piso del 55% de tasa base, ya implementado en `rpm.py` (`TASA_BASE_MINIMA`, Ley 797 art. 10, con el caso L3 de `casos-liquidados.md` liquidado a mano para verificarlo). Cierra el hueco 6 de la sección 4.2 |

Las otras 18 celdas que tocaba el hueco del aporte voluntario **siguen parciales** porque arrastran un segundo hueco abierto (rentas de capital, historia partida o pensionado). Cerrar un hueco de 28 celdas movió 10: es la aritmética de los huecos que se cruzan, y es la razón de que el eje de cálculo suba menos de lo que el tamaño del batch sugiere.

**Comportamiento, 44 celdas.** Detalle en 7.4.

**Corpus, ninguna.** Ver 7.5.

### 7.4 El eje de comportamiento: de 34,4% a 87,5%

Era el eje peor y pasó a ser el mejor. Cuatro de sus cinco huecos se cerraron, todos en `kit-contexto/system-prompt.md`, que es la única fuente que este eje acepta.

| Hueco (sección 4.3) | Celdas | Estado | Pieza verificada |
|---|---|---|---|
| 1. Capacidad de pago y segmento de BEPS | 32 | **cerrado** | Fila "cualquier palanca que cueste plata" en la tabla de accionabilidad, más el párrafo del 2026-07-28 y el corolario de segmento de BEPS |
| 2. Quien ya cumple requisitos | 16 | **cerrado** | Sección "Quien ya cumple los requisitos: la pregunta no es cuándo, es si reclama ya" |
| 3. Usuario ya pensionado | 16 | **cerrado por exclusión** | Sección "Quién está fuera de alcance: el ya pensionado" |
| 4. Rentista: patrimonio contra renta | 16 | **abierto** | La fila de la tabla sigue diciendo "sea independiente y tenga ingreso que lo respalde". El mapa del kit ya enruta a `rentista-de-capital.md`, pero eso es dónde buscar, no la regla |
| 5. Dos historias laborales | 16 | **cerrado** | Sección "Historia laboral partida en dos administradoras", 6 puntos, incluido que la regla dura 4 se aplica N veces y que quién liquida lo decide la afiliación vigente |

**Tres advertencias sobre este número, porque es el que más fácil se malinterpreta:**

1. **El hueco del pensionado se cerró declarando el caso fuera de alcance, no construyendo el flujo.** Es una respuesta legítima bajo el criterio de la sección 1.2 (el agente ya no tiene que improvisar: detecta, explica y deriva) y es una de las dos salidas que la sección 6 punto 2 planteaba. Pero 16 celdas pasaron de hueco a cubierto **sin que se construyera producto para ellas**. Quien lea el 87,5% como "Júbilo ya atiende bien al pensionado" lo está leyendo al revés: lo que hace bien es no atenderlo.
2. **El propio system prompt deja un cabo suelto ahí:** dice que la bienvenida le promete al pensionado algo que no le aplica y que, mientras ese texto no cambie, la corrección la hace el agente sobre la marcha. Es una regla completa apoyada en un texto que se sabe equivocado.
3. **El comportamiento del segmento MIX quedó en 100% con el corpus en 37,5%.** La regla de cómo tratar dos historias existe y es detallada; el documento de corpus que la ordene sigue sin existir. La asimetría es real y conviene mirarla: el agente sabe qué hacer, pero el conocimiento de fondo sigue repartido entre traslados, bonos y `reglas-rais.md` s.7.

**Por dimensión, el eje de comportamiento:**

| Dimensión | Antes | Ahora |
|---|---|---|
| MIX (historia partida) | 0,0% | 100,0% |
| PEN (ya pensionado) | 0,0% | 87,5% |
| EMP e IND | 50,0% | 100,0% |
| CUM (ya cumple) | 37,5% | 87,5% |
| REN (rentista) | 37,5% | 50,0% |
| SC (sin capacidad de ahorro) | 28,1% | 87,5% |

El rentista es el único segmento que se quedó atrás en este eje, y es el mismo que se quedó atrás en corpus y en cálculo. Ver 7.6.

### 7.5 Por qué el corpus no se movió, aunque sí trabajó

**Corpus: 72,7%, delta 0,0 pp.** Ninguna de sus 64 evaluaciones cambió de estado, y no es un error de conteo. Los cuatro huecos de corpus de la sección 4.1 siguen abiertos:

- **Hueco 1, el rentista (12 celdas).** `kit-contexto/rentista-de-capital.md` existe, tiene 13 secciones y cierra la mitad del hueco tal como estaba enunciado: ya trata las rentas mixtas, la frontera con el independiente por cuenta propia y la distinción entre patrimonio e ingreso. Pero el criterio de la sección 1.2 llama parcial a lo que tiene "una marca `[VERIFICAR]` abierta o una aproximación documentada", y el documento tiene **cinco `[VERIFICAR]` abiertos**, uno de ellos el coeficiente de costos presuntos del 28,08%, que es el número sin el cual no hay IBC. El segmento pasó de un documento pobre a uno bueno con una cifra clave sin confirmar. **Es mejora de calidad, no de completitud, y esta matriz mide completitud** (sección 1.2, último párrafo).
- **Hueco 2, historia partida (12 celdas).** No se creó documento. Sigue abierto.
- **Hueco 3, pensionado con excedente (4 celdas).** No se tocó. Además, la decisión de alcance lo vuelve discutible: si el pensionado está fuera, este hueco de corpus deja de importar.
- **Hueco 4, quién reconoce con semanas en dos regímenes (4 celdas).** **La respuesta ya existe**, con norma citada (Ley 100 art. 13 lit. b, la afiliación al sistema es única), pero está escrita en `system-prompt.md`, que por definición de la sección 1.2 es el eje de comportamiento. Es el arreglo más barato que queda en todo el tablero: mover ese párrafo a `bonos-tiempos-publicos-y-exterior.md` convierte 4 huecos de corpus en cubiertos sin investigar nada nuevo.

**Trabajo del batch que subió la calidad sin mover un solo punto porcentual.** Va aquí porque leer un delta de 0,0 pp en corpus y un +7,8 pp en cálculo como "no pasó gran cosa" sería el error de lectura más caro de esta sección:

- **`independientes.md`** corrigió una regla que describía el anexo derogado del Decreto 1601 de 2022 (los dividendos "se toman completos"). El agente venía diciendo lo contrario de lo correcto. Las celdas IND ya estaban en cubierto, así que la corrección de un error de fondo no mueve el porcentaje. Es la limitación de la métrica, no del trabajo.
- **Tres defectos corregidos en `rpm.py`** (IBL de toda la vida cuando es mayor y hay 1.250 semanas por el art. 21; fecha de cumplimiento de semanas medida contra el requisito del año correcto; IBC de empleadores simultáneos topado en 25 SMLMV **del año de la cotización**). Ninguno estaba en la lista de huecos de la sección 4: eran defectos latentes, no faltantes conocidos. Cambian los números que salen, no el estado de las celdas.
- **La banda del RAIS en `rais.py`** (mesada, edad de pensión anticipada y umbral del 110% en dos extremos: 4% de interés técnico normativo contra el mayor entre capital de prensa y piso de reserva de la TMR de la Carta Circular 038 de 2026), evaluada en los dos extremos por `comparador.py` y `recuperacion.py`, que declaran cuándo no hay ganador. Es probablemente la pieza más valiosa del batch para la confianza del producto y vale 0,0 pp en esta matriz, porque los huecos de la sección 4 nunca dijeron "falta una banda": decían que faltaba el modelo de aporte voluntario o el de modalidades.
- **`casos-liquidados.md` y `probar_casos_liquidados.py`**: casos de RPM liquidados a mano desde la norma con cifra esperada auditable. Es infraestructura de verificación, que esta matriz no mide en ningún eje.
- **Datos cerrados en fuente primaria**: vector TMR de la SFC, esperanza de vida del DANE, Colombia Mayor ($230.000 desde 70 años en mujeres y 75 en hombres, no 80), Decreto 1485 de 2025 y Decreto 543 de 2026 con la advertencia de que el Fondo no recibe solicitudes hoy.

**Conclusión de método, para la próxima sesión:** esta matriz mide si la pieza existe, no si es correcta. Un batch de corrección puntúa cero. Si se quiere que el tablero refleje también la calidad, hace falta un cuarto eje de confianza del dato, y esa es una decisión de diseño, no un recálculo.

### 7.6 Huecos abiertos, ordenados por celdas afectadas

Prioridad para la próxima sesión. Los tres primeros caen sobre los mismos dos segmentos: **rentista de capital** e **historia partida**.

| # | Celdas | Eje | Hueco | Celdas afectadas |
|---|---|---|---|---|
| 1 | **16** | Cálculo | Ningún módulo traduce rentas de capital a base de cotización. `rentista-de-capital.md` s.12 deja `ibc_rentista.py` como trabajo de V1 y advierte que no debe construirse antes de cerrar el `[VERIFICAR]` del coeficiente | C17 a C24, C49 a C56 |
| 2 | **16** | Comportamiento | La regla de patrimonio contra renta no está en el system prompt. Único hueco de comportamiento que sobrevive | C17 a C24, C49 a C56 |
| 3 | **16** | Cálculo | `comparador.py` sigue simulando el saldo del RAIS con el 11,5% e ignorando bono pensional y comisiones. **Ojo:** la otra mitad de este hueco (consolidar dos historias reales) **sí se cerró** en `diagnosticar.py`, pero la celda no sube porque el hueco es uno solo | C25 a C32, C57 a C64 |
| 4 | **16** | Cálculo | Nada calcula reajuste anual, retención en la fuente, mesada 14 ni excedentes de libre disponibilidad. **Discutible:** son las 16 celdas de pensionado, hoy declaradas fuera de alcance | C07, C08, C15, C16, C23, C24, C31, C32, C39, C40, C47, C48, C55, C56, C63, C64 |
| 5 | **12** | Corpus | No hay documento del kit que ordene la historia partida | C25, C26, C27, C28, C31, C32, C57, C58, C59, C60, C63, C64 |
| 6 | **12** | Corpus | El rentista tiene documento propio pero con 5 `[VERIFICAR]` abiertos, incluido el coeficiente de costos | C17 a C22, C49 a C54 |
| 7 | **8** | Cálculo | Ningún módulo compara modalidades de pensión; `rais.py` sigue entregando renta vitalicia sin beneficiarios de sobrevivencia (limitación V1 declarada en el propio módulo). **Es el único hueco que deja celdas en cero** | C37, C38, C45, C46, C53, C54, C61, C62 |
| 8 | **8** | Cálculo | `rpm.py` nombra la indemnización sustitutiva como camino pero no liquida su monto | C04, C06, C12, C14, C20, C22, C28, C30 |
| 9 | **4** | Corpus | Quién reconoce la pensión con semanas en los dos regímenes. **El más barato del tablero:** la respuesta ya está escrita en el system prompt, falta moverla al corpus | C29, C30, C61, C62 |
| 10 | **4** | Corpus | Pensionado de Colpensiones con excedente. Discutible por la decisión de alcance | C07, C15, C23, C31 |

**Dónde está la palanca.** Cerrar el `[VERIFICAR]` del coeficiente de costos de la Resolución UGPP 532 desbloquea el hueco 6, habilita construir el módulo del hueco 1 y le da sustento a la regla del hueco 2: **44 celdas de las 64 quedan tocadas por una sola verificación**, que además es un trámite (portal de transparencia de la UGPP), no una investigación jurídica.

**El segmento REN es el rezagado neto del batch:** 51,0% global contra 88,5% de EMP e IND. Es el único segmento que no mejoró en ningún eje pese a haber recibido un documento nuevo completo.

### 7.7 Pendiente de decisión de Santiago o del abogado

No se resolvió ninguna de estas aquí. Las cuatro de la sección 6 siguen vigentes, con dos ya afectadas por lo que este batch decidió.

**De Santiago:**

1. **El universo de la matriz, ahora que el pensionado está fuera de alcance.** El system prompt ya lo excluye, pero las 16 celdas PEN siguen contando en el denominador. Con ellas afuera (48 celdas), los números son: global **72,2%**, corpus 70,8%, cálculo 58,3%, comportamiento 87,5%. Casi iguales al de 64 celdas, así que la decisión no es cosmética por el número sino por qué se sigue midiendo. Recomendación: sacarlas del denominador y dejarlas listadas como excluidas, como ya hace la sección 5 con sus ocho.
2. **El texto de la bienvenida.** Hoy promete "te digo cuándo y con qué monto te vas a pensionar", que es justo lo que no le aplica al pensionado que el agente debe detectar y derivar. El system prompt asume que el texto no ha cambiado. Es una decisión de copy, no de producto.
3. **Si el rendimiento vigente es el prospectivo o el observado.** Verificado en `datos_sistema.py`: `RENDIMIENTO_REAL` apunta hoy al **prospectivo de largo plazo**, con el observado de la SFC 2011-2024 conservado como evidencia y la advertencia de que el moderado rindió menos que el conservador en el periodo medido. Está aplicado y documentado; queda registrar que es decisión tomada y no supuesto heredado.
4. **La quinta dimensión** (sección 6 punto 1). Sin cambios: la matriz sigue en 64 celdas.
5. **Los cuatro perfiles fuera de alcance** de la sección 5. Sin cambios, y ahora se cruzan con la exclusión del pensionado: C24 y C56 estaban excluidas por ser pregunta tributaria, y además son PEN.
6. **Si esta matriz debe medir calidad además de completitud** (ver 7.5). Hoy un batch de correcciones de norma puntúa cero.

**Del abogado pensional, en orden de celdas que desbloquean:**

1. **Coeficiente de costos presuntos de rentas de capital** (Resolución UGPP 532 de 2024, anexo no público). Toca 44 celdas por las tres vías descritas arriba. Hoy el kit usa 28,08% declarado como estimación de fuentes secundarias.
2. **Si los dividendos entran en la presunción de costos.** El anexo del Decreto 1601 de 2022 los excluía y fue derogado por el Decreto 379 de 2026; no se sabe qué dice el renglón vigente. Cambia el IBC de un rentista de dividendos en más de un cuarto.
3. **Ganancias ocasionales en el IBC del rentista** (`rentista-de-capital.md` s.2). Quien vendió un inmueble en el año podría estar obligado a cotizar sobre ese valor. Caso frecuente y de monto alto.
4. **Convenio Iberoamericano: elige el afiliado o aplica de oficio la entidad la vía más favorable** (`bonos-tiempos-publicos-y-exterior.md` s.9). Es la discrepancia CMISS que mantiene a C28 y C60 fuera de alcance.
5. **Edades de exclusión de la obligación de cotizar del rentista** (50 y 55 años, según el ABC de la UGPP sin artículo citado). El error posible es en la dirección cara: decirle a alguien que no está obligado cuando sí lo estaba.

### 7.8 Actualización del 2026-09-16: cerrado el coeficiente de rentistas

No reescribe el recuento del 2026-07-28 de las secciones 7.6 y 7.7, que queda como registro de esa fecha. Lo corrige por encima.

**Qué se cerró.** Las dos primeras marcas del pendiente del abogado de la sección 7.7, y sin abogado ni derecho de petición:

1. **El coeficiente de costos presuntos de rentas de capital.** 28,08%, leído en la calculadora oficial de IBC de la UGPP, que trae la tabla completa de 24 renglones embebida en su selector de actividad económica. El kit lo venía usando con fuentes secundarias.
2. **Si los dividendos entran en la presunción.** Sí. El renglón vigente se rotula "Rentistas de Capital incluidos dividendos y participaciones", que es la inversión exacta del paréntesis del anexo derogado del Decreto 1601 de 2022.

*Evidencia, método y límites en `verificacion/2026-09-16-coeficiente-rentista-ugpp.md`, con la captura y su hash en `verificacion/evidencia/`.* Lo que la calculadora no da es el texto del acto administrativo: no cita norma, así que la cifra se atribuye a la conducta oficial de la UGPP.

**Lo que hay que decir de una vez, porque es contraintuitivo: cerrar esta marca no sube ni una celda.** La sección 7.6 anunciaba que una sola verificación tocaba 44 celdas, y es cierto, pero las tocaba por tres vías y ninguna de las tres se completa sola:

| Hueco de 7.6 | Qué le pasó | Celdas |
|---|---|---|
| 1. Ningún módulo traduce rentas de capital a IBC | **Desbloqueado, no cerrado.** `ibc_rentista.py` ya se puede construir y `rentista-de-capital.md` s.12 ya trae la fórmula que debe implementar. Mientras no exista el módulo, la celda no se mueve | C17 a C24, C49 a C56 |
| 2. La regla de patrimonio contra renta no está en el system prompt | **Sin cambio.** No dependía de esta verificación | C17 a C24, C49 a C56 |
| 6. El rentista tiene documento propio con 5 marcas abiertas | **Mejora sin cambiar de estado.** Baja de 5 marcas a 3, más el residuo de la fecha de vigencia. Con una sola marca abierta la celda sigue siendo parcial bajo el criterio de la sección 1.2 | C17 a C22, C49 a C54 |

**Los porcentajes de cobertura no se recalculan aquí.** Ninguna celda cambió de estado, así que el recuento del 2026-07-28 sigue vigente tal como está. El próximo recuento se hace cuando exista `ibc_rentista.py`, que es el trabajo que esta verificación habilitó.

**Cómo queda el pendiente del abogado de 7.7.** Salen los puntos 1 y 2. Quedan tres, renumerados:

1. **Ganancias ocasionales en el IBC del rentista** (`rentista-de-capital.md` s.2). Dato nuevo, débil pero útil: la calculadora oficial no las menciona ni las excluye. Es ausencia de prueba, no prueba de ausencia.
2. **Convenio Iberoamericano: elige el afiliado o aplica de oficio la entidad la vía más favorable** (`bonos-tiempos-publicos-y-exterior.md` s.9). Mantiene C28 y C60 fuera de alcance.
3. **Edades de exclusión de la obligación de cotizar del rentista** (50 y 55 años). La calculadora oficial repite la regla con esas mismas edades y sigue sin citar artículo. El error posible es en la dirección cara.

**Lo que queda para gestión externa, ya sin ser bloqueante de producto:** el texto y anexo de la resolución (respaldo normativo), la fecha de publicación del Decreto 379 en el Diario Oficial, y las dos providencias de la s.11 del documento del rentista, que no son de la UGPP y se consiguen en los buscadores del Consejo de Estado y de la Corte Constitucional.

**Efecto lateral que sí amplía cobertura, aunque no en estas celdas:** la tabla completa por actividad CIIU entró al kit en `independientes.md` s. 2 bis. El agente pasó de poder dar el coeficiente de un solo perfil a poder darlo para cualquier independiente por cuenta propia.

**Lección de método, que vale más que el dato.** La marca llevaba semanas esperando un derecho de petición porque el kit asumió que el anexo no era público. La cifra estaba en el HTML de la herramienta oficial de la entidad, a una descarga de distancia. Antes de escalar una marca a trámite o a abogado, conviene revisar si la entidad ya está aplicando el dato en alguna herramienta pública: una calculadora web tiene que descargar sus parámetros al navegador para poder calcular.

---

## 8. Decisión del 2026-09-16: el pensionado sale del universo

> Las secciones 1 a 7 son fotos de julio y **no se reescriben**. Esta sección registra una decisión de alcance posterior y su efecto sobre el tablero.

**Decisión de Santiago:** el usuario ya pensionado queda **totalmente fuera de alcance**. No es un segmento desatendido ni un hueco por llenar: es un caso que el producto no atiende y en el que no se invierte foco.

**Cómo se ejecutó** (`kit-contexto/system-prompt.md`, sección "Quién está fuera de alcance: el ya pensionado"):
- **Sin paso nuevo de filtro.** No se pregunta si está pensionado. Habría costado un turno a todos los usuarios para atrapar a unos pocos que no son el mercado.
- **Detección pasiva** durante la conversación normal, por cuatro señales: lo dice él mismo, habla de su pensión en presente, manda un desprendible de mesada o una resolución en vez de una historia laboral, o la historia laboral trae estado de pensionado.
- **La bienvenida no se cambia.** "Te digo cuándo y con qué monto te vas a pensionar" es verdad y describe a quién sirve el producto: hace el filtro sola. Queda revertida la lectura anterior de que era un defecto.
- **Respuesta:** un solo mensaje corto y amable que deriva al fondo, a Colpensiones o a un abogado pensional. Sin plantilla, sin flujo, sin diagnóstico parcial.

**Efecto sobre el tablero.** Las 16 celdas PEN (C07, C08, C15, C16, C23, C24, C31, C32, C39, C40, C47, C48, C55, C56, C63, C64) salen del denominador. Sobre las 48 restantes: global **72,2%**, corpus 70,8%, cálculo **58,3%**, comportamiento 87,5%.

**El valor no está en el porcentaje, está en el trabajo borrado.** Cuatro de los diez huecos abiertos de la sección 7.6 desaparecen o se colapsan:

| Hueco de 7.6 | Celdas | Qué pasa |
|---|---|---|
| #4, Cálculo: reajuste anual, retención en la fuente, mesada 14, excedentes de libre disponibilidad | 16 | **Desaparece.** Era todo modelado para el pensionado |
| Comportamiento: no hay flujo ni plantilla para el pensionado (hueco #3 de la sección 4.3) | 16 | **Se colapsa** a una regla de detección y un mensaje. Deja de ser cero |
| #10, Corpus: pensionado de Colpensiones con excedente | 4 | **Desaparece** |
| Parte del #1 de cálculo (aporte voluntario) que caía sobre celdas PEN | 8 de 28 | Se reduce el alcance del hueco |

**Lo que NO cambia:** el corpus del pensionado se queda en el kit. Se le responde a quien todavía no se ha pensionado, porque cómo se cobra la pensión es parte de decidir cuándo pensionarse.

**Pendiente asociado:** la decisión 2 de la sección 7.7 ("el texto de la bienvenida") queda **cerrada sin cambio**. La decisión 1 ("el universo de la matriz") queda **cerrada**: el denominador es 48.
