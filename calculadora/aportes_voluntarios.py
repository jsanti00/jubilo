# Módulo de APORTES VOLUNTARIOS: qué pasa si el usuario le mete más plata a su
# pensión, cuánto cuesta la administración y cuánto se ahorra en impuestos.
#
# Por qué existe: `costo_y_retorno.py` responde cuánto cuesta COTIZAR y en
# cuánto se recupera. Esa es la mitad de la decisión de quien tiene excedente.
# La otra mitad es el aporte voluntario en sí, que hasta ahora nadie modelaba.
# El corpus lo tiene escrito (kit-contexto/aportes-voluntarios-y-sobrecotizacion.md
# y kit-contexto/tributario-pensional.md), la calculadora no lo tenía.
#
# FRONTERA DE ALCANCE (decisión de Santiago del 2026-07-27, punto 7, NO reabrir):
# este módulo compara alternativas PENSIONALES entre sí (aporte voluntario,
# sobrecotizar, BEPS, quedarse igual). NO compara contra inversiones por fuera
# del sistema y NO recomienda productos financieros, administradora ni
# portafolio. La asesoría de inversión es actividad regulada en Colombia.
# Si el usuario lo pregunta, el agente lo dice con la frase de abajo.
#
# NEGATIVA EXPLÍCITA EN RPM: en Colpensiones no existe vehículo de aporte
# voluntario. El módulo se NIEGA a estimar uno en vez de devolver un número
# (ver `evaluar_aporte_voluntario`). Devolver una cifra ahí sería inventarse un
# producto que no existe.
#
# QUÉ NO HACE ESTE MÓDULO, a propósito:
# - No convierte capital en mesada. Ese factor lo posee `rais.py` y está siendo
#   entregado como BANDA (decisiones 1 y 2). Aquí se recibe el factor de afuera,
#   nunca se calcula (ver `mesada_adicional` y `mesada_adicional_en_banda`).
# - No liquida el impuesto de renta del usuario ni prepara su declaración. El
#   ahorro tributario que estima es una MAGNITUD de orden, no una liquidación.
#
# Todo va en PESOS DE HOY (términos reales), igual que el resto de la
# calculadora: no se proyecta inflación en ningún punto.

from datos_sistema import (
    SMLMV, RENDIMIENTO_REAL, RENDIMIENTO_REAL_OBSERVADO, FUENTE_RENDIMIENTO,
    ADVERTENCIA_RENDIMIENTO, ADVERTENCIA_PROSPECTIVO, APORTE_A_CUENTA_RAIS,
)
# Reutilizamos el formateo de pesos y el salario mínimo del módulo de costo:
# una sola definición de cada utilidad en toda la calculadora.
from costo_y_retorno import pesos, smlmv_vigente

# ---------------------------------------------------------------------------
# Frases de frontera: las usa el agente tal cual cuando el usuario cruza la raya
# ---------------------------------------------------------------------------

FRASE_NO_COMPARA_INVERSIONES = (
    "Puedo comparar tus opciones dentro del sistema pensional entre sí: aportar "
    "voluntariamente, cotizar sobre una base más alta, o quedarte como estás. "
    "Lo que no hago es compararlo contra invertir esa plata por fuera ni "
    "recomendarte un fondo, un portafolio o una administradora: eso es asesoría "
    "de inversión, que es una actividad regulada y no es lo mío."
)

FRASE_RPM_SIN_VEHICULO = (
    "En Colpensiones no existe el aporte voluntario. Tu pensión ahí no sale de "
    "un saldo tuyo sino de una fórmula que mira tu promedio salarial y tus "
    "semanas, así que plata suelta no tiene por dónde entrar. Las dos palancas "
    "que sí existen son cotizar sobre una base más alta, si tu ingreso lo "
    "respalda, y sumar más semanas."
)

FRASE_FUERA_DE_ALCANCE_TRIBUTARIO = (
    "Te puedo mostrar el orden de magnitud del ahorro en impuestos y sus "
    "límites. Liquidar tu impuesto y armar tu declaración ya es trabajo de un "
    "contador o un tributarista, no mío."
)


# ---------------------------------------------------------------------------
# 1. Datos del sistema: cómo se reparte el aporte obligatorio en RAIS
# ---------------------------------------------------------------------------

# De cada 16 puntos cotizados al RAIS: 11,5 a la cuenta individual, 1,5 al
# Fondo de Garantía de Pensión Mínima y 3 a comisión de administración de la
# AFP más prima del seguro previsional.
# Fuente: Ley 100 de 1993 art. 20, modificado por Ley 797 de 2003 art. 7.
# Confianza: ALTA (el 11,5% ya vive en datos_sistema.APORTE_A_CUENTA_RAIS y el
# reparto está corroborado en las páginas de las propias AFP y en prensa
# económica que cita cifras registradas ante la Superfinanciera).
PUNTOS_APORTE_OBLIGATORIO = 0.16
PUNTOS_A_CUENTA = APORTE_A_CUENTA_RAIS          # 11,5%
PUNTOS_A_FGPM = 0.015                           # 1,5%
PUNTOS_A_COMISION_Y_SEGURO = 0.03               # 3%

# Dato clave de asesoría, y la razón por la que este módulo existe: el aporte
# VOLUNTARIO a la cuenta obligatoria entra COMPLETO al saldo. No se le
# descuentan los 4,5 puntos del obligatorio, porque esos financian el seguro
# previsional y la garantía de pensión mínima, que no dependen del aporte
# extra. Lo que sí se le cobra es una comisión sobre el saldo (sección 2).
# Confianza: MEDIA. Es lo que declaran las AFP en sus páginas de producto
# (Porvenir, Protección, Colfondos) y es coherente con la naturaleza del 3% y
# del 1,5% en la Ley 100 art. 20, pero no se ubicó la norma que lo diga de
# forma expresa. Ver SUPUESTOS_DECLARADOS.
APORTE_VOLUNTARIO_ENTRA_COMPLETO = True


# ---------------------------------------------------------------------------
# 2. Comisión de administración de la AFP sobre el saldo voluntario
# ---------------------------------------------------------------------------

