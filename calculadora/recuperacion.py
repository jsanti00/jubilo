# Módulo de recuperación: qué pasa con el número si las semanas se recuperan.
#
# Por qué existe: `lagunas.py` responde "¿dónde están mis huecos?". La pregunta
# que sigue, siempre, es "¿y cuánto me sube la pensión si los recupero?", y
# hasta ahora la respuesta era "V1 no lo calcula". Esa respuesta deja al usuario
# sin saber si vale la pena pelear la corrección, que es justo la decisión.
#
# LA REGLA QUE ORGANIZA TODO EL MÓDULO: no todos los huecos son iguales frente
# a esta pregunta, y la diferencia está en si el documento trae el salario.
#
#   | Grupo                          | ¿Ya cuenta? | ¿Se puede estimar la mesada? |
#   |--------------------------------|-------------|------------------------------|
#   | Mora o deuda presunta marcada  | SÍ, ya está | No hay nada que ganar. Lo que
#   |   por el propio documento      |             | hay es un RIESGO a la baja   |
#   | Filas con IBC y cero semanas   | No          | SÍ: hay salario y hay periodo|
#   | Vacíos y déficit de tramos     | No          | NO: no hay salario ni prueba |
#
# El tercer grupo es el más grande y el que NO se puede estimar. Se dice cuántas
# semanas serían y se para ahí. Inventar un salario para un periodo que el
# documento no reporta es exactamente la alucinación que el diseño evita.
#
# Cómo se estima: no hay una fórmula nueva. Se arma una copia del caso con las
# semanas acreditadas y se vuelve a correr el mismo módulo del régimen. Así el
# efecto sobre el IBL, sobre los bloques de 50 semanas y sobre la fecha de
# pensión sale del código que ya está probado, no de una cuenta aparte.

import copy

import lagunas
import rais
import rpm
from rpm import expandir_a_meses, mes_siguiente

# Observaciones con las que el documento marca un periodo que reclama el
# sistema pero que el aportante no pagó (o no se sabe si pagó).
OBSERVACIONES_DE_MORA = ("mora", "deuda_presunta")


# ---------------------------------------------------------------------------
# Paso 1: qué hay para recuperar, y de qué tipo es
# ---------------------------------------------------------------------------

def identificar(caso, fecha_calculo=None):
    """Clasifica lo recuperable en los tres grupos de la tabla de arriba."""
    analisis = lagunas.analizar(caso, fecha_calculo=fecha_calculo)
    if analisis.get("error"):
        return {"error": analisis["error"]}

    periodos = caso.get("periodos") or []
    meses = expandir_a_meses(lagunas._normalizar(periodos))

    # --- Grupo 1: mora ya acreditada por el documento ---
    # Ojo con la intuición: en el formato de Colpensiones estas filas suelen
    # traer semanas válidas mayores que cero, así que YA ESTÁN dentro del total
    # impreso y dentro del conteo de la calculadora. No son semanas por ganar.
    en_mora_ya_contadas, en_mora_sin_contar = [], []
    for p in periodos:
        if p.get("observacion") not in OBSERVACIONES_DE_MORA:
            continue
        semanas = _semanas_propias(p)
        ficha = {"desde": p["desde"][:7], "hasta": p["hasta"][:7],
                 "empleador": p.get("empleador"), "observacion": p["observacion"],
                 "semanas": semanas, "ibc": p.get("ibc")}
        (en_mora_ya_contadas if semanas else en_mora_sin_contar).append(ficha)

    # --- Grupo 2: filas con salario y cero semanas (el cuarto estado) ---
    # De estas sí se puede estimar, porque traen IBC y traen periodo. Pero solo
    # suman los días que el mes tenga LIBRES: si ese mes ya está lleno con otro
    # aportante, acreditarlas no agrega ni una semana (era simultaneidad).
    acreditables = []
    for fila in analisis["filas_ibc_sin_semanas"]:
        dias_libres = _dias_libres(meses, fila["desde"], fila["hasta"])
        acreditables.append({**fila,
                             "dias_acreditables": dias_libres,
                             "semanas_que_agregaria": round(dias_libres / 7, 2)})

    # --- Grupo 3: vacíos y déficit, sin salario que permita estimar ---
    resumen = lagunas.resumir(analisis)

    return {
        "mora_ya_contada": en_mora_ya_contadas,
        "mora_sin_contar": en_mora_sin_contar,
        "acreditables": acreditables,
        "semanas_acreditables": round(
            sum(a["semanas_que_agregaria"] for a in acreditables), 2),
        # Advertencia obligatoria cuando el documento agrupa por tramos: para
        # saber cuántos días tiene libres un mes hay que saber en qué meses del
        # rango cotizó, y eso el documento NO lo dice. La calculadora reparte
        # los días desde el inicio del rango, que es una aproximación. Si los
        # meses en blanco caían en otra parte del rango, los días libres de un
        # mes concreto cambian. El total de semanas no cambia; su reparto sí.
        "precision_de_los_dias_libres": (
            "aproximada: el documento agrupa por tramos y no dice en qué meses "
            "del rango se cotizó" if _agrupa_por_tramos(periodos) else "exacta"),
        "sin_salario_reportado": {
            "semanas": resumen["semanas_perdidas_total"],
            "por_que_no_se_estima": (
                "El documento no reporta salario para esos periodos, así que no "
                "hay con qué calcular cuánto subiría la mesada. Se puede decir "
                "cuántas semanas serían, no cuánta plata. Estimar un salario "
                "que el documento no trae sería inventarlo."),
        },
    }


