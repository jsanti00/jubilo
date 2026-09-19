# Prueba del reporte de cierre.
# Uso: python3 reporte/probar_armar_reporte.py   (termina en 1 si algo falla)
#
# Lo que esta prueba existe para garantizar, y es una sola cosa: **que ninguna
# cifra del reporte sea distinta de la del diagnostico**. El reporte lo arma el
# codigo justamente para que el modelo no pueda reescribir un numero, y esa
# promesa hay que poder comprobarla. Por eso casi todas las comprobaciones de
# abajo son de la forma "esta cifra del reporte es identica a esta clave del
# JSON".
#
# Desde el 2026-09-18 la promesa se extiende a las secciones 4 y 5, que ahora
# son un renderizado de `calculadora/palancas.py`. Ahi lo que se comprueba es
# que el reporte no reordene, no recorte, no redacte y no invente: cada frase y
# cada cifra tiene que ser identica a la que devolvio palancas.calcular.
#
# No toca internet ni el servidor: corre con los casos del set dorado.

import json
import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).parent.parent
sys.path.insert(0, str(RAIZ / "calculadora"))
sys.path.insert(0, str(Path(__file__).parent))

from diagnosticar import diagnosticar
import palancas as motor_palancas
import armar_reporte as rep

CASOS = RAIZ / "casos"
FECHA = date(2026, 7, 18)
SALIDA = Path("/tmp/jubilo-reporte-prueba.pdf")

fallas = []


def revisar(condicion, descripcion):
    """Anota el resultado de una comprobación y lo imprime."""
    print(f"  {'OK  ' if condicion else 'FALLA'}  {descripcion}")
    if not condicion:
        fallas.append(descripcion)


def caso_de(archivo):
    """Lee un caso del set dorado tal como sale del disco."""
    return json.loads((CASOS / archivo).read_text(encoding="utf-8"))


def diagnostico_de(archivo, sexo=None):
    return diagnosticar(caso_de(archivo), sexo=sexo, fecha_calculo=FECHA)


# ---------------------------------------------------------------------------
# Las cifras del reporte son las del diagnóstico, sin excepción
# ---------------------------------------------------------------------------

print("\nCaso de ahorro individual: las cifras salen intactas del diagnóstico")

caso_01 = caso_de("caso-01-porvenir-rais.json")
d = diagnosticar(caso_01, fecha_calculo=FECHA)
datos = rep.datos_del_reporte(d, "Juan Pablo Granada", "Porvenir", caso=caso_01)

enc = datos["encabezado"]
revisar(enc["semanas_hoy"] == d["diagnostico"]["semanas_hoy"],
        "las semanas del encabezado son las del diagnóstico")
revisar(enc["edad"] == d["diagnostico"]["edad"], "la edad es la del diagnóstico")
revisar(enc["sexo"] == d["diagnostico"]["sexo"], "el sexo es el del diagnóstico")
revisar(enc["requisito_semanas"] == d["diagnostico"]["semanas_gpm"],
        "en RAIS el requisito que se muestra es el de la garantía de pensión mínima")
revisar(enc["semanas_que_faltan"]
        == d["diagnostico"]["semanas_gpm"] - d["diagnostico"]["semanas_hoy"],
        "las semanas que faltan son la resta exacta, sin redondeos propios")

res = datos["resultado"]
# LA CIFRA DE LA SECCIÓN 2 SALE DEL ESCENARIO APLICABLE DEL DIAGNÓSTICO, no de
# `recuperacion.base`. Es el error real que ya se cometió una vez: los dos
# números coincidían por casualidad y `recuperacion.base` no responde a los
# supuestos de palanca.
clave_aplicable = motor_palancas.escenario_aplicable(d["diagnostico"])
esperada = d["diagnostico"]["escenarios"][clave_aplicable]["mesada_banda"]
revisar(res["mesada_banda"] == esperada,
        "la mesada de la sección 2 es la banda del escenario aplicable del diagnóstico")
revisar(res["perfil_de_la_cifra"] == clave_aplicable,
        "y el reporte declara de qué escenario salió esa banda")

alertas = datos["alertas"]
resumen = d["lagunas"]["resumen"]
revisar(alertas["semanas_perdidas_total"] == resumen["semanas_perdidas_total"],
        "las semanas perdidas son las del módulo de lagunas")
revisar(str(resumen["vacios"]) in alertas["lista"][0]["cifra"],
        "el número de huecos es el del módulo de lagunas")

# El nombre sí va (decisión de Santiago), la cédula no va nunca.
revisar(enc["nombre"] == "Juan Pablo Granada",
        "el nombre completo va en el reporte, como decidió Santiago")
texto_entero = json.dumps(datos, ensure_ascii=False, default=str)
for prohibido in ("cedula", "cédula", "documento_identidad", "1005320949"):
    revisar(prohibido not in texto_entero.lower(),
            f"el reporte no contiene '{prohibido}'")


# ---------------------------------------------------------------------------
# Secciones 4 y 5: el reporte renderiza palancas.py y no lo reinterpreta
# ---------------------------------------------------------------------------

print("\nSección 4: las palancas son exactamente las que calculó palancas.py")

# Se corre el motor por separado y se compara contra lo que armó el reporte.
motor = motor_palancas.calcular(caso_01, "RAIS",
                                sexo=d["diagnostico"]["sexo"],
                                edad=d["diagnostico"]["edad"],
                                fecha_calculo=FECHA)
pal = datos["palancas"]

revisar(pal["mesada_base"] == motor["mesada_base"],
        "la mesada base es la de palancas.calcular, no la de recuperacion.base")
revisar(pal["mesada_base"] == res["mesada_banda"][1],
        "y coincide con el extremo alto de la banda de la sección 2")

revisar([p["clave"] for p in pal["lista"]]
        == [p["clave"] for p in motor["palancas"]],
        "el orden de las palancas es tal cual el que trae palancas.py")
revisar([p["frase"] for p in pal["lista"]]
        == [p["frase"] for p in motor["palancas"]],
        "las frases son las de palancas.py, el reporte no redacta ninguna")
revisar([p["efecto_mes"] for p in pal["lista"]]
        == [p["efecto_mesada_mes"] for p in motor["palancas"]],
        "los efectos en pesos son los de palancas.py, sin recalcular")
revisar(len(pal["lista"]) > 0, "este caso sí trae palancas que mostrar")

