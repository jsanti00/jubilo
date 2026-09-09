# Prueba del comparador de regímenes: corre los 5 casos del set dorado por
# los dos módulos y muestra la comparación lado a lado.
# Uso: python3 probar_comparador.py

import json
import sys
from datetime import date
from pathlib import Path

from comparador import comparar, comparar_mesadas

CASOS = Path(__file__).parent.parent / "casos"
FECHA = date(2026, 7, 18)

# (archivo, sexo, edad si el doc no trae fecha de nacimiento)
PRUEBAS = [
    ("caso-01-porvenir-rais.json", "M", None),
    ("caso-02-skandia-rais.json", "M", None),
    ("caso-03-proteccion-rais.json", "M", 26),
    ("caso-04-colpensiones-rpm.json", "F", None),
    ("caso-05-colpensiones-rpm.json", "M", None),
]


def pesos(n):
    """Formatea pesos colombianos: 1750905 -> $1.750.905"""
    return "$" + f"{n:,.0f}".replace(",", ".") if n else "n/d"


for archivo, sexo, edad in PRUEBAS:
    caso = json.loads((CASOS / archivo).read_text(encoding="utf-8"))
    c = comparar(caso, sexo, edad=edad, fecha_calculo=FECHA)

    print("=" * 64)
    print(c["caso_id"])
    print("=" * 64)

    # Ventana de traslado
    v = c["ventana_traslado"]
    if v["abierta"]:
        print(f"Ventana de traslado ABIERTA: se cierra a los {v['edad_cierre']} "
              f"años (quedan {v['anios_restantes']} años para decidir)")
    else:
        print(f"Ventana de traslado CERRADA (desde los {v['edad_cierre']} años): "
              f"comparación solo informativa / posible vía judicial")

    # Mesada estimada en cada régimen (escenario: sigue cotizando igual)
    e_rpm = c["rpm"]["escenario_sigue_cotizando"]
    mesada_rpm = e_rpm.get("mesada") if e_rpm else None
    e_rais = c["rais"]["escenarios"].get("moderado", {})
    mesada_rais = e_rais.get("mesada")

    marca = " (saldo SIMULADO desde su historia salarial)" \
        if c["saldo_rais_simulado"] else ""
    # El RAIS va en banda: mostrar solo `mesada` sería mostrar el extremo
    # optimista, que es exactamente lo que la banda vino a evitar
    banda = e_rais.get("mesada_banda") or (mesada_rais, mesada_rais)
    print(f"\nMesada estimada si sigue cotizando igual (pesos de hoy):")
    print(f"  En RPM (Colpensiones):     {pesos(mesada_rpm)} (punto, fórmula determinista)")
    print(f"  En RAIS (perfil moderado): {pesos(banda[0])} a {pesos(banda[1])}{marca}")
    if e_rais.get("salida"):
        print(f"  Salida RAIS: {e_rais['salida']} (con precio de mercado: "
              f"{e_rais.get('salida_conservadora')})")
    print(f"  Veredicto: {c['mesadas']['veredicto']}")
    print()


# ---------------------------------------------------------------------------
# Regresión: el veredicto se evalúa en los DOS extremos de la banda
# ---------------------------------------------------------------------------
# Por qué son diagnósticos armados a mano y no casos del set dorado: el
# veredicto de un caso real depende de las cifras de rendimiento y del factor,
# que se están recalibrando. Lo que aquí se fija es la REGLA, que no debe
# cambiar aunque cambien las cifras: si el ganador depende del extremo, no hay
# veredicto. Con casos reales esta prueba se rompería cada recalibración.
print("=" * 64)
print("REGRESIÓN: el veredicto del traslado se evalúa en los dos extremos")

fallos = []


def _diags(mesada_rpm, conservadora, optimista):
    """Arma el par de diagnósticos mínimos que lee `comparar_mesadas`."""
    return ({"escenario_sigue_cotizando": {"mesada": mesada_rpm}},
            {"escenarios": {"moderado": {
                "mesada": optimista,
                "mesada_conservadora": conservadora,
                "mesada_banda": (conservadora, optimista)}}})


ESCENARIOS = [
    # (nombre, mesada RPM, extremo conservador RAIS, extremo optimista RAIS, veredicto)
    ("el fondo gana en los dos extremos", 1000000, 1200000, 2000000,
     "rais_arriba_en_los_dos_extremos"),
    ("Colpensiones gana en los dos extremos", 3000000, 1200000, 2000000,
     "rpm_arriba_en_los_dos_extremos"),
    # El caso que obliga a existir a esta prueba: con el precio de la norma
    # gana el fondo y con el de mercado gana Colpensiones
    ("el ganador cambia según el extremo", 1500000, 1200000, 2000000,
     "se_voltea_dentro_de_la_banda"),
]

for nombre, m_rpm, conservadora, optimista, esperado in ESCENARIOS:
    d_rpm, d_rais = _diags(m_rpm, conservadora, optimista)
    r = comparar_mesadas(d_rpm, d_rais)
    marca = "OK" if r["veredicto"] == esperado else "FALLA"
    print(f"  {marca}: {nombre} -> {r['veredicto']}")
    if r["veredicto"] != esperado:
        fallos.append(f"{nombre}: se esperaba {esperado} y dio {r['veredicto']}")

# Cuando se voltea, el mensaje tiene que decir que NO hay ganador, no elegir uno
d_rpm, d_rais = _diags(1500000, 1200000, 2000000)
mensaje = comparar_mesadas(d_rpm, d_rais)["mensaje"]
if "NO tiene ganador" not in mensaje:
    fallos.append("Cuando el veredicto se voltea, el mensaje no lo dice claro")
else:
    print("  OK: el mensaje dice que la comparación no tiene ganador")

# Sin una de las dos mesadas no se inventa un veredicto
sin_rpm = comparar_mesadas({"escenario_sigue_cotizando": {}}, _diags(0, 1, 2)[1])
if sin_rpm["veredicto"] != "sin_comparacion":
    fallos.append("Sin mesada de RPM se entregó un veredicto igual")
else:
    print("  OK: sin una de las dos mesadas no hay veredicto")

print()
if fallos:
    print("RESULTADO: HAY FALLOS")
    for f in fallos:
        print(f"  - {f}")
    sys.exit(1)
print("RESULTADO: TODO EN VERDE. El comparador lee la banda completa.")
