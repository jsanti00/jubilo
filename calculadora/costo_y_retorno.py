# Módulo de COSTO Y RETORNO: cuánto cuesta cotizar y en cuánto tiempo se recupera.
#
# Por qué existe: el diagnóstico responde "cuánta pensión te queda", pero la
# decisión real del usuario es "¿vale la pena pagar esto?". Hasta el 2026-07-27
# ese número se calculaba en scripts temporales fuera del repositorio y sin
# pruebas (pendiente 4 de ESTADO.md). Aquí queda fijo y verificado.
#
# FORMA DE LA SALIDA (decisión de producto del 2026-07-27, no reabrir):
# una TABLA DE ESCENARIOS ETIQUETADOS. Cada fila se nombra por la decisión que
# la produce ("cotizar sobre 7.600.000", "cotizar sobre el mínimo") y trae su
# costo y su breakeven como PUNTO ÚNICO. No es una banda ni un rango: la fila
# "sigues como hoy" y las alternativas se comparan una contra otra.
#
# Todo va en PESOS DE HOY (términos reales), igual que el resto de la
# calculadora: no se proyecta inflación en ningún punto.

from datos_sistema import SMLMV, MESADAS

# ---------------------------------------------------------------------------
# Tarifas de cotización mientras la persona APORTA
# ---------------------------------------------------------------------------

# Aporte a pensión: 16% del IBC.
# Fuente: Ley 100 de 1993 art. 20, modificado por Ley 797 de 2003 art. 7.
# Confianza: ALTA (norma verificada en kit-contexto/reglas-rpm.md sección 2).
APORTE_PENSION = 0.16

# Aporte a salud del cotizante: 12,5% del IBC.
# Fuente: Ley 100 de 1993 art. 204, modificado por Ley 1122 de 2007 art. 10.
# Confianza: ALTA.
APORTE_SALUD = 0.125

# Fondo de Solidaridad Pensional, subcuenta de solidaridad: +1% desde 4 SMLMV.
# Fuente: Ley 100 art. 27, modificado por Ley 797 de 2003 art. 8 num. 2 lit. a).
# Confianza: ALTA.
FSP_SOLIDARIDAD = 0.01
FSP_UMBRAL_SMLMV = 4

# Escalonado de la subcuenta de SUBSISTENCIA, desde 16 SMLMV.
# OJO, es un aporte que SE SUMA al 1% de solidaridad, no lo reemplaza: quien
# gana más de 20 SMLMV paga 2 puntos por encima del 16%.
# Cada tupla es (tope del tramo en SMLMV, porcentaje adicional).
# El último tramo (más de 20 SMLMV) es plano en 1%: la ley NO tiene tramos
# hasta 25 SMLMV, aunque una versión vieja del kit lo insinuaba.
# Fuente: Ley 100 art. 27, mod. Ley 797 de 2003 art. 8 num. 2 lit. a),
# tabla transcrita en kit-contexto/reglas-rpm.md sección 2.
# Confianza: MEDIA. La tabla está verificada, pero el kit deja dos preguntas
# abiertas para el abogado: (a) si hay decreto reglamentario posterior que
# ajuste los porcentajes y (b) si dentro de un tramo el escalonado se aplica
# por salto al cruzar el umbral o de forma proporcional. Aquí se aplica POR
# SALTO (al tocar 16 SMLMV se paga el 0,2% completo), que es la lectura
# literal de la tabla. Ver SUPUESTOS_DECLARADOS abajo.
FSP_SUBSISTENCIA = [
    (17, 0.002),   # De 16 a 17 SMLMV
    (18, 0.004),   # De 17 a 18 SMLMV
    (19, 0.006),   # De 18 a 19 SMLMV
    (20, 0.008),   # De 19 a 20 SMLMV
]
FSP_SUBSISTENCIA_UMBRAL_SMLMV = 16   # Debajo de esto no hay subsistencia
FSP_SUBSISTENCIA_TOPE = 0.01         # Superiores a 20 SMLMV: plano en 1%

# Piso y techo del IBC: 1 y 25 SMLMV. Fuente: Ley 100 art. 18.
IBC_MINIMO_SMLMV = 1
IBC_MAXIMO_SMLMV = 25

