# Prueba del cuaderno de bitacora del bot.
# Uso: python3 bot/probar_registro.py   (termina en 1 si algo falla)
#
# Lo que mas importa aqui no es que la base guarde: es que NO guarde lo que el
# aviso de privacidad prometio no guardar. Por eso la mitad de las
# comprobaciones son "esta cedula no puede aparecer en el texto guardado".

import sqlite3
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import registro

fallas = []


def revisar(condicion, descripcion):
    """Anota el resultado de una comprobación y lo imprime."""
    print(f"  {'OK  ' if condicion else 'FALLA'}  {descripcion}")
    if not condicion:
        fallas.append(descripcion)


# ---------------------------------------------------------------------------
# El seudónimo
# ---------------------------------------------------------------------------

print("\nEl seudónimo")

sal = "sal-de-prueba-no-es-la-real"
a = registro.seudonimo(5226290061, sal)
b = registro.seudonimo(5226290061, sal)
c = registro.seudonimo(9999999999, sal)
d = registro.seudonimo(5226290061, "otra-sal")

revisar(a == b, "la misma persona siempre da el mismo seudónimo")
revisar(a != c, "dos personas distintas dan seudónimos distintos")
revisar(a != d, "con otra sal, el mismo chat da otro seudónimo")
revisar(str(5226290061) not in a, "el chat de Telegram no aparece dentro del seudónimo")
revisar(len(a) == 12, "el seudónimo es corto y legible en un reporte")


# ---------------------------------------------------------------------------
# Tachar datos personales
# ---------------------------------------------------------------------------

print("\nLo que se tacha")

casos_tachados = [
    ("mi cédula es 79.482.310 y quiero saber",        "79.482.310"),
    ("CC 1015426789",                                  "1015426789"),
    ("soy el 1015426789",                              "1015426789"),
    ("escríbeme a juan.perez@gmail.com",               "juan.perez@gmail.com"),
    ("mi celular es +57 300 123 4567",                 "300 123 4567"),
    ("mi número es 3001234567",                        "3001234567"),
    ("me llamo Juan Pérez Gómez y tengo 58 años",      "Juan Pérez"),
    ("Nombre: María Fernanda Ruiz",                    "María Fernanda"),
    ("documento No. 41.238.905",                       "41.238.905"),
    ("[El usuario adjuntó un archivo: /srv/jubilo/usuarios/5226290061/hl.pdf]", "5226290061"),
]

for entrada, prohibido in casos_tachados:
    salida = registro.redactar(entrada)
    revisar(prohibido not in salida, f"se tacha «{prohibido}» en: {entrada[:40]}")


# ---------------------------------------------------------------------------
# Lo que NO se puede tachar: los números que sirven para iterar
# ---------------------------------------------------------------------------

print("\nLo que se conserva (si esto se tacha, el reporte no sirve)")

casos_intactos = [
    ("gano $1.300.000 al mes",                  "1.300.000"),
    ("mi salario es 2.500.000 pesos",           "2.500.000"),
    ("llevo 1150 semanas cotizadas",            "1150"),
    ("nací en 1968",                            "1968"),
    ("tu mesada sería de $1.423.500",           "1.423.500"),
    ("te faltan 87 semanas",                    "87"),
    ("te pensionas en 2031",                    "2031"),
    ("un ahorro de 120.000.000 en el fondo",    "120.000.000"),
]

for entrada, esperado in casos_intactos:
    salida = registro.redactar(entrada)
    revisar(esperado in salida, f"se conserva «{esperado}» en: {entrada[:40]}")

revisar(registro.redactar("") == "", "un texto vacío no rompe nada")
revisar(registro.redactar(None) is None, "un texto que no existe no rompe nada")


# ---------------------------------------------------------------------------
# Escribir y leer la bitácora
# ---------------------------------------------------------------------------

print("\nLa base de datos")

