# Prueba del detector de anomalías de la historia laboral.
# Uso: python3 -B probar_anomalias.py   (termina en 1 si algo falla)
#
# Esta prueba está escrita al revés de lo normal, y a propósito: la mitad de
# las comprobaciones verifican que el detector NO encuentre nada. En este
# módulo el error caro no es dejar pasar una anomalía, es inventarse una.
# Decirle a alguien "te faltan semanas" cuando no es cierto lo manda a pelear
# con su administradora por algo que está bien, y vuelve sintiéndose engañado.
# Por eso cada tipo de anomalía se prueba dos veces: con un caso que la
# dispara y con el caso legítimo que se le parece y que NO la debe disparar.

import json
import sys
from pathlib import Path

import anomalias
from datos_sistema import SMLMV

CASOS = Path(__file__).parent.parent / "casos"

fallas = []


def revisar(condicion, descripcion):
    """Anota el resultado de una comprobación y lo imprime."""
    print(f"  {'OK  ' if condicion else 'FALLA'}  {descripcion}")
    if not condicion:
        fallas.append(descripcion)


def cargar(ruta):
    return json.loads(Path(ruta).read_text(encoding="utf-8"))


def periodo(desde, hasta, **campos):
    """Arma una fila de historia laboral con todos los campos del esquema.

    Por defecto todo va en None, que es como llegan de verdad los documentos:
    cada administradora llena unas columnas y deja otras vacías.
    """
    fila = {
        "desde": desde, "hasta": hasta,
        "empleador": None, "nit": None, "tipo_cotizante": None,
        "ibc": None, "ibc_tipo": None, "cotizacion": None,
        "dias_cotizados": None, "semanas": None, "semanas_lic": None,
        "semanas_sim": None, "semanas_validas": None,
        "administradora": None, "observacion": "normal",
    }
    fila.update(campos)
    return fila


def caso(periodos, total_semanas=None):
    """Envuelve una lista de periodos en la forma mínima de un caso."""
    return {
        "caso_id": "sintetico",
        "resumen_documento": {"total_semanas": total_semanas},
        "periodos": periodos,
    }


def tipos(deteccion):
    """Lista los tipos de anomalía que salieron, para comparar fácil."""
    return [a["tipo"] for a in deteccion["anomalias"]]


# ---------------------------------------------------------------------------
# 1. Set dorado: el detector corre y no se inventa anomalías donde no las hay
# ---------------------------------------------------------------------------
# Los seis casos son documentos reales ya verificados contra el total impreso
# de cada uno. Los números esperados de abajo se revisaron fila por fila: son
# la línea de base que prueba que un cambio futuro de umbral no empiece a
# levantar alarmas sobre documentos que están bien.

print("=" * 70)
print("1. SET DORADO: qué encuentra en seis documentos reales")
print("=" * 70)

ESPERADO = {
    # caso: (cuántas anomalías, qué tipos, semanas en juego)
    "caso-01-porvenir-rais.json": (0, set(), None),
    "caso-02-skandia-rais.json": (0, set(), None),
    "caso-03-proteccion-rais.json": (0, set(), None),
    # Un mes de 2015 sin cotizar con el mismo empleador antes y después, y una
    # fila de 1999 con salario y cero semanas de la que solo quedan 2 días
    # libres (el resto del mes lo cubrió otro aportante).
    "caso-04-colpensiones-rpm.json": (
        2, {"hueco_corto_mismo_empleador", "ibc_sin_semanas"}, 4.57),
    # Las tres filas de la empresa temporal de 2026 (el "cuarto estado" del
    # kit) más el hueco de dos meses de 1997.
    "caso-05-colpensiones-rpm.json": (
        4, {"hueco_corto_mismo_empleador", "ibc_sin_semanas"}, 12.86),
    # El documento que no cuadra consigo mismo: la tabla suma 407,43 semanas y
    # el encabezado dice 398,0. Está documentado en su nota_verificacion.
    "caso-06-colfondos-rais.json": (
        1, {"descuadre_con_el_total_del_documento"}, None),
}

