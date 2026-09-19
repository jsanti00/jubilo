# Los parsers: convierten el texto de un documento en el JSON del esquema.
#
# QUE ES ESTO. Un parser es un programa que lee la tabla del documento fila por
# fila y la copia a la estructura estandar de `casos/esquema-datos.md`. No
# interpreta, no estima y no redondea: copia. Si una fila no se entiende, el
# parser lo dice en vez de inventarse un numero.
#
# HAY UN PARSER POR PLANTILLA, no uno por fondo. Cada administradora imprime su
# historia laboral distinta, asi que no existe un parser universal.
#
# DATOS PERSONALES. Ninguno de estos parsers guarda nombre, cedula, correo ni
# direccion del afiliado, aunque el documento los traiga. La cedula si se lee,
# pero solo para un uso: en Colpensiones, cuando el aportante de una fila es la
# propia cedula de la persona, esa fila es una cotizacion como independiente.
# Se usa en el momento y se descarta. Los empleadores y sus NIT si se guardan:
# la calculadora los necesita para detectar periodos simultaneos.
#
# QUE ES ESTABLE Y QUE ES FRAGIL. Al final de cada parser hay una nota que dice
# que partes son la estructura fija del formato (encabezados de columna, el NIT
# de la entidad, los rotulos numerados) y cuales dependen de como quedo
# repartido el texto en la hoja de esa muestra concreta.

import calendar
import re

# ---------------------------------------------------------------------------
# Ayudas comunes: numeros y fechas
# ---------------------------------------------------------------------------

# Los meses en espanol, para las fechas escritas con letras.
MESES = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6,
    "julio": 7, "agosto": 8, "septiembre": 9, "setiembre": 9, "octubre": 10,
    "noviembre": 11, "diciembre": 12,
}


def numero_co(texto):
    """Convierte '1.236,57' (estilo colombiano) al numero 1236.57."""
    return float(texto.strip().replace(".", "").replace(",", "."))


def numero_us(texto):
    """Convierte '1,000,000.00' (estilo estadounidense) al numero 1000000.0."""
    return float(texto.strip().replace(",", ""))


def fecha_dmy(texto):
    """Convierte '11/05/1967' a la fecha estandar '1967-05-11'."""
    dia, mes, anio = texto.strip().split("/")
    return f"{anio}-{mes}-{dia}"


def fecha_ymd(texto):
    """Convierte '2023/08/04' a '2023-08-04'."""
    anio, mes, dia = texto.strip().split("/")
    return f"{anio}-{mes}-{dia}"


def fecha_en_letras(dia, mes, anio):
    """Convierte ('30', 'junio', '2026') a '2026-06-30'. None si el mes no existe."""
    numero_mes = MESES.get(mes.strip().lower())
    if not numero_mes:
        return None
    return f"{int(anio):04d}-{numero_mes:02d}-{int(dia):02d}"


def rango_del_mes(anio, mes):
    """Del ano y el mes saca ('2015-03-01', '2015-03-31'): el mes completo."""
    anio, mes = int(anio), int(mes)
    ultimo = calendar.monthrange(anio, mes)[1]
    return f"{anio:04d}-{mes:02d}-01", f"{anio:04d}-{mes:02d}-{ultimo:02d}"


def sexo_de(palabra):
    """'Masculino' -> 'M', 'Femenino' -> 'F'. Cualquier otra cosa -> None."""
    p = (palabra or "").strip().lower()
    if p.startswith("masc"):
        return "M"
    if p.startswith("fem"):
        return "F"
    return None


def periodo_vacio():
    """Un periodo con todos los campos del esquema, para no olvidar ninguno."""
    return {
        "desde": None, "hasta": None, "empleador": None, "nit": None,
        "tipo_cotizante": None, "ibc": None, "ibc_tipo": None,
        "cotizacion": None, "dias_cotizados": None, "semanas": None,
        "semanas_lic": None, "semanas_sim": None, "semanas_validas": None,
        "administradora": None, "observacion": "normal",
    }