# Una palanca sin cifra se muestra sin cifra. Nunca con un cero, que se leería
# como "esta palanca no sirve" cuando lo que pasa es que no se pudo cuantificar.
sin_cifra = [p for p in pal["lista"] if p["efecto_mes"] is None]
revisar(bool(sin_cifra),
        "el caso trae al menos una palanca sin cuantificar, que es lo que se quiere probar")
revisar(all(p["efecto_mes_texto"] is None for p in sin_cifra),
        "la palanca sin cifra se muestra sin cifra, no con un $0")
revisar(all(p["frase"] for p in sin_cifra),
        "y aun así trae su frase, para que no salga muda")

# El límite de alcance no es opcional: si la palanca lo trae, el reporte lo lleva.
for original, mostrada in zip(motor["palancas"], pal["lista"]):
    if original.get("limite_de_alcance"):
        revisar(mostrada["limite_de_alcance"] == original["limite_de_alcance"],
                f"la palanca '{original['clave']}' muestra su límite de alcance")

# La administradora nunca aparece antes que el portafolio.
claves = [p["clave"] for p in pal["lista"]]
if "administradora" in claves and "portafolio" in claves:
    revisar(claves.index("administradora") == claves.index("portafolio") + 1,
            "la administradora va pegada justo debajo del portafolio")


print("\nLas cifras dicen de qué son: los tres textos que aclaran el significado")

# El dueño del producto preguntó, viendo el PDF: "esa plata por mes, ¿a qué se
# refiere?". palancas.py responde con tres textos y el reporte los copia tal
# cual: dos subtítulos de sección y una etiqueta por fila. El reporte no
# redacta ninguno, igual que no redacta las frases.
revisar(pal["que_significa_la_cifra"] == motor["que_significa_la_cifra"],
        "el subtítulo de la sección 4 es el que escribió palancas.py")
revisar(bool(pal["que_significa_la_cifra"]),
        "y este caso sí lo trae, que es lo que se quiere probar")
revisar(datos["escenarios"]["que_significan_los_escenarios"]
        == motor["que_significan_los_escenarios"],
        "el subtítulo de la sección 5 también es el de palancas.py")
revisar([p["etiqueta_efecto"] for p in pal["lista"]]
        == [p.get("etiqueta_efecto") if p.get("efecto_mesada_mes") is not None
            else None for p in motor["palancas"]],
        "cada fila lleva la etiqueta que le corresponde, sin reescribirla")

# La cifra ya no lleva pegado el " al mes" que el reporte le ponía a mano: ese
# texto decía cada cuánto pero no de qué, y era justo la confusión reportada.
revisar(all(not (p["efecto_mes_texto"] or "").endswith(" al mes")
            for p in pal["lista"]),
        "la cifra sale sola y el significado lo pone la etiqueta, no el reporte")

# LA REGLA QUE NO SE PUEDE ROMPER: sin cifra no hay etiqueta. La palanca de
# administradora no tiene cifra a propósito, y su casilla de la derecha tiene
# que seguir vacía, sin etiqueta y sin un $0.
for palanca_mostrada in pal["lista"]:
    if palanca_mostrada["efecto_mes"] is None:
        revisar(palanca_mostrada["etiqueta_efecto"] is None
                and palanca_mostrada["efecto_mes_texto"] is None,
                f"la palanca '{palanca_mostrada['clave']}' no tiene cifra, así "
                "que tampoco lleva etiqueta")


print("\nLa comparación de régimen va aparte, nunca mezclada entre las palancas")

revisar("regimen" not in claves,
        "el régimen no compite por puesto en la lista de palancas")
comp = pal["comparacion_de_regimen"]
revisar(comp is not None, "pero sí se muestra, en su propia sub-sección")
revisar(comp["frase"] == motor["comparacion_de_regimen"]["frase"],
        "con la frase que calculó palancas.py")
revisar(bool(comp["limite_de_alcance"]),
        "y siempre con su límite de alcance: Júbilo no recomienda trasladarse")
revisar("doble asesoría" in comp["limite_de_alcance"],
        "el límite nombra la doble asesoría obligatoria, que es requisito de ley")


print("\nSección 5: los escenarios, en su orden y sin amenazas")

esc = datos["escenarios"]
revisar([e["titulo"] for e in esc["lista"]]
        == [e["nombre"] for e in motor["escenarios"]],
        "los escenarios van en el orden en que los trae palancas.py")
revisar([e["mesada"] for e in esc["lista"]]
        == [e["mesada"] for e in motor["escenarios"]],
        "cada mesada de escenario es la que calculó palancas.py")
revisar(esc["lista"][0]["es_base"] is True,
        "el primer escenario es el base, o sea 'como vas hoy'")
revisar(esc["lista"][0]["mesada"] == motor["mesada_base"],
        "y su mesada es la mesada base, sin ningún supuesto encima")
texto_escenarios = json.dumps(esc, ensure_ascii=False).lower()
revisar("dejas de cotizar" not in texto_escenarios,
        "no se le ofrece a nadie el escenario de 'si dejas de cotizar hoy'")


print("\nEl reporte no usa el guion largo en ningún texto que genere")

# El guion largo está prohibido en todo el proyecto. Se revisa el diccionario
# entero, que es todo lo que puede terminar impreso en la página.
revisar("\u2014" not in texto_entero, "no aparece el guion largo en el reporte")


# ---------------------------------------------------------------------------
# El caso del piso de la garantía de pensión mínima
# ---------------------------------------------------------------------------

print("\nCaso 02: la persona a la que ninguna palanca le mueve la mesada")

caso_02 = caso_de("caso-02-skandia-rais.json")
d_02 = diagnosticar(caso_02, fecha_calculo=FECHA)
datos_02 = rep.datos_del_reporte(d_02, "Camilo Restrepo", "Skandia", caso=caso_02)
pal_02 = datos_02["palancas"]

revisar(pal_02["aviso"] is not None,
        "se dispara el aviso de la garantía de pensión mínima")
revisar(pal_02["aviso"]["tipo"] == "garantia_pension_minima",
        "y es el aviso de ese tipo, no otro")
revisar(pal_02["lista"] == [],
        "a esta persona no le queda ninguna palanca con cifra, y eso es correcto")
revisar(pal_02["sin_palancas"] is False,
        "pero la sección NO se declara vacía: el aviso es lo que hay que leer")
revisar(bool(pal_02["aviso"]["lo_que_de_verdad_importa"]),
        "el aviso dice qué es lo que sí está en juego para ella")
revisar("semanas" in pal_02["aviso"]["lo_que_de_verdad_importa"].lower()
        or "cotiza" in pal_02["aviso"]["lo_que_de_verdad_importa"].lower(),
        "y lo que está en juego son las semanas, no el tamaño de la mesada")
