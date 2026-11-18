"""Grafica el Ensayo B: pulsos alineados en t_cmd (superpuestos), con el ajuste retardo+rampa de cada uno. Uso: graficar_ensayo_B.py <csv> [--mostrar]"""
import sys, os, csv, subprocess
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ensayo_B_respuesta_dinamica import ajustar, PASOS_MM
ruta = sys.argv[1]
cab = open(ruta).readline().strip()
filas = [r for r in csv.reader(open(ruta)) if r and not r[0].startswith("#") and r[0] != "t_s"]
t = np.array([float(r[0]) for r in filas]); fase = [r[1] for r in filas]; F = np.array([float(r[2]) for r in filas])
ini = [i for i in range(1, len(fase)) if fase[i].startswith("baja") and not fase[i-1].startswith("baja")]
vels = sorted({int(fase[i].split("v")[-1]) for i in ini})
fig, ax = plt.subplots(1, len(vels), figsize=(7 * len(vels), 5.5), facecolor="white", squeeze=False)
for a, v in zip(ax[0], vels):
    for i in [j for j in ini if fase[j].endswith(f"v{v}")]:
        tc = t[i] - 0.0072        # el comando se emite justo antes del primer bloque de la fase
        m = (t - tc > -0.4) & (t - tc < 0.55); a.plot((t[m] - tc) * 1000, F[m], lw=.8, alpha=.7)
        r = ajustar(t - tc, F, tc, 0.2)
        if r:
            x = np.linspace(-0.3, 0.2, 100); a.plot(x * 1000, r["b_n"] + r["s_n_s"] * np.clip(x - r["d_ms"] / 1000, 0, None), "k--", lw=1)
    a.axvline(0, color="r", lw=1); a.axvline(200, color="gray", ls=":", lw=1)
    a.set(title=f"Bajada a {v} pasos/s ({v/PASOS_MM:.1f} mm/s): rojo = comando, gris = fin del pulso (luego sube)", xlabel="t - t_comando [ms]", ylabel="Fz [N]")
    a.grid(alpha=.3)
fig.suptitle("Ensayo B: respuesta de Fz a pulsos de velocidad CON contacto (ajuste retardo+rampa en negro)\n" + cab[:150], fontsize=10)
fig.tight_layout(rect=(0, 0, 1, .92))
out = ruta.replace(".csv", ".png"); fig.savefig(out, dpi=100, facecolor="white"); print(out)
if "--mostrar" in sys.argv:
    subprocess.Popen([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "herramientas", "mostrar_figura.py"), out],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
