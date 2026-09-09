# Módulo RAIS: diagnóstico de pensión en fondos privados (ahorro individual).
# Implementa las reglas de kit-contexto/reglas-rais.md tal cual están escritas.
# La lógica es distinta al RPM: aquí no hay fórmula legal sobre el salario;
# el saldo de la cuenta se proyecta con rendimientos y se convierte en mesada.

from datetime import date

# Datos verificados del sistema y parámetros RAIS
from datos_sistema import (
    SMLMV, EDAD_PENSION, APORTE_A_CUENTA_RAIS, SEMANAS_GPM, semanas_gpm,
    CAPITAL_MINIMO_PCT, INTERES_TECNICO, EXPECTATIVA_VIDA, RENDIMIENTO_REAL,
    RENDIMIENTO_REAL_OBSERVADO, RENDIMIENTO_REAL_OBSERVADO_CENTRAL,
    RENDIMIENTO_REAL_PROSPECTIVO, FUENTE_RENDIMIENTO, ADVERTENCIA_RENDIMIENTO,
    ADVERTENCIA_PROSPECTIVO, FUENTE_PRIMA_RENTA_VARIABLE,
    EXPOSICION_RENTA_VARIABLE, PRIMA_RENTA_VARIABLE_LARGO_PLAZO,
    MODERADO_NO_SUPERA_A_CONSERVADOR,
    INTERES_MERCADO, FUENTE_FACTOR, MESADAS, interes_mercado, factor_mercado,
    FACTOR_MERCADO_REFERENCIA, FACTOR_MERCADO_REFERENCIA_SEXO,
    FACTOR_MERCADO_REFERENCIA_EDAD, ANIO_DECRETO_1485, CAPITAL_RV_UN_SMLMV,
    EDAD_CAPITAL_RV, tmr_real, factor_tmr, factor_solo_prensa, TMR_FUENTE,
    TMR_QUE_ES, TMR_PLAZO_MAXIMO_LIMPIO,
)
# Reutilizamos del módulo RPM el conteo de semanas, la densidad, el salario
# actual y las utilidades de fechas (una sola definición de cada regla)
from rpm import (
    expandir_a_meses, total_dias, densidad_reciente, ibc_actual,
    sumar_anios, meses_entre,
)


# ---------------------------------------------------------------------------
# Conversión de capital a mesada: LA BANDA
# ---------------------------------------------------------------------------
# Decisiones 1 y 2 de Santiago (2026-07-27). Todo lo que dependa del factor sale
# en banda: la mesada, la edad de pensión anticipada y el capital que exige el
# umbral del 110% del salario mínimo. El porqué y las fuentes de cada extremo
# están en datos_sistema.py, bajo "BANDA DEL FACTOR DE CONVERSIÓN".

# Los dos extremos, nombrados una sola vez para que nadie los cruce por error.
# "optimista" da la mesada MÁS ALTA (capital más barato de convertir en renta).
# El extremo optimista es una constante de la norma; el conservador depende del
# sexo y del año de pensión, porque el precio de mercado sí depende de los dos.


def extremos(sexo="M", anio_pension=None):
    """Las dos tasas con las que se convierte capital en mesada.

    sexo y anio_pension solo mueven el extremo conservador: el ancla de mercado
    es distinta para hombres y mujeres, y desde 2027 el Decreto 1485 encarece la
    renta vitalicia. El extremo optimista es siempre el 4% de la norma.
    """
    return {"optimista": INTERES_TECNICO,
            "conservador": interes_mercado(sexo, anio_pension)}


# Valores por defecto (hombre, precio de mercado vigente), para el código que
# no necesita distinguir. Se conserva el nombre que ya usaban otros módulos.
EXTREMOS = extremos()


