"""Bot de Telegram de Júbilo.

Cada mensaje dispara una ejecución de `claude -p` en el directorio privado
del usuario que escribió. Nadie comparte contexto con nadie.
"""

import asyncio
import datetime
import hashlib
import json
import logging
import os
import pathlib
import re
import sqlite3
import subprocess
import sys
import time
import unicodedata
import urllib.parse
import urllib.request

from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters

# El cuaderno de bitacora: vive al lado de este archivo, en el mismo servidor.
import registro

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
#
# 1.2 (2026-09-18): la cedula deja de ser solo una llave para abrir el PDF y
# pasa a ser un dato que se le transmite a Colpensiones cuando la persona pide
# que le consigamos su historia laboral. Eso es un tratamiento nuevo y por eso
# sube la version. El historial de las versiones esta en
# kit-contexto/aviso-de-privacidad.md.
VERSION_AVISO = "1.2"

# El secreto con el que se disfraza el chat de Telegram de cada persona antes de
# anotar nada. Se crea solo la primera vez que arranca el bot y no sale de aqui.
ARCHIVO_SAL = BASE / "config" / "sal.txt"
SAL = None                                  # se llena al arrancar, en main()

# --- El reporte de cierre y la pregunta del final ---------------------------
#
# Cuando una conversacion se queda callada, quiere decir que ya termino. En ese
# momento el bot le manda a la persona su diagnostico en una pagina de PDF, que
# es algo que se guarda, se relee y se reenvia, a diferencia de unos mensajes
# de chat que se pierden hacia arriba en el scroll.

# Cuanto silencio hace falta para dar la conversacion por terminada: 30 minutos.
#
# Por que 30 y no menos: la respuesta mas lenta medida hasta hoy tardo 320
# segundos (algo mas de 5 minutos), y la conversacion mas larga del primer grupo
# de prueba duro 57 minutos con pausas de varios minutos entre mensajes. Con 10
# o 15 minutos el reporte le caeria encima a alguien que todavia esta leyendo y
# pensando la siguiente pregunta, y eso se siente como que lo estan echando.
#
# Por que 30 y no mas: pasada la media hora la persona ya se fue del chat, y un
# reporte que llega tres horas despues llega cuando ya nadie se acuerda del tema.
# Media hora es el punto donde la conversacion claramente acabo y la persona
# todavia tiene el tema fresco.
#
# Esta en una constante justamente para poder moverlo sin buscarlo. Es el numero
# que mas probablemente haya que ajustar con datos reales.
MINUTOS_DE_SILENCIO_PARA_CERRAR = 30

# Lo mismo en segundos, que es lo que pide el temporizador de la libreria.
ESPERA_PARA_CERRAR = MINUTOS_DE_SILENCIO_PARA_CERRAR * 60

# Donde se escribe el PDF mientras se manda. Es una carpeta aparte, y no la del
# usuario, para que la regla sea simple de verificar: todo lo que este aqui es
# temporal y se puede borrar.
#
# **Que pasa con el PDF despues de mandarlo, que es lo importante:** el archivo
# lleva datos personales (el nombre de la persona y toda su situacion pensional),
# asi que se borra apenas Telegram confirma que lo recibio, en el `finally` de
# `mandar_reporte_de_cierre`. En disco no queda nada. Y por si el proceso se
# muere justo en la mitad, al arrancar se barre la carpeta entera (ver `main`).
# El unico sitio donde el reporte sobrevive es el chat de su dueno.
CARPETA_REPORTES = BASE / "reportes"

# El texto que acompana al PDF en el mismo mensaje.
TEXTO_REPORTE = (
    "Te dejo tu diagnóstico en una página, para que lo guardes o se lo muestres "
    "a quien quieras. Es preliminar: no es una liquidación certificada."
)

# La pregunta que va DESPUES del reporte, nunca antes.
#
# TEXTO APROBADO POR SANTIAGO EL 2026-09-19. No se cambia sin decirselo.
#
# Que pide, y son dos cosas en una sola pregunta: si le quedo alguna duda de su
# pension (o sea, si hay algo mas que podamos hacer por ella) y que deberiamos
# hacer distinto como producto.
#
# Tres decisiones de redaccion que estan detras de este texto, para que nadie
# las deshaga sin querer al "mejorarlo":
#
#   1. Es ABIERTA, no una escala de 1 a 5. Viene del bloque 4 de
#      `analisis/mejoras-por-hacer.md`. Un numero del 1 al 5 no dice que hay
#      que arreglar; una frase suya si.
#   2. Dice QUIEN LEE la respuesta. La version anterior decia "es para mi, no
#      para ti", y eso personaliza en el bot algo que en realidad va a una
#      bitacora que lee un equipo. La persona acaba de aceptar un aviso de
#      privacidad: ser literal aqui es coherente con ese aviso.
#   3. Va al final de TODO, despues del PDF. Preguntar antes de entregar lo que
#      la persona vino a buscar es pedirle algo antes de darle nada.
TEXTO_SATISFACCION = (
    "Antes de cerrar: ¿te quedó alguna duda sobre tu pensión, o algo que "
    "hubieras querido que hiciera distinto? Cualquier cosa que me escribas "
    "la lee el equipo que está construyendo Júbilo."
)

# --- Los comandos que el bot contesta solo, sin molestar a Claude -----------
#
# Por que existe esto: el 2026-09-16 una persona creyo que el bot estaba caido y
# probo /restart, /refresh, /clear y /start. Esos mensajes se los pasabamos a
# Claude, que corre sobre el CLI, y el CLI le respondio en ingles y a la cara:
# "/restart isn't available in this environment". Un mensaje de la infraestructura
# llego al chat de una persona. Atendiendo los comandos aqui, eso es imposible:
# el mensaje nunca llega a Claude. De paso ahorra la cuota de esas llamadas.

