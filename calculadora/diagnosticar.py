# Orquestador de Júbilo: la puerta de entrada única de la calculadora.
#
# Encadena todo el flujo de una sola vez, para que el agente NO tenga que
# llamar las piezas a mano ni decidir el orden:
#
#   verificación cruzada -> router -> rpm o rais -> comparador -> salida
#
# Regla dura 4 del kit: si la extracción no cuadra contra el total impreso del
# documento, aquí se detiene todo y NO se entrega diagnóstico. Esa es la
# salvaguarda que protege al usuario de un dato mal leído.
#
# Historia partida (varias administradoras): se pasan varios archivos. Cada uno
# se verifica contra SU propio total impreso y después se consolidan las semanas
# sin doble conteo. Ver `diagnosticar_historias`.
#
# Uso desde la terminal:
#   python3 diagnosticar.py ../casos/caso-03-proteccion-rais.json
#   python3 diagnosticar.py caso.json --sexo M --edad 26
#   python3 diagnosticar.py caso.json --json     (salida JSON, para máquina)
#   python3 diagnosticar.py colpensiones.json porvenir.json --afiliacion-actual Porvenir

import argparse                      # Para leer las opciones de la terminal
import json                          # Para leer y escribir JSON
import sys                           # Para terminar el programa con código de error
from collections import defaultdict  # Para agrupar días por mes
from datetime import date            # Para la fecha de cálculo

import router                        # Clasifica el caso y levanta alertas
import lagunas                       # Dónde están los huecos de la historia
import recuperacion                  # Qué pasa con el número si se recuperan
import rpm                           # Diagnóstico de Colpensiones
import rais                          # Diagnóstico de fondos privados
import comparador                    # Los dos regímenes lado a lado

# Diferencia máxima aceptada entre lo que calculamos y el total impreso.
# Es la misma tolerancia del verificador del set dorado: los fondos redondean
# distinto, pero una diferencia mayor a esto ya huele a error de lectura.
TOLERANCIA_SEMANAS = 0.15


# ---------------------------------------------------------------------------
# Paso 0: validación de estructura
# ---------------------------------------------------------------------------
# El JSON lo arma la IA leyendo el documento del usuario, así que puede venir
# mal formado. Esto lo detecta antes de calcular y dice QUÉ falta, en vez de
# reventar con un error críptico a mitad del proceso.

def validar_estructura(caso):
    """Revisa que el JSON tenga la forma del esquema (casos/esquema-datos.md).

    Devuelve la lista de problemas encontrados. Lista vacía = estructura sana.
    """
    problemas = []

    for bloque in ("documento", "afiliado", "resumen_documento", "periodos"):
        if bloque not in caso:
            problemas.append(f"falta el bloque '{bloque}'")

    if problemas:
        return problemas  # Sin los bloques base no tiene sentido seguir revisando

    regimen = caso["documento"].get("regimen")
    if regimen not in ("RPM", "RAIS"):
        problemas.append("documento.regimen debe ser 'RPM' o 'RAIS' "
                         f"(llegó: {regimen!r})")

    if not isinstance(caso["periodos"], list) or not caso["periodos"]:
        problemas.append("periodos debe ser una lista con al menos un periodo")
        return problemas

    # Cada periodo necesita fechas y alguna medida de tiempo cotizado
    for i, p in enumerate(caso["periodos"], start=1):
        if not p.get("desde") or not p.get("hasta"):
            problemas.append(f"periodo {i}: le faltan 'desde' o 'hasta'")
        tiene_tiempo = any(p.get(c) is not None for c in
                           ("dias_cotizados", "semanas", "semanas_validas"))
        if not tiene_tiempo:
            problemas.append(f"periodo {i}: no trae días ni semanas cotizadas")

    # El total impreso es el ancla de la verificación cruzada
    if caso["resumen_documento"].get("total_semanas") is None:
        problemas.append("resumen_documento.total_semanas está vacío: sin el total "
                         "impreso no hay contra qué verificar la lectura")

    # En RAIS el saldo es el insumo principal de la proyección
    if regimen == "RAIS" and caso["resumen_documento"].get(
            "saldo_cuenta_individual") is None:
        problemas.append("AVISO (no bloquea): el documento RAIS no trae saldo; "
                         "se estimará un piso desde los aportes y hay que decirlo")

    return problemas


# ---------------------------------------------------------------------------
# Paso 1: verificación cruzada (la salvaguarda que puede abortar todo)
# ---------------------------------------------------------------------------

def semanas_recalculadas(caso):
    """Recalcula las semanas desde los periodos, sin mirar el total impreso.

    Es la misma lógica del verificador del set dorado: si el documento trae
    semanas válidas (formato Colpensiones) se reconstruyen desde los días;
    si trae días por periodo (fondos privados) se suman topando cada mes en
    30 días, porque dos empleadores en el mismo mes no dan semanas dobles.
    """
    periodos = caso["periodos"]

    # Formato Colpensiones: las filas ya traen semanas válidas
    if any(p.get("semanas_validas") is not None for p in periodos):
        total_dias = sum(round((p.get("semanas_validas") or 0) * 7) for p in periodos)
        return total_dias / 7

    # Formato de fondos privados: días por mes, cada mes tope 30
    dias_por_mes = defaultdict(int)
    for p in periodos:
        mes = p["desde"][:7]  # "2021-09-01" -> "2021-09"
        dias_por_mes[mes] += p.get("dias_cotizados") or 0
    total_dias = sum(min(dias, 30) for dias in dias_por_mes.values())
    return total_dias / 7


def verificar(caso):
    """Compara lo extraído contra el total impreso del documento.

    Devuelve un diccionario con el resultado. 'cuadra' en False significa que
    el diagnóstico NO se puede entregar (regla dura 4).
    """
    total_documento = caso["resumen_documento"].get("total_semanas")
    calculado = round(semanas_recalculadas(caso), 2)

    # Sin total impreso no hay contra qué verificar: es el caso del screenshot
    # recortado. No se inventa un ancla: se pide el documento completo.
    if total_documento is None:
        return {
            "cuadra": False,
            "motivo": "sin_total_impreso",
            "calculado": calculado,
            "documento": None,
            "mensaje": ("El documento no trae el total de semanas impreso, así que "
                        "no hay contra qué verificar la lectura. Pedir el documento "
                        "completo antes de calcular nada."),
        }

    diferencia = round(abs(calculado - total_documento), 2)

    # Una discrepancia YA ESTUDIADA del propio documento (ej. caso-06, cuyo
    # total impreso no cuadra con su propia tabla) no es un error de lectura.
    nota = caso["resumen_documento"].get("nota_verificacion")
    if diferencia > TOLERANCIA_SEMANAS and nota:
        return {
            "cuadra": True,
            "motivo": "discrepancia_documental_conocida",
            "calculado": calculado,
            "documento": total_documento,
            "diferencia": diferencia,
            "mensaje": ("El documento se contradice a sí mismo, y ya está estudiado: "
                        f"{nota}"),
        }

    if diferencia > TOLERANCIA_SEMANAS:
        return {
            "cuadra": False,
            "motivo": "no_cuadra",
            "calculado": calculado,
            "documento": total_documento,
            "diferencia": diferencia,
            "mensaje": (f"La suma de los periodos da {calculado} semanas, pero el "
                        f"documento dice {total_documento} (diferencia de "
                        f"{diferencia}). Hay un error de lectura: NO se entrega "
                        f"diagnóstico."),
        }

    return {
        "cuadra": True,
        "motivo": "ok",
        "calculado": calculado,
        "documento": total_documento,
        "diferencia": diferencia,
        "mensaje": "La extracción cuadra contra el total impreso del documento.",
    }