for archivo in sorted(CASOS.glob("caso-*.json")):
    deteccion = anomalias.detectar(cargar(archivo))
    resumen = anomalias.resumir(deteccion)
    esperado_total, esperado_tipos, esperado_semanas = ESPERADO[archivo.name]
    print(f"\n{archivo.name}")
    print(f"  anomalías: {resumen['total']} "
          f"(alta {resumen['alta']}, media {resumen['media']}, "
          f"baja {resumen['baja']}) | "
          f"semanas en juego: {resumen['semanas_en_juego_total']}")
    for a in deteccion["anomalias"]:
        print(f"    - {a['tipo']} [{a['confianza']}] "
              f"semanas={a['semanas_en_juego']} filas={a['periodos_afectados']}")

    revisar(resumen["total"] == esperado_total,
            f"{archivo.name}: encuentra {esperado_total} anomalías")
    revisar(set(tipos(deteccion)) == esperado_tipos,
            f"{archivo.name}: son de los tipos esperados")
    revisar(deteccion["semanas_en_juego_total"] == esperado_semanas,
            f"{archivo.name}: pone en juego {esperado_semanas} semanas")
    # La salida se guarda y se pasa entre módulos: tiene que ser JSON puro
    try:
        json.dumps(deteccion)
        serializable = True
    except TypeError:
        serializable = False
    revisar(serializable, f"{archivo.name}: la salida se puede guardar como JSON")

# Los tres casos de fondos privados están limpios, y eso es la prueba de fuego
# contra los falsos positivos: son 159 filas reales sin una sola alarma.
limpios = [anomalias.detectar(cargar(CASOS / n))["hay_algo_que_revisar"]
           for n in ("caso-01-porvenir-rais.json", "caso-02-skandia-rais.json",
                     "caso-03-proteccion-rais.json")]
revisar(not any(limpios),
        "los tres documentos de fondos privados no levantan ninguna alarma")


# ---------------------------------------------------------------------------
# 2. Anomalía 1: salario reportado y cero semanas acreditadas
# ---------------------------------------------------------------------------

print("\n" + "=" * 70)
print("2. IBC SIN SEMANAS: dispara, y no dispara donde no debe")
print("=" * 70)

dispara = anomalias.detectar(caso([
    periodo("2025-01-01", "2025-01-31", empleador="ACME", ibc=2_000_000,
            dias_cotizados=30),
    # Mes con salario impreso y cero días: el cuarto estado del kit
    periodo("2025-02-01", "2025-02-28", empleador="ACME", ibc=2_000_000,
            dias_cotizados=0),
]))
revisar("ibc_sin_semanas" in tipos(dispara),
        "una fila con salario y cero días se reporta")
revisar(dispara["anomalias"][0]["semanas_en_juego"] == 4.29,
        "y estima las 4,29 semanas del mes completo que quedó libre")

# Falso positivo 1: el documento ya marcó la fila como simultánea
no_dispara = anomalias.detectar(caso([
    periodo("2025-01-01", "2025-01-31", empleador="ACME", ibc=2_000_000,
            semanas_validas=4.29),
    periodo("2025-01-01", "2025-01-31", empleador="OTRA", ibc=1_000_000,
            semanas_validas=0.0, semanas_sim=4.29, observacion="simultaneo"),
]))
revisar("ibc_sin_semanas" not in tipos(no_dispara),
        "una fila que el documento marcó como simultánea NO se reporta")

# Falso positivo 2: otro empleador llenó el mes, así que no hay nada que ganar
tapado = anomalias.detectar(caso([
    periodo("2025-02-01", "2025-02-28", empleador="ACME", ibc=2_000_000,
            dias_cotizados=30),
    periodo("2025-02-01", "2025-02-28", empleador="OTRA", ibc=900_000,
            dias_cotizados=0),
]))
solo = [a for a in tapado["anomalias"] if a["tipo"] == "ibc_sin_semanas"]
revisar(solo and solo[0]["semanas_en_juego"] == 0.0,
        "si otro aportante ya llenó el mes, no promete ni una semana")
