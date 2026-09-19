# Prueba del módulo RPM con los dos casos Colpensiones del set dorado.
# Chequea que las semanas calculadas cuadren con el documento (la "respuesta
# del profesor") y muestra el diagnóstico completo de cada caso.
# Incluye al final cuatro secciones de REGRESIÓN, con cifras liquidadas a mano,
# que SÍ terminan en código de salida 1 si fallan:
#   1. Piso del 55% de la tasa base (art. 34).
#   2. La fecha de semanas se mide contra el requisito del año que llega, no
#      contra el de hoy (hallazgo 2 de casos-liquidados.md).
#   3. Tope de 25 SMLMV al IBC mensual con empleadores simultáneos, medido con
#      el salario mínimo del año de la cotización (hallazgo 3 del mismo).
#   4. La mesada se liquida con el MAYOR de los dos IBL que da la ley, y la
#      alternativa de toda la vida exige 1.250 semanas (hallazgo 1 del mismo).
# Uso: python3 probar_rpm.py

import json
import sys
from datetime import date
from pathlib import Path

from rpm import (diagnosticar, calcular_mesada, calcular_ibl, expandir_a_meses,
                 fecha_en_que_cumple_semanas, elegir_ibl,
                 TASA_BASE_MINIMA, TASA_BASE_MAXIMA)
from datos_sistema import SMLMV, semanas_requeridas

# Carpeta donde viven los casos del set dorado
CASOS = Path(__file__).parent.parent / "casos"

# Fecha fija de cálculo para que la prueba sea reproducible
FECHA = date(2026, 7, 18)

# El sexo no viene en el documento: aquí simulamos la respuesta del usuario
# (en producción es una pregunta adaptativa del agente)
PRUEBAS = [
    ("caso-04-colpensiones-rpm.json", "F"),
    ("caso-05-colpensiones-rpm.json", "M"),
]


def pesos(n):
    """Formatea un número como pesos colombianos: 1750905 -> $1.750.905"""
    return "$" + f"{n:,.0f}".replace(",", ".")


for archivo, sexo in PRUEBAS:
    caso = json.loads((CASOS / archivo).read_text(encoding="utf-8"))
    d = diagnosticar(caso, sexo, FECHA)

    print("=" * 64)
    print(f"{d['caso_id']}  (sexo: {sexo}, edad: {d['edad']} años)")
    print("=" * 64)

    # Verificación contra el total del documento (tolerancia de extracción)
    dif = abs(d["semanas_hoy"] - d["semanas_documento"])
    check = "CUADRA" if dif <= 0.15 else "NO CUADRA (revisar)"
    print(f"Semanas hoy: {d['semanas_hoy']} (documento: {d['semanas_documento']}, "
          f"dif {dif:.2f} -> {check})")
    print(f"Requisito de semanas este año: {d['requisito_semanas_hoy']}")
    print(f"Densidad de cotización (últimos 3 años): {d['densidad_ultimos_3_anios']:.0%}")
    print(f"Cumple la edad: {d['fecha_cumple_edad']}")
    print(f"Cumple las semanas: {d['fecha_cumple_semanas']}")
    print(f"Pensión estimada desde: {d['fecha_pension_estimada']}")

    # Escenario 1: sigue cotizando igual que hoy
    e = d["escenario_sigue_cotizando"]
    print("\nSi sigue cotizando al ritmo actual:")
    if e and "mesada" in e:
        print(f"  Semanas proyectadas a la pensión: {e['semanas_proyectadas']}")
        print(f"  IBL (últimos 10 años, pesos de hoy): {pesos(e['ibl'])} "
              f"(s = {e['s']} salarios mínimos)")
        print(f"  Tasa de reemplazo: {e['tasa_pct']}% "
              f"(incluye {e['bloques_extra']} bloques de 50 semanas extra)")
        print(f"  Mesada estimada: {pesos(e['mesada'])} en pesos de hoy, x13 al año")
    else:
        print(f"  {e}")

    # Escenario 2: deja de cotizar hoy
    e = d["escenario_deja_de_cotizar"]
    print("\nSi deja de cotizar hoy:")
    if e and "mesada" in e:
        print(f"  Se pensiona igual al cumplir la edad, con {d['semanas_hoy']} semanas")
        print(f"  Tasa de reemplazo: {e['tasa_pct']}%  |  "
              f"Mesada estimada: {pesos(e['mesada'])} en pesos de hoy")
    else:
        print(f"  {e.get('nota', e)}")

    # IBL alternativo de toda la vida (informativo)
    if d["ibl_toda_la_vida"]:
        print(f"\nIBL toda la vida (alternativa por tener 1.250+ semanas): "
          f"{d['ibl_toda_la_vida']}")
    print()


