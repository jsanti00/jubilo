# Prueba del módulo de aportes voluntarios.
# Uso: python3 probar_aportes_voluntarios.py   (termina en 1 si algo falla)
#
# Filosofía de esta prueba, aprendida del bug del IBL: no basta con verificar
# que el flujo CORRE. Cada bloque de aquí compara contra un número calculado a
# mano desde la norma, o contra una propiedad que el módulo no puede violar
# (por ejemplo, que en RPM no salga ninguna cifra).

import sys

import aportes_voluntarios as av
from datos_sistema import (
    SMLMV, RENDIMIENTO_REAL, RENDIMIENTO_REAL_OBSERVADO_CENTRAL,
    EXPOSICION_RENTA_VARIABLE, PRIMA_RENTA_VARIABLE_LARGO_PLAZO,
)

SMLMV_2026 = SMLMV[2026]       # $1.750.905
UVT_2026 = av.UVT[2026]        # $52.374

fallas = []


def revisar(condicion, descripcion):
    print(f"  {'OK  ' if condicion else 'FALLA'}  {descripcion}")
    if not condicion:
        fallas.append(descripcion)


def cerca(obtenido, esperado, tolerancia, descripcion):
    """Compara con tolerancia explícita y muestra la diferencia si falla."""
    ok = obtenido is not None and abs(obtenido - esperado) <= tolerancia
    revisar(ok, f"{descripcion}: esperado {esperado}, obtenido {obtenido}")


# ---------------------------------------------------------------------------
# 1. RPM: EL MÓDULO SE NIEGA, NO DEVUELVE UN NÚMERO
#    Es la prueba más importante del archivo. Estimar un aporte voluntario en
#    Colpensiones sería inventarse un producto que no existe.
# ---------------------------------------------------------------------------

print("=" * 78)
print("1. RPM: negativa explícita, cero cifras")
print("=" * 78)
print()

rpm = av.evaluar_aporte_voluntario("RPM", meses=120, aporte_mensual=500_000,
                                   aporte_unico=20_000_000,
                                   ingreso_anual=180_000_000)

revisar(rpm["aplica"] is False, "en RPM la evaluación no aplica")
revisar("proyeccion" not in rpm, "en RPM no hay proyección de capital")
revisar("beneficio_tributario_primer_anio" not in rpm,
        "en RPM no hay estimación de beneficio tributario")

# Ningún valor numérico puede salir de la negativa: si sale, alguien metió una
# cifra donde el corpus dice que no existe el vehículo.
numeros = [k for k, v in rpm.items() if isinstance(v, (int, float))
           and not isinstance(v, bool)]
revisar(not numeros, f"la respuesta de RPM no trae ninguna cifra (trajo {numeros})")

revisar("no existe" in rpm["que_decir"].lower(),
        "la frase para el usuario dice que el vehículo no existe")
revisar(len(rpm["palancas_que_si_existen"]) == 2,
        "remite a las dos palancas del RPM: subir el IBC y sumar semanas")

# Minúsculas, mayúsculas y espacios no deben abrir una puerta trasera
for variante in ("rpm", " RPM ", "Rpm", "colpensiones", None, ""):
    r = av.evaluar_aporte_voluntario(variante, meses=60, aporte_mensual=100_000)
    revisar(r["aplica"] is False,
            f"régimen {variante!r} tampoco produce una estimación")

print()

# ---------------------------------------------------------------------------
# 2. IMPUESTO DE RENTA, ART. 241, CALCULADO A MANO
#    La tabla se aplica en UVT; estos tres puntos se verificaron con lápiz.
# ---------------------------------------------------------------------------

print("=" * 78)
print("2. Tabla del art. 241 (cifras calculadas a mano)")
print("=" * 78)
print()

# 1.000 UVT: está dentro del primer rango (hasta 1.090), tarifa 0%
cerca(av.impuesto_renta(1_000 * UVT_2026, 2026), 0, 1,
      "1.000 UVT de base gravable no pagan impuesto")

