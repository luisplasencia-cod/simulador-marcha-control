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
# posición ORDENADA de Y (mm, + = arriba): columna y_mm desde 2026-11-18; en logs anteriores se reconstruye integrando u
y = np.array([float(x["y_mm"]) for x in rows]) if "y_mm" in rows[0] else np.cumsum(u * 0.01) / 80.0
v = u / 80.0                                                      # mm/s, + = subir
cmap = plt.get_cmap("viridis")
fig, ax = plt.subplots(4, 1, figsize=(13, 11.5), facecolor="white", sharex=True)
rms = []
for k in range(n):
    m = c == k; col = cmap(k / max(1, n - 1)); e = ref[m] - F[m]; rms.append(float(np.sqrt(np.mean(e ** 2))))
    ax[0].plot(t[m], F[m], color=col, lw=.9, label=f"ciclo {k} (RMS {rms[-1]:.2f} N)"); ax[1].plot(t[m], e, color=col, lw=.7)
    ax[2].plot(t[m], y[m], color=col, lw=.9); ax[3].plot(t[m], v[m], color=col, lw=.7)
    tm, Fm = t[m], F[m]
    T = t.max() + 0.01                                                    # duración del ciclo (depende de la escala de tiempo)
    def _f(sel, fn): v = Fm[sel]; return f"{fn(v):.1f}" if v.size else "-"      # pisada abortada: tramos vacíos
    print(f"ciclo {k}: RMS(r-F) {rms[-1]:.2f} N | pico1 {_f((tm>.136*T)&(tm<.352*T), np.max)} valle {_f((tm>.38*T)&(tm<.6*T), np.min)} pico2 {_f((tm>.65*T)&(tm<.9*T), np.max)} N | |v| max {abs(v[m]).max():.0f} mm/s | Y {y[m].min():.1f}..{y[m].max():.1f} mm | hasta t={tm.max():.2f} s")
ax[0].plot(t[c == 0], ref[c == 0], "k--", lw=1.6, label="referencia r(t)"); ax[0].legend(ncol=2, fontsize=8); ax[0].set_ylabel("Fz [N]"); ax[0].grid(alpha=.3)
ax[1].set_ylabel("error real r - F [N]"); ax[1].grid(alpha=.3); ax[2].set_ylabel("Y ordenada [mm]\n(+ arriba, desde el inicio)"); ax[2].grid(alpha=.3)
ax[3].set_ylabel("velocidad de Y [mm/s]\n(+ sube; 80 pasos/mm)"); ax[3].set_xlabel("t dentro del ciclo [s]"); ax[3].grid(alpha=.3)
fig.suptitle((a.titulo or os.path.basename(a.csv)) + f"\nRMS real por ciclo: " + " → ".join(f"{x:.1f}" for x in rms) + " N", fontsize=11)
fig.tight_layout(rect=(0, 0, 1, .94)); out = a.salida or a.csv.replace(".csv", ".png"); fig.savefig(out, dpi=100, facecolor="white"); print(out)
if a.mostrar:
    subprocess.Popen([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "herramientas", "mostrar_figura.py"), out], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