revisar(solo and solo[0]["confianza"] == "baja",
        "y lo dice con confianza baja, no como un hallazgo")

# Falso positivo 3: fila sin días informados (None), que no es lo mismo que cero
sin_dato = anomalias.detectar(caso([
    periodo("2025-01-01", "2025-01-31", empleador="ACME", ibc=2_000_000),
]))
revisar("ibc_sin_semanas" not in tipos(sin_dato),
        "una fila sin dato de días no se trata como fila en ceros")


# ---------------------------------------------------------------------------
# 3. Anomalía 2: días cotizados con el salario en blanco o en cero
# ---------------------------------------------------------------------------

print("\n" + "=" * 70)
print("3. SEMANAS SIN IBC: dispara, y no dispara donde no debe")
print("=" * 70)

dispara = anomalias.detectar(caso([
    periodo("2025-01-01", "2025-01-31", empleador="ACME", ibc=2_000_000,
            dias_cotizados=30),
    periodo("2025-02-01", "2025-02-28", empleador="ACME", ibc=None,
            dias_cotizados=30),
]))
revisar("semanas_sin_ibc" in tipos(dispara),
        "un mes cotizado sin salario reportado se reporta")
hallazgo = [a for a in dispara["anomalias"] if a["tipo"] == "semanas_sin_ibc"][0]
revisar(hallazgo["semanas_en_juego"] is None,
        "sin semanas en juego: las semanas cuentan, lo que se afecta es la mesada")

cero = anomalias.detectar(caso([
    periodo("2025-01-01", "2025-01-31", empleador="ACME", ibc=2_000_000,
            dias_cotizados=30),
    periodo("2025-02-01", "2025-02-28", empleador="ACME", ibc=0,
            dias_cotizados=30),
]))
hallazgo = [a for a in cero["anomalias"] if a["tipo"] == "semanas_sin_ibc"][0]
revisar(hallazgo["confianza"] == "alta",
        "un salario impreso en cero con días cotizados es imposible: confianza alta")

# Falso positivo: un formato que sencillamente no imprime el salario. Si
# ninguna fila lo trae, no hay 200 anomalías, hay otro formato.
sin_columna = anomalias.detectar(caso([
    periodo("2025-01-01", "2025-01-31", empleador="ACME", dias_cotizados=30),
    periodo("2025-02-01", "2025-02-28", empleador="ACME", dias_cotizados=30),
]))
revisar("semanas_sin_ibc" not in tipos(sin_columna),
        "un documento que no imprime salario en NINGUNA fila no genera alarmas")
revisar(any(x["que"] == "semanas_sin_ibc" for x in sin_columna["no_evaluado"]),
        "y se dice claramente que ese detector no se pudo evaluar")


# ---------------------------------------------------------------------------
# 4. Anomalía 3: IBC por debajo del mínimo del año
# ---------------------------------------------------------------------------

print("\n" + "=" * 70)
print("4. IBC BAJO EL MÍNIMO: el prorrateo es lo que evita la masacre")
print("=" * 70)

minimo_2025 = SMLMV[2025]
dispara = anomalias.detectar(caso([
    # Mes completo cotizado sobre la mitad del mínimo: ilegal (Ley 100, art. 18)
    periodo("2025-06-01", "2025-06-30", empleador="ACME",
            ibc=round(minimo_2025 / 2), dias_cotizados=30),
]))
revisar("ibc_bajo_el_minimo" in tipos(dispara),
        "un mes completo cotizado por debajo del mínimo se reporta")
revisar(dispara["anomalias"][0]["confianza"] == "alta",
        "con confianza alta: el mes es completo y la cifra es verificable")

