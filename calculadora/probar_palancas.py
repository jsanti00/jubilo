# Prueba del director de orquesta de las palancas (palancas.py).
# Uso: python3 probar_palancas.py   (termina en 1 si algo falla)
#
# QUE PROTEGE ESTA PRUEBA. palancas.py no calcula pensiones: decide QUE se le
# ofrece a cada persona, en que orden y con que advertencia. Casi todas esas
# decisiones son de producto y no de matematica, asi que un cambio las puede
# romper sin que ningun numero se vea raro. Cada bloque de abajo corresponde a
# una de esas decisiones, y en el comentario queda escrito por que existe.
#
# La fecha de calculo es fija a proposito: una prueba que dependa de
# date.today() se pone roja sola dentro de unos meses sin que nadie toque el
# codigo, y entonces deja de ser una senal util.

import json
import sys
from datetime import date
from pathlib import Path

import palancas

# Carpeta donde viven los casos reales del set dorado.
CASOS = Path(__file__).parent.parent / "casos"

# La fecha con la que se corre todo. Si se cambia, cambian las cifras.
FECHA = date(2026, 9, 18)

# Los casos del set dorado con los datos que el documento NO trae y que en
# produccion se le preguntan a la persona: (archivo, regimen, sexo, edad).
# El caso 03 solo trae edad y el 06 no trae ni sexo ni fecha de nacimiento, que
# es justo lo que se usa para probar la robustez.
CASO_01 = ("caso-01-porvenir-rais.json", "RAIS", "M", None)
CASO_02 = ("caso-02-skandia-rais.json", "RAIS", "M", None)
CASO_03 = ("caso-03-proteccion-rais.json", "RAIS", "M", 26)
CASO_04 = ("caso-04-colpensiones-rpm.json", "RPM", "M", None)
CASO_05 = ("caso-05-colpensiones-rpm.json", "RPM", "M", None)
CASO_06 = ("caso-06-colfondos-rais.json", "RAIS", None, None)

TODOS = [CASO_01, CASO_02, CASO_03, CASO_04, CASO_05]

fallas = []


def revisar(condicion, descripcion):
    """Anota el resultado de una comprobacion y lo imprime."""
    print(f"  {'OK  ' if condicion else 'FALLA'}  {descripcion}")
    if not condicion:
        fallas.append(descripcion)


def cargar(archivo):
    """Lee un caso del set dorado desde su archivo .json."""
    return json.loads((CASOS / archivo).read_text(encoding="utf-8"))


def correr(config, datos=None, caso=None):
    """Corre el banco de palancas de un caso con la fecha fija de la prueba."""
    archivo, regimen, sexo, edad = config
    caso = caso if caso is not None else cargar(archivo)
    return palancas.calcular(caso, regimen, sexo=sexo, edad=edad,
                             fecha_calculo=FECHA, datos=datos)


def huella(resultado):
    """Convierte un resultado entero en un texto comparable.

    Sirve para preguntar "estos dos resultados son identicos?" sin tener que
    recorrer a mano cada diccionario anidado. `default=str` es para que un dato
    que no sea JSON puro (una fecha, por ejemplo) no tumbe la comparacion.
    """
    return json.dumps(resultado, sort_keys=True, ensure_ascii=False,
                      default=str)


def buscar(lista, clave):
    """Devuelve la primera palanca de la lista con esa clave, o None."""
    return next((p for p in lista if p["clave"] == clave), None)


# ---------------------------------------------------------------------------
# 0. El banco corre en los cinco casos con datos suficientes
# ---------------------------------------------------------------------------
# Antes de mirar invariantes hace falta saber que el flujo completo no revienta
# y que devuelve todas las llaves que el reporte espera. Si falta una llave, el
# que arma el reporte se rompe en produccion y no aqui.

print("=" * 70)
print("0. EL BANCO CORRE Y DEVUELVE LA FORMA COMPLETA")
print("=" * 70)

LLAVES = ("caso_id", "regimen", "fecha_calculo", "base", "mesada_base",
          "palancas", "palancas_todas", "descartadas", "preguntas_pendientes",
          "alternativas_del_segmento", "escenarios", "comparacion_de_regimen",
          "aviso_de_segmento")

resultados = {}
for config in TODOS:
    archivo = config[0]
    r = correr(config)
    resultados[archivo] = r
    print(f"\n{archivo}  ({config[1]})")
    revisar(not r.get("error"), f"{archivo}: corre sin error")
    if r.get("error"):
        continue
    faltantes = [k for k in LLAVES if k not in r]
    revisar(not faltantes, f"{archivo}: no le falta ninguna llave de salida")
    print(f"  mesada base: {palancas.pesos(r['mesada_base'])} | "
          f"{len(r['palancas'])} palancas mostradas | "
          f"{len(r['descartadas'])} descartadas | "
          f"{len(r['escenarios'])} escenarios")
    for p in r["palancas"]:
        efecto = (palancas.pesos(p["efecto_mesada_mes"])
                  if p["efecto_mesada_mes"] is not None else "sin cuantificar")
        print(f"    {p['numero']:>2}. {p['clave']:<22} {efecto:>12}")


# ---------------------------------------------------------------------------
# 1. Determinismo: dos llamadas iguales dan exactamente lo mismo
# ---------------------------------------------------------------------------
# Por que importa tanto. Si el mismo caso da dos respuestas distintas, ninguna
# prueba de las de abajo significa nada, y peor: la persona que vuelve a
# preguntar manana recibe otra cifra y pierde la confianza en todo el reporte.

print("\n" + "=" * 70)
print("1. DETERMINISMO: la misma pregunta da la misma respuesta")
print("=" * 70)

for config in TODOS:
    archivo = config[0]
    primera = huella(resultados[archivo])
    segunda = huella(correr(config))
    revisar(primera == segunda,
            f"{archivo}: dos corridas identicas dan el mismo resultado")

# Y con datos de por medio tambien, que es el camino que mas ramas toca.
con_datos = {"es_independiente": True, "tiene_capacidad_de_pago": True,
             "ingreso_anual": 120000000}
revisar(huella(correr(CASO_01, datos=con_datos))
        == huella(correr(CASO_01, datos=con_datos)),
        "caso-01 con datos del usuario: tambien es determinista")