revisar(pal_02["mesada_base"] == datos_02["resultado"]["mesada_banda"][1]
        == datos_02["escenarios"]["lista"][0]["mesada"],
        "aun en este caso las secciones 2, 4 y 5 muestran la misma mesada de partida")


# ---------------------------------------------------------------------------
# Caso 05: dos palancas que son la misma acción no salen juntas
# ---------------------------------------------------------------------------

print("\nCaso 05: no se le ofrecen dos veces la misma acción")

caso_05 = caso_de("caso-05-colpensiones-rpm.json")
d_05 = diagnosticar(caso_05, sexo="M", fecha_calculo=FECHA)
datos_05 = rep.datos_del_reporte(d_05, "Jorge Eliécer Mora", "Colpensiones",
                                 caso=caso_05)
pal_05 = datos_05["palancas"]
claves_05 = [p["clave"] for p in pal_05["lista"]]

# "Cotizar todos los meses" (palanca 2) y "Lo que cotizas ahora pesa más"
# (palanca 12) le piden a la persona exactamente lo mismo. Mostrarlas juntas
# gasta dos de los cuatro puestos del reporte en un solo consejo.
revisar(not ("cerrar_lagunas" in claves_05
             and "densidad_ultimo_tramo" in claves_05),
        "no aparecen a la vez 'cotizar todos los meses' y 'lo que cotizas ahora "
        "pesa más'")
revisar(pal_05["mesada_base"] == datos_05["resultado"]["mesada_banda"][0]
        == datos_05["escenarios"]["lista"][0]["mesada"],
        "las secciones 2, 4 y 5 del caso 05 muestran la misma mesada de partida")


# ---------------------------------------------------------------------------
# Si palancas.calcular devuelve un error, el reporte no revienta
# ---------------------------------------------------------------------------

print("\nSi la calculadora de palancas devuelve error, el reporte aguanta")

# Es la forma exacta en que palancas.calcular avisa que le falta el sexo:
# trae "error" y la lista vacía. El reporte tiene que tratarlo como "no se
# pudieron cuantificar", no reventar y no dejar la sección en blanco.
error_de_palancas = {"error": "Falta el sexo: preguntar al usuario.",
                     "palancas": [], "palancas_todas": [], "descartadas": [],
                     "preguntas_pendientes": [], "escenarios": []}
datos_err = rep.datos_del_reporte(d, "Juan Pablo Granada", "Porvenir",
                                  caso=caso_01,
                                  resultado_palancas=error_de_palancas)
revisar(datos_err["palancas"]["sin_palancas"] is True,
        "un resultado con error se trata como 'no se pudieron cuantificar'")
revisar(bool(datos_err["palancas"]["texto_sin_palancas"]),
        "y la sección lleva un texto honesto, no queda en blanco")
revisar(datos_err["escenarios"]["lista"] == [],
        "y la sección de escenarios tampoco se inventa nada")
revisar(datos_err["palancas"]["motivo_tecnico"] == error_de_palancas["error"],
        "el motivo del error queda anotado para auditar")
rep.escribir_pdf(datos_err, Path("/tmp/jubilo-reporte-error.pdf"))
revisar(Path("/tmp/jubilo-reporte-error.pdf").read_bytes().startswith(b"%PDF-"),
        "y el PDF se genera igual")


# ---------------------------------------------------------------------------
# Sin el caso no se pueden calcular palancas, y se dice honestamente
# ---------------------------------------------------------------------------

print("\nSin el caso: la sección no queda en blanco ni se rellena con obviedades")

datos_sin = rep.datos_del_reporte(d, "Juan Pablo Granada", "Porvenir")
pal_sin = datos_sin["palancas"]
revisar(pal_sin["sin_palancas"] is True, "se reconoce que no hay palancas")
revisar(pal_sin["lista"] == [] and pal_sin["aviso"] is None,
        "y no se inventa ninguna")
revisar("no se pudieron cuantificar" in pal_sin["texto_sin_palancas"],
        "se dice honestamente que no se pudieron cuantificar")
revisar(bool(pal_sin.get("motivo_tecnico")),
        "y queda anotado el motivo técnico, para que el fallo no sea invisible")
revisar(pal_sin["motivo_tecnico"] not in json.dumps(
            {k: v for k, v in pal_sin.items() if k != "motivo_tecnico"},
            ensure_ascii=False),
        "pero el motivo técnico no se le muestra a la persona")
revisar(datos_sin["escenarios"]["lista"] == [],
        "y la sección de escenarios tampoco se rellena")
# El PDF tiene que salir igual: las otras cinco secciones son útiles solas.
rep.escribir_pdf(datos_sin, Path("/tmp/jubilo-reporte-sin-palancas.pdf"))
revisar(Path("/tmp/jubilo-reporte-sin-palancas.pdf").read_bytes().startswith(b"%PDF-"),
        "el PDF se genera igual, sin palancas")


print("\nCaso de prima media: lee sus propias claves, no las del otro régimen")

caso_04 = caso_de("caso-04-colpensiones-rpm.json")
d_rpm = diagnosticar(caso_04, sexo="F", fecha_calculo=FECHA)
datos_rpm = rep.datos_del_reporte(d_rpm, "María Fernanda Ruiz", "Colpensiones",
                                  caso=caso_04)
enc_rpm = datos_rpm["encabezado"]
dd = d_rpm["diagnostico"]

revisar(datos_rpm["modulo"] == "rpm", "se reconoce que es prima media")
revisar(enc_rpm["semanas_hoy"] == dd["semanas_hoy"],
        "las semanas son las del bloque de prima media")
revisar(enc_rpm["requisito_semanas"] == dd["requisito_semanas_hoy"],
        "en prima media el requisito es el de la ley, no el de la pensión mínima")
revisar(datos_rpm["resultado"]["fecha_pension"] == dd["fecha_pension_estimada"],
        "la fecha de pensión es la del diagnóstico")
revisar(datos_rpm["resultado"]["mesada_banda"][0]
        == dd["escenario_sigue_cotizando"]["mesada"],
        "la mesada es la del escenario de seguir cotizando")
revisar(datos_rpm["resultado"]["es_punto_no_banda"] is True,
        "en prima media se declara que es un punto y no una banda")

motor_rpm = motor_palancas.calcular(caso_04, "RPM", sexo="F",
                                    edad=dd["edad"], fecha_calculo=FECHA)
