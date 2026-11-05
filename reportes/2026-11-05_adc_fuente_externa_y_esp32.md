# 2026-11-05 (14:40–15:00) — ADC con fuente externa de 5 V, ESP32 conectado, latencia total

## 1. ADS1256 tras poner el 5 V con fuente externa — NO resuelto

**Objetivo:** comprobar si la causa de las caídas del ADS1256 era corriente insuficiente del 5 V del RPi (hipótesis de Luis) y, con el ADC sano, medir la latencia total del lazo.

**Metodología:** (a) `leer_ads1256_fz.py --diagnostico` (3 + 3 + 3 intentos); (b) revisión del log del monitor `logs/monitor_20261105_144227.log` y de `dmesg`/`journalctl -k`; (c) `fuser`/`ps` para ver quién tenía el SPI.

**Resultado (hechos medidos):**
- 14:42–**14:48:20**: el monitor leyó Fz real (≈ −1.8 N de media, rango −3.8…+0.7 N, plato vacío) → el ADC SÍ funcionó con la fuente externa.
- Desde **14:48:20** el monitor lee exactamente 0.0 N / 0.00000 V (n≈1190/línea): el SPI devuelve ceros.
- Con el monitor cerrado (kill por PID 3003; `fuser` no muestra otro proceso con el SPI), el diagnóstico falla 3/3: registros leídos 0/0/0 (a las 14:40, con el monitor corriendo, daba MUX=1 / DRATE=240 = valores de reset).
- `get_throttled`=0x0 (sin subtensión del RPi).
- ESP32 (CP2102) apareció como `/dev/ttyUSB0` a **14:45:39** (dmesg); el PING/PONG corrió 14:46 y terminó 14:46:17. La caída (14:48:20) ocurrió ~2 min después: **no coincide con el PING**.
- **Qué pasó a las 14:48:20 se desconoce** (pendiente: preguntar a Luis qué tocó/conectó en ese momento).
- Patrón a vigilar (correlación, NO causa probada): es la 3.ª vez que el ADC cae con el ESP32 recién conectado por USB / en uso (10:53 y hoy); la 1.ª (11-03) sin registro de ESP32.

**Corrección propia:** a las 14:45 dije que el diagnóstico fallaba "por competir con el monitor" y retiré la hipótesis de fallo del chip. Era **incompleto/incorrecto**: ahora falla también sin monitor. Los fallos de 14:40 sí pudieron deberse al monitor, pero no explican los de ahora.

**Limitaciones:** no se midió el 5 V ni el GND común de la fuente externa; no se sabe si el GND de la fuente está unido al del RPi; no se probó desconectar el USB del ESP32 para ver si el ADC vuelve.

**Fuentes:** logs `logs/monitor_20261105_*.log`, `dmesg`, `journalctl -k`, salida de `leer_ads1256_fz.py --diagnostico`.

## 2. PING/PONG con el ESP32 conectado — OK

**Objetivo:** confirmar el enlace RPi↔ESP32 por USB. **Metodología:** `pruebas/medir_latencia_ping_pong.py`, n=100. **Resultado:** 100/100 válidos, RTT 5.990 ms (σ 0.042, mín 5.848, máx 6.267); igual al 5.97 ms previo; ≈5 ms es el sondeo `vTaskDelay(5ms)` del firmware. CSV: `pruebas/resultados/ping_pong_20261105_esp32_conectado.csv`. **Limitaciones:** solo enlace, no movió motores. **Fuentes:** `communication.h` (firmware), script citado.

## 3. Latencia total del lazo — sin resultado

**Objetivo:** medir con un solo reloj flanco GPIO27 → AIN1 → detección → `MANUAL` al ESP32 → ack `OK`. **Metodología:** script nuevo `pruebas/medir_latencia_lazo_total.py` (mueve el eje sagital K ±40 pasos alternando; aborta antes de mover si GPIO27 no llega a AIN1). **Resultado:** **no se obtuvo número**: el script falló al inicializar el ADS1256 (ver §1); no se movió ningún motor. **Limitaciones previstas del método:** el ack se envía al aceptar el comando, no mide cuándo el motor empieza a girar; no incluye el retardo del amplificador AMTI (supuesto 2–3 ms, ver CLAUDE.md); el divisor GPIO27→AIN1 es temporal y no se verificó que siga cableado. **Fuentes:** `pruebas/medir_latencia_gpio_adc.py`, `pruebas/medir_latencia_comandos.py`.