# Tabla de Porvenir, escalonada por el saldo en aportes voluntarios medido en
# salarios mínimos. Cada tupla es (tope del tramo en SMLMV, comisión anual).
# El cobro es mensual sobre el saldo.
# Fuente: Porvenir, "Conoce qué son los aportes voluntarios a pensión
# obligatoria", consultada el 2026-07-27 (fuente primaria: la propia AFP).
# Confianza: ALTA para la tabla. MEDIA para su vigencia: una página comercial
# puede quedar desactualizada y no trae fecha de última revisión.
COMISION_VOLUNTARIO_PORVENIR = [
    (5, 0.0390),      # Hasta 5 SMLMV de saldo
    (20, 0.0350),     # Más de 5 y hasta 20
    (50, 0.0250),     # Más de 20 y hasta 50
    (75, 0.0220),     # Más de 50 y hasta 75
    (100, 0.0200),    # Más de 75 y hasta 100
    (150, 0.0180),    # Más de 100 y hasta 150
    (300, 0.0175),    # Más de 150 y hasta 300
    (500, 0.0150),    # Más de 300 y hasta 500
    (900, 0.0125),    # Más de 500 y hasta 900
    (1280, 0.0100),   # Más de 900 y hasta 1.280
]
COMISION_VOLUNTARIO_PORVENIR_TOPE = 0.0075   # Más de 1.280 SMLMV de saldo

# Comisión plana de Protección sobre el saldo de aportes voluntarios en
# pensiones obligatorias: 2% anual, liquidado diariamente sobre el saldo.
# Fuente: página de producto de Protección, referida por buscador el
# 2026-07-27. [VERIFICAR] No se pudo abrir la página de Protección de forma
# directa (el sitio devuelve contenido vacío a la lectura automatizada), así
# que la cifra viene de la reseña del buscador, no del texto leído.
COMISION_VOLUNTARIO_PROTECCION = 0.02

# Comisión que se usa cuando no se sabe con qué AFP está el usuario. Es un
# SUPUESTO declarado, no un dato: se escoge el 2% porque queda en la zona media
# de las tarifas observadas y porque un saldo voluntario típico de un usuario
# con excedente cae entre 20 y 100 SMLMV, donde Porvenir cobra entre 2,0% y
# 2,5%. El módulo siempre marca cuándo está usando este supuesto.
COMISION_VOLUNTARIO_SUPUESTA = 0.02

# Catálogo de AFP con comisión conocida. Las que no están aquí caen en el
# supuesto de arriba, marcado como tal. No se inventa una cifra por AFP.
COMISIONES_POR_AFP = {
    "porvenir": {
        "tipo": "escalonada_por_saldo",
        "fuente": "Porvenir, página de aportes voluntarios a pensión "
                  "obligatoria, consultada 2026-07-27",
        "confianza": "ALTA en la tabla, MEDIA en su vigencia",
    },
    "proteccion": {
        "tipo": "plana",
        "pct": COMISION_VOLUNTARIO_PROTECCION,
        "fuente": "Protección, página de producto, referida por buscador "
                  "2026-07-27 [VERIFICAR: no se leyó la página directamente]",
        "confianza": "BAJA",
    },
}


def comision_administracion_anual(saldo_voluntario, afp=None, smlmv=None):
    """Comisión anual que le cobran por administrar su saldo voluntario.

    saldo_voluntario: saldo en aportes voluntarios, en pesos de hoy.
    afp: "porvenir", "proteccion" o None. Si no se sabe, se usa el supuesto
         declarado y se marca, en vez de inventarse una cifra.

    Devuelve un diccionario con el porcentaje, su fuente y si es supuesto. El
    porcentaje siempre viaja con su procedencia: es la regla del proyecto.
    """
    smlmv = smlmv or smlmv_vigente()
    clave = (afp or "").strip().lower()

    if clave == "porvenir":
        # Buscamos el primer tramo cuyo tope todavía no se pasó
        saldo_en_smlmv = saldo_voluntario / smlmv
        pct = COMISION_VOLUNTARIO_PORVENIR_TOPE
        for tope, tarifa in COMISION_VOLUNTARIO_PORVENIR:
            if saldo_en_smlmv <= tope:
                pct = tarifa
                break
        return {
            "pct_anual": pct,
            "es_supuesto": False,
            "afp": "Porvenir",
            "base": "saldo en aportes voluntarios, cobro mensual",
            "fuente": COMISIONES_POR_AFP["porvenir"]["fuente"],
            "confianza": COMISIONES_POR_AFP["porvenir"]["confianza"],
        }

    if clave == "proteccion":
        return {
            "pct_anual": COMISION_VOLUNTARIO_PROTECCION,
            "es_supuesto": False,
            "afp": "Protección",
            "base": "saldo en aportes voluntarios, liquidación diaria",
            "fuente": COMISIONES_POR_AFP["proteccion"]["fuente"],
            "confianza": COMISIONES_POR_AFP["proteccion"]["confianza"],
        }

    # No sabemos la AFP: se usa el supuesto y se dice que lo es
    return {
        "pct_anual": COMISION_VOLUNTARIO_SUPUESTA,
        "es_supuesto": True,
        "afp": None,
        "base": "saldo en aportes voluntarios",
        "fuente": "SUPUESTO del modelo, no es un dato de la AFP del usuario. "
                  "Para afinarlo hay que preguntar con qué administradora está.",
        "confianza": "SUPUESTO DECLARADO",
    }


# ---------------------------------------------------------------------------
# 3. Proyección del saldo voluntario, neta de comisión
# ---------------------------------------------------------------------------

# DOS COSAS DISTINTAS QUE NO SE PUEDEN MEZCLAR (estructura del 2026-07-27):
#
#   RENDIMIENTO_REAL_OBSERVADO es EVIDENCIA: lo que los fondos rindieron de
#   verdad entre marzo de 2011 y octubre de 2024, según la Superfinanciera.
#   Es pasado y es dato. No es monótono: el moderado observado NO le ganó al
#   conservador.
#
#   RENDIMIENTO_REAL es SUPUESTO: el prospectivo de largo plazo que Santiago
#   decidió usar para proyectar, construido sobre el ancla del conservador más
#   una prima de renta variable por la exposición adicional de cada perfil. Es
#   futuro y es supuesto. Sí es monótono, por construcción.
#
# Las dos viven en datos_sistema y aquí se CONSUMEN, no se redefinen: tener
# copias del mismo supuesto es cómo se desincronizan las cifras del producto.
# La regla de este módulo al hablarle al usuario es una sola línea: el futuro
# es supuesto, el pasado es dato, y cada cifra dice cuál de los dos es.
#
# OJO, NO CONFUNDIR ninguna de las dos con la rentabilidad MÍNIMA regulatoria
# (Carta Circular 39 de la Superfinanciera, a 31 de marzo de 2025: conservador
# 5,87%, moderado 4,16%, mayor riesgo 7,25%). Esa es NOMINAL y es un piso
# obligatorio, no un rendimiento esperado. Mezclarla con las cifras reales
# infla el resultado dos veces: por la inflación y por confundir un piso con
# una expectativa. Por eso no vive en este módulo ni como constante.


