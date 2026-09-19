"""Un escritor de PDF sencillo, sin librerias de terceros.

**Por que esto y no una libreria.** El servidor de Júbilo no tiene ninguna
libreria de PDF instalada (se comprobo el 2026-09-18: ni reportlab, ni fpdf, ni
PIL), y meter una dependencia nueva a produccion para dibujar una pagina de
texto no se paga. Un PDF es, por dentro, un archivo de texto con una estructura
fija, y lo que necesita el reporte de Júbilo es texto, lineas y rectangulos. Eso
cabe en este archivo.

**Que si hace y que no.** Hace texto en las fuentes que todo lector de PDF
trae de fabrica (Helvetica normal, negrita y cursiva), lineas y rectangulos de
relleno, en hojas tamano carta. No hace imagenes ni tablas automaticas.

**Si hace salto de pagina, desde el 2026-09-19.** El reporte sigue siendo de
una hoja por diseno y casi siempre cabe, pero antes, cuando no cabia, el texto
se escribia por debajo del borde y desaparecia sin dar ningun error. Quien
dibuja llama a `nueva_pagina()` cuando ve que lo que sigue ya no cabe, y el
documento sale con las hojas que haga falta en vez de perder el final.

**Las tildes.** Se usa la codificacion WinAnsi, que es la que traen las fuentes
de fabrica y cubre el espanol completo (tildes, enes, signos de apertura). Los
caracteres que no existen en esa tabla se reemplazan por su version sin tilde en
vez de romper el archivo.

Como se usa:

    pagina = Pagina()
    pagina.texto(50, 750, "Hola", tamano=18, negrita=True)
    pagina.linea(50, 740, 560, 740)
    pagina.guardar("/ruta/reporte.pdf")
"""

# Medidas de la pagina carta, en puntos (72 puntos = una pulgada).
# El origen (0, 0) del PDF esta abajo a la izquierda, no arriba.
ANCHO_CARTA = 612
ALTO_CARTA = 792

# Los nombres internos con los que el PDF llama a cada fuente.
FUENTES = {
    "normal": "Helvetica",
    "negrita": "Helvetica-Bold",
    "cursiva": "Helvetica-Oblique",
}

# Cuanto mide cada caracter en Helvetica, como milesimas del tamano de letra.
# Son los anchos reales de la fuente, no un promedio: hacen falta para alinear
# texto a la derecha sin que quede descuadrado. Los caracteres que no esten en
# la tabla usan el ancho de la "n", que es el mas comun.
ANCHOS_HELVETICA = {
    " ": 278, "!": 278, '"': 355, "#": 556, "$": 556, "%": 889, "&": 667,
    "'": 191, "(": 333, ")": 333, "*": 389, "+": 584, ",": 278, "-": 333,
    ".": 278, "/": 278, "0": 556, "1": 556, "2": 556, "3": 556, "4": 556,
    "5": 556, "6": 556, "7": 556, "8": 556, "9": 556, ":": 278, ";": 278,
    "<": 584, "=": 584, ">": 584, "?": 556, "@": 1015, "[": 278, "\\": 278,
    "]": 278, "^": 469, "_": 556, "`": 333, "{": 334, "|": 260, "}": 334,
    "~": 584, "¿": 611, "¡": 333,
    "a": 556, "b": 556, "c": 500, "d": 556, "e": 556, "f": 278, "g": 556,
    "h": 556, "i": 222, "j": 222, "k": 500, "l": 222, "m": 833, "n": 556,
    "o": 556, "p": 556, "q": 556, "r": 333, "s": 500, "t": 278, "u": 556,
    "v": 500, "w": 722, "x": 500, "y": 500, "z": 500,
    "A": 667, "B": 667, "C": 722, "D": 722, "E": 667, "F": 611, "G": 778,
    "H": 722, "I": 278, "J": 500, "K": 667, "L": 556, "M": 833, "N": 722,
    "O": 778, "P": 667, "Q": 778, "R": 722, "S": 667, "T": 611, "U": 722,
    "V": 667, "W": 944, "X": 667, "Y": 667, "Z": 611,
}
# Las vocales con tilde y la ene miden lo mismo que su letra sin tilde.
for _con, _sin in (("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"),
                   ("ü", "u"), ("ñ", "n"),
                   ("Á", "A"), ("É", "E"), ("Í", "I"), ("Ó", "O"), ("Ú", "U"),
                   ("Ñ", "N")):
    ANCHOS_HELVETICA[_con] = ANCHOS_HELVETICA[_sin]

ANCHO_POR_DEFECTO = 556

# La negrita es un poco mas ancha que la normal, de forma bastante pareja.
FACTOR_NEGRITA = 1.06


