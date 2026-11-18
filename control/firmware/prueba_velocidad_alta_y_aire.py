"""Prueba EN EL AIRE de velocidades altas de SET_VEL en Y (2026-11-18): ¿el servo vertical sigue sin rampa de aceleración?
Por cada velocidad: SUBE 10 mm (lo seguro primero), para 0.3 s, BAJA 10 mm, para. Neto 0. Pie a ~57 mm del contacto.
Comprueba con el contador del firmware que vuelve al inicio; el contador NO detecta si el servo se quedó atrás o entró en
alarma (cuenta pasos ordenados): Luis debe mirar el driver/escuchar y decir si hubo alarma o ruido anormal.
Uso: .venv/bin/python control/firmware/prueba_velocidad_alta_y_aire.py [2000,4000,...]  (por defecto 2000..12000)"""
import sys, os, time, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import lazo_fz_tiempo_real as L
VELS = [int(v) for v in (sys.argv[1].split(",") if len(sys.argv) > 1 else "2000,4000,6000,9000,12000".split(","))]
MM = 10.0
assert max(VELS) <= 12000
e = L.ClienteVelocidadESP32()
res = {"y0": e.y0, "pruebas": []}
try:
    for v in VELS:
        fila = {"v": v, "mm_s": v / 80}
        for nombre, signo in (("sube", +1), ("baja", -1)):
            pasos_obj = int(MM * 80); t_obj = pasos_obj / v
            y_a = e.pos_y_rel(); t0 = time.monotonic(); n = 0
            while time.monotonic() - t0 < t_obj:
                e.set_vel(1, signo * v); n += 1
            e.detener(1); time.sleep(0.3)
            fila[nombre + "_pasos"] = e.pos_y_rel() - y_a; fila[nombre + "_envios"] = n
        fila["y_rel_tras"] = e.pos_y_rel()
        print(fila, flush=True); res["pruebas"].append(fila)
        if abs(fila["y_rel_tras"]) > 200:
            print("!!! el contador no volvió al inicio: se detiene la prueba"); break
finally:
    e.detener(1); res["y_rel_final"] = e.pos_y_rel(); print("Y final respecto al inicio:", res["y_rel_final"]); e.cerrar()
json.dump(res, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "pruebas", "resultados",
                                  time.strftime("velocidad_alta_y_aire_%Y%m%d_%H%M%S.json")), "w"), indent=1)