def armar_caso(formato, emisora, regimen, tipo_documento, fecha_generacion,
               afiliado, resumen, periodos, nota=None):
    """Mete todo en la estructura estandar del esquema de datos."""
    documento = {
        "administradora_emisora": emisora,
        "regimen": regimen,
        "formato": formato,
        "fecha_generacion": fecha_generacion,
        # Campo nuevo: distingue una historia laboral de un extracto de cuenta.
        # Son documentos distintos y no se pueden usar para lo mismo.
        "tipo_documento": tipo_documento,
    }
    if nota:
        documento["nota"] = nota
    # El `caso_id` es solo una etiqueta para poder referirse a esta lectura.
    # La calculadora la exige, asi que se pone una generica: nunca lleva el
    # nombre ni la cedula de nadie.
    return {"caso_id": f"extraccion-{formato}",
            "documento": documento, "afiliado": afiliado,
            "resumen_documento": resumen, "periodos": periodos}


class NoSePudoLeer(Exception):
    """Se levanta cuando el documento tiene la pinta correcta pero la tabla no
    se dejo leer. Quien llama al parser lo traduce en "mandalo al modelo"."""


# ---------------------------------------------------------------------------
# Colpensiones: "REPORTE DE SEMANAS COTIZADAS EN PENSIONES"
# ---------------------------------------------------------------------------
#
# La tabla que se lee es el "RESUMEN DE SEMANAS COTIZADAS POR EMPLEADOR": una
# fila por tramo de tiempo con un mismo empleador, con el ULTIMO salario del
# tramo (no un promedio) y cuatro columnas de semanas.
#
# Columnas: [1] identificacion del aportante, [2] nombre, [3] desde, [4] hasta,
# [5] ultimo salario, [6] semanas, [7] licencias, [8] simultaneas, [9] total.

FILA_COLPENSIONES = re.compile(
    r"^\s*(\d{6,14})\s+(.+?)\s+(\d{2}/\d{2}/\d{4})\s+(\d{2}/\d{2}/\d{4})\s+"
    r"\$\s?([\d\.]+)\s+([\d\.,]+)\s+([\d\.,]+)\s+([\d\.,]+)\s+([\d\.,]+)\s*$"
)


def parsear_colpensiones(texto):
    lineas = texto.splitlines()

    # --- Encabezado: los datos del afiliado que SI se guardan ---
    def buscar(patron, bandera=0):
        m = re.search(patron, texto, bandera)
        return m.group(1).strip() if m else None

    nacimiento = buscar(r"Fecha de Nacimiento:\s*(\d{2}/\d{2}/\d{4})")
    afiliacion = buscar(r"Fecha Afiliaci[oó]n:\s*(\d{2}/\d{2}/\d{4})")
    estado = buscar(r"Estado Afiliaci[oó]n:\s*([A-Za-zÁÉÍÓÚáéíóúñÑ ]+?)\s*$", re.MULTILINE)
    # La cedula se usa solo para saber si una fila es cotizacion propia. No se
    # guarda en ninguna parte del resultado.
    cedula = buscar(r"N[uú]mero de Documento:\s*(\d+)")

    # La fecha del reporte viene con el mes en letras: "ACTUALIZADO A: 30 junio 2026".
    generacion = None
    m = re.search(r"ACTUALIZADO A:\s*(\d{1,2})\s+([A-Za-zÁÉÍÓÚáéíóúñÑ]+)\s+(\d{4})", texto)
    if m:
        generacion = fecha_en_letras(*m.groups())

    # --- La tabla ---
    periodos = []
    for linea in lineas:
        # El rotulo [10] cierra el resumen. Lo que viene despues son los
        # detalles de pagos, que tienen otras columnas y no se leen aqui.
        if "TOTAL SEMANAS COTIZADAS" in linea:
            break
        m = FILA_COLPENSIONES.match(linea)
        if not m:
            continue
        nit, nombre, desde, hasta, salario, sem, lic, sim, total = m.groups()
        p = periodo_vacio()
        p.update({
            "desde": fecha_dmy(desde),
            "hasta": fecha_dmy(hasta),
            "empleador": nombre.strip(),
            "nit": nit,
            # Si el aportante es la propia cedula, cotizo como independiente.
            "tipo_cotizante": "independiente" if (cedula and nit == cedula) else "empleado",
            "ibc": int(numero_co(salario)),
            "ibc_tipo": "ultimo_del_rango",
            "semanas": numero_co(sem),
            "semanas_lic": numero_co(lic),
            "semanas_sim": numero_co(sim),
            "semanas_validas": numero_co(total),
            "administradora": "Colpensiones",
            "observacion": "simultaneo" if numero_co(sim) > 0 else "normal",
        })
        periodos.append(p)

    if not periodos:
        raise NoSePudoLeer("el resumen por empleador no trajo ninguna fila legible")

    # --- El total impreso, que es contra lo que se verifica la lectura ---
    # Se prefiere el rotulo [26], que es el total definitivo del documento
    # (cotizadas + tiempos publicos - simultaneos) y viene en la misma linea.
    total_doc = None
    m = re.search(r"\[26\]\s*TOTAL SEMANAS[^\n]*?([\d\.]+,\d{2})", texto)
    if m:
        total_doc = numero_co(m.group(1))
    else:
        # Respaldo: el rotulo [10], cuyo numero cae en una linea posterior.
        for i, linea in enumerate(lineas):
            if "TOTAL SEMANAS COTIZADAS" in linea:
                for siguiente in lineas[i:i + 4]:
                    enc = re.search(r"([\d\.]+,\d{2})\s*$", siguiente)
                    if enc:
                        total_doc = numero_co(enc.group(1))
                        break
                break

    afiliado = {
        "fecha_nacimiento": fecha_dmy(nacimiento) if nacimiento else None,
        "edad_en_documento": None,
        # El reporte de Colpensiones no dice el sexo: se le pregunta a la persona.
        "sexo": None,
        "fecha_afiliacion": fecha_dmy(afiliacion) if afiliacion else None,
        "estado_afiliacion": (estado.lower().replace(" ", "_") if estado else None),
    }
    resumen = {"total_semanas": total_doc, "total_dias": None,
               "saldo_cuenta_individual": None, "semanas_en_otros_fondos": None}
    return armar_caso("colpensiones_reporte_semanas", "Colpensiones", "RPM",
                      "historia_laboral", generacion, afiliado, resumen, periodos)