# 1.500 UVT: (1.500 - 1.090) x 19% = 77,9 UVT
cerca(av.impuesto_renta(1_500 * UVT_2026, 2026), round(77.9 * UVT_2026), 1,
      "1.500 UVT: (1.500-1.090) x 19% = 77,9 UVT")

# 2.000 UVT: (2.000 - 1.700) x 28% + 116 UVT = 84 + 116 = 200 UVT
cerca(av.impuesto_renta(2_000 * UVT_2026, 2026), 200 * UVT_2026, 1,
      "2.000 UVT: (2.000-1.700) x 28% + 116 = 200 UVT")

# 10.000 UVT: (10.000 - 8.670) x 35% + 2.296 UVT = 465,5 + 2.296 = 2.761,5 UVT
cerca(av.impuesto_renta(10_000 * UVT_2026, 2026), round(2_761.5 * UVT_2026), 1,
      "10.000 UVT: (10.000-8.670) x 35% + 2.296 = 2.761,5 UVT")

# La tarifa marginal se lee del mismo lugar que el impuesto
revisar(av.tarifa_marginal(2_000 * UVT_2026, 2026) == 0.28,
        "la tarifa marginal de 2.000 UVT es 28%")

print()

# ---------------------------------------------------------------------------
# 3. LOS DOS DESTINOS TIENEN LÍMITES DISTINTOS
#    Confundirlos es el error más caro de esta materia.
# ---------------------------------------------------------------------------

print("=" * 78)
print("3. Cupo del beneficio: art. 55 contra art. 126-1 con techo del art. 336")
print("=" * 78)
print()

# Destino obligatoria (ET art. 55): el menor entre 25% del ingreso y 2.500 UVT.
# Con ingreso de 180.000.000, el 25% son 45.000.000 y 2.500 UVT son
# 130.935.000: muerde el porcentaje.
c = av.cupo_beneficio_tributario(180_000_000, "obligatoria", 2026)
cerca(c["limite_del_anio"], 45_000_000, 1,
      "art. 55 con ingreso de 180.000.000: 25% = 45.000.000")
revisar(c["tope_que_muerde"] == "25% del ingreso",
        "y el tope que muerde es el porcentaje, no las UVT")

# Con ingreso de 800.000.000 el 25% son 200.000.000 y muerde el tope en UVT
c = av.cupo_beneficio_tributario(800_000_000, "obligatoria", 2026)
cerca(c["limite_del_anio"], 2_500 * UVT_2026, 1,
      "art. 55 con ingreso alto: muerde el tope de 2.500 UVT")

# Destino voluntaria (ET art. 126-1) con ingreso de 180.000.000:
# 30% = 54.000.000; 3.800 UVT = 199.021.200; techo del art. 336 = el menor
# entre 40% (72.000.000) y 1.340 UVT (70.181.160) = 70.181.160.
# El cupo es el menor de todos: 54.000.000.
c = av.cupo_beneficio_tributario(180_000_000, "voluntaria", 2026)
cerca(c["limite_del_anio"], 54_000_000, 1,
      "art. 126-1 con ingreso de 180.000.000: 30% = 54.000.000")
cerca(c["topes"]["techo_global_art_336"], 1_340 * UVT_2026, 1,
      "el techo del art. 336 son 1.340 UVT (muerde antes que el 40%)")

# Con ingreso de 400.000.000 el que muerde ya es el techo global del art. 336:
# 30% = 120.000.000, pero 1.340 UVT = 70.181.160.
c = av.cupo_beneficio_tributario(400_000_000, "voluntaria", 2026)
cerca(c["limite_del_anio"], 1_340 * UVT_2026, 1,
      "con ingreso de 400.000.000 muerde el techo de 1.340 UVT")
revisar("336" in c["tope_que_muerde"],
        "y el módulo declara que el que muerde es el art. 336")

# El art. 55 NO pasa por el techo del art. 336: es ingreso no constitutivo de
# renta, no renta exenta. Con el mismo ingreso alto los dos cupos difieren.
c55 = av.cupo_beneficio_tributario(400_000_000, "obligatoria", 2026)
revisar(c55["limite_del_anio"] > 1_340 * UVT_2026,
        "el cupo del art. 55 supera el techo del art. 336 (no le aplica)")

