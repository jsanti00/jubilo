#!/bin/bash
# Recaptura la calculadora de IBC de la UGPP y avisa si los coeficientes de
# presunción de costos cambiaron respecto de la última captura archivada.
#
# Por qué existe: el coeficiente de rentas de capital (28,08%) define el IBC de
# todo el segmento rentista, y la UGPP lo puede cambiar sin avisar. La captura
# del 2026-09-16 cerró dos marcas [VERIFICAR] del kit; si el número cambia y
# nadie se da cuenta, el kit queda dando una cifra falsa con cara de verificada.
#
# Cuándo correrlo:
#   - antes de construir o modificar calculadora/ibc_rentista.py
#   - en cada revisión anual del kit
#   - cuando salga noticia de una resolución nueva de la UGPP
#
# Qué hace: guarda una captura NUEVA con la fecha de hoy (nunca reemplaza la
# anterior, para conservar la serie histórica) y compara el renglón de rentistas
# contra la captura más reciente que ya estaba archivada.
#
# Uso:  bash verificacion/recapturar-calculadora-ugpp.sh

set -euo pipefail

URL="https://www.ugpp.gov.co/calculadora-ibc"
# Carpeta de evidencia, calculada desde la ubicación de este script
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/evidencia"
HOY="$(date +%Y-%m-%d)"
NUEVA="$DIR/$HOY-ugpp-calculadora-ibc.html"

# La captura anterior es la más reciente que ya exista, excluyendo la de hoy
ANTERIOR="$(ls -1 "$DIR"/*-ugpp-calculadora-ibc.html 2>/dev/null | grep -v "$HOY" | tail -1 || true)"

if [ -f "$NUEVA" ]; then
  echo "Ya existe una captura de hoy: $(basename "$NUEVA")"
  echo "Bórrala a mano si quieres rehacerla. No se sobrescribe sola."
  exit 0
fi

echo "Descargando $URL ..."
curl -sfL -A "Mozilla/5.0" "$URL" -o "$NUEVA"

# Extrae el porcentaje del renglón de rentistas del HTML recién bajado
extraer_rentista() {
  grep -o 'data-porcent="[^"]*"[^>]*>[^<]*Rentistas de Capital[^<]*' "$1" \
    | grep -o 'data-porcent="[^"]*"' | head -1 | cut -d'"' -f2
}

NUEVO_PCT="$(extraer_rentista "$NUEVA" || true)"

if [ -z "$NUEVO_PCT" ]; then
  echo
  echo "AVISO: no encontré el renglón de rentistas en la captura nueva."
  echo "La UGPP pudo cambiar la estructura de la página. Revisar a mano:"
  echo "  $NUEVA"
  exit 1
fi

echo "Captura guardada: $(basename "$NUEVA")"
echo "sha256: $(shasum -a 256 "$NUEVA" | cut -d' ' -f1)"
echo "Coeficiente de rentistas de capital hoy: $NUEVO_PCT%"

if [ -z "$ANTERIOR" ]; then
  echo "No hay captura anterior con la que comparar. Esta queda como la primera."
  exit 0
fi

VIEJO_PCT="$(extraer_rentista "$ANTERIOR" || true)"
echo "Coeficiente en $(basename "$ANTERIOR"): $VIEJO_PCT%"
echo

if [ "$NUEVO_PCT" = "$VIEJO_PCT" ]; then
  echo "SIN CAMBIOS en el renglón de rentistas. El kit sigue vigente."
  echo "Conviene igual revisar el diff completo, porque otros renglones o la"
  echo "fórmula pueden haber cambiado:"
  echo "  diff <(grep -o 'data-porcent=\"[^\"]*\"' \"$ANTERIOR\") <(grep -o 'data-porcent=\"[^\"]*\"' \"$NUEVA\")"
else
  echo "*** EL COEFICIENTE CAMBIÓ: de $VIEJO_PCT% a $NUEVO_PCT% ***"
  echo
  echo "Hay que actualizar, en este orden:"
  echo "  1. kit-contexto/rentista-de-capital.md  s.5 y s.6"
  echo "  2. kit-contexto/independientes.md       s.2 bis (tabla completa) y s.3"
  echo "  3. kit-contexto/costo-de-cotizar.md     fila del rentista"
  echo "  4. calculadora/ibc_rentista.py          si ya existe, y sus pruebas"
  echo "  5. verificacion/  una ficha nueva con la fecha de hoy, sin borrar la vieja"
fi