# ARL y caja de compensación NO entran en este cálculo, a propósito:
# para el rentista de capital y el independiente por cuenta propia son
# APORTES VOLUNTARIOS, no obligatorios (la ARL solo es obligatoria para
# contratistas con riesgo IV o V). Meterlos inflaría el costo de la decisión
# que el usuario está evaluando, que es cotizar a pensión. Si en algún momento
# el producto quiere mostrarlos, van como línea aparte y etiquetada como
# opcional, nunca dentro del aporte obligatorio.
# Confianza: MEDIA. Pendiente de confirmar con el abogado el caso del
# contratista de riesgo alto, que hoy queda fuera de alcance.

# ---------------------------------------------------------------------------
# Tarifas de salud cuando la persona YA ES PENSIONADA
# ---------------------------------------------------------------------------

# La salud del pensionado se descuenta de la mesada y va toda a su cargo.
# Fuente: Ley 100 art. 143 inciso 2.
# La tarifa depende del tamaño de la mesada medido en salarios mínimos.
# Cada tupla es (tope del tramo en SMLMV, porcentaje). El tope es inclusive.
# Fuentes: Ley 100 art. 204 par. 5, adicionado por Ley 2010 de 2019 art. 142
# (tramos de 4%, 10% y 12%); Ley 2294 de 2023 art. 78, que bajó a 10% el tramo
# de 2 a 3 SMLMV desde 2024.
# Confianza: ALTA para 4%, 10% (1 a 2) y 12%. MEDIA para el 10% del tramo de
# 2 a 3 SMLMV: la rebaja se corroboró con la Resolución 1271 de 2023 del
# Ministerio de Salud por fuentes secundarias, no en diario oficial, y podría
# perder vigencia al terminar el cuatrienio del PND 2022-2026. Revisar en
# enero de 2027 (kit-contexto/vida-del-pensionado.md sección 4).
SALUD_PENSIONADO = [
    (1, 0.04),    # Hasta 1 SMLMV
    (2, 0.10),    # Más de 1 y hasta 2 SMLMV
    (3, 0.10),    # Más de 2 y hasta 3 SMLMV
]
SALUD_PENSIONADO_TOPE = 0.12   # Más de 3 SMLMV

# Supuestos que viajan con toda cifra que produce este módulo. La regla del
# kit es que ningún número sale sin sus supuestos al lado.
SUPUESTOS_DECLARADOS = [
    "Todo en pesos de hoy (términos reales): no se proyecta inflación.",
    "La base de salud y la de pensión son la MISMA. No se pueden separar para "
    "cotizar a pensión sobre una base alta y a salud sobre el mínimo (criterio "
    "UGPP: el IBC es único para el sistema de seguridad social integral).",
    "ARL y caja de compensación quedan fuera: son voluntarias para el rentista "
    "de capital y para el independiente por cuenta propia.",
    "El escalonado del Fondo de Solidaridad se aplica por salto al cruzar el "
    "umbral, no proporcional dentro del tramo. Pendiente de confirmar.",
    "El breakeven es nominal y sin descuento: no incorpora el rendimiento que "
    "esa misma plata habría dado invertida en otra parte. Es un punto de "
    "recuperación de caja, no un análisis de valor presente.",
    f"Se asumen {MESADAS} mesadas al año (Acto Legislativo 01 de 2005).",
]


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------

def smlmv_vigente(anio=None):
    """Salario mínimo del año pedido, o el más reciente que tenga la tabla."""
    if anio is not None and anio in SMLMV:
        return SMLMV[anio]
    return SMLMV[max(SMLMV)]


def pesos(valor):
    """Formatea un número como pesos colombianos: 1750905 -> $1.750.905"""
    if valor is None:
        return "sin dato"
    return "$" + f"{round(valor):,}".replace(",", ".")


# ---------------------------------------------------------------------------
# Paso 1: el aporte mensual, con su desglose
# ---------------------------------------------------------------------------

