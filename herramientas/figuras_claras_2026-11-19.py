#!/usr/bin/env python3
"""Regenera las figuras del 2026-11-19 con titulos, ejes y leyendas en espanol claro (sufijo _claro.png).
Solo lee CSV ya guardados en reportes/datos/ (sin hardware). Las originales NO se tocan.
Reusa leer/metricas/FASES de herramientas/analizar_pisadas_interfaz.py. Uso: python herramientas/figuras_claras_2026-11-19.py"""
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(RAIZ, "herramientas"))
sys.path.insert(0, os.path.join(RAIZ, "control", "telemetria"))
from analizar_pisadas_interfaz import leer, metricas, FASES, recolectar  # noqa: E402
import espectro_corrida as esp  # noqa: E402

D = os.path.join(RAIZ, "reportes", "datos")
F = os.path.join(RAIZ, "reportes", "figuras")
P = "2026-11-19_"
C3 = "Y en lazo cerrado de Fz; X y ángulo del pie en lazo abierto (trayectoria), pie plano"

# serie (fecha_hora del archivo) -> (carpeta, nombre claro)
SERIES = {
    "20261119_111244": ("2026-11-19_pisadas_3ejes_interfaz_40kg", "40 kg, talla 170"),
    "20261119_112242": ("2026-11-19_pisadas_3ejes_interfaz_60kg", "60 kg, talla 170"),
    "20261119_112547": ("2026-11-19_pisadas_3ejes_interfaz_75kg", "75 kg, talla 170"),
    "20261119_113006": ("2026-11-19_pisadas_3ejes_interfaz_80kg", "80 kg, talla 170"),
    "20261119_113607": ("2026-11-19_pisadas_3ejes_interfaz_80kg_talla174", "80 kg, talla 174"),
    "20261119_114714": ("2026-11-19_mejora_ff_ilc_80kg/A_base", "80 kg, sin mejora (ILC base)"),
    "20261119_114846": ("2026-11-19_mejora_ff_ilc_80kg/B_ff07_m30", "80 kg, con anticipación + adelanto del ILC"),
}


def cargar(serie):
    carpeta, _ = SERIES[serie]
    ser = recolectar([os.path.join(D, carpeta)])[serie]
    items = []
    for p, _, f in ser:
        d = leer(f)
        m, e, v, z = metricas(d)
        items.append((p, d, e, v, z, m))
    return items


NOTA = ("RMSE = error cuadrático medio entre fuerza objetivo y medida, calculado sobre TODA la curva de fuerza de la pisada (no solo los picos). "
        "r = correlación de forma (1 = idéntica). ILC = aprendizaje pisada a pisada. Kp = ganancia del lazo. Pisada = un apoyo del pie.")


def pie(fig, texto=NOTA):
    fig.text(0.5, 0.006, texto, ha="center", va="bottom", fontsize=9, wrap=True)


def fig_pisadas(serie, titulo, out, delta=False, mixto=False):
    from matplotlib.lines import Line2D
    items = cargar(serie)
    n = len(items)
    cmap = plt.get_cmap("viridis")
    fig, ax = plt.subplots(4, 1, figsize=(12, 14), sharex=True)
    for i, (p, d, e, v, z, m) in enumerate(items):
        c = cmap(i / max(1, n - 1) * 0.9)
        ax[0].plot(d["t_s"], d["Fz_N"], color=c, lw=1.8)
        ax[0].plot(d["t_s"], d["objetivo_N"], "--", color=c, lw=1.0, alpha=0.8)
        ax[1].plot(d["t_s"], e, color=c, lw=1.1)
        if delta:
            ax[2].plot(d["t_s"], d["delta_ilc_N"], color=c, lw=1.4)
            ax[3].plot(d["t_s"][1:], np.diff(d["t_s"]) * 1000, color=c, lw=0.9)
        else:
            ax[2].plot(d["t_s"], v, color=c, lw=1.0)
            ax[3].plot(d["t_s"], z, color=c, lw=1.5)
    ax[0].set_ylabel("Fuerza vertical (N)\ncontinua = medida, rayada = objetivo", fontsize=11)
    ax[1].set_ylabel("Error = objetivo − medida (N)\n(>0: falta fuerza)", fontsize=11)
    if delta:
        ax[2].set_ylabel("Corrección que el ILC suma\nal objetivo (N)", fontsize=11)
        ax[3].set_ylabel("Tiempo entre muestras\ndel lazo (ms)", fontsize=11)
    else:
        ax[2].set_ylabel("Velocidad ordenada\nal eje vertical (mm/s)\n(+ = subir)", fontsize=11)
        ax[3].set_ylabel("Desplazamiento ordenado\ndel eje vertical (mm)\n(+ = subir; contado, no medido)", fontsize=11)
    ax[3].set_xlabel("Tiempo desde el inicio de cada pisada (s)", fontsize=11)
    for a in ax:
        a.grid(alpha=0.3)
        a.axhline(0, color="k", lw=0.5)
        a.tick_params(labelsize=10)
    h = [Line2D([0], [0], color=cmap(i / max(1, n - 1) * 0.9), lw=2.5) for i in range(n)]
    h += [Line2D([0], [0], color="k", lw=1.8), Line2D([0], [0], color="k", lw=1.0, ls="--")]
    et = [f"Pisada {it[0]}" for it in items] + ["Fuerza medida (línea continua)", "Fuerza objetivo (línea rayada)"]
    fig.legend(h, et, loc="upper center", bbox_to_anchor=(0.5, 0.925), ncol=min(n + 2, 4), fontsize=10, frameon=True)
    r1, rn = items[0][5]["RMSE_N"], items[-1][5]["RMSE_N"]
    escala = "escala de tiempo x10"
    sub = ("Solo el eje vertical en lazo cerrado de Fz (X y ángulo quietos), pie plano" if mixto else
           "Eje vertical en lazo cerrado de Fz; X y ángulo del pie en lazo abierto (trayectoria), pie plano")
    fig.suptitle(f"{titulo}: {SERIES[serie][1]}, {escala}, pisadas 1 a {n}\n{sub}\n"
                 f"Lectura clave: el error (RMSE) baja de {r1:.0f} N en la pisada 1 a {rn:.0f} N en la pisada {n}", fontsize=12)
    pie(fig)
    fig.tight_layout(rect=(0, 0.03, 1, 0.885))
    fig.savefig(out, dpi=110, facecolor="white")
    plt.close(fig)
    print(out)


