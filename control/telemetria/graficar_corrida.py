"""Grafica una corrida del lazo de Fz (CSV de control/telemetria/registros/): F medida por ciclo vs referencia, error real r-F y u.
Imprime RMS real (r-F), picos y valle por ciclo. Uso: graficar_corrida.py <csv> [--titulo "..."] [--salida x.png] [--mostrar]"""
import argparse, csv, os, subprocess, sys
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
ap = argparse.ArgumentParser(); ap.add_argument("csv"); ap.add_argument("--titulo", default=""); ap.add_argument("--salida"); ap.add_argument("--mostrar", action="store_true")
a = ap.parse_args()
rows = list(csv.DictReader(open(a.csv)))
t = np.array([float(x["t"]) for x in rows]); c = np.array([int(x["ciclo"]) for x in rows]); ref = np.array([float(x["r"]) for x in rows])
F = np.array([float(x["F_med"]) for x in rows]); u = np.array([float(x["u"]) for x in rows]); n = int(c.max()) + 1
cmap = plt.get_cmap("viridis")
fig, ax = plt.subplots(3, 1, figsize=(13, 9), facecolor="white", sharex=True)
rms = []
for k in range(n):
    m = c == k; col = cmap(k / max(1, n - 1)); e = ref[m] - F[m]; rms.append(float(np.sqrt(np.mean(e ** 2))))
    ax[0].plot(t[m], F[m], color=col, lw=.9, label=f"ciclo {k} (RMS {rms[-1]:.2f} N)"); ax[1].plot(t[m], e, color=col, lw=.7); ax[2].plot(t[m], u[m], color=col, lw=.7)
    tm, Fm = t[m], F[m]
    def _f(sel, fn): v = Fm[sel]; return f"{fn(v):.1f}" if v.size else "-"      # pisada abortada: tramos vacíos
    print(f"ciclo {k}: RMS(r-F) {rms[-1]:.2f} N | pico1 {_f((tm>.5)&(tm<1.3), np.max)} valle {_f((tm>1.4)&(tm<2.2), np.min)} pico2 {_f((tm>2.4)&(tm<3.3), np.max)} N | |u| max {abs(u[m]).max():.0f} pasos/s | hasta t={tm.max():.2f} s")
ax[0].plot(t[c == 0], ref[c == 0], "k--", lw=1.6, label="referencia r(t)"); ax[0].legend(ncol=2, fontsize=8); ax[0].set_ylabel("Fz [N]"); ax[0].grid(alpha=.3)
ax[1].set_ylabel("error real r - F [N]"); ax[1].grid(alpha=.3); ax[2].set_ylabel("u = SET_VEL [pasos/s]\n(+ sube, - baja)"); ax[2].set_xlabel("t dentro del ciclo [s]"); ax[2].grid(alpha=.3)
fig.suptitle((a.titulo or os.path.basename(a.csv)) + f"\nRMS real por ciclo: " + " → ".join(f"{x:.1f}" for x in rms) + " N", fontsize=11)
fig.tight_layout(rect=(0, 0, 1, .94)); out = a.salida or a.csv.replace(".csv", ".png"); fig.savefig(out, dpi=100, facecolor="white"); print(out)
if a.mostrar:
    subprocess.Popen([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "herramientas", "mostrar_figura.py"), out], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