pal_rpm = datos_rpm["palancas"]
revisar(pal_rpm["mesada_base"] == dd["escenario_sigue_cotizando"]["mesada"],
        "en prima media la mesada base de las palancas es la del mismo escenario "
        "que muestra la sección 2")
revisar([p["frase"] for p in pal_rpm["lista"]]
        == [p["frase"] for p in motor_rpm["palancas"]],
        "las palancas de prima media también salen intactas de palancas.py")
revisar(pal_rpm["mesada_base"] == datos_rpm["resultado"]["mesada_banda"][0]
        == datos_rpm["escenarios"]["lista"][0]["mesada"],
        "las secciones 2, 4 y 5 de prima media muestran la misma mesada de partida")
texto_rpm = json.dumps(datos_rpm, ensure_ascii=False, default=str)
revisar("dejas de cotizar" not in texto_rpm.lower(),
        "tampoco a esta persona se le ofrece el escenario de dejar de cotizar")
revisar("\u2014" not in texto_rpm, "el reporte de prima media tampoco usa guion largo")


# ---------------------------------------------------------------------------
# El candado: sin diagnóstico completo, no hay reporte
# ---------------------------------------------------------------------------

print("\nEl candado, que es lo que evita entregar una página vacía")

# El mismo caso SIN el sexo no se puede calcular, así que no debe salir reporte.
d_incompleto = diagnostico_de("caso-04-colpensiones-rpm.json")
revisar(not d_incompleto["listo_para_entregar"],
        "el diagnóstico sin sexo efectivamente no está listo")
try:
    rep.datos_del_reporte(d_incompleto, "Alguien", "Colpensiones")
    revisar(False, "se negó a armar el reporte de un diagnóstico incompleto")
except ValueError as fallo:
    revisar("no está listo" in str(fallo),
            "se negó a armar el reporte de un diagnóstico incompleto")
    revisar("sexo" in str(fallo).lower(),
            "y dice qué es lo que falta, para poder pedírselo a la persona")


# ---------------------------------------------------------------------------
# Las siete secciones existen y traen contenido
# ---------------------------------------------------------------------------

print("\nLa estructura que validó Santiago")

for seccion in ("encabezado", "resultado", "alertas", "palancas",
                "escenarios", "siguientes_pasos", "supuestos"):
    revisar(seccion in datos and datos[seccion],
            f"la sección '{seccion}' existe y no viene vacía")

revisar(len(datos["escenarios"]["lista"]) >= 2,
        "la sección de escenarios trae el base y al menos uno más")
revisar(all("mesada" in e for e in datos["escenarios"]["lista"]),
        "cada escenario trae su mesada")
revisar(len(datos["siguientes_pasos"]) >= 1,
        "hay al menos un siguiente paso, y pueden ser varios")
revisar(any("no una liquidación certificada" in l
            for l in datos["supuestos"]["limites"]),
        "los límites dicen que esto no es una liquidación certificada")


# ---------------------------------------------------------------------------
# El PDF se genera, es válido, y las cifras están adentro
# ---------------------------------------------------------------------------

print("\nEl archivo PDF")

rep.escribir_pdf(datos, SALIDA)
crudo = SALIDA.read_bytes()
revisar(crudo.startswith(b"%PDF-"), "el archivo empieza como un PDF de verdad")
revisar(crudo.rstrip().endswith(b"%%EOF"), "y termina como un PDF de verdad")
revisar(("/Count %d" % datos["paginas"]).encode() in crudo,
        f"el PDF declara las {datos['paginas']} hojas que dice haber usado")
revisar(len(crudo) > 1500, "tiene contenido, no es un archivo vacío")

# La comprobación que de verdad importa: la mesada que salió al papel es la
# misma del diagnóstico. Se busca el texto dentro del PDF, que no va comprimido.
contenido = crudo.decode("cp1252", "ignore")
limpio = contenido.replace("\\", "")
mesada_esperada = rep.pesos(res["mesada_banda"][1])
revisar(mesada_esperada.replace("$", "") in limpio,
        f"la mesada {mesada_esperada} está escrita en el PDF")
revisar("Juan Pablo Granada" in contenido,
        "el nombre está escrito en el PDF")

# Y que la palanca de mayor impacto haya llegado al papel con su cifra: es el
# número que el reporte existe para mostrar.
mejor = next((p for p in pal["lista"] if p["efecto_mes"] is not None), None)
if mejor:
    revisar(rep.pesos(mejor["efecto_mes"]).replace("$", "") in limpio,
            f"la cifra de la mejor palanca ({rep.pesos(mejor['efecto_mes'])}) "
            "está escrita en el PDF")

# Y que las tildes sobrevivan: si se rompieran, la página se leería mal entera.
revisar("Diagn" in contenido, "los títulos con tilde se escribieron")


# ---------------------------------------------------------------------------
# El contenido cabe en la única página que tiene el reporte
# ---------------------------------------------------------------------------

print("\nQue no se desborde la página, que es un error que no se ve")

# El escritor de PDF no hace salto de página: si el contenido se pasa de largo
# se escribe fuera de la hoja y desaparece sin que falle nada. Desde que las
# secciones 4 y 5 traen texto de verdad (las frases con cifra y los límites de
# alcance, que son obligatorios) la página va justa, así que esto se comprueba
# caso por caso y no de vista.
# Desde el 2026-09-19 `pdf_simple.py` sabe hacer salto de página, así que un
# contenido que ya no cabe pasa a una hoja nueva en vez de escribirse por
# debajo del borde. Eso cambia lo que hay que vigilar: ya no es "cabe en una
# página" sino "no se perdió nada", y son dos comprobaciones.
for etiqueta, unos_datos, hojas_esperadas in (
        ("ahorro individual", datos, 2),
        ("prima media", datos_rpm, 1),
        ("prima media (caso 05)", datos_05, 1),
        ("garantía de pensión mínima", datos_02, 1),
        ("sin palancas", datos_sin, 1)):
    rep.escribir_pdf(unos_datos, Path("/tmp/jubilo-espacio.pdf"))
    sobrante = unos_datos["espacio_sobrante"]
    revisar(sobrante >= 0,
            f"en el reporte de {etiqueta} no se escribió nada por debajo del "
            f"pie de página (sobran {sobrante} puntos en la última hoja)")
    revisar(unos_datos["paginas"] == hojas_esperadas,
            f"el reporte de {etiqueta} ocupa {hojas_esperadas} hoja(s), que es "
            f"lo esperado (ocupa {unos_datos['paginas']})")

