# Datos del sistema pensional colombiano que usa la calculadora.
# REGLA DE ORO: aquí solo entran valores verificados contra fuentes oficiales
# (ver kit-contexto/supuestos-actuariales.md). Si un dato no está verificado,
# NO se inventa: la calculadora reporta "no disponible" y lo marca como pendiente.

# Salario mínimo mensual legal vigente (SMLMV) por año, en pesos colombianos.
# Fuente: decretos anuales; 2026 verificado (Decretos 1469 y 1470 de 2025).
SMLMV = {
    1992: 65_190,
    1993: 81_510,
    1994: 98_700,
    1995: 118_934,
    1996: 142_125,
    1997: 172_005,
    1998: 203_825,
    1999: 236_438,
    2000: 260_100,
    2001: 286_000,
    2002: 309_000,
    2003: 332_000,
    2004: 358_000,
    2005: 381_500,
    2006: 408_000,
    2007: 433_700,
    2008: 461_500,
    2009: 496_900,
    2010: 515_000,
    2011: 535_600,
    2012: 566_700,
    2013: 589_500,
    2014: 616_000,
    2015: 644_350,
    2016: 689_455,
    2017: 737_717,
    2018: 781_242,
    2019: 828_116,
    2020: 877_803,
    2021: 908_526,
    2022: 1_000_000,
    2023: 1_160_000,
    2024: 1_300_000,
    2025: 1_423_500,
    2026: 1_750_905,
}

# Inflación anual (IPC diciembre a diciembre) por año, en porcentaje.
# Fuente: DANE (serie 1993-2014 cotejada en dos fuentes secundarias que citan
# al DANE; chequear contra el archivo oficial del DANE antes del piloto).
IPC = {
    1993: 22.60,
    1994: 22.59,
    1995: 19.46,
    1996: 21.63,
    1997: 17.68,
    1998: 16.70,
    1999: 9.23,
    2000: 8.75,
    2001: 7.65,
    2002: 6.99,
    2003: 6.49,
    2004: 5.50,
    2005: 4.85,
    2006: 4.48,
    2007: 5.69,
    2008: 7.67,
    2009: 2.00,
    2010: 3.17,
    2011: 3.73,
    2012: 2.44,
    2013: 1.94,
    2014: 3.66,
    2015: 6.77,
    2016: 5.75,
    2017: 4.09,
    2018: 3.18,
    2019: 3.80,
    2020: 1.61,
    2021: 5.62,
    2022: 13.12,
    2023: 9.28,
    2024: 5.20,
    2025: 5.10,
}

# Edad de pensión de vejez en el RPM (Ley 100 art. 33, mod. Ley 797/2003).
EDAD_PENSION = {"F": 57, "M": 62}

# Semanas mínimas para pensión de vejez.
# Hombres: 1.300 fijas. Mujeres: tabla por año (Sentencia C-197 de 2023).
SEMANAS_HOMBRE = 1300
SEMANAS_MUJER_POR_ANIO = {
    2025: 1300,
    2026: 1250,
    2027: 1225,
    2028: 1200,
    2029: 1175,
    2030: 1150,
    2031: 1125,
    2032: 1100,
    2033: 1075,
    2034: 1050,
    2035: 1025,
    # De 2036 en adelante: 1.000 (la función semanas_requeridas lo maneja)
}
SEMANAS_MUJER_DESDE_2036 = 1000

# Mesadas al año (Acto Legislativo 01 de 2005: 13 para pensiones nuevas).
MESADAS = 13

# --- Parámetros del RAIS (fondos privados), ver kit-contexto/reglas-rais.md ---

# De cada peso cotizado (16%), lo que de verdad entra a la cuenta del afiliado
# es el 11,5%. El resto es garantía de pensión mínima y comisión. [VERIFICAR]
APORTE_A_CUENTA_RAIS = 0.115

# Semanas para la Garantía de Pensión Mínima en RAIS (Ley 100 art. 65).
# Hombres: 1.150 fijas. Mujeres: bajan 15 semanas por año desde 2026 hasta
# llegar a 1.000, por la Sentencia C-054 de 2024 (verificada 2026-07-21).
# La Corte declaró inexequible la exigencia de 1.150 semanas "en relación con
# sus efectos para las mujeres", difirió los efectos al 31 de diciembre de 2025
# y fijó esta regla supletiva, que opera porque el Congreso no legisló.
SEMANAS_GPM = 1150          # Hombres (y valor base de la reducción)
SEMANAS_GPM_MUJER_PISO = 1000
SEMANAS_GPM_REDUCCION_ANUAL = 15
SEMANAS_GPM_ANIO_INICIO = 2026

# Capital suficiente = financiar una renta de al menos 110% del salario mínimo
# (Ley 100 art. 64: permite pensionarse a cualquier edad).
CAPITAL_MINIMO_PCT = 1.10

# Interés técnico real, para convertir capital ahorrado en mesada mensual.
# FUENTE CONFIRMADA (2026-07-21): Circular Básica Jurídica de la Superfinanciera,
# Parte II, Título III, Capítulo I, numeral 2: las administradoras del SGP y las
# aseguradoras deben emplear "un interés técnico real del 4%" en los cálculos que
# usan tablas de mortalidad. Queda descartado que el 4% viniera de Chile.
#
# PERO OJO, el 4% es la tasa de RESERVA del sistema, no el precio de mercado de
# una renta vitalicia. Para mesadas cercanas a 1 SMLMV el modelo se queda corto,
# porque esa mesada sube cada año con el salario mínimo (que crece más que el
# IPC) y eso encarece mucho la renta. Efecto medido: el factor de este modelo da
# ~182 y el implícito de mercado ~268 para un hombre a los 62, así que la
# pensión anticipada del caso-03 pasaría de los 35 a los 39 años.
#
# DESDE EL 2026-07-27 ESTE 4% YA NO VIAJA SOLO: es el EXTREMO OPTIMISTA de una
# banda (decisiones 1 y 2 de Santiago). El extremo conservador está abajo.
INTERES_TECNICO = 0.04

# Años de expectativa de vida residual al llegar a la edad de pensión.
# VALORES EXACTOS, verificados el 2026-07-27 sobre la tabla oficial completa de
# la Resolución 1555 de 2010 de la Superfinanciera (rentistas válidos,
# experiencia 2005-2008), leída directamente del PDF. Confianza: ALTA.
# Mujer a los 57 años: 29,7. Hombre a los 62 años: 21,3.
# Antes estaban redondeados a 29 y 21. El cambio baja las mesadas RAIS un 0,9%
# y NO mueve la edad de pensión anticipada; acerca el modelo al simulador de
# Protección (la validación pasa de +4,9% a cerca de +3,9%).
# Tabla por edades en ../kit-contexto/supuestos-actuariales.md marca 3.
# No confundir con la RV08 de inválidos ni con las tablas del DANE.
EXPECTATIVA_VIDA = {"F": 29.7, "M": 21.3}

