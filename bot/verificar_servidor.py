# -*- coding: utf-8 -*-
"""Comprueba que el servidor tenga TODO lo que el bot necesita para correr.

POR QUE EXISTE ESTE ARCHIVO, y vale la pena contarlo entero porque el error
que lo origino no lo caza ninguna prueba normal.

El 2026-09-19 se desplego el cierre por inactividad: a los 30 minutos de
silencio, Jubilo manda el reporte y hace la pregunta de satisfaccion. En el Mac
todas las pruebas estaban en verde y el codigo era correcto. Pero el servidor
tenia `python-telegram-bot` instalado SIN su extra `job-queue`, asi que
`app.job_queue` valia None. La libreria suelta un warning que se pierde entre el
ruido del arranque, cada llamada a programar_cierre se devolvia en silencio, y
la funcion entera nacio muerta. Desde fuera el bot se veia perfectamente sano.

Se descubrio por casualidad, leyendo el log. Este script existe para que no
haga falta la casualidad.

QUE COMPRUEBA, y en este orden:

  1. Que se pueda entrar al servidor.
  2. Que exista el interprete del entorno virtual que usa el servicio. Ojo con
     esto: el `pip3` suelto del servidor instala en OTRO sitio, y mirar ahi fue
     lo que confundio el diagnostico el dia del error. El servicio corre con
     `/srv/jubilo/venv/bin/python` y esa es la unica opinion que cuenta.
  3. Que cada libreria de fuera que importan `bot.py` y `registro.py` se pueda
     importar CON ESE interprete. La lista no esta escrita a mano: se lee de
     los propios archivos, asi que manana, cuando alguien importe algo nuevo y
     se le olvide instalarlo en el servidor, esto lo caza solo.
  4. Que el JobQueue exista de verdad. Esta no es una comprobacion de import:
     `telegram.ext.JobQueue` se importa igual sin el extra. Hay que construir
     una Application y mirar si su `job_queue` es None, que es exactamente lo
     que fallo. No toca la red ni molesta al bot que esta corriendo: construir
     el objeto no arranca nada.
  5. Que el servicio exista y este activo.

Devuelve 0 si todo esta bien y 1 si algo falta, para que el script de
despliegue se pueda detener antes de subir nada.

Uso:
    python3 bot/verificar_servidor.py
"""

import ast
import subprocess
import sys
from pathlib import Path

# El servidor y el interprete estan fijos a proposito: este script sirve para
# este servidor y para ninguno mas.
SERVIDOR = "jubilo@128.140.125.112"
PYTHON_DEL_SERVICIO = "/srv/jubilo/venv/bin/python"
SERVICIO = "jubilo"

# Los archivos de los que se leen los imports. Son los dos que se despliegan.
ARCHIVOS = ["bot.py", "registro.py"]

# Lo que trae Python de fabrica no hace falta comprobarlo: si falta eso, el
# problema es otro. Desde Python 3.10 la lista viene en la propia libreria; en
# versiones anteriores (el Mac de Santiago trae una) se usa la lista de abajo,
# que cubre lo que estos dos archivos importan de verdad. Si algun dia se
# importa un modulo estandar que no este aqui, el script lo va a buscar en el
# servidor, lo va a encontrar igual, y no pasara nada: el respaldo puede
# quedarse corto sin romper nada, solo hace una comprobacion de mas.
if hasattr(sys, "stdlib_module_names"):
    DE_FABRICA = set(sys.stdlib_module_names)
else:
    DE_FABRICA = {
        "abc", "argparse", "ast", "asyncio", "base64", "collections",
        "contextlib", "csv", "datetime", "decimal", "difflib", "enum",
        "functools", "hashlib", "hmac", "html", "http", "importlib", "io",
        "itertools", "json", "logging", "math", "mimetypes", "os", "pathlib",
        "platform", "pprint", "random", "re", "secrets", "shutil", "signal",
        "sqlite3", "statistics", "string", "subprocess", "sys", "tempfile",
        "textwrap", "threading", "time", "traceback", "types", "typing",
        "unicodedata", "urllib", "uuid", "warnings", "zipfile", "zoneinfo",
    }

# Modulos propios del repo: viven al lado del bot, no se instalan con pip.
PROPIOS = {"registro", "diagnosticar", "armar_reporte", "palancas", "rpm",
           "rais", "router", "lagunas", "recuperacion", "comparador",
           "datos_sistema", "anomalias", "costo_y_retorno",
           "aportes_voluntarios", "abrir_pdf", "pdf_simple", "pedir_historia"}


def librerias_de_fuera(ruta):
    """Lee un archivo de Python y devuelve las librerias externas que importa.

    Se hace leyendo el arbol del codigo y no con una busqueda de texto, porque
    asi no se cuelan los imports que estan dentro de un comentario o de un
    texto. Solo interesa la primera parte del nombre: de `telegram.ext` basta
    con `telegram`, que es lo que se instala.
    """
    arbol = ast.parse(Path(ruta).read_text(encoding="utf-8"))
    encontradas = set()
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Import):
            for alias in nodo.names:
                encontradas.add(alias.name.split(".")[0])
        elif isinstance(nodo, ast.ImportFrom):
            # Un import relativo (nivel > 0) es de casa, no de fuera.
            if nodo.level == 0 and nodo.module:
                encontradas.add(nodo.module.split(".")[0])
    # Se quitan los de fabrica y los del propio repo: quedan las de pip.
    return {m for m in encontradas if m not in DE_FABRICA and m not in PROPIOS}