# ---------------------------------------------------------------------------
# Paso 1 bis: historia partida (varios documentos de la misma persona)
# ---------------------------------------------------------------------------
# Por qué existe: en Colombia es frecuente haber pasado por Colpensiones y por
# un fondo privado, o por dos fondos. Cada administradora emite SU propia
# historia laboral, con SU propio total impreso, y ninguna trae la carrera
# completa. Hasta aquí el flujo asumía un documento y un total.
#
# Las dos reglas que gobiernan este bloque:
#   1. La regla dura 4 NO se relaja. Cada documento se verifica contra su
#      propio total impreso. Si uno solo no cuadra, no se entrega diagnóstico
#      y se dice cuál falló.
#   2. Las semanas se consolidan con la convención que ya existe (regla 3 de
#      casos/esquema-datos.md): los días de un mes se topan en 30, porque dos
#      aportes del mismo mes no dan semanas dobles. Aquí ese tope se aplica
#      además ENTRE documentos, que es donde nace el doble conteo.

DIAS_POR_MES = 30  # Convención del sistema, la misma de lagunas.py y rpm.py


def _repartir_dias_por_mes(periodo):
    """Reparte los días de una fila entre los meses que cubre.

    Usa exactamente la regla de `rpm.expandir_a_meses`: los días se reconstruyen
    desde las semanas exactas (x 7) cuando el documento trae semanas válidas, y
    se reparten desde el inicio del rango, máximo 30 por mes. No es una
    convención nueva: es la que ya usa toda la calculadora.

    Devuelve una lista de pares (mes 'AAAA-MM', días de ese mes).
    """
    if periodo.get("semanas_validas") is not None:
        dias_fila = round((periodo["semanas_validas"] or 0) * 7)
    elif periodo.get("dias_cotizados") is not None:
        dias_fila = periodo["dias_cotizados"] or 0
    else:
        # Algunos formatos solo traen semanas sueltas
        dias_fila = round((periodo.get("semanas") or 0) * 7)

    anio, mes = int(periodo["desde"][:4]), int(periodo["desde"][5:7])
    fin_anio, fin_mes = int(periodo["hasta"][:4]), int(periodo["hasta"][5:7])
    reparto, restantes = [], dias_fila
    while (anio, mes) <= (fin_anio, fin_mes):
        del_mes = min(DIAS_POR_MES, restantes)
        if del_mes > 0:
            reparto.append((f"{anio}-{mes:02d}", del_mes))
        restantes -= del_mes
        # Avanzamos un mes
        anio, mes = (anio + 1, 1) if mes == 12 else (anio, mes + 1)
    return reparto


def _clave_empleador(periodo, indice_documento):
    """Identifica al aportante de una fila, para no contarlo dos veces.

    Si dos documentos reportan el MISMO empleador en el MISMO mes, es el mismo
    trabajo visto por dos administradoras: se cuenta una sola vez. Si el
    documento no dice quién es el empleador no se puede saber, así que la fila
    se deja separada por documento y se levanta una alerta.
    """
    nit = (periodo.get("nit") or "").strip()
    empleador = (periodo.get("empleador") or "").strip().upper()
    if nit:
        return ("nit", nit)
    if empleador:
        return ("empleador", empleador)
    return ("sin_identificar", indice_documento)


def mapa_mensual(historias):
    """Cruza todas las historias en un solo mapa mes -> aportante -> días.

    Es el corazón de la consolidación. Para cada mes y cada aportante se toma
    el MÁXIMO de días reportado entre los documentos (no la suma: el mismo
    trabajo reportado dos veces sigue siendo un solo trabajo). Los aportantes
    distintos del mismo mes sí se suman, y el mes se topa en 30 días después.
    """
    mapa = {}       # 'AAAA-MM' -> clave_aportante -> registro
    conflictos = []  # discrepancias de salario entre documentos
    for i, historia in enumerate(historias):
        for p in historia.get("periodos") or []:
            if not p.get("desde") or not p.get("hasta"):
                continue
            clave = _clave_empleador(p, i)
            for mes, dias in _repartir_dias_por_mes(p):
                registro = mapa.setdefault(mes, {}).get(clave)
                nuevo = {
                    "dias": dias,
                    "ibc": p.get("ibc"),
                    "empleador": p.get("empleador"),
                    "nit": p.get("nit"),
                    "tipo_cotizante": p.get("tipo_cotizante"),
                    "administradora": p.get("administradora"),
                    "observacion": p.get("observacion") or "normal",
                    "documentos": {i},
                }
                if registro is None:
                    mapa[mes][clave] = nuevo
                    continue
                # Ya había una fila de este aportante en este mes: puede ser
                # otro pago del mismo documento (se suman los días) o el mismo
                # trabajo visto por otro documento (se toma el máximo)
                if i in registro["documentos"]:
                    registro["dias"] = min(DIAS_POR_MES, registro["dias"] + dias)
                else:
                    if registro.get("ibc") and p.get("ibc") \
                            and registro["ibc"] != p["ibc"]:
                        conflictos.append(
                            f"{mes} {p.get('empleador') or 'sin empleador'}: un "
                            f"documento reporta salario {pesos(registro['ibc'])} "
                            f"y el otro {pesos(p['ibc'])}; se usa el de la fila "
                            f"con más días")
                    if dias > registro["dias"]:
                        registro.update({k: nuevo[k] for k in
                                         ("dias", "ibc", "tipo_cotizante",
                                          "administradora", "observacion")})
                    registro["documentos"].add(i)
    return mapa, conflictos