# ---------------------------------------------------------------------------
# BANDA DEL FACTOR DE CONVERSIÓN DE CAPITAL A MESADA
# Decisiones 1 y 2 de Santiago (2026-07-27). Aplicada el 2026-07-27.
# ---------------------------------------------------------------------------
# El problema en una frase: convertir un saldo en mesada exige un PRECIO de renta
# vitalicia, y ese precio no está fijado por norma. Son tres tasas distintas:
#   (a) interés técnico del SGP, 4% real, que es norma (Circular Básica Jurídica);
#   (b) reserva matemática de la aseguradora (Decreto 2555 art. 2.31.4.3.2);
#   (c) el precio que la aseguradora le ofrece al usuario, que fija cada una en
#       su nota técnica y NO está en ninguna norma.
# Lo que el usuario necesita saber es (c), y de (c) no hay fuente oficial. Por eso
# la calculadora deja de dar un punto y da una BANDA entre dos extremos.
#
# EXTREMO OPTIMISTA: el 4% normativo. Es lo que la calculadora daba antes de este
# cambio, así que todas las cifras históricas del proyecto siguen siendo el borde
# superior de la banda nueva. Confianza de la fuente: ALTA (norma citada arriba).
#
# EXTREMO CONSERVADOR: el factor implícito de MERCADO. Confianza: BAJA.
#   Procedencia: nota de prensa de Infobae del 14 de enero de 2026 que cita el
#   Decreto 1485 de 2025, con el capital que hoy exige una renta vitalicia de un
#   salario mínimo. NO es fuente oficial y NO se pudo verificar en fuente
#   primaria: el precio de venta de las rentas vitalicias no se publica.
#   Esto se DECLARA en la salida del diagnóstico, no se esconde.
#
# De esos capitales sale el factor dividiendo por el salario mínimo del año.
# Para el hombre da 470.000.000 / 1.750.905 = 268,4, que coincide con el ~268 que
# venía citando el proyecto desde la investigación del 2026-07-21. Para la mujer
# es un ancla NUEVA: antes se extrapolaba con la tasa del hombre.
#
# CIFRA QUE NO SE DEBE CITAR COMO OFICIAL: el "14%" de encarecimiento que circula
# en prensa no aparece en el decreto ni en ningún documento oficial. Es una cifra
# derivada por el medio a partir de estos capitales. Aquí se recalcula desde los
# capitales, y da 14,3% para hombres y 15,3% para mujeres, no un 14% parejo.
CAPITAL_RV_UN_SMLMV = {
    # Capital que exige una renta vitalicia de 1 SMLMV, en pesos de cada año
    2026: {"M": 470_000_000, "F": 504_000_000},   # Precio de mercado vigente
    2027: {"M": 537_000_000, "F": 581_000_000},   # Ya con el Decreto 1485
}
# La edad a la que corresponde cada capital NO la dice la fuente. Se supone la
# edad legal de pensión de cada sexo (62 y 57). Supuesto declarado, no verificado.
EDAD_CAPITAL_RV = {"M": 62, "F": 57}

# QUÉ CAMBIA EL DECRETO 1485 DE 2025, verificado el 2026-07-27.
# Publicado el 31 de diciembre de 2025, vigente desde el 1 de enero de 2026,
# sustituye el Título 17 del Decreto 1833 de 2016. Obliga a las aseguradoras a
# proyectar el crecimiento anual de la mesada de las rentas vitalicias inmediata
# y diferida con el mayor valor entre la productividad promedio de los últimos 10
# años y el 35% del IPC promedio de los últimos 10 años (datos de la Oficina de
# Bonos Pensionales del Ministerio de Hacienda), y elimina la cobertura completa
# del Estado sobre el componente político de los incrementos del salario mínimo.
# ALCANCE: aplica a rentas vitalicias y pólizas NUEVAS desde 2027. Los
# pensionados y afiliados actuales no se afectan.
# Confianza: MEDIA. Confirmado en compilación oficial alterna (CER Latam sobre el
# texto de MinHacienda); el SUIN Juriscol falló por error de certificado, así que
# el texto literal crudo no se leyó.
ANIO_DECRETO_1485 = 2027     # Desde qué año de pensión aplica el precio nuevo

# Dónde muerde de verdad el extremo conservador: la referencia de mercado se
# construyó sobre una mesada cercana a 1 SMLMV, que es donde el precio se dispara
# porque esa mesada se reajusta cada año con el salario mínimo (que sube más que
# el IPC). Para mesadas altas la validación contra el simulador de Protección dio
# +4,9% con el 4% normativo, o sea que ahí el precio real se parece más al extremo
# OPTIMISTA. La banda se aplica igual en todas partes (decisión 2 de Santiago:
# "si el factor es incierto, lo es en todas partes"), pero esta asimetría se
# declara junto a las cifras para que nadie lea el piso como una predicción.
BANDA_CALIBRADA_CERCA_DE_UN_SMLMV = True


def tasa_implicita(factor, anios_esperados, mesadas=MESADAS,
                   minimo=-0.05, maximo=0.20):
    """Qué tasa de descuento anual produce ese factor de conversión.

    Sirve para traducir un factor observado en el mercado (por ejemplo 268) a una
    tasa, y poder aplicar esa misma tasa a cualquier edad y sexo en vez de tener
    una cifra suelta que solo vale para un hombre de 62 años.
    Se resuelve por bisección: se prueba una tasa, se mira si el factor que sale
    es muy alto o muy bajo, y se va partiendo el intervalo a la mitad.
    Devuelve None si el factor pedido queda fuera del rango de tasas explorado.
    """
    def factor_de(i):
        # Valor presente de recibir 1 peso, 13 veces al año, durante n años
        if abs(i) < 1e-12:
            return mesadas * anios_esperados      # Sin descuento es la suma pelada
        return mesadas * (1 - (1 + i) ** -anios_esperados) / i

    # A mayor tasa, menor factor: si el objetivo no cae entre los dos bordes,
    # no se inventa un resultado
    if not (factor_de(maximo) <= factor <= factor_de(minimo)):
        return None
    bajo, alto = minimo, maximo
    for _ in range(200):
        medio = (bajo + alto) / 2
        if factor_de(medio) > factor:
            bajo = medio          # El factor sale muy alto: hay que subir la tasa
        else:
            alto = medio          # El factor sale muy bajo: hay que bajar la tasa
    return (bajo + alto) / 2