# Falso positivo 1, el grande: mes parcial. Diez días al mínimo son un tercio
# del mínimo mensual, y eso es perfectamente legal.
parcial = anomalias.detectar(caso([
    periodo("2025-06-01", "2025-06-30", empleador="ACME",
            ibc=round(minimo_2025 * 10 / 30), dias_cotizados=10),
]))
revisar("ibc_bajo_el_minimo" not in tipos(parcial),
        "un mes parcial cotizado al mínimo prorrateado NO se reporta")

# Falso positivo 2: dos empleos en el mismo mes, cada uno por medio mínimo.
# Ninguno llega solo, la suma sí, y es lo que exige la norma.
simultaneo = anomalias.detectar(caso([
    periodo("2025-06-01", "2025-06-30", empleador="ACME",
            ibc=round(minimo_2025 * 0.55), dias_cotizados=15),
    periodo("2025-06-01", "2025-06-30", empleador="OTRA",
            ibc=round(minimo_2025 * 0.55), dias_cotizados=15),
]))
revisar("ibc_bajo_el_minimo" not in tipos(simultaneo),
        "dos empleos que juntos llegan al mínimo NO se reportan")

# Falso positivo 3: quedarse un pelo por debajo. El documento redondea y
# prorratea a su manera; por un 3% nadie va a reclamar.
casi = anomalias.detectar(caso([
    periodo("2025-06-01", "2025-06-30", empleador="ACME",
            ibc=round(minimo_2025 * 0.97), dias_cotizados=30),
]))
revisar("ibc_bajo_el_minimo" not in tipos(casi),
        "quedar 3% por debajo del mínimo es redondeo, no anomalía")

# Año sin salario mínimo verificado en la tabla: no se inventa uno
futuro = anomalias.detectar(caso([
    periodo("2035-06-01", "2035-06-30", empleador="ACME", ibc=100,
            dias_cotizados=30),
]))
revisar("ibc_bajo_el_minimo" not in tipos(futuro),
        "sin salario mínimo verificado para ese año, no se compara nada")
revisar(any("ibc_bajo_el_minimo" in x["que"] for x in futuro["no_evaluado"]),
        "y se reporta como no evaluado en vez de callarlo")


# ---------------------------------------------------------------------------
# 5. Anomalía 4: el mismo empleador reportado dos veces sobre el mismo tiempo
# ---------------------------------------------------------------------------

print("\n" + "=" * 70)
print("5. SOLAPAMIENTO: duplicado de verdad contra pago partido")
print("=" * 70)

duplicado = anomalias.detectar(caso([
    periodo("2025-01-01", "2025-01-31", empleador="ACME", nit="900", ibc=2_000_000,
            dias_cotizados=30, administradora="Colpensiones"),
    periodo("2025-01-01", "2025-01-31", empleador="ACME", nit="900", ibc=2_000_000,
            dias_cotizados=30, administradora="Colpensiones"),
]))
hallazgos = [a for a in duplicado["anomalias"]
             if a["tipo"] == "solapamiento_mismo_empleador"]
revisar(len(hallazgos) == 1 and hallazgos[0]["confianza"] == "alta",
        "el mismo renglón repetido exacto se reporta con confianza alta")

tramos = anomalias.detectar(caso([
    periodo("2020-01-01", "2020-12-31", empleador="ACME", nit="900", ibc=2_000_000,
            semanas_validas=52.14, administradora="Colpensiones"),
    periodo("2020-06-01", "2021-03-31", empleador="ACME", nit="900", ibc=2_500_000,
            semanas_validas=43.0, administradora="Colpensiones"),
]))
revisar("solapamiento_mismo_empleador" in tipos(tramos),
        "dos tramos largos del mismo empleador que se pisan se reportan")

