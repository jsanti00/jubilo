# Prueba del módulo RAIS con los tres casos de fondos privados del set dorado.
# Chequea que las semanas cuadren con el documento y muestra el diagnóstico.
# Uso: python3 probar_rais.py

import json
import sys
from datetime import date
from pathlib import Path

from rais import diagnosticar

# Carpeta donde viven los casos del set dorado
CASOS = Path(__file__).parent.parent / "casos"

# Fecha fija de cálculo para que la prueba sea reproducible
FECHA = date(2026, 7, 18)

# Datos que el documento no trae y en producción se preguntan al usuario:
# (archivo, sexo simulado). El caso 03 solo trae edad, no fecha de nacimiento.
PRUEBAS = [
    ("caso-01-porvenir-rais.json", None),   # El doc sí trae sexo M
    ("caso-02-skandia-rais.json", None),    # El doc sí trae sexo M
    ("caso-03-proteccion-rais.json", "M"),  # Sexo simulado (el doc no lo trae)
]

NOMBRE_SALIDA = {
    "pension_por_capital": "PENSIÓN POR CAPITAL (el saldo la financia solo)",
    "garantia_pension_minima": "GARANTÍA DE PENSIÓN MÍNIMA (el Estado completa a 1 SMLMV)",
    "devolucion_de_saldos": "DEVOLUCIÓN DE SALDOS (no alcanza pensión)",
}


def pesos(n):
    """Formatea un número como pesos colombianos: 1750905 -> $1.750.905"""
    return "$" + f"{n:,.0f}".replace(",", ".")


for archivo, sexo in PRUEBAS:
    caso = json.loads((CASOS / archivo).read_text(encoding="utf-8"))
    d = diagnosticar(caso, sexo=sexo, fecha_calculo=FECHA)

    print("=" * 64)
    print(f"{d['caso_id']}  (sexo: {d['sexo']}, edad: {d['edad']} años)")
    print("=" * 64)

    # Verificación contra el total del documento
    dif = abs(d["semanas_hoy"] - d["semanas_documento"])
    check = "CUADRA" if dif <= 0.15 else "NO CUADRA (revisar)"
    print(f"Semanas hoy: {d['semanas_hoy']} (documento: {d['semanas_documento']}, "
          f"dif {dif:.2f} -> {check})")

    # Situación de la cuenta
    marca = " (ESTIMADO desde aportes, sin rendimientos: pedir saldo real)" \
        if d["saldo_es_estimado"] else ""
    print(f"Saldo hoy: {pesos(d['saldo_hoy'])}{marca}")
    print(f"Salario actual (IBC): {pesos(d['ibc_actual'])}  |  "
          f"Densidad últimos 3 años: {d['densidad_ultimos_3_anios']:.0%}")
    print(f"Semanas proyectadas a los {d['edad_legal']}: "
          f"{d['semanas_proyectadas_edad_legal']} "
          f"(GPM exige {d['semanas_gpm']})")

    # Escenarios por perfil de fondo (a la edad legal, en pesos de hoy).
    # Cada perfil trae su BANDA: el piso con el precio de mercado de la renta
    # vitalicia y el techo con el 4% de la norma. Perfil en las filas, banda en
    # las columnas: los dos rangos NO se multiplican entre sí.
    print(f"\nMesada estimada a los {d['edad_legal']} años (pesos de hoy, x13),"
          f" en banda:")
    print(f"  {'perfil':<13} {'saldo':>16}  {'conservador':>14} .. "
          f"{'optimista':>14}   salida")
    for perfil in ["conservador", "moderado", "mayor_riesgo", "deja_de_cotizar"]:
        e = d["escenarios"][perfil]
        etiqueta = "si deja hoy" if perfil == "deja_de_cotizar" else perfil
        bajo, alto = e["mesada_banda"]
        salidas = NOMBRE_SALIDA[e["salida"]]
        if e["salida"] != e["salida_conservadora"]:
            # Los dos extremos pueden caer en salidas distintas del RAIS, y eso
            # cambia la conversación, no solo la cifra
            salidas = (f"{NOMBRE_SALIDA[e['salida_conservadora']]} .. "
                       f"{NOMBRE_SALIDA[e['salida']]}")
        print(f"  {etiqueta:<13} {pesos(e['saldo_proyectado']):>16}  "
              f"{pesos(bajo):>14} .. {pesos(alto):>14}   {salidas}")

    # La SEGUNDA banda, la del rendimiento, va aparte y con otro nombre: no es
    # incertidumbre del modelo sino la diferencia entre administradoras, que el
    # usuario sí puede accionar. Nunca se fusiona con la de arriba.
    print("\nLo que pesa la administradora (mismo perfil, misma edad, "
          "solo cambia la AFP):")
    for perfil in ["conservador", "moderado", "mayor_riesgo"]:
        e = d["escenarios"][perfil]
        piso_r, techo_r = e["rendimiento_rango"]
        bajo_afp, alto_afp = e["mesada_banda_afp"]
        print(f"  {perfil:<13} rendimiento {piso_r:.2%} a {techo_r:.2%}  ->  "
              f"{pesos(bajo_afp)} a {pesos(alto_afp)}")
    print(f"  {d['banda_rendimiento']['que_significa_el_rango']}")

    # Pensión anticipada (el "aha" del RAIS), también en banda
    temprana, tardia = d["edad_pension_anticipada_banda"]
    if temprana and temprana < d["edad_legal"]:
        if tardia and tardia != temprana:
            print(f"\nPensión anticipada: entre los {temprana} y los {tardia} años, "
                  f"según el precio de la renta vitalicia (perfil moderado, "
                  f"Ley 100 art. 64)")
        elif tardia == temprana:
            print(f"\nPensión anticipada: desde los {temprana} años con los dos "
                  f"extremos del factor (perfil moderado, Ley 100 art. 64)")
        else:
            print(f"\nPensión anticipada: desde los {temprana} años con el factor "
                  f"normativo; con el factor de mercado NO alcanza el umbral "
                  f"antes de la edad legal")

    # El umbral del 110%, que es lo que decide lo anterior, también en banda
    cap = d["capital_umbral_110_pct"]
    if cap:
        print(f"Capital que exige el umbral del 110% del SMLMV a los "
              f"{d['edad_legal']}: entre {pesos(cap['optimista'])} (norma) y "
              f"{pesos(cap['conservador'])} (mercado)")

    # La declaración de los dos extremos va pegada a las cifras, siempre
    b = d["banda_factor"]
    print("\nDe dónde sale cada extremo:")
    for nombre in ["optimista", "conservador"]:
        x = b["extremos"][nombre]
        print(f"  {nombre:<12} factor {x['factor']:>6}  tasa real "
              f"{x['tasa_real_anual']:.4%}  ({x['de_donde_sale']})")
        print(f"               fuente: {x['fuente']}")
        print(f"               confianza: {x['confianza']}")
    print(f"  Decreto 1485 de 2025: {b['decreto_1485_de_2025']}")
    print(f"  Salvedad de la fuente: {b['inconsistencia_de_la_fuente']}")
    print()


