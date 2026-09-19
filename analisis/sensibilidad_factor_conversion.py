"""
Sensibilidad del factor de conversion de capital a mesada (RAIS).

QUE PREGUNTA RESPONDE, en palabras simples:
En el RAIS la plata ahorrada se convierte en una mesada mensual dividiendola
por un "factor". Ese factor depende de una tasa de interes. Hoy la calculadora
usa dos tasas: el 4% que ordena la norma (tasa de reserva) y una tasa de
mercado que se despeja del precio real de una renta vitalicia. Nadie sabe cual
es la tasa buena, y de esa tasa depende TODO: cuanta mesada sale, a que edad se
puede pensionar anticipadamente y cuanto capital exige el umbral del 110% del
salario minimo. Este script mueve esa tasa en un barrido y mide cuanto se
mueve cada caso del set dorado.

QUE NO HACE: no modifica nada. Ni la calculadora, ni el set dorado, ni el 4%.
Solo lee y mide. La decision sobre que tasa usar es de Santiago.

COMO CORRERLO:
    python3 -B analisis/sensibilidad_factor_conversion.py

Imprime las tablas en pantalla y reescribe analisis/sensibilidad-factor-conversion.md
"""

import json
import sys
from datetime import date
from pathlib import Path

# ---------------------------------------------------------------------------
# De donde sale cada cosa
# ---------------------------------------------------------------------------

# Carpeta raiz del repo (este archivo vive en analisis/)
RAIZ = Path(__file__).resolve().parent.parent
# La calculadora importa sus modulos entre si por nombre suelto (import rpm),
# asi que hay que poner su carpeta en la lista de sitios donde Python busca.
sys.path.insert(0, str(RAIZ / "calculadora"))

import rais                      # noqa: E402  el motor RAIS que vamos a medir
import comparador                # noqa: E402  para simular el saldo de los casos RPM
import datos_sistema as datos    # noqa: E402  las constantes oficiales del sistema

CASOS = RAIZ / "casos"
SALIDA = Path(__file__).resolve().parent / "sensibilidad-factor-conversion.md"

# Fecha fija de calculo, la misma que usan las pruebas, para que el resultado
# sea reproducible y comparable con lo que ya esta liquidado en el repo.
FECHA = date(2026, 7, 18)

# El perfil de fondo sobre el que se lee la mesada. Se usa el moderado porque
# es el que ya usan las pruebas y el comparador como cifra de referencia.
PERFIL = "moderado"


# ---------------------------------------------------------------------------
# Los casos del set dorado (SOLO LECTURA)
# ---------------------------------------------------------------------------
# Cada entrada dice: archivo, si es RAIS de verdad o un contrafactual RPM, y
# los datos que el documento NO trae y en produccion se le preguntan al usuario.
# Esos supuestos quedan escritos aqui a proposito: no se infieren en silencio.
CASOS_A_MEDIR = [
    {"archivo": "caso-01-porvenir-rais.json", "tipo": "RAIS",
     "sexo": None, "edad": None, "nota": "el documento trae sexo y nacimiento"},
    {"archivo": "caso-02-skandia-rais.json", "tipo": "RAIS",
     "sexo": None, "edad": None,
     "nota": "sin saldo en el documento: se usa el piso estimado desde aportes"},
    {"archivo": "caso-03-proteccion-rais.json", "tipo": "RAIS",
     "sexo": "M", "edad": None, "nota": "sexo simulado (el documento no lo trae)"},
    {"archivo": "caso-06-colfondos-rais.json", "tipo": "RAIS",
     "sexo": "M", "edad": 35,
     "nota": "sexo Y edad simulados (el documento no trae ninguno de los dos)"},
    {"archivo": "caso-04-colpensiones-rpm.json", "tipo": "RPM (contrafactual)",
     "sexo": "M", "edad": None,
     "nota": "esta en Colpensiones: el saldo RAIS se simula desde sus salarios"},
    {"archivo": "caso-05-colpensiones-rpm.json", "tipo": "RPM (contrafactual)",
     "sexo": "M", "edad": None,
     "nota": "esta en Colpensiones: el saldo RAIS se simula desde sus salarios"},
]