# Falso positivo 1, el más frecuente de todos: pagos partidos. Varias filas
# del mismo mes y del mismo empleador son normales (esquema-datos, regla 1).
partido = anomalias.detectar(caso([
    periodo("2025-01-01", "2025-01-31", empleador="ACME", nit="900", ibc=85_738,
            dias_cotizados=2, administradora="Porvenir"),
    periodo("2025-01-01", "2025-01-31", empleador="ACME", nit="900", ibc=3_036_776,
            dias_cotizados=28, administradora="Porvenir"),
]))
revisar("solapamiento_mismo_empleador" not in tipos(partido),
        "dos pagos partidos del mismo mes NO se reportan como duplicado")

# Falso positivo 2: el mismo empleador reportado por dos administradoras es el
# patrón de un traslado de fondo, no un doble registro.
traslado = anomalias.detectar(caso([
    periodo("2020-01-01", "2020-12-31", empleador="ACME", nit="900", ibc=2_000_000,
            semanas_validas=52.14, administradora="Porvenir"),
    periodo("2020-06-01", "2021-03-31", empleador="ACME", nit="900", ibc=2_000_000,
            semanas_validas=43.0, administradora="Protección"),
]))
revisar("solapamiento_mismo_empleador" not in tipos(traslado),
        "un periodo heredado de otra administradora NO se reporta como duplicado")

# Falso positivo 3: dos empleadores distintos en el mismo mes es simultaneidad
dos_empleos = anomalias.detectar(caso([
    periodo("2025-01-01", "2025-01-31", empleador="ACME", ibc=2_000_000,
            dias_cotizados=30),
    periodo("2025-01-01", "2025-01-31", empleador="OTRA", ibc=1_500_000,
            dias_cotizados=30),
]))
revisar("solapamiento_mismo_empleador" not in tipos(dos_empleos),
        "dos empleadores distintos en el mismo mes NO son un solapamiento")


# ---------------------------------------------------------------------------
# 6. Anomalía 5: hueco de uno o dos meses con el mismo empleador a los lados
# ---------------------------------------------------------------------------

print("\n" + "=" * 70)
print("6. HUECO CORTO: mora no registrada contra laguna real")
print("=" * 70)

dispara = anomalias.detectar(caso([
    periodo("2020-01-01", "2020-03-31", empleador="ACME", ibc=2_000_000,
            dias_cotizados=90),
    periodo("2020-05-01", "2020-08-31", empleador="ACME", ibc=2_000_000,
            dias_cotizados=120),
]))
hallazgos = [a for a in dispara["anomalias"]
             if a["tipo"] == "hueco_corto_mismo_empleador"]
revisar(len(hallazgos) == 1,
        "un mes suelto sin cotizar con el mismo empleador a los lados se reporta")
revisar(hallazgos and hallazgos[0]["semanas_en_juego"] == 4.29,
        "y pone en juego las 4,29 semanas de ese mes")
revisar(hallazgos and hallazgos[0]["confianza"] == "media",
        "con confianza media: puede ser mora, pero también una licencia")

# Falso positivo 1: el mes lo cubrió otro empleador. No hay hueco ninguno.
cubierto = anomalias.detectar(caso([
    periodo("2020-01-01", "2020-03-31", empleador="ACME", ibc=2_000_000,
            dias_cotizados=90),
    periodo("2020-04-01", "2020-04-30", empleador="OTRA", ibc=1_000_000,
            dias_cotizados=30),
    periodo("2020-05-01", "2020-08-31", empleador="ACME", ibc=2_000_000,
            dias_cotizados=120),
]))
revisar("hueco_corto_mismo_empleador" not in tipos(cubierto),
        "si otro empleador cubrió el mes, NO se reporta hueco")

# Falso positivo 2: un hueco largo no es mora, es que la persona se fue. Eso
# lo reporta lagunas.py, que es el módulo que habla de huecos.
largo = anomalias.detectar(caso([
    periodo("2020-01-01", "2020-03-31", empleador="ACME", ibc=2_000_000,
            dias_cotizados=90),
    periodo("2021-05-01", "2021-08-31", empleador="ACME", ibc=2_000_000,
            dias_cotizados=120),
]))
revisar("hueco_corto_mismo_empleador" not in tipos(largo),
        "un hueco de un año con el mismo empleador NO se lee como mora")