## Pendiente
1. Luis: qué se hizo a las 14:48:20; medir 5 V de la placa y verificar GND común fuente–RPi–placa.
2. Desconectar el USB del ESP32 y reiniciar el RPi: ¿el ADC vuelve? (descarta/confirma la correlación).
3. Con el ADC sano: correr `pruebas/medir_latencia_lazo_total.py` y reabrir el monitor con `--con-esp32`.

## Actualización 14:50 — causa de la caída de las 14:48:20
Luis informó que el ADC "se había desconectado" (un cable) y lo reconectó. Verificado: el monitor reabierto a las 14:49 (`logs/monitor_20261105_144923.log`) vuelve a leer Fz ≈ −2.5 N, plato vacío; un pico de −188.7 N a las 14:50:04 coincide con manipulación (no verificado). **Esto sustituye la sospecha de correlación con el USB del ESP32** (§1) como explicación de esta caída. No se sabe qué cable fue. Pendiente: asegurar el conexionado (tercera caída con síntomas de contacto) y decidir si la fuente externa es necesaria probando sin ella con cableado firme. Nota de proceso: mi script falló con 'GPIO busy' porque el monitor (PID 3371, reabierto 14:49) tenía el GPIO17; cerrar el monitor por PID antes de medir.

## Resultado 14:55 — latencia total del lazo MEDIDA (hasta el ack del ESP32)
**Objetivo:** latencia flanco eléctrico → ADC → RPi → comando al ESP32 → ack, con un solo reloj. **Metodología:** `pruebas/medir_latencia_lazo_total.py --n 30` (GPIO27 → divisor → AIN1; detección al 50 % del escalón; `<MANUAL:2:±40>` al sagital K, alternando signo; 1 s entre eventos). Niveles: bajo 52.8 mV, alto 1617.7 mV. **Resultado (n=30, 30/30 con `OK`, sin otras respuestas):**

| Tramo | media | σ | mín | p95 | máx |
|---|---|---|---|---|---|
| adquisición (flanco→detección) | 1.619 ms | 0.288 | 1.139 | 2.056 | 2.106 |
| comando (detección→ack OK) | 6.325 ms | 1.794 | 3.258 | 8.973 | 9.846 |
| **TOTAL (flanco→ack)** | **7.945 ms** | 1.791 | 4.398 | 10.478 | 11.535 |

CSV: `pruebas/resultados/latencia_lazo_total.csv`. El tramo de adquisición coincide con el 1.61 ms (50 %) medido el 11-03. El tramo de comando tiene más σ que el PING/PONG (0.042 ms): incluye el ack de `MANUAL` (el firmware lo responde tras procesarlo) además del sondeo de 5 ms; no se separó cuánto es cada cosa. **Movimiento realizado (autorizado por Luis):** sagital K ±40 pasos × 30 eventos, alternando → neto 0 pasos; el ESP32 se reinicia al abrir el puerto, así que su contador parte de 0 (no se leyó la posición).
**Limitaciones:** (1) el ack no es el instante en que el motor empieza a girar (sin sensor para medirlo); (2) no incluye el retardo del amplificador AMTI (SUPUESTO 2–3 ms, no medido) ni el cómputo de un controlador real (aquí es ~0); (3) escalón eléctrico de 3.3 V, no una señal de fuerza; (4) MANUAL del firmware original, no `SET_VEL` (que no está flasheado); (5) n=30, una sola sesión; (6) un lazo real mandaría en continuo, no con 1 s de pausa. **Lectura:** total medido 7.9 ms (p95 10.5, máx 11.5) + AMTI supuesto 2–3 ms → ≈ 10–14 ms hasta el ack; sigue muy por debajo del techo de ~130 ms donde la simulación mostró inestabilidad del híbrido, **pero esa comparación hereda los supuestos de la simulación**.

