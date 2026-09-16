# Verificación del coeficiente de costos presuntos de rentas de capital

> **Fecha:** 2026-09-16. **Marcas que cierra:** `rentista-de-capital.md` s.5 (coeficiente) y s.6 (alcance sobre dividendos).
> **Qué es este documento:** el registro de una verificación, no corpus. El agente no lee esta carpeta en producción. Vive aquí para que cualquiera pueda auditar de dónde salió una cifra del kit y hasta dónde llega esa prueba.

---

## 1. Qué se verificó

Dos cosas que el kit venía sosteniendo con fuentes secundarias:

1. El coeficiente de costos presuntos aplicable a rentas de capital, que el kit usaba en 28,08% citando prensa contable convergente.
2. Si los dividendos y participaciones entran en esa presunción, punto que quedó abierto cuando el Decreto 379 del 7 de abril de 2026 derogó el anexo del Decreto 1601 de 2022, cuyo renglón de rentistas los excluía con un paréntesis literal.

Ambas quedaron verificadas contra fuente oficial de la UGPP. Ver la sección 5 para el límite exacto de esa prueba.

## 2. Método

La calculadora de IBC de la UGPP es una aplicación JavaScript que corre en el navegador del usuario. Eso significa que el navegador tiene que descargar los coeficientes para poder calcular, y por tanto los coeficientes viajan en el HTML de la página. No hicieron falta simulaciones ni despeje: la tabla está embebida en el selector "Costos asociados: esquema presunción de costos", donde cada opción carga su coeficiente en los atributos `data-porcent` y `data-porcentdec`.

```
URL:              https://www.ugpp.gov.co/calculadora-ibc
Captura:          2026-09-16, con curl, sin sesión ni autenticación
Tamaño:           68.873 bytes
sha256:           05eca0b399650bfa3429dc9bcd2f6efc40a864cda84ab2c2276f69b211d8a86f
Archivo:          verificacion/evidencia/2026-09-16-ugpp-calculadora-ibc.html
Lógica de cálculo: /sites/default/files/js/js_xVvxLFLVYaOvzBCx0FOExrsiX1E5a3xdjfr1-B4NuCM.js
```

La página es de acceso libre y gratuito. No requiere registro. No hubo derecho de petición.

## 3. El renglón de rentistas, literal

```html
<option data-codciuu="" data-porcent="28,08" data-porcentdec="0.2808" value="0.2808">
  Rentistas de Capital incluidos dividendos y participaciones
</option>
```

Dos hallazgos en una sola línea: el coeficiente de **28,08%** y la **inclusión expresa** de dividendos y participaciones, que es la inversión exacta del paréntesis del anexo derogado.

La pestaña que contiene ese selector se rotula "Contrato diferente a prestación de servicios, Cuenta propia o Rentista de Capital, Cálculo de IBC con esquema de presunción de costos", así que la propia UGPP confirma que el rentista entra por la vía del independiente con contrato distinto a prestación de servicios, y no como categoría aparte. Es coherente con el Decreto 780 de 2016 art. 3.2.7.2 lit. b.

## 4. La fórmula que aplica la UGPP

Transcrita del JavaScript de la calculadora, con los nombres de variable originales:

```javascript
costos_cpropiap = IngresoMenCpropia * porcent_descto_cpropia_presuncion;  // 0.2808
if (costos_cpropiat > costos_cpropiap) { descuentoparaibc = costos_cpropiat; }  // reales
else                                   { descuentoparaibc = costos_cpropiap; }  // presuntos
IBC = (IngresoMenCpropia - descuentoparaibc) * 0.4;
if (IBC < SalarioMinimo)          { IBC = SalarioMinimo; }
else if (IBC > TopeMaximoSalario) { IBC = TopeMaximoSalario; }
```

En limpio:

```
costos_presuntos = ingreso_bruto * 0,2808
descuento        = el mayor entre costos reales digitados y costos presuntos
IBC              = (ingreso_bruto - descuento) * 40%
piso: 1 SMLMV                               techo: 25 SMLMV
```