def _agrupa_por_tramos(periodos):
    """True si el documento resume varios meses en una fila (Colpensiones)."""
    return any(p.get("ibc_tipo") == "ultimo_del_rango" or
               p["desde"][:7] != p["hasta"][:7] for p in periodos)


def _semanas_propias(p):
    """Semanas que esa fila aporta por sí sola, en cualquiera de los 2 formatos."""
    if p.get("semanas_validas") is not None:
        return p["semanas_validas"]
    return round((p.get("dias_cotizados") or 0) / 7, 2)


def _dias_libres(meses, desde, hasta):
    """Días que quedan libres en los meses de un rango (tope de 30 por mes).

    Es la pieza que evita prometer semanas que no existen: si en ese mes la
    persona ya cotizó 30 días por otro lado, acreditar esta fila **no le suma
    nada**, porque las semanas se cuentan una sola vez (regla 3 de
    esquema-datos.md). Es simultaneidad, no un hueco.
    """
    libres = 0
    actual = (int(desde[:4]), int(desde[5:7]))
    fin = (int(hasta[:4]), int(hasta[5:7]))
    while actual <= fin:
        libres += max(0, 30 - meses.get(actual, {}).get("dias", 0))
        actual = mes_siguiente(*actual)
    return libres


# ---------------------------------------------------------------------------
# Paso 2: correr el diagnóstico otra vez, con y sin esas semanas
# ---------------------------------------------------------------------------

def simular(caso, sexo, edad=None, fecha_calculo=None):
    """Compara el diagnóstico de hoy contra el de los escenarios recuperables.

    Devuelve el antes, el después y la diferencia. Los dos escenarios van en
    direcciones opuestas a propósito:

    - `acreditar_lo_pendiente`: lo que GANA si las filas con salario y cero
      semanas se le acreditan.
    - `perder_la_mora`: lo que PIERDE si las semanas en mora que el documento ya
      le cuenta no se convalidan. Es el escenario que nadie le muestra y es un
      riesgo real, porque esas semanas están dentro de su total impreso.
    """
    inventario = identificar(caso, fecha_calculo=fecha_calculo)
    if inventario.get("error"):
        return inventario

    base = _correr(caso, sexo, edad, fecha_calculo)
    escenarios = {}

    # --- Escenario al alza: se le acreditan las filas pendientes ---
    if inventario["semanas_acreditables"] > 0:
        caso_mas = _con_filas_acreditadas(caso, inventario["acreditables"])
        escenarios["acreditar_lo_pendiente"] = _comparar(
            base, _correr(caso_mas, sexo, edad, fecha_calculo),
            f"Si le acreditan las {inventario['semanas_acreditables']} semanas "
            f"de las filas con salario reportado y cero semanas")

    # --- Escenario a la baja: no le convalidan la mora que ya tiene contada ---
    if inventario["mora_ya_contada"]:
        caso_menos = _sin_filas(caso, inventario["mora_ya_contada"])
        semanas_en_riesgo = round(
            sum(f["semanas"] for f in inventario["mora_ya_contada"]), 2)
        escenarios["perder_la_mora"] = _comparar(
            base, _correr(caso_menos, sexo, edad, fecha_calculo),
            f"Si NO le convalidan las {semanas_en_riesgo} semanas en mora que "
            f"el documento ya le cuenta")

    return {
        "regimen": caso["documento"].get("regimen"),
        "inventario": inventario,
        "base": base,
        "escenarios": escenarios,
        # Con qué cifra se midió la palanca. En RAIS son dos, una por extremo de
        # la banda del factor; en RPM es una sola porque la fórmula es
        # determinista. Se declara para que nadie lea un delta suelto sin saber
        # contra qué borde se calculó.
        "nota_banda": (
            "las diferencias de mesada van en los dos extremos de la banda del "
            "factor de conversión: sin apellido, el 4% normativo; con "
            "'_conservadora', el precio de mercado"
            if base.get("mesada_conservadora") else
            "el RPM es determinista: la mesada es un punto, no una banda"),
    }