# ---------------------------------------------------------------------------
# VECTOR TMR DE LA SUPERFINANCIERA: la única pieza de fuente PRIMARIA que hay
# sobre el precio de una renta vitalicia. Incorporado el 2026-07-27.
# ---------------------------------------------------------------------------
# QUÉ ES Y QUÉ NO ES, y esto hay que tenerlo claro antes de usarlo. La TMR es la
# tasa con la que la aseguradora calcula su RESERVA MATEMÁTICA (Decreto 2555
# art. 2.31.4.3.2): es la tasa (b) de las tres que distingue el proyecto. NO es
# el precio que le ofrecen al usuario, que es la (c) y sigue SIN publicarse: lo
# fija cada aseguradora en su nota técnica. Que la TMR venga de fuente primaria
# no la convierte en precio de venta.
#
# PARA QUÉ SIRVE ENTONCES: como COTA. Una aseguradora no puede vender una renta
# más barata que la reserva que debe constituir, porque perdería plata en el
# momento de la venta. Así que el precio real es MAYOR O IGUAL que el que sale de
# la TMR, y la tasa implícita en el precio es MENOR O IGUAL que la TMR real. La
# calculadora la usa como piso del precio, no como el precio.
#
# FUENTE: Superintendencia Financiera, Carta Circular 038 del 8 de julio de 2026,
# corte al 30 de junio de 2026, anexo en Excel. Confianza: VERIFICADA EN FUENTE
# PRIMARIA (archivo oficial descargado y leído).
# Archivos: ../fuentes-datos/SFC-carta-circular-038-2026-anexo-TMR.xlsx y el PDF
# de la carta. El anexo trae 120 plazos, de 1 a 120 años, con TMR nominal e
# inflación implícita.
#
# MANTENIMIENTO, TRIMESTRAL Y MECÁNICO: la SFC publica una Carta Circular nueva
# cada trimestre (cortes a 31 de marzo, 30 de junio, 30 de septiembre y 31 de
# diciembre), y la carta sale entre 7 y 9 días después del cierre. La siguiente
# se espera alrededor del 7 al 9 de octubre de 2026. Es pública y sin login. Para
# actualizar: bajar el anexo, recalcular la tasa real de cada plazo como
# (1 + TMR) / (1 + inflación implícita) - 1, y reemplazar la tabla de abajo.
#
# TRAMPA DEL ANEXO, VERIFICADA A MANO EL 2026-07-27: la columna de inflación
# implícita NO es dato de mercado en todos los plazos. Se topa en 3,00% desde el
# plazo 30 en adelante, que es un supuesto de largo plazo, y el plazo 29 ya está
# en transición (4,44%). El ÚLTIMO PLAZO LIMPIO ES EL 28. Calcular la tasa real
# más allá del 28 con esa columna da resultados absurdos: 2,07% real en el plazo
# 29 y 3,49% en el 30, contra 0,63% en el 28. Por eso la tabla llega hasta 28.
TMR_REAL_POR_PLAZO = {
    15: 0.007489,
    16: 0.007351,
    17: 0.00722,
    18: 0.007097,
    19: 0.006982,
    20: 0.006876,
    21: 0.006777,
    22: 0.006685,
    23: 0.0066,
    24: 0.006521,
    25: 0.006448,
    26: 0.00638,
    27: 0.006316,
    28: 0.006257,
}
TMR_PLAZO_MAXIMO_LIMPIO = 28
TMR_FUENTE = (
    "Superintendencia Financiera, Carta Circular 038 del 8 de julio de 2026, "
    "corte al 30 de junio de 2026, anexo en Excel. Tasa real calculada como "
    "(1 + TMR) / (1 + inflación implícita) - 1 del mismo plazo. Confianza: "
    "VERIFICADA EN FUENTE PRIMARIA (archivo oficial leído). Se actualiza cada "
    "trimestre"
)
TMR_QUE_ES = (
    "tasa de la RESERVA MATEMÁTICA de la aseguradora (Decreto 2555 art. "
    "2.31.4.3.2), no el precio de venta de la renta vitalicia. El precio que le "
    "ofrecen al usuario no está publicado. Se usa como COTA: nadie vende una "
    "renta más barata que la reserva que debe constituir"
)


def tmr_real(anios):
    """Tasa real de la TMR para un plazo en años, sin salirse de la zona limpia.

    Los plazos que no son enteros se redondean, y los que pasan del último plazo
    con inflación implícita de verdad (28 años) se topan ahí. Topar es lo
    correcto y no una comodidad: más allá la columna de inflación del anexo trae
    un supuesto de 3,00% que no es dato de mercado. La curva es muy plana en esa
    zona (0,65% en el plazo 25 contra 0,63% en el 28), así que topar apenas mueve
    el resultado, y se declara en la salida.
    """
    plazo = min(max(int(round(anios)), min(TMR_REAL_POR_PLAZO)),
                TMR_PLAZO_MAXIMO_LIMPIO)
    return TMR_REAL_POR_PLAZO[plazo]


def factor_tmr(sexo):
    """Factor de conversión que sale de la TMR, o sea el PISO del precio."""
    anios = EXPECTATIVA_VIDA[sexo]
    i = tmr_real(anios)
    return MESADAS * (1 - (1 + i) ** -anios) / i


def factor_mercado(sexo, anio_pension=None):
    """Factor de conversión que se observa en el mercado, por sexo y año.

    Se calcula dividiendo el capital que exige una renta vitalicia de un salario
    mínimo entre ese salario mínimo. Desde 2027 se aplica el precio ya encarecido
    por el Decreto 1485; antes, el precio vigente en 2026.
    El encarecimiento se aplica como PROPORCIÓN (14,3% en hombres, 15,3% en
    mujeres) y no con el capital de 2027 en crudo, porque la calculadora trabaja
    en pesos de hoy y mezclar pesos de dos años daría un número sin sentido.
    """
    # Dos observaciones del precio, y se toma la MÁS CARA: el capital que
    # reporta la prensa y el piso que impone la reserva matemática (TMR). Más
    # factor es más caro, así que el máximo es el extremo conservador honesto.
    # Para el hombre gana la prensa (268,4 contra 258,6 de la TMR), que es lo
    # esperado: el precio de venta lleva margen sobre la reserva. Para la mujer
    # gana la TMR, y eso DESMIENTE el dato de prensa: 287,9 de prensa contra
    # 352,4 de la TMR significaría vender por debajo de la reserva, que ninguna
    # aseguradora hace. Ver INCONSISTENCIA_ANCLAS_POR_SEXO más abajo.
    base = max(CAPITAL_RV_UN_SMLMV[2026][sexo] / SMLMV[2026], factor_tmr(sexo))
    if anio_pension is not None and anio_pension >= ANIO_DECRETO_1485:
        encarecimiento = (CAPITAL_RV_UN_SMLMV[2027][sexo]
                          / CAPITAL_RV_UN_SMLMV[2026][sexo])
        return base * encarecimiento
    return base


