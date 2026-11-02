"""Calibracion de Fz con pesas conocidas (AMTI -> ADS1256 -> RPi).

Uso (interactivo, cada paso espera Enter):
    python pruebas/calibracion_pesas.py --masas 0 5 10 20 [--seg 2]
Masas en kg, en el orden en que las vas poniendo. Incluye 0 (plato vacio) como referencia.
Ajusta V = a*F + b con F = m*g, compara la pendiente con 1.7665 mV/N y reporta el signo.
"""
import argparse
import csv
import statistics as st
import sys
import time

from leer_ads1256_fz import ADS1256, N_PER_1000N

G = 9.80665  # m/s^2 (gravedad estandar; la local en Lima difiere ~0.05%)

ap = argparse.ArgumentParser()
ap.add_argument("--masas", type=float, nargs="+", required=True, help="kg, en orden")
ap.add_argument("--seg", type=float, default=2.0, help="segundos de captura por paso")
ap.add_argument("--espera", type=float, default=20.0, help="s de cuenta regresiva por paso si no hay teclado")
ap.add_argument("--salida", default="pruebas/calibracion_pesas.csv")
a = ap.parse_args()

adc = ADS1256()
filas = []
try:
    for m in a.masas:
        msg = f"\nPon {m:g} kg ({m*G:.2f} N) en el AMTI"
        if sys.stdin.isatty():
            input(msg + ", espera que se asiente y presiona Enter... ")
        else:
            print(msg + f" - mido en {a.espera:g} s...", flush=True)
            time.sleep(a.espera)
        adc.leer_volts()
        v = []
        t0 = time.perf_counter()
        while time.perf_counter() - t0 < a.seg:
            v.append(adc.leer_volts())
        media, sd = st.mean(v), st.pstdev(v)
        print(f"  {len(v)} muestras: {media*1000:+.3f} mV  (sigma {sd*1000:.3f} mV = {sd*1000/N_PER_1000N:.2f} N)")
        filas.append((m, m * G, media, sd, len(v)))
finally:
    adc.cerrar()

with open(a.salida, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["masa_kg", "F_N", "V_medio", "V_sigma", "n"])
    w.writerows(filas)

if len(filas) >= 2:
    x = [r[1] for r in filas]
    y = [r[2] * 1000 for r in filas]  # mV
    mx, my = st.mean(x), st.mean(y)
    sxx = sum((xi - mx) ** 2 for xi in x)
    pend = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y)) / sxx
    off = my - pend * mx
    res = [yi - (pend * xi + off) for xi, yi in zip(x, y)]
    ss_tot = sum((yi - my) ** 2 for yi in y)
    r2 = 1 - sum(r * r for r in res) / ss_tot if ss_tot else float("nan")
    esp = N_PER_1000N  # mV/N
    print(f"\nPendiente medida: {pend:+.4f} mV/N   (esperada {esp:+.4f})   error {100*(abs(pend)-esp)/esp:+.2f}%")
    print(f"Offset (plato vacio): {off:+.3f} mV = {off/pend:+.2f} N   R^2 = {r2:.5f}")
    print(f"Residuo maximo: {max(abs(r) for r in res):.3f} mV ({max(abs(r) for r in res)/abs(pend):.2f} N)")
    print("Signo: " + ("OK, carga hacia abajo da voltaje positivo" if pend > 0 else "INVERTIDO, carga da voltaje negativo"))