# ---------------------------------------------------------------------------
# 2. La mesada base sale del escenario que de verdad le aplica
# ---------------------------------------------------------------------------
# A partir de cierta edad la ley va pasando el saldo al fondo conservador
# (la convergencia de multifondos). Cuando eso ya arranco, el escenario real es
# la mezcla obligatoria y NO el moderado. Medir las palancas contra el moderado
# seria medirlas contra un escenario que esa persona no puede escoger.

print("\n" + "=" * 70)
print("2. MESADA BASE: se lee del escenario que de verdad aplica")
print("=" * 70)

# Primero la funcion sola, con diccionarios hechos a mano: es la forma mas
# clara de decir que la regla es "si esta la mezcla, manda la mezcla".
con_mezcla = {"escenarios": {"moderado": {"mesada": 1000},
                             "mezcla_obligatoria_por_edad": {"mesada": 900}}}
sin_mezcla = {"escenarios": {"moderado": {"mesada": 1000},
                             "conservador": {"mesada": 800}}}
revisar(palancas.escenario_aplicable(con_mezcla) == "mezcla_obligatoria_por_edad",
        "con convergencia arrancada, el escenario aplicable es la mezcla")
revisar(palancas.escenario_aplicable(sin_mezcla) == "moderado",
        "sin convergencia, el escenario aplicable es el moderado")
revisar(palancas.mesada_de(con_mezcla, "RAIS") == 900,
        "la mesada se lee de la mezcla (900), no del moderado (1000)")
revisar(palancas.escenario_aplicable({"escenarios": {}}) is None,
        "sin escenarios no se inventa uno: devuelve None")

# Y ahora de punta a punta, con un caso real al que solo se le cambia la fecha
# de nacimiento para que la convergencia ya le haya arrancado. Se toca el dato
# minimo para que todo lo demas siga siendo historia laboral real.
mayor = cargar(CASO_01[0])
mayor["afiliado"]["fecha_nacimiento"] = "1968-01-20"   # 58 anios en 2026
r_mayor = correr(CASO_01, caso=mayor)
escenarios_rais = (palancas._diagnosticar(mayor, "RAIS", "M", None, FECHA)
                   .get("escenarios") or {})
revisar("mezcla_obligatoria_por_edad" in escenarios_rais,
        "el caso de 58 anios si dispara la mezcla obligatoria por edad")
if "mezcla_obligatoria_por_edad" in escenarios_rais:
    esperada = escenarios_rais["mezcla_obligatoria_por_edad"]["mesada"]
    del_moderado = escenarios_rais["moderado"]["mesada"]
    print(f"\n  mezcla: {palancas.pesos(esperada)} | "
          f"moderado: {palancas.pesos(del_moderado)} | "
          f"mesada_base: {palancas.pesos(r_mayor['mesada_base'])}")
    revisar(r_mayor["mesada_base"] == esperada,
            "la mesada base del caso con convergencia sale de la mezcla")
    revisar(r_mayor["mesada_base"] != del_moderado,
            "y no sale del moderado, que es el error facil de cometer")

# A quien la ley ya le paso TODO el saldo al conservador no se le puede ofrecer
# el portafolio de mas riesgo: no es una opcion que tenga.
muy_mayor = cargar(CASO_01[0])
muy_mayor["afiliado"]["fecha_nacimiento"] = "1965-01-20"   # 61 anios en 2026
r_muy_mayor = correr(CASO_01, caso=muy_mayor)
portafolio_61 = buscar(r_muy_mayor["descartadas"], "portafolio")
revisar(portafolio_61 is not None,
        "con convergencia total, la palanca 9 (portafolio) se descarta")
if portafolio_61:
    revisar("convergencia" in (portafolio_61["motivo_no_aplica"] or "").lower(),
            "y el motivo nombra la convergencia de multifondos")


# ---------------------------------------------------------------------------
# 3. Orden por impacto: de mayor a menor, siempre
# ---------------------------------------------------------------------------
# El orden es el mensaje. La primera palanca de la lista es la que la persona
# va a intentar; si ahi va una que mueve poco, el reporte le hizo perder el
# esfuerzo en lo pequeno. Las que no tienen numero se saltan en esta revision
# porque no compiten por impacto (tienen su propio orden fijo).

print("\n" + "=" * 70)
print("3. ORDEN: las palancas con numero van de mayor a menor")
print("=" * 70)

for config in TODOS:
    archivo = config[0]
    r = resultados[archivo]
    for nombre_lista in ("palancas", "palancas_todas"):
        efectos = [p["efecto_mesada_mes"] for p in r[nombre_lista]
                   if p["efecto_mesada_mes"] is not None]
        ordenado = efectos == sorted(efectos, reverse=True)
        revisar(ordenado,
                f"{archivo}: '{nombre_lista}' va de mayor a menor {efectos}")
    # Y las que no tienen numero nunca se cuelan en medio de las que si.
    # Unica excepcion: la 8, que va pegada a la 9 por la regla del bloque 4.
    claves = [p["clave"] for p in r["palancas"] if p["clave"] != "administradora"]
    tiene_numero = [buscar(r["palancas"], c)["efecto_mesada_mes"] is not None
                    for c in claves]
    # sorted(..., reverse=True) sobre booleanos pone los True (con numero)
    # primero: esa es exactamente la forma que debe tener la lista.
    revisar(tiene_numero == sorted(tiene_numero, reverse=True),
            f"{archivo}: las palancas sin numero van al final, no en medio")


# ---------------------------------------------------------------------------
# 4. La palanca 8 (administradora) nunca va antes que la 9 (portafolio)
# ---------------------------------------------------------------------------
# El dato de la Superfinanciera dice que escoger portafolio pesa entre dos y
# diez veces mas que escoger administradora. Mostrarlas al reves invita a la
# persona a optimizar la decision pequena y a ignorar la grande. Ademas la 8
# sin la 9 al lado se lee como "cambiate de AFP", que es justo lo que Jubilo no
# puede decir.

print("\n" + "=" * 70)
print("4. PALANCA 8 SIEMPRE DESPUES DE LA 9, Y PEGADA A ELLA")
print("=" * 70)

for config in TODOS:
    archivo = config[0]
    r = resultados[archivo]
    for nombre_lista in ("palancas", "palancas_todas"):
        claves = [p["clave"] for p in r[nombre_lista]]
        if "administradora" not in claves:
            continue
        if "portafolio" in claves:
            pos_8 = claves.index("administradora")
            pos_9 = claves.index("portafolio")
            revisar(pos_8 > pos_9,
                    f"{archivo}/{nombre_lista}: la 8 va despues de la 9")
            revisar(pos_8 == pos_9 + 1,
                    f"{archivo}/{nombre_lista}: la 8 va pegada a la 9")
        else:
            # La 8 sola, sin la 9 al lado, es exactamente la lectura que el
            # modulo dice que quiere evitar.
            revisar(nombre_lista != "palancas",
                    f"{archivo}: la 8 no aparece huerfana en lo que se muestra")

