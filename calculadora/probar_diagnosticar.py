# Prueba del orquestador contra el set dorado completo.
#
# Comprueba tres cosas, en este orden de importancia:
#   1. Que la salvaguarda FUNCIONE: un caso con la extracción dañada debe
#      detener el flujo y NO entregar diagnóstico (regla dura 4).
#   2. Que los 6 casos reales pasen la verificación y produzcan diagnóstico.
#   3. Que el orquestador dé exactamente los mismos números que llamar los
#      módulos a mano (no puede introducir diferencias).
#
# Uso: python3 probar_diagnosticar.py

import contextlib                # Para capturar lo que se imprime y revisarlo
import copy                      # Para dañar una copia del caso sin tocar el original
import io                        # El buffer donde se captura esa impresión
import json                      # Para leer los casos
import sys                       # Para terminar con código de salida 1 si algo falla
from datetime import date        # Fecha fija, para que la prueba no cambie con el tiempo
from pathlib import Path         # Rutas

import diagnosticar              # Lo que estamos probando
import rais                      # Para comparar contra la llamada directa
import caso_sintetico_historia_partida as sintetico  # Los dos documentos que se solapan

CASOS_DIR = Path(__file__).parent.parent / "casos"
# Fecha fija: si usáramos "hoy", el resultado cambiaría cada día y la prueba
# dejaría de ser comparable
FECHA = date(2026, 7, 21)

# Los casos que no traen sexo o edad en el documento necesitan que se los demos
DATOS_FALTANTES = {
    "caso-01-porvenir-rais": {"sexo": "M", "edad": 40},
    "caso-02-skandia-rais": {"sexo": "F", "edad": 35},
    "caso-03-proteccion-rais": {"sexo": "M", "edad": 26},
    "caso-04-colpensiones-rpm": {"sexo": "M", "edad": 59},
    "caso-05-colpensiones-rpm": {"sexo": "F", "edad": 48},
    "caso-06-colfondos-rais": {"sexo": "M", "edad": 45},
}

fallos = []


def pesos_texto(valor):
    """Misma forma en que el orquestador imprime pesos, para buscarla en el texto."""
    return diagnosticar.pesos(valor)

# ---------------------------------------------------------------------------
# Prueba 1: la salvaguarda. Es la más importante de todas.
# ---------------------------------------------------------------------------
print("PRUEBA 1: la verificación cruzada detiene una extracción dañada")

caso_bueno = json.loads(
    (CASOS_DIR / "caso-03-proteccion-rais.json").read_text(encoding="utf-8"))

# Dañamos la extracción a propósito: le borramos días a un periodo, como si la
# IA hubiera leído mal una fila de la tabla
caso_danado = copy.deepcopy(caso_bueno)
for p in caso_danado["periodos"]:
    if p.get("dias_cotizados"):
        p["dias_cotizados"] = max(0, p["dias_cotizados"] - 20)
        break

r = diagnosticar.diagnosticar(caso_danado, sexo="M", edad=26, fecha_calculo=FECHA)
if r["verificacion"]["cuadra"] or r["listo_para_entregar"]:
    fallos.append("La extracción dañada NO fue detectada: la salvaguarda falló")
    print("  FALLA: se entregó diagnóstico con datos malos")
else:
    print(f"  OK: detenido ({r['verificacion']['motivo']}), "
          f"diferencia de {r['verificacion']['diferencia']} semanas")

# Segundo negativo: un documento sin total impreso (el screenshot recortado)
caso_sin_total = copy.deepcopy(caso_bueno)
caso_sin_total["resumen_documento"]["total_semanas"] = None
r2 = diagnosticar.diagnosticar(caso_sin_total, sexo="M", edad=26, fecha_calculo=FECHA)
if r2["verificacion"]["cuadra"]:
    fallos.append("Un documento sin total impreso pasó la verificación")
    print("  FALLA: sin ancla de verificación, igual calculó")
else:
    print(f"  OK: detenido ({r2['verificacion']['motivo']}), pide documento completo")