# ---------------------------------------------------------------------------
# Colfondos: "Reporte de historia laboral"
# ---------------------------------------------------------------------------
#
# Filas mensuales. El periodo viene como AAAAMM y los numeros van al estilo
# estadounidense (coma de miles, punto decimal). La ultima columna dice en que
# fondo quedo ese aporte, que puede no ser Colfondos: el total del encabezado
# es "al sistema general", o sea de todos los fondos juntos.

FILA_COLFONDOS = re.compile(
    r"^\s*(\d{6})\s+(.*?)\s+([\d,]*\.\d{2})\s+([\d,]*\.\d{2})\s+(\d+)\s*(\S.*?)?\s*$"
)


def _nit_y_empleador_colfondos(bloque):
    """Separa 'NIT 810,000,450 CONTACTAMOS LTDA' en el NIT y el nombre.

    Las filas de pagador sin identificar llegan como '0 .' y quedan vacias.
    """
    bloque = re.sub(r"^(NIT|C\.?C\.?)\s+", "", bloque.strip())
    partes = bloque.split(None, 1)
    if not partes:
        return None, None
    nit = partes[0].replace(",", "")
    nombre = partes[1].strip() if len(partes) > 1 else None
    if nit == "0":
        nit = None
    if nombre in (".", ""):
        nombre = None
    return nit, nombre


