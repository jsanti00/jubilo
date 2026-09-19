# -*- coding: utf-8 -*-
"""
Baja la serie mensual del IPC de Colombia y la deja en un CSV listo para usar.

Que hace, en orden:
  1. Le pide la serie al Banco de la Republica (portal SUAMECA, fuente original DANE).
  2. Comprueba que venga completa y ya empalmada en una sola base (dic-2018 = 100).
  3. Escribe 'ipc-colombia-mensual.csv' con el indice y la variacion anual de cada mes.

Se corre a mano desde el Mac cuando haya que refrescar la serie:

    python3 fuentes-datos/descargar_ipc.py

No lo ejecuta el agente en conversacion: es un script de mantenimiento.
"""

import csv
import datetime as dt
import json
import os
import ssl
import urllib.request


# Direccion del servicio del Banco de la Republica que devuelve la serie.
# El 100002 es el identificador del IPC dentro de su catalogo de series.
URL_IPC = (
    "https://suameca.banrep.gov.co/estadisticas-economicas-back/rest/"
    "estadisticaEconomicaRestService/consultaMenuXId?idMenu=100002"
)

# Carpeta donde vive este archivo. Todo lo que se escribe queda aqui al lado.
CARPETA = os.path.dirname(os.path.abspath(__file__))

# Los dos archivos que produce el script.
RUTA_CRUDO = os.path.join(CARPETA, "ipc-colombia-crudo.json")
RUTA_CSV = os.path.join(CARPETA, "ipc-colombia-mensual.csv")

# Los meses en que el DANE cambio de base. Los usamos solo para revisar que la
# serie no tenga un salto raro justo ahi, senal de que no estaria empalmada.
CAMBIOS_DE_BASE = ["1954-07", "1978-12", "1988-12", "1998-12", "2008-12", "2018-12"]


def bajar(ruta_json=RUTA_CRUDO):
    """Descarga la serie tal cual la entrega el Banco y la guarda en disco."""
    peticion = urllib.request.Request(
        URL_IPC,
        # Sin este encabezado el servidor no responde.
        headers={"Referer": "https://suameca.banrep.gov.co/estadisticas-economicas/"},
    )
    # El certificado de seguridad de este servidor viene incompleto (le falta un
    # eslabon de la cadena), asi que pedimos a Python que no lo valide.
    contexto = ssl._create_unverified_context()
    with urllib.request.urlopen(peticion, timeout=180, context=contexto) as respuesta:
        contenido = respuesta.read()
    with open(ruta_json, "wb") as archivo:
        archivo.write(contenido)
    return ruta_json


def leer(ruta_json=RUTA_CRUDO):
    """Convierte el JSON descargado en una lista ordenada de (mes, indice)."""
    datos = json.load(open(ruta_json))
    bruto = datos["SERIES"][0]["data"]
    serie = []
    for marca_tiempo, valor in bruto:
        # Las fechas llegan como milisegundos desde 1970 y apuntan al ultimo dia del mes.
        fecha = dt.datetime(1970, 1, 1) + dt.timedelta(milliseconds=marca_tiempo)
        serie.append(("%04d-%02d" % (fecha.year, fecha.month), float(valor)))
    serie.sort()
    return serie


def revisar(serie):
    """
    Comprueba tres cosas y devuelve la lista de avisos encontrados.

    1. Que no falte ningun mes entre el primero y el ultimo.
    2. Que el valor de diciembre de 2018 sea exactamente 100 (esa es la base).
    3. Que en los meses de cambio de base no haya un salto anormal, que seria la
       senal de que la serie viene en tramos sin unificar en vez de empalmada.
    """
    avisos = []

    # 1. Meses seguidos, sin huecos. Convertimos cada mes a un numero corrido.
    def numero_de_mes(texto):
        anio, mes = texto.split("-")
        return int(anio) * 12 + int(mes)

    for i in range(1, len(serie)):
        if numero_de_mes(serie[i][0]) - numero_de_mes(serie[i - 1][0]) != 1:
            avisos.append("Falta al menos un mes entre %s y %s" % (serie[i - 1][0], serie[i][0]))

    indice = dict(serie)

    # 2. La base declarada por el Banco es diciembre de 2018 = 100.
    if indice.get("2018-12") != 100.0:
        avisos.append("Diciembre de 2018 no vale 100, vale %s" % indice.get("2018-12"))

    # 3. En un cambio de base sin empalmar el indice se reinicia (cae a 100 o a 1).
    #    Si el mes siguiente al quiebre sigue la tendencia, la serie si esta empalmada.
    for mes in CAMBIOS_DE_BASE:
        anio, numero = int(mes[:4]), int(mes[5:])
        siguiente = "%04d-%02d" % (anio + (numero == 12), 1 if numero == 12 else numero + 1)
        antes, despues = indice.get(mes), indice.get(siguiente)
        if antes and despues:
            cambio = despues / antes - 1
            # Un mes normal en Colombia se mueve menos de 5%. Mas que eso en un
            # quiebre de base es sospechoso.
            if abs(cambio) > 0.05:
                avisos.append(
                    "Salto de %.1f%% entre %s y %s, revisar el empalme" % (cambio * 100, mes, siguiente)
                )
    return avisos


def rebasear(serie, mes_base):
    """
    Devuelve la misma serie expresada en otra base (el mes elegido vale 100).

    No hace falta para usar la serie, pero sirve si algun dia la calculadora
    prefiere trabajar con otro ano de referencia.
    """
    indice = dict(serie)
    referencia = indice[mes_base]
    return [(mes, valor / referencia * 100) for mes, valor in serie]


def escribir_csv(serie, ruta=RUTA_CSV):
    """Guarda la serie en un CSV con el indice y la inflacion de los ultimos 12 meses."""
    indice = dict(serie)
    with open(ruta, "w", newline="") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(["mes", "indice_base_dic2018", "variacion_anual_pct"])
        for mes, valor in serie:
            # El mismo mes del ano anterior, para calcular la inflacion anual.
            anio_anterior = "%04d-%s" % (int(mes[:4]) - 1, mes[5:])
            previo = indice.get(anio_anterior)
            variacion = round((valor / previo - 1) * 100, 2) if previo else ""
            escritor.writerow([mes, valor, variacion])
    return ruta


def main():
    print("Bajando la serie del Banco de la Republica...")
    bajar()
    serie = leer()
    print("Meses recibidos: %d, desde %s hasta %s" % (len(serie), serie[0][0], serie[-1][0]))

    avisos = revisar(serie)
    if avisos:
        print("AVISOS:")
        for aviso in avisos:
            print("  - " + aviso)
    else:
        print("Revision OK: serie completa, base dic-2018 = 100 y sin saltos en los cambios de base.")

    escribir_csv(serie)
    print("Escrito: " + RUTA_CSV)


if __name__ == "__main__":
    main()