# Lo ya aportado en el año consume cupo (el de 3.800 UVT es compartido con AFC)
c = av.cupo_beneficio_tributario(180_000_000, "voluntaria", 2026,
                                 aportes_previos_del_anio=20_000_000)
cerca(c["cupo_disponible"], 34_000_000, 1,
      "20.000.000 ya aportados en el año dejan 34.000.000 de cupo")

print()

# ---------------------------------------------------------------------------
# 4. AHORRO EN IMPUESTOS Y CUPO SATURADO
# ---------------------------------------------------------------------------

print("=" * 78)
print("4. Ahorro tributario (cifras calculadas a mano)")
print("=" * 78)
print()

# Ingreso 180.000.000 = 3.436,8 UVT, dentro del rango del 28%. Un aporte de
# 6.000.000 cabe entero en el cupo y no cruza de rango, así que el ahorro es
# exactamente el 28% del aporte: 1.680.000.
b = av.ahorro_tributario(180_000_000, 6_000_000, "obligatoria", 2026)
cerca(b["ahorro_en_impuestos"], 1_680_000, 1,
      "aporte de 6.000.000 al 28% marginal ahorra 1.680.000")
cerca(b["aporte_con_beneficio"], 6_000_000, 1, "el aporte cabe entero en el cupo")
cerca(b["aporte_sin_beneficio"], 0, 1, "no hay excedente sin beneficio")

# Cupo saturado: con ingreso de 100.000.000 el cupo del art. 55 es 25.000.000.
# Un aporte de 40.000.000 deja 15.000.000 SIN beneficio alguno.
b = av.ahorro_tributario(100_000_000, 40_000_000, "obligatoria", 2026)
cerca(b["aporte_con_beneficio"], 25_000_000, 1,
      "cupo del art. 55 con ingreso de 100.000.000: 25.000.000")
cerca(b["aporte_sin_beneficio"], 15_000_000, 1,
      "los 15.000.000 que se pasan del cupo no ahorran nada")
revisar(b["ahorro_por_peso_aportado"] < 0.28,
        "el ahorro por peso aportado cae cuando el cupo se satura")

# Aportar por encima del cupo NO aumenta el ahorro: es la sorpresa más común
b1 = av.ahorro_tributario(100_000_000, 25_000_000, "obligatoria", 2026)
b2 = av.ahorro_tributario(100_000_000, 60_000_000, "obligatoria", 2026)
revisar(b1["ahorro_en_impuestos"] == b2["ahorro_en_impuestos"],
        "pasarse del cupo no aumenta ni un peso el ahorro en impuestos")

# Toda recomendación de aporte viaja con sus condiciones de permanencia
revisar(b["condiciones"]["retencion_al_retiro"] == 0.35,
        "el destino obligatoria advierte la retención del 35% del art. 55")
cv = av.condiciones_de_permanencia("voluntaria")
revisar(cv["permanencia_minima"].startswith("10"),
        "el destino voluntaria advierte los 10 años del art. 126-1")

print()

# ---------------------------------------------------------------------------
# 5. COMISIÓN DE ADMINISTRACIÓN DE LA AFP
# ---------------------------------------------------------------------------

print("=" * 78)
print("5. Comisión de administración sobre el saldo voluntario")
print("=" * 78)
print()

# Tabla escalonada de Porvenir, leída de su propia página
revisar(av.comision_administracion_anual(3 * SMLMV_2026, "porvenir",
                                         SMLMV_2026)["pct_anual"] == 0.0390,
        "Porvenir: saldo de 3 SMLMV paga 3,90%")
revisar(av.comision_administracion_anual(10 * SMLMV_2026, "porvenir",
                                         SMLMV_2026)["pct_anual"] == 0.0350,
        "Porvenir: saldo de 10 SMLMV paga 3,50%")
revisar(av.comision_administracion_anual(2_000 * SMLMV_2026, "porvenir",
                                         SMLMV_2026)["pct_anual"] == 0.0075,
        "Porvenir: saldo por encima de 1.280 SMLMV paga 0,75%")