# ===========================================================================
# REGRESIÓN: salarios fantasma en `ibc_actual` (sesión de role-play 2026-07-26)
# ===========================================================================
# Qué se está protegiendo. La versión vieja de `rais.py` sacaba el salario
# actual de la ÚLTIMA FILA del documento que tuviera IBC:
#
#     next((p["ibc"] for p in reversed(periodos) if p.get("ibc")), None)
#
# Eso falla en tres formas, y la sesión de role-play del 2026-07-26 destapó la
# tercera con un caso real: las últimas filas del reporte eran de una empresa
# temporal con salario reportado y CERO semanas acreditadas. El código tomaba
# $1.750.905 (un salario que nadie cotizó) cuando el salario real del afiliado
# era $3.600.000. En ese caso no cambió el veredicto (la ventana de traslado
# estaba cerrada y el comparador no se usó), pero en un caso RAIS de verdad
# subestimaría la proyección cerca de la mitad.
#
# Hoy `ibc_actual` trabaja sobre el mapa mensual depurado. Estas pruebas fijan
# ese comportamiento para que no se pueda revertir sin que algo se ponga rojo.

fallas = []


def revisar(condicion, descripcion):
    print(f"  {'OK  ' if condicion else 'FALLA'}  {descripcion}")
    if not condicion:
        fallas.append(descripcion)


print("=" * 64)
print("REGRESIÓN: el salario actual ignora las filas sin cotización real")
print("=" * 64)

# --- 1. El caso real que lo destapó (Colpensiones, hombre 59, independiente) ---
# Se corre por el módulo RAIS a propósito: es la pierna que usaría el
# comparador de traslado si la ventana estuviera abierta.
caso_real = json.loads(
    (CASOS / "caso-05-colpensiones-rpm.json").read_text(encoding="utf-8"))
d = diagnosticar(caso_real, sexo="M", fecha_calculo=date(2026, 7, 26))
print(f"\n  caso-05: ibc_actual = {pesos(d['ibc_actual'])}")
revisar(d["ibc_actual"] == 3_600_000,
        "toma los $3.600.000 que el afiliado sí cotizó como independiente")
revisar(d["ibc_actual"] != 1_750_905,
        "NO toma los $1.750.905 de la fila temporal con cero semanas")

# --- 2. Salario fantasma al final del documento (formato mensual privado) ---
base = {
    "caso_id": "sintetico-fantasma",
    "documento": {"regimen": "RAIS"},
    "afiliado": {"sexo": "M", "fecha_nacimiento": "1996-01-15"},
    "resumen_documento": {"total_semanas": 8.57,
                          "saldo_cuenta_individual": 50_000_000},
    "periodos": [
        {"desde": "2026-04-01", "hasta": "2026-04-30", "empleador": "REAL",
         "ibc": 6_000_000, "dias_cotizados": 30, "observacion": "normal"},
        {"desde": "2026-05-01", "hasta": "2026-05-31", "empleador": "REAL",
         "ibc": 6_000_000, "dias_cotizados": 30, "observacion": "normal"},
        # Novedad administrativa: hay salario, no hay días cotizados
        {"desde": "2026-06-01", "hasta": "2026-06-30", "empleador": "TEMPORAL",
         "ibc": 1_750_905, "dias_cotizados": 0, "observacion": "normal"},
    ],
}
d = diagnosticar(base, fecha_calculo=date(2026, 7, 26))
print(f"\n  fila final sin días cotizados: ibc_actual = {pesos(d['ibc_actual'])}")
revisar(d["ibc_actual"] == 6_000_000,
        "una fila con salario y cero días no se toma como salario actual")

# --- 3. Documento desordenado: la última fila no es el último mes ---
desordenado = json.loads(json.dumps(base))
desordenado["periodos"] = [desordenado["periodos"][1],   # mayo
                           desordenado["periodos"][0]]   # abril, al final
d = diagnosticar(desordenado, fecha_calculo=date(2026, 7, 26))
print(f"  documento fuera de orden cronológico: ibc_actual = "
      f"{pesos(d['ibc_actual'])}")
revisar(d["ibc_actual"] == 6_000_000,
        "el salario sale del último MES, no de la última FILA")

# --- 4. Dos empleadores el mismo mes: los salarios se suman ---
simultaneo = json.loads(json.dumps(base))
simultaneo["periodos"] = [
    {"desde": "2026-05-01", "hasta": "2026-05-31", "empleador": "A",
     "ibc": 4_000_000, "dias_cotizados": 30, "observacion": "normal"},
    {"desde": "2026-05-01", "hasta": "2026-05-31", "empleador": "B",
     "ibc": 2_000_000, "dias_cotizados": 30, "observacion": "normal"},
]
d = diagnosticar(simultaneo, fecha_calculo=date(2026, 7, 26))
print(f"  dos empleadores el mismo mes: ibc_actual = {pesos(d['ibc_actual'])}")
revisar(d["ibc_actual"] == 6_000_000,
        "con dos empleadores se suman los dos IBC, no se toma uno solo")

# --- 5. El salario actual es el que alimenta el aporte a la cuenta ---
# No basta con que el campo salga bien en la salida: tiene que estar moviendo
# la proyección. Si el salario fantasma volviera, el saldo proyectado caería.
sano = json.loads(json.dumps(base))
sano["periodos"] = sano["periodos"][:2]          # sin la fila fantasma
d_sano = diagnosticar(sano, fecha_calculo=date(2026, 7, 26))
d_con_fantasma = diagnosticar(base, fecha_calculo=date(2026, 7, 26))
revisar(d_sano["escenarios"]["moderado"]["saldo_proyectado"]
        == d_con_fantasma["escenarios"]["moderado"]["saldo_proyectado"],
        "la fila fantasma no mueve el saldo proyectado ni un peso")