# El caso 01 es el que ya no cabe en una hoja. Se deja anotado aquí para que
# el día que vuelva a caber (o que se desborde otro) la prueba lo diga.
revisar(datos["paginas"] == 2,
        "el caso de ahorro individual necesita dos hojas: es el más largo y "
        "desde los subtítulos de las secciones 4 y 5 ya no cabe en una")


# ---------------------------------------------------------------------------
# El formato: la escala tipográfica y la escala de espaciado
# ---------------------------------------------------------------------------
#
# Lo que estas comprobaciones existen para impedir, y es una sola cosa: **que
# dos elementos del mismo nivel de jerarquía se vean distintos**. El dueño del
# producto lo detectó mirando el PDF: la mesada de la sección 2 salía más
# grande que el efecto de una palanca de la sección 4, aunque las dos son la
# cifra destacada de su fila.
#
# La forma de comprobarlo es espiar cada llamada de dibujo: se envuelve
# `Pagina.texto` para anotar qué se escribió, en qué posición y con qué
# tamaño. Así la prueba mide el PDF de verdad, no la intención del código.

print("\nEl formato: la escala tipográfica")

DIBUJOS = []
_texto_original = rep.Pagina.texto


def _texto_espia(self, x, y, contenido, tamano=10, negrita=False,
                 cursiva=False, color=(0, 0, 0), hoja=None):
    """Anota el dibujo y después deja que se dibuje de verdad.

    Anota también en qué hoja cayó cada trazo, que es lo que permite
    comprobar que el pie de página está en todas.
    """
    DIBUJOS.append({"x": x, "y": y, "texto": str(contenido),
                    "tamano": tamano, "negrita": negrita, "color": color,
                    "hoja": hoja if hoja is not None else self.paginas})
    return _texto_original(self, x, y, contenido, tamano=tamano,
                           negrita=negrita, cursiva=cursiva, color=color,
                           hoja=hoja)


rep.Pagina.texto = _texto_espia


def dibujar_y_espiar(unos_datos):
    """Genera el PDF de esos datos y devuelve la lista de lo que se dibujó."""
    DIBUJOS.clear()
    rep.escribir_pdf(unos_datos, Path("/tmp/jubilo-formato.pdf"))
    return list(DIBUJOS)


def dibujo_de(trazos, texto):
    """Busca el dibujo cuyo texto es exactamente el que se le pasa."""
    return next((t for t in trazos if t["texto"] == texto), None)


trazos = dibujar_y_espiar(datos)

# 1. Ningún dibujo usa un tamaño que no esté en la escala.
tamanos_usados = sorted({t["tamano"] for t in trazos})
fuera_de_escala = [t for t in tamanos_usados if t not in rep.TAMANOS_DE_LA_ESCALA]
revisar(not fuera_de_escala,
        f"todos los tamaños del PDF salen de la escala (sueltos: {fuera_de_escala})")

# 2. LA COMPROBACIÓN DEL DEFECTO REPORTADO. La mesada de la sección 2 y el
#    efecto de una palanca de la sección 4 son el valor de su fila, así que
#    tienen que medir exactamente lo mismo.
texto_mesada = rep.banda_en_pesos(res["mesada_banda"])
mejor_palanca = next(p for p in pal["lista"] if p["efecto_mes_texto"])
texto_palanca = mejor_palanca["efecto_mes_texto"]
texto_escenario = rep.pesos(esc["lista"][1]["mesada"])

trazo_mesada = dibujo_de(trazos, texto_mesada)
trazo_palanca = dibujo_de(trazos, texto_palanca)
trazo_escenario = dibujo_de(trazos, texto_escenario)

revisar(trazo_mesada is not None and trazo_palanca is not None
        and trazo_escenario is not None,
        "las tres cifras de fila (secciones 2, 4 y 5) se dibujaron en el PDF")
revisar(trazo_mesada["tamano"] == trazo_palanca["tamano"]
        == trazo_escenario["tamano"] == rep.NIVEL_VALOR["tamano"],
        f"el valor de fila mide lo mismo en las secciones 2, 4 y 5 "
        f"({rep.NIVEL_VALOR['tamano']} puntos), que era el defecto reportado")
revisar(trazo_mesada["negrita"] == trazo_palanca["negrita"] == trazo_escenario["negrita"],
        "y con el mismo peso en las tres")
revisar(trazo_mesada["color"] == trazo_palanca["color"] == trazo_escenario["color"],
        "y con el mismo color en las tres")

# 3. Las etiquetas de fila también son todas iguales entre secciones.
etiquetas = ("Mesada estimada", "Semanas cotizadas",
             mejor_palanca["titulo"], esc["lista"][0]["titulo"])
trazos_etiqueta = [dibujo_de(trazos, e) for e in etiquetas]
revisar(all(t is not None for t in trazos_etiqueta),
        "las etiquetas de fila de las secciones 1, 2, 4 y 5 están en el PDF")
revisar({t["tamano"] for t in trazos_etiqueta if t}
        == {rep.NIVEL_ETIQUETA["tamano"]},
        "y todas miden lo que dice la escala para una etiqueta de fila")

# 4. La jerarquía va de mayor a menor y sin empates raros: el título del
#    documento es lo más grande y la nota al pie lo más pequeño.
revisar(rep.NIVEL_TITULO["tamano"] > rep.NIVEL_NOMBRE["tamano"]
        > rep.NIVEL_FRANJA["tamano"] >= rep.NIVEL_VALOR["tamano"]
        > rep.NIVEL_APOYO["tamano"] > rep.NIVEL_NOTA["tamano"],
        "la escala tipográfica baja de tamaño a medida que baja la jerarquía")
revisar(rep.NIVEL_ETIQUETA["tamano"] == rep.NIVEL_VALOR["tamano"],
        "la etiqueta y el valor de una fila miden igual: van en la misma línea")


print("\nEl formato: la escala de espaciado")

# 5. Los espacios salen todos de la misma unidad base, no son números sueltos.
for nombre, valor in (("ESPACIO_LINEA", rep.ESPACIO_LINEA),
                      ("ESPACIO_FILA", rep.ESPACIO_FILA),
                      ("ESPACIO_BLOQUE", rep.ESPACIO_BLOQUE),
                      ("ESPACIO_ANTES_FRANJA", rep.ESPACIO_ANTES_FRANJA),
                      ("ESPACIO_DESPUES_FRANJA", rep.ESPACIO_DESPUES_FRANJA)):
    revisar(abs(valor / rep.UNIDAD - round(valor / rep.UNIDAD)) < 1e-9,
            f"{nombre} es un múltiplo exacto de la unidad base")