def consolidar(historias, regimen=None):
    """Funde varias historias laborales en un solo caso, sin doble conteo.

    Devuelve (caso_consolidado, resumen). El resumen explica de dónde sale el
    total consolidado, que es lo que el agente le muestra al usuario: la suma
    ingenua de los totales impresos, cuánto se descontó por solapamiento y
    cuánto por la convención de 30 días por mes.
    """
    alertas = []
    mapa, conflictos = mapa_mensual(historias)
    alertas.extend(f"salario_discrepante: {c}" for c in conflictos)

    # --- Los periodos consolidados: una fila por mes y aportante ---
    periodos = []
    dias_consolidados = 0
    for mes in sorted(mapa):
        aportantes = mapa[mes]
        # El tope de 30 días del mes se reparte entre los aportantes, en orden
        # de días (regla 3 del esquema: las semanas del mes se cuentan una vez)
        disponible = DIAS_POR_MES
        for clave, r in sorted(aportantes.items(), key=lambda x: -x[1]["dias"]):
            dias_fila = min(r["dias"], disponible)
            disponible -= dias_fila
            dias_consolidados += dias_fila
            anio, num = int(mes[:4]), int(mes[5:7])
            ultimo = 31
            while True:
                try:
                    date(anio, num, ultimo)
                    break
                except ValueError:
                    ultimo -= 1
            periodos.append({
                "desde": f"{mes}-01",
                "hasta": f"{mes}-{ultimo:02d}",
                "empleador": r["empleador"],
                "nit": r["nit"],
                "tipo_cotizante": r["tipo_cotizante"],
                "ibc": r["ibc"],
                "ibc_tipo": "mensual",
                "cotizacion": None,
                "dias_cotizados": dias_fila,
                "semanas": None,
                "semanas_lic": None,
                "semanas_sim": None,
                # En el consolidado todo queda en formato mensual de días: es
                # el único formato que admite mezclar Colpensiones con fondos
                # privados sin que los dos conteos se pisen
                "semanas_validas": None,
                "administradora": r["administradora"],
                "observacion": r["observacion"],
                "documentos_origen": sorted(r["documentos"]),
            })

    # --- De dónde sale el número: la cuenta que el agente le muestra al usuario ---
    totales_impresos = [(h.get("resumen_documento") or {}).get("total_semanas")
                        for h in historias]
    suma_ingenua = round(sum(t for t in totales_impresos if t is not None), 2)
    consolidado = round(dias_consolidados / 7, 2)

    # Días que cada documento aporta por su cuenta, con su propia convención,
    # antes de cruzarlo con los demás. Separar los dos ajustes importa: uno es
    # traslape real entre documentos, el otro es la convención de 30 días/mes
    # que también aplicaría a un documento solo.
    dias_por_documento = []
    for h in historias:
        mapa_solo, _ = mapa_mensual([h])
        dias_por_documento.append(
            sum(min(DIAS_POR_MES, sum(r["dias"] for r in aport.values()))
                for aport in mapa_solo.values()))
    suma_sin_cruzar = round(sum(dias_por_documento) / 7, 2)

    resumen = {
        "documentos": len(historias),
        "suma_ingenua_semanas": suma_ingenua,
        "semanas_consolidadas": consolidado,
        "descuento_por_solapamiento": round(suma_sin_cruzar - consolidado, 2),
        "ajuste_por_convencion_mensual": round(suma_ingenua - suma_sin_cruzar, 2),
        "meses_compartidos": sorted(
            mes for mes, aport in mapa.items()
            if len({d for r in aport.values() for d in r["documentos"]}) > 1),
        "alertas": alertas,
        "explicacion": (
            "Sumar los totales impresos de los documentos da "
            f"{suma_ingenua} semanas, pero ese número cuenta dos veces los "
            "meses que aparecen en más de un documento. Consolidando mes a "
            f"mes, con el tope de 30 días por mes que ya usa el sistema, "
            f"quedan {consolidado} semanas."),
    }

    if resumen["meses_compartidos"]:
        alertas.append(
            f"meses_en_dos_documentos: {len(resumen['meses_compartidos'])} "
            f"meses aparecen en más de un documento; se contaron una sola vez")
    if any(_clave_empleador(p, i)[0] == "sin_identificar"
           for i, h in enumerate(historias) for p in h.get("periodos") or []):
        alertas.append(
            "filas_sin_empleador: hay periodos sin empleador ni NIT, así que "
            "no se puede saber si dos documentos reportan el mismo trabajo. "
            "Se aplicó el tope de 30 días por mes, que evita contar de más, "
            "pero conviene revisar esos meses")
    if any((h.get("resumen_documento") or {}).get("semanas_en_otros_fondos")
           is not None for h in historias):
        alertas.append(
            "documento_ya_suma_otros_fondos: al menos un documento reporta "
            "semanas de otras administradoras en su propio resumen. La "
            "consolidación se hace sobre los periodos, no sobre los totales "
            "impresos, así que ese total no se vuelve a sumar")

    # --- El afiliado: los datos personales deben coincidir entre documentos ---
    afiliado, problemas_afiliado = _consolidar_afiliado(historias)
    alertas.extend(problemas_afiliado)

    # --- El saldo RAIS: NUNCA se suman los saldos de dos documentos ---
    saldo, nota_saldo = _consolidar_saldo(historias, regimen)
    if nota_saldo:
        alertas.append(nota_saldo)

    caso = {
        "caso_id": "consolidado:" + "+".join(
            str(h.get("caso_id") or f"doc{i + 1}") for i, h in enumerate(historias)),
        "documento": {
            "administradora_emisora": "consolidado de "
                                      f"{len(historias)} documentos",
            "regimen": regimen,
            "formato": "consolidado_mensual",
            "fecha_generacion": max(
                [(h.get("documento") or {}).get("fecha_generacion") or ""
                 for h in historias]) or None,
        },
        "afiliado": afiliado,
        "resumen_documento": {
            # Este total NO es un total impreso: es el resultado de consolidar
            # documentos que YA fueron verificados uno por uno contra el suyo.
            # Por eso el flujo consolidado no vuelve a correr la regla dura 4:
            # no hay un documento nuevo que verificar, y fingir que lo hay
            # sería inventarse un ancla.
            "total_semanas": consolidado,
            "total_dias": dias_consolidados,
            "saldo_cuenta_individual": saldo,
            "semanas_en_otros_fondos": None,
            "origen": "consolidacion_de_varios_documentos",
        },
        "periodos": periodos,
    }
    resumen["alertas"] = alertas
    return caso, resumen


def _consolidar_afiliado(historias):
    """Funde los datos del afiliado y avisa si dos documentos se contradicen."""
    afiliado, alertas = {}, []
    campos = ("fecha_nacimiento", "edad_en_documento", "sexo",
              "fecha_afiliacion", "estado_afiliacion")
    for campo in campos:
        valores = {(h.get("afiliado") or {}).get(campo)
                   for h in historias
                   if (h.get("afiliado") or {}).get(campo) is not None}
        if len(valores) > 1 and campo in ("fecha_nacimiento", "sexo"):
            alertas.append(
                f"datos_personales_discrepantes: los documentos traen "
                f"{campo} distinto ({sorted(str(v) for v in valores)}). "
                f"Puede que no sean de la misma persona: hay que confirmarlo "
                f"antes de usar el consolidado")
        if campo == "fecha_afiliacion" and valores:
            # La afiliación al sistema es la más antigua de todas
            afiliado[campo] = min(valores)
        elif valores:
            afiliado[campo] = sorted(valores)[0]
        else:
            afiliado[campo] = None
    return afiliado, alertas