# El texto con el que se contesta cualquier comando que empiece por barra.
# Es uno solo y no cambia: quien esta perdido necesita una respuesta estable,
# no una redaccion distinta cada vez.
TEXTO_COMANDO = (
    "Aquí no hacen falta comandos, hablame normal y ya. "
    "Si te perdiste, escríbeme \"empecemos de nuevo\" y retomamos."
)

# El unico comando que sí tiene sentido en Telegram, porque es el que se dispara
# solo al abrir el chat por primera vez.
TEXTO_START_CONOCIDO = (
    "Ya nos conocemos, así que no te repito todo. Seguimos donde íbamos: "
    "si quieres, cuéntame en qué quedamos o mándame tu historia laboral."
)

# --- El filtro de salida: la segunda capa contra las fugas del CLI ----------
#
# Aunque los comandos ya no lleguen a Claude, el CLI puede colar una frase suya
# por otro camino (un permiso denegado, una herramienta que no existe). Todas
# esas frases tienen dos cosas en comun: estan en ingles y hablan del entorno.
# Si la respuesta coincide con alguna, no se manda: se manda un texto propio y
# el caso queda anotado para verlo en el reporte.
FUGAS_DEL_CLI = re.compile(
    r"isn't available|is not available|in this environment|requires approval"
    r"|permission denied|not allowed to use|no such tool|claude code"
    r"|--allowedTools|--permission-mode|anthropic",
    re.IGNORECASE,
)

TEXTO_FUGA = (
    "Se me cruzaron los cables con eso. Escríbeme otra vez lo último que "
    "me dijiste y seguimos."
)


def parece_fuga_del_cli(respuesta):
    """Dice si la respuesta es un mensaje de la infraestructura y no de Júbilo.

    Solo se activa con respuestas cortas. Un diagnostico largo puede mencionar
    una de esas palabras de casualidad, y tumbarlo seria mucho peor que dejar
    pasar una frase rara.
    """
    if not respuesta:
        return False
    return len(respuesta) < 400 and bool(FUGAS_DEL_CLI.search(respuesta))

def herramientas_de(carpeta):
    """Lo unico que Júbilo puede hacer mientras atiende a una persona.

    Son cuatro cosas y ninguna mas: leer archivos, escribir, correr los
    programas de la calculadora, y correr los de `tramites/`.

    **Sobre `tramites/`, que es la unica que toca internet.** El principio del
    proyecto sigue en pie: el modelo no navega. Lo que puede hacer es ejecutar
    un programa nuestro, escrito por nosotros, que hace una cosa fija (pedirle
    a Colpensiones que le mande la historia laboral al correo de la persona) y
    devuelve un resultado. No es un navegador ni una busqueda: es una
    herramienta determinista, igual que la calculadora. Ver
    `tramites/pedir_historia.py`, que empieza explicando sus limites.

    El permiso de escribir hace falta porque el flujo del documento guarda la
    extraccion en un JSON. Sin el, ese paso es imposible y Júbilo se queda
    dando vueltas hasta que dice que tuvo un problema tecnico. Fue justo lo
    que paso el 2026-09-16 con los primeros usuarios de prueba.

    **Por que el permiso va suelto y no atado a una carpeta:** se probo contra
    el servidor y la forma acotada `Write(/ruta/**)` no la concede el CLI, ni
    con una barra ni con dos. Solo la concede `Write` a secas. El encierro se
    consigue entonces por otros dos lados, que son igual de efectivos:
      1. `--add-dir` limita lo que existe para el: su carpeta y el repositorio.
      2. El repositorio esta en solo lectura a nivel de archivos, asi que la
         calculadora y el kit no se pueden modificar desde una conversacion,
         aunque a Júbilo lo convenzan de intentarlo. Ver AGENTS.md seccion 4.
    """
    return f"Read,Write,Bash(python3 {REPO}/calculadora/*),Bash(python3 {REPO}/tramites/*)"

# El log va a un archivo en el servidor. En el Mac esa carpeta no existe, y sin
# este try no se podria ni importar este archivo para probar sus funciones
# sueltas. Cuando no se puede escribir el archivo, se escribe solo en pantalla.
try:
    destinos_log = [logging.FileHandler(BASE / "bot.log"), logging.StreamHandler()]
except OSError:
    destinos_log = [logging.StreamHandler()]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=destinos_log,
)
log = logging.getLogger("jubilo")

# La libreria de Telegram anota cada llamada a internet, y el token del bot va
# dentro de esa direccion. Le pedimos que solo hable cuando haya un problema,
# para que la llave del bot no quede escrita en el archivo de log.
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

# El archivo de log solo lo puede leer el usuario jubilo. Mismo caso que arriba:
# si el archivo no existe (o sea, no estamos en el servidor), no hay nada que cerrar.
try:
    os.chmod(BASE / "bot.log", 0o600)
except OSError:
    pass

# Cuantas conversaciones se atienden al mismo tiempo. Antes era una sola y la
# gente hacia fila: con cinco personas escribiendo a la vez, la ultima esperaba
# cinco veces lo que tarda una respuesta. El servidor aguanta de sobra dos
# (cada proceso usa medio giga y hay tres y medio libres); el freno de verdad
# es la cuota de la cuenta de Claude, que es una sola y compartida.
# Si algun dia algo se pone raro, bajar este numero a 1 devuelve el bot al
# comportamiento anterior sin tocar nada mas.
SIMULTANEOS = 2
CUPOS = asyncio.Semaphore(SIMULTANEOS)

# Ademas, cada persona tiene su propio candado. Esto no es por cuota: es porque
# dos respuestas suyas a la vez retomarian la misma conversacion de Claude en
# paralelo y se pisarian entre si. Sus mensajes se atienden en orden, siempre.
CANDADOS_PERSONA = {}


def candado_de(chat_id):
    """Devuelve el candado de esta persona, y lo crea la primera vez.

    El diccionario va creciendo con cada persona nueva. Son unos pocos bytes
    cada uno, asi que a esta escala no vale la pena limpiarlo.
    """
    if chat_id not in CANDADOS_PERSONA:
        CANDADOS_PERSONA[chat_id] = asyncio.Lock()
    return CANDADOS_PERSONA[chat_id]


