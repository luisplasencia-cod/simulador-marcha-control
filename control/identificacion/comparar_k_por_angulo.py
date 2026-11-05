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
for r in a.rutas:
    if Path(r).is_dir(): archivos += sorted(glob.glob(str(Path(r) / "ensayo_A_ang*.csv")) + glob.glob(str(Path(r) / "RAW_en_vivo_*.csv")))
    else: archivos.append(r)
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
    def etiqueta(cab, nom):
        d = dict(t.split("=", 1) for t in cab.split() if "=" in t)
        return f"{d.get('etiqueta') or 'sin etiqueta'} ({float(d['angulo_sagital_deg']):+.1f}\u00b0)" if "angulo_sagital_deg" in d else nom
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(13, 5.2), facecolor="white", gridspec_kw={"width_ratios": [1.6, 1]})
    col = ["#1f77b4", "#d62728", "#2ca02c", "#9467bd", "#ff7f0e"]
    nombres, kglob = [], []
    for j, (nom, cab, ks, baj, sub, h) in enumerate([d for d in datos if len(d[3]) >= 3]):
        pts = sorted(p for p in baj if p[1] >= 0)
        c0 = next((m for m, v in pts if v >= 3.0), pts[0][0] if pts else 0)   # punto de contacto (primer F>=3 N)
        et = etiqueta(cab, nom); k = ks["todo >=8 N"][0]
        ax.plot([m - c0 for m, v in pts], [v for m, v in pts], "o-", ms=3.5, lw=1.4, color=col[j % 5], label=f"{et}: k = {k:.1f} N/mm" if k else et)
        if sub:
            ss = sorted(sub); ax.plot([m - c0 for m, v in ss], [v for m, v in ss], "--", lw=1, color=col[j % 5])
        nombres.append(et); kglob.append(k or 0)
    ax.set_xlabel("penetracion desde el contacto [mm] (desplazamiento ORDENADO, no medido)"); ax.set_ylabel("Fz [N]")
    ax.grid(alpha=.3); ax.legend(fontsize=9, loc="upper left"); ax.set_title("Curva fuerza-penetracion por condicion del pie\n(continuo = bajada, discontinuo = subida)", fontsize=10)
    bx.bar(range(len(kglob)), kglob, color=[col[j % 5] for j in range(len(kglob))])
    for j, v in enumerate(kglob): bx.text(j, v, f"{v:.1f}", ha="center", va="bottom", fontsize=10)
    bx.set_xticks(range(len(nombres))); bx.set_xticklabels([n.replace(" (", "\n(") for n in nombres], fontsize=9)
    bx.set_ylabel("k [N/mm] (ajuste lineal, F>=8 N)"); bx.set_title("Rigidez de contacto k", fontsize=10); bx.grid(alpha=.3, axis="y")
    if len(kglob) >= 2 and min(kglob) > 0: bx.set_xlabel(f"max/min = {max(kglob)/min(kglob):.2f}x   ({100*(max(kglob)-min(kglob))/(sum(kglob)/len(kglob)):.0f} % de la media)", fontsize=9)
    fig.suptitle("Ensayo A - rigidez del pie segun el angulo sagital (prototipo, una pasada por condicion)", fontsize=11)
    fig.tight_layout(); fig.savefig(a.png, dpi=120, facecolor="white"); print("guardado", a.png)