def tarifa_fondo_solidaridad(ibc, smlmv=None):
    """Puntos porcentuales del Fondo de Solidaridad que le tocan a este IBC.

    Devuelve un diccionario con las DOS subcuentas por separado, porque se
    suman y confundirlas es el error clásico (el agente llegó a estimar el
    tramo alto a ojo el 2026-07-26; ahora se lee la tabla).
    """
    smlmv = smlmv or smlmv_vigente()
    s = ibc / smlmv   # El IBC medido en salarios mínimos

    # Subcuenta de solidaridad: 1% plano desde 4 SMLMV
    solidaridad = FSP_SOLIDARIDAD if s >= FSP_UMBRAL_SMLMV else 0.0

    # Subcuenta de subsistencia: escalonado desde 16 SMLMV
    subsistencia = 0.0
    if s >= FSP_SUBSISTENCIA_UMBRAL_SMLMV:
        # Buscamos el primer tramo cuyo tope todavía no se pasó
        subsistencia = FSP_SUBSISTENCIA_TOPE
        for tope, pct in FSP_SUBSISTENCIA:
            if s < tope:
                subsistencia = pct
                break

    return {
        "ibc_en_smlmv": round(s, 2),
        "solidaridad_pct": solidaridad,
        "subsistencia_pct": subsistencia,
        "total_pct": solidaridad + subsistencia,
    }


def aporte_mensual(ibc, smlmv=None, anio=None):
    """Cuánto paga al mes quien cotiza sobre este IBC, con todo desglosado.

    Suma tres cosas: 16% de pensión, el Fondo de Solidaridad que aplique y
    12,5% de salud sobre la MISMA base (no se pueden separar).
    Devuelve los valores exactos sin redondear en las llaves de cálculo: el
    redondeo a pesos ocurre solo al presentar, para que las cadenas largas
    (costo total, ganancia a 21 años) no acumulen error.
    """
    smlmv = smlmv or smlmv_vigente(anio)

    # Piso y techo legales del IBC: nadie cotiza por debajo de 1 ni encima de 25
    ibc_topado = min(max(ibc, IBC_MINIMO_SMLMV * smlmv), IBC_MAXIMO_SMLMV * smlmv)

    fsp = tarifa_fondo_solidaridad(ibc_topado, smlmv)

    pension = ibc_topado * APORTE_PENSION
    fsp_solidaridad = ibc_topado * fsp["solidaridad_pct"]
    fsp_subsistencia = ibc_topado * fsp["subsistencia_pct"]
    salud = ibc_topado * APORTE_SALUD
    total = pension + fsp_solidaridad + fsp_subsistencia + salud

    return {
        "ibc": ibc_topado,
        "ibc_topado": ibc_topado != ibc,   # Aviso de que el IBC pedido no cabía
        "ibc_en_smlmv": fsp["ibc_en_smlmv"],
        "pension": pension,
        "fsp_solidaridad": fsp_solidaridad,
        "fsp_subsistencia": fsp_subsistencia,
        "salud": salud,
        "total": total,
        # La tarifa combinada, útil para explicar de dónde sale el número
        "tarifa_total_pct": round(
            (APORTE_PENSION + fsp["total_pct"] + APORTE_SALUD) * 100, 3),
    }


def costo_total(ibc, meses_de_aporte, smlmv=None, anio=None):
    """Lo que pagaría en total desde hoy hasta pensionarse, en pesos de hoy."""
    return aporte_mensual(ibc, smlmv, anio)["total"] * meses_de_aporte


# ---------------------------------------------------------------------------
# Paso 2: la mesada neta (lo que de verdad le llega al bolsillo)
# ---------------------------------------------------------------------------

def tarifa_salud_pensionado(mesada_bruta, smlmv=None):
    """Porcentaje de salud que le descuentan de la mesada, según su tamaño."""
    smlmv = smlmv or smlmv_vigente()
    m = mesada_bruta / smlmv   # La mesada medida en salarios mínimos
    for tope, pct in SALUD_PENSIONADO:
        if m <= tope:
            return pct
    return SALUD_PENSIONADO_TOPE


