# Módulo de anomalías: qué se ve raro en la historia laboral y hay que ir a verificar.
#
# Por qué existe: es el detector de la palanca 10 del banco de palancas,
# "corregir la historia laboral". Esa palanca no es plata nueva ni esfuerzo
# nuevo: son semanas que la persona YA cotizó pero que el documento de la
# administradora registró mal. Por eso suele ser la de mejor relación entre
# esfuerzo y resultado: no hay que ahorrar más ni trabajar más años, hay que
# hacer corregir un papel.
#
# QUÉ HACE Y QUÉ NO HACE ESTE MÓDULO (el límite es a propósito):
#   - SÍ: detecta y clasifica lo que se ve raro, y estima cuántas semanas
#     están en juego cuando se puede saber.
#   - NO: no calcula cuánto sube la mesada si se corrige. Eso lo hace
#     `palancas.py` llamando a `recuperacion.py`, que vuelve a correr el
#     régimen completo con las semanas acreditadas.
#
# LA REGLA DE PRODUCTO QUE MANDA SOBRE TODO LO DEMÁS: un falso positivo
# destruye la confianza. Decirle a alguien "te faltan semanas" cuando no es
# cierto es peor que no decirle nada, porque lo manda a pelear con su
# administradora por algo que está bien y vuelve sintiéndose engañado. Por eso
# aquí:
#   1. Cada anomalía trae un nivel de confianza explícito (alta, media, baja).
#   2. Cada anomalía trae un texto que dice QUÉ IR A VERIFICAR, nunca una
#      afirmación de que hay un error.
#   3. Los umbrales están calibrados contra los seis casos del set dorado, que
#      son documentos reales ya verificados: un umbral que levanta alarmas en
#      ellos es un umbral malo, porque esos documentos están bien.
#
# TOLERANCIA A DATOS FALTANTES: cada administradora llena columnas distintas.
# Colpensiones trae semanas y no trae días; Porvenir trae días y no trae
# semanas; Colfondos ni siquiera trae el nombre del empleador en la mayoría de
# las filas. Todo detector tiene que aguantar nulls sin reventar y sin
# inventar: si le falta el dato con el que decidiría, no decide. Lo que no se
# pudo evaluar sale listado en "no_evaluado", que es una respuesta honesta.

from datos_sistema import SMLMV
from rpm import expandir_a_meses, mes_siguiente

# Convención de días por mes de todo el sistema pensional y del resto de la
# calculadora: un mes completo cotizado son 30 días, no los días del calendario.
DIAS_POR_MES = 30

# Cuánto puede quedar el IBC por debajo del mínimo prorrateado antes de que se
# reporte. Por qué 10% y no 0%: el documento redondea el IBC, redondea los días
# y a veces prorratea con los días del calendario en vez de con 30. Contra el
# set dorado, comparar sin margen levanta 3 filas que están bien (una de
# Protección al 97,8% del mínimo, dos de Colpensiones al 93%), y con este
# margen no levanta ninguna. Ese es exactamente el falso positivo que hay que
# evitar: nadie quiere que le digan que le cotizaron mal por un peso.
MARGEN_BAJO_EL_MINIMO = 0.90

# A partir de qué salto entre meses consecutivos se considera inverosímil un
# cambio de IBC. Por qué 10 veces: un aumento real de sueldo, un ascenso, una
# prima o un independiente que sube su base explican saltos de 2, 3 y hasta 5
# veces, y de hecho el set dorado tiene tres de esos (un independiente que pasa
# de 1 a 5 millones en 2020 y vuelve a bajar). Lo que un cambio real de salario
# NO explica es un factor de 10: eso es un dígito de más o de menos, que es el
# error mecánico típico al digitar o al leer una cifra. Con este umbral el set
# dorado no levanta ninguna alarma.
FACTOR_SALTO_IBC = 10

# Cuántas semanas de diferencia se toleran entre la suma de las filas y el
# total que el propio documento imprime. Por qué 1 semana: la regla del día
# exacto (esquema-datos.md, regla 6) ya hace que sumar filas redondeadas a dos
# decimales sobreestime, y en un documento de 293 filas esa cola de redondeo
# llegó a 0,70 semanas. Por debajo de una semana no hay noticia.
TOLERANCIA_DESCUADRE_SEMANAS = 1.0

# Hueco máximo, en meses, que se lee como "mora no registrada" y no como
# laguna real. Uno o dos meses con el MISMO empleador antes y después es el
# patrón de un pago que no se aplicó; seis meses es que la persona se fue y
# volvió, y eso lo reporta `lagunas.py`, no este módulo.
MAX_MESES_HUECO_CORTO = 2

# Orden de los niveles de confianza, para poder ordenar la lista de salida.
ORDEN_CONFIANZA = {"alta": 0, "media": 1, "baja": 2}

# Observaciones con las que el propio documento ya explica una fila en ceros.
# Si el documento dice "esto es simultáneo", no hay nada que descubrir.
OBSERVACIONES_YA_EXPLICADAS = ("simultaneo", "licencia")


# ---------------------------------------------------------------------------
# Utilidades: leer los campos del periodo sin suponer que existen
# ---------------------------------------------------------------------------

def _clave(fecha_iso):
    """Convierte '2026-03-31' en la clave de mes (2026, 3)."""
    return int(fecha_iso[:4]), int(fecha_iso[5:7])


def _pesos(valor):
    """Escribe una cifra en pesos al estilo colombiano: $1.750.905.

    Se hace aparte y no con un `replace` sobre la frase completa, porque una
    frase también lleva comas de puntuación y se romperían.
    """
    return "$" + f"{round(valor):,}".replace(",", ".")


def _semanas_texto(valor):
    """Escribe un número de semanas al estilo colombiano: 407,43 y no 407.43."""
    return f"{valor:.2f}".replace(".", ",")


def _texto(clave):
    """Convierte la clave (2026, 3) en el texto '2026-03'."""
    return f"{clave[0]}-{clave[1]:02d}"


def _meses_del_rango(desde, hasta):
    """Lista todos los meses entre dos fechas, ambos incluidos."""
    actual, fin = _clave(desde), _clave(hasta)
    meses = []
    while actual <= fin:
        meses.append(actual)
        actual = mes_siguiente(*actual)
    return meses


