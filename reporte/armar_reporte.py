"""Arma el reporte de cierre de Júbilo: una pagina en PDF.

**La regla que este archivo existe para cumplir.** El reporte lo arma el codigo,
no el modelo. Es una plantilla fija que se llena con la salida de
`calculadora/diagnosticar.py`. Si el modelo "dibujara" el reporte, cada uno
saldria distinto y, peor, podria reescribir una cifra. Es la misma regla dura del
proyecto: la IA conversa, el codigo fijo hace los numeros.

**Consecuencia practica, y es la mas importante de todo el archivo:** aqui NO se
calcula nada. Cada cifra se copia tal cual del diccionario del diagnostico. No
se redondea, no se promedia, no se reconstruye. Si una cifra no viene en el
diagnostico, el reporte dice que no la hay, en vez de inventarla. Su prueba
(`probar_armar_reporte.py`) compara cifra por cifra el reporte contra el JSON.

**Estructura de la pagina, validada por Santiago el 2026-09-18.** Siete
secciones, en este orden, que es la secuencia real de la pregunta que la persona
trae:

  1. Encabezado, con quien es y donde esta hoy.
  2. Tu resultado, si sigues como hoy.
  3. Tus alertas.
  4. Tus palancas.
  5. Tus escenarios, con el mismo formato del resultado.
  6. Tus siguientes pasos, pueden ser varios.
  7. Supuestos y limites.

**De donde salen las secciones 4 y 5 (cambio del 2026-09-18).** Antes las
armaba este archivo a mano, y salian frases genericas del tipo "cotizar sobre
un salario base mayor, si puedes", que no dicen nada y que el dueno del
producto rechazo. Ahora las dos secciones son un RENDERIZADO de lo que calcula
`calculadora/palancas.py`: aqui no se redacta ninguna frase con numero ni se
elige el orden. Reglas que este renderizado no puede romper:

  - El orden de la lista "palancas" se respeta tal cual: ya viene ordenada por
    impacto y con la administradora pegada debajo del portafolio.
  - La comparacion de regimen va en su propia sub-seccion, nunca mezclada entre
    las palancas, y siempre con su texto de limite de alcance. Jubilo no
    recomienda trasladarse.
  - Toda palanca con `limite_de_alcance` lo muestra. No es letra chica
    opcional: es lo que mantiene a Jubilo fuera de la asesoria de inversion.
  - Si viene `aviso_de_segmento`, va arriba de todo en la seccion 4.
  - Si no hay palancas ni aviso, se dice honestamente que no se pudieron
    cuantificar. Nunca se rellena con consejos genericos.
  - Si una palanca trae `efecto_mesada_mes` en None, se muestra su frase sin
    numero. Nunca se pone un cero en su lugar.
  - Los escenarios van en el orden en que vienen, empezando por el base, y
    nunca se anade uno de "si dejas de cotizar".

**Decisiones de Santiago del 2026-09-18 que este archivo respeta:**

  - **Formato: solo PDF**, una pagina. No se genera imagen.
  - **El reporte SI lleva el nombre completo de la persona.** Se le advirtio que
    el reporte se puede reenviar, y decidio que va. Lo que NO lleva, y eso no se
    negocia, es la cedula ni ningun numero de documento.
  - El sexo va como la letra sola, sin explicacion.

Como se usa:

    python3 reporte/armar_reporte.py diagnostico.json "Nombre Apellido" Porvenir salida.pdf caso.json

El quinto argumento (el caso, o sea la historia laboral ya extraida) es
opcional pero muy recomendado: sin el no se pueden correr las palancas, y las
secciones 4 y 5 salen con el texto honesto de "no se pudieron cuantificar".
"""

import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
# La calculadora vive en la carpeta de al lado; hay que decirle a Python donde
# buscarla para poder importar el modulo de palancas.
sys.path.insert(0, str(Path(__file__).parent.parent / "calculadora"))
from pdf_simple import Pagina, partir, ancho_de
import palancas as motor_palancas

# --- Como se ve la pagina ---------------------------------------------------
#
# LEER ESTO ANTES DE TOCAR CUALQUIER NUMERO DE MAS ABAJO.
#
# Todo lo visual del reporte (que tan grande es una letra, que tanto aire hay
# entre dos lineas) sale de las dos escalas que estan en este bloque. Ninguna
# llamada de dibujo, en ninguna seccion, puede traer un numero suelto escrito a
# mano. Esa es la regla que arregla el problema que reporto el dueno del
# producto: antes cada seccion elegia su tamano por su cuenta y dos cifras que
# significan lo mismo (la mesada de la seccion 2 y el efecto de una palanca de
# la seccion 4) salian de tamano distinto.
#
# Si hay que cambiar el aspecto del reporte, se cambia UN numero de aqui y el
# cambio baja solo a las siete secciones.

ANCHO_PAGINA = 612               # ancho de la hoja carta, en puntos
ALTO_PAGINA = 792                # alto de la hoja carta, en puntos
# Los tres margenes se recortaron (antes 46 a los lados, 44 arriba y 40 abajo)
# cuando se puso el aire correcto entre bloques: recortar margen es la forma de
# pagar ese aire sin apretar el interlineado, que es lo unico que no se puede
# tocar sin volver ilegible la pagina. Aun asi el caso mas largo queda al filo
# de la hoja: ver la nota sobre el desborde al final de `escribir_pdf`.
MARGEN = 42                      # margen izquierdo y derecho, en puntos
MARGEN_SUPERIOR = 32             # desde el borde de arriba hasta la primera linea
ANCHO_UTIL = ANCHO_PAGINA - 2 * MARGEN   # el ancho que queda para escribir
AZUL = (0.09, 0.24, 0.40)        # el color de los titulos de seccion
NEGRO = (0, 0, 0)                # el color del texto normal
GRIS = (0.42, 0.42, 0.42)        # para las notas al pie y las salvedades
GRIS_FONDO = (0.94, 0.95, 0.96)  # el fondo de las franjas de seccion
PIE_DE_PAGINA = 34               # la altura de la raya del pie de pagina

# EL SUELO DEL CONTENIDO. Por debajo de esta altura no se dibuja ni una linea
# del flujo: lo que no quepa encima se va a la hoja siguiente.
#
# Por que este valor y no la raya del pie a secas: si el limite fuera la raya,
# la ultima linea de la hoja podria quedar pegada a ella, tocandola. Se le suma
# el aire que separa dos bloques, que es el mismo colchon que hay entre
# cualquier bloque y el siguiente, para que el final de la hoja respire igual
# que el resto de la pagina. No se usa un numero mas grande porque cada punto
# de colchon es espacio que se le quita al contenido, y el reporte va justo.


# --- Escala 1: la tipografia ------------------------------------------------
#
# Cada nivel de la jerarquia tiene UN tamano, UN peso (normal o negrita) y UN
# color. Un nivel es "que tan importante es esto dentro de la pagina", no "en
# que seccion esta".
#
# LA REGLA, y es la unica que importa: **dos elementos del mismo nivel se ven
# exactamente igual, sin importar en que seccion aparezcan.** Si el valor de
# una fila mide 9 puntos en la seccion 2, mide 9 puntos en la 4 y en la 5.
#
# Cada nivel es un diccionario con las tres claves que necesita `Pagina.texto`,
# asi que dibujar es siempre "pasale el nivel", nunca "pasale los numeros".

# El titulo del documento. Aparece una sola vez, arriba de todo.
NIVEL_TITULO = {"tamano": 18, "negrita": True, "color": AZUL}

# El nombre de la persona, justo debajo del titulo.
NIVEL_NOMBRE = {"tamano": 11, "negrita": True, "color": NEGRO}

# La linea de metadatos: fondo, regimen, edad, sexo y fecha del diagnostico.
NIVEL_METADATOS = {"tamano": 8.5, "negrita": False, "color": GRIS}

# El texto dentro de la franja gris que abre cada una de las siete secciones.
NIVEL_FRANJA = {"tamano": 9.5, "negrita": True, "color": AZUL}

# La etiqueta de una fila: lo que se lee a la izquierda ("Mesada estimada",
# "Semanas cotizadas", el titulo de una palanca, el nombre de un escenario).
NIVEL_ETIQUETA = {"tamano": 9, "negrita": False, "color": NEGRO}

