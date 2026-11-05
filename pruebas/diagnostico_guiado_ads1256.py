#!/usr/bin/env python3
"""Diagnostico guiado del ADS1256: encuentra contactos flojos cable por cable.

Escribe MUX/ADCON/DRATE y los lee de vuelta ~20 veces/s. Muestra en pantalla
OK / MAL en grande, y te va pidiendo mover (reasentar) un cable a la vez.
Al final dice en que paso cambio el estado. NO usa el AMTI (puede estar
desconectado). Ctrl+C para salir en cualquier momento.

Uso:  python3 pruebas/diagnostico_guiado_ads1256.py
"""
import select
import sys
import time

import RPi.GPIO as GPIO
import spidev

DRDY_PIN = 17
ESCRIBE = [0x08, 0x00, 0xA1]  # MUX, ADCON, DRATE

# (nombre, pin de la placa, pin/GPIO del RPi, donde)
PASOS = [
    ("LINEA BASE", "-", "-", "No toques nada: ve como esta ahora."),
    ("GND", "GND (lado digital)", "pin 6 / GND", "Reasienta el cable de GND en AMBOS extremos."),
    ("5V", "5V", "pin 2 o 4", "Reasienta el cable de 5V en AMBOS extremos."),
    ("SCLK", "SCLK", "GPIO11 / pin 23", "Reasienta el cable SCLK en AMBOS extremos."),
    ("DIN", "DIN", "GPIO10 / pin 19", "Reasienta el cable DIN en AMBOS extremos."),
    ("DOUT", "DOUT", "GPIO9 / pin 21", "Reasienta el cable DOUT en AMBOS extremos."),
    ("CS", "CS", "GPIO8 / pin 24", "Reasienta el cable CS en AMBOS extremos."),
    ("DRDY", "DRDY", "GPIO17 / pin 11", "Reasienta el cable DRDY en AMBOS extremos."),
    ("PDWN", "PDWN", "+3.3V / pin 1", "Reasienta el cable PDWN en AMBOS extremos."),
]

VERDE, ROJO, AMARILLO, NEGRITA, FIN = "\033[92m", "\033[91m", "\033[93m", "\033[1m", "\033[0m"


def leer_tecla():
    """True si el usuario presiono ENTER (no bloqueante)."""
    if select.select([sys.stdin], [], [], 0)[0]:
        linea = sys.stdin.readline()
        return linea != ""  # EOF no cuenta como ENTER
    return False


def ciclo(spi):
    """Un ciclo: escribe 3 registros, los lee. Devuelve (ok, leido)."""
    spi.xfer2([0x0F])  # SDATAC
    spi.xfer2([0x51, 0x02] + ESCRIBE)  # WREG desde MUX, 3 registros
    time.sleep(0.0001)
    r = spi.xfer2([0x11, 0x02, 0, 0, 0])  # RREG desde MUX, 3 registros
    leido = r[2:5]
    return leido == ESCRIBE, leido


def main():
    spi = spidev.SpiDev()
    spi.open(0, 0)
    spi.max_speed_hz = 500_000
    spi.mode = 0b01
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(DRDY_PIN, GPIO.IN)
    resultados = []  # (nombre, n_ok, n_total, cambios)
    try:
        spi.xfer2([0xFE])  # RESET
        time.sleep(0.05)
        for idx, (nombre, borne, rpi, texto) in enumerate(PASOS):
            n_ok = n_tot = cambios = 0
            ultimo = None
            hist = []
            t_ini = time.time()
            while True:
                ok, leido = ciclo(spi)
                n_tot += 1
                n_ok += ok
                if ultimo is not None and ok != ultimo:
                    cambios += 1
                ultimo = ok
                hist.append("#" if ok else ".")
                hist = hist[-50:]
                if n_tot % 4 == 0:
                    estado = f"{VERDE}{NEGRITA}  ===  OK  ===  {FIN}" if ok else f"{ROJO}{NEGRITA}  ===  MAL ===  {FIN}"
                    pct = 100 * n_ok / n_tot
                    sys.stdout.write("\033[2J\033[H")
                    print(f"{NEGRITA}DIAGNOSTICO GUIADO ADS1256{FIN}   paso {idx + 1}/{len(PASOS)}: {NEGRITA}{nombre}{FIN}\n")
                    print(f"  ESTADO AHORA:{estado}")
                    print(f"  leido MUX/ADCON/DRATE = {[hex(x) for x in leido]}   (esperado {[hex(x) for x in ESCRIBE]})")
                    print(f"  ultimos 50 ciclos:  {''.join(hist)}      (# = OK, . = MAL)")
                    print(f"  en este paso: {pct:.0f}% OK, {cambios} cambios OK<->MAL, {time.time() - t_ini:.0f} s\n")
                    print(f"{AMARILLO}  QUE HACER:{FIN} {texto}")
                    if borne != "-":
                        print(f"     placa: {borne}      RPi: {rpi}")
                    print("     Mira si el estado pasa de MAL a OK (o al reves) cuando lo mueves.")
                    print("\n  Cuando termines con este cable, presiona ENTER para el siguiente.")
                    sys.stdout.flush()
                if leer_tecla():
                    break
                time.sleep(0.02)
            resultados.append((nombre, n_ok, n_tot, cambios))
    except KeyboardInterrupt:
        pass
    finally:
        spi.close()
        GPIO.cleanup()

    print("\033[2J\033[H" + f"{NEGRITA}RESUMEN{FIN}\n")
    print(f"  {'paso':<12}{'% OK':>6}{'cambios':>9}")
    for nombre, n_ok, n_tot, cambios in resultados:
        pct = 100 * n_ok / max(n_tot, 1)
        marca = f"  {AMARILLO}<-- cambio de estado aqui{FIN}" if cambios else ""
        print(f"  {nombre:<12}{pct:>5.0f}%{cambios:>9}{marca}")
    if resultados:
        total_ok = sum(r[1] for r in resultados)
        total = sum(r[2] for r in resultados)
        sin_cambios = all(r[3] == 0 for r in resultados)
        print()
        if total_ok == 0 and sin_cambios:
            print(f"{ROJO}  Nunca respondio OK, en ningun paso: no es un cable flojo.")
            print(f"  Lo mas probable es la placa/chip. Probar otra placa ADS1256.{FIN}")
        elif total_ok == total:
            print(f"{VERDE}  Siempre OK: el chip responde. El problema es otro.{FIN}")
        else:
            print(f"{AMARILLO}  Hubo cambios de estado: mira cual paso los tiene, ese cable es el sospechoso.{FIN}")


if __name__ == "__main__":
    main()