with tempfile.TemporaryDirectory() as carpeta:
    db = Path(carpeta) / "prueba.db"
    registro.inicializar(db)
    registro.inicializar(db)      # dos veces seguidas no puede fallar

    registro.anotar_turno(
        db,
        seudonimo="abc123abc123",
        ts="2026-09-16T10:00:00-05:00",
        texto_usuario="hola, mi cédula es 79.482.310",
        respuesta="Tu mesada sería de $1.423.500",
        tuvo_adjunto=0,
        resultado="ok",
        espera_cola_ms=12,
        latencia_ms=8400,
        costo_usd=0.0431,
        tokens_entrada=12000,
        tokens_salida=800,
        turnos_internos=3,
    )
    registro.anotar_evento(db, "abc123abc123", "2026-09-16T10:00:01-05:00", "aviso_mostrado")
    registro.anotar_evento(db, "otra-persona", "2026-09-16T11:00:00-05:00", "aviso_mostrado")

    con = sqlite3.connect(db)
    fila = con.execute("SELECT texto_usuario, respuesta, costo_usd FROM turnos").fetchone()
    n_eventos = con.execute("SELECT COUNT(*) FROM eventos").fetchone()[0]
    con.close()

    revisar("79.482.310" not in fila[0],
            "la cédula NO llega a la base aunque se pase sin tachar")
    revisar("1.423.500" in fila[1], "la cifra de la mesada sí llega a la base")
    revisar(abs(fila[2] - 0.0431) < 1e-9, "el costo del mensaje queda guardado")
    revisar(n_eventos == 2, "los eventos de dos personas quedan separados")

    # Alguien pide que le borren lo suyo: se va todo lo de esa persona y nada más.
    borradas = registro.borrar_persona(db, "abc123abc123")
    con = sqlite3.connect(db)
    quedan_turnos = con.execute("SELECT COUNT(*) FROM turnos").fetchone()[0]
    quedan_eventos = con.execute("SELECT COUNT(*) FROM eventos").fetchone()[0]
    con.close()

    revisar(borradas == 2, "borrar a una persona borra su turno y su evento")
    revisar(quedan_turnos == 0, "no queda ningún turno suyo")
    revisar(quedan_eventos == 1, "y la otra persona sigue intacta")

    # La sal se inventa sola la primera vez y despues no cambia.
    ruta_sal = Path(carpeta) / "config" / "sal.txt"
    s1 = registro.obtener_sal(ruta_sal)
    s2 = registro.obtener_sal(ruta_sal)
    revisar(s1 == s2, "la sal se crea una vez y después se reutiliza")
    revisar(len(s1) == 64, "la sal es suficientemente larga para no adivinarse")


# ---------------------------------------------------------------------------
# La pista de si hubo diagnóstico
# ---------------------------------------------------------------------------

print("\n¿La respuesta parece un diagnóstico?")

revisar(registro.parece_diagnostico("Te pensionas en 2031 con una mesada de $1.423.500"),
        "una respuesta con mesada y cifra cuenta como diagnóstico")
revisar(not registro.parece_diagnostico("¿En qué año naciste?"),
        "una pregunta suelta no cuenta como diagnóstico")
revisar(not registro.parece_diagnostico("Recibido. Dame un momento."),
        "el acuse de recibo no cuenta como diagnóstico")
revisar(not registro.parece_diagnostico(None),
        "una respuesta vacía no cuenta como diagnóstico")


# ---------------------------------------------------------------------------
# Las columnas nuevas de tokens, y que una base vieja se actualice sola
# ---------------------------------------------------------------------------

print("\nEl desglose de tokens de entrada")

with tempfile.TemporaryDirectory() as carpeta:
    # Primero se simula una base "vieja": la tabla `turnos` sin las tres
    # columnas nuevas. Es lo que hay hoy en el servidor.
    vieja = Path(carpeta) / "vieja.db"
    con = sqlite3.connect(vieja)
    con.execute("""
        CREATE TABLE turnos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            seudonimo TEXT NOT NULL, ts TEXT NOT NULL,
            texto_usuario TEXT, respuesta TEXT, tuvo_adjunto INTEGER,
            resultado TEXT, espera_cola_ms INTEGER, latencia_ms INTEGER,
            costo_usd REAL, tokens_entrada INTEGER, tokens_salida INTEGER,
            turnos_internos INTEGER
        )
    """)
    con.commit(); con.close()

    # Al arrancar, el modulo tiene que anadirle las columnas que le faltan.
    registro.inicializar(vieja)
    con = sqlite3.connect(vieja)
    columnas = {f[1] for f in con.execute("PRAGMA table_info(turnos)")}
    con.close()
    revisar({"tokens_frescos", "tokens_cache", "tokens_cache_creado"} <= columnas,
            "una base que ya existia recibe las columnas nuevas sin perder nada")

    # Y una base nueva tiene que poder guardarlas.
    db = Path(carpeta) / "nueva.db"
    registro.inicializar(db)
    registro.anotar_turno(db, seudonimo="abc123", ts="2026-09-18T10:00:00-05:00",
                          texto_usuario="hola", respuesta="hola, cuentame",
                          tokens_entrada=61792, tokens_frescos=1792,
                          tokens_cache=58000, tokens_cache_creado=2000)
    con = sqlite3.connect(db)
    fila = con.execute("SELECT tokens_entrada, tokens_frescos, tokens_cache, "
                       "tokens_cache_creado FROM turnos").fetchone()
    con.close()
    revisar(fila == (61792, 1792, 58000, 2000),
            "el desglose de tokens queda guardado tal como entro")
    revisar(fila[0] == fila[1] + fila[2] + fila[3],
            "el total de entrada es la suma de las tres partes")


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