def factor_conversion(anios_esperados, interes=None):
    """Cuántos 'pesos de capital' cuesta cada peso de mesada mensual.

    Es el valor presente de pagar 13 mesadas al año durante la expectativa
    de vida, descontado a la tasa que se le pase. Ejemplo: si el factor
    da 220, se necesitan $220 ahorrados por cada $1 de mesada de por vida.
    Si no se pasa tasa se usa el 4% normativo, que es el extremo optimista y
    lo que la calculadora daba antes de que existiera la banda.
    Limitación V1: no incluye beneficiarios de sobrevivencia (la mesada real
    puede ser menor); ver reglas-rais.md sección 5.
    """
    i = INTERES_TECNICO if interes is None else interes
    # Fórmula estándar de anualidad: valor presente de $1 al año por n años
    anualidad = (1 - (1 + i) ** -anios_esperados) / i
    return MESADAS * anualidad


def mesada_desde_saldo(saldo, anios_esperados, interes=None):
    """Convierte un saldo acumulado en mesada mensual estimada (pesos de hoy)."""
    return saldo / factor_conversion(anios_esperados, interes)


def banda_mesada(saldo, anios_esperados, sexo="M", anio_pension=None):
    """La mesada que financia ese saldo, en sus dos extremos.

    Devuelve un diccionario con las dos cifras. La conservadora siempre es la
    menor, porque comprar la misma renta cuesta más capital en el mercado que
    a la tasa de reserva de la norma.
    """
    return {nombre: mesada_desde_saldo(saldo, anios_esperados, tasa)
            for nombre, tasa in extremos(sexo, anio_pension).items()}


def capital_necesario(mesada_objetivo, anios_esperados, sexo="M",
                      anio_pension=None):
    """Cuánto capital hay que tener para financiar esa mesada, en los dos extremos.

    Es la cuenta al revés de la mesada, y es la que define el umbral del 110%
    del salario mínimo que decide la pensión anticipada (Ley 100 art. 64).
    """
    return {nombre: round(mesada_objetivo * factor_conversion(anios_esperados, tasa))
            for nombre, tasa in extremos(sexo, anio_pension).items()}


def declaracion_banda(anios_esperados, sexo="M", anio_pension=None):
    """El bloque que explica de dónde sale cada extremo y por qué difieren.

    Viaja DENTRO del diagnóstico, pegado a las cifras, para que el agente no
    pueda mostrar la banda sin decir qué la produce (decisión 1 de Santiago).
    """
    detalle = {}
    for nombre, tasa in extremos(sexo, anio_pension).items():
        ficha = FUENTE_FACTOR[nombre]
        detalle[nombre] = {
            "tasa_real_anual": round(tasa, 6),
            "factor": round(factor_conversion(anios_esperados, tasa), 1),
            "de_donde_sale": ficha["nombre"],
            "fuente": ficha["fuente"],
            "confianza": ficha["confianza"],
            "advertencia": ficha["advertencia"],
        }
    capital_ancla = CAPITAL_RV_UN_SMLMV[2026][sexo]
    aplica_1485 = anio_pension is not None and anio_pension >= ANIO_DECRETO_1485
    return {
        "extremos": detalle,
        "por_que_difieren": (
            "el 4% es la tasa de RESERVA que la norma le exige al sistema, no el "
            "precio al que una aseguradora vende una renta vitalicia. Ese precio "
            "lo fija cada aseguradora en su nota técnica y no está publicado, así "
            "que la calculadora no puede dar un número único sin fingir una "
            "precisión que no tiene"),
        "referencia_del_extremo_conservador": (
            f"capital de ${capital_ancla:,.0f}".replace(",", ".") +
            f" que exige hoy una renta vitalicia de un salario mínimo para "
            f"{'un hombre' if sexo == 'M' else 'una mujer'} de "
            f"{EDAD_CAPITAL_RV[sexo]} años, que equivale a un factor de "
            f"{factor_mercado(sexo):.1f}. La edad a la que corresponde ese "
            "capital NO la dice la fuente: se supone la edad legal de pensión, y "
            "ese supuesto no está verificado"),
        "decreto_1485_de_2025": (
            "aplicado: quien se pensione desde 2027 compra la renta ya "
            f"encarecida, un {100 * (factor_mercado(sexo, ANIO_DECRETO_1485) / factor_mercado(sexo) - 1):.1f}% "
            f"para {'hombres' if sexo == 'M' else 'mujeres'} según los capitales "
            "de la fuente. El '14%' que circula en prensa NO está en el decreto: "
            "es una cifra derivada por el medio, y recalculada da distinto por "
            "sexo"
            if aplica_1485 else
            "no aplicado: el decreto encarece las rentas vitalicias NUEVAS desde "
            "2027 y esta persona no queda dentro de ese alcance"),
        "inconsistencia_de_la_fuente": (
            "los dos capitales de prensa no se reproducen con una sola tasa de "
            "descuento: la mujer vive 39% más y su renta costaría apenas 7% más. "
            "El vector TMR de la Superfinanciera resolvió la duda: el dato del "
            "hombre queda por debajo de la reserva matemática, que es lo "
            "coherente, y el de la mujer quedaba por encima, o sea vendiendo por "
            "debajo de la reserva. El dato de prensa de la mujer no se sostiene y "
            "manda la cota de fuente primaria"),
        "piso_de_reserva_tmr": {
            "que_es": TMR_QUE_ES,
            "fuente": TMR_FUENTE,
            "tasa_real_al_plazo": round(tmr_real(anios_esperados), 6),
            "factor_piso": round(factor_tmr(sexo), 1),
            "factor_de_prensa": round(factor_solo_prensa(sexo), 1),
            "cual_mando": ("la TMR: el dato de prensa habría puesto el precio por "
                           "debajo de la reserva matemática"
                           if factor_tmr(sexo) > factor_solo_prensa(sexo) else
                           "el capital de prensa: queda por encima del piso de "
                           "reserva, que es lo esperado de un precio con margen"),
            "salvedad_del_plazo": (
                "la inflación implícita del anexo se topa en 3,00% desde el plazo "
                "30 y ya está en transición en el 29, así que la tasa real solo "
                "es legible hasta el plazo 28. Para expectativas mayores se usa "
                "el plazo 28, y la curva es tan plana en esa zona que el efecto "
                "es menor"
                if anios_esperados > TMR_PLAZO_MAXIMO_LIMPIO else
                "el plazo cae dentro de la zona donde la inflación implícita del "
                "anexo es dato de mercado, sin topes"),
        },
        "como_se_combina_con_los_perfiles_de_fondo": REGLA_BANDA_Y_PERFILES,
    }


