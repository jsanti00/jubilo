# Prueba del router con los 5 casos del set dorado más un caso sintético
# de régimen exceptuado (Policía) para verificar la detección, y las
# comprobaciones de qué régimen liquida cuando la historia está partida.
# Termina en código de salida 1 si algo falla.
# Uso: python3 probar_router.py

import copy
import json
import sys
from pathlib import Path

from router import clasificar, regimen_vigente
import caso_sintetico_historia_partida as sintetico

CASOS = Path(__file__).parent.parent / "casos"

# (archivo, sexo simulado, edad simulada)
PRUEBAS = [
    ("caso-01-porvenir-rais.json", None, None),
    ("caso-02-skandia-rais.json", None, None),
    ("caso-03-proteccion-rais.json", "M", 26),
    ("caso-04-colpensiones-rpm.json", "F", None),
    ("caso-05-colpensiones-rpm.json", "M", None),
    # Caso 06 sin sexo ni edad a propósito: debe pedir ambos datos
    ("caso-06-colfondos-rais.json", None, None),
]

for archivo, sexo, edad in PRUEBAS:
    caso = json.loads((CASOS / archivo).read_text(encoding="utf-8"))
    r = clasificar(caso, sexo=sexo, edad=edad)
    print(f"{caso['caso_id']:<28} modulo: {r['modulo']:<5} "
          f"comparador: {str(r.get('comparador')):<28}")
    for a in r["alertas"]:
        print(f"    alerta: {a}")

# Caso sintético: un policía con años en Colpensiones (carrera mixta)
policia = {
    "caso_id": "sintetico-policia",
    "documento": {"regimen": "RPM"},
    "afiliado": {"sexo": "M", "fecha_nacimiento": "1980-01-01"},
    "resumen_documento": {"total_semanas": 400},
    "periodos": [
        {"empleador": "POLICIA NACIONAL", "observacion": "normal"},
        {"empleador": "EMPRESA PRIVADA SAS", "observacion": "mora"},
    ],
}
r = clasificar(policia)
print(f"{policia['caso_id']:<28} modulo: {r['modulo']:<5}")
for a in r["alertas"]:
    print(f"    alerta: {a}")

# ---------------------------------------------------------------------------
# Historia partida: qué régimen liquida cuando hay semanas en los dos
# ---------------------------------------------------------------------------
# La regla que se está fijando aquí: la pensión la reconoce el régimen donde la
# persona está afiliada HOY (Ley 100 art. 13 lit. b), no el documento que trae
# más semanas. En el caso sintético, Colpensiones trae 270 semanas y el fondo
# privado 180, y aun así liquida el fondo privado.
print("\nHISTORIA PARTIDA: qué régimen decide")
fallos = []
historias = sintetico.historias()

# 1. Con estado de afiliación en el documento: decisión confiable
r1 = regimen_vigente(historias)
print(f"    con estado_afiliacion       -> {r1['regimen']} "
      f"(confiable: {r1['confiable']})")
if r1["regimen"] != "RAIS" or not r1["confiable"]:
    fallos.append("Con afiliación vigente declarada, el régimen debería ser "
                  f"RAIS y confiable; dio {r1['regimen']} / {r1['confiable']}")
if not any(a.startswith("bono_pensional_no_valorado") for a in r1["alertas"]):
    fallos.append("No se declaró que el bono pensional no se valora")

# 2. Sin estado de afiliación: hipótesis, no decisión, y hay que preguntar
sin_estado = copy.deepcopy(historias)
for h in sin_estado:
    h["afiliado"]["estado_afiliacion"] = None
r2 = regimen_vigente(sin_estado)
print(f"    sin estado_afiliacion       -> {r2['regimen']} "
      f"(confiable: {r2['confiable']})")
if r2["confiable"] or not r2["pregunta"]:
    fallos.append("Sin saber dónde está afiliado hoy, la decisión no puede "
                  "marcarse como confiable y tiene que preguntar")
if r2["regimen"] != "RAIS":
    fallos.append("La hipótesis por último mes cotizado debería dar RAIS; "
                  f"dio {r2['regimen']}")

# 3. El dato del usuario manda sobre la hipótesis
r3 = regimen_vigente(sin_estado, afiliacion_actual="Colpensiones")
print(f"    usuario dice 'Colpensiones' -> {r3['regimen']} "
      f"(confiable: {r3['confiable']})")
if r3["regimen"] != "RPM" or not r3["confiable"]:
    fallos.append("Lo que dice el usuario sobre su afiliación actual debe "
                  f"mandar; dio {r3['regimen']}")
if not any(a.startswith("traslado_de_saldo_no_valorado") for a in r3["alertas"]):
    fallos.append("Volviendo a Colpensiones, no se declaró que el traslado "
                  "del saldo no se modela")

# 4. Dos documentos del mismo régimen: no hay dilema ni alerta de bono
mismo = [copy.deepcopy(historias[1]), copy.deepcopy(historias[1])]
r4 = regimen_vigente(mismo)
print(f"    dos documentos del RAIS     -> {r4['regimen']} "
      f"(confiable: {r4['confiable']})")
if r4["regimen"] != "RAIS" or not r4["confiable"]:
    fallos.append("Con dos documentos del mismo régimen la decisión es directa")
if any(a.startswith("bono_pensional") for a in r4["alertas"]):
    fallos.append("No debe hablarse de bono pensional si la carrera nunca "
                  "pasó por Colpensiones")

print()
if fallos:
    print("RESULTADO: HAY FALLOS")
    for f in fallos:
        print(f"  - {f}")
    sys.exit(1)
print("RESULTADO: TODO EN VERDE. El router está sano.")
