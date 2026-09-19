# IPC de Colombia: serie mensual empalmada

**Fecha de descarga:** 2026-09-19. **Estado:** verificado en fuente oficial.

## Qué es y de dónde sale

| Campo | Valor |
|---|---|
| Serie | Índice de Precios al Consumidor (IPC), total nacional |
| Productor del dato | DANE |
| Publicador (de donde se baja) | Banco de la República, portal SUAMECA |
| URL exacta del servicio | `https://suameca.banrep.gov.co/estadisticas-economicas-back/rest/estadisticaEconomicaRestService/consultaMenuXId?idMenu=100002` |
| Página humana equivalente | https://suameca.banrep.gov.co/estadisticas-economicas/informacionSerie/100002/indice_de_precios_al_consumidor_ipc |
| Periodicidad | **Mensual** |
| Cobertura | **Julio de 1954 a agosto de 2026** (866 meses, sin un solo hueco) |
| Unidad, según los metadatos del propio servicio | "Indice, base dic/2018=100" |
| Ficha técnica del DANE | https://www.dane.gov.co/files/investigaciones/fichas/precios-y-costos/DSO-IPC-MET-001-v7.pdf |

## Lo importante: ya viene empalmada

La serie **llega empalmada en una sola base, diciembre de 2018 = 100**. No hay que
unirla a mano. Las bases históricas conocidas son jul-1954, dic-1978, dic-1988,
dic-1998, dic-2008 y dic-2018, y en ninguno de esos quiebres la serie se reinicia:

| Mes del quiebre | Índice ese mes | Índice el mes siguiente | Variación |
|---|---|---|---|
| dic-1978 | 0,56 | 0,57 | +1,8% |
| dic-1988 | 4,58 | 4,71 | +2,8% |
| dic-1998 | 36,42 | 37,23 | +2,2% |
| dic-2008 | 69,80 | 70,21 | +0,6% |
| dic-2018 | 100,00 | 100,60 | +0,6% |

Todas son variaciones mensuales normales. Si la serie viniera en tramos sin
unificar, en cada uno de esos meses el índice caería de golpe a 100 o a 1.

`descargar_ipc.py` vuelve a correr esta comprobación cada vez que se refresca la
serie, así que si algún día el Banco cambia de base y publica los tramos sueltos,
el script lo avisa en vez de dejarlo pasar en silencio.

## Validación contra cifras oficiales

La inflación anual calculada desde esta serie reproduce las cifras publicadas:
2022 = 13,12%, 2023 = 9,28%, 2024 = 5,20%, 2025 = 5,10%.

## Precisión: la advertencia que hay que respetar

El servicio entrega los valores con **solo dos decimales**. Como el índice está
anclado a dic-2018 = 100, los valores antiguos son muy pequeños y quedan
redondeados de forma brutal:

- Antes de **abr-1981** el índice vale menos de 1,00, o sea que hay como mucho dos
  cifras significativas. Las variaciones mes a mes de ese tramo **no sirven**
  (aparecen saltos de 33% en mar-1958 que son puro redondeo, no inflación real).
- Entre 1981 y 1992 el índice va de 1 a 10: tres cifras significativas, sirve para
  variaciones anuales pero no para mensuales finas.
- Desde **ene-1992** en adelante el índice pasa de 10 y la precisión es suficiente
  para cualquier uso.

Para la calculadora pensional esto no es un problema: los cálculos relevantes
usan el tramo reciente. Pero si alguna vez se indexa un salario de los años
sesenta, hay que usar la variación **anual**, nunca la mensual.

## Lo que NO se pudo cerrar

- La serie de precios de **1923 a 1954** (el índice de costo de vida anterior al
  IPC nacional) **no está** en el catálogo de SUAMECA: el menú de "Precios e
  inflación" arranca en el IPC de 1954. Vive en el visor dinámico
  (`https://uba.banrep.gov.co/htmlcommons/SeriesHistoricas/precios-inflacion.html`),
  que es un reporte de SAS Visual Analytics dentro de un iframe y necesita
  navegador. El navegador no estaba disponible en esta sesión, así que ese tramo
  queda **no verificado y pendiente**.
- El archivo `https://www.banrep.gov.co/sites/default/files/paginas/series%20historicas.xls`
  sí descarga (HTTP 200, 384 KB, en realidad es un `.xlsx` con extensión `.xls`),
  pero **no contiene la serie histórica de precios**: son los resultados de la
  encuesta mensual de expectativas de inflación, de 2003 en adelante. No sirve
  para este propósito.
- El portal `www.banrep.gov.co` responde con detección de bots (ShieldSquare) a
  las descargas por script, así que la página de notas metodológicas en inglés no
  se pudo leer directamente.

## Archivos de esta carpeta

| Archivo | Qué es |
|---|---|
| `descargar_ipc.py` | Baja la serie, la revisa y escribe el CSV. Se corre a mano en el Mac |
| `ipc-colombia-mensual.csv` | La serie lista para usar: `mes`, `indice_base_dic2018`, `variacion_anual_pct` |
| `ipc-colombia-crudo.json` | La respuesta original del Banco, tal cual, como respaldo |

El script también trae `rebasear(serie, mes_base)`, por si algún día conviene
expresar la serie en otra base.