# ===========================================================================
# REGRESIÓN: LA BANDA DEL FACTOR DE CONVERSIÓN (decisiones 1 y 2, 2026-07-27)
# ===========================================================================
# Qué se está protegiendo. La calculadora convertía capital en mesada con el 4%
# de interés técnico, que es la tasa de RESERVA del sistema y no el PRECIO al
# que una aseguradora vende una renta vitalicia. Daba un número único donde no
# hay certeza. Ahora entrega una banda, y estas pruebas fijan tres cosas:
#   1. que la banda existe en todo lo que depende del factor,
#   2. que los extremos nunca salen al revés,
#   3. que el extremo optimista es EXACTAMENTE lo que la calculadora daba antes
#      del cambio, para que ninguna cifra histórica del proyecto quede huérfana.

print("=" * 64)
print("REGRESIÓN: la banda del factor de conversión")
print("=" * 64)

# Cifras vigentes del extremo OPTIMISTA de la banda del factor, medidas el
# 2026-07-27 con la misma fecha de cálculo de esta prueba.
#
# OJO, ESTAS CIFRAS SE MOVIERON A PROPÓSITO EL 2026-07-27, en la recalibración
# del rendimiento por perfil de fondo (decisión de Santiago). No es que la banda
# del factor haya cambiado: el factor sigue idéntico y su compatibilidad se
# comprueba aparte, en el bloque "compatibilidad del factor" de más abajo, que no
# depende del supuesto de rendimiento. Lo que cambió es cuánto capital se acumula
# antes de convertirlo. Los valores viejos, para la historia del proyecto:
# caso-01 moderado 2.666.551 y anticipada a los 58; caso-03 moderado 17.029.586 y
# anticipada a los 35. Salían de suponer un 4% real en el perfil moderado, que
# queda por encima del techo del rango observado por la Superfinanciera.
#
# SEGUNDO MOVIMIENTO A PROPÓSITO, EL 2026-09-19: los límites de renta variable
# por tipo de fondo se verificaron en fuente primaria (Decreto 2555 de 2010,
# art. 2.6.12.1.4) y resultaron ser una BANDA encadenada, no un techo suelto:
# conservador 0% a 20%, moderado 20% a 45%, mayor riesgo 45% a 70%. El modelo
# metía a cada perfil con su TECHO, que era el borde optimista declarado; ahora
# entra con el PUNTO MEDIO de su banda (10%, 32,5% y 57,5%). El conservador no
# se mueve, porque es el ancla. Los otros dos bajan un poco: el moderado pasa de
# 2,895% a 2,8075% real y el mayor riesgo de 3,77% a 3,6825%, y de ahí sale la
# caída de entre 1,9% y 3,0% en las cifras de abajo.
# Los valores del 2026-07-27 al 2026-09-19, para la historia del proyecto:
#   caso-01: moderado 2.090.605, mayor riesgo 2.532.935, deja de cotizar
#            320.346, anticipada a los 61.
#   caso-02: deja de cotizar 206.082 (las tres mesadas ya estaban en el piso).
#   caso-03: moderado 13.200.055, mayor riesgo 16.136.877, deja de cotizar
#            1.980.637, anticipada a los 36 (no se movió).
ANTES_DE_LA_BANDA = {
    "caso-01-porvenir-rais.json": {
        "sexo": None,
        "mesadas": {"conservador": 1_750_905, "moderado": 2_051_542,
                    "mayor_riesgo": 2_484_132, "deja_de_cotizar": 311_080},
        "anticipada": 62,
    },
    "caso-02-skandia-rais.json": {
        "sexo": None,
        "mesadas": {"conservador": 1_750_905, "moderado": 1_750_905,
                    "mayor_riesgo": 1_750_905, "deja_de_cotizar": 200_036},
        "anticipada": None,
    },
    "caso-03-proteccion-rais.json": {
        "sexo": "M",
        "mesadas": {"conservador": 10_870_263, "moderado": 12_942_177,
                    "mayor_riesgo": 15_811_432, "deja_de_cotizar": 1_920_896},
        "anticipada": 36,
    },
}

for archivo, esperado in ANTES_DE_LA_BANDA.items():
    caso = json.loads((CASOS / archivo).read_text(encoding="utf-8"))
    d = diagnosticar(caso, sexo=esperado["sexo"], fecha_calculo=FECHA)
    print(f"\n  {d['caso_id']}")

    # --- 1. La banda existe en todo lo que depende del factor ---
    revisar(all(k in d for k in ("banda_factor",
                                 "edad_pension_anticipada_conservadora",
                                 "edad_pension_anticipada_banda",
                                 "capital_umbral_110_pct")),
            "el diagnóstico trae banda de mesada, de edad anticipada y de umbral")
    revisar(all({"mesada", "mesada_conservadora", "mesada_banda",
                 "salida", "salida_conservadora"} <= set(e)
                for e in d["escenarios"].values()),
            "cada escenario trae sus dos extremos de mesada y de salida")

    # --- 2. El orden de los extremos nunca se invierte ---
    revisar(all(e["mesada_conservadora"] <= e["mesada"]
                for e in d["escenarios"].values()),
            "la mesada conservadora nunca supera a la optimista")
    revisar(all(e["mesada_banda"] == (e["mesada_conservadora"], e["mesada"])
                for e in d["escenarios"].values()),
            "la banda de mesada viene ordenada de menor a mayor")
    temprana, tardia = d["edad_pension_anticipada_banda"]
    revisar(tardia is None or (temprana is not None and tardia >= temprana),
            "con el precio de mercado la pensión anticipada nunca llega antes")
    cap = d["capital_umbral_110_pct"]
    revisar(cap["conservador"] > cap["optimista"],
            "el umbral del 110% exige más capital al precio de mercado")

    # --- 3. El optimista, peso por peso ---
    for perfil, valor in esperado["mesadas"].items():
        revisar(d["escenarios"][perfil]["mesada"] == valor,
                f"{perfil}: el extremo optimista sigue en {pesos(valor)}")
    revisar(d["edad_pension_anticipada"] == esperado["anticipada"],
            f"la edad de pensión anticipada optimista sigue en "
            f"{esperado['anticipada']}")

# --- 4. Los dos extremos se DECLARAN, con fuente y confianza ---
print("\n  declaración de los extremos")
b = d["banda_factor"]
revisar(set(b["extremos"]) == {"optimista", "conservador"},
        "la declaración nombra los dos extremos")
revisar(all(x["fuente"] and x["confianza"] and x["de_donde_sale"]
            for x in b["extremos"].values()),
        "cada extremo dice de dónde sale, su fuente y su nivel de confianza")
revisar("NO es fuente oficial" in b["extremos"]["conservador"]["fuente"],
        "el extremo conservador declara que su fuente NO es oficial")
