# AGENTS.md: repo de Júbilo

> **Última actualización:** 2026-09-19 (segunda entrada del día). Cambio: **el usuario ya pensionado quedó fuera del alcance del producto y se borró todo lo que lo contemplaba.** Lo que se movió: **el mensaje de bienvenida se dejó como estaba** (Santiago lo decidió así: se probó reescribirlo y se revirtió, el aviso sigue en la **versión 1.2**); el `system-prompt.md` trae ahora el mensaje de cierre palabra por palabra; y la matriz de cobertura perdió sus 16 celdas PEN, así que el universo pasó de 64 a **48 celdas**. **Ojo con la distinción:** "ya pensionado" está fuera; "no alcanza a pensionarse" sigue dentro y es un usuario al que hay que decirle la verdad. Nada de esto está desplegado todavía.
>
> **Antes:** 2026-09-19. Cambio: se construyó el **banco de palancas** (`analisis/palancas-por-construir.md`). Lo nuevo: `calculadora/palancas.py` (elige, cuantifica, ordena y combina las palancas de cada persona), `calculadora/anomalias.py` (detecta lo que hay que verificar en la historia laboral), el parámetro `meses_aplazamiento` en `rpm.py` y `rais.py`, la tabla de rendimiento por AFP y fondo en `datos_sistema.py`, y las secciones 4 y 5 del reporte conectadas a todo eso. **Nada de eso está desplegado todavía.** Antes: 2026-09-18, se ejecutaron las mejoras del primer feedback real: la carpeta `tramites/`, la prueba `bot/probar_bot.py`, la convergencia de multifondos y el aviso de privacidad en versión 1.2. Antes: 2026-09-16, el bot se desplegó en producción y se compartió con los primeros usuarios de prueba.

Júbilo es un asesor pensional para Colombia en Telegram: **la IA conversa y el código fijo hace los números.** Ninguna cifra la calcula el modelo.

Este archivo orienta a cualquier LLM que trabaje en este repo. Léelo antes de actuar.

---

## 1. Qué hay aquí y qué hace cada parte

| Carpeta | Qué es | Quién lo usa |
|---|---|---|
| `calculadora/` | Los números: RPM, RAIS, lagunas, recuperación, costo y retorno, y el **banco de palancas**. Python puro, sin IA. Cada módulo tiene su `probar_*.py` | Claude la ejecuta, no la reescribe en caliente |
| `kit-contexto/` | Lo que Júbilo sabe y cómo habla. Incluye `system-prompt.md` y `bienvenida-y-aviso.txt` | Claude lo lee en cada conversación |
| `bot/` | El despliegue: `bot.py` (el cartero entre Telegram y Claude), `registro.py` (la bitácora), `jubilo.service`, `deploy_jubilo.sh` y `verificar_servidor.py` (comprueba la máquina antes de subir nada). Sus dos pruebas, `probar_registro.py` y `probar_bot.py`, corren en el Mac sin servidor | Corre en el VPS, no en el Mac |
| `tramites/` | **Lo único del repo que toca internet EN CONVERSACIÓN**, o sea lo único que Júbilo puede ejecutar mientras atiende a alguien. (El otro que descarga es `analisis/rendimiento_afp.py`, pero lo corre Santiago a mano en el Mac para refrescar una tabla de datos, nunca el agente.) Hoy solo `pedir_historia.py`, que le pide a Colpensiones que le mande la historia laboral al correo de la persona. Vive aparte a propósito: el cerebro del agente sigue sin internet y solo ejecuta esto como una herramienta determinista, igual que la calculadora | Claude lo ejecuta, con `--allowedTools` |
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

**Nunca pruebes un cambio mandándolo al bot de Telegram de producción.** Hay tres niveles y con esos basta.

**Cuántas suites hay, sin tener que creerle a este archivo.** Hoy son **18**: catorce en `calculadora/`, dos en `bot/`, una en `reporte/` y una en `tramites/`. Ese número crece, así que en vez de fiarte de él, cuéntalas y córrelas todas de una:

