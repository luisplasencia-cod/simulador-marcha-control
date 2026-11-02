"""Latencia RPi<->ESP32 con comandos REALES del firmware (no solo PING).

Comandos de solo lectura (no mueven nada): PING, GET_POSITION, TRAJ_STATUS.
Con --mover (OPT-IN, mueve el eje K/sagital unos pasos y lo regresa):
mide ademas el RTT del ack "OK" de MANUAL. Asegurate de que el simulador
este libre (sin personas ni prótesis atascada) antes de usar --mover.

Uso:
    .venv/bin/python pruebas/medir_latencia_comandos.py --n 100
    .venv/bin/python pruebas/medir_latencia_comandos.py --n 20 --mover --pasos 40
"""
import argparse
import csv
import statistics
import time

import serial

ap = argparse.ArgumentParser()
ap.add_argument("--puerto", default="/dev/ttyUSB0")
ap.add_argument("--n", type=int, default=100)
ap.add_argument("--mover", action="store_true")
ap.add_argument("--eje", type=int, default=2, help="0=X 1=Y 2=K(sagital)")
ap.add_argument("--pasos", type=int, default=40)
ap.add_argument("--salida", default="pruebas/latencia_comandos.csv")
a = ap.parse_args()

ser = serial.Serial()
ser.port, ser.baudrate, ser.timeout = a.puerto, 115200, 1.0
ser.dtr = False  # evitar reset del ESP32 al abrir (perderia la posicion)
ser.rts = False
ser.open()
ser.reset_input_buffer()


def rtt(cmd):
    ser.reset_input_buffer()
    t0 = time.perf_counter()
    ser.write(f"<{cmd}>".encode())
    r = ser.readline()
    t1 = time.perf_counter()
    return (t1 - t0) * 1000.0, r.decode(errors="replace").strip()


filas, resumen = [], {}


def bloque(nombre, cmd, n):
    vals, ultima = [], ""
    for i in range(n):
        ms, r = rtt(cmd)
        filas.append([nombre, i, round(ms, 3), r])
        if r:
            vals.append(ms)
            ultima = r
        time.sleep(0.02)
    resumen[nombre] = (vals, ultima)


bloque("PING", "PING", a.n)
bloque("GET_POSITION", "GET_POSITION", a.n)
bloque("TRAJ_STATUS", "TRAJ_STATUS", a.n)

if a.mover:
    vals = []
    for i in range(a.n):
        for signo in (+1, -1):
            ms, r = rtt(f"MANUAL:{a.eje}:{signo * a.pasos}")
            filas.append(["MANUAL", i, round(ms, 3), r])
            if r.startswith("OK"):
                vals.append(ms)
            time.sleep(1.0)  # dejar terminar el movimiento antes del siguiente (si no -> BUSY)
    resumen["MANUAL(ack)"] = (vals, "OK")

ser.close()
with open(a.salida, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["comando", "intento", "rtt_ms", "respuesta"])
    w.writerows(filas)

print(f"{'comando':<14}{'N':>5}{'media':>9}{'desv':>8}{'min':>8}{'max':>8}  ultima respuesta")
for k, (v, r) in resumen.items():
    if v:
        print(f"{k:<14}{len(v):>5}{statistics.mean(v):>9.3f}{statistics.pstdev(v):>8.3f}{min(v):>8.3f}{max(v):>8.3f}  {r}")
    else:
        print(f"{k:<14}{0:>5}  sin respuesta")
print(f"\nCSV: {a.salida}")
