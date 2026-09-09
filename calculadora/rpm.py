# Módulo RPM: diagnóstico de pensión en Colpensiones (Régimen de Prima Media).
# Implementa las reglas de kit-contexto/reglas-rpm.md tal cual están escritas.
# Entrada: un caso JSON con el esquema de V0/casos/esquema-datos.md + el sexo
# (que casi nunca viene en el documento y se le pregunta al usuario).
# Salida: un diccionario con el diagnóstico completo (semanas, requisitos,
# IBL, tasa de reemplazo y mesada estimada en pesos de hoy).

from datetime import date

# Importamos los datos verificados del sistema (salario mínimo, IPC, requisitos)
from datos_sistema import (
    SMLMV, EDAD_PENSION, MESADAS, TOPE_MESADA_EN_SMLMV,
    semanas_requeridas, factor_ipc,
)

# Límites legales de la TASA BASE de reemplazo, la que sale de la fórmula
# r = 65,5 - 0,5 s antes de sumar el premio por semanas adicionales.
# La ley dice que ese porcentaje "oscilará entre el 65 y el 55%" del IBL.
# Fuente: Ley 100 de 1993 art. 34, mod. Ley 797 de 2003 art. 10.
# Verificado el 2026-07-27 contra Secretaría del Senado. Confianza: ALTA.
# Ojo con la trampa que ya cayó una vez en este proyecto: 55,5% NO es el piso
# legal, es el valor de la fórmula en s = 20. El piso es 55%.
TASA_BASE_MINIMA = 55.0
TASA_BASE_MAXIMA = 65.0

# Tope legal del IBC de un mes: nadie cotiza sobre más de 25 salarios mínimos,
# ni siquiera sumando varios empleadores al tiempo.
# Fuente: Ley 100 de 1993 art. 18; reglas-rpm.md s.8.2 ("los IBC se suman
# sin exceder 25 SMLMV"). Ojo: se mide con el salario mínimo DEL AÑO de la
# cotización, no con el de hoy (ver tope_ibc_del_anio).
TOPE_IBC_EN_SMLMV = 25

# Semanas mínimas que exige la ley para poder usar el IBL de toda la vida
# laboral en vez del de los últimos 10 años.
# Fuente: Ley 100 de 1993 art. 21, inciso final; reglas-rpm.md s.4.2, que dice
# "si el afiliado cotizó al menos 1.250 semanas y ese promedio le resulta
# superior". Kit y norma coinciden en el número (verificado 2026-07-28).
SEMANAS_PARA_IBL_TODA_LA_VIDA = 1250

# Freno de seguridad de la proyección de semanas: 60 años de meses futuros.
# Si en 60 años no alcanza el requisito, no lo va a alcanzar nunca.
MAX_MESES_PROYECCION = 720


# ---------------------------------------------------------------------------
# Utilidades de fechas: trabajamos mes a mes con la convención de 30 días/mes
# ---------------------------------------------------------------------------

def mes_siguiente(anio, mes):
    """Devuelve el (año, mes) que sigue. Ejemplo: (2026, 12) -> (2027, 1)."""
    return (anio + 1, 1) if mes == 12 else (anio, mes + 1)


def meses_entre(desde, hasta):
    """Cuenta cuántos meses hay entre dos fechas. Ejemplo: ene a mar = 2."""
    return (hasta.year - desde.year) * 12 + (hasta.month - desde.month)


def sumar_anios(fecha, anios):
    """Suma años a una fecha (para calcular cuándo se cumple la edad de pensión)."""
    try:
        return fecha.replace(year=fecha.year + anios)
    except ValueError:  # Caso especial: nacido un 29 de febrero
        return fecha.replace(year=fecha.year + anios, day=28)


# ---------------------------------------------------------------------------
# Paso 1: convertir los periodos del documento a un mapa mes a mes
# ---------------------------------------------------------------------------

