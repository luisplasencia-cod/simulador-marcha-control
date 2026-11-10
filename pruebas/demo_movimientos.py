"""Demo de movimientos para mostrar (SIN ADC, sin contacto): 3 veces [X +10 cm / -10 cm, Y +5 cm, K -20 deg / +20 deg, Y -5 cm].
El giro del pie se hace con Y ya subido (mas hueco a la plataforma). Todo es relativo a la posicion actual y vuelve a 0.
Cada tramo (MANUAL) espera a que el contador deje de cambiar y verifica que se movio lo ordenado; si no, ABORTA y vuelve a 0
(en orden K, X, Y). Sin HOME. Registro en vivo en logs/prueba_en_vivo.csv (herramientas/en_vivo.py).
Uso: .venv/bin/python pruebas/demo_movimientos.py [--veces 3] [--x_cm 10] [--y_cm 5] [--k_deg 20] [--aviso_s 10]"""
import sys, os, time, json, argparse
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(R, "control")); sys.path.insert(0, os.path.join(R, "herramientas"))
import lazo_fz_tiempo_real as L
from en_vivo import EnVivo

ap = argparse.ArgumentParser()
ap.add_argument("--veces", type=int, default=3); ap.add_argument("--x_cm", type=float, default=10.0)
ap.add_argument("--y_cm", type=float, default=5.0); ap.add_argument("--k_deg", type=float, default=20.0)
ap.add_argument("--aviso_s", type=int, default=10); ap.add_argument("--pausa_s", type=float, default=1.0)
a = ap.parse_args()
PX, PY, PK = 400.0, 80.0 * 10, 5000 / 45.0   # pasos: X 400/cm, Y 800/cm (80/mm), K 111.11/deg
assert a.x_cm <= 15 and a.y_cm <= 8 and a.k_deg <= 25, "limites de seguridad de la demo"
EJE = {"X": 0, "Y": 1, "K": 2}
CHUNK = {"X": 800, "Y": 800, "K": 600}
ev = EnVivo(f"Demo: {a.veces} x [X +/-{a.x_cm:g} cm, Y +/-{a.y_cm:g} cm, K -/+{a.k_deg:g} deg]")
e = None
delta = {"X": 0, "Y": 0, "K": 0}
motivo = "completada"


def pos():
    """Lee el contador. Si la respuesta llega incompleta (error 2026-11-10: KeyError('Y')) reintenta; si no, error claro."""
    r = ""
    for _ in range(5):
        r = e._cmd("GET_POSITION")
        v = r.split(":")
        if v[0] == "POSITION" and len(v) == 4:
            try:
                return dict(zip("XYK", (int(x) for x in v[1:4])))
            except ValueError:
                pass
        time.sleep(0.1)
    raise RuntimeError(f"GET_POSITION sin respuesta valida tras 5 intentos (ultima: {r!r}); posible perdida del USB")


_ult = [0.0]


def estado(msg):
    ev.escribir("demo", float("nan"), delta["Y"], f"{msg}  [X={delta['X']/PX:+.1f} cm  Y={delta['Y']/PY:+.1f} cm  K={delta['K']/PK:+.1f}°]")
    if time.monotonic() - _ult[0] < 1.0: return
    _ult[0] = time.monotonic()
    print(f"  {msg:<34s} X={delta['X']/PX:+5.1f} cm  Y={delta['Y']/PY:+5.1f} cm  K={delta['K']/PK:+6.1f}°", flush=True)


def mover(eje, pasos, msg):
    if pasos == 0: return
    s = 1 if pasos > 0 else -1; falta = abs(pasos)
    while falta > 0:
        p = min(falta, CHUNK[eje]); antes = pos()[eje]
        for intento in range(20):
            r = e._cmd(f"MANUAL:{EJE[eje]}:{s * p}")
            if r.startswith("OK"): break
            if r.startswith("BUSY"): time.sleep(0.3); continue
            raise RuntimeError(f"MANUAL {eje} respondio {r!r}")
        else:
            raise RuntimeError(f"MANUAL {eje} siempre BUSY")
        quieto, ult, t0 = 0, antes, time.monotonic()
        while quieto < 3:
            time.sleep(0.12); c = pos()[eje]
            quieto = quieto + 1 if c == ult else 0; ult = c
            if time.monotonic() - t0 > 25: raise RuntimeError(f"{eje} no termina de moverse")
            estado(msg)
        if abs((ult - antes) - s * p) > 0.05 * p + 5:
            raise RuntimeError(f"{eje}: el contador se movio {ult - antes}, se ordeno {s * p} (final de carrera o perdida de pasos)")
        delta[eje] += s * p; falta -= p


try:
    e = L.ClienteVelocidadESP32()
    p0 = pos(); print("posicion inicial (contador):", p0)
    for i in range(a.aviso_s, 0, -1):
        ev.escribir("aviso", float("nan"), 0, f"ATENCION: el simulador se mueve en {i} s: manos y cables FUERA")
        print(f"  ATENCION: se mueve en {i} s ...", flush=True); time.sleep(1.0)
    for v in range(1, a.veces + 1):
        print(f"=== repeticion {v}/{a.veces}")
        mover("X", int(a.x_cm * PX), f"{v}/{a.veces} X ADELANTE");  time.sleep(a.pausa_s)
        mover("X", -int(a.x_cm * PX), f"{v}/{a.veces} X ATRAS");    time.sleep(a.pausa_s)
        mover("Y", int(a.y_cm * PY), f"{v}/{a.veces} Y SUBE");      time.sleep(a.pausa_s)
        mover("K", -int(a.k_deg * PK), f"{v}/{a.veces} K -{a.k_deg:g} deg"); time.sleep(a.pausa_s)
        mover("K", int(a.k_deg * PK), f"{v}/{a.veces} K +{a.k_deg:g} deg");  time.sleep(a.pausa_s)
        mover("Y", -int(a.y_cm * PY), f"{v}/{a.veces} Y BAJA");     time.sleep(a.pausa_s)
except BaseException as ex:
    motivo = f"ABORTADA: {ex!r}"; print(motivo, flush=True)
finally:
    try:
        if e:
            for eje in ("K", "X", "Y"):                      # vuelve a 0 (K primero, Y al final)
                if delta[eje]: mover(eje, -delta[eje], f"VOLVIENDO {eje} A 0")
            pf = pos(); print("posicion final (contador):", pf)
            if delta["K"]:  # por si K quedo sin volver
                est = os.path.join(R, "control/identificacion/estado_angulo_K.json"); j = json.load(open(est))
                j["angulo_deg"] += delta["K"] / PK; j["actualizado"] = time.strftime("%Y-%m-%d %H:%M:%S"); json.dump(j, open(est, "w"), indent=1)
    except BaseException as ex2:
        print("!!! NO SE PUDO VOLVER A 0 AUTOMATICAMENTE:", repr(ex2), "delta pendiente:", delta, flush=True)
    ev.cerrar(motivo)
    try: e.cerrar()
    except Exception: pass
    print("fin:", motivo)