# Cómo conviven las dos fuentes de rango. Se declara como texto porque el agente
# tiene que poder decirlo, no solo calcularlo.
REGLA_BANDA_Y_PERFILES = (
    "son dos rangos de naturaleza distinta y NO se multiplican entre sí. El "
    "perfil de fondo (conservador, moderado, mayor riesgo) es una DECISIÓN del "
    "usuario sobre dónde está su plata; la banda del factor es INCERTIDUMBRE del "
    "modelo sobre el precio de la renta vitalicia. Regla: el perfil manda las "
    "filas y la banda manda las columnas. Cada perfil trae sus dos extremos, y "
    "el rango que el agente comunica como 'tu mesada' es el del perfil que le "
    "aplica al usuario, no el que va del piso del perfil conservador al techo "
    "del de mayor riesgo. Para la pensión anticipada y el umbral del 110%, donde "
    "hoy solo se calcula el perfil moderado, el rango que se muestra es solo el "
    "del factor, y así se dice")


# Cómo conviven las DOS bandas del RAIS, medido antes de decidir (2026-07-27).
REGLA_DOS_BANDAS = (
    "el RAIS tiene dos fuentes de rango y NO se multiplican. (1) La banda del "
    "FACTOR de conversión es incertidumbre del modelo sobre el precio de la "
    "renta vitalicia: el usuario no puede hacer nada al respecto, y es la que se "
    "comunica como 'tu mesada'. (2) La banda del RENDIMIENTO es la diferencia "
    "entre administradoras observada por la Superfinanciera: NO es riesgo de "
    "mercado, es con cuál AFP está, así que es una palanca accionable y se "
    "muestra aparte, como 'lo que pesa tu administradora'. La cifra principal de "
    "cada perfil usa el rendimiento CENTRAL de su rango. La envolvente de las dos "
    "bandas se calcula y se guarda para auditoría, pero no se comunica: medida "
    "sobre el caso-03, el factor solo ya da un rango de 1,67 veces, y "
    "multiplicarlo por el de administradora lo lleva a 2,17 veces en el perfil "
    "moderado (de 6,5 a 14,0 millones). Un rango donde el techo es más del doble "
    "del piso no le permite decidir nada a nadie")


