#!/bin/bash
# Despliega el bot de Júbilo en el VPS y lo reinicia.
#
# Uso:  ~/Scripts/deploy_jubilo.sh [ruta-del-bot.py]
#
# Sin argumento usa el del repo (~/Developer/jubilo/bot/bot.py), que es la
# version oficial. Solo se pasa una ruta distinta para probar algo suelto.
#
# Hace siempre lo mismo y nada más: sube ese archivo como /srv/jubilo/bot.py
# junto con registro.py (el cuaderno de bitácora, que vive a su lado), revisa
# que sean Python válido, reinicia el servicio y confirma que quedó vivo.
# Si algo falla en el camino, se detiene y deja el servidor como estaba.

# "Si cualquier comando falla, para aquí": evita seguir adelante con un error.
set -euo pipefail

# El servidor al que se despliega. Está fijo a propósito: este script solo
# sirve para este servidor, y por eso es seguro darle permiso permanente.
SERVIDOR="jubilo@128.140.125.112"
DESTINO="/srv/jubilo/bot.py"

# El archivo que queremos subir. Si no nos dan ninguno, el del repo.
ORIGEN="${1:-$HOME/Developer/jubilo/bot/bot.py}"

# El cuaderno de bitácora viaja siempre con el bot: son un solo programa
# partido en dos archivos, y desplegar uno sin el otro lo deja roto.
REGISTRO="$(dirname "$ORIGEN")/registro.py"

# Si no nos dieron archivo, o no existe, no hacemos nada.
if [[ -z "$ORIGEN" || ! -f "$ORIGEN" ]]; then
  echo "Error: no encuentro el archivo: $ORIGEN"
  echo "Uso: ~/Scripts/deploy_jubilo.sh [ruta-del-bot.py]"
  exit 1
fi

# Revisión en tu Mac antes de tocar el servidor: que el archivo sea Python
# válido. Así un error de sintaxis nunca llega a producción.
echo "1/5 Revisando que los archivos sean Python valido..."
python3 -c "import ast,sys,pathlib; ast.parse(pathlib.Path(sys.argv[1]).read_text())" "$ORIGEN"
python3 -c "import ast,sys,pathlib; ast.parse(pathlib.Path(sys.argv[1]).read_text())" "$REGISTRO"

# Y que las pruebas del cuaderno de bitácora estén en verde. Si el filtro que
# tacha cédulas se rompió, esto para el despliegue aquí mismo.
echo "1b/5 Corriendo las pruebas del cuaderno de bitacora..."
python3 -B "$(dirname "$ORIGEN")/probar_registro.py" > /dev/null

# Copia de seguridad de la versión que está corriendo ahora mismo, por si hay
# que volver atrás. Se guarda con la fecha y hora en el nombre.
echo "2/5 Guardando copia de la version actual en el servidor..."
ssh "$SERVIDOR" "cp $DESTINO /srv/jubilo/bot.py.anterior-\$(date +%Y%m%d-%H%M%S)"

# Ahora sí, subimos el archivo nuevo.
echo "3/5 Subiendo los archivos..."
scp "$ORIGEN" "$SERVIDOR:$DESTINO"
scp "$REGISTRO" "$SERVIDOR:/srv/jubilo/registro.py"

# Segunda revisión, ya con el intérprete del propio servidor.
echo "4/5 Revisando el archivo ya en el servidor y reiniciando..."
ssh "$SERVIDOR" "/srv/jubilo/venv/bin/python -c \"import ast,pathlib; ast.parse(pathlib.Path('$DESTINO').read_text())\" && export XDG_RUNTIME_DIR=/run/user/\$(id -u) && systemctl --user restart jubilo"

# Esperamos unos segundos y confirmamos que el bot quedó vivo de verdad.
echo "5/5 Confirmando que quedo corriendo..."
sleep 6
ssh "$SERVIDOR" "export XDG_RUNTIME_DIR=/run/user/\$(id -u); systemctl --user is-active jubilo; echo '--- ultimas lineas del log ---'; tail -3 /srv/jubilo/bot.log"

echo "Listo. Si arriba dice 'active', el bot esta corriendo con la version nueva."
