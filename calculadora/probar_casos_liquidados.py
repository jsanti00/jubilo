# Prueba de resultado del módulo RPM contra cuatro casos liquidados A MANO.
#
# Qué la hace distinta de las otras pruebas del proyecto: las demás verifican
# que el flujo CORRA y que las semanas CUADREN. Esta verifica que el RESULTADO
# sea el correcto. Cada número esperado de aquí abajo está liquidado paso a paso,
# desde la norma, en calculadora/casos-liquidados.md, con sus cifras intermedias.
# Si una cifra de aquí cambia, hay que ir a ese documento y rehacer la cuenta:
# NO se ajusta el número esperado para que la prueba pase.
#
# Los cuatro casos son SINTÉTICOS y viven dentro de este archivo. No tocan el set
# dorado de casos/, que es la otra fuente de verdad del proyecto.
#
# Uso: python3 probar_casos_liquidados.py
# Termina en código de salida 1 si alguna comprobación falla.

import sys
from datetime import date

from rpm import diagnosticar, calcular_mesada
from datos_sistema import SMLMV

# Salario mínimo del año más reciente cargado: el ancla de todas las cifras
SMLMV_HOY = SMLMV[2026]

# Fecha de cálculo fija: sin esto las cifras cambiarían cada día que corra la prueba
FECHA = date(2026, 6, 30)


# ---------------------------------------------------------------------------
# Fábrica de casos sintéticos
# ---------------------------------------------------------------------------
# Cada caso se arma con un renglón por año (o por tramo de año), igual que los
# rangos del reporte de Colpensiones. Un renglón de 12 meses vale 360 días, que
# es la convención de 30 días por mes que usa todo el proyecto.

# Último día de cada mes, para cerrar bien el rango de cada renglón
ULTIMO_DIA = {1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30,
              7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}


def renglon(anio, meses, ibc):
    """Arma una fila de historia laboral: un año (o parte de un año) de aportes.

    anio: el año de la cotización. meses: cuántos meses del año cotizó (desde
    enero). ibc: el salario mensual sobre el que cotizó, en pesos de ese año.
    """
    dias = meses * 30                    # Convención del sistema: 30 días por mes
    semanas = round(dias / 7, 2)         # Regla del día exacto: 1 semana = 7 días
    return {
        "desde": f"{anio}-01-01",
        "hasta": f"{anio}-{meses:02d}-{ULTIMO_DIA[meses]}",
        "empleador": "EMPRESA SINTETICA", "nit": "900000000",
        "tipo_cotizante": "empleado",
        "ibc": ibc, "ibc_tipo": "ultimo_del_rango",
        "cotizacion": None, "dias_cotizados": None,
        "semanas": semanas, "semanas_lic": 0.0, "semanas_sim": 0.0,
        "semanas_validas": semanas,
        "administradora": "Colpensiones", "observacion": "normal",
    }


def construir_caso(caso_id, nacimiento, serie):
    """Arma el JSON completo del caso con el esquema de casos/esquema-datos.md.

    serie es una lista de (año, meses cotizados, IBC mensual de ese año).
    """
    periodos = [renglon(a, m, i) for (a, m, i) in serie]
    # El total del documento: lo que iría impreso en el resumen de Colpensiones
    dias = sum(round(p["semanas_validas"] * 7) for p in periodos)
    return {
        "caso_id": caso_id,
        "documento": {"administradora_emisora": "Colpensiones", "regimen": "RPM",
                      "formato": "colpensiones_reporte_semanas",
                      "fecha_generacion": "2026-06-30"},
        "afiliado": {"fecha_nacimiento": nacimiento, "edad_en_documento": None,
                     "sexo": None, "fecha_afiliacion": None,
                     "estado_afiliacion": "activo_cotizante"},
        "resumen_documento": {"total_semanas": round(dias / 7, 2), "total_dias": dias,
                              "saldo_cuenta_individual": None,
                              "semanas_en_otros_fondos": None},
        "periodos": periodos,
    }


# ---------------------------------------------------------------------------
# CASO L1: hombre de 64 años que ya cumple edad y semanas
# ---------------------------------------------------------------------------
# Liquidación completa en casos-liquidados.md sección 2.
# De 2000 a 2015 el salario sube $60.000 cada año desde $800.000
IBC_L1 = {a: 800_000 + (a - 2000) * 60_000 for a in range(2000, 2016)}
IBC_L1.update({2016: 2_000_000, 2017: 2_100_000, 2018: 2_200_000, 2019: 2_300_000,
               2020: 2_400_000, 2021: 2_500_000, 2022: 2_700_000, 2023: 3_000_000,
               2024: 3_200_000, 2025: 3_400_000, 2026: 3_600_000})