# El valor de esa misma fila: la cifra que se lee a la derecha. Va en negrita
# porque es lo que el ojo busca. Mide lo mismo que la etiqueta porque van en la
# misma linea, y mide lo mismo en TODAS las secciones: ese era el defecto que
# se vio en el PDF ("entre $1.750.905 y $2.090.605" salia mas grande que
# "$452.857 al mes" aunque las dos son la cifra destacada de su fila).
NIVEL_VALOR = {"tamano": 9, "negrita": True, "color": NEGRO}

# Un sub-titulo dentro de una seccion: encabeza un bloque pero no lleva cifra
# a la derecha (la comparacion de regimen, "Lo que de verdad importa").
NIVEL_SUBTITULO = {"tamano": 9, "negrita": True, "color": AZUL}

# El texto de apoyo: la frase que explica una fila. Es texto para leer, no para
# escanear, y por eso es mas pequeno que la fila pero sigue siendo negro.
NIVEL_APOYO = {"tamano": 7.5, "negrita": False, "color": NEGRO}

# La nota al pie de un bloque: los limites de alcance, las salvedades, los
# supuestos. Gris, porque acompana pero no es lo que se viene a leer.
NIVEL_NOTA = {"tamano": 7, "negrita": False, "color": GRIS}

# El pie de pagina, que es el mismo en todos los reportes.
NIVEL_PIE = {"tamano": 7, "negrita": False, "color": GRIS}

# Todos los niveles juntos. Sirve para dos cosas: documentar la escala de un
# vistazo, y dejar que la prueba compruebe que ningun dibujo usa un tamano que
# no este aqui.
NIVELES = {
    "titulo": NIVEL_TITULO,
    "nombre": NIVEL_NOMBRE,
    "metadatos": NIVEL_METADATOS,
    "franja": NIVEL_FRANJA,
    "etiqueta": NIVEL_ETIQUETA,
    "valor": NIVEL_VALOR,
    "subtitulo": NIVEL_SUBTITULO,
    "apoyo": NIVEL_APOYO,
    "nota": NIVEL_NOTA,
    "pie": NIVEL_PIE,
}
TAMANOS_DE_LA_ESCALA = {nivel["tamano"] for nivel in NIVELES.values()}


# --- Escala 2: el espacio vertical ------------------------------------------
#
# Lo mismo que arriba pero para el aire. Todos los espacios son multiplos de
# una sola unidad base, no numeros elegidos a ojo uno por uno.
#
# LA REGLA: **la separacion entre bloques tiene que ser visiblemente mayor que
# la separacion dentro de un bloque.** Si no, el ojo no distingue donde acaba
# una palanca y empieza la siguiente, que es exactamente lo que reporto el
# dueno del producto al mirar la seccion 4.
#
# Un "bloque" es un conjunto de lineas que se leen como una sola cosa: una
# palanca es su titulo mas su frase mas su nota de limite; un escenario es su
# titulo mas su descripcion; una alerta es su titulo mas su detalle.

UNIDAD = 1.5                      # la unidad base de la que salen los demas

# Entre dos lineas de un mismo parrafo. Es el aire mas apretado que hay.
ESPACIO_LINEA = 1 * UNIDAD        # 1.5

# Entre dos filas de la misma seccion, o entre dos vinetas de una misma lista.
# Son cosas distintas pero hermanas, asi que se separan un poco mas que dos
# lineas de un mismo parrafo.
ESPACIO_FILA = 2 * UNIDAD         # 3.0

# Entre un bloque y el siguiente. Es tres veces el aire entre lineas: esa
# diferencia es la que hace que se vean como dos cosas y no como una.
ESPACIO_BLOQUE = 3 * UNIDAD       # 4.5

# Antes y despues de la franja gris que abre una seccion. OJO CON COMO SE MIDEN
# ESTOS DOS, que no es como los de arriba: se miden desde el borde del
# rectangulo gris, no desde la linea base del texto. La franja ademas ocupa su
# propio alto, asi que el corte visual entre dos secciones termina siendo el
# mas grande de la pagina aunque estos dos numeros sean pequenos. La prueba lo
# comprueba midiendo el PDF, no estas constantes.
ESPACIO_ANTES_FRANJA = 1 * UNIDAD    # 1.5, del bloque anterior al borde de arriba
ESPACIO_DESPUES_FRANJA = 1 * UNIDAD  # 1.5, del borde de abajo a la primera fila

# El alto de la franja gris, y cuanto baja el rectangulo por debajo de la linea
# base de su texto. Los dos juntos dejan el texto dentro de la franja: por
# encima de la linea base quedan 9 puntos, que es lo que mide hacia arriba una
# mayuscula de 9.5, y por debajo 1.5 para la cola de las letras.
ALTO_FRANJA = 7 * UNIDAD             # 10.5
HUNDIDO_FRANJA = 1 * UNIDAD          # 1.5

# El suelo del contenido, ya con la escala disponible. Ver la explicacion de
# arriba, junto a PIE_DE_PAGINA.
SUELO_CONTENIDO = PIE_DE_PAGINA + ESPACIO_BLOQUE

# Cuanto hay que tener libre para empezar algo sin que quede huerfano al pie
# de la hoja. No son numeros nuevos: se calculan con la misma escala.
#
# Un bloque necesita como minimo su fila y dos lineas de apoyo; una franja de
# seccion necesita, ademas de su propio alto, que quepan dos filas debajo, o
# el titulo de la seccion quedaria solo al final de la hoja.
ALTO_LINEA_FILA = NIVEL_ETIQUETA["tamano"] + ESPACIO_LINEA
ALTO_LINEA_APOYO = NIVEL_APOYO["tamano"] + ESPACIO_LINEA
ALTO_MINIMO_BLOQUE = ALTO_LINEA_FILA + 2 * ALTO_LINEA_APOYO
ALTO_MINIMO_TRAS_FRANJA = ALTO_MINIMO_BLOQUE

# Las dos sangrias: la del contenido normal de una seccion y la del detalle
# que cuelga de una fila (la frase de una palanca, el detalle de una alerta).
SANGRIA_SECCION = 3 * UNIDAD     # 4.5
SANGRIA_DETALLE = 6 * UNIDAD     # 9.0

# Los meses en espanol, para escribir las fechas como las lee una persona.
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


# --- Piezas para escribir numeros como los lee una persona -----------------

def pesos(valor):
    """Pasa un numero a pesos colombianos: 2090605 queda como $2.090.605."""
    if valor is None:
        return "sin dato"
    return "$" + "{:,.0f}".format(round(valor)).replace(",", ".")


def banda_en_pesos(par):
    """Escribe una banda de mesada. Si los dos extremos son iguales, no repite."""
    if not par:
        return "sin dato"
    bajo, alto = par
    if bajo is None or alto is None:
        return "sin dato"
    if round(bajo) == round(alto):
        return pesos(bajo)
    return "entre %s y %s" % (pesos(bajo), pesos(alto))


def fecha_larga(iso):
    """Pasa 2061-01-20 a "enero de 2061". El dia no aporta a un horizonte asi."""
    if not iso:
        return None
    try:
        anio, mes, _ = str(iso).split("-")
        return "%s de %s" % (MESES[int(mes) - 1], anio)
    except (ValueError, IndexError):
        return str(iso)


def semanas(valor):
    """Escribe las semanas con un decimal, que es como las trae la calculadora."""
    if valor is None:
        return "sin dato"
    return "{:,.0f}".format(valor).replace(",", ".")


# --- Paso 1: sacar del diagnostico lo que va en la pagina ------------------

