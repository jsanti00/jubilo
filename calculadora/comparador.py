# Comparador de regímenes: corre el MISMO caso por los dos módulos (RPM y RAIS)
# con supuestos equivalentes. Es el corazón de la asesoría de traslados
# (ver kit-contexto/reglas-traslados.md): no da veredictos secos, produce las
# dos mesadas estimadas para conversar con números.

from datetime import date

from datos_sistema import (
    SMLMV, EDAD_PENSION, APORTE_A_CUENTA_RAIS, RENDIMIENTO_REAL, factor_ipc,
)
import rpm
import rais


# Edad desde la que el traslado queda prohibido por ley:
# 10 años antes de la edad de pensión (Ley 797/2003 art. 2 lit. e)
EDAD_CIERRE_VENTANA = {"F": 47, "M": 52}


def simular_saldo_rais(periodos, anio_hoy):
    """Estima el saldo que tendría en RAIS alguien que cotizó en Colpensiones.

    Recorre su historia real: cada mes habría entrado el 11,5% del salario a
    una cuenta individual, y ese aporte habría rendido hasta hoy (perfil
    moderado, en términos reales). Aproximación de laboratorio, siempre
    marcada como simulación; ignora el bono pensional y las comisiones
    variables de cada época.
    """
    rendimiento = RENDIMIENTO_REAL["moderado"]
    meses = rpm.expandir_a_meses(periodos)
    saldo = 0.0
    for (anio, mes), registro in meses.items():
        if registro["dias"] == 0 or registro["ibc"] == 0:
            continue
        # El aporte de ese mes: 11,5% del salario, proporcional a los días
        aporte = registro["ibc"] * (registro["dias"] / 30) * APORTE_A_CUENTA_RAIS
        # Lo traemos a pesos de hoy (inflación)...
        factor = factor_ipc(anio, anio_hoy)
        if factor is None:
            continue  # Año sin IPC en la serie: se omite (estimación de piso)
        # ...y le sumamos lo que habría rendido por encima de la inflación
        anios_rindiendo = anio_hoy - anio
        saldo += aporte * factor * (1 + rendimiento) ** anios_rindiendo
    return round(saldo)


# Perfil de fondo con el que se compara contra Colpensiones. Es el único que
# existe en los dos lados de la comparación, y la misma convención que usa
# recuperacion.py. Se declara en la salida, no se asume en silencio.
PERFIL_COMPARABLE = "moderado"


def comparar_mesadas(diag_rpm, diag_rais):
    """Pone la mesada del RPM (un punto) frente a la del RAIS (una banda).

    Por qué esto no es cosmético: hasta ahora la comparación se leía contra
    `escenarios[perfil]["mesada"]`, que es el extremo OPTIMISTA de la banda del
    factor. Un traslado decidido con ese borde puede voltearse con el extremo
    conservador, y el usuario nunca se enteraba. Aquí el veredicto se evalúa en
    los DOS extremos y, cuando no coinciden, se dice que no hay veredicto.

    Recordatorio de por qué los dos lados no son simétricos: en el RPM la
    fórmula es determinista y entrega un punto (excepción 1 bis del
    system-prompt); en el RAIS el rango refleja incertidumbre real del modelo.
    """
    sigue = (diag_rpm or {}).get("escenario_sigue_cotizando") or {}
    mesada_rpm = sigue.get("mesada")
    escenario = ((diag_rais or {}).get("escenarios") or {}).get(PERFIL_COMPARABLE) or {}
    banda = escenario.get("mesada_banda")

    lectura = {
        "perfil_comparado": PERFIL_COMPARABLE,
        "nota_perfil": ("se compara contra el perfil moderado del fondo privado, "
                        "que es el único que existe en los dos lados. Los otros "
                        "perfiles están en el diagnóstico RAIS"),
        "mesada_rpm": mesada_rpm,
        "mesada_rais_banda": banda,
        "rpm_es_punto_no_banda": ("en Colpensiones la fórmula es determinista: "
                                  "lo que varía es una decisión del usuario, no "
                                  "incertidumbre del modelo"),
    }
    if mesada_rpm is None or not banda:
        lectura["veredicto"] = "sin_comparacion"
        lectura["mensaje"] = ("falta una de las dos mesadas, así que no se "
                              "compara nada: no se entrega veredicto")
        return lectura

    conservadora, optimista = banda
    gana_rais_en_optimista = optimista > mesada_rpm
    gana_rais_en_conservador = conservadora > mesada_rpm
    lectura["gana_rais_con_precio_de_la_norma"] = gana_rais_en_optimista
    lectura["gana_rais_con_precio_de_mercado"] = gana_rais_en_conservador

    if gana_rais_en_optimista != gana_rais_en_conservador:
        # El caso que obliga a existir a esta función
        lectura["veredicto"] = "se_voltea_dentro_de_la_banda"
        lectura["mensaje"] = (
            "La comparación NO tiene ganador: con el precio de la renta que "
            "supone la norma el fondo privado deja más mesada, y con el precio "
            "de mercado deja menos que Colpensiones. La diferencia entre los dos "
            "regímenes es menor que la incertidumbre del modelo, así que aquí no "
            "se recomienda un traslado: se le muestran los dos escenarios y se "
            "le dice de qué depende")
    elif gana_rais_en_optimista:
        lectura["veredicto"] = "rais_arriba_en_los_dos_extremos"
        lectura["mensaje"] = (
            "El fondo privado deja más mesada en los dos extremos de la banda, "
            "así que la conclusión no depende del precio de la renta vitalicia. "
            "Sigue siendo una estimación, no una recomendación de traslado")
    else:
        lectura["veredicto"] = "rpm_arriba_en_los_dos_extremos"
        lectura["mensaje"] = (
            "Colpensiones deja más mesada en los dos extremos de la banda, así "
            "que la conclusión no depende del precio de la renta vitalicia. "
            "Sigue siendo una estimación, no una recomendación de traslado")
    return lectura


