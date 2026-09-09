# Módulo de lagunas: dónde están los huecos de la historia laboral.
#
# Por qué existe: "¿dónde están mis huecos?" es una de las preguntas más
# naturales que recibe Júbilo, y hasta ahora no había forma de responderla con
# la calculadora. El agente terminaba comparando rangos a mano, que es
# exactamente lo que prohíbe la regla dura 1 del kit (la IA nunca calcula).
# El esquema de datos ya prometía esto: "lagunas, semanas recalculadas y
# alertas las genera el código" (esquema-datos.md, regla 4).
#
# Qué responde, en tres bloques que no se solapan:
#   1. VACÍOS: periodos que ningún aportante reportó (nadie cotizó, nada).
#   2. DÉFICIT POR TRAMO: dentro de un rango sí reportado, cuántas semanas
#      faltaron frente a las que cabían en ese rango.
#   3. FILAS CON SALARIO Y CERO SEMANAS: hay aportante y hay salario, pero el
#      reporte no acreditó ni una semana. Es un cuarto estado que la taxonomía
#      de mora-y-correccion-historia-laboral.md no nombra (ver ese documento).
#
# LÍMITE DEL FORMATO QUE ESTE MÓDULO RESPETA (no romperlo nunca):
# Colpensiones agrupa por tramos con el mismo salario, así que el detalle mes a
# mes NO EXISTE en el documento. Este módulo puede decir "en este tramo faltan
# unos dos meses"; NO puede decir CUÁLES dos meses. Los meses que marca dentro
# de un tramo son el residuo del reparto de días, no una lectura del documento.
# Quien quiera el mes exacto va a su historial de pagos en PILA.

from datetime import date

from rpm import expandir_a_meses, mes_siguiente

# Convención de días por mes de todo el sistema pensional (y del resto de la
# calculadora): un mes completo cotizado son 30 días, no los días calendario.
# Por eso un tramo de 13 meses "cabe" 390 días, no 396.
DIAS_POR_MES = 30

# Por debajo de esto no se reporta nada: son colas de redondeo de las semanas
# con dos decimales del documento, no huecos reales. 7 días = 1 semana.
UMBRAL_DEFICIT_DIAS = 7

# Ventana de la densidad reciente: los mismos 3 años con los que `rpm.py`
# proyecta el futuro. Un hueco dentro de esta ventana no es historia, es el
# ritmo con el que se está proyectando toda la pensión.
MESES_VENTANA_RECIENTE = 36

# Por qué NO hay un umbral de semanas perdidas.
# La primera versión de este módulo alertaba a partir de 26 semanas, un número
# elegido a ojo. El problema de un umbral absoluto es que trata igual dos casos
# opuestos: 30 semanas repartidas en 20 años de vida laboral (ruido) y 30
# semanas en alguien a quien le faltan 20 para pensionarse (decisivo). Lo que
# hace material a un hueco no es su tamaño sino dos cosas que sí se pueden
# medir: si cae dentro de la ventana con la que se proyecta el futuro, y si
# pesa frente a lo que le falta a la persona para cumplir su requisito.
# Ver `alertas`.


# ---------------------------------------------------------------------------
# Utilidades de meses (trabajamos con claves (año, mes), como el resto)
# ---------------------------------------------------------------------------

def _clave(fecha_iso):
    """Convierte '2026-03-31' en la clave (2026, 3)."""
    return int(fecha_iso[:4]), int(fecha_iso[5:7])


def _texto(clave):
    """Convierte la clave (2026, 3) en el texto '2026-03'."""
    return f"{clave[0]}-{clave[1]:02d}"


def _meses_del_rango(desde, hasta):
    """Lista todos los meses entre dos fechas, ambos incluidos."""
    actual, fin = _clave(desde), _clave(hasta)
    meses = []
    while actual <= fin:
        meses.append(actual)
        actual = mes_siguiente(*actual)
    return meses


def _a_semanas(dias):
    """Pasa días a semanas con la convención del sistema (7 días = 1 semana)."""
    return round(dias / 7, 2)


