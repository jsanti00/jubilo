# Extrae la historia laboral de un documento sin pasar por el modelo.
#
# QUE HACE. Recibe la ruta de un PDF (o de un texto ya extraido), reconoce de
# que administradora viene y copia su tabla al JSON del esquema. Tarda menos de
# un segundo. Hasta ahora ese mismo trabajo lo hacia el modelo leyendo el
# documento, y tardaba cerca de minuto y medio.
#
# LA REGLA QUE MANDA: ESTO NUNCA FALLA DURO. Si el formato no se reconoce, si
# el PDF es una imagen sin letras, si la tabla no se deja leer o si las cifras
# no cuadran contra el total impreso, el programa no se cae: devuelve
# `estado: "fallback"` y un motivo. Eso significa "leelo tu, como siempre". El
# camino viejo sigue existiendo entero y este es solo un atajo para los
# documentos que ya sabemos leer.
#
# NO CALCULA NADA. Copia lo que el documento dice. Los numeros los sigue
# haciendo la calculadora, igual que antes.
#
# DATOS PERSONALES. El JSON que sale no lleva nombre, cedula, correo ni
# direccion, aunque el documento los traiga.
#
# Uso:
#   python3 extraer.py /ruta/historia.pdf
#   python3 extraer.py /ruta/historia.pdf --salida /ruta/extracciones/2026-07-21-porvenir.json
#
# Codigos de salida: 0 si se extrajo, 3 si hay que leerlo con el modelo.

import argparse
import json
import sys
import time
from pathlib import Path

# Se importan por ruta relativa al propio archivo para que funcione igual
# corriendolo desde cualquier carpeta.
sys.path.insert(0, str(Path(__file__).resolve().parent))

import detectar_formato          # noqa: E402
import diagnosticar              # noqa: E402
import extraccion_texto          # noqa: E402
import parsers_historia          # noqa: E402


def extraer(ruta):
    """Lee el documento y devuelve el resumen de lo que paso.

    Siempre devuelve un diccionario. Nunca lanza una excepcion hacia afuera:
    cualquier sorpresa se traduce en `estado: "fallback"`.
    """
    arranque = time.perf_counter()

    def respuesta(estado, motivo=None, **extra):
        salida = {"estado": estado, "motivo": motivo,
                  "latencia_ms": round((time.perf_counter() - arranque) * 1000, 1)}
        salida.update(extra)
        return salida

    ruta = Path(ruta)
    if not ruta.exists():
        return respuesta("fallback", "no_existe",
                         mensaje=f"No encuentro el archivo: {ruta}")

    # Paso 1: sacar el texto del documento.
    try:
        texto, fuente = extraccion_texto.texto_de(ruta)
    except Exception as e:
        return respuesta("fallback", "no_se_pudo_leer_el_archivo", mensaje=str(e))

    if not extraccion_texto.tiene_capa_de_texto(texto):
        return respuesta(
            "fallback", "sin_capa_de_texto", fuente_del_texto=fuente,
            mensaje=("El PDF no trae letras adentro, es una imagen. Hay que "
                     "leerlo mirandolo, como se hacia antes."))

    # Paso 2: reconocer la plantilla.
    deteccion = detectar_formato.detectar(texto)
    if not deteccion["reconocido"]:
        return respuesta("fallback", deteccion["motivo"],
                         formato=deteccion["formato"], fuente_del_texto=fuente,
                         mensaje=("No reconozco esta plantilla. Hay que leer el "
                                  "documento como siempre."))

    # Paso 3: leer la tabla con el parser que corresponde.
    parser = parsers_historia.PARSERS.get(deteccion["formato"])
    if parser is None:
        return respuesta("fallback", "formato_conocido_sin_parser",
                         formato=deteccion["formato"], fuente_del_texto=fuente)
    try:
        caso = parser(texto)
    except parsers_historia.NoSePudoLeer as e:
        return respuesta("fallback", "tabla_ilegible",
                         formato=deteccion["formato"], mensaje=str(e))
    except Exception as e:
        # Un error inesperado tampoco tumba nada: se va al camino viejo.
        return respuesta("fallback", "error_inesperado",
                         formato=deteccion["formato"],
                         mensaje=f"{type(e).__name__}: {e}")

    comun = {"formato": deteccion["formato"],
             "emisora": caso["documento"]["administradora_emisora"],
             "tipo_documento": caso["documento"]["tipo_documento"],
             "fuente_del_texto": fuente,
             "periodos": len(caso["periodos"]),
             "caso": caso}

    # Un extracto de cuenta no se verifica contra el total de semanas: sus
    # periodos son solo los del trimestre y nunca van a sumar el total.
    if caso["documento"]["tipo_documento"] != "historia_laboral":
        return respuesta("extraido_parcial", "solo_extracto_de_cuenta",
                         verificacion=None,
                         mensaje=("Es un extracto de cuenta, no una historia "
                                  "laboral: sirve para el saldo y el total de "
                                  "semanas, no para el detalle de periodos."),
                         **comun)

    # Paso 4: la verificacion cruzada de siempre, contra el total impreso.
    # Es la misma que usa el camino del modelo, asi que un atajo no relaja el
    # control de calidad: lo aplica igual.
    try:
        verificacion = diagnosticar.verificar(caso)
    except Exception as e:
        return respuesta("fallback", "no_se_pudo_verificar",
                         mensaje=f"{type(e).__name__}: {e}", **comun)

    if not verificacion["cuadra"]:
        # Lo leido no cuadra con lo que el documento dice de si mismo. Puede
        # ser un error del parser o una contradiccion del documento. En los dos
        # casos decide el modelo, que no se entrega nada dudoso (regla dura 4).
        return respuesta("fallback", "no_cuadra_con_el_total_impreso",
                         verificacion=verificacion, **comun)

    return respuesta("extraido", None, verificacion=verificacion, **comun)


def main():
    parser = argparse.ArgumentParser(
        description="Lee una historia laboral sin usar el modelo.")
    parser.add_argument("ruta", help="PDF de la historia laboral (o .txt/.md ya extraido)")
    parser.add_argument("--salida", help="donde escribir el JSON extraido")
    parser.add_argument("--caso-id", help="etiqueta opcional para el JSON")
    args = parser.parse_args()

    resultado = extraer(args.ruta)

    if resultado["estado"].startswith("extraido") and args.salida:
        caso = dict(resultado["caso"])
        if args.caso_id:
            # Se puede poner otra etiqueta, y va de primera como en el dorado.
            caso = {"caso_id": args.caso_id, **caso}
        destino = Path(args.salida)
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(json.dumps(caso, ensure_ascii=False, indent=1),
                           encoding="utf-8")
        resultado["archivo"] = str(destino)

    # En pantalla va el resumen sin el caso completo, que puede ser largo.
    resumen = {k: v for k, v in resultado.items() if k != "caso"}
    print(json.dumps(resumen, ensure_ascii=False, indent=2))
    sys.exit(0 if resultado["estado"].startswith("extraido") else 3)


if __name__ == "__main__":
    main()