revisar("Superfinanciera" in b["extremos"]["optimista"]["fuente"],
        "el extremo optimista cita la norma de la Superfinanciera")
revisar(b["extremos"]["conservador"]["factor"]
        > b["extremos"]["optimista"]["factor"],
        "el factor de mercado exige más capital por peso de mesada")
revisar(b["por_que_difieren"] and b["como_se_combina_con_los_perfiles_de_fondo"],
        "la declaración explica por qué difieren y cómo se combina con perfiles")

# --- 5. La calibración del extremo conservador se reproduce ---
# El factor de referencia es 268 para un hombre de 62 años. Si alguien cambia la
# tasa implícita sin querer, esto se pone rojo.
import datos_sistema as ds                     # Para las comprobaciones de datos
import rais                                    # Para probar la conversión directa
from rais import factor_conversion, EXTREMOS
factor_referencia = factor_conversion(
    ds.EXPECTATIVA_VIDA[ds.FACTOR_MERCADO_REFERENCIA_SEXO],
    ds.INTERES_MERCADO)
print(f"\n  factor de mercado reconstruido: {factor_referencia:.1f} "
      f"(referencia: {ds.FACTOR_MERCADO_REFERENCIA})")
revisar(abs(factor_referencia - ds.FACTOR_MERCADO_REFERENCIA) < 0.5,
        "la tasa implícita reproduce el factor de mercado de referencia")
revisar(abs(factor_conversion(21.3) - factor_conversion(21.3, EXTREMOS["optimista"]))
        < 1e-9,
        "el factor por defecto sigue siendo el 4% normativo (nada cambió solo)")

# --- 6. Los dos rangos no se multiplican entre sí ---
# La banda que se comunica es la del perfil que le aplica al usuario. Si alguien
# armara el rango del piso del perfil conservador al techo del de mayor riesgo,
# la banda del perfil moderado dejaría de estar contenida en su propio perfil.
caso = json.loads((CASOS / "caso-03-proteccion-rais.json").read_text(encoding="utf-8"))
d = diagnosticar(caso, sexo="M", fecha_calculo=FECHA)
mod = d["escenarios"]["moderado"]
todas = [e["mesada_banda"] for e in d["escenarios"].values()]
union = (min(b[0] for b in todas), max(b[1] for b in todas))
revisar(mod["mesada_banda"] != union,
        "la banda del perfil moderado es la suya, no la unión de los tres perfiles")
# Nota: NO se comprueba que moderado quede entre conservador y mayor riesgo. Con
# los rendimientos observados el moderado NO le gana al conservador, y exigir ese
# orden sería fijar en una prueba un supuesto que los datos desmienten.

# --- 7. El ancla de mercado es distinta por sexo (dato del 2026-07-27) ---
# Antes se extrapolaba el precio de la mujer con la tasa implícita del hombre.
# Ahora cada sexo tiene su propio capital de referencia, y la fuente misma es
# inconsistente entre los dos: eso se declara, no se promedia en silencio.
print("\n  ancla de mercado por sexo")
revisar(ds.factor_mercado("F") != ds.factor_mercado("M"),
        "hombres y mujeres no comparten el factor de mercado")
revisar(abs(ds.factor_mercado("M")
            - ds.CAPITAL_RV_UN_SMLMV[2026]["M"] / ds.SMLMV[2026]) < 1e-9,
        "el factor del hombre sale del capital de la fuente, no de una cifra suelta")
revisar(all(ds.interes_mercado(s) < ds.INTERES_TECNICO for s in ("M", "F")),
        "en los dos sexos el precio de mercado es más caro que el de la norma")
revisar(b["inconsistencia_de_la_fuente"],
        "la salida declara que las dos anclas de la fuente no son consistentes")

# --- 8. Decreto 1485 de 2025: aplicado solo a quien se pensione desde 2027 ---
# El decreto encarece la renta vitalicia NUEVA desde 2027. Quien se pensione en
# 2026 no lo enfrenta, y esa diferencia tiene que verse en las cifras.
print("\n  Decreto 1485 de 2025")
for sexo_x in ("M", "F"):
    revisar(ds.factor_mercado(sexo_x, 2027) > ds.factor_mercado(sexo_x, 2026),
            f"sexo {sexo_x}: desde 2027 la misma mesada exige más capital")
    revisar(abs(ds.factor_mercado(sexo_x, 2026) - ds.factor_mercado(sexo_x)) < 1e-9,
            f"sexo {sexo_x}: a quien se pensiona en 2026 no se le aplica el decreto")
encarecimiento = {s: ds.CAPITAL_RV_UN_SMLMV[2027][s] / ds.CAPITAL_RV_UN_SMLMV[2026][s] - 1
                  for s in ("M", "F")}
print(f"    encarecimiento recalculado: hombres {encarecimiento['M']:.1%}, "
      f"mujeres {encarecimiento['F']:.1%}")
revisar(abs(encarecimiento["M"] - encarecimiento["F"]) > 0.005,
        "el encarecimiento por sexo es distinto: no se usa un 14% parejo")
revisar("NO está en el decreto" in d["banda_factor"]["decreto_1485_de_2025"],
        "la salida advierte que el 14% de prensa no está en el decreto")

# --- 9. Compatibilidad del factor, sin depender del supuesto de rendimiento ---
# Esta es la garantía que protege la banda del factor: convertir un saldo dado en
# mesada al 4% normativo tiene que dar exactamente lo mismo que daba antes de que
# existiera la banda. Se comprueba sobre la conversión y no sobre el diagnóstico
# completo, a propósito: así la recalibración del rendimiento (que sí mueve las
# cifras finales) no puede tapar una regresión del factor.
print("\n  compatibilidad del factor (independiente del rendimiento)")
SALDO_PATRON = 500_000_000
# 500 millones a 21,3 años de expectativa y 13 mesadas, al 4% real: la cuenta
# vieja de la calculadora, hecha a mano y fijada aquí.
esperado_optimista = SALDO_PATRON / (13 * (1 - 1.04 ** -21.3) / 0.04)
revisar(abs(rais.mesada_desde_saldo(SALDO_PATRON, 21.3) - esperado_optimista) < 1e-6,
        "convertir saldo a mesada sin tasa explícita sigue dando el 4% normativo")
revisar(abs(rais.factor_conversion(21.3) - 184.047) < 0.01,
        "el factor del 4% a 21,3 años sigue siendo 184,0")

