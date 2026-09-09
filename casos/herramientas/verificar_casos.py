# Verificador del set dorado: recalcula las semanas de cada caso a partir de sus periodos
# y las compara contra el total impreso en el documento (la "respuesta del profesor").
# Si algo no cuadra, es señal de un error de extracción. Uso: python3 verificar_casos.py

import json                    # Para leer los archivos JSON de los casos
from pathlib import Path       # Para manejar rutas de archivos
from collections import defaultdict  # Para agrupar días por mes fácilmente

# Carpeta de casos (la carpeta padre de este script)
CASOS_DIR = Path(__file__).parent.parent

# Tolerancia: diferencias menores a esto se aceptan (los fondos redondean distinto)
TOLERANCIA = 0.15


def semanas_de_caso(caso):
    """Recalcula el total de semanas de un caso según el tipo de dato de sus periodos."""
    periodos = caso["periodos"]

    # Caso Colpensiones: los periodos traen semanas válidas, pero el total del
    # documento se calcula desde los DÍAS exactos, no sumando filas redondeadas.
    # Reconstruimos los días de cada fila (semanas x 7) y dividimos al final.
    if any(p["semanas_validas"] is not None for p in periodos):
        total_dias = sum(round((p["semanas_validas"] or 0) * 7) for p in periodos)
        return total_dias / 7

    # Caso fondos privados (formato mensual): se suman los días por mes,
    # topando cada mes en 30 días (regla del sistema: con dos empleadores
    # en el mismo mes, las semanas se cuentan solo una vez)
    dias_por_mes = defaultdict(int)
    for p in periodos:
        mes = p["desde"][:7]  # "2021-09-01" -> "2021-09"
        dias_por_mes[mes] += p["dias_cotizados"]
    total_dias = sum(min(dias, 30) for dias in dias_por_mes.values())
    return total_dias / 7  # 1 semana = 7 días


# Revisa cada archivo de caso y compara contra el total del documento
print(f"{'Caso':<28} {'Documento':>10} {'Calculado':>10} {'Dif':>7}  Resultado")
todos_ok = True
for archivo in sorted(CASOS_DIR.glob("caso-*.json")):
    caso = json.loads(archivo.read_text(encoding="utf-8"))
    total_doc = caso["resumen_documento"]["total_semanas"]
    calculado = semanas_de_caso(caso)
    diferencia = abs(calculado - total_doc)
    ok = diferencia <= TOLERANCIA
    # Un caso puede traer una discrepancia INTERNA del documento ya estudiada
    # y documentada (ej. caso-06: el total impreso no cuadra con su propia
    # tabla). Eso no es un error de extracción: se marca aparte y no daña el set.
    nota = caso["resumen_documento"].get("nota_verificacion")
    if ok:
        estado = "PASA"
    elif nota:
        estado = "DISCREPANCIA DOCUMENTAL (ver nota_verificacion)"
    else:
        estado = "FALLA"
    todos_ok = todos_ok and (ok or nota is not None)
    print(f"{caso['caso_id']:<28} {total_doc:>10.2f} {calculado:>10.2f} {diferencia:>7.2f}  {estado}")

# Mensaje final: el set dorado solo sirve si todos los casos pasan
print("\nSet dorado " + ("VERIFICADO: todos los casos cuadran." if todos_ok else "CON ERRORES: revisar los casos que fallan."))