# --- Guardar que sesion de Claude corresponde a cada chat -------------------

def inicializar_db():
    """Crea las cinco tablas si es la primera vez que arranca el bot."""
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

    # La huella de cada archivo que ya se recibio, para reconocer un reenvio.
    # La huella es un numero que sale del contenido del archivo: el mismo
    # archivo da siempre la misma huella, y de la huella no se puede volver al
    # archivo. Guarda el chat de verdad, como `sesiones`, asi que esta tabla
    # tampoco sale del servidor (ver `analisis/traer_datos.sh`).
    con.execute("""
        CREATE TABLE IF NOT EXISTS archivos (
            chat_id TEXT NOT NULL,
            huella  TEXT NOT NULL,
            ts      TEXT NOT NULL,
            PRIMARY KEY (chat_id, huella)
        )
    """)

    # A quien ya se le mando el reporte de cierre y a quien ya se le hizo la
    # pregunta del final. Existe por una razon concreta: el reporte se manda
    # UNA sola vez por persona, y un simple apunte en memoria no sirve, porque
    # el bot se reinicia en cada despliegue y systemd lo revive si se muere. Si
    # la memoria fuera lo unico, al volver a arrancar el bot creeria que no le
    # ha mandado nada a nadie y le mandaria a todos un segundo reporte.
    #
    # **Va con el seudonimo y no con el chat de Telegram, a proposito.** Aqui no
    # hace falta saber quien es la persona, solo si ya se le mando lo suyo, y el
    # seudonimo alcanza para eso. De paso esta tabla no queda entre las que
    # `analisis/traer_datos.sh` tiene que borrar antes de sacar la copia del
    # servidor: no hay nada que identifique a nadie.
    con.execute("""
        CREATE TABLE IF NOT EXISTS cierres (
            seudonimo    TEXT PRIMARY KEY,
            ts_reporte   TEXT,   -- cuando se le mando el PDF (vacio = no se le ha mandado)
            ts_pregunta  TEXT,   -- cuando se le hizo la pregunta de satisfaccion
            ts_respuesta TEXT    -- cuando contesto esa pregunta
        )
    """)

    con.commit()
    con.close()

    # Las dos tablas de la bitacora (turnos y eventos) las crea su propio modulo.
    registro.inicializar(DB)

    # La base ahora guarda conversaciones, asi que solo la puede leer el usuario
    # del bot. Es la misma proteccion que ya tenia el archivo de log.
    os.chmod(DB, 0o600)


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


def huella_de(ruta):
    """Calcula la huella del archivo: un texto corto que sale de su contenido.

    Se lee por pedazos para no cargar en memoria un PDF entero.
    """
    resumen = hashlib.sha256()
    with open(ruta, "rb") as f:
        for pedazo in iter(lambda: f.read(65536), b""):
            resumen.update(pedazo)
    return resumen.hexdigest()


def archivo_repetido(chat_id, huella):
    """Dice si esta persona ya habia mandado exactamente este mismo archivo.

    Si no lo habia mandado, lo anota de una y devuelve False. Asi la pregunta y
    el registro son una sola operacion y no se pueden desincronizar.
    """
    con = sqlite3.connect(DB)
    ya_estaba = con.execute(
        "SELECT 1 FROM archivos WHERE chat_id = ? AND huella = ?",
        (str(chat_id), huella),
    ).fetchone() is not None
    if not ya_estaba:
        con.execute("INSERT INTO archivos VALUES (?, ?, ?)", (str(chat_id), huella, ahora()))
        con.commit()
    con.close()
    return ya_estaba


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


# --- La bitacora: como quedan anotados los turnos y los hitos ---------------

def quien(chat_id):
    """Convierte el chat de Telegram en el seudonimo con el que se anota todo.

    En la bitacora nunca queda el chat de verdad: ni en los turnos, ni en los
    eventos. La tabla `autorizaciones` es la unica que guarda el chat real,
    porque la ley obliga a poder decir quien autorizo que.
    """
    return registro.seudonimo(chat_id, SAL)


def anotar(chat_id, evento, detalle=None):
    """Deja constancia de un hito. Si falla, se aguanta callado.

    Va entero dentro de un try a proposito: la bitacora es para nosotros, no
    para el usuario. Que se caiga una anotacion nunca puede tumbar una respuesta.
    """
    try:
        registro.anotar_evento(DB, quien(chat_id), ahora(), evento, detalle)
    except Exception as e:
        log.error("no se pudo anotar el evento '%s': %s", evento, e)


# --- Quien ya recibio su reporte de cierre ----------------------------------
#
# Las cuatro funciones de abajo son la memoria del cierre. Todas leen y escriben
# en la tabla `cierres`, y todas usan el seudonimo: el chat de Telegram no entra
# nunca aqui. Como viven en la base y no en memoria, sobreviven a un reinicio,
# que es justo lo que hace falta para no mandar dos veces el mismo reporte.

def _fila_de_cierre(chat_id):
    """Devuelve la fila de `cierres` de esta persona, o None si no tiene."""
    con = sqlite3.connect(DB)
    fila = con.execute(
        "SELECT ts_reporte, ts_pregunta, ts_respuesta FROM cierres WHERE seudonimo = ?",
        (quien(chat_id),),
    ).fetchone()
    con.close()
    return fila


def ya_se_mando_el_reporte(chat_id):
    """Dice si a esta persona ya se le mando su reporte de cierre alguna vez."""
    fila = _fila_de_cierre(chat_id)
    return bool(fila and fila[0])


