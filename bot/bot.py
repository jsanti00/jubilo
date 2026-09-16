"""Bot de Telegram de Júbilo.

Cada mensaje dispara una ejecución de `claude -p` en el directorio privado
del usuario que escribió. Nadie comparte contexto con nadie.
"""

import asyncio
import datetime
import json
import logging
import os
import pathlib
import sqlite3
import subprocess
import time
import unicodedata
import urllib.parse
import urllib.request

from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters

# --- Rutas y constantes -----------------------------------------------------

BASE = pathlib.Path("/srv/jubilo")          # todo vive debajo de aqui
USUARIOS = BASE / "usuarios"                # una carpeta por persona
REPO = BASE / "jubilo"                      # el codigo de la calculadora y el kit
DB = BASE / "estado.db"                     # que sesion de Claude tiene cada usuario
CLAUDE = str(pathlib.Path.home() / ".local/bin/claude")
TIMEOUT = 600                               # 10 minutos maximo por respuesta

# Donde el /login dejo guardada la llave de la cuenta de Claude. Es una sola
# cuenta para todo el bot, asi que cada usuario apunta a este mismo archivo.
CREDENCIALES = pathlib.Path.home() / ".claude" / ".credentials.json"

# El chat de Telegram del dueno del bot (Santiago). Ahi llegan los avisos de que
# algo se rompio, para que nadie tenga que darse cuenta mirando el log.
ADMIN_CHAT_ID = "5226290061"

# Donde queda anotada la hora del ultimo aviso que se le mando al dueno. Va en un
# archivo y no en memoria porque el servicio se reinicia solo y perderia la cuenta.
MARCA_ULTIMO_AVISO = BASE / "ultimo-aviso.txt"

# Cuanto hay que esperar entre un aviso y el siguiente: 6 horas, en segundos.
# Asi, aunque fallen cien mensajes seguidos, el telefono suena una sola vez.
ESPERA_ENTRE_AVISOS = 6 * 60 * 60

# El texto exacto de la bienvenida con el aviso de privacidad. Vive en el repo
# y en un solo lugar: si se edita alli, cambia aqui, sin tocar el bot.
ARCHIVO_BIENVENIDA = REPO / "kit-contexto" / "bienvenida-y-aviso.txt"

# La version del aviso que se esta mostrando hoy. Hay que subirla a mano cada vez
# que el texto cambie de fondo, porque la ley obliga a poder reconstruir
# que version vio cada persona.
VERSION_AVISO = "1.1"

# Solo puede leer archivos y correr la calculadora. Nada de escribir ni de internet.
HERRAMIENTAS = f"Read,Bash(python3 {REPO}/calculadora/*)"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.FileHandler(BASE / "bot.log"), logging.StreamHandler()],
)
log = logging.getLogger("jubilo")

# La libreria de Telegram anota cada llamada a internet, y el token del bot va
# dentro de esa direccion. Le pedimos que solo hable cuando haya un problema,
# para que la llave del bot no quede escrita en el archivo de log.
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

# El archivo de log solo lo puede leer el usuario jubilo.
os.chmod(BASE / "bot.log", 0o600)

# Un candado: atiende de a un usuario a la vez, para no reventar la cuota.
CANDADO = asyncio.Lock()


# --- Guardar que sesion de Claude corresponde a cada chat -------------------