# ---------------------------------------------------------------------------
# REGRESIÓN: el piso del 55% de la tasa base (art. 34, verificado 2026-07-27)
# ---------------------------------------------------------------------------
# Por qué existe esta sección: la fórmula r = 65,5 - 0,5 s corría sin límite
# inferior, así que por encima de 21 salarios mínimos de IBL la tasa base caía
# por debajo del 55% y la mesada quedaba subestimada. La ley dice que ese
# porcentaje "oscilará entre el 65 y el 55%".
# Fuente: Ley 100 art. 34, mod. Ley 797 de 2003 art. 10 (Secretaría del Senado).
# Trampa que ya cayó una vez en el proyecto: 55,5% no es el piso legal, es el
# valor de la fórmula en s = 20.

print("=" * 70)
print("REGRESIÓN: piso y techo de la tasa base")
print("=" * 70)

fallos = []


def revisar(condicion, descripcion):
    """Marca una comprobación como OK o FALLA y la deja anotada si falla."""
    print(f"  {'OK   ' if condicion else 'FALLA'} {descripcion}")
    if not condicion:
        fallos.append(descripcion)


smlmv_hoy = SMLMV[max(SMLMV)]

# 1. IBL de 24 salarios mínimos: la fórmula daría 53,5%, la ley pone piso en 55
alto = calcular_mesada(24 * smlmv_hoy, 1300, "M", 2026)
revisar(alto["tasa_base_pct"] == TASA_BASE_MINIMA,
        f"IBL de 24 SMLMV: tasa base {alto['tasa_base_pct']}% "
        f"(la fórmula sola daría 53,5%)")

# 2. IBL de 30 salarios mínimos: sigue en el piso, no baja más
altisimo = calcular_mesada(30 * smlmv_hoy, 1300, "M", 2026)
revisar(altisimo["tasa_base_pct"] == TASA_BASE_MINIMA,
        "IBL de 30 SMLMV: la tasa base no cae por debajo del piso")

# 3. El piso es 55, no 55,5 (el valor de la fórmula en s = 20)
revisar(TASA_BASE_MINIMA == 55.0,
        "El piso legal es 55%, no 55,5%")

# 4. IBL de 21 SMLMV: la fórmula da 55,0 justo, así que el piso no muerde
justo = calcular_mesada(21 * smlmv_hoy, 1300, "M", 2026)
revisar(justo["tasa_base_pct"] == 55.0,
        "IBL de 21 SMLMV: la fórmula ya da 55%, el piso no cambia nada")

# 5. IBL de 5 SMLMV: zona normal, la fórmula manda y nada se recorta
normal = calcular_mesada(5 * smlmv_hoy, 1300, "M", 2026)
revisar(normal["tasa_base_pct"] == 63.0,
        f"IBL de 5 SMLMV: tasa base {normal['tasa_base_pct']}%, sin recorte")

# 6. Techo de la tasa base: nunca por encima del 65%
bajo = calcular_mesada(int(0.5 * smlmv_hoy), 1300, "M", 2026)
revisar(bajo["tasa_base_pct"] <= TASA_BASE_MAXIMA,
        "IBL por debajo de 1 SMLMV: la tasa base no pasa del 65%")

# 7. El premio por semanas adicionales se suma DESPUÉS del piso
con_extra = calcular_mesada(24 * smlmv_hoy, 1300 + 200, "M", 2026)
revisar(con_extra["tasa_pct"] > con_extra["tasa_base_pct"],
        "Las semanas adicionales suman sobre la tasa base ya pisada")

# 8. Techo global del 80% del IBL, que la misma norma fija
tope = calcular_mesada(2 * smlmv_hoy, 3000, "M", 2026)
revisar(tope["tasa_pct"] <= 80.0,
        "El total nunca pasa del 80% del IBL")


# ---------------------------------------------------------------------------
# Fábrica de historias sintéticas para las dos regresiones que siguen
# ---------------------------------------------------------------------------
# Un renglón por año, igual que los rangos del reporte de Colpensiones.
# Un renglón de 12 meses vale 360 días (convención de 30 días por mes).