def tope_ibc_del_anio(anio):
    """Cuánto es el tope de 25 salarios mínimos en el año que se cotizó.

    Por qué el año importa: el salario mínimo ha crecido mucho más rápido que
    la inflación, así que 25 salarios mínimos de 2015 son muchísimo menos plata
    que 25 de hoy. Topar una cotización vieja con el salario mínimo de hoy sería
    dejar pasar salarios que en su momento eran ilegales por altos.
    Si el año queda fuera de la serie cargada, se usa el extremo más cercano
    (los años futuros ya vienen en pesos de hoy, así que les aplica el tope de
    hoy; y no se inventa un salario mínimo que nadie ha decretado).
    """
    anio_en_la_serie = min(max(anio, min(SMLMV)), max(SMLMV))
    return TOPE_IBC_EN_SMLMV * SMLMV[anio_en_la_serie]


def expandir_a_meses(periodos):
    """Convierte los periodos (rangos o meses) en un mapa: mes -> días e IBC.

    Reglas aplicadas (ver esquema-datos.md):
    - Los días de cada fila se reconstruyen desde las semanas exactas (x 7).
    - En rangos de Colpensiones, los días se reparten desde el inicio,
      máximo 30 por mes (así funcionan los rangos continuos del reporte).
    - Si dos empleadores caen en el mismo mes: los días se topan en 30
      (las semanas se cuentan una vez) pero los IBC se SUMAN (regla de
      simultaneidad para el promedio salarial), sin pasar de 25 SMLMV del
      año de la cotización, que es el tope legal del IBC mensual.
    - Aproximación V1 documentada: en rangos, el IBC es el último del rango
      y se aplica a todos sus meses (es lo único que trae el resumen).
    """
    meses = {}  # clave (año, mes) -> {"dias": int, "ibc": float}
    for p in periodos:
        # Reconstruimos los días exactos de la fila (regla del día exacto)
        if p.get("semanas_validas") is not None:
            dias_fila = round(p["semanas_validas"] * 7)
        else:
            dias_fila = p["dias_cotizados"] or 0

        # Recorremos los meses del rango repartiendo los días (máx. 30 por mes)
        anio, mes = int(p["desde"][:4]), int(p["desde"][5:7])
        fin_anio, fin_mes = int(p["hasta"][:4]), int(p["hasta"][5:7])
        dias_restantes = dias_fila
        while (anio, mes) <= (fin_anio, fin_mes):
            registro = meses.setdefault((anio, mes), {"dias": 0, "ibc": 0.0})
            dias_de_este_mes = min(30, dias_restantes)
            # Tope de 30 días por mes aunque haya varios empleadores
            registro["dias"] = min(30, registro["dias"] + dias_de_este_mes)
            # Los salarios de empleadores simultáneos se suman, pero solo si esa
            # fila reportó cotización de verdad (días propios o semanas marcadas
            # como simultáneas). Una fila en ceros es una novedad administrativa
            # sin aporte: sumar su salario inflaría el promedio del IBL.
            cotizo_de_verdad = dias_de_este_mes > 0 or (p.get("semanas_sim") or 0) > 0
            if p.get("ibc") and cotizo_de_verdad:
                registro["ibc"] += p["ibc"]
            dias_restantes -= dias_de_este_mes
            anio, mes = mes_siguiente(anio, mes)
    # Ya sumados todos los empleadores del mes, aplicamos el tope legal: el IBC
    # de un mes nunca pasa de 25 salarios mínimos DEL AÑO en que se cotizó.
    # Sin esto, dos empleos simultáneos de 20 SMLMV daban un IBC de 40 SMLMV y
    # la mesada salía sobreestimada (reglas-rpm.md s.8.2; Ley 100 art. 18).
    for (anio, _mes), registro in meses.items():
        registro["ibc"] = min(registro["ibc"], tope_ibc_del_anio(anio))
    return meses


def total_dias(periodos):
    """Total de días cotizados, directo de las filas del documento.

    Regla del día exacto: los rangos de Colpensiones cuentan días calendario
    reales (pueden superar 30 x meses del rango), así que el total se
    reconstruye fila por fila (semanas x 7), NO desde el mapa mensual,
    que es una aproximación de 30 días/mes para ponderar el IBL.
    Misma lógica que casos/herramientas/verificar_casos.py.
    """
    if any(p.get("semanas_validas") is not None for p in periodos):
        # Formato Colpensiones: las filas simultáneas ya vienen con válidas = 0
        return sum(round((p["semanas_validas"] or 0) * 7) for p in periodos)
    # Formato mensual de fondos privados: tope de 30 días por mes (simultaneidad)
    dias_por_mes = {}
    for p in periodos:
        mes = p["desde"][:7]
        dias_por_mes[mes] = dias_por_mes.get(mes, 0) + (p["dias_cotizados"] or 0)
    return sum(min(d, 30) for d in dias_por_mes.values())


