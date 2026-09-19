"""calculadora/palancas.py: el director de orquesta de las palancas.

QUÉ PROBLEMA RESUELVE. Antes de este módulo, Júbilo tenía todos los motores de
cálculo construidos (rpm.py, rais.py, recuperacion.py, comparador.py,
costo_y_retorno.py, aportes_voluntarios.py) y ninguno de ellos se usaba para
responder la única pregunta que de verdad le importa a la persona: "¿y yo qué
puedo hacer?". El reporte salía con frases genéricas del tipo "cotiza sobre un
salario base mayor, si puedes", que no son accionables y además son obvias.

QUÉ HACE EN SU LUGAR. Convierte cada consejo en una frase con número propio:
"si te suben el sueldo un 10%, tu mesada sube $177.026 al mes". Y hace cuatro
cosas, en este orden:

  1. ELIGE. Qué palancas le aplican a ESTA persona y cuáles no, con el motivo.
  2. CUANTIFICA. Cada palanca se corre por la calculadora. Nunca se estima.
  3. ORDENA. Por impacto en pesos, que es lo que decide qué va primero.
  4. COMBINA. Los escenarios son combinaciones de las MEJORES palancas, no el
     peor caso. Ofrecerle "si dejas de cotizar hoy" a alguien de 27 años no es
     un escenario, es una amenaza, y no mueve a nadie a hacer nada.

CINCO REGLAS QUE ESTE MÓDULO NO PUEDE ROMPER. Vienen de decisiones ya tomadas
del proyecto y están en el AGENTS.md del repo:

  - La IA no calcula. El número sale de aquí, no del modelo.
  - No se recomienda administradora, fondo ni portafolio. Es asesoría de
    inversión, que es actividad regulada. Se muestra el dato y la persona decide.
  - No se recomienda el traslado de régimen. Se muestran los dos escenarios y se
    dice que la doble asesoría obligatoria es un requisito de ley que esto no
    reemplaza.
  - Una palanca que no se puede cuantificar se nombra sin número, nunca con uno
    inventado.
  - Ojo con el error de segmento. Ofrecerle aportes voluntarios a quien no tiene
    con qué es tan malo como ofrecerle BEPS a quien sí.

UNA SEXTA REGLA QUE SALIÓ DE CONSTRUIR ESTO, y que no estaba prevista: una
palanca puede salir NEGATIVA, y cuando sale negativa no se ofrece. El caso real
que lo destapó está explicado abajo, en `palanca_aplazar`.

CUÁNDO SE PREGUNTAN LOS DATOS QUE FALTAN. Decisión de Santiago del 2026-09-18:
nada de cuestionario al principio. La pregunta aparece cuando la palanca se
vuelve relevante, y solo entonces. Por eso este módulo nunca pregunta: devuelve
las palancas que le faltan datos con la pregunta exacta que habría que hacer, y
quien conversa decide si ya es el momento de hacerla.
"""

import math
from datetime import date

import rais
import rpm
import recuperacion
import comparador
import aportes_voluntarios as av
from datos_sistema import (
    RENDIMIENTO_REAL_POR_AFP, PERFILES_ESCOGIBLES, ADVERTENCIA_POR_AFP,
    rendimiento_de, mejor_y_peor_afp, mezcla_obligatoria,
    # Los tres datos que necesita el valle de la garantia de pension minima:
    # el salario minimo (que es el piso), el umbral del 110% que hay que
    # superar para salir de la garantia, y la fraccion de cada peso cotizado
    # que de verdad entra a la cuenta individual.
    SMLMV, CAPITAL_MINIMO_PCT, APORTE_A_CUENTA_RAIS,
)

# El detector de anomalías de la historia laboral es opcional a propósito: si
# todavía no existe en el repo, el resto de las palancas tiene que seguir
# funcionando. Una palanca que falta es un hueco; un módulo que revienta al
# importarse deja a la persona sin diagnóstico.
try:
    import anomalias
except ImportError:
    anomalias = None


# ---------------------------------------------------------------------------
# Los supuestos de cada palanca, nombrados una sola vez
# ---------------------------------------------------------------------------
# Por qué viven aquí arriba y no enterrados en cada función: son decisiones de
# producto (cuánto es "un aumento", cuánto es "cerrar las lagunas") y tienen que
# poder discutirse y cambiarse en un solo sitio.

# Los tres tamaños de aumento que se le muestran. El 10% es el ancla porque es
# un aumento que la gente reconoce como posible; el 20% y el 30% existen para
# que se vea que el efecto es lineal y la persona pueda interpolar el suyo.
AUMENTOS_DE_SUELDO = (0.10, 0.20, 0.30)

# Cerrar lagunas: contra qué densidad se compara. 1.0 es cotizar los doce meses
# del año. Se muestra también un escalón intermedio porque saltar de golpe al
# 100% le suena imposible a quien viene cotizando el 60% del tiempo.
DENSIDADES_OBJETIVO = (0.9, 1.0)

# Aplazar la pensión: los tres horizontes que se evalúan, en meses.
APLAZAMIENTOS = (12, 24, 36)

# Aporte voluntario: el monto de referencia cuando la persona no ha dicho cuánto
# podría poner. Es un ancla para que la cifra se pueda mostrar, y se declara
# como supuesto en la propia frase, nunca como si la persona lo hubiera dicho.
APORTE_VOLUNTARIO_DE_REFERENCIA = 500000

# Una palanca que mueve menos que esto al mes no se muestra. No es que el número
# esté mal: es que ocupar el espacio más valioso del reporte con una palanca que
# mueve $8.000 al mes le quita el puesto a una que mueve $400.000, y hace que
# todo el reporte se sienta irrelevante.
UMBRAL_MINIMO_PESOS = 20000

# Cuántas palancas CON número se muestran como máximo. Más de cuatro y la
# persona no prioriza ninguna, que es el resultado contrario al que se busca.
# La palanca 8 (administradora) y la 4 (régimen) no gastan cupo: la 8 viaja
# pegada a la 9 y la 4 va aparte, por las razones explicadas más abajo.
MAXIMO_A_MOSTRAR = 4

# --- El valle de la garantia de pension minima (2026-09-19) ---------------
# Cuanto hay que pasarse del umbral del 110% del salario minimo para decir que
# la persona SALTO el valle. Se exige margen a proposito: quedar justo encima
# del umbral es quedar a un mal ano de rendimiento de volver a caer dentro, y
# ofrecerle a alguien un salto que no aguanta un tropiezo es venderle humo.
MARGEN_PARA_SALTAR_EL_VALLE = 0.05

# Hasta donde llega "un esfuerzo razonable", medido contra lo que la persona
# gana hoy. Por encima de esto el salto deja de ser un camino y pasa a ser una
# frase bonita: se le dice el numero y se le dice que no da. Es una decision de
# producto, no una regla de la ley, y por eso vive aqui arriba y se puede mover.
LIMITE_ESFUERZO_RAZONABLE = 0.25

# Los topes de la busqueda del aporte requerido. La busqueda es una biseccion
# que corre la calculadora en cada paso, asi que hay que decirle donde parar:
# 40 pasos dejan el resultado con error de menos de un peso, y el techo evita
# quedarse dando vueltas si por alguna razon la mesada nunca sube.
PASOS_DE_BUSQUEDA = 40
TECHO_DE_BUSQUEDA_MENSUAL = 200000000


def pesos(valor):
    """Formatea un número como pesos colombianos: 1750905 pasa a $1.750.905."""
    if valor is None:
        return "sin dato"
    # El formato de Python usa coma para los miles; en Colombia es punto.
    signo = "-" if valor < 0 else ""
    return signo + "$" + format(int(round(abs(valor))), ",d").replace(",", ".")


def porcentaje(valor, decimales=0):
    """Formatea 0.0834 como 8% (o como 8,3% si se piden decimales)."""
    if valor is None:
        return "sin dato"
    texto = format(valor * 100, "." + str(decimales) + "f")
    # Coma decimal, que es lo que se usa en Colombia.
    return texto.replace(".", ",") + "%"


# ---------------------------------------------------------------------------
# La forma de una palanca
# ---------------------------------------------------------------------------

def _palanca(clave, numero, titulo, **extra):
    """Crea una palanca con todos sus campos, para que ninguna venga coja.

    Que todas las palancas tengan exactamente las mismas llaves es lo que
    permite ordenarlas, filtrarlas y renderizarlas sin preguntarse cada vez si
    tal campo existe. Los que no apliquen quedan en None, nunca ausentes.
    """
    palanca = {
        "clave": clave,                 # Nombre corto para el código
        "numero": numero,               # Su número en el banco de palancas
        "titulo": titulo,               # Cómo se llama para la persona
        "aplica": True,                 # ¿Se le puede ofrecer a esta persona?
        "motivo_no_aplica": None,       # Si no aplica, por qué (siempre se dice)
        "frase": None,                  # El texto cuantificado, listo para usar
        "efecto_mesada_mes": None,      # Pesos al mes que suma, para ordenar
        # QUÉ SIGNIFICA ESA CIFRA, en palabras. Sin esto, el reporte imprime
        # "$782.030 al mes" al lado de un título y la persona no sabe si es lo
        # que tendría que aportar, lo que se ahorraría o lo que recibiría de
        # más. Es lo tercero, y hay que decirlo. Viaja con cada palanca porque
        # no todas significan lo mismo: la mayoría son "más pensión al mes",
        # pero la del portafolio es una diferencia entre dos opciones.
        "etiqueta_efecto": "más de pensión al mes",
        "efecto_pct": None,             # El mismo efecto en porcentaje
        "efecto_meses_pension": None,   # Meses que adelanta (negativo) o atrasa
        "detalle": [],                  # Los escalones (10%, 20%, 30%...)
        "supuesto": None,               # Qué se supuso para llegar al número
        "fuente": None,                 # Norma o módulo del que sale
        "confianza": "alta",            # alta / media / baja
        "requiere_dato": None,          # Qué dato falta, si falta alguno
        "pregunta": None,               # La pregunta exacta que habría que hacer
        "limite_de_alcance": None,      # Hasta dónde llega Júbilo y no más
    }
    palanca.update(extra)
    return palanca


def _no_aplica(clave, numero, titulo, motivo, **extra):
    """Atajo para la palanca que se descarta: se nombra igual y se dice por qué.

    Descartar en silencio es peor que no evaluar: si mañana alguien se pregunta
    por qué a esta persona no se le ofreció sobrecotizar, la respuesta tiene que
    estar escrita en la salida, no en la cabeza de quien programó.
    """
    return _palanca(clave, numero, titulo, aplica=False,
                    motivo_no_aplica=motivo, **extra)


# ---------------------------------------------------------------------------
# Leer la mesada de un diagnóstico, que es donde es fácil equivocarse
# ---------------------------------------------------------------------------
# AVISO QUE VIENE DE UN ERROR REAL (2026-09-18). El reporte leía la mesada de
# `recuperacion.base.mesada_banda`. Ese número NO responde a los supuestos de
# palanca: si se pide el diagnóstico con un sueldo futuro distinto, el escenario
# cambia y `recuperacion.base` ni se entera. Daba el mismo número por casualidad
# en el caso base y se habría roto justo al empezar a mostrar palancas.
# Moraleja: al construir una palanca, verificar SIEMPRE de qué clave sale la
# cifra, y que esa clave dependa de verdad del supuesto que se está moviendo.

def escenario_aplicable(diagnostico_rais):
    """Cuál de los escenarios del RAIS es el que de verdad le aplica a la persona.

    No es siempre "moderado". A partir de cierta edad la ley obliga a ir pasando
    el saldo al fondo conservador, quiera la persona o no (la convergencia de
    multifondos). Cuando eso ya arrancó, el escenario real es la mezcla
    obligatoria, y mostrar el de mayor riesgo sería mostrarle una opción que no
    tiene. Devuelve la clave del escenario, no el escenario.
    """
    escenarios = diagnostico_rais.get("escenarios") or {}
    # Si la convergencia ya arrancó, manda la mezcla que impone la ley.
    if "mezcla_obligatoria_por_edad" in escenarios:
        return "mezcla_obligatoria_por_edad"
    # Si no, el moderado, que es el fondo por defecto del sistema.
    return "moderado" if "moderado" in escenarios else None


def mesada_de(diagnostico, regimen, clave_escenario=None):
    """Saca de un diagnóstico la mesada mensual comparable, o None.

    POR QUÉ UN SOLO NÚMERO Y NO LA BANDA. Para MEDIR una palanca hay que
    comparar peras con peras: el mismo extremo de la banda antes y después. Si
    se compara el piso de un escenario contra el techo del otro, la diferencia
    mezcla el efecto de la palanca con el ancho de la banda, y deja de medir la
    palanca. Aquí se usa siempre la llave "mesada", que es el extremo optimista,
    en los dos lados de la resta. La banda completa se sigue mostrando en el
    reporte para la cifra principal; para el DELTA de una palanca se usa esto.
    """
    if not diagnostico:
        return None
    if regimen == "RPM":
        escenario = diagnostico.get("escenario_sigue_cotizando") or {}
        return escenario.get("mesada")
    escenarios = diagnostico.get("escenarios") or {}
    clave = clave_escenario or escenario_aplicable(diagnostico)
    if not clave:
        return None
    return (escenarios.get(clave) or {}).get("mesada")


def _diagnosticar(caso, regimen, sexo, edad, fecha_calculo, **supuestos):
    """Corre el diagnóstico del régimen que corresponda, con los supuestos dados.

    Es la única puerta por la que este módulo llama a la calculadora. Tenerla en
    un solo sitio es lo que garantiza que el caso base y el caso con palanca se
    calculen exactamente igual salvo por el supuesto que se está moviendo, que
    es la condición para que la resta signifique algo.
    """
    if regimen == "RPM":
        return rpm.diagnosticar(caso, sexo, fecha_calculo=fecha_calculo,
                                **supuestos)
    return rais.diagnosticar(caso, sexo=sexo, edad=edad,
                             fecha_calculo=fecha_calculo, **supuestos)