def proyectar_aporte_voluntario_en_rango(meses, perfil="moderado", **kwargs):
    """Proyecta el capital con el rango OBSERVADO, y aparte con el supuesto.

    Devuelve tres cifras que responden preguntas distintas:
    - capital_piso y capital_techo: qué habría dado el rango que los fondos
      rindieron de verdad. Es evidencia del pasado.
    - capital_central: lo que proyecta el supuesto prospectivo de largo plazo,
      que es el que usa el resto de la calculadora. Es supuesto del futuro.

    Las tres viajan etiquetadas. Mostrar el rango observado sin decir que es
    pasado, o el central sin decir que es supuesto, es la confusión que este
    módulo tiene prohibida.

    Acepta los mismos argumentos que `proyectar_aporte_voluntario` salvo
    `rendimiento_real`, que aquí lo fijan las constantes.
    """
    kwargs.pop("rendimiento_real", None)
    piso_tasa, techo_tasa = RENDIMIENTO_REAL_OBSERVADO.get(
        perfil, RENDIMIENTO_REAL_OBSERVADO["moderado"])
    central_tasa = RENDIMIENTO_REAL.get(perfil, RENDIMIENTO_REAL["moderado"])

    piso = proyectar_aporte_voluntario(meses, perfil, rendimiento_real=piso_tasa,
                                       **kwargs)
    techo = proyectar_aporte_voluntario(meses, perfil, rendimiento_real=techo_tasa,
                                        **kwargs)
    central = proyectar_aporte_voluntario(meses, perfil,
                                          rendimiento_real=central_tasa, **kwargs)

    return {
        "perfil": perfil,
        # Evidencia: lo que pasó
        "capital_piso": piso["capital_final"],
        "capital_techo": techo["capital_final"],
        "rendimiento_piso": piso_tasa,
        "rendimiento_techo": techo_tasa,
        "naturaleza_del_rango": "DATO: rendimiento observado entre marzo de "
                                "2011 y octubre de 2024",
        "fuente_del_rango": FUENTE_RENDIMIENTO,
        "advertencia_del_rango": ADVERTENCIA_RENDIMIENTO,
        # Supuesto: lo que la proyección asume hacia adelante
        "capital_central": central["capital_final"],
        "rendimiento_central": central_tasa,
        "naturaleza_del_central": "SUPUESTO: rendimiento prospectivo de largo "
                                  "plazo, no es lo que rindió el fondo",
        "advertencia_del_central": ADVERTENCIA_PROSPECTIVO,
        # El central puede quedar por FUERA del rango observado, y es a
        # propósito: son dos cosas distintas, no una descalibración.
        "central_fuera_del_rango_observado": not (piso_tasa <= central_tasa
                                                  <= techo_tasa),
        "proyeccion_piso": piso,
        "proyeccion_techo": techo,
        "proyeccion_central": central,
    }


def proyectar_aporte_voluntario(meses, perfil="moderado", aporte_mensual=0,
                                aporte_unico=0, afp=None, smlmv=None,
                                rendimiento_real=None):
    """Cuánto capital extra tiene al final si aporta de más, ya descontada la
    comisión de administración.

    meses: cuántos meses faltan hasta pensionarse.
    perfil: "conservador", "moderado" o "mayor_riesgo" (multifondos).
    aporte_mensual: cuánto pondría cada mes, en pesos de hoy.
    aporte_unico: cuánto pondría hoy de una sola vez, en pesos de hoy.
    afp: para saber qué comisión aplicar. Si es None se usa el supuesto.

    Los dos aportes conviven a propósito: la pregunta real del usuario con
    excedente suele ser mixta ("tengo estos 20 millones y puedo poner 500 mil
    al mes"). Devuelve también el saldo BRUTO (sin comisión) para que se vea
    cuánto se lleva la administración, que es la cifra que nadie le muestra.
    """
    smlmv = smlmv or smlmv_vigente()
    if rendimiento_real is None:
        rendimiento_real = RENDIMIENTO_REAL.get(perfil, RENDIMIENTO_REAL["moderado"])

    # Pasamos el rendimiento anual a mensual con interés compuesto, igual que
    # en rais.proyectar_saldo (misma convención en toda la calculadora)
    r_mes = (1 + rendimiento_real) ** (1 / 12) - 1

    saldo = float(aporte_unico)          # Saldo neto de comisión
    saldo_bruto = float(aporte_unico)    # El mismo saldo si no cobraran nada
    aportado = float(aporte_unico)       # Todo lo que salió de su bolsillo
    comision_pagada = 0.0
    pct_ultimo = None

    for _ in range(int(meses)):
        # La comisión se recalcula cada mes porque el tramo depende del saldo
        com = comision_administracion_anual(saldo, afp, smlmv)
        pct_ultimo = com
        # Comisión mensual equivalente a la tarifa anual declarada
        c_mes = 1 - (1 - com["pct_anual"]) ** (1 / 12)

        saldo = saldo * (1 + r_mes)
        cobro = saldo * c_mes
        comision_pagada += cobro
        saldo = saldo - cobro + aporte_mensual

        saldo_bruto = saldo_bruto * (1 + r_mes) + aporte_mensual
        aportado += aporte_mensual

    return {
        "meses": int(meses),
        "perfil": perfil,
        "rendimiento_real_anual": rendimiento_real,
        "aporte_mensual": round(aporte_mensual),
        "aporte_unico": round(aporte_unico),
        "total_aportado": round(aportado),
        "capital_final": round(saldo),
        "capital_final_sin_comision": round(saldo_bruto),
        "comision_pagada": round(comision_pagada),
        # Cuánto de lo que habría rendido se lo lleva la administración
        "comision_sobre_capital_pct": (round(comision_pagada / saldo_bruto * 100, 1)
                                       if saldo_bruto > 0 else None),
        "rendimiento_ganado": round(saldo - aportado),
        "comision": pct_ultimo or comision_administracion_anual(saldo, afp, smlmv),
    }


# ---------------------------------------------------------------------------
# 4. De capital extra a mesada extra: el factor NO se calcula aquí
# ---------------------------------------------------------------------------

def mesada_adicional(capital_adicional, factor_conversion):
    """Cuánta mesada compra ese capital extra, dado un factor que viene de fuera.

    factor_conversion: cuántos pesos de capital cuesta un peso de mesada. Lo
    posee `rais.py`, que lo entrega como banda. Este módulo NO lo calcula ni lo
    fija: si lo hiciera, habría dos definiciones del mismo número en la
    calculadora y la banda dejaría de ser una sola.
    """
    if not factor_conversion or factor_conversion <= 0:
        return None
    return capital_adicional / factor_conversion


