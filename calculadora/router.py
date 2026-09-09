# Router: la primera capa de decisión, en código fijo (nunca la IA).
# Recibe el JSON extraído de una historia laboral y decide:
#   1. ¿Qué régimen es? -> ¿qué módulo de la calculadora corre?
#   2. ¿Hay señales de régimen exceptuado o situación fuera de alcance?
#   3. ¿Aplica el comparador de regímenes (ventana de traslado abierta)?
# Ver kit-contexto/regimenes-especiales.md: detectar y decirlo honestamente
# es parte del diseño anti-alucinación.

from datetime import date

# Traemos la lógica del perfil de fondo por defecto (depende del corte de 2019)
# y los dos requisitos de semanas, uno por régimen
from datos_sistema import perfil_por_defecto, semanas_requeridas, semanas_gpm
# Y el análisis de huecos, que levanta sus propias alertas
import lagunas

# Palabras que delatan un empleador de régimen exceptuado (Ley 100 art. 279).
# Se buscan dentro del nombre del empleador, en mayúsculas.
SENALES_EXCEPTUADO = {
    "fuerzas_militares_policia": [
        "MINISTERIO DE DEFENSA", "POLICIA NACIONAL", "EJERCITO NACIONAL",
        "ARMADA NACIONAL", "FUERZA AEREA", "CREMIL", "CASUR",
    ],
    "magisterio": [
        "SECRETARIA DE EDUCACION", "FOMAG", "MAGISTERIO",
    ],
    "ecopetrol": [
        "ECOPETROL",
    ],
}

# Umbral de semanas del régimen de transición de la reforma suspendida
# (Ley 2381/2024): si revive, con estas semanas el usuario se queda en Ley 100.
TRANSICION_REFORMA = {"F": 750, "M": 900}


# ---------------------------------------------------------------------------
# Historia partida: qué régimen decide cuando hay semanas en los dos
# ---------------------------------------------------------------------------
# Regla de fondo (Ley 100 art. 13 lit. b, Secretaría del Senado): la afiliación
# al sistema es única y nadie puede estar en los dos regímenes al mismo tiempo.
# Entonces las semanas viejas del otro régimen NO se liquidan aparte: la
# pensión la reconoce el régimen donde la persona está afiliada HOY, y lo del
# régimen anterior viaja con ella (bono pensional si salió de Colpensiones,
# traslado del saldo si volvió a Colpensiones).
# Consecuencia práctica para el producto: el régimen NO se deduce de cuál
# documento trae más semanas. Se deduce de dónde está afiliada la persona hoy,
# y si el documento no lo dice, se pregunta.

# Valores de `afiliado.estado_afiliacion` (esquema-datos.md) que indican que
# esa es la administradora vigente y no una de la que ya se retiró.
ESTADOS_VIGENTES = ("activo_cotizante", "activo", "vigente", "afiliado_activo")


def _ultimo_mes_cotizado(caso):
    """Devuelve el último mes con cotización de una historia ('AAAA-MM').

    Sirve solo como hipótesis de cuál administradora es la actual cuando el
    documento no trae el estado de afiliación. NO es prueba: un documento puede
    estar desactualizado y por eso la hipótesis se marca como no confiable.
    """
    meses = []
    for p in caso.get("periodos") or []:
        # Solo cuentan los periodos con tiempo cotizado de verdad
        tiene_tiempo = (p.get("dias_cotizados") or 0) > 0 or \
                       (p.get("semanas_validas") or 0) > 0 or \
                       (p.get("semanas") or 0) > 0
        if tiene_tiempo and p.get("hasta"):
            meses.append(p["hasta"][:7])
    return max(meses) if meses else None


