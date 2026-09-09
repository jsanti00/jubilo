# Parser del reporte de historia laboral de Colfondos (herramienta de
# laboratorio; en producción la extracción la hace la IA con estos JSON
# como ejemplos). Convierte el texto del PDF (pdftotext -layout) al esquema
# de V0/casos/esquema-datos.md.
#
# Particularidades del formato Colfondos (distinto a Colpensiones):
# - Filas MENSUALES: PERIODO en formato YYYYMM, con días cotizados por mes.
# - Números estilo estadounidense: coma de miles y punto decimal (1,000,000.00).
# - Puede haber dos filas del mismo mes (dos aportantes): se conservan ambas.
# - Algunas filas traen aportante "0" y nombre ".": pagador sin identificar.
# - El total del encabezado es "al sistema general": incluye otros fondos
#   (la columna ADMINISTRADORA dice dónde quedó cada aporte).
# Uso: python3 parser_colfondos.py

import json
import re
from pathlib import Path

AQUI = Path(__file__).parent

# Archivo de texto ya extraído del PDF y JSON de salida
ENTRADA = Path("../../_entrada/historia-laboral-caso-06.txt")
SALIDA = AQUI.parent / "caso-06-colfondos-rais.json"

# Cada fila de datos: periodo (6 dígitos) ... IBC, cotización, días, administradora.
# Los números pueden venir vacíos como ".00" (meses en cero = lagunas explícitas)
# y en esas filas no hay administradora.
FILA = re.compile(
    r"^\s*(\d{6})\s+(.*?)\s+([\d,]*\.\d{2})\s+([\d,]*\.\d{2})\s+(\d+)\s*(\S.*?)?\s*$"
)


def numero(texto):
    """Convierte '1,000,000.00' (formato del reporte) a 1000000.0"""
    return float(texto.replace(",", ""))


def periodo_a_fechas(yyyymm):
    """'201503' -> ('2015-03-01', '2015-03-31'): el mes completo."""
    anio, mes = int(yyyymm[:4]), int(yyyymm[4:6])
    # Último día del mes (28/29/30/31 según el mes)
    import calendar
    ultimo = calendar.monthrange(anio, mes)[1]
    return f"{anio:04d}-{mes:02d}-01", f"{anio:04d}-{mes:02d}-{ultimo:02d}"


def separar_nit_y_empleador(texto):
    """Separa el bloque 'NIT 810,000,450 CONTACTAMOS LTDA' en (nit, nombre).

    Las filas de pagador sin identificar vienen como '0 .': quedan (None, None).
    """
    texto = re.sub(r"^(NIT|C\.?C\.?)\s+", "", texto.strip())  # Quita el tipo de id
    partes = texto.split(None, 1)
    if not partes:
        return None, None
    nit = partes[0].replace(",", "")
    nombre = partes[1].strip() if len(partes) > 1 else None
    if nit == "0" or nombre in (".", None):
        return (None if nit == "0" else nit), (None if nombre in (".", None) else nombre)
    return nit, nombre


# --- Leemos el texto y armamos los periodos ---
periodos = []
total_semanas = None
fecha_generacion = None
for linea in ENTRADA.read_text(encoding="utf-8").splitlines():
    # El total y la fecha vienen en el encabezado (repetido en cada página)
    m = re.search(r"Semanas cotizadas al sistema general de pensiones\s+([\d.]+)", linea)
    if m:
        total_semanas = float(m.group(1))
    m = re.search(r"Fecha de generación\s+(\d{4})/(\d{2})/(\d{2})", linea)
    if m:
        fecha_generacion = f"{m.group(1)}-{m.group(2)}-{m.group(3)}"

    m = FILA.match(linea)
    if not m:
        continue
    yyyymm, bloque_empleador, ibc, cotizacion, dias, administradora = m.groups()
    desde, hasta = periodo_a_fechas(yyyymm)
    nit, empleador = separar_nit_y_empleador(bloque_empleador)
    dias = int(dias)
    periodos.append({
        "desde": desde,
        "hasta": hasta,
        "empleador": empleador,
        "nit": nit,
        "tipo_cotizante": None if nit is None else "empleado",
        # Meses en cero: son lagunas explícitas, los valores quedan en null
        "ibc": numero(ibc) if dias > 0 else None,
        "ibc_tipo": "mensual",
        "cotizacion": numero(cotizacion) if dias > 0 else None,
        "dias_cotizados": dias,
        "semanas": None,
        "semanas_lic": None,
        "semanas_sim": None,
        "semanas_validas": None,
        "administradora": administradora.title() if administradora else None,
        "observacion": "normal" if dias > 0 else "sin_cotizacion",
    })

# --- Armamos el caso con el esquema estándar (anonimizado: sin nombre/cédula) ---
caso = {
    "caso_id": "caso-06-colfondos-rais",
    "documento": {
        "administradora_emisora": "Colfondos",
        "regimen": "RAIS",
        "formato": "colfondos_reporte_historia",
        "fecha_generacion": fecha_generacion,
    },
    "afiliado": {
        "fecha_nacimiento": None,   # El reporte no la trae
        "edad_en_documento": None,  # Tampoco trae edad
        "sexo": None,               # Ni sexo: todo se vuelve pregunta al usuario
        "fecha_afiliacion": "2015-03-01",
        "estado_afiliacion": None,
    },
    "resumen_documento": {
        "total_semanas": total_semanas,
        "total_dias": None,
        "saldo_cuenta_individual": None,  # Colfondos no imprime saldo aquí
        "semanas_en_otros_fondos": None,  # El total ya es "al sistema general"
        # La tabla de este documento suma 407,43 semanas (tope 30 días/mes)
        # pero el encabezado dice 398,0: 9,43 semanas de diferencia que ninguna
        # regla de conteo conocida reproduce. Discrepancia interna del documento.
        "nota_verificacion": ("discrepancia_documental: la tabla suma mas "
                              "semanas (407,43) que el total impreso (398,0); "
                              "el agente debe reportarla al usuario"),
    },
    "periodos": periodos,
}

SALIDA.write_text(json.dumps(caso, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"Escrito {SALIDA.name}: {len(periodos)} periodos, "
      f"total del documento: {total_semanas} semanas")