# ===========================================================================
# REGRESIÓN: LA SEGUNDA BANDA, LA DEL RENDIMIENTO POR PERFIL (2026-07-27)
# ===========================================================================
# Qué se está protegiendo. Los tres supuestos de rendimiento quedaban FUERA del
# rango observado por la Superfinanciera, y no en la misma dirección: el
# conservador subestimaba y los otros dos sobreestimaban. Santiago decidió
# recalibrar a rango. Lo delicado no es el dato sino que ahora hay DOS bandas, y
# multiplicarlas produce un rango que no le sirve a nadie.

print("=" * 64)
print("REGRESIÓN: la banda del rendimiento y la convivencia de las dos bandas")
print("=" * 64)

# --- 1. Los tres puntos centrales OBSERVADOS caen dentro de su rango ---
print("\n  recalibración")
for perfil, (piso, techo) in ds.RENDIMIENTO_REAL_OBSERVADO.items():
    punto = ds.RENDIMIENTO_REAL_OBSERVADO_CENTRAL[perfil]
    print(f"    {perfil:<13} observado {piso:.2%} a {techo:.2%}, central "
          f"{punto:.2%}  |  prospectivo "
          f"{ds.RENDIMIENTO_REAL_PROSPECTIVO[perfil]:.2%}")
    revisar(piso <= punto <= techo,
            f"{perfil}: el central observado cae dentro de su propio rango")
revisar(ds.RENDIMIENTO_REAL["moderado"] != 0.04,
        "el moderado ya no usa el 4% que se salía por encima del rango")

# --- 1 bis. LAS DOS CONSTANTES CONVIVEN Y NADIE MAQUILLÓ LA EVIDENCIA ---
# Esta es la prueba que pidió Santiago al aprobar el supuesto prospectivo: la
# proyección puede usar un supuesto de largo plazo, pero el dato observado no se
# borra ni se ajusta para que cuadre con él. Si alguien "arregla" el observado
# para hacerlo monótono, esto se pone rojo.
print("\n  evidencia y supuesto conviven, sin maquillar")
revisar(ds.RENDIMIENTO_REAL_OBSERVADO_CENTRAL != ds.RENDIMIENTO_REAL_PROSPECTIVO,
        "las dos constantes existen y son distintas")
prosp = ds.RENDIMIENTO_REAL_PROSPECTIVO
revisar(prosp["conservador"] < prosp["moderado"] < prosp["mayor_riesgo"],
        "el supuesto prospectivo sí es monótono creciente")
obs = ds.RENDIMIENTO_REAL_OBSERVADO_CENTRAL
# Antes del 2026-09-18 aquí se comprobaba lo contrario: que el observado NO era
# monótono, porque con las cifras de prensa el moderado rendía menos que el
# conservador. Con el dato primario de la SFC sí es monótono, y eso es un
# resultado, no un maquillaje: lo que se vigila ahora es que el observado siga
# siendo el dato medido y no una copia del supuesto.
revisar(obs["conservador"] < obs["moderado"] < obs["mayor_riesgo"],
        "con el dato primario el observado sí es monótono creciente")
revisar(not ds.MODERADO_NO_SUPERA_A_CONSERVADOR,
        "la contradicción del moderado contra el conservador quedó resuelta")
revisar(obs != ds.RENDIMIENTO_REAL_PROSPECTIVO,
        "el observado sigue siendo el dato medido, no una copia del supuesto")
revisar(ds.RENDIMIENTO_REAL_OBSERVADO_ANTERIOR["moderado"][0]
        < ds.RENDIMIENTO_REAL_OBSERVADO_ANTERIOR["conservador"][0],
        "la serie de prensa archivada conserva la contradicción que tenía")
revisar(ds.RENDIMIENTO_REAL == ds.RENDIMIENTO_REAL_PROSPECTIVO,
        "la proyección usa el prospectivo, no el observado")

# --- 1 ter. La construcción del prospectivo es reproducible y está declarada ---
print("\n  construcción del supuesto")
for perfil in ds.RENDIMIENTO_REAL_PROSPECTIVO:
    esperado = (ds.RENDIMIENTO_REAL_OBSERVADO_CENTRAL["conservador"]
                + (ds.EXPOSICION_RENTA_VARIABLE[perfil]
                   - ds.EXPOSICION_RENTA_VARIABLE["conservador"])
                * ds.PRIMA_RENTA_VARIABLE_LARGO_PLAZO)
    revisar(abs(ds.RENDIMIENTO_REAL_PROSPECTIVO[perfil] - esperado) < 1e-9,
            f"{perfil}: el prospectivo se reproduce con la fórmula declarada")
revisar(abs(ds.RENDIMIENTO_REAL_PROSPECTIVO["conservador"]
            - ds.RENDIMIENTO_REAL_OBSERVADO_CENTRAL["conservador"]) < 1e-9,
        "el conservador prospectivo es el observado: ahí está el ancla")

# --- 1 ter bis. Los límites de renta variable son una banda, no un techo ---
# Verificados en el Decreto 2555 de 2010, art. 2.6.12.1.4, el 2026-09-19.
# Estas cuatro comprobaciones son el candado: si alguien vuelve a modelar los
# fondos como "hasta X%" a secas, o mete a un perfil con su techo, se pone rojo.
print("\n  la banda legal de renta variable")
revisar(ds.EXPOSICION_RENTA_VARIABLE_BANDA == {"conservador": (0.00, 0.20),
                                               "moderado": (0.20, 0.45),
                                               "mayor_riesgo": (0.45, 0.70)},
        "las bandas de renta variable son las del artículo 2.6.12.1.4")
revisar(ds.EXPOSICION_RENTA_VARIABLE_BANDA["moderado"][0]
        == ds.EXPOSICION_RENTA_VARIABLE_BANDA["conservador"][1]
        and ds.EXPOSICION_RENTA_VARIABLE_BANDA["mayor_riesgo"][0]
        == ds.EXPOSICION_RENTA_VARIABLE_BANDA["moderado"][1],
        "las bandas van encadenadas: el mínimo de un fondo es el máximo del anterior")
for perfil, (piso, techo) in ds.EXPOSICION_RENTA_VARIABLE_BANDA.items():
    revisar(abs(ds.EXPOSICION_RENTA_VARIABLE[perfil] - (piso + techo) / 2) < 1e-9,
            f"{perfil}: la fórmula usa el punto medio de la banda, no el techo")
    piso_r, techo_r = ds.RENDIMIENTO_PROSPECTIVO_BANDA[perfil]
    revisar(piso_r <= ds.RENDIMIENTO_REAL_PROSPECTIVO[perfil] <= techo_r,
            f"{perfil}: el prospectivo cae dentro del rango que permite la ley")
