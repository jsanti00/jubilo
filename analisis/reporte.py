"""Convierte la bitacora del bot en un informe legible.

Uso:  python3 analisis/reporte.py analisis/datos/estado-20260920.db

Lee la base que se trajo del servidor y escribe un .md al lado, con dos partes:
  1. Los numeros: cuanta gente llego, hasta donde, cuanto tardo, cuanto costo.
  2. Las conversaciones completas, una tras otra, ya sin datos personales.

Ese .md es lo que se abre en una sesion nueva con Claude para iterar el bot: se
lee una sola vez, ya digerido, en vez de andar hurgando en la base.
"""

import datetime
import sqlite3
import sys
from pathlib import Path

# El servidor corre en UTC, asi que las horas vienen cinco adelante de Bogota.
# Se convierten al leerlas, para que el reporte se lea en hora colombiana y no
# haya que restar cinco a mano cada vez.
BOGOTA = datetime.timezone(datetime.timedelta(hours=-5))


def hora_local(ts):
    """Pasa la hora guardada a hora de Bogota, en formato corto y legible."""
    if not ts:
        return "sin hora"
    try:
        return datetime.datetime.fromisoformat(ts).astimezone(BOGOTA).strftime("%Y-%m-%d %H:%M")
    except ValueError:
        return ts[:16]        # si viene en un formato raro, se muestra tal cual


def percentil(valores, p):
    """El valor por debajo del cual queda el p% de los casos.

    El percentil 50 es la mediana (el caso tipico) y el 95 es el caso lento:
    el que sufre uno de cada veinte. El promedio esconde justo a ese.
    """
    if not valores:
        return None
    ordenados = sorted(valores)
    puesto = min(int(len(ordenados) * p / 100), len(ordenados) - 1)
    return ordenados[puesto]


def formato_duracion(ms):
    """Pasa milisegundos a algo que se lea de un vistazo."""
    if ms is None:
        return "sin dato"
    return f"{ms / 1000:.1f} s"