def mesada_adicional_en_banda(capital_adicional, factores):
    """Igual que arriba pero con los dos extremos de la banda del factor.

    factores: diccionario con las llaves "optimista" y "conservador", tal como
    lo entrega `rais.py`. Un factor más alto (más caro cada peso de mesada) da
    una mesada más baja, así que el extremo OPTIMISTA de la mesada sale del
    factor más bajo. Se ordena aquí para que el consumidor no se equivoque.
    """
    valores = [f for f in (factores or {}).values() if f and f > 0]
    if not valores:
        return None
    return {
        "mesada_optimista": capital_adicional / min(valores),
        "mesada_conservadora": capital_adicional / max(valores),
        "factores_usados": dict(factores),
        "nota": "La banda del factor de conversión la fija rais.py. Este "
                "módulo la propaga, no la origina.",
    }


# ---------------------------------------------------------------------------
# 5. El beneficio tributario: dos destinos, dos reglas distintas
# ---------------------------------------------------------------------------
#
# La confusión más cara de esta materia es tratar los dos destinos como si
# fueran lo mismo. No lo son:
#
#   DESTINO "obligatoria": cotización VOLUNTARIA a la cuenta de ahorro
#   individual de la AFP. Es INGRESO NO CONSTITUTIVO de renta, con su propio
#   límite del 25% del ingreso y 2.500 UVT, y NO consume el cupo global del
#   art. 336. Fuente: ET art. 55 inciso 2. Penalidad al retirar para fines
#   distintos a mayor pensión o retiro anticipado: renta líquida gravable con
#   retención del 35%. Fuente: ET art. 55. Es la penalidad más dura de las tres
#   y la menos conocida.
#
#   DESTINO "voluntaria": aporte a un fondo de pensiones VOLUNTARIAS. Es RENTA
#   EXENTA, con límite del 30% del ingreso y 3.800 UVT anuales COMPARTIDAS con
#   las cuentas AFC, y además queda sometida al techo global de la cédula
#   general: 40% del ingreso y 1.340 UVT anuales. Fuentes: ET art. 126-1 (mod.
#   Ley 1819 de 2016 art. 15) y ET art. 336 num. 3 (mod. Ley 2277 de 2022
#   art. 7). Permanencia mínima de 10 años salvo vivienda o cumplimiento de
#   requisitos de pensión.
#
# Confianza: ALTA en las reglas y sus límites (verificadas contra el texto del
# Estatuto Tributario en kit-contexto/tributario-pensional.md, secciones 5, 6,
# 7 y 8, que a su vez se cotejó en Secretaría del Senado el 2026-07-26).

# Valor de la UVT por año, en pesos.
# Fuente: Resolución DIAN 000238 del 15 de diciembre de 2025 para 2026.
# Confianza: MEDIA. La cifra ($52.374) está corroborada en varias fuentes
# secundarias que citan la resolución con número y fecha, pero no se leyó el
# texto de la resolución. [VERIFICAR] antes del piloto.
UVT = {
    2025: 49_799,
    2026: 52_374,
}

# Límites del destino "obligatoria" (ET art. 55 inciso 2)
LIMITE_ART55_PCT = 0.25
LIMITE_ART55_UVT = 2_500
RETENCION_RETIRO_ART55 = 0.35

# Límites del destino "voluntaria" (ET art. 126-1, cupo compartido con AFC)
LIMITE_ART126_1_PCT = 0.30
LIMITE_ART126_1_UVT = 3_800
PERMANENCIA_ART126_1_ANIOS = 10

# Techo global de rentas exentas y deducciones de la cédula general
# (ET art. 336 num. 3, modificado por Ley 2277 de 2022 art. 7). Bajó de 5.040
# a 1.340 UVT: es lo que saturó el beneficio mucho antes que en el pasado.
LIMITE_ART336_PCT = 0.40
LIMITE_ART336_UVT = 1_340

# Tabla del impuesto de renta de personas naturales residentes, en UVT.
# Cada tupla es (tope del rango en UVT, tarifa marginal, impuesto acumulado en
# UVT hasta el piso del rango).
# Fuente: ET art. 241, en su versión vigente tras la Ley 2277 de 2022.
# Confianza: MEDIA. La tabla se transcribió de una compilación del Estatuto
# (actualicese.com) el 2026-07-27; no se leyó en Secretaría del Senado, que ese
# día no respondió a la lectura automatizada. [VERIFICAR] contra fuente oficial.
TABLA_RENTA_241 = [
    (1_090, 0.00, 0),
    (1_700, 0.19, 0),
    (4_100, 0.28, 116),
    (8_670, 0.33, 788),
    (18_970, 0.35, 2_296),
    (31_000, 0.37, 5_901),
]
TABLA_RENTA_241_TOPE = (0.39, 10_352)   # Más de 31.000 UVT


def valor_uvt(anio=None):
    """UVT del año pedido, o la más reciente que tenga la tabla."""
    if anio is not None and anio in UVT:
        return UVT[anio]
    return UVT[max(UVT)]


def impuesto_renta(base_gravable, anio=None):
    """Impuesto de renta de una persona natural residente sobre esa base.

    base_gravable: renta líquida gravable ANUAL, en pesos.
    Devuelve el impuesto en pesos. Es la tabla del art. 241 aplicada literal,
    no una liquidación: no incorpora descuentos tributarios, ganancias
    ocasionales ni ninguna otra cédula.
    """
    uvt = valor_uvt(anio)
    base_uvt = base_gravable / uvt

    # Recorremos los rangos hasta encontrar el que contiene la base
    piso = 0
    for tope, tarifa, acumulado in TABLA_RENTA_241:
        if base_uvt <= tope:
            return ((base_uvt - piso) * tarifa + acumulado) * uvt
        piso = tope

    # Por encima del último rango de la tabla
    tarifa, acumulado = TABLA_RENTA_241_TOPE
    return ((base_uvt - piso) * tarifa + acumulado) * uvt


def tarifa_marginal(base_gravable, anio=None):
    """Tarifa marginal del art. 241 que le aplica a esa base gravable."""
    uvt = valor_uvt(anio)
    base_uvt = base_gravable / uvt
    for tope, tarifa, _ in TABLA_RENTA_241:
        if base_uvt <= tope:
            return tarifa
    return TABLA_RENTA_241_TOPE[0]


