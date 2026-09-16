# AGENTS.md: repo de Júbilo

> **Última actualización:** 2026-09-16. El bot está desplegado en producción desde hoy.

Júbilo es un asesor pensional para Colombia en Telegram: **la IA conversa y el código fijo hace los números.** Ninguna cifra la calcula el modelo.

Este archivo orienta a cualquier LLM que trabaje en este repo. Léelo antes de actuar.

---

## 1. Qué hay aquí y qué hace cada parte

| Carpeta | Qué es | Quién lo usa |
|---|---|---|
| `calculadora/` | Los números: RPM, RAIS, lagunas, recuperación, costo y retorno. Python puro, sin IA. Cada módulo tiene su `probar_*.py` | Claude la ejecuta, no la reescribe en caliente |
| `kit-contexto/` | Lo que Júbilo sabe y cómo habla. Incluye `system-prompt.md` y `bienvenida-y-aviso.txt` | Claude lo lee en cada conversación |
| `bot/` | El despliegue: `bot.py` (el cartero entre Telegram y Claude), `jubilo.service` y `deploy_jubilo.sh` | Corre en el VPS, no en el Mac |
| `casos/`, `cobertura/`, `verificacion/` | Casos de prueba y control de cobertura | Validación |
| `cumplimiento/` | Ley 1581 y tratamiento de datos | Marco legal |

**Dónde corre cada cosa:** la calculadora y el kit viven en el repo y se copian al servidor con `git pull`. El `bot.py` vive en `bot/` y se sube con el script de despliegue. El servidor es un VPS de Hetzner; el detalle completo está en la guía de montaje, en el OneDrive de Santiago (`Entrepreneurship (local)/Agentes para consumer tech/Jubilo -  Asesor pensional/V0/despliegue/`).

---

## 2. Cómo se prueban los cambios (obligatorio)

**Nunca pruebes un cambio mandándolo al bot de Telegram de producción.** Hay dos niveles y con esos dos basta:

**Nivel 1, la calculadora: las pruebas automáticas.** Todo cambio en `calculadora/` se valida corriendo las diez suites. Tarda segundos y no toca el servidor:

```bash
cd calculadora
for f in probar_*.py; do printf '%-32s ' $f; python3 -B $f >/tmp/out.txt 2>&1 && tail -1 /tmp/out.txt || { echo 'FALLO'; tail -5 /tmp/out.txt; }; done
```

Todas deben terminar en verde. Si tocas la lógica de un módulo y su prueba no cubre el caso nuevo, **añade el caso a la prueba** antes de dar el cambio por bueno.

**Nivel 2, el kit: conversando en la sesión.** Los cambios de `kit-contexto/` (qué pregunta, cómo responde, qué tono) se prueban aquí mismo con Santiago, leyendo el prompt modificado y razonando la respuesta esperada. No hace falta desplegar para saber si un texto quedó bien.

**No se monta un bot de pruebas por ahora.** Se evaluó y se descartó por complejidad frente al beneficio actual. Se reconsidera cuando haya usuarios reales en volumen.

---

## 3. Desplegar

Solo después de que las pruebas del nivel que corresponda estén en verde.

**Cambios del kit o la calculadora** (van por GitHub):

```bash
git add -A && git commit -m "..." && git push
ssh jubilo@128.140.125.112 'cd /srv/jubilo/jubilo && git pull && export XDG_RUNTIME_DIR=/run/user/$(id -u) && systemctl --user restart jubilo'
```

**Cambios del `bot.py`** (van por el script, que valida, respalda, sube y reinicia):

```bash
~/Scripts/deploy_jubilo.sh
```

En ambos casos el bot queda caído unos 6 segundos. Si el proceso muere, systemd lo revive en 10.

**`bot/bot.py` de este repo es la versión oficial.** Si alguna vez se edita directamente en el servidor, hay que traer el cambio de vuelta aquí o se pierde en el siguiente despliegue.

---

## 4. Cuentas y costos (no confundir)

- **En el Mac**, Claude Code corre con la cuenta personal de Santiago (MIT). Es la que se consume trabajando en el código.
- **En el servidor**, corre con `bot.jubilo@gmail.com`, plan **Pro**, sin API key. Es la que consumen los usuarios del bot, y es una sola cuota compartida entre todos.
- Hay que rehacer `/login` en el servidor cada ~11 días. Cuando se vence, el bot avisa por Telegram y le responde a todos que no tiene capacidad.

---

## 5. Reglas al tocar el código

- **La IA nunca calcula.** Si un cambio hace que el modelo estime, redondee o interpole una cifra, está mal. El número sale de `calculadora/`.
- **Comenta todo el código nuevo**, en español, breve y en lenguaje cotidiano: Santiago es principiante en código. Imita el registro de los comentarios que ya existen.
- Comentarios dentro del código sin tildes (así está el resto); los textos que lee el usuario, con tildes.
- **Nunca el guion largo** en ningún texto, ni en código ni en documentos.
- No toques sin pedirlo: el aislamiento por `CLAUDE_CONFIG_DIR`, el enlace de credenciales, `--allowedTools`, `--permission-mode default` ni el candado del aviso de privacidad. Son decisiones de diseño con razones escritas en la guía de montaje.
