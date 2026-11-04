# Tipo de control para Fz y Fy — REABIERTA (2026-11-04)

**(2026-11-04) Luis autoriza modificar el firmware del ESP32 para lograr tiempo real — revierte la decisión del 2026-11-03 de no tocarlo.** Esto cambia la conclusión de abajo: ya no es "ILC ciclo a ciclo porque el firmware no lo permite". Con el firmware nuevo (propuesto, NO probado en hardware — `control/firmware/control_velocidad_continua.patch` + protocolo de prueba en `control/firmware/README.md`), la realimentación en tiempo real **sí sería implementable**. Queda pendiente de banco de pruebas (no hay RPi ni ESP32 en esta sesión), así que la arquitectura objetivo vuelve a ser la propuesta original de abajo: **híbrido FB (tiempo real) + ILC**, con el ILC ya construido (`control/ilc/`) como la capa que aprende encima de la realimentación en tiempo real una vez que el firmware nuevo esté probado. Hasta que el firmware nuevo esté validado en banco, lo único que se puede correr de verdad es ILC solo (lo que ya hay).

## Comparación directa: qué se gana y qué se pierde con cada tipo (2026-11-04)

Con los mismos datos de la simulación (`control/simulacion/salida_consola.txt`; Kp=10, τ=20 ms SIN MEDIR, k_real=0.8 SIN MEDIR, T=10 ms ≈ la latencia parcial actual, RMS del último ciclo en %BW, pico ~100 %BW):

| Opción | RMS (T=10 ms) | Ventaja | Desventaja |
|---|---|---|---|
| **1. Realimentación en tiempo real sola** (RT) | 11.54 | Único que reacciona *dentro del mismo ciclo* a lo que no se repite (tropiezo, variación de la prótesis). No se desestabiliza con latencia alta: a 160 ms da 33.9 (malo, pero finito, no diverge). | Error alto y **no mejora con el tiempo** — a los 100 ciclos sigue en ~11.5, igual que en el primero. |
| **2. RT + prealimentación** (necesita conocer la rigidez k de la prótesis) | 2.00 | Mejor que RT solo en el rango medio de latencia (0–40 ms). | Depende de un parámetro (k) que **cambia por prótesis** — justo lo que el proyecto quiere comparar. Si k está mal estimado, empeora; a latencia alta (100 ms) queda **peor que RT solo** (11.90 vs 8.54): amplifica el error de fase. Recalibrar k por prótesis contaminaría la comparación (ya no sería "mismo control, prótesis distinta"). |
| **3. Híbrido RT+ILC** (lo construido en `control/ilc/`, pendiente de banco) | **0.40** | Mejor de los tres por lejos (≈29x menos error que RT solo) y **no necesita conocer la rigidez de antemano** — aprende la corrección que hace falta para cada prótesis sin calibrar nada manualmente a mano. Sigue reaccionando dentro del ciclo como (1): con una perturbación no repetible solo sube a 0.67 (vs. 0.68 para RT+pert, prácticamente igual de robusto). | Tiene un **techo de latencia**: en la simulación se desestabiliza a partir de ~130 ms (560 %BW, inestable a 160), mientras que RT solo seguía dando un número malo pero finito ahí. Si la latencia real termina siendo mucho peor de lo medido/supuesto, el híbrido es el que se cae primero. Tarda ~10–12 ciclos en aprender (≈40 s a ciclo de 4 s) y hay que reiniciar ese aprendizaje al cambiar de prótesis — esos primeros ciclos rinden como RT solo, no como el régimen aprendido. Exige el firmware nuevo (`SET_VEL`), sin probar en hardware. |
| **4. ILC puro, sin realimentación dentro del ciclo** (descartado, no simulado como tal) | — | — | No se simuló aislado porque es inseguro: nada reacciona si algo cambia a mitad de la pisada (tropiezo, prótesis que se traba). Todo "ILC" en esta simulación ya incluye el Kp de realimentación por dentro — por eso la fila 3 y no una fila 4 con datos. |

**Conclusión para la tesis:** el argumento central para el híbrido no es solo "da menos error" — es que es el único que **no requiere conocer de antemano la rigidez de cada prótesis**, que es justo la variable que el proyecto quiere dejar libre para comparar. El costo que hay que declarar junto con eso: el techo de latencia (no medido con la latencia real completa) y la dependencia de un firmware nuevo sin validar en hardware.

## Lo que ya estaba construido antes de esta reapertura (sigue válido)
`control/ilc/` (núcleo `ilc_core.py` + `fz_ilc.py`, ambos con autoprueba en planta sintética; cliente serial `protocolo_subida_esp32.py` sin probar en hardware). Metodología/datos previos: `reportes/2026-11-03_reporte_dia.md` §§ 4–8.

**Retardo del amplificador AMTI, dato usado para la latencia total (no para esta decisión, que no depende de la latencia): se buscó en internet (2026-11-04) un número publicado por AMTI y no existe públicamente — se confirmó con búsqueda web, no es que no se buscó. Se usa un número SUPUESTO por analogía (NO verificado con AMTI, NO es un dato de internet específico del Gen 5): cota calculada de los filtros analógicos (0.79 ms, `pruebas/calcular_retardo_amti_manual.py`) + ~1.5 ms supuesto por analogía con el retardo de un ADC de instrumentación sobremuestreado a una tasa similar (el propio ADS1256 midió 1.6–2.4 ms a 1000 SPS) para el sobremuestreo/DSP interno del Gen 5 (2000 Hz máx, no especificado en el manual). Total AMTI ≈ 2–3 ms, SUPUESTO. Si se necesita el número real: preguntar a soporte AMTI o medirlo con referencia física — ninguna de las dos se hizo.**