# 6. LA REGLA DE LA SEGUNDA QUEJA: separar bloques tiene que abrir más aire que
#    separar líneas, y bastante más, o el ojo no ve dónde acaba una palanca.
revisar(rep.ESPACIO_LINEA < rep.ESPACIO_FILA < rep.ESPACIO_BLOQUE,
        "la escala de espaciado crece de lo más junto a lo más separado")
revisar(rep.ESPACIO_BLOQUE >= 2 * rep.ESPACIO_LINEA,
        "el aire entre bloques es al menos el doble del aire entre líneas")

# 7. Y se comprueba sobre el PDF de verdad, no sobre las constantes: en la
#    sección 4, la distancia entre la última línea de una palanca y el título
#    de la siguiente tiene que ser mayor que la distancia entre dos líneas de
#    la misma palanca.
titulos_palanca = [dibujo_de(trazos, p["titulo"]) for p in pal["lista"]]
revisar(all(t is not None for t in titulos_palanca) and len(titulos_palanca) >= 2,
        "hay al menos dos palancas dibujadas para poder medir su separación")

# Se ordenan todos los trazos de arriba hacia abajo y se buscan los dos
# primeros títulos de palanca dentro de esa fila india.
por_altura = sorted(trazos, key=lambda t: -t["y"])
alturas = [t["y"] for t in por_altura]
inicio = alturas.index(titulos_palanca[0]["y"])
siguiente = alturas.index(titulos_palanca[1]["y"])
revisar(siguiente - inicio >= 2,
        "la primera palanca tiene más de una línea, que es lo que permite medir")

if siguiente - inicio >= 2:
    # Distancias entre líneas consecutivas dentro del primer bloque.
    dentro = [alturas[i] - alturas[i + 1] for i in range(inicio, siguiente - 1)]
    # Y la distancia entre la última línea del bloque y el título del siguiente.
    entre_bloques = alturas[siguiente - 1] - alturas[siguiente]
    revisar(entre_bloques > max(dentro),
            f"entre dos palancas hay más aire ({entre_bloques} puntos) que entre "
            f"las líneas de una misma palanca ({max(dentro)} puntos)")
    revisar(entre_bloques - max(dentro) >= rep.ESPACIO_BLOQUE / 2,
            "y la diferencia es lo bastante grande como para verse a simple vista")

# 7b. El corte entre dos secciones tiene que ser todavía mayor que el corte
#     entre dos bloques. No se mide con las constantes (las de la franja se
#     miden desde el borde del rectángulo gris, no desde la línea base) sino
#     sobre el PDF: cuánto baja de verdad de la última línea de una sección a
#     la primera fila de la siguiente.
franja_5 = dibujo_de(trazos, "5. TUS ESCENARIOS")
primera_fila_5 = dibujo_de(trazos, esc["lista"][0]["titulo"])
anterior_a_la_franja = [t["y"] for t in trazos if t["y"] > franja_5["y"]]
revisar(franja_5 is not None and primera_fila_5 is not None,
        "la franja de la sección 5 y su primera fila están en el PDF")
salto_de_seccion = min(anterior_a_la_franja) - primera_fila_5["y"]
revisar(salto_de_seccion > entre_bloques,
        f"pasar de una sección a otra abre más aire ({salto_de_seccion} puntos) "
        f"que pasar de un bloque al siguiente ({entre_bloques} puntos)")

# 7c. Y la franja gris no se monta sobre el texto de arriba ni sobre el de
#     abajo: la primera fila de la sección tiene que caber entera por debajo
#     del borde inferior del rectángulo.
borde_inferior = franja_5["y"] - rep.HUNDIDO_FRANJA
alto_de_la_letra = rep.NIVEL_ETIQUETA["tamano"]
revisar(primera_fila_5["y"] + alto_de_la_letra <= borde_inferior,
        "la primera fila de la sección no se monta sobre la franja gris")


print("\nEl formato: ningún número suelto en el código que dibuja")

# 8. La red de seguridad contra la reincidencia: se lee el propio código de la
#    parte que dibuja y se comprueba que no traiga tamaños, interlineados ni
#    colores escritos a mano. Todo tiene que venir de las constantes.
import re

fuente = Path(rep.__file__).read_text(encoding="utf-8")
codigo_que_dibuja = fuente.split("# --- Paso 2: dibujar la pagina")[1]
# Se quitan los comentarios: ahí sí se pueden nombrar números, y de hecho se
# nombran para explicar la escala.
sin_comentarios = "\n".join(l.split("#")[0] for l in codigo_que_dibuja.splitlines())

for etiqueta, patron in (
        ("un tamaño de letra", r"tamano\s*=\s*[0-9]"),
        ("un interlineado", r"interlineado\s*="),
        ("un color", r"color\s*=\s*\("),
        ("un salto vertical", r"bajar\(\s*[0-9]")):
    encontrados = re.findall(patron, sin_comentarios)
    revisar(not encontrados,
            f"la parte que dibuja no trae {etiqueta} escrito a mano "
            f"({len(encontrados)} casos)")


print("\nEl formato se aplica igual en los cinco casos")

# 9. La misma escala en todos los casos, no solo en el que se revisó a mano.
for etiqueta, unos_datos in (("prima media", datos_rpm),
                             ("prima media (caso 05)", datos_05),
                             ("garantía de pensión mínima", datos_02),
                             ("sin palancas", datos_sin)):
    otros = dibujar_y_espiar(unos_datos)
    sueltos = sorted({t["tamano"] for t in otros} - rep.TAMANOS_DE_LA_ESCALA)
    revisar(not sueltos,
            f"el reporte de {etiqueta} solo usa tamaños de la escala "
            f"(sueltos: {sueltos})")

# 10. Y en cada caso, la cifra de la sección 2 mide lo mismo que la de la 5.
for etiqueta, unos_datos in (("prima media", datos_rpm),
                             ("prima media (caso 05)", datos_05)):
    otros = dibujar_y_espiar(unos_datos)
    t_mesada = dibujo_de(otros,
                         rep.banda_en_pesos(unos_datos["resultado"]["mesada_banda"]))
    t_esc = dibujo_de(otros,
                      rep.pesos(unos_datos["escenarios"]["lista"][0]["mesada"]))
    revisar(t_mesada is not None and t_esc is not None
            and t_mesada["tamano"] == t_esc["tamano"] == rep.NIVEL_VALOR["tamano"],
            f"en {etiqueta} la mesada de la sección 2 y la del escenario base "
            "miden lo mismo")