def cargar(entrada):
    """Lee un caso del set dorado y lo deja listo para el motor RAIS.

    Importante: se lee del disco y se trabaja sobre la copia en memoria. El
    archivo del set dorado NO se toca nunca.
    """
    caso = json.loads((CASOS / entrada["archivo"]).read_text(encoding="utf-8"))
    if entrada["tipo"].startswith("RPM"):
        # Una historia de Colpensiones no trae saldo de cuenta individual,
        # porque en el regimen publico esa cuenta no existe. Para poder medir
        # el factor sobre estos casos se simula cuanto habrian ahorrado si
        # hubieran estado en un fondo privado, con la misma funcion que usa el
        # comparador cuando responde "y si me hubiera trasladado".
        caso["resumen_documento"]["saldo_cuenta_individual"] = (
            comparador.simular_saldo_rais(caso["periodos"], FECHA.year))
    return caso


# ---------------------------------------------------------------------------
# El barrido de tasas
# ---------------------------------------------------------------------------
# NOTA SOBRE EL RANGO. La sugerencia inicial era barrer de 3,0% a 6,0%. Al leer
# el codigo queda claro que ese rango deja por fuera justo la zona donde esta
# el problema: el 4% es el TECHO practico (es la tasa de reserva de la norma, y
# la mas optimista que usa hoy la calculadora), y la tasa que se despeja del
# precio real de mercado esta en 0,28% para hombres y 0,63% para mujeres, e
# incluso en negativo desde 2027 con el Decreto 1485. O sea: la incertidumbre
# vive entre casi cero y 4%, no entre 3% y 6%. El barrido se corre de 0,25% a
# 6,00% en pasos de 0,25 para cubrir la sugerencia original y, sobre todo, la
# zona que de verdad manda.
PASO = 0.0025                      # 0,25 puntos porcentuales
TASAS = [round(PASO * k, 6) for k in range(1, 25)]   # de 0,25% a 6,00%


def parchar_tasa(tasa):
    """Obliga a la calculadora a usar UNA sola tasa en todo el diagnostico.

    El motor RAIS pide sus dos tasas (la optimista y la conservadora) a una
    sola funcion, `rais.extremos`. Reemplazandola por una que devuelve la misma
    tasa en los dos extremos, TODO el diagnostico (mesada, edad de pension
    anticipada y capital del umbral) queda calculado a esa tasa, sin tocar una
    sola linea de rais.py. Es un cambio en memoria que dura lo que dura la
    corrida de este script.
    """
    def extremos_fijos(sexo="M", anio_pension=None):
        return {"optimista": tasa, "conservador": tasa}
    rais.extremos = extremos_fijos


def restaurar_tasa(original):
    """Devuelve la calculadora a su comportamiento normal."""
    rais.extremos = original


def medir(entrada, tasa):
    """Corre un caso a una tasa y devuelve las tres cifras que importan."""
    caso = cargar(entrada)
    parchar_tasa(tasa)
    d = rais.diagnosticar(caso, sexo=entrada["sexo"], edad=entrada["edad"],
                          fecha_calculo=FECHA)
    if "error" in d:
        return None
    escenario = d["escenarios"].get(PERFIL, {})
    # La llave "mesada" sin apellido es el extremo optimista, que con el parche
    # es simplemente la mesada a la tasa que estamos midiendo.
    return {
        "mesada": escenario.get("mesada"),
        "edad_anticipada": d["edad_pension_anticipada"],
        "capital_umbral": (d["capital_umbral_110_pct"] or {}).get("optimista"),
        "edad_hoy": d["edad"],
        "edad_legal": d["edad_legal"],
        "saldo_hoy": d["saldo_hoy"],
        "saldo_es_estimado": d["saldo_es_estimado"],
        "salida": escenario.get("salida"),
    }