```bash
cd ~/Developer/jubilo
for f in calculadora/probar_*.py bot/probar_*.py reporte/probar_*.py tramites/probar_*.py; do
  printf '%-40s ' "$f"; python3 -B "$f" >/tmp/o.txt 2>&1 && echo OK || { echo FALLO; tail -5 /tmp/o.txt; }
done
```

Todas tienen que decir OK. Ninguna necesita servidor ni internet.


**Nivel 1, la calculadora: las pruebas automáticas.** Todo cambio en `calculadora/` se valida corriendo las **catorce** suites (eran once hasta el 2026-09-19; se sumaron `probar_palancas.py`, `probar_anomalias.py` y `probar_extraer.py`). Tarda segundos y no toca el servidor:

```bash
cd calculadora
for f in probar_*.py; do printf '%-32s ' $f; python3 -B $f >/tmp/out.txt 2>&1 && tail -1 /tmp/out.txt || { echo 'FALLO'; tail -5 /tmp/out.txt; }; done
```

Todas deben terminar en verde. Si tocas la lógica de un módulo y su prueba no cubre el caso nuevo, **añade el caso a la prueba** antes de dar el cambio por bueno.

**Nivel 1b, la bitácora y el bot.** Todo cambio en `bot/registro.py` o en `bot/bot.py` se valida con sus dos pruebas, que no necesitan servidor ni internet:

```bash
python3 -B bot/probar_registro.py
python3 -B bot/probar_bot.py
```

La segunda cubre las tres defensas que se añadieron el 2026-09-18: el filtro que impide que un mensaje del CLI llegue al chat de una persona, la huella que reconoce un documento reenviado, y la memoria de archivos ya vistos. Para poder probarlas en el Mac, `bot.py` se puede importar sin que exista `/srv/jubilo`: sus dos efectos de arranque que tocan el disco van dentro de un `try`.

**Nivel 1c, el trámite.** `tramites/probar_pedir_historia.py` comprueba que leamos bien las respuestas del portal de Colpensiones, y **no toca internet**: trabaja sobre las respuestas reales guardadas del 2026-09-18.

```bash
python3 -B tramites/probar_pedir_historia.py
```

La mitad de sus comprobaciones verifican lo contrario de lo normal: que la cédula, el correo y el nombre **no** lleguen a la base, y que los salarios, las semanas y los años **sí** lleguen. Un filtro que tacha de más deja el reporte inservible. `deploy_jubilo.sh` corre esta prueba solo y se detiene si falla.

**Nivel 2, el kit: conversando en la sesión.** Los cambios de `kit-contexto/` (qué pregunta, cómo responde, qué tono) se prueban aquí mismo con Santiago, leyendo el prompt modificado y razonando la respuesta esperada. No hace falta desplegar para saber si un texto quedó bien.

**No se monta un bot de pruebas por ahora.** Se evaluó y se descartó por complejidad frente al beneficio actual. Se reconsidera cuando haya usuarios reales en volumen.

---

## 4. Desplegar

Solo después de que las pruebas del nivel que corresponda estén en verde.

**Y solo después de verificar el servidor.** Las pruebas del Mac comprueban el código; no comprueban la máquina donde va a correr. El 2026-09-19 se desplegó el cierre por inactividad con las 17 suites en verde y la función nació muerta, porque al servidor le faltaba el extra `job-queue` de `python-telegram-bot`: `app.job_queue` valía `None`, cada llamada se devolvía en silencio y no hubo un solo error. Se descubrió por casualidad leyendo el log.

```bash
python3 -B bot/verificar_servidor.py
```

Comprueba que se pueda entrar, que exista el intérprete del entorno virtual (**ojo:** el `pip3` suelto del servidor instala en otro sitio, y mirar ahí fue lo que confundió el diagnóstico ese día), que todas las librerías que importan `bot.py` y `registro.py` se importen **con ese** intérprete, que el `JobQueue` exista de verdad, y que el servicio esté activo. La lista de librerías no está escrita a mano: la lee de los propios archivos, así que un import nuevo sin instalar lo caza solo. `deploy_jubilo.sh` ya lo corre como paso 1d y se detiene si falla.

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