def _delta(mesada_base, mesada_nueva):
    """La diferencia entre dos mesadas, en pesos y en porcentaje.

    Devuelve (None, None) si falta alguna de las dos, en vez de inventarse un
    cero: un cero dice "esta palanca no sirve" y un None dice "no se pudo
    calcular", que son cosas distintas y no se pueden confundir.
    """
    if mesada_base is None or mesada_nueva is None or mesada_base <= 0:
        return None, None
    diferencia = mesada_nueva - mesada_base
    return round(diferencia), round(diferencia / mesada_base, 4)


# ---------------------------------------------------------------------------
# GRUPO 1: las palancas que ya se podían cuantificar y nadie estaba llamando
# ---------------------------------------------------------------------------

def palanca_subir_sueldo(caso, regimen, sexo, edad, fecha_calculo, base):
    """Palanca 1: que te suban el sueldo.

    Es la palanca que el reporte viejo enunciaba como "cotizar sobre un salario
    base mayor, si puedes", que no dice nada. Aquí se cuantifica: se vuelve a
    correr la calculadora con el IBC futuro subido un 10%, 20% y 30%, y se mide
    cuánto sube la mesada en cada caso.
    """
    ibc_hoy = base["ibc_actual"]
    if not ibc_hoy:
        return _no_aplica(
            "subir_sueldo", 1, "Que te suban el sueldo",
            "No hay un salario reciente en la historia laboral con el que "
            "comparar, así que no se puede calcular el efecto de subirlo.")

    detalle = []
    for aumento in AUMENTOS_DE_SUELDO:
        # El supuesto se mueve en pesos de hoy, igual que todo el resto de la
        # calculadora: aquí nunca se proyecta inflación.
        nuevo_ibc = ibc_hoy * (1 + aumento)
        diagnostico = _diagnosticar(caso, regimen, sexo, edad, fecha_calculo,
                                    ibc_futuro=nuevo_ibc)
        mesada = mesada_de(diagnostico, regimen)
        monto, pct = _delta(base["mesada"], mesada)
        detalle.append({"aumento": aumento, "ibc_nuevo": round(nuevo_ibc),
                        "mesada": mesada, "efecto_mes": monto, "efecto_pct": pct})

    # El escalón del 10% es el que se comunica: es el más creíble y el que ancla.
    ancla = detalle[0]
    if ancla["efecto_mes"] is None:
        return _no_aplica("subir_sueldo", 1, "Que te suban el sueldo",
                          "La calculadora no pudo proyectar la mesada con un "
                          "salario distinto.")

    return _palanca(
        "subir_sueldo", 1, "Que te suban el sueldo un 10%",
        # LA ACLARACIÓN DEL "UNA SOLA VEZ" NO ES UN DETALLE. Sin ella, la
        # persona no sabe si el 10% es un aumento que le dan ahora y se
        # queda, o uno que se repite todos los años. Son dos escenarios con
        # resultados muy distintos, y el que calcula la calculadora es el
        # primero: un salto del 10% que se mantiene hasta la pensión.
        frase=("Si te suben el sueldo un 10% una sola vez y ese sueldo nuevo "
               "se mantiene hasta que te pensiones, tu pensión mensual sería "
               + pesos(ancla["efecto_mes"]) + " más alta ("
               + porcentaje(ancla["efecto_pct"]) + " más), todos los meses."),
        efecto_mesada_mes=ancla["efecto_mes"],
        efecto_pct=ancla["efecto_pct"],
        detalle=detalle,
        supuesto=("Un solo aumento del 10% que arranca hoy y se mantiene hasta "
                  "la pensión, en pesos de hoy (no es un 10% cada año). El "
                  "salario de partida es " + pesos(ibc_hoy) + ", que es el "
                  "IBC del último mes con cotización real."),
        fuente="rpm.py / rais.py, mismo motor del diagnóstico")


def palanca_cerrar_lagunas(caso, regimen, sexo, edad, fecha_calculo, base):
    """Palanca 2: cerrar las lagunas hacia adelante.

    Ojo con qué mide y qué no: esto NO recupera el pasado (eso es la palanca 3),
    mide qué pasa si de aquí en adelante cotiza todos los meses en vez de
    saltarse algunos. Para alguien que viene cotizando el 80% del tiempo, pasar
    al 100% suele valer más que un aumento de sueldo del 20%, y casi nadie lo
    tiene en la cabeza.
    """
    densidad_hoy = base["densidad"]
    if densidad_hoy is None:
        return _no_aplica(
            "cerrar_lagunas", 2, "Cotizar todos los meses",
            "No hay suficiente historia reciente para medir con qué ritmo "
            "viene cotizando.")

    # Si ya cotiza prácticamente todos los meses, no hay laguna que cerrar y
    # ofrecérselo sería decirle que arregle algo que ya está bien.
    if densidad_hoy >= 0.98:
        return _no_aplica(
            "cerrar_lagunas", 2, "Cotizar todos los meses",
            "Ya viene cotizando prácticamente todos los meses (densidad "
            + porcentaje(densidad_hoy) + "): no hay lagunas que cerrar.")

    detalle = []
    for objetivo in DENSIDADES_OBJETIVO:
        # Un objetivo por debajo de lo que ya hace no es una mejora.
        if objetivo <= densidad_hoy:
            continue
        diagnostico = _diagnosticar(caso, regimen, sexo, edad, fecha_calculo,
                                    densidad_futura=objetivo)
        mesada = mesada_de(diagnostico, regimen)
        monto, pct = _delta(base["mesada"], mesada)
        # Cotizar más seguido también adelanta la fecha de pensión, porque las
        # semanas llegan antes. Ese efecto se mide aparte de los pesos.
        detalle.append({"densidad": objetivo, "mesada": mesada,
                        "efecto_mes": monto, "efecto_pct": pct,
                        "fecha_pension": _fecha_pension(diagnostico, regimen)})

    if not detalle or detalle[-1]["efecto_mes"] is None:
        return _no_aplica("cerrar_lagunas", 2, "Cotizar todos los meses",
                          "La calculadora no pudo proyectar la mesada con un "
                          "ritmo de cotización distinto.")

    # Aquí se comunica el escalón MÁS ALTO, al revés que en el sueldo: cerrar
    # del todo las lagunas sí depende de la persona, mientras que el aumento de
    # sueldo depende del empleador. Es una acción que puede tomar sola.
    tope = detalle[-1]
    return _palanca(
        "cerrar_lagunas", 2, "Cotizar todos los meses",
        # "10 de los 12 meses del año" se entiende de inmediato; "el 80% de
        # los meses" obliga a traducir mentalmente. Se dice en meses.
        frase=("Hoy cotizas unos " + str(round(densidad_hoy * 12))
               + " de los 12 meses del año. Si cotizas los 12, tu pensión "
               "mensual sería " + pesos(tope["efecto_mes"]) + " más alta ("
               + porcentaje(tope["efecto_pct"]) + " más), todos los meses."),
        efecto_mesada_mes=tope["efecto_mes"],
        efecto_pct=tope["efecto_pct"],
        detalle=detalle,
        supuesto=("Se compara su ritmo de los últimos 3 años ("
                  + porcentaje(densidad_hoy) + ") contra cotizar sin "
                  "interrupciones de aquí a la pensión, con el mismo salario."),
        fuente="rpm.py / rais.py, mismo motor del diagnóstico")


def edad_de_pension(diagnostico, regimen, caso, edad_hoy):
    """A qué edad se pensionaría esta persona, en años cumplidos.

    Existe para poder decir "trabajar hasta los 63 años" en vez de "trabajar un
    año más". La segunda frase obliga a la persona a hacer la cuenta; la
    primera le pone delante la decisión real. Devuelve None si no se puede
    saber, y entonces quien la use se queda con la frase genérica.
    """
    if regimen == "RAIS":
        # En el RAIS la edad de pensión la fija la ley y el diagnóstico la trae.
        return diagnostico.get("edad_legal")
    # En el RPM la pensión llega cuando se cumplen los DOS requisitos, así que
    # la edad sale de la fecha estimada menos la fecha de nacimiento.
    fecha = diagnostico.get("fecha_pension_estimada")
    nacimiento = (caso.get("afiliado") or {}).get("fecha_nacimiento")
    if not fecha or not nacimiento:
        # Sin fecha de nacimiento se puede aproximar con los meses que faltan.
        return edad_hoy
    dias = (date.fromisoformat(fecha) - date.fromisoformat(nacimiento)).days
    return dias // 365


def _fecha_pension(diagnostico, regimen):
    """La fecha estimada de pensión de un diagnóstico, en texto, o None."""
    if not diagnostico:
        return None
    if regimen == "RPM":
        return diagnostico.get("fecha_pension_estimada")
    # En RAIS el diagnóstico no devuelve una fecha sino los meses que faltan
    # para la edad legal, que es cuando se puede pensionar.
    return diagnostico.get("meses_hasta_edad_legal")


def palanca_recuperar_mora(caso, regimen, sexo, edad, fecha_calculo, base):
    """Palanca 3: recuperar las semanas que el empleador no pagó.

    Esta no es plata nueva de la persona: es plata que alguien más debía. Por
    eso, cuando aplica, suele ser la de mejor relación entre lo que cuesta
    (reclamar) y lo que rinde. El módulo recuperacion.py ya sabía simularla; lo
    que faltaba era que alguien lo llamara.
    """
    try:
        simulacion = recuperacion.simular(caso, sexo, edad=edad,
                                          fecha_calculo=fecha_calculo)
    except Exception as error:
        # Si la simulación falla no se tumba el resto de las palancas: se deja
        # constancia de que esta no se pudo evaluar y se sigue.
        return _no_aplica("recuperar_mora", 3, "Recuperar semanas en mora",
                          "No se pudo simular la recuperación: " + str(error),
                          confianza="baja")

    escenarios = simulacion.get("escenarios") or {}
    if not escenarios:
        return _no_aplica(
            "recuperar_mora", 3, "Recuperar semanas en mora",
            "En la historia laboral no aparecen periodos en mora ni semanas "
            "pendientes de acreditar.")

    # De todos los escenarios recuperables nos quedamos con el que más mueve.
    mejor_clave, mejor_efecto, mejor_mesada = None, None, None
    for clave, escenario in escenarios.items():
        mesada = escenario.get("mesada") if isinstance(escenario, dict) else None
        if mesada is None:
            continue
        monto, _ = _delta(base["mesada"], mesada)
        if monto is not None and (mejor_efecto is None or monto > mejor_efecto):
            mejor_clave, mejor_efecto, mejor_mesada = clave, monto, mesada

    if mejor_efecto is None:
        # Hay algo recuperable pero no se pudo traducir a pesos. Se nombra sin
        # número, que es la regla: nunca un número inventado.
        return _palanca(
            "recuperar_mora", 3, "Recuperar semanas en mora",
            frase=("En tu historia laboral hay periodos en mora o semanas sin "
                   "acreditar. Recuperarlas suma semanas, pero con los datos "
                   "del documento no se puede calcular cuánto sube la mesada."),
            confianza="media",
            supuesto="Se detectó lo recuperable pero no se pudo cuantificar.",
            fuente="recuperacion.py")

    _, pct = _delta(base["mesada"], mejor_mesada)
    return _palanca(
        "recuperar_mora", 3, "Recuperar semanas en mora",
        frase=("Si recuperas las semanas que aparecen en mora, tu mesada sube "
               + pesos(mejor_efecto) + " al mes ("
               + porcentaje(pct) + " más)."),
        efecto_mesada_mes=mejor_efecto,
        efecto_pct=pct,
        detalle=[{"escenario": mejor_clave, "mesada": mejor_mesada}],
        supuesto=("Supone que la reclamación prospera y que la administradora "
                  "acredita las semanas. No supone que el empleador pague "
                  "voluntariamente."),
        fuente="recuperacion.py",
        limite_de_alcance=("Júbilo señala la mora y explica cómo reclamarla. "
                           "No representa a la persona ante la administradora "
                           "ni ante el empleador."))


