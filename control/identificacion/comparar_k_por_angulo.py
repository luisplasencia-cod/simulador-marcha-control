"""Compara k entre corridas del Ensayo A (distintos angulos / pies). Uso:
  python comparar_k_por_angulo.py [carpeta_o_csv ...] [--png salida.png]
Imprime tabla k por tramos de fuerza (bajada fina), variacion relativa entre corridas e histeresis
(integrales de bajada y subida, N*mm = mJ; orientativo si los rangos de F difieren). Fondo blanco."""
import argparse, glob, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ajuste_k import k_por_bandas, BANDAS
ap = argparse.ArgumentParser(); ap.add_argument("rutas", nargs="*", default=["control/identificacion/resultados"]); ap.add_argument("--png", default=None)
a = ap.parse_args()
archivos = []
for r in a.rutas: archivos += sorted(glob.glob(str(Path(r) / "ensayo_A_ang*.csv"))) if Path(r).is_dir() else [r]
def leer(f):
    cab, mm, F, fase = "", [], [], []
    for l in open(f):
        if l.startswith("# angulo"): cab = l[2:].strip()
        elif l.startswith("#") or l.startswith("t_s"): continue
        else:
            p = l.strip().split(",")
            if len(p) == 4: fase.append(p[1]); mm.append(float(p[2])); F.append(float(p[3]))
    return cab, fase, mm, F
def trapz(x, y): return sum((x[i+1]-x[i])*(y[i]+y[i+1])/2 for i in range(len(x)-1))
datos = []
for f in archivos:
    cab, fase, mm, F = leer(f)
    baj = [(m, v) for m, v, ph in zip(mm, F, fase) if ph == "fino"]; sub = [(m, v) for m, v, ph in zip(mm, F, fase) if ph == "sube"]
    ks = k_por_bandas([p[0] for p in baj], [p[1] for p in baj])
    h = None
    if len(baj) > 2 and len(sub) > 2:
        sb = sorted(baj); ss = sorted(sub)
        h = (trapz([p[0] for p in sb], [p[1] for p in sb]), trapz([p[0] for p in ss], [p[1] for p in ss]))
    datos.append((Path(f).name, cab, ks, baj, sub, h))
if not datos: sys.exit("No hay corridas ensayo_A_ang*.csv")
print(f"{'corrida':<52}" + "".join(f"{b[0]:>13}" for b in BANDAS))
for nom, cab, ks, baj, sub, h in datos:
    print(f"{nom[:51]:<52}" + "".join(f"{('%.1f' % ks[b[0]][0]) if ks[b[0]][0] is not None else 'n/d':>13}" for b in BANDAS))
print("\nVariacion entre corridas (max-min)/media, por tramo:")
for b in BANDAS:
    v = [d[2][b[0]][0] for d in datos if d[2][b[0]][0] is not None]
    print(f"  {b[0]:<11}", f"{100*(max(v)-min(v))/(sum(v)/len(v)):.1f} %  (n corridas={len(v)})" if len(v) >= 2 else "n/d (menos de 2 corridas con datos)")
print("\nHisteresis (integral de F sobre el desplazamiento, N*mm = mJ; bajada vs subida, rangos no identicos -> orientativo):")
for nom, cab, ks, baj, sub, h in datos:
    print(f"  {nom[:51]:<52}", f"bajada={h[0]:.0f}  subida={h[1]:.0f}  diferencia={h[0]-h[1]:.0f} mJ" if h else "n/d (sin subida registrada)")
if a.png:
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(8, 5), facecolor="white")
    for nom, cab, ks, baj, sub, h in datos:
        etq = cab.split("hueco")[0].strip() or nom
        l, = ax.plot([p[0] for p in baj], [p[1] for p in baj], ".-", ms=3, label=etq)
        if sub: ax.plot([p[0] for p in sub], [p[1] for p in sub], "--", color=l.get_color(), lw=1)
    ax.set_xlabel("descenso acumulado [mm] (hueco distinto por corrida)"); ax.set_ylabel("Fz [N]"); ax.grid(alpha=.3); ax.legend(fontsize=8)
    ax.set_title("Ensayo A: F vs descenso (continuo = bajada, discontinuo = subida)", fontsize=10)
    fig.savefig(a.png, dpi=110, facecolor="white"); print("guardado", a.png)
