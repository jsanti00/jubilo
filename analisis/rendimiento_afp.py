"""
Rentabilidad nominal y real de los fondos de pensiones obligatorias de Colombia.

Que hace, en palabras simples:
1. Baja de datos.gov.co (dataset hds9-4524, de la Superintendencia Financiera) el valor
   total de cada fondo y cuantas "unidades" tiene, dia por dia.
2. Divide valor entre unidades. Eso da el "valor de la unidad", que es como el precio de
   una accion del fondo: si sube, el afiliado gano plata.
3. Baja el IPC de Colombia (el indice de precios que mide la inflacion) del Banco de la
   Republica, que lo publica con fuente DANE.
4. Calcula cuanto rindio cada fondo por año, en nominal y descontando la inflacion.

Como correrlo:
    python3 rendimiento_afp.py

Todo queda en la carpeta que indica CARPETA_DATOS (cache de los crudos) y el resultado
se imprime en pantalla como tabla de Markdown, lista para pegar en el reporte.
"""

import csv
import datetime as dt
import json
import os
import ssl
import urllib.parse
import urllib.request

# ---------------------------------------------------------------------------
# Configuracion
# ---------------------------------------------------------------------------

# Aqui se guardan los archivos crudos que bajamos, para no volver a bajarlos cada vez.
CARPETA_DATOS = os.environ.get("AFP_DATOS", "/tmp/afp_datos")

# El dataset de la Superfinanciera con la valoracion diaria de los fondos.
URL_SFC = "https://www.datos.gov.co/resource/hds9-4524.json"

# El servicio del Banco de la Republica que devuelve la serie mensual del IPC.
URL_IPC = (
    "https://suameca.banrep.gov.co/estadisticas-economicas-back/rest/"
    "estadisticaEconomicaRestService/consultaMenuXId?idMenu=100002"
)

# Renglon 300 = "valor del fondo al cierre del dia". Es el que usamos.
# (El renglon 305 es una variante del mismo cierre y da practicamente lo mismo.)
RENGLON = "300"

# Cuantos dias tiene un año en promedio, contando los bisiestos. Sirve para anualizar.
DIAS_ANIO = 365.25


# ---------------------------------------------------------------------------
# Paso 1: bajar el crudo de la Superfinanciera
# ---------------------------------------------------------------------------

def bajar_sfc(ruta_csv):
    """Baja valor del fondo y numero de unidades de todos los fondos de pensiones."""
    # Pedimos solo lo que necesitamos y excluimos cesantias, que no son pensiones.
    condicion = (
        "nombre_tipo_patrimonio != 'FONDO DE CESANTIA' "
        "AND cod_renglon = '%s'" % RENGLON
    )
    filas = []
    salto = 0
    while True:
        # La API entrega maximo 50.000 filas por llamada, asi que vamos por tandas.
        consulta = {
            "$select": "fecha_corte,nombre_entidad,nombre_patrimonio,"
                       "nombre_subtipo_patrimonio,nombre_columna,sum_valor",
            "$where": condicion,
            "$order": "fecha_corte,nombre_entidad,nombre_patrimonio,nombre_columna",
            "$limit": "50000",
            "$offset": str(salto),
        }
        url = URL_SFC + "?" + urllib.parse.urlencode(consulta)
        with urllib.request.urlopen(url, timeout=300) as respuesta:
            tanda = json.load(respuesta)
        if not tanda:
            break
        filas.extend(tanda)
        print("  bajadas %d filas" % len(filas))
        salto += 50000

    columnas = ["fecha_corte", "nombre_entidad", "nombre_patrimonio",
                "nombre_subtipo_patrimonio", "nombre_columna", "sum_valor"]
    with open(ruta_csv, "w", newline="") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=columnas)
        escritor.writeheader()
        for fila in filas:
            escritor.writerow({c: fila.get(c, "") for c in columnas})
    return ruta_csv


# ---------------------------------------------------------------------------
# Paso 2: bajar el IPC
# ---------------------------------------------------------------------------

def bajar_ipc(ruta_json):
    """Baja la serie mensual del IPC (indice, base diciembre 2018 = 100)."""
    peticion = urllib.request.Request(
        URL_IPC,
        # El servidor exige este encabezado para responder.
        headers={"Referer": "https://suameca.banrep.gov.co/estadisticas-economicas/"},
    )
    # El certificado de este servidor viene incompleto, asi que no lo verificamos.
    contexto = ssl._create_unverified_context()
    with urllib.request.urlopen(peticion, timeout=180, context=contexto) as respuesta:
        contenido = respuesta.read()
    with open(ruta_json, "wb") as archivo:
        archivo.write(contenido)
    return ruta_json