def en_el_servidor(comando, segundos=60):
    """Corre un comando en el servidor y devuelve (exito, salida)."""
    try:
        resultado = subprocess.run(
            ["ssh", "-o", "ConnectTimeout=15", "-o", "BatchMode=yes",
             SERVIDOR, comando],
            capture_output=True, text=True, timeout=segundos)
    except subprocess.TimeoutExpired:
        return False, "el servidor no respondio a tiempo"
    salida = (resultado.stdout + resultado.stderr).strip()
    return resultado.returncode == 0, salida


# Se van apuntando los problemas en vez de parar en el primero: es mas util
# ver de una vez todo lo que falta que arreglarlo de uno en uno.
problemas = []


def revisar(condicion, bien, mal):
    """Imprime el resultado de una comprobacion y apunta el fallo si lo hay."""
    if condicion:
        print("  OK    " + bien)
    else:
        print("  FALLA " + mal)
        problemas.append(mal)
    return condicion


print("=" * 70)
print("VERIFICANDO EL SERVIDOR ANTES DE DESPLEGAR")
print("=" * 70)

# --- 1. Se puede entrar ------------------------------------------------------
print("\n1. Acceso al servidor")
vivo, _ = en_el_servidor("echo ok")
if not revisar(vivo, "se puede entrar por ssh",
               "no se puede entrar al servidor por ssh"):
    # Sin acceso no tiene sentido seguir: todo lo demas iba a fallar igual.
    print("\n" + "=" * 70)
    print("RESULTADO: no se pudo verificar el servidor. NO despliegues a ciegas.")
    print("=" * 70)
    sys.exit(1)

# --- 2. El interprete correcto -----------------------------------------------
print("\n2. El interprete que usa el servicio")
hay_python, version = en_el_servidor(PYTHON_DEL_SERVICIO + " --version")
revisar(hay_python,
        "existe " + PYTHON_DEL_SERVICIO + " (" + version + ")",
        "no existe el interprete del entorno virtual: " + PYTHON_DEL_SERVICIO)

# --- 3. Las librerias que el bot importa -------------------------------------
print("\n3. Las librerias que importan bot.py y registro.py")
carpeta = Path(__file__).parent
necesarias = set()
for archivo in ARCHIVOS:
    ruta = carpeta / archivo
    if ruta.exists():
        necesarias |= librerias_de_fuera(ruta)

if not necesarias:
    print("  (ninguna libreria de fuera, nada que comprobar)")
for libreria in sorted(necesarias):
    ok, detalle = en_el_servidor(
        PYTHON_DEL_SERVICIO + " -c 'import " + libreria + "'")
    revisar(ok, "se importa " + libreria,
            "FALTA la libreria '" + libreria + "' en el entorno del servicio. "
            "Instalala con: " + PYTHON_DEL_SERVICIO + " -m pip install "
            + libreria)

# --- 4. El JobQueue, que es el que fallo -------------------------------------
print("\n4. El temporizador (JobQueue) del bot")
# Se construye una Application de mentiras, con un token falso, solo para
# preguntarle si tiene temporizador. No se conecta a Telegram ni arranca nada.
prueba = (
    'from telegram.ext import Application; '
    'app = Application.builder().token("1:x").build(); '
    'print("SI" if app.job_queue is not None else "NO")')
ok, salida = en_el_servidor(PYTHON_DEL_SERVICIO + " -c '" + prueba + "'")
tiene_cola = ok and salida.strip().endswith("SI")
revisar(tiene_cola,
        "el JobQueue existe: el reporte de cierre y la pregunta de "
        "satisfaccion van a salir",
        "NO HAY JobQueue. El cierre por inactividad no va a funcionar y no va "
        "a dar ningun error. Instala el extra: " + PYTHON_DEL_SERVICIO
        + " -m pip install 'python-telegram-bot[job-queue]'")

# --- 5. El servicio ----------------------------------------------------------
print("\n5. El servicio de systemd")
ok, estado = en_el_servidor(
    "export XDG_RUNTIME_DIR=/run/user/$(id -u); "
    "systemctl --user is-active " + SERVICIO)
revisar(estado.strip() == "active",
        "el servicio " + SERVICIO + " esta activo",
        "el servicio " + SERVICIO + " no esta activo (dice: "
        + estado.strip() + ")")

# --- Resultado ---------------------------------------------------------------
print("\n" + "=" * 70)
if problemas:
    print("RESULTADO: " + str(len(problemas)) + " cosa(s) que arreglar antes "
          "de desplegar")
    for problema in problemas:
        print("  - " + problema)
    print("=" * 70)
    sys.exit(1)
print("RESULTADO: el servidor tiene todo lo que el bot necesita")
print("=" * 70)
