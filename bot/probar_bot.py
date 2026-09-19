# Prueba de las piezas sueltas del bot que no necesitan ni servidor ni internet.
# Uso: python3 bot/probar_bot.py   (termina en 1 si algo falla)
#
# Aqui se prueban las tres defensas que se anadieron despues del primer feedback
# real (16 de septiembre de 2026):
#   1. El filtro que impide que un mensaje del CLI llegue al chat de una persona.
#   2. La huella de los archivos, que es lo que permite reconocer un reenvio.
#   3. Que un archivo reenviado se reconozca como repetido y no se procese otra vez.
#
# Y desde el 2026-09-19, el reporte de cierre y la pregunta del final: que salga
# una sola vez, que sobreviva a un reinicio, que un mensaje nuevo reinicie la
# cuenta atras, que sin diagnostico no pase nada, que el chat de Telegram no
# acabe en la bitacora, y que la pregunta vaya despues del reporte y no antes.
#
# Nada de eso toca internet ni el servidor: el temporizador y la API de Telegram
# son de mentiras y estan definidos mas abajo.

import asyncio
import datetime
import sqlite3
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import bot

fallas = []


def revisar(condicion, descripcion):
    """Anota el resultado de una comprobación y lo imprime."""
    print(f"  {'OK  ' if condicion else 'FALLA'}  {descripcion}")
    if not condicion:
        fallas.append(descripcion)


# ---------------------------------------------------------------------------
# El filtro de fugas del CLI
# ---------------------------------------------------------------------------

print("\nLo que nunca puede llegarle a una persona")

# Estas son frases del CLI. La primera es literal: le llegó a un usuario real.
fugas = [
    "/restart isn't available in this environment.",
    "This command is not available in this environment",
    "This action requires approval before continuing",
    "Permission denied: Write",
    "Error: no such tool 'WebSearch'",
    "I'm Claude Code, Anthropic's official CLI",
]
for texto in fugas:
    revisar(bot.parece_fuga_del_cli(texto), f"se intercepta: {texto[:45]}")


print("\nLo que sí tiene que pasar el filtro")

# Respuestas normales de Júbilo. Ninguna puede quedarse atrapada.
normales = [
    "Listo, ya tengo tu historia laboral. Dame dos minutos.",
    "¿En qué fondo estás afiliado: Colpensiones, Protección, Porvenir, Colfondos o Skandia?",
    "Con 1.150 semanas cotizadas te faltan 150 para cumplir el requisito.",
    "Tu mesada estimada está entre $1.380.000 y $1.620.000 al mes.",
]
for texto in normales:
    revisar(not bot.parece_fuga_del_cli(texto), f"pasa normal: {texto[:45]}")

revisar(not bot.parece_fuga_del_cli(None), "una respuesta vacía no rompe el filtro")
revisar(not bot.parece_fuga_del_cli(""), "una respuesta en blanco no rompe el filtro")

# Un diagnostico largo puede nombrar de casualidad una de esas palabras. Tumbarlo
# entero seria mucho peor que dejar pasar la palabra, asi que el filtro solo
# actua sobre respuestas cortas.
largo = ("Tu diagnóstico. " * 40) + "permission"
revisar(not bot.parece_fuga_del_cli(largo),
        "un diagnóstico largo no se tumba por una palabra suelta")


# ---------------------------------------------------------------------------
# La huella de los archivos
# ---------------------------------------------------------------------------

print("\nLa huella que reconoce un archivo reenviado")

with tempfile.TemporaryDirectory() as carpeta:
    c = Path(carpeta)
    (c / "historia.pdf").write_bytes(b"contenido del PDF de la historia laboral")
    (c / "copia.pdf").write_bytes(b"contenido del PDF de la historia laboral")
    (c / "otro.pdf").write_bytes(b"este es otro documento distinto")

    h1 = bot.huella_de(c / "historia.pdf")
    h2 = bot.huella_de(c / "copia.pdf")
    h3 = bot.huella_de(c / "otro.pdf")

    revisar(h1 == h2, "el mismo contenido da la misma huella, aunque cambie el nombre")
    revisar(h1 != h3, "dos documentos distintos dan huellas distintas")
    revisar(len(h1) == 64, "la huella tiene el largo esperado")

    # Y la memoria de archivos ya vistos, contra una base de verdad.
    bot.DB = c / "estado-de-prueba.db"
    bot.inicializar_db()

    revisar(not bot.archivo_repetido("111", h1), "la primera vez, el archivo no es repetido")
    revisar(bot.archivo_repetido("111", h1), "la segunda vez sí, y ahí se le corta el paso")
    revisar(bot.archivo_repetido("111", h1), "y sigue siendo repetido las veces que insista")
    revisar(not bot.archivo_repetido("111", h3), "otro documento suyo no cuenta como repetido")
    revisar(not bot.archivo_repetido("222", h1),
            "el mismo documento de otra persona es nuevo para ella")