def factor_solo_prensa(sexo):
    """El factor que sale solo del capital de prensa, sin la cota de la TMR.

    Existe para poder comparar las dos observaciones entre sí y declarar cuál
    mandó en cada sexo. No se usa para calcular mesadas.
    """
    return CAPITAL_RV_UN_SMLMV[2026][sexo] / SMLMV[2026]


def interes_mercado(sexo, anio_pension=None):
    """Tasa real implícita en el factor de mercado, por sexo y año de pensión.

    Sale por debajo del 4% normativo justamente porque el precio de mercado es
    MÁS CARO: más capital por el mismo peso de mesada equivale a descontar a una
    tasa más baja. Se despeja del factor observado para poder aplicarla a
    cualquier edad, que es lo que necesita la pensión anticipada.
    """
    return tasa_implicita(factor_mercado(sexo, anio_pension),
                          EXPECTATIVA_VIDA[sexo])


# Valor de referencia del hombre a los 62, que es el que el proyecto viene
# citando desde el 2026-07-21. Se conserva como constante para no romper nada.
FACTOR_MERCADO_REFERENCIA = round(factor_mercado("M"), 1)
FACTOR_MERCADO_REFERENCIA_SEXO = "M"
FACTOR_MERCADO_REFERENCIA_EDAD = EDAD_CAPITAL_RV["M"]
INTERES_MERCADO = interes_mercado("M")

# INCONSISTENCIA DE LA PRENSA, YA CON VEREDICTO DE FUENTE PRIMARIA (2026-07-27).
# Los dos capitales de prensa no se dejan reproducir con una sola tasa: la mujer
# vive 8,4 años más que el hombre (29,7 contra 21,3, un 39% más) y su renta
# costaría apenas un 7% más. Eso daba tasas implícitas de 0,28% (hombre) y 2,03%
# (mujer). Cuando llegó el vector TMR de la Superfinanciera, la duda se resolvió
# en buena parte: la TMR real está entre 0,63% y 0,68% en esos plazos.
#   - El hombre queda POR DEBAJO de la TMR (0,28% contra 0,68%), que es lo
#     coherente: el precio de venta lleva margen sobre la reserva. Su ancla de
#     prensa se conserva.
#   - La mujer quedaba POR ENCIMA (2,03% contra 0,63%), lo que significaría
#     vender por debajo de la reserva matemática. Ninguna aseguradora lo hace.
#     El dato de prensa de la mujer NO se sostiene, y se reemplaza por la cota
#     de la TMR, que la encarece.
# Lo que sigue sin saberse es de dónde salió la cifra de 504 millones: puede ser
# otra edad, otra cobertura de beneficiarios u otra tabla. Sigue siendo pregunta
# para el actuario, pero ya no es la calculadora la que tiene que decidir a
# ciegas: manda la cota de fuente primaria.
INCONSISTENCIA_ANCLAS_POR_SEXO = True

# Etiquetas que la calculadora imprime junto a cada extremo. Van aquí y no en el
# código de cálculo para que la fuente viaje pegada a la cifra.
FUENTE_FACTOR = {
    "optimista": {
        "tasa": INTERES_TECNICO,
        "nombre": "interés técnico normativo del 4%",
        "fuente": ("Circular Básica Jurídica de la Superfinanciera, Parte II, "
                   "Título III, Capítulo I, numeral 2"),
        "confianza": "ALTA (norma verificada el 2026-07-21)",
        "advertencia": ("es la tasa de RESERVA del sistema, no el precio que "
                        "cobra una aseguradora por una renta vitalicia"),
    },
    "conservador": {
        "tasa": INTERES_MERCADO,
        "nombre": "factor implícito de mercado",
        "fuente": ("el mayor de dos observaciones: (1) capital que exige una "
                   "renta vitalicia de un salario mínimo, según Infobae del 14 "
                   "de enero de 2026 citando el Decreto 1485 de 2025, que NO es "
                   "fuente oficial; y (2) el piso que impone la reserva "
                   "matemática, con el vector TMR de la Carta Circular 038 de "
                   "2026 de la Superfinanciera, que SÍ es fuente primaria"),
        "confianza": ("MEDIA. El piso viene de fuente primaria verificada; la "
                      "estimación del precio de venta sigue apoyada en prensa, "
                      "porque ese precio no se publica"),
        "advertencia": ("calibrado sobre una mesada cercana a 1 SMLMV, que es "
                        "donde el precio de mercado se dispara; para mesadas "
                        "altas el precio real se acerca más al otro extremo"),
    },
}

