"""Compara el ruido de Fz del lazo con y sin el filtro de 60 Hz (LectorFzUART), en reposo, SIN mover motores.
No abre el ESP32 de motores. Plato vacio y sin tocarlo.

Uso (RPi): .venv/bin/python -u pruebas/ruido_60hz_filtro.py [--puerto_fz /dev/ttyAMA0] [--segundos 20]
Criterio de paso: sigma con filtro <= 1.0 N y media con filtro a <= 0.3 N de la media sin filtro.
"""
import argparse
import os
import statistics as st
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "control"))
import lazo_fz_tiempo_real as L

ap = argparse.ArgumentParser()
ap.add_argument("--puerto_fz", default="/dev/ttyAMA0")
ap.add_argument("--signo_fz", type=float, default=1.0, choices=[1.0, -1.0])
ap.add_argument("--segundos", type=float, default=20.0)
a = ap.parse_args()

lec = L.LectorFzUART(a.puerto_fz, signo=a.signo_fz)
try:
    f0, p5, p95 = lec.tarar()
    print(f"tara f0 = {f0:.2f} N (p5 {p5:.2f}, p95 {p95:.2f})")
    res = {}
    for modo in (False, True, False, True):
        lec.filtro_60hz = modo
        vals, t0 = [], time.monotonic()
        while time.monotonic() - t0 < a.segundos / 4:
            vals.append(lec.leer_n())
            time.sleep(L.DT_CONTROL_S - 0.007)
        res.setdefault(modo, []).extend(vals)
        print(f"filtro_60hz={modo}: n={len(vals)} sigma {st.pstdev(vals):.2f} N, media {st.mean(vals):.2f} N")
    s_sin, s_con = st.pstdev(res[False]), st.pstdev(res[True])
    dm = abs(st.mean(res[True]) - st.mean(res[False]))
    print(f"\nTOTAL sin filtro sigma {s_sin:.2f} N | con filtro sigma {s_con:.2f} N | diferencia de media {dm:.2f} N")
    ok = s_con <= 1.0 and dm <= 0.3
    print("PASA" if ok else "NO PASA: no usar el filtro en el lazo (--sin_filtro_60hz) y reportar")
finally:
    lec.cerrar()