def _consolidar_saldo(historias, regimen):
    """Elige el saldo de la cuenta individual entre varios documentos RAIS.

    Los saldos NO se suman. Cuando alguien se traslada de fondo, el saldo se
    va con él: sumar el saldo del fondo viejo y el del nuevo contaría dos
    veces la misma plata. Se toma el del documento vigente, y si no se sabe
    cuál es, el del documento más reciente, diciéndolo.
    """
    con_saldo = [h for h in historias
                 if (h.get("resumen_documento") or {}).get(
                     "saldo_cuenta_individual") is not None]
    if not con_saldo:
        return None, None
    if len(con_saldo) == 1:
        return con_saldo[0]["resumen_documento"]["saldo_cuenta_individual"], None

    vigentes = [h for h in con_saldo
                if ((h.get("afiliado") or {}).get("estado_afiliacion") or "")
                .lower() in router.ESTADOS_VIGENTES]
    elegido = (vigentes or sorted(
        con_saldo,
        key=lambda h: (h.get("documento") or {}).get("fecha_generacion") or ""))[-1]
    return elegido["resumen_documento"]["saldo_cuenta_individual"], (
        "saldos_no_sumados: más de un documento trae saldo de cuenta "
        "individual. NO se suman, porque al trasladarse de fondo el saldo "
        "viaja con la persona y sumarlos contaría dos veces la misma plata. "
        f"Se usó el de {(elegido.get('documento') or {}).get('administradora_emisora') or elegido.get('caso_id')}; "
        "hay que confirmar con el usuario cuál es su cuenta vigente")


def diagnosticar_historias(historias, sexo=None, edad=None, fecha_calculo=None,
                           ibc_futuro=None, densidad_futura=None,
                           afiliacion_actual=None):
    """Diagnóstico con varias historias laborales de la misma persona.

    Es la puerta de entrada del caso de historia partida. El orden importa:
      1. Cada documento se verifica contra SU total impreso (regla dura 4).
      2. Solo si TODOS cuadran, se consolidan las semanas sin doble conteo.
      3. El régimen lo decide la afiliación de hoy, no el documento con más
         semanas. Si no se sabe cuál es, se pregunta y no se calcula.
      4. El caso consolidado corre por el flujo normal.
    """
    fecha_calculo = fecha_calculo or date.today()
    salida = {
        "caso_id": None,
        "fecha_calculo": fecha_calculo.isoformat(),
        "historias": [],
        "verificacion_por_documento": [],
        "consolidacion": None,
        "regimen_vigente": None,
        "preguntas_al_usuario": [],
        "listo_para_entregar": False,
    }

    if not historias:
        salida["consolidacion"] = {"error": "no se recibió ninguna historia laboral"}
        return salida
    if len(historias) == 1:
        # Un solo documento: es el flujo de siempre, sin consolidación
        return diagnosticar(historias[0], sexo=sexo, edad=edad,
                            fecha_calculo=fecha_calculo, ibc_futuro=ibc_futuro,
                            densidad_futura=densidad_futura)

    # --- Paso 1: cada documento contra su propio total impreso ---
    todos_cuadran = True
    for i, h in enumerate(historias, start=1):
        etiqueta = h.get("caso_id") or (h.get("documento") or {}).get(
            "administradora_emisora") or f"documento {i}"
        problemas = validar_estructura(h)
        bloqueantes = [p for p in problemas if not p.startswith("AVISO")]
        if bloqueantes:
            todos_cuadran = False
            salida["verificacion_por_documento"].append({
                "documento": etiqueta, "cuadra": False,
                "motivo": "estructura_invalida", "problemas": problemas,
                "mensaje": f"El documento {etiqueta} no cumple el esquema, así "
                           f"que no se puede verificar ni consolidar."})
            continue
        v = verificar(h)
        v["documento"] = etiqueta
        v["total_impreso"] = (h.get("resumen_documento") or {}).get("total_semanas")
        salida["verificacion_por_documento"].append(v)
        if not v["cuadra"]:
            todos_cuadran = False

    salida["caso_id"] = "+".join(
        str(h.get("caso_id") or f"doc{i + 1}") for i, h in enumerate(historias))

    # La regla dura 4 no se relaja porque haya varios documentos: si UNO solo
    # no cuadra, no se entrega diagnóstico. Se dice cuál, para que el usuario
    # sepa qué documento hay que volver a leer, y no se descarta el resto.
    if not todos_cuadran:
        fallaron = [v["documento"] for v in salida["verificacion_por_documento"]
                    if not v["cuadra"]]
        salida["consolidacion"] = {
            "error": "verificacion_fallida",
            "documentos_que_fallaron": fallaron,
            "mensaje": (
                "No se consolidan las semanas ni se entrega diagnóstico: "
                f"{', '.join(fallaron)} no cuadra contra su propio total "
                "impreso. Los demás documentos sí cuadraron, pero un "
                "consolidado con una parte mal leída da un número falso.")}
        return salida

    # --- Paso 2: qué régimen liquida ---
    plan_regimen = router.regimen_vigente(historias,
                                          afiliacion_actual=afiliacion_actual)
    salida["regimen_vigente"] = plan_regimen

    # --- Paso 3: consolidación de semanas sin doble conteo ---
    caso, resumen = consolidar(historias, regimen=plan_regimen["regimen"])
    salida["consolidacion"] = resumen
    salida["historias"] = [h.get("caso_id") for h in historias]

    if not plan_regimen["regimen"] or not plan_regimen["confiable"]:
        # Sin saber dónde está afiliado hoy no se calcula: el régimen cambia
        # todo el diagnóstico, y adivinarlo sería inventar el resultado
        if plan_regimen.get("pregunta"):
            salida["preguntas_al_usuario"].append(plan_regimen["pregunta"])
        salida["consolidacion"]["nota"] = (
            "Las semanas ya están consolidadas y son utilizables, pero el "
            "diagnóstico no corre hasta saber en qué régimen está hoy.")
        return salida

    # --- Paso 4: el caso consolidado corre por el flujo normal ---
    verificacion_previa = {
        "cuadra": True,
        "motivo": "consolidado_de_documentos_verificados",
        "calculado": resumen["semanas_consolidadas"],
        "documento": resumen["semanas_consolidadas"],
        "diferencia": 0.0,
        "mensaje": (f"Los {resumen['documentos']} documentos se verificaron uno "
                    f"por uno contra su propio total impreso y todos cuadraron. "
                    f"{resumen['explicacion']}"),
    }
    detalle = diagnosticar(caso, sexo=sexo, edad=edad, fecha_calculo=fecha_calculo,
                           ibc_futuro=ibc_futuro, densidad_futura=densidad_futura,
                           verificacion_previa=verificacion_previa)
    # El diagnóstico del consolidado se entrega junto con la trazabilidad de
    # de dónde salió cada semana
    detalle["historias"] = salida["historias"]
    detalle["verificacion_por_documento"] = salida["verificacion_por_documento"]
    detalle["consolidacion"] = salida["consolidacion"]
    detalle["regimen_vigente"] = plan_regimen
    detalle["preguntas_al_usuario"] = (salida["preguntas_al_usuario"]
                                       + detalle.get("preguntas_al_usuario", []))
    return detalle


# ---------------------------------------------------------------------------
# Paso 3 bis: la banda del factor de conversión, lista para mostrar
# ---------------------------------------------------------------------------
# Por qué existe este bloque: `rais.py` calcula los dos extremos de todo lo que
# depende del factor, pero el usuario solo ve lo que esta capa imprime. Sin
# esto, la banda existía en el diccionario y el usuario seguía viendo un número
# único, que además era el BORDE OPTIMISTA. Es el peor de los dos errores
# posibles: comunicar el mejor caso como si fuera la estimación.
#
# Regla de diseño que se respeta aquí (rais.REGLA_BANDA_Y_PERFILES): los dos
# rangos NO se multiplican. El perfil de fondo manda las filas (es una decisión
# del usuario) y la banda manda las columnas (es incertidumbre del modelo).