# ---------------------------------------------------------------------------
# Prueba 2: los 6 casos reales del set dorado
# ---------------------------------------------------------------------------
print("\nPRUEBA 2: los 6 casos del set dorado corren de punta a punta")
print(f"{'Caso':<30} {'Verificación':<14} {'Módulo':<7} {'Listo':<6}")

for archivo in sorted(CASOS_DIR.glob("caso-*.json")):
    caso = json.loads(archivo.read_text(encoding="utf-8"))
    extra = DATOS_FALTANTES.get(archivo.stem, {})
    s = diagnosticar.diagnosticar(caso, fecha_calculo=FECHA, **extra)

    v = s["verificacion"]["motivo"]
    modulo = (s["router"] or {}).get("modulo") or "-"
    listo = "sí" if s["listo_para_entregar"] else "NO"
    print(f"{archivo.stem:<30} {v:<14} {modulo:<7} {listo:<6}")

    if not s["verificacion"]["cuadra"]:
        fallos.append(f"{archivo.stem}: no pasó la verificación cruzada")
    elif not s["listo_para_entregar"]:
        fallos.append(f"{archivo.stem}: no quedó listo para entregar")

# ---------------------------------------------------------------------------
# Prueba 3: el orquestador no cambia los números
# ---------------------------------------------------------------------------
print("\nPRUEBA 3: el orquestador da los mismos números que la llamada directa")

caso = json.loads(
    (CASOS_DIR / "caso-03-proteccion-rais.json").read_text(encoding="utf-8"))
directo = rais.diagnosticar(caso, sexo="M", edad=26, fecha_calculo=FECHA)
via_orq = diagnosticar.diagnosticar(caso, sexo="M", edad=26,
                                    fecha_calculo=FECHA)["diagnostico"]

if directo == via_orq:
    print("  OK: idénticos")
else:
    fallos.append("El orquestador produce números distintos a la llamada directa")
    print("  FALLA: hay diferencias entre ambas rutas")

# ---------------------------------------------------------------------------
# Prueba 4: historia partida (dos documentos de la misma persona)
# ---------------------------------------------------------------------------
# La trampa que buscamos: sumar los dos totales impresos da 450 semanas y la
# persona solo tiene 398,57. Las 51,43 de diferencia son los 12 meses que
# aparecen en los dos documentos. Toda la cuenta está comentada en
# caso_sintetico_historia_partida.py.
print("\nPRUEBA 4: dos historias laborales que se solapan en el tiempo")

hs = sintetico.historias()
r4 = diagnosticar.diagnosticar_historias(hs, fecha_calculo=FECHA)
cons = r4.get("consolidacion") or {}

# 4.1 Cada documento se verificó contra SU propio total impreso
verificaciones = r4.get("verificacion_por_documento") or []
if len(verificaciones) != 2 or not all(v["cuadra"] for v in verificaciones):
    fallos.append("Historia partida: no se verificó cada documento por separado")
    print("  FALLA: la verificación documento por documento no corrió bien")
else:
    print(f"  OK: los 2 documentos se verificaron por separado "
          f"({verificaciones[0]['total_impreso']} y "
          f"{verificaciones[1]['total_impreso']} semanas impresas)")

# 4.2 La suma ingenua daría de más: el consolidado tiene que ser menor
if cons.get("suma_ingenua_semanas") != sintetico.SUMA_INGENUA:
    fallos.append(f"Historia partida: la suma ingenua debería ser "
                  f"{sintetico.SUMA_INGENUA} y dio {cons.get('suma_ingenua_semanas')}")
if cons.get("semanas_consolidadas") != sintetico.SEMANAS_CONSOLIDADAS:
    fallos.append(f"Historia partida: el consolidado debería ser "
                  f"{sintetico.SEMANAS_CONSOLIDADAS} y dio "
                  f"{cons.get('semanas_consolidadas')}")
    print(f"  FALLA: consolidado {cons.get('semanas_consolidadas')}")
else:
    print(f"  OK: suma ingenua {cons['suma_ingenua_semanas']} -> consolidado "
          f"{cons['semanas_consolidadas']} (se descontaron "
          f"{cons['descuento_por_solapamiento']} semanas de traslape)")