def leer_ipc(ruta_json):
    """Devuelve un diccionario {'2026-08': 160.42, ...} con el indice de cada mes."""
    datos = json.load(open(ruta_json))
    serie = datos["SERIES"][0]["data"]
    indice = {}
    for marca_tiempo, valor in serie:
        # Las fechas vienen como milisegundos desde 1970 y apuntan al cierre del mes.
        fecha = dt.datetime(1970, 1, 1) + dt.timedelta(milliseconds=marca_tiempo)
        indice["%04d-%02d" % (fecha.year, fecha.month)] = float(valor)
    return indice


# ---------------------------------------------------------------------------
# Paso 3: armar el valor de la unidad de cada fondo
# ---------------------------------------------------------------------------

def valor_unidad(ruta_csv):
    """
    Lee el crudo y devuelve {(entidad, fondo): {fecha: valor_unidad}}.

    El valor de la unidad es el valor total del fondo dividido por el numero de
    unidades. El dataset no publica ese precio directamente, asi que lo derivamos.
    """
    acumulado = {}
    with open(ruta_csv) as archivo:
        for fila in csv.DictReader(archivo):
            clave = (limpiar_entidad(fila["nombre_entidad"]),
                     fila["nombre_patrimonio"].strip())
            fecha = fila["fecha_corte"][:10]
            try:
                valor = float(fila["sum_valor"])
            except (TypeError, ValueError):
                continue
            casilla = acumulado.setdefault(clave, {}).setdefault(fecha, {})
            if fila["nombre_columna"] == "VALOR EN PESOS $":
                casilla["pesos"] = valor
            elif fila["nombre_columna"] == "NUMERO DE UNIDADES":
                casilla["unidades"] = valor

    resultado = {}
    for clave, por_fecha in acumulado.items():
        serie = {}
        for fecha, casilla in por_fecha.items():
            pesos = casilla.get("pesos")
            unidades = casilla.get("unidades")
            # Si falta un dato o las unidades son cero, no se puede calcular el precio.
            if pesos and unidades and unidades > 0:
                serie[fecha] = pesos / unidades
        if serie:
            resultado[clave] = serie
    return resultado


def limpiar_entidad(texto):
    """Deja el nombre de la AFP legible: '"Porvenir"' pasa a 'Porvenir'."""
    nombre = texto.replace('"', "").strip()
    if nombre.lower().startswith("colfondos"):
        return "Colfondos"
    if nombre.lower().startswith("porvenir"):
        return "Porvenir"
    if nombre.lower().startswith("proteccion"):
        return "Proteccion"
    if nombre.lower().startswith("skandia"):
        return "Skandia"
    return nombre


def cierres_de_mes(serie):
    """
    De una serie diaria deja solo el ultimo dia disponible de cada mes.

    Trabajamos con cierres de mes porque el IPC es mensual: asi la rentabilidad
    nominal y la real cubren exactamente el mismo periodo.
    """
    ultimo_por_mes = {}
    for fecha, valor in serie.items():
        mes = fecha[:7]
        if mes not in ultimo_por_mes or fecha > ultimo_por_mes[mes][0]:
            ultimo_por_mes[mes] = (fecha, valor)
    return ultimo_por_mes


# ---------------------------------------------------------------------------
# Paso 4: calcular rentabilidades
# ---------------------------------------------------------------------------

def anualizar(valor_inicial, valor_final, fecha_inicial, fecha_final):
    """Rentabilidad anual compuesta (geometrica) entre dos fechas."""
    dias = (dt.date.fromisoformat(fecha_final) - dt.date.fromisoformat(fecha_inicial)).days
    if dias <= 0 or valor_inicial <= 0:
        return None
    return (valor_final / valor_inicial) ** (DIAS_ANIO / dias) - 1


def a_real(nominal, ipc_inicial, ipc_final, fecha_inicial, fecha_final):
    """
    Pasa una rentabilidad nominal a real con la formula de Fisher.

    Primero anualizamos la inflacion del mismo periodo y luego aplicamos
    (1 + nominal) / (1 + inflacion) - 1.
    """
    if nominal is None or not ipc_inicial or not ipc_final:
        return None, None
    inflacion = anualizar(ipc_inicial, ipc_final, fecha_inicial, fecha_final)
    if inflacion is None:
        return None, None
    return (1 + nominal) / (1 + inflacion) - 1, inflacion