def inicializar_db():
    """Crea las tres tablas si es la primera vez que arranca el bot."""
    con = sqlite3.connect(DB)

    # La que ya existia: que conversacion de Claude le corresponde a cada persona.
    con.execute("CREATE TABLE IF NOT EXISTS sesiones (chat_id TEXT PRIMARY KEY, session_id TEXT)")

    # La prueba de la autorizacion. Una fila por persona.
    # ts_aviso     = cuando se le mostro el aviso de privacidad
    # ts_documento = cuando mando su historia laboral (eso es el "si" de la persona)
    con.execute("""
        CREATE TABLE IF NOT EXISTS autorizaciones (
            chat_id       TEXT PRIMARY KEY,
            version_aviso TEXT NOT NULL,
            ts_aviso      TEXT NOT NULL,
            ts_documento  TEXT,
            observaciones TEXT
        )
    """)

    # Las peticiones sobre sus propios datos. Los plazos legales corren desde aqui,
    # asi que la fecha de cada una tiene que quedar escrita.
    con.execute("""
        CREATE TABLE IF NOT EXISTS solicitudes (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id  TEXT NOT NULL,
            tipo     TEXT NOT NULL,
            ts       TEXT NOT NULL,
            atendida TEXT
        )
    """)

    con.commit()
    con.close()


def leer_sesion(chat_id):
    """Devuelve el id de sesion de este usuario, o None si es su primer mensaje."""
    con = sqlite3.connect(DB)
    fila = con.execute("SELECT session_id FROM sesiones WHERE chat_id = ?", (str(chat_id),)).fetchone()
    con.close()
    return fila[0] if fila else None


def guardar_sesion(chat_id, session_id):
    """Anota el id de sesion para que el proximo mensaje continue la conversacion."""
    con = sqlite3.connect(DB)
    con.execute("INSERT OR REPLACE INTO sesiones VALUES (?, ?)", (str(chat_id), session_id))
    con.commit()
    con.close()


# --- El registro de la autorizacion (Ley 1581) ------------------------------

def ahora():
    """La hora actual en formato ISO, con zona horaria. Es lo que queda como prueba."""
    return datetime.datetime.now(datetime.timezone.utc).astimezone().isoformat(timespec="seconds")


def vio_el_aviso(chat_id):
    """Dice si a esta persona ya se le mostro el aviso de privacidad alguna vez."""
    con = sqlite3.connect(DB)
    fila = con.execute("SELECT 1 FROM autorizaciones WHERE chat_id = ?", (str(chat_id),)).fetchone()
    con.close()
    return fila is not None


def registrar_aviso(chat_id):
    """Anota que a esta persona se le acaba de mostrar el aviso, con hora y version.
    Si ya estaba anotada no hace nada: el aviso se muestra una sola vez."""
    con = sqlite3.connect(DB)
    con.execute(
        "INSERT OR IGNORE INTO autorizaciones (chat_id, version_aviso, ts_aviso) VALUES (?, ?, ?)",
        (str(chat_id), VERSION_AVISO, ahora()),
    )
    con.commit()
    con.close()
    log.info("aviso %s mostrado a %s", VERSION_AVISO, chat_id)


def registrar_documento(chat_id):
    """Anota la hora en que la persona mando su historia laboral. Solo la primera vez:
    ese primer envio, hecho despues de ver el aviso, es la autorizacion."""
    con = sqlite3.connect(DB)
    con.execute(
        "UPDATE autorizaciones SET ts_documento = ? WHERE chat_id = ? AND ts_documento IS NULL",
        (ahora(), str(chat_id)),
    )
    con.commit()
    con.close()


def registrar_solicitud(chat_id, tipo):
    """Anota que la persona pidio algo sobre sus propios datos, con la fecha.
    Los plazos de respuesta (10 o 15 dias habiles) se cuentan desde esta fecha."""
    con = sqlite3.connect(DB)
    con.execute(
        "INSERT INTO solicitudes (chat_id, tipo, ts) VALUES (?, ?, ?)",
        (str(chat_id), tipo, ahora()),
    )
    con.commit()
    con.close()
    log.info("solicitud '%s' de %s", tipo, chat_id)


def detectar_solicitud(texto):
    """Mira si el mensaje es una de las dos peticiones de datos que el aviso le prometio.
    Compara en minusculas y sin tildes para que 'Politica de datos' tambien entre."""
    limpio = unicodedata.normalize("NFD", texto.lower())
    limpio = "".join(c for c in limpio if unicodedata.category(c) != "Mn")
    if "mis datos" in limpio:
        return "mis datos"
    if "politica de datos" in limpio:
        return "politica de datos"
    return None