if cons.get("descuento_por_solapamiento") != sintetico.SEMANAS_TRASLAPADAS:
    fallos.append(f"Historia partida: el descuento por traslape debería ser "
                  f"{sintetico.SEMANAS_TRASLAPADAS} y dio "
                  f"{cons.get('descuento_por_solapamiento')}")
if cons.get("meses_compartidos") != sintetico.MESES_COMPARTIDOS:
    fallos.append("Historia partida: no se identificaron los 12 meses que "
                  "aparecen en los dos documentos")

# 4.3 El régimen lo decide la afiliación vigente, no el documento con más semanas.
# Ojo: el documento de Colpensiones trae MÁS semanas (270 contra 180) y aun así
# el régimen que liquida es el RAIS, porque es donde cotiza hoy.
rv = r4.get("regimen_vigente") or {}
if rv.get("regimen") != "RAIS" or not rv.get("confiable"):
    fallos.append(f"Historia partida: el régimen debería ser RAIS por la "
                  f"afiliación vigente y dio {rv.get('regimen')}")
    print("  FALLA: el régimen no salió de la afiliación vigente")
else:
    print("  OK: liquida el RAIS (afiliación vigente), aunque Colpensiones "
          "tenga más semanas")

# 4.4 Lo que NO se puede resolver queda declarado, no escondido
alertas_rv = " ".join(rv.get("alertas", []))
if "bono_pensional_no_valorado" not in alertas_rv:
    fallos.append("Historia partida: no se declaró que el bono pensional no se valora")
if "semanas_exterior_no_resueltas" not in alertas_rv:
    fallos.append("Historia partida: no se declaró que las semanas del exterior "
                  "siguen abiertas")

# 4.5 El diagnóstico corrió sobre el consolidado, no sobre un documento suelto
diag = r4.get("diagnostico") or {}
if diag.get("semanas_hoy") != sintetico.SEMANAS_CONSOLIDADAS:
    fallos.append(f"Historia partida: el diagnóstico usó "
                  f"{diag.get('semanas_hoy')} semanas en vez del consolidado")
elif not r4.get("listo_para_entregar"):
    fallos.append("Historia partida: el consolidado no quedó listo para entregar")
else:
    print(f"  OK: el diagnóstico corrió sobre las {diag['semanas_hoy']} "
          f"semanas consolidadas")

# 4.6 La regla dura 4 NO se relaja: si UN documento no cuadra, no hay números
partida_danada = copy.deepcopy(hs)
for p in partida_danada[1]["periodos"]:
    if p.get("dias_cotizados"):
        p["dias_cotizados"] = max(0, p["dias_cotizados"] - 20)
        break
r5 = diagnosticar.diagnosticar_historias(partida_danada, fecha_calculo=FECHA)
cons5 = r5.get("consolidacion") or {}
if cons5.get("error") != "verificacion_fallida" or r5.get("listo_para_entregar"):
    fallos.append("Historia partida: un documento dañado NO detuvo el flujo")
    print("  FALLA: se consolidó con un documento que no cuadra")
elif cons5.get("documentos_que_fallaron") != [hs[1]["caso_id"]]:
    fallos.append("Historia partida: no se dijo cuál documento falló")
else:
    print(f"  OK: con un documento dañado se detiene y dice cuál "
          f"({cons5['documentos_que_fallaron'][0]})")

# 4.7 Con un solo documento, el flujo de siempre no cambia
uno = json.loads(
    (CASOS_DIR / "caso-03-proteccion-rais.json").read_text(encoding="utf-8"))
por_lista = diagnosticar.diagnosticar_historias([uno], sexo="M", edad=26,
                                                fecha_calculo=FECHA)
directo_uno = diagnosticar.diagnosticar(uno, sexo="M", edad=26, fecha_calculo=FECHA)
if por_lista != directo_uno:
    fallos.append("Con una sola historia, la ruta nueva cambia el resultado")
    print("  FALLA: la ruta de varias historias alteró el caso de un documento")
else:
    print("  OK: con un solo documento el resultado es idéntico al de siempre")