def cupo_beneficio_tributario(ingreso_anual, destino="voluntaria", anio=None,
                              aportes_previos_del_anio=0,
                              otras_rentas_exentas_del_anio=0):
    """Cuánto puede aportar este año con beneficio tributario, y por qué tope.

    ingreso_anual: ingreso laboral o tributario del año, en pesos.
    destino: "obligatoria" (cotización voluntaria al RAIS, ET art. 55) o
             "voluntaria" (fondo de pensiones voluntarias, ET art. 126-1).
    aportes_previos_del_anio: lo que ya aportó este año al mismo cupo. Para el
             destino "voluntaria" incluye también lo que haya puesto en AFC:
             el cupo de 3.800 UVT es UNO SOLO para los dos, no se suman.
    otras_rentas_exentas_del_anio: lo que ya consume del techo del art. 336
             por otra vía (típicamente la renta exenta del 25% laboral, hoy
             limitada a 790 UVT). Solo aplica al destino "voluntaria".

    Devuelve el cupo disponible y CUÁL de los topes es el que muerde, que es lo
    que el usuario necesita saber para decidir cuánto poner.
    """
    uvt = valor_uvt(anio)

    if destino == "obligatoria":
        # ET art. 55: el menor entre 25% del ingreso y 2.500 UVT. Este cupo NO
        # pasa por el techo del art. 336, porque no es renta exenta sino
        # ingreso no constitutivo de renta, que se resta antes.
        por_porcentaje = ingreso_anual * LIMITE_ART55_PCT
        por_uvt = LIMITE_ART55_UVT * uvt
        limite = min(por_porcentaje, por_uvt)
        topes = {
            "por_porcentaje_del_ingreso": round(por_porcentaje),
            "por_tope_en_uvt": round(por_uvt),
        }
        cual_muerde = ("25% del ingreso" if por_porcentaje < por_uvt
                       else f"{LIMITE_ART55_UVT:,}".replace(",", ".") + " UVT")
        norma = "ET art. 55 inciso 2 (ingreso no constitutivo de renta)"
    else:
        # ET art. 126-1: el menor entre 30% del ingreso y 3.800 UVT...
        por_porcentaje = ingreso_anual * LIMITE_ART126_1_PCT
        por_uvt = LIMITE_ART126_1_UVT * uvt
        limite_126 = min(por_porcentaje, por_uvt)
        # ...y encima el techo global del art. 336, que es el que en la
        # práctica muerde primero desde la Ley 2277 de 2022.
        techo_336 = min(ingreso_anual * LIMITE_ART336_PCT, LIMITE_ART336_UVT * uvt)
        techo_336_disponible = max(0.0, techo_336 - otras_rentas_exentas_del_anio)
        limite = min(limite_126, techo_336_disponible)
        topes = {
            "por_porcentaje_del_ingreso": round(por_porcentaje),
            "por_tope_en_uvt": round(por_uvt),
            "techo_global_art_336": round(techo_336),
            "techo_global_disponible": round(techo_336_disponible),
        }
        cual_muerde = ("techo global del art. 336 (40% del ingreso o 1.340 UVT)"
                       if techo_336_disponible <= limite_126
                       else ("30% del ingreso" if por_porcentaje < por_uvt
                             else "3.800 UVT compartidas con AFC"))
        norma = ("ET art. 126-1 (renta exenta) con el techo del ET art. 336 "
                 "num. 3, mod. Ley 2277 de 2022 art. 7")

    disponible = max(0.0, limite - aportes_previos_del_anio)
    return {
        "destino": destino,
        "anio": anio or max(UVT),
        "uvt_usada": uvt,
        "limite_del_anio": round(limite),
        "aportes_previos_del_anio": round(aportes_previos_del_anio),
        "cupo_disponible": round(disponible),
        "tope_que_muerde": cual_muerde,
        "topes": topes,
        "norma": norma,
    }


def ahorro_tributario(ingreso_anual, aporte_anual, destino="voluntaria",
                      anio=None, aportes_previos_del_anio=0,
                      otras_rentas_exentas_del_anio=0):
    """Cuánto impuesto de renta se ahorra en el año por hacer ese aporte.

    Se calcula por diferencia: el impuesto sobre el ingreso sin el aporte
    menos el impuesto sobre el ingreso ya restado el aporte reconocido. La
    parte del aporte que se pasa del cupo NO ahorra un peso, y eso se reporta
    aparte porque es la sorpresa más común del usuario que aporta de más.

    IMPORTANTE, y viaja como supuesto: aquí se usa el ingreso anual como si
    fuera ya la base gravable. Un caso real tiene depuraciones (aportes
    obligatorios, costos, otras deducciones) que bajan esa base y con ella el
    ahorro. Esto es un ORDEN DE MAGNITUD, no una liquidación.
    """
    cupo = cupo_beneficio_tributario(
        ingreso_anual, destino, anio, aportes_previos_del_anio,
        otras_rentas_exentas_del_anio)

    reconocido = min(aporte_anual, cupo["cupo_disponible"])
    excedente = max(0.0, aporte_anual - reconocido)

    impuesto_sin = impuesto_renta(ingreso_anual, anio)
    impuesto_con = impuesto_renta(max(0.0, ingreso_anual - reconocido), anio)
    ahorro = impuesto_sin - impuesto_con

    return {
        "aporte_anual": round(aporte_anual),
        "aporte_con_beneficio": round(reconocido),
        "aporte_sin_beneficio": round(excedente),
        "impuesto_sin_aporte": round(impuesto_sin),
        "impuesto_con_aporte": round(impuesto_con),
        "ahorro_en_impuestos": round(ahorro),
        # Cuánto vale cada peso aportado en impuesto ahorrado. Es la cifra que
        # de verdad compara alternativas: si da 0, el cupo ya está saturado.
        "ahorro_por_peso_aportado": (round(ahorro / aporte_anual, 3)
                                     if aporte_anual > 0 else None),
        "tarifa_marginal": tarifa_marginal(ingreso_anual, anio),
        "cupo": cupo,
        "condiciones": condiciones_de_permanencia(destino),
    }