# El comportamiento tambien se prueba en la funcion que lo garantiza, con una
# lista armada a mano en el peor orden posible.
desordenadas = [{"clave": "administradora"}, {"clave": "subir_sueldo"},
                {"clave": "portafolio"}, {"clave": "aplazar"}]
reordenadas = [p["clave"] for p in
               palancas._administradora_despues_de_portafolio(desordenadas)]
print(f"\n  antes: {[p['clave'] for p in desordenadas]}")
print(f"  despues: {reordenadas}")
revisar(reordenadas.index("administradora") == reordenadas.index("portafolio") + 1,
        "la reordenacion pone la 8 justo debajo de la 9 aunque venga primera")


# ---------------------------------------------------------------------------
# 5. La comparacion de regimen viaja aparte, nunca dentro de "palancas"
# ---------------------------------------------------------------------------
# Corriendo el caso 01 el traslado salio como la palanca de MAYOR impacto. Si
# se ordenara por impacto quedaria de primera, y una palanca de primera con ese
# numero no se lee como "aqui estan los dos escenarios": se lee como
# "trasladese". El traslado casi nunca se puede deshacer y por ley exige doble
# asesoria, asi que Jubilo lo muestra y no lo recomienda.

print("\n" + "=" * 70)
print("5. EL REGIMEN SALE DEL RANKING Y VIAJA EN SU PROPIA LLAVE")
print("=" * 70)

for config in TODOS:
    archivo = config[0]
    r = resultados[archivo]
    revisar(buscar(r["palancas"], "regimen") is None,
            f"{archivo}: el regimen no esta en 'palancas'")
    revisar(buscar(r["palancas_todas"], "regimen") is None,
            f"{archivo}: el regimen tampoco esta en 'palancas_todas'")

# El caso 03 es el que de verdad trae la comparacion calculada: sirve para
# comprobar que cuando existe, existe donde debe y con su advertencia.
r_03 = resultados[CASO_03[0]]
comparacion = r_03["comparacion_de_regimen"]
revisar(comparacion is not None,
        "caso-03: la comparacion de regimen si se calcula y se entrega")
if comparacion:
    print(f"\n  efecto del traslado en caso-03: "
          f"{palancas.pesos(comparacion['efecto_mesada_mes'])} al mes")
    revisar(comparacion["clave"] == "regimen",
            "caso-03: la llave 'comparacion_de_regimen' trae la palanca 4")
    limite = (comparacion["limite_de_alcance"] or "").lower()
    revisar("doble asesor" in limite,
            "caso-03: la comparacion advierte que la ley exige doble asesoria")
    revisar("no recomienda" in limite,
            "caso-03: la comparacion dice explicitamente que no recomienda")
    # Si el traslado hubiera competido por el podio, habria quedado de primero.
    mejor_mostrada = next((p["efecto_mesada_mes"] for p in r_03["palancas"]
                           if p["efecto_mesada_mes"] is not None), 0)
    print(f"  la mejor palanca mostrada mueve "
          f"{palancas.pesos(mejor_mostrada)}: el traslado la superaba")
    revisar(comparacion["efecto_mesada_mes"] > mejor_mostrada,
            "caso-03: el traslado supera a toda palanca y aun asi no compite")

# EL CASO CONTRARIO, que es el que de verdad protege esta regla. En los dos
# casos del RPM trasladarse al RAIS le BAJARIA la mesada. Ese numero es
# informacion valiosa ("quedarse donde esta vale tanto al mes") y tiene que
# llegar igual a 'comparacion_de_regimen'. El umbral de los $20.000 es una
# regla del ranking por impacto, y el regimen no compite en ese ranking: si el
# umbral se lo traga, Jubilo solo muestra la comparacion cuando el traslado
# sale favorable, que es justo el sesgo que el modulo dice querer evitar.
for config in (CASO_04, CASO_05):
    archivo = config[0]
    r = resultados[archivo]
    descartada = buscar(r["descartadas"], "regimen")
    if descartada is not None and descartada["efecto_mesada_mes"] is not None:
        print(f"\n  {archivo}: el traslado movería "
              f"{palancas.pesos(descartada['efecto_mesada_mes'])} al mes")
        print(f"    motivo con el que se descarto: {descartada['motivo_no_aplica']}")
    revisar(r["comparacion_de_regimen"] is not None or descartada is None
            or descartada["efecto_mesada_mes"] is None,
            f"{archivo}: la comparacion de regimen calculada si llega a su llave")
    if descartada is not None:
        revisar("mueve menos" not in (descartada["motivo_no_aplica"] or "").lower(),
                f"{archivo}: al regimen no se le aplica el umbral del ranking")


# ---------------------------------------------------------------------------
# 6. Toda palanca descartada dice por que
# ---------------------------------------------------------------------------
# Descartar en silencio es peor que no evaluar. Si manana alguien pregunta por
# que a esta persona no se le ofrecio sobrecotizar, la respuesta tiene que
# estar escrita en la salida y no en la cabeza de quien programo.

print("\n" + "=" * 70)
print("6. NINGUNA PALANCA SE DESCARTA EN SILENCIO")
print("=" * 70)

for config in TODOS:
    archivo = config[0]
    r = resultados[archivo]
    sin_motivo = [p["clave"] for p in r["descartadas"]
                  if not (p["motivo_no_aplica"] or "").strip()]
    revisar(not sin_motivo,
            f"{archivo}: todas las descartadas traen motivo {sin_motivo or ''}")
    # El motivo lo lee una persona: tiene que ser una frase, no un tecnicismo
    # ni el texto de una excepcion de Python que quedo vacia.
    ilegibles = [p["clave"] for p in r["descartadas"]
                 if (p["motivo_no_aplica"] or "").strip().endswith(": None")
                 or (p["motivo_no_aplica"] or "").strip() == "None"]
    revisar(not ilegibles,
            f"{archivo}: ningun motivo es un error tecnico vacio {ilegibles or ''}")
    # Y una palanca no puede estar en las dos listas a la vez.
    mostradas = {p["clave"] for p in r["palancas"]}
    descartadas = {p["clave"] for p in r["descartadas"]}
    revisar(not (mostradas & descartadas),
            f"{archivo}: ninguna palanca esta mostrada y descartada a la vez")


