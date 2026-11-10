# 2026-11-10 (tarde) — Restauración del firmware original del ESP32 y retoma del parche SET_VEL

## Objetivo
1. Volver el ESP32 al firmware ORIGINAL (binario de la laptop), porque el que tenía desde la mañana estaba compilado con otra versión de plataforma y respondía peor (original recompilado en la Pi: 82/100 respuestas).
2. Comprobar que el original restaurado responde igual que antes (RTT ≈ 5.97 ms).
3. Compilar el parche v3 con la versión correcta (`espressif32 @ 7.0.1`) y repetir regresión + latencia (la degradación de la mañana se midió con otro core: 6.5.0 / core 2.0.14 / IDF v4.4.6).

## Metodología
- `git pull` (fast-forward `f632fdd..2824726`): trajo `control/firmware/binarios/original_laptop/` (firmware.bin, bootloader.bin, partitions.bin, SHA-256, versiones) y `platformio.ini` con `platform = espressif32 @ 7.0.1`.
- **Respaldo ANTES de flashear** (regla del día): `respaldar_y_flashear.sh respaldo` → `control/firmware/respaldos_flash/flash_0x0_0x80000_20261110_150634.bin` (512 KB, SHA-256 `25740146…baa7`, leído en 12.4 s). Es el firmware compilado con 6.5.0 que tenía el ESP32.
- Flasheo con esptool de PlatformIO: `bootloader.bin` en 0x1000, `partitions.bin` en 0x8000, `firmware.bin` en 0x10000 (offsets estándar de esp32dev/Arduino; no se escribió 0xe000: `boot_app0` ya estaba de flasheos anteriores). esptool reportó "Hash of data verified".
- Pruebas SIN movimiento (ningún eje se movió, solo PING / TRAJ_STATUS / GET_POSITION): `control/firmware/prueba_regresion_sin_movimiento.py --sin_set_vel` y `pruebas/medir_latencia_ping_pong.py --n 200`.

## Resultado
| Medida | Original restaurado (laptop, 7.0.1) | Referencia |
|---|---|---|
| Regresión (PING, TRAJ_STATUS=IDLE, posición sin cambio) | TODO OK | — |
| PING/PONG válidos | 200/200 | firmware original 100/100 |
| RTT medio | **5.993 ms** (σ 0.347, mín 5.174, máx 7.706) | 5.97 ms (2026-11-03); 5.990 ms (2026-11-05) |
| Original recompilado en la Pi con 6.5.0 (mañana) | — | 82/100 |

→ El ESP32 quedó en el estado bueno: latencia igual a la medida antes de cualquier flasheo de hoy. CSV: `pruebas/resultados/ping_pong_20261110_original_restaurado.csv`.

Incidente menor: la primera corrida de regresión, lanzada a los pocos segundos del flasheo, leyó basura. No era un bucle de reinicio: una escucha pasiva a 115200 y a 74880 baud dio 0 bytes, y repetida tras esperar 4 s dio TODO OK. Causa más probable (NO verificada): abrí el puerto en pleno arranque. Regla práctica: esperar ≥4 s tras flashear.

## (Superado por la sección 'Resultado v3' al final) Pendiente al escribir la parte inicial
- **Error mío, corregido:** al preparar la copia para compilar v3 usé `patch -p4` en vez de `-p3`; el parche NO se aplicó (main.cpp quedó en 846 líneas). La compilación que corría en ese momento es del original SIN parche con 7.0.1. Sirve de control (¿reproduce el binario original, IDF v4.4.7?), no de prueba del parche.
- Falta: aplicar v3 con `-p3`, compilar con 7.0.1, comprobar `esp-idf: v4.4.7`, respaldar, flashear, repetir regresión (con `SET_VEL`) y latencia (GET_POSITION contra 4.94 ms). Resultado: se agrega abajo cuando exista; si no hay sección "Resultado v3", no se hizo.

## Limitaciones
- Una sola medición de 200 muestras del original restaurado; no se midió GET_POSITION en esta tanda (solo PING).
- El `firmware.bin` recompilado con 7.0.1 tiene el mismo tamaño que el original pero SHA-256 distinto (la laptop no investigó por qué); por eso el ESP32 se restauró con el binario ORIGINAL de la laptop, no con uno recompilado.
- El respaldo es de 0x0–0x80000 (arranque + app), no de los 4 MB completos (la lectura completa tardaría ~17 min por este CP2102).
- Reiniciar el ESP32 (flasheo, apertura de puerto) libera el freno vertical en `setup()`; no hubo carga ni movimiento durante la prueba.

## Fuentes
- `PEDIDO_PARA_LAPTOP.md` y `control/firmware/binarios/original_laptop/versiones_pio.txt` (respuesta de la laptop: IDF v4.4.7 con 7.0.1, medido por ella recompilando).
- Salidas de esptool y de los scripts de esta sesión; `reportes/2026-11-10_firmware_pruebas_banco_sin_movimiento.md` (pruebas de la mañana).