def _a_meses_aprox(dias):
    """Pasa días a meses aproximados. Es la unidad en la que piensa el usuario."""
    return round(dias / DIAS_POR_MES, 1)


def _normalizar(periodos):
    """Deja solo los periodos con fechas y les pone los campos que falten.

    Este módulo lo llama el router, que corre ANTES de la validación de
    estructura, así que le puede llegar un JSON a medio armar. En vez de
    reventar, se ignora lo que no tenga fechas: un periodo sin fechas no se
    puede ubicar en la línea de tiempo, y el validador ya lo reporta aparte.
    """
    limpios = []
    for p in periodos:
        if not p.get("desde") or not p.get("hasta"):
            continue
        completo = dict(p)
        completo.setdefault("dias_cotizados", None)
        completo.setdefault("semanas_validas", None)
        completo.setdefault("semanas_sim", None)
        completo.setdefault("ibc", None)
        limpios.append(completo)
    return limpios


# ---------------------------------------------------------------------------
# El análisis completo
# ---------------------------------------------------------------------------

def analizar(caso, fecha_calculo=None):
    """Recibe el JSON extraído y devuelve dónde están los huecos.

    Todo sale del mapa mes a mes que ya construye `rpm.expandir_a_meses`, que
    es el mismo que alimenta el IBL. Eso importa por dos razones: usa una sola
    definición de "mes cotizado" en toda la calculadora, y **ya topa los días
    en 30 cuando hay dos aportantes el mismo mes** (regla 3 de esquema-datos).
    Ese tope es justo lo que evita inventar déficits donde hubo simultaneidad
    legítima: si un mes lo cubrió el otro aportante, el mes cuenta como lleno.
    """
    fecha_calculo = fecha_calculo or date.today()
    periodos = _normalizar(caso.get("periodos") or [])
    if not periodos:
        # Sin fechas no hay línea de tiempo contra la cual medir un hueco. Se
        # dice, no se inventa: el router llama este módulo antes de que la
        # validación de estructura haya corrido, así que puede llegar de todo.
        return {"error": "Los periodos no traen fechas: no se puede ubicar "
                         "ningún hueco en el tiempo"}

    # Mapa mes -> {"dias": int, "ibc": float} con TODOS los aportantes juntos
    meses = expandir_a_meses(periodos)

    # Todos los meses que algún tramo del documento dice cubrir. Un mes que
    # está aquí y no tiene días es un déficit; un mes que no está aquí y cae
    # entre el primero y el último es un vacío. Los dos conjuntos no se cruzan.
    meses_en_tramos = set()
    for p in periodos:
        meses_en_tramos.update(_meses_del_rango(p["desde"], p["hasta"]))

    primer_mes, ultimo_mes = min(meses_en_tramos), max(meses_en_tramos)

    # Déficit total SIN doble conteo. No se puede sumar el déficit de los
    # tramos: dos filas pueden cubrir el mismo mes (dos aportantes, o un pago
    # partido) y ese mes se contaría dos veces. El total se mide una sola vez
    # por mes, sobre el mapa global.
    dias_faltantes_global = sum(
        DIAS_POR_MES - min(DIAS_POR_MES, meses.get(m, {}).get("dias", 0))
        for m in meses_en_tramos)

    return {
        "cobertura": {
            "desde": _texto(primer_mes),
            "hasta": _texto(ultimo_mes),
            "meses_del_documento": len(_meses_del_rango(
                f"{_texto(primer_mes)}-01", f"{_texto(ultimo_mes)}-01")),
        },
        "vacios": _vacios(meses, meses_en_tramos, periodos,
                          primer_mes, ultimo_mes),
        "tramos_con_deficit": _deficit_por_tramo(meses, periodos),
        "filas_ibc_sin_semanas": _filas_ibc_sin_semanas(periodos),
        # Ojo al leer la lista de arriba: dos tramos pueden solaparse, así que
        # sus déficits NO se suman. El número bueno es este.
        "deficit_de_tramos_semanas": _a_semanas(dias_faltantes_global),
        "deficit_de_tramos_meses_aprox": _a_meses_aprox(dias_faltantes_global),
        "reciente": _reciente(meses, fecha_calculo, primer_mes, ultimo_mes),
        "limite_del_formato": (
            "Este documento agrupa las cotizaciones por tramos con un mismo "
            "salario, así que el detalle mes a mes no existe en él. Se puede "
            "decir cuántos meses faltan dentro de un tramo, no cuáles. El mes "
            "exacto está en el historial de pagos de PILA."
        ),
    }