# La comisión baja al subir el saldo, en todos los tramos y sin saltos al alza
anterior = 1.0
for tope, _ in av.COMISION_VOLUNTARIO_PORVENIR:
    pct = av.comision_administracion_anual(
        tope * SMLMV_2026, "porvenir", SMLMV_2026)["pct_anual"]
    revisar(pct <= anterior, f"la comisión no sube al pasar los {tope} SMLMV")
    anterior = pct

# Sin AFC conocida se usa un supuesto Y SE MARCA como tal
sin_afp = av.comision_administracion_anual(50_000_000, None, SMLMV_2026)
revisar(sin_afp["es_supuesto"] is True,
        "sin AFP conocida la comisión se marca como supuesto")
revisar("SUPUESTO" in sin_afp["fuente"],
        "y la fuente dice que es un supuesto, no un dato de la AFP")

# Con AFP conocida no se marca como supuesto
con_afp = av.comision_administracion_anual(50_000_000, "porvenir", SMLMV_2026)
revisar(con_afp["es_supuesto"] is False,
        "con AFP conocida la comisión no es supuesto")

print()

# ---------------------------------------------------------------------------
# 6. PROYECCIÓN DEL CAPITAL, NETA DE COMISIÓN
# ---------------------------------------------------------------------------

print("=" * 78)
print("6. Proyección del saldo voluntario")
print("=" * 78)
print()

# Caso a mano: 10.000.000 de aporte único, 12 meses, rendimiento cero y
# comisión plana del 2% de Protección. Al cabo de un año el saldo debe ser
# exactamente 10.000.000 x 0,98 = 9.800.000.
p = av.proyectar_aporte_voluntario(12, aporte_unico=10_000_000,
                                   afp="proteccion", smlmv=SMLMV_2026,
                                   rendimiento_real=0.0)
cerca(p["capital_final"], 9_800_000, 1,
      "12 meses al 2% de comisión y 0% de rendimiento dejan 9.800.000")
cerca(p["capital_final_sin_comision"], 10_000_000, 1,
      "sin comisión el saldo se habría quedado en 10.000.000")
cerca(p["comision_pagada"], 200_000, 1, "la comisión del año fue 200.000")

# Sin horizonte no pasa nada: el aporte único sigue intacto
p = av.proyectar_aporte_voluntario(0, aporte_unico=5_000_000, afp="porvenir",
                                   smlmv=SMLMV_2026)
cerca(p["capital_final"], 5_000_000, 1, "con 0 meses el capital no se mueve")

# Propiedades que el modelo no puede violar
p = av.proyectar_aporte_voluntario(120, perfil="moderado",
                                   aporte_mensual=500_000, afp="porvenir",
                                   smlmv=SMLMV_2026)
revisar(p["capital_final"] < p["capital_final_sin_comision"],
        "la comisión siempre deja menos capital del que habría sin ella")
revisar(p["capital_final"] + p["comision_pagada"]
        <= p["capital_final_sin_comision"] + 1,
        "lo cobrado más lo que queda no puede superar el saldo sin comisión")
cerca(p["total_aportado"], 60_000_000, 1,
      "120 aportes de 500.000 son 60.000.000 salidos del bolsillo")

# AQUÍ VIVÍA la aserción "el capital ordena conservador < moderado < mayor
# riesgo". SE ELIMINÓ el 2026-07-27, y no por conveniencia: con la serie real
# de la Superfinanciera el punto central del moderado (2,56%) queda por debajo
# del conservador (2,61%), así que en el periodo medido el fondo moderado NO le
# ganó al conservador. Esa aserción no verificaba el modelo: congelaba el
# supuesto de que a más riesgo va más rendimiento, que los datos desmienten.
# Una prueba que fija un supuesto falso lo blinda contra la evidencia, que es
# justo cómo el bug del IBL sobrevivió a cinco pruebas.
#
# En su lugar quedan las dos propiedades que sí son del modelo y que sí hay que
# defender.

