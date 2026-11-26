"""Compara normalizaciones del error del lazo de Fz con los datos ya medidos (2026-11-26).

Pregunta: ¿qué métrica de error usar para decir "Fz cerrado"? RMSE en N, RMSE en %BW, NRMSE por el pico,
por el rango, por la media o por la DE de la curva, y r de Pearson.

Datos (solo los que traen el peso del sujeto): reportes/datos/
  - interfaz 3 ejes 2026-11-19 (40/60/75/80 kg, talla 170; 80 kg talla 174): CSV por pisada (t_s, objetivo_N, Fz_N)
  - script solo Y 2026-11-19 mejora ff/ILC a 80 kg (A_base, B_ff07_m30): CSV por pisada
  - script solo Y 2026-11-18 escalera 50-90 kg y 2026-11-19 Kp 3/5/8: <hora>_fz.csv (t, ciclo, r, F_med) + .meta.txt (peso_sujeto_n)
  Se omite 2026-11-18_pisadas_3ejes_interfaz (sin peso registrado, series casi todas abortadas).
Error e = referencia - Fz medida, sobre TODA la pisada (regla de Luis 2026-11-20); referencia SIN el delta del ILC.
"Estabilizadas" = las últimas 3 pisadas de cada serie (el ILC ya aprendió); en series de <=4 pisadas, la última 2.
Uso: python comparar_normalizaciones_rmse.py   (escribe comparar_normalizaciones_rmse.csv/.txt/.png en reportes/)
"""
import csv
import glob
import os
import re

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATOS = os.path.join(RAIZ, "reportes", "datos")
SALIDA = os.path.join(RAIZ, "reportes", "figuras", "2026-11-26_normalizaciones_rmse")
G = 9.81
METRICAS = ["RMSE_N", "pct_BW", "pct_pico", "pct_rango", "pct_media", "pct_DE", "r"]


def met(r, F, peso_n):
    e = r - F
    rm = float(np.sqrt(np.mean(e ** 2)))
    return {"RMSE_N": rm, "pct_BW": 100 * rm / peso_n, "pct_pico": 100 * rm / r.max(),
            "pct_rango": 100 * rm / (r.max() - r.min()), "pct_media": 100 * rm / r.mean(),
            "pct_DE": 100 * rm / r.std(), "r": float(np.corrcoef(r, F)[0, 1])}


def leer_pisadas(carpeta, kg, nombre, tipo):
    series = {}
    for f in glob.glob(os.path.join(carpeta, "*_p*.csv")):
        mt = re.search(r"(\d{8}_\d{6}).*_p(\d+)\.csv$", os.path.basename(f))
        with open(f, newline="") as fh:
            filas = list(csv.DictReader(fh))
        r = np.array([float(x["objetivo_N"]) for x in filas]); F = np.array([float(x["Fz_N"]) for x in filas])
        series.setdefault(mt.group(1), []).append((int(mt.group(2)), r, F))
    out = []
    for hora, lst in series.items():
        lst.sort(key=lambda x: x[0])
        out.append({"serie": f"{nombre} {hora[9:]}", "tipo": tipo, "kg": kg, "pisadas": [(p, r, F) for p, r, F in lst]})
    return out


def leer_fz(f, tipo, etiqueta):
    meta = open(f.replace("_fz.csv", "_fz.meta.txt")).read()
    peso = float(re.search(r"peso_sujeto_n=([\d.]+)", meta).group(1))
    kp = re.search(r"kp=([\d.]+)", meta).group(1) + ("prog" if "kp_programado=True" in meta else "")
    with open(f, newline="") as fh:
        filas = list(csv.DictReader(fh))
    c = np.array([int(x["ciclo"]) for x in filas]); r = np.array([float(x["r"]) for x in filas])
    F = np.array([float(x["F_med"]) for x in filas])
    pis = [(int(k) + 1, r[c == k], F[c == k]) for k in np.unique(c)]
    return {"serie": f"{etiqueta} Kp{kp} {os.path.basename(f)[11:17]}", "tipo": tipo, "kg": round(peso / G), "pisadas": pis}


def cargar():
    S = []
    for kg in (40, 60, 75, 80):
        S += leer_pisadas(os.path.join(DATOS, f"2026-11-19_pisadas_3ejes_interfaz_{kg}kg"), kg, f"interfaz 3 ejes {kg} kg", "interfaz_3ejes_t170")
    S += leer_pisadas(os.path.join(DATOS, "2026-11-19_pisadas_3ejes_interfaz_80kg_talla174"), 80, "interfaz 3 ejes 80 kg t174", "interfaz_3ejes_t174")
    for sub, et in (("A_base", "solo Y base"), ("B_ff07_m30", "solo Y ff0.7+30ms")):
        S += leer_pisadas(os.path.join(DATOS, "2026-11-19_mejora_ff_ilc_80kg", sub), 80, f"{et} 80 kg", "soloY_mejora")
    for f in sorted(glob.glob(os.path.join(DATOS, "2026-11-18_escalera_50_90kg_x10", "*_fz.csv"))):
        S.append(leer_fz(f, "soloY_escalera", "escalera solo Y"))
    for f in sorted(glob.glob(os.path.join(DATOS, "2026-11-19_kp3_vs_kp5_70kg", "*_fz.csv"))):
        S.append(leer_fz(f, "soloY_kp", "solo Y"))
    for s in S:
        peso = s["kg"] * G
        s["m"] = [met(r, F, peso) for _, r, F in s["pisadas"]]
        n = len(s["m"]); k = 3 if n > 4 else 2
        s["est"] = {q: float(np.median([x[q] for x in s["m"][-k:]])) for q in METRICAS}
        s["pico_obj_pctBW"] = 100 * max(r.max() for _, r, _ in s["pisadas"]) / peso
    return S