ULTIMO_DIA = {1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30,
              7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}


def renglon(anio, meses, ibc):
    """Arma una fila de historia laboral: un año (o parte) de aportes."""
    dias = meses * 30
    semanas = round(dias / 7, 2)      # Regla del día exacto: 1 semana = 7 días
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
    """Arma el JSON del caso con el esquema de casos/esquema-datos.md."""
    periodos = [renglon(a, m, i) for (a, m, i) in serie]
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
# REGRESIÓN: la fecha de semanas se mide contra el requisito DEL AÑO QUE LLEGA
# ---------------------------------------------------------------------------
# Por qué existe: la proyección usaba `requisito_hoy`, el requisito del año de
# cálculo. Como el de la mujer baja 25 semanas por año (Sentencia C-197), se le
# exigía en un año futuro un número que en ese año ya no rige, y la fecha salía
# más tarde. Hallazgo 2 de casos-liquidados.md.
#
# EL CASO, LIQUIDADO A MANO (fecha de cálculo 2026-06-30):
#   Mujer nacida el 1969-01-15 (ya cumplió 57 años, así que manda el requisito
#   de semanas). Cotiza sobre $2.000.000 de 2005 a 2025 completos y los cuatro
#   primeros meses de 2026, al 100% de densidad.
#   Días de hoy    = 21 años x 360 + 4 meses x 30 = 7.560 + 120 = 7.680
#   Semanas de hoy = 7.680 / 7 = 1.097,14
#   Al ritmo de 30 días por mes, cada mes futuro suma 30 días:
#     - contra las 1.250 semanas de 2026 (8.750 días) faltarían 1.070 días,
#       o sea 35,7 meses: junio de 2029. Esto es lo que devolvía el módulo.
#     - contra las 1.200 semanas de 2028 (8.400 días) faltan 720 días,
#       o sea 24 meses exactos desde junio de 2026: JUNIO DE 2028.
#   En mayo de 2028 lleva 8.370 días (1.195,7 semanas) y todavía no alcanza,
#   así que junio de 2028 es el primer mes que cumple. Son 12 meses de pensión.

print()
print("=" * 70)
print("REGRESIÓN: la fecha de semanas usa el requisito del año que llega")
print("=" * 70)

FECHA_REG = date(2026, 6, 30)

SERIE_MUJER = [(a, 12, 2_000_000) for a in range(2005, 2026)] + [(2026, 4, 2_000_000)]
CASO_MUJER = construir_caso("caso-R1-mujer-semanas-c197", "1969-01-15", SERIE_MUJER)

dm = diagnosticar(CASO_MUJER, "F", FECHA_REG, densidad_futura=1.0)

revisar(dm["semanas_hoy"] == 1097.14,
        f"Semanas hoy: {dm['semanas_hoy']} (7.680 días / 7)")
revisar(dm["requisito_semanas_hoy"] == 1250,
        f"Requisito de 2026: {dm['requisito_semanas_hoy']} semanas")
revisar(semanas_requeridas("F", 2028) == 1200,
        f"Requisito de 2028: {semanas_requeridas('F', 2028)} semanas (C-197)")
revisar(dm["fecha_cumple_semanas"] == "2028-06-01",
        f"Cumple las semanas el {dm['fecha_cumple_semanas']} "
        f"(a mano: 2028-06-01, con 8.400 días contra las 1.200 de 2028)")
revisar(dm["fecha_pension_estimada"] == "2028-06-01",
        f"Pensión el {dm['fecha_pension_estimada']}: ya tiene la edad, "
        f"manda la fecha de semanas")
# El valor viejo, el que producía el defecto: si vuelve a aparecer, la
# proyección volvió a medirse contra el requisito del año de cálculo.
revisar(dm["fecha_cumple_semanas"] != "2029-06-01",
        "No reaparece el 2029-06-01 que salía de exigirle las 1.250 de hoy")

# El hombre es el control: su requisito no cambia con el año, así que la
# corrección no puede moverle la fecha.
SERIE_HOMBRE = [(a, 12, 2_000_000) for a in range(2005, 2026)] + [(2026, 4, 2_000_000)]
CASO_HOMBRE = construir_caso("caso-R1-hombre-control", "1962-01-15", SERIE_HOMBRE)
dh = diagnosticar(CASO_HOMBRE, "M", FECHA_REG, densidad_futura=1.0)
# Le faltan 1.300 x 7 - 7.680 = 1.420 días = 47,3 meses: el mes 48 es junio 2030
revisar(dh["fecha_cumple_semanas"] == "2030-06-01",
        f"Hombre (control): cumple las 1.300 el {dh['fecha_cumple_semanas']} "
        f"(a mano: 2030-06-01, 1.420 días faltantes / 30)")