def _correr(caso, sexo, edad, fecha_calculo):
    """Corre el módulo del régimen y saca las 3 cifras que se comparan.

    La mesada de referencia es la del escenario en que la persona sigue
    cotizando: RPM entrega una sola; en RAIS se toma el **perfil moderado**,
    porque es el único que existe en los dos lados de la comparación. Es una
    simplificación declarada, no un veredicto: el rango de perfiles sigue
    saliendo del diagnóstico principal.
    """
    if caso["documento"].get("regimen") == "RPM":
        d = rpm.diagnosticar(caso, sexo, fecha_calculo=fecha_calculo)
        escenario = d.get("escenario_sigue_cotizando") or {}
        return {"semanas": d["semanas_hoy"],
                "mesada": escenario.get("mesada"),
                "ibl": escenario.get("ibl"),
                "fecha_pension": d.get("fecha_pension_estimada"),
                "fecha_cumple_semanas": d.get("fecha_cumple_semanas")}
    d = rais.diagnosticar(caso, sexo=sexo, edad=edad, fecha_calculo=fecha_calculo)
    if d.get("error"):
        return {"error": d["error"]}
    moderado = (d.get("escenarios") or {}).get("moderado") or {}
    return {"semanas": d["semanas_hoy"],
            # "mesada" sin apellido es el extremo OPTIMISTA de la banda del
            # factor (el 4% normativo). Se conserva con ese nombre porque es lo
            # que ya leían los otros módulos, y viaja acompañada de su extremo
            # conservador para que ninguna diferencia se calcule solo contra el
            # borde bueno.
            "mesada": moderado.get("mesada"),
            "mesada_conservadora": moderado.get("mesada_conservadora"),
            "mesada_banda": moderado.get("mesada_banda"),
            "salida": moderado.get("salida"),
            "salida_conservadora": moderado.get("salida_conservadora"),
            "edad_pension_anticipada": d.get("edad_pension_anticipada"),
            "edad_pension_anticipada_banda": d.get("edad_pension_anticipada_banda"),
            "fecha_pension": None,
            "fecha_cumple_semanas": None}


