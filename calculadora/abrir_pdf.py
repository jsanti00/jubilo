# Quita la clave de una historia laboral protegida.
#
# Uso:
#   python3 abrir_pdf.py /ruta/historiaLaboral.pdf 1234567890
#
# Colpensiones manda la historia laboral cifrada con la cedula del afiliado.
# Un PDF asi no se puede leer: hay que abrirlo primero con la clave. Este
# programa hace eso y nada mas. Deja al lado una copia sin clave, con el mismo
# nombre y "-abierto" al final, que ya se puede leer normalmente.
#
# Esta en `calculadora/` y no en otra carpeta por una razon practica: el bot
# solo tiene permiso de correr programas de esta carpeta, y ese permiso es una
# decision de seguridad que no se toca por conveniencia.
#
# Siempre imprime un JSON, para que quien lo llame no tenga que adivinar que paso.

import json
import sys
from pathlib import Path

from pypdf import PdfReader, PdfWriter


def variantes_de_clave(clave):
    """Las formas en que la misma clave se puede haber escrito.

    La gente escribe su cedula de muchas maneras: con puntos, con espacios, con
    guiones. La clave del PDF es una sola, asi que se prueban las variantes
    razonables en vez de devolver "clave incorrecta" por un punto de mas.
    """
    limpia = "".join(c for c in clave if c.isdigit())
    # Se usa un diccionario y no un conjunto para no perder el orden: primero
    # lo que la persona escribio, despues lo limpio.
    return list(dict.fromkeys([clave.strip(), limpia]))


def abrir(ruta, clave):
    """Intenta quitarle la clave al PDF. Devuelve el resumen de lo que paso."""
    origen = Path(ruta)

    if not origen.exists():
        return {"estado": "no_existe", "mensaje": f"No encuentro el archivo: {origen}"}

    try:
        lector = PdfReader(origen)
    except Exception as e:
        return {"estado": "ilegible",
                "mensaje": f"El archivo no parece un PDF valido: {e}"}

    # Si no tiene clave, no hay nada que hacer: se puede leer tal como llego.
    if not lector.is_encrypted:
        return {"estado": "sin_clave",
                "mensaje": "Este PDF no esta protegido, se puede leer directamente.",
                "archivo": str(origen)}

    # Se prueban las variantes de la clave, una por una, hasta que alguna abra.
    abierto = False
    for intento in variantes_de_clave(clave):
        try:
            if lector.decrypt(intento):
                abierto = True
                break
        except Exception:
            continue          # una variante que revienta no descarta a las demas

    if not abierto:
        return {"estado": "clave_incorrecta",
                "mensaje": "La clave no abre este PDF. Puede que no sea la cedula "
                           "del titular, o que el documento use otra clave."}

    # Ya abierto, se guarda una copia sin clave al lado del original.
    destino = origen.with_name(origen.stem + "-abierto.pdf")
    escritor = PdfWriter()
    for pagina in lector.pages:
        escritor.add_page(pagina)
    with open(destino, "wb") as f:
        escritor.write(f)

    return {"estado": "abierto",
            "mensaje": "El PDF quedo sin clave y ya se puede leer.",
            "archivo": str(destino),
            "paginas": len(lector.pages)}


def main():
    if len(sys.argv) < 3:
        print(json.dumps({"estado": "uso",
                          "mensaje": "Uso: python3 abrir_pdf.py <ruta.pdf> <clave>"},
                         ensure_ascii=False))
        sys.exit(1)

    resultado = abrir(sys.argv[1], sys.argv[2])
    print(json.dumps(resultado, ensure_ascii=False, indent=2))

    # Termina en 0 solo si el PDF quedo legible. Asi quien lo llame sabe si
    # puede seguir adelante sin tener que interpretar el texto.
    sys.exit(0 if resultado["estado"] in ("abierto", "sin_clave") else 1)


if __name__ == "__main__":
    main()