# Cotiza todos los meses de 2000 a 2025 y los seis primeros de 2026
SERIE_L1 = [(a, 12 if a < 2026 else 6, IBC_L1[a]) for a in range(2000, 2027)]
CASO_L1 = construir_caso("caso-L1-rpm-hombre-cumple-hoy", "1962-02-20", SERIE_L1)

# ---------------------------------------------------------------------------
# CASO L2: mujer de 54 años que se pensiona en 2029
# ---------------------------------------------------------------------------
# Liquidación completa en casos-liquidados.md sección 3. Este es el caso que
# habría atrapado el bug del IBL: la ventana se ancla a 2029, no a 2026.
IBC_L2 = {a: 700_000 + (a - 2004) * 70_000 for a in range(2004, 2016)}
IBC_L2.update({2016: 1_900_000, 2017: 2_000_000, 2018: 2_100_000, 2019: 2_300_000,
               2020: 2_400_000, 2021: 2_600_000, 2022: 2_900_000, 2023: 3_200_000,
               2024: 3_500_000, 2025: 3_800_000, 2026: 4_000_000})
SERIE_L2 = [(a, 12 if a < 2026 else 6, IBC_L2[a]) for a in range(2004, 2027)]
CASO_L2 = construir_caso("caso-L2-rpm-mujer-proyeccion", "1972-03-10", SERIE_L2)

# ---------------------------------------------------------------------------
# CASO L3: alto ingreso donde muerde el piso del 55%
# ---------------------------------------------------------------------------
# Liquidación completa en casos-liquidados.md sección 4. Cotiza sobre 4 salarios
# mínimos de 1993 a 2015, pasa ocho años sin cotizar, y vuelve en 2024 sobre el
# tope legal de 25 salarios mínimos. Esa forma es la única que lleva el IBL por
# encima de los 21 salarios mínimos donde el piso empieza a operar.
IBC_L3 = {a: 4 * SMLMV[a] for a in range(1993, 2016)}
IBC_L3.update({2024: 25 * SMLMV[2024], 2025: 25 * SMLMV[2025], 2026: 25 * SMLMV[2026]})
SERIE_L3 = ([(a, 12, IBC_L3[a]) for a in range(1993, 2016)] +
            [(2024, 12, IBC_L3[2024]), (2025, 12, IBC_L3[2025]), (2026, 6, IBC_L3[2026])])
CASO_L3 = construir_caso("caso-L3-rpm-piso-55", "1962-05-10", SERIE_L3)

# ---------------------------------------------------------------------------
# CASO L4: cuando gana el IBL de toda la vida laboral
# ---------------------------------------------------------------------------
# Liquidación completa en casos-liquidados.md sección 5. Es el caso que respalda
# la función elegir_ibl, agregada el 2026-07-28 al corregir el hallazgo 1: la ley
# ofrece dos formas de calcular el IBL y manda usar la que le resulte superior al
# afiliado. Este señor ganó muy bien de 1994 a 2015 y terminó cotizando cerca del
# mínimo, así que la ventana de los últimos 10 años le borra sus mejores años.
# El salario del tramo viejo va por debajo del tope de 25 SMLMV de 1994
# ($2.467.500) para que el tope de IBC no intervenga y el caso pruebe una sola cosa.
SERIE_L4 = ([(a, 12, 2_400_000) for a in range(1994, 2016)] +
            [(a, 12 if a < 2026 else 6, 1_800_000) for a in range(2016, 2027)])
CASO_L4 = construir_caso("caso-L4-rpm-ibl-toda-la-vida", "1962-08-15", SERIE_L4)


# ---------------------------------------------------------------------------
# Motor de comprobación
# ---------------------------------------------------------------------------

fallos = []   # Aquí se acumula todo lo que no cuadre, para reportarlo junto


def pesos(n):
    """Formatea un número como pesos colombianos: 2338280 -> $2.338.280"""
    return "$" + f"{n:,.0f}".replace(",", ".")


def revisar(obtenido, esperado, descripcion):
    """Compara una cifra del módulo contra la cifra liquidada a mano."""
    ok = obtenido == esperado
    print(f"  {'OK   ' if ok else 'FALLA'} {descripcion}: {obtenido}"
          + ("" if ok else f"  (esperado a mano: {esperado})"))
    if not ok:
        fallos.append(f"{descripcion}: el módulo da {obtenido}, la cuenta a mano "
                      f"da {esperado}")


print("=" * 72)
print("CASOS DE RPM LIQUIDADOS A MANO  (ver calculadora/casos-liquidados.md)")
print("=" * 72)
print(f"Fecha de cálculo fija: {FECHA.isoformat()}   SMLMV 2026: {pesos(SMLMV_HOY)}")

