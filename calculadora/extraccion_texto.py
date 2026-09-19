# Saca el texto de un PDF respetando las columnas.
#
# POR QUE EXISTE. Los parsers de historia laboral leen tablas, y una tabla solo
# se puede leer si las columnas siguen una al lado de la otra. La extraccion
# "normal" de texto revuelve las columnas y deja una sopa de palabras. Aqui se
# pide siempre el modo "layout", que conserva los espacios y deja cada columna
# donde estaba en la hoja.
#
# Hay dos maneras de hacerlo y se usan en este orden:
#   1. `pdftotext -layout` (programa del sistema, del paquete poppler). Es el
#      que se uso para armar las muestras, asi que es la referencia.
#   2. `pypdf` en modo layout, si el programa anterior no esta instalado. Asi
#      esto funciona igual en el Mac y en el servidor, sin depender de que
#      alguien instale poppler.
#
# Este archivo no sabe nada de fondos ni de pensiones: solo convierte PDF en
# texto. Quien interpreta ese texto es `detectar_formato.py`.

import shutil
import subprocess
from pathlib import Path

# Si el texto que sale del PDF es mas corto que esto, damos por hecho que el
# documento es una imagen escaneada y no tiene letras de verdad adentro. Ese
# caso existe: los PDF que se vuelven a guardar despues de quitarles la clave
# a veces pierden la capa de texto y quedan como una foto.
MINIMO_DE_LETRAS = 200


def _con_pdftotext(ruta):
    """Usa el programa del sistema. Devuelve el texto, o None si no se pudo."""
    # Si el programa no esta instalado, no hay nada que intentar.
    if not shutil.which("pdftotext"):
        return None
    try:
        # "-layout" es lo importante: mantiene las columnas alineadas.
        # "-" al final significa "escribeme el resultado en pantalla".
        salida = subprocess.run(
            ["pdftotext", "-layout", str(ruta), "-"],
            capture_output=True, timeout=60,
        )
        if salida.returncode != 0:
            return None
        return salida.stdout.decode("utf-8", errors="replace")
    except Exception:
        # Cualquier problema (timeout, permisos) no es fatal: queda el plan B.
        return None


def _con_pypdf(ruta):
    """Plan B, con la libreria que ya usa `abrir_pdf.py`."""
    try:
        from pypdf import PdfReader
        lector = PdfReader(str(ruta))
        paginas = [p.extract_text(extraction_mode="layout") or "" for p in lector.pages]
        return "\n".join(paginas)
    except Exception:
        return None


def texto_de(ruta):
    """Devuelve (texto, fuente). `texto` puede ser cadena vacia.

    `fuente` dice de donde salio el texto, para poder explicarlo despues:
    "pdftotext", "pypdf", "archivo_de_texto" o "ninguna".
    """
    ruta = Path(ruta)

    # Las muestras de laboratorio son .md o .txt ya extraidos: se leen tal cual.
    if ruta.suffix.lower() in (".txt", ".md"):
        return ruta.read_text(encoding="utf-8", errors="replace"), "archivo_de_texto"

    texto = _con_pdftotext(ruta)
    if texto and len(texto.strip()) >= MINIMO_DE_LETRAS:
        return texto, "pdftotext"

    texto_b = _con_pypdf(ruta)
    if texto_b and len(texto_b.strip()) >= MINIMO_DE_LETRAS:
        return texto_b, "pypdf"

    # Ninguna de las dos saco letras suficientes: es un PDF de imagen.
    return (texto or texto_b or ""), "ninguna"


def tiene_capa_de_texto(texto):
    """True si el documento trae letras de verdad y no es una foto."""
    return len(texto.strip()) >= MINIMO_DE_LETRAS