def _dias_de(periodo):
    """Días cotizados de una fila, venga el documento en días o en semanas.

    Devuelve None cuando el documento no dice ni una cosa ni la otra, que es
    distinto de decir cero: cero significa "no acreditó nada" y None significa
    "no sabemos". Confundir los dos es la forma más fácil de inventar una
    anomalía.
    """
    if periodo.get("dias_cotizados") is not None:
        return periodo["dias_cotizados"]
    # `semanas_validas` manda sobre `semanas`: es la columna de Colpensiones
    # que ya descontó licencias y simultaneidad, o sea lo que de verdad cuenta.
    semanas = periodo.get("semanas_validas")
    if semanas is None:
        semanas = periodo.get("semanas")
    if semanas is None:
        return None
    return round(semanas * 7)


def _es_de_un_solo_mes(periodo):
    """True si la fila cubre un solo mes (formato mensual de los fondos privados).

    Importa porque en una fila de un solo mes el IBC es el de ese mes y se
    puede prorratear contra los días. En un rango de Colpensiones el IBC es el
    ÚLTIMO del rango (esquema-datos.md, regla 2) y no se puede repartir.
    """
    return periodo["desde"][:7] == periodo["hasta"][:7]


def _ibc_mes_completo(periodo):
    """Lleva el IBC de la fila a su equivalente de mes completo.

    Por qué hace falta: en los formatos mensuales el IBC viene prorrateado por
    los días trabajados. Una fila de 6 días con IBC de 165.640 pesos no es un
    sueldo de 165.640, es un sueldo de 828.200 del que se cotizaron 6 días.
    Comparar saltos de IBC sin esta corrección haría que cada mes de entrada o
    de salida de un empleo pareciera un salto inverosímil.
    """
    ibc = periodo.get("ibc")
    dias = _dias_de(periodo)
    if not ibc or not dias:
        return None
    if _es_de_un_solo_mes(periodo) and dias < DIAS_POR_MES:
        return ibc * DIAS_POR_MES / dias
    return ibc


def _identidad_empleador(periodo):
    """Con qué se decide que dos filas son del mismo empleador.

    Se usa el par (empleador, NIT) porque dos empresas distintas pueden
    aparecer con el mismo nombre abreviado. Si no hay nombre de empleador
    (pasa en la mayoría de las filas de Colfondos), se devuelve None y los
    detectores que comparan empleadores simplemente no miran esa fila.
    """
    empleador = periodo.get("empleador")
    if not empleador:
        return None
    return (empleador, periodo.get("nit"))


def _normalizar(periodos):
    """Deja pasar solo las filas con fechas, guardando su índice original.

    Una fila sin fechas no se puede ubicar en la línea de tiempo, así que
    ningún detector de este módulo puede opinar sobre ella. No se descarta en
    silencio: se cuenta y se reporta en "no_evaluado".

    De paso se rellenan con None los campos que el JSON pueda no traer. No es
    cosmético: `rpm.expandir_a_meses` lee `dias_cotizados` directamente y
    reventaría con un caso a medio armar, que es justo lo que llega cuando la
    extracción salió incompleta.
    """
    utiles, sin_fechas = [], []
    for indice, periodo in enumerate(periodos):
        if not periodo.get("desde") or not periodo.get("hasta"):
            sin_fechas.append(indice)
            continue
        completo = dict(periodo)
        for campo in ("dias_cotizados", "semanas", "semanas_validas",
                      "semanas_sim", "ibc", "empleador", "nit",
                      "administradora", "observacion", "ibc_tipo"):
            completo.setdefault(campo, None)
        utiles.append((indice, completo))
    return utiles, sin_fechas


# ---------------------------------------------------------------------------
# La función principal
# ---------------------------------------------------------------------------

def detectar(caso):
    """Revisa una historia laboral y devuelve lo que habría que ir a verificar.

    Recibe el caso completo con el esquema de `casos/esquema-datos.md` y
    devuelve un diccionario con:

      - "anomalias": la lista de hallazgos, ordenada por semanas en juego de
        mayor a menor y, a igual número, por confianza.
      - "hay_algo_que_revisar": True si la lista trae al menos un hallazgo.
      - "semanas_en_juego_total": las semanas que se podrían recuperar, SIN
        doble conteo entre hallazgos (ver `_sumar_semanas_en_juego`). Es None
        cuando no hay nada cuantificable.
      - "no_evaluado": qué detectores no pudieron correr y por qué. Existe
        para que el agente pueda decir "esto no lo pude revisar" en vez de
        dejar creer que revisó todo.

    Por qué la firma es `detectar(caso)` y no recibe fecha de cálculo, a
    diferencia de `lagunas.analizar`: aquí ninguna regla depende de hoy. Una
    anomalía de 1999 es igual de anómala hoy que el año entrante, y meter una
    fecha que no se usa solo invita a que alguien crea que sí se usa.
    """
    periodos_brutos = caso.get("periodos") or []
    utiles, sin_fechas = _normalizar(periodos_brutos)

    no_evaluado = []
    if sin_fechas:
        no_evaluado.append({
            "que": "filas sin fechas",
            "cuantas": len(sin_fechas),
            "por_que": ("sin fecha de inicio y fin no se puede ubicar la fila "
                        "en el tiempo, así que ningún detector opina sobre ella"),
        })

    if not utiles:
        # Sin filas con fechas no hay nada que revisar y tampoco hay derecho a
        # decir que está todo bien. Se dice que no se pudo evaluar.
        return {
            "anomalias": [],
            "hay_algo_que_revisar": False,
            "semanas_en_juego_total": None,
            "no_evaluado": no_evaluado + [{
                "que": "todos los detectores",
                "cuantas": 0,
                "por_que": "el documento no trae ningún periodo con fechas",
            }],
        }

    solo_periodos = [periodo for _indice, periodo in utiles]

    # Mapa mes -> {"dias", "ibc"} con TODOS los aportantes juntos. Es la misma
    # pieza que usan `lagunas.py` y `recuperacion.py`, y se usa aquí por la
    # misma razón: ya topa los días en 30 por mes, así que un mes que otro
    # empleador llenó no puede aparecer como semanas por recuperar.
    meses = expandir_a_meses(solo_periodos)

    anomalias = []
    anomalias += _ibc_sin_semanas(utiles, meses)
    anomalias += _semanas_sin_ibc(utiles, no_evaluado)
    anomalias += _ibc_bajo_el_minimo(utiles, no_evaluado)
    anomalias += _solapamiento_mismo_empleador(utiles, no_evaluado)
    anomalias += _hueco_corto_mismo_empleador(utiles, meses)
    anomalias += _salto_de_ibc_inverosimil(utiles)
    anomalias += _descuadre_con_el_documento(caso, solo_periodos, no_evaluado)

    # Orden de salida: primero lo que más semanas pone en juego, porque es lo
    # que más le cambia la vida a la persona. Los hallazgos sin semanas
    # cuantificables van al final, ordenados por confianza: son reales, pero
    # no son por lo que uno empieza a pelear.
    anomalias.sort(key=lambda a: (
        -(a["semanas_en_juego"] or 0),
        ORDEN_CONFIANZA[a["confianza"]],
    ))

    return {
        "anomalias": anomalias,
        "hay_algo_que_revisar": bool(anomalias),
        "semanas_en_juego_total": _sumar_semanas_en_juego(anomalias),
        "no_evaluado": no_evaluado,
    }


