"""Mide latencia de comunicacion RPi<->ESP32 usando el comando PING/PONG que YA existe
en el firmware actual (communication.h / main.cpp, command_dispatcher). No requiere
tocar el firmware.

Protocolo confirmado leyendo communication.h:
  - 115200 baudios, 8N1.
  - RPi envia: "<PING>"
  - ESP32 responde: "PONG\n"

AVISO (leido en communication.h): el ESP32 espera datos seriales con vTaskDelay(5 ms)
mientras no hay nada disponible -> hasta 5 ms de latencia de sondeo (polling) propios
del firmware se suman a cada medicion. No es latencia del cable ni del AMTI.

Uso en el RPi:
    pip install pyserial
    python medir_latencia_ping_pong.py --puerto /dev/ttyUSB0 --n 100
"""
import argparse
import csv
import statistics
import time

import serial

ap = argparse.ArgumentParser()
ap.add_argument("--puerto", required=True, help="ej. /dev/ttyUSB0 o /dev/ttyACM0")
ap.add_argument("--baud", type=int, default=115200)
ap.add_argument("--n", type=int, default=100)
ap.add_argument("--salida", default="latencia_ping_pong.csv")
ap.add_argument("--timeout_s", type=float, default=1.0)
a = ap.parse_args()

ser = serial.Serial(a.puerto, a.baud, timeout=a.timeout_s)
time.sleep(2.0)  # esperar reset del ESP32 al abrir el puerto serial
ser.reset_input_buffer()

rtts_ms = []
filas = []

for i in range(a.n):
    ser.reset_input_buffer()
    t0 = time.perf_counter()
    ser.write(b"<PING>")
    linea = ser.readline()  # espera hasta timeout_s o '\n'
    t1 = time.perf_counter()

    if not linea.startswith(b"PONG"):
        print(f"[{i}] respuesta inesperada o timeout: {linea!r}")
        filas.append([i, "", "ERROR", linea])
        continue

    rtt_ms = (t1 - t0) * 1000.0
    rtts_ms.append(rtt_ms)
    filas.append([i, round(rtt_ms, 3), "OK", linea.strip()])
    print(f"[{i}] RTT = {rtt_ms:.3f} ms")

ser.close()

with open(a.salida, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["intento", "rtt_ms", "estado", "respuesta_cruda"])
    w.writerows(filas)

if rtts_ms:
    print("\n--- Resumen ---")
    print(f"N validos: {len(rtts_ms)} / {a.n}")
    print(f"RTT medio: {statistics.mean(rtts_ms):.3f} ms")
    print(f"Desviacion estandar: {statistics.pstdev(rtts_ms):.3f} ms")
    print(f"Minimo: {min(rtts_ms):.3f} ms  /  Maximo: {max(rtts_ms):.3f} ms")
    print(f"Latencia de comunicacion unidireccional aprox (RTT/2): {statistics.mean(rtts_ms)/2:.3f} ms")
    print(f"\nRecuerda: hasta 5 ms de este valor puede venir del polling del firmware (vTaskDelay(5ms) en communication_rx), no del cable.")
else:
    print("No se obtuvo ninguna respuesta valida. Revisa el puerto/baudrate.")

print(f"\nCSV guardado en: {a.salida}")
