# Prueba del abridor de PDFs protegidos.
# Uso: python3 probar_abrir_pdf.py   (termina en 1 si algo falla)
#
# Se fabrican PDFs de mentira aquí mismo (uno con clave y uno sin ella), así que
# la prueba no necesita la historia laboral de nadie. Es a propósito: ningún
# documento de una persona real entra a este repositorio.

import json
import logging
import subprocess
import sys
import tempfile
from pathlib import Path

# pypdf se queja en pantalla cuando le pasan un archivo que no es un PDF. Aqui
# eso pasa a proposito (hay una prueba para ese caso), asi que se le pide que
# se calle para que la salida de la prueba no parezca un error.
logging.getLogger("pypdf").setLevel(logging.CRITICAL)

from pypdf import PdfWriter

import abrir_pdf

AQUI = Path(__file__).parent
fallas = []


def revisar(condicion, descripcion):
    """Anota el resultado de una comprobación y lo imprime."""
    print(f"  {'OK  ' if condicion else 'FALLA'}  {descripcion}")
    if not condicion:
        fallas.append(descripcion)


def pdf_de_mentira(ruta, clave=None):
    """Crea un PDF de dos páginas en blanco, con clave o sin ella."""
    escritor = PdfWriter()
    escritor.add_blank_page(width=200, height=200)
    escritor.add_blank_page(width=200, height=200)
    if clave:
        escritor.encrypt(clave)
    with open(ruta, "wb") as f:
        escritor.write(f)
    return ruta


with tempfile.TemporaryDirectory() as carpeta:
    carpeta = Path(carpeta)

    # -----------------------------------------------------------------------
    # Un PDF protegido con la cédula, que es como llega el de Colpensiones
    # -----------------------------------------------------------------------

    print("\nUn PDF protegido con clave")

    protegido = pdf_de_mentira(carpeta / "historiaLaboral.pdf", clave="1000708925")

    r = abrir_pdf.abrir(protegido, "1000708925")
    revisar(r["estado"] == "abierto", "con la clave correcta, el PDF se abre")
    revisar(Path(r.get("archivo", "")).exists(), "y queda un archivo nuevo, sin clave")
    revisar(r.get("paginas") == 2, "con todas sus páginas")

    # El archivo que sale ya no debe pedir clave: si la pidiera, no serviría de nada.
    from pypdf import PdfReader
    revisar(not PdfReader(r["archivo"]).is_encrypted,
            "el archivo que sale ya no tiene clave")

    # La persona escribe su cédula con puntos, como la lee en su documento.
    r = abrir_pdf.abrir(protegido, "1.000.708.925")
    revisar(r["estado"] == "abierto", "la cédula con puntos también abre el PDF")

    r = abrir_pdf.abrir(protegido, "1 000 708 925")
    revisar(r["estado"] == "abierto", "y con espacios también")

    # -----------------------------------------------------------------------
    # Otros fondos, otras claves. No siempre es la cédula.
    # -----------------------------------------------------------------------

    print("\nClaves que no son la cédula (otros fondos)")

    # Algunos fondos usan la fecha de nacimiento.
    por_fecha = pdf_de_mentira(carpeta / "porvenir.pdf", clave="15081968")
    r = abrir_pdf.abrir(por_fecha, "15081968")
    revisar(r["estado"] == "abierto", "una fecha de nacimiento como clave también abre")

    # Y otros mandan una clave alfanumérica aparte, en el correo.
    alfanumerica = pdf_de_mentira(carpeta / "proteccion.pdf", clave="HL2026XZ")
    r = abrir_pdf.abrir(alfanumerica, "HL2026XZ")
    revisar(r["estado"] == "abierto", "una clave con letras abre igual")

    # La persona la escribe en minúsculas, como suele pasar al copiarla a mano.
    r = abrir_pdf.abrir(alfanumerica, "hl2026xz")
    revisar(r["estado"] == "abierto", "y si la escribe en minúsculas, también")

    # Con espacios de más al copiar y pegar del correo.
    r = abrir_pdf.abrir(alfanumerica, "  HL2026XZ  ")
    revisar(r["estado"] == "abierto", "y con espacios pegados al copiar del correo")

    # -----------------------------------------------------------------------
    # Los casos en que no se puede abrir
    # -----------------------------------------------------------------------

    print("\nCuando no se puede abrir")

    r = abrir_pdf.abrir(protegido, "79482310")
    revisar(r["estado"] == "clave_incorrecta", "una cédula que no es, no abre nada")
    revisar("clave no abre" in r["mensaje"].lower(),
            "y el mensaje dice claramente qué pasó")

    r = abrir_pdf.abrir(carpeta / "no-existe.pdf", "123")
    revisar(r["estado"] == "no_existe", "un archivo que no está se reporta como tal")

    roto = carpeta / "roto.pdf"
    roto.write_text("esto no es un PDF")
    r = abrir_pdf.abrir(roto, "123")
    revisar(r["estado"] == "ilegible", "un archivo que no es PDF no revienta el programa")

    # -----------------------------------------------------------------------
    # Un PDF que nunca tuvo clave
    # -----------------------------------------------------------------------

    print("\nUn PDF sin clave")

    suelto = pdf_de_mentira(carpeta / "suelto.pdf")
    r = abrir_pdf.abrir(suelto, "1000708925")
    revisar(r["estado"] == "sin_clave", "un PDF sin clave se reconoce y se deja quieto")
    revisar(r["archivo"] == str(suelto), "y se devuelve el original, que ya se puede leer")

    # -----------------------------------------------------------------------
    # Llamado desde la línea de comandos, que es como lo va a usar el bot
    # -----------------------------------------------------------------------

    print("\nLlamado como lo hace el bot")

    salida = subprocess.run(
        [sys.executable, str(AQUI / "abrir_pdf.py"), str(protegido), "1000708925"],
        capture_output=True, text=True,
    )
    revisar(salida.returncode == 0, "termina en 0 cuando el PDF quedó legible")
    datos = json.loads(salida.stdout)
    revisar(datos["estado"] == "abierto", "y la salida es un JSON que se puede leer")

    salida = subprocess.run(
        [sys.executable, str(AQUI / "abrir_pdf.py"), str(protegido), "00000000"],
        capture_output=True, text=True,
    )
    revisar(salida.returncode == 1, "termina en 1 cuando la clave no sirve")


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
