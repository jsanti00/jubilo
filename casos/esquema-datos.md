# Esquema de datos de historia laboral (V0)

> **Última actualización:** 2026-07-13. Validado con Santiago.
> **Qué es:** el "formulario estándar" que la IA llena al leer cualquier historia laboral. Es el único formato que la calculadora acepta como entrada, sin importar de qué fondo venga el documento.

## Flujo (pipeline)

```
PDF del usuario → extracción de texto (pdftotext) → si no hay texto: lectura visual del PDF → JSON con este esquema → verificación automática → calculadora
```

**Regla de producción:** el insumo oficial es el **PDF** (así llegan por Telegram y WhatsApp). Los `.md` de la carpeta de ejemplos son solo material de laboratorio. La lectura visual es obligatoria como respaldo: hay PDFs sin capa de texto (ej. los re-guardados tras quitarles la contraseña).

## Estructura

```json
{
  "caso_id": "caso-05-colpensiones-rpm",

  "documento": {
    "administradora_emisora": "Colpensiones",   // quién emite el reporte
    "regimen": "RPM",                            // RPM o RAIS
    "formato": "colpensiones_reporte_semanas",   // plantilla detectada
    "fecha_generacion": "2026-07-13"             // fecha del reporte (null si no aparece)
  },

  "afiliado": {
    "fecha_nacimiento": "1967-05-11",   // null si el documento no la trae
    "edad_en_documento": null,          // algunos formatos solo traen la edad (ej. Protección)
    "sexo": null,                       // solo si el documento lo dice; NUNCA se infiere del nombre
    "fecha_afiliacion": "1992-05-12",
    "estado_afiliacion": "activo_cotizante"
  },

  "resumen_documento": {
    // Los totales TAL CUAL los imprime el documento. Es la "respuesta del profesor"
    // contra la que se verifica la extracción periodo a periodo.
    "total_semanas": 1236.57,
    "total_dias": null,
    "saldo_cuenta_individual": null,     // solo RAIS
    "semanas_en_otros_fondos": null      // ej. reporte de Protección que suma semanas de Porvenir
  },

  "periodos": [
    {
      "desde": "2018-03-01",             // inicio del periodo
      "hasta": "2018-07-31",             // fin del periodo
      "empleador": "EMPLEADOR-08",
      "nit": "91252815",
      "tipo_cotizante": "independiente", // empleado | independiente | null si no se puede saber
      "ibc": 1200000,                    // salario base de cotización
      "ibc_tipo": "ultimo_del_rango",    // mensual | ultimo_del_rango (Colpensiones resume rangos)
      "cotizacion": null,                // aporte pagado, si el documento lo trae
      "dias_cotizados": 150,             // lo que reporte el documento: días...
      "semanas": null,                   // ...o semanas (al menos uno de los dos)
      "semanas_lic": null,               // semanas en licencia (Colpensiones)
      "semanas_sim": null,               // semanas simultáneas (Colpensiones)
      "semanas_validas": null,           // total válido del rango (Colpensiones, columna [9])
      "administradora": "Colpensiones",  // dónde quedó ese aporte (puede diferir de la emisora)
      "observacion": "normal"            // normal | mora | en_verificacion | simultaneo | licencia | deuda_presunta
    }
  ]
}
```

## Reglas de normalización

1. **Formatos mensuales (Porvenir, Protección, Skandia):** cada fila del documento es un periodo con `desde` = primer día del mes y `hasta` = último día del mes. Puede haber varias filas del mismo mes (pagos partidos o dos empleadores): se conservan todas tal cual.
2. **Formato Colpensiones (resumen por empleador):** cada fila es un rango `desde/hasta` con semanas. El salario es el **último** del rango (`ibc_tipo: "ultimo_del_rango"`).
3. **Semanas contadas una sola vez:** si hay dos empleadores en el mismo mes, los días del mes se topan en 30 para el conteo de semanas (regla del sistema, verificada con caso real: 265,71 semanas de un reporte con un mes simultáneo).
4. **Lo extraído y lo calculado van separados:** la IA solo llena lo que el documento dice. Lagunas, semanas recalculadas y alertas las genera el código, comparando contra `resumen_documento`. Las semanas recalculadas y las alertas salen de `calculadora/diagnosticar.py` y `calculadora/router.py`; **las lagunas, de `calculadora/lagunas.py`** (existe desde el 2026-07-26; antes esta regla prometía algo que ningún módulo hacía).
5. **Nada se infiere:** si el documento no trae sexo o fecha de nacimiento, el campo queda `null` y se convierte en pregunta adaptativa al usuario (momento 3 de la experiencia).
6. **Regla del día exacto (Colpensiones):** el total impreso se calcula desde los días exactos, no sumando las filas redondeadas a 2 decimales. Sumar filas sobreestima (verificado: +0,70 semanas en un caso de 293 filas). Todo conteo debe reconstruir días (`semanas × 7`) y dividir al final.

## Anonimización (set dorado)

Los JSON del set dorado **no llevan** nombre, cédula, correo ni dirección. Solo fecha de nacimiento (o edad) y sexo, que la calculadora necesita. El mapeo caso ↔ persona vive únicamente en el `README.md` de esta carpeta, que es privado.

## Campo opcional: `resumen_documento.nota_verificacion`

Cuando el documento **no cuadra consigo mismo** (caso-06: la tabla suma más semanas que el total impreso) y la diferencia ya se estudió sin encontrar regla que la explique, se documenta en este campo. El verificador lo trata como discrepancia documental (no como error de extracción) y el agente debe reportarla al usuario.

## Pendientes

- ~~Ejemplo de **Colfondos**~~ Listo: caso-06 (con discrepancia documental anotada).
- `tipo_cotizante` en formatos Colpensiones: se marca `independiente` cuando el NIT del aportante es la cédula del propio afiliado; en los demás casos queda `empleado`.
- Definir cómo se detecta el formato (`documento.formato`) automáticamente: se resolverá al construir el system prompt de extracción.