def calcular(series, ipc):
    """Para cada fondo calcula rentabilidad de todo el periodo y de los ultimos 5 años."""
    # Solo podemos llegar hasta el ultimo mes con IPC publicado.
    ultimo_mes_ipc = max(ipc)
    resultados = []

    for (entidad, fondo), serie_diaria in sorted(series.items()):
        mensual = cierres_de_mes(serie_diaria)
        meses = sorted(m for m in mensual if m <= ultimo_mes_ipc)
        if len(meses) < 13:
            continue

        mes_ini, mes_fin = meses[0], meses[-1]
        fecha_ini, valor_ini = mensual[mes_ini]
        fecha_fin, valor_fin = mensual[mes_fin]

        # Para los 5 años buscamos el cierre de mes que este 60 meses antes del final.
        mes_5a = meses[-61] if len(meses) >= 61 else None

        nominal_total = anualizar(valor_ini, valor_fin, fecha_ini, fecha_fin)
        real_total, infl_total = a_real(nominal_total, ipc.get(mes_ini), ipc.get(mes_fin),
                                        fecha_ini, fecha_fin)

        nominal_5a = real_5a = infl_5a = None
        if mes_5a:
            fecha_5a, valor_5a = mensual[mes_5a]
            nominal_5a = anualizar(valor_5a, valor_fin, fecha_5a, fecha_fin)
            real_5a, infl_5a = a_real(nominal_5a, ipc.get(mes_5a), ipc.get(mes_fin),
                                      fecha_5a, fecha_fin)

        resultados.append({
            "entidad": entidad,
            "fondo": fondo,
            "fecha_ini": fecha_ini,
            "fecha_fin": fecha_fin,
            "obs": len(meses),
            "nominal_total": nominal_total,
            "real_total": real_total,
            "inflacion_total": infl_total,
            "nominal_5a": nominal_5a,
            "real_5a": real_5a,
            "inflacion_5a": infl_5a,
            "unidad_ini": valor_ini,
            "unidad_fin": valor_fin,
        })
    return resultados


# ---------------------------------------------------------------------------
# Paso 5: imprimir
# ---------------------------------------------------------------------------

def porcentaje(valor):
    """Convierte 0.0912 en '9,12%'. Si no hay dato, lo dice."""
    if valor is None:
        return "sin dato"
    return ("%.2f%%" % (valor * 100)).replace(".", ",")


def imprimir(resultados):
    print("| AFP | Portafolio | Nominal periodo completo | Real periodo completo | "
          "Nominal 5 años | Real 5 años | Desde | Hasta | Obs. mensuales |")
    print("|---|---|---|---|---|---|---|---|---|")
    for r in resultados:
        print("| %s | %s | %s | %s | %s | %s | %s | %s | %d |" % (
            r["entidad"], r["fondo"],
            porcentaje(r["nominal_total"]), porcentaje(r["real_total"]),
            porcentaje(r["nominal_5a"]), porcentaje(r["real_5a"]),
            r["fecha_ini"], r["fecha_fin"], r["obs"]))


def main():
    os.makedirs(CARPETA_DATOS, exist_ok=True)
    ruta_csv = os.path.join(CARPETA_DATOS, "crudo.csv")
    ruta_ipc = os.path.join(CARPETA_DATOS, "ipc.json")

    if not os.path.exists(ruta_csv):
        print("Bajando datos de la Superfinanciera...")
        bajar_sfc(ruta_csv)
    if not os.path.exists(ruta_ipc):
        print("Bajando IPC del Banco de la Republica...")
        bajar_ipc(ruta_ipc)

    ipc = leer_ipc(ruta_ipc)
    series = valor_unidad(ruta_csv)
    resultados = calcular(series, ipc)

    print("\nIPC usado: indice mensual de Colombia, base diciembre 2018 = 100.")
    print("Ultimo mes de IPC disponible: %s (indice %.2f)\n"
          % (max(ipc), ipc[max(ipc)]))
    imprimir(resultados)

    # Guardamos tambien el resultado en JSON, por si se quiere reusar.
    with open(os.path.join(CARPETA_DATOS, "resultados.json"), "w") as archivo:
        json.dump(resultados, archivo, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