# Nombres legibles de las tres salidas posibles del RAIS, para que el veredicto
# se pueda decir en español y no en jerga de código.
NOMBRE_SALIDA = {
    "pension_por_capital": "pensión financiada con su propio capital",
    "garantia_pension_minima": "garantía de pensión mínima (un salario mínimo)",
    "devolucion_de_saldos": "devolución de saldos (no alcanza a pensionarse)",
}


def resumen_banda(diagnostico):
    """Traduce la banda del diagnóstico RAIS a algo que se pueda mostrar.

    Devuelve None cuando no aplica (RPM es determinista y va en tabla de
    escenarios, no en banda: excepción 1 bis del system-prompt).

    Lo que resuelve, y que no es cosmético:
      - La cifra que se muestra es el RANGO, nunca el borde superior.
      - Cuando los dos extremos caen en SALIDAS distintas del RAIS, la banda no
        cambia una cifra: cambia el veredicto. Eso se dice aparte y primero.
      - Cuando los dos extremos coinciden porque la garantía de pensión mínima
        los iguala, no se muestra un rango de ancho cero como si fuera
        incertidumbre: se dice que el piso legal absorbe la diferencia.
    """
    if not diagnostico or diagnostico.get("error"):
        return None
    declaracion = diagnostico.get("banda_factor")
    if not declaracion:
        return None  # No es un diagnóstico RAIS

    perfiles = {}
    veredictos_en_disputa = []
    for nombre, e in (diagnostico.get("escenarios") or {}).items():
        if "mesada_banda" not in e:
            continue
        bajo, alto = e["mesada_banda"]
        salida_baja = e.get("salida_conservadora")
        salida_alta = e.get("salida")
        fila = {
            "banda": (bajo, alto),
            "salida_conservadora": salida_baja,
            "salida_optimista": salida_alta,
            "ancho_cero": bajo == alto,
            "veredicto_cambia": salida_baja != salida_alta,
        }
        if fila["ancho_cero"]:
            # Caso del piso legal: los dos extremos dan lo mismo porque la
            # garantía de pensión mínima los levanta a un salario mínimo. No es
            # que el modelo sea preciso aquí: es que el piso absorbe la
            # diferencia. Mostrarlo como banda de ancho cero confundiría.
            fila["por_que_coinciden"] = (
                "los dos extremos dan la misma cifra porque la garantía de "
                "pensión mínima es un piso legal de un salario mínimo y "
                "absorbe la diferencia entre los dos precios de la renta. No "
                "hay incertidumbre que mostrar en el monto"
                if salida_baja == "garantia_pension_minima" else
                "los dos extremos coinciden en este escenario")
        if fila["veredicto_cambia"]:
            fila["cambio_de_veredicto"] = (
                f"con el precio de la norma la salida sería "
                f"{NOMBRE_SALIDA.get(salida_alta, salida_alta)}, y con el "
                f"precio de mercado sería "
                f"{NOMBRE_SALIDA.get(salida_baja, salida_baja)}. La banda no "
                f"cambia solo el monto: cambia qué le pasa al pensionarse")
            veredictos_en_disputa.append(nombre)
        perfiles[nombre] = fila

    # Pensión anticipada y umbral del 110%: hoy solo existen en perfil moderado,
    # así que el rango que se muestra es SOLO el del factor, y se dice.
    temprana, tardia = diagnostico.get("edad_pension_anticipada_banda") or (None, None)
    anticipada = {
        "banda": (temprana, tardia),
        "solo_perfil_moderado": True,
        "nota": ("el rango de edad viene solo del precio de la renta vitalicia, "
                 "no de los perfiles de fondo: esta cifra hoy se calcula únicamente "
                 "en perfil moderado"),
    }
    if temprana is not None and tardia is None:
        anticipada["advertencia"] = (
            "con el precio de mercado NO alcanza el umbral del 110% del salario "
            "mínimo antes de la edad legal: la pensión anticipada existe en un "
            "extremo de la banda y desaparece en el otro")
    elif temprana is None and tardia is None:
        anticipada = None

    return {
        "aplica_a": "mesada, edad de pensión anticipada y umbral del 110%",
        "perfiles": perfiles,
        "hay_cambio_de_veredicto": bool(veredictos_en_disputa),
        "escenarios_con_veredicto_en_disputa": veredictos_en_disputa,
        "pension_anticipada": anticipada,
        "capital_umbral_110_pct": diagnostico.get("capital_umbral_110_pct"),
        "declaracion": declaracion,
        "regla_de_lectura": declaracion.get(
            "como_se_combina_con_los_perfiles_de_fondo"),
    }


# ---------------------------------------------------------------------------
# Paso 2: el flujo completo
# ---------------------------------------------------------------------------