# ---------------------------------------------------------------------------
# Utilidades de presentacion
# ---------------------------------------------------------------------------

def pesos(n):
    """Formatea un numero como pesos colombianos: 1750905 -> $1.750.905"""
    if n is None:
        return "n/d"
    return "$" + f"{n:,.0f}".replace(",", ".")


def millones(n):
    """Version corta para las tablas: 17029586 -> 17,0 M"""
    if n is None:
        return "n/d"
    return f"{n / 1e6:,.1f} M".replace(",", "X").replace(".", ",").replace("X", ".")


def pct(t):
    """0.0425 -> '4,25%'"""
    return f"{t * 100:.2f}".replace(".", ",") + "%"


def coma(x, decimales=2):
    """Escribe un decimal a la colombiana: 1.75 -> '1,75'"""
    if x is None:
        return "n/d"
    return f"{x:.{decimales}f}".replace(".", ",")


def anclas(entrada):
    """Corre el caso con la calculadora TAL COMO ESTA HOY, sin parchar nada.

    Sirve de linea base: muestra la banda que el proyecto ya publica (el 4% de
    la norma contra el precio de mercado por sexo y ano), para poder comparar
    el barrido contra el estado actual del codigo.
    """
    caso = cargar(entrada)
    d = rais.diagnosticar(caso, sexo=entrada["sexo"], edad=entrada["edad"],
                          fecha_calculo=FECHA)
    if "error" in d:
        return None
    esc = d["escenarios"].get(PERFIL, {})
    return {
        "mesada_norma": esc.get("mesada"),
        "mesada_mercado": esc.get("mesada_conservadora"),
        "edad_norma": d["edad_pension_anticipada"],
        "edad_mercado": d["edad_pension_anticipada_conservadora"],
        "capital_norma": (d["capital_umbral_110_pct"] or {}).get("optimista"),
        "capital_mercado": (d["capital_umbral_110_pct"] or {}).get("conservador"),
    }


# ---------------------------------------------------------------------------
# Corrida principal
# ---------------------------------------------------------------------------

def main():
    original = rais.extremos          # guardamos la funcion real para devolverla
    resultados = {}                   # {caso_id: {tasa: cifras}}
    fichas = {}                       # datos fijos de cada caso (edad, saldo)
    base = {}                         # la linea base con el codigo sin tocar

    # Primero la linea base, ANTES de parchar nada.
    for entrada in CASOS_A_MEDIR:
        base[entrada["archivo"].replace(".json", "")] = anclas(entrada)

    try:
        for entrada in CASOS_A_MEDIR:
            fila = {}
            for tasa in TASAS:
                fila[tasa] = medir(entrada, tasa)
            clave = entrada["archivo"].replace(".json", "")
            resultados[clave] = fila
            # La ficha del caso se toma de cualquier corrida: no depende de la tasa
            muestra = next(v for v in fila.values() if v)
            # La salida (pension por capital, garantia minima o devolucion)
            # puede CAMBIAR con la tasa: se guarda la del 4% y se marca si
            # cambia en algun punto del barrido.
            salidas = {v["salida"] for v in fila.values() if v}
            fichas[clave] = {
                "tipo": entrada["tipo"],
                "nota": entrada["nota"],
                "edad_hoy": muestra["edad_hoy"],
                "edad_legal": muestra["edad_legal"],
                "saldo_hoy": muestra["saldo_hoy"],
                "saldo_es_estimado": muestra["saldo_es_estimado"],
                "salida": fila[0.04]["salida"] if fila.get(0.04) else muestra["salida"],
                "salida_cambia": len(salidas) > 1,
                "salidas_vistas": sorted(s for s in salidas if s),
            }
    finally:
        # Pase lo que pase, la calculadora queda como estaba
        restaurar_tasa(original)

    escribir_documento(resultados, fichas, base)
    imprimir_resumen(resultados, fichas)