def regimen_vigente(historias, afiliacion_actual=None):
    """Decide qué régimen liquida la pensión cuando hay varias historias.

    `historias` es la lista de casos ya extraídos (uno por documento).
    `afiliacion_actual` es el dato que da el usuario cuando se le pregunta:
    'RPM', 'RAIS', o el nombre de la administradora donde está hoy.

    Devuelve un diccionario con el régimen elegido, de dónde salió esa
    decisión, si es confiable, qué preguntar si no lo es, y las alertas de lo
    que este módulo NO resuelve (el bono pensional, sobre todo).
    """
    alertas = []
    regimenes = [(h.get("documento") or {}).get("regimen") for h in historias]
    distintos = sorted({r for r in regimenes if r in ("RPM", "RAIS")})

    # --- Caso 1: el usuario ya dijo dónde está hoy. Manda ese dato ---
    if afiliacion_actual:
        texto = str(afiliacion_actual).strip().upper()
        if texto in ("RPM", "COLPENSIONES"):
            elegido, fuente = "RPM", "afiliación actual declarada por el usuario"
        elif texto in ("RAIS", "PORVENIR", "PROTECCION", "PROTECCIÓN",
                       "COLFONDOS", "SKANDIA"):
            elegido, fuente = "RAIS", "afiliación actual declarada por el usuario"
        else:
            elegido, fuente = None, f"no se reconoce la administradora '{afiliacion_actual}'"
        if elegido:
            return _resultado_regimen(elegido, fuente, True, None,
                                      alertas, distintos)

    # --- Caso 2: todos los documentos son del mismo régimen. No hay dilema ---
    if len(distintos) == 1:
        return _resultado_regimen(
            distintos[0], "todas las historias son del mismo régimen",
            True, None, alertas, distintos)

    if not distintos:
        return _resultado_regimen(
            None, "ningún documento declara régimen", False,
            "¿En qué entidad estás: Colpensiones, o un fondo privado "
            "(Porvenir, Protección, Colfondos, Skandia)?", alertas, distintos)

    # --- Caso 3: hay semanas en los dos regímenes ---
    # Primero, el dato duro: ¿algún documento se declara vigente?
    vigentes = [h for h in historias
                if ((h.get("afiliado") or {}).get("estado_afiliacion") or "")
                .lower() in ESTADOS_VIGENTES]
    regimenes_vigentes = {(h["documento"] or {}).get("regimen") for h in vigentes}
    if len(regimenes_vigentes) == 1:
        return _resultado_regimen(
            regimenes_vigentes.pop(),
            "es el régimen del documento que se declara afiliación vigente "
            "(estado_afiliacion)", True, None, alertas, distintos)

    # Sin dato duro: hipótesis por el último mes cotizado, declarada como tal
    ultimos = [(_ultimo_mes_cotizado(h), (h["documento"] or {}).get("regimen"))
               for h in historias]
    ultimos = [(m, r) for m, r in ultimos if m and r]
    hipotesis = max(ultimos)[1] if ultimos else None
    pregunta = ("Tienes semanas en Colpensiones y en un fondo privado. ¿En "
                "cuál de los dos estás afiliado hoy? De eso depende quién "
                "liquida tu pensión, no de en cuál tienes más semanas.")
    return _resultado_regimen(
        hipotesis,
        "hipótesis por el último mes cotizado; el documento no dice dónde "
        "está afiliado hoy", False, pregunta, alertas, distintos)


def _resultado_regimen(elegido, fuente, confiable, pregunta, alertas, distintos):
    """Arma la respuesta de `regimen_vigente` y le añade lo que queda abierto."""
    # Lo que este módulo NO resuelve y no se puede inventar. Se declara siempre
    # que la carrera esté partida entre los dos regímenes.
    if len(distintos) > 1:
        if elegido == "RAIS":
            alertas.append(
                "bono_pensional_no_valorado: las semanas de Colpensiones "
                "viajan como bono pensional tipo A, que NO aparece en la "
                "historia laboral y esta calculadora no lo valora. El saldo "
                "proyectado queda subestimado en el valor del bono "
                "(bonos-tiempos-publicos-y-exterior.md s.5)")
        elif elegido == "RPM":
            alertas.append(
                "traslado_de_saldo_no_valorado: al volver a Colpensiones el "
                "saldo del fondo privado se traslada y las semanas se "
                "reconocen, pero el efecto del traslado no se modela aquí "
                "(bonos-tiempos-publicos-y-exterior.md s.5)")
        alertas.append(
            "historia_partida: cada documento se verifica contra su propio "
            "total impreso y las semanas se consolidan sin doble conteo; "
            "la decisión de régimen es de la afiliación de hoy, no del "
            "documento con más semanas (Ley 100 art. 13 lit. b)")

    # Semanas en el exterior: la discrepancia CMISS sigue abierta con el
    # abogado y aquí no se inventa ninguna regla de convenio internacional.
    alertas.append(
        "semanas_exterior_no_resueltas: si alguna de las historias trae "
        "tiempos cotizados fuera de Colombia, NO se suman ni se convierten "
        "aquí. La discrepancia sobre el convenio CMISS está abierta "
        "(bonos-tiempos-publicos-y-exterior.md s.8 y s.9)")

    return {"regimen": elegido, "fuente": fuente, "confiable": confiable,
            "pregunta": pregunta, "alertas": alertas,
            "regimenes_en_documentos": distintos}