def _reciente(meses, fecha_calculo, primer_mes, ultimo_mes):
    """Cuánto se perdió dentro de la ventana con la que se proyecta el futuro.

    Por qué se mide aparte: `rpm.py` y `rais.py` proyectan toda la pensión con
    la densidad de los últimos 3 años. Un hueco dentro de esa ventana no es
    historia pasada, **es el supuesto con el que se está calculando el futuro**,
    y por eso merece mención aunque sea chico. Uno de hace veinte años, no.

    La ventana se recorta por los dos lados contra lo que cubre el documento:
    los meses posteriores al corte del reporte no son huecos de la persona (es
    el reporte que se acabó), y los anteriores a su primera cotización tampoco
    (todavía no había empezado a trabajar). Sin ese recorte, alguien que se
    afilió hace un año parecería tener dos años de huecos.
    """
    fin = min(ultimo_mes, (fecha_calculo.year, fecha_calculo.month))
    # Retrocedemos la ventana mes a mes desde el final
    inicio = fin
    for _ in range(MESES_VENTANA_RECIENTE - 1):
        inicio = (inicio[0] - 1, 12) if inicio[1] == 1 else (inicio[0], inicio[1] - 1)
    inicio = max(inicio, primer_mes)

    dias_faltantes, meses_contados = 0, 0
    actual = inicio
    while actual <= fin:
        dias_faltantes += DIAS_POR_MES - min(
            DIAS_POR_MES, meses.get(actual, {}).get("dias", 0))
        meses_contados += 1
        actual = mes_siguiente(*actual)

    return {
        "desde": _texto(inicio),
        "hasta": _texto(fin),
        "meses_evaluados": meses_contados,
        "semanas_perdidas": _a_semanas(dias_faltantes),
        "meses_perdidos_aprox": _a_meses_aprox(dias_faltantes),
    }


def _vacios(meses, meses_en_tramos, periodos, primer_mes, ultimo_mes):
    """Periodos que ningún aportante reportó: ni una fila los menciona.

    Se buscan solo ENTRE la primera y la última cotización del documento: lo
    de antes de afiliarse y lo posterior al corte del reporte no son huecos.
    """
    vacios = []
    corrida = []          # Meses vacíos consecutivos que se van acumulando
    actual = primer_mes
    while actual <= ultimo_mes:
        # Vacío = ningún tramo lo menciona Y no tiene días acreditados
        vacio = actual not in meses_en_tramos and meses.get(actual, {}).get("dias", 0) == 0
        if vacio:
            corrida.append(actual)
        elif corrida:
            vacios.append(_cerrar_vacio(corrida, periodos))
            corrida = []
        actual = mes_siguiente(*actual)
    if corrida:
        vacios.append(_cerrar_vacio(corrida, periodos))
    return vacios


def _cerrar_vacio(corrida, periodos):
    """Arma la ficha de un vacío: cuándo empezó, cuándo terminó, cuánto duró."""
    inicio, fin = corrida[0], corrida[-1]
    # Con qué empleador venía y con cuál retomó: le da contexto al usuario
    antes = [p for p in periodos if _clave(p["hasta"]) < inicio]
    despues = [p for p in periodos if _clave(p["desde"]) > fin]
    return {
        "desde": _texto(inicio),
        "hasta": _texto(fin),
        "meses": len(corrida),
        "anios_aprox": round(len(corrida) / 12, 1),
        "semanas_no_cotizadas": _a_semanas(len(corrida) * DIAS_POR_MES),
        # El tramo que cerró justo antes y el que abrió justo después
        "ultimo_aportante_antes": max(
            antes, key=lambda p: p["hasta"])["empleador"] if antes else None,
        "primer_aportante_despues": min(
            despues, key=lambda p: p["desde"])["empleador"] if despues else None,
    }