def fig_resumen(series, titulo, out):
    fig, ax = plt.subplots(1, 3, figsize=(18, 6.6))
    ancho = 0.8 / len(series)
    ult = []
    for j, s in enumerate(series):
        items = cargar(s)
        nom = SERIES[s][1]
        ps = [it[0] for it in items]
        ms = [it[5] for it in items]
        ult.append((ms[0]["RMSE_N"], ms[-1]["RMSE_N"], ms[-1]["r_pearson"]))
        ax[0].plot(ps, [m["RMSE_N"] for m in ms], "o-", lw=2, label=nom)
        ax[1].plot(ps, [m["r_pearson"] for m in ms], "o-", lw=2, label=nom)
        x = np.arange(len(FASES)) + (j - (len(series) - 1) / 2) * ancho
        ax[2].bar(x, [ms[-1][f"RMSE_fase_{a}_{b}_N"] for a, b in FASES], ancho, label=f"{nom} (pisada {ps[-1]})")
    ax[0].set_ylabel("RMSE objetivo − medida (N)\n(menor = mejor)", fontsize=11)
    ax[0].set_title("Error de fuerza por pisada", fontsize=12)
    ax[1].set_ylabel("Parecido de forma objetivo–medida\n(correlación r; 1 = idéntica)", fontsize=11)
    ax[1].set_title("Parecido de forma por pisada", fontsize=12)
    for a in ax[:2]:
        a.set_xlabel("Número de pisada", fontsize=11)
        a.xaxis.set_major_locator(plt.MaxNLocator(integer=True))
    ax[2].set_xticks(range(len(FASES)))
    ax[2].set_xticklabels([f"{a}–{b}" for a, b in FASES])
    ax[2].set_xlabel("Fase del apoyo (% de la duración de la pisada)", fontsize=11)
    ax[2].set_ylabel("RMSE dentro de la fase (N)", fontsize=11)
    ax[2].set_title("Dónde falla: error por fase, última pisada", fontsize=12)
    for a in ax:
        a.grid(alpha=0.3)
        a.legend(fontsize=10)
        a.tick_params(labelsize=10)
    lo, hi = min(u[1] for u in ult), max(u[1] for u in ult)
    if len(series) == 1:
        clave = f"el error (RMSE) baja de {ult[0][0]:.0f} N en la pisada 1 a {ult[0][1]:.0f} N en la última (r final {ult[0][2]:.3f})"
    else:
        clave = f"en la última pisada de cada serie el error (RMSE) queda entre {lo:.0f} y {hi:.0f} N, y el mayor error está en 0–10 % y 90–100 % del apoyo"
    fig.suptitle(f"{titulo}\nLectura clave: {clave}", fontsize=13)
    pie(fig)
    fig.tight_layout(rect=(0, 0.04, 1, 0.9))
    fig.savefig(out, dpi=110, facecolor="white")
    plt.close(fig)
    print(out)