# Nadie que no cotice puede tener fecha: la proyección devuelve None, no un bucle
sin_cotizar = fecha_en_que_cumple_semanas(7_680, "F", FECHA_REG, 0.0)
revisar(sin_cotizar is None,
        "Con densidad 0 no hay fecha de semanas (y la cuenta no se cuelga)")


# ---------------------------------------------------------------------------
# REGRESIÓN: tope de 25 SMLMV al IBC mensual con empleadores simultáneos
# ---------------------------------------------------------------------------
# Por qué existe: los IBC de empleadores simultáneos se suman, pero la ley los
# tope en 25 salarios mínimos (reglas-rpm.md s.8.2, Ley 100 art. 18). Sin el
# tope, dos empleos de 20 SMLMV daban un IBC de 40 SMLMV y la mesada salía
# sobreestimada. Hallazgo 3 de casos-liquidados.md.
#
# LAS CIFRAS, A MANO:
#   SMLMV 2025 = $1.423.500. Dos empleadores a 20 SMLMV = 2 x $28.470.000 =
#   $56.940.000, que son 40 SMLMV. El tope de 2025 es 25 x 1.423.500 =
#   $35.587.500. Es el tope DEL AÑO: usar el de 2026 ($43.772.625) dejaría
#   pasar $8,2 millones mensuales que en 2025 nadie podía cotizar.
#
#   IBL de esa historia (2025 completo + 6 meses de 2026, todo topado):
#     2025: 35.587.500 x 1,051 (IPC a pesos de 2026) = $37.402.462,5 x 360 días
#     2026: 43.772.625 x 1,0                          = $43.772.625   x 180 días
#     IBL = (13.464.886.500 + 7.879.072.500) / 540 = $39.525.850
#   Sin el tope el IBL habría sido $63.241.360, o sea 36 salarios mínimos:
#   imposible, porque el IBL es un promedio de IBC y el IBC no pasa de 25.

print()
print("=" * 70)
print("REGRESIÓN: tope de 25 SMLMV al IBC mensual (empleadores simultáneos)")
print("=" * 70)

# Dos empleadores simultáneos todo 2025, cada uno sobre 20 SMLMV de ese año
simultaneos_2025 = [renglon(2025, 12, 20 * SMLMV[2025]),
                    renglon(2025, 12, 20 * SMLMV[2025])]
mes_2025 = expandir_a_meses(simultaneos_2025)[(2025, 6)]
revisar(mes_2025["ibc"] == 25 * SMLMV[2025],
        f"IBC del mes topado en {pesos(mes_2025['ibc'])} "
        f"(sin tope daban {pesos(2 * 20 * SMLMV[2025])}, o sea 40 SMLMV)")
revisar(mes_2025["ibc"] != 25 * SMLMV[2026],
        f"El tope es el de 2025, no el de hoy ({pesos(25 * SMLMV[2026])})")
revisar(mes_2025["dias"] == 30,
        "Las semanas del mes se siguen contando una sola vez (30 días)")

# El mismo par de empleadores en un año viejo: el tope es mucho más pequeño
simultaneos_2015 = [renglon(2015, 12, 20 * SMLMV[2015]),
                    renglon(2015, 12, 20 * SMLMV[2015])]
mes_2015 = expandir_a_meses(simultaneos_2015)[(2015, 6)]
revisar(mes_2015["ibc"] == 25 * SMLMV[2015],
        f"En 2015 el tope es {pesos(25 * SMLMV[2015])}, no el de 2025 ni el de hoy")

# Un solo empleador por debajo del tope: nada se debe recortar
uno_solo = expandir_a_meses([renglon(2025, 12, 10 * SMLMV[2025])])[(2025, 6)]
revisar(uno_solo["ibc"] == 10 * SMLMV[2025],
        f"Un empleador a 10 SMLMV no se toca: {pesos(uno_solo['ibc'])}")

# Efecto en el IBL, que es lo que termina moviendo la mesada
historia_simultanea = [renglon(2025, 12, 20 * SMLMV[2025]),
                       renglon(2025, 12, 20 * SMLMV[2025]),
                       renglon(2026, 6, 20 * SMLMV[2026]),
                       renglon(2026, 6, 20 * SMLMV[2026])]