# ---------------------------------------------------------------------------
# RENDIMIENTO REAL POR PERFIL DE FONDO: RECALIBRADO A RANGO EL 2026-07-27
# ---------------------------------------------------------------------------
# Decisión de Santiago del 2026-07-27: se recalibra A RANGO, no a punto.
# Los supuestos viejos (conservador 2%, moderado 4%, mayor riesgo 5%) quedaban
# los tres FUERA del rango observado, y ni siquiera en la misma dirección: el
# conservador subestimaba y los otros dos sobreestimaban. El moderado se salía
# por encima del techo del rango, que es el peor sitio para equivocarse porque
# es el perfil por defecto de buena parte de los afiliados.
#
# FUENTE, hasta el 2026-09-18: Superintendencia Financiera, periodo marzo 2011 a
# octubre 2024, vía El Colombiano del 15 de enero de 2025, confianza MEDIA. Esa
# fuente se REEMPLAZÓ el 2026-09-18 por el dato primario. La construcción a
# rango, que es la decisión de Santiago del 2026-07-27, se mantiene igual: lo
# único que cambió son los números y su confianza. Ver abajo.
# ACTUALIZADO EL 2026-09-18: estas cifras ya NO vienen de prensa.
#
# De dónde salen ahora. Del dato primario DIARIO de la Superfinanciera,
# publicado en datos.gov.co (dataset `hds9-4524`, propiedad de la SFC, con
# frecuencia de actualización diaria, verificada el 2026-09-18). Se bajó la
# serie completa, se derivó el valor de la unidad de cada fondo (el dataset no
# lo publica: es el valor del fondo en pesos dividido por el número de
# unidades), se tomó el cierre de cada mes y se anualizó geométricamente. La
# inflación para pasar de nominal a real es el índice del DANE que publica el
# Banco de la República. El script está en `analisis/rendimiento_afp.py` y se
# puede volver a correr.
#
# POR QUÉ ESTO ES MEJOR QUE LO QUE HABÍA, y son tres razones:
#   1. Es dato primario, no una nota de prensa que cita a la SFC. Confianza ALTA.
#   2. Las cuatro AFP comparten EXACTAMENTE el mismo periodo (140 cierres
#      mensuales, enero de 2015 a agosto de 2026), así que el rango de verdad
#      compara administradoras entre sí. Las cifras de prensa mezclaban
#      periodos distintos por fondo, así que su rango comparaba peras con manzanas.
#   3. Se puede reproducir y auditar. La cifra anterior no.
#
# POR QUÉ ES LA MEDIDA CORRECTA PARA ESTA CALCULADORA. Es la rentabilidad DEL
# FONDO, no la del afiliado: no descuenta la comisión de administración ni el
# seguro previsional. Y así tiene que ser, porque esta calculadora ya los
# descuenta antes, en `APORTE_A_CUENTA_RAIS` (de cada peso cotizado solo entra
# a la cuenta el 11,5%). Si además se descontaran aquí, se estarían cobrando
# dos veces.
#
# QUÉ SIGNIFICA ESTE RANGO, Y ES LO QUE MÁS IMPORTA: es un rango POR
# ADMINISTRADORA, no una banda de riesgo de mercado. La distancia entre los dos
# extremos no es "cómo le puede ir a la bolsa", es CON CUÁL AFP ESTÁ EL USUARIO.
RENDIMIENTO_REAL_OBSERVADO = {
    "conservador": (0.0193, 0.0211),      # peor Protección, mejor Porvenir
    "moderado": (0.0227, 0.0325),         # peor Colfondos, mejor Porvenir
    "mayor_riesgo": (0.0331, 0.0413),     # peor Protección, mejor Colfondos
}

# Los últimos 5 años, aparte. NO los usa la proyección, y por una razón: cinco
# años es una ventana corta y la inflación de 2021 a 2026 (7,91% anualizada) fue
# excepcional. Pero el dato importa y no se esconde, porque dice algo fuerte:
# en ese periodo los portafolios defensivos DESTRUYERON valor real. Todo el
# conservador rindió menos del 1% real, y el moderado de una AFP quedó negativo.
RENDIMIENTO_REAL_ULTIMOS_5_ANIOS = {
    "conservador": (0.0039, 0.0088),
    "moderado": (-0.0047, 0.0104),
    "mayor_riesgo": (0.0200, 0.0237),
}

# La serie que se reemplazó, conservada para poder reconstruir con qué números
# se calculó un diagnóstico anterior al 2026-09-18. No se usa.
RENDIMIENTO_REAL_OBSERVADO_ANTERIOR = {
    "conservador": (0.0253, 0.0269),
    "moderado": (0.0197, 0.0315),
    "mayor_riesgo": (0.0288, 0.0425),
}

# Nombre viejo, conservado para no romper a quien ya lo importaba.
RENDIMIENTO_REAL_RANGO = RENDIMIENTO_REAL_OBSERVADO

FUENTE_RENDIMIENTO = (
    "Superintendencia Financiera de Colombia, dato primario diario del dataset "
    "hds9-4524 de datos.gov.co, periodo enero de 2015 a agosto de 2026 (140 "
    "cierres mensuales, el mismo periodo para las cuatro AFP). Valor de la "
    "unidad derivado del valor del fondo entre el número de unidades; "
    "anualización geométrica; inflación del índice DANE publicado por el Banco "
    "de la República (5,85% anualizado en el periodo). Rango POR ADMINISTRADORA, "
    "no promedio ponderado del sistema. Es rentabilidad DEL FONDO, no del "
    "afiliado: la comisión ya se descuenta en APORTE_A_CUENTA_RAIS. Confianza "
    "ALTA (fuente primaria, reproducible con analisis/rendimiento_afp.py)"
)

FUENTE_RENDIMIENTO_ANTERIOR = (
    "Hasta el 2026-09-18 se usó: Superintendencia Financiera, periodo marzo 2011 "
    "a octubre 2024, vía El Colombiano del 15 de enero de 2025. Confianza MEDIA "
    "(fuente secundaria; el dato crudo estaba en un tablero de Power BI no "
    "extraíble). Se reemplazó por el dato primario"
)

ADVERTENCIA_RENDIMIENTO = (
    "la distancia entre los dos extremos NO es riesgo de mercado: es con cuál "
    "AFP está el usuario. Es una palanca accionable, no una incertidumbre que le "
    "toque aguantar. Aun así la calculadora no recomienda administradora"
)

# OJO, NO CONFUNDIR con la rentabilidad MÍNIMA regulatoria que publica la
# Superfinanciera: esa es NOMINAL y es un piso obligatorio, no un rendimiento
# esperado. Mezclarla con estas cifras reales infla el resultado dos veces.

# Punto central observado de cada perfil: el medio de su rango.
RENDIMIENTO_REAL_OBSERVADO_CENTRAL = {
    perfil: round((piso + techo) / 2, 6)
    for perfil, (piso, techo) in RENDIMIENTO_REAL_OBSERVADO.items()}

