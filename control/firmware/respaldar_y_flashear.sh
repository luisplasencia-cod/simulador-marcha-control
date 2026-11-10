#!/usr/bin/env bash
# Respaldo de la flash del ESP32 ANTES de flashear (regla 2026-11-10: se perdio el binario original por no respaldar).
# Uso:  control/firmware/respaldar_y_flashear.sh respaldo               -> lee y guarda 0x0..0x80000 (bootloader+tabla+otadata+app, 512 KB)
#       control/firmware/respaldar_y_flashear.sh flashear <carpeta_pio>  -> respalda, luego flashea esa carpeta PlatformIO
#       control/firmware/respaldar_y_flashear.sh restaurar <archivo.bin> -> escribe un respaldo completo en 0x0
# Medido 2026-11-10: la lectura va a ~4 KB/s por este CP2102 (4 MB = ~17 min, NO practico): por eso solo la zona de arranque+app. TAM=0x400000 para todo.
# Requiere el venv de PlatformIO (PIO_VENV) y su core (PLATFORMIO_CORE_DIR). Puerto: PUERTO (default /dev/ttyUSB0).
# NO mueve ejes, pero reinicia el ESP32 (y el firmware libera el freno vertical en setup()): avisar a Luis antes.
set -euo pipefail
PUERTO="${PUERTO:-/dev/ttyUSB0}"
PIO_VENV="${PIO_VENV:?definir PIO_VENV (carpeta del venv con platformio)}"
ESPTOOL="$(ls -d "${PLATFORMIO_CORE_DIR:-$HOME/.platformio}"/packages/tool-esptoolpy*/esptool.py | head -1)"
DEST="$(dirname "$0")/respaldos_flash"; mkdir -p "$DEST"
respaldar(){ f="$DEST/flash_0x0_""${TAM:-0x80000}""_$(date +%Y%m%d_%H%M%S).bin"
  "$PIO_VENV/bin/python" "$ESPTOOL" --chip esp32 --port "$PUERTO" --baud 460800 read_flash 0x0 "${TAM:-0x80000}" "$f"
  [ -s "$f" ] || { echo "ERROR: el respaldo NO se escribio"; exit 1; }
  sha256sum "$f" | tee "$f.sha256"; echo "RESPALDO: $f"; }
case "${1:-}" in
  respaldo) respaldar ;;
  flashear) respaldar; ( cd "$2" && "$PIO_VENV/bin/pio" run -t upload --upload-port "$PUERTO" ) ;;
  restaurar) "$PIO_VENV/bin/python" "$ESPTOOL" --chip esp32 --port "$PUERTO" --baud 460800 write_flash 0x0 "$2" ;;
  *) sed -n 2,8p "$0"; exit 1 ;;
esac
