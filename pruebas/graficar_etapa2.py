"""Graficas de resultados de la ETAPA 2 (R2 y R3). Escrito 2026-11-18; probado SOLO con datos sinteticos.
  r2  <lecturas.csv> [--contra <otro.csv>] [--etiqueta_contra "L3 laptop"]
        CSV de pruebas/leer_ads1256_fz_esp32_uart.py (intento,t_s,fz_n). Fz(t), histograma, espectro y tiempo entre
        muestras. --contra superpone otra corrida del MISMO formato (p. ej. L3 en la laptop) para el criterio
        "σ en el RPi ≈ σ en la laptop".
  r3  <vigilar.csv>
        CSV de pruebas/vigilar_adc_esp32_uart.py. Linea de tiempo de estados, Fz mediana, σ y muestras/s por segundo.
Salida: PNG (por defecto en pruebas/resultados/etapa2/figuras/). --mostrar lo abre en la pantalla del RPi
(herramientas/mostrar_figura.py, en segundo plano).
Limites que la figura NO resuelve: el tiempo `t_s` es de LLEGADA al RPi (los paquetes del UART llegan en rafagas, no es el
instante de conversion del ADC); el espectro asume el muestreo nominal de 1000 /s; el offset (media) NO es comparable entre
corridas con carga distinta en el plato."""
import argparse, csv, os, subprocess, sys, time
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
FS_NOMINAL = 1000.0
COLOR = {"OK": "#2e7d32", "PICOS": "#f9a825", "CAIDO": "#c62828", "CEROS": "#6a1b9a", "SATURADO": "#e65100",
         "CONGELADO": "#455a64", "RECUPERADO": "#0277bd"}


def leer_r2(ruta):
    t, f = [], []
    for fila in csv.DictReader(open(ruta)):
        try:
            t.append(float(fila["t_s"])); f.append(float(fila["fz_n"]))
        except (KeyError, ValueError):
            pass
    if len(f) < 20:
        raise SystemExit(f"{ruta}: solo {len(f)} lecturas validas, no alcanza para graficar")
    return np.array(t), np.array(f)


def resumen(t, f, umbral=50.0):
    med = float(np.median(f))
    dur = t[-1] - t[0]
    return {"n": len(f), "media": float(f.mean()), "mediana": med, "sd": float(f.std()), "pp": float(f.max() - f.min()),
            "sd_rob": float(1.4826 * np.median(np.abs(f - med))),   # σ robusta (MAD): no la inflan los pocos picos de error de bit
            "tasa": (len(f) - 1) / dur if dur > 0 else float("nan"), "picos": int(np.sum(np.abs(f - med) > umbral)),
            "ceros": int(np.sum(f == 0.0))}


def psd(f, fs, umbral=50.0):
    f = np.where(np.abs(f - np.median(f)) > umbral, np.median(f), f)   # picos de error de bit fuera: aplanarian el espectro
    x = f - f.mean()
    n = len(x) // 2 * 2
    seg = 512 if n >= 1024 else n
    ps, k = 0, 0
    w = np.hanning(seg)
    for i in range(0, n - seg + 1, seg // 2):
        ps = ps + np.abs(np.fft.rfft(x[i:i + seg] * w)) ** 2; k += 1
    return np.fft.rfftfreq(seg, 1 / fs), np.sqrt(ps / k / (fs * np.sum(w ** 2) / 2 + 1e-30)) if k else None


def r2(a):
    t, f = leer_r2(a.csv)
    s = resumen(t, f)
    o = None
    if a.contra:
        to, fo = leer_r2(a.contra); o = (to, fo, resumen(to, fo))
    fig, ax = plt.subplots(2, 2, figsize=(14, 8.5), facecolor="white")
    ax[0, 0].plot(t, f, lw=.6, color="k", label="RPi (esta corrida)")
    if o: ax[0, 0].plot(o[0], o[1], lw=.6, color="tab:orange", alpha=.7, label=a.etiqueta_contra)
    ax[0, 0].set(title="Fz en el tiempo (tiempo = llegada al RPi)", xlabel="t [s]", ylabel="Fz [N]"); ax[0, 0].legend()
    lo, hi = np.percentile(f, [0.5, 99.5]); pad = max(1.0, 0.2 * (hi - lo))
    bins = np.linspace(lo - pad, hi + pad, 60)
    ax[0, 1].hist(f, bins=bins, color="k", alpha=.6, density=True, label=f"RPi σ={s['sd']:.2f} N (robusta {s['sd_rob']:.2f})")
    if o: ax[0, 1].hist(o[1], bins=bins, color="tab:orange", alpha=.5, density=True, label=f"{a.etiqueta_contra} σ={o[2]['sd']:.2f} N (robusta {o[2]['sd_rob']:.2f})")
    ax[0, 1].set(title="Histograma (vista 0.5-99.5 %; los picos cuentan en σ, no en σ robusta)",
                 xlabel="Fz [N]", ylabel="densidad"); ax[0, 1].legend()
    fr, am = psd(f, s['tasa'])
    ax[1, 0].loglog(fr[1:], am[1:], color="k", label="RPi")
    if o:
        fr2, am2 = psd(o[1], o[2]['tasa']); ax[1, 0].loglog(fr2[1:], am2[1:], color="tab:orange", alpha=.7, label=a.etiqueta_contra)
    ax[1, 0].set(title="Espectro (picos >50 N reemplazados; fs = tasa medida de cada serie)", xlabel="f [Hz]", ylabel="N/√Hz"); ax[1, 0].legend(); ax[1, 0].grid(alpha=.3, which="both")
    dt = np.diff(t) * 1000
    ax[1, 1].plot(dt, lw=.5, color="k"); ax[1, 1].axhline(1.0, color="tab:red", ls="--", lw=1, label="1 ms nominal")
    ax[1, 1].set(title="Tiempo entre paquetes [ms] (llegada al RPi, no el ADC)", xlabel="muestra", ylabel="ms")
    ax[1, 1].set_ylim(0, max(5, np.percentile(dt, 99.5))); ax[1, 1].legend()
    txt = (f"n={s['n']}  tasa={s['tasa']:.0f}/s (esperado ~1000)  media={s['media']:+.2f} N  σ={s['sd']:.2f} N (robusta {s['sd_rob']:.2f})  "
           f"p-p={s['pp']:.1f} N  |picos|>50 N: {s['picos']}  ceros exactos: {s['ceros']}")
    if o: txt += f"\n{a.etiqueta_contra}: n={o[2]['n']}  tasa={o[2]['tasa']:.0f}/s  media={o[2]['media']:+.2f} N  σ={o[2]['sd']:.2f} N (robusta {o[2]['sd_rob']:.2f})  picos: {o[2]['picos']}"
    fig.suptitle("ETAPA 2 · R2 — Fz por UART (ESP32 de lectura)\n" + txt, fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, .92))
    return fig, os.path.splitext(os.path.basename(a.csv))[0]