def datos_del_reporte(diagnostico, nombre, fondo, caso=None, datos_persona=None,
                      resultado_palancas=None):
    """Extrae del diagnostico las cifras exactas que van en cada seccion.

    Devuelve un diccionario con las siete secciones. Esta separado de la parte
    que dibuja a proposito: asi la prueba puede comparar estas cifras contra el
    JSON sin tener que leer un PDF.

    NO calcula nada aqui. Cada valor sale de una clave del diagnostico o de la
    salida de `palancas.calcular`. Las dos cosas nuevas que recibe:

    caso: la historia laboral ya extraida (el mismo diccionario que se le paso
        a `diagnosticar`). Hace falta porque las palancas se calculan volviendo
        a correr la calculadora con supuestos distintos, y para eso se necesita
        el caso, no el diagnostico ya resuelto.
    datos_persona: lo que la persona haya contado en la conversacion (si es
        independiente, si le sobra para ahorrar, etc). Lo que no este, no se
        inventa: la palanca que lo necesite sale descartada con su pregunta.
    resultado_palancas: se puede pasar ya calculado, para no correrlo dos
        veces. Sirve sobre todo para las pruebas.
    """
    # EL CANDADO, y es lo primero por una razon. Si el diagnostico no quedo
    # completo (porque falta el sexo, porque la verificacion no cuadro, o
    # porque el documento venia incompleto), NO se arma el reporte. Una pagina
    # llena de "sin dato" es peor que no mandar nada: parece un resultado y no
    # lo es. Se levanta un error con las preguntas que faltan, para que quien
    # llame pueda decirle a la persona que le falta.
    if not diagnostico.get("listo_para_entregar"):
        pendientes = diagnostico.get("preguntas_al_usuario") or []
        motivo = (diagnostico.get("diagnostico") or {}).get("error")
        raise ValueError(
            "El diagnóstico no está listo, así que no se arma reporte. "
            "Motivo: %s. Falta: %s" % (motivo or "sin especificar",
                                       "; ".join(pendientes) or "sin especificar"))

    modulo = diagnostico["router"]["modulo"]           # "rpm" o "rais"
    encabezado = diagnostico["diagnostico"]
    base = (diagnostico.get("recuperacion") or {}).get("base") or {}

    # Las palancas se calculan una sola vez y alimentan las secciones 4 y 5.
    if resultado_palancas is None:
        resultado_palancas = calcular_palancas(diagnostico, caso, datos_persona)

    datos = {
        "modulo": modulo,
        "encabezado": _encabezado(diagnostico, encabezado, nombre, fondo, modulo),
        "resultado": _resultado(diagnostico, base, modulo),
        "alertas": _alertas(diagnostico),
        "palancas": _palancas(resultado_palancas),
        "escenarios": _escenarios(resultado_palancas),
        "siguientes_pasos": _siguientes_pasos(diagnostico, modulo),
        "supuestos": _supuestos(diagnostico, encabezado, modulo),
    }
    return datos


def calcular_palancas(diagnostico, caso, datos_persona=None):
    """Corre `palancas.calcular` con los mismos supuestos del diagnostico.

    Cuando no se puede correr (porque no llego el caso, o porque la calculadora
    devolvio un error) devuelve un diccionario con la clave "error" y el motivo
    escrito. No devuelve None a secas ni un diccionario a medias: quien
    renderiza necesita distinguir "no hubo palancas" de "no se pudieron
    calcular", y quien audite el reporte necesita poder leer por que.

    Los tres supuestos (regimen, sexo y fecha de calculo) se toman del propio
    diagnostico, no de valores por defecto. Si se tomaran de otro lado, las
    palancas se estarian midiendo contra un punto de partida distinto del que
    muestra el resto del reporte, y las cifras no cuadrarian entre secciones.
    """
    if not caso:
        return {"error": "No llegó la historia laboral, así que no se pudo "
                         "correr la calculadora de palancas."}

    # El router ya decidio el regimen; aqui solo se traduce al nombre que usa
    # el modulo de palancas ("rpm" pasa a "RPM").
    regimen = "RPM" if diagnostico["router"]["modulo"] == "rpm" else "RAIS"
    encabezado = diagnostico["diagnostico"]

    # La fecha del diagnostico viene como texto "2026-07-18"; palancas la
    # necesita como fecha de verdad para poder hacer cuentas con ella.
    try:
        fecha_calculo = date.fromisoformat(str(diagnostico.get("fecha_calculo")))
    except (TypeError, ValueError):
        fecha_calculo = None

    try:
        resultado = motor_palancas.calcular(
            caso, regimen,
            sexo=encabezado.get("sexo"),
            edad=encabezado.get("edad"),
            fecha_calculo=fecha_calculo,
            datos=datos_persona or {})
    except Exception as fallo:
        # Si la calculadora de palancas revienta, el reporte tiene que salir
        # igual: las otras cinco secciones son utiles por si solas. La 4 y la 5
        # diran honestamente que no se pudieron cuantificar. El motivo tecnico
        # se guarda para que el fallo no quede invisible: un reporte que se
        # degrada en silencio se entrega roto sin que nadie se entere.
        return {"error": "La calculadora de palancas falló: "
                         + type(fallo).__name__ + ": " + str(fallo)}

    if resultado.get("error"):
        return resultado
    return resultado


def _encabezado(diagnostico, enc, nombre, fondo, modulo):
    """Quien es la persona y donde esta hoy. Seccion 1."""
    # Ojo: los dos regimenes traen claves distintas. En prima media el requisito
    # viene en el propio bloque del diagnostico; en ahorro individual, lo que
    # marca el umbral son las semanas de la garantia de pension minima.
    faltan = None
    if modulo == "rpm":
        requisito = enc.get("requisito_semanas_hoy")
    else:
        requisito = enc.get("semanas_gpm")
    if requisito is not None and enc.get("semanas_hoy") is not None:
        faltan = max(0.0, requisito - enc["semanas_hoy"])

    return {
        "nombre": nombre,
        "fondo": fondo,
        "fecha_calculo": diagnostico.get("fecha_calculo"),
        "edad": enc.get("edad"),
        "sexo": enc.get("sexo"),
        "regimen": "Prima media (Colpensiones)" if modulo == "rpm"
                   else "Ahorro individual (fondo privado)",
        "semanas_hoy": enc.get("semanas_hoy"),
        # El requisito depende del regimen: en prima media son las semanas para
        # pensionarse, en ahorro individual las de la garantia de pension minima.
        "requisito_semanas": requisito,
        "que_es_el_requisito": ("semanas para pensionarte" if modulo == "rpm"
                                else "semanas para la garantía de pensión mínima"),
        "semanas_que_faltan": faltan,
        "edad_legal": enc.get("edad_legal"),
    }


def _resultado(diagnostico, base, modulo):
    """El resultado si sigue como hoy. Seccion 2."""
    if modulo == "rpm":
        rpm = diagnostico["diagnostico"]
        escenario = rpm.get("escenario_sigue_cotizando") or {}
        return {
            "fecha_pension": rpm.get("fecha_pension_estimada"),
            # En Colpensiones la formula es determinista, asi que los dos
            # extremos de la banda son el mismo numero y no se repite al
            # escribirlo. Se deja como par para que las dos secciones que
            # muestran mesada (esta y la de escenarios) usen el mismo formato.
            "mesada_banda": (escenario.get("mesada"), escenario.get("mesada")),
            "tasa_de_reemplazo_pct": escenario.get("tasa_pct"),
            "ibl": escenario.get("ibl"),
            "es_punto_no_banda": True,
            "nota": ("en Colpensiones la fórmula es determinista, así que el "
                     "resultado es un punto y no una banda"),
        }
    # OJO CON LA FUENTE DE ESTA CIFRA, que es donde ya se cometio un error real.
    # La mesada sale del escenario que de verdad le aplica a la persona dentro
    # del propio diagnostico, NO de `recuperacion.base`. Los dos numeros suelen
    # coincidir, pero no son la misma cosa: `recuperacion.base` es el punto de
    # partida contra el que se comparan los escenarios de recuperacion, y se
    # calcula SIN los supuestos de palanca (si se pide el diagnostico con un
    # sueldo futuro distinto, `recuperacion.base` no se entera y el escenario si).
    # Leer de ahi funcionaba por casualidad. Por eso ya no hay respaldo a esa
    # clave: si el escenario no esta, se dice "sin dato" y no se rellena con un
    # numero que responde a otra pregunta.
    #
    # Cual escenario "de verdad le aplica" lo decide la misma funcion que usa
    # palancas.py, para que la cifra de la seccion 2 y la mesada base contra la
    # que se miden las palancas sean siempre el mismo escenario. A partir de
    # cierta edad la ley obliga a pasar el saldo al fondo conservador, y ahi el
    # escenario aplicable ya no es el moderado sino la mezcla obligatoria.
    escenarios = diagnostico["diagnostico"].get("escenarios") or {}
    clave_escenario = motor_palancas.escenario_aplicable(
        diagnostico["diagnostico"]) or "moderado"
    escenario_base = escenarios.get(clave_escenario) or {}
    return {
        "fecha_pension": base.get("fecha_pension"),
        "edad_pension": diagnostico["diagnostico"].get("edad_legal"),
        "mesada_banda": escenario_base.get("mesada_banda"),
        "perfil_de_la_cifra": clave_escenario,
        "es_punto_no_banda": False,
        "salida": base.get("salida"),
        "nota": ("la banda no es imprecisión: sus dos extremos son dos precios "
                 "distintos de la renta vitalicia, el de la norma y el de mercado"),
    }