def fig_espectro(out):
    corridas = [("2026-11-19_103942_fz.csv", "Kp 5 (ganancia alta), primera corrida"),
                ("2026-11-19_104134_fz.csv", "Kp 3 (ganancia baja)"),
                ("2026-11-19_104323_fz.csv", "Kp 5 (ganancia alta), repetición")]
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(15, 6.4)); media = {}
    for ruta, nom in corridas:
        filas = esp.analizar(os.path.join(D, "2026-11-19_kp3_vs_kp5_70kg", ruta), (3, 15), (5, 10))
        sel = [x for x in filas if x["c"] + 1 >= 6]
        n = min(len(x["f"]) for x in sel)
        amp = np.mean([x["amp"][:n] for x in sel], axis=0)
        fp = float(np.median([x["f_pico"] for x in sel]))
        ax.plot(sel[0]["f"][:n], amp, lw=1.5, label=f"{nom} (pico en {fp:.1f} Hz)")
        ax2.plot([x["c"] + 1 for x in filas], [x["rms_e"] for x in filas], "o-", ms=5, lw=2, label=nom)
        media[nom] = float(np.mean([x["rms_e"] for x in filas]))
    ax.axvspan(5, 10, color="0.9", zorder=0, label="Banda 5–10 Hz (oscilación sospechosa)")
    ax.set_xlim(0, 20); ax.set_ylim(0, 10)
    ax.set_xlabel("Frecuencia (Hz)", fontsize=11)
    ax.set_ylabel("Amplitud del error de fuerza (N)", fontsize=11)
    ax.set_title("Qué frecuencias tiene el error (pisadas 6 a 10)", fontsize=12)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=9, loc="upper right")
    ax2.set_xlabel("Número de pisada", fontsize=11)
    ax2.set_ylabel("Tamaño de la oscilación 5–10 Hz del error (N rms)", fontsize=11)
    ax2.set_title("Oscilación 5–10 Hz en cada pisada", fontsize=12)
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=10, loc="upper right")
    ax2.xaxis.set_major_locator(plt.MaxNLocator(integer=True))
    ks = [v for k, v in media.items() if "baja" in k]; ka = [v for k, v in media.items() if "alta" in k]
    fig.suptitle("Carga 70 kg, escala de tiempo x10, 10 pisadas: ¿la ganancia Kp cambia la oscilación de 5–10 Hz?\n"
                 f"Lectura clave: con Kp 3 la oscilación media es {np.mean(ks):.1f} N rms; con Kp 5, {np.mean(ka):.1f} N rms", fontsize=12)
    pie(fig, "Kp = ganancia del lazo (más alta = reacciona más fuerte al error). Oscilación 5–10 Hz = vaivén rápido de la fuerza alrededor del objetivo. rms = valor eficaz. En el panel izquierdo se recorta el pico de 0 Hz (deriva lenta).")
    fig.tight_layout(rect=(0, 0.03, 1, 0.9))
    fig.savefig(out, dpi=110, facecolor="white")
    plt.close(fig)
    print(out)


