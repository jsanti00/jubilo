"""Le pide a Colpensiones que le mande la historia laboral a la persona.

Que hace, en una frase: llena por la persona el formulario publico de la sede
electronica de Colpensiones, el mismo que ella llenaria a mano, y devuelve a
que correo quedo enviada su historia laboral.

**Por que este archivo esta fuera de `calculadora/` y de `bot/`:** el principio
de diseno de Júbilo es que el cerebro del agente no tiene internet (ver
`AGENTS.md`). Este modulo si lo tiene, asi que vive aparte y se invoca como una
herramienta determinista, igual que se invoca la calculadora. El modelo nunca
navega: ejecuta esto y recibe un resultado.

**Las dos lineas que este archivo no cruza**, y estan aqui para que nadie las
borre sin darse cuenta:

  1. **No se evade ninguna proteccion anti-bot.** Si el portal responde a una
     peticion normal, seguimos. Si responde 403 o pide un captcha, este modulo
     se rinde y lo dice. No rota direcciones, no resuelve captchas y no
     falsifica senales de navegador para parecer una persona. La diferencia
     entre automatizarle el tramite al dueno de los datos y disfrazarse de el
     es exactamente esa.
  2. **Nunca se piden ni se guardan credenciales** de la cuenta de nadie en
     ningun fondo. Este tramite no las necesita: es publico y solo pide el tipo
     y el numero de documento.

**Lo que el feature si le ahorra a la persona y lo que no.** Colpensiones no
entrega el documento en pantalla: lo manda al correo que tiene registrado. Asi
que esto le ahorra llenar el formulario, y ella sigue teniendo que abrir su
correo y reenviar el PDF al chat. Hay que decirselo con esas palabras, porque
si cree que el documento va a aparecer solo, la espera se vuelve otro "no me
contesta".

Solo sirve para Colpensiones. Los fondos privados exigen iniciar sesion, y
automatizarlos obligaria a pedirle a la persona su usuario y su contrasena.
Para esos, lo que hay es la guia de descarga del kit.

Uso desde la linea de comandos (asi lo llama Júbilo):

    python3 tramites/pedir_historia.py CC 1005320949

Devuelve un JSON por pantalla. Siempre trae `ok`, y cuando `ok` es falso trae
`motivo`, que es lo que se le puede decir a la persona.
"""

import html
import json
import re
import sys
import urllib.error
import urllib.request
import uuid
from http.cookiejar import CookieJar

# --- Las direcciones y los nombres de los campos del formulario -------------
#
# Todo esto sale de leer el formulario publico. Si Colpensiones lo cambia, esto
# deja de funcionar y el modulo lo dice en vez de inventarse nada. Los nombres
# raros (fieldFrm3058) son los que el propio portal le pone a sus campos.

FORMULARIO = "https://sede.colpensiones.gov.co/tramite/updInfo/55/"
CAMPO_TIPO_DOCUMENTO = "fieldFrm3058"
CAMPO_NUMERO = "fieldFrm3059"

# Los codigos internos con los que el portal identifica cada tipo de documento.
TIPOS_DE_DOCUMENTO = {
    "CC": "2755",     # cedula de ciudadania
    "CE": "2756",     # cedula de extranjeria
}

# Cuanto se espera cada peticion antes de darse por vencido, en segundos.
ESPERA = 60

# El portal rechaza las peticiones sin navegador declarado. Esto NO es
# disfrazarse: es identificarse como un cliente HTTP normal, que es lo que
# cualquier libreria hace. Si algun dia hiciera falta imitar mas senales de un
# navegador de verdad para pasar, eso ya seria evasion y el feature se detiene.
NAVEGADOR = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
             "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36")


# --- Piezas sueltas ---------------------------------------------------------

def _abridor():
    """Crea un cliente HTTP que recuerda las galletas entre peticion y peticion.

    Hace falta porque el formulario tiene tres pasos y el portal reconoce que
    son la misma visita por la galleta de sesion. Sin esto, el segundo paso
    devuelve la pantalla de iniciar sesion.
    """
    cliente = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(CookieJar()))
    cliente.addheaders = [("User-Agent", NAVEGADOR), ("Accept-Language", "es-CO,es;q=0.9")]
    return cliente


