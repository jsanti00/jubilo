"""Arma el reporte de cierre de Júbilo: una pagina en PDF.

**La regla que este archivo existe para cumplir.** El reporte lo arma el codigo,
no el modelo. Es una plantilla fija que se llena con la salida de
`calculadora/diagnosticar.py`. Si el modelo "dibujara" el reporte, cada uno
saldria distinto y, peor, podria reescribir una cifra. Es la misma regla dura del
proyecto: la IA conversa, el codigo fijo hace los numeros.

**Consecuencia practica, y es la mas importante de todo el archivo:** aqui NO se
calcula nada. Cada cifra se copia tal cual del diccionario del diagnostico. No
se redondea, no se promedia, no se reconstruye. Si una cifra no viene en el
diagnostico, el reporte dice que no la hay, en vez de inventarla. Su prueba
(`probar_armar_reporte.py`) compara cifra por cifra el reporte contra el JSON.

**Estructura de la pagina, validada por Santiago el 2026-09-18.** Siete
secciones, en este orden, que es la secuencia real de la pregunta que la persona
trae:

  1. Encabezado, con quien es y donde esta hoy.
  2. Tu resultado, si sigues como hoy.
  3. Tus alertas.
  4. Tus palancas.
  5. Tus escenarios, dos, con el mismo formato del resultado.
  6. Tus siguientes pasos, pueden ser varios.
  7. Supuestos y limites.

**Decisiones de Santiago del 2026-09-18 que este archivo respeta:**

  - **Formato: solo PDF**, una pagina. No se genera imagen.
  - **El reporte SI lleva el nombre completo de la persona.** Se le advirtio que
    el reporte se puede reenviar, y decidio que va. Lo que NO lleva, y eso no se
    negocia, es la cedula ni ningun numero de documento.
  - El sexo va como la letra sola, sin explicacion.

Como se usa:

    python3 reporte/armar_reporte.py diagnostico.json "Nombre Apellido" Porvenir salida.pdf
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from pdf_simple import Pagina, partir, ancho_de

# --- Como se ve la pagina ---------------------------------------------------

MARGEN = 46                      # margen izquierdo y derecho, en puntos
ANCHO_UTIL = 612 - 2 * MARGEN    # el ancho que queda para escribir
AZUL = (0.09, 0.24, 0.40)        # el color de los titulos de seccion
GRIS = (0.42, 0.42, 0.42)        # para las notas al pie y las salvedades
GRIS_FONDO = (0.94, 0.95, 0.96)  # el fondo de las franjas de seccion

# Los meses en espanol, para escribir las fechas como las lee una persona.
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


# --- Piezas para escribir numeros como los lee una persona -----------------

def pesos(valor):
    """Pasa un numero a pesos colombianos: 2090605 queda como $2.090.605."""
    if valor is None:
        return "sin dato"
    return "$" + "{:,.0f}".format(round(valor)).replace(",", ".")


def banda_en_pesos(par):
    """Escribe una banda de mesada. Si los dos extremos son iguales, no repite."""
    if not par:
        return "sin dato"
    bajo, alto = par
    if bajo is None or alto is None:
        return "sin dato"
    if round(bajo) == round(alto):
        return pesos(bajo)
    return "entre %s y %s" % (pesos(bajo), pesos(alto))


def fecha_larga(iso):
    """Pasa 2061-01-20 a "enero de 2061". El dia no aporta a un horizonte asi."""
    if not iso:
        return None
    try:
        anio, mes, _ = str(iso).split("-")
        return "%s de %s" % (MESES[int(mes) - 1], anio)
    except (ValueError, IndexError):
        return str(iso)


def semanas(valor):
    """Escribe las semanas con un decimal, que es como las trae la calculadora."""
    if valor is None:
        return "sin dato"
    return "{:,.0f}".format(valor).replace(",", ".")


# --- Paso 1: sacar del diagnostico lo que va en la pagina ------------------

def datos_del_reporte(diagnostico, nombre, fondo):
    """Extrae del diagnostico las cifras exactas que van en cada seccion.

    Devuelve un diccionario con las siete secciones. Esta separado de la parte
    que dibuja a proposito: asi la prueba puede comparar estas cifras contra el
    JSON sin tener que leer un PDF.

    NO calcula nada. Cada valor sale de una clave del diagnostico.
    """
    # EL CANDADO, y es lo primero por una razon. Si el diagnostico no quedo
    # completo (porque falta el sexo, porque la verificacion no cuadro, o
    # porque el documento venia incompleto), NO se arma el reporte. Una pagina
    # llena de "sin dato" es peor que no mandar nada: parece un resultado y no
    # lo es. Se levanta un error con las preguntas que faltan, para que quien
    # llame pueda decirle a la persona que le falta.
    if not diagnostico.get("listo_para_entregar"):
        pendientes = diagnostico.get("preguntas_al_usuario") or []
        motivo = (diagnostico.get("diagnostico") or {}).get("error")
        raise ValueError(
            "El diagnóstico no está listo, así que no se arma reporte. "
            "Motivo: %s. Falta: %s" % (motivo or "sin especificar",
                                       "; ".join(pendientes) or "sin especificar"))

    modulo = diagnostico["router"]["modulo"]           # "rpm" o "rais"
    encabezado = diagnostico["diagnostico"]
    base = (diagnostico.get("recuperacion") or {}).get("base") or {}

    datos = {
        "modulo": modulo,
        "encabezado": _encabezado(diagnostico, encabezado, nombre, fondo, modulo),
        "resultado": _resultado(diagnostico, base, modulo),
        "alertas": _alertas(diagnostico),
        "palancas": _palancas(diagnostico, modulo),
        "escenarios": _escenarios(diagnostico, base, modulo),
        "siguientes_pasos": _siguientes_pasos(diagnostico, modulo),
        "supuestos": _supuestos(diagnostico, encabezado, modulo),
    }
    return datos


def _encabezado(diagnostico, enc, nombre, fondo, modulo):
    """Quien es la persona y donde esta hoy. Seccion 1."""
    # Ojo: los dos regimenes traen claves distintas. En prima media el requisito
    # viene en el propio bloque del diagnostico; en ahorro individual, lo que
    # marca el umbral son las semanas de la garantia de pension minima.
    faltan = None
    if modulo == "rpm":
        requisito = enc.get("requisito_semanas_hoy")
    else:
        requisito = enc.get("semanas_gpm")
    if requisito is not None and enc.get("semanas_hoy") is not None:
        faltan = max(0.0, requisito - enc["semanas_hoy"])

    return {
        "nombre": nombre,
        "fondo": fondo,
        "fecha_calculo": diagnostico.get("fecha_calculo"),
        "edad": enc.get("edad"),
        "sexo": enc.get("sexo"),
        "regimen": "Prima media (Colpensiones)" if modulo == "rpm"
                   else "Ahorro individual (fondo privado)",
        "semanas_hoy": enc.get("semanas_hoy"),
        # El requisito depende del regimen: en prima media son las semanas para
        # pensionarse, en ahorro individual las de la garantia de pension minima.
        "requisito_semanas": requisito,
        "que_es_el_requisito": ("semanas para pensionarte" if modulo == "rpm"
                                else "semanas para la garantía de pensión mínima"),
        "semanas_que_faltan": faltan,
        "edad_legal": enc.get("edad_legal"),
    }


def _resultado(diagnostico, base, modulo):
    """El resultado si sigue como hoy. Seccion 2."""
    if modulo == "rpm":
        rpm = diagnostico["diagnostico"]
        escenario = rpm.get("escenario_sigue_cotizando") or {}
        return {
            "fecha_pension": rpm.get("fecha_pension_estimada"),
            # En Colpensiones la formula es determinista, asi que los dos
            # extremos de la banda son el mismo numero y no se repite al
            # escribirlo. Se deja como par para que las dos secciones que
            # muestran mesada (esta y la de escenarios) usen el mismo formato.
            "mesada_banda": (escenario.get("mesada"), escenario.get("mesada")),
            "tasa_de_reemplazo_pct": escenario.get("tasa_pct"),
            "ibl": escenario.get("ibl"),
            "es_punto_no_banda": True,
            "nota": ("en Colpensiones la fórmula es determinista, así que el "
                     "resultado es un punto y no una banda"),
        }
    # OJO CON LA FUENTE DE ESTA CIFRA. La mesada sale del escenario "moderado"
    # del propio diagnostico, NO de `recuperacion.base`. Hoy los dos numeros son
    # identicos, pero no son la misma cosa: `recuperacion.base` es el punto de
    # partida contra el que se comparan los escenarios de recuperacion, y se
    # calcula SIN los supuestos de palanca (si se pide el diagnostico con un
    # sueldo futuro distinto, `recuperacion.base` no se entera y el escenario si).
    # Leer de ahi funcionaba por casualidad y se habria roto en el momento en que
    # el reporte empezara a mostrar palancas.
    escenario_base = (diagnostico["diagnostico"].get("escenarios") or {}).get("moderado") or {}
    return {
        "fecha_pension": base.get("fecha_pension"),
        "edad_pension": diagnostico["diagnostico"].get("edad_legal"),
        "mesada_banda": escenario_base.get("mesada_banda") or base.get("mesada_banda"),
        "perfil_de_la_cifra": "moderado",
        "es_punto_no_banda": False,
        "salida": base.get("salida"),
        "nota": ("la banda no es imprecisión: sus dos extremos son dos precios "
                 "distintos de la renta vitalicia, el de la norma y el de mercado"),
    }


def _alertas(diagnostico):
    """Moras y lagunas, con su impacto en semanas. Seccion 3."""
    resumen = (diagnostico.get("lagunas") or {}).get("resumen") or {}
    inventario = (diagnostico.get("recuperacion") or {}).get("inventario") or {}
    alertas = []

    if resumen.get("vacios"):
        alertas.append({
            "titulo": "Meses sin cotizar",
            "cifra": "%s huecos, %s semanas perdidas"
                     % (resumen["vacios"], semanas(resumen.get("semanas_en_vacios"))),
            "detalle": "son periodos en que nadie cotizó por ti",
        })
    if resumen.get("tramos_con_deficit"):
        alertas.append({
            "titulo": "Periodos cotizados de forma incompleta",
            "cifra": "%s tramos, %s semanas"
                     % (resumen["tramos_con_deficit"],
                        semanas(resumen.get("semanas_en_deficit_de_tramos"))),
            "detalle": "se cotizó, pero no el periodo completo",
        })
    if inventario.get("mora_sin_contar"):
        alertas.append({
            "titulo": "Mora del empleador que aún no te cuenta",
            "cifra": "%s periodos" % len(inventario["mora_sin_contar"]),
            "detalle": "tu empleador reportó el salario pero no pagó",
        })
    if resumen.get("filas_ibc_sin_semanas"):
        alertas.append({
            "titulo": "Filas con salario y cero semanas",
            "cifra": "%s fila%s" % (resumen["filas_ibc_sin_semanas"],
                                    "" if resumen["filas_ibc_sin_semanas"] == 1 else "s"),
            "detalle": "es la señal típica de un error en la historia laboral",
        })

    return {
        "lista": alertas,
        "semanas_perdidas_total": resumen.get("semanas_perdidas_total"),
        "sin_alertas": not alertas,
    }


def _palancas(diagnostico, modulo):
    """Que puede hacer y que gana. Seccion 4.

    Las palancas con cifra salen de `recuperacion.escenarios`, que es lo que la
    calculadora sabe cuantificar. Las que no tienen cifra se nombran sin numero,
    porque poner un numero inventado al lado seria peor que no poner ninguno.
    """
    escenarios = (diagnostico.get("recuperacion") or {}).get("escenarios") or {}
    inventario = (diagnostico.get("recuperacion") or {}).get("inventario") or {}
    palancas = []

    for nombre, contenido in escenarios.items():
        palancas.append({
            "que": nombre.replace("_", " "),
            "gana": banda_en_pesos(contenido.get("mesada_banda")),
            "semanas": contenido.get("semanas"),
            "cuantificada": True,
        })

    if inventario.get("semanas_acreditables"):
        palancas.append({
            "que": "Reclamar las semanas en mora a tu empleador",
            "gana": "%s semanas acreditables" % semanas(inventario["semanas_acreditables"]),
            "cuantificada": True,
        })

    # Palancas que siempre aplican y que la calculadora no cuantifica sola.
    ventana = (diagnostico.get("comparacion") or {}).get("ventana_traslado") or {}
    if ventana.get("abierta"):
        palancas.append({
            "que": "Evaluar el cambio de régimen, que tienes la ventana abierta",
            "gana": "se cierra a los %s años, te quedan %s"
                    % (ventana.get("edad_cierre"), ventana.get("anios_restantes")),
            "cuantificada": False,
            "salvedad": ("cambiar de régimen exige la doble asesoría obligatoria "
                         "de ley: esto no la reemplaza"),
        })
    if modulo == "rais":
        palancas.append({
            "que": "Cotizar sobre un salario base mayor, si puedes",
            "gana": "cada peso que entra a tu cuenta rinde hasta que te pensiones",
            "cuantificada": False,
        })

    return {"lista": palancas, "sin_palancas": not palancas}


def _escenarios(diagnostico, base, modulo):
    """Dos escenarios con palancas aplicadas. Seccion 5.

    Formato igual al de la seccion "Tu resultado", que es lo que pidio Santiago:
    fecha de pension y mesada como banda, para poder compararlos de un vistazo.

    De donde salen, en este orden de preferencia:
      1. De `recuperacion.escenarios`, que son las palancas ya cuantificadas.
      2. De los escenarios de perfil de fondo que la ley le permite, que son
         una comparacion real y no un supuesto inventado.
    Si no hay ni dos, se devuelven los que haya y se dice cuantos son.
    """
    salida = []

    for nombre, contenido in ((diagnostico.get("recuperacion") or {}).get("escenarios") or {}).items():
        salida.append({
            "titulo": "Si %s" % nombre.replace("_", " "),
            "fecha_pension": contenido.get("fecha_pension"),
            "mesada_banda": contenido.get("mesada_banda"),
            "de_donde": "palanca cuantificada",
        })

    if len(salida) < 2 and modulo == "rais":
        convergencia = diagnostico["diagnostico"].get("convergencia_obligatoria") or {}
        permitidos = convergencia.get("perfiles_permitidos") or []
        escenarios_fondo = diagnostico["diagnostico"].get("escenarios") or {}
        # El escenario de "dejar de cotizar" es el mas informativo de todos,
        # porque es el que la gente no se imagina. Va primero.
        for clave, titulo in (("deja_de_cotizar", "Si dejas de cotizar hoy"),
                              ("mayor_riesgo", "Si tu saldo va al portafolio de mayor riesgo"),
                              ("conservador", "Si tu saldo va al portafolio conservador")):
            if len(salida) >= 2:
                break
            if clave not in escenarios_fondo:
                continue
            # No se ofrece un perfil que la ley ya no le permite por su edad.
            if clave in ("mayor_riesgo", "conservador") and permitidos and clave not in permitidos:
                continue
            contenido = escenarios_fondo[clave]
            salida.append({
                "titulo": titulo,
                "fecha_pension": None,
                "mesada_banda": contenido.get("mesada_banda"),
                "salida_del_sistema": contenido.get("salida"),
                "de_donde": "escenario de la calculadora",
            })

    if len(salida) < 2 and modulo == "rpm":
        rpm = diagnostico["diagnostico"]
        deja = rpm.get("escenario_deja_de_cotizar") or {}
        if deja:
            salida.append({
                "titulo": "Si dejas de cotizar hoy",
                "fecha_pension": None,
                "mesada_banda": (deja.get("mesada"), deja.get("mesada")),
                "salida_del_sistema": deja.get("salida"),
                "de_donde": "escenario de la calculadora",
            })

    return {"lista": salida[:2], "cuantos": len(salida[:2])}


def _siguientes_pasos(diagnostico, modulo):
    """Los pasos concretos. Seccion 6. Santiago pidio que puedan ser varios."""
    pasos = []
    resumen = (diagnostico.get("lagunas") or {}).get("resumen") or {}
    inventario = (diagnostico.get("recuperacion") or {}).get("inventario") or {}

    if inventario.get("mora_sin_contar"):
        pasos.append("Reclámale a tu empleador los periodos en mora, o radica la "
                     "corrección de historia laboral ante tu administradora.")
    if resumen.get("filas_ibc_sin_semanas"):
        pasos.append("Pide la corrección de las filas que tienen salario "
                     "reportado y cero semanas: es un error del registro.")
    if resumen.get("vacios"):
        pasos.append("Revisa los meses sin cotizar: si en alguno estabas "
                     "trabajando, hay con qué reclamarlo.")

    ventana = (diagnostico.get("comparacion") or {}).get("ventana_traslado") or {}
    if ventana.get("abierta"):
        pasos.append("Si vas a evaluar el cambio de régimen, pide la doble "
                     "asesoría obligatoria en tu fondo y en Colpensiones. Es "
                     "gratis y es un requisito de ley.")

    pasos.append("Vuelve a bajar tu historia laboral en un año y compárala con "
                 "este reporte: es la forma de darte cuenta a tiempo si algo "
                 "quedó mal registrado.")
    return pasos


def _supuestos(diagnostico, enc, modulo):
    """Que se asumio y que no cubre este diagnostico. Seccion 7."""
    lineas = []
    if enc.get("ibc_futuro_supuesto"):
        lineas.append("Se asumió que sigues cotizando sobre %s, en pesos de hoy."
                      % pesos(enc["ibc_futuro_supuesto"]))
    if enc.get("densidad_futura_supuesta") is not None:
        lineas.append("Se asumió que cotizas el %.0f%% del tiempo de aquí en "
                      "adelante, que es tu ritmo de los últimos 3 años."
                      % (enc["densidad_futura_supuesta"] * 100))
    if modulo == "rais":
        banda = enc.get("banda_rendimiento") or {}
        prospectivo = banda.get("prospectivo") or {}
        if prospectivo.get("moderado"):
            # El separador decimal en espanol es la coma, no el punto.
            tasa = ("%.2f" % (prospectivo["moderado"] * 100)).replace(".", ",")
            lineas.append("El rendimiento del ahorro se proyectó al %s%% real "
                          "anual (portafolio moderado), un supuesto de largo "
                          "plazo, no una promesa." % tasa)
        convergencia = enc.get("convergencia_obligatoria") or {}
        if (convergencia.get("mezcla") or {}).get("conservador"):
            lineas.append("Por tu edad, la ley ya obliga a que el %.0f%% de tu "
                          "saldo esté en el portafolio conservador."
                          % (convergencia["mezcla"]["conservador"] * 100))

    limites = [
        "Este es un diagnóstico preliminar, no una liquidación certificada. "
        "La cifra oficial la da tu administradora cuando reclamas.",
        "Todas las cifras están en pesos de hoy, sin proyectar inflación.",
        "No reemplaza la doble asesoría obligatoria para cambiar de régimen.",
    ]
    verificacion = diagnostico.get("verificacion") or {}
    if verificacion.get("cuadra"):
        limites.insert(0, "Las semanas de este reporte cuadran contra el total "
                          "impreso de tu historia laboral (calculado %s, "
                          "documento %s)."
                          % (semanas(verificacion.get("calculado")),
                             semanas(verificacion.get("documento"))))
    return {"supuestos": lineas, "limites": limites}


# --- Paso 2: dibujar la pagina --------------------------------------------

class _Lienzo:
    """Lleva la cuenta de por donde va la pagina, para no pisar lo anterior."""

    def __init__(self):
        self.pagina = Pagina()
        self.y = 792 - 44          # se empieza cerca del borde de arriba

    def bajar(self, puntos):
        self.y -= puntos

    def titulo_seccion(self, texto):
        """Una franja gris con el titulo de la seccion."""
        self.bajar(20)
        self.pagina.rectangulo(MARGEN, self.y - 4, ANCHO_UTIL, 15, GRIS_FONDO)
        self.pagina.texto(MARGEN + 5, self.y, texto, tamano=9.5, negrita=True,
                          color=AZUL)
        self.bajar(14)

    def renglon(self, izquierda, derecha=None, tamano=9, negrita=False,
                color=(0, 0, 0)):
        """Una linea con texto a la izquierda y, si se pasa, algo a la derecha."""
        self.pagina.texto(MARGEN + 5, self.y, izquierda, tamano=tamano,
                          negrita=negrita, color=color)
        if derecha:
            ancho = ancho_de(derecha, tamano, negrita)
            self.pagina.texto(612 - MARGEN - 5 - ancho, self.y, derecha,
                              tamano=tamano, negrita=negrita, color=color)
        self.bajar(tamano + 3.5)

    def parrafo(self, texto, tamano=8, color=GRIS, sangria=5):
        """Texto que se parte solo cuando no cabe en el ancho."""
        for linea in partir(texto, tamano, ANCHO_UTIL - sangria - 5):
            self.pagina.texto(MARGEN + sangria, self.y, linea, tamano=tamano,
                              color=color)
            self.bajar(tamano + 2)


def escribir_pdf(datos, ruta):
    """Dibuja la pagina con los datos ya extraidos y la guarda."""
    lienzo = _Lienzo()
    enc = datos["encabezado"]

    # --- 1. Encabezado ---
    lienzo.pagina.texto(MARGEN, lienzo.y, "Tu diagnóstico pensional",
                        tamano=19, negrita=True, color=AZUL)
    lienzo.bajar(16)
    lienzo.pagina.texto(MARGEN, lienzo.y, enc["nombre"] or "", tamano=11,
                        negrita=True)
    lienzo.bajar(12)
    lienzo.pagina.texto(
        MARGEN, lienzo.y,
        "%s  |  %s  |  %s años  |  %s  |  Diagnóstico del %s"
        % (enc["fondo"] or "", enc["regimen"], enc["edad"], enc["sexo"] or "",
           enc["fecha_calculo"] or ""),
        tamano=8.5, color=GRIS)
    lienzo.bajar(10)
    lienzo.pagina.linea(MARGEN, lienzo.y, 612 - MARGEN, lienzo.y, grosor=1,
                        color=AZUL)

    lienzo.titulo_seccion("1. DÓNDE ESTÁS HOY")
    lienzo.renglon("Semanas cotizadas", semanas(enc["semanas_hoy"]), negrita=True)
    lienzo.renglon("Las que te exigen (%s)" % enc["que_es_el_requisito"],
                   semanas(enc["requisito_semanas"]))
    if enc["semanas_que_faltan"] is not None:
        # Decir "te faltan 0" es confuso. Si ya cumple, se dice que ya cumple.
        if enc["semanas_que_faltan"] <= 0:
            lienzo.renglon("Requisito de semanas", "ya lo cumples", negrita=True)
        else:
            lienzo.renglon("Te faltan", semanas(enc["semanas_que_faltan"]),
                           negrita=True)
    if enc["edad_legal"]:
        lienzo.renglon("Edad legal de pensión", "%s años" % enc["edad_legal"])

    # --- 2. Tu resultado ---
    res = datos["resultado"]
    lienzo.titulo_seccion("2. TU RESULTADO, SI SIGUES COMO HOY")
    fecha = fecha_larga(res.get("fecha_pension"))
    if fecha:
        lienzo.renglon("Fecha estimada de pensión", fecha, negrita=True)
    elif res.get("edad_pension"):
        lienzo.renglon("Te pensionarías a los", "%s años" % res["edad_pension"],
                       negrita=True)
    lienzo.renglon("Mesada estimada", banda_en_pesos(res.get("mesada_banda")),
                   tamano=10, negrita=True)
    if res.get("nota"):
        lienzo.parrafo(res["nota"])

    # --- 3. Tus alertas ---
    alertas = datos["alertas"]
    lienzo.titulo_seccion("3. TUS ALERTAS")
    if alertas["sin_alertas"]:
        lienzo.parrafo("Tu historia laboral no muestra huecos ni moras. Es poco "
                       "común, y es una buena noticia.", color=(0, 0, 0))
    else:
        for alerta in alertas["lista"]:
            lienzo.renglon(alerta["titulo"], alerta["cifra"], negrita=True)
            lienzo.parrafo(alerta["detalle"], sangria=10)
        if alertas.get("semanas_perdidas_total"):
            lienzo.renglon("Total de semanas perdidas",
                           semanas(alertas["semanas_perdidas_total"]),
                           tamano=9.5, negrita=True)

    # --- 4. Tus palancas ---
    lienzo.titulo_seccion("4. TUS PALANCAS")
    if datos["palancas"]["sin_palancas"]:
        lienzo.parrafo("No se identificaron palancas cuantificables con este "
                       "documento.", color=(0, 0, 0))
    for palanca in datos["palancas"]["lista"]:
        lienzo.renglon(palanca["que"], palanca.get("gana"), negrita=False)
        if palanca.get("salvedad"):
            lienzo.parrafo(palanca["salvedad"], sangria=10)

    # --- 5. Tus escenarios ---
    lienzo.titulo_seccion("5. TUS ESCENARIOS")
    for escenario in datos["escenarios"]["lista"]:
        lienzo.renglon(escenario["titulo"],
                       banda_en_pesos(escenario.get("mesada_banda")),
                       tamano=9.5, negrita=True)
        detalle = []
        if fecha_larga(escenario.get("fecha_pension")):
            detalle.append("te pensionarías en %s"
                           % fecha_larga(escenario["fecha_pension"]))
        if escenario.get("salida_del_sistema"):
            detalle.append("salida: %s"
                           % escenario["salida_del_sistema"].replace("_", " "))
        if detalle:
            lienzo.parrafo(", ".join(detalle), sangria=10)

    # --- 6. Tus siguientes pasos ---
    lienzo.titulo_seccion("6. TUS SIGUIENTES PASOS")
    for numero, paso in enumerate(datos["siguientes_pasos"], start=1):
        for indice, linea in enumerate(partir(paso, 8.5, ANCHO_UTIL - 22)):
            prefijo = "%d. " % numero if indice == 0 else "   "
            lienzo.pagina.texto(MARGEN + 8, lienzo.y, prefijo + linea, tamano=8.5)
            lienzo.bajar(10.5)

    # --- 7. Supuestos y limites ---
    lienzo.titulo_seccion("7. SUPUESTOS Y LÍMITES")
    for linea in datos["supuestos"]["supuestos"] + datos["supuestos"]["limites"]:
        lienzo.parrafo("- " + linea, tamano=7.5)

    # Pie de pagina.
    lienzo.pagina.linea(MARGEN, 40, 612 - MARGEN, 40, grosor=0.5, color=GRIS)
    lienzo.pagina.texto(MARGEN, 30,
                        "Júbilo. Diagnóstico preliminar, no es una liquidación "
                        "certificada. Las cifras las calcula un programa, no una "
                        "inteligencia artificial.", tamano=7, color=GRIS)
    return lienzo.pagina.guardar(ruta)


def armar(diagnostico, nombre, fondo, ruta):
    """Saca los datos del diagnostico y escribe el PDF. Devuelve los dos."""
    datos = datos_del_reporte(diagnostico, nombre, fondo)
    escribir_pdf(datos, ruta)
    return datos, ruta


def main():
    if len(sys.argv) < 5:
        print("Uso: python3 reporte/armar_reporte.py <diagnostico.json> "
              "<nombre> <fondo> <salida.pdf>")
        sys.exit(1)
    diagnostico = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    _, ruta = armar(diagnostico, sys.argv[2], sys.argv[3], sys.argv[4])
    print(json.dumps({"ok": True, "archivo": str(ruta)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