def _comparar(base, otro, descripcion):
    """Arma el antes y después con la diferencia ya calculada."""
    if otro.get("error") or base.get("error"):
        return {"error": otro.get("error") or base.get("error")}
    resultado = {
        "que_pasaria": descripcion,
        "semanas": otro["semanas"],
        "delta_semanas": round(otro["semanas"] - base["semanas"], 2),
        "mesada": otro["mesada"],
        "fecha_pension": otro.get("fecha_pension"),
    }
    if base["mesada"] and otro["mesada"]:
        resultado["delta_mesada"] = round(otro["mesada"] - base["mesada"])
        resultado["delta_mesada_pct"] = round(
            100 * (otro["mesada"] - base["mesada"]) / base["mesada"], 2)
        # El resultado contraintuitivo que hay que saber explicar: en el RPM,
        # sumar semanas cotizadas sobre un salario bajo BAJA el promedio (IBL)
        # y puede bajar la mesada. Más semanas no siempre es más plata. Sin esta
        # advertencia el agente presentaría una pérdida como una ganancia.
        if resultado["delta_semanas"] > 0 and resultado["delta_mesada"] < 0:
            resultado["advertencia"] = (
                "Recuperar estas semanas SUBE el conteo y BAJA la mesada: el "
                "salario de esos periodos está por debajo de su promedio, así "
                "que entra al IBL tirándolo hacia abajo. Sirve si le faltan "
                "semanas para cumplir el requisito; no sirve para subir el "
                "monto. Hay que decírselo en esos términos.")
    # En RAIS la mesada viene en banda, así que la diferencia se calcula en los
    # DOS extremos. Medir la palanca solo contra el borde optimista la
    # exageraría, que es justo el error que la banda vino a evitar.
    if base.get("mesada_conservadora") and otro.get("mesada_conservadora"):
        resultado["mesada_banda"] = otro.get("mesada_banda")
        resultado["delta_mesada_conservadora"] = round(
            otro["mesada_conservadora"] - base["mesada_conservadora"])
        resultado["delta_mesada_conservadora_pct"] = round(
            100 * (otro["mesada_conservadora"] - base["mesada_conservadora"])
            / base["mesada_conservadora"], 2)
        resultado["base_de_comparacion"] = (
            "las cifras sin apellido son el extremo optimista de la banda del "
            "factor (4% normativo); las '_conservadora' son el extremo de "
            "precio de mercado. El agente comunica el rango, no un borde")
        # Si el signo cambia entre extremos, la recuperación no tiene un
        # veredicto único y hay que decirlo en vez de mostrar una ganancia
        if (resultado.get("delta_mesada") or 0) * \
                resultado["delta_mesada_conservadora"] < 0:
            resultado["veredicto_depende_del_extremo"] = (
                "recuperar estas semanas sube la mesada en un extremo de la "
                "banda y la baja en el otro: no hay un veredicto único que dar")
        # Si el extremo conservador cae en otra salida del RAIS, el cambio de
        # veredicto pesa más que cualquier diferencia de monto
        if base.get("salida_conservadora") != base.get("salida"):
            resultado["salidas_distintas_en_la_banda"] = (
                f"según el extremo, la salida es {base.get('salida')} o "
                f"{base.get('salida_conservadora')}: antes de hablar de cuánto "
                f"sube la mesada hay que decir que el desenlace mismo depende "
                f"del precio de la renta vitalicia")

    # Adelantar o atrasar la fecha suele importar más que la mesada
    if base.get("fecha_pension") != otro.get("fecha_pension"):
        resultado["cambia_la_fecha_de_pension"] = True
    if base.get("edad_pension_anticipada") != otro.get("edad_pension_anticipada"):
        resultado["edad_pension_anticipada"] = otro.get("edad_pension_anticipada")
    return resultado


# ---------------------------------------------------------------------------
# Paso 3: construir las copias del caso (nunca se toca el original)
# ---------------------------------------------------------------------------

def _con_filas_acreditadas(caso, acreditables):
    """Copia del caso con las filas pendientes acreditadas, solo por los días
    libres del mes. Acreditar más sería contar dos veces el mismo mes."""
    nuevo = copy.deepcopy(caso)
    pendientes = {(a["desde"], a["hasta"], a["empleador"]): a
                  for a in acreditables if a["dias_acreditables"] > 0}
    for p in nuevo["periodos"]:
        clave = (p["desde"][:7], p["hasta"][:7], p.get("empleador"))
        a = pendientes.get(clave)
        if not a:
            continue
        semanas = round(a["dias_acreditables"] / 7, 2)
        if p.get("semanas_validas") is not None:
            p["semanas_validas"] = semanas
            p["semanas"] = semanas
        else:
            p["dias_cotizados"] = a["dias_acreditables"]
    # El total impreso deja de cuadrar a propósito: este caso ya no es el
    # documento, es un escenario. No se vuelve a verificar contra el total.
    nuevo["resumen_documento"] = dict(nuevo["resumen_documento"])
    nuevo["resumen_documento"]["total_semanas"] = None
    return nuevo


def _sin_filas(caso, filas):
    """Copia del caso sin las semanas de unas filas (escenario a la baja)."""
    nuevo = copy.deepcopy(caso)
    quitar = {(f["desde"], f["hasta"], f["empleador"]) for f in filas}
    for p in nuevo["periodos"]:
        if (p["desde"][:7], p["hasta"][:7], p.get("empleador")) in quitar:
            if p.get("semanas_validas") is not None:
                p["semanas_validas"] = 0.0
                p["semanas"] = 0.0
            else:
                p["dias_cotizados"] = 0
    nuevo["resumen_documento"] = dict(nuevo["resumen_documento"])
    nuevo["resumen_documento"]["total_semanas"] = None
    return nuevo