def mesada_neta(mesada_bruta, smlmv=None, anio=None):
    """Mesada después del descuento de salud, con el detalle del descuento."""
    smlmv = smlmv or smlmv_vigente(anio)
    tarifa = tarifa_salud_pensionado(mesada_bruta, smlmv)
    descuento = mesada_bruta * tarifa
    return {
        "mesada_bruta": mesada_bruta,
        "mesada_en_smlmv": round(mesada_bruta / smlmv, 2),
        "salud_pct": tarifa,
        "descuento_salud": descuento,
        "mesada_neta": mesada_bruta - descuento,
    }


# ---------------------------------------------------------------------------
# Paso 3: breakeven y ganancia neta
# ---------------------------------------------------------------------------

def breakeven_meses(costo, mesada_neta_mensual, mesadas_al_anio=MESADAS):
    """En cuántos meses de pensión recupera todo lo que puso.

    Ojo con las 13 mesadas: en un año recibe 13 pagos pero pasan 12 meses, así
    que el ingreso por MES de calendario es la mesada por 13/12. Ignorarlo
    alarga el breakeven un 8% de mentira.

    Devuelve None si la mesada es cero o negativa (no hay recuperación posible).
    """
    if not mesada_neta_mensual or mesada_neta_mensual <= 0:
        return None
    ingreso_por_mes = mesada_neta_mensual * mesadas_al_anio / 12
    return costo / ingreso_por_mes


def ganancia_neta(costo, mesada_neta_mensual, horizonte_anios,
                  mesadas_al_anio=MESADAS):
    """Todo lo que recibe en el horizonte, menos todo lo que puso.

    horizonte_anios es parametrizable a propósito: el número honesto depende de
    cuántos años espere vivir pensionado, y eso lo decide el usuario, no el
    modelo. Por defecto el producto usa la expectativa de vida del sexo
    correspondiente (datos_sistema.EXPECTATIVA_VIDA).
    """
    return mesada_neta_mensual * mesadas_al_anio * horizonte_anios - costo


# ---------------------------------------------------------------------------
# Paso 4: un escenario etiquetado (una fila de la tabla)
# ---------------------------------------------------------------------------

def evaluar_escenario(etiqueta, ibc, meses_de_aporte, mesada_bruta,
                      horizonte_anios=21, smlmv=None, anio=None, es_base=False):
    """Arma una fila de la tabla: la decisión, su costo y su retorno.

    etiqueta: la DECISIÓN que produce esta fila, en palabras del usuario
              ("cotizar sobre 7.600.000", "cotizar sobre el mínimo",
              "sigues como hoy"). Es lo que hace legible la tabla.
    ibc: base mensual sobre la que cotizaría, en pesos de hoy.
    meses_de_aporte: cuántos meses seguiría cotizando hasta pensionarse.
    mesada_bruta: la mesada que ESE escenario produce, en pesos de hoy. Sale
                  del módulo del régimen (rpm.py o rais.py), nunca de aquí:
                  este módulo no calcula pensiones, calcula plata.
    horizonte_anios: años de pensión que se asumen para la ganancia neta.
    es_base: marca la fila "sigues como hoy", que es el punto de comparación.
    """
    smlmv = smlmv or smlmv_vigente(anio)

    aporte = aporte_mensual(ibc, smlmv)
    costo = aporte["total"] * meses_de_aporte
    neta = mesada_neta(mesada_bruta, smlmv)

    # Valores exactos (sin redondear) para las cadenas de cálculo
    neta_exacta = neta["mesada_neta"]
    meses_be = breakeven_meses(costo, neta_exacta)
    ganancia = ganancia_neta(costo, neta_exacta, horizonte_anios)

    return {
        "etiqueta": etiqueta,
        "es_base": es_base,
        "ibc": round(aporte["ibc"]),
        "ibc_topado": aporte["ibc_topado"],
        "meses_de_aporte": meses_de_aporte,
        "aporte_mensual": round(aporte["total"]),
        "aporte_desglose": {
            "pension_16_pct": round(aporte["pension"]),
            "fsp_solidaridad": round(aporte["fsp_solidaridad"]),
            "fsp_subsistencia": round(aporte["fsp_subsistencia"]),
            "salud_12_5_pct": round(aporte["salud"]),
            "tarifa_total_pct": aporte["tarifa_total_pct"],
        },
        "costo_total": round(costo),
        "mesada_bruta": round(mesada_bruta),
        "mesada_neta": round(neta_exacta),
        "salud_pensionado_pct": round(neta["salud_pct"] * 100, 1),
        "descuento_salud": round(neta["descuento_salud"]),
        "breakeven_meses": round(meses_be, 1) if meses_be is not None else None,
        "breakeven_anios": round(meses_be / 12, 1) if meses_be is not None else None,
        "horizonte_anios": horizonte_anios,
        "ganancia_neta_horizonte": round(ganancia),
        # Cuántas veces recupera lo que puso, en el horizonte asumido
        "multiplo_sobre_lo_aportado": round(
            (ganancia + costo) / costo, 1) if costo > 0 else None,
    }