def parsear_colfondos(texto):
    periodos = []
    total_semanas = None
    generacion = None
    afiliacion = None

    for linea in texto.splitlines():
        # El encabezado se repite en cada pagina: basta con leerlo una vez.
        m = re.search(r"Semanas cotizadas al sistema general de pensiones\s+([\d\.]+)", linea)
        if m:
            total_semanas = float(m.group(1))
        m = re.search(r"Fecha de generaci[oó]n\s+(\d{4}/\d{2}/\d{2})", linea)
        if m:
            generacion = fecha_ymd(m.group(1))
        m = re.search(r"Fecha de afiliaci[oó]n a Colfondos\s+(\d{4}/\d{2}/\d{2})", linea)
        if m:
            afiliacion = fecha_ymd(m.group(1))

        m = FILA_COLFONDOS.match(linea)
        if not m:
            continue
        aaaamm, bloque, ibc, cotizacion, dias, administradora = m.groups()
        nit, empleador = _nit_y_empleador_colfondos(bloque)
        dias = int(dias)
        desde, hasta = rango_del_mes(aaaamm[:4], aaaamm[4:])
        p = periodo_vacio()
        p.update({
            "desde": desde, "hasta": hasta,
            "empleador": empleador, "nit": nit,
            "tipo_cotizante": None if nit is None else "empleado",
            # Los meses en cero son lagunas declaradas: no llevan cifras.
            "ibc": numero_us(ibc) if dias > 0 else None,
            "ibc_tipo": "mensual",
            "cotizacion": numero_us(cotizacion) if dias > 0 else None,
            "dias_cotizados": dias,
            "administradora": administradora.title() if administradora else None,
            "observacion": "normal" if dias > 0 else "sin_cotizacion",
        })
        periodos.append(p)

    if not periodos:
        raise NoSePudoLeer("la tabla mensual no trajo ninguna fila legible")

    afiliado = {"fecha_nacimiento": None, "edad_en_documento": None, "sexo": None,
                "fecha_afiliacion": afiliacion, "estado_afiliacion": None}
    resumen = {"total_semanas": total_semanas, "total_dias": None,
               "saldo_cuenta_individual": None,
               # El total del encabezado ya incluye los otros fondos.
               "semanas_en_otros_fondos": None}
    return armar_caso("colfondos_reporte_historia", "Colfondos", "RAIS",
                      "historia_laboral", generacion, afiliado, resumen, periodos)


# ---------------------------------------------------------------------------
# Porvenir: "Resumen de tu Historia Laboral"
# ---------------------------------------------------------------------------
#
# La complicacion de este formato: el nombre del empleador va en una celda de
# dos renglones, asi que en el texto queda partido arriba y abajo de la fila de
# datos. La fila util es la que trae mes, dias, IBC y administradora.

FILA_PORVENIR = re.compile(
    r"^(.*?)\s*(\d{4})/(\d{2})\s+(\d{1,3})\s+\$\s*([\d\.]+)\s+([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ \.]*?)\s*$"
)

# Renglones que nunca son parte de un nombre de empleador.
RUIDO_PORVENIR = re.compile(
    r"^\s*$|P[aá]gina|Empleador|cotizados|ingreso base|Administradora|"
    r"Ten en cuenta|^-|Total Semanas|Resumen de tu|Detalle de tu|Hola,|"
    r"documento|nacimiento|G[eé]nero|Aqu[ií] encontrar", re.IGNORECASE
)