**El descuento es el mayor de los dos, no el que elija el aportante.** Como un descuento mayor produce un IBC menor, la calculadora nunca deja al aportante en peor posición que la presunción. La consecuencia operativa es que **los costos reales solo le sirven al rentista si superan el 28,08% del ingreso bruto**; por debajo de ese umbral, digitarlos no cambia el resultado.

Parámetros de 2026 que trae la página: SMLMV de $1.750.905 (atributo `data-salminimo`) y tope de cotización de $43.772.625, que son 25 SMLMV.

Comprobación numérica con un ingreso de 10.000.000 de renta de capital:

| Paso | Valor |
|---|---|
| Ingreso bruto mensual | 10.000.000 |
| Costos presuntos (28,08%) | 2.808.000 |
| Base depurada | 7.192.000 |
| IBC (40%) | 2.876.800 |
| Aporte a pensión (16%) | 460.288 |
| Aporte a salud (12,5%) | 359.600 |

Sin la presunción, el IBC sería de 4.000.000 y el aporte a pensión de 640.000. La presunción le ahorra 179.712 mensuales.

## 5. Hasta dónde llega esta prueba, y dónde no llega

Esto es lo que hay que leer antes de citar esta ficha.

**Lo que prueba:** que al 2026-09-16 la UGPP, entidad que fiscaliza los aportes, aplica un coeficiente de 28,08% a las rentas de capital en su herramienta oficial y pública, y que rotula ese renglón incluyendo los dividendos y participaciones. Es conducta oficial documentada de la entidad, capturada con su hash.

**Lo que no prueba:** el contenido del acto administrativo. La página **no cita ninguna norma**: se verificó que no menciona la Resolución UGPP 532 de 2024, ni el Decreto 379 de 2026, ni ningún otro acto. Así que esta evidencia no permite atribuir la cifra a un artículo o a un anexo concreto, ni fija desde cuándo es exigible.

**Consecuencia para el kit:** el agente afirma "el coeficiente que aplica la UGPP en su calculadora oficial es 28,08%" y no "el artículo X de la Resolución 532 fija 28,08%". La diferencia importa si el usuario está en un proceso de fiscalización, donde lo que se discute es el acto administrativo.

**Lo que sigue abierto tras esta verificación:**

| Pregunta | Estado | Cómo se cierra |
|---|---|---|
| Texto y anexo de la Resolución UGPP 532 de 2024 | Abierto, solo para respaldo normativo | Petición de acceso a información pública a la UGPP |
| Fecha desde la cual rige el esquema | Abierto. Circulan tres fechas | Diario Oficial de abril de 2026, para la publicación del Decreto 379 |
| Ganancias ocasionales en el IBC del rentista | Abierto. La calculadora no las menciona ni las excluye | Doctrina o concepto de la UGPP |
| Norma que fija las edades de 50 y 55 | Abierto. La calculadora repite la regla sin citar artículo | Doctrina o concepto de la UGPP |
| Consejo de Estado exp. 28624 y Sentencia C-578 de 2009 | Abierto | Buscadores del Consejo de Estado y relatoría de la Corte Constitucional, sin petición |

Dato menor que refuerza la fecha sin cerrarla: al 2026-09-16 la calculadora ya está operando el esquema con parámetros de 2026, lo que es consistente con que el esquema rige. No es prueba de su fecha de inicio.

## 6. La tabla completa, 24 renglones

Transcrita del selector por extracción automática, no a mano. Son 21 secciones CIIU (A a la U), más "No clasificados en otra parte", más el renglón de rentistas, más un renglón de "Presunción media".

El porcentaje es el de **costos presuntos** que se descuenta del ingreso bruto antes de aplicar el 40%. Un porcentaje mayor significa un IBC menor.

