"""Grafica el CSV que genera medir_latencia_ping_pong.py: histograma de RTT +
serie temporal (para ver si hay deriva o picos de jitter a lo largo de la prueba).
Uso (en el RPi, despues de correr medir_latencia_ping_pong.py):
    pip install matplotlib
    python graficar_latencia.py --csv latencia_ping_pong.csv
"""
import argparse
import csv
import statistics

import matplotlib.pyplot as plt

ap = argparse.ArgumentParser()
ap.add_argument("--csv", default="latencia_ping_pong.csv")
ap.add_argument("--salida", default="latencia_ping_pong.png")
a = ap.parse_args()

intentos, rtts = [], []
with open(a.csv, newline="") as f:
    for row in csv.DictReader(f):
        if row["estado"] == "OK":
            intentos.append(int(row["intento"]))
            rtts.append(float(row["rtt_ms"]))

if not rtts:
    raise SystemExit(f"No hay datos validos en {a.csv}")

media = statistics.mean(rtts)
desv = statistics.pstdev(rtts)

AZUL = "#2563eb"
GRIS = "#6b7280"

plt.rcParams.update({"font.size": 11, "axes.edgecolor": "#d1d5db", "axes.grid": True,
                      "grid.color": "#e5e7eb", "grid.linewidth": 0.8})

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))

ax1.hist(rtts, bins=20, color=AZUL, edgecolor="white", linewidth=0.5)
ax1.axvline(media, color=GRIS, linestyle="--", linewidth=1.5, label=f"media {media:.2f} ms")
ax1.set_title("Distribucion de latencia RTT")
ax1.set_xlabel("RTT (ms)")
ax1.set_ylabel("Cantidad de intentos")
ax1.legend(frameon=False)
ax1.spines[["top", "right"]].set_visible(False)

ax2.scatter(intentos, rtts, s=14, color=AZUL, alpha=0.8)
ax2.axhline(media, color=GRIS, linestyle="--", linewidth=1.5)
ax2.set_title("RTT por intento (deriva / picos)")
ax2.set_xlabel("Numero de intento")
ax2.set_ylabel("RTT (ms)")
ax2.spines[["top", "right"]].set_visible(False)

fig.suptitle(f"Latencia RPi<->ESP32 (PING/PONG) — N={len(rtts)}, media={media:.2f} ms, "
             f"desv={desv:.2f} ms, min={min(rtts):.2f}, max={max(rtts):.2f}", fontsize=11)
fig.tight_layout(rect=[0, 0, 1, 0.94])
fig.savefig(a.salida, dpi=150)
print(f"Grafico guardado en: {a.salida}")