# ---------------------------------------------------------------------------
# El reporte de cierre y la pregunta del final
# ---------------------------------------------------------------------------
#
# Las tres clases de abajo imitan lo justo de python-telegram-bot para poder
# probar sin servidor: el temporizador que dispara el reporte y la API que lo
# manda. Ninguna habla con internet.

class TrabajoFalso:
    """Un temporizador programado: guarda a quien hay que atender y cuando."""

    def __init__(self, funcion, cuando, data, name, cola):
        self.funcion = funcion      # que se va a ejecutar cuando suene
        self.cuando = cuando        # dentro de cuantos segundos
        self.data = data            # el chat y el nombre de la persona
        self.name = name            # la etiqueta, una por persona
        self.cola = cola

    def schedule_removal(self):
        """Cancela este temporizador. Es lo que pasa cuando la persona escribe otra vez."""
        if self in self.cola.trabajos:
            self.cola.trabajos.remove(self)


class ColaFalsa:
    """El JobQueue de mentiras: en vez de esperar, anota lo que se programo."""

    def __init__(self):
        self.trabajos = []

    def get_jobs_by_name(self, nombre):
        return [t for t in self.trabajos if t.name == nombre]

    def run_once(self, funcion, cuando, data=None, name=None):
        trabajo = TrabajoFalso(funcion, cuando, data, name, self)
        self.trabajos.append(trabajo)
        return trabajo


class BotFalso:
    """La API de Telegram de mentiras: apunta lo que se mandaria, en orden."""

    def __init__(self):
        self.enviado = []           # la lista en orden: documentos y mensajes mezclados

    async def send_document(self, chat_id, document, filename=None, caption=None):
        # Se lee el archivo aqui mismo para comprobar despues que existia de verdad
        # en el momento de mandarlo, y que se borro despues.
        self.enviado.append({"tipo": "documento", "chat_id": chat_id,
                             "bytes": document.read(), "caption": caption})

    async def send_message(self, chat_id, text):
        self.enviado.append({"tipo": "mensaje", "chat_id": chat_id, "text": text})


class ContextoFalso:
    """Lo que la libreria le pasa a la funcion del temporizador cuando suena."""

    def __init__(self, trabajo, bot_falso):
        self.job = trabajo
        self.bot = bot_falso


def disparar(trabajo, bot_falso):
    """Hace sonar un temporizador ya, sin esperar sus 30 minutos.

    Al terminar lo saca de la cola, que es lo que hace la libreria de verdad con
    un temporizador de una sola vez: suena y desaparece.
    """
    asyncio.run(trabajo.funcion(ContextoFalso(trabajo, bot_falso)))
    trabajo.schedule_removal()


print("\nEl reporte de cierre")