def _deficit_por_tramo(meses, periodos):
    """Dentro de cada tramo reportado: cuántas semanas cabían y cuántas hubo.

    El déficit se mide contra el MAPA GLOBAL de meses, no contra las semanas
    de la propia fila. Es la diferencia que evita el doble conteo: si en un mes
    de este tramo cotizó otro aportante, el mes está lleno y no hay déficit,
    aunque esta fila sola no lo llene.
    """
    tramos = []
    for p in periodos:
        semanas_propias = p.get("semanas_validas")
        if semanas_propias is None:
            semanas_propias = round((p.get("dias_cotizados") or 0) / 7, 2)

        # Una fila puramente simultánea (semanas válidas en cero porque las
        # semanas ya las contó el otro aportante) no genera déficit por
        # definición: su tiempo sí está cotizado, solo que acreditado al otro.
        if not semanas_propias and (p.get("semanas_sim") or 0) > 0:
            continue
        # Una fila con salario y cero semanas se reporta aparte (bloque 3):
        # no se sabe todavía si es un hueco o un aporte mal aplicado.
        if not semanas_propias and p.get("ibc"):
            continue

        del_rango = _meses_del_rango(p["desde"], p["hasta"])
        dias_posibles = len(del_rango) * DIAS_POR_MES
        dias_acreditados = sum(
            min(DIAS_POR_MES, meses.get(m, {}).get("dias", 0)) for m in del_rango)
        dias_faltantes = max(0, dias_posibles - dias_acreditados)
        if dias_faltantes < UMBRAL_DEFICIT_DIAS:
            continue

        dias_propios = round(semanas_propias * 7)
        tramos.append({
            "desde": p["desde"][:7],
            "hasta": p["hasta"][:7],
            "empleador": p.get("empleador"),
            "meses_del_rango": len(del_rango),
            "semanas_reportadas": _a_semanas(dias_propios),
            "semanas_posibles": _a_semanas(dias_posibles),
            "semanas_acreditadas_en_la_ventana": _a_semanas(dias_acreditados),
            "deficit_semanas": _a_semanas(dias_faltantes),
            "deficit_meses_aprox": _a_meses_aprox(dias_faltantes),
            # True = parte del hueco aparente de esta fila lo llenó otro
            # aportante en los mismos meses. Sin esto se inventarían déficits.
            "cubierto_por_otro_aportante": dias_acreditados > dias_propios,
        })
    return tramos


def _filas_ibc_sin_semanas(periodos):
    """Filas con aportante y salario reportado, pero cero semanas acreditadas.

    Es el cuarto estado que la taxonomía de mora no nombra: no es mora
    patronal, ni deuda presunta, ni periodo no reportado. Hay aportante, hay
    salario y la columna de semanas simultáneas también está en cero, así que
    tampoco es simultaneidad marcada. El módulo lo REPORTA; qué significa y
    qué hacer está en mora-y-correccion-historia-laboral.md sección 1.
    """
    filas = []
    for p in periodos:
        semanas_propias = p.get("semanas_validas")
        if semanas_propias is None:
            semanas_propias = round((p.get("dias_cotizados") or 0) / 7, 2)
        if semanas_propias:
            continue
        if (p.get("semanas_sim") or 0) > 0:
            continue        # Simultaneidad marcada: estado conocido, no es este
        if not p.get("ibc"):
            continue        # Sin salario reportado no es este caso
        filas.append({
            "desde": p["desde"][:7],
            "hasta": p["hasta"][:7],
            "empleador": p.get("empleador"),
            "nit": p.get("nit"),
            "ibc": p["ibc"],
            "observacion_documento": p.get("observacion"),
        })
    return filas