# ---------------------------------------------------------------------------
# 7. Nada por debajo del umbral ocupa el espacio del reporte
# ---------------------------------------------------------------------------
# No es que el numero pequeno este mal: es que ocupar el lugar mas valioso del
# reporte con una palanca que mueve $8.000 al mes le quita el puesto a una que
# mueve $400.000, y hace que todo se sienta irrelevante.

print("\n" + "=" * 70)
print(f"7. UMBRAL: nada por debajo de "
      f"{palancas.pesos(palancas.UMBRAL_MINIMO_PESOS)} se muestra")
print("=" * 70)

for config in TODOS:
    archivo = config[0]
    r = resultados[archivo]
    pequenas = [(p["clave"], p["efecto_mesada_mes"]) for p in r["palancas"]
                if p["efecto_mesada_mes"] is not None
                and p["efecto_mesada_mes"] < palancas.UMBRAL_MINIMO_PESOS]
    revisar(not pequenas,
            f"{archivo}: ninguna palanca mostrada mueve menos del umbral "
            f"{pequenas or ''}")

# El caso 02 es el que lo dispara de verdad: todas sus palancas mueven menos
# del umbral porque su mesada esta clavada en el piso de la ley.
r_02 = resultados[CASO_02[0]]
bajadas = [p for p in r_02["descartadas"]
           if "mueve menos" in (p["motivo_no_aplica"] or "").lower()]
print(f"\n  caso-02: {len(bajadas)} palancas bajadas por el umbral")
revisar(len(bajadas) >= 1,
        "caso-02: el umbral si baja palancas y deja constancia del motivo")
revisar(all(p["efecto_mesada_mes"] is None
            or p["efecto_mesada_mes"] < palancas.UMBRAL_MINIMO_PESOS
            for p in bajadas),
        "caso-02: las bajadas por umbral de verdad mueven menos que el umbral")


# ---------------------------------------------------------------------------
# 8. Error de segmento: no ofrecerle a alguien lo que no le sirve
# ---------------------------------------------------------------------------
# Ofrecerle aportes voluntarios a quien no tiene con que es tan malo como
# ofrecerle BEPS a quien si tiene. Y a un asalariado no se le pide que suba su
# base de cotizacion, porque su base la fija el salario y no la escoge el.

print("\n" + "=" * 70)
print("8. SEGMENTO: a cada quien lo que si puede hacer")
print("=" * 70)

r_asalariado = correr(CASO_01, datos={"es_independiente": False})
sobrecotizar = (buscar(r_asalariado["descartadas"], "sobrecotizar")
                or buscar(r_asalariado["palancas_todas"], "sobrecotizar"))
revisar(sobrecotizar is not None and not sobrecotizar["aplica"],
        "al asalariado la palanca 6 (sobrecotizar) sale descartada")
if sobrecotizar:
    motivo = (sobrecotizar["motivo_no_aplica"] or "").lower()
    print(f"\n  motivo palanca 6: {sobrecotizar['motivo_no_aplica']}")
    revisar("ibc" in motivo and "salario" in motivo,
            "y el motivo explica que su IBC lo fija el salario")

r_sin_plata = correr(CASO_01, datos={"tiene_capacidad_de_pago": False})
voluntarios = (buscar(r_sin_plata["descartadas"], "aportes_voluntarios")
               or buscar(r_sin_plata["palancas_todas"], "aportes_voluntarios"))
revisar(voluntarios is not None and not voluntarios["aplica"],
        "a quien no le sobra nada, la palanca 5 sale descartada")
if voluntarios:
    motivo = (voluntarios["motivo_no_aplica"] or "").lower()
    print(f"  motivo palanca 5: {voluntarios['motivo_no_aplica']}")
    revisar("segmento" in motivo,
            "y el motivo lo nombra como lo que es: un error de segmento")

# El contraste: al independiente si se le ofrece, y con numero propio.
r_independiente = correr(CASO_01, datos={"es_independiente": True})
sobre_ok = buscar(r_independiente["palancas_todas"], "sobrecotizar")
revisar(sobre_ok is not None and sobre_ok["aplica"],
        "al independiente si se le ofrece la palanca 6")
if sobre_ok:
    revisar(sobre_ok["efecto_mesada_mes"] is not None,
            "y viene cuantificada, no enunciada")
    revisar("cuesta" in (sobre_ok["frase"] or "").lower(),
            "la palanca 6 dice tambien lo que cuesta, no solo lo que rinde")


# ---------------------------------------------------------------------------
# 9. Las preguntas aparecen cuando la palanca se vuelve relevante
# ---------------------------------------------------------------------------
# Decision de Santiago del 2026-09-18: nada de cuestionario al principio. El
# modulo nunca pregunta: devuelve la palanca marcada con el dato que le falta y
# la pregunta exacta, y quien conversa decide cuando hacerla.

print("\n" + "=" * 70)
print("9. PREGUNTAS: se dejan listas, no se hacen de entrada")
print("=" * 70)

r_pelado = resultados[CASO_01[0]]   # sin ningun dato del usuario
for clave, dato in (("aportes_voluntarios", "tiene_capacidad_de_pago"),
                    ("sobrecotizar", "es_independiente")):
    p = (buscar(r_pelado["descartadas"], clave)
         or buscar(r_pelado["palancas_todas"], clave))
    revisar(p is not None and p["requiere_dato"] == dato,
            f"sin datos, la palanca '{clave}' pide '{dato}'")
    revisar(p is not None and bool((p["pregunta"] or "").strip()),
            f"sin datos, la palanca '{clave}' trae la pregunta ya redactada")

pendientes = {q["dato"] for q in r_pelado["preguntas_pendientes"]}
print(f"\n  preguntas pendientes sin datos: {sorted(pendientes)}")
revisar({"tiene_capacidad_de_pago", "es_independiente"} <= pendientes,
        "las dos preguntas aparecen en 'preguntas_pendientes'")
revisar(all(q["pregunta"] and q["para_la_palanca"]
            for q in r_pelado["preguntas_pendientes"]),
        "cada pregunta pendiente dice su texto y para que palanca es")