# LA CONTRADICCIÓN QUE HABÍA, Y QUE EL DATO PRIMARIO RESOLVIÓ (2026-09-18).
#
# Con las cifras de prensa que se usaron hasta el 2026-09-18, el punto central
# del perfil MODERADO (2,56%) quedaba POR DEBAJO del conservador (2,61%): el
# fondo moderado no le ganaba al conservador. Eso era raro, iba contra la
# intuición financiera, y era la razón por la que el supuesto prospectivo de
# abajo se tuvo que construir a mano importando una prima de renta variable de
# una serie mundial, en vez de usar la evidencia colombiana.
#
# Con el dato primario de la Superfinanciera, medido sobre el mismo periodo
# para las cuatro AFP, la contradicción DESAPARECE: conservador 2,02%, moderado
# 2,76%, mayor riesgo 3,72%, en el orden esperado.
#
# Y hay algo más, que es la mejor noticia de este cambio: el supuesto
# prospectivo y la evidencia ahora casi coinciden (moderado 2,90% prospectivo
# contra 2,76% observado, mayor riesgo 3,77% contra 3,72%). O sea que la prima
# importada de la serie mundial reproduce lo que de verdad pasó en Colombia.
# Eso valida el supuesto en vez de debilitarlo, y es la razón para no tocarlo.
#
# Esta bandera se deja calculada y no fija en False a propósito: si mañana se
# actualiza la serie y la contradicción vuelve, el código se da cuenta solo.
MODERADO_NO_SUPERA_A_CONSERVADOR = (
    RENDIMIENTO_REAL_OBSERVADO_CENTRAL["moderado"]
    < RENDIMIENTO_REAL_OBSERVADO_CENTRAL["conservador"])

# ---------------------------------------------------------------------------
# SUPUESTO PROSPECTIVO DE RENDIMIENTO: lo que usa la proyección
# ---------------------------------------------------------------------------
# DECISIÓN DE PRODUCTO DE SANTIAGO, 2026-07-28. No se reabre.
# Qué decidió: la proyección usa un supuesto de LARGO PLAZO en el que el fondo
# moderado sí rinde más que el conservador. Su argumento: a horizontes de varias
# décadas, más exposición a renta variable debe pagar más, y el periodo 2011-2024
# es una ventana, no el largo plazo.
#
# QUÉ ES ESTO Y QUÉ NO ES. `RENDIMIENTO_REAL_OBSERVADO` es EVIDENCIA: lo que
# rindieron los fondos en el periodo medido. Esto de aquí es un SUPUESTO: una
# apuesta sobre el futuro, construida a mano y con eslabones sin verificar. No se
# pueden confundir, y por eso viven en dos constantes con nombres distintos.
# EN EL ÚNICO PERIODO MEDIDO EL ORDEN QUE ESTE SUPUESTO ASUME NO SE CUMPLE.
#
# CÓMO SE CONSTRUYÓ, paso a paso, para que se pueda auditar y discutir:
#
#   Paso 1. ANCLA en el dato colombiano observado. El perfil conservador se deja
#   en su punto central observado (2,61%). Es el perfil donde una ventana de 13
#   años distorsiona menos, porque su cartera es sobre todo renta fija, cuyo
#   rendimiento de largo plazo se parece más al del periodo medido.
#   Fuente: la misma de RENDIMIENTO_REAL_OBSERVADO. Confianza MEDIA.
#
#   Paso 2. PRIMA DE RENTA VARIABLE de largo plazo: 3,5 puntos porcentuales
#   reales por encima de los bonos. Sale de la serie mundial de 125 años
#   (1900-2024): renta variable 5,2% real anual contra bonos 1,7% real anual.
#   Fuente: Dimson, Marsh y Staunton, Global Investment Returns Yearbook 2025
#   (London Business School, Cambridge Judge Business School y UBS).
#   Confianza MEDIA: cifras del resumen público de la publicación, no del
#   yearbook completo. ES UN SUPUESTO IMPORTADO DE OTRO MERCADO: la prima
#   mundial de 125 años no es la prima colombiana, y se declara así.
#
#   Paso 3. EXPOSICIÓN ADICIONAL A RENTA VARIABLE de cada perfil respecto del
#   conservador, que es lo que convierte la prima en puntos de rendimiento.
#   [VERIFICAR] ESTE ES EL ESLABÓN DÉBIL DE LA CADENA. Los porcentajes de abajo
#   son los límites que se citan habitualmente para el régimen de inversiones de
#   los multifondos, y NO se verificaron en fuente primaria el 2026-07-28: el
#   Gestor Normativo no entregó el articulado del Decreto 2555 y el documento
#   técnico de la URF es un PDF del que no se puede extraer texto.
#   QUÉ CAMBIARÍA SI SE VERIFICAN: los tres números prospectivos se recalculan
#   solos, porque la fórmula está escrita abajo. Si el límite del moderado
#   resultara más bajo, su prima baja y se acerca al conservador.
#   SUPUESTO ADICIONAL, declarado: se asume que cada fondo usa su límite
#   completo. Ningún fondo lo hace, así que estos números son el borde optimista
#   de la construcción.
EXPOSICION_RENTA_VARIABLE = {          # [VERIFICAR] límites del régimen
    "conservador": 0.20,
    "moderado": 0.45,
    "mayor_riesgo": 0.70,
}
PRIMA_RENTA_VARIABLE_LARGO_PLAZO = 0.035
FUENTE_PRIMA_RENTA_VARIABLE = (
    "Dimson, Marsh y Staunton, Global Investment Returns Yearbook 2025 (London "
    "Business School, Cambridge Judge y UBS): serie mundial 1900-2024, renta "
    "variable 5,2% real anual contra bonos 1,7% real anual. Confianza MEDIA, "
    "cifras del resumen público. Supuesto importado de otro mercado: la prima "
    "mundial de 125 años no es la prima colombiana"
)

# El cálculo, en una línea por perfil: al ancla del conservador se le suma la
# exposición ADICIONAL a renta variable respecto de ese mismo perfil, multiplicada
# por la prima. El conservador queda igual por construcción (su exposición
# adicional es cero) y los otros dos quedan por encima, en orden.
RENDIMIENTO_REAL_PROSPECTIVO = {
    perfil: round(
        RENDIMIENTO_REAL_OBSERVADO_CENTRAL["conservador"]
        + (EXPOSICION_RENTA_VARIABLE[perfil]
           - EXPOSICION_RENTA_VARIABLE["conservador"])
        * PRIMA_RENTA_VARIABLE_LARGO_PLAZO, 6)
    for perfil in EXPOSICION_RENTA_VARIABLE
}

# Lo que usa la proyección. Es el PROSPECTIVO, por la decisión de Santiago.
# Se conserva como diccionario de números porque `comparador.py` y
# `aportes_voluntarios.py` lo leen así, y esos archivos son de otros agentes.
RENDIMIENTO_REAL = dict(RENDIMIENTO_REAL_PROSPECTIVO)