print("\nEl formato de los textos nuevos y el invariante del pie de página")

# 11. Los dos subtítulos se dibujan en el nivel de texto de apoyo, no en uno
#     propio, y la etiqueta de cada cifra también: son aclaraciones, no filas.
trazos = dibujar_y_espiar(datos)
sub4 = dibujo_de(trazos, pal["que_significa_la_cifra"])
sub5 = dibujo_de(trazos, esc["que_significan_los_escenarios"])
revisar(sub4 is not None and sub4["tamano"] == rep.NIVEL_APOYO["tamano"],
        "el subtítulo de la sección 4 se dibuja en el nivel de texto de apoyo")
revisar(sub5 is not None and sub5["tamano"] == rep.NIVEL_APOYO["tamano"],
        "el subtítulo de la sección 5, en el mismo nivel que el de la 4")

# 12. La etiqueta va pegada a la cifra, en la misma línea y un nivel por
#     debajo, y todas las filas la tratan igual.
trazos_etiqueta = [dibujo_de(trazos, " " + p["etiqueta_efecto"])
                   for p in pal["lista"] if p["etiqueta_efecto"]]
revisar(len(trazos_etiqueta) >= 2 and all(t is not None for t in trazos_etiqueta),
        "las etiquetas de las cifras se dibujaron")
revisar({t["tamano"] for t in trazos_etiqueta if t}
        == {rep.NIVEL_APOYO["tamano"]},
        "todas las etiquetas miden lo mismo, el nivel de texto de apoyo")
for palanca_mostrada in pal["lista"]:
    if not palanca_mostrada["etiqueta_efecto"]:
        continue
    t_cifra = dibujo_de(trazos, palanca_mostrada["efecto_mes_texto"])
    # La misma etiqueta se repite en varias filas ("más de pensión al mes"),
    # así que no sirve buscarla por su texto: se busca la que está a la altura
    # de esta cifra, que es la de esta fila.
    t_etiq = next((t for t in trazos
                   if t["texto"] == " " + palanca_mostrada["etiqueta_efecto"]
                   and t["y"] == t_cifra["y"]), None)
    revisar(t_etiq is not None,
            f"la cifra de '{palanca_mostrada['clave']}' y su etiqueta van en "
            "la misma línea")
    revisar(t_etiq is not None and t_cifra["x"] < t_etiq["x"],
            "y la etiqueta va a la derecha de la cifra, no al revés")
    # Y ninguna de las dos se monta sobre el título de la fila.
    t_titulo = dibujo_de(trazos, palanca_mostrada["titulo"])
    fin_del_titulo = t_titulo["x"] + rep.ancho_de(
        palanca_mostrada["titulo"], rep.NIVEL_ETIQUETA["tamano"],
        rep.NIVEL_ETIQUETA["negrita"])
    revisar(fin_del_titulo < t_cifra["x"],
            f"en '{palanca_mostrada['clave']}' el título y la cifra no se "
            "solapan: la fila cabe en una línea")

# 13. LA COMPROBACIÓN MÁS FUERTE DE TODAS, y la que reemplaza al viejo "cabe
#     en una página": ningún trazo queda por debajo del pie de página.
#
#     Está escrita para que no dependa de los casos de hoy: recibe cualquier
#     diccionario de datos, dibuja su PDF y recorre TODOS los trazos de TODAS
#     sus hojas. Si dentro de seis meses alguien alarga un texto y el reporte
#     crece, esta comprobación lo sigue protegiendo sin que haya que tocarla.
#     Es la garantía de que el fallo silencioso (texto escrito fuera de la
#     hoja, que no se ve y no falla) ya no es posible.

def revisar_nada_bajo_el_pie(unos_datos, etiqueta):
    """Comprueba que ninguna línea de contenido cayó por debajo del pie."""
    otros = dibujar_y_espiar(unos_datos)
    # El pie de página y su numeración se dibujan a propósito por debajo de la
    # raya, así que se excluyen: lo que se vigila es el contenido, que es lo
    # que se puede perder sin que nadie se entere.
    del_pie = set(rep.partir(rep.TEXTO_PIE, rep.NIVEL_PIE["tamano"],
                             rep.ANCHO_UTIL))
    del_pie |= {rep._numero_de_hoja(i, unos_datos["paginas"])
                for i in range(1, unos_datos["paginas"] + 1)}
    del_contenido = [t for t in otros if t["texto"] not in del_pie]
    mas_bajo = min(t["y"] for t in del_contenido)
    revisar(mas_bajo >= rep.PIE_DE_PAGINA,
            f"en {etiqueta} no hay ni un trazo por debajo del pie de página "
            f"(lo más bajo está en {round(mas_bajo, 1)}, el pie en "
            f"{rep.PIE_DE_PAGINA})")
    # Y el margen de seguridad: el contenido tampoco toca la raya del pie.
    revisar(mas_bajo >= rep.SUELO_CONTENIDO,
            f"y en {etiqueta} tampoco baja del suelo de contenido "
            f"({rep.SUELO_CONTENIDO})")
    return otros


for etiqueta, unos_datos in (("ahorro individual", datos),
                             ("prima media", datos_rpm),
                             ("prima media (caso 05)", datos_05),
                             ("garantía de pensión mínima", datos_02),
                             ("sin palancas", datos_sin)):
    revisar_nada_bajo_el_pie(unos_datos, etiqueta)

# 14. El pie va en todas las hojas y numerado.
trazos_dos_hojas = dibujar_y_espiar(datos)
for hoja in range(1, datos["paginas"] + 1):
    revisar(dibujo_de(trazos_dos_hojas,
                      rep._numero_de_hoja(hoja, datos["paginas"])) is not None,
            f"la hoja {hoja} lleva su numeración '"
            f"{rep._numero_de_hoja(hoja, datos['paginas'])}'")
primera_linea_del_pie = rep.partir(rep.TEXTO_PIE, rep.NIVEL_PIE["tamano"],
                                   rep.ANCHO_UTIL)[0]
veces = len([t for t in trazos_dos_hojas
             if t["texto"] == primera_linea_del_pie])
revisar(veces == datos["paginas"],
        f"el texto del pie se repite en las {datos['paginas']} hojas "
        f"(aparece {veces} veces)")


print("\nEl desbordamiento forzado: la prueba de que ya no se pierde texto")