def condiciones_de_permanencia(destino="voluntaria"):
    """Las letras chicas del beneficio, que el usuario se entera tarde.

    Nunca se recomienda un aporte voluntario sin esto al lado: es regla del
    kit (tributario-pensional.md sección 10, punto 5).
    """
    if destino == "obligatoria":
        return {
            "permanencia_minima": "ninguna, pero el DESTINO sí importa",
            "penalidad": (
                "Si retira esa plata para algo distinto a obtener una mayor "
                "pensión o un retiro anticipado, se vuelve renta líquida "
                "gravable y la administradora le retiene el 35% al momento "
                "del retiro. Es la penalidad más dura de las tres vías."),
            "retencion_al_retiro": RETENCION_RETIRO_ART55,
            "norma": "ET art. 55",
        }
    return {
        "permanencia_minima": f"{PERMANENCIA_ART126_1_ANIOS} años",
        "penalidad": (
            "Si retira antes de 10 años y no es para comprar vivienda ni "
            "porque ya cumplió los requisitos de pensión, se pierde el "
            "beneficio y el fondo le practica la retención que no le hizo, "
            "más la de los rendimientos."),
        "excepciones": [
            "permanencia de al menos 10 años",
            "cumplir los requisitos para acceder a la pensión de vejez o "
            "jubilación, o muerte o incapacidad certificada",
            "destinar el retiro a adquisición de vivienda, financiada o no",
        ],
        "norma": "ET art. 126-1 y su parágrafo 1",
        "advertencia_pensionado": (
            "Aportar estando YA pensionado y retirar enseguida sin impuesto no "
            "funciona: la DIAN cerró esa lectura (Oficio 3706 de 2018). Esa "
            "plata nueva cumple igual la permanencia."),
    }


# ---------------------------------------------------------------------------
# 6. La negativa en RPM y la evaluación completa
# ---------------------------------------------------------------------------

def evaluar_aporte_voluntario(regimen, meses, ingreso_anual=None,
                              aporte_mensual=0, aporte_unico=0,
                              destino="obligatoria", perfil="moderado",
                              afp=None, anio=None, smlmv=None,
                              aportes_previos_del_anio=0,
                              otras_rentas_exentas_del_anio=0):
    """La entrada principal: qué pasa si esta persona aporta de más.

    regimen: "RAIS" o "RPM". EN RPM ESTE MÓDULO NO DEVUELVE UN NÚMERO. Se
    niega, explica por qué y remite a las dos palancas que sí existen. Estimar
    un aporte voluntario en Colpensiones sería inventarse un producto que no
    existe, que es exactamente el error que el corpus manda no cometer
    (aportes-voluntarios-y-sobrecotizacion.md sección 1).

    ingreso_anual: para el beneficio tributario. Si no se pasa, el módulo
    calcula el capital pero deja el beneficio en None y dice que falta el dato,
    en vez de suponerlo.
    """
    if (regimen or "").strip().upper() != "RAIS":
        return {
            "aplica": False,
            "regimen": regimen,
            "motivo": "En el RPM (Colpensiones) no existe vehículo de aporte "
                      "voluntario: la pensión no sale de un saldo propio sino "
                      "de una fórmula sobre el IBL y las semanas.",
            "que_decir": FRASE_RPM_SIN_VEHICULO,
            "palancas_que_si_existen": [
                "Subir el IBC dentro de lo que respalde su ingreso real "
                "(ver costo_y_retorno.py). Ojo con el salto de última hora: "
                "es zona gris y se deriva a abogado pensional.",
                "Sumar semanas por encima del mínimo: cada bloque completo de "
                "50 semanas sube la tasa de reemplazo 1,5 puntos, con techo "
                "del 80% del IBL (Ley 100 art. 34, mod. Ley 797 de 2003).",
            ],
            "advertencia": "Quien cotiza de más en Colpensiones NO recupera el "
                           "exceso: su aporte va a un fondo común. En RAIS sí "
                           "existe el excedente de libre disponibilidad "
                           "(Ley 100 art. 85).",
            "fuente": "kit-contexto/aportes-voluntarios-y-sobrecotizacion.md "
                      "secciones 1 y 2",
            "supuestos": SUPUESTOS_DECLARADOS,
        }

    proyeccion = proyectar_aporte_voluntario(
        meses, perfil=perfil, aporte_mensual=aporte_mensual,
        aporte_unico=aporte_unico, afp=afp, smlmv=smlmv)

    # El beneficio tributario es anual: el aporte del año son 12 mensualidades
    # más el aporte único, que se hace una sola vez y en un solo año gravable.
    aporte_del_primer_anio = aporte_mensual * min(12, meses) + aporte_unico
    aporte_de_anio_corriente = aporte_mensual * min(12, meses)

    if ingreso_anual:
        beneficio = ahorro_tributario(
            ingreso_anual, aporte_del_primer_anio, destino, anio,
            aportes_previos_del_anio, otras_rentas_exentas_del_anio)
        # El año del aporte único es distinto a los siguientes: conviene ver
        # los dos, porque el usuario compara mal si solo ve el primero.
        beneficio_anios_siguientes = (
            ahorro_tributario(ingreso_anual, aporte_de_anio_corriente, destino,
                              anio, aportes_previos_del_anio,
                              otras_rentas_exentas_del_anio)
            if aporte_unico and aporte_mensual else None)
    else:
        beneficio = None
        beneficio_anios_siguientes = None

    return {
        "aplica": True,
        "regimen": "RAIS",
        "destino": destino,
        "destino_explicado": (
            "cotización voluntaria a su cuenta obligatoria de la AFP"
            if destino == "obligatoria"
            else "aporte a un fondo de pensiones voluntarias"),
        "proyeccion": proyeccion,
        "beneficio_tributario_primer_anio": beneficio,
        "beneficio_tributario_anios_siguientes": beneficio_anios_siguientes,
        "falta_dato": (None if ingreso_anual else
                       "no se conoce el ingreso anual: sin ese dato no se "
                       "estima el ahorro en impuestos, no se supone"),
        "conversion_a_mesada": (
            "Este módulo entrega CAPITAL, no mesada. Para convertirlo hay que "
            "pasar el factor de conversión de rais.py, que hoy es una banda."),
        "frontera": FRASE_NO_COMPARA_INVERSIONES,
        "supuestos": SUPUESTOS_DECLARADOS,
    }


# ---------------------------------------------------------------------------
# 7. Comparar alternativas PENSIONALES entre sí (nunca contra el mercado)
# ---------------------------------------------------------------------------

