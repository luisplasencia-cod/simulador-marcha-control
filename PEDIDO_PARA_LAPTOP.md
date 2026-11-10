# Pedido de la sesión RPi a la sesión de la laptop (2026-11-10)

Contexto: en la Pi flasheé firmware al ESP32 SIN respaldar el binario original; se perdió. El código fuente está en el repo, pero compilado en la Pi (espressif32@6.5.0, core 2.0.14) el original responde peor (82/100) que tu binario (100/100, GET_POSITION 4.94 ms). Necesito tu build real como base.

## Lo que hay que subir al repo (commit + push desde la laptop)
1. **El `firmware.bin` original** de la laptop: `Codigo ESP32 MOV/platformIO_control_trayectoria_v1/.pio/build/esp32dev/firmware.bin`. Si existen, también `bootloader.bin` y `partitions.bin` de la misma carpeta. Copiarlos a `control/firmware/binarios/original_laptop/` y anotar su SHA-256 (`sha256sum`).
2. **`platformio.ini` tal como compila en la laptop** y el resultado de `pio pkg list` (o `pio platform show espressif32`) para saber la versión EXACTA de la plataforma y del framework Arduino. Guardar la salida en `control/firmware/binarios/original_laptop/versiones_pio.txt`.
3. Confirmar si el firmware que está en el ESP32 desde antes de hoy coincide con ese código (fecha del último flasheo desde la laptop, si la recuerdas).

## Reglas
- No tocar `main.cpp`, `communication.h` ni el parche; solo agregar esos archivos.
- Después avisar a Luis; en la Pi se hace `git pull` y se compara con el original recompilado.