revisar("2.6.12.1.4" in ds.FUENTE_EXPOSICION_RENTA_VARIABLE
        and "ALTA" in ds.FUENTE_EXPOSICION_RENTA_VARIABLE,
        "la banda cita el artículo exacto y declara confianza ALTA")
revisar("Dimson" in ds.FUENTE_PRIMA_RENTA_VARIABLE
        and "otro mercado" in ds.FUENTE_PRIMA_RENTA_VARIABLE,
        "la prima cita su fuente y declara que se importa de otro mercado")

# --- 1 quater. La salida declara la contradicción, sin esconderla ---
d_sup = diagnosticar(caso, sexo="M", fecha_calculo=FECHA)
bs = d_sup["banda_rendimiento"]
print("\n  la salida declara la contradicción")
revisar("desapareció" in bs["contradiccion_con_lo_observado"],
        "la salida explica que la contradicción se resolvió con el dato primario")
revisar("2,02%" in bs["contradiccion_con_lo_observado"],
        "y trae las cifras nuevas para que se pueda verificar")
revisar(bs["observado_ultimos_5_anios"]["moderado"][0] < 0
        and "no se esconde" in bs["advertencia_ultimos_5_anios"],
        "la salida entrega la ventana de 5 años sin maquillarla")
revisar("sigue siendo el dato" in bs["contradiccion_con_lo_observado"],
        "la salida sigue diciendo que el observado manda sobre el supuesto")
revisar("LARGO PLAZO" in bs["prospectivo_advertencia"]
        and "no lo que los fondos rindieron" in bs["prospectivo_advertencia"],
        "la salida advierte que la proyección no usa el rendimiento histórico")
# Hasta el 2026-09-19 aquí se comprobaba lo contrario: que la salida marcara
# con [VERIFICAR] el eslabón de los límites de renta variable, porque no se
# habían podido leer en la norma. Ya se leyeron (Decreto 2555, art. 2.6.12.1.4),
# así que ahora lo que se vigila es que la salida traiga la banda verificada y
# cite su fuente. Si alguien vuelve a poner un techo suelto, esto se pone rojo.
revisar("VERIFICADO" in bs["prospectivo_limites_verificados"]
        and "2.6.12.1.4" in bs["prospectivo_limites_verificados"],
        "la salida declara que los límites se verificaron, y en qué artículo")
revisar(bs["exposicion_renta_variable_banda"]["moderado"] == [0.20, 0.45]
        and bs["exposicion_renta_variable_banda"]["mayor_riesgo"] == [0.45, 0.70]
        and bs["exposicion_renta_variable_banda"]["conservador"] == [0.00, 0.20],
        "la salida trae la banda de renta variable de cada fondo, no un techo")
# Las bandas van ENCADENADAS: donde termina un fondo empieza el siguiente. Es
# el numeral 2 del artículo, y es lo que impide que el moderado baje del 20%.
revisar(bs["exposicion_renta_variable_banda"]["moderado"][0]
        == bs["exposicion_renta_variable_banda"]["conservador"][1]
        and bs["exposicion_renta_variable_banda"]["mayor_riesgo"][0]
        == bs["exposicion_renta_variable_banda"]["moderado"][1],
        "las bandas están encadenadas: el piso de un fondo es el techo del otro")
revisar("2555" in bs["exposicion_renta_variable_fuente"]
        and "ALTA" in bs["exposicion_renta_variable_fuente"],
        "la banda cita el decreto del que sale y declara confianza ALTA")
revisar(bs["observado_rangos"] and bs["prospectivo"],
        "la salida entrega las dos cosas: la evidencia y el supuesto")

# --- 1 quinquies. La dispersión entre AFP sigue siendo dato observado ---
# El nivel es supuesto, la dispersión es hecho medido. Si alguien inventara
# también la dispersión, el ancho dejaría de coincidir con el de la SFC.
print("\n  el nivel es supuesto, la dispersión es dato")
for perfil in ("conservador", "moderado", "mayor_riesgo"):
    e = d_sup["escenarios"][perfil]
    piso_r, techo_r = e["rendimiento_rango"]
    obs_piso, obs_techo = ds.RENDIMIENTO_REAL_OBSERVADO[perfil]
    revisar(abs((techo_r - piso_r) - (obs_techo - obs_piso)) < 1e-9,
            f"{perfil}: la dispersión entre AFP es la observada por la SFC")
    revisar(abs(e["rendimiento_central"]
                - ds.RENDIMIENTO_REAL_PROSPECTIVO[perfil]) < 1e-9,
            f"{perfil}: el nivel central es el prospectivo")

# --- 2. El rango se declara con fuente, confianza y qué significa ---
d = diagnosticar(caso, sexo="M", fecha_calculo=FECHA)
br = d["banda_rendimiento"]
revisar("Superintendencia Financiera" in br["observado_fuente"]
        and "hds9-4524" in br["observado_fuente"],
        "el rango declara su fuente y el dataset primario de donde sale")
revisar("ALTA" in br["observado_confianza"],
        "el rango declara confianza ALTA, porque ya es dato primario")
revisar("rendimiento_afp.py" in br["observado_fuente"],
        "la fuente dice con qué script se reproduce el cálculo")
revisar("NO es riesgo de mercado" in br["que_significa_el_rango"]
        and "AFP" in br["que_significa_el_rango"],
        "la salida dice que el rango es entre administradoras, no riesgo de mercado")
revisar(not br["moderado_no_supera_a_conservador"],
        "la bandera de la contradicción viaja en la salida, hoy apagada")

# --- 3. Cada escenario trae la banda de administradora, ordenada ---
print("\n  las dos bandas en cada escenario")
for perfil, e in d["escenarios"].items():
    revisar({"mesada_banda_afp", "mesada_envolvente", "rendimiento_rango"} <= set(e),
            f"{perfil}: trae la banda por administradora y la envolvente")
    revisar(e["mesada_banda_afp"][0] <= e["mesada_banda_afp"][1],
            f"{perfil}: la banda por administradora viene ordenada")
    revisar(e["mesada_envolvente"][0] <= e["mesada_banda"][0]
            and e["mesada_envolvente"][1] >= e["mesada_banda"][1],
            f"{perfil}: la envolvente contiene a la banda que se comunica")

# --- 4. La banda que se comunica NO es la envolvente ---
# Es el corazón de la decisión de diseño: si alguien fusiona las dos bandas,
# esto se pone rojo.
mod = d["escenarios"]["moderado"]
ancho_comunicado = mod["mesada_banda"][1] / mod["mesada_banda"][0]
ancho_envolvente = mod["mesada_envolvente"][1] / mod["mesada_envolvente"][0]
print(f"\n    ancho comunicado x{ancho_comunicado:.2f}  contra envolvente "
      f"x{ancho_envolvente:.2f}")
