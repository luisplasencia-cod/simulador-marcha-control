"""Primera prueba de SET_VEL en el eje Y REAL, EN EL AIRE (2026-11-10).

Mueve Y ~2.5 mm (400 pasos/s x 0.5 s = ~200 pasos), prueba el watchdog y regresa con MANUAL.
NO usa HOME. NO mide Fz. Requiere: pie SIN tocar la plataforma, Luis junto al paro de emergencia.

Fases:
  A) SET_VEL:1:+VEL reenviado cada 20 ms durante 0.5 s, luego SET_VEL:1:0.
     -> la posicion (contador de pasos ORDENADOS, no medida) debe subir ~VEL*0.5 pasos. Luis mira el signo fisico.
  B) Watchdog: UN solo SET_VEL:1:+VEL y silencio 0.6 s. Debe parar solo: pasos ~ VEL*0.08 s + un periodo.
  C) Regreso: MANUAL:1:-(neto) (comando original, signo ya medido en el Ensayo 0: + = subir).
Guarda todo en --salida (JSON). Aborta (SET_VEL 0) ante cualquier respuesta distinta de OK.
"""
import argparse
import json
import sys
import time

import serial

ap = argparse.ArgumentParser()
ap.add_argument("--puerto", default="/dev/ttyUSB0")
ap.add_argument("--vel", type=int, default=400, help="pasos/s (80 pasos/mm: 400 = 5 mm/s)")
ap.add_argument("--dur_s", type=float, default=0.5)
ap.add_argument("--periodo_s", type=float, default=0.02)
ap.add_argument("--salida", default="pruebas/resultados/set_vel_aire_20261110.json")
a = ap.parse_args()
assert 0 < a.vel <= 800 and a.dur_s <= 1.0, "limites de seguridad de la prueba"

ser = serial.Serial(a.puerto, 115200, timeout=1.0)
time.sleep(6.0)  # reinicio por apertura del puerto + arranque (lecciones del 2026-11-10)
ser.reset_input_buffer()
log = {"vel": a.vel, "dur_s": a.dur_s, "eventos": []}


def pedir(cmd):
    ser.reset_input_buffer()
    t0 = time.perf_counter()
    ser.write(f"<{cmd}>".encode())
    r = ser.readline().decode(errors="replace").strip()
    dt = (time.perf_counter() - t0) * 1e3
    log["eventos"].append({"cmd": cmd, "resp": r, "ms": round(dt, 2)})
    return r, dt


def pos():
    r, _ = pedir("GET_POSITION")
    try:
        return int(r.split(":")[2])  # POSITION:x:y:k -> y
    except Exception:
        return None


def abortar(msg):
    print("ABORTO:", msg)
    pedir("SET_VEL:1:0")
    ser.close()
    json.dump(log, open(a.salida, "w"), indent=1)
    sys.exit(1)


r, _ = pedir("PING")
if r != "PONG":
    r, _ = pedir("PING")  # primera lectura tras el reinicio puede traer basura
if r != "PONG":
    abortar(f"PING no respondio: {r!r}")
p0 = pos()
print("posicion inicial Y (contador):", p0)
if p0 is None:
    abortar("GET_POSITION ilegible")

# ---- A) velocidad continua con reenvio ----
print(f">>> A) SET_VEL +{a.vel} pasos/s durante {a.dur_s} s (mira hacia donde se mueve el eje)")
t_ini = time.perf_counter()
n = 0
rtts = []
while time.perf_counter() - t_ini < a.dur_s:
    r, dt = pedir(f"SET_VEL:1:{a.vel}")
    rtts.append(dt)
    n += 1
    if r != "OK":
        abortar(f"SET_VEL respondio {r!r}")
    time.sleep(max(0.0, a.periodo_s - dt / 1e3))
r, _ = pedir("SET_VEL:1:0")
time.sleep(0.3)
p1 = pos()
print(f"    {n} SET_VEL, RTT medio {sum(rtts)/len(rtts):.2f} ms, max {max(rtts):.2f}; pasos ordenados: {p1 - p0}  (~{(p1-p0)/80:.2f} mm)")
log["A"] = {"n": n, "rtt_medio_ms": sum(rtts) / len(rtts), "rtt_max_ms": max(rtts), "pasos": p1 - p0}

# ---- B) watchdog ----
print(">>> B) watchdog: un solo SET_VEL y silencio")
time.sleep(1.0)
r, _ = pedir(f"SET_VEL:1:{a.vel}")
time.sleep(0.6)
p2 = pos()
pasos_wd = p2 - p1
print(f"    respuesta {r!r}; pasos tras el unico SET_VEL: {pasos_wd}  (esperado <= ~{int(a.vel*0.08)+a.vel*0.02:.0f} si el watchdog de 80 ms funciona)")
log["B"] = {"resp": r, "pasos": pasos_wd}
pedir("SET_VEL:1:0")

# ---- C) regreso con MANUAL ----
neto = p2 - p0
print(f">>> C) regreso con MANUAL:1:{-neto}")
if neto != 0:
    r, _ = pedir(f"MANUAL:1:{-neto}")
    print("    respuesta:", r)
    time.sleep(max(2.0, abs(neto) / 800 + 1.5))
p3 = pos()
print("posicion final Y (contador):", p3, "(debe ser", p0, ")")
log["C"] = {"neto": neto, "pos_final": p3, "pos_inicial": p0}
ser.close()
json.dump(log, open(a.salida, "w"), indent=1)
print("guardado:", a.salida)
