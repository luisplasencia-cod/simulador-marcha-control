"""Visor en vivo del lazo Fz: lee un CSV con el formato de formato_log.md MIENTRAS otro proceso
lo escribe, y grafica 3 tiras (strip charts) con los nombres de variable del diagrama matematico
(control/diagramas/diagrama_lazo_hibrido.py) para poder comparar directo:
    1) r*(t) (referencia corregida) vs F_med(t)  -- lo que se persigue vs lo que se mide
    2) e(t)                                       -- error
    3) u(t) (SET_VEL, pasos/s) y delta(t)         -- señal de control y lo que aprendió el ILC

Pensado para correr en el RPi junto al script real del lazo (que todavia no existe -- ver
README.md). Se probo con datos sinteticos (generar_datos_sinteticos.py), no con datos reales.

Uso:
    python visor_en_vivo.py <archivo.csv>          # ventana interactiva, si hay pantalla
    python visor_en_vivo.py --ultimo                # usa el CSV mas reciente de registros/
    python visor_en_vivo.py --ultimo --guardar visor.gif   # SIN pantalla: guarda un GIF
                                                             # recorriendo todo el archivo
                                                             # (asi se puede ver sin RPi y sin
                                                             # entorno grafico -- probado 2026-11-05)
"""
import argparse
import csv
import glob
import os
import time

REGISTROS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "registros")

AP = argparse.ArgumentParser()
AP.add_argument("archivo", nargs="?", default=None)
AP.add_argument("--ultimo", action="store_true", help="usar el CSV mas reciente en registros/")
AP.add_argument("--ventana-s", type=float, default=8.0, help="segundos visibles en pantalla")
AP.add_argument("--intervalo-ms", type=int, default=200, help="cada cuanto releer el archivo")
AP.add_argument("--guardar", default=None, help="en vez de ventana interactiva, guardar un GIF recorriendo todo el archivo (no necesita pantalla)")
AP.add_argument("--fps", type=int, default=12, help="cuadros por segundo del GIF (solo con --guardar)")
AP.add_argument("--cuadros", type=int, default=90, help="total de cuadros del GIF, repartidos en todo el archivo (controla el tamaño del archivo)")
A = AP.parse_args()

import matplotlib
matplotlib.use("Agg" if A.guardar else "TkAgg")  # Agg no necesita pantalla; TkAgg es la ventana interactiva
import matplotlib.pyplot as plt
import matplotlib.animation as animation

if A.ultimo:
    candidatos = sorted(glob.glob(os.path.join(REGISTROS, "*.csv")))
    if not candidatos:
        raise SystemExit(f"No hay ningun .csv en {REGISTROS}")
    RUTA = candidatos[-1]
elif A.archivo:
    RUTA = A.archivo
else:
    raise SystemExit("Dar la ruta del CSV, o --ultimo para el mas reciente en registros/")

print(f"Leyendo: {RUTA}")
while not os.path.exists(RUTA):
    print("Esperando a que exista el archivo...")
    time.sleep(1.0)

datos = {"t": [], "r_corregida": [], "F_med": [], "e": [], "u": [], "delta": []}
_pos_leida = [0]
_cabecera = [None]


def leer_nuevas_filas():
    with open(RUTA, "r", newline="") as f:
        f.seek(_pos_leida[0])
        nuevas = f.read()
        _pos_leida[0] = f.tell()
    if not nuevas.strip():
        return
    filas = list(csv.reader(nuevas.splitlines()))
    if _cabecera[0] is None:
        _cabecera[0] = filas[0]
        filas = filas[1:]
    idx = {c: i for i, c in enumerate(_cabecera[0])}
    for fila in filas:
        if len(fila) != len(_cabecera[0]):
            continue  # fila a medio escribir, se recoge en la proxima pasada
        datos["t"].append(float(fila[idx["t"]]))
        datos["r_corregida"].append(float(fila[idx["r_corregida"]]))
        datos["F_med"].append(float(fila[idx["F_med"]]))
        datos["e"].append(float(fila[idx["e"]]))
        datos["u"].append(float(fila[idx["u"]]))
        datos["delta"].append(float(fila[idx["delta"]]))


fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
fig.suptitle("Lazo Fz en vivo — " + os.path.basename(RUTA))

l_r, = ax1.plot([], [], label=r"$r^*(t)$ (referencia corregida)", color="#1565c0")
l_f, = ax1.plot([], [], label=r"$F_{med}(t)$ (medida)", color="#c62828")
ax1.set_ylabel("%BW")
ax1.legend(loc="upper right", fontsize=8)
ax1.grid(alpha=0.3)