# ---------------------------------------------------------------------------
# Paso 2: IBL (el salario promedio sobre el que se calcula la pensión)
# ---------------------------------------------------------------------------

def calcular_ibl(meses, anio_calculo, ventana_anios=10, anio_ventana=None):
    """Promedio de los salarios cotizados, traídos a pesos de hoy con IPC.

    ventana_anios=10: regla general (últimos 10 años). ventana_anios=None:
    toda la vida laboral (alternativa si hay 1.250+ semanas, Ley 100 art. 21).
    Cada mes pesa según sus días cotizados.

    anio_calculo es el año al que se indexan los pesos (siempre "hoy": todo lo
    que entrega la calculadora está en pesos de hoy). anio_ventana es el año
    contra el que se mide la ventana de 10 años; por defecto es el mismo, pero
    al proyectar una pensión futura hay que anclarla al AÑO DE PENSIÓN, porque
    la ley promedia los 10 años anteriores a esa fecha, no a hoy.
    Los meses futuros ya vienen expresados en pesos de hoy, así que no se
    indexan (factor_ipc devuelve 1,0 cuando el año es igual o posterior).

    Devuelve (ibl, mensaje). Si falta IPC para indexar algún año, devuelve
    (None, explicación): la regla de oro es no inventar datos.
    """
    anio_ventana = anio_ventana or anio_calculo
    suma_ponderada = 0.0   # Acumula salario indexado x días
    suma_dias = 0          # Acumula los días (el peso de cada mes)
    for (anio, mes), registro in meses.items():
        if registro["dias"] == 0 or registro["ibc"] == 0:
            continue  # Meses sin cotización no entran al promedio
        # Si hay ventana, solo entran los meses de los últimos N años
        if ventana_anios is not None and anio < anio_ventana - ventana_anios:
            continue
        # Traemos el salario de ese año a pesos del año de cálculo
        factor = factor_ipc(anio, anio_calculo)
        if factor is None:
            return None, (f"Falta el IPC de años anteriores a 2015 para indexar "
                          f"salarios de {anio} (pendiente: cargar serie DANE completa)")
        suma_ponderada += registro["ibc"] * factor * registro["dias"]
        suma_dias += registro["dias"]
    if suma_dias == 0:
        return None, "No hay cotizaciones en la ventana de cálculo"
    return suma_ponderada / suma_dias, None


