"""Guarda el diagnostico que el ESP32 de lectura imprime por su USB (main.cpp, 2026-11-18):
informe de arranque (motivo del reinicio, registros del ADS1256) + una linea CSV por segundo.
Pensado para la ETAPA LAPTOP (ver INICIO_RPI.md): no hace falta adaptador, solo el cable USB.
Al abrir el puerto el ESP32 se REINICIA (DTR/RTS): es a proposito, asi queda el informe de arranque.

Uso: python registrar_diag_esp32_usb.py --puerto COM7 --minutos 30
"""
import argparse, os, time
import serial

ap = argparse.ArgumentParser()
ap.add_argument("--puerto", required=True)
ap.add_argument("--minutos", type=float, default=30.0)
a = ap.parse_args()

R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
os.makedirs(os.path.join(R, "pruebas", "resultados"), exist_ok=True)
ruta = os.path.join(R, "pruebas", "resultados", time.strftime("diag_esp32_usb_%Y%m%d_%H%M%S.txt"))

ser = serial.Serial(a.puerto, 115200, timeout=0.5)
fin = time.monotonic() + a.minutos * 60
alertas = 0
with open(ruta, "w", buffering=1) as f:
    while time.monotonic() < fin:
        linea = ser.readline().decode("ascii", errors="replace").strip()
        if not linea or linea.startswith("F,"):   # F,<valor> = copia a 100/s para el visor
            continue
        f.write(f"{time.strftime('%H:%M:%S')} {linea}\n")
        campos = linea.split(",")
        es_resumen = len(campos) >= 11 and campos[0].isdigit()
        problema = ("ERROR" in linea or "ALERTA" in linea or "BROWNOUT" in linea or "PANIC" in linea
                    or (es_resumen and campos[1].isdigit() and any(c not in ("", "0") for c in campos[7:10])))
        if problema:
            alertas += 1
        if not es_resumen or problema or campos[0].endswith("0"):   # resumen OK: 1 de cada 10 s
            print(linea, flush=True)
ser.close()
print(f"fin: {alertas} lineas con problema (ERROR/ALERTA/perdidas/ceros/saturadas). Registro: {ruta}")