# Falso positivo 3: sin nombre de empleador no se puede afirmar que sea el
# mismo, así que no se opina (es el caso del formato de Colfondos).
anonimo = anomalias.detectar(caso([
    periodo("2020-01-01", "2020-03-31", ibc=2_000_000, dias_cotizados=90),
    periodo("2020-05-01", "2020-08-31", ibc=2_000_000, dias_cotizados=120),
]))
revisar("hueco_corto_mismo_empleador" not in tipos(anonimo),
        "sin nombre de empleador no se afirma que sea el mismo")


# ---------------------------------------------------------------------------
# 7. Anomalía 6: saltos de IBC inverosímiles
# ---------------------------------------------------------------------------

print("\n" + "=" * 70)
print("7. SALTO DE IBC: un dígito de más contra un aumento de sueldo")
print("=" * 70)

dispara = anomalias.detectar(caso([
    periodo("2024-01-01", "2024-01-31", empleador="ACME", ibc=2_000_000,
            dias_cotizados=30),
    # Un cero de más: 20 millones donde iban 2
    periodo("2024-02-01", "2024-02-29", empleador="ACME", ibc=20_000_000,
            dias_cotizados=30),
]))
revisar("salto_de_ibc_inverosimil" in tipos(dispara),
        "un salto de diez veces entre meses seguidos se reporta")
hallazgo = [a for a in dispara["anomalias"]
            if a["tipo"] == "salto_de_ibc_inverosimil"][0]
revisar(hallazgo["confianza"] == "baja",
        "con confianza baja: también podría ser real, solo hay que mirarlo")
revisar(hallazgo["semanas_en_juego"] is None,
        "y sin semanas en juego: un IBC mal escrito no quita semanas")

# Falso positivo 1: un aumento grande pero verosímil (un ascenso, o un
# independiente que sube su base). El set dorado tiene tres de estos.
aumento = anomalias.detectar(caso([
    periodo("2024-01-01", "2024-01-31", empleador="ACME", ibc=1_000_000,
            dias_cotizados=30),
    periodo("2024-02-01", "2024-02-29", empleador="ACME", ibc=5_000_000,
            dias_cotizados=30),
]))
revisar("salto_de_ibc_inverosimil" not in tipos(aumento),
        "un aumento de cinco veces NO se reporta: pasa en la vida real")

# Falso positivo 2, el que obliga a normalizar: el mes de entrada al empleo
# trae el IBC prorrateado por pocos días. Sin normalizar a mes completo,
# parecería un desplome salarial en todos los documentos.
entrada = anomalias.detectar(caso([
    periodo("2024-01-01", "2024-01-31", empleador="ACME", ibc=400_000,
            dias_cotizados=6),
    periodo("2024-02-01", "2024-02-29", empleador="ACME", ibc=2_000_000,
            dias_cotizados=30),
]))
revisar("salto_de_ibc_inverosimil" not in tipos(entrada),
        "el mes de entrada al empleo NO se lee como salto de salario")

# Falso positivo 3: entre dos empleos separados por años, todo cambio es normal
lejano = anomalias.detectar(caso([
    periodo("2010-01-01", "2010-01-31", empleador="ACME", ibc=500_000,
            dias_cotizados=30),
    periodo("2024-02-01", "2024-02-29", empleador="ACME", ibc=20_000_000,
            dias_cotizados=30),
]))
revisar("salto_de_ibc_inverosimil" not in tipos(lejano),
        "entre meses lejanos no se comparan salarios: eso es la vida")


# ---------------------------------------------------------------------------
# 8. Anomalía 7: el documento no cuadra consigo mismo
# ---------------------------------------------------------------------------

print("\n" + "=" * 70)
print("8. DESCUADRE: la suma de las filas contra el total impreso")
print("=" * 70)