def elegir_ibl(meses, anio_calculo, semanas, anio_ventana=None):
    """Elige el IBL con el que se liquida: el MAYOR de los dos que da la ley.

    La ley ofrece dos formas de calcular el salario base de la pensión:
    el promedio de los últimos 10 años (la regla general) o el promedio de
    TODA la vida laboral, y esta segunda solo está disponible para quien
    cotizó al menos 1.250 semanas. Cuando las dos aplican, manda la que le
    resulte superior al afiliado.
    Fuente: Ley 100 de 1993 art. 21, inciso final; reglas-rpm.md s.4.

    A quién le cambia la vida: a quien ganó mucho más hace más de 10 años y
    terminó su vida laboral cotizando poco (perdió el empleo formal, se volvió
    independiente o bajó de cargo). Liquidarlo siempre con los últimos 10 años
    le borra sus mejores años de aportes.

    Devuelve (ibl, error, detalle). detalle deja a la vista los dos valores y
    cuál se usó, para que la cifra se pueda explicar y auditar.
    """
    ibl_10, error = calcular_ibl(meses, anio_calculo, ventana_anios=10,
                                 anio_ventana=anio_ventana)
    if ibl_10 is None:
        return None, error, {}
    detalle = {"ibl_10_anios": round(ibl_10),
               "ibl_toda_la_vida": None,
               "ibl_usado": "10_anios"}
    # Sin las 1.250 semanas la alternativa no existe: no hay nada que comparar
    if semanas < SEMANAS_PARA_IBL_TODA_LA_VIDA:
        detalle["nota_ibl"] = (f"El IBL de toda la vida exige "
                               f"{SEMANAS_PARA_IBL_TODA_LA_VIDA} semanas "
                               f"cotizadas (Ley 100 art. 21) y aquí hay "
                               f"{semanas}")
        return ibl_10, None, detalle
    ibl_vida, error_vida = calcular_ibl(meses, anio_calculo, ventana_anios=None)
    if ibl_vida is None:
        # Falta el IPC de algún año viejo para indexar. No inventamos el dato:
        # liquidamos con los 10 años y avisamos que la alternativa no se pudo
        # evaluar, porque pudo haber sido la mejor para el afiliado.
        detalle["nota_ibl"] = (f"No se pudo evaluar el IBL de toda la vida "
                               f"(podría ser el mayor): {error_vida}")
        return ibl_10, None, detalle
    detalle["ibl_toda_la_vida"] = round(ibl_vida)
    # La ley dice "el que le resulte superior": aquí se elige
    if ibl_vida > ibl_10:
        detalle["ibl_usado"] = "toda_la_vida"
        return ibl_vida, None, detalle
    return ibl_10, None, detalle


# ---------------------------------------------------------------------------
# Paso 3: tasa de reemplazo y mesada (la fórmula de la Ley 797/2003)
# ---------------------------------------------------------------------------