def _sumar_semanas_en_juego(anomalias):
    """Suma las semanas recuperables sin contar dos veces el mismo mes.

    Por qué no basta con sumar el campo de cada anomalía: dos hallazgos
    distintos pueden estar reclamando los mismos meses. El caso concreto es
    una fila con salario y cero semanas de un empleador y, en esos mismos
    meses, un hueco corto de otro empleador. Los dos apuntan al mismo tiempo
    vacío del calendario y ese tiempo solo se puede recuperar una vez. Por eso
    cada detector que estima semanas deja anotado QUÉ MESES reclama, y aquí se
    unen los meses antes de convertirlos a semanas.
    """
    dias_por_mes = {}
    for anomalia in anomalias:
        for mes, dias in anomalia.get("_dias_reclamados", {}).items():
            # De dos hallazgos sobre el mismo mes se queda el mayor, no la suma
            dias_por_mes[mes] = max(dias_por_mes.get(mes, 0), dias)
    if not dias_por_mes:
        return None
    return round(sum(dias_por_mes.values()) / 7, 2)


# ---------------------------------------------------------------------------
# Anomalía 1: salario reportado y cero semanas acreditadas
# ---------------------------------------------------------------------------

def _ibc_sin_semanas(utiles, meses):
    """Filas con aportante y salario, pero con cero semanas acreditadas.

    Es el "cuarto estado" de `kit-contexto/mora-y-correccion-historia-laboral.md`
    (sección 1 bis): no es mora patronal, ni deuda presunta, ni periodo no
    reportado. Hay salario impreso y hay cero semanas, y el documento no dice
    por qué. Aparece en los dos reportes de Colpensiones del set dorado, y en
    los dos el aportante es una empresa de servicios temporales.

    Por qué NO se afirma que las semanas se perdieron: hay cuatro causas
    posibles (mora o pago mal aplicado, simultaneidad no marcada, aporte que se
    fue a salud, novedad administrativa sin días efectivos) y cada una se
    resuelve en una puerta distinta. La respuesta correcta es "esto no te está
    sumando, hay que averiguar por qué", no "te robaron semanas".
    """
    hallazgos = []
    for indice, periodo in utiles:
        ibc = periodo.get("ibc")
        dias = _dias_de(periodo)
        # Hace falta que el documento afirme las dos cosas: que hubo salario y
        # que las semanas fueron cero. Con días en None no sabemos nada.
        if not ibc or dias is None or dias > 0:
            continue
        # Si el propio documento marcó la fila como simultánea o como licencia,
        # ya está explicada: el tiempo lo acreditó el otro aportante.
        if (periodo.get("semanas_sim") or 0) > 0:
            continue
        if periodo.get("observacion") in OBSERVACIONES_YA_EXPLICADAS:
            continue

        # Cuántas semanas habría de verdad en juego: solo los días que quedan
        # libres en esos meses. Si en ese mes la persona ya completó 30 días
        # por otro empleador, acreditar esta fila no le suma nada.
        reclamados = _dias_libres_por_mes(meses, periodo["desde"], periodo["hasta"])
        dias_libres = sum(reclamados.values())
        semanas = round(dias_libres / 7, 2)

        if dias_libres > 0:
            # El hecho es directo y se lee en el propio documento: hay salario
            # y no hay semanas, y nadie más cubrió esos meses. La confianza
            # baja a media cuando lo que queda libre es menos de medio mes:
            # ahí la explicación inocente (un ingreso o un retiro a mitad de
            # mes que el otro registro ya cubrió casi entero) es tan probable
            # como la mora, y no vale la pena mandar a nadie a reclamar dos
            # días.
            confianza = "alta" if dias_libres >= DIAS_POR_MES / 2 else "media"
            que_verificar = (
                f"{periodo.get('empleador') or 'Un aportante'} aparece reportando "
                f"un salario en {periodo['desde'][:7]} a {periodo['hasta'][:7]}, "
                f"pero con cero semanas acreditadas: ese tiempo hoy no le está "
                f"sumando. Antes de reclamar hay que averiguar por qué. Las dos "
                f"preguntas que lo resuelven son si usted trabajó con esa empresa "
                f"en esos meses y si en el desprendible le descontaron pensión. "
                f"Con eso se sabe si es mora del empleador (que sí se recupera), "
                f"un aporte que se fue a salud, o un registro que no le "
                f"corresponde.")
        else:
            # Los mismos meses ya están llenos por otro aportante: no hay
            # semanas que ganar. Se reporta igual, porque el usuario ve la fila
            # rara en su documento, pero sin prometer nada.
            confianza = "baja"
            que_verificar = (
                f"{periodo.get('empleador') or 'Un aportante'} reporta salario y "
                f"cero semanas en {periodo['desde'][:7]} a {periodo['hasta'][:7]}, "
                f"pero esos meses ya están completos con otro aportante. "
                f"Probablemente sea simultaneidad que el reporte no marcó. No hay "
                f"semanas que recuperar ahí.")

        hallazgos.append({
            "tipo": "ibc_sin_semanas",
            "confianza": confianza,
            "periodos_afectados": [indice],
            "semanas_en_juego": semanas,
            "que_verificar": que_verificar,
            "motivo": ("Cuarto estado de mora-y-correccion-historia-laboral.md "
                       "sección 1 bis. Si resulta ser mora del empleador, las "
                       "semanas se reconocen aunque la empresa no haya pagado "
                       "(Corte Constitucional, SU-226 de 2019 y T-043 de 2025; "
                       "Ley 100 de 1993, art. 22)."),
            "detalle": {
                "desde": periodo["desde"][:7],
                "hasta": periodo["hasta"][:7],
                "empleador": periodo.get("empleador"),
                "ibc": ibc,
                "observacion_documento": periodo.get("observacion"),
            },
            "_dias_reclamados": reclamados,
        })
    return hallazgos