def _alertas(diagnostico):
    """Moras y lagunas, con su impacto en semanas. Seccion 3."""
    resumen = (diagnostico.get("lagunas") or {}).get("resumen") or {}
    inventario = (diagnostico.get("recuperacion") or {}).get("inventario") or {}
    alertas = []

    if resumen.get("vacios"):
        alertas.append({
            "titulo": "Meses sin cotizar",
            "cifra": "%s huecos, %s semanas perdidas"
                     % (resumen["vacios"], semanas(resumen.get("semanas_en_vacios"))),
            "detalle": "son periodos en que nadie cotizó por ti",
        })
    if resumen.get("tramos_con_deficit"):
        alertas.append({
            "titulo": "Periodos cotizados de forma incompleta",
            "cifra": "%s tramos, %s semanas"
                     % (resumen["tramos_con_deficit"],
                        semanas(resumen.get("semanas_en_deficit_de_tramos"))),
            "detalle": "se cotizó, pero no el periodo completo",
        })
    if inventario.get("mora_sin_contar"):
        alertas.append({
            "titulo": "Mora del empleador que aún no te cuenta",
            "cifra": "%s periodos" % len(inventario["mora_sin_contar"]),
            "detalle": "tu empleador reportó el salario pero no pagó",
        })
    if resumen.get("filas_ibc_sin_semanas"):
        alertas.append({
            "titulo": "Filas con salario y cero semanas",
            "cifra": "%s fila%s" % (resumen["filas_ibc_sin_semanas"],
                                    "" if resumen["filas_ibc_sin_semanas"] == 1 else "s"),
            "detalle": "es la señal típica de un error en la historia laboral",
        })

    return {
        "lista": alertas,
        "semanas_perdidas_total": resumen.get("semanas_perdidas_total"),
        "sin_alertas": not alertas,
    }


TEXTO_SIN_PALANCAS = ("Con los datos de este documento no se pudieron "
                      "cuantificar palancas para tu caso. No significa que no "
                      "las haya: significa que para ponerles un número hacen "
                      "falta datos que todavía no tenemos.")


def _palancas(resultado):
    """Que puede hacer y cuanto gana, con su cifra. Seccion 4.

    Aqui NO se redacta ni se ordena nada: todo se copia de la salida de
    `palancas.calcular`. La frase de cada palanca ya viene escrita y con su
    numero adentro, y la lista ya viene ordenada por impacto y recortada.

    `resultado` es esa salida, o un diccionario con "error" si no se pudo
    correr.
    """
    # Caso 1: la calculadora de palancas no se pudo correr. Se dice y punto.
    # Nunca se rellena la seccion con consejos genericos, que era justo el
    # problema del reporte viejo.
    if not resultado or resultado.get("error"):
        return {"aviso": None, "lista": [], "comparacion_de_regimen": None,
                "sin_palancas": True, "texto_sin_palancas": TEXTO_SIN_PALANCAS,
                # El motivo tecnico NO se imprime en la pagina: no le sirve de
                # nada a la persona. Queda aqui para quien audite el reporte.
                "motivo_tecnico": (resultado or {}).get("error"),
                "mesada_base": None}

    # El aviso de segmento manda sobre todo lo demas. Es el caso de la persona
    # cuya mesada la fija el piso de la garantia de pension minima: a ella
    # ninguna palanca le mueve la mesada, y sin este aviso su reporte se leeria
    # como "no hay nada que hacer", que es falso.
    aviso = resultado.get("aviso_de_segmento")

    lista = []
    for palanca in resultado.get("palancas") or []:
        lista.append({
            "titulo": palanca["titulo"],
            # La frase ya viene con el numero adentro, escrita por palancas.py.
            "frase": palanca.get("frase"),
            # El efecto en pesos se muestra como etiqueta a la derecha. Si
            # viene en None es que esta palanca no se puede cuantificar, y
            # entonces NO se pone un cero: se deja la casilla vacia y la frase
            # habla sola.
            "efecto_mes": palanca.get("efecto_mesada_mes"),
            # La cifra sola, sin el " al mes" que el reporte le pegaba a mano.
            # Ese texto decia cada cuanto pero no de que, que es justo lo que
            # pregunto el dueno del producto. Ahora el "de que" lo dice la
            # etiqueta de aqui abajo, y la escribe palancas.py.
            "efecto_mes_texto": (pesos(palanca["efecto_mesada_mes"])
                                 if palanca.get("efecto_mesada_mes") is not None
                                 else None),
            # Que significa la cifra de ESTA fila, porque no todas significan
            # lo mismo: unas son "mas de pension al mes" y la del portafolio
            # es "de diferencia en tu pension mensual". Si la palanca no trae
            # cifra, tampoco lleva etiqueta: la de administradora tiene la
            # casilla de la derecha vacia a proposito y asi debe seguir.
            "etiqueta_efecto": (palanca.get("etiqueta_efecto")
                                if palanca.get("efecto_mesada_mes") is not None
                                else None),
            # El limite de alcance no es letra chica opcional: cuando una
            # palanca lo trae, se muestra siempre.
            "limite_de_alcance": palanca.get("limite_de_alcance"),
            "clave": palanca.get("clave"),
        })

    # La comparacion de regimen viaja aparte a proposito y se renderiza aparte.
    # Mezclarla entre las palancas la convertiria en una recomendacion de
    # traslado, y Jubilo no recomienda trasladarse.
    comparacion = resultado.get("comparacion_de_regimen")
    regimen = None
    if comparacion:
        regimen = {
            "titulo": comparacion["titulo"],
            "frase": comparacion.get("frase"),
            "limite_de_alcance": comparacion.get("limite_de_alcance"),
        }

    return {
        "aviso": aviso,
        "lista": lista,
        "comparacion_de_regimen": regimen,
        # El subtitulo de la seccion: de que hablan todas las cifras de la
        # columna derecha. Lo redacta palancas.py; aqui solo se muestra. Si
        # viene en None, la seccion sale sin subtitulo y ya.
        "que_significa_la_cifra": resultado.get("que_significa_la_cifra"),
        # "sin palancas" es solo cuando no hay ni palancas ni aviso ni
        # comparacion: ahi si la seccion quedaria en blanco.
        "sin_palancas": not lista and not aviso and not regimen,
        "texto_sin_palancas": TEXTO_SIN_PALANCAS,
        # La mesada contra la que se midieron todas las palancas. Sale de la
        # clave "mesada_base" de palancas.calcular, NO de recuperacion.base:
        # ese otro numero no responde a los supuestos de palanca y daba el
        # mismo valor por casualidad.
        "mesada_base": resultado.get("mesada_base"),
    }


def _escenarios(resultado):
    """A donde puede llegar, combinando palancas. Seccion 5.

    Los escenarios vienen ya armados de `palancas.calcular`, en el orden en que
    hay que mostrarlos y empezando por el base ("Como vas hoy"). Aqui no se
    reordenan, no se recortan y no se anade ninguno.

    Lo que ya NO aparece, y es el cambio de fondo: el escenario de "si dejas de
    cotizar hoy". A alguien de 27 anios eso no es un escenario, es una amenaza,
    y no mueve a nadie a hacer nada. Los escenarios existen para mostrar a
    donde se puede llegar.
    """
    if not resultado or resultado.get("error"):
        return {"lista": [], "cuantos": 0,
                "que_significan_los_escenarios": None}

    salida = []
    for escenario in resultado.get("escenarios") or []:
        salida.append({
            "titulo": escenario["nombre"],
            "descripcion": escenario.get("descripcion"),
            # La mesada de cada escenario sale de la clave "mesada" del propio
            # escenario, que la calculo palancas.py corriendo la calculadora
            # con esos supuestos. Aqui no se suma ni se estima nada.
            "mesada": escenario.get("mesada"),
            "efecto_mes": escenario.get("efecto_mes"),
            "es_base": bool(escenario.get("es_base")),
        })

    return {
        "lista": salida,
        "cuantos": len(salida),
        # El subtitulo de la seccion, con la misma logica que el de la 4: dice
        # de que hablan las cifras de la derecha. Lo redacta palancas.py.
        "que_significan_los_escenarios":
            resultado.get("que_significan_los_escenarios"),
    }