| CIIU | Actividad | Costos presuntos | Valor en el selector |
|---|---|---|---|
| A | Agricultura, ganadería, caza, silvicultura y pesca | 68,85% | 0.6685 |
| B | Explotación de minas y canteras | 56,39% | 0.5639 |
| C | Industrias manufactureras | 62,34% | 0.6234 |
| D | Suministro de electricidad, gas, vapor y aire acondicionado | 60,30% | 0.6030 |
| E | Distribución de agua; evacuación y tratamiento de aguas residuales, gestión de desechos y actividades de saneamiento ambiental | 65,15% | 0.6515 |
| F | Construcción | 62,89% | 0.6289 |
| G | Comercio al por mayor y menor; reparación de vehículos automotores y motocicletas | 66,97% | 0.6697 |
| H | Transporte y almacenamiento (sin transporte de carga por carretera) | 63,79% | 0.6379 |
| I | Alojamiento y servicios de comida | 61,67% | 0.6167 |
| J | Información y comunicaciones | 61,17% | 0.6117 |
| K | Actividades financieras y de seguros | 60,65% | 0.6065 |
| L | Actividades inmobiliarias | 61,73% | 0.6173 |
| M | Actividades profesionales, científicas y técnicas | 62,04% | 0.6204 |
| N | Actividades de servicios administrativos y de apoyo | 59,10% | 0.591 |
| O | Administración pública y defensa; planes de seguridad social de afiliación obligatoria | 65,25% | 0.6525 |
| P | Educación | 67,08% | 0.6708 |
| Q | Actividades de atención de la salud humana y de asistencia social | 63,24% | 0.6324 |
| R | Actividades artísticas de entretenimiento y recreación | 56,92% | 0.5692 |
| S | Otras actividades de servicios | 56,33% | 0.5633 |
| T | Actividades de los hogares individuales en calidad de empleadores; actividades no diferenciadas de los hogares individuales como productores de bienes y servicios para uso propio | 56,01% | 0.5601 |
| U | Actividades de organizaciones y entidades extraterritoriales | 64,26% | 0.6426 |
| (sin código) | No clasificados en otra parte | 62,53% | 0.6253 |
| (sin código) | **Rentistas de capital incluidos dividendos y participaciones** | **28,08%** | 0.2808 |
| (sin código) | Presunción media | 62,88% | 0.6288 |

Tres lecturas de la tabla, para que nadie tenga que sacarlas de nuevo:

1. **Rentistas es el descuento más bajo de toda la tabla, por mucho.** 28,08% contra un rango de 56,01% a 68,85% en el resto. Con el mismo ingreso bruto, el rentista cotiza sobre una base más alta que cualquier otro independiente. Es coherente con el diseño del esquema: la renta de capital tiene menos costos asociados que una actividad productiva.
2. **El resto de la tabla es un pañuelo.** Entre el mínimo y el máximo de las 22 actividades hay menos de 13 puntos, así que clasificar mal la actividad dentro de ese grupo cambia poco. Clasificar mal entre rentista y no rentista cambia todo.
3. **Qué es el renglón de "Presunción media" no quedó verificado.** No es el promedio simple de las 21 secciones CIIU (62,01%) ni su mediana (62,04%), así que no se le atribuye un método. Es un valor propio del esquema y el agente no lo usa mientras no se sepa cuándo aplica.

## 7. Reproducir esta verificación y vigilar que el dato no cambie

Hay un script para esto, que es la forma recomendada:

```bash
bash verificacion/recapturar-calculadora-ugpp.sh
```

Guarda una captura nueva fechada, **sin reemplazar las anteriores** para conservar la serie, imprime el hash, y compara el renglón de rentistas contra la captura más reciente ya archivada. Si el coeficiente cambió, lista los archivos del kit que hay que actualizar y en qué orden. Si la UGPP cambia la estructura de la página y el renglón deja de encontrarse, avisa y termina con error en vez de guardar una captura muda.

A mano, si se quiere verificar sin el script:

```bash
curl -sL -A "Mozilla/5.0" https://www.ugpp.gov.co/calculadora-ibc -o calc.html
grep -oE '<option[^>]*data-porcent="[^"]*"[^>]*>[^<]*' calc.html
```

**Cuándo correrlo:** antes de construir o tocar `ibc_rentista.py`, en cada revisión anual del kit, y cuando salga noticia de una resolución nueva de la UGPP. Si el coeficiente de rentistas cambia, cambia el IBC de todo el segmento.
