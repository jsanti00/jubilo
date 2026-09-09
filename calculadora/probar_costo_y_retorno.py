# Prueba del módulo de costo y retorno.
# Uso: python3 probar_costo_y_retorno.py   (termina en 1 si algo falla)
#
# La prueba central es el CASO REAL corrido a mano el 2026-07-27, con sus seis
# cifras esperadas. Es una prueba con números calculados a mano, no una que
# solo verifica que el flujo corre: eso último no detecta un cálculo malo.

import sys

import costo_y_retorno as cr
from datos_sistema import SMLMV

SMLMV_2026 = SMLMV[2026]   # $1.750.905

fallas = []


def revisar(condicion, descripcion):
    print(f"  {'OK  ' if condicion else 'FALLA'}  {descripcion}")
    if not condicion:
        fallas.append(descripcion)


def cerca(obtenido, esperado, tolerancia, descripcion):
    """Compara con tolerancia explícita y muestra la diferencia si falla."""
    ok = obtenido is not None and abs(obtenido - esperado) <= tolerancia
    detalle = f"{descripcion}: esperado {esperado}, obtenido {obtenido}"
    revisar(ok, detalle)


# ---------------------------------------------------------------------------
# 1. CASO REAL DE VALIDACIÓN (corrido a mano, 2026-07-27)
#    IBC 7.600.000, 34 meses de aporte, mesada bruta 2.722.674
# ---------------------------------------------------------------------------

print("=" * 78)
print("1. CASO REAL DE VALIDACIÓN (cifras calculadas a mano el 2026-07-27)")
print("=" * 78)
print()

IBC = 7_600_000
MESES = 34
MESADA_BRUTA = 2_722_674
HORIZONTE = 21

fila = cr.evaluar_escenario("cotizar sobre 7.600.000", IBC, MESES, MESADA_BRUTA,
                            horizonte_anios=HORIZONTE, smlmv=SMLMV_2026,
                            es_base=True)

# Tolerancia de 1 peso: el módulo redondea al presentar, el cálculo a mano
# también. Nada aquí depende de decimales de peso.
cerca(fila["aporte_mensual"], 2_242_000, 1, "aporte mensual")
cerca(fila["costo_total"], 76_228_000, 1, "costo total (34 meses)")
cerca(fila["mesada_neta"], 2_450_407, 1, "mesada neta")
# El breakeven se compara con tolerancia de 0,05 meses porque se reporta con
# un decimal: 28,7 meses son unos 36 días de margen, irrelevante para decidir.
cerca(fila["breakeven_meses"], 28.7, 0.05, "breakeven en meses")
# La ganancia a 21 años sí se compara al peso: es la cifra más grande y la que
# más se propaga si hay un error de redondeo intermedio.
cerca(fila["ganancia_neta_horizonte"], 592_733_002, 1,
      "ganancia neta a 21 años")

print()
print("  Desglose del aporte mensual:")
d = fila["aporte_desglose"]
print(f"    Pensión 16%          {cr.pesos(d['pension_16_pct'])}")
print(f"    Fondo Solidaridad    {cr.pesos(d['fsp_solidaridad'])}")
print(f"    Fondo Subsistencia   {cr.pesos(d['fsp_subsistencia'])}")
print(f"    Salud 12,5%          {cr.pesos(d['salud_12_5_pct'])}")
print(f"    Tarifa combinada     {d['tarifa_total_pct']}%")
print()

# El desglose también tiene que cuadrar pieza por pieza, no solo el total:
# un error de compensación entre dos líneas daría el mismo total y estaría mal.
cerca(d["pension_16_pct"], 1_216_000, 1, "línea de pensión (16%)")
cerca(d["fsp_solidaridad"], 76_000, 1, "línea de solidaridad (1%)")
cerca(d["fsp_subsistencia"], 0, 0,
      "sin subsistencia: 4,34 SMLMV está lejos de los 16")
cerca(d["salud_12_5_pct"], 950_000, 1, "línea de salud (12,5%)")
revisar(d["tarifa_total_pct"] == 29.5, "la tarifa combinada es 29,5%")
revisar(fila["salud_pensionado_pct"] == 10.0,
        "salud del pensionado 10%: la mesada es 1,56 SMLMV (tramo de 1 a 2)")


# ---------------------------------------------------------------------------
# 2. TABLA DEL FONDO DE SOLIDARIDAD (reglas-rpm.md sección 2)
#    Lo que se prueba es que el escalonado SE SUMA al 1%, no lo reemplaza.
# ---------------------------------------------------------------------------

print("=" * 78)
print("2. FONDO DE SOLIDARIDAD: los dos aportes se suman")
print("=" * 78)
print()

