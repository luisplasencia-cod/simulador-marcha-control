"""¿Abrir el puerto del ESP32 (sin mover nada) tumba o corre el ADC? (2026-11-10)
Proceso A (este): ADC leyendo en continuo; registra Fz y cualquier fallo. Proceso B (subprocess): abre SOLO el puerto del
ESP32, PING/GET_POSITION y cierra (NO manda SET_VEL/MANUAL). Fases: base 3 s -> ESP32 abierto -> 4 s despues.
Se ve en vivo en la pantalla (herramientas/en_vivo.py). Uso: .venv/bin/python pruebas/causalidad_adc_esp32.py"""
import sys, os, time, subprocess, statistics as st
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(R, "pruebas")); sys.path.insert(0, os.path.join(R, "herramientas"))
from leer_ads1256_fz import ADS1256, volts_a_newtons
from en_vivo import EnVivo

ev = EnVivo("Causalidad: abrir el puerto del ESP32 (sin mover) vs ADC")
adc = ADS1256()
B = ("import sys,time;sys.path.insert(0,'control');import lazo_fz_tiempo_real as L;e=L.ClienteVelocidadESP32();"
     "print('B: ESP32 abierto, GET_POSITION =',e._cmd('GET_POSITION'),flush=True);time.sleep(1.0);e.cerrar();print('B: cerrado',flush=True)")
fases = {}
fallos = []
f0 = None
procB = None
t_ini = time.monotonic()


def leer_bloque():
    raw = sorted(volts_a_newtons(adc.leer_volts()) for _ in range(7))
    return raw[3]


def fase(nombre, msg, cond):
    global f0
    v = []
    while cond():
        try:
            f = leer_bloque()
            if f0 is None: f0 = f
            v.append(f - f0); ev.escribir(nombre, f - f0, 0, msg)
        except Exception as e:
            fallos.append((nombre, round(time.monotonic() - t_ini, 2), repr(e)[:80]))
            ev.escribir(nombre, 0, 0, f"ADC FALLA: {repr(e)[:60]}")
            time.sleep(0.05)
    fases[nombre] = v


try:
    t0 = time.monotonic()
    fase("base", "ADC SOLO leyendo (linea base 3 s)", lambda: time.monotonic() - t0 < 3.0)
    procB = subprocess.Popen([sys.executable, "-c", B], cwd=R, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    fase("ESP32 abierto", "ABRIENDO el puerto del ESP32 (sin mover nada) - mirar Fz", lambda: procB.poll() is None)
    t0 = time.monotonic()
    fase("despues", "ESP32 cerrado: ADC 4 s despues", lambda: time.monotonic() - t0 < 4.0)
    print(procB.stdout.read().strip())
finally:
    ev.cerrar("fin")
    try: adc.cerrar()
    except Exception: pass
    for k, v in fases.items():
        if v: print(f"{k:14s} n={len(v):4d}  mediana {st.median(v):6.1f}  min {min(v):6.1f}  max {max(v):6.1f} N")
        else: print(f"{k:14s} sin lecturas")
    print("fallos del ADC:", len(fallos)); [print("  ", x) for x in fallos[:5]]