def _dias_libres_por_mes(meses, desde, hasta):
    """Días que quedan sin cotizar en cada mes de un rango, con tope de 30.

    Devuelve un diccionario mes -> días libres, y no un total, porque quien
    suma al final necesita saber CUÁLES meses se están reclamando para no
    contar dos veces el mismo (ver `_sumar_semanas_en_juego`). El mes va como
    texto '2026-03' y no como pareja de números, para que toda la salida del
    módulo se pueda guardar como JSON sin traducirla.
    """
    libres = {}
    for mes in _meses_del_rango(desde, hasta):
        disponibles = max(0, DIAS_POR_MES - meses.get(mes, {}).get("dias", 0))
        if disponibles:
            libres[_texto(mes)] = disponibles
    return libres


# ---------------------------------------------------------------------------
# Anomalía 2: semanas acreditadas y salario en blanco
# ---------------------------------------------------------------------------

def _semanas_sin_ibc(utiles, no_evaluado):
    """Filas con días cotizados pero con el salario base en cero o en blanco.

    Es el espejo de la anomalía 1 y tiene una consecuencia distinta: las
    semanas SÍ están contadas, lo que queda cojo es el salario. Y el salario
    importa porque el IBL del RPM es el promedio de los IBC de los últimos 10
    años (Ley 100 de 1993, art. 21): un mes sin salario, o con salario en cero,
    arrastra ese promedio hacia abajo y baja la mesada.

    Por eso `semanas_en_juego` es None y no cero: no hay semanas en juego, hay
    mesada en juego, y cuantificarla no es trabajo de este módulo.

    Defensa contra el falso positivo masivo: si NINGUNA fila del documento trae
    IBC, es que ese formato no imprime el salario. Ahí no hay 200 anomalías,
    hay un formato distinto, y se reporta como "no evaluado".
    """
    hay_algun_ibc = any(periodo.get("ibc") for _indice, periodo in utiles)
    if not hay_algun_ibc:
        no_evaluado.append({
            "que": "semanas_sin_ibc",
            "cuantas": len(utiles),
            "por_que": ("ninguna fila del documento trae salario base, así que "
                        "el formato no lo imprime: que falte no dice nada"),
        })
        return []

    hallazgos = []
    for indice, periodo in utiles:
        dias = _dias_de(periodo)
        if not dias:
            continue          # Sin días cotizados esta anomalía no aplica
        if periodo.get("ibc"):
            continue          # Hay salario: todo en orden

        # Cero y "en blanco" no son lo mismo, y la diferencia cambia la
        # confianza. Un cero impreso es imposible (no se puede cotizar sobre
        # nada); un campo vacío puede ser simplemente que no se pudo leer.
        es_cero_explicito = periodo.get("ibc") == 0
        hallazgos.append({
            "tipo": "semanas_sin_ibc",
            "confianza": "alta" if es_cero_explicito else "media",
            "periodos_afectados": [indice],
            "semanas_en_juego": None,
            "que_verificar": (
                f"En {periodo['desde'][:7]} a {periodo['hasta'][:7]} el reporte "
                f"acredita tiempo cotizado pero no muestra el salario base. Las "
                f"semanas sí le cuentan, lo que puede quedar mal es el promedio "
                f"salarial con el que se calcula la mesada. Vale la pena pedir el "
                f"detalle de ese periodo a la administradora o revisar el "
                f"desprendible de pago de esos meses."),
            "motivo": ("El IBL del RPM es el promedio de los IBC del periodo de "
                       "referencia (Ley 100 de 1993, art. 21). Un IBC faltante o "
                       "en cero arrastra ese promedio hacia abajo."),
            "detalle": {
                "desde": periodo["desde"][:7],
                "hasta": periodo["hasta"][:7],
                "empleador": periodo.get("empleador"),
                "dias_cotizados": dias,
                "ibc": periodo.get("ibc"),
            },
            "_dias_reclamados": {},
        })
    return hallazgos


# ---------------------------------------------------------------------------
# Anomalía 3: IBC por debajo del salario mínimo del año
# ---------------------------------------------------------------------------