# Con el dato ya dado, esa pregunta no se vuelve a hacer.
r_con_uno = correr(CASO_01, datos={"es_independiente": True})
revisar("es_independiente" not in
        {q["dato"] for q in r_con_uno["preguntas_pendientes"]},
        "con 'es_independiente' dado, ya no se vuelve a preguntar")

r_con_todo = correr(CASO_01, datos={"es_independiente": True,
                                    "tiene_capacidad_de_pago": True,
                                    "ingreso_anual": 120000000})
faltan = {q["dato"] for q in r_con_todo["preguntas_pendientes"]}
print(f"  preguntas pendientes con todos los datos: {sorted(faltan)}")
revisar(not faltan,
        "con todos los datos dados no queda ninguna pregunta pendiente")


# ---------------------------------------------------------------------------
# 10. Los escenarios van hacia arriba, nunca hacia abajo
# ---------------------------------------------------------------------------
# El reporte viejo le ofrecia "si dejas de cotizar hoy" a alguien de 27 anios.
# Eso no es un escenario, es una amenaza, y no mueve a nadie a hacer nada. Los
# escenarios existen para mostrar a donde se puede llegar.

print("\n" + "=" * 70)
print("10. ESCENARIOS: el primero es el de hoy y los demas van hacia arriba")
print("=" * 70)

PROHIBIDOS = ("dejas de cotizar", "deja de cotizar", "deja_de_cotizar",
              "si te retiras", "peor caso")

for config in TODOS:
    archivo = config[0]
    r = resultados[archivo]
    escenarios = r["escenarios"]
    print(f"\n  {archivo}")
    for e in escenarios:
        print(f"    {e['nombre']:<34} {palancas.pesos(e['mesada'])}")

    revisar(bool(escenarios) and escenarios[0].get("es_base"),
            f"{archivo}: el primer escenario es el caso base")
    base_mesada = escenarios[0]["mesada"]
    peores = [e["nombre"] for e in escenarios
              if e["mesada"] is not None and base_mesada is not None
              and e["mesada"] < base_mesada]
    revisar(not peores,
            f"{archivo}: ningun escenario queda por debajo del base {peores or ''}")

    texto = " ".join((e.get("nombre", "") + " " + e.get("descripcion", "")).lower()
                     for e in escenarios)
    encontrados = [x for x in PROHIBIDOS if x in texto]
    revisar(not encontrados,
            f"{archivo}: ningun escenario es de 'dejas de cotizar' {encontrados or ''}")
    # El escenario base tampoco puede venir con un efecto distinto de cero:
    # es el punto de partida contra el que se miden los demas.
    revisar(escenarios[0].get("efecto_mes") == 0,
            f"{archivo}: el escenario base no se atribuye ninguna mejora")


# ---------------------------------------------------------------------------
# 11. El escenario combinado se calcula de una pasada, no sumando efectos
# ---------------------------------------------------------------------------
# Sueldo, ritmo de cotizacion y aplazamiento son supuestos del mismo motor y su
# efecto conjunto NO es la suma de sus efectos por separado. Sumarlos uno por
# uno daria un numero inflado, y un numero inflado en un reporte de pension es
# una promesa que no se puede cumplir.

print("\n" + "=" * 70)
print("11. LOS ESCENARIOS NO SON LA SUMA DE LAS PALANCAS")
print("=" * 70)

# Que supuesto de la calculadora corresponde a cada palanca.
SUPUESTO_DE = {"densidad_futura": "cerrar_lagunas",
               "meses_aplazamiento": "aplazar",
               "ibc_futuro": "subir_sueldo"}

comprobados = 0
for config in TODOS:
    archivo = config[0]
    r = resultados[archivo]
    efectos = {p["clave"]: p["efecto_mesada_mes"] for p in r["palancas_todas"]}
    for escenario in r["escenarios"]:
        supuestos = escenario.get("supuestos") or {}
        combinadas = [SUPUESTO_DE[s] for s in supuestos if s in SUPUESTO_DE]
        # Con una sola palanca el escenario SI puede coincidir con su efecto:
        # la prueba solo tiene sentido cuando de verdad se combinan dos o mas.
        if len(combinadas) < 2:
            continue
        suma_ingenua = r["mesada_base"] + sum(efectos.get(c) or 0
                                              for c in combinadas)
        real = escenario["mesada"]
        diferencia = real - suma_ingenua
        print(f"\n  {archivo} / {escenario['nombre']}")
        print(f"    combinando {combinadas}")
        print(f"    de una pasada: {palancas.pesos(real)} | "
              f"sumando efectos: {palancas.pesos(suma_ingenua)} | "
              f"diferencia: {palancas.pesos(diferencia)}")
        revisar(real != suma_ingenua,
                f"{archivo}/{escenario['nombre']}: no es la suma de los efectos")
        comprobados += 1

revisar(comprobados >= 1,
        "hay al menos un escenario que de verdad combina dos palancas o mas")


# ---------------------------------------------------------------------------
# 12. Aplazar puede salir negativa, y entonces NO se ofrece
# ---------------------------------------------------------------------------
# El hallazgo que obligo a cambiar el diseno. En el RPM, a quien ya tiene la
# tasa de reemplazo en el tope y a quien le liquidan con el IBL de toda la vida
# (Ley 100 art. 21), cada mes extra cotizando por debajo de su promedio
# historico le BAJA la mesada. Decirle "trabaja un anio mas" la empobrece.

print("\n" + "=" * 70)
print("12. APLAZAR NEGATIVA: se convierte en aviso, no en consejo")
print("=" * 70)

r_04 = resultados[CASO_04[0]]
aplazar_04 = buscar(r_04["descartadas"], "aplazar")
revisar(aplazar_04 is not None,
        "caso-04: la palanca 7 (aplazar) sale en descartadas")
if aplazar_04:
    print(f"\n  efecto a 12 meses: "
          f"{palancas.pesos(aplazar_04['efecto_mesada_mes'])} al mes")
    print(f"  motivo: {aplazar_04['motivo_no_aplica']}")
    revisar(aplazar_04["efecto_mesada_mes"] is not None
            and aplazar_04["efecto_mesada_mes"] < 0,
            "caso-04: el efecto de aplazar es negativo y se conserva el numero")
    motivo = (aplazar_04["motivo_no_aplica"] or "").lower()
    revisar("toda tu vida" in motivo or "toda su vida" in motivo,
            "caso-04: el motivo explica el IBL de toda la vida laboral")
    revisar(buscar(r_04["palancas"], "aplazar") is None,
            "caso-04: y no se le ofrece como palanca en ninguna parte")
    # El detalle de los tres horizontes se guarda igual, para poder auditarlo.
    revisar(len(aplazar_04["detalle"]) == len(palancas.APLAZAMIENTOS),
            "caso-04: se guardan los tres horizontes evaluados aunque no se muestren")

