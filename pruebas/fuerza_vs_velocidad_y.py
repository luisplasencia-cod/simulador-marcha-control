"""Fz medida con el eje Y EN EL AIRE a distintas velocidades (sin contacto). Pregunta: ¿el servo vertical corre la lectura?
Sube/baja Y a 400/800/1600 pasos/s por 0.5 s (neto 0, <=10 mm; hueco >= ~100 mm), midiendo Fz en reposo, en movimiento y
despues de parar. SIEMPRE repone Y al final (incluso si el ADC se cae). Todo en vivo en la pantalla (herramientas/en_vivo.py).
Uso: .venv/bin/python pruebas/fuerza_vs_velocidad_y.py"""
import sys, os, time, json, statistics as st
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "control"))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "herramientas"))
import lazo_fz_tiempo_real as L
from en_vivo import EnVivo

ev = EnVivo("Fz vs velocidad de Y (en el aire, sin contacto)")
e = l = None
y = 0
res, motivo = {}, "completada"


def leer(fase, msg, seg):
    v, t0 = [], time.monotonic()
    while time.monotonic() - t0 < seg:
        f = l.leer_n(); v.append(f); ev.escribir(fase, f, y, msg)
    return v


def mover(fase, vel, msg, seg=0.5):
    global y
    v, t0, tp = [], time.monotonic(), time.monotonic()
    while time.monotonic() - t0 < seg:
        e.set_vel(L.EJE_VERTICAL, vel); f = l.leer_n(); v.append(f)
        now = time.monotonic(); y += vel * (now - tp); tp = now
        ev.escribir(fase, f, y, msg)
    e.detener(L.EJE_VERTICAL)
    return v


try:
    ev.escribir("inicio", 0, 0, "CONECTANDO (el ESP32 se reinicia al abrir el puerto: espera 6 s)")
    e = L.ClienteVelocidadESP32(); l = L.LectorFzFiltrado()
    ev.escribir("tara", 0, 0, "TARA: eje quieto y sin contacto")
    print("tara f0 =", round(l.tarar()[0], 1))
    v = leer("reposo", "REPOSO inicial (eje quieto)", 1.0); res["reposo_inicial"] = st.median(v)
    for vel in (400, 800, 1600):
        for signo, nombre in ((-1, "baja"), (1, "sube")):
            v = mover(f"{nombre} {vel}", signo * vel, f"{nombre.upper()} Y a {vel/80:.0f} mm/s (Y se esta moviendo)")
            p = leer("tras parar", f"Y detenido tras {nombre} {vel}: leyendo 0.5 s", 0.5)
            print(f"{nombre:5s} {vel:4d}: en movimiento mediana {st.median(v):6.1f} N (min {min(v):.1f} max {max(v):.1f}) | tras parar {st.median(p):6.1f} N")
            res[f"{nombre}_{vel}"] = {"mov_mediana": st.median(v), "mov_min": min(v), "mov_max": max(v), "post_mediana": st.median(p)}
    v = leer("reposo", "REPOSO final", 1.0); res["reposo_final"] = st.median(v)
except BaseException as ex:
    motivo = f"ABORTADA: {ex!r}"
    print(motivo)
finally:
    try:
        ev.escribir("retorno", 0, y, f"{motivo} -> REPONIENDO Y")
        if e:
            e.detener(L.EJE_VERTICAL); n = e.pos_y()
            if n < 0: e.subir_pasos(-n)
            print("contador final:", e._cmd("GET_POSITION"))
    except BaseException as ex2:
        print("!!! NO SE PUDO REPONER Y:", repr(ex2))
    for o in (e, l):
        try: o.cerrar()
        except Exception: pass
    ev.cerrar(motivo)
    json.dump(res, open("pruebas/resultados/fuerza_vs_velocidad_y_20261110.json", "w"), indent=1)