revisar(mod["mesada_banda"] != mod["mesada_envolvente"],
        "la banda que se comunica no es la envolvente de las dos")
revisar(ancho_envolvente > ancho_comunicado,
        "la envolvente es más ancha, que es justo la razón de no comunicarla")
revisar("no se comunica" in d["regla_dos_bandas"]
        or "no se le muestra" in mod["mesada_envolvente_no_comunicar"],
        "la envolvente viene marcada como no comunicable")
revisar("accionable" in d["regla_dos_bandas"],
        "la regla explica que la banda de administradora sí es accionable")

# ===========================================================================
# REGRESIÓN: EL VECTOR TMR COMO PISO DEL PRECIO (2026-07-27)
# ===========================================================================
# Qué se está protegiendo. El extremo conservador se apoyaba solo en prensa.
# Llegó el vector TMR de la Superfinanciera, que SÍ es fuente primaria, pero que
# NO es el precio de venta: es la tasa de la reserva matemática. Usarlo como si
# fuera el precio sería repetir el error original del proyecto en la dirección
# contraria. Se usa como COTA: nadie vende una renta más barata que la reserva
# que debe constituir. Estas pruebas fijan las dos cosas a la vez.

print("=" * 64)
print("REGRESIÓN: el vector TMR como piso del precio")
print("=" * 64)

# --- 1. La tabla reproduce el anexo oficial, en los plazos que importan ---
# Valores leídos del Excel de la Carta Circular 038 de 2026 el 2026-07-27.
print("\n  tabla de tasas reales")
for plazo, esperado in [(20, 0.006876), (21, 0.006777), (25, 0.006448),
                        (28, 0.006257)]:
    revisar(abs(ds.TMR_REAL_POR_PLAZO[plazo] - esperado) < 1e-9,
            f"plazo {plazo}: la tasa real sigue en {esperado:.4%}")

# --- 2. La zona contaminada del anexo queda fuera ---
# La inflación implícita se topa en 3,00% desde el plazo 30 y el 29 ya está en
# transición. Si alguien extendiera la tabla más allá del 28, la tasa real se
# dispararía a 2,07% en el 29 y 3,49% en el 30, que no son precios de mercado.
print("\n  zona limpia del anexo")
revisar(max(ds.TMR_REAL_POR_PLAZO) == 28,
        "la tabla llega hasta el plazo 28, el último con inflación de mercado")
revisar(ds.tmr_real(29.7) == ds.TMR_REAL_POR_PLAZO[28],
        "una expectativa de 29,7 años se topa en el plazo 28, no extrapola")
revisar(all(v < 0.01 for v in ds.TMR_REAL_POR_PLAZO.values()),
        "ninguna tasa real de la tabla se sale del orden de magnitud esperado")

# --- 3. Se usa como COTA, y se declara que no es el precio de venta ---
print("\n  la TMR es cota, no precio")
for sexo_x in ("M", "F"):
    revisar(abs(ds.factor_mercado(sexo_x)
                - max(ds.factor_solo_prensa(sexo_x), ds.factor_tmr(sexo_x))) < 1e-9,
            f"sexo {sexo_x}: el factor usado es el mayor entre prensa y TMR")
    revisar(ds.factor_mercado(sexo_x) >= ds.factor_tmr(sexo_x),
            f"sexo {sexo_x}: el precio nunca queda por debajo de la reserva")
d_h = diagnosticar(caso, sexo="M", fecha_calculo=FECHA)
tmr_h = d_h["banda_factor"]["piso_de_reserva_tmr"]
print(f"    hombre: prensa {tmr_h['factor_de_prensa']}, TMR {tmr_h['factor_piso']}")
revisar("no el precio de venta" in tmr_h["que_es"],
        "la salida declara que la TMR no es el precio de venta")
revisar("Carta Circular 038" in tmr_h["fuente"] and "PRIMARIA" in tmr_h["fuente"],
        "la salida cita la carta circular y que es fuente primaria")
revisar("prensa" in tmr_h["cual_mando"],
        "en el hombre manda el dato de prensa, que queda por encima del piso")

# --- 4. En la mujer manda la TMR, y eso desmiente el dato de prensa ---
# El capital de prensa de la mujer implicaría vender por debajo de la reserva
# matemática. Ninguna aseguradora lo hace, así que ahí manda la cota.
print("\n  el caso de la mujer")
revisar(ds.factor_tmr("F") > ds.factor_solo_prensa("F"),
        "el dato de prensa de la mujer queda por debajo del piso de reserva")
mujer = json.loads((CASOS / "caso-01-porvenir-rais.json").read_text(encoding="utf-8"))
d_m = diagnosticar(mujer, sexo="F", fecha_calculo=FECHA)
tmr_m = d_m["banda_factor"]["piso_de_reserva_tmr"]
print(f"    mujer: prensa {tmr_m['factor_de_prensa']}, TMR {tmr_m['factor_piso']}")
revisar("la TMR" in tmr_m["cual_mando"],
        "en la mujer manda la TMR y la salida lo dice")
revisar("plazo 28" in tmr_m["salvedad_del_plazo"],
        "en la mujer se declara que el plazo se topó en 28")

# --- 5. El orden de la banda aguanta en los dos sexos ---
for sexo_x, dx in (("M", d_h), ("F", d_m)):
    revisar(all(e["mesada_conservadora"] <= e["mesada"]
                for e in dx["escenarios"].values()),
            f"sexo {sexo_x}: la banda sigue ordenada con el piso de reserva")

# --- 6. La convergencia obligatoria hacia el fondo conservador ---
# Verificado contra el texto literal del Decreto 2555 de 2010, artículos
# 2.6.11.1.5 y 2.6.11.1.6, el 2026-09-18. Lo que se prueba aquí es que la tabla
# del código sea la tabla de la norma, incluido el corrimiento de dos años que
# mete el parágrafo 2 y que es lo más fácil de pasar por alto.
print("\n  la convergencia obligatoria por edad")