# El contraste: en el caso 05, del mismo regimen, aplazar si sube y si se ofrece.
r_05 = resultados[CASO_05[0]]
aplazar_05 = buscar(r_05["palancas"], "aplazar")
revisar(aplazar_05 is not None and aplazar_05["efecto_mesada_mes"] > 0,
        "caso-05 (mismo regimen): ahi aplazar si sube y si se ofrece")


# ---------------------------------------------------------------------------
# 13. El aviso de la garantia de pension minima
# ---------------------------------------------------------------------------
# A quien su capital no le alcanza para mas que el salario minimo, la mesada se
# la fija un PISO de la ley, y contra un piso no hay palanca que valga. Sin este
# aviso su reporte sale vacio, y un reporte vacio se lee como "no hay nada que
# hacer", que es lo contrario de la verdad: para ella lo que esta en juego no es
# cuanto recibe, es CALIFICAR.

print("\n" + "=" * 70)
print("13. GARANTIA DE PENSION MINIMA: el segmento que hay que nombrar")
print("=" * 70)

aviso_02 = r_02["aviso_de_segmento"]
revisar(aviso_02 is not None,
        "caso-02: se levanta el aviso de segmento")
if aviso_02:
    print(f"\n  {aviso_02['mensaje']}")
    print(f"  LO QUE IMPORTA: {aviso_02['lo_que_de_verdad_importa']}")
    revisar(aviso_02["tipo"] == "garantia_pension_minima",
            "caso-02: el aviso es el de la garantia de pension minima")
    revisar(bool((aviso_02["mensaje"] or "").strip()),
            "caso-02: el aviso trae un mensaje para la persona")
    revisar(bool((aviso_02["lo_que_de_verdad_importa"] or "").strip()),
            "caso-02: y dice cual es la palanca que si le cambia algo")
    revisar(aviso_02["semanas_exigidas"] is not None,
            "caso-02: el aviso trae las semanas que exige la garantia")
    revisar(isinstance(aviso_02["alcanza_el_requisito"], bool),
            "caso-02: el aviso dice si las alcanza o no, sin ambiguedad")
    revisar("fuente" in aviso_02 and aviso_02["fuente"],
            "caso-02: el aviso cita la norma de la que sale")

revisar(resultados[CASO_01[0]]["aviso_de_segmento"] is None,
        "caso-01: a quien no esta en el piso no se le levanta el aviso")
for config in (CASO_04, CASO_05):
    revisar(resultados[config[0]]["aviso_de_segmento"] is None,
            f"{config[0]}: el aviso es del RAIS, no aplica al RPM")


# ---------------------------------------------------------------------------
# 14. Robustez: sin sexo ni fecha de nacimiento se dice, no se inventa
# ---------------------------------------------------------------------------
# La regla del proyecto es que nada se infiere. Un caso incompleto tiene que
# devolver un error explicito que quien conversa pueda convertir en pregunta,
# y no una cifra armada con un supuesto silencioso.

print("\n" + "=" * 70)
print("14. ROBUSTEZ: el caso sin datos devuelve error, no una cifra inventada")
print("=" * 70)

r_06 = correr(CASO_06)
print(f"\n  error devuelto: {r_06.get('error')}")
revisar(bool(r_06.get("error")),
        "caso-06: sin sexo ni fecha de nacimiento devuelve error explicito")
mensaje_06 = (r_06.get("error") or "").lower()
revisar("sexo" in mensaje_06 or "edad" in mensaje_06,
        "caso-06: el error dice cual es el dato que falta")
revisar(r_06.get("palancas") == [] and r_06.get("descartadas") == [],
        "caso-06: no se devuelve ninguna palanca calculada a medias")
revisar(r_06.get("mesada_base") is None,
        "caso-06: no se inventa una mesada base")

# EL SEXO TIENE SU PROPIA SALIDA, y tiene que ser una PREGUNTA y no un error
# criptico. rpm.diagnosticar revienta con un KeyError cuando el sexo viene
# vacio, y un KeyError en produccion es un diagnostico perdido. Los documentos
# del caso 05 y del 06 no traen sexo, asi que este es el camino normal y no el
# raro: la mitad del set dorado pasa por aqui.
for archivo, regimen in (("caso-05-colpensiones-rpm.json", "RPM"),
                         ("caso-06-colfondos-rais.json", "RAIS")):
    caso = cargar(archivo)
    revisar(not caso["afiliado"].get("sexo"),
            f"{archivo}: el documento de verdad no trae el sexo")
    sin_sexo = palancas.calcular(caso, regimen, fecha_calculo=FECHA)
    print(f"\n  {archivo} sin sexo: {sin_sexo.get('error')}")
    revisar("sexo" in (sin_sexo.get("error") or "").lower(),
            f"{archivo}: sin sexo devuelve un error que nombra el sexo")
    revisar(sin_sexo.get("palancas") == [],
            f"{archivo}: sin sexo no se calcula ninguna palanca")
    pedidos = {q["dato"] for q in sin_sexo.get("preguntas_pendientes") or []}
    revisar("sexo" in pedidos,
            f"{archivo}: el sexo queda como pregunta pendiente, lista para usar")
    texto_pregunta = next((q["pregunta"] for q in
                           sin_sexo.get("preguntas_pendientes") or []
                           if q["dato"] == "sexo"), "")
    revisar("?" in (texto_pregunta or ""),
            f"{archivo}: la pregunta por el sexo viene ya redactada")

# Un caso vacio tampoco puede tumbar el modulo.
vacio = {"caso_id": "sintetico-vacio", "documento": {"regimen": "RAIS"},
         "afiliado": {}, "resumen_documento": {}, "periodos": []}
try:
    r_vacio = palancas.calcular(vacio, "RAIS", sexo="M", fecha_calculo=FECHA)
    revisar(bool(r_vacio.get("error")) or r_vacio.get("mesada_base") is not None,
            "un caso sin periodos responde algo coherente y no revienta")
except Exception as error:
    revisar(False, f"un caso sin periodos no deberia reventar: {error}")