# ---------------------------------------------------------------------------
# Prueba 5: la banda del factor llega hasta la salida que ve el usuario
# ---------------------------------------------------------------------------
# El bug que esta prueba impide que vuelva: `rais.py` calculaba los dos
# extremos y `diagnosticar.py` imprimía solo el optimista, así que el usuario
# veía el MEJOR caso presentado como si fuera la estimación.
#
# Qué se fija aquí y qué no: se fijan las INVARIANTES (que la banda existe, que
# viene ordenada, que la declaración de fuentes viaja con ella, que el texto
# impreso trae los dos extremos). NO se fijan cifras del set dorado, porque el
# factor y los rendimientos se están recalibrando y una prueba atada a esas
# cifras se rompería en cada ajuste sin que nada estuviera mal.
print("\nPRUEBA 5: la banda del factor llega a la salida, no se queda en el diccionario")

CASOS_RAIS = ("caso-01-porvenir-rais", "caso-02-skandia-rais",
              "caso-03-proteccion-rais", "caso-06-colfondos-rais")

for nombre in CASOS_RAIS:
    caso = json.loads((CASOS_DIR / f"{nombre}.json").read_text(encoding="utf-8"))
    s = diagnosticar.diagnosticar(caso, fecha_calculo=FECHA,
                                  **DATOS_FALTANTES[nombre])
    b = s.get("banda")
    if not b:
        fallos.append(f"{nombre}: la salida no trae la banda del factor")
        print(f"  FALLA: {nombre} sin banda")
        continue
    # La banda siempre de menor a mayor: mostrarla al revés sería peor que no
    # mostrarla, porque el usuario leería el conservador como su techo
    desordenadas = [p for p, f in b["perfiles"].items() if f["banda"][0] > f["banda"][1]]
    if desordenadas:
        fallos.append(f"{nombre}: banda al revés en {desordenadas}")
    # La declaración de dónde sale cada extremo viaja pegada a las cifras
    dec = b["declaracion"]["extremos"]
    for extremo in ("optimista", "conservador"):
        if not dec[extremo].get("fuente") or not dec[extremo].get("confianza"):
            fallos.append(f"{nombre}: al extremo {extremo} le falta fuente o confianza")
    print(f"  OK: {nombre} trae banda en {len(b['perfiles'])} escenarios "
          f"(veredicto en disputa: "
          f"{b['escenarios_con_veredicto_en_disputa'] or 'ninguno'})")

# Cada extremo declara SU fuente y SU nivel de confianza, sea cual sea ese
# nivel. Es la regla dura 3 de la sesión: todo dato lleva fuente y confianza.
#
# Historia de esta comprobación, que explica por qué está escrita así: hasta el
# 2026-07-28 fijaba que el extremo conservador declarara confianza BAJA, porque
# su ancla era prensa. Ese día el ancla pasó a fuente primaria (vector de Tasa
# de Mercado de Referencia de la Superfinanciera, Carta Circular 038 del 8 de
# julio de 2026) y la confianza subió, así que la prueba se puso roja PORQUE EL
# PROYECTO MEJORÓ. Una prueba que castiga la mejora de una fuente termina
# desincentivándola. Lo que se vigila ahora es que la declaración EXISTA y
# LLEGUE al usuario, no qué nivel tiene: el nivel es un dato que debe poder
# subir y bajar cuando la evidencia cambie.
caso = json.loads(
    (CASOS_DIR / "caso-01-porvenir-rais.json").read_text(encoding="utf-8"))
s1 = diagnosticar.diagnosticar(caso, fecha_calculo=FECHA,
                               **DATOS_FALTANTES["caso-01-porvenir-rais"])
extremos_declarados = s1["banda"]["declaracion"]["extremos"]
for extremo, ficha in extremos_declarados.items():
    if not (ficha.get("fuente") or "").strip():
        fallos.append(f"El extremo {extremo} no declara fuente")
    if not (ficha.get("confianza") or "").strip():
        fallos.append(f"El extremo {extremo} no declara nivel de confianza")
