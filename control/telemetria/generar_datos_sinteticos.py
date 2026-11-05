"""Genera un log sintetico con el formato de formato_log.md, para probar visor_en_vivo.py
SIN RPi ni ESP32 (no hay hardware en esta sesion).

Reusa la misma fisica de ../simulacion/rt_vs_ilc_latencia.py (servo + contacto + ILC), pero
escribe cada muestra al CSV en vez de solo devolver el RMS -- aqui es donde se necesitan
t, u(t) y delta(t) punto por punto, que la simulacion original no guarda.

Uso:
    python generar_datos_sinteticos.py                 # escribe todo de una vez
    python generar_datos_sinteticos.py --en-vivo        # simula llegada en tiempo real
                                                         # (duerme entre muestras, para
                                                         # probar visor_en_vivo.py de verdad)
"""
import argparse
import csv
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "simulacion"))
import rt_vs_ilc_latencia as sim  # noqa: E402

AP = argparse.ArgumentParser()
AP.add_argument("--en-vivo", action="store_true", help="dormir entre muestras para simular tiempo real")
AP.add_argument("--ciclos", type=int, default=12)
AP.add_argument("--latencia-ms", type=float, default=10.0)
AP.add_argument("--salida", default=None)
A = AP.parse_args()

REGISTROS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "registros")
os.makedirs(REGISTROS, exist_ok=True)
salida = A.salida or os.path.join(REGISTROS, time.strftime("%Y%m%d_%H%M%S") + "_fz_SINTETICO.csv")

DT = sim.DT
T = A.latencia_ms / 1000.0
n = int(sim.CFG["tc"] / DT)
ref = sim.referencia(n)
m = int(round((T + 1.0 / sim.KP) / DT))
cola = [0.0] * (int(round(T / DT)) + 1)
delta = np.zeros(n)
F = v = 0.0
t_abs = 0.0

print(f"Generando {A.ciclos} ciclos sintéticos (NO es dato real) -> {salida}")
with open(salida, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["t", "ciclo", "r", "delta", "r_corregida", "F_med", "e", "u"])
    for j in range(A.ciclos):
        e_ciclo = np.empty(n)
        for i in range(n):
            cola.append(F)
            Fm = cola.pop(0)
            r_corr = ref[i] + delta[i]
            e = r_corr - Fm
            u = sim.KP * e
            v += DT * (u - v) / sim.TAU_A
            F += DT * (sim.K_REAL * v)
            w.writerow([f"{t_abs:.4f}", j, f"{ref[i]:.3f}", f"{delta[i]:.3f}",
                        f"{r_corr:.3f}", f"{Fm:.3f}", f"{e:.3f}", f"{u:.3f}"])
            e_ciclo[i] = e
            t_abs += DT
            if A.en_vivo and i % 20 == 0:
                f.flush()
                time.sleep(DT * 20)
        e_adel = np.r_[e_ciclo[m:], np.zeros(m)]
        delta = sim.suavizar(delta + sim.GAMMA * e_adel, int(0.1 / DT))
    f.flush()

print("listo.")
