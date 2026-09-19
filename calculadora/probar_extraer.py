# Pruebas del detector de formato y de los parsers.
#
# DOS NIVELES, y el primero corre siempre:
#
#   Nivel A, sin documentos de nadie. Comprueba el detector y el comportamiento
#   ante lo inesperado con textos inventados aqui mismo. No toca ningun archivo
#   de una persona real, asi que funciona en cualquier maquina.
#
#   Nivel B, contra las muestras reales. Corre los parsers sobre los PDF de
#   verdad y compara el resultado, fila por fila, contra el set dorado de
#   `casos/`, que es la extraccion que hoy produce el modelo. Asi se comprueba
#   lo unico que importa: que el atajo no pierda ni deforme un solo dato.
#
# COMO SE PRENDE EL NIVEL B. Las muestras son historias laborales de personas
# reales y por eso no viven en este repositorio ni se nombran aqui. Hay que
# decirle donde estan con una variable de entorno:
#
#   JUBILO_MUESTRAS="/ruta/a/la/carpeta/con/los/pdf" python3 -B probar_extraer.py
#
# Sin esa variable, el nivel B se salta y lo dice. No falla: en el servidor y
# en una maquina prestada esas muestras no existen y eso no es un error.
#
# NADA DE DATOS PERSONALES EN LA SALIDA. Las pruebas nunca imprimen nombres de
# archivo, nombres de personas ni de empleadores. Los documentos se identifican
# por su formato y por el caso dorado con el que emparejan.

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import detectar_formato          # noqa: E402
import diagnosticar              # noqa: E402
import extraer                   # noqa: E402
import parsers_historia as ph    # noqa: E402

CASOS = Path(__file__).resolve().parent.parent / "casos"

fallos = []


def revisar(condicion, descripcion):
    """Anota el resultado de una comprobacion y lo muestra en pantalla."""
    if condicion:
        print(f"  ok   {descripcion}")
    else:
        print(f"  FALLA {descripcion}")
        fallos.append(descripcion)


# ---------------------------------------------------------------------------
# Nivel A.1: las ayudas de numeros y fechas
# ---------------------------------------------------------------------------

def probar_ayudas():
    print("\nAyudas de numeros y fechas")
    revisar(ph.numero_co("1.236,57") == 1236.57, "numero colombiano")
    revisar(ph.numero_us("1,000,000.00") == 1000000.0, "numero estadounidense")
    revisar(ph.fecha_dmy("11/05/1967") == "1967-05-11", "fecha con barras dia/mes/ano")
    revisar(ph.fecha_ymd("2023/08/04") == "2023-08-04", "fecha con barras ano/mes/dia")
    revisar(ph.fecha_en_letras("30", "junio", "2026") == "2026-06-30", "fecha con mes en letras")
    revisar(ph.fecha_en_letras("30", "brumario", "2026") is None, "mes inventado no pasa")
    revisar(ph.rango_del_mes(2024, 2) == ("2024-02-01", "2024-02-29"), "febrero bisiesto")
    revisar(ph.sexo_de("Masculino") == "M" and ph.sexo_de("Femenino") == "F",
            "sexo leido del documento")
    revisar(ph.sexo_de("") is None, "sin sexo en el documento queda vacio")


# ---------------------------------------------------------------------------
# Nivel A.2: el detector
# ---------------------------------------------------------------------------
# Los textos de abajo son inventados: llevan solo los rotulos de cada plantilla
# y ni un dato de nadie. Sirven para comprobar que el detector se fija en la
# estructura del documento y no en las cifras.

RELLENO = ("linea de relleno para que el documento tenga tamano suficiente. " * 12)