def clasificar(caso, sexo=None, edad=None):
    """Clasifica un caso extraído y devuelve el plan de trabajo del agente."""
    alertas = []

    # --- 1. Régimen y módulo ---
    regimen = caso["documento"].get("regimen")
    if regimen == "RPM":
        modulo = "rpm"
    elif regimen == "RAIS":
        modulo = "rais"
    else:
        # Sin régimen claro no se calcula nada: mejor preguntar que adivinar
        return {"modulo": None, "alertas": ["regimen_desconocido: preguntar "
                                            "al usuario en qué entidad está"]}

    # --- 2. Señales de régimen exceptuado en los empleadores ---
    for p in caso["periodos"]:
        empleador = (p.get("empleador") or "").upper()
        for tipo, palabras in SENALES_EXCEPTUADO.items():
            if any(palabra in empleador for palabra in palabras):
                alertas.append(f"posible_exceptuado:{tipo} (empleador: "
                               f"{p['empleador']}): la parte exceptuada no se "
                               f"calcula; ver regimenes-especiales.md")

    # --- 3. Datos faltantes que se vuelven preguntas al usuario ---
    afiliado = caso["afiliado"]
    if sexo is None and not afiliado.get("sexo"):
        alertas.append("falta_sexo: preguntar (nunca se infiere del nombre)")
    if edad is None and not afiliado.get("fecha_nacimiento") \
            and afiliado.get("edad_en_documento") is None:
        alertas.append("falta_edad: preguntar fecha de nacimiento")

    # --- 4. Observaciones del documento que merecen mención ---
    con_mora = sum(1 for p in caso["periodos"]
                   if p.get("observacion") in ("mora", "deuda_presunta"))
    if con_mora:
        alertas.append(f"mora_detectada: {con_mora} periodos en mora o deuda "
                       f"presunta (semanas recuperables, ver reglas-rpm.md s.8)")
    en_verificacion = sum(1 for p in caso["periodos"]
                          if p.get("observacion") == "en_verificacion")
    if en_verificacion:
        alertas.append(f"en_verificacion: {en_verificacion} periodos aún no "
                       f"confirmados por la administradora")

    # --- 4 bis. Huecos de la historia laboral ---
    # El documento no los marca: hay que calcularlos comparando lo cotizado
    # contra lo que cabía en cada tramo. La alerta no depende del tamaño del
    # hueco sino de si es material para esta persona (ver `alertas` en
    # lagunas.py): si cae en la ventana de proyección, o si pesa frente a lo
    # que le falta para su requisito. Por eso hay que pasarle el requisito.
    total_semanas = caso["resumen_documento"].get("total_semanas")
    sexo_para_requisito = sexo or afiliado.get("sexo")
    requisito = None
    if sexo_para_requisito:
        anio = date.today().year
        # El requisito no es el mismo en los dos regímenes: en Colpensiones son
        # las semanas de la pensión de vejez; en un fondo privado, las de la
        # garantía de pensión mínima, que es el único mínimo de semanas que
        # existe ahí. Se evalúa en el año en curso (aproximación declarada: la
        # cifra exacta depende del año de pensión y la calcula cada módulo).
        requisito = (semanas_requeridas(sexo_para_requisito, anio) if modulo == "rpm"
                     else semanas_gpm(sexo_para_requisito, anio))
    alertas.extend(lagunas.alertas(lagunas.analizar(caso),
                                   semanas_hoy=total_semanas,
                                   semanas_requeridas=requisito))

    # --- 5. ¿Aplica el comparador? (solo si la ventana de traslado está abierta) ---
    comparador = None
    sexo_efectivo = sexo or afiliado.get("sexo")
    if sexo_efectivo and (edad or afiliado.get("fecha_nacimiento")
                          or afiliado.get("edad_en_documento") is not None):
        # La edad exacta la calcula cada módulo; aquí solo decidimos si se ofrece
        comparador = "ofrecer_si_ventana_abierta"

    # --- 6. Nota de transición de la reforma (información valiosa, no cálculo) ---
    total = caso["resumen_documento"].get("total_semanas")
    if total is not None and sexo_efectivo in TRANSICION_REFORMA:
        umbral = TRANSICION_REFORMA[sexo_efectivo]
        if total >= umbral:
            alertas.append(f"transicion_reforma: con {total} semanas supera el "
                           f"umbral de {umbral}; si la reforma revive, quedaría "
                           f"en las reglas actuales (reforma-ley-2381.md)")

    # --- 7. Perfil de multifondos (solo RAIS): qué asumir como escenario base ---
    perfil_default = None
    if modulo == "rais":
        # Edad aproximada para la tabla de default (la exacta la calcula el módulo)
        edad_aprox = edad or afiliado.get("edad_en_documento")
        if edad_aprox is None and afiliado.get("fecha_nacimiento"):
            nac = date.fromisoformat(afiliado["fecha_nacimiento"])
            edad_aprox = (date.today() - nac).days // 365
        perfil, confiable, motivo = perfil_por_defecto(
            afiliado.get("fecha_afiliacion"), sexo_efectivo, edad_aprox)
        perfil_default = {"perfil": perfil, "confiable": confiable, "motivo": motivo}
        # Siempre se pregunta primero si cambió de perfil; el default solo se usa
        # como escenario base cuando es confiable
        if confiable:
            alertas.append(f"perfil_default: si nunca cambió de perfil, su "
                           f"escenario base es {perfil} ({motivo}). Confirmar "
                           f"con la pregunta de perfil (reglas-rais.md s.6)")
        else:
            alertas.append(f"perfil_incierto: {motivo}. NO asumir un perfil; "
                           f"preguntar o pedir el extracto (reglas-rais.md s.6)")

    return {"modulo": modulo, "alertas": alertas, "comparador": comparador,
            "perfil_default": perfil_default}