def elasticidad_edad(fila):
    """Cuantos anios de pension anticipada se mueven por cada 0,5 puntos de tasa.

    Se mide de dos maneras, porque las dos dicen cosas distintas:
    - 'promedio': el recorrido total de la edad dividido por el recorrido total
      de la tasa, llevado a 0,5 puntos. Es la pendiente media.
    - 'tramo_critico': lo mismo pero solo entre 0,25% y 4%, que es la banda
      donde de verdad vive la incertidumbre del precio de la renta vitalicia.
    """
    def pendiente(desde, hasta):
        pares = [(t, v["edad_anticipada"]) for t, v in fila.items()
                 if desde <= t <= hasta and v and v["edad_anticipada"] is not None]
        if len(pares) < 2:
            return None
        pares.sort()
        (t0, e0), (t1, e1) = pares[0], pares[-1]
        # Ojo al signo: a MAS tasa, MENOS edad (la pension llega antes). Se
        # reporta como anios ganados por cada medio punto de tasa, en positivo.
        return (e0 - e1) / ((t1 - t0) / 0.005)

    return {"promedio": pendiente(min(TASAS), max(TASAS)),
            "tramo_critico": pendiente(0.0025, 0.04)}


def rango(fila, campo):
    """Devuelve (minimo, maximo) de un campo a lo largo del barrido."""
    valores = [v[campo] for v in fila.values() if v and v[campo] is not None]
    if not valores:
        return (None, None)
    return (min(valores), max(valores))