# ---------------------------------------------------------------------------
# Proyección del saldo hacia el futuro
# ---------------------------------------------------------------------------

def proyectar_saldo(saldo_hoy, aporte_mensual, meses_futuros, rendimiento_real):
    """Proyecta el saldo mes a mes: lo ahorrado rinde y cada mes entra un aporte.

    Todo en términos reales (pesos de hoy): el rendimiento ya descuenta la
    inflación, así el resultado se lee directo en poder adquisitivo actual.
    """
    # Convertimos el rendimiento anual a mensual (interés compuesto)
    r_mes = (1 + rendimiento_real) ** (1 / 12) - 1
    saldo = saldo_hoy
    for _ in range(meses_futuros):
        saldo = saldo * (1 + r_mes) + aporte_mensual
    return saldo


def estimar_saldo_desde_aportes(periodos):
    """Estimación de PISO del saldo cuando el documento no lo trae.

    Suma lo que entró a la cuenta (11,5 de cada 16 puntos cotizados) SIN
    rendimientos: el saldo real debería ser mayor. Se usa solo como respaldo
    y siempre marcado como estimación; el agente debe pedir el saldo real.
    """
    total = 0.0
    for p in periodos:
        if p.get("cotizacion"):
            # De cada peso cotizado, solo la fracción 11,5/16 va a la cuenta
            total += p["cotizacion"] * (APORTE_A_CUENTA_RAIS / 0.16)
    return round(total) if total > 0 else None


# ---------------------------------------------------------------------------
# El diagnóstico completo RAIS
# ---------------------------------------------------------------------------

def clasificar_salida(mesada, semanas, smlmv, sexo="M", anio=2026):
    """Decide cuál de las 3 salidas del RAIS aplica (reglas-rais.md sección 3).

    El mínimo de semanas de la GPM depende del sexo y del año desde la
    Sentencia C-054 de 2024: las mujeres bajan 15 por año desde 2026.
    """
    if mesada >= CAPITAL_MINIMO_PCT * smlmv:
        return "pension_por_capital"       # El saldo financia la pensión solo
    if semanas >= semanas_gpm(sexo, anio):
        return "garantia_pension_minima"   # El Estado completa hasta 1 SMLMV
    return "devolucion_de_saldos"          # Devuelven el saldo con rendimientos


