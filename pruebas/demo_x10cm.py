"""Demo: con el pie ya LEVANTADO y libre, mueve X +10 cm (adelante = pasos positivos, 400 pasos/cm), espera y lo devuelve.
NO toca Y ni K. Se ve en vivo en la pantalla (herramientas/en_vivo.py). Exige --y_arriba (Luis confirma que el pie esta libre).
Uso: .venv/bin/python pruebas/demo_x10cm.py --y_arriba [--cm 10] [--pausa_s 2]"""
import sys, os, time, argparse
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(R, "control")); sys.path.insert(0, os.path.join(R, "herramientas"))
import lazo_fz_tiempo_real as L
from en_vivo import EnVivo

ap = argparse.ArgumentParser()
ap.add_argument("--cm", type=float, default=10.0)
ap.add_argument("--pausa_s", type=float, default=2.0)
ap.add_argument("--y_arriba", action="store_true", help="OBLIGATORIO: el pie esta levantado y libre del suelo/plataforma")
a = ap.parse_args()
if not a.y_arriba:
    sys.exit("Falta --y_arriba: confirmar que el pie esta levantado y libre antes de mover X.")
PASOS = int(round(a.cm * 400))
ev = EnVivo(f"Demo: X +{a.cm:g} cm y de vuelta")
e = L.ClienteVelocidadESP32()
x = 0


def mover(delta, msg):
    global x
    falta = abs(delta); s = 1 if delta > 0 else -1
    while falta > 0:
        p = min(falta, 800); r = e._cmd(f"MANUAL:0:{s * p}")
        if not r.startswith("OK"): raise RuntimeError(f"MANUAL X respondio {r!r}")
        t0 = time.monotonic()
        while time.monotonic() - t0 < p / 1600 + 0.3:
            ev.escribir("X", 0, 0, f"{msg}  (X = {x / 400:+.1f} cm)"); time.sleep(0.1)
        x += s * p; falta -= p


motivo = "completada"
try:
    print("antes:", e._cmd("GET_POSITION"))
    mover(PASOS, f"X ADELANTE {a.cm:g} cm")
    t0 = time.monotonic()
    while time.monotonic() - t0 < a.pausa_s: ev.escribir("pausa", 0, 0, f"pausa: X = +{a.cm:g} cm"); time.sleep(0.1)
    mover(-PASOS, f"X DE VUELTA {a.cm:g} cm")
except BaseException as ex:
    motivo = f"ABORTADA: {ex!r}"; print(motivo)
finally:
    print("despues:", e._cmd("GET_POSITION")); ev.cerrar(motivo); e.cerrar()
