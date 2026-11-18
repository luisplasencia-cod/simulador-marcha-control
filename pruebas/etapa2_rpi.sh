#!/usr/bin/env bash
# Atajos de la ETAPA 2 (RPi) del ADC con ESP32 de lectura. NO mueve ejes ni abre /dev/ttyUSB*.
# Escrito 2026-11-18; NO probado con el ESP32 de lectura conectado.
#   etapa2_rpi.sh preflight          R0/R1: revisa configuracion y escucha el UART
#   etapa2_rpi.sh r2 [N]             R2: N lecturas (defecto 5000) -> CSV + salida guardada
#   etapa2_rpi.sh r3 [MIN]           R3: vigilante en reposo MIN minutos (defecto 30)
#   etapa2_rpi.sh r5 [vel1,vel2]     R5: SERVO Y EN EL AIRE -- pide confirmacion de Luis en pantalla
# Puerto del ESP32 de lectura: variable PUERTO_FZ (defecto /dev/ttyAMA0; en Pi 5 /dev/serial0 NO sirve).
set -u
cd "$(dirname "$0")/.."
PUERTO="${PUERTO_FZ:-/dev/ttyAMA0}"
PY="${PYTHON:-python3}"; [ -x .venv/bin/python ] && PY=.venv/bin/python
OUT=pruebas/resultados/etapa2; mkdir -p "$OUT"; TS=$(date +%Y%m%d_%H%M%S)
case "${1:-}" in
  preflight) exec "$PY" pruebas/etapa2_preflight.py --puerto "$PUERTO" ;;
  r2) "$PY" pruebas/etapa2_preflight.py --puerto "$PUERTO" >"$OUT/preflight_$TS.txt" 2>&1 \
        || { cat "$OUT/preflight_$TS.txt"; echo ">> preflight MAL: no se corre R2"; exit 1; }
      "$PY" pruebas/leer_ads1256_fz_esp32_uart.py --puerto "$PUERTO" --n "${2:-5000}" \
        --salida "$OUT/R2_lecturas_$TS.csv" 2>&1 | tee "$OUT/R2_$TS.txt" ;;
  r3) "$PY" pruebas/vigilar_adc_esp32_uart.py --puerto "$PUERTO" --minutos "${2:-30}" 2>&1 | tee "$OUT/R3_$TS.txt" ;;
  r5) echo "R5 = Y SE VA A MOVER (<=10 mm, en el aire, hueco >= 100 mm). Luis: manos fuera, paro de emergencia a mano."
      read -r -p "Escribe SI para continuar: " r; [ "$r" = "SI" ] || { echo cancelado; exit 1; }
      "$PY" pruebas/fuerza_vs_velocidad_y.py "${2:-400,800,1600}" --fuente_fz uart --puerto_fz "$PUERTO" 2>&1 | tee "$OUT/R5_$TS.txt" ;;
  *) sed -n 2,9p "$0"; exit 2 ;;
esac