# ---------------------------------------------------------------------------
# 15. Ninguna cifra inventada, y ninguna palanca coja
# ---------------------------------------------------------------------------
# La regla del proyecto: una palanca que no se puede cuantificar se nombra sin
# numero, nunca con uno inventado. La palanca 8 (administradora) es la
# excepcion documentada: su efecto en pesos es None A PROPOSITO para que no
# compita de tu a tu con la 9, y su frase habla de rendimientos, no de mesada.

print("\n" + "=" * 70)
print("15. SIN CIFRAS INVENTADAS NI PALANCAS COJAS")
print("=" * 70)

for config in TODOS:
    archivo = config[0]
    r = resultados[archivo]
    for p in r["palancas"]:
        etiqueta = f"{archivo}/{p['clave']}"
        # Toda palanca mostrada le habla a la persona: sin frase no sirve.
        revisar(bool((p["frase"] or "").strip()),
                f"{etiqueta}: la palanca mostrada trae su frase")
        # "sin dato" es lo que imprime el formateador cuando le llega un None:
        # si sale en una frase, es que se colo un hueco a la cara de la persona.
        revisar("sin dato" not in (p["frase"] or "").lower(),
                f"{etiqueta}: la frase no muestra un hueco de dato al usuario")
        if p["efecto_mesada_mes"] is None:
            # Sin efecto en pesos, la frase no puede afirmar un monto en pesos:
            # eso seria exactamente la cifra inventada que la regla prohibe.
            revisar("$" not in (p["frase"] or ""),
                    f"{etiqueta}: sin efecto calculado, la frase no promete pesos")
        else:
            # Con efecto en pesos, el numero tiene que estar redondeado: una
            # mesada con decimales delata que ese numero no paso por el mismo
            # redondeo que los demas y no es comparable con ellos.
            valor = p["efecto_mesada_mes"]
            revisar(float(valor) == float(int(valor)),
                    f"{etiqueta}: el efecto viene redondeado a pesos ({valor})")
        # Toda palanca mostrada dice de donde sale y que supuso.
        revisar(bool((p["fuente"] or "").strip()),
                f"{etiqueta}: la palanca mostrada cita su fuente")

# La excepcion documentada, verificada como tal y no asumida.
admin = buscar(resultados[CASO_01[0]]["palancas"], "administradora")
revisar(admin is not None, "caso-01: la palanca 8 si se muestra")
if admin:
    print(f"\n  palanca 8: {admin['frase']}")
    revisar(admin["efecto_mesada_mes"] is None,
            "la palanca 8 no trae efecto en pesos, a proposito")
    revisar("%" in (admin["frase"] or ""),
            "la palanca 8 habla de rendimientos en porcentaje, no de mesada")
    revisar("$" not in (admin["frase"] or ""),
            "la palanca 8 no promete pesos de mesada")
    revisar(bool((admin["limite_de_alcance"] or "").strip()),
            "la palanca 8 viene con su advertencia de alcance")

# Las palancas que solo aparecen cuando la persona ya dio sus datos pasan por
# el mismo filtro: son las que menos se miran y las que mas facil se cuelan
# con un numero a medio cocinar.
r_completo = correr(CASO_01, datos={"es_independiente": True,
                                    "tiene_capacidad_de_pago": True,
                                    "ingreso_anual": 120000000})
print()
for p in r_completo["palancas"]:
    etiqueta = f"con datos/{p['clave']}"
    revisar("sin dato" not in (p["frase"] or "").lower(),
            f"{etiqueta}: la frase no muestra un hueco de dato al usuario")
    if p["efecto_mesada_mes"] is not None:
        valor = p["efecto_mesada_mes"]
        # Un efecto con decimales delata que ese numero no paso por el mismo
        # redondeo que los demas, y entonces no es comparable con ellos ni se
        # puede ordenar contra ellos con confianza.
        revisar(float(valor) == float(int(valor)),
                f"{etiqueta}: el efecto viene redondeado a pesos ({valor})")


# ---------------------------------------------------------------------------
# 16. Rango de cordura: ninguna cifra absurda pasa sin que nadie la vea
# ---------------------------------------------------------------------------
# EL CASO REAL QUE OBLIGA A ESTA PRUEBA (2026-09-18). La palanca 5 le pasaba
# `rais.extremos()` a una funcion que esperaba FACTORES DE CONVERSION, pero
# esa funcion devuelve TASAS DE INTERES (0,04 y -0,009). Dividir un capital
# entre 0,04 dio una mesada adicional de $6.094 millones al mes. Compilaba,
# corria y no fallaba nada: ninguna prueba de estructura lo habria visto.
# Una prueba de rango si. El tope de 20 veces la mesada base es holgado a
# proposito: no busca afinar, busca que un error de dos ordenes de magnitud no
# llegue nunca a los ojos de una persona.

print("\n" + "=" * 70)
print("16. RANGO DE CORDURA: ninguna palanca se sale de la realidad")
print("=" * 70)

TOPE = 20   # veces la mesada base

def revisar_rango(etiqueta, palanca, mesada_base):
    """Comprueba que el efecto de una palanca no sea absurdo frente a la base."""
    efecto = palanca.get("efecto_mesada_mes")
    if efecto is None or not mesada_base:
        return
    veces = abs(efecto) / mesada_base
    revisar(veces <= TOPE,
            f"{etiqueta}: el efecto es {veces:.1f} veces la mesada base "
            f"({palancas.pesos(efecto)} sobre {palancas.pesos(mesada_base)})")

for config in TODOS:
    archivo = config[0]
    r = resultados[archivo]
    base_mesada = r["mesada_base"]
    revisados = (r["palancas_todas"] + r["descartadas"]
                 + ([r["comparacion_de_regimen"]]
                    if r["comparacion_de_regimen"] else []))
    mayor = max((abs(p["efecto_mesada_mes"]) / base_mesada
                 for p in revisados if p["efecto_mesada_mes"] is not None),
                default=0)
    print(f"\n  {archivo}: la palanca mas grande mueve {mayor:.1f} veces la "
          f"mesada base")
    for p in revisados:
        revisar_rango(f"{archivo}/{p['clave']}", p, base_mesada)
    # Los escenarios combinados pasan por la misma vara.
    for e in r["escenarios"]:
        if e["mesada"] is not None:
            revisar(e["mesada"] <= base_mesada * TOPE,
                    f"{archivo}/escenario '{e['nombre']}': la mesada es creible")