## Adenda (tarde): ADC sin respuesta al intentar preparar el lazo vertical
- Luis autorizó seguir y confirmó: junto al paro de emergencia, ADC reconectado, pie montado y recorrido despejado, sin HOME. No se movió ningún eje (el ADC falló antes y el parche v3 aún no está validado).
- `pruebas/leer_ads1256_fz.py --diagnostico` → "El ADS1256 no devolvio lo escrito: leido={ADCON:0, MUX:0, DRATE:0} esperado={ADCON:0, MUX:8, DRATE:161}". Leer todo ceros es el mismo síntoma que el 2026-11-05 14:48 (línea digital desconectada/floja). Comprobado con `ps` que ningún proceso tenía el SPI abierto (el PID que mostró un `pgrep -f` era la propia shell). Causa NO determinada; falta que Luis revise los cables digitales (SCLK/DIN/DOUT/CS/DRDY/5V/GND) o use `pruebas/diagnostico_guiado_ads1256.py`.
- Sin Fz no se puede cerrar el lazo: el movimiento con contacto queda bloqueado hasta que el ADC responda.
- **Luis reconectó el ADC; `--diagnostico` repetido: registros correctos** (STATUS 0x30, MUX 0x08, ADCON 0x00, DRATE 0xA1). AIN0 (Fz) media −55.66 mV (≈ −31.5 N de offset, se tara; igual al −55 mV visto antes hoy), pico-pico 11.3 mV con el pie montado. Los pico-a-pico de los demás canales (800 mV) son canales sin conectar y, según el reporte de picos del 2026-11-05, incluyen errores de bit del SPI: usar mediana de 3–5, no el pico-pico como medida de ruido. Qué cable estaba suelto: no se sabe (Luis no lo dijo). Sigue sin movimiento.


## Resultado v3 (parche SET_VEL v3 compilado con espressif32 @ 7.0.1) — sin movimiento
**Bloqueos encontrados en el camino (todos resueltos, documentados por si se repiten):**
1. Mi `patch -p4` no aplicó el parche (era `-p3`); detectado por `wc -l` (846 líneas). Con `-p3`: main.cpp 846→**1002** líneas, `SET_VEL` presente en main.cpp (11) y communication.h (2), sin `.rej`.
2. El build se colgó ~25 min: un `pio run` abandonado de la mañana (PID 7087, `build_base617`) tenía `packages.lock`; lo terminé por PID.
3. `No space left on device`: `/tmp` es tmpfs de 4 GB y el core de PlatformIO ocupaba 2.8 GB. Se movió el core al disco: `/home/simgaitlibra/pio_core_scratch` (fuera del repo; usar `PLATFORMIO_CORE_DIR=` ahí).
4. Con 7.0.1 el esptool (4.11) necesitó `pip install intelhex` en el venv de PlatformIO.
5. Un `pgrep -f` en un bucle de espera se habría encontrado a sí mismo (regla 7): detenido antes de que importara.

**Compilación:** `esp-idf: v4.4.7 38eeba213a` (igual al original); `bootloader.bin` y `partitions.bin` con SHA-256 IDÉNTICO al original; `firmware.bin` 284192 B (original 283408; +784 B del parche), SHA-256 `ba6c2954…a0d5`. Binarios guardados en `control/firmware/binarios/v3_7.0.1/` (+ `sha256sums.txt`).

**Flasheo:** hash verificado por esptool en los 3 offsets. **Respaldo previo NO hecho en este flasheo** (el script de respaldo se colgó y lo maté; el encadenado siguió al flasheo porque `| tail` devolvía éxito). Lo que había en la flash era el original restaurado, cuyos binarios y SHA están en `binarios/original_laptop/`, así que el estado anterior es recuperable. Mejora pendiente: no encadenar el flasheo al respaldo con un pipe.

**Pruebas (ningún eje se movió; solo PING, GET_POSITION, TRAJ_STATUS y SET_VEL con velocidad 0):**
| Medida | v3 con 7.0.1 | Original | v3 con 6.5.0 (mañana) |
|---|---|---|---|
| Regresión + `SET_VEL:1:0`→OK, `SET_VEL:9:0`→BUSY | TODO OK | — | 5/5 |
| PING válidos / RTT | 200/200, **5.983 ms (σ 0.077)** | 5.97–5.99 ms | — |
| GET_POSITION (n=100) | **4.970 ms (σ 0.478, máx 9.68)** | 4.94 ms | 44 ms |
| TRAJ_STATUS (n=100) | 4.947 ms (σ 0.376, máx 8.49) | — | — |

→ La degradación de la mañana era del toolchain (6.5.0), no del parche. Con 7.0.1, v3 tiene la misma latencia que el original.
Datos: `pruebas/resultados/ping_pong_20261110_v3_701.csv`, `pruebas/resultados/latencia_comandos_20261110_v3_701.csv`.

**Limitaciones:** (a) en la corrida de `medir_latencia_comandos.py` PING dio 98/100 válidos con un máximo de 107.9 ms; probablemente las primeras respuestas durante el arranque tras abrir el puerto, NO verificado (la corrida de 200 PING no perdió ninguno). (b) Como tras restaurar, la primera apertura del puerto tras flashear lee basura; hace falta repetir tras ≥5 s. (c) `SET_VEL` con velocidad distinta de 0, el watchdog (80 ms) y el comportamiento real del motor NO están probados: requieren mover Y. (d) Que el eje responda en el sentido correcto (signo) sigue sin medir.