# ---------------------------------------------------------------------------
# L1
# ---------------------------------------------------------------------------
print("\nCASO L1: hombre de 64 años, ya cumple edad y semanas")
d = diagnosticar(CASO_L1, "M", FECHA)
e = d["escenario_sigue_cotizando"]

revisar(d["semanas_hoy"], 1362.86, "Semanas hoy (9.540 días / 7)")
revisar(d["requisito_semanas_hoy"], 1300, "Requisito del hombre")
revisar(d["fecha_cumple_edad"], "2024-02-20", "Fecha en que cumplió 62 años")
revisar(d["fecha_pension_estimada"], "2026-06-30", "Fecha de pensión")
revisar(e["ibl"], 3_543_487, "IBL de los 10 años, indexado por IPC")
revisar(e["s"], 2.02, "IBL en salarios mínimos (s)")
revisar(e["tasa_base_pct"], 64.49, "Tasa base = 65,5 - 0,5 x s")
revisar(e["bloques_extra"], 1, "Bloques completos de 50 semanas extra")
revisar(e["tasa_pct"], 65.99, "Tasa total = 64,49 + 1,5")
revisar(e["mesada"], 2_338_280, "MESADA liquidada a mano")
revisar(d["ibl_toda_la_vida"]["ibl"], 3_232_467, "IBL de toda la vida (informativo)")
print(f"  ->  {pesos(e['mesada'])} al mes, {pesos(e['mesada'] * 13)} al año con 13 mesadas")

# ---------------------------------------------------------------------------
# L2
# ---------------------------------------------------------------------------
print("\nCASO L2: mujer de 54 años, se pensiona en 2029")
d = diagnosticar(CASO_L2, "F", FECHA)
e = d["escenario_sigue_cotizando"]

revisar(d["semanas_hoy"], 1157.14, "Semanas hoy (8.100 días / 7)")
revisar(d["requisito_semanas_hoy"], 1250, "Requisito de la mujer en 2026 (C-197)")
revisar(d["fecha_cumple_edad"], "2029-03-10", "Fecha en que cumple 57 años")
revisar(d["fecha_pension_estimada"], "2029-03-10", "Fecha de pensión (manda la edad)")
revisar(e["semanas_proyectadas"], 1298.6, "Semanas al pensionarse (8.100 + 990 días)")
revisar(e["requisito_semanas"], 1175, "Requisito del año de pensión, 2029")
# Esta es la cifra que verifica la corrección del bug del IBL: la ventana de 10
# años se ancla a 2029, así que los 33 meses futuros entran al promedio salarial.
revisar(e["ibl"], 3_850_666, "IBL de los 10 años ANTERIORES A 2029, con futuro")
revisar(e["tasa_base_pct"], 64.4, "Tasa base = 65,5 - 0,5 x 2,199")
revisar(e["bloques_extra"], 2, "Bloques de 50 semanas sobre las 1.175")
revisar(e["tasa_pct"], 67.4, "Tasa total = 64,4 + 3,0")
revisar(e["mesada"], 2_595_364, "MESADA liquidada a mano")
# Si deja de cotizar hoy no llega a las semanas: el camino sería indemnización
revisar(d["escenario_deja_de_cotizar"].get("resultado"), "sin_pension",
        "Si deja de cotizar hoy, no alcanza las semanas")
print(f"  ->  {pesos(e['mesada'])} al mes, {pesos(e['mesada'] * 13)} al año con 13 mesadas")

# ---------------------------------------------------------------------------
# L3
# ---------------------------------------------------------------------------
print("\nCASO L3: alto ingreso, aquí muerde el piso del 55%")
d = diagnosticar(CASO_L3, "M", FECHA)
e = d["escenario_sigue_cotizando"]

revisar(d["semanas_hoy"], 1311.43, "Semanas hoy (9.180 días / 7)")
revisar(d["fecha_pension_estimada"], "2026-06-30", "Fecha de pensión")
revisar(e["ibl"], 38_088_986, "IBL de los 10 años (solo 2024, 2025 y 2026 pesan)")
revisar(e["s"], 21.75, "IBL en salarios mínimos: por encima de 21, donde muerde el piso")
# La fórmula sola daría 54,62%. La ley no deja bajar del 55%.
revisar(e["tasa_base_pct"], 55.0, "Tasa base pisada en 55% (la fórmula daría 54,62%)")
revisar(e["bloques_extra"], 0, "Cero bloques: solo tiene 11,4 semanas de sobra")
revisar(e["tasa_pct"], 55.0, "Tasa total, sin premio por semanas")
revisar(e["mesada"], 20_948_942, "MESADA liquidada a mano")
print(f"  ->  {pesos(e['mesada'])} al mes, {pesos(e['mesada'] * 13)} al año con 13 mesadas")

