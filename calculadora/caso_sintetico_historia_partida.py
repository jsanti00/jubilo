# Caso sintético de historia partida: la misma persona en dos administradoras.
#
# Por qué es sintético y no del set dorado: el set dorado (casos/) son
# documentos reales y ninguno de ellos viene partido en dos. Este caso existe
# para probar el único escenario que no se puede probar con datos reales todavía,
# y vive DENTRO de calculadora/ justamente para no contaminar el set dorado.
#
# Está escrito en Python y no en JSON a propósito: así los números quedan con su
# cuenta al lado y Santiago puede auditar de dónde sale cada semana sin rehacer
# la aritmética. Corriéndolo (`python3 caso_sintetico_historia_partida.py`)
# imprime los dos documentos en JSON, por si se quieren probar desde la terminal.
#
# LA CUENTA QUE ESTE CASO FIJA (la trampa que buscamos):
#
#   Documento A, Colpensiones:  2013-01 a 2018-03 = 63 meses x 30 días = 1.890 días = 270,00 semanas
#   Documento B, Porvenir:      2017-04 a 2020-09 = 42 meses x 30 días = 1.260 días = 180,00 semanas
#   Suma ingenua                                                       = 450,00 semanas
#   Meses que aparecen en LOS DOS: 2017-04 a 2018-03 = 12 meses = 360 días = 51,43 semanas
#   Total correcto: (1.890 + 1.260 - 360) / 7 = 2.790 / 7             = 398,57 semanas
#
# Sumar los dos totales impresos regalaría 51,43 semanas que la persona no tiene.
# Son más de un año de cotización: en alguien cerca del requisito, ese error
# cambia el veredicto del producto, no solo la cifra.
#
# Por qué el traslape es realista: cuando alguien se traslada, el fondo nuevo
# empieza a reportar antes de que el reporte del anterior deje de hacerlo, y el
# mismo empleador queda en los dos documentos durante la transición.

import json

# Datos de la persona. Los mismos en los dos documentos: si no coincidieran,
# la consolidación lo denuncia en vez de fundir a dos personas distintas.
FECHA_NACIMIENTO = "1970-06-15"
SEXO = "M"

# El empleador compartido, el que produce el traslape
ALFA = {"empleador": "ALFA SAS", "nit": "900111222"}
BETA = {"empleador": "BETA SAS", "nit": "900333444"}


def _fila_mensual(mes, empleador, ibc, dias=30):
    """Arma una fila mensual con el formato de los fondos privados."""
    anio, num = int(mes[:4]), int(mes[5:7])
    ultimo = [31, 29 if anio % 4 == 0 and (anio % 100 != 0 or anio % 400 == 0)
              else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][num - 1]
    return {
        "desde": f"{mes}-01",
        "hasta": f"{mes}-{ultimo:02d}",
        "empleador": empleador["empleador"],
        "nit": empleador["nit"],
        "tipo_cotizante": "empleado",
        "ibc": ibc,
        "ibc_tipo": "mensual",
        "cotizacion": None,
        "dias_cotizados": dias,
        "semanas": None,
        "semanas_lic": None,
        "semanas_sim": None,
        "semanas_validas": None,
        "administradora": "Porvenir",
        "observacion": "normal",
    }


def _meses(desde, hasta):
    """Lista los meses 'AAAA-MM' entre dos meses, ambos incluidos."""
    anio, num = int(desde[:4]), int(desde[5:7])
    fin = (int(hasta[:4]), int(hasta[5:7]))
    salida = []
    while (anio, num) <= fin:
        salida.append(f"{anio}-{num:02d}")
        anio, num = (anio + 1, 1) if num == 12 else (anio, num + 1)
    return salida


def documento_colpensiones():
    """Documento A: reporte de semanas de Colpensiones (formato por rangos).

    Un solo tramo con el mismo empleador, que es como Colpensiones agrupa.
    270,00 semanas x 7 = 1.890 días, que es lo que dice el total impreso.
    """
    return {
        "caso_id": "sintetico-historia-partida-A-colpensiones",
        "documento": {
            "administradora_emisora": "Colpensiones",
            "regimen": "RPM",
            "formato": "colpensiones_reporte_semanas",
            "fecha_generacion": "2020-10-05",
        },
        "afiliado": {
            "fecha_nacimiento": FECHA_NACIMIENTO,
            "edad_en_documento": None,
            "sexo": SEXO,
            "fecha_afiliacion": "2013-01-15",
            # Ya no cotiza aquí: se trasladó. Este es el dato que decide el
            # régimen, y por eso el esquema lo pide.
            "estado_afiliacion": "inactivo",
        },
        "resumen_documento": {
            "total_semanas": 270.0,
            "total_dias": 1890,
            "saldo_cuenta_individual": None,
            "semanas_en_otros_fondos": None,
        },
        "periodos": [{
            "desde": "2013-01-01",
            "hasta": "2018-03-31",
            "empleador": ALFA["empleador"],
            "nit": ALFA["nit"],
            "tipo_cotizante": "empleado",
            "ibc": 4000000,
            "ibc_tipo": "ultimo_del_rango",
            "cotizacion": None,
            "dias_cotizados": None,
            "semanas": None,
            "semanas_lic": None,
            "semanas_sim": None,
            "semanas_validas": 270.0,
            "administradora": "Colpensiones",
            "observacion": "normal",
        }],
    }


def documento_porvenir():
    """Documento B: certificado mensual de un fondo privado.

    42 filas de 30 días. Las 12 primeras son del MISMO empleador del documento A
    y del mismo periodo: ese es el traslape que la consolidación debe descontar.
    """
    periodos = []
    for mes in _meses("2017-04", "2018-03"):
        periodos.append(_fila_mensual(mes, ALFA, 4000000))
    for mes in _meses("2018-04", "2020-09"):
        periodos.append(_fila_mensual(mes, BETA, 6000000))
    return {
        "caso_id": "sintetico-historia-partida-B-porvenir",
        "documento": {
            "administradora_emisora": "Porvenir",
            "regimen": "RAIS",
            "formato": "porvenir_certificado_mensual",
            "fecha_generacion": "2020-10-05",
        },
        "afiliado": {
            "fecha_nacimiento": FECHA_NACIMIENTO,
            "edad_en_documento": None,
            "sexo": SEXO,
            "fecha_afiliacion": "2017-04-01",
            # Aquí sí cotiza hoy: es el régimen que liquidaría la pensión
            "estado_afiliacion": "activo_cotizante",
        },
        "resumen_documento": {
            "total_semanas": 180.0,
            "total_dias": 1260,
            "saldo_cuenta_individual": 85000000,
            "semanas_en_otros_fondos": None,
        },
        "periodos": periodos,
    }


# Los números que la prueba verifica, escritos aquí para que estén al lado de
# la cuenta de arriba y no escondidos dentro del archivo de pruebas.
SEMANAS_DOCUMENTO_A = 270.0
SEMANAS_DOCUMENTO_B = 180.0
SUMA_INGENUA = 450.0
SEMANAS_TRASLAPADAS = 51.43          # 12 meses x 30 días / 7
SEMANAS_CONSOLIDADAS = 398.57        # 2.790 días / 7
MESES_COMPARTIDOS = _meses("2017-04", "2018-03")


def historias():
    """Los dos documentos, en el orden en que llegarían del usuario."""
    return [documento_colpensiones(), documento_porvenir()]


if __name__ == "__main__":
    for h in historias():
        print(json.dumps(h, ensure_ascii=False, indent=2))
