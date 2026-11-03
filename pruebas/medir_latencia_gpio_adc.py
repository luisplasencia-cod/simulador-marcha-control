"""Latencia de adquisicion RPi + ADS1256 con escalon ELECTRICO (sin video).

Un GPIO del RPi (GPIO27, 3.3 V a traves de un divisor ~10k/10k -> ~1.65 V) alimenta un
canal libre del ADS1256 (AIN1 vs AINCOM, MUX=0x18). El instante del flanco (t0) y el de
deteccion (t_det) salen del MISMO reloj (time.perf_counter_ns), asi que la diferencia es
el retardo de: filtro digital del ADS1256 + SPI + software Python.

NO incluye el retardo del amplificador analogico del AMTI (eso sale del manual AMTI, no se mide
aqui y no se inventa). Latencia de adquisicion total = este resultado + retardo AMTI (manual).

Cableado (por confirmar en la etiqueta fisica de la placa - ver CLAUDE.md 2026-11-03):
    GPIO27 --[10k]--+--[10k]-- GND(RPi)
                    +--> AIN1 (ADS1256)      GND de AIN1 (= AINCOM) comun con GND del RPi

Incertidumbre de t0: se toma justo ANTES de GPIO.output() (cota superior). La llamada tarda
algunas decenas de us; se reporta como incertidumbre, no se resta.

IMPORTANTE: cerrar antes `herramientas/monitor_gaitsim.py` (reserva GPIO17/DRDY y SPI0).

Uso:
    python pruebas/medir_latencia_gpio_adc.py --n 200 --salida pruebas/latencia_gpio_adc.csv
"""
import argparse
import csv
import random
import statistics as st
import sys
import time
from pathlib import Path

import RPi.GPIO as GPIO

sys.path.insert(0, str(Path(__file__).resolve().parent))
from leer_ads1256_fz import ADS1256, DRDY_PIN, FULL_SCALE_V  # noqa: E402

PIN_ESCALON = 27
MUX_AIN1_AINCOM = 0x18  # PSEL=AIN1, NSEL=AINCOM
T_MAX_S = 0.100         # si no se detecta en 100 ms, el evento falla (cableado?)


def leer_ahora(adc):
    """Espera DRDY (busy-wait, sin sleep) y devuelve (volts, t_ns tomado DESPUES de leer)."""
    while GPIO.input(DRDY_PIN) == 1:
        pass
    b = adc.spi.xfer2([0, 0, 0])
    t = time.perf_counter_ns()
    raw = (b[0] << 16) | (b[1] << 8) | b[2]
    if raw & 0x800000:
        raw -= 1 << 24
    return raw * FULL_SCALE_V / (1 << 23), t


def nivel_estable(adc, n=30):
    return st.mean(leer_ahora(adc)[0] for _ in range(n))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=200, help="numero de escalones (subida+bajada alternados)")
    ap.add_argument("--salida", default="pruebas/latencia_gpio_adc.csv")
    a = ap.parse_args()

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PIN_ESCALON, GPIO.OUT, initial=GPIO.LOW)
    adc = ADS1256(mux=MUX_AIN1_AINCOM)
    try:
        # Niveles de referencia
        GPIO.output(PIN_ESCALON, GPIO.LOW);  time.sleep(0.2); v_lo = nivel_estable(adc)
        GPIO.output(PIN_ESCALON, GPIO.HIGH); time.sleep(0.2); v_hi = nivel_estable(adc)
        GPIO.output(PIN_ESCALON, GPIO.LOW);  time.sleep(0.2)
        print(f"Nivel bajo = {v_lo*1000:.1f} mV | nivel alto = {v_hi*1000:.1f} mV | salto = {(v_hi-v_lo)*1000:.1f} mV")
        if (v_hi - v_lo) < 0.5:
            sys.exit("Salto < 0.5 V: el GPIO no llega a AIN1 (revisar divisor/cableado/MUX). Abortado.")
        umb50 = v_lo + 0.5 * (v_hi - v_lo)
        umb90 = v_lo + 0.9 * (v_hi - v_lo)

        filas, estado = [], False
        for i in range(a.n):
            time.sleep(random.uniform(0.020, 0.070))  # fase aleatoria respecto al muestreo del ADC
            subida = not estado
            objetivo_50 = (lambda v: v > umb50) if subida else (lambda v: v < umb50)
            objetivo_90 = (lambda v: v > umb90) if subida else (lambda v: v < umb90)
            t0 = time.perf_counter_ns()
            GPIO.output(PIN_ESCALON, GPIO.HIGH if subida else GPIO.LOW)
            t50 = t90 = None
            while True:
                v, t = leer_ahora(adc)
                if t50 is None and objetivo_50(v):
                    t50 = t
                if objetivo_90(v):
                    t90 = t
                    break
                if (t - t0) > T_MAX_S * 1e9:
                    break
            estado = subida
            filas.append([i, "subida" if subida else "bajada",
                          (t50 - t0) / 1e6 if t50 else "", (t90 - t0) / 1e6 if t90 else ""])
        GPIO.output(PIN_ESCALON, GPIO.LOW)
    finally:
        adc.cerrar()

    Path(a.salida).parent.mkdir(parents=True, exist_ok=True)
    with open(a.salida, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["evento", "flanco", "ms_hasta_50pct", "ms_hasta_90pct"])
        w.writerows(filas)

    for col, nombre in ((2, "50 % del escalon"), (3, "90 % del escalon")):
        x = [r[col] for r in filas if r[col] != ""]
        fallos = len(filas) - len(x)
        if x:
            xs = sorted(x)
            print(f"{nombre}: n={len(x)} fallos={fallos} media={st.mean(x):.3f} ms  "
                  f"sigma={st.pstdev(x):.3f} ms  min={xs[0]:.3f}  p95={xs[int(0.95*(len(xs)-1))]:.3f}  max={xs[-1]:.3f}")
        else:
            print(f"{nombre}: sin detecciones")
    print(f"CSV: {a.salida}")


if __name__ == "__main__":
    main()