## Primer movimiento con SET_VEL en el eje Y real, EN EL AIRE (2026-11-10, ~16:15)
**Objetivo:** comprobar con hardware real que `SET_VEL` mueve Y, que el watchdog de 80 ms lo detiene y que el contador vuelve a cero. Script: `control/firmware/prueba_set_vel_aire.py` (sin HOME, sin Fz; datos en `pruebas/resultados/set_vel_aire_20261110.json`).
**Condiciones:** Luis junto al paro de emergencia, pie montado y sin tocar la plataforma (el hueco NO se remidió esta vez: Y no se había movido desde el Ensayo A, que terminó con el eje arriba y sin carga). Comprobación previa con el ADC poco fiable: AIN0 −73.3 mV (−55.7 mV a las 15:40, ≈10 N de diferencia) y DRATE leído 0x00 en vez de 0xA1 (error de lectura SPI); no sirvió para descartar contacto.
**Metodología:** A) `SET_VEL:1:400` (5 mm/s) reenviado cada 20 ms durante 0.5 s, luego `SET_VEL:1:0`. B) un solo `SET_VEL:1:400` y silencio 0.6 s. C) regreso con `MANUAL:1:-neto`.
**Resultado (contador de pasos ORDENADOS, no medido físicamente):**
| Fase | Medido | Esperado |
|---|---|---|
| A: pasos | **202** (≈2.52 mm); 25 comandos, RTT 6.37 ms (máx 9.71), todos `OK` | ≈200 (400 pasos/s × 0.5 s) |
| B: pasos tras un solo `SET_VEL` | **32** | ≈32 (400 pasos/s × 80 ms) → el watchdog de 80 ms detuvo el eje |
| C: contador final | **0** (tras `MANUAL:1:-234`) | 0 |
**Limitaciones:** el contador cuenta pasos ordenados; que el eje se haya movido de verdad 2.5 mm y en qué sentido físico NO está medido (falta lo que observó Luis); una sola corrida; sin carga ni contacto; el parche v3 sigue sin probarse junto a `RUN`; los pasos de B coinciden con el cálculo teórico, pero no se midió el instante de parada con osciloscopio.

### Repetición con cuenta regresiva (2026-11-10, ~16:25): signo CONFIRMADO por Luis
La primera corrida (2.5 mm) Luis no la vio. Repetición: `--dur_s 1.0 --cuenta_s 10` (datos: `pruebas/resultados/set_vel_aire_20261110_rep2.json`). Contador: A **402 pasos** (≈5.03 mm; 50 comandos `OK`, RTT 5.77 ms, máx 8.67), B **32 pasos** (igual que la primera corrida: el watchdog de 80 ms), C retorno a 0 con `MANUAL:1:-434`.
**Luis, textual: "si subio"** → `SET_VEL` con velocidad positiva SUBE el eje Y, la misma convención que `MANUAL` (+ = subir). Esto sí es observación física, pero cualitativa: Luis no dijo cuánto subió (no se midió con regla) ni que se detuviera en B, y el retorno a 0 es del contador, no medido. Limitaciones previas siguen: sin contacto, sin Fz, una sola repetición del sentido.

## Lazo cerrado de Fz: revisión crítica y reescritura de `control/lazo_fz_tiempo_real.py` (2026-11-10, ~16:40) — NO probado en hardware
**Problemas reales encontrados al revisar el script antes de usarlo con contacto (todos corregidos):**
1. **Sin tara:** `leer_n()` daba Fz con el offset del ADC (−31 N a −49 N; deriva ≈10 N entre las 15:40 y las 16:10). El lazo lo habría tomado como fuerza. Ahora `tarar()` (mediana de 200 muestras con el eje quieto, sin contacto; aborta si p5–p95 > 15 N).
2. **Sin aproximación:** la referencia pide fuerza desde t=0, y el lazo habría bajado saturado (20 mm/s) a ciegas hasta el contacto. Ahora: descenso rápido (20 mm/s) hasta `hueco−30 mm`, luego lento (5 mm/s) hasta F > 8 N; recién ahí empieza el lazo.
3. **Sin tope de descenso:** ahora aborta si el descenso ordenado integrado ≥ `hueco + 20 mm`.
4. **Lecturas anómalas:** aborta si F < −30 N o |ΔF| > 30 N entre muestras filtradas; también ante 3 respuestas seguidas ≠ `OK` a `SET_VEL`.
5. **Espera de 2 s al abrir el puerto** → 6 s (con 2.5 s se leyó basura de arranque hoy).
6. **`SystemExit` incondicional** → ahora sin `--ejecutar` solo imprime el plan; en real exige `--hueco_remedido` (regla de Luis: el hueco se mide de nuevo en cada corrida) y registra el ángulo (`--angulo_deg`) en un `.meta.txt` junto al log.
7. **Retorno seguro al final** (también ante abortos): `SET_VEL 0`, lee el contador y sube con `MANUAL` en tramos de ≤800 pasos, como la subida gruesa del Ensayo A. Si falla, lo avisa en voz alta.
Se quitó el `\n` extra del marco `<SET_VEL:…>` (la prueba que sí funcionó no lo mandaba).