def calcular_mesada(ibl, semanas, sexo, anio_pension):
    """Aplica la fórmula r = 65,5% - 0,5 x s y devuelve la mesada en pesos de hoy.

    - s = IBL medido en salarios mínimos de hoy.
    - La tasa base tiene PISO del 55% y techo del 65% (ver abajo).
    - Suma 1,5% por cada 50 semanas completas por encima de las mínimas.
    - Techo del total: 80% del IBL. Piso: 1 SMLMV. Tope: 25 SMLMV.
    """
    smlmv_hoy = SMLMV[max(SMLMV)]  # Salario mínimo del año más reciente cargado
    s = ibl / smlmv_hoy
    requisito = semanas_requeridas(sexo, anio_pension)
    # Fórmula base de la ley
    tasa_base = 65.5 - 0.5 * s
    # Piso y techo de la tasa BASE, antes de premiar semanas adicionales.
    # La ley no deja que la fórmula corra sin límite: dice que el monto
    # "oscilará entre el 65 y el 55%" del IBL en función del nivel de ingresos.
    # Sin este piso, un IBL de más de 21 salarios mínimos producía una tasa
    # base por debajo del 55% y la mesada quedaba subestimada.
    # Fuente: Ley 100 de 1993 art. 34, modificado por Ley 797 de 2003 art. 10.
    # Texto literal verificado el 2026-07-27 contra Secretaría del Senado:
    # "A partir del 2004, el monto mensual de la pensión de vejez será un
    # porcentaje que oscilará entre el 65 y el 55% del ingreso base de
    # liquidación de los afiliados, en forma decreciente en función de su
    # nivel de ingresos calculado con base en la fórmula señalada."
    # Confianza: ALTA (fuente primaria, la que el proyecto prefiere para la
    # Ley 100 sobre el Gestor Normativo de Función Pública).
    tasa_base = max(TASA_BASE_MINIMA, min(tasa_base, TASA_BASE_MAXIMA))
    # Premio por semanas adicionales: 1,5% por cada bloque completo de 50
    bloques_extra = max(0, int((semanas - requisito) // 50))
    tasa = tasa_base + 1.5 * bloques_extra
    # Techo legal del total: nunca más del 80% del IBL.
    # Misma norma: "El valor total de la pensión no podrá ser superior al
    # ochenta (80%) del ingreso base de liquidación, ni inferior a la pensión
    # mínima." Concuerda con el máximo "entre el 80 y el 70,5%" que la propia
    # norma anuncia, que es justo 65 + 15 y 55 + 15,5.
    tasa = min(tasa, 80.0)
    mesada = ibl * tasa / 100
    # Piso: ninguna pensión por debajo del salario mínimo
    mesada = max(mesada, smlmv_hoy)
    # Tope: ninguna pensión por encima de 25 salarios mínimos
    mesada = min(mesada, TOPE_MESADA_EN_SMLMV * smlmv_hoy)
    return {"tasa_pct": round(tasa, 2), "mesada": round(mesada),
            "s": round(s, 2), "bloques_extra": bloques_extra,
            "tasa_base_pct": round(tasa_base, 2),
            "requisito_semanas": requisito}


# ---------------------------------------------------------------------------
# Paso 4: densidad de cotización (qué tanto cotiza la persona últimamente)
# ---------------------------------------------------------------------------

def densidad_reciente(meses, fecha_calculo, anios=3):
    """Fracción del tiempo que la persona cotizó en los últimos N años.

    Ejemplo: 1,0 = cotizó todos los meses completos; 0,5 = la mitad del tiempo.
    Se usa para proyectar el futuro (supuesto ajustable por el usuario).
    """
    dias = 0
    # Contamos los días cotizados de los últimos N años (meses completos)
    for (anio, mes), registro in meses.items():
        inicio_ventana = (fecha_calculo.year - anios, fecha_calculo.month)
        if inicio_ventana <= (anio, mes) <= (fecha_calculo.year, fecha_calculo.month):
            dias += registro["dias"]
    return min(1.0, dias / (anios * 12 * 30))


def ibc_actual(meses):
    """El salario sobre el que cotiza hoy: el del último mes con cotización real.

    Es el punto de partida de toda proyección ("si sigue cotizando como hoy").
    Se ignoran los meses en ceros del final del reporte, que son novedades
    administrativas y no cotizaciones.
    """
    con_cotizacion = [k for k, v in meses.items() if v["dias"] > 0 and v["ibc"] > 0]
    if not con_cotizacion:
        return None
    return meses[max(con_cotizacion)]["ibc"]


def fecha_en_que_cumple_semanas(dias_hoy, sexo, fecha_calculo, densidad):
    """Primer mes en que las semanas acumuladas alcanzan el requisito DE ESE AÑO.

    Por qué no basta una división: el requisito de la mujer no es fijo, baja 25
    semanas cada año hasta 2036 por la Sentencia C-197. Dividir los días que
    faltan entre el ritmo mensual, usando el requisito de HOY, le exige un
    número de semanas que en ese año futuro ya no rige, y la fecha sale más
    tarde de lo que corresponde (hasta más de un año de pensión perdida).

    Por eso avanzamos mes a mes y en cada mes comparamos contra el requisito del
    año de ese mes. La cuenta siempre converge y nunca oscila: los días
    cotizados solo suben y el requisito solo baja (nunca sube de un año al
    siguiente), así que en cuanto la condición se cumple ya no se deshace, y el
    primer mes que la cumple es la respuesta. MAX_MESES_PROYECCION es un simple
    freno por si la persona cotiza tan poco que nunca llega.

    Devuelve la fecha (día 1 del mes) o None si no alcanza dentro del horizonte.
    """
    dias_por_mes = 30 * densidad
    if dias_por_mes <= 0:
        return None  # No está cotizando: al ritmo actual nunca llega
    anio, mes = fecha_calculo.year, fecha_calculo.month
    dias = dias_hoy
    for _ in range(MAX_MESES_PROYECCION):
        anio, mes = mes_siguiente(anio, mes)   # El mes en curso ya está contado
        dias += dias_por_mes
        # El requisito que hay que vencer es el del año de ESTE mes, no el de hoy
        if dias >= semanas_requeridas(sexo, anio) * 7:
            return date(anio, mes, 1)
    return None


def proyectar_meses(meses, fecha_calculo, fecha_pension, ibc_futuro, densidad):
    """Agrega al mapa de meses los que la persona cotizaría de aquí a pensionarse.

    Por qué existe: la pensión se liquida sobre el promedio de los 10 años
    ANTERIORES A LA PENSIÓN, no anteriores a hoy. Si a alguien le faltan 3 años,
    esos 3 años futuros pesan casi un tercio de su promedio. Proyectar solo las
    semanas y dejar el promedio congelado en la historia pasada subestima (o
    sobreestima) la mesada.

    ibc_futuro va en PESOS DE HOY: no se proyecta inflación en ningún punto,
    igual que el resto de la calculadora.
    Devuelve un mapa nuevo; el original no se toca.
    """
    proyectado = {k: dict(v) for k, v in meses.items()}
    anio, mes = fecha_calculo.year, fecha_calculo.month
    anio, mes = mes_siguiente(anio, mes)  # El mes en curso ya viene del documento
    dias_por_mes = round(30 * densidad)
    while (anio, mes) <= (fecha_pension.year, fecha_pension.month):
        if dias_por_mes > 0:
            proyectado[(anio, mes)] = {"dias": dias_por_mes, "ibc": ibc_futuro}
        anio, mes = mes_siguiente(anio, mes)
    return proyectado


# ---------------------------------------------------------------------------
# Paso 5: el diagnóstico completo (lo que junta todas las piezas)
# ---------------------------------------------------------------------------

def diagnosticar(caso, sexo, fecha_calculo=None, ibc_futuro=None,
                 densidad_futura=None):
    """Produce el diagnóstico RPM completo de un caso del set dorado.

    sexo se pasa aparte porque el documento casi nunca lo trae (regla:
    nunca se infiere; se le pregunta al usuario).

    ibc_futuro y densidad_futura son los dos supuestos del escenario "sigue
    cotizando". Si no se pasan, se usan los del propio historial (el salario
    del último mes cotizado y el ritmo de los últimos 3 años). Cambiarlos es lo
    que permite responder "¿y si cotizo sobre más?" con números, no con
    intuiciones. ibc_futuro va en pesos de hoy.
    """
    fecha_calculo = fecha_calculo or date.today()
    anio_hoy = fecha_calculo.year

    # --- Situación actual: edad y semanas ---
    nacimiento = date.fromisoformat(caso["afiliado"]["fecha_nacimiento"])
    edad = (fecha_calculo - nacimiento).days // 365
    meses = expandir_a_meses(caso["periodos"])          # Para IBL y densidad
    dias = total_dias(caso["periodos"])                 # Para el conteo exacto
    semanas = round(dias / 7, 2)  # Regla del día exacto

    # --- Requisitos: cuándo cumple edad y cuándo cumple semanas ---
    fecha_edad = sumar_anios(nacimiento, EDAD_PENSION[sexo])
    requisito_hoy = semanas_requeridas(sexo, anio_hoy)
    densidad = densidad_reciente(meses, fecha_calculo)
    # El ritmo con el que se proyecta el futuro: el suyo, salvo que el usuario
    # diga que va a cotizar más (o menos) de aquí en adelante.
    densidad_proyectada = densidad if densidad_futura is None else densidad_futura

    if semanas >= requisito_hoy:
        # Ya tiene las semanas: solo espera la edad
        fecha_semanas = fecha_calculo
    else:
        # Proyectamos mes a mes al ritmo supuesto (30 x densidad días por mes),
        # midiendo cada mes contra el requisito del año de ese mes.
        fecha_semanas = fecha_en_que_cumple_semanas(dias, sexo, fecha_calculo,
                                                    densidad_proyectada)

    # La pensión llega cuando se cumplen AMBOS requisitos
    fecha_pension = max(fecha_edad, fecha_semanas) if fecha_semanas else None

    # --- Escenario base: sigue cotizando hasta pensionarse ---
    # Por defecto "como hoy" (mismo salario, mismo ritmo), pero el usuario puede
    # cambiar cualquiera de los dos supuestos y ver cuánto mueve su mesada.
    escenario_base = None
    ibc_proyectado = ibc_futuro or ibc_actual(meses)
    if fecha_pension:
        # Semanas que acumularía entre hoy y la fecha de pensión
        meses_a_pension = meses_entre(fecha_calculo, fecha_pension)
        dias_futuros = meses_a_pension * 30 * densidad_proyectada
        semanas_proyectadas = round((dias + dias_futuros) / 7, 1)
        if not ibc_proyectado:
            ibl, error_ibl = None, "No hay salario reciente para proyectar el IBL"
        else:
            # El IBL se arma con los 10 años anteriores a la PENSIÓN: la parte
            # ya cotizada más los meses que le faltan por cotizar.
            meses_con_futuro = proyectar_meses(meses, fecha_calculo, fecha_pension,
                                               ibc_proyectado, densidad_proyectada)
            # De los dos IBL que da la ley se liquida con el mayor. Las semanas
            # que abren la alternativa son las que TENDRÁ al pensionarse, y su
            # vida laboral incluye los meses que le faltan por cotizar.
            ibl, error_ibl, detalle_ibl = elegir_ibl(meses_con_futuro, anio_hoy,
                                                     semanas_proyectadas,
                                                     anio_ventana=fecha_pension.year)
        if ibl:
            escenario_base = calcular_mesada(ibl, semanas_proyectadas, sexo,
                                             fecha_pension.year)
            escenario_base["semanas_proyectadas"] = semanas_proyectadas
            escenario_base["ibl"] = round(ibl)
            # Los dos IBL y cuál mandó, para poder explicar la cifra
            escenario_base.update(detalle_ibl)
            # Los supuestos que produjeron esta cifra, visibles con la cifra
            escenario_base["ibc_futuro_supuesto"] = ibc_proyectado
            escenario_base["densidad_futura_supuesta"] = round(densidad_proyectada, 2)
            # Cuando faltan 10+ años, la ventana es puro futuro: el IBL deja de
            # ser historia y pasa a ser proyección pura del salario supuesto.
            escenario_base["ibl_proyectado_desde_salario_actual"] = meses_a_pension >= 120
        escenario_base = escenario_base or {"error": error_ibl}

    # --- Escenario alterno: deja de cotizar hoy mismo ---
    requisito_en_anio_edad = semanas_requeridas(sexo, fecha_edad.year)
    if semanas >= requisito_en_anio_edad:
        # Aun sin cotizar más, se pensiona al cumplir la edad. Aquí la vida
        # laboral es la que ya tiene: no se le suma ningún mes futuro.
        ibl, error_ibl, detalle_ibl = elegir_ibl(meses, anio_hoy, semanas)
        if ibl:
            escenario_sin_cotizar = calcular_mesada(ibl, semanas, sexo,
                                                    fecha_edad.year)
            escenario_sin_cotizar["ibl"] = round(ibl)
            escenario_sin_cotizar.update(detalle_ibl)
        else:
            escenario_sin_cotizar = {"error": error_ibl}
    else:
        # No alcanzaría: el camino sería la indemnización sustitutiva
        escenario_sin_cotizar = {
            "resultado": "sin_pension",
            "nota": ("Si deja de cotizar hoy no alcanza las semanas: al cumplir "
                     "la edad solo tendría derecho a indemnización sustitutiva "
                     "(devolución sin rendimientos, ver reglas-rpm.md seccion 7)")
        }

    # --- IBL alternativo de toda la vida (si tiene 1.250+ semanas) ---
    ibl_toda_vida = None
    if semanas >= 1250:
        valor, error = calcular_ibl(meses, anio_hoy, ventana_anios=None)
        ibl_toda_vida = {"ibl": round(valor)} if valor else {"error": error}

    # Armamos el diagnóstico final con todas las piezas
    return {
        "caso_id": caso["caso_id"],
        "fecha_calculo": fecha_calculo.isoformat(),
        "edad": edad,
        "sexo": sexo,
        "semanas_hoy": semanas,
        "semanas_documento": caso["resumen_documento"]["total_semanas"],
        "requisito_semanas_hoy": requisito_hoy,
        "densidad_ultimos_3_anios": round(densidad, 2),
        "fecha_cumple_edad": fecha_edad.isoformat(),
        "fecha_cumple_semanas": fecha_semanas.isoformat() if fecha_semanas else None,
        "fecha_pension_estimada": fecha_pension.isoformat() if fecha_pension else None,
        "escenario_sigue_cotizando": escenario_base,
        "escenario_deja_de_cotizar": escenario_sin_cotizar,
        "ibl_toda_la_vida": ibl_toda_vida,
    }