def fig_delta(out):
    sys.path.insert(0, os.path.join(RAIZ, "control", "ilc"))
    from fz_ilc import ControlFzILC
    d18 = os.path.join(D, "2026-11-18_pisadas_3ejes_interfaz")

    def rd(f):
        return np.genfromtxt(f, delimiter=",", names=True)
    a = rd(os.path.join(d18, "20261118_175820_Control_apoyo_talla170_montaje37_p1.csv"))
    b = rd(os.path.join(d18, "20261118_175820_Control_apoyo_talla170_montaje37_p2.csv"))
    s = rd(os.path.join(D, "2026-11-19_kp3_vs_kp5_70kg", "2026-11-19_103942_fz.csv"))

    def rms(x):
        return float(np.sqrt(np.mean(np.square(x))))
    dur = 6.0
    n = len(a["t_s"])

    def ilc_con(t_axis):
        c = ControlFzILC(75 * 9.81, duracion_s=dur, rigidez_n_por_mm=26.4)
        tm = np.linspace(0, dur, c.n, endpoint=False)
        e = c.ref_n - np.interp(tm, t_axis, a["Fz_N"])
        c.ilc.actualizar(e)
        return c, tm, e
    cr, tm, er = ilc_con(a["t_s"])
    cn, _, en = ilc_con(np.arange(n) * 0.010)
    fig, ax = plt.subplots(2, 2, figsize=(16, 10.5))
    ax[0, 0].plot(a["t_s"], a["objetivo_N"], label="Objetivo de fuerza")
    ax[0, 0].plot(a["t_s"], a["Fz_N"], label="Fuerza vertical medida")
    ax[0, 0].axvline(6.0, color="k", ls="--", label="6,0 s: duración que supone el ILC")
    ax[0, 0].set_title("Interfaz, pisada 1 (18-nov, 75 kg): el lazo dura 8,27 s, no 6,0 s", fontsize=10)
    ax[0, 0].set_xlabel("Tiempo real (s)")
    ax[0, 0].set_ylabel("Fuerza vertical (N)")
    ax[0, 0].set_ylim(top=1200)
    ax[0, 0].legend(fontsize=10, loc="upper center")
    ax[0, 1].plot(tm, er, label=f"Error visto por el ILC con el tiempo real (rms {rms(er):.0f} N)")
    ax[0, 1].plot(tm, en, label=f"Error si se asume 10 ms por muestra (rms {rms(en):.0f} N)")
    ax[0, 1].set_title("Error de fuerza que recibe el ILC para aprender", fontsize=10)
    ax[0, 1].set_xlabel("Tiempo (s)")
    ax[0, 1].set_ylabel("Error objetivo − medida (N)")
    ax[0, 1].legend(fontsize=10)
    ax[1, 0].plot(tm, cr.ilc.delta, label="Corrección calculada con el tiempo real (lo que hace la interfaz)")
    ax[1, 0].plot(tm, cn.ilc.delta, label="Corrección calculada asumiendo 10 ms por muestra")
    ax[1, 0].plot(b["t_s"], b["delta_ilc_N"], "k.", ms=3, label="Corrección realmente guardada en la pisada 2 (0–0,5 s)")
    ax[1, 0].set_title("Corrección del ILC para la pisada 2", fontsize=10)
    ax[1, 0].set_xlabel("Tiempo (s)")
    ax[1, 0].set_ylabel("Corrección del ILC (N)")
    ax[1, 0].legend(fontsize=10)
    for c, nom in ((0, "pisada 1 (sin corrección aún)"), (1, "pisada 2"), (9, "pisada 10")):
        m = s["ciclo"] == c
        ax[1, 1].plot(s["t"][m], s["delta"][m], label=nom)
    ax[1, 1].set_title("Prueba del 19-nov (lazo por script), 70 kg, Kp 5: la corrección también arranca grande", fontsize=10)
    ax[1, 1].set_xlabel("Tiempo nominal (s)")
    ax[1, 1].set_ylabel("Corrección del ILC (N)")
    ax[1, 1].legend(fontsize=10)
    for a_ in ax.ravel():
        a_.grid(alpha=0.3)
    fig.suptitle("Por qué el ILC de la interfaz arranca con una corrección grande y no aprende bien\n"
                 f"Lectura clave: el apoyo real dura 8,27 s y el ILC supone 6,0 s; por eso ve un error de {rms(er):.0f} N rms en vez de {rms(en):.0f} N", fontsize=12)
    pie(fig, "ILC = aprendizaje pisada a pisada (corrige la referencia con el error de la pisada anterior). Kp = ganancia del lazo. rms = valor eficaz. 75 kg y 70 kg: cargas de cada prueba.")
    fig.tight_layout(rect=(0, 0.03, 1, 0.92))
    fig.savefig(out, dpi=110, facecolor="white")
    plt.close(fig)
    print(out)
    print("rms t real", rms(er), "rms t nominal", rms(en), "(original: 220 y 89)")


def main():
    T = "Seguimiento de la fuerza vertical objetivo"
    fig_pisadas("20261119_111244", T, f"{F}/{P}pisadas_3ejes_40kg_claro.png", delta=True)
    for kg, s in (("40kg", "20261119_111244"), ("60kg", "20261119_112242"), ("75kg", "20261119_112547"),
                  ("80kg", "20261119_113006"), ("80kg_talla174", "20261119_113607")):
        fig_pisadas(s, T, f"{F}/{P}analisis_{kg}_{s}_pisadas_claro.png")
        fig_pisadas(s, T, f"{F}/{P}analisis_todas_{s}_pisadas_claro.png")
        fig_resumen([s], f"Resumen — {SERIES[s][1]}: Y en lazo cerrado de Fz, X y ángulo en lazo abierto",
                    f"{F}/{P}analisis_{kg}_resumen_claro.png")
    fig_resumen(["20261119_111244", "20261119_112242", "20261119_112547", "20261119_113006", "20261119_113607"],
                "Comparación por carga y talla (pruebas de 3 ejes del 19-nov): Y en lazo cerrado de Fz, X y ángulo en lazo abierto",
                f"{F}/{P}analisis_todas_resumen_claro.png")
    for s in ("20261119_114714", "20261119_114846"):
        fig_pisadas(s, T, f"{F}/{P}mejora_ff_ilc_80kg_{s}_pisadas_claro.png", mixto=True)
    fig_resumen(["20261119_114714", "20261119_114846"],
                "80 kg, escala x10, solo eje vertical, pie plano: sin mejora vs con anticipación + adelanto del ILC",
                f"{F}/{P}mejora_ff_ilc_80kg_resumen_claro.png")
    fig_espectro(f"{F}/{P}espectro_kp5_kp3_kp5_70kg_claro.png")
    fig_delta(f"{F}/{P}analisis_delta_ilc_interfaz_claro.png")


if __name__ == "__main__":
    main()