def _siguientes_pasos(diagnostico, modulo):
    """Los pasos concretos. Seccion 6. Santiago pidio que puedan ser varios."""
    pasos = []
    resumen = (diagnostico.get("lagunas") or {}).get("resumen") or {}
    inventario = (diagnostico.get("recuperacion") or {}).get("inventario") or {}

    if inventario.get("mora_sin_contar"):
        pasos.append("Reclámale a tu empleador los periodos en mora, o radica la "
                     "corrección de historia laboral ante tu administradora.")
    if resumen.get("filas_ibc_sin_semanas"):
        pasos.append("Pide la corrección de las filas que tienen salario "
                     "reportado y cero semanas: es un error del registro.")
    if resumen.get("vacios"):
        pasos.append("Revisa los meses sin cotizar: si en alguno estabas "
                     "trabajando, hay con qué reclamarlo.")

    ventana = (diagnostico.get("comparacion") or {}).get("ventana_traslado") or {}
    if ventana.get("abierta"):
        pasos.append("Si vas a evaluar el cambio de régimen, pide la doble "
                     "asesoría obligatoria en tu fondo y en Colpensiones. Es "
                     "gratis y es un requisito de ley.")

    pasos.append("Vuelve a bajar tu historia laboral en un año y compárala con "
                 "este reporte: es la forma de darte cuenta a tiempo si algo "
                 "quedó mal registrado.")
    return pasos


def _supuestos(diagnostico, enc, modulo):
    """Que se asumio y que no cubre este diagnostico. Seccion 7."""
    lineas = []
    if enc.get("ibc_futuro_supuesto"):
        lineas.append("Se asumió que sigues cotizando sobre %s, en pesos de hoy."
                      % pesos(enc["ibc_futuro_supuesto"]))
    if enc.get("densidad_futura_supuesta") is not None:
        lineas.append("Se asumió que cotizas el %.0f%% del tiempo de aquí en "
                      "adelante, que es tu ritmo de los últimos 3 años."
                      % (enc["densidad_futura_supuesta"] * 100))
    if modulo == "rais":
        banda = enc.get("banda_rendimiento") or {}
        prospectivo = banda.get("prospectivo") or {}
        if prospectivo.get("moderado"):
            # El separador decimal en espanol es la coma, no el punto.
            tasa = ("%.2f" % (prospectivo["moderado"] * 100)).replace(".", ",")
            lineas.append("El rendimiento del ahorro se proyectó al %s%% real "
                          "anual (portafolio moderado), un supuesto de largo "
                          "plazo, no una promesa." % tasa)
        convergencia = enc.get("convergencia_obligatoria") or {}
        if (convergencia.get("mezcla") or {}).get("conservador"):
            lineas.append("Por tu edad, la ley ya obliga a que el %.0f%% de tu "
                          "saldo esté en el portafolio conservador."
                          % (convergencia["mezcla"]["conservador"] * 100))

    limites = [
        "Este es un diagnóstico preliminar, no una liquidación certificada. "
        "La cifra oficial la da tu administradora cuando reclamas.",
        "Todas las cifras están en pesos de hoy, sin proyectar inflación.",
        "No reemplaza la doble asesoría obligatoria para cambiar de régimen.",
    ]
    verificacion = diagnostico.get("verificacion") or {}
    if verificacion.get("cuadra"):
        limites.insert(0, "Las semanas de este reporte cuadran contra el total "
                          "impreso de tu historia laboral (calculado %s, "
                          "documento %s)."
                          % (semanas(verificacion.get("calculado")),
                             semanas(verificacion.get("documento"))))
    return {"supuestos": lineas, "limites": limites}


# --- Paso 2: dibujar la pagina --------------------------------------------

def alto_de_parrafo(texto, nivel, sangria=SANGRIA_SECCION):
    """Cuanto va a ocupar un texto, en puntos, una vez partido en lineas.

    Sirve para preguntar "¿cabe esto?" ANTES de empezar a dibujarlo, que es
    lo unico que permite mandar un bloque entero a la hoja siguiente en vez
    de partirlo por la mitad.
    """
    if not texto:
        return 0
    ancho = ANCHO_UTIL - sangria - SANGRIA_SECCION
    lineas = partir(texto, nivel["tamano"], ancho)
    return len(lineas) * (nivel["tamano"] + ESPACIO_LINEA)


def alto_de_bloque(filas=0, parrafos=()):
    """Lo que ocupa un bloque: unas cuantas filas y sus parrafos de detalle.

    `parrafos` es una lista de tripletas (texto, nivel, sangria). Se usa para
    medir una palanca (su fila, su frase y su limite de alcance), un escenario
    (su fila y su descripcion) o una alerta (su fila y su detalle).
    """
    alto = filas * ALTO_LINEA_FILA
    for texto, nivel, sangria in parrafos:
        alto += alto_de_parrafo(texto, nivel, sangria)
    return alto


