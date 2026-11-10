# 2026-11-10 — Firmware ESP32: compilación, flasheo desde la Pi y pruebas de banco SIN movimiento

## Objetivo
Compilar y flashear desde la Pi el parche `SET_VEL` (v2) sin afectar el funcionamiento normal (condición de Luis), usando solo comandos que no mueven ningún eje.

## Metodología
- PlatformIO instalado en un venv del scratchpad (no en el repo). `platformio.ini` del repo: `platform = espressif32` sin versión y `upload_port = COM10`; en las copias de compilación se fijó la plataforma y se pasó `--upload-port /dev/ttyUSB0`.
- Con `espressif32@8.0.0` (core Arduino 3.x, el que baja por defecto) NO se probó compilar: se canceló antes por la API de timers del código (hipótesis, no verificada). Se usó `espressif32@6.5.0` (Arduino-ESP32 2.0.14).
- Pruebas: `control/firmware/prueba_regresion_sin_movimiento.py` (PING, GET_POSITION, TRAJ_STATUS, `SET_VEL:1:0`, `SET_VEL:9:0`; nunca velocidad ≠ 0) y `pruebas/medir_latencia_comandos.py --n 100` (solo lectura). Cada apertura del puerto reinicia el ESP32 (conocido).
- Nunca se envió MANUAL, GOTO, RUN, HOME ni SET_VEL con velocidad distinta de 0. Ningún eje se movió.

## Resultado
1. **Compilan** el original y el v2 con core 2.0.14 (RAM 11.1 %, flash 21.4 % → 21.5 %).
2. **v2 (tal cual el repo + fix v2) FALLA en banco**: respuestas perdidas o con más de 1 s de retraso, a veces truncadas, y la respuesta aparece cuando entra el comando siguiente. Reproducible (3/3 corridas). No se observó en el firmware original que estaba flasheado.
3. **Bisección** (regresión ×3 por variante; "falla" = alguna respuesta incorrecta):
   | Variante | Resultado |
   |---|---|
   | original recompilado (core 2.0.14) | pasa 2/2 |
   | v2 completo | falla |
   | v2 con `vTaskDelay` de la tarea auxiliar a 100 ms (A) | falla |
   | v2 con stacks de 8000 B (D) | falla |
   | v2 sin la llamada a `revisar_watchdog_velocidad()` (E) | pasa 3/3 |
   | watchdog que solo llama a `millis()` (G1) | pasa 3/3 |
   | watchdog con el bucle de ejes, sin sección crítica ni `axis_stop` (G2) | pasa 3/3 |
   | watchdog con `portENTER_CRITICAL` + `nop` (H) | falla 3/3 |
   | watchdog con `axis_stop` sin sección crítica (I) | pasa 1/3 |
   Conclusión medida: el watchdog implementado como código en `auxiliar_task` que toma `axes_mux` perturba la comunicación. El **mecanismo exacto NO se entiende**: según el código, `continuous_mode` solo se pone en 1 en `axis_set_velocity` (línea 301 del v2), así que la sección crítica no debería ejecutarse en reposo, y aun así H falla. Posible sensibilidad al layout/compilación; no verificado.
4. **v3** (`control_velocidad_continua_v3.patch`): el watchdog se movió a la ISR del eje continuo (compara `esp_timer_get_time()` 32 bits con el instante del último `SET_VEL`; solo corre mientras el eje gira), sin tarea, sin sección crítica y sin tocar el `vTaskDelay` original. Regresión **5/5 correctas**. `git apply --check` OK. **main.cpp v3: 846 → 1002 líneas, 164 agregadas / 8 borradas** (diff exacto en `control/firmware/diff_exacto/main_cpp_v3.diff`). **Pero la latencia con v3 es mala**: GET_POSITION 44.2 ms de media (σ 35.6), TRAJ_STATUS 50.9 ms, PING 14.9 ms con máx 104 ms (CSV `pruebas/resultados/latencia_comandos_2026-11-10_firmware_v3.csv`), contra 4.94 ms (σ 0.03) del firmware original.
5. **El original recompilado con mi toolchain también se degrada**: GET_POSITION 5.63 ms (σ 1.0) con 82/100 respuestas, TRAJ_STATUS 5.94 ms con 82/100, PING 87/100 (CSV `latencia_comandos_2026-11-10_original_recompilado.csv`), contra 100/100 del binario que estaba antes en el ESP32. Es decir, **mi toolchain (core 2.0.14) no es equivalente al que compiló el firmware original**, y las comparaciones de 2–4 quedan confundidas por eso: no se puede atribuir al parche la degradación de v3 sin una base compilada igual.

## ⚠️ Error de procedimiento (mío)
**No respaldé la flash del ESP32 antes de sobrescribirla** (`esptool read_flash`). El binario original (el que daba 100/100 y 4.94 ms) **ya no está en la Pi**. Lo único que existe es el código fuente del repo, recompilado con un core que puede no ser el original. Si Luis conserva el `.pio/build/esp32dev/firmware.bin` en su laptop (o su versión de plataforma), esa es la forma de restaurar el estado exacto anterior.

## Estado del ESP32 al escribir esto
Ver la sección "Estado final" al pie (se actualiza al terminar).

## Limitaciones
- Nada se probó con movimiento: el watchdog del v3, `SET_VEL` ≠ 0, la parada, la regla de `RUN` con Y continuo, el cambio de sentido. Solo comunicación.
- La regresión usa timeout de 1 s: detecta pérdidas pero NO retrasos de decenas de ms; hay que mirar siempre la latencia además de OK/MAL.
- Sin la versión original del core no se sabe si v2/v3 son realmente más lentos que el original o si es el toolchain.

## Fuentes
`control/firmware/diff_exacto/*`, `control/firmware/binarios/*.bin` (SHA-256 en el listado del repo), `pruebas/resultados/regresion_*.json` y `latencia_comandos_2026-11-10_*.csv`, logs de PlatformIO del scratchpad.