ibl_topado, _ = calcular_ibl(expandir_a_meses(historia_simultanea), 2026)
revisar(round(ibl_topado) == 39_525_850,
        f"IBL con el tope aplicado: {pesos(round(ibl_topado))} (a mano: $39.525.850)")
revisar(ibl_topado <= 25 * smlmv_hoy,
        f"El IBL nunca pasa de 25 SMLMV ({pesos(25 * smlmv_hoy)}): "
        f"es un promedio de IBC y el IBC está topado")



# ---------------------------------------------------------------------------
# REGRESIÓN: se liquida con el MAYOR de los dos IBL que da la ley
# ---------------------------------------------------------------------------
# Por qué existe: el IBL de toda la vida se calculaba y se reportaba, pero la
# mesada siempre salía del IBL de los últimos 10 años. La ley da las dos formas
# y manda la que le resulte superior al afiliado, si cotizó 1.250 semanas o más.
# Fuente: Ley 100 art. 21, inciso final; reglas-rpm.md s.4.2. Hallazgo 1 de
# casos-liquidados.md. A quien le pega es a quien ganó mucho más hace más de
# 10 años y terminó cotizando poco.
#
# EL CASO, LIQUIDADO A MANO (fecha de cálculo 2026-06-30):
#   Hombre nacido el 1962-02-20 (ya cumplió 62 años). Cotiza sobre 10 salarios
#   mínimos de cada año de 1996 a 2012, y sobre 1 salario mínimo de 2013 en
#   adelante hasta junio de 2026.
#   Días  = 17 años x 360 + 13 años x 360 + 6 meses x 30 = 10.980
#   Semanas = 10.980 / 7 = 1.568,57, o sea muy por encima de las 1.250 que
#   exige la alternativa: le aplican los dos IBL.
#     IBL de los últimos 10 años  = $1.339.351 (solo sus años de 1 SMLMV)
#     IBL de toda la vida laboral = $6.380.340 (entran sus 17 años buenos)
#   Con el de 10 años: tasa 72,5% sobre $1.339.351 da $971.030, por debajo del
#   salario mínimo, así que la mesada quedaba recortada al piso: $1.750.905.
#   Con el mayor, que es el que manda:
#     s = 6.380.340 / 1.750.905 = 3,64 salarios mínimos
#     tasa base = 65,5 - 0,5 x 3,644 = 63,68%
#     bloques   = (1.568,57 - 1.300) / 50 = 5 completos -> +7,5%
#     tasa      = 71,18%; el techo del 80% no muerde
#     MESADA    = $4.541.398
#   (con las cifras ya redondeadas la multiplicación da $4.541.526; el módulo
#   trabaja con los valores exactos, de ahí los $128 de diferencia)
#   Son $2.790.493 más al mes, 2,6 veces la mesada anterior.

print()
print("=" * 70)
print("REGRESIÓN: la mesada se liquida con el MAYOR de los dos IBL")
print("=" * 70)

# 10 salarios mínimos de cada año hasta 2012, 1 salario mínimo de ahí en adelante
SERIE_MAYOR = ([(a, 12, 10 * SMLMV[a]) for a in range(1996, 2013)] +
               [(a, 12, SMLMV[a]) for a in range(2013, 2026)] +
               [(2026, 6, SMLMV[2026])])
CASO_MAYOR = construir_caso("caso-R3-ibl-toda-la-vida", "1962-02-20", SERIE_MAYOR)

dv = diagnosticar(CASO_MAYOR, "M", FECHA_REG)
ev = dv["escenario_sigue_cotizando"]

revisar(dv["semanas_hoy"] == 1568.57,
        f"Semanas hoy: {dv['semanas_hoy']} (10.980 días / 7)")
revisar(ev["ibl_10_anios"] == 1_339_351,
        f"IBL de los últimos 10 años: {pesos(ev['ibl_10_anios'])} (a mano: $1.339.351)")
revisar(ev["ibl_toda_la_vida"] == 6_380_340,
        f"IBL de toda la vida: {pesos(ev['ibl_toda_la_vida'])} (a mano: $6.380.340)")
revisar(ev["ibl_usado"] == "toda_la_vida",
        f"Se liquida con el mayor de los dos: {ev['ibl_usado']}")
