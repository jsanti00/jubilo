# Reglas operativas RAIS (fondos privados) - Documento 3 del kit

> **Última actualización:** 2026-07-18. **Estado:** destilado inicial bajo Ley 100 de 1993 vigente. Marcas `[VERIFICAR]` para el abogado pensional o actuario antes del piloto.
> **Convención:** cada regla cita su fuente legal. La calculadora implementa estas reglas tal cual; si una regla cambia, se cambia aquí primero.

## 1. Qué es el RAIS

Régimen de Ahorro Individual con Solidaridad, administrado por las AFP (Porvenir, Protección, Colfondos, Skandia). Cada afiliado tiene una **cuenta individual**: la pensión depende del **saldo acumulado más sus rendimientos**, no de una fórmula sobre el salario. *Fuente: Ley 100 de 1993, arts. 59-60.*

**Diferencia central con el RPM:** aquí no hay tasa de reemplazo definida por ley; el capital ahorrado se convierte en mesada. Más ahorro y más rendimiento = más pensión, sin techo del 80%.

## 2. Cotización

| Concepto | Regla | Fuente |
|---|---|---|
| Tasa total | 16% del IBC (misma que RPM) | Ley 100 art. 20, mod. Ley 797/2003 art. 7 |
| Destino del 16% | 11,5% a la cuenta individual + 1,5% al Fondo de Garantía de Pensión Mínima + 3,0% comisión de administración y seguros previsionales | Ley 797/2003 art. 7 y reglamentación posterior; marca 1 de `supuestos-actuariales.md` s.4 |
| IBC mínimo / máximo | 1 SMLMV / 25 SMLMV | Ley 100 art. 18, mod. Ley 797/2003 art. 5 |
| Fondo de Solidaridad Pensional | Igual que RPM: +1% desde 4 SMLMV, más un escalonado de +0,2% a +1% desde 16 SMLMV (tabla completa en `reglas-rpm.md` s.2) | Ley 100 art. 27, mod. Ley 797/2003 art. 8 |

**Implicación clave para la calculadora:** de cada $100 cotizados, solo $71,9 llegan a la cuenta del afiliado (11,5 de 16). El resto es garantía colectiva y comisión.

## 3. Tres salidas posibles (en orden de evaluación)

1. **Pensión por capital (a cualquier edad):** si el saldo alcanza para financiar una renta vitalicia de al menos el **110% del SMLMV**, el afiliado se puede pensionar sin importar edad ni semanas. *Fuente: Ley 100 art. 64.* Es la vía de los altos ahorradores y el mayor "aha" del RAIS: la pensión anticipada existe.
2. **Garantía de Pensión Mínima (GPM):** si a los **57 años (mujer) / 62 (hombre)** el saldo no alcanza, pero tiene las semanas mínimas, el Fondo de Garantía completa lo necesario para una mesada de 1 SMLMV. *Fuente: Ley 100 art. 65.*
   - **Hombres: 1.150 semanas.**
   - **Mujeres: bajan 15 semanas por año desde 2026** (1.135 en 2026, 1.120 en 2027) hasta el piso de **1.000 en 2035**. *Fuente: Sentencia C-054 de 2024, que declaró inexequible la exigencia de 1.150 semanas en cuanto a sus efectos para las mujeres, difirió los efectos al 31 de diciembre de 2025 y fijó esta regla supletiva, hoy operando porque el Congreso no legisló.* **Verificado el 2026-07-21 contra la relatoría de la Corte.**
   - Es la contraparte en el RAIS de lo que la C-197 de 2023 hizo en el RPM, pero por una sentencia distinta y con otra escala. **No confundir las dos tablas.** La del RPM está en `reglas-rpm.md`; ambas viven codificadas en `calculadora/datos_sistema.py` (`semanas_gpm` y `semanas_requeridas`).
3. **Devolución de saldos:** si no alcanza pensión ni GPM, se devuelve el saldo **con rendimientos** (y el bono pensional si existe). *Fuente: Ley 100 art. 66.*

## 4. Modalidades de pensión

Retiro programado (el saldo queda en la AFP y se recalcula cada año), renta vitalicia (una aseguradora paga de por vida) y modalidades mixtas. *Fuente: Ley 100 art. 79-81.* **V1 aproxima todo como renta vitalicia** (la modalidad más conservadora y estable para estimar).

## 5. Conversión de capital a mesada (aproximación V1)

```
mesada = saldo_proyectado / factor
factor = 13 mesadas x valor presente de una anualidad
         (expectativa de vida a la edad de pensión, interés técnico 4% real)
```

- Expectativa usada (tablas RV08, **valores exactos verificados el 2026-07-27**): mujer a los 57, **29,7 años**; hombre a los 62, **21,3 años**.

**Verificado el 2026-07-27, ya no es marca:** los valores exactos salieron de la tabla oficial completa de la *Resolución 1555 de 2010 de la Superfinanciera* (rentistas válidos), leída directamente del PDF. Confirmaron los aproximados que el kit venía usando. La tabla por edades está en `supuestos-actuariales.md` marca 3. **Lo que sigue abierto es el interés técnico** (marca 2 de ese documento), que es lo que de verdad mueve el factor de conversión y va al actuario.
- **Limitación conocida de V1:** no incluye beneficiarios de sobrevivencia (cónyuge, hijos), que encarecen la renta. La mesada real puede ser **menor** a la estimada; por eso toda cifra se presenta como rango y con supuestos visibles.

