"""Fase A4 (2026-11-18): firmware v4, SET_VEL del eje Y en el AIRE sin trayectoria: sube ~1 mm y vuelve.
Sube PRIMERO (alejarse del plato es lo seguro). Reenvia SET_VEL cada ~10 ms (watchdog de 80 ms). Comprueba que el
contador vuelve al inicial. Eje como ENTERO (1 = Y); + = subir. No manda HOME/RUN/MANUAL/GOTO."""
import sys, os, time, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import lazo_fz_tiempo_real as L
V, T = 400, 0.2            # 400 pasos/s x 0.2 s = 80 pasos = 1 mm
e = L.ClienteVelocidadESP32()
res = {"y0": e.y0}
try:
    for nombre, v in (("sube", +V), ("baja", -V)):
        t0, n_ok, rtt = time.monotonic(), 0, []
        while time.monotonic() - t0 < T:
            a = time.perf_counter(); r = e.set_vel(1, v); rtt.append((time.perf_counter() - a) * 1e3); n_ok += r.startswith("OK")
        e.detener(1); time.sleep(0.15)
        res[nombre] = {"y_rel": e.pos_y_rel(), "set_vel_ok": n_ok, "envios": len(rtt), "rtt_ms_max": round(max(rtt), 3)}
        print(nombre, res[nombre])
finally:
    e.detener(1)
    res["y_rel_final"] = e.pos_y_rel(); print("Y final respecto al inicio:", res["y_rel_final"], "pasos")
    e.cerrar()
json.dump(res, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "pruebas", "resultados", "prueba_v4_set_vel_y_aire_20261118.json"), "w"), indent=1)