## Propuesta original (2026-11-03, superada para Fz por lo de arriba — se deja para Fy, que aún no se decide)
**Control híbrido por eje (Fz vertical, Fy horizontal): lazo de realimentación de fuerza en tiempo real (RPi, AMTI) como base + ILC que aprende ciclo a ciclo encima.** No ILC solo, no tiempo real solo. Para Fz, la parte "en tiempo real" de esta propuesta queda fuera de alcance por la restricción de firmware (ver arriba); para Fy sigue abierta hasta que se decida con el mismo criterio.

## Por qué (evidencia y límites)
| # | Argumento | Respaldo |
|---|---|---|
| 1 | El tiempo real **solo** deja un error de seguimiento grande: llega tarde a la curva (≈ 11.5 %BW a Kp=10; 5.9 a Kp=20) | simulación, panel (a)(b) — bajo supuestos |
| 2 | Subir la ganancia para arreglarlo choca con la latencia: T máx 60 ms a Kp=10, 23 ms a Kp=20, 6 ms a Kp=40 | analítico, margen de fase 45° — depende de τ servo supuesto |
| 3 | ILC lleva el error repetible a ≈ 0.4 %BW en ~12 ciclos y tolera latencia hasta ~60 ms con error < 1 %BW (0.78 a 60 ms, 3.4 a 100 ms, inestable hacia 130) | simulación, panel (b)(c) |
| 4 | La marcha simulada **se repite por diseño** (trayectoria capturada, ciclos iguales a x6): es la condición que ILC necesita | CLAUDE.md (arquitectura) |
| 5 | Lo que se compara cambia la planta: cada prótesis tiene rigidez/amortiguamiento distintos. Un control en tiempo real con prealimentación necesita conocer esa rigidez; ILC **aprende sin identificarla** | *(razonamiento)*; la sensibilidad a k se vio solo parcialmente (k real = 0.8 del modelo) |
| 6 | Hace falta realimentación debajo del ILC porque ILC no corrige lo que no se repite dentro del ciclo (riesgo 4 del proyecto) y para estabilizar el lazo | CLAUDE.md riesgo (4); simulación panel (d) (pulso pequeño) |
| 7 | ILC ≪ RT puro se mantiene al barrer servo (10–50 ms), rigidez (0.5–1.5) y apoyo (3–5 s): RT 6.1–17.9 %BW, ILC 0.21–1.56 %BW | simulación, sensibilidad |
| 8 | La latencia medida hoy (≈ 8–9 ms parcial) **no obliga** a abandonar el tiempo real a ganancia moderada | medición + simulación |

## Restricción de la interfaz actual del ESP32 (verificada en el código, no probada; decisión de Luis: no modificar el firmware)
El firmware no tiene una orden de velocidad/posición continua (solo movimientos finitos y trayectorias precargadas de hasta 500 puntos; una orden nueva sobre un eje en movimiento se ignora). Entonces: **ILC** (recargar los arreglos de pasos entre ciclos) es compatible sin cambiar el firmware; el **lazo de realimentación en tiempo real** dentro del ciclo necesitaría firmware nuevo. Orden de trabajo coherente con no tocar el ESP32: **primero ILC sobre la interfaz actual**; la realimentación en tiempo real queda como mejora posterior que requeriría cambiar el firmware (a decidir con Luis). Por confirmar: tiempo de carga de una trayectoria y si se puede recargar entre ciclos (reporte § 9).

## Qué cambiaría la propuesta
- Variabilidad ciclo a ciclo alta (prótesis activa prototipo, holguras) → ILC aprende poco: pesar más el tiempo real + prealimentación.
- Latencia total medida ≫ 30 ms (con cómputo RPi y ESP32) → bajar Kp; el ILC pasa a hacer casi todo el seguimiento.
- Impacto de talón o rigidez que cambia dentro de la pisada → perturbación no repetible: más realimentación, más ganancia, o ILC con filtro más conservador.
- Aprendizaje de ~10 ciclos (≈ 40 s a ciclo de 4 s) inaceptable para el protocolo de ensayo → revisar.

## Restricciones que el control debe respetar (del proyecto)
- Horizontal (Fy): nunca retrocede → saturar la corrección y verificar con el sensor de posición.
- Carga máxima: pico 1500 N (decidido por Luis) → limitar la corrección aprendida.
- Fz, Fy y sagital se ejecutan a la vez en el mismo ciclo; primero Fz y Fy, sagital fijo por ahora.
- Opcional (a decidir con la asesora): ANFIS-PID como mejora de la parte de realimentación, solo después de tener el ILC básico.

## Precedentes (DOI verificado, lectura **sin confirmar** → no usar como respaldo final)
Aubin 2012 (lógica difusa sobre GRF vertical), Insam 2021 (hardware-in-the-loop). Ninguno compara ILC con tiempo real en este tipo de simulador.

## Cómo confirmarlo (en orden)
1. Latencia restante: AMTI (manual), cómputo RPi, ESP32 (Paso 3).
2. Identificar servo vertical y rigidez de contacto con ≥ 2 prótesis.
3. Repetir el barrido de la simulación con esos valores + perturbación de impacto.
4. Probar híbrido en el simulador real (Fz primero) contra el lazo abierto actual (RMSE/correlación, como en el artículo).