def _a_winansi(texto):
    """Pasa el texto a la codificacion que entienden las fuentes de fabrica.

    Lo que no se puede representar se cambia por su equivalente sin tilde, que
    es mucho mejor que un archivo roto o un caracter en blanco.
    """
    reemplazos = {
        "\u2014": ",",      # guion largo, que en este proyecto no se usa nunca
        "\u2013": "-",      # guion medio
        "\u2018": "'", "\u2019": "'",     # comillas simples tipograficas
        "\u201c": '"', "\u201d": '"',     # comillas dobles tipograficas
        "\u2026": "...",    # puntos suspensivos en un solo caracter
        "\u00a0": " ",      # espacio que no se parte
        "\u2022": "-",      # vineta
    }
    for malo, bueno in reemplazos.items():
        texto = texto.replace(malo, bueno)
    try:
        texto.encode("cp1252")
        return texto
    except UnicodeEncodeError:
        # Caracter por caracter: lo que no entra, se deja sin tilde.
        sin_tilde = {"á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u",
                     "Á": "A", "É": "E", "Í": "I", "Ó": "O", "Ú": "U",
                     "ñ": "n", "Ñ": "N", "ü": "u", "Ü": "U"}
        salida = []
        for caracter in texto:
            try:
                caracter.encode("cp1252")
                salida.append(caracter)
            except UnicodeEncodeError:
                salida.append(sin_tilde.get(caracter, "?"))
        return "".join(salida)


def _escapar(texto):
    """Tapa los tres caracteres que tienen significado propio dentro de un PDF."""
    return texto.replace("\\", r"\\").replace("(", r"\(").replace(")", r"\)")


def ancho_de(texto, tamano, negrita=False):
    """Cuanto mide una linea de texto, en puntos, sumando caracter por caracter."""
    milesimas = sum(ANCHOS_HELVETICA.get(c, ANCHO_POR_DEFECTO) for c in str(texto))
    ancho = milesimas / 1000.0 * tamano
    return ancho * FACTOR_NEGRITA if negrita else ancho


def partir(texto, tamano, ancho_maximo, negrita=False):
    """Parte un texto largo en varias lineas que quepan en el ancho dado."""
    palabras = texto.split()
    lineas, actual = [], ""
    for palabra in palabras:
        prueba = (actual + " " + palabra).strip()
        if ancho_de(prueba, tamano, negrita) <= ancho_maximo or not actual:
            actual = prueba
        else:
            lineas.append(actual)
            actual = palabra
    if actual:
        lineas.append(actual)
    return lineas