**Prueba SIN hardware (`--simulado`, planta sintética k=25 N/mm, contacto a 75 mm con hueco declarado 80, offset −40 N, ruido σ 0.9 N, pico ~118 N, 3 ciclos):** contacto detectado a 75.3 mm; RMS por ciclo 8.78 → 5.44 → 4.01 N; contador final 0. Valida la lógica (tara, aproximación, abortos, retorno). **No valida** la dinámica real: la planta simulada no tiene el servo, el retardo del AMTI (supuesto), la histéresis ni el acople de ruido del servo.
**Limitaciones/pendiente:** (a) con el pie en punta (−37.3°, k≈2.4 N/mm, la última posición) `pasos_por_n` calculado con k=26.4 es 11× menor al necesario: respuesta lentísima y no llega a la fuerza; para una primera prueba conviene plana (0°, k≈23) — falta mover el sagital (movimiento: pedir a Luis); (b) hay que medir el hueco con el pie ya en su ángulo; (c) primera corrida real: escala baja (`--peso_sujeto_n 100`, pico ~118 N, ya probado hasta 163 N en el Ensayo A), `--fmax_n 150`; (d) el ADC con el servo activo sigue dando errores de bit (mediana de 5, sin verificar que alcance).

## Pie a PLANA (2026-11-10, ~16:50)
Con `rotar_sagital.py --a 0`: +4144 pasos del sagital K (de −37.3° a 0.0°), 7/7 tramos con ack OK. Es el ángulo ESTIMADO por pasos desde el 2026-11-05 (no medido con instrumento; asumí que nadie movió el pie a mano desde entonces — Luis estaba presente). Solo K; Y y X no se movieron. Falta: que Luis mida el hueco suela→plataforma con el pie en esta posición y diga si el ángulo físico se ve plano.

## Primeras corridas REALES del lazo de Fz (2026-11-10, ~16:12–16:20): ninguna llegó a contacto
Hueco dado por Luis: "unos 10 cm" (≈100 mm, aproximado); pie plana (0° estimado); Luis junto al paro; `--peso_sujeto_n 100 --fmax_n 150`; sin HOME.
1. **16:12 — abortó ANTES de mover** (contador Y = 0): "Tara inestable (p5–p95 = 20.1 N)". Medí el ruido del ADC con el eje quieto (2000 muestras): mediana de |desviación| 3.63 N, p90 9.6 N; 58 % de las muestras a más de 3 N de la mediana, 8.5 % a más de 10 N, 0.2 % a más de 50 N (máx 1333 N). Tras la mediana de 5: σ 3.12 N, p99 8.3 N. **Es ruido de banda ancha ≈5× mayor que el del 2026-11-05 (σ≈0.9 N), no solo errores de bit. Causa NO determinada** (sospecha sin probar: acople del servo vertical, ahora energizado).
   Cambios por esto: la dispersión de la tara se mide sobre la señal filtrada que usa el lazo (mediana de 5), no sobre la cruda (el umbral de 15 N se mantuvo); el contacto exige **5 lecturas seguidas** > 8 N (con p99 = 8.3 N un solo valor habría dado falsos contactos).
2. **16:13 — abortó en la aproximación:** "sin contacto en el descenso máximo" (la integral de lo ordenado llegó a 120 mm) y **el contador de Y quedó en 0**. Esto NO cuadra: si hubiera bajado 120 mm el contador habría dado ≈−9600. **Sin explicar.** Descartado: USB (sin cortes en dmesg a esa hora), constante de pasos/mm (80), manejo de velocidad negativa por el firmware (el código lo soporta) y la velocidad rápida: probados después por separado en el eje real, en el aire: `SET_VEL:1:-400` 0.5 s → **−205 pasos** (27 respuestas `OK`); `SET_VEL:1:-1600` 1.5 s → **−2426 pasos (30.3 mm)**, iteraciones de 18.8 ms; ambos con retorno a 0. No se sabe si en esa corrida el eje bajó (y el contador falló) o no se movió; Luis no informó lo que vio. Para que no pase inadvertido: el lazo ahora contrasta cada 0.5 s lo ordenado contra el contador del ESP32 y aborta si difiere más del 25 % + 150 pasos.
3. **~16:15 — el ADC volvió a caerse** (registros leen 0/64, erráticos; mismo síntoma que las caídas por contacto flojo del 11-05) justo después de las pruebas con el ESP32 abierto; persistió en 3 reintentos sin ningún proceso usando el SPI. Sin Fz no se puede correr el lazo con contacto. Causa NO determinada (coincide en el tiempo con abrir el puerto del ESP32, no probado como causa).
**Estado físico:** Y volvió a su contador 0 en todas las pruebas (retorno por `MANUAL`); pie en plana; ningún contacto con la plataforma que se sepa (el lazo no registró F > 8 N).
**Limitaciones:** hueco "unos 10 cm" sin medición precisa; el 0° del pie es estimado; la discrepancia del punto 2 sigue abierta.