# 1. Más rendimiento, más capital. Esto es aritmética de la proyección y debe
#    cumplirse siempre, sin importar qué perfil rinda más en el mundo real.
bajo = av.proyectar_aporte_voluntario(120, aporte_mensual=500_000,
                                      afp="porvenir", smlmv=SMLMV_2026,
                                      rendimiento_real=0.01)
alto = av.proyectar_aporte_voluntario(120, aporte_mensual=500_000,
                                      afp="porvenir", smlmv=SMLMV_2026,
                                      rendimiento_real=0.05)
revisar(bajo["capital_final"] < alto["capital_final"],
        "a mayor tasa de rendimiento, mayor capital final (propiedad del modelo)")

# 2. El capital ordena los perfiles IGUAL que sus rendimientos supuestos,
#    cualquiera que sea ese orden. Detecta un error de proyección sin decidir
#    de antemano cuál perfil rinde más: el orden lo ponen los datos, no la
#    prueba. Hoy ese orden es moderado < conservador < mayor riesgo.
capitales = {
    perfil: av.proyectar_aporte_voluntario(120, perfil, aporte_mensual=500_000,
                                           afp="porvenir",
                                           smlmv=SMLMV_2026)["capital_final"]
    for perfil in av.RENDIMIENTO_REAL_OBSERVADO
}
por_rendimiento = sorted(capitales, key=lambda x: RENDIMIENTO_REAL[x])
por_capital = sorted(capitales, key=lambda x: capitales[x])
revisar(por_rendimiento == por_capital,
        "los perfiles ordenan por capital igual que por rendimiento supuesto "
        f"(hoy: {' < '.join(por_capital)})")


# La salida trae el rango OBSERVADO y el central PROSPECTIVO, etiquetados
r = av.proyectar_aporte_voluntario_en_rango(120, "moderado",
                                            aporte_mensual=500_000,
                                            afp="porvenir", smlmv=SMLMV_2026)
revisar(r["capital_piso"] < r["capital_techo"],
        "el rango observado produce un piso y un techo de capital")
revisar(r["rendimiento_piso"] == 0.0197 and r["rendimiento_techo"] == 0.0315,
        "el rango observado del moderado es 1,97% a 3,15% (SFC, 2011 a 2024)")
revisar("Power BI" in r["fuente_del_rango"],
        "el rango declara por qué no se verificó en el dato crudo de la SFC")
# El central prospectivo del moderado (3,49%) supera el techo observado, así
# que su capital queda POR ENCIMA del techo del rango. No es un error: son dos
# cifras que responden preguntas distintas.
revisar(r["capital_central"] > r["capital_techo"],
        "el capital del supuesto prospectivo supera el del techo observado")

# VIGILANCIA DE LAS DOS CONSTANTES, separadas a propósito (2026-07-27).
# Desde que la proyección usa un supuesto PROSPECTIVO, hay dos cosas distintas
# que vigilar y una sola aserción no puede cubrir las dos. Se vigilan ambas, y
# cada aserción nombra la constante que mira: mezclarlas es de donde nació la
# confusión que costó una vuelta entera.
#
# (a) LA EVIDENCIA. Que nadie maquille el dato observado.
for perfil, (piso, techo) in av.RENDIMIENTO_REAL_OBSERVADO.items():
    cerca(RENDIMIENTO_REAL_OBSERVADO_CENTRAL[perfil], (piso + techo) / 2, 1e-6,
          f"el central OBSERVADO de {perfil} es el medio de su rango observado")

# La evidencia NO es monótona, y eso se conserva escrito. Si un día alguien
# "arregla" el dato para que el moderado le gane al conservador, esta aserción
# lo caza: sería cambiar la evidencia para que se parezca al supuesto.
revisar(RENDIMIENTO_REAL_OBSERVADO_CENTRAL["moderado"]
        < RENDIMIENTO_REAL_OBSERVADO_CENTRAL["conservador"],
        "la evidencia sigue diciendo que el moderado observado rindió menos "
        "que el conservador (no se maquilla para que ordene bonito)")

