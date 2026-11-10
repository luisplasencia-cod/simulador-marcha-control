"""Visor en vivo (pantalla del RPi) de cualquier prueba que use herramientas/en_vivo.py.
Proceso aparte: NO usa SPI ni puerto serie. Muestra: Fz(t) con las fases sombreadas, contador de Y(t) y, en grande,
QUE se esta haciendo ahora. --png salida.png renderiza el archivo completo sin ventana (para probar)."""
import argparse, os
ap = argparse.ArgumentParser()
ap.add_argument("archivo", nargs="?", default="logs/prueba_en_vivo.csv")
ap.add_argument("--ventana-s", type=float, default=40.0)
ap.add_argument("--png", default=None)
a = ap.parse_args()
import matplotlib
if a.png: matplotlib.use("Agg")
else:
    os.environ.setdefault("XDG_RUNTIME_DIR", "/run/user/%d" % os.getuid()); os.environ.setdefault("WAYLAND_DISPLAY", "wayland-0")
    os.environ.setdefault("DISPLAY", ":0"); matplotlib.use("TkAgg")
import matplotlib.pyplot as plt


def leer():
    t, fase, F, y, msg, tit, fin = [], [], [], [], [], "", ""
    try:
        for l in open(a.archivo):
            if l.startswith("#"):
                if not t: tit = l[1:].strip()
                else: fin = l[1:].strip()
                continue
            p = l.rstrip("\n").split(",", 4)
            if len(p) == 5:
                try: t.append(float(p[0])); fase.append(p[1]); F.append(float(p[2])); y.append(int(p[3])); msg.append(p[4])
                except ValueError: pass
    except FileNotFoundError: pass
    return t, fase, F, y, msg, tit, fin


fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), facecolor="white", sharex=True, gridspec_kw={"height_ratios": [3, 1]})
if not a.png:
    try:
        w = fig.canvas.manager.window; w.attributes("-topmost", True); w.attributes("-zoomed", True)
    except Exception: pass
PAL = ["#dbeafe", "#fde68a", "#d1fae5", "#fecaca", "#e9d5ff", "#fed7aa", "#cffafe"]


def dibujar(_=None):
    t, fase, F, y, msg, tit, fin = leer()
    ax1.clear(); ax2.clear()
    if t:
        t1 = t[-1]; i0 = 0 if a.png else next((i for i, x in enumerate(t) if x >= t1 - a.ventana_s), 0)
        # fases sombreadas
        nombres, k, ini = {}, i0, i0
        for i in range(i0, len(t) + 1):
            if i == len(t) or fase[i] != fase[ini]:
                c = PAL[nombres.setdefault(fase[ini], len(nombres)) % len(PAL)]
                for ax in (ax1, ax2): ax.axvspan(t[ini], t[min(i, len(t) - 1)], color=c, alpha=.6, lw=0)
                ax1.text(t[ini], ax1.get_ylim()[1] if False else 0, "", fontsize=1)
                ini = i
        ax1.plot(t[i0:], F[i0:], lw=1, color="k"); ax2.plot(t[i0:], y[i0:], lw=1.5, color="tab:blue")
        ax1.set_xlim(t[i0], max(t1, t[i0] + 1))
        mov = abs(y[-1]) > 0
        ax1.set_title(f"Fz = {F[-1]:+.1f} N", fontsize=34, color="#b00020" if abs(F[-1]) > 20 else "black", loc="left")
        ax2.set_title(f"Y (pasos emitidos) = {y[-1]}  ({y[-1]/80:+.1f} mm)", fontsize=14, loc="left")
        fig.suptitle(f"{msg[-1]}   [fase: {fase[-1]}]" + (f"   --  {fin}" if fin else ""), fontsize=22, fontweight="bold",
                     color="#b00020" if "ABORT" in (fin + msg[-1]).upper() else "#14532d")
    else:
        fig.suptitle(tit or "esperando datos...", fontsize=18)
    ax1.set_ylabel("Fz [N] (con tara)"); ax1.grid(alpha=.3); ax2.set_ylabel("Y [pasos]"); ax2.set_xlabel("t [s]"); ax2.grid(alpha=.3)


if a.png:
    dibujar(); fig.savefig(a.png, dpi=100, facecolor="white"); print("guardado", a.png)
else:
    from matplotlib.animation import FuncAnimation
    an = FuncAnimation(fig, dibujar, interval=200, cache_frame_data=False); plt.show()