## Actualización 15:35 — preparación del Ensayo A (rigidez k) y hallazgos de la tarde
**Resumen de todo lo medido/hecho desde las 14:40 (cada ítem tiene su detalle en el reporte indicado):**
1. ADC cayó 14:48:20 = cable desconectado (reconectado por Luis); no se sabe cuál (§ arriba).
2. PING/PONG con ESP32: 5.990 ms (σ 0.042, n=100) (§2).
3. Latencia total del lazo hasta el ack del ESP32: 7.945 ms (σ 1.79, p95 10.48, máx 11.54, n=30), sin AMTI ni cómputo (§ "Resultado 14:55").
4. Picos de Fz = errores de bit SPI aislados (0.06–0.5 %); mediana causal de 3 aplicada al monitor; residual en vivo ≈1 % de ventanas → `2026-11-05_picos_fz_y_filtrado.md`.
5. **El servo vertical Y multiplica los errores (0.26 %→1.44 %, ráfagas de 3, σ 0.93→1.86 N) y no vuelven a lo anterior al parar (2.24 %, σ 2.17 N)**; sagital sin efecto; causa NO verificada → mismo reporte, § "Prueba con motores".
6. **Eje Y subido 200 mm** (16000 pasos, 4×50 mm, 4/4 `OK`) para que Luis monte el pie. El contador (`POSITION:0:16000:0`) solo cuenta pasos ordenados: elevación real SIN verificar. No se usó HOME.
7. Lo que dice el firmware (leído de `main.cpp`, `configurable_motion_data.h`, NO probado moviendo): `axis_move_steps` rechaza mover hacia un final de carrera ya presionado; hay interrupciones de límite en X/Y/K (`isr_limit`); `MANUAL` es no bloqueante y devuelve `BUSY` si algún eje se mueve; velocidad de `MANUAL` en Y = 1600 pasos/s = 20 mm/s; rango de búsqueda de HOME en Y 72000 pasos (90 cm, 20 cm de retroceso). **Los arreglos de trayectoria compilados en el firmware están vacíos (`gait_data_length = 0`)**: las trayectorias capturadas no están en el RPi ni en este repo; viven en el script generador de Luis y se suben por `TRAJ_BEGIN/POINT/END`.

**Decisión de diseño del Ensayo A (propuesta de Claude, para que Luis confirme): NO mover horizontal ni sagital durante la medición de k.** Motivo: k es una pendiente fuerza/desplazamiento cuasi-estática de UN grado de libertad; mover X arrastra la suela sobre la plataforma (fricción y cortante sin caracterizar) y mover el ángulo cambia qué parte del pie carga; mezclar eso confunde `k` y añade riesgo. Que sea "antinatural" no importa: es identificación, no marcha. La marcha acoplada llega en la fase ILC. Ensayo posterior útil (propuesto, no hecho): repetir A con el sagital quieto en 3–4 ángulos fijos (talón/plano/antepié), porque la rigidez del pie depende de dónde carga. No se puede "simular una trayectoria guardada" desde el RPi sin que Luis aporte el archivo; no se inventó ninguna.
**Pendiente de Luis:** pie montado, hueco suela–plataforma en mm, elevación real del eje (¿20 cm?), confirmar no mover X/K en el Ensayo A, y aportar el archivo de trayectoria si se quiere un ensayo acoplado más adelante.