class Pagina:
    """Una o varias hojas en blanco a las que se les van poniendo cosas encima.

    Se sigue llamando `Pagina`, en singular, porque casi siempre es una sola:
    el reporte de Júbilo esta disenado para caber en una hoja. Pero cuando el
    contenido no cabe hay que poder seguir en otra, y para eso esta
    `nueva_pagina`. La alternativa era escribir por debajo del borde, que en
    un PDF no produce ningun error: el texto simplemente no se ve, y lo
    primero que se pierde es el final del documento, que en este reporte son
    las salvedades legales.
    """

    def __init__(self, ancho=ANCHO_CARTA, alto=ALTO_CARTA):
        self.ancho = ancho
        self.alto = alto
        # Una lista de dibujos, uno por hoja. Cada dibujo es la lista de
        # ordenes en el lenguaje interno del PDF. Siempre hay al menos una.
        self._hojas = [[]]

    @property
    def _ordenes(self):
        """Las ordenes de la hoja en la que se esta dibujando ahora mismo."""
        return self._hojas[-1]

    @property
    def paginas(self):
        """Cuantas hojas tiene el documento."""
        return len(self._hojas)

    def nueva_pagina(self):
        """Cierra la hoja actual y empieza a dibujar en una nueva."""
        self._hojas.append([])
        return self.paginas

    # --- Lo que se puede poner en la pagina --------------------------------

    def texto(self, x, y, contenido, tamano=10, negrita=False, cursiva=False,
              color=(0, 0, 0), hoja=None):
        """Escribe una linea de texto. (x, y) es la esquina inferior izquierda.

        `hoja` sirve para escribir en una hoja que ya se cerro, contando desde
        1. Hace falta para una sola cosa: la numeracion del pie ("1 de 3"), que
        no se puede escribir cuando se cierra la hoja porque en ese momento
        todavia no se sabe cuantas hojas van a ser en total.
        """
        if not contenido:
            return
        estilo = "negrita" if negrita else ("cursiva" if cursiva else "normal")
        limpio = _escapar(_a_winansi(str(contenido)))
        r, g, b = color
        orden = ("BT %.3f %.3f %.3f rg /%s %.2f Tf %.2f %.2f Td (%s) Tj ET"
                 % (r, g, b, estilo, tamano, x, y, limpio))
        destino = self._ordenes if hoja is None else self._hojas[hoja - 1]
        destino.append(orden)

    def linea(self, x1, y1, x2, y2, grosor=0.5, color=(0, 0, 0)):
        """Dibuja una linea recta entre dos puntos."""
        r, g, b = color
        self._ordenes.append(
            "%.3f %.3f %.3f RG %.2f w %.2f %.2f m %.2f %.2f l S"
            % (r, g, b, grosor, x1, y1, x2, y2))

    def rectangulo(self, x, y, ancho, alto, color=(0.95, 0.95, 0.95)):
        """Pinta un rectangulo relleno. Sirve para los fondos de seccion."""
        r, g, b = color
        self._ordenes.append(
            "%.3f %.3f %.3f rg %.2f %.2f %.2f %.2f re f"
            % (r, g, b, x, y, ancho, alto))

    # --- Guardar -----------------------------------------------------------

    def guardar(self, ruta):
        """Escribe el archivo PDF en disco."""
        with open(ruta, "wb") as archivo:
            archivo.write(self._bytes())
        return ruta

    def _bytes(self):
        """Arma el archivo PDF completo, byte por byte.

        Un PDF tiene cuatro partes: una cabecera, una lista de objetos
        numerados, una tabla que dice en que posicion del archivo empieza cada
        objeto, y un cierre. Se arma en ese orden.

        Los objetos van numerados desde 1 y se referencian entre si por ese
        numero (el "4 0 R" quiere decir "el objeto 4"). Como el documento
        puede tener varias hojas, los numeros no se pueden escribir a mano:
        se calculan. El reparto es este, con N hojas:

            1                el catalogo, la raiz
            2                la lista de hojas
            3 .. 2+N         una hoja cada uno
            3+N .. 2+2N      el dibujo de cada hoja
            3+2N .. 5+2N     las tres fuentes de fabrica
        """
        cuantas = self.paginas
        primera_hoja = 3
        primer_dibujo = primera_hoja + cuantas
        primera_fuente = primer_dibujo + cuantas

        objetos = []
        # 1: el catalogo, la raiz del documento.
        objetos.append(b"<< /Type /Catalog /Pages 2 0 R >>")
        # 2: la lista de hojas, con cuantas son y donde esta cada una.
        hijos = " ".join("%d 0 R" % (primera_hoja + i) for i in range(cuantas))
        objetos.append(("<< /Type /Pages /Kids [%s] /Count %d >>"
                        % (hijos, cuantas)).encode("ascii"))
        # Una hoja por cada dibujo, todas del mismo tamano y con las mismas
        # tres fuentes disponibles.
        for indice in range(cuantas):
            objetos.append(
                ("<< /Type /Page /Parent 2 0 R /MediaBox [0 0 %d %d] "
                 "/Resources << /Font << /normal %d 0 R /negrita %d 0 R "
                 "/cursiva %d 0 R >> >> /Contents %d 0 R >>"
                 % (self.ancho, self.alto, primera_fuente, primera_fuente + 1,
                    primera_fuente + 2, primer_dibujo + indice)).encode("ascii"))
        # Y el dibujo de cada hoja, en el mismo orden.
        for ordenes in self._hojas:
            dibujo = "\n".join(ordenes).encode("cp1252", "replace")
            objetos.append(b"<< /Length %d >>\nstream\n%s\nendstream"
                           % (len(dibujo) + 1, dibujo))
        # Las tres fuentes de fabrica, compartidas por todas las hojas.
        for estilo in ("normal", "negrita", "cursiva"):
            objetos.append(
                ("<< /Type /Font /Subtype /Type1 /BaseFont /%s "
                 "/Encoding /WinAnsiEncoding >>" % FUENTES[estilo]).encode("ascii"))

        salida = bytearray(b"%PDF-1.4\n")
        posiciones = []
        for numero, cuerpo in enumerate(objetos, start=1):
            posiciones.append(len(salida))
            salida += b"%d 0 obj\n" % numero + cuerpo + b"\nendobj\n"

        # La tabla que dice donde empieza cada objeto.
        inicio_tabla = len(salida)
        salida += b"xref\n0 %d\n" % (len(objetos) + 1)
        salida += b"0000000000 65535 f \n"
        for posicion in posiciones:
            salida += b"%010d 00000 n \n" % posicion

        salida += (b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n"
                   % (len(objetos) + 1, inicio_tabla))
        return bytes(salida)