l_e, = ax2.plot([], [], color="#e65100")
ax2.set_ylabel(r"$e(t)$  [%BW]")
ax2.axhline(0, color="black", lw=0.6)
ax2.grid(alpha=0.3)

l_u, = ax3.plot([], [], label=r"$u(t)$ (SET_VEL, pasos/s)", color="#2e7d32")
l_d, = ax3.plot([], [], label=r"$\delta(t)$ (aprendido por ILC) [%BW]", color="#6a1b9a")
ax3.set_ylabel("u [pasos/s] / δ [%BW]")
ax3.set_xlabel("t [s]")
ax3.legend(loc="upper right", fontsize=8)
ax3.grid(alpha=0.3)


def actualizar(_frame):
    leer_nuevas_filas()
    if not datos["t"]:
        return l_r, l_f, l_e, l_u, l_d
    t = datos["t"]
    t0 = max(0.0, t[-1] - A.ventana_s)
    i0 = 0
    for i0, tt in enumerate(t):
        if tt >= t0:
            break
    ts = t[i0:]
    l_r.set_data(ts, datos["r_corregida"][i0:])
    l_f.set_data(ts, datos["F_med"][i0:])
    l_e.set_data(ts, datos["e"][i0:])
    l_u.set_data(ts, datos["u"][i0:])
    l_d.set_data(ts, datos["delta"][i0:])
    for ax, ys in ((ax1, datos["r_corregida"][i0:] + datos["F_med"][i0:]),
                   (ax2, datos["e"][i0:]),
                   (ax3, datos["u"][i0:] + datos["delta"][i0:])):
        ax.set_xlim(t0, max(t0 + A.ventana_s, ts[-1] if ts else t0 + A.ventana_s))
        if ys:
            lo, hi = min(ys), max(ys)
            pad = max(1.0, (hi - lo) * 0.1)
            ax.set_ylim(lo - pad, hi + pad)
    return l_r, l_f, l_e, l_u, l_d


plt.tight_layout()

if A.guardar:
    # Archivo ya completo (no va a crecer mas): se lee entero una vez y se recorre con un
    # cursor de tiempo, para poder "ver" el lazo avanzar sin necesitar que algo lo escriba en vivo.
    leer_nuevas_filas()
    if not datos["t"]:
        raise SystemExit("El archivo no tiene filas -- generar con generar_datos_sinteticos.py primero.")
    t_max = datos["t"][-1]
    n_cuadros = A.cuadros  # total fijo, repartido en todo el archivo (no depende de la duracion)

    def actualizar_guardado(frame_idx):
        t0 = (frame_idx / max(1, n_cuadros - 1)) * max(0.0, t_max - A.ventana_s)
        i0 = 0
        for i0, tt in enumerate(datos["t"]):
            if tt >= t0:
                break
        i1 = i0
        for i1, tt in enumerate(datos["t"]):
            if tt >= t0 + A.ventana_s:
                break
        ts = datos["t"][i0:i1] or [t0]
        l_r.set_data(ts, datos["r_corregida"][i0:i1])
        l_f.set_data(ts, datos["F_med"][i0:i1])
        l_e.set_data(ts, datos["e"][i0:i1])
        l_u.set_data(ts, datos["u"][i0:i1])
        l_d.set_data(ts, datos["delta"][i0:i1])
        for ax, ys in ((ax1, datos["r_corregida"][i0:i1] + datos["F_med"][i0:i1]),
                       (ax2, datos["e"][i0:i1]),
                       (ax3, datos["u"][i0:i1] + datos["delta"][i0:i1])):
            ax.set_xlim(t0, t0 + A.ventana_s)
            if ys:
                lo, hi = min(ys), max(ys)
                pad = max(1.0, (hi - lo) * 0.1)
                ax.set_ylim(lo - pad, hi + pad)
        return l_r, l_f, l_e, l_u, l_d

    ani = animation.FuncAnimation(fig, actualizar_guardado, frames=n_cuadros, cache_frame_data=False)
    ani.save(A.guardar, writer=animation.PillowWriter(fps=A.fps))
    print(f"GIF guardado: {A.guardar} ({n_cuadros} cuadros, cubre {t_max:.1f} s de datos a 2x)")
else:
    ani = animation.FuncAnimation(fig, actualizar, interval=A.intervalo_ms, cache_frame_data=False)
    plt.show()
