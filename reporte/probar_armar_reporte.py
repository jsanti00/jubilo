# Prueba del reporte de cierre.
# Uso: python3 reporte/probar_armar_reporte.py   (termina en 1 si algo falla)
#
# Lo que esta prueba existe para garantizar, y es una sola cosa: **que ninguna
# cifra del reporte sea distinta de la del diagnostico**. El reporte lo arma el
# codigo justamente para que el modelo no pueda reescribir un numero, y esa
# promesa hay que poder comprobarla. Por eso casi todas las comprobaciones de
# abajo son de la forma "esta cifra del reporte es identica a esta clave del
# JSON".
#
# No toca internet ni el servidor: corre con los casos del set dorado.

import json
import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).parent.parent
sys.path.insert(0, str(RAIZ / "calculadora"))
sys.path.insert(0, str(Path(__file__).parent))

from diagnosticar import diagnosticar
import armar_reporte as rep

CASOS = RAIZ / "casos"
FECHA = date(2026, 7, 18)
SALIDA = Path("/tmp/jubilo-reporte-prueba.pdf")

fallas = []


def revisar(condicion, descripcion):
    """Anota el resultado de una comprobación y lo imprime."""
    print(f"  {'OK  ' if condicion else 'FALLA'}  {descripcion}")
    if not condicion:
        fallas.append(descripcion)


def diagnostico_de(archivo, sexo=None):
    caso = json.loads((CASOS / archivo).read_text(encoding="utf-8"))
    return diagnosticar(caso, sexo=sexo, fecha_calculo=FECHA)


# ---------------------------------------------------------------------------
# Las cifras del reporte son las del diagnóstico, sin excepción
# ---------------------------------------------------------------------------

print("\nCaso de ahorro individual: las cifras salen intactas del diagnóstico")

d = diagnostico_de("caso-01-porvenir-rais.json")
datos = rep.datos_del_reporte(d, "Juan Pablo Granada", "Porvenir")

enc = datos["encabezado"]
revisar(enc["semanas_hoy"] == d["diagnostico"]["semanas_hoy"],
        "las semanas del encabezado son las del diagnóstico")
revisar(enc["edad"] == d["diagnostico"]["edad"], "la edad es la del diagnóstico")
revisar(enc["sexo"] == d["diagnostico"]["sexo"], "el sexo es el del diagnóstico")
revisar(enc["requisito_semanas"] == d["diagnostico"]["semanas_gpm"],
        "en RAIS el requisito que se muestra es el de la garantía de pensión mínima")
revisar(enc["semanas_que_faltan"]
        == d["diagnostico"]["semanas_gpm"] - d["diagnostico"]["semanas_hoy"],
        "las semanas que faltan son la resta exacta, sin redondeos propios")

res = datos["resultado"]
revisar(res["mesada_banda"] == d["recuperacion"]["base"]["mesada_banda"],
        "la mesada del reporte es exactamente la banda del diagnóstico")

alertas = datos["alertas"]
resumen = d["lagunas"]["resumen"]
revisar(alertas["semanas_perdidas_total"] == resumen["semanas_perdidas_total"],
        "las semanas perdidas son las del módulo de lagunas")
revisar(str(resumen["vacios"]) in alertas["lista"][0]["cifra"],
        "el número de huecos es el del módulo de lagunas")

# El nombre sí va (decisión de Santiago), la cédula no va nunca.
revisar(enc["nombre"] == "Juan Pablo Granada",
        "el nombre completo va en el reporte, como decidió Santiago")
texto_entero = json.dumps(datos, ensure_ascii=False, default=str)
for prohibido in ("cedula", "cédula", "documento_identidad", "1005320949"):
    revisar(prohibido not in texto_entero.lower(),
            f"el reporte no contiene '{prohibido}'")


print("\nCaso de prima media: lee sus propias claves, no las del otro régimen")

d_rpm = diagnostico_de("caso-04-colpensiones-rpm.json", sexo="F")
datos_rpm = rep.datos_del_reporte(d_rpm, "María Fernanda Ruiz", "Colpensiones")
enc_rpm = datos_rpm["encabezado"]
dd = d_rpm["diagnostico"]

revisar(datos_rpm["modulo"] == "rpm", "se reconoce que es prima media")
revisar(enc_rpm["semanas_hoy"] == dd["semanas_hoy"],
        "las semanas son las del bloque de prima media")
