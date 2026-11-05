"""Visor en vivo del Ensayo A: lee logs/ensayo_A_en_vivo.csv (que escribe ensayo_A_rigidez.py) cada 200 ms.
Proceso aparte: NO usa SPI ni puerto serie, se puede abrir/cerrar sin afectar el ensayo.
Paneles: F(t) (ultimos --ventana-s s) y F vs mm bajados (bajada/subida: la separacion es la histeresis).
--png salida.png renderiza el archivo completo sin ventana (para probar)."""
import argparse, os, sys, csv
ap = argparse.ArgumentParser()
ap.add_argument("archivo", nargs="?", default="logs/ensayo_A_en_vivo.csv")
ap.add_argument("--ventana-s", type=float, default=20.0)
ap.add_argument("--png", default=None)
a = ap.parse_args()
import matplotlib
if a.png: matplotlib.use("Agg")
else:
    os.environ.setdefault("XDG_RUNTIME_DIR", "/run/user/%d" % os.getuid()); os.environ.setdefault("WAYLAND_DISPLAY", "wayland-0")
    os.environ.setdefault("DISPLAY", ":0"); matplotlib.use("TkAgg")
import matplotlib.pyplot as plt

def leer():
    t, fase, mm, F, tit = [], [], [], [], ""
    try:
        for l in open(a.archivo):
            if l.startswith("# angulo"): tit = l[2:].strip()
            elif l.startswith("#") or l.startswith("t_s"): continue
            else:
                p = l.strip().split(",")
                if len(p) == 4:
                    try: t.append(float(p[0])); fase.append(p[1]); mm.append(float(p[2])); F.append(float(p[3]))
                    except ValueError: pass
    except FileNotFoundError: pass
    return t, fase, mm, F, tit

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), facecolor="white")
COL = {"aprox": "tab:gray", "fino": "tab:blue", "sube": "tab:red", "sube2": "tab:red"}
def dibujar(_=None):
    t, fase, mm, F, tit = leer()
    ax1.clear(); ax2.clear()
    if t:
        t1 = t[-1]; i0 = next((i for i, x in enumerate(t) if x >= t1 - a.ventana_s), 0) if not a.png else 0
        ax1.plot(t[i0:], F[i0:], lw=1, color="k"); ax1.set_xlim(t[i0], max(t1, t[i0] + 1))
        for nom in ("aprox", "fino", "sube"):
            xs = [m for m, f in zip(mm, fase) if f.startswith(nom)]; ys = [v for v, f in zip(F, fase) if f.startswith(nom)]
            if xs: ax2.plot(xs, ys, ".", ms=3, color=COL[nom], label={"aprox": "aproximacion", "fino": "bajada fina", "sube": "subida"}[nom])
        fx = [m for m, f in zip(mm, fase) if f.startswith("fino") or f.startswith("sube")]
        if fx: ax2.set_xlim(min(fx) - 1, max(fx) + 1)   # zoom a la zona de contacto
        ax2.legend(loc="upper left", fontsize=8)
        ax1.set_title(f"Fz ahora = {F[-1]:.1f} N   |   bajado = {mm[-1]:.1f} mm", fontsize=10)
    ax1.set_xlabel("t [s]"); ax1.set_ylabel("Fz [N] (tara previa al ensayo)"); ax1.grid(alpha=.3)
    ax2.set_xlabel("descenso acumulado [mm]"); ax2.set_ylabel("Fz [N]"); ax2.grid(alpha=.3)
    fig.suptitle(tit or "Ensayo A: esperando datos...", fontsize=9)
if a.png:
    dibujar(); fig.savefig(a.png, dpi=110, facecolor="white"); print("guardado", a.png)
else:
    from matplotlib.animation import FuncAnimation
    an = FuncAnimation(fig, dibujar, interval=200, cache_frame_data=False); plt.show()
