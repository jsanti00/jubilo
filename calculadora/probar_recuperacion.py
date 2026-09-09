# Prueba del módulo de recuperación contra el set dorado.
# Uso: python3 probar_recuperacion.py   (termina en 1 si algo falla)

import json
import sys
from datetime import date
from pathlib import Path

import recuperacion

CASOS = Path(__file__).parent.parent / "casos"
FECHA = date(2026, 7, 26)

fallas = []


def revisar(condicion, descripcion):
    print(f"  {'OK  ' if condicion else 'FALLA'}  {descripcion}")
    if not condicion:
        fallas.append(descripcion)


def cargar(nombre):
    return json.loads((CASOS / nombre).read_text(encoding="utf-8"))


def pesos(n):
    if n is None:
        return "sin dato"
    return "$" + f"{n:,.0f}".replace(",", ".")


# ---------------------------------------------------------------------------
# 1. El caso real: qué es recuperable y qué no
# ---------------------------------------------------------------------------

print("=" * 70)
print("1. CASO REAL (Colpensiones RPM, hombre 59, independiente)")
print("=" * 70)

caso = cargar("caso-05-colpensiones-rpm.json")
inv = recuperacion.identificar(caso, fecha_calculo=FECHA)

print(f"\n  Filas con salario y cero semanas: {len(inv['acreditables'])}")
for a in inv["acreditables"]:
    print(f"    {a['desde']}  {a['empleador'][:22]:<22} {pesos(a['ibc']):>12}  "
          f"-> agregaría {a['semanas_que_agregaria']} semanas "
          f"({a['dias_acreditables']} días libres en el mes)")

# El hallazgo que separa este módulo de una suma a ojo: de las 3 filas, solo
# una agrega semanas. En abril y mayo el afiliado YA cotizó 30 días por su
# cuenta como independiente, así que ese mes está lleno: acreditar la fila de
# la temporal no le suma nada, era simultaneidad.
revisar(len(inv["acreditables"]) == 3, "se listan las 3 filas pendientes")
revisar(inv["semanas_acreditables"] == 4.29,
        "solo 4,29 semanas son recuperables, no las 12,86 de las 3 filas")
por_mes = {a["desde"]: a["semanas_que_agregaria"] for a in inv["acreditables"]}
revisar(por_mes["2026-03"] == 4.29, "marzo/2026 estaba vacío: sí agrega un mes")
revisar(por_mes["2026-04"] == 0.0 and por_mes["2026-05"] == 0.0,
        "abril y mayo ya estaban llenos con su aporte propio: no agregan nada")

print(f"\n  Semanas sin salario reportado (no estimables): "
      f"{inv['sin_salario_reportado']['semanas']}")
revisar(inv["sin_salario_reportado"]["semanas"] > 500,
        "los vacíos grandes se cuentan en semanas pero NO se les estima mesada")
revisar(inv["precision_de_los_dias_libres"].startswith("aproximada"),
        "se declara que el reparto de días dentro de un tramo es aproximado")

# La mora que el documento ya trae con semanas válidas YA ESTÁ CONTADA. Es la
# intuición que hay que corregir: no son semanas por ganar, son semanas en riesgo.
print(f"\n  Mora ya contada en el total impreso: {len(inv['mora_ya_contada'])} filas")
revisar(len(inv["mora_ya_contada"]) == 0 or
        all(f["semanas"] > 0 for f in inv["mora_ya_contada"]),
        "las filas de mora clasificadas como 'ya contadas' sí traen semanas")


# ---------------------------------------------------------------------------
# 2. La simulación: antes, después y la trampa del IBL
# ---------------------------------------------------------------------------

print("\n" + "=" * 70)
print("2. SIMULACIÓN: qué le pasa al número")
print("=" * 70)

sim = recuperacion.simular(caso, "M", fecha_calculo=FECHA)
base = sim["base"]
print(f"\n  Hoy: {base['semanas']} semanas | mesada {pesos(base['mesada'])} | "
      f"IBL {pesos(base['ibl'])} | pensión {base['fecha_pension']}")

revisar(base["mesada"] is not None, "el escenario base produce una mesada")