faltan = anomalias.detectar(caso([
    periodo("2024-01-01", "2024-01-31", empleador="ACME", ibc=2_000_000,
            dias_cotizados=30),
], total_semanas=100.0))
hallazgo = [a for a in faltan["anomalias"]
            if a["tipo"] == "descuadre_con_el_total_del_documento"][0]
revisar(hallazgo["semanas_en_juego"] is not None,
        "si el total impreso supera a la tabla, hay semanas de detalle que buscar")
revisar(hallazgo["confianza"] == "alta",
        "una diferencia grande se reporta con confianza alta")

sobran = anomalias.detectar(caso([
    periodo("2024-01-01", "2024-12-31", empleador="ACME", ibc=2_000_000,
            dias_cotizados=360),
], total_semanas=40.0))
hallazgo = [a for a in sobran["anomalias"]
            if a["tipo"] == "descuadre_con_el_total_del_documento"][0]
revisar(hallazgo["semanas_en_juego"] is None,
        "si la tabla suma MÁS que el total impreso, no se prometen semanas")

# Falso positivo 1: diferencias de redondeo. Sumar filas redondeadas a dos
# decimales sobreestima, y en documentos largos eso llega a media semana.
redondeo = anomalias.detectar(caso([
    periodo("2024-01-01", "2024-01-31", empleador="ACME", ibc=2_000_000,
            dias_cotizados=30),
], total_semanas=4.0))
revisar("descuadre_con_el_total_del_documento" not in tipos(redondeo),
        "una diferencia menor a una semana es redondeo, no descuadre")

# Falso positivo 2: sin total impreso no hay nada contra qué comparar
sin_total = anomalias.detectar(caso([
    periodo("2024-01-01", "2024-01-31", empleador="ACME", ibc=2_000_000,
            dias_cotizados=30),
]))
revisar("descuadre_con_el_total_del_documento" not in tipos(sin_total),
        "sin total impreso no se inventa un descuadre")
revisar(any("descuadre" in x["que"] for x in sin_total["no_evaluado"]),
        "y se dice que ese detector no se pudo evaluar")


# ---------------------------------------------------------------------------
# 9. Datos incompletos: el detector aguanta nulls sin reventar y sin inventar
# ---------------------------------------------------------------------------

print("\n" + "=" * 70)
print("9. NULLS Y CASOS DEGENERADOS: aguantar sin inventar")
print("=" * 70)

vacio = anomalias.detectar({"periodos": []})
revisar(vacio["hay_algo_que_revisar"] is False,
        "un caso sin periodos no revienta")
revisar(vacio["semanas_en_juego_total"] is None,
        "y no se inventa un número de semanas")
revisar(len(vacio["no_evaluado"]) >= 1,
        "pero deja claro que no pudo evaluar nada")

revisar(anomalias.detectar({})["hay_algo_que_revisar"] is False,
        "un caso completamente vacío tampoco revienta")

todo_nulo = anomalias.detectar(caso([
    periodo("2024-01-01", "2024-01-31"),
    periodo("2024-02-01", "2024-02-29"),
]))
revisar(todo_nulo["anomalias"] == [],
        "filas con todos los campos en null no generan ninguna anomalía")

sin_fechas = anomalias.detectar(caso([
    {"desde": None, "hasta": None, "empleador": "ACME", "ibc": 2_000_000},
    periodo("2024-01-01", "2024-01-31", empleador="ACME", ibc=2_000_000,
            dias_cotizados=30),
]))
revisar(any(x["que"] == "filas sin fechas" for x in sin_fechas["no_evaluado"]),
        "una fila sin fechas se cuenta aparte en vez de romper el módulo")

# Una fila a la que le falten claves enteras del esquema (extracción a medias)
incompleta = anomalias.detectar({"periodos": [
    {"desde": "2024-01-01", "hasta": "2024-01-31", "ibc": 2_000_000},
]})
revisar(isinstance(incompleta["anomalias"], list),
        "una fila sin la mitad de las claves del esquema no rompe nada")