## 🛑 ERROR GRAVE MÍO (2026-11-10, ~16:30): las corridas del lazo movieron el eje X (horizontal), NO el vertical
**Causa:** `control/lazo_fz_tiempo_real.py` usaba `EJE_VERTICAL = "Y"` (texto) y mandaba `SET_VEL:Y:<v>`. El firmware parsea los parámetros con `atoi()` (`communication.h:152`), y `atoi("Y") = 0` → **eje 0 = X**. Respondió `OK` siempre (X es un eje válido), por eso nada alertó. Mis pruebas sueltas usaban el número `1` y por eso funcionaban. La constante venía del script original (escrito sin hardware) y yo la heredé sin revisarla al reescribir.
**Qué explica:** la discrepancia "contador Y = 0 con 120 mm ordenados" de la corrida de las 16:13 y la de las 16:22 (contador 0 vs −469 ordenados). La aproximación del 16:13 y 16:22 movió X, no bajó Y.
**Cuánto se pudo mover X (ESTIMADO, no medido; el contador de X se pierde al cerrar el puerto):** corrida 16:13: lo ordenado equivale a ≈9600 pasos de velocidad (1600 pasos/s ≈ 3.5 s + 400 pasos/s ≈ 10 s) ⇒ hasta ≈24 cm de X a 400 pasos/cm; corrida 16:22: ≈469 pasos ≈ 1.2 cm. El sentido físico de X con velocidad negativa NO está verificado, y X tiene finales de carrera que podrían haber detenido el eje antes (ISR `isr_limit`, no verificada moviendo). **La posición real de X hay que verla con los ojos: Luis.** El retorno automático del script solo repone Y, no X.
**Corrección:** `EJE_VERTICAL = 1` (entero) y guarda en `set_vel`/`detener` que aborta si el eje no es el entero 0, 1 o 2.
**Lección/regla:** en comandos al ESP32 el eje va SIEMPRE como entero (0=X, 1=Y, 2=K); y todo lazo nuevo debe verificar el eje correcto con una prueba de movimiento mínima antes de correr completo (la verificación contador-vs-ordenado sí lo detectó a las 16:22 y abortó a los ~0.3 s).

### Verificación del error del eje y medición de cuánto se movió X (2026-11-10, ~16:35)
Prueba mínima en el aire con la constante corregida (`EJE_VERTICAL = 1`): `SET_VEL` −400 pasos/s × 0.5 s → `POSITION:-8491:-205:4144` y retorno a `POSITION:-8491:0:4144`. **Y se mueve (−205 pasos) y X/K no cambian: el eje correcto queda confirmado por el contador** (la observación visual de Luis de esta prueba no está registrada).
**El contador NO se reinició al abrir el puerto esta vez** (a diferencia de otras veces; causa no investigada), y por eso conserva: K = 4144 (el giro a plana de las 16:55, coherente) y **X = −8491 pasos ≈ 21.2 cm** (a 400 pasos/cm, valor del 2026-11-05 no remedido) = lo que movieron mis dos corridas del lazo por el error del eje. Es el contador de pasos ORDENADOS/emitidos, no una medición física; el sentido físico de X negativo sigue sin verificar.
Pendiente: decidir con Luis si se repone X con `MANUAL:0:+8491` (movimiento exacto inverso) o a mano; no se movió X.

### X repuesto (2026-11-10, ~16:40)
Con OK de Luis ("si contua"). Verifiqué primero que el contador seguía en −8491 (si el ESP32 se hubiera reiniciado no habría movido). `MANUAL:0:+800` ×10 + `+491`, todos los ack `OK`; contador final `POSITION:0:0:4144` (X=0, Y=0, K=4144 = plana). Es el contador de pasos emitidos: que X esté físicamente donde estaba antes NO está medido (Luis no confirmó la posición ni que el recorrido estuviera despejado por palabra, solo autorizó seguir); si hubo pérdida de pasos o un final de carrera en la ida, el retorno no la corrige.

### X retrocedido 10 cm para quedar sobre la plataforma (2026-11-10, ~16:50)
Pedido de Luis: "retrocede unos 10 cm para que X quede sobre la plataforma", luego "10 centímetros hacia negativo, retrocédelo más". Interpretado como 10 cm en total hacia pasos NEGATIVOS. Prueba de 1 cm (`MANUAL:0:-400`) y, tras la indicación de Luis de seguir hacia negativo, 9 cm más (−3600 en 5 tramos, todos `OK`). **Contador final `POSITION:-4000:0:4144`** (X = −4000 pasos = −10.0 cm a 400 pasos/cm; Y = 0; K = 4144, plana). Luis no dijo explícitamente si la prueba de 1 cm fue hacia atrás; siguió con "hacia negativo". Posición física de X y que quede sobre la plataforma: NO medido, solo lo juzga Luis a ojo. Ojo: este contador es respecto al arranque del ESP32; cualquier reinicio lo vuelve a 0 sin mover el eje.

