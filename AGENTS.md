# AGENTS.md: repo de Júbilo

> **Última actualización:** 2026-09-16. El bot está desplegado en producción y se comparte con los primeros usuarios de prueba.

Júbilo es un asesor pensional para Colombia en Telegram: **la IA conversa y el código fijo hace los números.** Ninguna cifra la calcula el modelo.

Este archivo orienta a cualquier LLM que trabaje en este repo. Léelo antes de actuar.

---

## 1. Qué hay aquí y qué hace cada parte

| Carpeta | Qué es | Quién lo usa |
|---|---|---|
| `calculadora/` | Los números: RPM, RAIS, lagunas, recuperación, costo y retorno. Python puro, sin IA. Cada módulo tiene su `probar_*.py` | Claude la ejecuta, no la reescribe en caliente |
| `kit-contexto/` | Lo que Júbilo sabe y cómo habla. Incluye `system-prompt.md` y `bienvenida-y-aviso.txt` | Claude lo lee en cada conversación |
| `bot/` | El despliegue: `bot.py` (el cartero entre Telegram y Claude), `registro.py` (la bitácora), `jubilo.service` y `deploy_jubilo.sh` | Corre en el VPS, no en el Mac |
| `analisis/` | El ciclo de feedback: `traer_datos.sh` baja la bitácora del servidor y `reporte.py` la vuelve un `.md` legible. La carpeta `datos/` está en el `.gitignore` | Se corre en el Mac después de que la gente use el bot |
| `casos/`, `cobertura/`, `verificacion/` | Casos de prueba y control de cobertura | Validación |
| `cumplimiento/` | Ley 1581 y tratamiento de datos | Marco legal |

**Dónde corre cada cosa:** la calculadora y el kit viven en el repo y se copian al servidor con `git pull`. El `bot.py` vive en `bot/` y se sube con el script de despliegue. El servidor es un VPS de Hetzner; el detalle completo está en la guía de montaje, en el OneDrive de Santiago (`Entrepreneurship (local)/Agentes para consumer tech/Jubilo -  Asesor pensional/V0/despliegue/`).

**Cómo atiende:** hay dos filas. Cada persona tiene la suya (sus mensajes se
responden en orden, nunca dos a la vez, porque retomar la misma conversación de
Claude en paralelo la corrompería) y encima hay un cupo global de `SIMULTANEOS`
conversaciones al tiempo, hoy **2**. Bajar esa constante a 1 devuelve el bot al
comportamiento de una sola fila, sin tocar nada más.

---

## 2. Qué queda registrado de cada conversación

El bot lleva una bitácora en `estado.db`, en dos tablas que crea `bot/registro.py`:

- **`turnos`**: una fila por mensaje. Qué escribió la persona, qué respondió Júbilo, cuánto tardó, cuánto costó en dólares, cuántos tokens, cuánto esperó en fila y si salió bien o mal. Los números salen del JSON que devuelve `claude -p`, no se estiman.
- **`eventos`**: los hitos del embudo. `aviso_mostrado`, `documento_recibido`, `diagnostico_probable`, `medio_no_soportado`, `solicitud_datos`.

**Tres reglas que este registro no puede romper**, porque están escritas en el aviso de privacidad que la gente acepta:

1. En la bitácora **nunca** entra el chat de Telegram: entra un seudónimo con sal (`/srv/jubilo/config/sal.txt`, solo en el servidor). El chat real vive únicamente en `autorizaciones`, que la ley obliga a conservar.
2. Los textos pasan por `registro.redactar()` **dentro** de `anotar_turno`, no en quien la llama. Si se añade un campo de texto nuevo, tiene que pasar por ahí.
3. `analisis/traer_datos.sh` borra `sesiones`, `autorizaciones` y `solicitudes` de la copia **antes** de que salga del servidor. Al Mac solo viaja lo seudonimizado.

Si alguien pide que le borren lo suyo, `registro.borrar_persona(DB, seudonimo)` lo hace. Hoy se corre a mano en el servidor: el seudónimo se saca con `registro.seudonimo(chat_id, sal)`.

**Para leer lo que pasó:** `~/Developer/jubilo/analisis/traer_datos.sh`. Trae la bitácora, arma el `.md` y lo abre. Ese `.md` es lo que se lleva a una sesión nueva con Claude para iterar, en vez de hurgar en la base.

---

## 3. Cómo se prueban los cambios (obligatorio)

**Nunca pruebes un cambio mandándolo al bot de Telegram de producción.** Hay tres niveles y con esos basta:

**Nivel 1, la calculadora: las pruebas automáticas.** Todo cambio en `calculadora/` se valida corriendo las diez suites. Tarda segundos y no toca el servidor:

```bash
cd calculadora
for f in probar_*.py; do printf '%-32s ' $f; python3 -B $f >/tmp/out.txt 2>&1 && tail -1 /tmp/out.txt || { echo 'FALLO'; tail -5 /tmp/out.txt; }; done
```

Todas deben terminar en verde. Si tocas la lógica de un módulo y su prueba no cubre el caso nuevo, **añade el caso a la prueba** antes de dar el cambio por bueno.

**Nivel 1b, la bitácora.** Todo cambio en `bot/registro.py` se valida con su propia prueba, que no necesita servidor ni internet:

```bash
python3 -B bot/probar_registro.py
```

La mitad de sus comprobaciones verifican lo contrario de lo normal: que la cédula, el correo y el nombre **no** lleguen a la base, y que los salarios, las semanas y los años **sí** lleguen. Un filtro que tacha de más deja el reporte inservible. `deploy_jubilo.sh` corre esta prueba solo y se detiene si falla.

**Nivel 2, el kit: conversando en la sesión.** Los cambios de `kit-contexto/` (qué pregunta, cómo responde, qué tono) se prueban aquí mismo con Santiago, leyendo el prompt modificado y razonando la respuesta esperada. No hace falta desplegar para saber si un texto quedó bien.

**No se monta un bot de pruebas por ahora.** Se evaluó y se descartó por complejidad frente al beneficio actual. Se reconsidera cuando haya usuarios reales en volumen.

---

## 4. Desplegar

Solo después de que las pruebas del nivel que corresponda estén en verde.

**Cambios del kit o la calculadora** (van por GitHub):

```bash
git add -A && git commit -m "..." && git push
ssh jubilo@128.140.125.112 'cd /srv/jubilo/jubilo && chmod -R u+w . && git pull && chmod -R a-w . && chmod -R u+w .git && export XDG_RUNTIME_DIR=/run/user/$(id -u) && systemctl --user restart jubilo'
```

**Por qué esos `chmod`.** El repositorio del servidor queda en **solo lectura** entre despliegues, y no es cosmético: Júbilo necesita permiso de escritura para guardar la extracción, y ese permiso el CLI solo lo concede suelto (`Write`), no acotado a una carpeta (se probó, `Write(/ruta/**)` no funciona). El candado de que no pueda tocar la calculadora ni el kit es entonces el sistema de archivos. El `git pull` necesita escribir, así que se abre justo para eso y se vuelve a cerrar. `.git` se deja escribible porque git lo necesita para operar.

**Cambios del `bot.py` o de `registro.py`** (van por el script, que valida, corre la prueba de la bitácora, respalda, sube los dos archivos y reinicia):

```bash
~/Scripts/deploy_jubilo.sh
```

En ambos casos el bot queda caído unos 6 segundos. Si el proceso muere, systemd lo revive en 10.

**`bot/bot.py` y `bot/registro.py` de este repo son la versión oficial.** Si alguna vez se edita directamente en el servidor, hay que traer el cambio de vuelta aquí o se pierde en el siguiente despliegue.

---

## 5. Cuentas y costos (no confundir)

- **En el Mac**, Claude Code corre con la cuenta personal de Santiago (MIT). Es la que se consume trabajando en el código.
- **En el servidor**, corre con `bot.jubilo@gmail.com`, plan **Pro**, sin API key. Es la que consumen los usuarios del bot, y es una sola cuota compartida entre todos.
- Hay que rehacer `/login` en el servidor cada ~11 días. Cuando se vence, el bot avisa por Telegram y le responde a todos que no tiene capacidad.

---

## 6. Reglas al tocar el código

- **La IA nunca calcula.** Si un cambio hace que el modelo estime, redondee o interpole una cifra, está mal. El número sale de `calculadora/`.
- **Comenta todo el código nuevo**, en español, breve y en lenguaje cotidiano: Santiago es principiante en código. Imita el registro de los comentarios que ya existen.
- Comentarios dentro del código sin tildes (así está el resto); los textos que lee el usuario, con tildes.
- **Nunca el guion largo** en ningún texto, ni en código ni en documentos.
- **Nada de lo que entra a la bitácora se guarda sin pasar por el filtro.** Si añades un campo de texto a `turnos` o `eventos`, va por `redactar()` y su caso va a `probar_registro.py`.
- No toques sin pedirlo: el aislamiento por `CLAUDE_CONFIG_DIR`, el enlace de credenciales, `--allowedTools`, `--permission-mode default` ni el candado del aviso de privacidad. Son decisiones de diseño con razones escritas en la guía de montaje.
