"""Grafica la curva de Fz vs velocidad: Fukuchi 2018 (cinta, 0.50-1.81 m/s) y Gutenberg 2021 (suelo, 1.40 m/s).
Lee referencia_fz_gutenberg.csv y curva_vs_velocidad_fukuchi.csv + resumen_velocidad_fukuchi.txt (velocidades reales)."""
import csv, os, re
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

aqui = os.path.dirname(os.path.abspath(__file__))
fu = np.genfromtxt(os.path.join(aqui, "curva_vs_velocidad_fukuchi.csv"), delimiter=",", names=True)
gu = np.genfromtxt(os.path.join(aqui, "referencia_fz_gutenberg.csv"), delimiter=",", names=True)
vel = {}
for l in open(os.path.join(aqui, "resumen_velocidad_fukuchi.txt")):
    m = re.match(r"(T\d\d): velocidad ([\d.]+) m/s", l)
    if m:
        vel[m.group(1)] = float(m.group(2))
fig, ax = plt.subplots(figsize=(8.5, 5.2))
col = plt.cm.viridis(np.linspace(0.05, 0.85, len(vel)))
for c, k in zip(vel, col):
    ax.plot(fu["pct_apoyo"], fu[f"{c}_Fz_BW_media"] * 100, color=k, lw=2, label=f"Fukuchi cinta, {vel[c]:.2f} m/s")
ax.plot(gu["pct_apoyo"], gu["Fz_BW_media"] * 100, "k--", lw=2, label="Gutenberg suelo, 1.40 m/s")
ax.axhline(100, color="gray", lw=0.8, ls=":")
ax.set_xlabel("% del apoyo"); ax.set_ylabel("Fz [%BW]"); ax.set_ylim(0, 150)
ax.set_title("Fuerza vertical vs velocidad de marcha (sanos, media entre sujetos)")
ax.legend(fontsize=8, loc="lower center", ncol=2)
fig.tight_layout(); fig.savefig(os.path.join(aqui, "curvas_fz_vs_velocidad.png"), dpi=130)