def parsear_porvenir(texto):
    lineas = texto.splitlines()

    def buscar(patron):
        m = re.search(patron, texto)
        return m.group(1).strip() if m else None

    nacimiento = buscar(r"Fecha de nacimiento:\s*(\d{2}/\d{2}/\d{4})")
    genero = buscar(r"G[eé]nero:\s*([A-Za-zÁÉÍÓÚáéíóú]+)")
    total = buscar(r"Total Semanas Cotizadas\s*\|\s*([\d\.]+,\d{2})")
    saldo = buscar(r"Saldo Total Acumulado\s*\|\s*\$\s*([\d\.]+)")

    # El nombre del empleador vive en una celda de dos renglones y la fila de
    # datos queda en la mitad: un pedazo arriba y otro abajo. Para repartir
    # bien esos pedazos hay que saber donde esta cada fila de datos.
    indices_de_fila = [i for i, l in enumerate(lineas) if FILA_PORVENIR.match(l)]

    def pedazos(i, paso, tope):
        """Recoge los renglones de nombre que estan pegados a la fila `i`.

        Camina hacia arriba (paso -1) o hacia abajo (paso +1) y se detiene en
        cuanto encuentra algo que no puede ser parte del nombre: un renglon en
        blanco, un encabezado de columna, un parrafo del documento o el limite
        que marca la fila vecina. Solo lo pegado a la fila es suyo.
        """
        salida = []
        j = i + paso
        while 0 <= j < len(lineas) and len(salida) < 2:
            if paso < 0 and j < tope:
                break
            if paso > 0 and j >= tope:
                break
            trozo = lineas[j].strip()
            if not trozo or RUIDO_PORVENIR.search(lineas[j]):
                break
            # En esta plantilla los nombres de empleador van todos en
            # mayusculas. Un renglon con minusculas es prosa del documento
            # (una advertencia, una nota al pie), no un nombre.
            if trozo != trozo.upper():
                break
            salida.append(trozo)
            j += paso
        return list(reversed(salida)) if paso < 0 else salida

    periodos = []
    for puesto, i in enumerate(indices_de_fila):
        m = FILA_PORVENIR.match(lineas[i])
        prefijo, anio, mes, dias, ibc, administradora = m.groups()

        # Un renglon solo puede ser de una fila. El de justo encima de la fila
        # siguiente es suyo, no nuestro, y el de justo debajo de la anterior ya
        # esta tomado. Estas dos fronteras evitan mezclar dos empleadores.
        anterior = indices_de_fila[puesto - 1] if puesto > 0 else None
        siguiente = indices_de_fila[puesto + 1] if puesto + 1 < len(indices_de_fila) else None
        tope_arriba = (anterior + 2) if anterior is not None else 0
        tope_abajo = (siguiente - 1) if siguiente is not None else len(lineas)

        arriba = pedazos(i, -1, tope_arriba)
        abajo = pedazos(i, +1, tope_abajo)
        nombre = " ".join([t for t in arriba + [prefijo.strip()] + abajo if t])

        desde, hasta = rango_del_mes(anio, mes)
        p = periodo_vacio()
        p.update({
            "desde": desde, "hasta": hasta,
            "empleador": nombre or None,
            "tipo_cotizante": "empleado",
            "ibc": int(numero_co(ibc)),
            "ibc_tipo": "mensual",
            "dias_cotizados": int(dias),
            "administradora": administradora.strip().title(),
        })
        periodos.append(p)

    if not periodos:
        raise NoSePudoLeer("la tabla de meses no trajo ninguna fila legible")

    afiliado = {"fecha_nacimiento": fecha_dmy(nacimiento) if nacimiento else None,
                "edad_en_documento": None, "sexo": sexo_de(genero),
                "fecha_afiliacion": None, "estado_afiliacion": None}
    resumen = {"total_semanas": numero_co(total) if total else None,
               "total_dias": None,
               "saldo_cuenta_individual": int(numero_co(saldo)) if saldo else None,
               "semanas_en_otros_fondos": None}
    # Este formato no imprime fecha de generacion.
    return armar_caso("porvenir_historia_laboral", "Porvenir", "RAIS",
                      "historia_laboral", None, afiliado, resumen, periodos)


# ---------------------------------------------------------------------------
# Historia Laboral Consolidada (la muestra disponible es de Skandia)
# ---------------------------------------------------------------------------
#
# El documento trae tres tablas: RPM valido para bono, RPM no valido, y RAIS.
# En la muestra solo la de RAIS tiene filas. Las tablas de RPM llevan otras
# columnas (fecha de ingreso y de retiro), asi que el parser vigila: si ve
# filas en una seccion que no sabe leer, se niega y manda el documento al
# camino del modelo en vez de entregar una lectura incompleta.

FILA_CONSOLIDADA = re.compile(
    r"^\s*(\d{6})\s+(\d+)\s+(.+?)\s+\$\s*([\d,]+\.\d{2})\s+(\S+)\s+(\S+)\s+"
    r"\$\s*([\d,]+)\s+(\d+)\s+([\d,]+)\s*$"
)

# Una fila de las secciones de RPM empieza igual (periodo y NIT) pero sigue con
# dos fechas. Sirve para darse cuenta de que hay datos que no se estan leyendo.
FILA_RPM_CONSOLIDADA = re.compile(r"^\s*(\d{6})\s+(\d+)\s+.*\d{2}/\d{2}/\d{4}")