## Corridas con contacto con el eje corregido (2026-11-10, ~16:30–16:40): NINGUNA llegó a contacto; bloqueo = el ADC con el servo Y en marcha
Antes: X movido −5 cm más a pedido de Luis ("unos 5 cm más atrás y ya continúa") → contador `POSITION:-6000:0:4144` (X −15 cm en total desde 0; posición física y que quede sobre la plataforma: NO verificados por mí).
1. **16:31:19** (mediana causal de 5): abortó a −53 pasos (0.7 mm): "lectura anómala, F=48.0 N, previa 4.0". Retorno OK (Y=0).
2. **Cambio:** mediana de BLOQUE de 7 lecturas por ciclo de control (el ADC da 1000 SPS; el lazo usaba 1). En reposo: σ **1.38 N**, p99 3.6 N, máx 4.0 N (con la causal de 5: σ 3.1, máx 13 N); cuesta ≈8 ms por lectura.
3. **16:32:12** (bloque de 7): abortó otra vez a −61 pasos (0.8 mm): "F=38.6 N, previa −0.4". Que una mediana de 7 dé 38.6 N indica que NO es un pico aislado sino un **corrimiento sostenido del ADC mientras Y se mueve**: en la prueba aislada de 1.5 s a −1600 pasos/s (eje en el aire) ya se veía Fz = +43 a +52 N respecto de la tara (lo registré como "el eje se mueve bien" y no vi esa columna). Sin contacto no hay fuerza real: es acople eléctrico/ruido del servo (causa NO determinada, sin probar).
4. **Medición sistemática (fuerza vs velocidad de Y en el aire) — NO completada:** la tara y el reposo inicial salieron bien (media −0.1, mediana 0.0, rango ±3.2 N, n=130), pero tras el primer movimiento (−400 pasos/s × 0.5 s) el ADC dejó de convertir: `TimeoutError: DRDY no bajo a tiempo`. Mi script se cortó sin reponer Y (quedó −205 pasos); lo repuse a mano con `MANUAL` (`POSITION:-6000:0:4144`). `--diagnostico` posterior: registros 0 (ADC caído, 5.ª vez hoy con síntoma de contacto/alimentación).
**Conclusión (con límites):** hoy NO se puede cerrar el lazo de Fz con esta cadena de medición mientras el servo vertical se mueve: (a) corrimiento de ≈+45 N sostenido con Y en movimiento (visto en 3 de 3 arranques; magnitud con una sola velocidad medida, 1600 pasos/s); (b) el ADC se cae al activarse el servo/ESP32. Causas no determinadas: hipótesis NO verificadas — acople del servo por masa/cables, alimentación de 5 V del RPi insuficiente (hipótesis de Luis; el 11-05 con fuente externa funcionó 6 min), contacto flojo. **Tampoco es seguro operar a ciegas:** sin Fz fiable, el tope de fuerza no protege.
**Siguiente (no hecho):** (1) alimentar el ADS1256 con la fuente externa de 5 V y GND común; (2) fijar/soldar los cables digitales; (3) cables cortos y separados del cable del servo, ferritas; (4) repetir la medición fuerza-vs-velocidad en el aire (script listo en este reporte, ver arriba) con ADC sano; (5) solo entonces repetir el lazo con contacto.

## Visor en vivo para TODA prueba + nueva caída del ADC (2026-11-10, ~17:00)
**Pedido de Luis:** que todo lo que se haga se vea en la pantalla del RPi (regla 4 de trabajo). **Hecho:** `herramientas/en_vivo.py` (cada prueba escribe `logs/prueba_en_vivo.csv`: t, fase, Fz, contador de Y, mensaje) y `herramientas/visor_pruebas.py` (proceso aparte, sin SPI ni serie): Fz en grande, Fz(t) con las fases sombreadas, Y(t) y, arriba, **el texto de lo que se está haciendo en ese momento** (se pone rojo si dice ABORT). Verificado primero con datos sintéticos (PNG revisado) y abierto en la pantalla (PID 15067). Probado con hardware solo hasta el aborto de abajo. El lazo (`control/telemetria/visor_en_vivo.py`) conserva su propio visor, no integrado todavía con este.
**Prueba `pruebas/fuerza_vs_velocidad_y.py`** (Fz con Y en el aire a 400/800/1600 pasos/s, neto 0, con retorno garantizado en `finally`): **abortó al inicio**, `TimeoutError: DRDY no bajó a tiempo` al crear el lector del ADC (t = 8.1 s, tras abrir el ESP32); Y = 0, no se movió nada. Luis había reiniciado el ADC (tras el reinicio respondió bien: registros 0x30/0x08/0x00/0xA1).
**Prueba de aislamiento (ADC SOLO, sin ESP32 ni servo): 0/8 aperturas correctas** (`no devolvio lo escrito`, registros 0). Es decir, el ADC queda inutilizable tras abrir el ESP32 / correr el script, y no se recupera por software (sí cuando Luis lo reinicia). Patrón repetido hoy: 16:15, 16:40 y 17:00 — el ADC respondió bien justo antes y quedó caído justo después de una sesión con el ESP32 abierto. **Causa NO determinada. Hipótesis (no probada): una perturbación de alimentación/masa al abrir el puerto del ESP32 o activar el servo deja al chip en un estado que solo un ciclo de energía borra.** No sé qué hace Luis al "reiniciar el ADC" (¿corta el 5 V?).
**Prueba de causalidad propuesta (no hecha):** Luis reinicia el ADC → abro el ADC y lo dejo leyendo → en otro proceso abro SOLO el puerto del ESP32 (sin mover) → miro si el ADC falla y cuándo. Si sí: es el ESP32/USB. Si no: es el servo (repetir con un movimiento mínimo).
**Mejora de hardware propuesta (no hecha):** pasar PDWN del ADS1256 de +3.3 V fijo a un GPIO (p. ej. GPIO22) para poder reiniciar el chip por software (PDWN bajo → alto lo resetea) sin que Luis tenga que intervenir. Requiere un cable; no se hizo.