## 6. Multifondos: perfiles, asignación por defecto y convergencia

Tres perfiles desde la Ley 1328 de 2009: **conservador, moderado y mayor riesgo**. Los supuestos de rendimiento real por perfil están en `supuestos-actuariales.md` (2%, 4% y 5% real, con su marca `[VERIFICAR]` y su respuesta operativa en la sección 3 de ese documento: se usan siempre como rango, y falta cotejarlos contra la serie real de la Superfinanciera).

### Qué asigna la ley a quien nunca eligió (Decreto 959 de 2018, vigente desde marzo de 2019)

**La asignación por defecto depende de la edad y el sexo, no es "moderado" para todos.** Antes de 2019 sí era moderado para todos; el Decreto 959 lo cambió para que los jóvenes aprovechen el tiempo:

| Etapa | Mujeres | Hombres | Asignación por defecto |
|---|---|---|---|
| Acumulación temprana | hasta 41 | hasta 46 | **100% mayor riesgo** |
| Transición a moderado | 42 a 45 | 47 a 50 | Traslado gradual de mayor riesgo a moderado (20 puntos porcentuales por año) |
| Consolidación | 46 a 51 | 51 a 56 | **100% moderado** |
| Convergencia a conservador | desde 52 | desde 57 | Traslado gradual a conservador (20 puntos porcentuales por año), empezando con 20% conservador y 80% moderado |
| Edad de pensión | 57+ | 62+ | **100% conservador** |

`[VERIFICAR]` **Respuesta operativa:** el agente usa la tabla de arriba, **pero solo como punto de partida de una pregunta, nunca como dato del usuario**. Esto ya está resuelto por la regla de la sección "Cómo lo usa el agente": al perfil no se le adivina, se le pregunta o se lee en el extracto. Por eso una imprecisión en el cronograma no puede colarse a un diagnóstico como si fuera un hecho. El marco normativo sí está confirmado: el **Decreto 959 del 5 de junio de 2018** modificó el Decreto 2555 de 2010 (art. 2.6.11.1.6) y creó las reglas de asignación por defecto para quien no elige, diferenciadas por sexo y edad, con migración gradual. **Falta confirmar:** la tabla literal año por año dentro de ese artículo. La investigación del 2026-07-26 no pudo abrir el texto (fallas de certificado en Función Pública y SUIN Juriscol) y las edades de corte y los saltos de 20 puntos vienen de fuentes secundarias que coinciden entre sí. **Si cambia:** movería el escenario por defecto de un afiliado posterior a 2019 que nunca eligió, no el de quien confirma su perfil.

**Reglas prácticas que se derivan:**
1. **El default de "mayor riesgo para jóvenes" solo aplica limpio a quien se afilió desde marzo de 2019.** Antes de esa fecha el default era **moderado para todos**. Por eso NO se puede asumir que un joven está en mayor riesgo solo por su edad: si se afilió antes de 2019 y nunca se movió, probablemente sigue en moderado (o en una mezcla de transición). Al entrar el Decreto 959, las AFP migraron los flujos nuevos de aportes, pero el saldo ya acumulado se trasladó de forma gradual con reglas propias.

   `[VERIFICAR]` **Respuesta operativa:** el agente le dice al usuario afiliado antes de 2019 que **su saldo puede estar repartido entre dos perfiles**, y que por eso el número exacto solo sale de su extracto. No inventa la proporción. **Falta confirmar:** el mecanismo exacto de migración de flujo frente a saldo y sus tiempos, en el texto del Decreto 959 de 2018. **Si cambia:** cambiaría lo que el agente puede suponer de alguien que no consulta su extracto. **Por qué esto no bloquea nada:** el efecto práctico ya está cubierto por la regla de mostrar el rango de los tres perfiles cuando el perfil no está confirmado. Es la aplicación literal de "siempre rango, nunca punto medio" del system prompt, y aquí funciona además como salvaguarda.
2. **Quien eligió alguna vez conserva su elección**: la asignación por defecto no lo toca.
3. Se puede cambiar de perfil **cada seis meses** (o de inmediato si no está conforme con la asignación por defecto).

   `[VERIFICAR]` **Respuesta operativa:** el agente responde **"cada seis meses, y el trámite lo haces en tu fondo"**, sin prometer el cambio inmediato como un derecho. La regla de los seis meses es la que puede afirmar; la puerta del cambio inmediato existe pero sus condiciones no están verificadas. **Falta confirmar:** las condiciones exactas del cambio inmediato en el texto del Decreto 959 de 2018 y en la reglamentación de la Superfinanciera. **Si cambia:** solo afecta el **cuándo**, no el **si**. **Por qué la respuesta conservadora es la correcta aquí:** el perfil es una de las palancas gratuitas más potentes que tiene un joven, así que lo importante es que el usuario sepa que puede moverlo y vaya a su fondo. Prometerle que se lo cambian el mismo día y que no ocurra convierte una buena noticia en una frustración con el producto.