revisar(ev["ibl"] == 6_380_340,
        f"El IBL que entra a la fórmula es {pesos(ev['ibl'])}")
revisar(ev["tasa_pct"] == 71.18,
        f"Tasa: {ev['tasa_pct']}% (63,68 de base + 7,5 por 5 bloques)")
revisar(ev["mesada"] == 4_541_398,
        f"MESADA con el IBL mayor: {pesos(ev['mesada'])} (a mano: $4.541.398)")
# La cifra vieja: el piso de 1 SMLMV, que es donde caía al usar solo los 10 años
revisar(ev["mesada"] != smlmv_hoy,
        f"Ya no cae al piso de 1 SMLMV ({pesos(smlmv_hoy)}), que era la mesada "
        f"anterior: son {pesos(ev['mesada'] - smlmv_hoy)} más al mes")

# --- La condición de las 1.250 semanas, probada en los dos sentidos ---
# Mismo insumo exacto, cambiando solo las semanas: así se aísla la variable.
meses_mayor = expandir_a_meses(CASO_MAYOR["periodos"])

_, _, con_derecho = elegir_ibl(meses_mayor, 2026, 1568.57)
revisar(con_derecho["ibl_usado"] == "toda_la_vida",
        "Con 1.568,57 semanas la alternativa aplica y gana")

_, _, sin_derecho = elegir_ibl(meses_mayor, 2026, 1249.99)
revisar(sin_derecho["ibl_usado"] == "10_anios",
        "Con 1.249,99 semanas la alternativa NO aplica: manda el de 10 años "
        "aunque el de toda la vida fuera mayor")
revisar(sin_derecho["ibl_toda_la_vida"] is None,
        f"Y se dice por qué: {sin_derecho.get('nota_ibl')}")

_, _, en_el_umbral = elegir_ibl(meses_mayor, 2026, 1250)
revisar(en_el_umbral["ibl_usado"] == "toda_la_vida",
        "Con 1.250 exactas ya aplica: la ley dice 'al menos 1.250'")

# --- El control: cuando el de 10 años es mayor, no se toca ---
# Misma historia al revés (1 salario mínimo hasta 2012, 10 desde 2013): ahora
# los buenos años están dentro de la ventana y el de 10 años debe ganar.
SERIE_CRECIENTE = ([(a, 12, SMLMV[a]) for a in range(1996, 2013)] +
                   [(a, 12, 10 * SMLMV[a]) for a in range(2013, 2026)] +
                   [(2026, 6, 10 * SMLMV[2026])])
CASO_CRECIENTE = construir_caso("caso-R3-control-creciente", "1962-02-20",
                                SERIE_CRECIENTE)
dc = diagnosticar(CASO_CRECIENTE, "M", FECHA_REG)["escenario_sigue_cotizando"]
revisar(dc["ibl_usado"] == "10_anios",
        f"Control: con la historia al revés gana el de 10 años "
        f"({pesos(dc['ibl_10_anios'])} contra {pesos(dc['ibl_toda_la_vida'])})")
revisar(dc["ibl"] == dc["ibl_10_anios"],
        "Control: la mesada se liquida con ese, no con el de toda la vida")


# ---------------------------------------------------------------------------
# REGRESIÓN: el caso femenino del set dorado (caso-04 corrido como mujer)
# ---------------------------------------------------------------------------
# Por qué existe: hasta aquí el set dorado se corría como mujer en UN solo sitio
# (la lista PRUEBAS del comienzo de este archivo), pero solo IMPRIMÍA el
# diagnóstico. Ninguna cifra quedaba fijada, así que un cambio que rompiera la
# mitad femenina del modelo no hacía fallar nada. Esta sección clava las cifras.
#
# El sexo no viene en el documento de Colpensiones: lo responde la persona. Aquí
# se corre la MISMA historia laboral con los dos sexos, y la comparación es la
# prueba de que el sexo sí atraviesa todo el cálculo de punta a punta.
#
# LAS DOS REGLAS QUE MUEVE EL SEXO, verificadas en este caso:
#   1. Edad legal: mujer 57, hombre 62. Nacida el 18/05/1978, cumple 57 el
#      18/05/2035 y 62 el 18/05/2040. Son cinco años de pensión de diferencia.
#   2. Semanas exigidas: al hombre siempre 1.300. A la mujer le bajan 25 por año
#      desde las 1.250 de 2026 (Sentencia C-197), así que en 2035 son 1.025.
#      Eso le da más bloques de 50 semanas extra y, con ellos, más tasa.
#
# Las cifras esperadas de abajo salen de correr esta misma calculadora el día
# que se fijaron. NO son una liquidación a mano: son un ancla de regresión. Si
# alguna se mueve, hay que entender POR QUÉ antes de actualizarla.

