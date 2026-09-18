# Prueba de las piezas sueltas del bot que no necesitan ni servidor ni internet.
# Uso: python3 bot/probar_bot.py   (termina en 1 si algo falla)
#
# Aqui se prueban las tres defensas que se anadieron despues del primer feedback
# real (16 de septiembre de 2026):
#   1. El filtro que impide que un mensaje del CLI llegue al chat de una persona.
#   2. La huella de los archivos, que es lo que permite reconocer un reenvio.
#   3. Que un archivo reenviado se reconozca como repetido y no se procese otra vez.

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