def diagnosticar(caso, sexo=None, edad=None, fecha_calculo=None,
                 ibc_futuro=None, densidad_futura=None,
                 verificacion_previa=None):
    """Corre el flujo entero y devuelve todo lo que el agente necesita.

    Nunca lanza una excepción por datos faltantes: devuelve el problema
    descrito, porque un dato que falta es una pregunta al usuario, no un error.

    ibc_futuro y densidad_futura cambian los supuestos del escenario "sigue
    cotizando" (salario en pesos de hoy y ritmo de cotización). Sirven para
    responder "¿y si cotizo sobre más?" con la calculadora, no a ojo.

    verificacion_previa es el ÚNICO camino por el que un caso puede saltarse el
    paso 1, y existe solo para el consolidado de varios documentos: ahí la
    regla dura 4 ya se cumplió documento por documento (ver
    `diagnosticar_historias`). Un caso que viene de un documento nunca lo usa.
    """
    fecha_calculo = fecha_calculo or date.today()
    salida = {
        "caso_id": caso.get("caso_id"),
        "fecha_calculo": fecha_calculo.isoformat(),
        "estructura": None,
        "verificacion": None,
        "router": None,
        "lagunas": None,
        "recuperacion": None,
        "diagnostico": None,
        # La banda del factor de conversión, ya lista para mostrar. Va como
        # llave propia para que ningún consumidor de esta salida pueda entregar
        # la cifra sin el rango y sin su declaración de fuentes.
        "banda": None,
        "comparacion": None,
        "preguntas_al_usuario": [],
        "listo_para_entregar": False,
    }

    # --- Paso 0: ¿el JSON está bien armado? ---
    problemas = validar_estructura(caso)
    # Los avisos no bloquean; los demás problemas sí
    bloqueantes = [p for p in problemas if not p.startswith("AVISO")]
    salida["estructura"] = {"ok": not bloqueantes, "problemas": problemas}
    if bloqueantes:
        salida["verificacion"] = {
            "cuadra": False,
            "motivo": "estructura_invalida",
            "mensaje": ("El JSON extraído no cumple el esquema, así que no se "
                        "calcula nada. Corregir la extracción y volver a correr."),
        }
        return salida

    # --- Paso 1: verificación cruzada. Si no cuadra, aquí se acaba todo ---
    # El consolidado de varias historias llega con su verificación ya hecha,
    # documento por documento, y no se vuelve a verificar contra un total
    # impreso que no existe (ver `consolidar`).
    salida["verificacion"] = verificacion_previa or verificar(caso)
    if not salida["verificacion"]["cuadra"]:
        return salida

    # --- Paso 2: el router decide qué módulo corre y qué falta preguntar ---
    plan = router.clasificar(caso, sexo=sexo, edad=edad)
    salida["router"] = plan

    # --- Paso 2 bis: dónde están los huecos ---
    # Va aquí, después de la verificación y antes del régimen, porque es
    # independiente del régimen: los huecos son del documento, no del cálculo.
    # Es la única fuente autorizada para responder "¿dónde están mis huecos?":
    # comparar rangos a mano rompe la regla dura 1 del kit.
    analisis_lagunas = lagunas.analizar(caso)
    salida["lagunas"] = {"resumen": lagunas.resumir(analisis_lagunas),
                         "detalle": analisis_lagunas}

    if not plan.get("modulo"):
        # Sin régimen claro no se calcula: se le pregunta al usuario
        salida["preguntas_al_usuario"].append(
            "¿En qué entidad estás: Colpensiones, o un fondo privado (Porvenir, "
            "Protección, Colfondos, Skandia)?")
        return salida

    # Las alertas de datos faltantes se traducen a preguntas en lenguaje humano
    for alerta in plan.get("alertas", []):
        if alerta.startswith("falta_sexo"):
            salida["preguntas_al_usuario"].append(
                "¿Eres hombre o mujer? (si el nombre del documento es inequívoco, "
                "se asume y se declara el supuesto; ver system-prompt.md)")
        if alerta.startswith("falta_edad"):
            salida["preguntas_al_usuario"].append("¿Cuál es tu fecha de nacimiento?")

    # --- Paso 3: el módulo del régimen que corresponde ---
    # Los dos módulos reciben datos distintos: rpm saca la edad de la fecha de
    # nacimiento (la exige), mientras rais acepta la edad suelta porque varios
    # documentos privados solo traen la edad.
    sexo_efectivo = sexo or caso["afiliado"].get("sexo")
    if plan["modulo"] == "rpm":
        if not caso["afiliado"].get("fecha_nacimiento"):
            salida["diagnostico"] = {
                "error": "El módulo de Colpensiones necesita la fecha de "
                         "nacimiento exacta, no basta la edad."}
            salida["preguntas_al_usuario"].append("¿Cuál es tu fecha de nacimiento?")
            return salida
        if not sexo_efectivo:
            salida["diagnostico"] = {"error": "Falta el sexo para calcular."}
            return salida
        resultado = rpm.diagnosticar(caso, sexo_efectivo, fecha_calculo=fecha_calculo,
                                     ibc_futuro=ibc_futuro,
                                     densidad_futura=densidad_futura)
    else:
        resultado = rais.diagnosticar(caso, sexo=sexo, edad=edad,
                                      fecha_calculo=fecha_calculo,
                                      ibc_futuro=ibc_futuro,
                                      densidad_futura=densidad_futura)
    salida["diagnostico"] = resultado

    # El módulo avisa si le faltan datos: eso es pregunta, no falla
    if isinstance(resultado, dict) and resultado.get("error"):
        return salida

    # La banda del factor, traducida a algo mostrable. En RPM devuelve None,
    # porque ahí la fórmula es determinista y va en tabla de escenarios.
    salida["banda"] = resumen_banda(resultado)

    # --- Paso 3 bis: qué pasaría si esas semanas se recuperan ---
    # Va después del diagnóstico porque necesita el número base contra el cual
    # comparar. Solo corre si hay algo que recuperar: si el historial está sano
    # no se le muestra al agente un bloque vacío que lo tiente a llenarlo.
    if sexo_efectivo:
        try:
            salida["recuperacion"] = recuperacion.simular(
                caso, sexo_efectivo, edad=edad, fecha_calculo=fecha_calculo)
        except Exception as e:
            # Igual que el comparador: es un extra, y si falla el diagnóstico
            # principal sigue siendo válido
            salida["recuperacion"] = {"error": f"no se pudo simular: {e}"}

    # --- Paso 4: el comparador (los dos regímenes lado a lado) ---
    # El sexo real puede venir del documento y no del argumento
    sexo_real = sexo or caso["afiliado"].get("sexo")
    if sexo_real:
        try:
            salida["comparacion"] = comparador.comparar(
                caso, sexo_real, edad=edad, fecha_calculo=fecha_calculo,
                ibc_futuro=ibc_futuro, densidad_futura=densidad_futura)
        except Exception as e:
            # El comparador es un extra: si falla, el diagnóstico principal
            # sigue siendo válido y se reporta el problema sin tumbar todo
            salida["comparacion"] = {"error": f"no se pudo comparar: {e}"}

    salida["listo_para_entregar"] = True
    return salida


# ---------------------------------------------------------------------------
# Presentación en terminal (para que el humano lea rápido lo que salió)
# ---------------------------------------------------------------------------

def pesos(valor):
    """Formatea un número como pesos colombianos: 1750905 -> $1.750.905"""
    if valor is None:
        return "sin dato"
    return "$" + f"{round(valor):,}".replace(",", ".")


def rango(par):
    """Formatea una banda de pesos: (1750905, 2666551) -> '$1.750.905 a $2.666.551'"""
    bajo, alto = par
    if bajo == alto:
        return pesos(bajo)
    return f"{pesos(bajo)} a {pesos(alto)}"