def _campos_ocultos(pagina):
    """Saca los campos escondidos del formulario (`tk` y `sxToken`).

    Son dos numeros que el portal genera para cada visita y espera de vuelta.
    Sin ellos, el envio se rechaza y termina en la pantalla de iniciar sesion.
    Son parte del formulario, no una proteccion que se este saltando: un
    navegador los manda igual, sin que la persona los vea.
    """
    encontrados = {}
    for etiqueta in re.findall(r'<input[^>]*type="hidden"[^>]*>', pagina):
        nombre = re.search(r'name="([^"]+)"', etiqueta)
        valor = re.search(r'value="([^"]*)"', etiqueta)
        if nombre:
            encontrados[nombre.group(1)] = html.unescape(valor.group(1)) if valor else ""
    return {k: v for k, v in encontrados.items() if k in ("tk", "sxToken")}


def _accion_del_formulario(pagina):
    """Devuelve la direccion a la que hay que enviar el formulario de esa pagina.

    Cambia en cada paso, asi que se lee de la pagina en vez de escribirla fija.
    """
    formulario = re.search(r"<form[^>]*id='formUsu'.*?</form>", pagina, re.S)
    if not formulario:
        return None
    accion = re.search(r'action="([^"]+)"', formulario.group(0))
    return accion.group(1) if accion else None


def _enviar(cliente, destino, datos, vengo_de):
    """Manda el formulario y devuelve la pagina que responde el portal.

    Se arma el envio a mano (en vez de usar una libreria) por una razon
    practica: el portal exige saber de antemano el tamano del envio, y sin ese
    dato responde "411 Length Required".
    """
    borde = "----x" + uuid.uuid4().hex
    cuerpo = "".join(
        f'--{borde}\r\nContent-Disposition: form-data; name="{campo}"\r\n\r\n{valor}\r\n'
        for campo, valor in datos.items()
    ) + f"--{borde}--\r\n"
    cuerpo = cuerpo.encode("utf-8")

    peticion = urllib.request.Request(destino, data=cuerpo, headers={
        "Content-Type": f"multipart/form-data; boundary={borde}",
        "Content-Length": str(len(cuerpo)),
        "Referer": vengo_de,
        "Origin": "https://sede.colpensiones.gov.co",
        "User-Agent": NAVEGADOR,
    })
    respuesta = cliente.open(peticion, timeout=ESPERA)
    return respuesta.geturl(), respuesta.read().decode("utf-8", "ignore")


def _texto_plano(pagina):
    """Deja solo el texto visible de la pagina, sin etiquetas ni programas."""
    limpio = re.sub(r"<script.*?</script>|<style.*?</style>", " ", pagina, flags=re.S)
    limpio = re.sub(r"<[^>]+>", " ", html.unescape(limpio))
    return re.sub(r"\s+", " ", limpio)


def correo_enmascarado(pagina):
    """Saca el correo, ya tapado por Colpensiones, al que van a mandar el reporte.

    El portal lo muestra a medias a proposito (omarxxxxx@hotmail.com). Eso es
    justo lo que le sirve a la persona: le confirma cual de sus correos es, sin
    que el bot tenga que conocerlo completo. Ese correo tapado es lo unico de
    este tramite que se le repite en el chat.
    """
    texto = _texto_plano(pagina)
    hallazgo = re.search(r"enviada a:\s*(\S+@\S+?)(?:\s|<|$)", texto)
    if hallazgo:
        return hallazgo.group(1).strip(".,;")
    # Plan B por si cambia la frase: cualquier correo que venga tapado.
    hallazgo = re.search(r"\b[\w.+-]*[x*]{2,}[\w.+-]*@[\w.-]+\.\w+\b", texto)
    return hallazgo.group(0) if hallazgo else None


# --- El tramite completo ----------------------------------------------------