# (b) LO QUE USA LA PROYECCIÓN. Que salga de la fórmula, no de un número
#     escrito a mano. Se reconstruye aquí de forma independiente: ancla del
#     conservador más exposición ADICIONAL a renta variable por la prima.
for perfil, exposicion in EXPOSICION_RENTA_VARIABLE.items():
    esperado = (RENDIMIENTO_REAL_OBSERVADO_CENTRAL["conservador"]
                + (exposicion - EXPOSICION_RENTA_VARIABLE["conservador"])
                * PRIMA_RENTA_VARIABLE_LARGO_PLAZO)
    cerca(RENDIMIENTO_REAL[perfil], esperado, 1e-6,
          f"el supuesto PROSPECTIVO de {perfil} lo reproduce su fórmula "
          "(ancla del conservador más prima por exposición adicional)")

# El conservador queda anclado en su propio observado: es el puente entre las
# dos constantes y lo que impide que el supuesto flote libre del dato.
cerca(RENDIMIENTO_REAL["conservador"],
      RENDIMIENTO_REAL_OBSERVADO_CENTRAL["conservador"], 1e-6,
      "el prospectivo del conservador sigue anclado en su observado")

# Que el prospectivo se salga del rango observado es DECISIÓN, no descalibrado.
# Se deja fijado para que quede claro que la prueba lo sabe y lo acepta.
fuera = [p for p, (piso, techo) in av.RENDIMIENTO_REAL_OBSERVADO.items()
         if not (piso <= RENDIMIENTO_REAL[p] <= techo)]
revisar(set(fuera) == {"moderado", "mayor_riesgo"},
        "el prospectivo sale por encima del rango observado solo en moderado y "
        f"mayor riesgo, por decisión de producto (hoy: {sorted(fuera)})")

# Y el módulo consume las constantes de datos_sistema, no copias propias
from datos_sistema import RENDIMIENTO_REAL_OBSERVADO as OBSERVADO_ORIGEN
revisar(av.RENDIMIENTO_REAL_OBSERVADO is OBSERVADO_ORIGEN,
        "el módulo usa el rango observado de datos_sistema, no una copia suya")

# La salida distingue dato de supuesto: es la regla que el agente le repite al
# usuario y tiene que estar en la estructura, no solo en el texto.
revisar(r["naturaleza_del_rango"].startswith("DATO"),
        "el rango observado sale etiquetado como DATO")
revisar(r["naturaleza_del_central"].startswith("SUPUESTO"),
        "el central prospectivo sale etiquetado como SUPUESTO")
revisar(r["central_fuera_del_rango_observado"] is True,
        "y la salida avisa que el central del moderado queda fuera del "
        "rango observado")

print()

# ---------------------------------------------------------------------------
# 7. LA MESADA NO SE CALCULA AQUÍ, Y LA BANDA CONSERVA SU ORDEN
# ---------------------------------------------------------------------------

print("=" * 78)
print("7. Conversión a mesada: el factor viene de rais.py")
print("=" * 78)
print()

revisar(not hasattr(av, "factor_conversion"),
        "el módulo no define su propio factor de conversión (lo posee rais.py)")

banda = av.mesada_adicional_en_banda(100_000_000,
                                     {"optimista": 182, "conservador": 268})
revisar(banda["mesada_optimista"] > banda["mesada_conservadora"],
        "el extremo optimista de la mesada sale del factor más bajo")
cerca(round(banda["mesada_conservadora"]), round(100_000_000 / 268), 1,
      "la mesada conservadora es el capital sobre el factor más alto")

revisar(av.mesada_adicional(100_000_000, 0) is None,
        "sin factor válido no se inventa una mesada")

print()

# ---------------------------------------------------------------------------
# 8. DECISIÓN 7: SE COMPARAN ALTERNATIVAS PENSIONALES, NADA MÁS
# ---------------------------------------------------------------------------

print("=" * 78)
print("8. Frontera de alcance y accionabilidad de las palancas")
print("=" * 78)
print()

t = av.comparar_alternativas_pensionales("RAIS", tiene_capacidad_de_pago=True)
etiquetas = " ".join(a["alternativa"] for a in t["alternativas"]).lower()
for prohibida in ("invertir", "acciones", "cdt", "finca raíz", "portafolio"):
    revisar(prohibida not in etiquetas,
            f"ninguna alternativa es '{prohibida}' (fuera del alcance)")