# La tabla tal como queda después del parágrafo 2: mujeres desde 52, hombres
# desde 57, y 20 puntos más cada año hasta el 100%.
TABLA_ESPERADA = [
    ("F", 51, 0.00), ("F", 52, 0.20), ("F", 53, 0.40), ("F", 54, 0.60),
    ("F", 55, 0.80), ("F", 56, 1.00), ("F", 70, 1.00),
    ("M", 56, 0.00), ("M", 57, 0.20), ("M", 58, 0.40), ("M", 59, 0.60),
    ("M", 60, 0.80), ("M", 61, 1.00), ("M", 75, 1.00),
]
for sexo_c, edad_c, esperado in TABLA_ESPERADA:
    obtenido = ds.mezcla_obligatoria(sexo_c, edad_c)["conservador"]
    revisar(abs(obtenido - esperado) < 1e-9,
            f"{sexo_c} de {edad_c} años: {esperado:.0%} en conservador por ley")

# El reparto del 2.6.11.1.5 entre mayor riesgo y moderado, para quien no eligió.
revisar(ds.mezcla_obligatoria("F", 41)["mayor_riesgo"] == 1.0,
        "mujer de 41: todavía toda en mayor riesgo")
revisar(abs(ds.mezcla_obligatoria("F", 42)["moderado"] - 0.20) < 1e-9,
        "mujer de 42: arranca el paso al moderado con 20%")
revisar(ds.mezcla_obligatoria("M", 46)["mayor_riesgo"] == 1.0,
        "hombre de 46: todavía todo en mayor riesgo (arranca a los 47)")
revisar(abs(ds.mezcla_obligatoria("M", 51)["moderado"] - 1.0) < 1e-9,
        "hombre de 51: ya todo el saldo libre en moderado")

# Las tres partes siempre suman uno: si no, el saldo se estaría perdiendo.
for sexo_c in ("F", "M"):
    for edad_c in range(30, 80):
        m = ds.mezcla_obligatoria(sexo_c, edad_c)
        suma = m["conservador"] + m["moderado"] + m["mayor_riesgo"]
        if abs(suma - 1.0) > 1e-9:
            revisar(False, f"{sexo_c} de {edad_c}: las partes suman {suma}, no 1")
            break
    else:
        revisar(True, f"sexo {sexo_c}: las tres partes suman 1 en todas las edades")

# Sin sexo o sin edad no se inventa una mezcla.
revisar(ds.mezcla_obligatoria(None, 60) is None, "sin sexo no se inventa la mezcla")
revisar(ds.mezcla_obligatoria("M", None) is None, "sin edad no se inventa la mezcla")

# Y lo que de verdad importa para el usuario: que no se le ofrezca un perfil
# que la ley ya no le permite.
_, prohibidos_viejo, _ = ds.perfiles_que_la_ley_le_permite("M", 63)
revisar(set(prohibidos_viejo) == {"moderado", "mayor_riesgo"},
        "a un hombre de 63 no se le ofrecen ni moderado ni mayor riesgo")
_, prohibidos_joven, _ = ds.perfiles_que_la_ley_le_permite("M", 35)
revisar(prohibidos_joven == [],
        "a un hombre de 35 no se le prohíbe ningún perfil")

# El rendimiento de la mezcla queda entre el del conservador y el del perfil
# más agresivo que todavía le quede: ni por encima ni por debajo de los dos.
tasa_mezcla = ds.rendimiento_de_la_mezcla("M", 58, ds.RENDIMIENTO_REAL_PROSPECTIVO)
revisar(ds.RENDIMIENTO_REAL_PROSPECTIVO["conservador"] <= tasa_mezcla
        <= ds.RENDIMIENTO_REAL_PROSPECTIVO["mayor_riesgo"],
        "el rendimiento de la mezcla queda dentro del rango de los perfiles")

# --- 7. Las tasas de rendimiento vienen del dato primario, no de prensa ---
# Cambiadas el 2026-09-18. Se fijan aquí porque mueven TODAS las proyecciones:
# si alguien las toca sin querer, esta prueba se pone roja y se da cuenta.
print("\n  las tasas de rendimiento observado")

ESPERADO_OBSERVADO = {
    "conservador": (0.0193, 0.0211),
    "moderado": (0.0227, 0.0325),
    "mayor_riesgo": (0.0331, 0.0413),
}
for perfil, rango in ESPERADO_OBSERVADO.items():
    revisar(ds.RENDIMIENTO_REAL_OBSERVADO[perfil] == rango,
            f"{perfil}: el rango observado es el del dato primario de la SFC")

revisar("hds9-4524" in ds.FUENTE_RENDIMIENTO and "ALTA" in ds.FUENTE_RENDIMIENTO,
        "la fuente dice de qué dataset sale y que la confianza es ALTA")

# El orden entre perfiles tiene que respetarse, en la evidencia y en el supuesto.
for serie, nombre in ((ds.RENDIMIENTO_REAL_OBSERVADO_CENTRAL, "observado"),
                      (ds.RENDIMIENTO_REAL_PROSPECTIVO, "prospectivo")):
    revisar(serie["conservador"] < serie["moderado"] < serie["mayor_riesgo"],
            f"{nombre}: conservador < moderado < mayor riesgo")

# Con el dato primario la contradicción desapareció. Si vuelve, hay que saberlo.
revisar(not ds.MODERADO_NO_SUPERA_A_CONSERVADOR,
        "con el dato primario el moderado ya le gana al conservador")

# Y el supuesto prospectivo quedó pegado a la evidencia: menos de medio punto
# de diferencia en cada perfil. Eso es lo que lo valida.
for perfil in ESPERADO_OBSERVADO:
    brecha = abs(ds.RENDIMIENTO_REAL_PROSPECTIVO[perfil]
                 - ds.RENDIMIENTO_REAL_OBSERVADO_CENTRAL[perfil])
    revisar(brecha < 0.005,
            f"{perfil}: el supuesto no se despega de la evidencia (brecha {brecha:.3%})")

# Los últimos 5 años se guardan aparte y NO los usa la proyección.
revisar(ds.RENDIMIENTO_REAL_ULTIMOS_5_ANIOS["moderado"][0] < 0,
        "el dato de 5 años conserva el moderado negativo, sin maquillar")
revisar(ds.RENDIMIENTO_REAL_PROSPECTIVO != ds.RENDIMIENTO_REAL_ULTIMOS_5_ANIOS,
        "la proyección no usa la ventana de 5 años")

# Y la serie anterior queda guardada, para poder reconstruir un diagnóstico viejo.
revisar(ds.RENDIMIENTO_REAL_OBSERVADO_ANTERIOR["moderado"] == (0.0197, 0.0315),
        "la serie de prensa queda archivada para reconstruir diagnósticos previos")

print()
if fallas:
    print(f"REGRESIÓN: {len(fallas)} FALLAS")
    sys.exit(1)
print("REGRESIÓN: TODO EN VERDE")