## Actualización 15:50 — trayectoria acoplada y HOME: DIFERIDOS (decisión de Luis)
**Objetivo (aplazado):** correr una trayectoria de apoyo (X y ángulo sagital del montaje 37, de `~/Projects/gaitsim-control/data/trajectories/`, solo lectura) escalada a x6 con Y fijo, tras calibrar (HOME) sin el pie. **Estado:** NO ejecutado; no se mandó HOME ni se movió X/K. Luis decidió dejarlo pendiente porque faltan probar parámetros.
**Reglas registradas:** nunca HOME con la prótesis colocada (puede romper un mecanismo); `gaitsim-control` es solo referencia, no se edita.
**Hechos leídos (no probados moviendo):** HOME recorre Y→X→K buscando mínimo y máximo (límites de búsqueda Y 72000 / X 28000 / K 14000 pasos; 1600/1600/3200 pasos/s; varios minutos); las trayectorias capturadas son solo de apoyo, ~61 puntos a 10 ms (tiempo real), columnas tiempo/X cm/Y cm/ángulo; el montaje disponible es 35 y 37 (el "36.5" mencionado era el 37); las tallas van de 160 a 180.
**Pendiente al retomar:** (1) talla (propuesta 174, no confirmada); (2) pie en el aire o apoyado; (3) script único con el puerto abierto, porque el ESP32 se reinicia al abrir el puerto y pierde la referencia; (4) conversión cm→pasos (X: 400 pasos/rev ÷ paso de husillo — verificar el valor del eje X, solo el de Y está confirmado: 80 pasos/mm) y signo del ángulo (K_POSITIVE_DIR=0); (5) OK explícito de Luis para HOME en ese momento.

## Actualización 16:05 — parámetros del Ensayo A
**Datos de Luis:** hueco suela→plataforma 23 cm; ángulo sagital del pie ≈ 5° (aproximado; método no indicado). **Decisión de método:** la rigidez depende del ángulo, así que `k` se reporta por ángulo y el ángulo se fija y registra (argumento obligatorio, encabezado del CSV). **Cambio de script** (`control/identificacion/ensayo_A_rigidez.py`, sin ejecutar): con escalones de 0.2 mm y ~0.6 s de asentamiento por escalón, 230 mm tomarían >10 min; se añadió aproximación rápida (tramos de 50 mm hasta hueco−30 mm vigilando Fz) y escalones finos solo en el tramo final. **Limitaciones:** hueco medido a mano (incertidumbre no anotada); ángulo ≈5° sin instrumento declarado (¿inclinómetro/IMU?) → incertidumbre desconocida; la aproximación rápida baja a 20 mm/s con vigilancia cada 50 mm, así que un contacto inesperado antes de lo previsto solo se detecta al final del tramo (límite de fuerza de aborto: 8 N en la aproximación, 150 N en la fase fina); no probado en hardware. **Pendiente:** confirmar cómo se midió el ángulo; Luis confirma el pie montado; ejecutar con el monitor cerrado.

## Aclaración 16:15 — qué miden hueco y ángulo
Hueco = 23 cm con el sustituto del muñón + prótesis montados, desde el punto más inferior hasta la plataforma (dato de Luis; cinta/regla, incertidumbre no anotada). Ángulo ≈5° **a ojo**. **Limitación:** `k` depende del ángulo y este dato no está medido → cualquier `k` obtenido queda con ángulo incierto hasta medirlo con inclinómetro. **Pendiente:** medir el ángulo con instrumento; confirmar que el montaje está terminado; remedir el hueco antes de la corrida.

## Plan 16:20 — Ensayo A en tres ángulos (talón / planta / dedos)
**Objetivo:** obtener `k` para tres condiciones de apoyo del mismo pie, para ver cuánto depende la rigidez de qué parte carga. **Metodología propuesta (no ejecutada):** tres corridas de `ensayo_A_rigidez.py`, una por ángulo sagital fijo; ángulos candidatos de la trayectoria de apoyo real talla174/montaje37 (solo lectura): +11.1° (contacto inicial), ≈0° (20 % del apoyo), −27…−37° (90–100 %). K ≈ 111.1 pasos/° (comentarios del firmware, no medido). **Resultado:** ninguno aún. **Limitaciones:** (1) el mapeo ángulo→zona de contacto es una hipótesis (el ángulo del CSV podría ser tibial y el pie estar montado con otro offset); (2) el signo del paso K frente al ángulo no está verificado; (3) el ángulo de partida (≈5°) es a ojo, y los giros se harían en pasos relativos desde ahí, así que el error se arrastra; (4) riesgo de colisión de los dedos al girar; (5) fmax 100 N en talón y dedos es elección de diseño, no dato. **Fuentes:** `~/Projects/gaitsim-control/data/trajectories/Control_apoyo_talla174_montaje37.csv`, `configurable_motion_data.h`.