def marcar_reporte_enviado(chat_id):
    """Anota que el reporte ya salio. Desde aqui, a esta persona no se le manda otro."""
    con = sqlite3.connect(DB)
    # INSERT OR IGNORE primero y UPDATE despues: asi funciona igual si la fila
    # ya existia y si es la primera vez, sin tener que preguntar antes.
    con.execute("INSERT OR IGNORE INTO cierres (seudonimo) VALUES (?)", (quien(chat_id),))
    con.execute("UPDATE cierres SET ts_reporte = ? WHERE seudonimo = ?",
                (ahora(), quien(chat_id)))
    con.commit()
    con.close()


def marcar_pregunta_hecha(chat_id):
    """Anota que ya se le hizo la pregunta del final. Se hace una sola vez por persona."""
    con = sqlite3.connect(DB)
    con.execute("INSERT OR IGNORE INTO cierres (seudonimo) VALUES (?)", (quien(chat_id),))
    con.execute("UPDATE cierres SET ts_pregunta = ? WHERE seudonimo = ?",
                (ahora(), quien(chat_id)))
    con.commit()
    con.close()


def espera_respuesta_de_satisfaccion(chat_id):
    """Dice si a esta persona se le pregunto y todavia no ha contestado.

    Sirve para reconocer que el siguiente mensaje que escriba es la respuesta a
    esa pregunta, y poder anotarla. Despues de contestada, deja de ser cierto.
    """
    fila = _fila_de_cierre(chat_id)
    return bool(fila and fila[1] and not fila[2])