def parsear_consolidada(texto):
    lineas = texto.splitlines()

    # --- Datos del afiliado: el valor va en el renglon de abajo del rotulo ---
    def valor_debajo(rotulo, patron):
        for i, linea in enumerate(lineas):
            if rotulo in linea:
                for siguiente in lineas[i + 1:i + 3]:
                    m = re.search(patron, siguiente)
                    if m:
                        return m.group(1)
        return None

    nacimiento = valor_debajo("Fecha de nacimiento", r"(\d{2}/\d{2}/\d{4})\s*$")
    genero = valor_debajo("Sexo", r"([A-Za-zÁÉÍÓÚáéíóú]+)\s*$")

    generacion = None
    m = re.search(r"Fecha:\s*(\d{4})-(\d{2})-(\d{2})", texto)
    if m:
        generacion = "-".join(m.groups())

    # --- El resumen del final: dias y semanas totales ---
    total_dias = total_semanas = None
    m = re.search(r"Tiempo total cotizado al Sistema General de Pensiones\s+"
                  r"([\d,]+)\s+([\d,]+\.\d{2})", texto)
    if m:
        total_dias = int(numero_us(m.group(1)))
        total_semanas = numero_us(m.group(2))

    # --- Las filas de la tabla de RAIS ---
    periodos = []
    entidades = []
    filas_no_leidas = 0
    for i, linea in enumerate(lineas):
        m = FILA_CONSOLIDADA.match(linea)
        if not m:
            # Una fila con dos fechas es de las tablas de RPM: se cuenta para
            # avisar que el documento trae datos que este parser no cubre.
            if FILA_RPM_CONSOLIDADA.match(linea):
                filas_no_leidas += 1
            continue
        aaaamm, nit, nombre, ibc, entidad_aporte, responsable, cotizacion, dias, _acum = m.groups()

        # El nombre del empleador puede seguir en el renglon de abajo cuando no
        # cabe en la celda. Ese renglon no empieza por un periodo de 6 digitos.
        if i + 1 < len(lineas):
            cola = lineas[i + 1].strip()
            if cola and not re.match(r"^\d{6}\s", cola) and not re.search(r"\$|P[aá]gina|Fecha:", cola):
                nombre = f"{nombre.strip()} {cola}"

        desde, hasta = rango_del_mes(aaaamm[:4], aaaamm[4:])
        entidades.append(responsable)
        p = periodo_vacio()
        p.update({
            "desde": desde, "hasta": hasta,
            "empleador": nombre.strip(), "nit": nit,
            "tipo_cotizante": "empleado",
            "ibc": numero_us(ibc), "ibc_tipo": "mensual",
            "cotizacion": numero_us(cotizacion),
            "dias_cotizados": int(dias),
            "administradora": responsable.title(),
        })
        periodos.append(p)

    if not periodos:
        raise NoSePudoLeer("la tabla de ahorro individual no trajo filas legibles")
    if filas_no_leidas:
        raise NoSePudoLeer(
            f"el documento trae {filas_no_leidas} filas en las tablas de prima "
            "media, que este parser no sabe leer")

    # La emisora no esta en el encabezado: se toma de la entidad responsable
    # que mas se repite en la tabla. Asi el mismo parser sirve si otra
    # administradora usa esta misma plantilla.
    emisora = max(set(entidades), key=entidades.count).title() if entidades else None

    afiliado = {"fecha_nacimiento": fecha_dmy(nacimiento) if nacimiento else None,
                "edad_en_documento": None, "sexo": sexo_de(genero),
                "fecha_afiliacion": None, "estado_afiliacion": None}
    resumen = {"total_semanas": total_semanas, "total_dias": total_dias,
               "saldo_cuenta_individual": None, "semanas_en_otros_fondos": None}
    return armar_caso("historia_laboral_consolidada", emisora, "RAIS",
                      "historia_laboral", generacion, afiliado, resumen, periodos)


# ---------------------------------------------------------------------------
# Proteccion: extracto trimestral (NO es una historia laboral)
# ---------------------------------------------------------------------------
#
# CUIDADO CON ESTE DOCUMENTO. Trae el saldo y el total de semanas de toda la
# vida, pero la tabla de movimientos es solo del trimestre. No sirve para
# reconstruir la historia laboral: sirve para saber el saldo, que en RAIS es el
# insumo principal. Por eso el resultado lleva `cobertura_periodos` en
# "solo_trimestre" y no se verifica contra el total de semanas: nunca cuadraria.

FILA_EXTRACTO = re.compile(
    r"^\s*([A-Za-zÁÉÍÓÚáéíóú]+)\s+(\d{4})\s+(\d{1,2})\s+(.*?)\s*\$\s?([\d\.]+)\s+"
    r"\$\s?([\d\.]+)\s+\$\s?([\d\.]+)\s*$"
)