def main():
    if len(sys.argv) < 2:
        print("Uso: python3 analisis/reporte.py <ruta-de-la-base.db>")
        sys.exit(1)

    db = Path(sys.argv[1])
    if not db.exists():
        print(f"No encuentro la base: {db}")
        sys.exit(1)

    con = sqlite3.connect(db)
    con.row_factory = sqlite3.Row

    turnos = con.execute("SELECT * FROM turnos ORDER BY seudonimo, ts").fetchall()
    eventos = con.execute("SELECT * FROM eventos ORDER BY ts").fetchall()
    con.close()

    if not turnos and not eventos:
        print("La bitacora esta vacia: todavia no ha escrito nadie.")
        sys.exit(0)

    lineas = []
    e = lineas.append

    e(f"# Reporte de Júbilo")
    e("")
    e(f"Base leída: `{db.name}`. Todas las horas están en hora de Bogotá.")
    e("")

    # --- El embudo ----------------------------------------------------------
    # Cuánta gente llegó a cada etapa. Es la métrica que importa en esta fase:
    # dónde se cae la gente dice qué hay que arreglar primero.

    def personas_con(evento):
        return {ev["seudonimo"] for ev in eventos if ev["evento"] == evento}

    vieron_aviso = personas_con("aviso_mostrado")
    mandaron_doc = personas_con("documento_recibido")
    con_diagnostico = personas_con("diagnostico_probable")
    escribieron = {t["seudonimo"] for t in turnos}

    e("## El embudo")
    e("")
    e("| Etapa | Personas |")
    e("|---|---|")
    e(f"| Abrieron el bot y vieron el aviso | {len(vieron_aviso)} |")
    e(f"| Escribieron algo después del aviso | {len(escribieron)} |")
    e(f"| Mandaron su historia laboral | {len(mandaron_doc)} |")
    e(f"| Recibieron algo que parece un diagnóstico | {len(con_diagnostico)} |")
    e("")
    e("La última fila es aproximada: se cuenta como diagnóstico toda respuesta "
      "que trae una cifra en pesos y habla de pensión.")
    e("")

    # --- Desempeño ----------------------------------------------------------

    ok = [t for t in turnos if t["resultado"] == "ok"]
    latencias = [t["latencia_ms"] for t in ok if t["latencia_ms"] is not None]
    colas = [t["espera_cola_ms"] for t in turnos if t["espera_cola_ms"] is not None]
    costos = [t["costo_usd"] for t in ok if t["costo_usd"] is not None]

    e("## Desempeño")
    e("")
    e(f"- Turnos totales: **{len(turnos)}** ({len(ok)} bien, {len(turnos) - len(ok)} con problema)")
    e(f"- Tiempo de respuesta típico (p50): **{formato_duracion(percentil(latencias, 50))}**")
    e(f"- Tiempo de respuesta lento (p95): **{formato_duracion(percentil(latencias, 95))}**")
    e(f"- Espera en fila típica (p50): {formato_duracion(percentil(colas, 50))}")
    e(f"- Espera en fila peor (p95): **{formato_duracion(percentil(colas, 95))}**")
    e(f"- Costo total: **US$ {sum(costos):.2f}**")
    if escribieron:
        e(f"- Costo por persona: US$ {sum(costos) / len(escribieron):.2f}")
    if ok:
        e(f"- Costo por turno: US$ {sum(costos) / len(ok):.3f}")
    e("")
    e("La espera en fila es cuánto aguantó la persona antes de que el bot "
      "siquiera empezara a pensar, porque atiende de a uno. Si el p95 se "
      "dispara, ahí está el cuello de botella.")
    e("")

    # --- De dónde sale el gasto de entrada ----------------------------------
    # El total de tokens de entrada no dice nada por sí solo: un token leído de
    # caché cuesta una décima parte de uno fresco. Separarlos es lo que dice si
    # el gasto está en el kit que se relee o en la conversación, y evita
    # optimizar apuntando al lugar equivocado.

    def suma(columna):
        """Suma una columna de los turnos que salieron bien, tolerando vacíos.

        Las bases anteriores al 2026-09-18 no tienen las columnas del desglose,
        así que si no existen se devuelve None y la sección no se imprime.
        """
        if columna not in turnos[0].keys():
            return None
        return sum(t[columna] or 0 for t in ok)

    frescos = suma("tokens_frescos")
    de_cache = suma("tokens_cache")
    cache_creado = suma("tokens_cache_creado")

    if frescos is not None and (frescos + de_cache + cache_creado) > 0:
        total_entrada = frescos + de_cache + cache_creado
        e("## De dónde sale el gasto de entrada")
        e("")
        e("| Tipo de token de entrada | Total | Del total |")
        e("|---|---|---|")
        e(f"| Frescos (se pagan completos cada vez) | {frescos:,} | {frescos / total_entrada:.0%} |")
        e(f"| Leídos de caché (cuestan una décima parte) | {de_cache:,} | {de_cache / total_entrada:.0%} |")
        e(f"| Guardados en caché (cuestan un poco más que uno fresco) | {cache_creado:,} | {cache_creado / total_entrada:.0%} |")
        e("")
        if ok:
            e(f"- Tokens frescos por turno: **{frescos / len(ok):,.0f}**")
            e(f"- Tokens de salida por turno: {(suma('tokens_salida') or 0) / len(ok):,.0f}")
        e("")
        e("Cómo leerlo: si casi todo es caché, el kit no es el problema y el "
          "ahorro está en no llamar al modelo cuando no hace falta. Si los "
          "frescos son altos, el kit se está releyendo entero en cada turno y "
          "ahí sí vale cargarlo por etapas.")
        e("")

    # --- Lo que salió mal ---------------------------------------------------

    problemas = {}
    for t in turnos:
        if t["resultado"] != "ok":
            problemas[t["resultado"]] = problemas.get(t["resultado"], 0) + 1
    for ev in eventos:
        if ev["evento"] == "medio_no_soportado":
            clave = f"mandó {ev['detalle']}"
            problemas[clave] = problemas.get(clave, 0) + 1
        # Cada fuga es un mensaje del CLI que el filtro alcanzo a interceptar
        # antes de que le llegara a la persona. Que no se vea no quiere decir
        # que no pase: es una grieta que hay que ir a tapar en su origen.
        if ev["evento"] == "fuga_cli":
            problemas["se interceptó un mensaje del CLI"] = \
                problemas.get("se interceptó un mensaje del CLI", 0) + 1

    e("## Lo que salió mal")
    e("")
    if problemas:
        for clave, n in sorted(problemas.items(), key=lambda x: -x[1]):
            e(f"- {clave}: {n} {'vez' if n == 1 else 'veces'}")
    else:
        e("Nada. Ningún turno falló.")
    e("")

    # --- Cuánto dura una conversación --------------------------------------

    por_persona = {}
    for t in turnos:
        por_persona.setdefault(t["seudonimo"], []).append(t)

    largos = sorted(len(v) for v in por_persona.values())
    e("## Longitud de las conversaciones")
    e("")
    e(f"- Mediana de mensajes por persona: {percentil(largos, 50)}")
    e(f"- La conversación más larga: {max(largos) if largos else 0} mensajes")
    e(f"- Personas que escribieron una sola vez y no volvieron: "
      f"{sum(1 for n in largos if n == 1)}")
    e("")

    # --- Las conversaciones -------------------------------------------------

    e("---")
    e("")
    e("## Las conversaciones")
    e("")
    e("Ya sin nombres ni cédulas. Cada persona aparece con su etiqueta.")
    e("")

    for persona, sus_turnos in por_persona.items():
        n = len(sus_turnos)
        e(f"### Persona `{persona}` ({n} {'mensaje' if n == 1 else 'mensajes'})")
        e("")
        for t in sus_turnos:
            marca = "" if t["resultado"] == "ok" else f" [{t['resultado']}]"
            adjunto = " (con archivo)" if t["tuvo_adjunto"] else ""
            e(f"**La persona{adjunto}, {hora_local(t['ts'])}{marca}:**")
            e("")
            e("```")
            e((t["texto_usuario"] or "").strip() or "(sin texto)")
            e("```")
            e("")
            if t["respuesta"]:
                e(f"**Júbilo ({formato_duracion(t['latencia_ms'])}):**")
                e("")
                e("```")
                e(t["respuesta"].strip())
                e("```")
                e("")
        e("")

    destino = db.parent / f"reporte-{db.stem}.md"
    destino.write_text("\n".join(lineas), encoding="utf-8")
    print(f"Listo: {destino}")


if __name__ == "__main__":
    main()