esc = sim["escenarios"].get("acreditar_lo_pendiente")
if esc:
    print(f"\n  Si le acreditan lo pendiente:")
    print(f"    semanas {esc['semanas']} ({esc['delta_semanas']:+})  |  "
          f"mesada {pesos(esc['mesada'])} ({esc['delta_mesada']:+} = "
          f"{esc['delta_mesada_pct']:+}%)")
    revisar(esc["delta_semanas"] == 4.29, "suma exactamente las 4,29 semanas")
    # EL RESULTADO CONTRAINTUITIVO, y la razón de ser de este módulo: el mes
    # recuperable se cotizó sobre $641.999, muy por debajo de su promedio de
    # $3.001.446. Entra al IBL y lo tira hacia abajo. Más semanas, menos plata.
    revisar(esc["delta_mesada"] < 0,
            "recuperar semanas de salario bajo BAJA la mesada (entra al IBL)")
    revisar("advertencia" in esc,
            "el módulo advierte el caso contraintuitivo en vez de dejarlo pasar")
    print(f"    {esc['advertencia'][:70]}...")

riesgo = sim["escenarios"].get("perder_la_mora")
if riesgo:
    print(f"\n  Si NO le convalidan la mora que ya tiene contada:")
    print(f"    semanas {riesgo['semanas']} ({riesgo['delta_semanas']:+})  |  "
          f"mesada {pesos(riesgo['mesada'])}")
    revisar(riesgo["delta_semanas"] < 0,
            "el escenario a la baja resta semanas, no las suma")


# ---------------------------------------------------------------------------
# 3. No se estima lo que no se puede estimar
# ---------------------------------------------------------------------------

print("\n" + "=" * 70)
print("3. LO QUE EL MÓDULO SE NIEGA A ESTIMAR")
print("=" * 70)

# Un caso con un vacío grande y sin ninguna fila con salario reportado: no debe
# aparecer ningún escenario al alza, porque no hay con qué calcularlo.
solo_vacios = {
    "caso_id": "sintetico-solo-vacios",
    "documento": {"regimen": "RPM"},
    "afiliado": {"fecha_nacimiento": "1970-01-01", "sexo": "M"},
    "resumen_documento": {"total_semanas": 8.57},
    "periodos": [
        {"desde": "2015-01-01", "hasta": "2015-01-31", "empleador": "A",
         "ibc": 2_000_000, "semanas_validas": 4.29, "semanas_sim": 0,
         "observacion": "normal"},
        {"desde": "2020-01-01", "hasta": "2020-01-31", "empleador": "A",
         "ibc": 2_000_000, "semanas_validas": 4.29, "semanas_sim": 0,
         "observacion": "normal"},
    ],
}
inv2 = recuperacion.identificar(solo_vacios, fecha_calculo=FECHA)
sim2 = recuperacion.simular(solo_vacios, "M", fecha_calculo=FECHA)
print(f"\n  vacío de ~5 años, sin filas con salario reportado")
print(f"    semanas no estimables: {inv2['sin_salario_reportado']['semanas']}")
print(f"    escenarios producidos: {list(sim2['escenarios'].keys()) or 'ninguno'}")
revisar(inv2["semanas_acreditables"] == 0, "no hay nada acreditable")
revisar("acreditar_lo_pendiente" not in sim2["escenarios"],
        "sin salario reportado NO se inventa un escenario al alza")
revisar(inv2["sin_salario_reportado"]["semanas"] > 200,
        "las semanas del vacío sí se cuentan y se reportan")


# ---------------------------------------------------------------------------
# 4. El resto del set dorado corre sin reventar
# ---------------------------------------------------------------------------

print("\n" + "=" * 70)
print("4. SET DORADO COMPLETO")
print("=" * 70)
print()

SEXOS = {"caso-01-porvenir-rais.json": None, "caso-02-skandia-rais.json": None,
         "caso-03-proteccion-rais.json": "M", "caso-04-colpensiones-rpm.json": "M",
         "caso-05-colpensiones-rpm.json": "M", "caso-06-colfondos-rais.json": "M"}

for archivo, sexo_forzado in SEXOS.items():
    c = cargar(archivo)
    sexo = sexo_forzado or c["afiliado"].get("sexo") or "M"
    s = recuperacion.simular(c, sexo, fecha_calculo=FECHA)
    inv_x = s["inventario"]
    print(f"  {archivo:<32} acreditables: {inv_x['semanas_acreditables']:>6} sem  "
          f"| no estimables: {inv_x['sin_salario_reportado']['semanas']:>7} sem  "
          f"| escenarios: {len(s['escenarios'])}")
    revisar(not s.get("error"), f"{archivo}: la simulación corre sin error")
    # Nunca se puede prometer más semanas de las que caben en los meses libres
    revisar(all(a["semanas_que_agregaria"] <= a["dias_acreditables"] / 7 + 0.01
                for a in inv_x["acreditables"]),
            f"{archivo}: las semanas prometidas no superan los días libres")