def comparar_alternativas_pensionales(regimen, tiene_capacidad_de_pago=True,
                                      es_independiente=False,
                                      ingreso_respalda_ibc_mayor=False,
                                      sisben_1_2_o_3=False):
    """Qué palancas tiene realmente disponibles esta persona, y cuáles no.

    Es la tabla de accionabilidad del corpus convertida en código: antes de
    ofrecer una palanca se verifica que el usuario pueda accionarla. Una
    palanca que no puede accionar no es un consejo, es ruido.
    Fuente: kit-contexto/aportes-voluntarios-y-sobrecotizacion.md sección 6.

    Devuelve TODAS las alternativas, las disponibles y las que no, con el
    motivo. Las no disponibles importan tanto como las otras: son el "no se
    puede" dicho a tiempo.
    """
    en_rais = (regimen or "").strip().upper() == "RAIS"
    alternativas = []

    alternativas.append({
        "alternativa": "quedarse como está",
        "disponible": True,
        "motivo": "Siempre es una opción y es el punto de comparación de todas "
                  "las demás.",
    })

    alternativas.append({
        "alternativa": "aporte voluntario a la cuenta obligatoria (RAIS)",
        "disponible": en_rais and tiene_capacidad_de_pago,
        "motivo": (
            "Está en RAIS y tiene excedente: el aporte entra al saldo y "
            "capitaliza." if en_rais and tiene_capacidad_de_pago
            else ("No está en RAIS: en Colpensiones no existe este vehículo."
                  if not en_rais
                  else "No hay excedente con qué aportar. Ofrecerlo sería "
                       "ruido.")),
        "norma": "Ley 100 de 1993, compilación Decreto 1833 de 2016; "
                 "tributario en ET art. 55",
    })

    alternativas.append({
        "alternativa": "aporte a fondo de pensiones voluntarias",
        "disponible": tiene_capacidad_de_pago,
        "motivo": (
            "Tiene excedente. Júbilo explica el efecto tributario y las "
            "condiciones de permanencia, y hasta ahí llega."
            if tiene_capacidad_de_pago else "No hay excedente con qué aportar."),
        "limite_de_alcance": (
            "Júbilo NO recomienda administradora, fondo ni portafolio. Explica "
            "la regla tributaria (ET art. 126-1), no el producto."),
    })

    alternativas.append({
        "alternativa": "cotizar sobre una base más alta (sobrecotizar)",
        "disponible": (es_independiente and ingreso_respalda_ibc_mayor
                       and tiene_capacidad_de_pago),
        "motivo": (
            "Es independiente y su ingreso respalda una base mayor."
            if es_independiente and ingreso_respalda_ibc_mayor
               and tiene_capacidad_de_pago
            else ("Es asalariado: su IBC lo fija su salario, no lo escoge."
                  if not es_independiente
                  else ("Su ingreso no respalda una base mayor: subirla sin "
                        "respaldo es justo el patrón que las entidades revisan."
                        if not ingreso_respalda_ibc_mayor
                        else "No hay excedente para pagar el aporte mayor."))),
        "advertencia": (
            "Un salto abrupto en la base justo antes de pensionarse es zona "
            "gris. El agente no la resuelve: deriva a abogado pensional. "
            "Además el IBL se calcula sobre 10 años o toda la vida laboral si "
            "resulta superior (Ley 100 art. 21), así que subir la base tres "
            "años no mueve tanto el promedio."),
        "modulo": "costo_y_retorno.py",
    })

    alternativas.append({
        "alternativa": "BEPS",
        "disponible": sisben_1_2_o_3 and not tiene_capacidad_de_pago,
        "motivo": (
            "No logra cotizar por salario mínimo y está en Sisbén 1, 2 o 3: es "
            "su segmento." if sisben_1_2_o_3 and not tiene_capacidad_de_pago
            else ("Tiene capacidad de pago: ofrecer BEPS aquí es un ERROR DE "
                  "SEGMENTO. Los BEPS no mejoran una pensión, son para quien "
                  "no alcanza a cotizar por el mínimo."
                  if tiene_capacidad_de_pago
                  else "No consta que esté en Sisbén 1, 2 o 3: hay que "
                       "preguntarlo antes de ofrecerlo.")),
        "norma": "Ley 1328 de 2009 art. 87",
    })

    return {
        "regimen": regimen,
        "alternativas": alternativas,
        "disponibles": [a for a in alternativas if a["disponible"]],
        "descartadas": [a for a in alternativas if not a["disponible"]],
        "frontera": FRASE_NO_COMPARA_INVERSIONES,
        "nota": "Todas las alternativas de esta tabla son PENSIONALES y se "
                "comparan entre sí. No hay una fila de 'invertir por fuera' a "
                "propósito: eso es asesoría de inversión y está fuera del "
                "alcance de Júbilo.",
    }


# ---------------------------------------------------------------------------
# 8. Supuestos que viajan con toda cifra de este módulo
# ---------------------------------------------------------------------------

SUPUESTOS_DECLARADOS = [
    "Todo en pesos de hoy (términos reales): no se proyecta inflación.",
    "El aporte voluntario a la cuenta obligatoria entra COMPLETO al saldo, sin "
    "los 4,5 puntos que en el aporte obligatorio van al seguro previsional y "
    "al Fondo de Garantía de Pensión Mínima. Es lo que declaran las AFP, pero "
    "no se ubicó la norma que lo diga expreso.",
    "La comisión de administración se cobra sobre el SALDO y se recalcula cada "
    "mes, porque el tramo depende del saldo acumulado.",
    "Si no se sabe con qué AFP está el usuario se usa una comisión supuesta "
    "del 2% anual, marcada como supuesto en la salida. No es un dato suyo.",
    "El rendimiento por perfil de fondo es el supuesto que más mueve el "
    "resultado. La proyección usa un supuesto PROSPECTIVO de largo plazo "
    "(datos_sistema.RENDIMIENTO_REAL), no lo que los fondos rindieron: el "
    "futuro es supuesto, el pasado es dato, y aquí se proyecta el futuro.",
    "Lo que los fondos rindieron de verdad entre marzo de 2011 y octubre de "
    "2024 es otra cifra, y en dos perfiles es MENOR que la proyectada. Para "
    "verla al lado del supuesto, usar proyectar_aporte_voluntario_en_rango, "
    "que entrega las dos etiquetadas.",
    "El rango observado es POR ADMINISTRADORA, no dispersión de mercado: la "
    "diferencia entre sus extremos es con cuál AFP está el usuario.",
    "El supuesto prospectivo SÍ asume que a más riesgo va más rendimiento; la "
    "evidencia observada NO lo respalda (el moderado rindió menos que el "
    "conservador en el único periodo medido). Por eso el módulo no sugiere "
    "cambiar de perfil de fondo como palanca: eso sería recomendar un "
    "portafolio apoyándose en un supuesto, no en el dato.",
    "El ahorro en impuestos usa el ingreso anual como si ya fuera la base "
    "gravable, sin depuraciones. Es un orden de magnitud, no una liquidación.",
    "Este módulo entrega CAPITAL. La conversión a mesada usa el factor de "
    "rais.py, que hoy se entrega como banda, y no se calcula aquí.",
    "No se compara contra inversiones por fuera del sistema pensional ni se "
    "recomienda ningún producto financiero (decisión de alcance del proyecto).",
]


# ---------------------------------------------------------------------------
# 9. Presentación en terminal (para leer rápido, NO es el mensaje al usuario)
# ---------------------------------------------------------------------------