TEXTOS_FALSOS = {
    "colpensiones_reporte_semanas": (
        "COLPENSIONES Nit 900.336.004-7\n"
        "REPORTE DE SEMANAS COTIZADAS EN PENSIONES\n"
        "[1]Identificación Aportante [2]Nombre o Razón Social [3]Desde\n" + RELLENO),
    "colfondos_reporte_historia": (
        "Colfondos Pensiones y Cesantías S.A.\nReporte de historia laboral\n"
        "Semanas cotizadas al sistema general de pensiones 0.0\n" + RELLENO),
    "porvenir_historia_laboral": (
        "Resumen de tu Historia Laboral\nDetalle de tu Historia Laboral\n"
        "Saldo Total Acumulado | $ 0\nAdministradora de pensiones PORVENIR\n" + RELLENO),
    "historia_laboral_consolidada": (
        "Historia Laboral Consolidada\nDatos básicos del afiliado\n"
        "Historia Laboral Régimen de Ahorro Individual con Solidaridad\n" + RELLENO),
    "proteccion_extracto_trimestral": (
        "Extracto de Pensión Obligatoria\n"
        "Resumen de mi cuenta individual de ahorro pensional a lo largo de mi vida laboral\n"
        "Movimientos de mi cuenta de ahorro individual en el trimestre\n" + RELLENO),
}


def probar_detector():
    print("\nDetector de formato")
    for esperado, texto in TEXTOS_FALSOS.items():
        d = detectar_formato.detectar(texto)
        revisar(d["reconocido"] and d["formato"] == esperado,
                f"reconoce la plantilla {esperado}")

    # Un documento sin letras (PDF escaneado) no se adivina.
    d = detectar_formato.detectar("")
    revisar(not d["reconocido"] and d["motivo"] == "sin_capa_de_texto",
            "un PDF sin letras cae al camino del modelo")

    # Un texto largo que no es ninguna plantilla conocida tampoco.
    d = detectar_formato.detectar("contrato de arrendamiento. " * 40)
    revisar(not d["reconocido"] and d["motivo"] == "formato_desconocido",
            "un documento cualquiera cae al camino del modelo")

    # Una plantilla a la que le falta una sola senal NO se reconoce a medias.
    a_medias = TEXTOS_FALSOS["colpensiones_reporte_semanas"].replace(
        "REPORTE DE SEMANAS COTIZADAS EN PENSIONES", "")
    d = detectar_formato.detectar(a_medias)
    revisar(not d["reconocido"], "si falta una senal, no se reconoce")

    # Las tildes y los espacios de mas no pueden cambiar el resultado.
    con_ruido = TEXTOS_FALSOS["colfondos_reporte_historia"].replace(" ", "  ")
    con_ruido = con_ruido.replace("é", "e").replace("í", "i")
    d = detectar_formato.detectar(con_ruido)
    revisar(d["reconocido"] and d["formato"] == "colfondos_reporte_historia",
            "tildes y espacios de mas no despistan al detector")

    # La historia laboral de Proteccion se reconoce como conocida sin parser.
    d = detectar_formato.detectar(
        "Protección\nHistoria Laboral\nOrigen de la información\n" + RELLENO)
    revisar(d["motivo"] == "formato_conocido_sin_parser",
            "la historia laboral de Proteccion se identifica pero aun no se lee")

    # Cada plantilla tiene que reconocer SOLO la suya.
    cruces = 0
    for nombre, texto in TEXTOS_FALSOS.items():
        d = detectar_formato.detectar(texto)
        if d["formato"] != nombre:
            cruces += 1
    revisar(cruces == 0, "ninguna plantilla se confunde con otra")


# ---------------------------------------------------------------------------
# Nivel A.3: nunca falla duro
# ---------------------------------------------------------------------------

def probar_fallback(tmp):
    print("\nEl atajo nunca falla duro")

    r = extraer.extraer(tmp / "no-existe-este-archivo.pdf")
    revisar(r["estado"] == "fallback" and r["motivo"] == "no_existe",
            "un archivo que no existe devuelve fallback, no un error")

    basura = tmp / "basura.txt"
    basura.write_text("hola " * 200, encoding="utf-8")
    r = extraer.extraer(basura)
    revisar(r["estado"] == "fallback" and r["motivo"] == "formato_desconocido",
            "un texto cualquiera devuelve fallback")

    vacio = tmp / "vacio.txt"
    vacio.write_text("", encoding="utf-8")
    r = extraer.extraer(vacio)
    revisar(r["estado"] == "fallback" and r["motivo"] == "sin_capa_de_texto",
            "un archivo vacio devuelve fallback")

    # Plantilla reconocida pero sin tabla: es el caso del recorte de pantalla.
    mocho = tmp / "mocho.txt"
    mocho.write_text(TEXTOS_FALSOS["colpensiones_reporte_semanas"], encoding="utf-8")
    r = extraer.extraer(mocho)
    revisar(r["estado"] == "fallback" and r["motivo"] == "tabla_ilegible",
            "una plantilla conocida sin filas devuelve fallback")

    # Todas las respuestas traen el reloj, para poder medir la latencia.
    revisar(isinstance(r["latencia_ms"], float), "toda respuesta trae su latencia")