if not [f for f in fallos if "no declara" in f]:
    print("  OK: los dos extremos declaran fuente y nivel de confianza "
          f"(conservador: {extremos_declarados['conservador']['confianza'].split('.')[0]})")

# En RPM no hay banda: la fórmula es determinista y va en tabla de escenarios
caso_rpm = json.loads(
    (CASOS_DIR / "caso-04-colpensiones-rpm.json").read_text(encoding="utf-8"))
s_rpm = diagnosticar.diagnosticar(caso_rpm, fecha_calculo=FECHA,
                                  **DATOS_FALTANTES["caso-04-colpensiones-rpm"])
if s_rpm.get("banda") is not None:
    fallos.append("El RPM no debería traer banda: su fórmula es determinista")
else:
    print("  OK: el RPM no trae banda (excepción 1 bis del system-prompt)")

# Y lo que de verdad importa: que el TEXTO que se imprime traiga el rango y la
# declaración. La banda dentro del diccionario no le sirve de nada al usuario.
texto = io.StringIO()
with contextlib.redirect_stdout(texto):
    diagnosticar.imprimir(s1)
impreso = texto.getvalue()
moderado = s1["banda"]["perfiles"]["moderado"]
conservador = extremos_declarados["conservador"]
faltantes = [t for t in (pesos_texto(moderado["banda"][0]),
                         pesos_texto(moderado["banda"][1]),
                         "confianza", "rango, no cifra única",
                         # La fuente y la confianza se imprimen TAL CUAL vienen
                         # del diagnóstico, sin parafrasear: si el agente A
                         # cambia el texto de la declaración, el usuario ve el
                         # texto nuevo sin que haya que tocar nada aquí
                         conservador["fuente"][:40],
                         conservador["confianza"][:20])
             if t not in impreso]
if faltantes:
    fallos.append(f"La salida impresa no muestra la banda completa: falta {faltantes}")
    print(f"  FALLA: al texto impreso le falta {faltantes}")
else:
    print("  OK: el texto impreso trae los dos extremos y su declaración")

# El caso crítico: cuando los dos extremos caen en salidas distintas del RAIS,
# la banda cambia el VEREDICTO. Se prueba con un diagnóstico armado a mano para
# que no dependa de las cifras que se están recalibrando.
diag_sintetico = {
    "escenarios": {"moderado": {
        "mesada": 2000000, "mesada_conservadora": 1750905,
        "mesada_banda": (1750905, 2000000),
        "salida": "pension_por_capital",
        "salida_conservadora": "garantia_pension_minima"}},
    "edad_pension_anticipada_banda": (55, None),
    "capital_umbral_110_pct": {"optimista": 354474375, "conservador": 590700000},
    "banda_factor": rais.declaracion_banda(21.3, "M", 2040),
}
b_sin = diagnosticar.resumen_banda(diag_sintetico)
if not b_sin["hay_cambio_de_veredicto"]:
    fallos.append("Dos salidas distintas del RAIS no se marcaron como cambio "
                  "de veredicto")
    print("  FALLA: el cambio de veredicto no se detectó")
else:
    texto2 = io.StringIO()
    with contextlib.redirect_stdout(texto2):
        diagnosticar.imprimir_banda(b_sin)
    impreso2 = texto2.getvalue()
    if "CAMBIA EL VEREDICTO" not in impreso2:
        fallos.append("El cambio de veredicto no se comunica en la salida impresa")
    elif "desaparece en el otro" not in impreso2:
        fallos.append("No se dijo que la pensión anticipada existe en un extremo "
                      "y desaparece en el otro")
    else:
        print("  OK: salidas distintas se comunican como cambio de veredicto, "
              "no como dos cifras")

# ---------------------------------------------------------------------------
print()
if fallos:
    print("RESULTADO: HAY FALLOS")
    for f in fallos:
        print(f"  - {f}")
    # Código de salida 1: así el fallo se ve desde la terminal y desde
    # cualquier script que corra las pruebas, sin leer el texto
    sys.exit(1)
else:
    print("RESULTADO: TODO EN VERDE. El orquestador está sano.")
