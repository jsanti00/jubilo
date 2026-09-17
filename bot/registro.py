"""El cuaderno de bitacora de Júbilo.

Aqui vive todo lo que el bot anota mientras conversa: cada turno, cuanto tardo,
cuanto costo y que paso. Es lo que despues se lee en frio para saber si el bot
esta sirviendo y donde se atasca la gente.

Esta separado de `bot.py` a proposito: aqui no se importa nada de Telegram, asi
que estas funciones se pueden probar en el Mac sin servidor y sin internet
(`python3 bot/probar_registro.py`).

Dos promesas que este archivo tiene que cumplir, porque estan escritas en el
aviso de privacidad que la gente acepta:
  1. La conversacion se guarda SIN nombre y SIN cedula.
  2. Nadie queda identificado por su chat de Telegram: se guarda un seudonimo.
"""

import hashlib
import re
import secrets
import sqlite3


# --- Las tablas -------------------------------------------------------------

def inicializar(db):
    """Crea las dos tablas de bitacora si no existen todavia.

    `turnos`  = una fila por mensaje que alguien manda y por lo que se le respondio.
    `eventos` = una fila por hito suelto (vio el aviso, mando el documento, fallo algo).
    """
    con = sqlite3.connect(db)

    con.execute("""
        CREATE TABLE IF NOT EXISTS turnos (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            seudonimo       TEXT NOT NULL,   -- quien, sin poder saber quien
            ts              TEXT NOT NULL,   -- cuando, con fecha y hora
            texto_usuario   TEXT,            -- lo que escribio, ya sin datos personales
            respuesta       TEXT,            -- lo que Júbilo contesto
            tuvo_adjunto    INTEGER,         -- 1 si mando un archivo o una foto
            resultado       TEXT,            -- ok, error, timeout o sin_capacidad
            espera_cola_ms  INTEGER,         -- cuanto espero su turno por el candado
            latencia_ms     INTEGER,         -- cuanto tardo Claude en responder
            costo_usd       REAL,            -- lo que costo ese mensaje
            tokens_entrada  INTEGER,
            tokens_salida   INTEGER,
            turnos_internos INTEGER          -- cuantas vueltas dio Claude por dentro
        )
    """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS eventos (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            seudonimo TEXT NOT NULL,
            ts        TEXT NOT NULL,
            evento    TEXT NOT NULL,
            detalle   TEXT
        )
    """)

    # Indices para que el reporte no tenga que recorrer toda la tabla.
    con.execute("CREATE INDEX IF NOT EXISTS idx_turnos_persona ON turnos (seudonimo, ts)")
    con.execute("CREATE INDEX IF NOT EXISTS idx_eventos_persona ON eventos (seudonimo, ts)")

    con.commit()
    con.close()


# --- El seudonimo: quien escribio, sin poder saber quien es -----------------

def obtener_sal(ruta):
    """Devuelve la sal del servidor, y la inventa la primera vez.

    Una "sal" es un numero secreto al azar que se mezcla con el chat de Telegram
    antes de convertirlo en seudonimo. Sin ella, cualquiera que consiga la base
    podria probar chats uno por uno hasta dar con el que cuadra. Con ella, no.
    Vive solo en el servidor y nunca sale en los reportes.
    """
    if not ruta.exists():
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_text(secrets.token_hex(32))
        ruta.chmod(0o600)          # solo el usuario del bot puede leerla
    return ruta.read_text().strip()


def seudonimo(chat_id, sal):
    """Convierte el chat de Telegram en una etiqueta corta y estable.

    Estable quiere decir que la misma persona siempre da la misma etiqueta, asi
    se puede seguir su conversacion completa. Y no se puede devolver: de la
    etiqueta no se llega al chat.
    """
    revuelto = hashlib.sha256(f"{sal}:{chat_id}".encode("utf-8")).hexdigest()
    return revuelto[:12]


# --- Tachar los datos personales antes de guardar ---------------------------

# Palabras que en Colombia anteceden a un numero de documento. Si vemos una de
# estas seguida de cualquier numero, ese numero se tacha sin preguntar.
PALABRAS_DOCUMENTO = r"(?:c[eé]dula|c\.?\s?c\.?|documento|identificaci[oó]n|nit|pasaporte|t\.?\s?i\.?)"

# Frases con las que la gente dice su nombre. Se tacha lo que venga despues.
PALABRAS_NOMBRE = r"(?:me llamo|mi nombre es|nombre completo|soy el se[nñ]or|soy la se[nñ]ora|nombre\s*:)"

REGLAS = [
    # La ruta de la carpeta privada del usuario. Lleva su chat de Telegram
    # dentro del nombre, asi que dejarla pasar echaria a perder el seudonimo.
    (re.compile(r"/srv/jubilo/usuarios/\d+"), "[carpeta-de-la-persona]"),

    # Correos electronicos.
    (re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b"), "[correo]"),

    # Un numero que viene despues de la palabra "cedula", "CC", "NIT", etc.
    # Entre la palabra y el numero se permiten hasta tres palabritas de relleno
    # ("mi cedula ES 79.482.310", "documento NO. 41.238.905"). Se conserva la
    # palabra y se tacha solo el numero.
    (re.compile(
        rf"(\b{PALABRAS_DOCUMENTO}\s*(?:(?:es|son|el|la|n[uú]mero|no|nro|n°|num)\.?\s*){{0,3}}[:#.-]?\s*)"
        r"([\d][\d.,\s-]{5,}\d)",
        re.IGNORECASE), r"\1[documento]"),

    # Telefonos escritos con indicativo: +57 300 123 4567.
    (re.compile(r"\+\s?57[\s-]?\d[\d\s-]{8,12}\d"), "[telefono]"),

    # Un numero largo pegado, sin puntos ni comas: 8 a 11 digitos. Asi se escribe
    # una cedula o un celular. La plata en cambio casi siempre lleva puntos o un
    # signo de pesos delante, y por eso los salarios no caen aqui.
    (re.compile(r"(?<![\d.,$])\d{8,11}(?![\d.,])"), "[numero-largo]"),

    # El nombre que la persona dice de viva voz. Se tachan hasta cuatro palabras
    # que empiecen en mayuscula despues de la frase que las anuncia.
    (re.compile(rf"({PALABRAS_NOMBRE})(\s+(?:[A-ZÁÉÍÓÚÑ][\wÁÉÍÓÚÑáéíóúñ'-]*\s*){{1,4}})", re.IGNORECASE), r"\1 [nombre]"),
]


def redactar(texto):
    """Devuelve el mismo texto con los datos personales tachados.

    No es magia: tacha lo que sigue un patron claro (correos, cedulas, telefonos,
    "me llamo X"). Un nombre suelto en mitad de una frase se le puede escapar, y
    por eso el reporte se lee sabiendo eso. Lo que si esta garantizado es que el
    archivo de la historia laboral nunca entra aqui: de el solo se guarda que
    hubo un adjunto, no su contenido.
    """
    if not texto:
        return texto
    for patron, reemplazo in REGLAS:
        texto = patron.sub(reemplazo, texto)
    return texto


# --- Escribir en la bitacora ------------------------------------------------

def anotar_turno(db, **campos):
    """Guarda una fila de la tabla `turnos`.

    Se llama con los nombres de las columnas (anotar_turno(db, seudonimo=..., ts=...)).
    Lo que no se pase queda vacio. Los textos se tachan aqui adentro, de modo que
    es imposible guardarlos sin pasar por el filtro aunque alguien se olvide.
    """
    campos["texto_usuario"] = redactar(campos.get("texto_usuario"))
    campos["respuesta"] = redactar(campos.get("respuesta"))

    columnas = ", ".join(campos)
    huecos = ", ".join("?" for _ in campos)
    con = sqlite3.connect(db)
    con.execute(f"INSERT INTO turnos ({columnas}) VALUES ({huecos})", tuple(campos.values()))
    con.commit()
    con.close()


def anotar_evento(db, seudonimo_, ts, evento, detalle=None):
    """Guarda un hito suelto: vio el aviso, mando el documento, se cayo algo."""
    con = sqlite3.connect(db)
    con.execute(
        "INSERT INTO eventos (seudonimo, ts, evento, detalle) VALUES (?, ?, ?, ?)",
        (seudonimo_, ts, evento, redactar(detalle)),
    )
    con.commit()
    con.close()


def borrar_persona(db, seudonimo_):
    """Borra todo rastro de una persona en la bitacora.

    Es lo que hay que correr cuando alguien escribe "mis datos" y pide que se le
    borre lo suyo. Devuelve cuantas filas se fueron, para dejarlo por escrito.
    """
    con = sqlite3.connect(db)
    t = con.execute("DELETE FROM turnos WHERE seudonimo = ?", (seudonimo_,)).rowcount
    e = con.execute("DELETE FROM eventos WHERE seudonimo = ?", (seudonimo_,)).rowcount
    con.commit()
    con.close()
    return t + e


# --- Una pista de si la respuesta fue el diagnostico ------------------------

# Un diagnostico entregado casi siempre trae una cifra en pesos y la palabra
# pension. No es infalible, y por eso en el reporte sale marcado como "probable".
SENA_DIAGNOSTICO = re.compile(r"\$\s?[\d.,]{5,}", re.IGNORECASE)


def parece_diagnostico(respuesta):
    """Dice si la respuesta parece ser ya el diagnostico y no una pregunta mas."""
    if not respuesta:
        return False
    tiene_plata = bool(SENA_DIAGNOSTICO.search(respuesta))
    tiene_tema = any(p in respuesta.lower() for p in ("pensión", "pension", "mesada"))
    return tiene_plata and tiene_tema