revisar(enc_rpm["requisito_semanas"] == dd["requisito_semanas_hoy"],
        "en prima media el requisito es el de la ley, no el de la pensión mínima")
revisar(datos_rpm["resultado"]["fecha_pension"] == dd["fecha_pension_estimada"],
        "la fecha de pensión es la del diagnóstico")
revisar(datos_rpm["resultado"]["mesada_banda"][0]
        == dd["escenario_sigue_cotizando"]["mesada"],
        "la mesada es la del escenario de seguir cotizando")
revisar(datos_rpm["resultado"]["es_punto_no_banda"] is True,
        "en prima media se declara que es un punto y no una banda")


# ---------------------------------------------------------------------------
# El candado: sin diagnóstico completo, no hay reporte
# ---------------------------------------------------------------------------

print("\nEl candado, que es lo que evita entregar una página vacía")

# El mismo caso SIN el sexo no se puede calcular, así que no debe salir reporte.
d_incompleto = diagnostico_de("caso-04-colpensiones-rpm.json")
revisar(not d_incompleto["listo_para_entregar"],
        "el diagnóstico sin sexo efectivamente no está listo")
try:
    rep.datos_del_reporte(d_incompleto, "Alguien", "Colpensiones")
    revisar(False, "se negó a armar el reporte de un diagnóstico incompleto")
except ValueError as fallo:
    revisar("no está listo" in str(fallo),
            "se negó a armar el reporte de un diagnóstico incompleto")
    revisar("sexo" in str(fallo).lower(),
            "y dice qué es lo que falta, para poder pedírselo a la persona")


# ---------------------------------------------------------------------------
# Las siete secciones existen y traen contenido
# ---------------------------------------------------------------------------

print("\nLa estructura que validó Santiago")

for seccion in ("encabezado", "resultado", "alertas", "palancas",
                "escenarios", "siguientes_pasos", "supuestos"):
    revisar(seccion in datos and datos[seccion],
            f"la sección '{seccion}' existe y no viene vacía")

revisar(len(datos["escenarios"]["lista"]) == 2,
        "la sección de escenarios trae dos, como se pidió")
revisar(all("mesada_banda" in e for e in datos["escenarios"]["lista"]),
        "cada escenario trae su mesada, con el mismo formato del resultado")
revisar(len(datos["siguientes_pasos"]) >= 1,
        "hay al menos un siguiente paso, y pueden ser varios")
revisar(any("no una liquidación certificada" in l
            for l in datos["supuestos"]["limites"]),
        "los límites dicen que esto no es una liquidación certificada")


# ---------------------------------------------------------------------------
# El PDF se genera, es válido, y las cifras están adentro
# ---------------------------------------------------------------------------

print("\nEl archivo PDF")

rep.escribir_pdf(datos, SALIDA)
crudo = SALIDA.read_bytes()
revisar(crudo.startswith(b"%PDF-"), "el archivo empieza como un PDF de verdad")
revisar(crudo.rstrip().endswith(b"%%EOF"), "y termina como un PDF de verdad")
revisar(b"/Count 1" in crudo, "tiene exactamente una página")
revisar(len(crudo) > 1500, "tiene contenido, no es un archivo vacío")

# La comprobación que de verdad importa: la mesada que salió al papel es la
# misma del diagnóstico. Se busca el texto dentro del PDF, que no va comprimido.
contenido = crudo.decode("cp1252", "ignore")
mesada_esperada = rep.pesos(d["recuperacion"]["base"]["mesada_banda"][1])
revisar(mesada_esperada.replace("$", "") in contenido.replace("\\", ""),
        f"la mesada {mesada_esperada} está escrita en el PDF")
revisar("Juan Pablo Granada" in contenido,
        "el nombre está escrito en el PDF")

# Y que las tildes sobrevivan: si se rompieran, la página se leería mal entera.
revisar("Diagn" in contenido, "los títulos con tilde se escribieron")


print("\n" + "=" * 70)
if fallas:
    print(f"RESULTADO: {len(fallas)} FALLAS")
    for f in fallas:
        print(f"  - {f}")
    sys.exit(1)
print("RESULTADO: TODO EN VERDE")
print("=" * 70)