class _Lienzo:
    """Lleva la cuenta de por donde va la pagina, para no pisar lo anterior.

    **Esta clase es la unica que dibuja.** Las siete secciones no llaman nunca
    a `Pagina.texto` con numeros propios: piden "escribe esto como una fila",
    "escribe esto como una nota", y la clase pone el tamano, el peso, el color
    y el aire que manda la escala de arriba. Ese es el candado que evita que
    vuelvan a aparecer dos cifras del mismo nivel con tamanos distintos.
    """

    def __init__(self):
        self.pagina = Pagina()
        # Se empieza cerca del borde de arriba. El origen del PDF esta abajo,
        # asi que "arriba del todo" es el alto de la hoja menos el margen.
        self.y = ALTO_PAGINA - MARGEN_SUPERIOR

    # --- Mover el cursor ---------------------------------------------------

    def bajar(self, puntos):
        """Corre el cursor hacia abajo. Es la unica forma de gastar pagina."""
        self.y -= puntos

    # --- Cambiar de hoja ---------------------------------------------------
    #
    # El reporte esta disenado para caber en una hoja y casi siempre cabe.
    # Estos tres metodos son la red de seguridad para cuando no: antes, lo que
    # no cabia se escribia por debajo del borde y desaparecia sin que fallara
    # nada, y lo primero que se perdia era el final del documento, o sea las
    # salvedades legales.

    def cabe(self, altura):
        """Dice si en la hoja actual todavia queda sitio para eso de alto."""
        return self.y - altura >= SUELO_CONTENIDO

    def saltar_pagina(self):
        """Cierra la hoja (con su pie) y sigue arriba de la siguiente."""
        self.pie()
        self.pagina.nueva_pagina()
        self.y = ALTO_PAGINA - MARGEN_SUPERIOR

    def asegurar_espacio(self, altura):
        """Salta de hoja si lo que viene no cabe entero en la actual.

        Se llama ANTES de empezar algo que se lee como una sola cosa (una
        palanca, un escenario, una seccion), para que no quede partido entre
        dos hojas.
        """
        if self.cabe(altura):
            return False
        # Si ya estamos arriba del todo de una hoja, saltar no arregla nada:
        # lo que viene es mas alto que una hoja entera y va a tener que
        # partirse igual. Saltar solo dejaria una hoja en blanco.
        if self.y >= ALTO_PAGINA - MARGEN_SUPERIOR:
            return False
        self.saltar_pagina()
        return True

    def pie(self):
        """La raya y la letra pequena del final de cada hoja.

        Va anclado abajo, fuera del flujo del contenido, asi que no le quita
        espacio a lo que se esta escribiendo. Se repite en todas las hojas.

        El numero de hoja NO se escribe aqui: en este momento todavia no se
        sabe cuantas hojas va a tener el documento. Lo pone `numerar()` al
        final, y aqui solo se le reserva el ancho.
        """
        self.pagina.linea(MARGEN, PIE_DE_PAGINA, ANCHO_PAGINA - MARGEN,
                          PIE_DE_PAGINA, grosor=0.5, color=GRIS)
        # Se le quita al texto el ancho que va a ocupar la numeracion, para
        # que no se solapen. Se reserva con dos digitos por lado, que es mas
        # de lo que este reporte va a necesitar nunca.
        reserva = ancho_de(_numero_de_hoja(99, 99) + " ", NIVEL_PIE["tamano"],
                           NIVEL_PIE["negrita"])
        alto_linea = NIVEL_PIE["tamano"] + ESPACIO_LINEA
        # Se escriben de arriba hacia abajo, empezando justo debajo de la raya.
        tope = PIE_DE_PAGINA - alto_linea
        for indice, linea in enumerate(partir(TEXTO_PIE, NIVEL_PIE["tamano"],
                                              ANCHO_UTIL - reserva)):
            self.pagina.texto(MARGEN, tope - indice * alto_linea, linea,
                              tamano=NIVEL_PIE["tamano"],
                              negrita=NIVEL_PIE["negrita"],
                              color=NIVEL_PIE["color"])

    def numerar(self):
        """Escribe "1 de 2" en el pie de cada hoja, ya sabiendo cuantas son.

        Se llama al final del todo, cuando el documento esta cerrado. Cada
        numero se escribe en su hoja, incluidas las que ya se cerraron, y se
        alinea a la derecha, a la altura de la primera linea del pie.
        """
        total = self.pagina.paginas
        alto_linea = NIVEL_PIE["tamano"] + ESPACIO_LINEA
        for hoja in range(1, total + 1):
            texto = _numero_de_hoja(hoja, total)
            ancho = ancho_de(texto, NIVEL_PIE["tamano"], NIVEL_PIE["negrita"])
            self.pagina.texto(ANCHO_PAGINA - MARGEN - ancho,
                              PIE_DE_PAGINA - alto_linea, texto,
                              tamano=NIVEL_PIE["tamano"],
                              negrita=NIVEL_PIE["negrita"],
                              color=NIVEL_PIE["color"], hoja=hoja)

    def separar_bloques(self, alto_del_que_viene=ALTO_MINIMO_BLOQUE):
        """Abre el aire que separa un bloque del siguiente.

        Se llama al terminar cada palanca, cada escenario y cada alerta. Es lo
        que hace que se vean como cosas distintas y no como un muro de texto.

        Y es el sitio natural para preguntar si el bloque que viene cabe: si
        no cabe, se pasa a la hoja siguiente entero, en vez de dejar su titulo
        colgando al final de la anterior.
        """
        self.bajar(ESPACIO_BLOQUE)
        self.asegurar_espacio(alto_del_que_viene)

    def separar_filas(self):
        """Abre el aire mas pequeno que separa dos hermanas de una misma lista."""
        self.bajar(ESPACIO_FILA)

    # --- Escribir ----------------------------------------------------------

    def _escribir(self, x, texto, nivel):
        """Pone una linea de texto con el tamano, peso y color de su nivel."""
        self.pagina.texto(x, self.y, texto, tamano=nivel["tamano"],
                          negrita=nivel["negrita"], color=nivel["color"])

    def franja(self, texto, alto_del_primer_bloque=ALTO_MINIMO_BLOQUE):
        """La franja gris que abre una seccion, con su aire arriba y abajo.

        El rectangulo sobresale por encima y por debajo de la linea base de su
        texto, asi que hay que reservarle ese alto o se monta sobre lo de
        arriba y sobre lo de abajo. Eso es exactamente lo que pasaba: la
        primera fila de cada seccion quedaba pisando la franja.
        """
        # Lo que la franja sube por encima de la linea base de su texto.
        sobresale = ALTO_FRANJA - HUNDIDO_FRANJA
        # Una franja sola al final de una hoja no sirve de nada: si no caben
        # tambien las primeras filas de la seccion, la seccion entera empieza
        # en la hoja siguiente.
        self.asegurar_espacio(ESPACIO_ANTES_FRANJA + ALTO_FRANJA
                              + ESPACIO_DESPUES_FRANJA
                              + alto_del_primer_bloque)
        # Nota: ALTO_MINIMO_TRAS_FRANJA es lo que ocupa el primer bloque de la
        # seccion (su fila y su detalle), no una fila suelta. Asi la franja
        # nunca se queda sola al pie de una hoja con su contenido en la
        # siguiente, que es de las cosas que peor se leen.
        # Se baja el aire pedido MAS lo que sobresale, para que el borde de
        # arriba del rectangulo quede justo a esa distancia del bloque anterior.
        self.bajar(ESPACIO_ANTES_FRANJA + sobresale)
        self.pagina.rectangulo(MARGEN, self.y - HUNDIDO_FRANJA, ANCHO_UTIL,
                               ALTO_FRANJA, GRIS_FONDO)
        self._escribir(MARGEN + SANGRIA_SECCION, texto, NIVEL_FRANJA)
        # Y al bajar se descuenta lo que la franja se hunde por debajo de la
        # linea base, mas el aire pedido, mas el alto de la letra de la primera
        # fila (que se dibuja hacia arriba desde su linea base).
        self.bajar(HUNDIDO_FRANJA + ESPACIO_DESPUES_FRANJA
                   + NIVEL_ETIQUETA["tamano"])

    def fila(self, etiqueta, valor=None, unidad=None):
        """Una fila: la etiqueta a la izquierda y, si la hay, su cifra a la derecha.

        Es el ladrillo del reporte y se usa igual en las siete secciones: la
        mesada de la seccion 2, el efecto de una palanca de la 4 y la mesada de
        un escenario de la 5 son todas filas, asi que salen identicas.

        `unidad` es el texto que dice de que es la cifra ("mas de pension al
        mes"). Va pegado a la derecha de la cifra, en la misma linea y en el
        nivel de texto de apoyo: asi la cifra sigue siendo lo primero que el
        ojo encuentra y la aclaracion la acompana sin competir con ella. Si no
        hay unidad no se escribe nada, nunca un texto por defecto.

        Todo lo de la derecha se alinea midiendo cuanto ocupa cada trozo y
        restandolo del borde, y por eso se dibuja de derecha a izquierda:
        primero la unidad y despues la cifra.
        """
        # Ultima red: ni una linea se dibuja por debajo del pie de pagina.
        self.asegurar_espacio(ALTO_LINEA_FILA)
        self._escribir(MARGEN + SANGRIA_SECCION, etiqueta, NIVEL_ETIQUETA)
        if valor:
            borde = ANCHO_PAGINA - MARGEN - SANGRIA_SECCION
            if unidad:
                # El espacio que separa la cifra de su unidad se mide con la
                # misma fuente, para no inventarse una distancia a mano.
                texto_unidad = " " + unidad
                ancho_unidad = ancho_de(texto_unidad, NIVEL_APOYO["tamano"],
                                        NIVEL_APOYO["negrita"])
                self._escribir(borde - ancho_unidad, texto_unidad, NIVEL_APOYO)
                borde -= ancho_unidad
            ancho = ancho_de(valor, NIVEL_VALOR["tamano"], NIVEL_VALOR["negrita"])
            self._escribir(borde - ancho, valor, NIVEL_VALOR)
        # Todo va en la misma linea, y la letra mas alta es la de la etiqueta
        # y la cifra, asi que es la que manda cuanto hay que bajar.
        self.bajar(NIVEL_ETIQUETA["tamano"] + ESPACIO_LINEA)

    def subtitulo(self, texto):
        """Encabeza un bloque que no lleva cifra a la derecha."""
        self.asegurar_espacio(NIVEL_SUBTITULO["tamano"] + ESPACIO_LINEA)
        self._escribir(MARGEN + SANGRIA_SECCION, texto, NIVEL_SUBTITULO)
        self.bajar(NIVEL_SUBTITULO["tamano"] + ESPACIO_LINEA)

    def parrafo(self, texto, nivel=NIVEL_APOYO, sangria=SANGRIA_SECCION,
                prefijo="", sangria_continuacion=None):
        """Texto que se parte solo en varias lineas cuando no cabe en el ancho.

        El aire entre linea y linea es siempre `ESPACIO_LINEA`: dentro de un
        parrafo no hay razon para que una seccion respire distinto de otra.

        `prefijo` es lo que va delante de la primera linea (el numero de un
        paso, la vineta de un supuesto). Las lineas siguientes se corren hacia
        la derecha lo que ocupa ese prefijo, para que el texto quede alineado
        en bloque y no debajo del numero.
        """
        tamano = nivel["tamano"]
        if sangria_continuacion is None:
            sangria_continuacion = sangria
        ancho_primera = ANCHO_UTIL - sangria - SANGRIA_SECCION
        # El prefijo se mide con la misma fuente para saber cuanto ancho le
        # quita a la primera linea.
        ancho_prefijo = ancho_de(prefijo, tamano, nivel["negrita"]) if prefijo else 0
        lineas = partir(texto, tamano, ancho_primera - ancho_prefijo)
        # El parrafo se reserva entero antes de empezar a escribirlo, para que
        # no queden dos lineas sueltas al pie de una hoja y el resto en la
        # siguiente. Si no cabe ni en una hoja vacia, se parte por lo sano.
        self.asegurar_espacio(len(lineas) * (tamano + ESPACIO_LINEA))
        for indice, linea in enumerate(lineas):
            # La misma red de seguridad que en las filas, linea por linea.
            self.asegurar_espacio(tamano + ESPACIO_LINEA)
            if indice == 0 and prefijo:
                self._escribir(MARGEN + sangria, prefijo + linea, nivel)
            elif indice == 0:
                self._escribir(MARGEN + sangria, linea, nivel)
            else:
                self._escribir(MARGEN + sangria_continuacion, linea, nivel)
            self.bajar(tamano + ESPACIO_LINEA)

    def nota(self, texto, sangria=SANGRIA_DETALLE):
        """Una salvedad o un limite de alcance: mismo trato en toda la pagina."""
        self.parrafo(texto, nivel=NIVEL_NOTA, sangria=sangria)


