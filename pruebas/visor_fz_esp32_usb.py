"""Ventana en vivo de Fz leida por el ESP32 de lectura (ADS1256 diferencial), por su USB.
Para la ETAPA LAPTOP (INICIO_RPI.md): ver que el ADC realmente sensa (poner una masa -> escalon).

Usa lo que el firmware manda por el USB (main.cpp, 2026-11-18):
  "F,<valor>"  Fz cada 10 muestras (100/s)
  linea CSV    resumen por segundo (n, sd, perdidas, ceros, saturadas, ...)
  ERROR/ALERTA mensajes del firmware
Al abrir el puerto el ESP32 se reinicia (normal) y a los ~2 s empieza a llegar Fz.

Teclas en la ventana:  t = tarar (poner en cero),  r = quitar tara,
                       m = marcar un evento en el registro (ej. "puse la masa")
Todo queda en pruebas/resultados/visor_fz_<fecha>.csv (para el reporte).

Si dice "acceso denegado": otro programa tiene el puerto. En esta laptop suele ser
C:\\PB2\\display\\server.py (busca cualquier ESP32 CP210x y se queda con COM8): cerrarlo.

Uso: python pruebas/visor_fz_esp32_usb.py --puerto COM8
"""
import argparse, collections, os, statistics as st, threading, time
import serial
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

ap = argparse.ArgumentParser()
ap.add_argument("--puerto", required=True)
ap.add_argument("--ventana_s", type=float, default=10.0, help="segundos visibles en la grafica")
a = ap.parse_args()

R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
os.makedirs(os.path.join(R, "pruebas", "resultados"), exist_ok=True)
ruta = os.path.join(R, "pruebas", "resultados", time.strftime("visor_fz_%Y%m%d_%H%M%S.csv"))
reg = open(ruta, "w", buffering=1)
reg.write("t_s,tipo,dato\n")

try:
    ser = serial.Serial(a.puerto, 115200, timeout=0.5)
except serial.SerialException as e:
    raise SystemExit(f"No se pudo abrir {a.puerto}: {e}\n"
                     "Si es 'acceso denegado', cerrar el programa que lo usa (p. ej. C:\\PB2\\display\\server.py).")

t0 = time.monotonic()
datos = collections.deque(maxlen=int(a.ventana_s * 100) + 50)   # (t, Fz)
estado = {"resumen": None, "msg": "esperando al ESP32 (se reinicia al abrir el puerto)...",
          "alerta": False, "t_ult": None, "tara": 0.0, "marcas": [], "n_marcas": 0}
lock = threading.Lock()


def lector():
    while True:
        try:
            linea = ser.readline().decode("ascii", errors="replace").strip()
        except serial.SerialException as e:
            with lock:
                estado["msg"], estado["alerta"] = f"PUERTO PERDIDO: {e}", True
            return
        if not linea:
            continue
        t = time.monotonic() - t0
        if linea.startswith("F,"):
            try:
                f = float(linea[2:])
            except ValueError:
                continue
            with lock:
                datos.append((t, f))
                estado["t_ult"] = t
            reg.write(f"{t:.3f},F,{f:.3f}\n")
            continue
        reg.write(f"{t:.3f},linea,{linea.replace(',', ';')}\n")
        c = linea.split(",")
        with lock:
            if len(c) >= 11 and c[0].isdigit() and c[1].isdigit() and c[1] != "0":
                estado["resumen"] = c
                malos = any(x not in ("", "0") for x in c[7:10])
                estado["alerta"] = malos
                estado["msg"] = ("OK" if not malos else
                                 f"PROBLEMA en este segundo: perdidas={c[7]} ceros={c[8]} saturadas={c[9]}")
            elif "ERROR" in linea or "ALERTA" in linea or "BROWNOUT" in linea or "MAL" in linea:
                estado["msg"], estado["alerta"] = linea, True
            elif "ADS1256 OK" in linea or "Ultimo reinicio" in linea:
                estado["msg"] = linea


threading.Thread(target=lector, daemon=True).start()

fig, ax = plt.subplots(figsize=(11, 6))
fig.canvas.manager.set_window_title("Fz en vivo - ESP32 + ADS1256 (diferencial)")
linea_plot, = ax.plot([], [], lw=1.5, color="#1565c0")
ax.set_xlabel("tiempo (s)")
ax.set_ylabel("Fz (N)")
ax.grid(alpha=0.3)
txt_valor = fig.text(0.99, 0.95, "", ha="right", va="top", fontsize=30, weight="bold")
txt_info = fig.text(0.01, 0.95, "", ha="left", va="top", fontsize=10, family="monospace")
txt_msg = fig.text(0.01, 0.01, "", ha="left", va="bottom", fontsize=11)
fig.subplots_adjust(top=0.80)


def tecla(ev):
    with lock:
        if ev.key == "t" and datos:
            ult = [f for t, f in datos if t > datos[-1][0] - 1.0]
            estado["tara"] = st.mean(ult)
            reg.write(f"{time.monotonic() - t0:.3f},tara,{estado['tara']:.3f}\n")
        elif ev.key == "r":
            estado["tara"] = 0.0
            reg.write(f"{time.monotonic() - t0:.3f},tara,0\n")
        elif ev.key == "m":
            tm = time.monotonic() - t0
            estado["marcas"].append(tm)
            estado["n_marcas"] += 1
            reg.write(f"{tm:.3f},marca,evento {estado['n_marcas']}\n")


fig.canvas.mpl_connect("key_press_event", tecla)


def actualizar(_):
    with lock:
        pts = list(datos)
        e = dict(estado)
        e["marcas"] = estado["marcas"][:]
        estado["marcas"].clear()
    ahora = time.monotonic() - t0
    if pts:
        ts = [p[0] for p in pts]
        fs = [p[1] - e["tara"] for p in pts]
        linea_plot.set_data(ts, fs)
        ax.set_xlim(max(0, ts[-1] - a.ventana_s), max(a.ventana_s, ts[-1]))
        lo, hi = min(fs), max(fs)
        margen = max(2.0, 0.15 * (hi - lo))
        ax.set_ylim(lo - margen, hi + margen)
        actual = st.mean(fs[-30:])
        txt_valor.set_text(f"{actual:+.1f} N")
    for tm in e["marcas"]:
        ax.axvline(tm, color="#e65100", lw=1, ls="--")
    sin_datos = e["t_ult"] is None or ahora - e["t_ult"] > 2.0
    r = e["resumen"]
    info = (f"muestras/s {r[1]}   ruido sd {float(r[3]):.2f} N   perdidas {r[7]}   ceros {r[8]}   saturadas {r[9]}"
            if r else "sin resumen todavia")
    tara = f"   tara {e['tara']:+.2f} N" if e["tara"] else "   (sin tara: t = tarar)"
    txt_info.set_text(info + tara + "\nteclas: t tarar | r quitar tara | m marcar evento")
    if sin_datos and e["t_ult"] is not None:
        txt_msg.set_text(f"SIN DATOS hace {ahora - e['t_ult']:.0f} s (ADC caido o cable USB)")
        txt_msg.set_color("#c62828")
    else:
        txt_msg.set_text(e["msg"])
        txt_msg.set_color("#c62828" if e["alerta"] else "#2e7d32")
    return linea_plot, txt_valor, txt_info, txt_msg


anim = FuncAnimation(fig, actualizar, interval=100, cache_frame_data=False)
plt.show()
ser.close()
reg.close()
print(f"Registro: {ruta}")