def palanca_regimen(caso, regimen, sexo, edad, fecha_calculo, base):
    """Palanca 4: quedarte donde estás o trasladarte de régimen.

    LÍMITE DURO. Júbilo NO recomienda el traslado. Muestra los dos escenarios
    con los mismos supuestos y dice que la doble asesoría obligatoria es un
    requisito de ley que esto no reemplaza. Presentarlo como recomendación sería
    meterse en terreno regulado y, peor, arriesgar el patrimonio de alguien con
    una decisión que casi nunca se puede deshacer.
    """
    try:
        comparacion = comparador.comparar(caso, sexo, edad=edad,
                                          fecha_calculo=fecha_calculo)
    except Exception as error:
        return _no_aplica("regimen", 4, "Quedarte o trasladarte de régimen",
                          "No se pudo comparar los dos regímenes: " + str(error),
                          confianza="baja")

    # La llave que trae el veredicto se llama "mesadas" (verificado contra la
    # salida real de comparador.comparar el 2026-09-18, no supuesta).
    veredicto = comparacion.get("mesadas") or {}
    mesada_rpm = veredicto.get("mesada_rpm")
    banda_rais = veredicto.get("mesada_rais_banda")
    if mesada_rpm is None or not banda_rais:
        return _no_aplica("regimen", 4, "Quedarte o trasladarte de régimen",
                          "No hay datos suficientes para comparar los dos "
                          "regímenes con los mismos supuestos.")

    # El efecto se mide contra el régimen en el que YA está la persona. Si está
    # en RAIS, la alternativa es el RPM, y al revés.
    if regimen == "RAIS":
        alternativa, etiqueta = mesada_rpm, "Colpensiones (RPM)"
    else:
        # Del lado del RAIS la mesada es una banda; para medir el efecto se usa
        # su extremo alto, que es el mismo criterio de mesada_de().
        alternativa, etiqueta = max(banda_rais), "tu fondo privado (RAIS)"

    monto, pct = _delta(base["mesada"], alternativa)

    return _palanca(
        "regimen", 4, "Quedarte o trasladarte de régimen",
        frase=("Con los mismos supuestos, en " + etiqueta + " tu mesada sería "
               + pesos(alternativa) + " frente a " + pesos(base["mesada"])
               + " donde estás hoy."),
        efecto_mesada_mes=monto,
        efecto_pct=pct,
        etiqueta_efecto="de diferencia entre los dos regímenes",
        detalle=[{"mesada_rpm": mesada_rpm, "mesada_rais_banda": banda_rais}],
        supuesto=("Los dos regímenes se proyectan con el mismo salario y el "
                  "mismo ritmo de cotización, que es la única forma de que la "
                  "comparación signifique algo."),
        fuente="comparador.py",
        limite_de_alcance=(
            "Júbilo NO recomienda trasladarse ni quedarse: muestra los dos "
            "números. El traslado exige por ley una doble asesoría con las dos "
            "administradoras, y esto no la reemplaza. Además hay ventanas de "
            "tiempo que pueden cerrar la puerta para siempre."))


# ---------------------------------------------------------------------------
# GRUPO 3: las palancas nuevas que Santiago aprobó el 2026-09-18
# ---------------------------------------------------------------------------

def _titulo_aplazar(diagnostico, regimen, caso, edad_hoy):
    """El título de la palanca 7, con la edad concreta si se puede saber.

    "Trabajar un año más" obliga a la persona a hacer la cuenta de hasta
    cuándo. "Trabajar hasta los 63 años" le pone delante la decisión real, que
    es la que va a tomar o no tomar.
    """
    edad_pension = edad_de_pension(diagnostico, regimen, caso, edad_hoy)
    if not edad_pension:
        return "Trabajar un año más"
    return ("Trabajar hasta los " + str(edad_pension + 1)
            + " años (un año más)")


def palanca_aplazar(caso, regimen, sexo, edad, fecha_calculo, base):
    """Palanca 7: trabajar un año más.

    POR QUÉ ES LA MÁS POTENTE, y casi nadie la piensa. En el RAIS empuja por
    tres caminos a la vez: entran más aportes, el saldo que ya tenía rinde más
    tiempo, y la mesada tiene que durar menos años, así que cada peso del saldo
    compra más mesada. Los tres van en la misma dirección.

    EL HALLAZGO QUE OBLIGÓ A CAMBIAR EL DISEÑO (2026-09-18). En el RPM esto
    puede salir NEGATIVO, y no es un error de la calculadora. Pasa cuando se
    juntan dos cosas: la persona ya tiene tantas semanas que su tasa de
    reemplazo está en el tope, así que sumar semanas no le sube nada; y el IBL
    que la ley le liquida es el de TODA LA VIDA (porque es mayor que el de los
    últimos 10 años), mientras su salario de hoy está por debajo de ese
    promedio. Cada mes extra que cotiza diluye el promedio hacia abajo. En el
    caso 04 del set dorado, aplazar 24 meses le BAJA la mesada casi $30.000.

    Por eso esta función mide y deja que el número salga como salga, y quien
    ordena las palancas descarta las negativas. Decirle a esa persona "trabaja
    un año más" sería un consejo que la empobrece.
    """
    detalle = []
    for meses in APLAZAMIENTOS:
        diagnostico = _diagnosticar(caso, regimen, sexo, edad, fecha_calculo,
                                    meses_aplazamiento=meses)
        mesada = mesada_de(diagnostico, regimen)
        monto, pct = _delta(base["mesada"], mesada)
        detalle.append({"meses": meses, "mesada": mesada,
                        "efecto_mes": monto, "efecto_pct": pct})

    # La edad a la que se pensionaría hoy y a la que se pensionaría aplazando:
    # son las dos cifras que hacen concreta esta palanca.
    edad_pension = edad_de_pension(base["diagnostico"], regimen, caso, edad)
    titulo = _titulo_aplazar(base["diagnostico"], regimen, caso, edad)

    ancla = detalle[0]  # Un año, que es el horizonte que la gente se imagina
    if ancla["efecto_mes"] is None:
        return _no_aplica("aplazar", 7, titulo,
                          "La calculadora no pudo proyectar la mesada "
                          "aplazando la pensión.")

    # El caso en el que aplazar EMPOBRECE. No se esconde: se convierte en un
    # aviso, que es información valiosa y poco conocida.
    if ancla["efecto_mes"] < 0:
        return _no_aplica(
            "aplazar", 7, titulo,
            "En tu caso aplazar la pensión NO te conviene: bajaría tu mesada "
            "en " + pesos(abs(ancla["efecto_mes"])) + " al mes. Te liquidan "
            "con el promedio de toda tu vida laboral, que es más alto que lo "
            "que ganas hoy, así que cada mes extra cotizando baja ese promedio.",
            detalle=detalle,
            efecto_mesada_mes=ancla["efecto_mes"],
            efecto_pct=ancla["efecto_pct"],
            fuente="Ley 100 de 1993 art. 21 (el IBL mayor de los dos)")

    if edad_pension:
        frase = ("Hoy te pensionarías a los " + str(edad_pension) + " años. "
                 "Si en vez de eso sigues cotizando hasta los "
                 + str(edad_pension + 1) + ", tu pensión mensual sería "
                 + pesos(ancla["efecto_mes"]) + " más alta ("
                 + porcentaje(ancla["efecto_pct"]) + " más), todos los meses "
                 "y para el resto de tu vida.")
    else:
        frase = ("Si sigues cotizando un año más antes de pensionarte, tu "
                 "pensión mensual sería " + pesos(ancla["efecto_mes"])
                 + " más alta (" + porcentaje(ancla["efecto_pct"]) + " más), "
                 "todos los meses y para el resto de tu vida.")

    return _palanca(
        "aplazar", 7, titulo,
        frase=frase,
        efecto_mesada_mes=ancla["efecto_mes"],
        efecto_pct=ancla["efecto_pct"],
        efecto_meses_pension=APLAZAMIENTOS[0],
        detalle=detalle,
        supuesto=("Supone que sigue cotizando con el mismo salario y el mismo "
                  "ritmo durante ese tiempo extra."),
        fuente="rpm.py / rais.py con meses_aplazamiento")


def palanca_portafolio(caso, regimen, sexo, edad, fecha_calculo, base):
    """Palanca 9: en qué portafolio está tu plata (solo RAIS).

    POR QUÉ ES LA MÁS IMPORTANTE DEL GRUPO. Con el dato primario de la
    Superfinanciera (ene-2015 a ago-2026, el mismo periodo para las cuatro AFP),
    moverse de conservador a mayor riesgo DENTRO de la misma administradora vale
    entre 138 y 209 puntos básicos de rendimiento real al año. Cambiar de
    administradora dentro del mismo portafolio vale entre 18 y 98. O sea que la
    decisión de portafolio pesa entre dos y diez veces más que la de AFP. Sobre
    décadas de capitalización, esa diferencia es la mesada.

    LO QUE LA LEY LE QUITA A LOS MAYORES, Y EL ERROR QUE ESTO TENÍA. A partir de
    cierta edad el saldo se va pasando al fondo conservador de forma
    obligatoria (la convergencia de multifondos). La primera versión de esta
    función se apoyaba solo en la marca `prohibido_por_convergencia` que pone
    rais.py, y eso estaba mal: esa marca **solo aparece cuando la convergencia
    llega al 100%**, o sea a los 61 años en hombres. Entre los 57 y los 60 la
    ley ya obliga a tener entre el 20% y el 80% del saldo en conservador y la
    marca sigue vacía, así que a esa persona se le mostraba el diferencial
    COMPLETO entre conservador y mayor riesgo como si pudiera mover todo su
    saldo. A los 60 años solo puede mover el 20%: mostrarle el efecto entero es
    prometerle cinco veces lo que puede capturar.

    Por eso aquí, además de respetar la marca, se escala el diferencial por la
    fracción del saldo que de verdad le queda libre, y se le dice cuánta parte
    ya no es suya para escoger. Un número honesto y más pequeño vale más que
    uno grande que no puede alcanzar.
    """
    if regimen != "RAIS":
        return _no_aplica(
            "portafolio", 9, "En qué portafolio está tu plata",
            "Está en Colpensiones (RPM), donde la pensión la define una fórmula "
            "de la ley y no el rendimiento de un fondo: no hay portafolio que "
            "escoger.")

    escenarios = (base["diagnostico"] or {}).get("escenarios") or {}
    # Los perfiles que la ley SÍ le permite hoy, en orden de menos a más riesgo.
    permitidos = [p for p in PERFILES_ESCOGIBLES
                  if p in escenarios
                  and not escenarios[p].get("prohibido_por_convergencia")]

    if len(permitidos) < 2:
        # O la convergencia ya le cerró las opciones, o no hay con qué comparar.
        bloqueados = [p for p in PERFILES_ESCOGIBLES
                      if p in escenarios
                      and escenarios[p].get("prohibido_por_convergencia")]
        motivo = ("Por su edad la ley ya le está pasando el saldo al fondo "
                  "conservador (convergencia de multifondos), así que los "
                  "perfiles de más riesgo no son una opción que pueda escoger."
                  if bloqueados else
                  "No hay suficientes escenarios de fondo para comparar.")
        return _no_aplica("portafolio", 9, "En qué portafolio está tu plata",
                          motivo)

    detalle = []
    for perfil in permitidos:
        mesada = escenarios[perfil].get("mesada")
        detalle.append({
            "perfil": perfil,
            "mesada": mesada,
            "rendimiento_real_observado": rendimiento_de(perfil),
        })

    # El efecto de la palanca: la distancia entre el perfil más defensivo y el
    # más agresivo que la ley le permite. Es el tamaño de la decisión, no una
    # recomendación de tomarla.
    mas_defensivo, mas_agresivo = detalle[0], detalle[-1]
    monto, pct = _delta(mas_defensivo["mesada"], mas_agresivo["mesada"])
    if monto is None:
        return _no_aplica("portafolio", 9, "En qué portafolio está tu plata",
                          "No se pudo calcular la mesada de los distintos "
                          "perfiles de fondo.")

    # Cuánto del saldo puede de verdad mover, según su edad. La convergencia le
    # va congelando una parte en el conservador, y sobre esa parte no decide.
    mezcla = mezcla_obligatoria(sexo, edad) or {}
    obligado_en_conservador = mezcla.get("conservador") or 0.0
    fraccion_libre = max(0.0, 1.0 - obligado_en_conservador)

    if fraccion_libre <= 0:
        return _no_aplica(
            "portafolio", 9, "En qué portafolio está tu plata",
            "Por su edad la ley ya le tiene todo el saldo en el fondo "
            "conservador (convergencia de multifondos): no hay portafolio que "
            "escoger.")

    # El efecto que de verdad puede capturar, no el teórico.
    monto_alcanzable = round(monto * fraccion_libre)
    pct_alcanzable = round(pct * fraccion_libre, 4) if pct is not None else None

    frase = ("Si tu saldo estuviera en el fondo de "
             + mas_agresivo["perfil"].replace("_", " ") + " en vez del "
             + mas_defensivo["perfil"].replace("_", " ") + ", tu pensión "
             "mensual sería " + pesos(monto_alcanzable) + " más alta. Es la "
             "misma plata tuya, en dos portafolios distintos.")
    if obligado_en_conservador > 0:
        # Se dice en voz alta, porque es la diferencia entre una cifra honesta
        # y una promesa que la ley no le deja cumplir.
        frase += (" Ten en cuenta que por tu edad la ley ya te obliga a tener "
                  "el " + porcentaje(obligado_en_conservador) + " de tu saldo "
                  "en el fondo conservador, así que esa parte no la escoges "
                  "tú. La cifra de arriba ya descuenta eso: sobre el saldo "
                  "completo la diferencia sería " + pesos(monto) + ".")

    return _palanca(
        "portafolio", 9, "En qué portafolio está tu plata",
        frase=frase,
        efecto_mesada_mes=monto_alcanzable,
        efecto_pct=pct_alcanzable,
        etiqueta_efecto="de diferencia en tu pensión mensual",
        detalle=detalle + [{"diferencial_sobre_saldo_completo": monto,
                            "fraccion_del_saldo_que_puede_mover": fraccion_libre,
                            "obligado_en_conservador": obligado_en_conservador}],
        supuesto=("Supone que se mantiene en ese portafolio hasta que la ley lo "
                  "obligue a moverse. Los rendimientos son los observados "
                  "entre enero de 2015 y agosto de 2026, no una promesa."),
        fuente="Superfinanciera, dataset hds9-4524 (dato primario)",
        limite_de_alcance=(
            "Júbilo NO recomienda portafolio: muestra la diferencia y la "
            "persona decide. Más rendimiento pasado viene con más variación "
            "año a año, y quien está cerca de pensionarse tiene menos tiempo "
            "para recuperarse de un mal año."))