def parsear_extracto_proteccion(texto):
    def buscar(patron, bandera=0):
        m = re.search(patron, texto, bandera)
        return m.group(1).strip() if m else None

    # "Fecha de Afiliación   Marzo 01 de 2024"
    afiliacion = None
    m = re.search(r"Fecha de Afiliaci[oó]n\s+([A-Za-zÁÉÍÓÚáéíóú]+)\s+(\d{1,2})\s+de\s+(\d{4})", texto)
    if m:
        afiliacion = fecha_en_letras(m.group(2), m.group(1), m.group(3))

    # La fecha de expedicion es la mas tardia de las tres del encabezado (las
    # otras dos son el inicio y el fin del trimestre, y un extracto se expide
    # despues de que el trimestre termina). Se busca solo en el encabezado.
    generacion = None
    encabezado = texto[:3000]
    for mm in re.finditer(r"([A-Za-zÁÉÍÓÚáéíóú]+)\s+(\d{1,2})\s+de\s+(\d{4})", encabezado):
        candidata = fecha_en_letras(mm.group(2), mm.group(1), mm.group(3))
        if candidata:
            generacion = candidata if generacion is None or candidata > generacion else generacion

    # El trio de semanas del resumen: prima media, ahorro individual y total.
    semanas_rpm = semanas_rais = total_semanas = None
    m = re.search(r"(\d{1,3},\d{2})\s+(\d{1,3},\d{2})\s+(\d{1,3},\d{2})", texto)
    if m:
        semanas_rpm = numero_co(m.group(1))
        semanas_rais = numero_co(m.group(2))
        total_semanas = numero_co(m.group(3))

    saldo = buscar(r"Mi saldo total ahorrado[\s\S]{0,400}?\$\s?([\d\.]+)\s*$", re.MULTILINE)
    # Respaldo: el saldo tambien es el ultimo de la fila de cuatro cifras.
    if saldo is None:
        m = re.search(r"\$\s?([\d\.]+)\s+\$0\s+\$\s?([\d\.]+)\s+\$0\s+\$\s?([\d\.]+)", texto)
        if m:
            saldo = m.group(3)

    aportes = None
    m = re.search(r"Aportes totales en mi cuenta de ahorro individual\s+\$\s?([\d\.]+)", texto)
    if m:
        aportes = int(numero_co(m.group(1)))
    rendimientos = None
    m = re.search(r"Mis rendimientos totales en mi cuenta de ahorro individual\s+\$\s?([\d\.]+)", texto)
    if m:
        rendimientos = int(numero_co(m.group(1)))

    # En que fondo esta el ahorro: se lee de la torta de distribucion, que
    # imprime "100,00% Mayor riesgo". Si hay varios, quedan todos.
    fondos = [f"{pct}% {nombre.strip()}" for pct, nombre in re.findall(
        r"(\d{1,3},\d{2})%\s*(Mayor riesgo|Moderado|Conservador|Retiro [Pp]rogramado)",
        texto)]
    fondo = "; ".join(dict.fromkeys(fondos)) or None

    # --- Los movimientos del trimestre ---
    periodos = []
    for linea in texto.splitlines():
        m = FILA_EXTRACTO.match(linea)
        if not m:
            continue
        mes, anio, dias, empleador, salario, monto, _abonado = m.groups()
        numero_mes = MESES.get(mes.lower())
        if not numero_mes:
            continue
        desde, hasta = rango_del_mes(anio, numero_mes)
        p = periodo_vacio()
        p.update({
            "desde": desde, "hasta": hasta,
            # El nombre del empleador viene partido en varios renglones; aqui
            # solo queda el pedazo que cayo en esta linea.
            "empleador": empleador.strip() or None,
            "tipo_cotizante": "empleado",
            "ibc": int(numero_co(salario)), "ibc_tipo": "mensual",
            "cotizacion": int(numero_co(monto)),
            "dias_cotizados": int(dias),
            "administradora": "Proteccion",
        })
        periodos.append(p)

    afiliado = {"fecha_nacimiento": None, "edad_en_documento": None, "sexo": None,
                "fecha_afiliacion": afiliacion, "estado_afiliacion": None}
    resumen = {
        "total_semanas": total_semanas,
        "total_dias": None,
        "saldo_cuenta_individual": int(numero_co(saldo)) if saldo else None,
        # Semanas que el total incluye pero que no estan en esta cuenta.
        "semanas_en_otros_fondos": semanas_rpm if semanas_rpm else None,
        # Aviso para quien lea esto despues: los periodos NO son toda la vida.
        "cobertura_periodos": "solo_trimestre",
        "aportes_acumulados": aportes,
        "rendimientos_acumulados": rendimientos,
        "semanas_rais": semanas_rais,
        "fondo": fondo,
    }
    nota = ("Extracto trimestral, no historia laboral: los periodos son solo "
            "los del trimestre. Sirve para el saldo y el total de semanas; "
            "para el detalle hay que pedir la historia laboral.")
    return armar_caso("proteccion_extracto_trimestral", "Proteccion", "RAIS",
                      "extracto_cuenta", generacion, afiliado, resumen,
                      periodos, nota=nota)