def comparar(caso, sexo, edad=None, fecha_calculo=None,
             ibc_futuro=None, densidad_futura=None):
    """Devuelve la comparación RPM vs RAIS de un caso, con supuestos iguales.

    ibc_futuro y densidad_futura son los supuestos de proyección; van a las DOS
    piernas, porque comparar regímenes con supuestos distintos no compara nada.
    """
    fecha_calculo = fecha_calculo or date.today()
    caso = dict(caso)  # Copia superficial para poder inyectar datos simulados
    caso["afiliado"] = dict(caso["afiliado"])
    caso["resumen_documento"] = dict(caso["resumen_documento"])

    # Si el documento solo trae la edad (ej. Protección), fabricamos una fecha
    # de nacimiento aproximada SOLO para simular (error máximo: 1 año)
    if not caso["afiliado"].get("fecha_nacimiento"):
        edad_doc = edad or caso["afiliado"].get("edad_en_documento")
        nacimiento_aprox = fecha_calculo.replace(year=fecha_calculo.year - edad_doc)
        caso["afiliado"]["fecha_nacimiento"] = nacimiento_aprox.isoformat()

    # --- Pierna RPM: el caso como si estuviera en Colpensiones ---
    # (las semanas se suman entre regímenes al trasladarse, así que la historia
    # completa cuenta tal cual)
    diag_rpm = rpm.diagnosticar(caso, sexo, fecha_calculo,
                                ibc_futuro=ibc_futuro,
                                densidad_futura=densidad_futura)

    # --- Pierna RAIS: el caso como si estuviera en un fondo privado ---
    saldo_simulado = False
    if caso["resumen_documento"].get("saldo_cuenta_individual") is None:
        estimado = rais.estimar_saldo_desde_aportes(caso["periodos"])
        if estimado is None:
            # Historia de Colpensiones: simulamos el saldo desde los salarios
            estimado = simular_saldo_rais(caso["periodos"], fecha_calculo.year)
            saldo_simulado = True
        caso["resumen_documento"]["saldo_cuenta_individual"] = estimado
    diag_rais = rais.diagnosticar(caso, sexo=sexo, edad=edad,
                                  fecha_calculo=fecha_calculo,
                                  ibc_futuro=ibc_futuro,
                                  densidad_futura=densidad_futura)

    # --- Ventana de traslado: ¿todavía puede cambiarse de régimen? ---
    edad_actual = diag_rpm["edad"]
    cierre = EDAD_CIERRE_VENTANA[sexo]
    ventana = {
        "abierta": edad_actual < cierre,
        "edad_cierre": cierre,
        "anios_restantes": max(0, cierre - edad_actual),
    }

    return {
        "caso_id": caso["caso_id"],
        "ventana_traslado": ventana,
        "rpm": diag_rpm,
        "rais": diag_rais,
        "saldo_rais_simulado": saldo_simulado,
        # El punto del RPM contra la banda del RAIS, con el veredicto evaluado
        # en los dos extremos. Sin esto la comparación se leía contra el borde
        # optimista y podía voltearse sin que nadie lo viera.
        "mesadas": comparar_mesadas(diag_rpm, diag_rais),
    }