def palanca_administradora(caso, regimen, sexo, edad, fecha_calculo, base,
                           perfil_actual=None):
    """Palanca 8: con cuál administradora estás (solo RAIS).

    VA SUBORDINADA A LA 9, Y ESO ES UNA DECISIÓN, NO UN DETALLE. El dato dice
    que la decisión de portafolio pesa entre dos y diez veces más que la de
    administradora. Presentarlas como dos palancas del mismo tamaño invita a la
    persona a optimizar la pequeña y a ignorar la grande. Por eso esta palanca
    solo se calcula DENTRO del perfil en el que ya está, y el reporte la muestra
    después de la 9, nunca antes.

    Y OJO: no existe "la mejor AFP". Depende del perfil. Colfondos es la peor en
    moderado (2,27% real) y la mejor en mayor riesgo (4,13%). Cualquier frase
    del tipo "cámbiate a X" sin decir el portafolio es sencillamente falsa.
    """
    if regimen != "RAIS":
        return _no_aplica(
            "administradora", 8, "Con cuál administradora estás",
            "Está en Colpensiones (RPM), que es una sola entidad pública: no "
            "hay administradoras entre las cuales escoger.")

    # Sin saber el perfil no se puede comparar, porque la comparación solo tiene
    # sentido dentro de un mismo portafolio.
    perfil = perfil_actual or "moderado"
    extremos = mejor_y_peor_afp(perfil)
    if not extremos:
        return _no_aplica("administradora", 8, "Con cuál administradora estás",
                          "No hay datos de rendimiento para ese perfil.")

    nombre_peor, valor_peor, nombre_mejor, valor_mejor = extremos
    brecha = valor_mejor - valor_peor

    return _palanca(
        "administradora", 8, "Con cuál administradora estás",
        frase=("Dentro del fondo " + perfil.replace("_", " ") + ", la "
               "administradora que mejor rindió (" + nombre_mejor + ", "
               + porcentaje(valor_mejor, 2) + " real al año) y la que peor ("
               + nombre_peor + ", " + porcentaje(valor_peor, 2) + ") están a "
               + porcentaje(brecha, 2) + " de distancia."),
        # A propósito sin efecto en pesos: ponerle un número de mesada la
        # pondría a competir de tú a tú con la palanca 9, que es diez veces más
        # grande. El orden importa más que la cifra.
        efecto_mesada_mes=None,
        efecto_pct=None,
        # Sin cifra no hay etiqueta que poner: el reporte no debe imprimir
        # "más de pensión al mes" al lado de una casilla vacía.
        etiqueta_efecto=None,
        detalle=[{"perfil": perfil,
                  "por_afp": dict(RENDIMIENTO_REAL_POR_AFP[perfil])}],
        confianza="alta",
        supuesto=("Rendimiento real anualizado de enero de 2015 a agosto de "
                  "2026, los mismos 140 cierres mensuales para las cuatro "
                  "administradoras. Es rentabilidad del fondo, no del afiliado."),
        fuente="Superfinanciera, dataset hds9-4524 (dato primario)",
        limite_de_alcance=ADVERTENCIA_POR_AFP)


def palanca_corregir_historia(caso, regimen, sexo, edad, fecha_calculo, base):
    """Palanca 10: corregir la historia laboral.

    No es plata nueva: son semanas que la persona YA cotizó y que están mal
    registradas en el documento. Por eso suele tener la mejor relación entre
    esfuerzo y resultado de todo el banco.

    LA REGLA QUE MANDA AQUÍ ES NO DAÑAR LA CONFIANZA. Decirle a alguien "te
    faltan semanas" cuando no es cierto es peor que no decirle nada. Por eso
    esta palanca nunca afirma que hay un error: dice qué hay que ir a verificar,
    y solo muestra lo que el detector marcó con confianza alta o media.
    """
    if anomalias is None:
        return _no_aplica("corregir_historia", 10, "Corregir tu historia laboral",
                          "El detector de anomalías no está disponible.",
                          confianza="baja")

    try:
        hallazgos = anomalias.detectar(caso)
    except Exception as error:
        return _no_aplica("corregir_historia", 10, "Corregir tu historia laboral",
                          "No se pudo revisar la historia laboral: " + str(error),
                          confianza="baja")

    lista = [a for a in (hallazgos.get("anomalias") or [])
             if a.get("confianza") in ("alta", "media")]
    if not lista:
        return _no_aplica(
            "corregir_historia", 10, "Corregir tu historia laboral",
            "Se revisó la historia laboral y no aparecen inconsistencias que "
            "valga la pena reclamar.")

    semanas = hallazgos.get("semanas_en_juego_total")
    # Solo se cuantifica en pesos si se sabe cuántas semanas están en juego.
    # Si no se sabe, se nombra sin número, que es la regla del proyecto.
    # El plural bien puesto: "1 cosa(s)" se lee a máquina y resta confianza.
    cuantas = (str(len(lista)) + " cosas" if len(lista) > 1 else "una cosa")
    if semanas:
        frase = ("En tu historia laboral hay " + cuantas + " que vale la pena "
                 "verificar, y están en juego cerca de "
                 + str(round(semanas, 1)).replace(".", ",")
                 + " semanas que ya cotizaste.")
    else:
        frase = ("En tu historia laboral hay " + cuantas + " que vale la pena "
                 "verificar con tu administradora.")

    return _palanca(
        "corregir_historia", 10, "Corregir tu historia laboral",
        frase=frase,
        efecto_mesada_mes=None,
        detalle=lista,
        confianza="media",
        supuesto=("Son señales para verificar, no errores confirmados. Lo que "
                  "manda es lo que diga la administradora cuando se le "
                  "pregunte formalmente."),
        fuente="anomalias.py",
        limite_de_alcance=("Júbilo señala qué revisar. La corrección se pide a "
                           "la administradora y, si no responde, por derecho "
                           "de petición."))


def palanca_densidad_ultimo_tramo(caso, regimen, sexo, edad, fecha_calculo, base):
    """Palanca 12: lo que cotizas ahora pesa más que nunca (solo RPM).

    LA MECÁNICA, que es fina y muy poco conocida. En el RPM la pensión se
    liquida sobre el promedio de los 10 años ANTERIORES A LA PENSIÓN. Para
    alguien a quien le faltan 4 años, esos 4 años futuros son el 40% del
    promedio con el que le van a liquidar la pensión del resto de su vida. Lo
    que cotice ahora pesa desproporcionadamente, y lo que deje de cotizar
    también.

    CUÁNDO NO SE OFRECE, y aquí está el matiz que casi se nos pasa. Si a la
    persona la liquidan con el IBL de TODA LA VIDA (porque le resulta mayor que
    el de los últimos 10 años, Ley 100 art. 21), esta palanca se invierte: la
    ventana de 10 años deja de mandar, y cotizar ahora por debajo de su promedio
    histórico le BAJA la mesada. Ofrecérsela a esa persona sería un consejo que
    la empobrece, así que se descarta y se le explica por qué.
    """
    if regimen != "RPM":
        return _no_aplica(
            "densidad_ultimo_tramo", 12, "Lo que cotizas ahora pesa más",
            "Aplica al RPM (Colpensiones), donde la pensión se liquida sobre "
            "el promedio de los últimos 10 años. En el RAIS la mesada sale del "
            "saldo, no de un promedio.")

    diagnostico = base["diagnostico"] or {}
    escenario = diagnostico.get("escenario_sigue_cotizando") or {}
    fecha_pension = diagnostico.get("fecha_pension_estimada")
    if not fecha_pension:
        return _no_aplica("densidad_ultimo_tramo", 12,
                          "Lo que cotizas ahora pesa más",
                          "No hay una fecha de pensión estimada con la que "
                          "medir cuánto falta.")

    # Cuántos meses de la ventana de 10 años todavía están por cotizar.
    meses_al_retiro = rpm.meses_entre(fecha_calculo,
                                      date.fromisoformat(fecha_pension))
    if meses_al_retiro <= 0:
        return _no_aplica("densidad_ultimo_tramo", 12,
                          "Lo que cotizas ahora pesa más",
                          "Ya cumple los requisitos: la ventana del IBL ya "
                          "está prácticamente cerrada.")
    if meses_al_retiro > 120:
        return _no_aplica(
            "densidad_ultimo_tramo", 12, "Lo que cotizas ahora pesa más",
            "Le faltan más de 10 años para pensionarse, así que toda la "
            "ventana del IBL todavía está por cotizar y este efecto no lo "
            "distingue de cotizar normal.")

    # El caso en que la palanca se invierte: manda el IBL de toda la vida.
    if escenario.get("ibl_usado") == "toda_la_vida":
        return _no_aplica(
            "densidad_ultimo_tramo", 12, "Lo que cotizas ahora pesa más",
            "A usted la ley lo liquida con el promedio de TODA su vida laboral, "
            "que le resulta mayor que el de los últimos 10 años. Eso es bueno, "
            "pero significa que la ventana de 10 años no manda en su caso: "
            "cotizar ahora por debajo de su promedio histórico le bajaría la "
            "mesada en vez de subirla.",
            fuente="Ley 100 de 1993 art. 21")

    # El peso del futuro dentro de la ventana: la cifra que hace entender la
    # palanca de un vistazo.
    peso_futuro = round(meses_al_retiro / 120, 3)

    # SE MIDE SOLO LA DENSIDAD, Y ESO ES UNA CORRECCIÓN DE MECE. El primer
    # intento movía la densidad Y el salario a la vez, y el resultado se
    # mostraba junto a la palanca 1 ("que te suban el sueldo"), que ya cuenta
    # el salario. La persona veía dos cifras que se solapaban sin saberlo y
    # podía sumarlas. Ahora cada palanca mide una sola cosa: la 1 el salario,
    # esta el ritmo de cotización. Lo que esta aporta y la 2 no es el ARGUMENTO,
    # que es lo que la hace valiosa cerca del retiro.
    nuevo = _diagnosticar(caso, regimen, sexo, edad, fecha_calculo,
                          densidad_futura=1.0)
    monto, pct = _delta(base["mesada"], mesada_de(nuevo, regimen))
    if monto is None or monto <= 0:
        return _no_aplica("densidad_ultimo_tramo", 12,
                          "Lo que cotizas ahora pesa más",
                          "Con los supuestos de este tramo la mesada no sube, "
                          "así que no hay nada que ofrecer.")

    return _palanca(
        "densidad_ultimo_tramo", 12, "Lo que cotizas ahora pesa más",
        frase=("Te faltan " + str(meses_al_retiro) + " meses para pensionarte, "
               "y tu pensión se calcula con el promedio de los últimos 10 años. "
               "O sea que lo que cotices de aquí en adelante es el "
               + porcentaje(peso_futuro) + " de ese promedio. Cotizar todos los "
               "meses de aquí a que te pensiones te subiría la mesada "
               + pesos(monto) + " al mes."),
        efecto_mesada_mes=monto,
        efecto_pct=pct,
        detalle=[{"meses_al_retiro": meses_al_retiro,
                  "peso_del_futuro_en_el_ibl": peso_futuro,
                  "ibl_usado": escenario.get("ibl_usado")}],
        supuesto=("Supone cotizar sin interrupciones durante el tramo que "
                  "falta, con el mismo salario de hoy."),
        fuente="Ley 100 de 1993 art. 21; rpm.py")


# ---------------------------------------------------------------------------
# GRUPO 2: las palancas que necesitan un dato que la persona no ha dado
# ---------------------------------------------------------------------------
# Decisión de Santiago del 2026-09-18: nada de cuestionario al principio. La
# pregunta aparece cuando la palanca se vuelve relevante. Por eso estas
# funciones no preguntan nada: devuelven la palanca marcada con el dato que le
# falta y la pregunta exacta, y quien conversa decide cuándo hacerla.

