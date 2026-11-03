"""Compara la Fz del AMTI (exportado de .bsf a .txt con bsf_to_txt.py) contra
la Fz leida por el RPi via ADS1256 (lecturas_fz_20261102_175759.csv).

Las dos capturas se iniciaron a mano en momentos distintos, sin disparo comun;
por eso se alinean por correlacion cruzada (solo para poder comparar, el
desfase no es una metrica). Con la alineacion se calculan RMSE (N) en la
region de solape y error pico a pico (%) sobre toda la grabacion.

Uso:
    pip install matplotlib numpy
    python comparar_amti_vs_ads1256.py
"""
import numpy as np
import matplotlib.pyplot as plt

AZUL = "#2563eb"
NARANJA = "#e65100"
GRIS = "#6b7280"

plt.rcParams.update({"font.size": 11, "axes.edgecolor": "#d1d5db", "axes.grid": True,
                      "grid.color": "#e5e7eb", "grid.linewidth": 0.8})


def leer_amti_txt(path):
    with open(path) as f:
        lineas = [l for l in f if not l.startswith("#")]
    cols = lineas[0].strip().split("\t")
    i_t, i_fz = cols.index("Tiempo_s"), cols.index("Fz_N")
    t, fz = [], []
    for l in lineas[1:]:
        p = l.strip().split("\t")
        t.append(float(p[i_t]))
        fz.append(float(p[i_fz]))
    return t, fz


def leer_rpi_csv(path):
    import csv
    t, fz = [], []
    with open(path) as f:
        for row in csv.DictReader(f):
            t.append(float(row["t_s"]))
            fz.append(float(row["newtons_tarados"]))
    t0 = t[0]
    return [x - t0 for x in t], fz


def mejor_desfase(t_a, fz_a, t_r, fz_r):
    t_common = np.arange(0, min(t_a[-1], t_r[-1]), 0.001)
    a = np.interp(t_common, t_a, fz_a)
    r = np.interp(t_common, t_r, fz_r)
    corr = np.correlate(a - a.mean(), r - r.mean(), mode="full")
    lag = corr.argmax() - (len(r) - 1)
    r_shift = np.roll(r, lag)
    r_shift[:lag] = np.nan if lag > 0 else r_shift[:lag]
    valid = ~np.isnan(r_shift) if lag > 0 else slice(None)
    pearson = np.corrcoef(a[valid], r_shift[valid])[0, 1]
    return lag / 1000.0, pearson


def metricas(t_amti, fz_amti, t_rpi_alineado, fz_rpi):
    """RMSE (N) en la region de solape (RPi interpolado a los instantes del AMTI)
    y error pico a pico (%) sobre la grabacion completa."""
    t_a = np.asarray(t_amti); f_a = np.asarray(fz_amti)
    t_r = np.asarray(t_rpi_alineado); f_r = np.asarray(fz_rpi)
    solape = (t_a >= t_r[0]) & (t_a <= t_r[-1])
    f_r_i = np.interp(t_a[solape], t_r, f_r)
    rmse = float(np.sqrt(np.mean((f_a[solape] - f_r_i) ** 2)))
    pp_a = f_a.max() - f_a.min()
    pp_r = f_r.max() - f_r.min()
    err_pp = abs(pp_a - pp_r) / pp_a * 100
    return rmse, err_pp, pp_a, pp_r


if __name__ == "__main__":
    t_amti, fz_amti = leer_amti_txt("Trial00535.txt")
    t_rpi, fz_rpi = leer_rpi_csv("lecturas_fz_20261102_175759.csv")

    desfase_s, pearson = mejor_desfase(t_amti, fz_amti, t_rpi, fz_rpi)
    t_rpi_alineado = [t + desfase_s for t in t_rpi]

    rmse, err_pp, pp_a, pp_r = metricas(t_amti, fz_amti, t_rpi_alineado, fz_rpi)

    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(t_amti, fz_amti, color=AZUL, linewidth=1.4, label="AMTI directo (Trial00535.bsf)")
    ax.plot(t_rpi_alineado, fz_rpi, color=NARANJA, linewidth=1.2, linestyle="--",
            label="RPi via ADS1256 (tarado)", alpha=0.85)
    ax.set_xlabel("Tiempo (s)")
    ax.set_ylabel("Fz (N)")
    ax.set_title(f"Fz: AMTI vs. RPi+ADS1256 (alineadas por correlacion, r={pearson:.4f})")
    ax.legend(frameon=False, loc="upper right")
    ax.text(0.01, 0.97,
            f"RMSE (region de solape) = {rmse:.2f} N\n"
            f"Error pico a pico = {err_pp:.2f} %\n"
            f"(AMTI {pp_a:.1f} N, RPi {pp_r:.1f} N)",
            transform=ax.transAxes, va="top", ha="left", fontsize=10,
            bbox=dict(boxstyle="round,pad=0.4", fc="white", ec="#d1d5db"))
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig("comparacion_amti_vs_ads1256.png", dpi=150)
    print(f"Pearson tras alinear: {pearson:.4f}")
    print(f"RMSE: {rmse:.4f} N, error pico a pico: {err_pp:.4f} % (AMTI {pp_a:.3f} N, RPi {pp_r:.3f} N)")
    print("Grafico guardado en: comparacion_amti_vs_ads1256.png")