def escribir_documento(resultados, fichas, base):
    """Arma el .md con las tablas, la elasticidad y el cierre."""
    L = []   # lista de lineas del documento
    A = L.append

    A("# Sensibilidad del factor de conversion de capital a mesada (RAIS)")
    A("")
    A(f"> Generado por `analisis/sensibilidad_factor_conversion.py` el "
      f"{date.today().isoformat()}. Fecha de calculo de todos los casos: "
      f"{FECHA.isoformat()}. Perfil de fondo: {PERFIL}. "
      "Este documento se regenera corriendo el script; no se edita a mano.")
    A("")
    A("## 1. Que se esta midiendo y por que importa")
    A("")
    A("En el RAIS la mesada no sale de una formula sobre el salario: sale de "
      "dividir el capital ahorrado entre un **factor de conversion**, que es el "
      "valor presente de 13 mesadas al ano durante la expectativa de vida. Ese "
      "factor depende por completo de una tasa de descuento, y esa tasa es hoy "
      "el supuesto mas fragil de toda la calculadora.")
    A("")
    A(f"- La calculadora usa hoy **{pct(datos.INTERES_TECNICO)}** como extremo "
      "optimista. No es el precio de una renta vitalicia: es la tasa de "
      "**reserva** que la norma le exige al sistema (Decreto 2555).")
    A(f"- El extremo conservador se despeja del precio observado: "
      f"**{pct(datos.interes_mercado('M', 2026))}** para hombres y "
      f"**{pct(datos.interes_mercado('F', 2026))}** para mujeres en 2026.")
    A(f"- Desde 2027, con el Decreto 1485, el mismo despeje da "
      f"**{pct(datos.interes_mercado('M', 2027))}** para hombres y "
      f"**{pct(datos.interes_mercado('F', 2027))}** para mujeres, o sea tasa "
      "negativa: la renta es tan cara que el capital pierde valor al convertirse.")
    A("")
    A("**Correccion al rango del barrido.** El encargo sugeria barrer de 3,0% a "
      "6,0%. Ese rango es el equivocado: el 4% es el techo practico y el piso "
      "real esta cerca de cero, incluso en negativo. Todo lo que pase de 4% es "
      "zona teorica (ninguna aseguradora vende por debajo de la reserva "
      "matematica). El barrido se corre de 0,25% a 6,00% en pasos de 0,25 para "
      "no perder la sugerencia, pero la lectura util esta entre 0,25% y 4%.")
    A("")

    A("## 2. Los casos medidos")
    A("")
    A("| Caso | Tipo | Edad hoy | Edad legal | Saldo usado | Supuesto declarado |")
    A("|---|---|---|---|---|---|")
    for clave, f in fichas.items():
        marca = " (estimado)" if f["saldo_es_estimado"] else ""
        A(f"| `{clave}` | {f['tipo']} | {f['edad_hoy']} | {f['edad_legal']} | "
          f"{pesos(f['saldo_hoy'])}{marca} | {f['nota']} |")
    A("")
    A("Los dos casos de Colpensiones se miden como **contrafactual**: se les "
      "simula el saldo que tendrian en un fondo privado, con la misma funcion "
      "que usa `comparador.py` para responder la pregunta del traslado. Entran "
      "porque el factor no solo mueve su mesada hipotetica: mueve el **veredicto "
      "de traslado de regimen**, que es una recomendacion con consecuencias "
      "legales.")
    A("")

    A("## 3. Linea base: lo que la calculadora dice hoy, sin tocar nada")
    A("")
    A("Antes del barrido, esto es lo que ya entrega `rais.py` con sus dos "
      "extremos vigentes: el 4% de la norma y el precio de mercado que "
      "corresponde al sexo y al ano de pension de cada caso.")
    A("")
    A("| Caso | Mesada al 4% | Mesada a precio de mercado | Edad anticipada al 4% | "
      "Edad a precio de mercado |")
    A("|---|---|---|---|---|")
    for clave, b in base.items():
        if not b:
            continue
        en = b["edad_norma"] if b["edad_norma"] is not None else "no alcanza"
        em = b["edad_mercado"] if b["edad_mercado"] is not None else "no alcanza"
        A(f"| `{clave}` | {pesos(b['mesada_norma'])} | "
          f"{pesos(b['mesada_mercado'])} | {en} | {em} |")
    A("")

    A("## 4. Resultados del barrido")
    A("")
    for clave, fila in resultados.items():
        f = fichas[clave]
        A(f"### `{clave}` ({f['tipo']})")
        A("")
        A("| Tasa | Mesada proyectada | Edad pension anticipada | Capital umbral 110% |")
        A("|---|---|---|---|")
        for tasa in TASAS:
            v = fila[tasa]
            if not v:
                A(f"| {pct(tasa)} | n/d | n/d | n/d |")
                continue
            marca = ""
            if abs(tasa - datos.INTERES_TECNICO) < 1e-9:
                marca = "  **(el 4% que usa hoy la calculadora)**"
            edad_txt = (str(v["edad_anticipada"]) if v["edad_anticipada"] is not None
                        else f"no alcanza antes de los {f['edad_legal']}")
            A(f"| {pct(tasa)}{marca} | {pesos(v['mesada'])} | {edad_txt} | "
              f"{pesos(v['capital_umbral'])} |")
        A("")
        m_min, m_max = rango(fila, "mesada")
        e_min, e_max = rango(fila, "edad_anticipada")
        c_min, c_max = rango(fila, "capital_umbral")
        if m_min:
            edades = (f"la edad anticipada va de {e_max} a {e_min} anos"
                      if e_min is not None
                      else "no alcanza la pension anticipada a ninguna tasa")
            A(f"**Recorrido completo:** mesada de {pesos(m_min)} a {pesos(m_max)} "
              f"({coma(m_max / m_min)} veces); {edades}; capital del umbral de "
              f"{pesos(c_min)} a {pesos(c_max)}.")
            if f["salida_cambia"]:
                A("")
                A("**Ojo: la salida del RAIS cambia dentro del barrido** "
                  f"({', '.join(f['salidas_vistas'])}). La tasa no solo mueve la "
                  "cifra: mueve en que regla cae la persona.")
        A("")

    A("## 5. Elasticidad: anios de pension por cada 0,5 puntos de tasa")
    A("")
    A("| Caso | Edad anticipada a 0,25% | Edad a 4% (hoy) | Anios en juego | "
      "Anios por cada 0,5 pp (tramo 0,25%-4%) |")
    A("|---|---|---|---|---|")
    elasticidades = {}
    for clave, fila in resultados.items():
        el = elasticidad_edad(fila)
        elasticidades[clave] = el
        baja = fila[0.0025]
        alta = fila[0.04]
        e_baja = baja["edad_anticipada"] if baja else None
        e_alta = alta["edad_anticipada"] if alta else None
        if e_baja is None or e_alta is None:
            juego = "n/d"
        else:
            juego = f"{e_baja - e_alta} anos"
        tramo = (f"{el['tramo_critico']:.2f}".replace(".", ",")
                 if el["tramo_critico"] is not None else "n/d")
        A(f"| `{clave}` | {e_baja if e_baja is not None else 'no alcanza'} | "
          f"{e_alta if e_alta is not None else 'no alcanza'} | {juego} | {tramo} |")
    A("")
    A("La elasticidad **no es constante**: la edad de pension anticipada es una "
      "variable entera (se mueve a saltos de un ano) y depende de cuando el "
      "saldo proyectado cruza el umbral del 110% del salario minimo. En los "
      "casos con mucho capital y mucho tiempo por delante, el cruce es plano y "
      "la tasa lo mueve varios anos; en los casos que ni siquiera alcanzan el "
      "umbral, la tasa no mueve nada porque no hay nada que mover. Cuando un "
      "caso solo alcanza el umbral en parte del tramo, la pendiente se mide "
      "sobre esa parte y no sobre todo el tramo.")
    A("")

    A("## 6. Que casos son mas fragiles al supuesto")
    A("")
    fragiles = []
    for clave, fila in resultados.items():
        m_min, m_max = rango(fila, "mesada")
        e_min, e_max = rango(fila, "edad_anticipada")
        veces = (m_max / m_min) if (m_min and m_max) else None
        anios = (e_max - e_min) if (e_min is not None and e_max is not None) else None
        fragiles.append((clave, veces, anios, fichas[clave]["salida"]))
    # Se ordenan por cuantos anios de pension mueve la tasa, que es el efecto
    # que la persona siente de verdad.
    fragiles.sort(key=lambda x: (-(x[2] or 0), -(x[1] or 0)))
    A("| Caso | Mesada: techo / piso | Anios de pension en juego | Salida del RAIS |")
    A("|---|---|---|---|")
    for clave, veces, anios, salida in fragiles:
        A(f"| `{clave}` | "
          f"{coma(veces) + ' veces' if veces else 'n/d'} | "
          f"{anios if anios is not None else 0} | {salida or 'n/d'} |")
    A("")
    A("**Cuatro patrones, y son MECE entre si:**")
    A("")
    A("1. **Fragiles de verdad: los que se pensionan por capital y aun tienen "
      "horizonte largo.** Su mesada y su edad de pension dependen enteramente "
      "del factor, y como les faltan decadas, cada punto de tasa mueve anos. "
      "Es el perfil del caso estrella.")
    A("2. **Fragiles en el borde: los que quedan pegados al umbral de la "
      "garantia de pension minima.** Su mesada esta clavada en un salario "
      "minimo en la parte baja del barrido y se despega en la parte alta, asi "
      "que la tasa decide si su cifra la pone su ahorro o la pone el Estado.")
    A("3. **Inmunes en la practica: los que terminan en devolucion de saldos.** "
      "La mesada que se les calcula se mueve tanto como la del caso estrella "
      "en proporcion, pero es una cifra teorica: no alcanzan pension, les "
      "devuelven el saldo, y el factor no toca lo que reciben.")
    A("4. **Fragiles en el veredicto, no en la cifra: los contrafactuales de "
      "Colpensiones.** Lo que el factor mueve ahi no es cuanto reciben, es si "
      "el RAIS le gana o le pierde al RPM, que es la comparacion con la que "
      "alguien decide trasladarse.")
    A("")

    A("## 7. So whats")
    A("")
    # El caso estrella del proyecto: el que tiene capital de sobra y 36 anos
    # por delante, o sea donde el supuesto pesa mas.
    estrella = base.get("caso-03-proteccion-rais") or {}
    if estrella.get("mesada_mercado"):
        veces_estrella = estrella["mesada_norma"] / estrella["mesada_mercado"]
    else:
        veces_estrella = None
    A("1. **El rango de incertidumbre es mas ancho que cualquier palanca que le "
      "ofrezcamos a la persona.** En el caso estrella, el factor solo, sin "
      "tocar rendimiento ni aportes, ya abre la mesada "
      f"{coma(veces_estrella)} veces entre los dos extremos vigentes "
      f"({pesos(estrella.get('mesada_mercado'))} contra "
      f"{pesos(estrella.get('mesada_norma'))}). Eso supera con holgura lo que "
      "esa persona gana cambiando de AFP o de perfil de fondo. Mientras el "
      "factor sea un supuesto abierto, presentar palancas finas al lado de la "
      "mesada le da a la cifra una precision que no tiene.")
    A("2. **La edad de pension anticipada no deberia comunicarse como un numero, "
      "y el rango real es mas ancho de lo que el proyecto venia asumiendo.** El "
      "proyecto trabajaba con la idea de que el caso estrella se movia de los 35 "
      f"a los 39 anos. Medido, se mueve de los {estrella.get('edad_norma')} "
      f"(precio de la norma) a los {estrella.get('edad_mercado')} (precio de "
      "mercado), y en el barrido completo cubre once anos. Una persona que oye "
      "'te puedes pensionar a los 36' toma decisiones de vida distintas a la que "
      "oye 'entre los 36 y los 46'. La banda ya esta calculada en el codigo "
      "(`edad_pension_anticipada_banda`): la decision pendiente es si el agente "
      "puede seguir citando el extremo optimista sin apellido.")
    A("3. **La forma de cerrar esto no es elegir mejor la tasa, es conseguir el "
      "dato.** El precio de la renta vitalicia no esta publicado, pero existe: "
      "son las notas tecnicas de las aseguradoras ante la Superfinanciera. "
      "Conseguir dos o tres cotizaciones reales convierte el supuesto mas caro "
      "del proyecto en un dato, y esta medicion dice exactamente cuanto vale "
      "ese esfuerzo.")
    A("")

    SALIDA.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"\nDocumento escrito en: {SALIDA}")


def imprimir_resumen(resultados, fichas):
    """Resumen corto en pantalla, para leer sin abrir el .md"""
    print("\n" + "=" * 72)
    print("SENSIBILIDAD DEL FACTOR DE CONVERSION: RESUMEN")
    print("=" * 72)
    for clave, fila in resultados.items():
        m_min, m_max = rango(fila, "mesada")
        e_min, e_max = rango(fila, "edad_anticipada")
        print(f"\n{clave} ({fichas[clave]['tipo']}, salida: {fichas[clave]['salida']})")
        if m_min:
            print(f"  mesada: {pesos(m_min)} a {pesos(m_max)} "
                  f"({m_max / m_min:.2f} veces)")
        if e_min is not None:
            print(f"  edad anticipada: {e_max} a {e_min} anos "
                  f"({e_max - e_min} anos en juego)")
        else:
            print("  edad anticipada: no alcanza el umbral a ninguna tasa")


if __name__ == "__main__":
    main()
