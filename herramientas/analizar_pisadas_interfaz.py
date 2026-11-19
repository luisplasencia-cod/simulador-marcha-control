#!/usr/bin/env python3
"""Analiza pisadas registradas por la interfaz vigente (~/Projects/gaitsim-control/logs/fz/*.csv).

Columnas del CSV (escritas por src/ui/screens/fz_control_screen.py):
  t_s          tiempo desde el inicio de la pisada [s]
  objetivo_N   referencia r(t) = %BW/100 * peso [N]  (SIN el delta del ILC)
  delta_ilc_N  corrección del ILC sumada a r en el lazo [N]
  Fz_N         Fz medida (ADS1256 por UART, mediana de bloque) [N]
  vel_pasos_s  SET_VEL ordenado al eje Y [pasos/s]  (+ = SUBIR Y, firmware)
Nombre: <YYYYMMDD_HHMMSS>_<trayectoria>_p<n>.csv ; una serie = mismo prefijo fecha_hora.

Salidas por serie (prefijo --salida, se añade _<serie>):
  <prefijo>_<serie>_pisadas.png   4 paneles por pisada superpuestas
  <prefijo>_<serie>_metricas.csv  tabla de métricas por pisada
y una figura resumen <prefijo>_resumen.png (RMSE y r vs pisada; RMSE por fase de la última pisada).

Desplazamiento de Y = integral de vel_pasos_s/80 (retención de orden cero: cada orden vale hasta la muestra
siguiente). Es lo ORDENADO al contador del ESP32, NO medido por sensor (no hay sensor de desplazamiento).

Uso: analizar_pisadas_interfaz.py --salida reportes/figuras/<prefijo> [--titulo "..."] csv_o_carpeta [...]
"""
import argparse
import csv
import glob
import os
import re
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PASOS_POR_MM_Y = 80.0  # confirmado 2026-11-05 (Ensayo 0)
FASES = [(0, 10), (10, 30), (30, 50), (50, 70), (70, 90), (90, 100)]
PATRON = re.compile(r"^(\d{8}_\d{6})_(.+)_p(\d+)\.csv$")


def recolectar(entradas):
    archivos = []
    for e in entradas:
        if os.path.isdir(e):
            archivos += glob.glob(os.path.join(e, "*_p*.csv"))
        else:
            archivos += glob.glob(e) or [e]
    series = {}
    for f in sorted(set(archivos)):
        m = PATRON.match(os.path.basename(f))
        if not m:
            print(f"AVISO: nombre no reconocido, se omite: {f}", file=sys.stderr)
            continue
        series.setdefault(m.group(1), []).append((int(m.group(3)), m.group(2), f))
    for k in series:
        series[k].sort()
    return series


def leer(f):
    with open(f, newline="") as fh:
        filas = list(csv.DictReader(fh))
    return {k: np.array([float(x[k]) for x in filas]) for k in ("t_s", "objetivo_N", "delta_ilc_N", "Fz_N", "vel_pasos_s")}


def rmse(x):
    return float(np.sqrt(np.mean(x ** 2))) if len(x) else float("nan")


def metricas(d):
    t, r, F, u = d["t_s"], d["objetivo_N"], d["Fz_N"], d["vel_pasos_s"]
    e = r - F
    v_mm_s = u / PASOS_POR_MM_Y
    dt = np.diff(t, prepend=0.0)
    # retención de orden cero: la orden de la muestra i-1 actúa entre t[i-1] y t[i]
    z_mm = np.concatenate([[0.0], np.cumsum(v_mm_s[:-1] * np.diff(t))])
    frac = 100.0 * t / t[-1]
    m = {
        "n_muestras": len(t),
        "duracion_s": float(t[-1]),
        "RMSE_N": rmse(e),
        "objetivo_max_N": float(r.max()),
        "F_max_N": float(F.max()),
        "RMSE_pct_pico": 100.0 * rmse(e) / float(r.max()),
        "r_pearson": float(np.corrcoef(r, F)[0, 1]),
        "error_max_abs_N": float(np.max(np.abs(e))),
        "error_max_con_signo_N": float(e[np.argmax(np.abs(e))]),
        "t_error_max_s": float(t[np.argmax(np.abs(e))]),
        "desplaz_ordenado_min_mm": float(z_mm.min()),
        "desplaz_ordenado_max_abs_mm": float(np.max(np.abs(z_mm))),
        "desplaz_ordenado_final_mm": float(z_mm[-1]),
        "vel_ordenada_max_abs_mm_s": float(np.max(np.abs(v_mm_s))),
        "delta_ilc_max_abs_N": float(np.max(np.abs(d["delta_ilc_N"]))),
    }
    for a, b in FASES:
        sel = (frac >= a) & ((frac < b) if b < 100 else (frac <= b))
        m[f"RMSE_fase_{a}_{b}_N"] = rmse(e[sel])
        m[f"error_medio_fase_{a}_{b}_N"] = float(np.mean(e[sel])) if sel.any() else float("nan")
    return m, e, v_mm_s, z_mm