with tempfile.TemporaryDirectory() as carpeta:
    c = Path(carpeta)

    # El bot apuntando a una base y una carpeta de reportes de usar y tirar.
    bot.DB = c / "estado-cierre.db"
    bot.CARPETA_REPORTES = c / "reportes"
    bot.SAL = "sal-de-prueba"
    bot.inicializar_db()

    CHAT = "987654321"

    # En vez del generador de PDF de verdad (que necesita el repo en el
    # servidor, y cuyo formato esta cambiando en paralelo), uno de mentiras que
    # escribe un archivo cualquiera. Lo que se prueba aqui es el disparador y el
    # envio, no el contenido de la pagina: de eso se encarga
    # reporte/probar_armar_reporte.py.
    llamadas = {"veces": 0, "nombres": []}

    def pdf_de_mentiras(chat_id, nombre, destino):
        llamadas["veces"] += 1
        llamadas["nombres"].append(nombre)
        destino.write_bytes(b"%PDF-falso")
        return destino

    def sin_diagnostico(chat_id, nombre, destino):
        return None

    bot.construir_pdf_de_cierre = pdf_de_mentiras

    # --- Sin diagnostico, el disparador no hace nada -----------------------
    bot.construir_pdf_de_cierre = sin_diagnostico
    cola = ColaFalsa()
    telegram = BotFalso()
    bot.programar_cierre(cola, CHAT, "Juan Perez")
    disparar(cola.trabajos[0], telegram)

    revisar(telegram.enviado == [], "sin diagnóstico no se manda nada")
    revisar(not bot.ya_se_mando_el_reporte(CHAT),
            "y no queda marcado como enviado, así que se puede reintentar después")

    # --- Un mensaje nuevo reinicia la cuenta atras -------------------------
    cola = ColaFalsa()
    bot.programar_cierre(cola, CHAT, "Juan Perez")
    primero = cola.trabajos[0]
    bot.programar_cierre(cola, CHAT, "Juan Perez")     # la persona escribió otra vez

    revisar(len(cola.trabajos) == 1, "solo queda un temporizador por persona")
    revisar(cola.trabajos[0] is not primero,
            "el temporizador viejo se cancela y la cuenta atrás arranca de cero")
    revisar(cola.trabajos[0].cuando == bot.ESPERA_PARA_CERRAR,
            "el nuevo vuelve a contar los 30 minutos completos")

    # Dos personas distintas no se pisan el temporizador.
    bot.programar_cierre(cola, "111222333", "Ana Gomez")
    revisar(len(cola.trabajos) == 2, "cada persona tiene su propio temporizador")

    # --- Con diagnostico, el reporte sale y la pregunta va detras ----------
    bot.construir_pdf_de_cierre = pdf_de_mentiras
    cola = ColaFalsa()
    telegram = BotFalso()
    bot.programar_cierre(cola, CHAT, "Juan Perez")
    disparar(cola.get_jobs_by_name(f"cierre-{CHAT}")[0], telegram)

    tipos = [e["tipo"] for e in telegram.enviado]
    revisar(tipos == ["documento", "mensaje"],
            "sale el PDF y después la pregunta, en ese orden y no al revés")
    revisar(telegram.enviado[0]["bytes"] == b"%PDF-falso",
            "el PDF que se manda es el que se acabó de armar")
    revisar(telegram.enviado[1]["text"] == bot.TEXTO_SATISFACCION,
            "el segundo mensaje es la pregunta de satisfacción")
    revisar(llamadas["nombres"] == ["Juan Perez"],
            "el reporte se arma con el nombre de la persona")
    revisar(list(bot.CARPETA_REPORTES.glob("*.pdf")) == [],
            "el PDF con datos personales se borra del disco apenas se manda")
    revisar(bot.ya_se_mando_el_reporte(CHAT), "y queda marcado como enviado")

    # --- Una sola vez por persona ------------------------------------------
    antes = len(telegram.enviado)
    bot.programar_cierre(cola, CHAT, "Juan Perez")
    revisar(cola.get_jobs_by_name(f"cierre-{CHAT}") == [],
            "a quien ya recibió su reporte no se le vuelve a programar")

    # Y aunque el temporizador suene igual (por ejemplo, uno que quedo
    # programado de antes), tampoco manda un segundo reporte.
    disparar(TrabajoFalso(bot.mandar_reporte_de_cierre, 0,
                          {"chat_id": CHAT, "nombre": "Juan Perez"},
                          f"cierre-{CHAT}", cola), telegram)
    revisar(len(telegram.enviado) == antes,
            "un temporizador rezagado no manda un segundo reporte")

    # --- Sobrevive a un reinicio del proceso -------------------------------
    # Un reinicio se lleva por delante todo lo que estuviera en memoria. Aqui se
    # imita con objetos nuevos y sin ningun rastro de los anteriores: si la
    # memoria de "ya se mando" estuviera en una variable y no en la base, esta
    # comprobacion fallaria y la persona recibiria su reporte dos veces.
    cola_nueva = ColaFalsa()
    telegram_nuevo = BotFalso()
    bot.CANDADOS_PERSONA.clear()

    revisar(bot.ya_se_mando_el_reporte(CHAT),
            "después de un reinicio, el bot sigue sabiendo que ya le mandó el reporte")
    bot.programar_cierre(cola_nueva, CHAT, None)
    revisar(cola_nueva.trabajos == [],
            "y no le programa uno nuevo aunque siga callado")
    disparar(TrabajoFalso(bot.mandar_reporte_de_cierre, 0, {"chat_id": CHAT}, "x", cola_nueva),
             telegram_nuevo)
    revisar(telegram_nuevo.enviado == [], "ni le manda un segundo PDF")

    # --- La pregunta del final y su respuesta ------------------------------
    revisar(bot.espera_respuesta_de_satisfaccion(CHAT),
            "después de preguntar, el bot queda esperando la respuesta")
    bot.anotar(CHAT, "respuesta_satisfaccion", "Sí me sirvió, escríbeme a juan@correo.com")
    bot.marcar_respuesta_recibida(CHAT)
    revisar(not bot.espera_respuesta_de_satisfaccion(CHAT),
            "y una vez contestada, no se le vuelve a tomar la palabra")

    con = sqlite3.connect(bot.DB)
    eventos = con.execute("SELECT seudonimo, evento, detalle FROM eventos").fetchall()
    cierres = con.execute("SELECT * FROM cierres").fetchall()
    turnos = con.execute("SELECT * FROM turnos").fetchall()
    con.close()

    nombres_de_evento = [e[1] for e in eventos]
    revisar("reporte_enviado" in nombres_de_evento,
            "el envío del reporte queda como hito en la bitácora")
    revisar("pregunta_satisfaccion" in nombres_de_evento,
            "la pregunta del final también")

    respuesta = [e[2] for e in eventos if e[1] == "respuesta_satisfaccion"][0]
    revisar("[correo]" in respuesta and "juan@correo.com" not in respuesta,
            "la respuesta pasa por el filtro de datos personales")

    # --- El chat de Telegram no puede estar en ninguna parte de esto -------
    todo = str(eventos) + str(cierres) + str(turnos)
    revisar(CHAT not in todo,
            "el chat de Telegram no aparece ni en la bitácora ni en la tabla de cierres")
    revisar(all(e[0] == bot.quien(CHAT) for e in eventos if e[0]),
            "los hitos quedan anotados con el seudónimo, como el resto")
    revisar(all(f[0] == bot.quien(CHAT) for f in cierres),
            "la tabla de cierres se lleva por seudónimo, no por chat")

    # --- Retomar los temporizadores que se llevo el reinicio ---------------
    # Los temporizadores viven en memoria, asi que en cada despliegue se pierden.
    # Al arrancar, el bot mira quien quedo callado y sin reporte, y les vuelve a
    # poner el suyo con el tiempo que les faltaba.
    OTRO = "555666777"
    con = sqlite3.connect(bot.DB)
    # Dos personas con conversacion abierta: la que ya recibio su reporte y otra
    # que escribio hace diez minutos y todavia no.
    con.execute("INSERT INTO sesiones VALUES (?, ?)", (CHAT, "sesion-1"))
    con.execute("INSERT INTO sesiones VALUES (?, ?)", (OTRO, "sesion-2"))
    hace_diez_minutos = (datetime.datetime.now(datetime.timezone.utc)
                         - datetime.timedelta(minutes=10)).isoformat(timespec="seconds")
    con.execute("INSERT INTO turnos (seudonimo, ts, resultado) VALUES (?, ?, 'ok')",
                (bot.quien(OTRO), hace_diez_minutos))
    con.commit()
    con.close()

    pendientes = dict(bot.conversaciones_para_retomar())
    revisar(OTRO in pendientes,
            "tras un reinicio se le vuelve a poner el temporizador a quien quedó callado")
    revisar(CHAT not in pendientes,
            "pero no a quien ya recibió su reporte")
    # Escribio hace 10 minutos, asi que le faltan unos 20 de los 30.
    revisar(19 * 60 < pendientes[OTRO] < 21 * 60,
            "y se le respeta el tiempo que le faltaba, no se le reinicia entero")


# ---------------------------------------------------------------------------
# Resultado
# ---------------------------------------------------------------------------

print("\n" + "=" * 70)
if fallas:
    print(f"RESULTADO: {len(fallas)} FALLAS")
    for f in fallas:
        print(f"  - {f}")
    sys.exit(1)
print("RESULTADO: TODO EN VERDE")
print("=" * 70)