def porcentaje(valor, decimales=2):
    """Formatea 0.039 como 3,90% (coma decimal, formato colombiano)."""
    if valor is None:
        return "sin dato"
    texto = f"{valor * 100:.{decimales}f}"
    return texto.replace(".", ",") + "%"


def imprimir_evaluacion(r):
    """Imprime la evaluación de un aporte voluntario. El agente redacta con el
    system-prompt, no copiando este texto."""
    print("=" * 78)
    print("APORTE VOLUNTARIO")
    print("=" * 78)
    print()

    # Caso RPM: la negativa se imprime completa, sin ninguna cifra
    if not r["aplica"]:
        print(f"  Régimen: {r['regimen']}. NO APLICA.")
        print(f"  {r['motivo']}")
        print()
        print("  Lo que sí existe:")
        for p in r["palancas_que_si_existen"]:
            print(f"    - {p}")
        print()
        print(f"  {r['advertencia']}")
        print()
        return

    p = r["proyeccion"]
    com = p["comision"]
    print(f"  Destino: {r['destino_explicado']}")
    print(f"  Perfil de fondo: {p['perfil']} "
          f"(rendimiento real {porcentaje(p['rendimiento_real_anual'], 1)})")
    print(f"  Horizonte: {p['meses']} meses")
    print()
    print(f"  Aporte único hoy:        {pesos(p['aporte_unico'])}")
    print(f"  Aporte mensual:          {pesos(p['aporte_mensual'])}")
    print(f"  Total que sale del bolsillo: {pesos(p['total_aportado'])}")
    print()
    print(f"  Capital al final:        {pesos(p['capital_final'])}")
    print(f"  Rendimiento ganado:      {pesos(p['rendimiento_ganado'])}")
    # El porcentaje se imprime con coma decimal, no con punto (formato local)
    parte = (str(p["comision_sobre_capital_pct"]).replace(".", ",")
             if p["comision_sobre_capital_pct"] is not None else "sin dato")
    print(f"  Comisión pagada:         {pesos(p['comision_pagada'])} "
          f"({parte}% de lo que habría acumulado)")
    marca = " (SUPUESTO, no es la comisión de su AFP)" if com["es_supuesto"] else ""
    print(f"  Comisión anual aplicada: {porcentaje(com['pct_anual'])}{marca}")
    print(f"    Fuente: {com['fuente']}")
    print()

    b = r.get("beneficio_tributario_primer_anio")
    if b:
        print("  BENEFICIO TRIBUTARIO DEL PRIMER AÑO")
        print(f"    Aporte del año:        {pesos(b['aporte_anual'])}")
        print(f"    Con beneficio:         {pesos(b['aporte_con_beneficio'])}")
        print(f"    Sin beneficio (pasa del cupo): "
              f"{pesos(b['aporte_sin_beneficio'])}")
        print(f"    Ahorro en impuestos:   {pesos(b['ahorro_en_impuestos'])}")
        print(f"    Tope que muerde:       {b['cupo']['tope_que_muerde']}")
        print(f"    Norma:                 {b['cupo']['norma']}")
        print()
        c = b["condiciones"]
        print(f"    Permanencia mínima: {c['permanencia_minima']}")
        print(f"    {c['penalidad']}")
        print()
    elif r.get("falta_dato"):
        print(f"  BENEFICIO TRIBUTARIO: {r['falta_dato']}")
        print()

    print(f"  {r['conversion_a_mesada']}")
    print()
    print("  SUPUESTOS:")
    for s in r["supuestos"]:
        print(f"    - {s}")
    print()
    print(f"  FRONTERA: {r['frontera']}")
    print()


def imprimir_alternativas(t):
    """Imprime la tabla de accionabilidad de las palancas pensionales."""
    print("=" * 78)
    print(f"ALTERNATIVAS PENSIONALES ({t['regimen']})")
    print("=" * 78)
    print()
    print("  DISPONIBLES:")
    for a in t["disponibles"]:
        print(f"    + {a['alternativa']}")
        print(f"      {a['motivo']}")
    print()
    print("  DESCARTADAS (el 'no se puede' dicho a tiempo):")
    for a in t["descartadas"]:
        print(f"    - {a['alternativa']}")
        print(f"      {a['motivo']}")
    print()
    print(f"  {t['nota']}")
    print()


def main():
    """CLI mínima.

    Ejemplos:
      python3 aportes_voluntarios.py --regimen RAIS --meses 120 \\
          --aporte-mensual 500000 --ingreso-anual 180000000 --afp porvenir
      python3 aportes_voluntarios.py --regimen RPM --meses 120 \\
          --aporte-mensual 500000
    """
    import argparse

    p = argparse.ArgumentParser(
        description="Aporte voluntario en RAIS: capital, comisión e impuestos.")
    p.add_argument("--regimen", required=True, choices=["RAIS", "RPM"],
                   help="Régimen del afiliado. En RPM el módulo se niega.")
    p.add_argument("--meses", type=int, required=True,
                   help="Meses que faltan hasta pensionarse")
    p.add_argument("--aporte-mensual", type=float, default=0,
                   help="Aporte periódico mensual, en pesos de hoy")
    p.add_argument("--aporte-unico", type=float, default=0,
                   help="Aporte de una sola vez, hoy, en pesos de hoy")
    p.add_argument("--destino", default="obligatoria",
                   choices=["obligatoria", "voluntaria"],
                   help="Cuenta obligatoria de la AFP o fondo de voluntarias")
    p.add_argument("--perfil", default="moderado",
                   choices=["conservador", "moderado", "mayor_riesgo"])
    p.add_argument("--afp", default=None,
                   help="porvenir o proteccion. Sin esto se usa un supuesto.")
    p.add_argument("--ingreso-anual", type=float, default=None,
                   help="Ingreso anual, para estimar el ahorro en impuestos")
    p.add_argument("--anio", type=int, default=None, help="Año gravable")
    p.add_argument("--alternativas", action="store_true",
                   help="Imprime además la tabla de palancas accionables")
    args = p.parse_args()

    r = evaluar_aporte_voluntario(
        args.regimen, args.meses, ingreso_anual=args.ingreso_anual,
        aporte_mensual=args.aporte_mensual, aporte_unico=args.aporte_unico,
        destino=args.destino, perfil=args.perfil, afp=args.afp, anio=args.anio)
    imprimir_evaluacion(r)

    if args.alternativas:
        # Con excedente para aportar, se asume capacidad de pago
        capacidad = bool(args.aporte_mensual or args.aporte_unico)
        imprimir_alternativas(
            comparar_alternativas_pensionales(args.regimen, capacidad))


if __name__ == "__main__":
    main()