def figura_serie(serie, items, prefijo, titulo):
    fig, ax = plt.subplots(4, 1, figsize=(11, 12), sharex=True)
    cmap = plt.get_cmap("viridis")
    n = len(items)
    for i, (p, d, e, v, z) in enumerate(items):
        c = cmap(i / max(1, n - 1) * 0.9)
        ax[0].plot(d["t_s"], d["Fz_N"], color=c, lw=1.2, label=f"p{p} Fz")
        ax[0].plot(d["t_s"], d["objetivo_N"], "--", color=c, lw=0.9, alpha=0.7)
        ax[1].plot(d["t_s"], e, color=c, lw=1.0, label=f"p{p}")
        ax[2].plot(d["t_s"], v, color=c, lw=0.9, label=f"p{p}")
        ax[3].plot(d["t_s"], z, color=c, lw=1.2, label=f"p{p}")
    ax[0].set_ylabel("Fz [N]\n(— medida, -- objetivo)")
    ax[1].set_ylabel("error objetivo − Fz [N]")
    ax[2].set_ylabel("vel. ORDENADA de Y [mm/s]\n(+ = subir)")
    ax[3].set_ylabel("desplaz. ORDENADO de Y [mm]\n(contador, NO medido; + = subir)")
    ax[3].set_xlabel("t desde inicio de la pisada [s]")
    for a in ax:
        a.grid(alpha=0.3)
        a.axhline(0, color="k", lw=0.5)
        a.legend(fontsize=7, ncol=min(n, 6))
    fig.suptitle(f"{titulo} — serie {serie}")
    fig.tight_layout()
    out = f"{prefijo}_{serie}_pisadas.png"
    fig.savefig(out, dpi=110)
    plt.close(fig)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--salida", required=True, help="prefijo de salida (ruta sin extensión)")
    ap.add_argument("--titulo", default="Pisadas desde la interfaz (Y lazo cerrado de Fz)")
    ap.add_argument("entradas", nargs="+", help="CSV, patrones o carpetas")
    a = ap.parse_args()
    series = recolectar(a.entradas)
    if not series:
        sys.exit("No se encontraron CSV de pisadas.")
    os.makedirs(os.path.dirname(os.path.abspath(a.salida)), exist_ok=True)
    resumen = {}
    for serie, lista in series.items():
        items, filas = [], []
        for p, tray, f in lista:
            d = leer(f)
            m, e, v, z = metricas(d)
            items.append((p, d, e, v, z))
            filas.append({"serie": serie, "trayectoria": tray, "pisada": p, **m})
        print(figura_serie(serie, items, a.salida, a.titulo))
        out_csv = f"{a.salida}_{serie}_metricas.csv"
        with open(out_csv, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(filas[0].keys()))
            w.writeheader()
            for fl in filas:
                w.writerow({k: (f"{x:.4f}" if isinstance(x, float) else x) for k, x in fl.items()})
        print(out_csv)
        print(f"\nSerie {serie} ({filas[0]['trayectoria']})")
        print(" p  RMSE[N] %pico    r    |e|max[N]  Fmax/objmax[N]  zmax[mm] vmax[mm/s] | RMSE por fase [N] " +
              " ".join(f"{x}-{y}" for x, y in FASES))
        for fl in filas:
            print(f"{fl['pisada']:2d}  {fl['RMSE_N']:6.1f} {fl['RMSE_pct_pico']:5.1f}  {fl['r_pearson']:.3f}  "
                  f"{fl['error_max_abs_N']:7.1f}    {fl['F_max_N']:6.1f}/{fl['objetivo_max_N']:6.1f}  "
                  f"{fl['desplaz_ordenado_max_abs_mm']:7.1f}  {fl['vel_ordenada_max_abs_mm_s']:7.1f}   | " +
                  " ".join(f"{fl[f'RMSE_fase_{x}_{y}_N']:5.1f}" for x, y in FASES))
        resumen[serie] = filas

    fig, ax = plt.subplots(1, 3, figsize=(15, 4.5))
    ancho = 0.8 / len(resumen)
    for j, (serie, filas) in enumerate(resumen.items()):
        ps = [fl["pisada"] for fl in filas]
        ax[0].plot(ps, [fl["RMSE_N"] for fl in filas], "o-", label=serie)
        ax[1].plot(ps, [fl["r_pearson"] for fl in filas], "o-", label=serie)
        ult = filas[-1]
        x = np.arange(len(FASES)) + (j - (len(resumen) - 1) / 2) * ancho
        ax[2].bar(x, [ult[f"RMSE_fase_{a_}_{b_}_N"] for a_, b_ in FASES], ancho, label=f"{serie} p{ult['pisada']}")
    ax[0].set_xlabel("pisada"); ax[0].set_ylabel("RMSE objetivo−Fz [N]")
    ax[1].set_xlabel("pisada"); ax[1].set_ylabel("r de Pearson (objetivo, Fz)")
    ax[2].set_xticks(range(len(FASES))); ax[2].set_xticklabels([f"{x}–{y}" for x, y in FASES])
    ax[2].set_xlabel("fase del apoyo [% del tiempo de la pisada]"); ax[2].set_ylabel("RMSE en la fase [N] (última pisada)")
    for x_ in ax:
        x_.grid(alpha=0.3); x_.legend(fontsize=8)
    fig.suptitle(a.titulo + " — resumen")
    fig.tight_layout()
    out = f"{a.salida}_resumen.png"
    fig.savefig(out, dpi=110)
    plt.close(fig)
    print("\n" + out)


if __name__ == "__main__":
    main()