# Cada caso: (SMLMV de la base, solidaridad esperada, subsistencia esperada)
CASOS_FSP = [
    (1.0, 0.0, 0.0),      # Un mínimo: no paga nada adicional
    (3.9, 0.0, 0.0),      # Justo debajo del umbral de 4
    (4.0, 0.01, 0.0),     # En el umbral: entra el 1% de solidaridad
    (10.0, 0.01, 0.0),    # Entre 4 y 16: solo solidaridad
    (16.0, 0.01, 0.002),  # Entra el escalonado, SUMADO al 1%
    (17.5, 0.01, 0.004),
    (18.5, 0.01, 0.006),
    (19.5, 0.01, 0.008),
    (21.0, 0.01, 0.01),   # Más de 20: 2 puntos por encima del 16%
]
for smlmv_base, sol_esp, sub_esp in CASOS_FSP:
    t = cr.tarifa_fondo_solidaridad(smlmv_base * SMLMV_2026, SMLMV_2026)
    ok = t["solidaridad_pct"] == sol_esp and t["subsistencia_pct"] == sub_esp
    revisar(ok, f"IBC de {smlmv_base} SMLMV -> solidaridad {sol_esp * 100}% + "
                f"subsistencia {sub_esp * 100}% "
                f"(obtenido {t['solidaridad_pct'] * 100}% + "
                f"{t['subsistencia_pct'] * 100}%)")

# El error que esta prueba existe para impedir: que el escalonado reemplace
# al 1% en vez de sumarse. Quien gana 21 SMLMV paga 18% en total.
t_alto = cr.aporte_mensual(21 * SMLMV_2026, SMLMV_2026)
revisar(t_alto["tarifa_total_pct"] == 30.5,
        "con 21 SMLMV la tarifa es 30,5% (16 + 1 + 1 de FSP + 12,5 de salud)")


# ---------------------------------------------------------------------------
# 3. PISO Y TECHO DEL IBC (Ley 100 art. 18)
# ---------------------------------------------------------------------------

print()
print("=" * 78)
print("3. PISO Y TECHO DEL IBC")
print("=" * 78)
print()

bajo = cr.aporte_mensual(500_000, SMLMV_2026)
revisar(bajo["ibc"] == SMLMV_2026 and bajo["ibc_topado"],
        "un IBC por debajo del mínimo se sube a 1 SMLMV y se avisa")

alto = cr.aporte_mensual(60_000_000, SMLMV_2026)
revisar(alto["ibc"] == 25 * SMLMV_2026 and alto["ibc_topado"],
        "un IBC por encima de 25 SMLMV se topa ahí y se avisa")

justo = cr.aporte_mensual(7_600_000, SMLMV_2026)
revisar(not justo["ibc_topado"], "un IBC dentro de los límites no se topa")


# ---------------------------------------------------------------------------
# 4. SALUD DEL PENSIONADO POR TRAMOS (vida-del-pensionado.md sección 4)
# ---------------------------------------------------------------------------

print()
print("=" * 78)
print("4. SALUD DEL PENSIONADO: 4 / 10 / 12% por tramo")
print("=" * 78)
print()

CASOS_SALUD = [
    (1.0, 0.04),   # Mesada de un mínimo
    (1.5, 0.10),   # Más de 1 y hasta 2
    (2.0, 0.10),
    (2.5, 0.10),   # Tramo de 2 a 3: la rebaja de la Ley 2294 de 2023
    (3.0, 0.10),
    (3.1, 0.12),   # Más de 3
    (10.0, 0.12),
]
for mesada_smlmv, pct_esp in CASOS_SALUD:
    pct = cr.tarifa_salud_pensionado(mesada_smlmv * SMLMV_2026, SMLMV_2026)
    revisar(pct == pct_esp,
            f"mesada de {mesada_smlmv} SMLMV -> {pct_esp * 100}% de salud "
            f"(obtenido {pct * 100}%)")

# Una mesada de salario mínimo no puede quedar debajo del mínimo por el
# descuento: se descuenta el 4% justamente por eso, pero conviene verlo.
n = cr.mesada_neta(SMLMV_2026, SMLMV_2026)
revisar(round(n["mesada_neta"]) == round(SMLMV_2026 * 0.96),
        "mesada de 1 SMLMV: le descuentan el 4%")


# ---------------------------------------------------------------------------
# 5. LAS 13 MESADAS EN EL BREAKEVEN
#    Ignorarlas alarga el breakeven un 8% de mentira.
# ---------------------------------------------------------------------------

print()
print("=" * 78)
print("5. LAS 13 MESADAS AL AÑO")
print("=" * 78)
print()

