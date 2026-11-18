#!/usr/bin/env bash
# Atajos de la ETAPA 2 (RPi) del ADC con ESP32 de lectura. NO mueve ejes ni abre /dev/ttyUSB*.
# Escrito 2026-11-18; NO probado con el ESP32 de lectura conectado.
#   etapa2_rpi.sh preflight          R0/R1: revisa configuracion y escucha el UART
#   etapa2_rpi.sh r2 [N]             R2: N lecturas (defecto 5000) -> visor en vivo + CSV + figura (CONTRA=csv_L3 la superpone)
#   etapa2_rpi.sh r3 [MIN]           R3: vigilante en reposo MIN minutos (defecto 30) -> visor en vivo + figura final
#   etapa2_rpi.sh r5 [vel1,vel2]     R5: SERVO Y EN EL AIRE -- pide confirmacion de Luis en pantalla
# Puerto del ESP32 de lectura: variable PUERTO_FZ (defecto /dev/ttyAMA0; en Pi 5 /dev/serial0 NO sirve).
set -u
cd "$(dirname "$0")/.."
PUERTO="${PUERTO_FZ:-/dev/ttyAMA0}"
PY="${PYTHON:-python3}"; [ -x .venv/bin/python ] && PY=.venv/bin/python
OUT=pruebas/resultados/etapa2; mkdir -p "$OUT" logs; TS=$(date +%Y%m%d_%H%M%S)
# Visor en vivo en la pantalla del RPi (proceso aparte; no usa serial ni SPI). Se mata por PID (nunca pkill -f).
VISOR_PID=""
visor_on()  { "$PY" herramientas/visor_pruebas.py >/dev/null 2>&1 & VISOR_PID=$!; sleep 1; }
visor_off() { [ -n "$VISOR_PID" ] && kill "$VISOR_PID" 2>/dev/null; VISOR_PID=""; }
trap visor_off EXIT
case "${1:-}" in
  preflight) exec "$PY" pruebas/etapa2_preflight.py --puerto "$PUERTO" ;;
  r2) "$PY" pruebas/etapa2_preflight.py --puerto "$PUERTO" >"$OUT/preflight_$TS.txt" 2>&1 \
        || { cat "$OUT/preflight_$TS.txt"; echo ">> preflight MAL: no se corre R2"; exit 1; }
      visor_on
      "$PY" pruebas/leer_ads1256_fz_esp32_uart.py --puerto "$PUERTO" --n "${2:-5000}" --en_vivo \
        --salida "$OUT/R2_lecturas_$TS.csv" 2>&1 | tee "$OUT/R2_$TS.txt"
      visor_off
      # CONTRA=<csv de L3 en la laptop> superpone esa corrida (criterio: sigma en el RPi ~ sigma en la laptop)
      [ -s "$OUT/R2_lecturas_$TS.csv" ] && "$PY" pruebas/graficar_etapa2.py r2 "$OUT/R2_lecturas_$TS.csv" \
        ${CONTRA:+--contra "$CONTRA"} --mostrar ;;
  r3) visor_on
      "$PY" pruebas/vigilar_adc_esp32_uart.py --puerto "$PUERTO" --minutos "${2:-30}" 2>&1 | tee "$OUT/R3_$TS.txt"
      visor_off
      CSV3=$(ls -t pruebas/resultados/vigilar_adc_esp32_uart_*.csv 2>/dev/null | head -1)
      [ -n "$CSV3" ] && "$PY" pruebas/graficar_etapa2.py r3 "$CSV3" --mostrar ;;
  r5) echo "R5 = Y SE VA A MOVER (<=10 mm, en el aire, hueco >= 100 mm). Luis: manos fuera, paro de emergencia a mano."
      read -r -p "Escribe SI para continuar: " r; [ "$r" = "SI" ] || { echo cancelado; exit 1; }
      visor_on
      "$PY" pruebas/fuerza_vs_velocidad_y.py "${2:-400,800,1600}" --fuente_fz uart --puerto_fz "$PUERTO" 2>&1 | tee "$OUT/R5_$TS.txt"
      visor_off   # el visor se cierra por PID; se deja el estado FINAL como figura en pantalla
      "$PY" herramientas/visor_pruebas.py --png "$OUT/R5_$TS.png" && "$PY" herramientas/mostrar_figura.py "$OUT/R5_$TS.png" >/dev/null 2>&1 & ;;
  *) sed -n 2,11p "$0"; exit 2 ;;
esac