## Causalidad del ADC y medición de Fz con Y en el aire (2026-11-10, ~17:10–17:20)
**Luis aclara cómo "reinicia" el ADC:** solo quita y vuelve a poner el cable del 5 V → un ciclo de energía del chip lo recupera (refuerza la hipótesis de alimentación/masa; no la prueba).
**Prueba A — abrir el puerto del ESP32 SIN mover (`pruebas/causalidad_adc_esp32.py`):** ADC leyendo en este proceso, otro proceso abre el puerto del ESP32 (PING/GET_POSITION) y lo cierra. **0 fallos del ADC.** Fz (mediana, con tara): base 1.8 N (n=320), con el ESP32 abierto 1.5 N (n=770, rango −7.5…+7.8), después 0.8 N (n=408, rango −16…+10). Límite: el ESP32 NO se reinició en esa apertura (el contador siguió en −6000), así que el efecto de un reinicio no quedó probado.
**Prueba B — Y en el aire a 400/800/1600 pasos/s (`pruebas/fuerza_vs_velocidad_y.py`, ADC iniciado ANTES que el ESP32; 6 movimientos neto 0, contador final `POSITION:-6000:0:4144`, completada):**
| Movimiento | Fz en movimiento (mediana; min–max) | 0.5 s tras parar (mediana) |
|---|---|---|
| baja 400 | 8.0 N (−12.7…26.7) | 32.0 N |
| sube 400 | 39.8 N (31.4…43.8) | −4.2 N |
| baja 800 | 24.2 N (−2.9…42.0) | 30.9 N |
| sube 800 | 40.2 N (31.0…43.5) | −4.0 N |
| baja 1600 | 39.7 N (0.8…42.7) | 27.0 N |
| sube 1600 | 40.8 N (33.6…43.3) | 32.4 N |
Reposo inicial 0.9 N; reposo final 7.7 N. **Sin ningún contacto, Fz se mueve entre −10 y +43 N sincronizada con el movimiento de Y** (figura: `reportes/figuras/2026-11-10_fuerza_vs_velocidad_y_aire.png`; registro: `pruebas/resultados/fuerza_vs_velocidad_y_20261110_en_vivo.csv`). La magnitud (≈40 N, ≈35 % del pico objetivo de 118 N) NO es proporcional a la velocidad (en "sube" ≈40 N a las tres; en "baja" crece 8→24→40) ni vuelve a cero al parar (27–32 N tras bajar). **Causa NO determinada y sin separar:** acople eléctrico del servo/freno vs acoplamiento mecánico (la masa del carro cargando el bastidor donde está el AMTI). No se probó cuál.
**Después de la prueba B el ADC quedó caído** (`--diagnostico`: registros 0) — igual que tras las otras sesiones con el servo en marcha; tras la prueba A (sin mover) NO se cayó. Un solo caso por condición, pero consistente con las cinco caídas anteriores de hoy. Un intento posterior (50/100/200 pasos/s) no pudo correr: ADC caído al iniciar, Y no se movió.
**Cambios de código:** el ADC se inicializa ANTES de abrir el ESP32 (en `pruebas/fuerza_vs_velocidad_y.py` y `control/lazo_fz_tiempo_real.py`); la prueba acepta las velocidades por argumento.
**Conclusión (límites incluidos):** el lazo de Fz con contacto sigue bloqueado: con el servo vertical activo la medición de Fz tiene un error de hasta ≈40 N sin contacto y el ADC se cae. Es un problema de la cadena de medición (eléctrico o mecánico), no del controlador ni del firmware. **Antes de cualquier lazo hay que resolverlo.**
**Para Luis (hardware, en este orden):** (1) alimentar el ADS1256 con 5 V aparte (fuente externa, GND común en un solo punto) en vez del 5 V del RPi; (2) cables del ADC y del AMTI cortos, trenzados/blindados y lejos del cable del servo y del freno; (3) ferritas; (4) medir la salida del AMTI con multímetro/osciloscopio mientras Y se mueve: si cambia ahí, es el AMTI/acople previo al ADC; si no, es el ADC/SPI; (5) comprobar si la placa del AMTI está montada en el mismo bastidor que el carro (acople mecánico); (6) PDWN a un GPIO para reiniciar el chip por software.

