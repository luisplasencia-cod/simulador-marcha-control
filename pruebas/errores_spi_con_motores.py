"""Errores de bit SPI del ADS1256 en 3 condiciones: quieto / sagital K moviendose / eje Y moviendose.
Y solo hace +400 pasos (5 mm ARRIBA) y -400 (vuelve): nunca baja de su posicion inicial. Sin HOME."""
import sys, time, threading, statistics as st
from pathlib import Path
import serial
sys.path.insert(0, str(Path(__file__).resolve().parent))
import leer_ads1256_fz as m
N = 20000
ser = serial.Serial("/dev/ttyUSB0", 115200, timeout=2.0); time.sleep(2.0); ser.reset_input_buffer()
parar = threading.Event()
def mover(eje, pasos):
    s = 1
    while not parar.is_set():
        ser.reset_input_buffer(); ser.write(f"<MANUAL:{eje}:{s*pasos}>".encode())
        r = ser.readline().decode(errors="replace").strip()
        if not r.startswith("OK"): print("  ack:", r); time.sleep(0.2)
        else: time.sleep(abs(pasos) / 1600 + 0.15)
        s = -s
def medir(nombre, eje=None, pasos=0):
    parar.clear(); th = None
    if eje is not None:
        th = threading.Thread(target=mover, args=(eje, pasos)); th.start(); time.sleep(0.3)
    adc = m.ADS1256(); v = [adc.leer_volts() for _ in range(N)]; adc.cerrar()
    parar.set()
    if th: th.join()
    med = st.median(v); mala = [abs(x - med) > 0.05 for x in v]
    runs, c = [], 0
    for b in mala:
        if b: c += 1
        elif c: runs.append(c); c = 0
    if c: runs.append(c)
    ok = [x for x, b in zip(v, mala) if not b]
    print(f"{nombre:<22} malas {sum(mala)}/{N} ({100*sum(mala)/N:.2f} %) rafagas={len(runs)} max_len={max(runs) if runs else 0} "
          f"len>=2={sum(1 for r in runs if r>=2)} sigma_buenas={st.pstdev(ok)*1000/1.7665:.2f} N", flush=True)
try:
    medir("quieto")
    medir("sagital K +-40", 2, 40)
    medir("eje Y +-400 (5 mm)", 1, 400)
    medir("quieto (final)")
finally:
    parar.set(); ser.close()
