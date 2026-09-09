# Set dorado de historias laborales (V0)

> **Última actualización:** 2026-07-13. Estado: 5 casos extraídos y verificados (0,00-0,01 semanas de diferencia contra el total impreso de cada documento).

**Qué es:** los casos de ejemplo del documento 9 del kit de contexto. Cada caso es un JSON con el [esquema de datos](esquema-datos.md), extraído a mano en laboratorio y verificado contra los totales del documento original. Sirven como ejemplos few-shot para la extracción del agente y como casos de prueba de la calculadora.

## Procedencia y anonimización

Los seis casos salen de historias laborales reales, extraídas a mano y verificadas
contra el total impreso de cada documento. Cinco vienen de personas que dieron su
documento voluntariamente; el sexto es un PDF público encontrado en internet.

**Qué se quitó antes de publicarlos:** nombre, cédula, correo y dirección del
titular no estaban en el JSON desde el principio. Además, aquí se reemplazó el
nombre de cada empleador por una etiqueta (`EMPLEADOR-01`, `EMPLEADOR-02`, ...)
y se anularon los NIT, porque la combinación de empleador, fechas y salario
permite reconocer a una persona aunque su nombre no aparezca. La correspondencia
entre caso y persona no vive en este repositorio.

**Qué se conservó:** todas las cifras. Semanas, salarios base, fechas de
cotización y fecha de nacimiento quedaron intactas, porque son exactamente lo que
estos casos existen para verificar. Cambiarlas convertiría el set dorado en
decoración.

| Caso | Fondo / Régimen | Semanas | Verificación |
|---|---|---|---|
| caso-01-porvenir-rais | Porvenir / RAIS | 205,28 | PASA |
| caso-02-skandia-rais | Skandia / RAIS | 154,43 | PASA |
| caso-03-proteccion-rais | Protección / RAIS | 265,71 | PASA |
| caso-04-colpensiones-rpm | Colpensiones / RPM | 1.478,43 | PASA |
| caso-05-colpensiones-rpm | Colpensiones / RPM | 1.236,57 | PASA |
| caso-06-colfondos-rais | Colfondos / RAIS | 398,0 | DISCREPANCIA DOCUMENTAL |

## Herramientas (`herramientas/`)

- `parser_resumen_colpensiones.py`: convierte la tabla resumen de un reporte Colpensiones (texto) al esquema JSON. Herramienta de laboratorio; en producción la extracción la hace la IA.
- `parser_colfondos.py`: ídem para el reporte de historia laboral de Colfondos (filas mensuales, números estilo estadounidense).
- `verificar_casos.py`: recalcula las semanas de cada caso desde sus periodos y las compara contra el total impreso. Correr después de agregar o editar cualquier caso.

## Hallazgos de extracción (insumos para el agente)

1. **PDFs sin capa de texto existen** (caso-03: el PDF re-guardado tras quitarle la contraseña quedó como imagen). La extracción necesita lectura visual como respaldo.
2. **Regla del día exacto en Colpensiones:** el total impreso se calcula desde días exactos; sumar las filas redondeadas sobreestima (+0,70 semanas en 293 filas).
3. **Semanas contadas una sola vez con empleadores simultáneos:** verificado en caso-03 (mes con dos empleadores, 43 días reportados, 30 contados) y caso-04 (doble cotización empleada + independiente durante años, con una fila marcada simultánea en 0).
4. **Meses COVID (Decreto 558/2020):** aparecen con semanas parciales (0,86) en ambas filas; el documento las cuenta como válidas para el requisito de 1.300 semanas.
5. **El reporte de un fondo puede incluir periodos de otro** (caso-03: Protección hereda el detalle de Porvenir tras el traslado, con la columna "Origen de la información").
6. **Formato Colfondos** (caso-06): filas mensuales con números estilo estadounidense (1,000,000.00), meses en cero impresos como filas (lagunas explícitas), aportantes sin identificar (NIT "0", nombre "."), y el total del encabezado es "al sistema general" (incluye otros fondos).
7. **Los documentos pueden no cuadrar consigo mismos** (caso-06): la tabla suma 407,43 semanas pero el encabezado dice 398,0; ninguna regla de conteo conocida reproduce esa diferencia. El agente debe detectarlo y reportarlo al usuario como inconsistencia del documento (campo `nota_verificacion` del esquema), no ocultarlo ni "resolverlo" en silencio.