def r3(a):
    filas = [f for f in csv.DictReader(open(a.csv))]
    if not filas:
        raise SystemExit(f"{a.csv}: sin filas")
    est = [f["estado"] for f in filas]
    x = np.arange(len(filas))
    def col(k):
        out = []
        for f in filas:
            try: out.append(float(f[k]))
            except (ValueError, KeyError): out.append(np.nan)
        return np.array(out)
    med, sd, ms = col("fz_mediana_n"), col("fz_sd_n"), col("muestras_s")
    fig, ax = plt.subplots(3, 1, figsize=(14, 8.5), facecolor="white", sharex=True, gridspec_kw={"height_ratios": [3, 1.5, 1.5]})
    ax[0].plot(x, med, color="k", lw=.8)
    for e in set(est):
        i = [k for k, v in enumerate(est) if v == e]
        ax[0].scatter(x[i], med[i], s=18 if e == "OK" else 45, color=COLOR.get(e, "gray"), label=f"{e} ({len(i)})", zorder=3)
    ax[0].set(ylabel="Fz mediana [N]", title="Fz en reposo, un punto por segundo (el color es el estado del vigilante)"); ax[0].legend(ncol=4); ax[0].grid(alpha=.3)
    ax[1].plot(x, sd, color="tab:blue", lw=.8); ax[1].set(ylabel="σ en 1 s [N]"); ax[1].grid(alpha=.3)
    ax[2].plot(x, ms, color="tab:green", lw=.8); ax[2].axhline(1000, color="tab:red", ls="--", lw=1)
    ax[2].set(ylabel="muestras/s", xlabel="segundo de la corrida"); ax[2].grid(alpha=.3)
    n_mal = sum(1 for e in est if e not in ("OK", "RECUPERADO"))
    fig.suptitle(f"ETAPA 2 · R3 — vigilante del ADC: {len(est)} s registrados, {n_mal} no-OK  "
                 + ("→ 0 fallas (criterio de paso)" if n_mal == 0 else "→ HAY FALLAS: anotar qué se hizo justo antes"), fontsize=13,
                 color="#2e7d32" if n_mal == 0 else "#c62828")
    fig.tight_layout(rect=(0, 0, 1, .95))
    return fig, os.path.splitext(os.path.basename(a.csv))[0]


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="modo", required=True)
    for m in ("r2", "r3"):
        p = sp.add_parser(m); p.add_argument("csv"); p.add_argument("--salida"); p.add_argument("--mostrar", action="store_true")
    sp.choices["r2"].add_argument("--contra"); sp.choices["r2"].add_argument("--etiqueta_contra", default="L3 laptop")
    a = ap.parse_args()
    fig, nombre = (r2 if a.modo == "r2" else r3)(a)
    carpeta = os.path.join(R, "pruebas", "resultados", "etapa2", "figuras"); os.makedirs(carpeta, exist_ok=True)
    out = a.salida or os.path.join(carpeta, f"{a.modo}_{nombre}.png")
    fig.savefig(out, dpi=100, facecolor="white"); print("figura:", out)
    if a.mostrar:   # regla 4: toda figura generada en el RPi se ve en su pantalla; segundo plano para no bloquear
        subprocess.Popen([sys.executable, os.path.join(R, "herramientas", "mostrar_figura.py"), out],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)


if __name__ == "__main__":
    main()