# ---------------------------------------------------------------------------
# L4
# ---------------------------------------------------------------------------
print("\nCASO L4: aquí gana el IBL de toda la vida laboral (elegir_ibl)")
d = diagnosticar(CASO_L4, "M", FECHA)
e = d["escenario_sigue_cotizando"]

revisar(d["semanas_hoy"], 1671.43, "Semanas hoy (11.700 días / 7)")
revisar(d["fecha_pension_estimada"], "2026-06-30", "Fecha de pensión")
# Los dos IBL que ofrece la ley, cada uno liquidado a mano por separado
revisar(e["ibl_10_anios"], 2_502_892, "IBL de los 10 años (el tramo mal pagado)")
revisar(e["ibl_toda_la_vida"], 6_800_501, "IBL de toda la vida (incluye 1994 a 2015)")
# Esta es la comprobación nueva: la ley manda usar el mayor de los dos
revisar(e["ibl_usado"], "toda_la_vida", "Cuál se usa: el MAYOR, como manda el art. 21")
revisar(e["ibl"], 6_800_501, "IBL con el que se liquida")
revisar(e["s"], 3.88, "IBL en salarios mínimos (s)")
revisar(e["tasa_base_pct"], 63.56, "Tasa base = 65,5 - 0,5 x 3,884")
revisar(e["bloques_extra"], 7, "Bloques de 50 semanas (1.671,4 - 1.300 = 371,4)")
revisar(e["tasa_pct"], 74.06, "Tasa total = 63,56 + 10,5")
revisar(e["mesada"], 5_036_315, "MESADA liquidada a mano, con el IBL correcto")
print(f"  ->  {pesos(e['mesada'])} al mes, {pesos(e['mesada'] * 13)} al año con 13 mesadas")
print(f"      Con el IBL de 10 años habría sido $1.884.308: "
      f"{pesos(e['mesada'] - 1_884_308)} menos al mes")

# Contraprueba: en los otros tres casos gana el IBL de 10 años. Sin esto, la
# corrección del hallazgo 1 podría haber cambiado un sesgo por otro.
print("\n  Contraprueba: en L1, L2 y L3 el mayor es el de 10 años")
for nombre, caso, sexo in [("L1", CASO_L1, "M"), ("L2", CASO_L2, "F"),
                           ("L3", CASO_L3, "M")]:
    detalle = diagnosticar(caso, sexo, FECHA)["escenario_sigue_cotizando"]
    revisar(detalle["ibl_usado"], "10_anios",
            f"{nombre}: se liquida con el IBL de 10 años")

# ---------------------------------------------------------------------------
# Los topes, verificados aparte (casos-liquidados.md sección 6)
# ---------------------------------------------------------------------------
# Ninguno de los tres casos activa el techo del 80%, el piso de 1 SMLMV ni el
# tope de 25 SMLMV, así que se verifican con entradas directas a calcular_mesada.
print("\nTOPES Y PISOS (entradas sintéticas, liquidadas a mano igual que los casos)")

# Techo del 80%: base 64,5% + 11 bloques x 1,5% = 81%, recortado a 80%
techo = calcular_mesada(2 * SMLMV_HOY, 1850, "M", 2026)
revisar(techo["tasa_pct"], 80.0, "Techo: 64,5 + 16,5 = 81% se recorta a 80%")
revisar(techo["mesada"], 2_801_448, "Techo: mesada = 80% de 2 SMLMV")

# Piso de 1 SMLMV: la mesada calculada da $650.000 y se sube al salario mínimo
piso = calcular_mesada(1_000_000, 1300, "M", 2026)
revisar(piso["tasa_base_pct"], 65.0, "Piso: la tasa base no pasa del techo de 65%")
revisar(piso["mesada"], SMLMV_HOY, "Piso: ninguna pensión por debajo de 1 SMLMV")

# Tope de 25 SMLMV: IBL imposible en la práctica (ver hallazgo 4 del documento)
tope = calcular_mesada(100_000_000, 1300, "M", 2026)
revisar(tope["tasa_base_pct"], 55.0, "Tope: s = 57,1 deja la tasa base en el piso de 55%")
revisar(tope["mesada"], 25 * SMLMV_HOY, "Tope: ninguna pensión por encima de 25 SMLMV")


# ---------------------------------------------------------------------------
# Veredicto
# ---------------------------------------------------------------------------
print()
print("=" * 72)
if fallos:
    print(f"RESULTADO: {len(fallos)} FALLAS contra la liquidación manual")
    for f in fallos:
        print(f"  - {f}")
    print()
    print("NO ajustes el número esperado para que la prueba pase. Rehaz la cuenta")
    print("en calculadora/casos-liquidados.md y decide cuál de los dos está mal.")
    sys.exit(1)
print("RESULTADO: los cuatro casos liquidados a mano cuadran con rpm.py, peso por peso")