4. **El perfil sí aparece en el extracto de la cuenta** (no en la historia laboral). Verificado en un extracto real de Protección: la sección "Fondo donde están mis aportes" muestra el perfil y el porcentaje (ej. "100,00% Mayor riesgo"). Cómo consultarlo por administradora: `tramites-y-consultas.md`.

**Consecuencia para el escenario base:** por lo anterior, la edad y el sexo NO bastan para saber el perfil de nadie que se haya afiliado antes de 2019. La única vía confiable es preguntar (ver abajo) o leer el extracto de la cuenta. Solo para afiliados posteriores a marzo de 2019 que nunca eligieron se puede usar la tabla de default como escenario base.

### Cómo lo usa el agente

En vez de pedirle al usuario un dato técnico que quizá no conoce, se le pregunta por lo que sí sabe: **"¿alguna vez cambiaste el perfil de tu fondo (conservador, moderado o mayor riesgo)?"**
- **Sí**: se le pregunta en cuál quedó y se le indica dónde confirmarlo en su extracto (`tramites-y-consultas.md`).
- **No / no sabe, y se afilió desde marzo de 2019**: se usa la tabla de default según edad y sexo como escenario base, diciéndole cuál es.
- **No / no sabe, y se afilió antes de 2019**: NO se asume. Probablemente está en moderado (default viejo), pero pudo migrar parcialmente. Se le pide confirmar en el extracto ("Fondo donde están mis aportes"), y mientras tanto se presenta el rango completo de perfiles en lugar de un solo escenario base.
- **En cualquier caso**, se le recuerda que el perfil se puede cambiar (palanca gratis de las más potentes a edad temprana).

## 7. Semanas en otros fondos y bonos pensionales

- El reporte de una AFP puede incluir el detalle de fondos anteriores tras un traslado (verificado en caso-03: Protección hereda el detalle de Porvenir). El **total de semanas incluye todas las administradoras**.
- Quien cotizó al ISS/Colpensiones antes de trasladarse al RAIS suele tener un **bono pensional** que se suma al capital al pensionarse.

`[VERIFICAR]` **Respuesta operativa:** el agente **detecta el bono, lo menciona como plata adicional que hoy no está en el cálculo, y no lo suma**. Tres cosas sí puede afirmar: (a) quien cotizó **menos de 150 semanas al ISS** antes de trasladarse **no tiene bono** (*Ley 100 art. 115, parágrafo*); (b) el bono tipo A se redime a los **62 años el hombre y a los 60 la mujer**, no a los 57 (*Decreto 1299 de 1994 art. 3*); y (c) por lo anterior, **en todo escenario de pensión anticipada el bono no está disponible ese día**. **Falta confirmar:** la fórmula de cálculo del bono, y qué pasa exactamente cuando alguien se pensiona antes de la fecha de redención (si se negocia, si se descuenta a valor presente, o si la AFP financia con el resto del saldo). **Si cambia:** al alza. Sumar el bono aumentaría el capital, así que la postura actual **subestima a propósito**. Es la dirección correcta del error: el usuario se lleva una sorpresa buena, no una mala. **Regla dura, ya escrita en `bonos-tiempos-publicos-y-exterior.md`:** no sumar el bono al capital de un escenario de pensión anticipada hasta que el abogado lo verifique.

## 8. Devolución de saldos vs. indemnización sustitutiva (regla de asesoría clave)

| | RAIS: devolución de saldos | RPM: indemnización sustitutiva |
|---|---|---|
| Qué devuelven | Saldo de la cuenta | Aportes indexados |
| Rendimientos | **Sí** (todo lo que ganó la cuenta) | **No** (solo inflación) |

Para quien probablemente no alcanzará pensión, esta diferencia es central en la decisión de régimen.

## 9. Fuera de alcance V1 (el router lo detecta y lo dice)

**Sin cálculo, pero ya con respuesta informativa** (actualizado 2026-07-21: tienen documento propio; lo que sigue fuera es *calcular*, no *explicar*):

- Pensión de invalidez: ver `invalidez-e-incapacidades.md`.
- Pensión de sobrevivientes y seguro previsional: ver `beneficiarios-y-sobrevivientes.md`.
- Excedentes de libre disponibilidad (Ley 100 art. 85) y modalidades: ver `modalidades-de-pension.md`.
- Fiscalidad de los aportes voluntarios: ver `tributario-pensional.md`.
- Bono pensional: ver `bonos-tiempos-publicos-y-exterior.md` (el cálculo sigue fuera; solo se detecta y explica).

**Fuera de alcance del todo:**

- Retiro programado con recálculo anual (V1 aproxima todo como renta vitalicia).

## 10. Relación con traslados

Misma regla del RPM: **bloqueado a menos de 10 años de la edad de pensión** (mujer desde 47, hombre desde 52), con doble asesoría obligatoria antes. El comparador de regímenes (RPM vs. RAIS con los dos módulos de la calculadora) es el corazón de esa asesoría: detalle en `reglas-traslados.md` (pendiente).
