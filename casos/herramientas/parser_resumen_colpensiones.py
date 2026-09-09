# Herramienta de laboratorio: convierte el "Resumen de semanas cotizadas por empleador"
# de un reporte de Colpensiones (ya extraído a texto .md) al esquema de datos JSON de Júbilo.
# Uso: python3 parser_resumen_colpensiones.py

import json      # Para escribir el archivo JSON de salida
import re        # Para reconocer las filas de la tabla con un patrón de texto
from pathlib import Path  # Para manejar rutas de archivos

# Carpeta donde está este script (así las rutas funcionan sin importar desde dónde se corra)
AQUI = Path(__file__).parent

# Configuración de cada caso: archivo de entrada, archivo de salida y datos del afiliado
# que se leen a mano del encabezado del documento (anonimizados: sin nombre ni cédula).
# "cedula" se usa SOLO para detectar cotizaciones como independiente; no se guarda en el JSON.
CASOS = [
    {
        "entrada": AQUI / "../../_entrada/historia-laboral-caso-04.md",
        "salida": AQUI / "../caso-04-colpensiones-rpm.json",
        "caso_id": "caso-04-colpensiones-rpm",
        "fecha_generacion": "2026-06-30",
        "fecha_nacimiento": "1978-05-18",
        "fecha_afiliacion": "2025-07-01",
        "cedula": "37559380",
    },
    {
        "entrada": AQUI / "../../_entrada/historia-laboral-caso-05.md",
        "salida": AQUI / "../caso-05-colpensiones-rpm.json",
        "caso_id": "caso-05-colpensiones-rpm",
        "fecha_generacion": "2026-07-13",
        "fecha_nacimiento": "1967-05-11",
        "fecha_afiliacion": "1992-05-12",
        "cedula": "91252815",
    },
]

# Patrón que reconoce una fila de la tabla resumen. Una fila tiene:
# número de aportante, nombre, fecha desde, fecha hasta, $salario, y 4 números de semanas
FILA = re.compile(
    r"^\s*(\d{6,12})\s+(.+?)\s+(\d{2}/\d{2}/\d{4})\s+(\d{2}/\d{2}/\d{4})\s+"
    r"\$\s?([\d\.]+)\s+([\d\.,]+)\s+([\d\.,]+)\s+([\d\.,]+)\s+([\d\.,]+)\s*$"
)


def numero(texto):
    # Convierte "1.236,57" (formato colombiano) al número 1236.57
    return float(texto.replace(".", "").replace(",", "."))


def fecha_iso(texto):
    # Convierte "11/05/1967" al formato estándar "1967-05-11"
    dia, mes, anio = texto.split("/")
    return f"{anio}-{mes}-{dia}"


def procesar(caso):
    # Lee el documento completo como texto
    lineas = caso["entrada"].read_text(encoding="utf-8").splitlines()

    periodos = []
    for linea in lineas:
        # La tabla resumen termina donde aparece el total; ahí dejamos de leer
        if "TOTAL SEMANAS COTIZADAS" in linea:
            break
        m = FILA.match(linea)
        if not m:
            continue  # Las líneas que no son filas de la tabla se ignoran
        nit, nombre, desde, hasta, salario, sem, lic, sim, total = m.groups()
        periodos.append({
            "desde": fecha_iso(desde),
            "hasta": fecha_iso(hasta),
            "empleador": nombre.strip(),
            "nit": nit,
            # Si el aportante es la propia cédula del afiliado, cotizó como independiente
            "tipo_cotizante": "independiente" if nit == caso["cedula"] else "empleado",
            "ibc": int(numero(salario)),
            "ibc_tipo": "ultimo_del_rango",
            "cotizacion": None,
            "dias_cotizados": None,
            "semanas": numero(sem),
            "semanas_lic": numero(lic),
            "semanas_sim": numero(sim),
            "semanas_validas": numero(total),
            "administradora": "Colpensiones",
            # Si tiene semanas simultáneas, lo marcamos; si no, es un periodo normal
            "observacion": "simultaneo" if numero(sim) > 0 else "normal",
        })

    # Busca el total de semanas impreso en el documento (línea siguiente al rótulo)
    total_doc = None
    for i, linea in enumerate(lineas):
        if "TOTAL SEMANAS COTIZADAS" in linea:
            # El número puede estar en la misma línea o en las siguientes
            for busca in lineas[i:i + 3]:
                encontrado = re.search(r"([\d\.]+,\d{2})\s*$", busca)
                if encontrado:
                    total_doc = numero(encontrado.group(1))
                    break
            break

    # Arma el JSON final con la estructura del esquema de datos
    resultado = {
        "caso_id": caso["caso_id"],
        "documento": {
            "administradora_emisora": "Colpensiones",
            "regimen": "RPM",
            "formato": "colpensiones_reporte_semanas",
            "fecha_generacion": caso["fecha_generacion"],
        },
        "afiliado": {
            "fecha_nacimiento": caso["fecha_nacimiento"],
            "edad_en_documento": None,
            "sexo": None,  # El reporte de Colpensiones no trae sexo: será pregunta al usuario
            "fecha_afiliacion": caso["fecha_afiliacion"],
            "estado_afiliacion": "activo_cotizante",
        },
        "resumen_documento": {
            "total_semanas": total_doc,
            "total_dias": None,
            "saldo_cuenta_individual": None,
            "semanas_en_otros_fondos": None,
        },
        "periodos": periodos,
    }

    # Escribe el JSON con las tildes bien puestas y formato legible
    caso["salida"].write_text(
        json.dumps(resultado, ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
    print(f"{caso['caso_id']}: {len(periodos)} periodos, total del documento = {total_doc}")


# Procesa los dos casos configurados arriba
for c in CASOS:
    procesar(c)