def palanca_aportes_voluntarios(caso, regimen, sexo, edad, fecha_calculo, base,
                                datos):
    """Palanca 5: aportes voluntarios.

    EL ERROR DE SEGMENTO QUE HAY QUE EVITAR. Ofrecerle aportes voluntarios a
    quien no tiene con qué es exactamente igual de malo que ofrecerle BEPS a
    quien sí tiene. Por eso esta palanca no se calcula hasta que la persona haya
    dicho que le sobra algo, y esa pregunta no se hace antes de tiempo porque es
    incómoda y solo sirve para esto.
    """
    if datos.get("tiene_capacidad_de_pago") is None:
        return _palanca(
            "aportes_voluntarios", 5, "Aportes voluntarios",
            aplica=False,
            motivo_no_aplica="Falta saber si le sobra algo para ahorrar.",
            requiere_dato="tiene_capacidad_de_pago",
            pregunta=("¿Te queda algo de dinero libre cada mes después de tus "
                      "gastos? Te lo pregunto solo para saber si vale la pena "
                      "que miremos el ahorro voluntario."))

    if not datos["tiene_capacidad_de_pago"]:
        return _no_aplica(
            "aportes_voluntarios", 5, "Aportes voluntarios",
            "No tiene excedente para ahorrar. Ofrecerle aportes voluntarios "
            "aquí sería un error de segmento.")

    # El monto: el que dijo la persona, o el de referencia declarado como tal.
    aporte = datos.get("aporte_mensual_posible") or APORTE_VOLUNTARIO_DE_REFERENCIA
    es_supuesto = not datos.get("aporte_mensual_posible")

    diagnostico = base["diagnostico"] or {}
    meses = diagnostico.get("meses_hasta_edad_legal")
    if regimen == "RPM":
        return _no_aplica(
            "aportes_voluntarios", 5, "Aportes voluntarios",
            "Está en Colpensiones (RPM), donde la mesada la define una fórmula "
            "de la ley: aportar de más a la cuenta no la sube. El ahorro "
            "voluntario en un fondo aparte sigue siendo posible, pero es "
            "ahorro, no pensión.")
    if not meses:
        return _no_aplica("aportes_voluntarios", 5, "Aportes voluntarios",
                          "No hay horizonte de proyección con el que calcular "
                          "el efecto del aporte.")

    try:
        evaluacion = av.evaluar_aporte_voluntario(
            regimen, meses,
            ingreso_anual=datos.get("ingreso_anual"),
            aporte_mensual=aporte,
            destino="obligatoria")
    except Exception as error:
        return _no_aplica("aportes_voluntarios", 5, "Aportes voluntarios",
                          "No se pudo evaluar el aporte: " + str(error),
                          confianza="baja")

    # OJO CON ESTO, que es donde es fácil equivocarse. evaluar_aporte_voluntario
    # NO devuelve una mesada: devuelve el CAPITAL extra que la persona tendría
    # al final. Convertir capital en mesada es un paso aparte, y hay que hacerlo
    # con el mismo factor de conversión que usa el resto del diagnóstico, o el
    # número no sería comparable con el de las otras palancas.
    proyeccion = evaluacion.get("proyeccion") or {}
    # Capital que suma el aporte, YA DESCONTADA la comisión de administración.
    # Se usa el neto y no el bruto a propósito: la comisión se la come de verdad
    # y en este caso llegó a ser el 22,7% del capital final.
    capital_extra = proyeccion.get("capital_final")

    efecto = None
    banda = None
    if capital_extra:
        # UN ERROR QUE CASI SE VA ASÍ, y que vale la pena dejar escrito. El
        # primer intento pasó `rais.extremos()` a `mesada_adicional_en_banda()`.
        # Compila, corre y no avisa nada, pero `extremos()` devuelve TASAS DE
        # INTERÉS (0,04 y -0,009) y esa función espera FACTORES DE CONVERSIÓN.
        # Dividir el capital entre 0,04 dio una mesada de $6.094 millones al
        # mes. Moraleja, la misma del aviso de arriba: verificar siempre qué
        # devuelve de verdad la función que se llama, no lo que sugiere su
        # nombre. Lo correcto es `banda_mesada`, que hace la conversión entera.
        anios = diagnostico.get("anios_a_financiar")
        anio = diagnostico.get("anio_pension") or fecha_calculo.year
        if anios:
            banda = rais.banda_mesada(capital_extra, anios, sexo, anio)
            # Se comunica el extremo optimista, que es el mismo criterio de
            # mesada_de(): así esta palanca es comparable con las demás.
            if isinstance(banda, dict):
                efecto = banda.get("optimista") or banda.get("mesada_optimista")
            elif isinstance(banda, (list, tuple)) and banda:
                efecto = max(banda)
            # Se redondea igual que todas las demás. Las otras palancas pasan
            # por _delta(), que ya redondea; esta sale directa de banda_mesada
            # y venía con decimales, lo que la hacía incomparable con el resto
            # y ensuciaba cualquier prueba que comparara cifras exactas.
            if efecto is not None:
                efecto = round(efecto)

    if efecto is None:
        return _no_aplica("aportes_voluntarios", 5, "Aportes voluntarios",
                          "No se pudo convertir el capital del aporte en "
                          "mesada con el factor de conversión del caso.",
                          confianza="baja")

    frase = ("Si aportas " + pesos(aporte) + " al mes de forma voluntaria a tu "
             "cuenta, tu mesada subiría " + pesos(efecto) + " al mes.")
    if es_supuesto:
        frase += " (Tomé " + pesos(aporte) + " como ejemplo; dime tu monto y lo recalculo.)"

    # La comisión de administración se dice siempre que sea material. Es la
    # letra chica que la persona se entera tarde, y callarla mientras se le
    # muestra el beneficio sería vender el producto, no asesorarla.
    comision_pct = proyeccion.get("comision_sobre_capital_pct")
    if comision_pct and comision_pct >= 5:
        frase += (" Ten en cuenta que la comisión de administración se llevaría "
                  "cerca del " + str(comision_pct).replace(".", ",") + "% de "
                  "ese capital, y eso ya está descontado en la cifra.")

    # El ahorro tributario solo se puede calcular si se sabe el ingreso anual.
    ahorro = ((evaluacion.get("beneficio_tributario_primer_anio") or {})
              .get("ahorro_en_impuestos"))
    if ahorro:
        frase += (" Además te ahorrarías " + pesos(ahorro) + " de impuesto de "
                  "renta este año.")
        pregunta_pendiente = None
        dato_pendiente = None
    else:
        pregunta_pendiente = ("¿Cuánto ganas al año, más o menos? Es solo para "
                              "calcular cuánto impuesto de renta te ahorrarías.")
        dato_pendiente = "ingreso_anual"

    return _palanca(
        "aportes_voluntarios", 5, "Aportes voluntarios",
        frase=frase,
        efecto_mesada_mes=efecto,
        detalle=[{"aporte_mensual": aporte,
                  "capital_extra_neto_de_comision": capital_extra,
                  "mesada_adicional_banda": banda,
                  "ahorro_tributario_primer_anio": ahorro,
                  "comision_sobre_capital_pct": comision_pct}],
        requiere_dato=dato_pendiente,
        pregunta=pregunta_pendiente,
        supuesto=("Supone que aporta ese monto todos los meses hasta "
                  "pensionarse y que no retira antes de tiempo."),
        fuente="aportes_voluntarios.py; ET art. 55 y 126-1",
        limite_de_alcance=(
            "Júbilo explica la regla tributaria y las condiciones de "
            "permanencia. No recomienda administradora, fondo ni portafolio."))


def palanca_sobrecotizar(caso, regimen, sexo, edad, fecha_calculo, base, datos):
    """Palanca 6: cotizar sobre una base más alta (solo independientes).

    A un asalariado esto NO se le ofrece, y el motivo es sencillo: su IBC lo
    fija su salario, no lo escoge él. El módulo aportes_voluntarios.py ya lo
    sabía y lo decía con esas palabras; aquí se respeta.
    """
    if datos.get("es_independiente") is None:
        return _palanca(
            "sobrecotizar", 6, "Cotizar sobre una base más alta",
            aplica=False,
            motivo_no_aplica="Falta saber si es asalariado o independiente.",
            requiere_dato="es_independiente",
            pregunta=("¿Trabajas como empleado con nómina o por tu cuenta? Lo "
                      "pregunto porque cambia qué puedes hacer con tu base de "
                      "cotización."))

    if not datos["es_independiente"]:
        return _no_aplica(
            "sobrecotizar", 6, "Cotizar sobre una base más alta",
            "Es asalariado: su IBC lo fija su salario, no lo escoge. Para él "
            "la palanca equivalente es que le suban el sueldo.")

    ibc_hoy = base["ibc_actual"]
    if not ibc_hoy:
        return _no_aplica("sobrecotizar", 6, "Cotizar sobre una base más alta",
                          "No hay una base de cotización reciente con la que "
                          "comparar.")

    # El independiente cotiza sobre el 40% de su ingreso por defecto. Subir al
    # 60% es el escalón que se evalúa: sube la base la mitad.
    nueva_base = ibc_hoy * 1.5
    diagnostico = _diagnosticar(caso, regimen, sexo, edad, fecha_calculo,
                                ibc_futuro=nueva_base)
    monto, pct = _delta(base["mesada"], mesada_de(diagnostico, regimen))
    if monto is None:
        return _no_aplica("sobrecotizar", 6, "Cotizar sobre una base más alta",
                          "No se pudo proyectar la mesada con una base mayor.")

    # Lo que le costaría al mes, que es la mitad de la decisión y casi nunca se
    # dice. Una palanca sin su costo es media palanca.
    import costo_y_retorno
    costo_antes = costo_y_retorno.aporte_mensual(ibc_hoy)["total"]
    costo_despues = costo_y_retorno.aporte_mensual(nueva_base)["total"]
    costo_extra = costo_despues - costo_antes

    return _palanca(
        "sobrecotizar", 6, "Cotizar sobre una base más alta",
        frase=("Si cotizas sobre " + pesos(nueva_base) + " en vez de "
               + pesos(ibc_hoy) + ", tu mesada sube " + pesos(monto)
               + " al mes y te cuesta " + pesos(costo_extra) + " más al mes "
               "mientras cotizas."),
        efecto_mesada_mes=monto,
        efecto_pct=pct,
        detalle=[{"ibc_antes": round(ibc_hoy), "ibc_despues": round(nueva_base),
                  "costo_mensual_extra": round(costo_extra)}],
        supuesto=("Supone que su ingreso respalda esa base y que la mantiene "
                  "hasta pensionarse."),
        fuente="costo_y_retorno.py; rpm.py / rais.py",
        limite_de_alcance=(
            "Subir la base de golpe justo antes de pensionarse es zona gris "
            "frente a la administradora. Júbilo no la resuelve: deriva a "
            "abogado pensional. Y el IBL se calcula sobre 10 años o toda la "
            "vida laboral si resulta superior (Ley 100 art. 21), así que subir "
            "la base tres años no mueve tanto el promedio."))


# ---------------------------------------------------------------------------
# El segmento al que ninguna palanca le sirve, y que hay que nombrar
# ---------------------------------------------------------------------------

def _mesada_con_aporte_extra(caso, sexo, edad, fecha_calculo, diagnostico,
                             aporte_extra):
    """Vuelve a correr la calculadora metiendole X pesos extra a la cuenta cada mes.

    COMO SE METE EL APORTE. La calculadora no tiene un parametro que diga
    "ademas aporta tanto al mes": lo que tiene es el IBC futuro, y de cada peso
    de IBC entran a la cuenta 11,5 centavos, ajustados por la densidad con la
    que la persona cotiza. Asi que se hace la cuenta al reves: se traduce el
    aporte extra en el IBC que lo produciria, y se corre el diagnostico con ese
    IBC. El numero sale entero de la calculadora, no de una formula aparte, que
    es la regla dura de este modulo.

    Devuelve (mesada, salida, saldo_proyectado) del escenario que le aplica.
    """
    ibc_base = diagnostico.get("ibc_futuro_supuesto") or 0
    densidad = diagnostico.get("densidad_futura_supuesta") or 0
    if not densidad:
        return None, None, None
    ibc = ibc_base + aporte_extra / (APORTE_A_CUENTA_RAIS * densidad)
    nuevo = _diagnosticar(caso, "RAIS", sexo, edad, fecha_calculo,
                          ibc_futuro=ibc)
    if nuevo.get("error"):
        return None, None, None
    escenario = ((nuevo.get("escenarios") or {})
                 .get(escenario_aplicable(nuevo)) or {})
    return (escenario.get("mesada"), escenario.get("salida"),
            escenario.get("saldo_proyectado"))


def _aporte_minimo_que_logra(correr, condicion):
    """El aporte mensual mas pequeno que cumple la condicion, por biseccion.

    `correr` es la funcion que devuelve la mesada de un aporte, y `condicion`
    dice si esa mesada ya sirve. Primero se dobla el aporte hasta encontrar uno
    que si sirva (para saber entre que dos numeros buscar) y despues se parte el
    intervalo por la mitad 40 veces. Devuelve None si ni con el techo se logra.
    """
    alto = 100000.0
    encontrado = False
    while alto <= TECHO_DE_BUSQUEDA_MENSUAL:
        mesada = correr(alto)
        if mesada is not None and condicion(mesada):
            encontrado = True
            break
        alto *= 2
    if not encontrado:
        return None
    bajo = 0.0
    for _ in range(PASOS_DE_BUSQUEDA):
        medio = (bajo + alto) / 2
        mesada = correr(medio)
        if mesada is not None and condicion(mesada):
            alto = medio
        else:
            bajo = medio
    return alto


