"""Lee la fuerza Fz del AMTI, calculada por el ESP32 dedicado al ADC
(firmware en `Codigo ESP32 ADS1256/platformIO_medicion_sensores_v1/src/main.cpp`).

Esta es una arquitectura DISTINTA a `leer_ads1256_fz.py`: ese script asumia que
el RPi lee el ADS1256 el mismo, por SPI/GPIO directo. En este firmware, en
cambio, un ESP32 aparte (nombre Bluetooth "ESP32_simulador") lee el ADS1256
por su propio bus SPI y manda el valor de fuerza ya calculado al RPi por
UART2 (pines ESP32 RX=16, TX=17), a 115200 baudios, en paquetes:

    <force>

(un solo numero, 3 decimales, entre '<' y '>'). Verificar con el main.cpp
del firmware si cambia el formato o NUM_PARAMETERS.

Diferencia importante respecto a lo documentado antes para el ADS1256 conectado
directo al RPi (ver esquemas/amti_ads1256_rpi/CONFIGURACION_ACTUAL.md):
  - MUX del ADS1256 en ESTE firmware: diferencial AIN1(+) - AIN0(-)
    (ADS1256_MUX_AIN1_AIN0 = 0x10), NO single-ended AIN0 vs AINCOM/GND.
    Son dos configuraciones de cableado distintas - no mezclar los pines de
    una con la otra.
  - Sensibilidad usada en el firmware: 1.7631 mV/N (mas precisa que el
    1.7 V/1000N usado antes - revisar con Luis cual es la medicion vigente).
  - VREF = 2.5V igual que antes (ADR03B), PGA=1, full-scale = 5V - coherente.

Uso (en el RPi, con el ESP32-ADS1256 conectado por USB o por UART2->USB-TTL):
    pip install pyserial
    python leer_fz_esp32_ads1256.py --puerto /dev/ttyUSB0 --n 200
"""
import argparse
import csv
import re
import time

import serial

PATRON_PAQUETE = re.compile(r"<([-\d.]+)>")


def leer_fuerzas(puerto, baudrate, n, timeout_s):
    ser = serial.Serial(puerto, baudrate, timeout=timeout_s)
    filas = []
    buffer = ""
    t_inicio = time.monotonic()
    try:
        while len(filas) < n:
            chunk = ser.read(ser.in_waiting or 1).decode("ascii", errors="ignore")
            if not chunk:
                if time.monotonic() - t_inicio > timeout_s * n:
                    print("Timeout esperando paquetes - revisar puerto/cableado/firmware.")
                    break
                continue
            buffer += chunk
            for m in PATRON_PAQUETE.finditer(buffer):
                filas.append([len(filas), time.monotonic() - t_inicio, float(m.group(1))])
                if len(filas) >= n:
                    break
            ultimo = buffer.rfind(">")
            if ultimo != -1:
                buffer = buffer[ultimo + 1:]
    finally:
        ser.close()
    return filas


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--puerto", default="/dev/ttyUSB0")
    ap.add_argument("--baudrate", type=int, default=115200)
    ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--timeout_s", type=float, default=1.0)
    ap.add_argument("--salida", default="lecturas_fz_esp32.csv")
    a = ap.parse_args()

    filas = leer_fuerzas(a.puerto, a.baudrate, a.n, a.timeout_s)

    with open(a.salida, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["intento", "t_s", "fz_newtons"])
        w.writerows(filas)

    if filas:
        valores = [r[2] for r in filas]
        print(f"Leidos {len(filas)} paquetes. Fz: min={min(valores):.2f} N, max={max(valores):.2f} N")
        print("Con 0 N reales aplicados, deberia estar cerca de 0 (si no, hay offset de cero pendiente).")
    print(f"CSV guardado en: {a.salida}")
