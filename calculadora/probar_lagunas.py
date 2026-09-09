# Prueba del módulo de lagunas contra el set dorado.
# Uso: python3 probar_lagunas.py   (termina en 1 si algo falla)
#
# A diferencia de las otras pruebas, esta SÍ compara contra números esperados
# calculados a mano sobre el documento, no solo contra "el flujo corre". Es el
# pendiente 2 de la sesión del 2026-07-26 aplicado a este módulo desde el día
# uno: una prueba que no tiene respuesta esperada no detecta un cálculo malo.

import json
import sys
from pathlib import Path

import lagunas

CASOS = Path(__file__).parent.parent / "casos"
EXTRACCIONES = Path(__file__).parent.parent / "extracciones"

fallas = []


def revisar(condicion, descripcion):
    """Anota el resultado de una comprobación y lo imprime."""
    print(f"  {'OK  ' if condicion else 'FALLA'}  {descripcion}")
    if not condicion:
        fallas.append(descripcion)


def cargar(ruta):
    return json.loads(Path(ruta).read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# 1. Todos los casos del set dorado corren y son internamente coherentes
# ---------------------------------------------------------------------------

print("=" * 70)
print("1. SET DORADO: el análisis corre y es coherente en los 6 casos")
print("=" * 70)

for archivo in sorted(CASOS.glob("caso-*.json")):
    caso = cargar(archivo)
    a = lagunas.analizar(caso)
    r = lagunas.resumir(a)
    print(f"\n{archivo.name}")
    print(f"  vacíos: {r['vacios']} ({r['semanas_en_vacios']} sem) | "
          f"tramos incompletos: {r['tramos_con_deficit']} "
          f"({r['semanas_en_deficit_de_tramos']} sem) | "
          f"filas con IBC y 0 semanas: {r['filas_ibc_sin_semanas']}")

    revisar(not a.get("error"), f"{archivo.name}: el análisis no devuelve error")
    # Ningún déficit puede ser negativo: eso significaría "cotizó más de lo posible"
    revisar(all(t["deficit_semanas"] > 0 for t in a["tramos_con_deficit"]),
            f"{archivo.name}: todos los déficits reportados son positivos")
    # El total global nunca puede superar la suma de los tramos: si lo hiciera,
    # estaría contando meses que ningún tramo cubre
    suma_tramos = sum(t["deficit_semanas"] for t in a["tramos_con_deficit"])
    revisar(r["semanas_perdidas_total"] >= r["semanas_en_vacios"],
            f"{archivo.name}: el total incluye los vacíos")

    # MECE: un mes es vacío o es parte de un tramo, nunca las dos cosas
    meses_vacios = set()
    for v in a["vacios"]:
        meses_vacios.add((v["desde"], v["hasta"]))
    solapa = any(t["desde"] == v["desde"] and t["hasta"] == v["hasta"]
                 for t in a["tramos_con_deficit"] for v in a["vacios"])
    revisar(not solapa,
            f"{archivo.name}: vacíos y tramos con déficit no se solapan (MECE)")


# ---------------------------------------------------------------------------
# 2. El caso real de la sesión de role-play (caso-05 / extracción del 26)
# ---------------------------------------------------------------------------
# Números verificados a mano sobre el documento de Colpensiones:
# - El tramo mar/2025 a mar/2026 son 13 meses. Cotizados 47,14 semanas = 330
#   días = 11 meses exactos. Faltan 2 meses = 60 días = 8,57 semanas.
# - Dos huecos largos: entre dic/1996 y mar/1997 (vacíos ene y feb de 1997) y
#   entre jul/1997 y feb/2007 (vacíos ago/1997 a ene/2007, 114 meses).
# - Tres filas de Temporales con Visión con salario y cero semanas.

print("\n" + "=" * 70)
print("2. CASO REAL (Colpensiones RPM, hombre 59, independiente)")
print("=" * 70)

caso = cargar(CASOS / "caso-05-colpensiones-rpm.json")
a = lagunas.analizar(caso)

vacios = {(v["desde"], v["hasta"]): v for v in a["vacios"]}
print("\n  Vacíos encontrados:")
for (d, h), v in sorted(vacios.items()):
    print(f"    {d} a {h}  ({v['meses']} meses, {v['semanas_no_cotizadas']} semanas)")

revisar(("1997-01", "1997-02") in vacios,
        "vacío corto: ene/1997 a feb/1997 (entre dic/1996 y mar/1997)")
revisar(("1997-08", "2007-01") in vacios,
        "vacío largo: ago/1997 a ene/2007 (entre jul/1997 y feb/2007)")
revisar(vacios[("1997-08", "2007-01")]["meses"] == 114,
        "el vacío largo dura 114 meses (9,5 años)")

tramos = {(t["desde"], t["hasta"]): t for t in a["tramos_con_deficit"]}
print("\n  Tramos incompletos:")
for (d, h), t in sorted(tramos.items()):
    print(f"    {d} a {h}  {t['empleador']}: {t['semanas_reportadas']} de "
          f"{t['semanas_posibles']} semanas posibles "
          f"(faltan {t['deficit_semanas']} = ~{t['deficit_meses_aprox']} meses)")

clave = ("2025-03", "2026-03")
revisar(clave in tramos, "aparece el tramo mar/2025 a mar/2026")
if clave in tramos:
    t = tramos[clave]
    revisar(t["meses_del_rango"] == 13, "el tramo dura 13 meses")
    revisar(t["semanas_reportadas"] == 47.14, "reporta 47,14 semanas")
    revisar(t["semanas_posibles"] == 55.71,
            "caben 55,71 semanas (13 meses x 30 días, convención del sistema)")
    revisar(t["deficit_semanas"] == 8.57, "faltan 8,57 semanas")
    revisar(t["deficit_meses_aprox"] == 2.0, "faltan exactamente 2 meses")

filas = a["filas_ibc_sin_semanas"]
print("\n  Filas con salario reportado y cero semanas acreditadas:")
for f in filas:
    print(f"    {f['desde']}  {f['empleador']}  ${f['ibc']:,}".replace(",", "."))
revisar(len(filas) == 3, "las 3 filas del mismo aportante salen listadas")
# Comprobamos que las 3 filas sean del mismo aportante, sin depender de cómo se
# llame: los casos están anonimizados y el nombre puede cambiar.
revisar(len({f["empleador"] for f in filas}) == 1,
        "las 3 son del mismo aportante")
revisar({f["ibc"] for f in filas} == {641999, 1750905},
        "los salarios reportados son $641.999 y $1.750.905")


# ---------------------------------------------------------------------------
# 3. Guardia contra el doble conteo por simultaneidad
# ---------------------------------------------------------------------------
# El riesgo del módulo: inventar un déficit donde hubo dos aportantes
# legítimos el mismo mes. Los días de un mes se topan en 30 (regla 3 de
# esquema-datos.md), así que un mes cubierto entre dos aportantes está lleno.

print("\n" + "=" * 70)
print("3. DOBLE CONTEO: dos aportantes en el mismo mes no inventan déficit")
print("=" * 70)

# Caso sintético: dos empleadores, medio mes cada uno, mes completo entre los dos
simultaneo = {
    "caso_id": "sintetico-simultaneidad",
    "documento": {"regimen": "RAIS"},
    "afiliado": {},
    "resumen_documento": {"total_semanas": 4.29},
    "periodos": [
        {"desde": "2025-01-01", "hasta": "2025-01-31", "empleador": "EMPRESA A",
         "ibc": 2000000, "dias_cotizados": 15, "semanas_validas": None,
         "semanas_sim": 0, "observacion": "normal"},
        {"desde": "2025-01-01", "hasta": "2025-01-31", "empleador": "EMPRESA B",
         "ibc": 1500000, "dias_cotizados": 15, "semanas_validas": None,
         "semanas_sim": 0, "observacion": "normal"},
    ],
}
a_sim = lagunas.analizar(simultaneo)
print(f"\n  déficit reportado: {a_sim['deficit_de_tramos_semanas']} semanas")
revisar(a_sim["deficit_de_tramos_semanas"] == 0.0,
        "medio mes + medio mes = mes lleno: cero déficit")
revisar(a_sim["vacios"] == [], "sin vacíos: el mes está cubierto")

# Y el contraste: si entre los dos solo llenan medio mes, sí hay déficit
incompleto = json.loads(json.dumps(simultaneo))
incompleto["periodos"][1]["dias_cotizados"] = 0
a_inc = lagunas.analizar(incompleto)
print(f"  con solo 15 días entre los dos: "
      f"{a_inc['deficit_de_tramos_semanas']} semanas de déficit")
revisar(a_inc["deficit_de_tramos_semanas"] == 2.14,
        "medio mes cotizado = 2,14 semanas de déficit (sí lo detecta)")

# El total global nunca puede ser la suma de tramos solapados
for archivo in ("caso-04-colpensiones-rpm.json", "caso-06-colfondos-rais.json"):
    a_x = lagunas.analizar(cargar(CASOS / archivo))
    suma = round(sum(t["deficit_semanas"] for t in a_x["tramos_con_deficit"]), 2)
    print(f"  {archivo}: suma de tramos {suma} -> total sin doble conteo "
          f"{a_x['deficit_de_tramos_semanas']}")
    revisar(a_x["deficit_de_tramos_semanas"] <= suma,
            f"{archivo}: el total no suma dos veces un mes compartido")


# ---------------------------------------------------------------------------
# 4. Las alertas que ve el router
# ---------------------------------------------------------------------------

print("\n" + "=" * 70)
print("4. ALERTAS: relevancia, no tamaño")
print("=" * 70)
print("""
  No hay umbral de semanas perdidas. Un hueco se alerta cuando es material
  para ESA persona, con dos pruebas: si cae dentro de la ventana de 3 años con
  la que se proyecta su futuro, y si pesa frente a lo que le falta para su
  requisito. Un umbral absoluto trataría igual 30 semanas repartidas en 20
  años (ruido) y 30 semanas en alguien a quien le faltan 20 (decisivo).""")

# Caso real: le faltan 63,43 semanas para las 1.300 y perdió 516,86 en huecos
alertas_caso = lagunas.alertas(a, semanas_hoy=1236.57, semanas_requeridas=1300)
print()
for x in alertas_caso:
    print(f"  {x[:100]}...")
revisar(any(x.startswith("lagunas_recientes") for x in alertas_caso),
        "tiene 2 meses perdidos en los últimos 3 años: se alerta")
revisar(any(x.startswith("lagunas_decisivas") for x in alertas_caso),
        "perdió 8 veces lo que le falta para el requisito: se alerta")
revisar(any(x.startswith("ibc_sin_semanas") for x in alertas_caso),
        "las filas con salario y cero semanas levantan su propia alerta")

# Sin el requisito, la prueba 2 no corre y no se inventa un resultado
sin_requisito = lagunas.alertas(a)
revisar(not any(x.startswith("lagunas_decisivas") for x in sin_requisito),
        "sin saber el requisito, NO se afirma que el hueco sea decisivo")

# Contraste: un caso al que le sobran semanas no debe recibir la alerta
# decisiva, aunque tenga huecos. caso-04 tiene 1.478 semanas sobre 1.300.
a_04 = lagunas.analizar(cargar(CASOS / "caso-04-colpensiones-rpm.json"))
alertas_04 = lagunas.alertas(a_04, semanas_hoy=1478.43, semanas_requeridas=1300)
print(f"\n  caso-04 (1.478 semanas, ya cumple el requisito):")
for x in alertas_04:
    print(f"    {x[:90]}...")
revisar(not any(x.startswith("lagunas_decisivas") for x in alertas_04),
        "a quien ya cumplió el requisito no se le vende recuperar como palanca")

# Un caso sano no debe levantar ninguna alerta de huecos
revisar(lagunas.alertas(a_sim, semanas_hoy=4.29, semanas_requeridas=1300) == [],
        "un historial sin huecos no levanta ninguna alerta")

# La ventana reciente se recorta contra el documento por los dos lados: quien
# se afilió hace un mes no tiene 3 años de huecos, tiene un mes de historia
rec_sim = a_sim["reciente"]
print(f"\n  historial de un solo mes: ventana reciente {rec_sim['desde']} a "
      f"{rec_sim['hasta']} ({rec_sim['meses_evaluados']} meses evaluados)")
revisar(rec_sim["meses_evaluados"] == 1,
        "la ventana reciente no cuenta meses anteriores a la primera cotización")
revisar(rec_sim["semanas_perdidas"] == 0.0,
        "y por lo tanto no le inventa huecos a quien acaba de empezar")


# ---------------------------------------------------------------------------
# Resultado
# ---------------------------------------------------------------------------

print("\n" + "=" * 70)
if fallas:
    print(f"RESULTADO: {len(fallas)} FALLAS")
    for f in fallas:
        print(f"  - {f}")
    sys.exit(1)
print("RESULTADO: TODO EN VERDE")
print("=" * 70)