def valle_de_la_garantia_minima(caso, sexo, edad, fecha_calculo, diagnostico):
    """Los dos caminos de quien esta en el piso de la garantia, con numeros.

    EL CONCEPTO, que es una idea de producto de Santiago. La garantia de
    pension minima crea un VALLE de esfuerzo desperdiciado. Mientras el capital
    de la persona no financie mas que un salario minimo, el Estado le completa
    hasta ese minimo, y entonces cada peso extra que ahorre DENTRO del valle no
    le sube la mesada ni un centavo: el retorno marginal es exactamente cero.
    El retorno solo vuelve cuando junta lo suficiente para SALTAR el valle
    entero y pensionarse por su propio capital, por encima del umbral del 110%
    del salario minimo. Decirle "ahorra un poco mas" a quien esta en el fondo
    del valle es pedirle que regale plata.

    POR ESO ESTO NO ES UN CONSEJO, SON DOS CAMINOS CON PRECIO:
      1. Aceptar el minimo: no hacer esfuerzo extra y dejar que el Estado
         complete. Se cuantifica cuanta plata estaria botando si aportara de
         mas sin llegar a saltar.
      2. Saltar el valle: cuanto tendria que aportar cada mes, de aqui a su
         edad de pension, para superar el umbral con margen.

    El numero que convierte esto en una decision es el segundo. Si son
    $200.000 al mes mucha gente lo considera; si son $2 millones la respuesta
    es obvia y lo util es que deje de perder plata hoy.

    Los dos numeros se encuentran corriendo la calculadora una y otra vez
    (biseccion), nunca estimando: es la regla dura del banco de palancas.

    Devuelve None si no se puede calcular (falta el caso, o la persona ya
    cumplio la edad de pension y no le quedan meses por delante).
    """
    if not caso or not sexo or not diagnostico:
        return None
    meses = diagnostico.get("meses_hasta_edad_legal")
    if not meses or meses <= 0:
        return None

    clave = escenario_aplicable(diagnostico)
    escenario = (diagnostico.get("escenarios") or {}).get(clave) or {}
    mesada_piso = escenario.get("mesada")
    saldo_piso = escenario.get("saldo_proyectado")
    if mesada_piso is None:
        return None

    smlmv = SMLMV[max(SMLMV)]
    # La meta: superar el umbral del 110% del salario minimo, y con margen.
    mesada_objetivo = CAPITAL_MINIMO_PCT * smlmv * (1 + MARGEN_PARA_SALTAR_EL_VALLE)

    def mesada_de_aporte(aporte):
        return _mesada_con_aporte_extra(caso, sexo, edad, fecha_calculo,
                                        diagnostico, aporte)[0]

    # CAMINO 1. Hasta donde puede aportar sin que le suba la mesada ni un peso.
    # Es el borde del fondo plano del valle, y sale de la calculadora: es el
    # aporte mas pequeno con el que la mesada por fin se mueve, menos nada.
    aporte_que_mueve = _aporte_minimo_que_logra(mesada_de_aporte,
                                                lambda m: m > mesada_piso)
    aporte_sin_efecto = (round(aporte_que_mueve) - 1
                         if aporte_que_mueve is not None else None)
    desperdicio = (round(aporte_sin_efecto * meses)
                   if aporte_sin_efecto is not None else None)

    # CAMINO 2. El aporte mensual que si la saca del valle, con margen.
    aporte_requerido = _aporte_minimo_que_logra(mesada_de_aporte,
                                                lambda m: m >= mesada_objetivo)
    mesada_lograda = salida_lograda = saldo_logrado = None
    if aporte_requerido is not None:
        # Se redondea HACIA ARRIBA al peso ANTES de calcular la mesada que se
        # le va a mostrar. El numero que se le dice a la persona tiene que ser
        # exactamente el que produce esa mesada: redondear hacia abajo la
        # dejaria un peso por debajo del objetivo y la cifra dejaria de ser
        # reproducible corriendo la calculadora con lo que se le pidio.
        aporte_requerido = float(math.ceil(aporte_requerido))
        mesada_lograda, salida_lograda, saldo_logrado = _mesada_con_aporte_extra(
            caso, sexo, edad, fecha_calculo, diagnostico, aporte_requerido)

    ingreso_hoy = diagnostico.get("ibc_actual")
    pct_del_ingreso = (round(aporte_requerido / ingreso_hoy, 3)
                       if aporte_requerido and ingreso_hoy else None)
    # ALCANZABLE O NO. No es una opinion: es el aporte requerido contra lo que
    # la persona gana hoy. Si pasa del limite, se le dice con el numero en la
    # mano en vez de ofrecerle un camino que no existe.
    alcanzable = bool(aporte_requerido is not None
                      and pct_del_ingreso is not None
                      and pct_del_ingreso <= LIMITE_ESFUERZO_RAZONABLE)

    # El IBC equivalente, para quien piensa en sueldo y no en aportes.
    ibc_requerido = None
    if aporte_requerido is not None:
        densidad = diagnostico.get("densidad_futura_supuesta") or 0
        base_ibc = diagnostico.get("ibc_futuro_supuesto") or 0
        if densidad:
            ibc_requerido = round(base_ibc
                                  + aporte_requerido / (APORTE_A_CUENTA_RAIS * densidad))

    anios = round(meses / 12, 1)
    anios_texto = str(anios).replace(".", ",")

    camino_1 = {
        "titulo": "Aceptar el mínimo",
        "frase": ("Hoy tu mesada es " + pesos(mesada_piso) + " y la fija la "
                  "garantía, no tu ahorro. Puedes aportar hasta "
                  + pesos(aporte_sin_efecto) + " al mes durante los próximos "
                  + anios_texto + " años, poner " + pesos(desperdicio)
                  + " de tu bolsillo, y tu mesada seguiría siendo exactamente "
                  + pesos(mesada_piso) + ". Ese esfuerzo no te compra nada."
                  if aporte_sin_efecto is not None else
                  "Tu mesada la fija la garantía, no tu ahorro: aportar de más "
                  "sin salir de la garantía no te la sube."),
        "aporte_maximo_sin_efecto_mes": aporte_sin_efecto,
        "plata_que_botaria": desperdicio,
        "mesada_si_lo_hace": mesada_piso,
        "retorno_marginal": 0,
    }

    if aporte_requerido is None:
        frase_2 = ("Con tus números no encontré un aporte mensual que te saque "
                   "de la garantía antes de tu edad de pensión.")
    elif alcanzable:
        frase_2 = ("Para salir de la garantía necesitas aportar "
                   + pesos(round(aporte_requerido)) + " al mes durante "
                   + anios_texto + " años (el "
                   + porcentaje(pct_del_ingreso) + " de lo que ganas hoy). "
                   "Con eso tu mesada pasaría de " + pesos(mesada_piso)
                   + " a " + pesos(mesada_lograda) + ", o sea "
                   + pesos(mesada_lograda - mesada_piso) + " más al mes, y "
                   "dejaría de depender de que califiques a la garantía.")
    else:
        frase_2 = ("Saltar la garantía te exigiría aportar "
                   + pesos(round(aporte_requerido)) + " al mes durante "
                   + anios_texto + " años, el "
                   + porcentaje(pct_del_ingreso) + " de lo que ganas hoy. No "
                   "es un camino real para ti, y prefiero decírtelo con el "
                   "número que ofrecerte una esperanza falsa.")

    camino_2 = {
        "titulo": "Saltar el valle",
        "alcanzable": alcanzable,
        "frase": frase_2,
        "aporte_mensual_requerido": (round(aporte_requerido)
                                     if aporte_requerido is not None else None),
        "aporte_como_pct_del_ingreso_hoy": pct_del_ingreso,
        "ibc_equivalente_requerido": ibc_requerido,
        "meses_de_esfuerzo": meses,
        "capital_adicional_requerido": (round(saldo_logrado - saldo_piso)
                                        if saldo_logrado and saldo_piso else None),
        "mesada_si_lo_logra": mesada_lograda,
        "salto_en_la_mesada": (mesada_lograda - mesada_piso
                               if mesada_lograda is not None else None),
        "salida_si_lo_logra": salida_lograda,
    }

    if aporte_requerido is None:
        veredicto = ("Lo sensato es no poner un peso de más en la cuenta y "
                     "concentrarse en asegurar las semanas de la garantía.")
    elif alcanzable:
        veredicto = ("O llegas a " + pesos(round(aporte_requerido))
                     + " al mes o no pones nada: cualquier cifra intermedia es "
                     "plata que sale de tu bolsillo y no vuelve como mesada.")
    else:
        veredicto = ("El camino que sí te sirve es el primero: no aportar de "
                     "más y asegurar las semanas. Todo lo que pongas por "
                     "debajo de " + pesos(round(aporte_requerido))
                     + " al mes lo estarías regalando.")

    return {
        "que_es_el_valle": (
            "Mientras tu capital no financie más que un salario mínimo, la "
            "garantía te completa hasta ese mínimo. Por eso ahorrar más dentro "
            "de esa zona no te sube la mesada: solo cuando superas el umbral "
            "del 110% del salario mínimo vuelves a ganar algo por cada peso."),
        "mesada_hoy": mesada_piso,
        "piso_smlmv": smlmv,
        "mesada_umbral": round(CAPITAL_MINIMO_PCT * smlmv),
        "mesada_objetivo_con_margen": round(mesada_objetivo),
        "margen_exigido": MARGEN_PARA_SALTAR_EL_VALLE,
        "camino_1_aceptar_el_minimo": camino_1,
        "camino_2_saltar_el_valle": camino_2,
        "veredicto": veredicto,
        "supuesto": ("Supone que el aporte extra entra a la cuenta todos los "
                     "meses hasta la edad de pensión, en pesos de hoy, con el "
                     "rendimiento del escenario que le aplica. Lo razonable se "
                     "mide contra su ingreso de hoy: por encima de "
                     + porcentaje(LIMITE_ESFUERZO_RAZONABLE)
                     + " el salto se declara inalcanzable."),
        "fuente": "rais.py corrido por bisección; Ley 100 de 1993 art. 64 y 65",
    }


def aviso_de_segmento(diagnostico, regimen, caso=None, sexo=None, edad=None,
                      fecha_calculo=None):
    """Detecta a la persona a la que la garantía de pensión mínima le manda.

    EL CASO QUE LO DESTAPO (caso 02 del set dorado, 2026-09-18). Se corrieron
    las once palancas y TODAS movieron menos de $20.000 al mes. No era un error:
    a esa persona su capital no le alcanza para mas que el salario minimo, asi
    que la mesada se la fija la Garantia de Pension Minima, que es un PISO. Y
    contra un piso no hay palanca que valga: suba lo que suba su saldo, mientras
    no supere el minimo, su mesada es el minimo.

    LA AMBIGUEDAD QUE HABIA AQUI, y que era un bug (encontrada el 2026-09-19).
    Este aviso se disparaba por la ETIQUETA de salida del diagnostico, y esa
    etiqueta tapa DOS situaciones que no son la misma:

      A. La persona esta de verdad en el piso: su capital financia menos de un
         salario minimo y el Estado le completa. Ahi si es cierto que ninguna
         palanca le mueve la mesada.
      B. Su capital financia MAS de un salario minimo pero todavia no llega al
         umbral del 110% con el que la ley la deja pensionarse por capital
         propio. A ella el Estado no le completa nada, y sus palancas SI le
         suben la mesada peso a peso. Lo que tiene en juego es otra cosa: sigue
         dependiendo de calificar a la garantia por semanas, y esta a un mal
         supuesto de caer al piso.

    Decirle a la segunda "tu mesada la fija la garantia, subir el sueldo no te
    la sube" es falso y le quita la accion a quien si puede mejorar (le pasaba
    al caso 01, con una mesada de $1.916.567 contra un minimo de $1.750.905).
    Por eso cada situacion tiene su propio tipo y su propio mensaje, y no se
    colapsan en uno.

    caso, sexo, edad y fecha_calculo son opcionales y sirven para una sola
    cosa: cuantificar el valle de la garantia (los dos caminos con numeros).
    Sin ellos el aviso sale igual, pero sin esa cuantificacion.

    Devuelve None cuando no es el caso, que es lo normal.
    """
    if regimen != "RAIS" or not diagnostico:
        return None
    clave = escenario_aplicable(diagnostico)
    escenario = (diagnostico.get("escenarios") or {}).get(clave) or {}
    if escenario.get("salida") != "garantia_pension_minima":
        return None

    # Las dos cifras que deciden si califica o no.
    exigidas = diagnostico.get("semanas_gpm")
    proyectadas = diagnostico.get("semanas_proyectadas_edad_legal")
    alcanza = (exigidas is not None and proyectadas is not None
               and proyectadas >= exigidas)

    # LA COMPROBACION QUE FALTABA: no basta la etiqueta, hay que mirar si la
    # mesada esta DE VERDAD clavada en el piso. La calculadora entrega
    # max(mesada propia, salario minimo), asi que una mesada por encima del
    # minimo significa que el piso no le esta dando nada.
    smlmv = SMLMV[max(SMLMV)]
    mesada = escenario.get("mesada")
    umbral = CAPITAL_MINIMO_PCT * smlmv
    en_el_piso = mesada is not None and round(mesada) <= round(smlmv)

    faltan = (round(exigidas - proyectadas, 1)
              if exigidas is not None and proyectadas is not None and not alcanza
              else None)
    # El texto de las semanas es el mismo en las dos situaciones, porque en las
    # dos la pension depende de calificar a la garantia. Se arma una sola vez.
    if alcanza:
        texto_semanas = ("Con el ritmo que llevas sí alcanzas las "
                         + str(exigidas) + " semanas que exige la garantía.")
    else:
        texto_semanas = ("Con el ritmo que llevas NO llegas a las "
                         + str(exigidas) + " semanas que la garantía exige"
                         + (" (te faltarían " + str(faltan) + ")" if faltan else "")
                         + ". Si no llegas no recibes una mesada más pequeña: "
                         "no recibes pensión, te devuelven el saldo.")

    valle = None

    if en_el_piso:
        # SITUACION A: el piso manda y ninguna palanca mueve la mesada.
        tipo = "garantia_pension_minima"
        mensaje = ("Tu mesada la fija la Garantía de Pensión Mínima: con tu "
                   "ahorro, la ley te asegura un salario mínimo. Por eso subir "
                   "el sueldo o ahorrar más no te sube la mesada, porque ya "
                   "estás en el piso garantizado. " + texto_semanas)
        if alcanza:
            que_importa = ("Mantener el ritmo de cotización hasta la edad de "
                           "pensión. Lo que está en juego no es cuánto recibes, "
                           "es que lo recibas.")
        else:
            que_importa = ("Cerrar la brecha de semanas. Para ti esa es la "
                           "única palanca que cambia algo, y cambia todo.")
        por_que = ("La garantía es un piso, no un porcentaje: mientras el "
                   "capital no financie más que un salario mínimo, cualquier "
                   "mejora del saldo se la come el piso y la mesada no cambia.")
        no_mueven = por_que
        # Y aqui es donde el aviso deja de ser solo un aviso: se le ponen
        # numeros a los dos caminos que de verdad tiene.
        valle = valle_de_la_garantia_minima(caso, sexo, edad, fecha_calculo,
                                            diagnostico)
    else:
        # SITUACION B: la etiqueta dice garantia, pero el piso no le esta
        # dando nada. Sus palancas si funcionan. Lo que hay que decirle es que
        # esta en el borde y que su pension todavia depende de calificar.
        tipo = "riesgo_de_caer_en_la_garantia_minima"
        distancia = round(umbral - mesada)
        conservadora = escenario.get("mesada_conservadora")
        mensaje = ("Tu propio capital financia una mesada de " + pesos(mesada)
                   + ", por encima del salario mínimo de " + pesos(smlmv)
                   + ", así que la garantía no te está completando nada y lo "
                   "que hagas sí te sube la mesada. Pero te faltan "
                   + pesos(distancia) + " para llegar al umbral de "
                   + pesos(round(umbral)) + " con el que te pensionarías por "
                   "capital propio, así que tu pensión todavía depende de "
                   "calificar a la garantía. " + texto_semanas)
        if conservadora is not None and round(conservadora) <= round(smlmv):
            mensaje += (" Y con el precio conservador de la renta vitalicia tu "
                        "mesada ya cae al piso de " + pesos(smlmv) + ".")
        que_importa = ("Estás en el borde: te faltan " + pesos(distancia)
                       + " de mesada para salir de la garantía. Las palancas "
                       "sí te mueven la cifra, y además te alejan de la zona "
                       "donde ahorrar más dejaría de servirte.")
        por_que = ("Aquí las palancas sí mueven la mesada: el piso solo manda "
                   "cuando el capital financia menos de un salario mínimo, y "
                   "el tuyo financia más.")
        # La llave vieja se deja en None a proposito: en esta situacion la
        # frase "las palancas no mueven" seria falsa, y una llave con un texto
        # falso adentro es peor que una llave vacia.
        no_mueven = None

    return {
        "tipo": tipo,
        "mensaje": mensaje,
        "lo_que_de_verdad_importa": que_importa,
        "semanas_exigidas": exigidas,
        "semanas_proyectadas": proyectadas,
        "alcanza_el_requisito": alcanza,
        # Las tres cifras que distinguen una situacion de la otra, visibles
        # para que quien lea el aviso no tenga que deducirlas.
        "esta_en_el_piso": en_el_piso,
        "mesada_del_escenario": mesada,
        "piso_smlmv": smlmv,
        "mesada_umbral": round(umbral),
        "por_que_las_palancas_no_mueven": no_mueven,
        # Que hay que entender de las palancas en ESTA situacion. Existe
        # separada de la llave de arriba porque en la situacion B las palancas
        # si mueven, y no hay una sola frase que sirva para las dos.
        "que_pasa_con_las_palancas": por_que,
        # El valle solo viaja cuando la persona esta de verdad en el piso: es
        # ahi donde el retorno marginal es cero y la decision tiene dos
        # caminos. Va en su propia llave y NO entra al ranking de palancas,
        # por la misma razon que el traslado de regimen: ordenarlo por impacto
        # equivale a recomendarlo, y esto es una decision de fondo.
        "valle": valle,
        "fuente": "Ley 100 de 1993 art. 65; Ley 797 de 2003",
    }