def imprimir_banda(banda):
    """Imprime la mesada como RANGO y la declaración de dónde sale cada extremo.

    El orden no es estético: primero lo que cambia el veredicto, después las
    cifras, y al final de dónde salen. Un rango sin su declaración es una cifra
    inventada con dos decimales de más.
    """
    if not banda:
        return

    # 1. Lo primero, si existe: la banda no cambia una cifra, cambia el final
    if banda["hay_cambio_de_veredicto"]:
        print("    OJO, LA BANDA CAMBIA EL VEREDICTO, no solo el monto:")
        for perfil in banda["escenarios_con_veredicto_en_disputa"]:
            print(f"      {perfil}: {banda['perfiles'][perfil]['cambio_de_veredicto']}")

    # 2. Las cifras, siempre como rango
    print("    MESADA ESTIMADA (rango, no cifra única). Precio de mercado "
          "primero, precio de la norma después:")
    ya_explicado = False  # El motivo del ancho cero se dice una vez, no por fila
    for perfil in ("conservador", "moderado", "mayor_riesgo", "deja_de_cotizar"):
        fila = banda["perfiles"].get(perfil)
        if not fila:
            continue
        etiqueta = "si deja hoy" if perfil == "deja_de_cotizar" else perfil
        linea = f"    {etiqueta:<13} {rango(fila['banda']):>34}"
        if fila["veredicto_cambia"]:
            linea += (f"  -> {fila['salida_conservadora']} O BIEN "
                      f"{fila['salida_optimista']}, según el extremo")
        else:
            linea += f"  -> {fila['salida_optimista']}"
        print(linea)
        if fila["ancho_cero"] and not ya_explicado:
            print(f"                  {fila['por_que_coinciden']}")
            ya_explicado = True

    # 3. Lo que también depende del factor (decisión 2 de Santiago)
    ant = banda.get("pension_anticipada")
    if ant:
        temprana, tardia = ant["banda"]
        if tardia is None:
            print(f"    PENSIÓN ANTICIPADA: desde los {temprana} años con el "
                  f"precio de la norma (Ley 100 art. 64)")
            print(f"                  {ant['advertencia']}")
        elif temprana == tardia:
            print(f"    PENSIÓN ANTICIPADA: desde los {temprana} años en los "
                  f"dos extremos (Ley 100 art. 64)")
        else:
            print(f"    PENSIÓN ANTICIPADA: entre los {temprana} y los {tardia} "
                  f"años según el precio de la renta (Ley 100 art. 64)")
        print(f"                  {ant['nota']}")
    umbral = banda.get("capital_umbral_110_pct")
    if umbral:
        print(f"    CAPITAL QUE EXIGE EL UMBRAL DEL 110%: "
              f"{rango((umbral['optimista'], umbral['conservador']))}")

    # 4. De dónde sale cada extremo. Va pegado a las cifras a propósito: si se
    # separa, el agente termina mostrando un rango sin poder explicarlo.
    dec = banda["declaracion"]
    print("    DE DÓNDE SALE CADA EXTREMO:")
    for nombre in ("optimista", "conservador"):
        e = dec["extremos"][nombre]
        print(f"      {nombre}: factor {e['factor']} "
              f"(tasa {round(100 * e['tasa_real_anual'], 2)}% real anual), "
              f"{e['de_donde_sale']}")
        print(f"        fuente: {e['fuente']} | confianza: {e['confianza']}")
        if e.get("advertencia"):
            print(f"        OJO: {e['advertencia']}")
    print(f"      por qué difieren: {dec['por_que_difieren']}")
    print(f"      referencia del conservador: "
          f"{dec['referencia_del_extremo_conservador']}")
    print(f"      Decreto 1485 de 2025: {dec['decreto_1485_de_2025']}")
    print(f"      cómo se lee con los perfiles: {banda['regla_de_lectura']}")


def imprimir(s):
    """Imprime el resultado en texto legible. NO es el mensaje al usuario:
    el agente redacta con la plantilla del system-prompt, no copiando esto."""
    print("=" * 70)
    print(f"CASO: {s['caso_id']}   (calculado el {s['fecha_calculo']})")
    print("=" * 70)

    # 0 bis. Historia partida: la verificación documento por documento y la
    # consolidación van ANTES de todo, porque de ahí sale el número base
    if s.get("verificacion_por_documento"):
        print("\n[0b] HISTORIA PARTIDA: verificación documento por documento")
        for v in s["verificacion_por_documento"]:
            marca = "OK" if v["cuadra"] else "NO CUADRA"
            print(f"    {str(v.get('documento')):<32} {marca:<10} "
                  f"impreso: {v.get('total_impreso')} | "
                  f"recalculado: {v.get('calculado')}")
        cons = s.get("consolidacion") or {}
        if cons.get("error"):
            print(f"\n    {cons['mensaje']}")
            print("\n>>> NO SE ENTREGA DIAGNÓSTICO. Regla dura 4 del kit.\n")
            return
        print(f"\n    suma ingenua de los totales impresos: "
              f"{cons.get('suma_ingenua_semanas')} semanas")
        print(f"    menos solapamiento entre documentos:  "
              f"{cons.get('descuento_por_solapamiento')} semanas")
        print(f"    menos convención de 30 días por mes:  "
              f"{cons.get('ajuste_por_convencion_mensual')} semanas")
        print(f"    TOTAL CONSOLIDADO:                    "
              f"{cons.get('semanas_consolidadas')} semanas")
        if cons.get("meses_compartidos"):
            print(f"    meses en más de un documento: "
                  f"{', '.join(cons['meses_compartidos'])}")
        for a in cons.get("alertas", []):
            print(f"    alerta: {a}")
        rv = s.get("regimen_vigente") or {}
        if rv:
            print(f"\n    régimen que liquida: {rv.get('regimen')} "
                  f"({'confiable' if rv.get('confiable') else 'HIPÓTESIS, hay que preguntar'})")
            print(f"    de dónde sale: {rv.get('fuente')}")
            for a in rv.get("alertas", []):
                print(f"    alerta: {a}")
        if not (s.get("router") or {}).get("modulo"):
            if s.get("preguntas_al_usuario"):
                print("\n    PREGUNTAR ANTES DE CALCULAR:")
                for p in s["preguntas_al_usuario"]:
                    print(f"      - {p}")
            print("\nLISTO PARA ENTREGAR: NO (faltan datos)\n")
            return

    # 0. Estructura del JSON extraído
    est = s.get("estructura") or {}
    if est.get("problemas"):
        print(f"\n[0] ESTRUCTURA DEL JSON: {'OK con avisos' if est['ok'] else 'INVÁLIDA'}")
        for p in est["problemas"]:
            print(f"    {p}")
        if not est["ok"]:
            print("\n>>> NO SE CALCULA NADA. Corregir la extracción.\n")
            return

    # 1. Verificación
    v = s["verificacion"]
    marca = "OK" if v["cuadra"] else "DETENIDO"
    print(f"\n[1] VERIFICACIÓN CRUZADA: {marca}")
    print(f"    {v['mensaje']}")
    if v.get("documento") is not None:
        print(f"    documento: {v['documento']} semanas | "
              f"recalculado: {v['calculado']} semanas")
    if not v["cuadra"]:
        print("\n>>> NO SE ENTREGA DIAGNÓSTICO. Regla dura 4 del kit.\n")
        return

    # 2. Router
    plan = s["router"]
    print(f"\n[2] ROUTER: módulo '{plan.get('modulo')}'")
    for alerta in plan.get("alertas", []):
        print(f"    alerta: {alerta}")

    # 3. Huecos de la historia laboral
    lag = s.get("lagunas") or {}
    det, res = lag.get("detalle") or {}, lag.get("resumen") or {}
    if det and not det.get("error"):
        print(f"\n[3] HUECOS DE LA HISTORIA LABORAL "
              f"({res['semanas_perdidas_total']} semanas sin cotizar en total)")
        for v in det["vacios"]:
            print(f"    vacío   {v['desde']} a {v['hasta']}: {v['meses']} meses "
                  f"sin ninguna cotización ({v['semanas_no_cotizadas']} semanas)")
        for t in det["tramos_con_deficit"]:
            print(f"    tramo   {t['desde']} a {t['hasta']} ({t['empleador']}): "
                  f"{t['semanas_reportadas']} de {t['semanas_posibles']} semanas "
                  f"posibles, faltan ~{t['deficit_meses_aprox']} meses")
        for f in det["filas_ibc_sin_semanas"]:
            print(f"    ojo     {f['desde']} ({f['empleador']}): salario "
                  f"{pesos(f['ibc'])} reportado y 0 semanas acreditadas, sin "
                  f"marca de simultaneidad")
        if det["tramos_con_deficit"]:
            print("    NOTA: el documento agrupa por tramos. Se sabe CUÁNTOS "
                  "meses faltan, no CUÁLES: el mes exacto está en PILA.")

        # Qué pasaría si se recuperan: solo se imprime si hay algo que decir
        rec = s.get("recuperacion") or {}
        inv = rec.get("inventario") or {}
        if inv and not rec.get("error"):
            print(f"    recuperable con número: {inv['semanas_acreditables']} "
                  f"semanas | sin salario reportado (no estimable): "
                  f"{inv['sin_salario_reportado']['semanas']} semanas")
            for nombre, e in (rec.get("escenarios") or {}).items():
                if e.get("error"):
                    continue
                delta = f"{e['delta_mesada']:+}" if "delta_mesada" in e else "sin dato"
                print(f"    -> {nombre}: {e['delta_semanas']:+} semanas, "
                      f"mesada {delta} ({e.get('delta_mesada_pct', 0):+}%)")
                # En RAIS la palanca se mide en los dos extremos de la banda:
                # mostrar solo el optimista la exageraría
                if "delta_mesada_conservadora" in e:
                    print(f"       con el precio de mercado: "
                          f"{e['delta_mesada_conservadora']:+} "
                          f"({e.get('delta_mesada_conservadora_pct', 0):+}%)")
                if e.get("veredicto_depende_del_extremo"):
                    print(f"       OJO: {e['veredicto_depende_del_extremo']}")
                if e.get("salidas_distintas_en_la_banda"):
                    print(f"       OJO: {e['salidas_distintas_en_la_banda']}")
                if e.get("advertencia"):
                    print(f"       OJO: {e['advertencia']}")

    # 4. Diagnóstico del régimen
    d = s["diagnostico"]
    if d and d.get("error"):
        print(f"\n[4] DIAGNÓSTICO: incompleto ({d['error']})")
    elif d:
        print(f"\n[4] DIAGNÓSTICO ({plan.get('modulo').upper()})")
        print(f"    edad {d.get('edad')} | sexo {d.get('sexo')} | "
              f"semanas hoy: {d.get('semanas_hoy')}")
        if plan.get("modulo") == "rais":
            print(f"    saldo hoy: {pesos(d.get('saldo_hoy'))}"
                  f"{' (ESTIMADO)' if d.get('saldo_es_estimado') else ''}")
            print(f"    semanas exigidas para la garantía de pensión mínima: "
                  f"{d.get('semanas_gpm')}")
            imprimir_banda(s.get("banda"))
        else:
            # RPM: la mesada vive dentro del escenario, y las fechas importan
            # tanto como el monto (el "cuándo" del producto)
            print(f"    semanas exigidas hoy: {d.get('requisito_semanas_hoy')} | "
                  f"densidad: {d.get('densidad_ultimos_3_anios')}")
            print(f"    cumple edad: {d.get('fecha_cumple_edad')} | "
                  f"cumple semanas: {d.get('fecha_cumple_semanas')}")
            print(f"    fecha estimada de pensión: {d.get('fecha_pension_estimada')}")
            sigue = d.get("escenario_sigue_cotizando") or {}
            if sigue.get("mesada"):
                print(f"    si sigue cotizando: mesada {pesos(sigue['mesada'])} "
                      f"(tasa de reemplazo {sigue.get('tasa_pct')}%)")
            deja = d.get("escenario_deja_de_cotizar") or {}
            if deja:
                print(f"    si deja de cotizar hoy: {deja.get('resultado', 'sin dato')}")

    # 5. Comparación
    c = s.get("comparacion")
    if c and not c.get("error"):
        print("\n[5] COMPARACIÓN DE REGÍMENES: disponible en la salida JSON")
        # El veredicto sí se imprime: es lo que decide si se habla de traslado,
        # y hay que verlo evaluado en los dos extremos de la banda
        m = c.get("mesadas") or {}
        if m.get("mesada_rais_banda"):
            print(f"    Colpensiones {pesos(m['mesada_rpm'])} (punto) contra "
                  f"fondo privado {rango(m['mesada_rais_banda'])} (banda, perfil "
                  f"{m['perfil_comparado']})")
            print(f"    veredicto: {m['veredicto']}")
            print(f"    {m['mensaje']}")
    elif c:
        print(f"\n[5] COMPARACIÓN: {c['error']}")

    # 6. Lo que hay que preguntarle al usuario
    if s["preguntas_al_usuario"]:
        print("\n[6] PREGUNTAR AL USUARIO ANTES DE ENTREGAR:")
        for p in s["preguntas_al_usuario"]:
            print(f"    - {p}")

    estado = "SÍ" if s["listo_para_entregar"] else "NO (faltan datos)"
    print(f"\nLISTO PARA ENTREGAR: {estado}")
    print("Recordatorio: los números salen de aquí; la redacción sale de la "
          "plantilla del system-prompt.\n")


