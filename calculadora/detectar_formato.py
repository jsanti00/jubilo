# Detector de formato: mira el texto de un documento y dice de quien es.
#
# POR QUE EXISTE. Cada administradora imprime la historia laboral con su propia
# plantilla. Si sabemos cual plantilla es, un programa puede leer la tabla en
# menos de un segundo. Si no la reconocemos, no se adivina: el documento se
# manda al camino de siempre (que lo lea el modelo). Esa es la regla de oro de
# este archivo: **ante la duda, decir que no se sabe.** Una deteccion
# equivocada es peor que no detectar nada, porque el parser equivocado puede
# sacar numeros que parecen validos y no lo son.
#
# Como decide. Cada formato tiene unas "senales obligatorias": trozos de texto
# que SIEMPRE salen en esa plantilla (titulos, encabezados de columna, el NIT
# de la entidad). Si estan todas, el formato es ese. Si a un formato le falta
# una sola senal obligatoria, queda descartado.
#
# Dos conceptos que no hay que confundir:
#   - historia laboral: la lista completa de lo que ha cotizado la persona.
#   - extracto de cuenta: el resumen trimestral que manda un fondo privado.
#     Trae el saldo y el total de semanas, pero solo los movimientos de esos
#     tres meses. NO reemplaza a la historia laboral.

import re
import unicodedata


def _normalizar(texto):
    """Deja el texto comparable: sin tildes, en minusculas y sin espacios de mas.

    Los PDF de una misma entidad cambian los espacios entre palabras de una
    version a otra, y algunos pierden las tildes. Comparar sobre el texto
    normalizado evita que el detector falle por una tilde o un espacio doble.
    """
    sin_tildes = unicodedata.normalize("NFKD", texto)
    sin_tildes = "".join(c for c in sin_tildes if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", sin_tildes.lower())


# La tabla de formatos conocidos. Cada entrada dice: como se llama el formato,
# quien lo emite, de que regimen es, si es historia laboral o extracto, y que
# senales tienen que aparecer todas para darlo por reconocido.
#
# El orden importa: se revisa de arriba abajo y gana el primero que cumpla.
FORMATOS = [
    {
        "formato": "colpensiones_reporte_semanas",
        "emisora": "Colpensiones",
        "regimen": "RPM",
        "tipo_documento": "historia_laboral",
        "senales": [
            "colpensiones",
            "reporte de semanas cotizadas en pensiones",
            "[2]nombre o razon social",
        ],
    },
    {
        "formato": "colfondos_reporte_historia",
        "emisora": "Colfondos",
        "regimen": "RAIS",
        "tipo_documento": "historia_laboral",
        "senales": [
            "colfondos",
            "reporte de historia laboral",
            "semanas cotizadas al sistema general de pensiones",
        ],
    },
    {
        "formato": "porvenir_historia_laboral",
        "emisora": "Porvenir",
        "regimen": "RAIS",
        "tipo_documento": "historia_laboral",
        "senales": [
            "resumen de tu historia laboral",
            "detalle de tu historia laboral",
            "saldo total acumulado",
            # La plantilla no lleva el nombre del fondo en el encabezado: el
            # unico sitio donde aparece es la columna "Administradora de
            # pensiones". Por eso se exige aqui, para no confundirla con la
            # plantilla parecida de otro fondo.
            "porvenir",
        ],
    },
    {
        "formato": "historia_laboral_consolidada",
        "emisora": None,      # se lee del propio documento, ver el parser
        "regimen": "RAIS",
        "tipo_documento": "historia_laboral",
        "senales": [
            "historia laboral consolidada",
            "datos basicos del afiliado",
            "regimen de ahorro individual con solidaridad",
        ],
    },
    {
        "formato": "proteccion_extracto_trimestral",
        "emisora": "Proteccion",
        "regimen": "RAIS",
        "tipo_documento": "extracto_cuenta",
        "senales": [
            "extracto de pension obligatoria",
            "resumen de mi cuenta individual de ahorro pensional",
            "movimientos de mi cuenta de ahorro individual en el trimestre",
        ],
    },
]

# Formatos que sabemos que existen pero que todavia no tienen parser. Sirven
# para dar un motivo util en el reporte en vez de un "no se que es esto".
CONOCIDOS_SIN_PARSER = [
    {
        "formato": "proteccion_historia_laboral",
        "senales": ["proteccion", "historia laboral", "origen de la informacion"],
    },
]


def detectar(texto):
    """Dice de que formato es el documento.

    Devuelve siempre un diccionario, nunca lanza error. Las llaves:
      - reconocido: True solo si hay un parser capaz de leerlo.
      - formato, emisora, regimen, tipo_documento: lo que se detecto.
      - motivo: por que no se reconocio, cuando reconocido es False.
      - senales_vistas: que trozos de texto dispararon la deteccion. Sirve
        para depurar sin tener que abrir el documento de la persona.
    """
    plano = _normalizar(texto or "")

    # Caso 1: el documento no trae letras (es una foto o un escaneo).
    if len(plano.strip()) < 200:
        return {"reconocido": False, "formato": None, "emisora": None,
                "regimen": None, "tipo_documento": None,
                "motivo": "sin_capa_de_texto",
                "senales_vistas": []}

    # Caso 2: se busca la primera plantilla cuyas senales aparezcan todas.
    for ficha in FORMATOS:
        if all(s in plano for s in ficha["senales"]):
            return {"reconocido": True,
                    "formato": ficha["formato"],
                    "emisora": ficha["emisora"],
                    "regimen": ficha["regimen"],
                    "tipo_documento": ficha["tipo_documento"],
                    "motivo": None,
                    "senales_vistas": list(ficha["senales"])}

    # Caso 3: se parece a un formato que conocemos pero que aun no sabemos leer.
    for ficha in CONOCIDOS_SIN_PARSER:
        if all(s in plano for s in ficha["senales"]):
            return {"reconocido": False, "formato": ficha["formato"],
                    "emisora": None, "regimen": None, "tipo_documento": None,
                    "motivo": "formato_conocido_sin_parser",
                    "senales_vistas": list(ficha["senales"])}

    # Caso 4: no se parece a nada de lo que tenemos. Se va al camino de siempre.
    return {"reconocido": False, "formato": None, "emisora": None,
            "regimen": None, "tipo_documento": None,
            "motivo": "formato_desconocido", "senales_vistas": []}
