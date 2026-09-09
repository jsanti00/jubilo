# Regímenes especiales y exceptuados - Documento 5 del kit

> **Última actualización:** 2026-07-18. **Propósito:** este documento NO enseña a calcular estos regímenes (fuera de alcance V1). Enseña al router y al agente a **detectarlos, decirlo honestamente y orientar a dónde ir**. Responder "eso no lo cubro aún, y esto es lo que sé" es parte del diseño anti-alucinación.

## 1. Exceptuados de la Ley 100 (Art. 279)

| Régimen | Quiénes | Señal de detección en la conversación o el documento |
|---|---|---|
| Fuerzas Militares y Policía | Militares y policías (asignación de retiro, no pensión) | Empleador: Ministerio de Defensa, Ejército, Armada, FAC, Policía Nacional; Cajas: CREMIL, CASUR |
| Magisterio | Docentes oficiales vinculados hasta el corte legal | Empleador: secretarías de educación; menciona FOMAG o "Ley 91" |
| Ecopetrol | Trabajadores con régimen convencional antiguo | Empleador: Ecopetrol; menciona "convención colectiva" |

**Respuesta estándar:** "Tu régimen es exceptuado de la Ley 100; mis cálculos no aplican. Tu entidad es [CREMIL/CASUR/FOMAG/Ecopetrol] y allá está tu información." Si además tiene semanas en Colpensiones o un fondo (carreras mixtas), esas sí se pueden leer y contar, aclarando el límite.

## 2. Situaciones especiales dentro de la Ley 100 (detectar y acotar)

| Situación | Regla esencial | Qué hace el agente V1 |
|---|---|---|
| Régimen de transición | Terminó el 31 de diciembre de 2014 (Acto Legislativo 01/2005); beneficiaba a quienes en 1994 tenían 35/40 años o 15 de servicios | Si el usuario se pensionó o debió pensionarse bajo transición: decir que ese cálculo (Decreto 758/1990 u otro) no está cubierto |
| Alto riesgo (Decreto 2090/2003) | Mineros socavón, bomberos, controladores aéreos, INPEC, etc.: edad reducida con cotización adicional | Detectar por oficio del usuario o cotización especial en el reporte; decir que la edad especial no está simulada |
| Pensión familiar (Ley 1580/2012) | Cónyuges suman semanas para una sola pensión | Explicar requisitos con `beneficiarios-y-sobrevivientes.md`; no simular el monto |
| BEPS | Ahorro flexible con subsidio estatal del 20%, tope de anualidad del 85% de 1 SMLMV y reglas de incompatibilidad que sí cambian decisiones | Explicar con `sin-pension-alternativas.md`, incluidas las incompatibilidades; no simular el monto |
| Madre/padre de hijo con discapacidad | Pensión especial anticipada (Ley 797 art. 9 par. 4) | Detectar y recomendar abogado; no simular |
| Invalidez e incapacidades | Prestaciones por pérdida de capacidad laboral y pago de incapacidades | Ya no es "fuera de alcance": explicar con `invalidez-e-incapacidades.md`; sigue sin calcularse la mesada ni estimarse el porcentaje de PCL |

## 3. Reglas de conversación

1. **Detectar temprano:** el router pregunta o infiere del documento antes de prometer un diagnóstico.
2. **Nunca calcular con las fórmulas de RPM/RAIS** para un exceptuado: sale un número con apariencia de verdad y base falsa (el peor error posible del producto).
3. **Carreras mixtas** (años de Policía + años de empresa privada): calcular solo la parte Ley 100, nombrar la otra y sugerir dónde consultarla.
4. Registrar cada caso exceptuado que llegue al piloto: son la lista de espera de futuros módulos.