def _ibc_bajo_el_minimo(utiles, no_evaluado):
    """Filas que cotizaron sobre una base menor al mínimo que les correspondía.

    La norma: la base de cotización no puede ser inferior al salario mínimo
    legal mensual vigente (Ley 100 de 1993, art. 18). Cotizar por debajo del
    mínimo un mes completo no es legal.

    LA TRAMPA QUE HAY QUE ESQUIVAR, y es la que produciría más falsos positivos
    de todo el módulo: cotizar menos de un mínimo SÍ es legítimo cuando el mes
    fue parcial. Quien entró a trabajar el día 20 cotiza 10 días, y sobre 10
    días la base correcta es un tercio del mínimo. Comparar contra el mínimo
    pleno marcaría como ilegal cada mes de entrada y de salida de cada empleo.
    Por eso la comparación es siempre contra el mínimo PRORRATEADO por los días
    de la fila.

    La segunda trampa: con dos empleadores en el mismo mes, cada uno cotiza
    sobre su parte y ninguno de los dos llega al mínimo por separado, pero la
    suma sí. Por eso se compara la suma del mes, no la fila sola.
    """
    hallazgos = []
    anios_sin_dato = set()

    # Suma de los IBC de cada mes, para no acusar a una fila de simultaneidad
    # legítima. Solo entran filas de un solo mes: en un rango de Colpensiones
    # el IBC es el último del rango y sumarlo a otros meses no significa nada.
    ibc_del_mes = {}
    for _indice, periodo in utiles:
        if periodo.get("ibc") and _es_de_un_solo_mes(periodo):
            clave = periodo["desde"][:7]
            ibc_del_mes[clave] = ibc_del_mes.get(clave, 0) + periodo["ibc"]

    for indice, periodo in utiles:
        ibc = periodo.get("ibc")
        dias = _dias_de(periodo)
        if not ibc or not dias:
            continue          # Sin salario o sin días no hay nada que comparar

        # El año que manda es el del final del periodo, porque en los rangos de
        # Colpensiones el IBC impreso es el del último mes del rango.
        anio = int(periodo["hasta"][:4])
        if anio not in SMLMV:
            # No se inventa un salario mínimo para un año que no está en la
            # tabla verificada. Se anota y se sigue.
            anios_sin_dato.add(anio)
            continue

        de_un_mes = _es_de_un_solo_mes(periodo)
        if de_un_mes:
            # Mes suelto: el mínimo se prorratea por los días efectivamente
            # cotizados, con tope de 30 (un mes no tiene más de 30 días para el
            # sistema pensional).
            minimo = SMLMV[anio] * min(dias, DIAS_POR_MES) / DIAS_POR_MES
            # Con simultaneidad, lo que tiene que llegar al mínimo es la suma
            suma_del_mes = ibc_del_mes.get(periodo["desde"][:7], ibc)
        else:
            # Rango de varios meses: el IBC es el del último mes y no se sabe
            # cuántos días tuvo ESE mes, así que solo se puede comparar contra
            # el mínimo pleno, y el resultado vale menos (confianza más baja).
            minimo = SMLMV[anio]
            suma_del_mes = ibc

        if suma_del_mes >= minimo * MARGEN_BAJO_EL_MINIMO:
            continue          # Llega al mínimo, solo o sumado con el otro empleo

        # Confianza: en un mes completo de una sola fila el hecho es limpio y
        # verificable contra el decreto de salario mínimo de ese año. En un
        # rango de Colpensiones el último mes pudo ser parcial, y eso explicaría
        # la diferencia sin que nadie haya hecho nada mal.
        if de_un_mes and dias >= DIAS_POR_MES:
            confianza = "alta"
        elif de_un_mes:
            confianza = "media"
        else:
            confianza = "baja"

        hallazgos.append({
            "tipo": "ibc_bajo_el_minimo",
            "confianza": confianza,
            "periodos_afectados": [indice],
            # No hay semanas en juego: las semanas están acreditadas. Lo que
            # está mal es la base, y eso pega en la mesada, no en el conteo.
            "semanas_en_juego": None,
            "que_verificar": (
                f"En {periodo['desde'][:7]} a {periodo['hasta'][:7]} la base de "
                f"cotización reportada es de {_pesos(ibc)} y el mínimo que "
                f"correspondía por ese tiempo era de unos {_pesos(minimo)}. Puede "
                f"ser que el mes haya sido parcial y esté bien, o que le hayan "
                f"cotizado por debajo de lo que le pagaban. Compare esa cifra con "
                f"su desprendible de pago de esos meses: si le descontaron sobre "
                f"un salario mayor, hay algo que corregir."),
            "motivo": ("La base de cotización no puede ser inferior al salario "
                       "mínimo legal mensual vigente (Ley 100 de 1993, art. 18). "
                       "La comparación se hace contra el mínimo prorrateado por "
                       "los días cotizados, porque un mes parcial sí puede ir por "
                       "debajo del mínimo pleno legítimamente."),
            "detalle": {
                "desde": periodo["desde"][:7],
                "hasta": periodo["hasta"][:7],
                "empleador": periodo.get("empleador"),
                "ibc": ibc,
                "dias_cotizados": dias,
                "minimo_prorrateado": round(minimo),
                "smlmv_del_anio": SMLMV[anio],
                "proporcion_del_minimo": round(suma_del_mes / minimo, 2),
            },
            "_dias_reclamados": {},
        })

    if anios_sin_dato:
        no_evaluado.append({
            "que": "ibc_bajo_el_minimo en algunos años",
            "cuantas": len(anios_sin_dato),
            "por_que": ("no hay salario mínimo verificado en la tabla para los "
                        f"años {sorted(anios_sin_dato)}, y no se inventa"),
        })
    return hallazgos


# ---------------------------------------------------------------------------
# Anomalía 4: el mismo empleador reportado dos veces sobre el mismo tiempo
# ---------------------------------------------------------------------------