def main():
    S = cargar()
    lin = ["Error estabilizado (mediana de las últimas pisadas) por serie", "serie | kg | n | " + " | ".join(METRICAS) + " | pico_obj %BW"]
    for s in S:
        e = s["est"]
        lin.append(f"{s['serie']} | {s['kg']} | {len(s['m'])} | " + " | ".join(f"{e[q]:.3f}" if q == "r" else f"{e[q]:.2f}" for q in METRICAS)
                   + f" | {s['pico_obj_pctBW']:.1f}")
    # dependencia con la carga: mismo tipo de ensayo a varias cargas
    lin += ["", "Dependencia con la carga (series de un mismo tipo a distintas cargas): pendiente de un ajuste lineal metrica~kg",
            "y CV entre cargas [%]. Una métrica que no depende de la carga deja comparar 40 kg con 80 kg."]
    for tipo in ("interfaz_3ejes_t170", "soloY_escalera"):
        ss = [s for s in S if s["tipo"] == tipo]
        kg = np.array([s["kg"] for s in ss], float)
        lin.append(f"  {tipo} (cargas {sorted(set(kg.astype(int)))}):")
        for q in METRICAS:
            y = np.array([s["est"][q] for s in ss])
            b = np.polyfit(kg, y, 1)[0]
            lin.append(f"    {q:9s} pendiente {b:+.4f} /kg  (cambio 40->80 kg {100 * b * 40 / y.mean():+.0f} % de la media)  CV {100 * y.std(ddof=1) / y.mean():.0f} %")
    # repetibilidad: mismas condiciones repetidas
    rep = [s for s in S if s["tipo"] == "soloY_kp" and s["kg"] == 70 and "Kp5.0 " in s["serie"]]
    if len(rep) >= 2:
        lin += ["", "Repetición (solo Y, 70 kg, Kp 5 fijo, 2 corridas): " +
                "; ".join(f"{q} {rep[0]['est'][q]:.3f} vs {rep[1]['est'][q]:.3f}" for q in ("pct_BW", "pct_pico", "r"))]
    txt = "\n".join(lin)
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    open(SALIDA + ".txt", "w", encoding="utf-8").write(txt)
    with open(SALIDA + ".csv", "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["serie", "tipo", "kg", "pisada", *METRICAS])
        for s in S:
            for (p, _, _), m in zip(s["pisadas"], s["m"]):
                w.writerow([s["serie"], s["tipo"], s["kg"], p, *[f"{m[q]:.4f}" for q in METRICAS]])
    # figura: métrica estabilizada vs carga, una columna por normalización
    fig, ax = plt.subplots(1, 4, figsize=(16, 4.2))
    for a_, q, tit in zip(ax, ("RMSE_N", "pct_BW", "pct_pico", "r"),
                          ("RMSE [N] (sin normalizar)", "RMSE [% del peso corporal]", "RMSE [% del pico del objetivo]", "r de Pearson")):
        for tipo, mk, lab in (("interfaz_3ejes_t170", "o", "Interfaz, 3 ejes"), ("soloY_escalera", "s", "Solo Y, escalera 11-18"),
                              ("soloY_kp", "^", "Solo Y, Kp 11-19"), ("soloY_mejora", "D", "Solo Y, mejora ff/ILC")):
            ss = [s for s in S if s["tipo"] == tipo]
            a_.plot([s["kg"] for s in ss], [s["est"][q] for s in ss], mk, ms=7, label=lab, alpha=.8)
        if q == "pct_BW":
            a_.axhline(5.0, ls="--", color="tab:red", label="Fukuchi 0,50 m/s, mediana (5,1 %BW)")
            a_.axhline(4.0, ls=":", color="tab:red", label="Fukuchi 1,24 m/s, mediana (4,0 %BW)")
            a_.set_ylim(0, 6)
        if q == "r":
            a_.axhline(0.986, ls="--", color="tab:red", label="Fukuchi p25 (0,986)")
        a_.set_title(tit, fontsize=10); a_.set_xlabel("carga del sujeto simulado [kg]"); a_.grid(alpha=.3)
    ax[0].legend(fontsize=7); ax[1].legend(fontsize=7, loc="lower right"); ax[3].legend(fontsize=7, loc="lower left")
    fig.suptitle("Error del lazo de Fz con distintas normalizaciones (últimas pisadas de cada serie, datos 18 y 19-nov)", fontsize=11)
    fig.text(0.01, 0.005, "RMSE = raíz del error cuadrático medio (objetivo − Fz medida) sobre toda la pisada. %BW = respecto al peso "
             "corporal. Línea roja = variabilidad paso a paso de una persona sana (Fukuchi 2018).", fontsize=7.5)
    fig.tight_layout(rect=(0, 0.03, 1, 0.95)); fig.savefig(SALIDA + ".png", dpi=130)
    print(txt); print(SALIDA + ".png")


if __name__ == "__main__":
    main()
