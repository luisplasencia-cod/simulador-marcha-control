"""Vigila el ADS1256 en reposo para atrapar CUANDO y COMO se cae (sin ESP32, sin servo, sin mover nada).
Cada 1 s registra: muestras/s, Fz, flancos de DRDY, nivel de MISO, EXT5V del RPi y 'throttled'. Si falla, anota el instante
y el estado de los pines, y sigue intentando re-inicializar cada 2 s (para ver si se recupera solo). Todo en vivo en pantalla
(herramientas/en_vivo.py) y en pruebas/resultados/vigilar_adc_<hora>.csv. Parar con Ctrl+C o --minutos N.
Uso: .venv/bin/python pruebas/vigilar_adc.py --minutos 20"""
import sys, os, time, subprocess, argparse, statistics as st
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(R, "pruebas")); sys.path.insert(0, os.path.join(R, "herramientas"))
import RPi.GPIO as G
from leer_ads1256_fz import ADS1256, volts_a_newtons
from en_vivo import EnVivo

ap = argparse.ArgumentParser(); ap.add_argument("--minutos", type=float, default=20.0); a = ap.parse_args()
ev = EnVivo("Vigilante del ADC en reposo (sin ESP32 ni servo)")
sal = open(os.path.join(R, "pruebas/resultados", time.strftime("vigilar_adc_%Y%m%d_%H%M%S.csv")), "w", buffering=1)
sal.write("hora,estado,muestras_s,Fz_N,flancos_drdy,miso,ext5v,throttled,nota\n")


def pmic():
    try:
        o = subprocess.run(["vcgencmd", "pmic_read_adc"], capture_output=True, text=True, timeout=3).stdout
        v = [l for l in o.splitlines() if "EXT5V_V" in l][0].split("=")[1].replace("V", "").strip()
        t = subprocess.run(["vcgencmd", "get_throttled"], capture_output=True, text=True, timeout=3).stdout.strip().split("=")[1]
        return v, t
    except Exception: return "?", "?"


def pines():
    o = subprocess.run(["pinctrl", "get", "9"], capture_output=True, text=True).stdout
    return "hi" if "| hi" in o else "lo"


adc, f0, fin = None, None, time.monotonic() + a.minutos * 60
caidas = 0
while time.monotonic() < fin:
    try:
        if adc is None:
            adc = ADS1256(); f0 = None
            ev.escribir("OK", 0, 0, "ADC INICIADO - vigilando"); sal.write(f"{time.strftime('%H:%M:%S')},REINICIADO,,,,,,,reinicio por software OK\n")
        t0 = time.monotonic(); v = []
        while time.monotonic() - t0 < 1.0:
            v.append(volts_a_newtons(adc.leer_volts()))
        m = st.median(v); f0 = m if f0 is None else f0
        e5, th = pmic()
        ev.escribir("OK", m - f0, 0, f"ADC OK: {len(v)} muestras/s  Fz={m - f0:+.1f} N  5V={e5}  caidas={caidas}")
        sal.write(f"{time.strftime('%H:%M:%S')},OK,{len(v)},{m - f0:.2f},,{pines()},{e5},{th},\n")
    except Exception as ex:
        caidas += 1
        try:
            G.setmode(G.BCM); G.setup(17, G.IN); t0 = time.monotonic(); prev = G.input(17); fl = 0
            while time.monotonic() - t0 < 0.5:
                x = G.input(17); fl += (x != prev); prev = x
        except Exception: fl = -1
        e5, th = pmic()
        msg = f"ADC CAIDO ({repr(ex)[:50]}) DRDY flancos/0.5s={fl} MISO={pines()} 5V={e5} thr={th}"
        print(time.strftime("%H:%M:%S"), msg, flush=True)
        ev.escribir("CAIDO", 0, 0, "ABORT? " + msg); sal.write(f"{time.strftime('%H:%M:%S')},CAIDO,,,{fl},{pines()},{e5},{th},{repr(ex)[:60]}\n")
        try:
            if adc: adc.cerrar()
        except Exception: pass
        adc = None; time.sleep(2.0)
ev.cerrar("fin del vigilante")
try:
    if adc: adc.cerrar()
except Exception: pass
print(f"fin: {caidas} caidas en {a.minutos:g} min")