def _solapamiento_mismo_empleador(utiles, no_evaluado):
    """Dos filas del mismo empleador que cubren el mismo tiempo.

    LO QUE NO ES UNA ANOMALÍA, y descartarlo es la mitad del trabajo: en los
    formatos mensuales es completamente normal que un mes tenga varias filas
    del mismo empleador (esquema-datos.md, regla 1). Son pagos partidos: la
    empresa pagó en dos planillas, o corrigió y volvió a pagar. El set dorado
    tiene diez de esos en un solo caso, todos legítimos. Marcarlos sería
    inundar al usuario de alarmas falsas.

    Lo que sí se reporta son dos cosas mucho más estrechas:
      - La fila duplicada exacta: mismas fechas, mismo empleador, mismo salario
        y los mismos días. Eso no es un pago partido, es el mismo renglón dos
        veces.
      - El solapamiento de rangos largos: dos tramos del mismo empleador que se
        pisan y al menos uno cubre varios meses. En el formato de tramos cada
        rango es un periodo continuo con un salario, así que dos rangos del
        mismo empleador no deberían pisarse.
    """
    hallazgos = []
    sin_empleador = sum(1 for _i, p in utiles if _identidad_empleador(p) is None)
    if sin_empleador:
        no_evaluado.append({
            "que": "solapamiento_mismo_empleador en filas sin empleador",
            "cuantas": sin_empleador,
            "por_que": ("el documento no trae el nombre del aportante en esas "
                        "filas, así que no se puede saber si son del mismo"),
        })

    for posicion, (indice_a, periodo_a) in enumerate(utiles):
        identidad = _identidad_empleador(periodo_a)
        if identidad is None:
            continue
        for indice_b, periodo_b in utiles[posicion + 1:]:
            if _identidad_empleador(periodo_b) != identidad:
                continue
            # ¿Se pisan en el tiempo? Dos rangos se pisan si cada uno empieza
            # antes de que el otro termine.
            if not (periodo_a["desde"] <= periodo_b["hasta"]
                    and periodo_b["desde"] <= periodo_a["hasta"]):
                continue
            # Dos administradoras distintas reportando el mismo empleador es el
            # patrón normal de un traslado de fondo: el fondo nuevo hereda el
            # detalle del anterior (pasa en el caso 03 del set dorado). No es
            # un doble registro.
            if (periodo_a.get("administradora") and periodo_b.get("administradora")
                    and periodo_a["administradora"] != periodo_b["administradora"]):
                continue

            es_duplicado_exacto = (
                periodo_a["desde"] == periodo_b["desde"]
                and periodo_a["hasta"] == periodo_b["hasta"]
                and periodo_a.get("ibc") == periodo_b.get("ibc")
                and _dias_de(periodo_a) == _dias_de(periodo_b))
            es_rango_largo = (not _es_de_un_solo_mes(periodo_a)
                              or not _es_de_un_solo_mes(periodo_b))

            if es_duplicado_exacto:
                confianza = "alta"
                texto = (
                    f"El mismo periodo de {periodo_a.get('empleador')} "
                    f"({periodo_a['desde'][:7]} a {periodo_a['hasta'][:7]}) "
                    f"aparece dos veces con exactamente el mismo salario y los "
                    f"mismos días. Puede ser un renglón repetido del reporte. "
                    f"Conviene pedirle a la administradora que confirme si son "
                    f"dos pagos distintos o el mismo registrado dos veces.")
            elif es_rango_largo:
                confianza = "media"
                texto = (
                    f"Dos registros de {periodo_a.get('empleador')} se cruzan en "
                    f"el tiempo ({periodo_a['desde'][:7]} a "
                    f"{periodo_a['hasta'][:7]} y {periodo_b['desde'][:7]} a "
                    f"{periodo_b['hasta'][:7]}). En este formato cada tramo "
                    f"debería ser un periodo continuo, así que vale la pena "
                    f"pedir el detalle de esos meses para ver cuál es cuál.")
            else:
                # Dos filas del mismo mes con datos distintos: pago partido.
                # Es normal y no se reporta.
                continue

            hallazgos.append({
                "tipo": "solapamiento_mismo_empleador",
                "confianza": confianza,
                "periodos_afectados": [indice_a, indice_b],
                # Un doble registro no esconde semanas por recuperar: las
                # semanas de un mes se cuentan una sola vez con tope de 30 días
                # (esquema-datos.md, regla 3). Lo que hay es un dato sucio.
                "semanas_en_juego": None,
                "que_verificar": texto,
                "motivo": ("Las semanas de un mes se cuentan una sola vez aunque "
                           "haya varios registros (regla de simultaneidad del "
                           "sistema). Un doble registro no suma semanas, pero sí "
                           "puede indicar que el reporte está mal armado."),
                "detalle": {
                    "empleador": periodo_a.get("empleador"),
                    "primero": f"{periodo_a['desde']} a {periodo_a['hasta']}",
                    "segundo": f"{periodo_b['desde']} a {periodo_b['hasta']}",
                    "duplicado_exacto": es_duplicado_exacto,
                },
                "_dias_reclamados": {},
            })
    return hallazgos


# ---------------------------------------------------------------------------
# Anomalía 5: hueco de uno o dos meses con el mismo empleador a los dos lados
# ---------------------------------------------------------------------------

def _hueco_corto_mismo_empleador(utiles, meses):
    """Uno o dos meses sin cotizar, con el mismo empleador antes y después.

    Por qué este patrón vale la pena separarlo de una laguna cualquiera: si la
    persona siguió trabajando en la misma empresa antes y después, lo más
    probable es que no se haya ido un mes y haya vuelto, sino que ese mes se
    pagó y no quedó registrado, o no se pagó y nadie lo cobró. Es el patrón
    típico de una mora no registrada, y se resuelve distinto que una laguna
    real de desempleo: aquí hay un tercero responsable.

    Lo que lo separa de `lagunas.py`: ese módulo dice dónde están los huecos,
    todos. Este dice cuáles de esos huecos huelen a mora en vez de a desempleo.

    El filtro que evita el falso positivo: si otro empleador cubrió ese mes, no
    hay hueco ninguno. En el set dorado, tres de los cinco huecos cortos
    detectados estaban tapados por otro aportante y se descartan aquí.
    """
    hallazgos = []

    # Se agrupan las filas por empleador y se ordenan por fecha
    por_empleador = {}
    for indice, periodo in utiles:
        identidad = _identidad_empleador(periodo)
        if identidad is None:
            continue
        if not _dias_de(periodo):
            continue          # Una fila sin días no marca presencia laboral
        por_empleador.setdefault(identidad, []).append((indice, periodo))

    for identidad, filas in por_empleador.items():
        filas.sort(key=lambda par: par[1]["desde"])
        for posicion in range(len(filas) - 1):
            indice_a, periodo_a = filas[posicion]
            indice_b, periodo_b = filas[posicion + 1]
            fin = _clave(periodo_a["hasta"])
            inicio = _clave(periodo_b["desde"])
            # Meses completos que quedan entre el final de uno y el inicio del otro
            hueco = (inicio[0] - fin[0]) * 12 + (inicio[1] - fin[1]) - 1
            if not 1 <= hueco <= MAX_MESES_HUECO_CORTO:
                continue

            # Los meses concretos del hueco, y cuántos días quedan libres en
            # ellos después de contar lo que reportaron TODOS los aportantes.
            reclamados, mes = {}, fin
            for _ in range(hueco):
                mes = mes_siguiente(*mes)
                libres = max(0, DIAS_POR_MES - meses.get(mes, {}).get("dias", 0))
                if libres:
                    reclamados[_texto(mes)] = libres
            if not reclamados:
                continue      # Otro empleador llenó esos meses: no hay hueco

            meses_texto = ", ".join(sorted(reclamados))
            # Un solo mes de hueco es el patrón más limpio. Dos meses ya se
            # parecen más a un contrato que terminó y se volvió a firmar, que
            # es una explicación inocente y frecuente.
            confianza = "media" if hueco == 1 else "baja"

            hallazgos.append({
                "tipo": "hueco_corto_mismo_empleador",
                "confianza": confianza,
                "periodos_afectados": [indice_a, indice_b],
                "semanas_en_juego": round(sum(reclamados.values()) / 7, 2),
                "que_verificar": (
                    f"Con {periodo_a.get('empleador')} hay cotizaciones antes y "
                    f"después, pero no en {meses_texto}. Si usted siguió "
                    f"trabajando ahí esos meses, ese aporte debió hacerse y no "
                    f"aparece. Revise su desprendible de pago de esos meses: si "
                    f"le descontaron pensión, la empresa quedó debiendo y esas "
                    f"semanas son suyas aunque no las hayan pagado."),
                "motivo": ("Si el vínculo laboral estaba vigente, la mora del "
                           "empleador no se le puede oponer al afiliado y las "
                           "semanas se reconocen (Corte Constitucional, SU-226 de "
                           "2019 y SU-062 de 2023; Ley 100 de 1993, arts. 22 y "
                           "23). La carga es probar que el vínculo continuó."),
                "detalle": {
                    "empleador": periodo_a.get("empleador"),
                    "ultimo_mes_cotizado": _texto(fin),
                    "meses_del_hueco": meses_texto,
                    "vuelve_a_cotizar": _texto(inicio),
                },
                "_dias_reclamados": reclamados,
            })
    return hallazgos


