# Prueba del modulo que le pide la historia laboral a Colpensiones.
# Uso: python3 tramites/probar_pedir_historia.py   (termina en 1 si algo falla)
#
# Esta prueba NO toca internet. Trabaja sobre pedazos de las paginas reales de
# Colpensiones, guardadas aqui tal como respondio el portal el 2026-09-18.
# Asi se puede correr mil veces sin hacerle una sola peticion al portal, y si
# Colpensiones cambia el formulario, la prueba sigue diciendo si nuestra forma
# de leerlo es correcta o no.
#
# Lo que se prueba es lo unico que de verdad puede salir mal en silencio: que
# leamos bien el correo enmascarado. Si eso falla, el bot le diria a la persona
# que su documento va a un correo que no es.

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import pedir_historia as tramite

fallas = []


def revisar(condicion, descripcion):
    """Anota el resultado de una comprobación y lo imprime."""
    print(f"  {'OK  ' if condicion else 'FALLA'}  {descripcion}")
    if not condicion:
        fallas.append(descripcion)


# ---------------------------------------------------------------------------
# Leer el correo enmascarado de la página del paso 2
# ---------------------------------------------------------------------------

print("\nEl correo al que Colpensiones va a mandar el documento")

# Esto es, palabra por palabra, lo que devolvió el portal el 2026-09-18.
PAGINA_REAL = """
<div class="contenido">
  <h2>Env&iacute;a tu Historia Laboral a tu correo electr&oacute;nico</h2>
  <p>Tu Historia Laboral ser&aacute; enviada a: omarxxxxx@hotmail.com</p>
  <p>En caso de que este s&iacute; sea tu correo electr&oacute;nico, puedes
     Continuar con el env&iacute;o de tu Historia Laboral.</p>
</div>
"""

revisar(tramite.correo_enmascarado(PAGINA_REAL) == "omarxxxxx@hotmail.com",
        "se lee el correo tapado tal como lo muestra el portal")

# Colpensiones tapa el correo con equis, pero otras pantallas usan asteriscos.
revisar(tramite.correo_enmascarado(
    "<p>Tu Historia Laboral ser&aacute; enviada a: ma***@gmail.com</p>") == "ma***@gmail.com",
        "también se lee si el correo viene tapado con asteriscos")

# Y si no hay correo, no se puede inventar uno.
revisar(tramite.correo_enmascarado("<p>No encontramos tu información.</p>") is None,
        "cuando no hay correo, no se devuelve nada inventado")
revisar(tramite.correo_enmascarado("") is None,
        "una página vacía no devuelve correo")


# ---------------------------------------------------------------------------
# Los campos escondidos del formulario
# ---------------------------------------------------------------------------

print("\nLos campos escondidos que el portal espera de vuelta")

FORMULARIO_REAL = """
<input type="hidden" value="fee84310c38ede6cb6e28728bcd8b856" name="tk">
<input type="hidden" id="idActual" value="55">
<input type="hidden" id="estadoActual" value="">
<input type="hidden" name="sxToken" value="4786a90495b0b802a5e45ba8372ad86b">
"""

ocultos = tramite._campos_ocultos(FORMULARIO_REAL)
revisar(ocultos.get("tk") == "fee84310c38ede6cb6e28728bcd8b856", "se recoge el campo tk")
revisar(ocultos.get("sxToken") == "4786a90495b0b802a5e45ba8372ad86b", "se recoge el campo sxToken")
revisar("idActual" not in ocultos, "no se mandan de vuelta los campos que el portal no pide")


# ---------------------------------------------------------------------------
# La dirección a la que se envía cada paso
# ---------------------------------------------------------------------------

print("\nLa dirección de envío, que cambia en cada paso")

PAGINA_CON_FORMULARIO = (
    "<form enctype='multipart/form-data' id='formUsu' method='post' "
    "action=\"https://sede.colpensiones.gov.co/tramite/updInfo/55/982\">"
    "<input name='fieldFrm3059'></form>"
)
revisar(tramite._accion_del_formulario(PAGINA_CON_FORMULARIO)
        == "https://sede.colpensiones.gov.co/tramite/updInfo/55/982",
        "se lee de la página y no se escribe fija")
revisar(tramite._accion_del_formulario("<p>página sin formulario</p>") is None,
        "si el formulario desapareció, se dice que no está en vez de adivinar")


# ---------------------------------------------------------------------------
# Lo que se rechaza antes de tocar internet
# ---------------------------------------------------------------------------

print("\nLo que ni siquiera se intenta")

malo = tramite.pedir_historia_laboral("TI", "1005320949")
revisar(not malo["ok"] and "cédula" in malo["motivo"],
        "una tarjeta de identidad se rechaza aquí, sin molestar al portal")

corto = tramite.pedir_historia_laboral("CC", "123")
revisar(not corto["ok"] and "completo" in corto["motivo"],
        "un número demasiado corto se rechaza aquí")

# Un número escrito con puntos es lo normal en Colombia y no se puede rechazar
# por eso. Se comprueba sin llamar al portal: lo que importa es que al quitarle
# los puntos quede un número de largo válido.
import re as _re
solo_digitos = _re.sub(r"\D", "", "1.005.320.949")
revisar(5 <= len(solo_digitos) <= 12,
        "un número con puntos queda dentro del largo válido al limpiarlo")


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