revisar("regulada" in t["frontera"],
        "la tabla trae la frase de frontera sobre asesoría de inversión")

# BEPS a alguien con capacidad de pago es un error de segmento
beps = next(a for a in t["alternativas"] if a["alternativa"] == "BEPS")
revisar(beps["disponible"] is False, "con capacidad de pago, BEPS no se ofrece")
revisar("SEGMENTO" in beps["motivo"], "y se dice que sería un error de segmento")

# Sin capacidad de pago no se ofrece ninguna palanca que cueste plata
sin_plata = av.comparar_alternativas_pensionales("RAIS",
                                                 tiene_capacidad_de_pago=False)
ofrecidas = [a["alternativa"] for a in sin_plata["disponibles"]]
revisar("aporte voluntario a la cuenta obligatoria (RAIS)" not in ofrecidas,
        "sin excedente no se ofrece aportar voluntariamente")
revisar("cotizar sobre una base más alta (sobrecotizar)" not in ofrecidas,
        "sin excedente no se ofrece sobrecotizar")

# Sobrecotizar solo se ofrece a quien puede mover su base y tiene con qué
t = av.comparar_alternativas_pensionales("RPM", tiene_capacidad_de_pago=True,
                                         es_independiente=True,
                                         ingreso_respalda_ibc_mayor=True)
sobre = next(a for a in t["alternativas"]
             if a["alternativa"].startswith("cotizar sobre"))
revisar(sobre["disponible"] is True,
        "al independiente con ingreso que lo respalde sí se le ofrece")
revisar("abogado" in sobre["advertencia"],
        "y viaja con la advertencia de zona gris que deriva a abogado")

# En RPM el aporte voluntario nunca aparece como disponible
rpm_alt = av.comparar_alternativas_pensionales("RPM", tiene_capacidad_de_pago=True)
revisar(all("cuenta obligatoria (RAIS)" not in a["alternativa"]
            for a in rpm_alt["disponibles"]),
        "en RPM el aporte voluntario nunca queda como disponible")

print()

# ---------------------------------------------------------------------------
# 9. EL MÓDULO NO SUPONE LO QUE NO SABE
# ---------------------------------------------------------------------------

print("=" * 78)
print("9. Datos faltantes: se declaran, no se inventan")
print("=" * 78)
print()

sin_ingreso = av.evaluar_aporte_voluntario("RAIS", meses=60,
                                           aporte_mensual=300_000,
                                           afp="porvenir")
revisar(sin_ingreso["beneficio_tributario_primer_anio"] is None,
        "sin ingreso anual no se estima el beneficio tributario")
revisar(sin_ingreso["falta_dato"] is not None,
        "y se dice cuál es el dato que falta")
revisar(sin_ingreso["proyeccion"]["capital_final"] > 0,
        "pero el capital sí se proyecta: ese no depende del ingreso")

# Toda salida viaja con sus supuestos, incluida la negativa del RPM
revisar(len(sin_ingreso["supuestos"]) >= 5, "la salida trae sus supuestos")
revisar(len(rpm["supuestos"]) >= 5, "la negativa del RPM también los trae")

# El reparto del 16% no se contradice con datos_sistema
cerca(av.PUNTOS_A_CUENTA + av.PUNTOS_A_FGPM + av.PUNTOS_A_COMISION_Y_SEGURO,
      av.PUNTOS_APORTE_OBLIGATORIO, 1e-9,
      "11,5% + 1,5% + 3% suman los 16 puntos del aporte obligatorio")

print()

# ---------------------------------------------------------------------------
# Resultado
# ---------------------------------------------------------------------------

print("=" * 78)
if fallas:
    print(f"RESULTADO: {len(fallas)} FALLA(S)")
    for f in fallas:
        print(f"  - {f}")
    print("=" * 78)
    sys.exit(1)

print("RESULTADO: todo en verde")
print("=" * 78)
sys.exit(0)