# ---------------------------------------------------------------------------
# El director de orquesta
# ---------------------------------------------------------------------------

def _salida_vacia(caso, regimen, fecha_calculo, motivo, preguntas=None):
    """La salida de error, con EXACTAMENTE las mismas llaves que la buena.

    POR QUÉ IMPORTA. `calcular` tenía tres puertas de salida distintas y cada
    una devolvía un diccionario con un juego de llaves diferente: una con seis,
    otra con cuatro y la buena con trece. Quien consume la salida (el reporte,
    el agente) tendría que acordarse de cuál puerta le tocó y protegerse con un
    `.get()` en cada acceso. Tarde o temprano alguien lee una llave que en la
    salida de error no existe y revienta justo cuando ya algo había salido mal,
    que es el peor momento. Con esto, la forma es siempre la misma y lo único
    que cambia es que "error" viene lleno y las listas vienen vacías.
    """
    return {
        "error": motivo,
        "caso_id": (caso or {}).get("caso_id"),
        "regimen": regimen,
        "fecha_calculo": fecha_calculo.isoformat() if fecha_calculo else None,
        "base": {},
        "mesada_base": None,
        "palancas": [],
        "palancas_todas": [],
        "descartadas": [],
        "preguntas_pendientes": preguntas or [],
        "alternativas_del_segmento": None,
        "escenarios": [],
        "comparacion_de_regimen": None,
        "aviso_de_segmento": None,
        "que_significa_la_cifra": None,
        "que_significan_los_escenarios": None,
    }


def calcular(caso, regimen, sexo=None, edad=None, fecha_calculo=None,
             datos=None):
    """La entrada principal: todas las palancas de esta persona, ya ordenadas.

    caso: el caso del set dorado (la historia laboral ya extraída).
    regimen: "RPM" o "RAIS".
    datos: lo que la persona haya ido contando por el camino. Las llaves que
        entiende son es_independiente, tiene_capacidad_de_pago, ingreso_anual,
        aporte_mensual_posible, perfil_actual y afp. Lo que no esté, no se
        inventa: la palanca que lo necesite sale marcada con su pregunta.

    Devuelve un diccionario con:
      "base": el diagnóstico de partida y sus supuestos
      "palancas": las que aplican, ordenadas por impacto de mayor a menor
      "descartadas": las que no aplican, cada una con su motivo
      "preguntas_pendientes": qué falta por preguntar y para qué palanca
      "alternativas_del_segmento": la salida cruda del segmentador, para auditar
    """
    fecha_calculo = fecha_calculo or date.today()
    datos = dict(datos or {})

    # Sin sexo no hay nada que calcular, y NO se infiere (regla dura del
    # proyecto: nada se infiere en silencio, se pregunta). Se comprueba aquí y
    # no más abajo porque rpm.diagnosticar revienta con un KeyError críptico
    # cuando el sexo viene vacío, y un error críptico en producción es un
    # diagnóstico perdido.
    if not sexo:
        return _salida_vacia(
            caso, regimen, fecha_calculo,
            "Falta el sexo: preguntar al usuario (nada se infiere). Sin él no "
            "se puede saber la edad de pensión ni las semanas que le exige la "
            "ley.",
            preguntas=[{"dato": "sexo",
                        "pregunta": "¿Eres hombre o mujer? Te lo pregunto "
                                    "porque la ley pide edades y semanas "
                                    "distintas.",
                        "para_la_palanca": "todas"}])

    # --- El punto de partida contra el que se mide todo ---
    diagnostico = _diagnosticar(caso, regimen, sexo, edad, fecha_calculo)
    if diagnostico.get("error"):
        return _salida_vacia(caso, regimen, fecha_calculo,
                             diagnostico["error"])

    if regimen == "RPM":
        meses_mapa = rpm.expandir_a_meses(caso["periodos"])
        densidad = diagnostico.get("densidad_ultimos_3_anios")
        ibc = rpm.ibc_actual(meses_mapa)
    else:
        densidad = diagnostico.get("densidad_ultimos_3_anios")
        ibc = diagnostico.get("ibc_actual")

    base = {
        "diagnostico": diagnostico,
        "mesada": mesada_de(diagnostico, regimen),
        "densidad": densidad,
        "ibc_actual": ibc,
    }

    if base["mesada"] is None:
        return _salida_vacia(caso, regimen, fecha_calculo,
                             "No se pudo calcular la mesada base: sin ella no "
                             "hay contra qué medir ninguna palanca.")

    # --- El segmentador: qué le aplica a esta persona según su situación ---
    # Se llama con lo que se sepa hoy. Sus defaults son conservadores, así que
    # una respuesta que todavía no tenemos no habilita nada por error.
    alternativas = av.comparar_alternativas_pensionales(
        regimen,
        tiene_capacidad_de_pago=bool(datos.get("tiene_capacidad_de_pago")),
        es_independiente=bool(datos.get("es_independiente")),
        ingreso_respalda_ibc_mayor=bool(datos.get("ingreso_respalda_ibc_mayor")),
        sisben_1_2_o_3=bool(datos.get("sisben_1_2_o_3")))

    # --- Se corren todas ---
    todas = [
        palanca_subir_sueldo(caso, regimen, sexo, edad, fecha_calculo, base),
        palanca_cerrar_lagunas(caso, regimen, sexo, edad, fecha_calculo, base),
        palanca_recuperar_mora(caso, regimen, sexo, edad, fecha_calculo, base),
        palanca_regimen(caso, regimen, sexo, edad, fecha_calculo, base),
        palanca_aplazar(caso, regimen, sexo, edad, fecha_calculo, base),
        palanca_portafolio(caso, regimen, sexo, edad, fecha_calculo, base),
        palanca_administradora(caso, regimen, sexo, edad, fecha_calculo, base,
                               perfil_actual=datos.get("perfil_actual")),
        palanca_corregir_historia(caso, regimen, sexo, edad, fecha_calculo, base),
        palanca_densidad_ultimo_tramo(caso, regimen, sexo, edad, fecha_calculo,
                                      base),
        palanca_aportes_voluntarios(caso, regimen, sexo, edad, fecha_calculo,
                                    base, datos),
        palanca_sobrecotizar(caso, regimen, sexo, edad, fecha_calculo, base,
                             datos),
    ]

    # --- La 12 y la 2 son la misma acción: no pueden ir las dos ---
    # Cerrar lagunas (2) y la densidad del último tramo (12) le piden a la
    # persona exactamente lo mismo: cotizar todos los meses. Lo que cambia es
    # el argumento, y cerca del retiro el de la 12 es mucho más fuerte porque
    # explica POR QUÉ ahora pesa más. Mostrar las dos sería pedir dos veces lo
    # mismo con dos cifras casi iguales, y la persona pensaría que se suman.
    doce = next((p for p in todas if p["clave"] == "densidad_ultimo_tramo"), None)
    dos = next((p for p in todas if p["clave"] == "cerrar_lagunas"), None)
    if doce and dos and doce["aplica"] and dos["aplica"]:
        dos["aplica"] = False
        dos["motivo_no_aplica"] = (
            "Es la misma acción que la palanca del último tramo (cotizar todos "
            "los meses), y cerca del retiro esa la explica mejor. Se muestra "
            "una sola para que la persona no crea que son dos cosas distintas "
            "que se suman.")

    # --- Se separan las que aplican de las que no ---
    aplican = [p for p in todas if p["aplica"]]
    descartadas = [p for p in todas if not p["aplica"]]

    # OJO CON EL ORDEN DE ESTOS DOS BLOQUES, que es donde estuvo un bug real
    # (encontrado al escribir probar_palancas.py, 2026-09-18). El régimen se
    # extraía DESPUÉS del filtro del umbral, y el filtro se lo comía. El sesgo
    # que eso producía era exactamente el contrario del que se busca: como el
    # filtro descarta lo que mueve POCO, y el régimen desfavorable mueve en
    # NEGATIVO, la comparación solo sobrevivía cuando trasladarse convenía. A
    # quien le conviene quedarse (la mayoría en Colpensiones) la comparación
    # desaparecía en silencio, y saber que quedarse vale $345.424 al mes es la
    # información más valiosa de su reporte. El régimen se saca ANTES.
    # --- EL RÉGIMEN SALE DEL RANKING, Y ES UNA DECISIÓN DE FONDO ---
    # Corriendo el caso 01 el traslado salió como la palanca de MAYOR impacto
    # ($1.586.535 al mes). Ordenar por impacto la habría puesto de primera en el
    # reporte, y una palanca de primera con ese número no se lee como "aquí
    # están los dos escenarios": se lee como "trasládese". Eso es exactamente lo
    # que Júbilo no puede hacer, porque el traslado es una decisión que casi
    # nunca se puede deshacer y que por ley exige doble asesoría.
    # Por eso el régimen se saca de la competencia por el podio y se entrega
    # aparte, con su comparación completa y su límite de alcance.
    # Se saca de `aplican`, que es la lista que existe en este punto, y no de
    # `relevantes`, que se construye más abajo con el filtro del umbral.
    regimen_palanca = None
    for palanca in list(aplican):
        if palanca["clave"] == "regimen":
            regimen_palanca = palanca
            aplican.remove(palanca)

    # Las que mueven menos que el umbral se bajan a descartadas: no están mal,
    # es que ocupan el espacio de una que mueve de verdad.
    relevantes, pequenas = [], []
    for palanca in aplican:
        efecto = palanca["efecto_mesada_mes"]
        if efecto is not None and efecto < UMBRAL_MINIMO_PESOS:
            palanca["aplica"] = False
            palanca["motivo_no_aplica"] = (
                "Mueve menos de " + pesos(UMBRAL_MINIMO_PESOS) + " al mes: se "
                "calcula y se guarda, pero no se muestra para no quitarle el "
                "puesto a una palanca que sí mueve la aguja.")
            pequenas.append(palanca)
        else:
            relevantes.append(palanca)
    descartadas.extend(pequenas)

    # --- Se ordenan por impacto ---
    # Las que tienen número van primero, de mayor a menor. Las que no se pueden
    # cuantificar van después, en un orden fijo por importancia de producto:
    # corregir la historia antes que la administradora, porque la primera es
    # plata que ya es suya y la segunda es una decisión de inversión.
    orden_sin_numero = {"corregir_historia": 0, "administradora": 1}
    con_numero = [p for p in relevantes if p["efecto_mesada_mes"] is not None]
    sin_numero = [p for p in relevantes if p["efecto_mesada_mes"] is None]
    con_numero.sort(key=lambda p: p["efecto_mesada_mes"], reverse=True)
    sin_numero.sort(key=lambda p: orden_sin_numero.get(p["clave"], 99))
    ordenadas = con_numero + sin_numero

    # REGLA DE PRESENTACIÓN: la administradora (8) va siempre DESPUÉS del
    # portafolio (9). El dato dice que el portafolio pesa entre dos y diez veces
    # más, y mostrarlas al revés invita a optimizar la pequeña.
    ordenadas = _administradora_despues_de_portafolio(ordenadas)

    # El corte se aplica solo a las que compiten por impacto. Después se vuelve
    # a pegar la 8 debajo de la 9 si la 9 sobrevivió al corte, para que la
    # comparación entre AFP nunca aparezca huérfana.
    a_mostrar = [p for p in ordenadas if p["clave"] != "administradora"][:MAXIMO_A_MOSTRAR]
    administradora = next((p for p in ordenadas
                           if p["clave"] == "administradora"), None)
    if administradora and any(p["clave"] == "portafolio" for p in a_mostrar):
        a_mostrar = _administradora_despues_de_portafolio(
            a_mostrar + [administradora])

    # --- Qué falta por preguntar ---
    preguntas = [{"dato": p["requiere_dato"], "pregunta": p["pregunta"],
                  "para_la_palanca": p["titulo"]}
                 for p in todas if p.get("pregunta")]

    return {
        # Los dos subtítulos de las secciones 4 y 5 del reporte. Viven aquí y
        # no en el renderizador para que exista una sola versión del texto: si
        # mañana cambia lo que significan las cifras, cambia en un solo sitio.
        "que_significa_la_cifra": (
            "Cuánto más recibirías de pensión cada mes, para siempre, si "
            "accionas cada palanca."),
        "que_significan_los_escenarios": (
            "Tu pensión mensual proyectada en cada caso, en pesos de hoy."),
        # "error" viaja siempre, en None cuando todo salió bien. Así la salida
        # buena y la de error tienen exactamente las mismas llaves y quien las
        # consume no tiene que adivinar cuál le tocó.
        "error": None,
        "caso_id": caso.get("caso_id"),
        "regimen": regimen,
        "fecha_calculo": fecha_calculo.isoformat(),
        "base": {k: v for k, v in base.items() if k != "diagnostico"},
        "mesada_base": base["mesada"],
        "palancas": a_mostrar,
        "palancas_todas": ordenadas,
        # El régimen viaja en su propia llave, nunca mezclado con las palancas
        # que se ordenan por impacto. Quien renderice el reporte lo pone en su
        # propia sección, con su advertencia de doble asesoría.
        "comparacion_de_regimen": regimen_palanca,
        # Cuando esto no es None, manda sobre todo lo demás: significa que a
        # esta persona las palancas no le mueven la mesada y hay que decirle
        # por qué, en vez de entregarle un reporte vacío.
        # Se le pasa el caso completo porque el aviso ya no solo avisa: cuando
        # la persona esta en el piso, cuantifica los dos caminos del valle, y
        # para eso tiene que volver a correr la calculadora.
        "aviso_de_segmento": aviso_de_segmento(diagnostico, regimen, caso=caso,
                                               sexo=sexo, edad=edad,
                                               fecha_calculo=fecha_calculo),
        "descartadas": descartadas,
        "preguntas_pendientes": preguntas,
        "alternativas_del_segmento": alternativas,
        "escenarios": escenarios_combinados(caso, regimen, sexo, edad,
                                            fecha_calculo, base, ordenadas),
    }