# ---------------------------------------------------------------------------
# Anomalía 6: el salario base pega un salto que no se explica
# ---------------------------------------------------------------------------

def _salto_de_ibc_inverosimil(utiles):
    """Cambios de salario base de un orden de magnitud entre meses seguidos.

    Por qué el umbral es de 10 veces y no de 2 o de 3, que sería lo intuitivo:
    un salto de 2, 3 o 5 veces tiene explicaciones legítimas y frecuentes. Un
    ascenso, un cambio de contrato, una bonificación que sí entra en la base, o
    un independiente que decide cotizar sobre más. El set dorado tiene tres
    saltos de entre 3 y 7,5 veces y ninguno es un error: uno es un independiente
    que pasó de un millón a cinco en 2020 y volvió a bajar. Lo que un cambio
    real de sueldo no explica es un factor de diez: eso es un dígito de más o de
    menos al digitar la cifra.

    Antes de comparar, los dos IBC se llevan a mes completo. Sin eso, el mes en
    que alguien entra a trabajar (6 días cotizados, IBC prorrateado a la quinta
    parte) parecería un desplome salarial en todos los documentos.

    La confianza siempre es baja: el módulo no puede distinguir un error de
    digitación de un cambio real muy grande, y un IBC mal registrado no le quita
    semanas a nadie, solo le mueve el promedio. No es para alarmar, es para
    mirar.
    """
    hallazgos = []

    por_empleador = {}
    for indice, periodo in utiles:
        identidad = _identidad_empleador(periodo)
        if identidad is None:
            continue
        normalizado = _ibc_mes_completo(periodo)
        if not normalizado:
            continue
        por_empleador.setdefault(identidad, []).append(
            (indice, periodo, normalizado))

    for identidad, filas in por_empleador.items():
        filas.sort(key=lambda t: t[1]["desde"])
        for posicion in range(len(filas) - 1):
            indice_a, periodo_a, ibc_a = filas[posicion]
            indice_b, periodo_b, ibc_b = filas[posicion + 1]
            fin_a = _clave(periodo_a["hasta"])
            inicio_b = _clave(periodo_b["desde"])
            # Solo se comparan meses seguidos: entre dos periodos separados por
            # años, un salario diez veces mayor es simplemente la vida.
            distancia = (inicio_b[0] - fin_a[0]) * 12 + (inicio_b[1] - fin_a[1])
            if distancia > 1:
                continue
            razon = ibc_b / ibc_a
            if 1 / FACTOR_SALTO_IBC < razon < FACTOR_SALTO_IBC:
                continue

            direccion = "subió" if razon > 1 else "bajó"
            veces = razon if razon > 1 else 1 / razon
            hallazgos.append({
                "tipo": "salto_de_ibc_inverosimil",
                "confianza": "baja",
                "periodos_afectados": [indice_a, indice_b],
                "semanas_en_juego": None,
                "que_verificar": (
                    f"Con {periodo_a.get('empleador')} el salario base reportado "
                    f"{direccion} unas {veces:.0f} veces entre "
                    f"{periodo_a['hasta'][:7]} y {periodo_b['desde'][:7]} "
                    f"(de {_pesos(ibc_a)} a {_pesos(ibc_b)} al mes). "
                    f"Puede ser real, pero un cambio de esa magnitud también se "
                    f"ve cuando se digita un dígito de más. Vale la pena "
                    f"compararlo con sus desprendibles de esos meses."),
                "motivo": ("Un IBC mal registrado no cambia las semanas, pero sí "
                           "el promedio salarial con el que se liquida la mesada "
                           "(IBL, Ley 100 de 1993, art. 21)."),
                "detalle": {
                    "empleador": periodo_a.get("empleador"),
                    "mes_anterior": periodo_a["hasta"][:7],
                    "mes_siguiente": periodo_b["desde"][:7],
                    "ibc_mes_completo_anterior": round(ibc_a),
                    "ibc_mes_completo_siguiente": round(ibc_b),
                    "veces": round(razon, 2),
                },
                "_dias_reclamados": {},
            })
    return hallazgos


# ---------------------------------------------------------------------------
# Anomalía 7: el documento no cuadra consigo mismo
# ---------------------------------------------------------------------------