ADVERTENCIA_PROSPECTIVO = (
    "la proyección usa un supuesto de rendimiento de LARGO PLAZO, no lo que los "
    "fondos rindieron de verdad. Desde el 2026-09-18 ese supuesto y la "
    "evidencia primaria de la Superfinanciera casi coinciden (moderado 2,90% "
    "supuesto contra 2,76% observado), así que la diferencia dejó de ser "
    "material. Aun así son dos cosas distintas: si la pregunta es qué rindió "
    "cada fondo, la respuesta es el dato observado, no este supuesto. Y ojo con "
    "el periodo: en los últimos 5 años los portafolios defensivos rindieron muy "
    "por debajo de su propio promedio de largo plazo"
)

# Fecha en que entró a regir el Decreto 959 de 2018: cambió el perfil por
# defecto de "moderado para todos" a uno por edad y sexo. Antes de esta fecha
# el default era moderado; después, mayor riesgo para los jóvenes.
FECHA_DECRETO_959 = "2019-03-05"


def perfil_por_defecto(fecha_afiliacion, sexo, edad):
    """Devuelve el perfil de multifondos que la ley asigna a quien nunca eligió.

    Regresa (perfil, confiable, motivo):
    - perfil: "mayor_riesgo" | "moderado" | "conservador" | None
    - confiable: True solo si se puede asumir con seguridad (afiliado desde 2019).
    - motivo: explicación en lenguaje simple para el agente.

    Clave (aprendida de un caso real, 2026-07-20): el default por edad SOLO
    aplica limpio a quien se afilió desde el Decreto 959 (marzo 2019). Quien se
    afilió antes partió del default viejo (moderado para todos) y sigue ahí
    salvo que se haya movido: en ese caso NO se puede asumir, hay que preguntar
    o leer el extracto.
    """
    # Sin fecha de afiliación no se sabe de qué lado del corte está: preguntar
    if not fecha_afiliacion:
        return None, False, ("no se conoce la fecha de afiliación: no se puede "
                             "asumir el perfil, hay que preguntar o leer el extracto")

    # Afiliado ANTES del Decreto 959: el default fue moderado, pero pudo migrar
    if fecha_afiliacion < FECHA_DECRETO_959:
        return None, False, ("se afilió antes de marzo de 2019: su default fue "
                             "moderado, pero pudo cambiar; confirmar en el extracto")

    # Afiliado DESDE el Decreto 959: aplica la tabla por edad y sexo
    if sexo is None or edad is None:
        return None, False, "falta sexo o edad para aplicar la tabla de default"

    if sexo == "F":
        cortes = [(41, "mayor_riesgo"), (45, "transicion"), (51, "moderado"),
                  (200, "conservador")]
    else:
        cortes = [(46, "mayor_riesgo"), (50, "transicion"), (56, "moderado"),
                  (200, "conservador")]
    for tope, perfil in cortes:
        if edad <= tope:
            if perfil == "transicion":
                # En la franja de transición hay una mezcla, no un solo perfil
                return None, False, ("está en la franja de transición de la ley "
                                     "(mezcla de mayor riesgo y moderado)")
            return perfil, True, f"default de ley para su edad y sexo: {perfil}"
    return "conservador", True, "default de ley para su edad y sexo: conservador"

# ---------------------------------------------------------------------------
# CONVERGENCIA OBLIGATORIA HACIA EL FONDO CONSERVADOR
# ---------------------------------------------------------------------------
# Verificado contra el texto literal de la norma el 2026-09-18. Confianza ALTA.
#
# QUÉ ES. A partir de cierta edad la ley OBLIGA a que una parte del saldo esté
# en el fondo conservador, y esa parte crece 20 puntos cada año hasta llegar al
# 100%. No es una recomendación ni un default: es obligatorio, y la persona
# solo puede moverse hacia MÁS conservador, nunca hacia menos.
#
# POR QUÉ IMPORTA PARA EL CÁLCULO, y es el hallazgo que motivó esto: sin esta
# regla, a alguien de 60 años se le podría mostrar el escenario de "mayor
# riesgo" cuando la ley ya lo tiene mayoritariamente en conservador. Sería una
# banda optimista de más, y justo para el segmento que está a punto de decidir.
#
# LA TRAMPA DE LA NORMA. El cuadro del artículo 2.6.11.1.6 dice 50 años para
# mujeres y 55 para hombres. Pero su parágrafo 2 dice, textualmente: "A partir
# del año 2014 las edades señaladas en el cuadro previsto en este artículo se
# aumentarán en dos (2) años tanto para hombres como para mujeres". O sea que
# las edades que aplican hoy son 52 y 57. Quien lea el cuadro y no el parágrafo
# se equivoca por dos años en todo el tramo. Por eso las dos cosas están abajo
# separadas: la tabla como la trae la norma, y el corrimiento aparte.
FUENTE_CONVERGENCIA = (
    "Decreto 2555 de 2010, artículos 2.6.11.1.5 (asignación por defecto, en la "
    "redacción del Decreto 959 de 2018) y 2.6.11.1.6 (reglas de convergencia). "
    "Texto literal verificado en el Gestor Normativo de Función Pública el "
    "2026-09-18. Confianza ALTA"
)

# Las edades del cuadro del 2.6.11.1.6, tal cual las trae la norma.
EDAD_BASE_CONVERGENCIA = {"F": 50, "M": 55}

# Lo que les suma el parágrafo 2 del mismo artículo, desde 2014.
CORRIMIENTO_PARAGRAFO_2 = 2

# El saldo mínimo que debe estar en el conservador, por años cumplidos desde
# que arranca la convergencia. Posición 0 es el año en que arranca.
SALDO_MINIMO_CONSERVADOR = [0.20, 0.40, 0.60, 0.80, 1.00]

# La otra mitad: la asignación por defecto del 2.6.11.1.5, que reparte entre
# mayor riesgo y moderado a quien nunca eligió portafolio. Misma estructura:
# la edad en que arranca, y cuánto pasa al moderado cada año.
EDAD_INICIO_DEFECTO = {"F": 42, "M": 47}
SALDO_MINIMO_MODERADO_POR_DEFECTO = [0.20, 0.40, 0.60, 0.80, 1.00]


