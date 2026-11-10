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