# El directorio que conecta cada formato detectado con su parser.
PARSERS = {
    "colpensiones_reporte_semanas": parsear_colpensiones,
    "colfondos_reporte_historia": parsear_colfondos,
    "porvenir_historia_laboral": parsear_porvenir,
    "historia_laboral_consolidada": parsear_consolidada,
    "proteccion_extracto_trimestral": parsear_extracto_proteccion,
}


# ---------------------------------------------------------------------------
# Que es estructura estable y que se puede romper con otro documento
# ---------------------------------------------------------------------------
#
# Esto importa porque de cuatro de los cinco formatos hay UNA sola muestra. Un
# parser hecho sobre una sola muestra puede estar copiando, sin querer, como
# quedo repartido el texto en esa hoja concreta. Aqui queda escrito que parte
# de cada parser es la plantilla de verdad y que parte es sospechosa, para que
# el dia que llegue una segunda muestra se sepa donde mirar primero.
#
# COLPENSIONES (3 muestras, la base mas solida)
#   Estable: los rotulos numerados [1] a [26] son parte del formato oficial y
#     no cambian. El orden de las columnas y el formato de las fechas tampoco.
#   Ojo con: el total se toma del rotulo [26] y, si no esta, del [10], cuyo
#     numero cae en un renglon distinto segun cuanto ocupe la tabla. Y solo se
#     lee el resumen por empleador: si alguien tiene tiempos publicos, esas
#     semanas entran en el total [26] pero no en las filas, y la verificacion
#     lo cazaria mandando el documento al modelo. Eso es lo correcto, no un
#     error, pero significa que esos casos no ganan velocidad.
#
# COLFONDOS (1 muestra)
#   Estable: el periodo en formato AAAAMM, los numeros al estilo
#     estadounidense y la columna final con la administradora.
#   Ojo con: las filas de pagador sin identificar ("0 ."), que aqui se
#     traducen a empleador vacio. Con otro documento pueden venir escritas de
#     otra manera.
#
# PORVENIR (1 muestra)
#   Estable: los rotulos del encabezado y las columnas mes, dias, IBC y
#     administradora.
#   Ojo con: el nombre del empleador. Viene partido en dos renglones, uno
#     arriba y otro abajo de la fila, y para volverlo a armar el parser asume
#     dos cosas de esa muestra: que los pedazos estan pegados a la fila y que
#     van en mayusculas. Un nombre de tres renglones o escrito en minusculas
#     saldria incompleto. No afecta ni las semanas ni los salarios: afecta a
#     quien se le atribuye el periodo, que es lo que usa la deteccion de
#     periodos simultaneos.
#
# HISTORIA LABORAL CONSOLIDADA (1 muestra, de Skandia)
#   Estable: las tres secciones (prima media valida para bono, prima media no
#     valida, y ahorro individual) y las columnas de la tercera.
#   Ojo con: en la muestra las dos secciones de prima media estan vacias, asi
#     que sus columnas nunca se han leido. Por eso el parser cuenta las filas
#     que parecen de esas secciones y, si encuentra alguna, se niega a
#     entregar una lectura a medias. Tambien: la administradora emisora se
#     deduce de la columna "Entidad responsable", no del encabezado.
#
# EXTRACTO TRIMESTRAL DE PROTECCION (1 muestra)
#   Estable: los rotulos de los totales, que son los datos que valen de este
#     documento (saldo, semanas, aportes, rendimientos).
#   Ojo con: la tabla de movimientos. El nombre del empleador y el concepto
#     quedan repartidos en varios renglones y el parser solo recoge el pedazo
#     que cayo en la linea de la fila. La fecha de expedicion se deduce como
#     la mas tardia de las tres del encabezado.