# ---------------------------------------------------------------------------
# Resumen para el router y para la salida del orquestador
# ---------------------------------------------------------------------------

def resumir(analisis):
    """Condensa el análisis en los números que el agente puede decir en voz alta."""
    if analisis.get("error"):
        return analisis

    semanas_vacios = round(sum(v["semanas_no_cotizadas"]
                               for v in analisis["vacios"]), 2)
    # NO se suman los déficits de los tramos: se solapan. Se usa el total
    # global, que cuenta cada mes una sola vez (ver `analizar`).
    semanas_deficit = analisis["deficit_de_tramos_semanas"]
    return {
        "vacios": len(analisis["vacios"]),
        "semanas_en_vacios": semanas_vacios,
        "tramos_con_deficit": len(analisis["tramos_con_deficit"]),
        "semanas_en_deficit_de_tramos": semanas_deficit,
        "semanas_perdidas_total": round(semanas_vacios + semanas_deficit, 2),
        "semanas_perdidas_ultimos_3_anios": analisis["reciente"]["semanas_perdidas"],
        "filas_ibc_sin_semanas": len(analisis["filas_ibc_sin_semanas"]),
    }


def alertas(analisis, semanas_hoy=None, semanas_requeridas=None):
    """Alertas para el router, en el mismo formato de texto que usa hoy.

    NO hay umbral de semanas perdidas. Un hueco se alerta cuando es material
    para ESTA persona, y eso se decide con dos pruebas independientes:

    1. **¿Está dentro de la ventana con la que se proyecta su futuro?**
       Los tres últimos años son la densidad con la que se calcula toda la
       pensión. Un hueco ahí no es historia, es un supuesto vivo.
    2. **¿Pesa frente a lo que le falta?** Si lo perdido en huecos alcanza para
       cubrir lo que le falta para su requisito, recuperarlo es la palanca más
       grande que tiene. Si no llega ni a la mitad de lo que le falta, no lo es.

    `semanas_hoy` y `semanas_requeridas` son opcionales: sin ellas la prueba 2
    no corre (y no se inventa un resultado), pero la 1 sigue funcionando.
    """
    if analisis.get("error"):
        return []
    r = resumir(analisis)
    salida = []

    # --- Prueba 1: huecos dentro de la ventana de proyección ---
    rec = analisis["reciente"]
    if rec["semanas_perdidas"] >= 4.29:      # Al menos un mes completo perdido
        salida.append(
            f"lagunas_recientes: {rec['semanas_perdidas']} semanas sin cotizar "
            f"entre {rec['desde']} y {rec['hasta']} "
            f"(~{rec['meses_perdidos_aprox']} meses). Es la ventana con la que "
            f"se proyecta su futuro: el supuesto de continuidad ya viene "
            f"castigado por esto y hay que decírselo")

    # --- Prueba 2: huecos que pesan frente a lo que le falta ---
    if semanas_hoy is not None and semanas_requeridas is not None:
        faltantes = round(max(0, semanas_requeridas - semanas_hoy), 2)
        if faltantes > 0 and r["semanas_perdidas_total"] >= faltantes:
            veces = round(r["semanas_perdidas_total"] / faltantes, 1)
            salida.append(
                f"lagunas_decisivas: perdió {r['semanas_perdidas_total']} semanas "
                f"en huecos y le faltan {faltantes} para su requisito "
                f"({veces}x). Recuperar lo recuperable es su palanca más grande; "
                f"ver recuperacion.py y mora-y-correccion-historia-laboral.md")

    # --- Siempre: el cuarto estado, que no depende de tamaños ---
    if r["filas_ibc_sin_semanas"]:
        salida.append(
            f"ibc_sin_semanas: {r['filas_ibc_sin_semanas']} filas con salario "
            f"reportado y cero semanas acreditadas, sin marca de simultaneidad. "
            f"Estado no clasificado: preguntar al usuario antes de concluir "
            f"(mora-y-correccion-historia-laboral.md s.1 bis)")
    return salida