# Y las palancas que solo existen cuando la persona ya dio sus datos, que son
# las menos miradas y por donde se colo el error de los $6.094 millones.
r_datos = correr(CASO_01, datos={"es_independiente": True,
                                 "tiene_capacidad_de_pago": True,
                                 "ingreso_anual": 120000000})
print()
for p in r_datos["palancas_todas"] + r_datos["descartadas"]:
    revisar_rango(f"con datos/{p['clave']}", p, r_datos["mesada_base"])


# ---------------------------------------------------------------------------
# 17. La palanca 2 y la 12 son la misma accion: nunca se muestran las dos
# ---------------------------------------------------------------------------
# Cerrar lagunas (2) y la densidad del ultimo tramo (12) le piden a la persona
# exactamente lo mismo: cotizar todos los meses. Lo que cambia es el argumento.
# Mostrar las dos seria pedir dos veces lo mismo con dos cifras casi iguales, y
# la persona pensaria que se suman. Es la regla MECE aplicada al reporte.

print("\n" + "=" * 70)
print("17. MECE: cotizar todos los meses se pide una sola vez")
print("=" * 70)

for config in TODOS:
    archivo = config[0]
    r = resultados[archivo]
    todas_las_palancas = r["palancas_todas"] + r["descartadas"]
    dos = buscar(todas_las_palancas, "cerrar_lagunas")
    doce = buscar(todas_las_palancas, "densidad_ultimo_tramo")
    ambas = bool(dos and doce and dos["aplica"] and doce["aplica"])
    revisar(not ambas,
            f"{archivo}: la 2 y la 12 nunca aplican las dos a la vez")
    # Y tampoco pueden salir las dos en lo que se muestra.
    mostradas = {p["clave"] for p in r["palancas"]}
    revisar(not {"cerrar_lagunas", "densidad_ultimo_tramo"} <= mostradas,
            f"{archivo}: la 2 y la 12 nunca se muestran juntas")

# El caso 05 es el que dispara la regla: le faltan menos de 10 anios, asi que
# la 12 aplica y la 2 se apaga por ser la misma accion.
r_05_mece = resultados[CASO_05[0]]
todas_05 = r_05_mece["palancas_todas"] + r_05_mece["descartadas"]
dos_05 = buscar(todas_05, "cerrar_lagunas")
doce_05 = buscar(todas_05, "densidad_ultimo_tramo")
revisar(dos_05 is not None and not dos_05["aplica"],
        "caso-05: la palanca 2 se apaga porque la 12 dice lo mismo mejor")
if dos_05:
    print(f"\n  motivo con el que se apaga la 2: {dos_05['motivo_no_aplica']}")
    revisar("misma acción" in (dos_05["motivo_no_aplica"] or "")
            or "misma accion" in (dos_05["motivo_no_aplica"] or ""),
            "caso-05: el motivo dice que son la misma accion, no un tecnicismo")

# LA PRUEBA DE QUE NO HAY DOBLE CONTEO. La 12 mide SOLO la densidad, igual que
# la 2. Si alguien vuelve a meterle el salario (que es lo que mide la palanca
# 1), su efecto se despegaria del de la 2 y las dos cifras se solaparian sin
# que la persona lo sepa. Que sean identicas es justo lo que hay que proteger.
if dos_05 and doce_05:
    print(f"  efecto de la 2:  {palancas.pesos(dos_05['efecto_mesada_mes'])}")
    print(f"  efecto de la 12: {palancas.pesos(doce_05['efecto_mesada_mes'])}")
    revisar(dos_05["efecto_mesada_mes"] == doce_05["efecto_mesada_mes"],
            "caso-05: la 12 mide lo mismo que la 2 (solo densidad, sin salario)")
    revisar(doce_05["efecto_mesada_mes"] == 14501,
            "caso-05: y ese efecto son los $14.501 verificados a mano")
    # Y no puede confundirse con la palanca 1, que es la que mide el salario.
    uno_05 = buscar(todas_05, "subir_sueldo")
    if uno_05 and uno_05["efecto_mesada_mes"] is not None:
        revisar(doce_05["efecto_mesada_mes"] != uno_05["efecto_mesada_mes"],
                "caso-05: la 12 no mide lo mismo que la 1 (el salario)")


# ---------------------------------------------------------------------------
# 18. Los textos se leen como los escribiria una persona
# ---------------------------------------------------------------------------
# Un "1 cosa(s)" en medio de un reporte de pension no es un detalle de estilo:
# delata que el texto lo armo una maquina sin revisar, y quien lo lee le baja
# la confianza a todo lo demas, incluidas las cifras que si estan bien.

print("\n" + "=" * 70)
print("18. TEXTOS: sin plurales de maquina ni guiones largos")
print("=" * 70)

# El tercero es el guion largo, escrito con su codigo y no con el caracter,
# porque la regla del repo es que ese caracter no aparezca en ningun texto.
FEOS = ("(s)", "None", chr(0x2014))

for config in TODOS:
    archivo = config[0]
    r = resultados[archivo]
    revisables = (r["palancas"] + r["descartadas"]
                  + ([r["comparacion_de_regimen"]]
                     if r["comparacion_de_regimen"] else []))
    for p in revisables:
        # Se pegan solo los campos que traen texto: si se pegaran tambien los
        # vacios, la union inventaria espacios dobles que no estan en el texto.
        texto = " | ".join(str(p.get(campo)) for campo in
                           ("frase", "motivo_no_aplica", "supuesto",
                            "limite_de_alcance", "pregunta")
                           if p.get(campo))
        encontrados = [x for x in FEOS if x in texto]
        revisar(not encontrados,
                f"{archivo}/{p['clave']}: el texto no trae restos de maquina "
                f"{encontrados or ''}")
    for e in r["escenarios"]:
        texto = (e.get("nombre") or "") + " " + (e.get("descripcion") or "")
        encontrados = [x for x in FEOS if x in texto]
        revisar(not encontrados,
                f"{archivo}/escenario '{e['nombre']}': texto limpio "
                f"{encontrados or ''}")

# El caso puntual que lo destapo: la palanca 10 contando hallazgos.
p10 = buscar(resultados[CASO_04[0]]["palancas"], "corregir_historia")
if p10:
    print(f"\n  palanca 10: {p10['frase']}")
    revisar("cosa(s)" not in (p10["frase"] or ""),
            "la palanca 10 pluraliza bien, no dice 'cosa(s)'")


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
