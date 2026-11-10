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

## Pendiente (en curso al escribir esto)
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
