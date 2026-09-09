# Júbilo

Un asesor pensional para Colombia. Recibe la historia laboral de una persona y le
dice, con números y no con generalidades, qué pensión le espera, qué le falta y
qué decisiones todavía puede tomar.

Nació como una herramienta para que mis papás entendieran su propia pensión.

## Por qué hace falta

En Colombia se pensiona alrededor de una de cada cuatro personas que cotizan. Las
reglas son difíciles de verdad: dos regímenes que funcionan distinto, un traslado
entre ellos con una ventana que se cierra, semanas que se pierden por meses que
nadie reportó, y un cálculo de mesada que depende de decisiones tomadas veinte
años antes.

Y las herramientas oficiales fallan justo donde más se necesitan. El simulador de
Colpensiones **se niega a calcular** para quien está a menos de diez años de la
edad de pensión: exactamente la persona que está tomando la decisión. Eso está
verificado contra afiliados reales en la carpeta de validación del proyecto.

## La decisión de arquitectura que sostiene todo

**El modelo de lenguaje nunca calcula.**

Toda cifra sale de código fijo y auditable (`calculadora/`), que implementa las
reglas tal como están escritas en el corpus normativo. La IA conversa, entiende
el documento que le mandaron, decide qué módulo correr y explica el resultado.
Pero no hace aritmética, porque un error de un dígito en una proyección de
pensión es un error que la persona no puede detectar y que se lleva su decisión
por delante.

```
historia laboral (PDF)  ->  extracción  ->  router  ->  calculadora  ->  explicación
                                                        (código fijo)      (IA)
```

## Qué hay aquí

| Carpeta | Qué es |
|---|---|
| `calculadora/` | El motor. Regímenes público (RPM) y privado (RAIS), comparador entre los dos, detección de lagunas, costo y retorno de seguir cotizando, aportes voluntarios. Cada módulo con sus pruebas |
| `casos/` | Set dorado: seis historias laborales reales, anonimizadas, verificadas a mano contra el total impreso de cada documento. Es contra esto que se prueba la calculadora |
| `kit-contexto/` | El corpus normativo: 25 documentos sobre reglas de RPM y RAIS, traslados, independientes, invalidez, sobrevivientes, tributario, modalidades de pensión |
| `cobertura/` | Matriz de escenarios: qué situaciones cubre el sistema y cuáles no |
| `cumplimiento/` | Manual interno de tratamiento de datos y procedimiento ante incidentes |

## Cómo correr las pruebas

```bash
cd calculadora
python3 probar_diagnosticar.py   # el flujo completo, de punta a punta
python3 probar_rpm.py            # régimen público
python3 probar_rais.py           # régimen privado
```

No hay dependencias externas: es Python de la biblioteca estándar.

## Lo que este repositorio no tiene

- **Ninguna historia laboral con nombre.** Los casos están anonimizados: sin
  nombre, cédula, correo ni dirección, y con los empleadores reemplazados por
  etiquetas, porque la combinación de empleador, fechas y salario permite
  reconocer a una persona aunque su nombre no aparezca. La correspondencia entre
  caso y persona no vive aquí.
- **Ningún documento original.** Los PDF de los fondos se quedan fuera.
- Las cifras sí se conservaron intactas, porque son lo que estos casos existen
  para verificar.

## Estado

Versión 0, en construcción. El corpus normativo lleva marcas `[VERIFICAR]` en
cada afirmación que todavía necesita revisión de un abogado pensional: están ahí
a propósito, para que ninguna se cuele a un usuario como si fuera certeza.

Esto no es asesoría legal ni financiera. Es una herramienta para entender un
sistema difícil y llegar mejor preparado a la decisión.