# --- Preparar el espacio privado de cada usuario ----------------------------

def asegurar_credenciales(carpeta_claude):
    """Deja en la carpeta privada del usuario un acceso directo a la llave de la cuenta.

    Cada usuario tiene su propio almacen de conversaciones (ahi esta el aislamiento),
    pero todos usan la misma suscripcion de Claude. Sin este acceso directo, Claude
    responderia "no has iniciado sesion". Se revisa en cada mensaje por si el archivo
    se reemplazo al renovarse el token.
    """
    enlace = carpeta_claude / ".credentials.json"
    if enlace.is_symlink() and enlace.resolve() == CREDENCIALES.resolve():
        return                               # ya esta bien puesto, no hay nada que hacer
    if enlace.exists() or enlace.is_symlink():
        enlace.unlink()                      # quitamos lo que haya quedado mal
    enlace.symlink_to(CREDENCIALES)          # y ponemos el acceso directo correcto


def carpeta_del_usuario(chat_id):
    """Crea (la primera vez) y devuelve la carpeta privada de esta persona."""
    carpeta = USUARIOS / str(chat_id)
    if not carpeta.exists():
        carpeta.mkdir(parents=True)
        (carpeta / ".claude").mkdir()        # su propio almacen de sesiones
        (carpeta / "extracciones").mkdir()   # donde deja los JSON extraidos
        # Este archivo es lo que Claude lee al arrancar en esta carpeta.
        # Le dice quien es y donde esta su kit.
        (carpeta / "CLAUDE.md").write_text(
            f"""# Eres Júbilo

Tu system prompt completo está en `{REPO}/kit-contexto/system-prompt.md`.
Léelo antes de responder nada y síguelo al pie de la letra.

Tu kit de contexto está en `{REPO}/kit-contexto/`.
Tu calculadora está en `{REPO}/calculadora/`.
Las extracciones de esta conversación van en `{carpeta}/extracciones/`.

Estás hablando por Telegram con una persona. Responde en texto plano,
sin encabezados de markdown y sin bloques de código.
""",
            encoding="utf-8",
        )
    asegurar_credenciales(carpeta / ".claude")
    return carpeta


# --- Avisarle al dueno cuando la sesion de Claude se vence ------------------

def leer_token():
    """Saca la llave del bot de Telegram del archivo de configuracion.

    Es el mismo archivo que usa el arranque. Se lee linea por linea y nos
    quedamos con lo que viene despues del '=' en la linea del token.
    Devuelve None si no la encuentra.
    """
    for linea in (BASE / "config/.env").read_text().splitlines():
        if linea.startswith("TELEGRAM_TOKEN="):
            return linea.split("=", 1)[1].strip()
    return None


def toca_avisar():
    """Dice si ya pasaron las 6 horas desde el ultimo aviso.

    Lee la hora guardada en el archivo de marca. Si el archivo no existe, o no
    se puede leer, asumimos que nunca se ha avisado y decimos que si.
    """
    try:
        anterior = float(MARCA_ULTIMO_AVISO.read_text().strip())
    except (OSError, ValueError):
        return True
    return (time.time() - anterior) >= ESPERA_ENTRE_AVISOS