def diagnosticar(caso, sexo=None, edad=None, fecha_calculo=None,
                 ibc_futuro=None, densidad_futura=None):
    """Produce el diagnóstico RAIS completo de un caso del set dorado.

    sexo y edad se pasan aparte cuando el documento no los trae (regla:
    nunca se infiere; se le pregunta al usuario).

    ibc_futuro y densidad_futura son los dos supuestos del escenario "sigue
    cotizando", iguales a los del módulo RPM: el salario sobre el que cotizaría
    de aquí en adelante (en pesos de hoy) y el ritmo con que lo haría. Si no se
    pasan, se usan los del propio historial. Son la palanca para responder
    "¿y si cotizo sobre más?" con la calculadora y no a ojo.
    """
    fecha_calculo = fecha_calculo or date.today()
    smlmv_hoy = SMLMV[max(SMLMV)]
    afiliado = caso["afiliado"]
    periodos = caso["periodos"]

    # --- Datos del afiliado: sexo y edad (del documento o del usuario) ---
    sexo = sexo or afiliado.get("sexo")
    nacimiento = None
    if afiliado.get("fecha_nacimiento"):
        nacimiento = date.fromisoformat(afiliado["fecha_nacimiento"])
    if edad is None:
        if nacimiento:
            edad = (fecha_calculo - nacimiento).days // 365
        else:
            edad = afiliado.get("edad_en_documento")  # Ej. Protección solo trae edad
    if sexo is None or edad is None:
        return {"error": "Faltan sexo o edad: preguntar al usuario (nada se infiere)"}

    # --- Situación actual: semanas, saldo, ritmo de cotización ---
    dias = total_dias(periodos)
    semanas = round(dias / 7, 2)
    saldo = caso["resumen_documento"]["saldo_cuenta_individual"]
    saldo_estimado = False
    if saldo is None:
        # El documento no trae saldo (ej. Skandia): estimamos un piso y lo marcamos
        saldo = estimar_saldo_desde_aportes(periodos)
        saldo_estimado = True

    meses = expandir_a_meses(periodos)
    densidad = densidad_reciente(meses, fecha_calculo)
    # El salario actual: el IBC del último MES con cotización real, no el de la
    # última fila del documento. La diferencia importa por tres razones: el
    # documento puede no venir en orden cronológico, la última fila puede ser
    # una novedad administrativa sin aporte (salario fantasma), y si ese mes
    # tuvo dos empleadores hay que sumar los dos IBC, no quedarse con uno.
    ibc_hoy = ibc_actual(meses)

    # --- Supuestos del escenario "sigue cotizando" ---
    # Por defecto los suyos (mismo salario, mismo ritmo); el usuario puede
    # cambiar cualquiera de los dos y ver cuánto mueve su mesada.
    densidad_proyectada = densidad if densidad_futura is None else densidad_futura
    ibc_proyectado = ibc_futuro or ibc_hoy

    # --- Proyección a la edad legal (57/62) en los 3 perfiles de fondo ---
    edad_legal = EDAD_PENSION[sexo]
    expectativa = EXPECTATIVA_VIDA[sexo]
    # Cuántos meses faltan para la edad legal. Con fecha de nacimiento se cuenta
    # de fecha a fecha; contarlo en años enteros de edad se come hasta 11 meses
    # de aportes y de rendimientos, que es plata real en la cuenta.
    if nacimiento:
        fecha_edad_legal = sumar_anios(nacimiento, edad_legal)
        meses_futuros = max(0, meses_entre(fecha_calculo, fecha_edad_legal))
        anio_edad_legal = fecha_edad_legal.year
        horizonte_exacto = True
    else:
        # Solo tenemos la edad en años: el horizonte queda con un margen de
        # hasta 12 meses y se declara como aproximado (nada se infiere en
        # silencio). Con la fecha de nacimiento el número se afina.
        meses_futuros = max(0, (edad_legal - edad) * 12)
        anio_edad_legal = fecha_calculo.year + max(0, edad_legal - edad)
        horizonte_exacto = False
    # Semanas que tendría a la edad legal si sigue cotizando al ritmo supuesto
    semanas_futuras = round((dias + meses_futuros * 30 * densidad_proyectada) / 7, 1)
    # El año en que cumple la edad legal es el momento en que se evalúa la GPM,
    # y para las mujeres el requisito de semanas depende de ese año (C-054/2024)
    semanas_gpm_aplicable = semanas_gpm(sexo, anio_edad_legal)
    # Aporte mensual real a la cuenta: 11,5% del salario, ajustado por densidad
    aporte_mensual = (ibc_proyectado or 0) * APORTE_A_CUENTA_RAIS * densidad_proyectada

    def mesada_con_piso(saldo_final, tasa, semanas_aplicables):
        """Mesada que financia un saldo a una tasa, ya con el piso de la GPM.

        La garantía de pensión mínima es un PISO: garantiza al menos 1 SMLMV,
        pero si el propio capital financia más, la mesada no baja. Va en función
        aparte porque lo necesitan por igual la banda del factor y la del
        rendimiento, y aplicarlo en un sitio y no en el otro deja cifras que se
        contradicen entre sí (pasó al armar la banda por administradora).
        """
        mesada = mesada_desde_saldo(saldo_final, expectativa, tasa)
        salida = clasificar_salida(mesada, semanas_aplicables, smlmv_hoy,
                                   sexo, anio_edad_legal)
        if salida == "garantia_pension_minima":
            return max(mesada, smlmv_hoy), salida
        return mesada, salida

    def escenario_desde_saldo(saldo_final, semanas_aplicables):
        """Arma un escenario con sus DOS extremos de mesada a partir de un saldo.

        El saldo proyectado no depende del factor (depende del rendimiento del
        fondo), así que es uno solo; lo que se abre en banda es la conversión de
        ese saldo en mesada. Las llaves "mesada" y "salida", sin apellido, son el
        extremo OPTIMISTA: son las que la calculadora daba antes de la banda y
        las que siguen leyendo los otros módulos.
        """
        fila = {"saldo_proyectado": round(saldo_final)}
        # El precio de mercado depende del sexo y del año en que compre la renta
        for nombre, tasa in extremos(sexo, anio_edad_legal).items():
            mesada_final, salida = mesada_con_piso(saldo_final, tasa,
                                                   semanas_aplicables)
            sufijo = "" if nombre == "optimista" else "_conservadora"
            fila["mesada" + sufijo] = round(mesada_final)
            fila["salida" + ("" if nombre == "optimista" else "_conservadora")] = salida
        # La banda lista de menor a mayor, para que nunca se muestre al revés
        fila["mesada_banda"] = (fila["mesada_conservadora"], fila["mesada"])
        return fila

    def escenario_de_perfil(perfil, aporte, semanas_aplicables):
        """Arma el escenario de un perfil con SUS DOS BANDAS, sin multiplicarlas.

        La banda que se comunica (`mesada_banda`) es la del factor, calculada con
        el rendimiento CENTRAL del perfil. La del rendimiento va aparte, en
        `mesada_banda_afp`, porque no es incertidumbre sino la diferencia entre
        administradoras, que el usuario sí puede accionar. Y la envolvente de las
        dos se calcula pero se marca como no comunicable: ver REGLA_DOS_BANDAS.
        """
        # El NIVEL es supuesto (prospectivo de largo plazo, decisión de Santiago
        # del 2026-07-28) y la DISPERSIÓN es dato (lo que separa a la mejor AFP
        # de la peor en el periodo medido). No se mezclan: se toma la distancia
        # observada de cada extremo a su centro y se traslada al nivel supuesto.
        # Así la banda entre administradoras sigue midiendo un hecho, aunque el
        # punto sobre el que se apoya sea una apuesta sobre el largo plazo.
        obs_piso, obs_techo = RENDIMIENTO_REAL_OBSERVADO[perfil]
        obs_centro = RENDIMIENTO_REAL_OBSERVADO_CENTRAL[perfil]
        centro_r = RENDIMIENTO_REAL_PROSPECTIVO[perfil]
        piso_r = centro_r + (obs_piso - obs_centro)
        techo_r = centro_r + (obs_techo - obs_centro)

        def saldo_con(rendimiento):
            return proyectar_saldo(saldo, aporte, meses_futuros, rendimiento)

        # La cifra principal del perfil: rendimiento central, banda del factor
        fila = escenario_desde_saldo(saldo_con(centro_r), semanas_aplicables)

        # Efecto de la administradora, aislado: mismo factor (el optimista),
        # solo cambia el rendimiento. Así se ve cuánto pesa la AFP y nada más.
        tasa_optimista = extremos(sexo, anio_edad_legal)["optimista"]
        tasa_conservadora = extremos(sexo, anio_edad_legal)["conservador"]
        mesada_afp_piso, _ = mesada_con_piso(saldo_con(piso_r), tasa_optimista,
                                             semanas_aplicables)
        mesada_afp_techo, _ = mesada_con_piso(saldo_con(techo_r), tasa_optimista,
                                              semanas_aplicables)
        fila["mesada_banda_afp"] = (round(mesada_afp_piso),
                                    round(mesada_afp_techo))
        fila["rendimiento_rango"] = (piso_r, techo_r)
        fila["rendimiento_central"] = centro_r

        # Envolvente de las dos bandas: la peor combinación contra la mejor.
        # Se entrega para que se pueda auditar, con la marca de no comunicarla.
        peor, _ = mesada_con_piso(saldo_con(piso_r), tasa_conservadora,
                                  semanas_aplicables)
        fila["mesada_envolvente"] = (round(peor), round(mesada_afp_techo))
        fila["mesada_envolvente_no_comunicar"] = (
            "esta envolvente multiplica las dos bandas y se entrega solo para "
            "auditoría. No se le muestra al usuario: ver REGLA_DOS_BANDAS")
        return fila

    escenarios = {}
    if saldo is not None:
        for perfil in RENDIMIENTO_REAL_PROSPECTIVO:
            # Escenario "sigue cotizando": saldo crece con rendimiento + aportes
            escenarios[perfil] = escenario_de_perfil(perfil, aporte_mensual,
                                                     semanas_futuras)

        # Escenario "deja de cotizar hoy" (perfil moderado): solo rinde el saldo
        escenarios["deja_de_cotizar"] = escenario_de_perfil("moderado", 0,
                                                            semanas)

        # --- Pensión anticipada: ¿a qué edad el saldo financia 110% del mínimo? ---
        # (Ley 100 art. 64; perfil moderado, aproximación V1 de expectativa)
        # Se calcula una edad por cada extremo de la banda: con el precio de la
        # norma la pensión anticipada llega antes que con el precio de mercado.
        edades_anticipadas = {}
        for nombre in ("optimista", "conservador"):
            edades_anticipadas[nombre] = None
            for edad_x in range(edad, edad_legal + 1):
                # El año en que compraría la renta si se pensionara a esa edad:
                # decide si le aplica el precio encarecido por el Decreto 1485
                anio_x = fecha_calculo.year + (edad_x - edad)
                tasa = extremos(sexo, anio_x)[nombre]
                # Meses de aquí a que cumpla esa edad, con el mismo criterio de
                # fechas de arriba (de fecha a fecha si se conoce el nacimiento)
                if nacimiento:
                    meses_x = max(0, meses_entre(fecha_calculo,
                                                 sumar_anios(nacimiento, edad_x)))
                else:
                    meses_x = max(0, (edad_x - edad) * 12)
                saldo_x = proyectar_saldo(saldo, aporte_mensual, meses_x,
                                          RENDIMIENTO_REAL["moderado"])
                # A menor edad, más años de expectativa de vida por financiar
                expectativa_x = expectativa + (edad_legal - edad_x)
                mesada_x = mesada_desde_saldo(saldo_x, expectativa_x, tasa)
                if mesada_x >= CAPITAL_MINIMO_PCT * smlmv_hoy:
                    edades_anticipadas[nombre] = edad_x
                    break
        # Sin apellido = extremo optimista, igual que en las mesadas
        edad_anticipada = edades_anticipadas["optimista"]
        edad_anticipada_conservadora = edades_anticipadas["conservador"]
        # Cuánto capital exige el umbral del 110% del salario mínimo a la edad
        # legal, en los dos extremos: es el mismo umbral, con dos precios
        capital_umbral = capital_necesario(CAPITAL_MINIMO_PCT * smlmv_hoy,
                                           expectativa, sexo, anio_edad_legal)
    else:
        edad_anticipada = None
        edad_anticipada_conservadora = None
        capital_umbral = None

    # Armamos el diagnóstico final
    return {
        "caso_id": caso["caso_id"],
        "fecha_calculo": fecha_calculo.isoformat(),
        "edad": edad,
        "sexo": sexo,
        "edad_legal": edad_legal,
        "semanas_hoy": semanas,
        "semanas_documento": caso["resumen_documento"]["total_semanas"],
        "semanas_proyectadas_edad_legal": semanas_futuras,
        "semanas_gpm": semanas_gpm_aplicable,
        "saldo_hoy": saldo,
        "saldo_es_estimado": saldo_estimado,
        "ibc_actual": ibc_hoy,
        "densidad_ultimos_3_anios": round(densidad, 2),
        # Los supuestos que produjeron estas cifras, visibles junto a las cifras
        "ibc_futuro_supuesto": ibc_proyectado,
        "densidad_futura_supuesta": round(densidad_proyectada, 2),
        "meses_hasta_edad_legal": meses_futuros,
        # False = el horizonte se contó en años enteros de edad porque el
        # documento no trae fecha de nacimiento (margen de hasta 12 meses)
        "horizonte_exacto": horizonte_exacto,
        "escenarios": escenarios,
        # Sin apellido = extremo optimista (4% normativo), que es lo que la
        # calculadora entregaba antes de que existiera la banda
        "edad_pension_anticipada": edad_anticipada,
        "edad_pension_anticipada_conservadora": edad_anticipada_conservadora,
        # La banda de edad ordenada: primero la más temprana. None cuando alguno
        # de los dos extremos nunca alcanza el umbral antes de la edad legal
        "edad_pension_anticipada_banda": (edad_anticipada,
                                          edad_anticipada_conservadora),
        # Capital que exige el umbral del 110% del SMLMV, con los dos precios
        "capital_umbral_110_pct": capital_umbral,
        # De dónde sale cada extremo y por qué difieren: viaja con las cifras
        "banda_factor": declaracion_banda(expectativa, sexo, anio_edad_legal),
        # La segunda banda del RAIS, la del rendimiento, con su fuente y su
        # advertencia. Va separada de la del factor a propósito: no se mezclan.
        "banda_rendimiento": {
            # EVIDENCIA: lo que rindieron los fondos en el periodo medido
            "observado_rangos": dict(RENDIMIENTO_REAL_OBSERVADO),
            "observado_centrales": dict(RENDIMIENTO_REAL_OBSERVADO_CENTRAL),
            "observado_fuente": FUENTE_RENDIMIENTO,
            "observado_confianza": "MEDIA (fuente secundaria que cita a la SFC)",
            # SUPUESTO: lo que usa la proyección, por decisión de producto
            "prospectivo": dict(RENDIMIENTO_REAL_PROSPECTIVO),
            "prospectivo_advertencia": ADVERTENCIA_PROSPECTIVO,
            "prospectivo_construccion": (
                "ancla en el conservador observado "
                f"({RENDIMIENTO_REAL_OBSERVADO_CENTRAL['conservador']:.2%}), más "
                "la exposición ADICIONAL a renta variable de cada perfil respecto "
                f"de él, por una prima de {PRIMA_RENTA_VARIABLE_LARGO_PLAZO:.1%} "
                "real de largo plazo. Exposiciones supuestas: " +
                ", ".join(f"{p} {e:.0%}"
                          for p, e in EXPOSICION_RENTA_VARIABLE.items())),
            "prospectivo_fuente_de_la_prima": FUENTE_PRIMA_RENTA_VARIABLE,
            "prospectivo_eslabon_sin_verificar": (
                "[VERIFICAR] los límites de exposición a renta variable por "
                "perfil no se verificaron en fuente primaria el 2026-07-28: el "
                "Gestor Normativo no entregó el articulado del Decreto 2555 y el "
                "documento técnico de la URF es un PDF del que no se puede "
                "extraer texto. Además se asume que cada fondo usa su límite "
                "completo, cosa que ninguno hace, así que el supuesto es el borde "
                "optimista de la construcción"),
            "que_significa_el_rango": ADVERTENCIA_RENDIMIENTO,
            # La contradicción, escrita y no maquillada
            "contradiccion_con_lo_observado": (
                "en el único periodo medido por la Superfinanciera (2011 a 2024) "
                "el punto central del perfil moderado (2,56%) quedó POR DEBAJO "
                "del conservador (2,61%): el moderado NO le ganó al conservador. "
                "La proyección usa un supuesto de largo plazo que asume lo "
                "contrario, por decisión de producto de Santiago del 2026-07-28. "
                "El dato observado no se borra ni se ajusta: si la pregunta es "
                "qué rindió cada fondo, la respuesta es el dato, no el supuesto"),
            "moderado_no_supera_a_conservador": MODERADO_NO_SUPERA_A_CONSERVADOR,
        },
        # Cómo conviven las dos bandas, para que el agente pueda explicarlo
        "regla_dos_bandas": REGLA_DOS_BANDAS,
    }