# 15. LA PRUEBA QUE DE VERDAD IMPORTA. Se infla un caso a propósito, muy por
#     encima de lo que produce hoy la calculadora, y se comprueba que el
#     reporte abre las hojas que haga falta y que NO se pierde ni una línea.
#
#     Antes del salto de página esto era imposible de detectar: el texto que
#     no cabía se escribía por debajo del borde de la hoja, no se veía, y no
#     fallaba nada. Por eso el caso sintético no se mide por "cuántas hojas
#     salieron" sino por "está todo lo que tenía que estar".

import copy

RELLENO = ("Esta frase se ha inflado a propósito para forzar el "
           "desbordamiento de la hoja y comprobar que el reporte no pierde "
           "ni una línea por el camino. ")

datos_gordo = copy.deepcopy(datos)
# Se alargan las frases y los límites de las palancas que ya hay...
for indice, palanca_gorda in enumerate(datos_gordo["palancas"]["lista"]):
    palanca_gorda["frase"] = (palanca_gorda["frase"] or "") + RELLENO * 3
    palanca_gorda["limite_de_alcance"] = (
        (palanca_gorda["limite_de_alcance"] or "") + RELLENO * 2)
# ...y se duplica la lista, para que no quepan ni de lejos en una hoja.
originales = list(datos_gordo["palancas"]["lista"])
for copia_numero in range(3):
    for palanca_gorda in originales:
        otra = copy.deepcopy(palanca_gorda)
        otra["titulo"] = "%s (copia %d)" % (otra["titulo"], copia_numero + 1)
        datos_gordo["palancas"]["lista"].append(otra)

trazos_gordo = dibujar_y_espiar(datos_gordo)

revisar(datos_gordo["paginas"] >= 2,
        f"el caso inflado no cabe en una hoja y se abren las que hagan falta "
        f"(salieron {datos_gordo['paginas']})")
revisar(datos_gordo["espacio_sobrante"] >= 0,
        f"y en la última hoja sigue sobrando espacio "
        f"({datos_gordo['espacio_sobrante']} puntos)")
revisar_nada_bajo_el_pie(datos_gordo, "el caso inflado a propósito")


def texto_dibujado(trazos):
    """Junta todo lo escrito en el PDF en un solo texto, para poder buscar."""
    return " ".join(" ".join(t["texto"].split()) for t in trazos)


todo_lo_escrito = texto_dibujado(trazos_gordo)

# NO SE PIERDE NI UNA LÍNEA: cada título, cada frase y cada límite de alcance
# de cada palanca tiene que estar escrito en alguna de las hojas.
perdidos = []
for palanca_gorda in datos_gordo["palancas"]["lista"]:
    for clave in ("titulo", "frase", "limite_de_alcance"):
        esperado = " ".join((palanca_gorda.get(clave) or "").split())
        if esperado and esperado not in todo_lo_escrito:
            perdidos.append((palanca_gorda["titulo"], clave))
revisar(not perdidos,
        f"no se perdió ni una línea de las {len(datos_gordo['palancas']['lista'])} "
        f"palancas infladas (perdidas: {perdidos[:3]})")

# Y tampoco se pierde el final del documento, que es lo primero que se perdía
# cuando el contenido se salía de la hoja: las salvedades legales.
for salvedad in (datos_gordo["supuestos"]["supuestos"]
                 + datos_gordo["supuestos"]["limites"]):
    revisar(" ".join(salvedad.split()) in todo_lo_escrito,
            f"la salvedad '{salvedad[:45]}...' llegó al papel")

# El pie y su numeración están en todas las hojas del caso inflado.
for hoja in range(1, datos_gordo["paginas"] + 1):
    revisar(dibujo_de(trazos_gordo,
                      rep._numero_de_hoja(hoja, datos_gordo["paginas"]))
            is not None,
            f"la hoja {hoja} de {datos_gordo['paginas']} lleva su numeración")

# Los bloques no se parten. Se comprueba sobre los trazos en el orden en que
# se dibujaron, no buscándolos por su texto: las palancas infladas son copias
# unas de otras y sus frases son idénticas, así que buscar por texto
# encontraría la de otra palanca. Lo que se mira es que, desde el título de
# una palanca hasta el título de la siguiente, todo caiga en la misma hoja.
indices_de_titulo = []
for palanca_gorda in datos_gordo["palancas"]["lista"]:
    indices_de_titulo += [i for i, t in enumerate(trazos_gordo)
                          if t["texto"] == palanca_gorda["titulo"]]
indices_de_titulo.sort()

partidas = []
for puesto, indice_titulo in enumerate(indices_de_titulo):
    siguiente = (indices_de_titulo[puesto + 1]
                 if puesto + 1 < len(indices_de_titulo) else len(trazos_gordo))
    del_bloque = trazos_gordo[indice_titulo:siguiente]
    # El bloque acaba donde empieza lo que ya no es suyo: la franja de la
    # sección siguiente. Se corta ahí, y lo que queda (título, cifra,
    # etiqueta, frase y límite de alcance) tiene que estar todo en una hoja.
    for puesto_interno, trazo in enumerate(del_bloque):
        if (trazo["tamano"] == rep.NIVEL_FRANJA["tamano"] and trazo["negrita"]
                and puesto_interno > 0):
            del_bloque = del_bloque[:puesto_interno]
            break
    hojas_del_bloque = {t["hoja"] for t in del_bloque}
    if len(hojas_del_bloque) > 1:
        partidas.append(trazos_gordo[indice_titulo]["texto"])
revisar(not partidas,
        f"ninguna palanca quedó partida entre dos hojas: su título, su cifra "
        f"y el principio de su frase van juntos (partidas: {partidas[:3]})")

# Y una franja de sección nunca es lo último de una hoja.
franjas = [t for t in trazos_gordo if t["tamano"] == rep.NIVEL_FRANJA["tamano"]
           and t["negrita"]]
huerfanas = []
for t_franja in franjas:
    debajo = [t for t in trazos_gordo
              if t["hoja"] == t_franja["hoja"] and t["y"] < t_franja["y"]
              and t["y"] >= rep.SUELO_CONTENIDO]
    if not debajo:
        huerfanas.append(t_franja["texto"])
revisar(not huerfanas,
        f"ninguna franja de sección se quedó sola al pie de una hoja "
        f"(huérfanas: {huerfanas})")


# Se devuelve el dibujo original, para no dejar el espía puesto.
rep.Pagina.texto = _texto_original


print("\n" + "=" * 70)
if fallas:
    print(f"RESULTADO: {len(fallas)} FALLAS")
    for f in fallas:
        print(f"  - {f}")
    sys.exit(1)
print("RESULTADO: TODO EN VERDE")
print("=" * 70)