# ---------------------------------------------------------------------------
# Paso 5: la tabla completa (lo que ve el usuario)
# ---------------------------------------------------------------------------

def tabla_de_escenarios(escenarios, horizonte_anios=21, smlmv=None, anio=None):
    """Construye la tabla de escenarios etiquetados.

    escenarios: lista de diccionarios con las llaves etiqueta, ibc,
                meses_de_aporte, mesada_bruta y, opcionalmente, es_base.
                La fila con es_base=True (o la primera, si ninguna lo marca)
                es "sigues como hoy" y encabeza la tabla; las demás quedan
                debajo ordenadas por costo de menor a mayor.

    Devuelve la tabla más los supuestos y el delta de cada alternativa contra
    la base: la comparación es el punto de la tabla, no las filas sueltas.
    """
    smlmv = smlmv or smlmv_vigente(anio)

    filas = [
        evaluar_escenario(
            e["etiqueta"], e["ibc"], e["meses_de_aporte"], e["mesada_bruta"],
            horizonte_anios=e.get("horizonte_anios", horizonte_anios),
            smlmv=smlmv, es_base=e.get("es_base", False))
        for e in escenarios
    ]
    if filas and not any(f["es_base"] for f in filas):
        filas[0]["es_base"] = True   # Sin marca explícita, la primera es la base

    base = next((f for f in filas if f["es_base"]), None)
    alternativas = sorted((f for f in filas if not f["es_base"]),
                          key=lambda f: f["costo_total"])

    # Cada alternativa se lee contra la base: cuánto más cuesta y cuánto más da
    for f in alternativas:
        if base:
            f["delta_vs_base"] = {
                "costo_total": f["costo_total"] - base["costo_total"],
                "mesada_neta": f["mesada_neta"] - base["mesada_neta"],
                "ganancia_neta_horizonte": (f["ganancia_neta_horizonte"]
                                            - base["ganancia_neta_horizonte"]),
            }

    return {
        "smlmv_usado": smlmv,
        "horizonte_anios": horizonte_anios,
        "mesadas_al_anio": MESADAS,
        "escenario_base": base,
        "alternativas": alternativas,
        "filas": ([base] if base else []) + alternativas,
        "supuestos": SUPUESTOS_DECLARADOS,
    }


def escenario_desde_diagnostico(etiqueta, diagnostico, meses_de_aporte,
                                es_base=False):
    """Traduce la salida de rpm.diagnosticar a una fila de esta tabla.

    Existe para que el IBC y la mesada NUNCA se tecleen a mano cuando ya
    existen en un diagnóstico: la regla del proyecto es que la mesada sale del
    módulo del régimen. Devuelve None si el diagnóstico no trae los datos
    (no se inventa nada).
    """
    escenario = (diagnostico or {}).get("escenario_sigue_cotizando") or {}
    ibc = escenario.get("ibc_futuro_supuesto")
    mesada = escenario.get("mesada")
    if not ibc or not mesada:
        return None
    return {
        "etiqueta": etiqueta,
        "ibc": ibc,
        "meses_de_aporte": meses_de_aporte,
        "mesada_bruta": mesada,
        "es_base": es_base,
    }


# ---------------------------------------------------------------------------
# Presentación en terminal (para leer rápido, NO es el mensaje al usuario)
# ---------------------------------------------------------------------------