def avisar_sesion_vencida(es_prueba=False):
    """Le manda un mensaje de Telegram al dueno diciendole que hay que volver a entrar.

    Va entero dentro de un try: si el aviso falla, se anota en el log y ya. El
    usuario que escribio igual recibe su respuesta; un aviso roto nunca puede
    tumbar el bot.

    Con es_prueba=True (solo cuando alguien lo dispara a mano para comprobar que
    el aviso funciona) el mensaje llega marcado como prueba, se salta la espera
    de las 6 horas y no anota la marca de tiempo, para no tapar un aviso de verdad.
    """
    try:
        # Si ya se aviso hace poco, no se repite. Las pruebas no cuentan.
        if not es_prueba and not toca_avisar():
            return

        token = leer_token()
        if not token:
            log.error("no se pudo avisar: no hay token en config/.env")
            return

        # El texto que va a leer el dueno en su chat. Si es una prueba, se avisa
        # al principio para que nadie salga corriendo a arreglar algo que no pasa.
        marca = "[PRUEBA, no es un fallo real] " if es_prueba else ""
        texto = (
            f"{marca}Júbilo: la sesión de Claude en el servidor se venció. "
            "Entra por SSH y corre `claude` y luego `/login`. "
            "Mientras tanto el bot le está diciendo a todos que no tiene capacidad."
        )

        # La direccion de la API de Telegram para mandar un mensaje. Los datos
        # van en el cuerpo de la peticion, no en la direccion, para que el token
        # no termine escrito en ningun log de red.
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        cuerpo = urllib.parse.urlencode({"chat_id": ADMIN_CHAT_ID, "text": texto}).encode("utf-8")
        peticion = urllib.request.Request(url, data=cuerpo)

        # Se manda y se espera maximo 10 segundos la respuesta.
        with urllib.request.urlopen(peticion, timeout=10):
            pass

        # Queda anotada la hora, para no volver a avisar en 6 horas. Una prueba
        # no la escribe: asi no bloquea el aviso real que venga despues.
        if not es_prueba:
            MARCA_ULTIMO_AVISO.write_text(str(time.time()))
        log.info("aviso de sesion vencida enviado al dueno (prueba=%s)", es_prueba)
    except Exception as e:
        # A proposito atrapamos cualquier error: el aviso es opcional.
        log.error("no se pudo mandar el aviso de sesion vencida: %s", e)


# --- Llamar a Claude --------------------------------------------------------

def preguntarle_a_claude(chat_id, texto):
    """Corre `claude -p` una vez y devuelve (respuesta, id_de_sesion)."""
    carpeta = carpeta_del_usuario(chat_id)

    # La variable clave del aislamiento: cada usuario, su propio directorio de estado.
    entorno = os.environ.copy()
    entorno["CLAUDE_CONFIG_DIR"] = str(carpeta / ".claude")

    comando = [
        CLAUDE, "-p", texto,
        "--output-format", "json",
        "--add-dir", str(carpeta),   # puede ver su propia carpeta
        "--add-dir", str(REPO),      # y el kit y la calculadora
        "--allowedTools", HERRAMIENTAS,
        # Sin esto, Claude arranca en modo automatico y decide solo que permite.
        # Con esto, manda la lista de arriba y nada mas.
        "--permission-mode", "default",
    ]

    # Si ya hablo antes, continuamos su conversacion en vez de empezar de cero.
    sesion = leer_sesion(chat_id)
    if sesion:
        comando += ["--resume", sesion]

    salida = subprocess.run(
        comando, cwd=str(carpeta), env=entorno,
        capture_output=True, text=True, timeout=TIMEOUT,
    )

    if salida.returncode != 0:
        log.error("claude fallo para %s: %s", chat_id, salida.stderr[:500])
        return None, None

    datos = json.loads(salida.stdout)

    # Claude a veces termina "bien" pero con un error adentro (por ejemplo, si la
    # sesion se vencio). Lo tratamos como fallo para no mandarle basura a la persona.
    if datos.get("is_error"):
        log.error("claude devolvio error para %s: %s", chat_id, str(datos.get("result"))[:300])

        # Si el error es que la cuenta ya no tiene sesion iniciada, nadie se
        # enteraria: al usuario solo le decimos que no hay capacidad. Asi que le
        # mandamos un mensaje al dueno para que entre a hacer /login.
        if "not logged in" in str(datos.get("result")).lower():
            avisar_sesion_vencida()

        return None, None

    return datos.get("result"), datos.get("session_id")