## 5 bis. El banco de palancas (añadido el 2026-09-19)

`calculadora/palancas.py` es el **director de orquesta**: los motores de cálculo ya existían y nadie los llamaba para responder la única pregunta que le importa a la persona, que es "¿y yo qué puedo hacer?". Este módulo elige qué palancas le aplican, las cuantifica corriendo la calculadora, las ordena por impacto y arma los escenarios. Su entrada es `palancas.calcular(caso, regimen, sexo, edad, fecha_calculo, datos)`.

**Lo consumen dos sitios y ninguno redacta nada por su cuenta:** el reporte (`reporte/armar_reporte.py`, secciones 4 y 5) y el agente en conversación (ver la sección "Las palancas salen de `palancas.py`" del `system-prompt.md`).

Seis reglas que este módulo impone y que no se pueden romper al tocarlo:

- **El número nunca se estima.** Cada palanca se cuantifica volviendo a correr la calculadora con el supuesto movido.
- **Una palanca puede salir negativa, y entonces no se ofrece.** En el RPM, aplazar la pensión BAJA la mesada cuando la tasa ya está en su tope y el IBL que manda es el de toda la vida (Ley 100 art. 21).
- **El traslado de régimen no entra al ranking por impacto.** Viaja en su propia llave. Ordenarlo por impacto equivale a recomendarlo, y el traslado exige por ley doble asesoría.
- **La palanca de administradora va siempre debajo de la de portafolio.** El portafolio pesa entre dos y diez veces más; presentarlas iguales invita a optimizar la pequeña.
- **Si la persona está en el PISO de la garantía de pensión mínima, ninguna palanca le mueve la mesada.** El módulo levanta `aviso_de_segmento` y eso manda sobre todo lo demás: para ella lo que está en juego no es cuánto recibe, es calificar. **Ojo con la distinción (corregida el 2026-09-19):** la etiqueta `garantia_pension_minima` tapa dos situaciones distintas y el aviso ya no las colapsa. Si su capital financia menos de un salario mínimo, está en el piso (`tipo: garantia_pension_minima`) y sus palancas valen cero. Si financia más que el mínimo pero no llega al umbral del 110%, el Estado no le completa nada y sus palancas SÍ le suben la mesada: ahí el aviso es el del borde (`tipo: riesgo_de_caer_en_la_garantia_minima`).
- **A quien está en el piso se le cuantifica el valle.** `aviso_de_segmento["valle"]` trae los dos caminos con número: aceptar el mínimo (cuánta plata botaría aportando dentro del valle, donde el retorno marginal es cero) y saltar el valle (cuánto tendría que aportar al mes para superar el umbral con margen). Los dos salen de correr la calculadora por bisección, nunca de estimar, y cuando el salto excede lo razonable frente a su ingreso se dice con el número en la mano en vez de ofrecer un camino falso.

`calculadora/anomalias.py` es su compañero: revisa la historia laboral y marca lo que hay que verificar (siete tipos, cada uno con su nivel de confianza). **Nunca afirma que hay un error**, porque un falso positivo aquí destruye la confianza: dice qué ir a preguntarle a la administradora.

## 6. Reglas al tocar el código

- **La IA nunca calcula.** Si un cambio hace que el modelo estime, redondee o interpole una cifra, está mal. El número sale de `calculadora/`.
- **Comenta todo el código nuevo**, en español, breve y en lenguaje cotidiano: Santiago es principiante en código. Imita el registro de los comentarios que ya existen.
- Comentarios dentro del código sin tildes (así está el resto); los textos que lee el usuario, con tildes.
- **Nunca el guion largo** en ningún texto, ni en código ni en documentos.
- **Nada de lo que entra a la bitácora se guarda sin pasar por el filtro.** Si añades un campo de texto a `turnos` o `eventos`, va por `redactar()` y su caso va a `probar_registro.py`.
- No toques sin pedirlo: el aislamiento por `CLAUDE_CONFIG_DIR`, el enlace de credenciales, `--allowedTools`, `--permission-mode default` ni el candado del aviso de privacidad. Son decisiones de diseño con razones escritas en la guía de montaje.