def _numero_de_hoja(hoja, total):
    """El texto de la numeracion del pie: "Pagina 1 de 2"."""
    return "Página %d de %d" % (hoja, total)


TEXTO_PIE = ("Júbilo. Diagnóstico preliminar, no es una liquidación "
             "certificada. Las cifras las calcula un programa, no una "
             "inteligencia artificial.")


def escribir_pdf(datos, ruta):
    """Dibuja la pagina con los datos ya extraidos y la guarda.

    Ni una sola llamada de esta funcion trae un tamano, un color o un espacio
    escrito a mano: todo sale de las dos escalas del principio del archivo, a
    traves de los metodos del lienzo. Si aqui aparece un numero suelto, la
    prueba `probar_armar_reporte.py` falla.
    """
    lienzo = _Lienzo()
    enc = datos["encabezado"]

    # --- 1. Encabezado ---
    # Las tres lineas del encabezado son tres niveles distintos de la escala,
    # y por eso se ven distintas: titulo, nombre y metadatos.
    lienzo._escribir(MARGEN, "Tu diagnóstico pensional", NIVEL_TITULO)
    lienzo.bajar(NIVEL_TITULO["tamano"] - ESPACIO_LINEA)
    lienzo._escribir(MARGEN, enc["nombre"] or "", NIVEL_NOMBRE)
    lienzo.bajar(NIVEL_NOMBRE["tamano"] + ESPACIO_LINEA)
    lienzo._escribir(
        MARGEN,
        "%s  |  %s  |  %s años  |  %s  |  Diagnóstico del %s"
        % (enc["fondo"] or "", enc["regimen"], enc["edad"], enc["sexo"] or "",
           enc["fecha_calculo"] or ""),
        NIVEL_METADATOS)
    lienzo.bajar(NIVEL_METADATOS["tamano"] + ESPACIO_LINEA)
    lienzo.pagina.linea(MARGEN, lienzo.y, ANCHO_PAGINA - MARGEN, lienzo.y,
                        grosor=1, color=AZUL)

    lienzo.franja("1. DÓNDE ESTÁS HOY")
    lienzo.fila("Semanas cotizadas", semanas(enc["semanas_hoy"]))
    lienzo.fila("Las que te exigen (%s)" % enc["que_es_el_requisito"],
                semanas(enc["requisito_semanas"]))
    if enc["semanas_que_faltan"] is not None:
        # Decir "te faltan 0" es confuso. Si ya cumple, se dice que ya cumple.
        if enc["semanas_que_faltan"] <= 0:
            lienzo.fila("Requisito de semanas", "ya lo cumples")
        else:
            lienzo.fila("Te faltan", semanas(enc["semanas_que_faltan"]))
    if enc["edad_legal"]:
        lienzo.fila("Edad legal de pensión", "%s años" % enc["edad_legal"])

    # --- 2. Tu resultado ---
    res = datos["resultado"]
    lienzo.franja("2. TU RESULTADO, SI SIGUES COMO HOY")
    fecha = fecha_larga(res.get("fecha_pension"))
    if fecha:
        lienzo.fila("Fecha estimada de pensión", fecha)
    elif res.get("edad_pension"):
        lienzo.fila("Te pensionarías a los", "%s años" % res["edad_pension"])
    # OJO: esta fila es la cifra mas importante del reporte, pero se dibuja
    # como cualquier otra fila. Antes se le daba un tamano propio y terminaba
    # viendose distinta del efecto de una palanca de la seccion 4, que esta al
    # mismo nivel de la jerarquia. Lo que la destaca es donde esta, no que sea
    # mas grande.
    lienzo.fila("Mesada estimada", banda_en_pesos(res.get("mesada_banda")))
    if res.get("nota"):
        lienzo.nota(res["nota"], sangria=SANGRIA_SECCION)

    # --- 3. Tus alertas ---
    alertas = datos["alertas"]
    lienzo.franja("3. TUS ALERTAS")
    if alertas["sin_alertas"]:
        lienzo.parrafo("Tu historia laboral no muestra huecos ni moras. Es poco "
                       "común, y es una buena noticia.")
    else:
        # Cada alerta es un bloque: su titulo con la cifra, y debajo el detalle
        # que explica que significa. Se separan entre si con el aire de bloque.
        for indice, alerta in enumerate(alertas["lista"]):
            # Se mide la alerta entera (su fila y su detalle) para poder
            # mandarla completa a la hoja siguiente si aqui ya no cabe.
            alto = alto_de_bloque(
                filas=1,
                parrafos=[(alerta["detalle"], NIVEL_APOYO, SANGRIA_DETALLE)])
            if indice:
                lienzo.separar_bloques(alto)
            else:
                lienzo.asegurar_espacio(alto)
            lienzo.fila(alerta["titulo"], alerta["cifra"])
            lienzo.parrafo(alerta["detalle"], sangria=SANGRIA_DETALLE)
        if alertas.get("semanas_perdidas_total"):
            lienzo.separar_bloques()
            lienzo.fila("Total de semanas perdidas",
                        semanas(alertas["semanas_perdidas_total"]))

    # --- 4. Tus palancas ---
    pal = datos["palancas"]
    # La franja reserva lo que ocupa el subtitulo de la seccion, para no
    # quedarse sola al pie de una hoja.
    lienzo.franja("4. TUS PALANCAS",
                  alto_del_primer_bloque=max(
                      ALTO_MINIMO_BLOQUE,
                      alto_de_parrafo(pal.get("que_significa_la_cifra"),
                                      NIVEL_APOYO)))

    # Que significan todas las cifras de la columna de la derecha. Va aqui
    # arriba, una sola vez, porque es la pregunta que hizo el dueno del
    # producto al ver el PDF: "esa plata por mes, a que se refiere". La frase
    # la redacta palancas.py; el reporte solo la coloca.
    if pal.get("que_significa_la_cifra"):
        lienzo.parrafo(pal["que_significa_la_cifra"])
        lienzo.separar_bloques()

    # El aviso de segmento va arriba de todo y manda sobre el resto: si esta,
    # es porque a esta persona las palancas no le mueven la mesada y hay que
    # decirle por que, y sobre todo que es lo que si esta en juego para ella.
    if pal.get("aviso"):
        aviso = pal["aviso"]
        lienzo.parrafo(aviso["mensaje"])
        lienzo.separar_bloques()
        lienzo.subtitulo("Lo que de verdad importa en tu caso")
        lienzo.parrafo(aviso["lo_que_de_verdad_importa"],
                       sangria=SANGRIA_DETALLE)

    # Si no hay nada que mostrar, se dice honestamente. Nunca se rellena la
    # seccion con consejos genericos: era justo el problema del reporte viejo.
    if pal["sin_palancas"]:
        lienzo.parrafo(pal["texto_sin_palancas"])

    # Las palancas van en el orden en que vienen. Ese orden ya lo decidio
    # palancas.py (por impacto, y con la administradora pegada al portafolio),
    # asi que aqui no se toca.
    #
    # Cada palanca es UN bloque de hasta tres piezas: su titulo con la cifra a
    # la derecha, su frase, y su nota de limite de alcance. Dentro del bloque
    # el aire es el de linea; entre una palanca y la siguiente, el de bloque,
    # que es cuatro veces mayor. Antes no habia ninguna diferencia y por eso el
    # dueno del producto veia las palancas pegadas unas a otras.
    for indice, palanca in enumerate(pal["lista"]):
        # La palanca entera es un bloque: titulo con su cifra, frase y limite
        # de alcance. Se mide antes de empezar a dibujarla para que no quede
        # el titulo al pie de una hoja y la frase al principio de la otra.
        alto = alto_de_bloque(
            filas=1,
            parrafos=[(palanca.get("frase"), NIVEL_APOYO, SANGRIA_DETALLE),
                      (palanca.get("limite_de_alcance"), NIVEL_NOTA,
                       SANGRIA_DETALLE)])
        if indice or pal.get("aviso") or pal.get("que_significa_la_cifra"):
            lienzo.separar_bloques(alto)
        else:
            lienzo.asegurar_espacio(alto)
        lienzo.fila(palanca["titulo"], palanca.get("efecto_mes_texto"),
                    unidad=palanca.get("etiqueta_efecto"))
        if palanca.get("frase"):
            lienzo.parrafo(palanca["frase"], sangria=SANGRIA_DETALLE)
        if palanca.get("limite_de_alcance"):
            lienzo.nota(palanca["limite_de_alcance"])

    # La comparacion de regimen, en su propia sub-seccion y con su limite.
    if pal.get("comparacion_de_regimen"):
        comp = pal["comparacion_de_regimen"]
        lienzo.separar_bloques(alto_de_bloque(
            filas=1,
            parrafos=[(comp.get("frase"), NIVEL_APOYO, SANGRIA_DETALLE),
                      (comp.get("limite_de_alcance"), NIVEL_NOTA,
                       SANGRIA_DETALLE)]))
        lienzo.subtitulo(comp["titulo"])
        if comp.get("frase"):
            lienzo.parrafo(comp["frase"], sangria=SANGRIA_DETALLE)
        if comp.get("limite_de_alcance"):
            lienzo.nota(comp["limite_de_alcance"])

    # --- 5. Tus escenarios ---
    lienzo.franja("5. TUS ESCENARIOS",
                  alto_del_primer_bloque=max(
                      ALTO_MINIMO_BLOQUE,
                      alto_de_parrafo(
                          datos["escenarios"].get(
                              "que_significan_los_escenarios"),
                          NIVEL_APOYO)))
    # El mismo subtitulo aclaratorio que la seccion 4, pero aqui las cifras
    # son la pension completa proyectada, no lo que sube. Son dos cosas
    # distintas y por eso cada seccion trae su propia frase.
    if datos["escenarios"].get("que_significan_los_escenarios"):
        lienzo.parrafo(datos["escenarios"]["que_significan_los_escenarios"])
        lienzo.separar_bloques()
    for indice, escenario in enumerate(datos["escenarios"]["lista"]):
        # Igual que las palancas: el escenario y su descripcion van juntos.
        # La descripcion se arma abajo, asi que aqui se mide con la de origen
        # mas el texto del efecto, que es lo mas largo que puede llegar a ser.
        alto = alto_de_bloque(
            filas=1,
            parrafos=[((escenario.get("descripcion") or "") + " Son "
                       + pesos(escenario.get("efecto_mes")) + " más al mes "
                       "que hoy.", NIVEL_APOYO, SANGRIA_DETALLE)])
        if indice:
            lienzo.separar_bloques(alto)
        else:
            lienzo.asegurar_espacio(alto)
        lienzo.fila(escenario["titulo"], pesos(escenario.get("mesada")))
        detalle = escenario.get("descripcion") or ""
        # Al escenario base no se le pone "+$0": no suma nada, es el punto de
        # partida contra el que se comparan los otros.
        if not escenario["es_base"] and escenario.get("efecto_mes"):
            detalle = (detalle + " Son " + pesos(escenario["efecto_mes"])
                       + " más al mes que hoy.").strip()
        if detalle:
            lienzo.parrafo(detalle, sangria=SANGRIA_DETALLE)

    # --- 6. Tus siguientes pasos ---
    # La lista numerada es UN bloque, no varios: son hermanas de la misma
    # lista, asi que se separan con el aire de fila, no con el de bloque.
    lienzo.franja("6. TUS SIGUIENTES PASOS")
    for numero, paso in enumerate(datos["siguientes_pasos"], start=1):
        if numero > 1:
            lienzo.separar_filas()
        lienzo.parrafo(paso, sangria=SANGRIA_SECCION, prefijo="%d. " % numero,
                       sangria_continuacion=SANGRIA_DETALLE)

    # --- 7. Supuestos y limites ---
    lienzo.franja("7. SUPUESTOS Y LÍMITES")
    # Cada salvedad es una sola frase, asi que la lista entera es un bloque y
    # entre una y otra va el aire mas pequeno de la escala, el de linea. Darles
    # aire de fila las separaria mas de lo que merecen y son ocho.
    for indice, linea in enumerate(datos["supuestos"]["supuestos"]
                                   + datos["supuestos"]["limites"]):
        if indice:
            lienzo.bajar(ESPACIO_LINEA)
        lienzo.nota(linea, sangria=SANGRIA_SECCION)

    # El pie de la ultima hoja. Las anteriores, si las hubo, ya lo llevan:
    # se lo pone `saltar_pagina` al cerrarlas. Y una vez cerrado el documento
    # ya se sabe cuantas hojas son, asi que se puede numerar.
    lienzo.pie()
    lienzo.numerar()

    # ESTADO DEL ESPACIO, 2026-09-19. El reporte esta disenado para caber en
    # una hoja, y cuatro de los cinco casos del set dorado caben con holgura.
    # El quinto (caso 01, ahorro individual: cuatro palancas, comparacion de
    # regimen y los dos subtitulos nuevos de las secciones 4 y 5) ya no cabe,
    # y por eso `pdf_simple.py` aprendio a hacer salto de pagina. Antes ese
    # caso se entregaba con el final del documento escrito por debajo del
    # borde de la hoja, o sea invisible, y lo que se perdia eran las
    # salvedades legales de la seccion 7.
    #
    # Las dos cosas que se anotan para que la prueba pueda vigilarlas:
    #  - "espacio_sobrante" es lo que quedo libre en la ULTIMA hoja. Sigue
    #    teniendo que ser positivo: si saliera negativo querria decir que algo
    #    se escribio por debajo del pie, que es el error que no se ve.
    #  - "paginas" es cuantas hojas hicieron falta. Lo normal es 1, y que
    #    suba a 2 es una senal de que el contenido crecio.
    datos["espacio_sobrante"] = round(lienzo.y - PIE_DE_PAGINA, 1)
    datos["paginas"] = lienzo.pagina.paginas
    return lienzo.pagina.guardar(ruta)


def armar(diagnostico, nombre, fondo, ruta, caso=None, datos_persona=None):
    """Saca los datos del diagnostico y escribe el PDF. Devuelve los dos."""
    datos = datos_del_reporte(diagnostico, nombre, fondo, caso=caso,
                              datos_persona=datos_persona)
    escribir_pdf(datos, ruta)
    return datos, ruta


def main():
    if len(sys.argv) < 5:
        print("Uso: python3 reporte/armar_reporte.py <diagnostico.json> "
              "<nombre> <fondo> <salida.pdf> [caso.json]")
        sys.exit(1)
    diagnostico = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    # El caso es opcional: sin el, las secciones 4 y 5 salen con el texto
    # honesto de que no se pudieron cuantificar palancas.
    caso = None
    if len(sys.argv) > 5:
        caso = json.loads(Path(sys.argv[5]).read_text(encoding="utf-8"))
    _, ruta = armar(diagnostico, sys.argv[2], sys.argv[3], sys.argv[4],
                    caso=caso)
    print(json.dumps({"ok": True, "archivo": str(ruta)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