def mezcla_obligatoria(sexo, edad):
    """Cómo tiene que estar repartido el saldo de esta persona, por ley.

    Devuelve un diccionario con la fracción de saldo en cada fondo, que suma 1.
    Sirve para dos cosas: no mostrarle a alguien un escenario que la ley no le
    permite, y calcular el rendimiento que de verdad le aplica.

    OJO con la diferencia entre las dos reglas que se combinan aquí:
      - La convergencia al conservador (2.6.11.1.6) aplica a TODO EL MUNDO,
        haya elegido portafolio o no. Solo se puede ir a más conservador.
      - El reparto entre mayor riesgo y moderado (2.6.11.1.5) aplica solo a
        quien NUNCA eligió. Quien eligió se queda donde eligió, en la parte del
        saldo que la convergencia le deja libre.
    Por eso esta función devuelve la parte del conservador como obligatoria y
    el resto como "libre": qué hace con esa parte libre depende de si eligió.
    """
    if sexo not in ("F", "M") or edad is None:
        return None

    # Cuánto del saldo tiene que estar en conservador, sí o sí.
    arranca = EDAD_BASE_CONVERGENCIA[sexo] + CORRIMIENTO_PARAGRAFO_2
    anios_dentro = edad - arranca
    if anios_dentro < 0:
        conservador = 0.0
    elif anios_dentro >= len(SALDO_MINIMO_CONSERVADOR):
        conservador = 1.0
    else:
        conservador = SALDO_MINIMO_CONSERVADOR[anios_dentro]

    # Lo que queda libre se reparte, para quien nunca eligió, entre moderado y
    # mayor riesgo segun la tabla del 2.6.11.1.5.
    libre = round(1.0 - conservador, 6)
    inicio = EDAD_INICIO_DEFECTO[sexo]
    anios_defecto = edad - inicio
    if anios_defecto < 0:
        moderado_del_libre = 0.0
    elif anios_defecto >= len(SALDO_MINIMO_MODERADO_POR_DEFECTO):
        moderado_del_libre = 1.0
    else:
        moderado_del_libre = SALDO_MINIMO_MODERADO_POR_DEFECTO[anios_defecto]

    return {
        "conservador": round(conservador, 6),
        "moderado": round(libre * moderado_del_libre, 6),
        "mayor_riesgo": round(libre * (1 - moderado_del_libre), 6),
        # La parte del saldo sobre la que la persona todavía decide algo.
        "libre_de_convergencia": libre,
        "fuente": FUENTE_CONVERGENCIA,
    }


def perfiles_que_la_ley_le_permite(sexo, edad):
    """Los perfiles que tiene sentido mostrarle a esta persona, y cuáles no.

    Devuelve (permitidos, prohibidos, explicacion). Un perfil se considera
    prohibido cuando la convergencia ya se llevó todo el saldo al conservador:
    ofrecerle "mayor riesgo" a alguien de 61 años no es optimista, es falso.
    """
    mezcla = mezcla_obligatoria(sexo, edad)
    if mezcla is None:
        return list(RENDIMIENTO_REAL_OBSERVADO), [], (
            "sin sexo o sin edad no se puede saber qué le exige la convergencia")

    libre = mezcla["libre_de_convergencia"]
    if libre <= 0:
        return ["conservador"], ["moderado", "mayor_riesgo"], (
            "por su edad, la ley ya le exige el 100% del saldo en el fondo "
            "conservador, así que los otros dos escenarios no le aplican")
    if mezcla["conservador"] > 0:
        return (["conservador", "moderado", "mayor_riesgo"], [],
                f"la ley ya le exige tener el {mezcla['conservador']:.0%} del saldo "
                "en el fondo conservador, así que ningún escenario puro le aplica "
                "del todo: lo que le aplica es la mezcla")
    return list(RENDIMIENTO_REAL_OBSERVADO), [], (
        "todavía no le arranca la convergencia: puede estar en cualquiera de "
        "los tres fondos")


def rendimiento_de_la_mezcla(sexo, edad, rendimientos):
    """El rendimiento que de verdad le aplica, pesando cada fondo por su parte.

    `rendimientos` es un diccionario perfil -> tasa (el prospectivo o el
    observado). Devuelve None si no se sabe el sexo o la edad, porque en ese
    caso inventar una mezcla sería peor que no dar el número.
    """
    mezcla = mezcla_obligatoria(sexo, edad)
    if mezcla is None:
        return None
    return round(sum(mezcla[perfil] * rendimientos[perfil]
                     for perfil in ("conservador", "moderado", "mayor_riesgo")), 6)


# Topes de la mesada: nunca menos de 1 SMLMV ni más de 25 SMLMV.
TOPE_MESADA_EN_SMLMV = 25


def semanas_requeridas(sexo, anio):
    """Devuelve las semanas mínimas que exige la ley según sexo y año.

    sexo: "F" o "M". anio: el año en que se evalúa el requisito.
    """
    if sexo == "M":
        return SEMANAS_HOMBRE
    # Mujeres: antes de 2025 aplicaba 1.300; desde 2036 son 1.000; entre esos
    # años manda la tabla de la Sentencia C-197 de 2023.
    if anio < 2025:
        return 1300
    if anio >= 2036:
        return SEMANAS_MUJER_DESDE_2036
    return SEMANAS_MUJER_POR_ANIO[anio]


def semanas_gpm(sexo, anio):
    """Semanas que exige la Garantía de Pensión Mínima del RAIS, por sexo y año.

    Los hombres siempre necesitan 1.150. Las mujeres bajan 15 semanas cada año
    desde 2026 (1.135) hasta tocar el piso de 1.000 en 2035, por la Sentencia
    C-054 de 2024. Antes de 2026 aplicaban las 1.150 para todos.
    """
    if sexo == "M" or anio < SEMANAS_GPM_ANIO_INICIO:
        return SEMANAS_GPM
    # Cuántos años han pasado desde que arrancó la reducción (2026 = 1 recorte)
    recortes = anio - SEMANAS_GPM_ANIO_INICIO + 1
    semanas = SEMANAS_GPM - recortes * SEMANAS_GPM_REDUCCION_ANUAL
    # Nunca baja del piso que fijó la Corte
    return max(semanas, SEMANAS_GPM_MUJER_PISO)


def factor_ipc(anio_origen, anio_destino):
    """Factor para traer un peso del año origen a pesos del año destino usando IPC.

    Ejemplo: un salario de 2016 se multiplica por la inflación acumulada
    de 2016 a 2025 para expresarlo en pesos de 2026.
    Devuelve None si falta algún año en la serie (regla de oro: no inventar).
    """
    if anio_origen >= anio_destino:
        return 1.0
    factor = 1.0
    # Recorremos cada año entre el origen y el destino acumulando la inflación
    for anio in range(anio_origen, anio_destino):
        if anio not in IPC:
            return None  # Falta el dato: la calculadora lo reporta, no lo inventa
        factor *= 1 + IPC[anio] / 100
    return factor
