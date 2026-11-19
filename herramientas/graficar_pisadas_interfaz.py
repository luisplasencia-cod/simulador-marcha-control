"""Grafica pisadas registradas por la interfaz vigente (~/Projects/gaitsim-control/logs/fz/*.csv:
t_s, objetivo_N, delta_ilc_N, Fz_N, vel_pasos_s). Uso: graficar_pisadas_interfaz.py salida.png csv1 [csv2 ...]"""
import sys, csv, os
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
salida, archivos = sys.argv[1], sys.argv[2:]
fig, ax = plt.subplots(4, 1, figsize=(11, 11), sharex=True)
for f in archivos:
    r = list(csv.DictReader(open(f)))
    t = [float(x["t_s"]) for x in r]; col = lambda k: [float(x[k]) for x in r]
    et = os.path.basename(f).replace("_Control_apoyo_talla170_montaje37", "").replace(".csv", "")
    l, = ax[0].plot(t, col("Fz_N"), label=f"Fz {et}")
    ax[0].plot(t, col("objetivo_N"), "--", color=l.get_color(), alpha=.6)
    ax[1].plot(t, [a - b for a, b in zip(col("objetivo_N"), col("Fz_N"))], color=l.get_color(), label=et)
    ax[2].plot(t, col("delta_ilc_N"), color=l.get_color(), label=et)
    ax[3].plot(t[1:], [1000 * (b - a) for a, b in zip(t, t[1:])], color=l.get_color(), label=et)
ax[0].set_ylabel("Fz [N] (-- objetivo)"); ax[1].set_ylabel("error obj-Fz [N]")
ax[2].set_ylabel("delta ILC [N]"); ax[3].set_ylabel("periodo del lazo [ms]"); ax[3].set_xlabel("t [s]")
for a in ax: a.grid(alpha=.3); a.legend(fontsize=7)
fig.suptitle("Pisadas desde la interfaz (ver LEEME) — X y ángulo lazo abierto, Y lazo cerrado de Fz")
fig.tight_layout(); fig.savefig(salida, dpi=110); print(salida)
