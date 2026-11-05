"""Captura CRUDA de Fz (ADS1256, 1000 SPS) para caracterizar el ruido y elegir el filtro.
ESCRITO 2026-11-05, NO EJECUTADO todavia. Procedimiento y criterios: reportes/2026-11-05_ruido_fz.md

Condiciones (una captura por condicion, MISMA configuracion del amplificador: excitacion 10 V, ganancia 2000):
  vacio_quieto          plato vacio, motores APAGADOS (ni energizados)         -> piso de ruido del AMTI+ADC
  motores_energizados   plato vacio, drivers ENERGIZADOS (servo ON), SIN moverse -> ruido por drivers/fuentes
  motores_moviendo      plato vacio, ejes moviendose SIN carga (sin prototesis)  -> ruido por movimiento/vibracion
(Solo la tercera mueve motores: hay que lanzarla con el simulador despejado y manos fuera; este script NO
manda nada al ESP32, solo lee el ADC. Los movimientos los lanza Luis aparte, p.ej. desde el monitor/herramienta
habitual, y anota la hora de inicio.)

IMPORTANTE: el monitor (herramientas/monitor_gaitsim.py) y este script NO pueden usar el SPI a la vez:
cierra el monitor antes. El script lo comprueba y aborta si lo encuentra abierto.

Uso:
  .venv/bin/python pruebas/capturar_ruido_fz.py --condicion vacio_quieto --duracion 120
Salida: pruebas/ruido_fz_<condicion>_<fecha>.csv  con columnas
  indice, t_perf_s, volts, newtons_crudos      (t_perf_s = perf_counter al leer; NO es el instante de conversion)
y un resumen por pantalla (muestras/s, dt>1.5 ms, estimacion de muestras perdidas).
Como RDATAC sobreescribe sin avisar, las muestras perdidas solo se detectan por huecos de tiempo:
si 'perdidas estimadas' > 0.5 % la captura NO sirve para espectro (repetir; con menos carga de CPU).
"""
import argparse
import csv
import os
import sys
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from leer_ads1256_fz import ADS1256, volts_a_newtons  # noqa: E402

CONDICIONES = ("vacio_quieto", "motores_energizados", "motores_moviendo")


def monitor_abierto():
    yo = os.getpid()
    for pid in filter(str.isdigit, os.listdir("/proc")):
        if int(pid) == yo:
            continue
        try:
            with open(f"/proc/{pid}/cmdline", "rb") as f:
                if b"monitor_gaitsim" in f.read():
                    return int(pid)
        except OSError:
            pass
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--condicion", required=True, choices=CONDICIONES)
    ap.add_argument("--duracion", type=float, default=120.0, help="segundos (>=60 recomendado)")
    ap.add_argument("--salida", default=None)
    a = ap.parse_args()

    pid = monitor_abierto()
    if pid:
        raise SystemExit(f"El monitor sigue abierto (PID {pid}): cierralo antes (el SPI no es compartible).")

    n_obj = int(a.duracion * 1000)
    adc = ADS1256()
    t = []
    v = []
    try:
        print(f"Capturando {a.duracion:.0f} s en condicion '{a.condicion}'... no tocar el plato.")
        for _ in range(n_obj):
            volt = adc.leer_volts()
            t.append(time.perf_counter())
            v.append(volt)
    finally:
        adc.cerrar()

    salida = a.salida or os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        f"ruido_fz_{a.condicion}_{datetime.now():%Y%m%d_%H%M%S}.csv")
    with open(salida, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["indice", "t_perf_s", "volts", "newtons_crudos"])
        for i, (ti, vi) in enumerate(zip(t, v)):
            w.writerow([i, f"{ti - t[0]:.6f}", f"{vi:.7f}", f"{volts_a_newtons(vi):.4f}"])

    dur = t[-1] - t[0]
    huecos = [t[i + 1] - t[i] for i in range(len(t) - 1)]
    n_huecos = sum(1 for d in huecos if d > 1.5e-3)
    perdidas = max(0.0, dur * 1000 - (len(t) - 1))
    n = [volts_a_newtons(x) for x in v]
    m = sum(n) / len(n)
    sd = (sum((x - m) ** 2 for x in n) / len(n)) ** 0.5
    print(f"{len(t)} muestras en {dur:.2f} s -> {(len(t)-1)/dur:.1f} muestras/s (esperado 1000)")
    print(f"dt > 1.5 ms: {n_huecos}; perdidas estimadas: {perdidas:.0f} ({100*perdidas/(dur*1000):.2f} %)")
    print(f"Fz crudo: media {m:.2f} N, sigma {sd:.3f} N, pico-pico {max(n)-min(n):.2f} N")
    print(f"CSV: {salida}")


if __name__ == "__main__":
    main()