print()
print("=" * 70)
print("REGRESIÓN: el caso femenino real del set dorado (caso-04)")
print("=" * 70)

caso_04 = json.loads(
    (CASOS / "caso-04-colpensiones-rpm.json").read_text(encoding="utf-8"))

# --- La mujer: es como se corre el caso en la lista PRUEBAS de arriba ---
df = diagnosticar(caso_04, "F", FECHA)
sf = df["escenario_sigue_cotizando"]
nf = df["escenario_deja_de_cotizar"]

revisar(df["semanas_hoy"] == 1478.43 == df["semanas_documento"],
        f"Semanas: {df['semanas_hoy']} y cuadran con el documento")
revisar(df["requisito_semanas_hoy"] == 1250,
        f"Requisito de la mujer en 2026: {df['requisito_semanas_hoy']} (C-197)")
revisar(df["fecha_cumple_edad"] == "2035-05-18",
        f"Cumple los 57 el {df['fecha_cumple_edad']}")
revisar(df["fecha_pension_estimada"] == "2035-05-18",
        f"Se pensiona el {df['fecha_pension_estimada']}: ya tiene las semanas, "
        f"manda la edad")

# Escenario en que sigue cotizando hasta pensionarse
revisar(sf["requisito_semanas"] == 1025,
        f"Requisito del año en que se pensiona (2035): {sf['requisito_semanas']}")
revisar(sf["ibl_usado"] == "toda_la_vida",
        "Le gana el IBL de toda la vida laboral (art. 21)")
revisar(sf["ibl"] == 2_711_151, f"IBL con el que se liquida: {pesos(sf['ibl'])}")
revisar(sf["bloques_extra"] == 18,
        f"Bloques de 50 semanas sobre las 1.025: {sf['bloques_extra']}")
revisar(sf["tasa_pct"] == 80.0,
        f"Tasa recortada al techo del 80% (base {sf['tasa_base_pct']}% + bloques)")
revisar(sf["mesada"] == 2_168_920, f"MESADA si sigue cotizando: {pesos(sf['mesada'])}")

# Escenario en que deja de cotizar hoy: aquí manda el IBL de los 10 años
revisar(nf["ibl_usado"] == "10_anios",
        "Si deja de cotizar hoy, el mayor pasa a ser el IBL de 10 años")
revisar(nf["mesada"] == 2_842_996,
        f"MESADA si deja de cotizar: {pesos(nf['mesada'])}")

# --- El hombre: la misma historia, el otro sexo. Es el control ---
# Sirve para dos cosas: comprobar que el sexo de verdad cambia el resultado
# (si las dos cifras fueran iguales, el parámetro no estaría llegando al
# cálculo) y dejar medido cuánto lo cambia.
dm4 = diagnosticar(caso_04, "M", FECHA)
sm4 = dm4["escenario_sigue_cotizando"]

revisar(dm4["requisito_semanas_hoy"] == 1300,
        f"Control hombre: le exigen {dm4['requisito_semanas_hoy']} semanas fijas")
revisar(dm4["fecha_cumple_edad"] == "2040-05-18",
        f"Control hombre: cumple los 62 el {dm4['fecha_cumple_edad']}, "
        f"cinco años después")
revisar(sm4["requisito_semanas"] == 1300,
        "Control hombre: su requisito no baja con el año, el de ella sí")
revisar(sm4["mesada"] == 2_078_724,
        f"Control hombre: mesada {pesos(sm4['mesada'])}")
revisar(sf["mesada"] != sm4["mesada"],
        f"El sexo SÍ mueve la mesada: {pesos(sf['mesada'] - sm4['mesada'])} "
        f"más para ella, y cinco años antes")

print()
if fallos:
    print(f"RESULTADO: {len(fallos)} FALLAS en las regresiones de RPM")
    for f in fallos:
        print(f"  - {f}")
    sys.exit(1)
print("RESULTADO: regresiones de RPM en verde (piso del 55%, fecha de semanas "
      "con el requisito del año, tope de 25 SMLMV al IBC, IBL mayor de los dos, "
      "caso femenino del set dorado)")