def _descuadre_con_el_documento(caso, periodos, no_evaluado):
    """La suma de las filas contra el total de semanas que imprime el documento.

    El total impreso es la "respuesta del profesor": si la tabla no llega a él,
    o se leyó mal el documento, o al documento le faltan filas. Las dos cosas
    importan y se dicen distinto, porque la consecuencia para la persona no es
    la misma.

    Existe de verdad: el caso 06 del set dorado es un reporte de Colfondos cuya
    tabla suma 407,43 semanas mientras el encabezado dice 398,0, y ninguna regla
    de conteo conocida explica la diferencia. El esquema de datos lo reconoce
    con el campo `nota_verificacion`, y la instrucción del kit es reportarlo al
    usuario, no resolverlo en silencio.
    """
    resumen = caso.get("resumen_documento") or {}
    total_documento = resumen.get("total_semanas")
    if total_documento is None:
        no_evaluado.append({
            "que": "descuadre_con_el_total_del_documento",
            "cuantas": 1,
            "por_que": ("el documento no imprime un total de semanas contra el "
                        "cual comparar la suma de las filas"),
        })
        return []

    calculado = _semanas_de_las_filas(periodos)
    if calculado is None:
        no_evaluado.append({
            "que": "descuadre_con_el_total_del_documento",
            "cuantas": 1,
            "por_que": ("las filas no traen ni días ni semanas, así que no hay "
                        "nada que sumar para comparar contra el total"),
        })
        return []

    diferencia = round(calculado - total_documento, 2)
    if abs(diferencia) <= TOLERANCIA_DESCUADRE_SEMANAS:
        return []

    if diferencia < 0:
        # El documento se acredita más semanas de las que muestra su propia
        # tabla: hay filas que no se leyeron o que el reporte no imprimió. Esas
        # semanas están en juego en el sentido bueno (podrían aparecer).
        faltantes = abs(diferencia)
        semanas_en_juego = faltantes
        texto = (
            f"El documento dice que usted tiene {_semanas_texto(total_documento)} "
            f"semanas, pero el detalle que aparece en él solo suma "
            f"{_semanas_texto(calculado)}. "
            f"Faltan {_semanas_texto(faltantes)} semanas de detalle. Puede ser que el reporte "
            f"esté incompleto o que haya periodos en otra administradora. Pida el "
            f"reporte completo de semanas y compárelo con este.")
    else:
        # Al revés: la tabla suma más de lo que el encabezado reconoce. No son
        # semanas por ganar, es una inconsistencia que hay que hacer aclarar.
        semanas_en_juego = None
        texto = (
            f"El detalle del documento suma {_semanas_texto(calculado)} semanas, "
            f"pero el total que el propio documento imprime es de "
            f"{_semanas_texto(total_documento)}. "
            f"El reporte no cuadra consigo mismo. No significa que le falten "
            f"semanas: significa que hay que pedirle a la administradora que "
            f"aclare cuál de las dos cifras es la buena antes de tomar cualquier "
            f"decisión con este número.")

    # La confianza depende del tamaño: una diferencia de pocas semanas puede
    # venir de la forma en que cada fondo redondea. Una grande no.
    if abs(diferencia) >= 4:
        confianza = "alta"
    else:
        confianza = "media"

    return [{
        "tipo": "descuadre_con_el_total_del_documento",
        "confianza": confianza,
        # Afecta al documento entero, no a una fila en particular
        "periodos_afectados": [],
        "semanas_en_juego": semanas_en_juego,
        "que_verificar": texto,
        "motivo": ("El total impreso es la referencia contra la que se verifica "
                   "toda extracción (esquema-datos.md, sección de verificación). "
                   "Si no cuadra, el número no se puede dar por bueno."),
        "detalle": {
            "total_del_documento": total_documento,
            "suma_de_las_filas": round(calculado, 2),
            "diferencia": diferencia,
            "nota_del_documento": resumen.get("nota_verificacion"),
        },
        "_dias_reclamados": {},
    }]


def _semanas_de_las_filas(periodos):
    """Recalcula el total de semanas del documento desde sus propias filas.

    Usa la misma convención que el resto del repo, y por buenas razones:

    - Formato Colpensiones (trae semanas válidas): se reconstruyen los días
      exactos de cada fila (semanas x 7) y se divide al final. Sumar las filas
      ya redondeadas a dos decimales sobreestima: en un documento de 293 filas
      la diferencia llegó a 0,70 semanas (esquema-datos.md, regla 6).
    - Formato mensual (trae días): se reparten los días de cada fila entre los
      meses que cubre, con tope de 30 por mes, porque con dos empleadores en
      el mismo mes las semanas se cuentan una sola vez (esquema-datos.md,
      regla 3). Casi siempre cada fila es un mes y el reparto no hace nada,
      pero una extracción puede traer una fila de varios meses y sin el
      reparto se perdería todo menos el primero.
    """
    if any(p.get("semanas_validas") is not None for p in periodos):
        dias = sum(round((p.get("semanas_validas") or 0) * 7) for p in periodos)
        return dias / 7

    if not any(p.get("dias_cotizados") is not None for p in periodos):
        return None           # Ni semanas ni días: no hay nada que sumar

    dias_por_mes = {}
    for p in periodos:
        restantes = p.get("dias_cotizados") or 0
        for mes in _meses_del_rango(p["desde"], p["hasta"]):
            del_mes = min(DIAS_POR_MES, restantes)
            dias_por_mes[mes] = dias_por_mes.get(mes, 0) + del_mes
            restantes -= del_mes
    return sum(min(d, DIAS_POR_MES) for d in dias_por_mes.values()) / 7


# ---------------------------------------------------------------------------
# Resumen para el agente
# ---------------------------------------------------------------------------

def resumir(deteccion):
    """Condensa la detección en lo que el agente puede decir en voz alta.

    Separa los hallazgos por confianza porque no se comunican igual: los de
    confianza alta se nombran como hechos del documento, los de confianza baja
    se mencionan solo si la persona pregunta o si el resto ya se resolvió.
    """
    anomalias = deteccion["anomalias"]
    por_tipo = {}
    for anomalia in anomalias:
        por_tipo[anomalia["tipo"]] = por_tipo.get(anomalia["tipo"], 0) + 1
    return {
        "total": len(anomalias),
        "alta": sum(1 for a in anomalias if a["confianza"] == "alta"),
        "media": sum(1 for a in anomalias if a["confianza"] == "media"),
        "baja": sum(1 for a in anomalias if a["confianza"] == "baja"),
        "por_tipo": por_tipo,
        "semanas_en_juego_total": deteccion["semanas_en_juego_total"],
    }