## 16:35 — Herramientas del Ensayo A (registro, visor, comparador)
**Objetivo:** (a) guardar el recorrido vertical completo de cada ensayo; (b) ver en vivo lo que pasa mientras se mueve; (c) comparar cuánto varía `k` entre ángulos. **Metodología:** `ensayo_A_rigidez.py` (registro por fase + subida), `visor_ensayo_A.py` (lee el archivo en vivo; proceso aparte), `comparar_k_por_angulo.py` (+ `ajuste_k.py`). **Resultado:** probado solo con datos sintéticos de 3 rigideces conocidas (25/60/40 N/mm): el ajuste las recuperó con 25.1/60.4/39.7 N/mm (error ≤ 1 %, con ruido σ=1 N); el visor renderiza (PNG). **No hay datos reales todavía.** **Limitaciones:** (1) hecho para un solo grado de libertad y carga cuasi-estática; (2) el 'mm' es desplazamiento ORDENADO (pasos/80), no medido: sin sensor de posición, el hundimiento de la prótesis y la holgura/ elasticidad del eje entran en `k` (es la rigidez del conjunto cadena+pie, no solo del pie); (3) la histéresis compara rangos de fuerza no idénticos (orientativa); (4) el visor y el comparador no se han probado con la ventana interactiva en la pantalla del RPi (solo PNG); (5) el monitor de Fz no puede coexistir con el ensayo (SPI/serial). **Pendiente:** ejecutar el Ensayo A real, tres ángulos.

## CORRECCIÓN DE HORAS y corrida 1 del Ensayo A (reloj real ~15:40–15:45)
**Corrección:** las horas de los títulos de las secciones posteriores a "14:55" (15:35, 15:50, 16:05, 16:15, 16:20, 16:35) y las de las entradas equivalentes de `CLAUDE.md` eran **estimaciones mías y están adelantadas**: el reloj real a ese punto era ~15:39. El orden correcto es el de `git log` (hora real de cada commit). Tampoco era cierto que el monitor de Fz estuviera reabierto: no corría desde las 15:15.
**Corrida 1 del Ensayo A (15:40, `ensayo_A_ang5_actual_5deg_a_ojo_20261105_154037.*`) — FALLÓ sin contacto:** (1) el ADC necesitó **6 intentos** para inicializar (lecturas de vuelta distintas en cada intento: errores de bit SPI también en la secuencia de arranque); (2) aproximación hasta 200 mm sin contacto (F≈0); (3) a **202.4 mm de descenso** el ADC dejó de dar `DRDY` (`TimeoutError`) y el ensayo abortó; (4) **la subida automática también falló** porque dependía de leer Fz (defecto de diseño mío) → el eje quedó **202.4 mm abajo, ~28 mm sobre el contacto previsto**, sin fuerza aplicada. Luis lo notó ("aún no ha llegado y no se está moviendo"). Se subió a mano de vuelta por serial: 16192 pasos en 5 tramos, 5/5 `OK`, 0 pasos pendientes (vuelta al punto de partida). Nunca hubo fuerza sobre la plataforma (F≈0–1.3 N en todo el descenso).
**Correcciones al script:** (a) `fz()` reinicializa el ADC y reintenta ante `TimeoutError`/init fallido (hasta 6 veces), registrando el evento; (b) la subida gruesa ya NO depende del ADC (solo serial, con 3 reintentos). **Hallazgo:** otra evidencia de que el ADC no es fiable con el servo vertical en marcha (cuarta falla: 10:53, 14:48 cable, init de las 15:40 con 6 intentos, DRDY a mitad del ensayo). Prioridad real antes de cualquier control: arreglar el acoplamiento/cableado del ADC (GND común, cables cortos y blindados, alejar del servo).