## Demo para el compañero de Luis (2026-11-10, ~17:35): preparada, NO ejecutada (ADC sin responder)
**Pedido de Luis:** bajar hasta 500 N, subir con Y hasta despegar, mover X 10 cm hacia adelante y devolver esos 10 cm ("desde donde está ahora avance 10 cm y retroceda 10 cm, nada más"; el 10 cm es solo de X).
**Preparado:** `pruebas/demo_x10cm.py` (X +10 cm = +4000 pasos, pausa, −4000; exige `--y_arriba`; no toca Y ni K; registro en vivo). La bajada a 500 N iría con `control/identificacion/ensayo_A_rigidez.py` (pasos controlados, ya validado hoy hasta 163 N): `--fmax_n 500 --paso_pasos 40 --max_extra_mm 45 --angulo_deg 0 --hueco_mm 100 --hueco_remedido --ejecutar`; al terminar sube solo hasta arriba. Visor del Ensayo A abierto en la pantalla (PID 15365).
**Bloqueo:** tras el "reinicio" de Luis (quitar/poner el 5 V) el ADC sigue sin responder: `--diagnostico` falla en 4 intentos (una vez MUX=8 correcto y ADCON/DRATE en 0; el resto todo 0), sin ningún proceso usando el SPI. No se movió ningún eje. Sin Fz no se baja a 500 N.
**Notas:** 500 N es ≈3× lo máximo probado hoy (163 N; el artículo de conferencia reporta ≈1325 N en este simulador). El error de Fz con el servo en marcha (±40 N, medido en el aire) afecta la lectura: el "500 N" del demo es ±~40 N. Hueco: la última cifra de Luis es "unos 10 cm", sin remedir tras mover X. Mi comando de las 17:35 incluyó un `pkill -x -f "x"` que no coincidía con nada (violación de la regla 7 de Luis por descuido, sin efecto).

## ¿Es el código? Revisión del ADC (2026-11-10, ~16:45; la hora real del RPi, el reloj de mis notas anteriores iba ≈50 min adelantado)
**Pedido de Luis:** que falla "por momentos" sin que él mueva los cables; que revise si es el código y compare cuándo funciona y cuándo no.
**Revisión de `pruebas/leer_ads1256_fz.py`:** secuencia de inicio (SDATAC×3 → RESET → 0.1 s → SDATAC → WREG ADCON/MUX/DRATE → verificar por RREG → SELFCAL → SYNC → WAKEUP → RDATAC), modo SPI 1 (CPOL=0/CPHA=1) y 500 kHz: no encontré un error de secuencia. Una debilidad: no hay forma de reiniciar el chip por hardware (PDWN fijo a 3.3 V).
**Comparación (medido):**
| | Funciona | Caído (medido a las 16:44) |
|---|---|---|
| Registros STATUS/MUX/ADCON/DRATE | 0x30/0x08/0x00/0xA1 | 0/0/0/0 |
| DRDY (GPIO17) | oscila (1000 SPS) | **fijo en ALTO, 0 flancos en 2 s** |
| MISO (GPIO9) | datos | fijo en bajo |
**Intento de revivirlo por software (caído):** WAKEUP + RESET + SDATAC + WREG/RREG en modo SPI 0 y 1, a 50 y 500 kHz → los 4 casos igual (DRATE=0, DRDY sin flancos). **Descarta el código y el modo/velocidad de SPI como causa del estado "caído".** Alimentación del RPi en ese momento: EXT5V 5.07 V, `throttled=0x0` (sin subtensión).
**Lectura:** el chip no está convirtiendo ni respondiendo: parece apagado, en reset o sin alimentación/reloj, no desincronizado (distinto del fallo del 2026-11-05, donde DRDY oscilaba y el SPI daba basura). Un ciclo de energía lo recupera. Hipótesis NO verificada que encaja: contacto intermitente en PDWN o en la alimentación de la placa (o brownout de su regulador), no en las líneas SPI. Los eventos `over-current` de los puertos USB del RPi (cientos a las 15:30:57) coinciden con la reconexión del ESP32 de esa hora, no con las otras caídas; no se pudo correlacionar el resto.
**Medición que lo decide (Luis, con el ADC caído, 2 min con multímetro):** voltaje en el pin PDWN de la placa (debe ser ≈3.3 V), salida 3.3 V del regulador de la placa (AMS1117) y el 5 V en su pin. Si PDWN o el 3.3 V están en ≈0 V mientras está caído, esa es la causa.
**Herramienta nueva:** `pruebas/vigilar_adc.py` (vigila el ADC en reposo, sin ESP32 ni servo; registra cada segundo muestras/s, Fz, DRDY, MISO, 5 V, `throttled`; al caerse anota el instante y los pines, y reintenta cada 2 s). Sirve para saber si se cae SOLO en reposo (alimentación/contacto) o solo con el servo/ESP32. Sin ejecutar todavía.