con_13 = cr.breakeven_meses(76_228_000, 2_450_406.6, mesadas_al_anio=13)
con_12 = cr.breakeven_meses(76_228_000, 2_450_406.6, mesadas_al_anio=12)
cerca(round(con_13, 1), 28.7, 0.05, "breakeven con 13 mesadas")
cerca(round(con_12, 1), 31.1, 0.05, "breakeven con 12 mesadas (referencia)")
revisar(con_13 < con_12,
        "con 13 mesadas el breakeven es más corto que con 12")

revisar(cr.breakeven_meses(1_000_000, 0) is None,
        "sin mesada no hay breakeven: devuelve None, no una división por cero")


# ---------------------------------------------------------------------------
# 6. LA TABLA DE ESCENARIOS ETIQUETADOS (la forma de salida del producto)
# ---------------------------------------------------------------------------

print()
print("=" * 78)
print("6. TABLA DE ESCENARIOS ETIQUETADOS")
print("=" * 78)
print()

escenarios = [
    {"etiqueta": "sigues como hoy (cotizar sobre 7.600.000)", "ibc": IBC,
     "meses_de_aporte": MESES, "mesada_bruta": MESADA_BRUTA, "es_base": True},
    {"etiqueta": "cotizar sobre el mínimo", "ibc": SMLMV_2026,
     "meses_de_aporte": MESES, "mesada_bruta": SMLMV_2026},
    {"etiqueta": "cotizar sobre 12.000.000", "ibc": 12_000_000,
     "meses_de_aporte": MESES, "mesada_bruta": 3_400_000},
]
tabla = cr.tabla_de_escenarios(escenarios, horizonte_anios=HORIZONTE,
                               smlmv=SMLMV_2026)

revisar(tabla["escenario_base"]["etiqueta"].startswith("sigues como hoy"),
        "la fila base es la marcada con es_base, no la más barata")
revisar(len(tabla["alternativas"]) == 2, "las otras dos filas son alternativas")
revisar(tabla["alternativas"][0]["costo_total"]
        <= tabla["alternativas"][1]["costo_total"],
        "las alternativas quedan ordenadas por costo de menor a mayor")
revisar(all("delta_vs_base" in f for f in tabla["alternativas"]),
        "cada alternativa trae su diferencia contra la base")
revisar(tabla["filas"][0]["es_base"], "la base encabeza la tabla")
revisar(len(tabla["supuestos"]) >= 5,
        "la tabla viaja con sus supuestos declarados")

# Cada fila es un PUNTO ÚNICO, no un rango: la decisión de producto del
# 2026-07-27. Si alguien reintroduce bandas, estas llaves dejan de ser números.
revisar(all(isinstance(f["costo_total"], int) for f in tabla["filas"]),
        "cada fila da un costo puntual, no una banda")

# Sin marca explícita de base, la primera fila hace de base
sin_marca = cr.tabla_de_escenarios(
    [{"etiqueta": "A", "ibc": IBC, "meses_de_aporte": 10, "mesada_bruta": 2_000_000},
     {"etiqueta": "B", "ibc": SMLMV_2026, "meses_de_aporte": 10,
      "mesada_bruta": 1_800_000}], smlmv=SMLMV_2026)
revisar(sin_marca["escenario_base"]["etiqueta"] == "A",
        "sin es_base explícito, la primera fila es la base")

print()
cr.imprimir_tabla(tabla)


# ---------------------------------------------------------------------------
# 7. PUENTE CON EL DIAGNÓSTICO (que la mesada no se teclee a mano)
# ---------------------------------------------------------------------------

print("=" * 78)
print("7. PUENTE CON EL DIAGNÓSTICO")
print("=" * 78)
print()

diag_falso = {"escenario_sigue_cotizando": {"ibc_futuro_supuesto": IBC,
                                            "mesada": MESADA_BRUTA}}
e = cr.escenario_desde_diagnostico("sigues como hoy", diag_falso, MESES,
                                   es_base=True)
revisar(e is not None and e["ibc"] == IBC and e["mesada_bruta"] == MESADA_BRUTA,
        "toma el IBC y la mesada del diagnóstico, sin teclearlos")
revisar(cr.escenario_desde_diagnostico("x", {}, 10) is None,
        "sin datos en el diagnóstico devuelve None: no inventa una mesada")
revisar(cr.escenario_desde_diagnostico(
    "x", {"escenario_sigue_cotizando": {"error": "sin salario"}}, 10) is None,
        "un diagnóstico con error no produce una fila de costo")


# ---------------------------------------------------------------------------

print("=" * 78)
if fallas:
    print(f"RESULTADO: {len(fallas)} FALLAS")
    for f in fallas:
        print(f"  - {f}")
    sys.exit(1)
print("RESULTADO: TODO EN VERDE")
print("=" * 78)
