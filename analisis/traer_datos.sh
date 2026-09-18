#!/bin/bash
# Trae la bitácora del bot desde el servidor y arma el reporte para leerlo.
#
# Uso:  ~/Developer/jubilo/analisis/traer_datos.sh
#
# Hace tres cosas y nada más: copia la base del servidor a tu Mac con la fecha
# en el nombre, corre el reporte y lo abre. No toca nada en el servidor: la
# copia se hace sobre una instantánea, así que el bot puede seguir atendiendo
# mientras esto corre.

set -euo pipefail

SERVIDOR="jubilo@128.140.125.112"
CARPETA="$HOME/Developer/jubilo/analisis/datos"
FECHA="$(date +%Y%m%d-%H%M)"
LOCAL="$CARPETA/estado-$FECHA.db"

mkdir -p "$CARPETA"

# Una instantánea consistente de la base. Se usa el propio sqlite del servidor
# (`.backup`) y no una copia con `cp`, porque copiar el archivo mientras el bot
# escribe puede traerlo a medias.
echo "1/3 Sacando una copia limpia de la base en el servidor..."
ssh "$SERVIDOR" "sqlite3 /srv/jubilo/estado.db \".backup '/tmp/jubilo-copia.db'\""

# Antes de que salga del servidor, se le quitan a la copia las cuatro tablas que
# guardan el chat de Telegram de verdad (sesiones, autorizaciones, solicitudes
# y archivos, que lleva la huella de cada documento recibido).
# Esas se quedan alla, que es donde tienen que estar por ley. A tu Mac solo
# viaja la bitacora, que ya viene con seudonimos y sin nombres ni cedulas.
# El VACUUM al final reescribe el archivo, para que lo borrado no quede
# escondido en el espacio libre de la base.
echo "1b/3 Quitandole a la copia los datos que identifican a la gente..."
ssh "$SERVIDOR" "sqlite3 /tmp/jubilo-copia.db \"DELETE FROM sesiones; DELETE FROM autorizaciones; DELETE FROM solicitudes; DROP TABLE IF EXISTS archivos; VACUUM;\""

echo "2/3 Trayendola a tu Mac..."
scp "$SERVIDOR:/tmp/jubilo-copia.db" "$LOCAL"
ssh "$SERVIDOR" "rm -f /tmp/jubilo-copia.db"

echo "3/3 Armando el reporte..."
python3 "$HOME/Developer/jubilo/analisis/reporte.py" "$LOCAL"

# Se abre solo, para no tener que ir a buscarlo.
open "$CARPETA/reporte-estado-$FECHA.md" 2>/dev/null || true

echo "Listo. La base quedo en: $LOCAL"