def marcar_respuesta_recibida(chat_id):
    """Anota que ya contesto la pregunta del final, para no volver a tomarle la palabra."""
    con = sqlite3.connect(DB)
    con.execute("UPDATE cierres SET ts_respuesta = ? WHERE seudonimo = ?",
                (ahora(), quien(chat_id)))
    con.commit()
    con.close()


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
    """Corre `claude -p` una vez.

    Devuelve tres cosas: la respuesta, el id de sesion y un diccionario con los
    numeros de esa llamada (cuanto tardo, cuanto costo, cuantos tokens). Esos
    numeros los regala el propio Claude en su respuesta y antes se botaban.
    """
    carpeta = carpeta_del_usuario(chat_id)

    # La variable clave del aislamiento: cada usuario, su propio directorio de estado.
    entorno = os.environ.copy()
    entorno["CLAUDE_CONFIG_DIR"] = str(carpeta / ".claude")

    comando = [
        CLAUDE, "-p", texto,
        "--output-format", "json",
        "--add-dir", str(carpeta),   # puede ver su propia carpeta
        "--add-dir", str(REPO),      # y el kit y la calculadora
        "--allowedTools", herramientas_de(carpeta),
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
        return None, None, {"resultado": "error"}

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
            return None, None, {"resultado": "sesion_vencida"}

        return None, None, {"resultado": "error"}

    # Los numeros de esta llamada. Vienen dentro del JSON que acaba de devolver
    # Claude: cuanto tardo en total, cuanto costo en dolares, cuantas vueltas
    # dio por dentro y cuantos tokens gasto.
    #
    # Los de entrada se guardan ademas separados en tres, porque no cuestan lo
    # mismo: los frescos se pagan completos, los que se leen de cache valen una
    # decima parte, y crear la cache cuesta un poco mas que un token fresco. Con
    # el total solo, no se sabe si el gasto esta en el kit que se relee o en la
    # conversacion en si, y se optimizaria a ciegas.
    uso = datos.get("usage") or {}
    frescos = uso.get("input_tokens") or 0
    de_cache = uso.get("cache_read_input_tokens") or 0
    cache_creado = uso.get("cache_creation_input_tokens") or 0
    metricas = {
        "resultado": "ok",
        "latencia_ms": datos.get("duration_ms"),
        "costo_usd": datos.get("total_cost_usd"),
        "turnos_internos": datos.get("num_turns"),
        "tokens_entrada": frescos + de_cache + cache_creado,
        "tokens_frescos": frescos,
        "tokens_cache": de_cache,
        "tokens_cache_creado": cache_creado,
        "tokens_salida": uso.get("output_tokens"),
    }

    return datos.get("result"), datos.get("session_id"), metricas


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
        anotar(chat_id, "aviso_mostrado", VERSION_AVISO)
        await mensaje.reply_text(ARCHIVO_BIENVENIDA.read_text(encoding="utf-8"))

        # Si de una mando su historia laboral sin haber visto el aviso, no se
        # procesa: se le pide que la reenvie, ya sabiendo a que dice que si.
        if mensaje.document or mensaje.photo:
            await mensaje.reply_text(
                "Vi que ya me mandaste un archivo, pero no lo abri todavia: "
                "queria que primero leyeras lo de arriba. Reenviamelo y sigo."
            )
        return

    # --- El temporizador del cierre ------------------------------------------
    # Cada mensaje que llega reinicia la cuenta atras del reporte. Va aqui
    # arriba, y no al final, para que cuente TODO lo que la persona escriba:
    # tambien un comando, tambien una nota de voz, tambien un archivo repetido.
    # Cualquiera de esas cosas significa que la conversacion sigue viva, y
    # mandarle su reporte de cierre en mitad de la charla seria absurdo.
    #
    # El nombre sale del perfil de Telegram de la propia persona y viaja solo en
    # la memoria del temporizador, para que su reporte salga con su nombre. No
    # se guarda en la base ni entra en la bitacora.
    nombre_de_perfil = getattr(update.effective_user, "full_name", None)
    programar_cierre(getattr(context, "job_queue", None), chat_id, nombre_de_perfil)

    # --- La respuesta a la pregunta del final --------------------------------
    # Si ya se le mando el reporte y se le pregunto si le sirvio, lo primero que
    # escriba despues es esa respuesta, y es lo unico que se tiene para saber si
    # esto le sirve a alguien. Queda anotada como un hito mas y el mensaje sigue
    # su camino normal hacia Claude, que le contesta como a cualquier otro.
    # El texto pasa por el filtro de datos personales dentro de `anotar_evento`.
    if espera_respuesta_de_satisfaccion(chat_id):
        dicho = (mensaje.text or mensaje.caption or "").strip()
        if dicho:
            anotar(chat_id, "respuesta_satisfaccion", dicho[:500])
            marcar_respuesta_recibida(chat_id)

    # --- Los comandos los contesta el bot, nunca Claude ----------------------
    # Va justo despues del candado del aviso, para que un /start de alguien que
    # nunca ha escrito siga mostrando la bienvenida completa. De aqui en
    # adelante, quien manda un comando ya la vio.
    crudo = (mensaje.text or "").strip()
    if crudo.startswith("/"):
        comando = crudo.split()[0].split("@")[0].lower()
        anotar(chat_id, "comando", comando)
        # A quien ya conocemos, el /start no le repite el aviso de privacidad
        # entero: lo unico que consigue es hacerle creer que se borro todo.
        await mensaje.reply_text(TEXTO_START_CONOCIDO if comando == "/start" else TEXTO_COMANDO)
        return

    # --- Lo que todavia no se sabe atender -----------------------------------
    # Notas de voz, audios y videos. Antes se ignoraban en silencio y la persona
    # se quedaba esperando una respuesta que nunca llegaba. Ahora se le dice.
    medio = None
    if mensaje.voice:
        medio = "nota de voz"
    elif mensaje.audio:
        medio = "audio"
    elif mensaje.video or mensaje.video_note:
        medio = "video"

    if medio:
        anotar(chat_id, "medio_no_soportado", medio)
        await mensaje.reply_text(
            f"Por ahora no puedo escuchar {medio}s. Escribeme el mensaje y seguimos."
        )
        return

    # --- Peticiones sobre sus propios datos ----------------------------------
    # Se registran antes de responder, porque los plazos legales corren desde
    # que la persona lo pide, no desde que se le contesta. Despues el mensaje
    # sigue su camino normal y Claude responde con lo que dice el system prompt.
    tipo = detectar_solicitud(mensaje.text or mensaje.caption or "")
    if tipo:
        registrar_solicitud(chat_id, tipo)
        anotar(chat_id, "solicitud_datos", tipo)

    # --- El archivo que manda la persona -------------------------------------
    tuvo_adjunto = bool(mensaje.document or mensaje.photo)
    if tuvo_adjunto:
        carpeta = carpeta_del_usuario(chat_id)
        archivo_tg = mensaje.document or mensaje.photo[-1]
        nombre = getattr(archivo_tg, "file_name", None) or f"{archivo_tg.file_unique_id}.jpg"
        destino = carpeta / nombre
        descargable = await context.bot.get_file(archivo_tg.file_id)
        await descargable.download_to_drive(str(destino))

        # Si es exactamente el mismo archivo que ya mando antes, se le contesta
        # aqui y no se llama a Claude. La gente reenvia porque no esta segura de
        # que llego, y esa noche una sola persona reenvio ocho veces: siete
        # llamadas al modelo para decir siete veces lo mismo con otras palabras.
        #
        # Va ANTES de anotar el documento: si no, cada reenvio contaria como un
        # documento recibido mas y el embudo del reporte diria que llegaron mas
        # documentos de los que llegaron.
        if archivo_repetido(chat_id, huella_de(destino)):
            anotar(chat_id, "archivo_repetido")
            await mensaje.reply_text(
                "Ese archivo ya lo tengo, no hace falta que lo reenvíes. "
                "Estoy trabajando con él."
            )
            return

        # Llego su historia laboral y ya habia visto el aviso: este envio es
        # la autorizacion, y queda con fecha y hora.
        registrar_documento(chat_id)
        anotar(chat_id, "documento_recibido")

        texto = (mensaje.caption or "") + f"\n\n[El usuario adjuntó un archivo: {destino}]"
    else:
        texto = mensaje.text or ""

    if not texto.strip():
        return

    # Acuse inmediato: la regla de producto prohibe el silencio mientras se procesa.
    # Si en este momento no hay cupo libre, se le dice, en vez de dejarlo
    # pensando que el bot se colgo. La gente aguanta la espera si sabe que la hay.
    #
    # El acuse largo, con tiempo estimado, solo va cuando viene un archivo: ese
    # es el caso lento de verdad (el peor medido fue de 320 segundos). Para un
    # mensaje de texto, que tarda 9 segundos tipicos, anunciarle "dos o tres
    # minutos" seria peor que no decir nada.
    if CUPOS.locked():
        await mensaje.reply_text(
            "Recibido. Estoy atendiendo a alguien más en este momento, "
            "así que me voy a demorar un poco más de lo normal. No te vayas."
        )
    elif tuvo_adjunto:
        await mensaje.reply_text(
            "Recibí tu documento. Leerlo y hacer las cuentas me toma dos o tres "
            "minutos, a veces un poco más. No te vayas y no lo reenvíes, ya lo tengo."
        )
    else:
        await mensaje.reply_text("Recibido. Dame un momento.")
    await context.bot.send_chat_action(chat_id, "typing")

    # Desde aqui se cronometra. Interesan dos tiempos distintos: lo que la
    # persona espera haciendo fila y lo que se demora Claude una vez le toca.
    # Si el primero empieza a crecer, es que hay que subir los cupos.
    llego = time.monotonic()
    metricas = {}

    # Dos filas, en este orden: primero la suya (que sus propios mensajes no se
    # atropellen) y despues la de todos (que no haya mas de SIMULTANEOS a la vez).
    async with candado_de(chat_id):
        async with CUPOS:
            espera_cola_ms = int((time.monotonic() - llego) * 1000)

            # Mientras espero, Telegram deja de mostrar "escribiendo...". Se
            # vuelve a poner justo antes de arrancar, ya con el cupo en la mano.
            await context.bot.send_chat_action(chat_id, "typing")

            try:
                respuesta, sesion, metricas = await asyncio.to_thread(preguntarle_a_claude, chat_id, texto)
            except subprocess.TimeoutExpired:
                anotar_turno_del_mensaje(chat_id, texto, None, tuvo_adjunto, espera_cola_ms,
                                         {"resultado": "timeout"})
                await mensaje.reply_text("Esto se está demorando más de lo normal. Escríbeme otra vez en unos minutos.")
                return

    # Pase lo que pase, el turno queda anotado: tambien los que fallaron. Un
    # reporte que solo muestra lo que salio bien no sirve para arreglar nada.
    anotar_turno_del_mensaje(chat_id, texto, respuesta, tuvo_adjunto, espera_cola_ms, metricas)

    if respuesta is None:
        await mensaje.reply_text(
            "Se me agotó la capacidad por ahora. Vuelve a escribirme en un rato "
            "y seguimos donde quedamos, no perdiste nada."
        )
        return

    if sesion:
        guardar_sesion(chat_id, sesion)

    # Ultima revision antes de mandar: si lo que salio es un mensaje del CLI y
    # no de Júbilo, no se manda. Queda anotado para verlo en el reporte, porque
    # cada una de estas es una grieta que hay que ir a tapar.
    if parece_fuga_del_cli(respuesta):
        log.error("fuga del CLI interceptada para %s: %s", chat_id, respuesta[:200])
        anotar(chat_id, "fuga_cli", respuesta[:200])
        await mensaje.reply_text(TEXTO_FUGA)
        return

    # Telegram corta en 4096 caracteres: partimos si hace falta.
    for i in range(0, len(respuesta), 4000):
        await mensaje.reply_text(respuesta[i:i + 4000])

    # La cuenta atras del cierre se reinicia otra vez, ahora que la persona ya
    # tiene la respuesta en la mano. Un documento puede tardar cinco minutos en
    # procesarse, y sin esto esos cinco minutos se le descontarian del rato que
    # tiene para seguir preguntando.
    programar_cierre(getattr(context, "job_queue", None), chat_id, nombre_de_perfil)


def anotar_turno_del_mensaje(chat_id, texto, respuesta, tuvo_adjunto, espera_cola_ms, metricas):
    """Deja el turno escrito en la bitacora, con sus numeros.

    Como `anotar`, va entero dentro de un try: si la anotacion falla, la persona
    igual recibe su respuesta y el problema queda en el log.
    """
    try:
        registro.anotar_turno(
            DB,
            seudonimo=quien(chat_id),
            ts=ahora(),
            texto_usuario=texto,
            respuesta=respuesta,
            tuvo_adjunto=1 if tuvo_adjunto else 0,
            resultado=metricas.get("resultado", "error"),
            espera_cola_ms=espera_cola_ms,
            latencia_ms=metricas.get("latencia_ms"),
            costo_usd=metricas.get("costo_usd"),
            tokens_entrada=metricas.get("tokens_entrada"),
            tokens_frescos=metricas.get("tokens_frescos"),
            tokens_cache=metricas.get("tokens_cache"),
            tokens_cache_creado=metricas.get("tokens_cache_creado"),
            tokens_salida=metricas.get("tokens_salida"),
            turnos_internos=metricas.get("turnos_internos"),
        )

        # Si la respuesta ya trae una cifra en pesos y habla de pension, es muy
        # probable que sea el diagnostico. Sirve para medir cuanta gente llega
        # hasta el final, sin tener que leer todas las conversaciones a mano.
        if registro.parece_diagnostico(respuesta):
            anotar(chat_id, "diagnostico_probable")
    except Exception as e:
        log.error("no se pudo anotar el turno de %s: %s", chat_id, e)


# --- El reporte de cierre: armarlo y mandarlo -------------------------------

def _extracciones_de(chat_id):
    """Los JSON que Júbilo dejo guardados de esta persona, del mas nuevo al mas viejo.

    Es la unica huella que queda de su historia laboral: el PDF original se
    borra apenas se extrae, y lo que se guarda es este JSON con los numeros y
    sin nombre ni cedula.
    """
    carpeta = USUARIOS / str(chat_id) / "extracciones"
    if not carpeta.is_dir():
        return []
    return sorted(carpeta.glob("*.json"), key=lambda r: r.stat().st_mtime, reverse=True)


def buscar_diagnostico(chat_id):
    """Rearma el diagnostico de esta persona. Devuelve (diagnostico, caso, fondo).

    Devuelve los tres en None cuando no hay nada que reportar, que es el caso de
    quien nunca mando su documento o cuyo documento no alcanzo para un
    diagnostico completo. En ese caso no se manda reporte: una pagina llena de
    "sin dato" es peor que el silencio.

    Busca en dos sitios, en este orden:
      1. Un JSON de diagnostico ya guardado, si existe. Es lo mas fiel, porque
         es exactamente lo que se le dijo a la persona en el chat.
      2. Si no lo hay, vuelve a correr `diagnosticar.py` sobre la extraccion.
         **Esto no es la IA calculando:** es el mismo programa de siempre, con
         el mismo archivo de entrada, asi que da el mismo resultado.

    OJO, limite conocido y anotado a proposito: `--sexo` y `--edad` se los pasa
    Júbilo a mano cuando el documento no los trae, y ese dato vive en la
    conversacion, no en la extraccion. Si el documento no traia ninguno de los
    dos, este recalculo sale incompleto y aqui se decide no mandar reporte.
    """
    archivos = _extracciones_de(chat_id)
    # Un archivo cuyo nombre diga "diagnostico" es la salida ya calculada;
    # cualquier otro es la extraccion de la historia laboral.
    ya_calculados = [r for r in archivos if "diagnostico" in r.name.lower()]
    casos = [r for r in archivos if r not in ya_calculados]
    if not casos:
        return None, None, None

    caso = json.loads(casos[0].read_text(encoding="utf-8"))

    diagnostico = None
    for ruta in ya_calculados:
        try:
            posible = json.loads(ruta.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if posible.get("listo_para_entregar"):
            diagnostico = posible
            break

    if diagnostico is None:
        # A correr la calculadora otra vez, con el mismo archivo de entrada.
        salida = subprocess.run(
            ["python3", str(REPO / "calculadora" / "diagnosticar.py"),
             str(casos[0]), "--json"],
            capture_output=True, text=True, timeout=120,
        )
        if salida.returncode != 0:
            log.error("no se pudo rehacer el diagnostico: %s", salida.stderr[:300])
            return None, None, None
        diagnostico = json.loads(salida.stdout)

    # El candado: sin diagnostico completo no hay reporte.
    if not diagnostico.get("listo_para_entregar"):
        return None, None, None

    fondo = (caso.get("documento") or {}).get("administradora_emisora")
    return diagnostico, caso, fondo


def construir_pdf_de_cierre(chat_id, nombre, destino):
    """Escribe el PDF del reporte en `destino`. Devuelve la ruta, o None si no hay nada.

    Todo el trabajo de verdad lo hace `reporte/armar_reporte.py`, que es una
    plantilla fija: aqui no se redacta ni se calcula nada. El modulo se importa
    aqui adentro y no arriba del archivo a proposito, porque en el Mac la
    carpeta del servidor no existe y si no, ni siquiera se podria importar
    `bot.py` para probarlo.
    """
    diagnostico, caso, fondo = buscar_diagnostico(chat_id)
    if diagnostico is None:
        return None

    carpeta_del_modulo = str(REPO / "reporte")
    if carpeta_del_modulo not in sys.path:
        sys.path.insert(0, carpeta_del_modulo)
    import armar_reporte

    armar_reporte.armar(diagnostico, nombre, fondo, str(destino), caso=caso)
    return destino


async def mandar_reporte_de_cierre(context):
    """Le manda a la persona su reporte, y despues la pregunta del final.

    La dispara el temporizador cuando la conversacion lleva
    MINUTOS_DE_SILENCIO_PARA_CERRAR sin un mensaje nuevo. El orden de los pasos
    no es casual:

      1. Si ya se le mando, no se hace nada. Ni siquiera se arma el PDF.
      2. Si no hay diagnostico, tampoco. Silencio, que es mejor que un
         "aqui esta tu reporte" vacio.
      3. Se manda el PDF, y solo cuando Telegram confirma, queda marcado como
         enviado. Si el envio falla, no queda marcado, y el proximo mensaje de
         la persona vuelve a armar el temporizador y se reintenta.
      4. La pregunta de satisfaccion va DESPUES del PDF, nunca antes. Preguntar
         "te sirvio" antes de entregar lo que sirve no tiene sentido.

    Va entera dentro de un try, como el resto de lo opcional del bot: que se
    caiga un reporte no puede tumbar el bot para todos los demas.
    """
    datos = getattr(context.job, "data", None) or {}
    chat_id = datos.get("chat_id")
    nombre = datos.get("nombre")
    destino = None

    try:
        # Paso 1: el candado de una sola vez por persona. Vive en la base, asi
        # que sigue en pie aunque el bot se haya reiniciado entre medias.
        if ya_se_mando_el_reporte(chat_id):
            return

        # Paso 2: armar el PDF. Escribir un PDF bloquea, asi que se hace en un
        # hilo aparte para no congelar al resto de las conversaciones.
        CARPETA_REPORTES.mkdir(parents=True, exist_ok=True)
        destino = CARPETA_REPORTES / f"cierre-{chat_id}.pdf"
        ruta = await asyncio.to_thread(construir_pdf_de_cierre, chat_id, nombre, destino)
        if ruta is None:
            log.info("no hay diagnostico para el reporte de cierre de %s", chat_id)
            return

        # Paso 3: mandarlo, y recien ahi marcarlo.
        with open(ruta, "rb") as archivo:
            await context.bot.send_document(
                chat_id=chat_id,
                document=archivo,
                filename="Jubilo - tu diagnostico pensional.pdf",
                caption=TEXTO_REPORTE,
            )
        marcar_reporte_enviado(chat_id)
        anotar(chat_id, "reporte_enviado")

        # Paso 4: la pregunta del final, despues del reporte y una sola vez.
        await context.bot.send_message(chat_id=chat_id, text=TEXTO_SATISFACCION)
        marcar_pregunta_hecha(chat_id)
        anotar(chat_id, "pregunta_satisfaccion")
    except Exception as e:
        log.error("no se pudo mandar el reporte de cierre a %s: %s", chat_id, e)
    finally:
        # El PDF lleva el nombre de la persona y toda su situacion pensional, asi
        # que no se queda en el disco del servidor ni un minuto de mas. Se borra
        # pase lo que pase, tambien cuando el envio fallo.
        if destino is not None:
            try:
                destino.unlink(missing_ok=True)
            except OSError as e:
                log.error("no se pudo borrar el reporte temporal %s: %s", destino, e)


def avisar_si_no_hay_temporizador(job_queue):
    """Grita en el log si el bot arranco sin JobQueue, en vez de callarse.

    POR QUE EXISTE. python-telegram-bot trae el JobQueue en un extra aparte
    (`pip install "python-telegram-bot[job-queue]"`). Si no esta instalado,
    `app.job_queue` es None, la libreria suelta un warning que se pierde entre
    el ruido del arranque, y TODO el cierre por inactividad deja de funcionar
    sin un solo error. El reporte no se manda, la pregunta de satisfaccion no
    se hace, y desde fuera el bot se ve perfectamente sano.

    Eso paso en el despliegue del 2026-09-19. Se detecto por casualidad, al
    leer el log. Con esto no vuelve a hacer falta la casualidad.

    Devuelve True si hay temporizador, False si no.
    """
    if job_queue is not None:
        return True
    log.error(
        "NO HAY JobQueue: el reporte de cierre y la pregunta de satisfaccion "
        "NO van a salir. Falta el extra en el servidor: "
        "pip install 'python-telegram-bot[job-queue]'. El resto del bot "
        "funciona normal.")
    return False


def programar_cierre(job_queue, chat_id, nombre=None, segundos=None):
    """Pone (o reinicia) el temporizador del cierre de esta conversacion.

    Se llama cada vez que la persona escribe. Como cada persona tiene un
    temporizador con su propio nombre, volver a llamarla borra el anterior y
    pone uno nuevo: o sea que la cuenta atras arranca de cero con cada mensaje,
    que es justo lo que se quiere. Mientras la conversacion siga viva, el
    reporte no sale.

    El nombre de la persona viaja aqui, en la memoria del temporizador, y no se
    guarda en ninguna parte: es para que su reporte salga con su nombre y nada
    mas. Si el bot se reinicia, el nombre se pierde y el reporte sale sin el.
    """
    if job_queue is None:            # en las pruebas no hay temporizador de verdad
        # OJO: en produccion esto NO deberia pasar nunca, y si pasa la funcion
        # entera queda muerta sin que nadie se entere. Ocurrio de verdad el
        # 2026-09-19: el servidor tenia python-telegram-bot sin el extra
        # `job-queue`, asi que `app.job_queue` era None, cada llamada se
        # devolvia en silencio y el log seguia diciendo "cierre pendiente
        # retomado" como si todo estuviera bien. Quien avisa ahora es
        # `avisar_si_no_hay_temporizador()`, que corre al arrancar.
        return
    try:
        # Si ya se le mando, no hay nada que programar.
        if ya_se_mando_el_reporte(chat_id):
            return

        etiqueta = f"cierre-{chat_id}"
        for anterior in job_queue.get_jobs_by_name(etiqueta):
            anterior.schedule_removal()

        job_queue.run_once(
            mandar_reporte_de_cierre,
            ESPERA_PARA_CERRAR if segundos is None else segundos,
            data={"chat_id": chat_id, "nombre": nombre},
            name=etiqueta,
        )
    except Exception as e:
        log.error("no se pudo programar el cierre de %s: %s", chat_id, e)


def conversaciones_para_retomar():
    """Quien se quedo esperando su reporte cuando el bot se reinicio.

    Los temporizadores viven en memoria, asi que un reinicio (y hay uno en cada
    despliegue) se los lleva por delante. Sin esto, quien estuviera callado en
    ese momento no recibiria nunca su reporte.

    Devuelve una lista de (chat_id, segundos_que_faltan). A quien ya se le paso
    la media hora estando el bot apagado, se le manda a los 30 segundos de
    arrancar, para no dispararle todo encima en el mismo instante del arranque.
    """
    pendientes = []
    try:
        con = sqlite3.connect(DB)
        chats = [fila[0] for fila in con.execute("SELECT chat_id FROM sesiones")]
        con.close()

        for chat_id in chats:
            if ya_se_mando_el_reporte(chat_id):
                continue

            # Cuando escribio por ultima vez. Sale de la bitacora, que se anota
            # con el seudonimo, asi que aqui se traduce el chat a seudonimo.
            con = sqlite3.connect(DB)
            fila = con.execute(
                "SELECT MAX(ts) FROM turnos WHERE seudonimo = ?", (quien(chat_id),)
            ).fetchone()
            con.close()
            if not fila or not fila[0]:
                continue

            ultimo = datetime.datetime.fromisoformat(fila[0])
            pasado = (datetime.datetime.now(datetime.timezone.utc) - ultimo).total_seconds()
            faltan = ESPERA_PARA_CERRAR - pasado
            pendientes.append((chat_id, max(30.0, faltan)))
    except Exception as e:
        log.error("no se pudieron retomar los cierres pendientes: %s", e)
    return pendientes


def main():
    global SAL

    USUARIOS.mkdir(parents=True, exist_ok=True)
    inicializar_db()

    # La carpeta de los reportes temporales, y una barrida de lo que haya
    # quedado dentro. Si el bot se murio justo mientras mandaba un reporte, ese
    # PDF con datos personales sigue ahi: se borra al arrancar, para que la
    # carpeta este siempre vacia salvo los segundos que dura un envio.
    CARPETA_REPORTES.mkdir(parents=True, exist_ok=True)
    for sobrante in CARPETA_REPORTES.glob("*.pdf"):
        sobrante.unlink(missing_ok=True)

    # El secreto del seudonimo. La primera vez se inventa solo y queda guardado;
    # de ahi en adelante siempre es el mismo, para que una misma persona conserve
    # su etiqueta entre reinicios.
    SAL = registro.obtener_sal(ARCHIVO_SAL)

    # La llave del bot sale del archivo de configuracion, con la misma funcion
    # que usa el aviso al dueno.
    token = leer_token()

    app = Application.builder().token(token).build()
    # Que tipos de mensaje atiende. Los audios y videos se aceptan aqui no porque
    # se sepan procesar, sino para poder contestarle a la persona que no se puede:
    # antes caian en un hueco y se quedaba esperando en silencio.
    medios = (filters.TEXT | filters.Document.ALL | filters.PHOTO
              | filters.VOICE | filters.AUDIO | filters.VIDEO | filters.VIDEO_NOTE)
    app.add_handler(MessageHandler(medios, al_recibir_mensaje))

    # Primero se comprueba que exista el temporizador. Si no existe, no se
    # anuncia en el log que se retoma nada: decir "cierre pendiente retomado"
    # cuando no se retomo nada es peor que no decir nada, porque deja el log
    # mintiendo y el problema tarda dias en salir.
    hay_temporizador = avisar_si_no_hay_temporizador(app.job_queue)

    # Los temporizadores de cierre viven en memoria y el reinicio se los llevo.
    # Aqui se vuelven a poner los de quien quedo callado y sin reporte, con el
    # tiempo que le faltaba. Sin nombre: ese solo existia en la memoria anterior.
    if hay_temporizador:
        for chat_id, faltan in conversaciones_para_retomar():
            programar_cierre(app.job_queue, chat_id, None, segundos=faltan)
            log.info("cierre pendiente retomado para %s, en %.0f s",
                     chat_id, faltan)

    log.info("Júbilo arrancó")
    app.run_polling()


if __name__ == "__main__":
    main()