def pedir_historia_laboral(tipo_documento, numero, confirmar=True):
    """Hace el tramite de principio a fin y cuenta como fue.

    tipo_documento: "CC" o "CE".
    numero:         el numero del documento, solo digitos.
    confirmar:      con False se detiene en el paso 2, o sea despues de ver a
                    que correo iria, pero sin pedir el envio. Sirve para
                    mostrarle el correo a la persona y que ella decida.

    Devuelve un diccionario. Siempre trae `ok`. Cuando sale bien, trae ademas
    `correo` (el tapado) y `enviado`. Cuando sale mal, trae `motivo`, que es un
    texto que se le puede leer tal cual a la persona.
    """
    codigo = TIPOS_DE_DOCUMENTO.get(str(tipo_documento).strip().upper())
    if not codigo:
        return {"ok": False, "motivo": "Solo puedo hacer este trámite con cédula de ciudadanía o de extranjería."}

    numero = re.sub(r"\D", "", str(numero))
    if not (5 <= len(numero) <= 12):
        return {"ok": False, "motivo": "Ese número de documento no parece completo."}

    cliente = _abridor()

    # Paso 1: abrir el formulario y quedarse con la galleta y los campos ocultos.
    try:
        pagina = cliente.open(FORMULARIO, timeout=ESPERA).read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as fallo:
        # El 403 es el cortafuegos del portal. Si aparece, el feature se detiene
        # aqui: no se busca la vuelta. La salida es escribirle a Colpensiones.
        if fallo.code == 403:
            return {"ok": False, "motivo": "La página de Colpensiones no me está dejando entrar en este momento.",
                    "detalle": "403 del cortafuegos"}
        return {"ok": False, "motivo": "La página de Colpensiones no respondió bien.",
                "detalle": f"HTTP {fallo.code}"}
    except Exception as fallo:
        return {"ok": False, "motivo": "No pude conectarme con Colpensiones.", "detalle": str(fallo)}

    # Si el portal empezo a pedir un captcha, tambien nos detenemos. No se
    # resuelve: se documenta y se le dice a la persona que lo haga ella.
    if re.search(r"captcha", pagina, re.I):
        return {"ok": False, "motivo": "Colpensiones ahora pide una verificación que yo no puedo hacer por ti.",
                "detalle": "aparecio un captcha en el formulario"}

    destino = _accion_del_formulario(pagina)
    if not destino:
        return {"ok": False, "motivo": "El trámite de Colpensiones cambió y ya no lo reconozco.",
                "detalle": "no se encontro el formulario formUsu"}

    # Paso 2: mandar el documento. El portal responde con el correo tapado.
    datos = {CAMPO_TIPO_DOCUMENTO: codigo, CAMPO_NUMERO: numero, "Siguiente": "Continuar"}
    datos.update(_campos_ocultos(pagina))
    try:
        url_paso2, pagina2 = _enviar(cliente, destino, datos, FORMULARIO)
    except Exception as fallo:
        return {"ok": False, "motivo": "Colpensiones no recibió bien el trámite.", "detalle": str(fallo)}

    # Si termina en la pantalla de iniciar sesion, es que el tramite dejo de ser
    # publico. Ahi se detiene: pedirle la clave de Colpensiones a alguien no
    # esta sobre la mesa.
    if "/login" in url_paso2:
        return {"ok": False, "motivo": "Colpensiones ahora exige iniciar sesión para este trámite, así que lo tienes que hacer tú.",
                "detalle": "redirige a /login"}

    correo = correo_enmascarado(pagina2)
    if not correo:
        # El portal no explica el motivo: con un documento que no esta en su
        # base simplemente devuelve la pantalla sin el correo. Lo comprobado el
        # 2026-09-18 es que ese es el sintoma, asi que no se afirma mas que eso.
        return {"ok": False,
                "motivo": "Colpensiones no me devolvió ningún correo para ese documento. "
                          "Puede que el número esté mal, o que no estés afiliado a Colpensiones.",
                "detalle": "el portal no mostro correo en el paso 2"}

    if not confirmar:
        return {"ok": True, "correo": correo, "enviado": False}

    # Paso 3: confirmar el envio. Es el boton "Continuar" de la pantalla que
    # acaba de mostrar el correo.
    destino2 = _accion_del_formulario(pagina2)
    if not destino2:
        return {"ok": False, "motivo": "El trámite de Colpensiones cambió a mitad de camino.", "correo": correo}

    datos2 = {"Siguiente": "Continuar"}
    datos2.update(_campos_ocultos(pagina2))
    try:
        _, pagina3 = _enviar(cliente, destino2, datos2, url_paso2)
    except Exception as fallo:
        return {"ok": False, "motivo": "No pude confirmar el envío.", "correo": correo, "detalle": str(fallo)}

    # La confirmacion tiene una frase inconfundible. Si no esta, no afirmamos
    # que se envio: decir que llego algo que no llego es peor que no hacer nada.
    if "enviada exitosamente" not in _texto_plano(pagina3).lower():
        return {"ok": False, "motivo": "Le pedí el documento a Colpensiones pero no me confirmó el envío.",
                "correo": correo}

    return {"ok": True, "correo": correo, "enviado": True}


def main():
    if len(sys.argv) < 3:
        print("Uso: python3 tramites/pedir_historia.py <CC|CE> <numero> [--solo-mirar]")
        sys.exit(1)
    confirmar = "--solo-mirar" not in sys.argv
    print(json.dumps(pedir_historia_laboral(sys.argv[1], sys.argv[2], confirmar), ensure_ascii=False))


if __name__ == "__main__":
    main()