def _administradora_despues_de_portafolio(palancas):
    """Garantiza que la palanca 8 nunca salga antes que la 9.

    Se hace con una reordenación explícita y no confiando en el impacto, porque
    el impacto de la 8 es a propósito None y un None podría quedar en cualquier
    parte según cómo se ordene el resto.
    """
    claves = [p["clave"] for p in palancas]
    if "administradora" not in claves or "portafolio" not in claves:
        return palancas
    # Se saca la 8 y se vuelve a meter JUSTO debajo de la 9, pegada a ella.
    # Pegada y no "en algún lugar después" a propósito: la 8 no tiene efecto en
    # pesos, así que sin esto se iría al final de la lista y el corte de
    # MAXIMO_A_MOSTRAR la dejaría fuera. Y la 8 sin la 9 al lado se lee como una
    # invitación a cambiar de AFP, que es justo lo que no queremos.
    administradora = palancas[claves.index("administradora")]
    resto = [p for p in palancas if p["clave"] != "administradora"]
    posicion = [p["clave"] for p in resto].index("portafolio") + 1
    return resto[:posicion] + [administradora] + resto[posicion:]


# ---------------------------------------------------------------------------
# Los escenarios: combinaciones de lo bueno, nunca el peor caso
# ---------------------------------------------------------------------------

def _enumerar(partes):
    """Une una lista en castellano corriente: "a, b y c", no "a y b y c".

    Es cosmético y aun así importa: el reporte se lee, y una frase mal pegada
    delata que la escribió una máquina, que es justo lo contrario de lo que se
    busca cuando se le está pidiendo a alguien que confíe en el número.
    """
    if not partes:
        return ""
    if len(partes) == 1:
        return partes[0]
    # Todas menos la última separadas por coma, y la última con "y".
    return ", ".join(partes[:-1]) + " y " + partes[-1]


def escenarios_combinados(caso, regimen, sexo, edad, fecha_calculo, base,
                          palancas):
    """Arma los escenarios juntando las mejores palancas, no el peor caso.

    POR QUÉ ASÍ. El reporte viejo le ofrecía "si dejas de cotizar hoy" a alguien
    de 27 años. Eso no es un escenario, es una amenaza, y no mueve a nadie a
    hacer nada. Los escenarios existen para mostrar a dónde se puede llegar, así
    que combinan las palancas que la persona sí puede accionar.

    SE COMBINAN SOLO LAS QUE SE PUEDEN CORRER JUNTAS EN UNA SOLA PASADA de la
    calculadora (sueldo, ritmo de cotización y aplazamiento), porque esas tres
    son supuestos del mismo motor y su efecto conjunto NO es la suma de sus
    efectos por separado. Sumar los efectos uno por uno daría un número inflado.
    """
    accionables = {p["clave"] for p in palancas if p["aplica"]}
    diagnostico = base["diagnostico"] or {}
    edad_hoy = diagnostico.get("edad")
    edad_pension = edad_de_pension(diagnostico, regimen, caso, edad_hoy)

    # LOS TRES DATOS QUE HACEN CONCRETO EL ESCENARIO BASE. "Si todo sigue igual
    # que ahora" no dice nada: la persona no sabe qué está asumiendo la
    # calculadora por ella. Aquí se le dice con números, que es lo que le
    # permite corregirnos si el supuesto está mal.
    cuanto = pesos(base["ibc_actual"]) if base["ibc_actual"] else None
    meses_al_anio = (round(base["densidad"] * 12)
                     if base["densidad"] is not None else None)

    # Se arma a mano y no con _enumerar porque las tres partes no son una
    # lista de cosas equivalentes: son cuánto, con qué frecuencia y hasta
    # cuándo. Unirlas con "y" las pone al mismo nivel y se lee mal.
    if cuanto and meses_al_anio is not None:
        descripcion_base = ("Si sigues cotizando sobre " + cuanto + " al mes, "
                            "unos " + str(meses_al_anio) + " de los 12 meses "
                            "del año")
        if edad_pension:
            descripcion_base += ", hasta los " + str(edad_pension) + " años"
        descripcion_base += "."
    else:
        descripcion_base = "Si todo sigue igual que ahora."

    escenarios = [{
        "nombre": "Como vas hoy",
        "descripcion": descripcion_base,
        "mesada": base["mesada"],
        "efecto_mes": 0,
        "es_base": True,
    }]

    # Escenario intermedio: lo que depende solo de la persona, sin pedirle nada
    # a nadie. Cotizar todos los meses y, si aplica, trabajar un año más.
    supuestos_medio = {}
    partes_medio = []
    if "cerrar_lagunas" in accionables:
        supuestos_medio["densidad_futura"] = 1.0
        partes_medio.append("cotizas los 12 meses del año")
    if "aplazar" in accionables:
        supuestos_medio["meses_aplazamiento"] = APLAZAMIENTOS[0]
        partes_medio.append("sigues hasta los " + str(edad_pension + 1)
                            + " años en vez de los " + str(edad_pension)
                            if edad_pension else "trabajas un año más")

    if supuestos_medio:
        diagnostico = _diagnosticar(caso, regimen, sexo, edad, fecha_calculo,
                                    **supuestos_medio)
        mesada = mesada_de(diagnostico, regimen)
        monto, pct = _delta(base["mesada"], mesada)
        escenarios.append({
            "nombre": "Si haces lo que está en tus manos",
            "descripcion": "Si " + _enumerar(partes_medio) + ".",
            "mesada": mesada,
            "efecto_mes": monto,
            "efecto_pct": pct,
            "supuestos": supuestos_medio,
        })

    # Escenario alto: todo lo anterior más el aumento de sueldo, que depende
    # también del empleador. Se declara esa dependencia en la descripción para
    # que no se lea como algo que la persona controla sola.
    supuestos_alto = dict(supuestos_medio)
    partes_alto = list(partes_medio)
    if "subir_sueldo" in accionables and base["ibc_actual"]:
        supuestos_alto["ibc_futuro"] = base["ibc_actual"] * (1 + AUMENTOS_DE_SUELDO[0])
        partes_alto.append("te suben el sueldo un 10% una sola vez (de "
                           + pesos(base["ibc_actual"]) + " a "
                           + pesos(base["ibc_actual"] * 1.10)
                           + ") y ese sueldo se mantiene")

    if supuestos_alto and supuestos_alto != supuestos_medio:
        diagnostico_alto = _diagnosticar(caso, regimen, sexo, edad,
                                         fecha_calculo, **supuestos_alto)
        mesada = mesada_de(diagnostico_alto, regimen)
        monto, pct = _delta(base["mesada"], mesada)
        # Se encadena con "todo lo anterior" en vez de repetir la lista
        # entera, que se vuelve ilegible en cuanto hay tres condiciones.
        nuevas = [p for p in partes_alto if p not in partes_medio]
        descripcion_alto = (("Todo lo anterior y además " + _enumerar(nuevas)
                             + ".") if partes_medio and nuevas
                            else "Si " + _enumerar(partes_alto) + ".")
        escenarios.append({
            # NO "si te acompaña la suerte". Un ascenso o un aumento no es
            # suerte, es algo que la persona negocia o busca, y llamarlo
            # suerte lo saca de su control justo cuando el reporte existe
            # para devolverle control. Además suena poco serio en un
            # documento que le está diciendo de cuánto va a vivir.
            "nombre": "Si además te suben el sueldo",
            "descripcion": descripcion_alto,
            "mesada": mesada,
            "efecto_mes": monto,
            "efecto_pct": pct,
            "supuestos": supuestos_alto,
        })

    return escenarios


# ---------------------------------------------------------------------------
# Para verlo por consola mientras se trabaja
# ---------------------------------------------------------------------------

def imprimir(resultado):
    """Imprime el banco de palancas. El agente redacta con el system-prompt;
    esto es para poder mirarlo mientras se construye."""
    if resultado.get("error"):
        print("ERROR:", resultado["error"])
        return
    print("=" * 78)
    print("PALANCAS DE", resultado["caso_id"], "|", resultado["regimen"],
          "| mesada base:", pesos(resultado["mesada_base"]))
    print("=" * 78)
    if resultado.get("aviso_de_segmento"):
        aviso = resultado["aviso_de_segmento"]
        print("\n*** AVISO DE SEGMENTO ***")
        print("   " + aviso["mensaje"])
        print("   LO QUE IMPORTA: " + aviso["lo_que_de_verdad_importa"])
        # Los dos caminos del valle, cuando la persona esta de verdad en el
        # piso. Se imprimen aqui pegados al aviso porque son su continuacion:
        # el aviso dice que pasa y el valle dice que puede hacer al respecto.
        if aviso.get("valle"):
            valle = aviso["valle"]
            for llave in ("camino_1_aceptar_el_minimo",
                          "camino_2_saltar_el_valle"):
                camino = valle[llave]
                print("\n   CAMINO: " + camino["titulo"])
                print("   " + camino["frase"])
            print("\n   VEREDICTO: " + valle["veredicto"])
    for i, p in enumerate(resultado["palancas"], 1):
        efecto = (pesos(p["efecto_mesada_mes"]) + "/mes"
                  if p["efecto_mesada_mes"] is not None else "sin cuantificar")
        print("\n%d. [%s] %s" % (i, efecto, p["titulo"]))
        print("   " + (p["frase"] or ""))
    if resultado.get("comparacion_de_regimen"):
        r = resultado["comparacion_de_regimen"]
        print("\n--- Comparación de régimen (aparte, no es recomendación) ---")
        print("   " + (r["frase"] or ""))
        print("   LÍMITE: " + (r["limite_de_alcance"] or ""))
    print("\n--- Escenarios ---")
    for e in resultado["escenarios"]:
        print("  %-32s %12s" % (e["nombre"], pesos(e["mesada"])))
    print("\n--- Descartadas (con su motivo) ---")
    for p in resultado["descartadas"]:
        print("  %-34s %s" % (p["titulo"], p["motivo_no_aplica"]))
    if resultado["preguntas_pendientes"]:
        print("\n--- Falta preguntar (solo cuando sea relevante) ---")
        for q in resultado["preguntas_pendientes"]:
            print("  [%s] %s" % (q["dato"], q["pregunta"]))


def main():
    """CLI mínima: palancas.py <ruta-al-caso.json> <RPM|RAIS> [sexo]"""
    import json
    import sys
    if len(sys.argv) < 3:
        print(main.__doc__)
        return
    caso = json.load(open(sys.argv[1], encoding="utf-8"))
    regimen = sys.argv[2].upper()
    sexo = sys.argv[3] if len(sys.argv) > 3 else caso["afiliado"].get("sexo")
    if not sexo:
        print("Este caso no trae el sexo en el documento. Pásalo como tercer "
              "argumento: palancas.py <caso.json> <RPM|RAIS> <M|F>")
        return
    imprimir(calcular(caso, regimen, sexo=sexo))


if __name__ == "__main__":
    main()