def main():
    p = argparse.ArgumentParser(
        description="Diagnóstico pensional completo de un caso de Júbilo.")
    p.add_argument("caso", nargs="+",
                   help="Ruta al JSON del caso extraído. Se pueden pasar varios "
                        "cuando la persona tiene la historia partida entre dos "
                        "administradoras: cada uno se verifica por separado")
    p.add_argument("--sexo", choices=["M", "F"],
                   help="M u F, cuando el documento no lo trae")
    p.add_argument("--edad", type=int, help="Edad, cuando el documento no la trae")
    p.add_argument("--fecha", help="Fecha de cálculo AAAA-MM-DD (por defecto, hoy)")
    p.add_argument("--json", action="store_true",
                   help="Imprime la salida completa en JSON")
    p.add_argument("--ibc-futuro", type=int,
                   help="Salario sobre el que cotizaría de aquí en adelante, "
                        "en pesos de hoy (por defecto, el actual)")
    p.add_argument("--densidad-futura", type=float,
                   help="Ritmo de cotización futuro, de 0 a 1 (por defecto, el "
                        "de sus últimos 3 años). 1 = todos los meses")
    p.add_argument("--afiliacion-actual",
                   help="Dónde está afiliado HOY (Colpensiones, Porvenir, "
                        "Protección, Colfondos, Skandia, RPM o RAIS). Solo "
                        "aplica con varias historias laborales")
    args = p.parse_args()

    historias = []
    for ruta in args.caso:
        with open(ruta, encoding="utf-8") as f:
            historias.append(json.load(f))

    fecha = date.fromisoformat(args.fecha) if args.fecha else None
    salida = diagnosticar_historias(
        historias, sexo=args.sexo, edad=args.edad, fecha_calculo=fecha,
        ibc_futuro=args.ibc_futuro, densidad_futura=args.densidad_futura,
        afiliacion_actual=args.afiliacion_actual)

    if args.json:
        print(json.dumps(salida, ensure_ascii=False, indent=2, default=str))
    else:
        imprimir(salida)

    # Código de salida 1 si la verificación detuvo el proceso: así el agente
    # sabe que algo falló sin tener que interpretar el texto. Con varias
    # historias, basta con que una no cuadre.
    detenido = (salida.get("consolidacion") or {}).get("error") == "verificacion_fallida"
    if detenido or not (salida.get("verificacion") or {}).get("cuadra", True):
        sys.exit(1)


if __name__ == "__main__":
    main()