# ---------------------------------------------------------------------------
# Nivel B: contra las muestras reales y el set dorado
# ---------------------------------------------------------------------------
# El set dorado (`casos/*.json`) es la extraccion que hoy produce el pipeline
# con el modelo. Cada muestra se empareja con su caso dorado por el total de
# semanas impreso, que es unico entre los casos. Asi la prueba no necesita
# saber el nombre del archivo ni de la persona.

# Campos que se comparan uno a uno. `empleador` y `nit` NO estan: en el set
# dorado se reemplazaron por etiquetas (EMPLEADOR-01) y se anularon los NIT
# para publicarlos, asi que el texto no puede coincidir. Lo que si se compara
# es la AGRUPACION: que las filas que el dorado pone bajo el mismo empleador
# sean exactamente las que el parser tambien agrupa junto.
CAMPOS = ("desde", "hasta", "tipo_cotizante", "ibc", "ibc_tipo", "cotizacion",
          "dias_cotizados", "semanas", "semanas_lic", "semanas_sim",
          "semanas_validas", "administradora", "observacion")


def cargar_dorados():
    """Indexa el set dorado por su total de semanas impreso."""
    porTotal = {}
    for archivo in sorted(CASOS.glob("caso-*.json")):
        caso = json.loads(archivo.read_text(encoding="utf-8"))
        total = caso["resumen_documento"].get("total_semanas")
        if total is not None:
            porTotal[round(float(total), 2)] = caso
    return porTotal


def firma_de_agrupacion(periodos):
    """Convierte la lista de periodos en el patron de "quien va con quien".

    A cada empleador distinto se le da un numero segun el orden en que aparece
    por primera vez. Dos extracciones del mismo documento tienen que dar el
    mismo patron aunque los nombres esten cambiados por etiquetas.
    """
    numeros, patron = {}, []
    for p in periodos:
        clave = p.get("empleador")
        if clave not in numeros:
            numeros[clave] = len(numeros)
        patron.append(numeros[clave])
    return patron


def comparar_con_dorado(caso, dorado):
    """Compara campo a campo. Devuelve la lista de diferencias encontradas."""
    diferencias = []

    for llave in ("regimen", "formato", "administradora_emisora", "fecha_generacion"):
        mio = caso["documento"].get(llave)
        suyo = dorado["documento"].get(llave)
        if mio != suyo:
            diferencias.append(f"documento.{llave}: parser={mio!r} dorado={suyo!r}")

    for llave, suyo in dorado["afiliado"].items():
        mio = caso["afiliado"].get(llave)
        if mio != suyo:
            diferencias.append(f"afiliado.{llave}: parser={mio!r} dorado={suyo!r}")

    for llave in ("total_semanas", "total_dias", "saldo_cuenta_individual",
                  "semanas_en_otros_fondos"):
        mio = caso["resumen_documento"].get(llave)
        suyo = dorado["resumen_documento"].get(llave)
        if mio != suyo:
            diferencias.append(f"resumen.{llave}: parser={mio!r} dorado={suyo!r}")

    if len(caso["periodos"]) != len(dorado["periodos"]):
        diferencias.append(f"numero de periodos: parser={len(caso['periodos'])} "
                           f"dorado={len(dorado['periodos'])}")
        return diferencias

    for i, (mio, suyo) in enumerate(zip(caso["periodos"], dorado["periodos"]), start=1):
        for campo in CAMPOS:
            a, b = mio.get(campo), suyo.get(campo)
            # Un entero y un decimal con el mismo valor son el mismo dato.
            if isinstance(a, (int, float)) and isinstance(b, (int, float)):
                if abs(float(a) - float(b)) > 0.005:
                    diferencias.append(f"periodo {i}.{campo}: parser={a} dorado={b}")
            elif a != b:
                diferencias.append(f"periodo {i}.{campo}: parser={a!r} dorado={b!r}")

    if firma_de_agrupacion(caso["periodos"]) != firma_de_agrupacion(dorado["periodos"]):
        diferencias.append("la agrupacion por empleador no coincide con la del dorado")

    return diferencias