# ---------------------------------------------------------------------------
# La banda del factor: la palanca no se mide solo contra el borde optimista
# ---------------------------------------------------------------------------
# Por qué importa: `_correr` toma la mesada del perfil moderado, y la llave
# "mesada" sin apellido es el EXTREMO OPTIMISTA de la banda. Si la diferencia
# se calculara solo con esa, cualquier recuperación se vería más grande de lo
# que es. Aquí se fija que la banda llega y que el delta va en los dos extremos.
print("\n" + "=" * 70)
print("LA BANDA DEL FACTOR EN LOS ESCENARIOS DE RECUPERACIÓN")
print("=" * 70)

caso_rais = cargar("caso-01-porvenir-rais.json")
sim = recuperacion.simular(caso_rais, "M", edad=40, fecha_calculo=FECHA)
if sim.get("error"):
    revisar(False, f"el caso RAIS no corrió: {sim['error']}")
else:
    base = sim["base"]
    revisar(base.get("mesada_conservadora") is not None,
            "el escenario base de RAIS trae el extremo conservador de la banda")
    revisar(base.get("mesada_banda") is not None and
            base["mesada_banda"][0] <= base["mesada_banda"][1],
            "la banda del escenario base viene ordenada de menor a mayor")
    revisar("banda" in (sim.get("nota_banda") or ""),
            "la salida declara contra qué extremo se midió la diferencia")
    print(f"  base: {pesos(base['mesada_banda'][0])} a "
          f"{pesos(base['mesada_banda'][1])}")

# Ningún caso RAIS del set dorado genera hoy escenarios de recuperación (no
# traen mora ni filas con salario y cero semanas), así que el camino del delta
# se ejercita con una copia del caso-01 a la que se le marcan periodos en mora.
# Sin esto, la parte que calcula la diferencia en los dos extremos nunca se
# probaría y podría estar rota sin que ninguna prueba lo notara.
con_mora = cargar("caso-01-porvenir-rais.json")
for p in con_mora["periodos"][:6]:
    p["observacion"] = "mora"
sim_mora = recuperacion.simular(con_mora, "M", edad=40, fecha_calculo=FECHA)
escenarios_rais = {n: e for n, e in (sim_mora.get("escenarios") or {}).items()
                   if not e.get("error") and "delta_mesada" in e}
revisar(bool(escenarios_rais),
        "el caso sintético con mora sí produce escenarios de recuperación")
for nombre, e in escenarios_rais.items():
    revisar("delta_mesada_conservadora" in e,
            f"{nombre}: la diferencia también se calcula con el precio de mercado")
    revisar("base_de_comparacion" in e,
            f"{nombre}: se declara qué extremo es cada cifra")
    print(f"  {nombre}: {e['delta_mesada']:+} con el precio de la norma, "
          f"{e['delta_mesada_conservadora']:+} con el de mercado")
    # Cuando los dos extremos caen en salidas distintas, eso pesa más que
    # cualquier diferencia de monto y tiene que estar dicho
    if e.get("salidas_distintas_en_la_banda"):
        print(f"    {e['salidas_distintas_en_la_banda']}")

# En RPM no hay banda que mostrar, y la salida tiene que decirlo en vez de
# callarlo: ahí la fórmula es determinista (excepción 1 bis del system-prompt)
sim_rpm = recuperacion.simular(cargar("caso-05-colpensiones-rpm.json"), "F",
                               fecha_calculo=FECHA)
revisar("determinista" in (sim_rpm.get("nota_banda") or ""),
        "en RPM se declara que la mesada es un punto y no una banda")

# ---------------------------------------------------------------------------

print("\n" + "=" * 70)
if fallas:
    print(f"RESULTADO: {len(fallas)} FALLAS")
    for f in fallas:
        print(f"  - {f}")
    sys.exit(1)
print("RESULTADO: TODO EN VERDE")
print("=" * 70)