def imprimir_tabla(t):
    """Imprime la tabla de escenarios. El agente redacta con el system-prompt,
    no copiando este texto."""
    print("=" * 78)
    print("COSTO Y RETORNO DE COTIZAR")
    print(f"Salario mínimo usado: {pesos(t['smlmv_usado'])}   "
          f"Horizonte: {t['horizonte_anios']} años   "
          f"Mesadas al año: {t['mesadas_al_anio']}")
    print("=" * 78)
    print()
    print(f"  {'Decisión':<32} {'Aporte/mes':>13} {'Costo total':>15} "
          f"{'Breakeven':>11}")
    print("  " + "-" * 74)
    for f in t["filas"]:
        marca = "*" if f["es_base"] else " "
        be = f"{f['breakeven_meses']} meses" if f["breakeven_meses"] else "no aplica"
        print(f"{marca} {f['etiqueta']:<32} {pesos(f['aporte_mensual']):>13} "
              f"{pesos(f['costo_total']):>15} {be:>11}")
    print("  " + "-" * 74)
    print("  * fila base: lo que pasa si sigue como hoy")
    print()
    for f in t["filas"]:
        print(f"  {f['etiqueta']}")
        print(f"    Mesada bruta {pesos(f['mesada_bruta'])} -> neta "
              f"{pesos(f['mesada_neta'])} "
              f"(salud del pensionado {f['salud_pensionado_pct']}%)")
        print(f"    Ganancia neta a {f['horizonte_anios']} años: "
              f"{pesos(f['ganancia_neta_horizonte'])} "
              f"({f['multiplo_sobre_lo_aportado']}x lo aportado)")
        if f.get("delta_vs_base"):
            d = f["delta_vs_base"]
            print(f"    Contra la base: {pesos(d['costo_total'])} más de costo, "
                  f"{pesos(d['mesada_neta'])} más de mesada neta")
        print()
    print("  SUPUESTOS:")
    for s in t["supuestos"]:
        print(f"    - {s}")
    print()


def main():
    """CLI mínima: un escenario base y las alternativas que se le pasen.

    Ejemplo (el caso real de validación):
      python3 costo_y_retorno.py --ibc 7600000 --meses 34 --mesada 2722674
    """
    import argparse

    p = argparse.ArgumentParser(
        description="Costo de cotizar y en cuánto tiempo se recupera.")
    p.add_argument("--ibc", type=float, required=True,
                   help="Base mensual de cotización del escenario base")
    p.add_argument("--meses", type=int, required=True,
                   help="Meses que seguiría cotizando hasta pensionarse")
    p.add_argument("--mesada", type=float, required=True,
                   help="Mesada bruta que produce ese escenario (sale de rpm.py)")
    p.add_argument("--etiqueta", default=None,
                   help="Nombre de la decisión (por defecto, el IBC)")
    p.add_argument("--horizonte", type=int, default=21,
                   help="Años de pensión asumidos (por defecto 21)")
    p.add_argument("--alternativa", action="append", default=[],
                   metavar="ETIQUETA:IBC:MESES:MESADA",
                   help="Fila alternativa, repetible. Ejemplo: "
                        "'cotizar sobre el mínimo:1750905:34:1750905'")
    args = p.parse_args()

    base_etiqueta = args.etiqueta or f"cotizar sobre {pesos(args.ibc)[1:]}"
    escenarios = [{"etiqueta": base_etiqueta, "ibc": args.ibc,
                   "meses_de_aporte": args.meses, "mesada_bruta": args.mesada,
                   "es_base": True}]

    # Cada alternativa viene como texto separado por dos puntos
    for texto in args.alternativa:
        etiqueta, ibc, meses, mesada = texto.rsplit(":", 3)
        escenarios.append({"etiqueta": etiqueta, "ibc": float(ibc),
                           "meses_de_aporte": int(meses),
                           "mesada_bruta": float(mesada)})

    imprimir_tabla(tabla_de_escenarios(escenarios, horizonte_anios=args.horizonte))


if __name__ == "__main__":
    main()