def probar_contra_muestras():
    carpeta = os.environ.get("JUBILO_MUESTRAS")
    print("\nMuestras reales contra el set dorado")
    if not carpeta or not Path(carpeta).is_dir():
        print("  SALTADA: no hay carpeta de muestras. Para correrla:")
        print("  JUBILO_MUESTRAS=/ruta/a/las/muestras python3 -B probar_extraer.py")
        return

    dorados = cargar_dorados()
    pdfs = sorted(Path(carpeta).rglob("*.pdf"))
    revisar(len(pdfs) > 0, "la carpeta de muestras trae documentos")

    emparejados = 0
    latencias = []
    for pdf in pdfs:
        resultado = extraer.extraer(pdf)
        latencias.append((resultado.get("formato"), resultado["latencia_ms"],
                          resultado["estado"]))
        caso = resultado.get("caso")
        if caso is None:
            # Sin tabla leida no hay nada que comparar. Lo unico exigible es
            # que haya caido al camino del modelo con un motivo claro.
            revisar(resultado["estado"] == "fallback" and resultado["motivo"],
                    f"documento sin lectura automatica: cae al modelo "
                    f"({resultado['motivo']})")
            continue

        total = caso["resumen_documento"].get("total_semanas")
        dorado = dorados.get(round(float(total), 2)) if total is not None else None
        if dorado is None:
            # Muestra sin caso dorado: se verifica contra el propio documento.
            revisar(resultado["estado"].startswith("extraido"),
                    f"{resultado['formato']}: sin caso dorado, cuadra contra su "
                    f"propio total impreso")
            continue

        # Lo extraido tiene que poder pasar por la calculadora completa, no
        # solo parecerse al dorado: si le falta un campo que la calculadora
        # exige, esto lo caza aqui y no en una conversacion real.
        if caso["documento"]["tipo_documento"] == "historia_laboral":
            try:
                diagnosticar.diagnosticar_historias([caso], sexo="M", edad=40)
                paso_la_calculadora = True
            except Exception as e:
                paso_la_calculadora = False
                print(f"        - {type(e).__name__}: {e}")
            revisar(paso_la_calculadora,
                    f"{resultado['formato']}: lo extraido pasa entero por la calculadora")

        emparejados += 1
        diferencias = comparar_con_dorado(caso, dorado)
        revisar(not diferencias,
                f"{dorado['caso_id']}: el parser saca lo mismo que el pipeline actual")
        for d in diferencias[:8]:
            print(f"        - {d}")

    revisar(emparejados >= 4, f"se compararon al menos 4 casos dorados ({emparejados})")

    print("\n  Latencia medida por documento (el camino con modelo tarda ~90 s):")
    for formato, ms, estado in latencias:
        print(f"    {str(formato or 'sin formato'):34} {ms:8.1f} ms   {estado}")
    solo_leidos = [ms for f, ms, e in latencias if e.startswith("extraido")]
    if solo_leidos:
        print(f"    peor caso de los leidos: {max(solo_leidos):.1f} ms")


def main():
    import tempfile
    print("Pruebas de extraccion automatica de documentos")
    probar_ayudas()
    probar_detector()
    with tempfile.TemporaryDirectory() as tmp:
        probar_fallback(Path(tmp))
    probar_contra_muestras()

    print()
    if fallos:
        print(f"RESULTADO: {len(fallos)} comprobaciones fallaron")
        sys.exit(1)
    print("RESULTADO: todas las comprobaciones pasaron")


if __name__ == "__main__":
    main()