# ---------------------------------------------------------------------------
# 10. Orden de salida y suma sin doble conteo
# ---------------------------------------------------------------------------

print("\n" + "=" * 70)
print("10. ORDEN Y TOTALES")
print("=" * 70)

mezcla = anomalias.detectar(cargar(CASOS / "caso-05-colpensiones-rpm.json"))
semanas = [a["semanas_en_juego"] or 0 for a in mezcla["anomalias"]]
revisar(semanas == sorted(semanas, reverse=True),
        "las anomalías salen ordenadas por semanas en juego, de mayor a menor")

sin_semanas = [a["confianza"] for a in mezcla["anomalias"]
               if not a["semanas_en_juego"]]
orden = [anomalias.ORDEN_CONFIANZA[c] for c in sin_semanas]
revisar(orden == sorted(orden),
        "y a igual número de semanas, primero las de mayor confianza")

# El mismo mes reclamado por dos hallazgos distintos: un hueco de ACME en
# febrero y, en ese mismo febrero, una fila de OTRA con salario y cero días.
# Los dos apuntan al mismo tiempo vacío, que solo se puede recuperar una vez.
doble = anomalias.detectar(caso([
    periodo("2024-01-01", "2024-01-31", empleador="ACME", ibc=2_000_000,
            dias_cotizados=30),
    periodo("2024-02-01", "2024-02-29", empleador="OTRA", ibc=1_500_000,
            dias_cotizados=0),
    periodo("2024-03-01", "2024-03-31", empleador="ACME", ibc=2_000_000,
            dias_cotizados=30),
]))
suma_ingenua = sum(a["semanas_en_juego"] or 0 for a in doble["anomalias"])
print(f"  suma ingenua: {suma_ingenua} | total sin doble conteo: "
      f"{doble['semanas_en_juego_total']}")
revisar(len(doble["anomalias"]) >= 2,
        "el mismo mes vacío lo reportan dos detectores distintos")
revisar(doble["semanas_en_juego_total"] == 4.29,
        "pero el total cuenta ese mes una sola vez (4,29 semanas, no 8,58)")

# El resumen para el agente tiene que cuadrar con la lista
resumen = anomalias.resumir(doble)
revisar(resumen["total"] == len(doble["anomalias"]),
        "el resumen cuenta las mismas anomalías que la lista")
revisar(resumen["alta"] + resumen["media"] + resumen["baja"] == resumen["total"],
        "y todas las anomalías tienen un nivel de confianza asignado")

# Todo hallazgo tiene que traer las cuatro piezas que el agente necesita para
# hablar: qué es, qué tan seguro, qué verificar y de dónde sale la regla.
completos = all(
    a["tipo"] and a["confianza"] in ("alta", "media", "baja")
    and isinstance(a["periodos_afectados"], list)
    and a["que_verificar"] and a["motivo"]
    for archivo in sorted(CASOS.glob("caso-*.json"))
    for a in anomalias.detectar(cargar(archivo))["anomalias"])
revisar(completos,
        "toda anomalía del set dorado trae tipo, confianza, qué verificar y motivo")

# Y ningún texto puede afirmarle a la persona que hay un error: son cosas por
# verificar. Esta es la regla de producto, comprobada como código.
prohibidas = ("te robaron", "seguro que", "definitivamente", "es un error")
textos = [a["que_verificar"].lower()
          for archivo in sorted(CASOS.glob("caso-*.json"))
          for a in anomalias.detectar(cargar(archivo))["anomalias"]]
revisar(not any(p in t for t in textos for p in prohibidas),
        "ningún texto afirma categóricamente que hay un error")


# ---------------------------------------------------------------------------
# Resultado
# ---------------------------------------------------------------------------

print("\n" + "=" * 70)
if fallas:
    print(f"RESULTADO: {len(fallas)} FALLAS")
    for f in fallas:
        print(f"  - {f}")
    sys.exit(1)
print("RESULTADO: TODO EN VERDE")
print("=" * 70)