# --- Lo que pasa cuando llega un mensaje ------------------------------------

async def al_recibir_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    mensaje = update.message

    # --- Candado de la autorizacion previa -----------------------------------
    # Si es la primera vez que esta persona escribe, el bot le contesta el
    # aviso de privacidad y ahi termina el turno. Claude no se entera todavia.
    # Asi es imposible que alguien mande su historia laboral sin haber visto
    # antes que se va a hacer con ella, que es lo que exige la ley.
    if not vio_el_aviso(chat_id):
        registrar_aviso(chat_id)
        await mensaje.reply_text(ARCHIVO_BIENVENIDA.read_text(encoding="utf-8"))

        # Si de una mando su historia laboral sin haber visto el aviso, no se
        # procesa: se le pide que la reenvie, ya sabiendo a que dice que si.
        if mensaje.document or mensaje.photo:
            await mensaje.reply_text(
                "Vi que ya me mandaste un archivo, pero no lo abri todavia: "
                "queria que primero leyeras lo de arriba. Reenviamelo y sigo."
            )
        return

    # --- Peticiones sobre sus propios datos ----------------------------------
    # Se registran antes de responder, porque los plazos legales corren desde
    # que la persona lo pide, no desde que se le contesta. Despues el mensaje
    # sigue su camino normal y Claude responde con lo que dice el system prompt.
    tipo = detectar_solicitud(mensaje.text or mensaje.caption or "")
    if tipo:
        registrar_solicitud(chat_id, tipo)

    # --- El archivo que manda la persona -------------------------------------
    if mensaje.document or mensaje.photo:
        # Llego su historia laboral y ya habia visto el aviso: este envio es
        # la autorizacion, y queda con fecha y hora.
        registrar_documento(chat_id)

        carpeta = carpeta_del_usuario(chat_id)
        archivo_tg = mensaje.document or mensaje.photo[-1]
        nombre = getattr(archivo_tg, "file_name", None) or f"{archivo_tg.file_unique_id}.jpg"
        destino = carpeta / nombre
        descargable = await context.bot.get_file(archivo_tg.file_id)
        await descargable.download_to_drive(str(destino))
        texto = (mensaje.caption or "") + f"\n\n[El usuario adjuntó un archivo: {destino}]"
    else:
        texto = mensaje.text or ""

    if not texto.strip():
        return

    # Acuse inmediato: la regla de producto prohibe el silencio mientras se procesa.
    await mensaje.reply_text("Recibido. Dame un momento.")
    await context.bot.send_chat_action(chat_id, "typing")

    # De a uno a la vez, para no reventar la cuota de la cuenta.
    async with CANDADO:
        try:
            respuesta, sesion = await asyncio.to_thread(preguntarle_a_claude, chat_id, texto)
        except subprocess.TimeoutExpired:
            await mensaje.reply_text("Esto se está demorando más de lo normal. Escríbeme otra vez en unos minutos.")
            return

    if respuesta is None:
        await mensaje.reply_text(
            "Se me agotó la capacidad por ahora. Vuelve a escribirme en un rato "
            "y seguimos donde quedamos, no perdiste nada."
        )
        return

    if sesion:
        guardar_sesion(chat_id, sesion)

    # Telegram corta en 4096 caracteres: partimos si hace falta.
    for i in range(0, len(respuesta), 4000):
        await mensaje.reply_text(respuesta[i:i + 4000])


def main():
    USUARIOS.mkdir(parents=True, exist_ok=True)
    inicializar_db()

    # La llave del bot sale del archivo de configuracion, con la misma funcion
    # que usa el aviso al dueno.
    token = leer_token()

    app = Application.builder().token(token).build()
    app.add_handler(MessageHandler(filters.TEXT | filters.Document.ALL | filters.PHOTO, al_recibir_mensaje))
    log.info("Júbilo arrancó")
    app.run_polling()


if __name__ == "__main__":
    main()
