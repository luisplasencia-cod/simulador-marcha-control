"""Espectro del error de Fz por pisada, a partir de los CSV de control/lazo_fz_tiempo_real.py.

Para la prueba Kp 3 vs Kp 5 (reportes/2026-11-19_protocolo_proxima_sesion_rpi.md): si la frecuencia del pico en
3-15 Hz NO cambia con Kp -> resonancia mecanica; si cambia, la crea el lazo. La amplitud sola no decide.

Uso: python control/telemetria/espectro_corrida.py A.csv [B.csv ...] [--desde 6] [--png salida.png]
Tiempo: columna t_real (reloj real) si existe; en CSV viejos `t` es NOMINAL (i*10 ms) y el periodo real era ~13.5 ms: las frecuencias de CSV viejos salen sobreestimadas ~1.35x.
Señales: e = r_corregida - F_med [N] y v_mm_s [mm/s], por pisada, remuestreadas a 100 Hz, sin tendencia, Hann.
Pico en 3-15 Hz (--banda_pico); RMS en 5-10 Hz (--banda_rms). Metrica del protocolo: pisadas 6-10 (--desde 6).
"""
import argparse
import csv
import os
import sys

import numpy as np

FS = 100.0


def leer(ruta):
    t, ciclo, e, v = [], [], [], []
    with open(ruta, newline="") as f:
        for fila in csv.DictReader(f):
            try:
                t.append(float(fila.get("t_real") or fila["t"])); ciclo.append(int(fila["ciclo"]))
                e.append(float(fila["e"])); v.append(float(fila["v_mm_s"]))
            except (KeyError, ValueError, TypeError):
                continue
    return np.array(t), np.array(ciclo), np.array(e), np.array(v)


def espectro(t, x):
    if len(t) < 32 or t[-1] - t[0] < 1.0:
        return None
    tu = np.arange(t[0], t[-1], 1.0 / FS)
    y = np.interp(tu, t, x)
    y = y - np.polyval(np.polyfit(tu, y, 1), tu)
    w = np.hanning(len(y))
    amp = 2.0 * np.abs(np.fft.rfft(y * w)) / w.sum()      # amplitud de pico de una senoide
    return np.fft.rfftfreq(len(y), 1.0 / FS), amp, tu[-1] - tu[0]


def rms_banda(f, amp, banda):
    b = (f >= banda[0]) & (f <= banda[1])
    return float(np.sqrt(np.sum((amp[b] / np.sqrt(2)) ** 2) / 1.5))   # 1.5 = ancho de banda equivalente de Hann (bins)


def analizar(ruta, banda_pico, banda_rms):
    t, ciclo, e, v = leer(ruta)
    filas = []
    for c in np.unique(ciclo):
        m = ciclo == c
        re_, rv = espectro(t[m], e[m]), espectro(t[m], v[m])
        if re_ is None:
            continue
        f, amp, dur = re_
        b = (f >= banda_pico[0]) & (f <= banda_pico[1])
        i = int(np.argmax(amp[b]))
        filas.append(dict(c=int(c), f_pico=float(f[b][i]), amp_pico=float(amp[b][i]), dur=dur, f=f, amp=amp,
                          rms_e=rms_banda(f, amp, banda_rms), rms_v=rms_banda(rv[0], rv[1], banda_rms)))
    return filas


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv", nargs="+")
    ap.add_argument("--banda_pico", nargs=2, type=float, default=[3.0, 15.0])
    ap.add_argument("--banda_rms", nargs=2, type=float, default=[5.0, 10.0])
    ap.add_argument("--desde", type=int, default=6, help="primera pisada (numerada desde 1) que entra en la metrica")
    ap.add_argument("--png", default=None)
    a = ap.parse_args()

    resumen = []
    for ruta in a.csv:
        filas = analizar(ruta, a.banda_pico, a.banda_rms)
        if not filas:
            print(f"{ruta}: sin pisadas analizables"); continue
        print(f"\n{os.path.basename(ruta)}  (pico {a.banda_pico[0]:g}-{a.banda_pico[1]:g} Hz, RMS {a.banda_rms[0]:g}-{a.banda_rms[1]:g} Hz)")
        print(" pisada  f_pico_Hz  amp_pico_N  rms_e_N  rms_v_mm_s")
        for x in filas:
            print(f" {x['c'] + 1:6d}  {x['f_pico']:9.2f}  {x['amp_pico']:10.2f}  {x['rms_e']:7.2f}  {x['rms_v']:10.2f}")
        sel = [x for x in filas if x["c"] + 1 >= a.desde] or filas[-1:]
        resumen.append(dict(ruta=ruta, sel=sel, f_pico=float(np.median([x["f_pico"] for x in sel])),
                            rms_e=float(np.mean([x["rms_e"] for x in sel])), rms_v=float(np.mean([x["rms_v"] for x in sel])),
                            res=1.0 / min(x["dur"] for x in sel)))

    if resumen:
        print(f"\nMetrica (pisadas >= {a.desde}; si la corrida tiene menos, solo la ultima):")
        for r in resumen:
            print(f"  {os.path.basename(r['ruta'])}: f_pico {r['f_pico']:.2f} Hz, RMS e {r['rms_e']:.2f} N, "
                  f"RMS v {r['rms_v']:.2f} mm/s  (n={len(r['sel'])}, resolucion {r['res']:.2f} Hz)")
    if len(resumen) > 1:
        fs_ = [r["f_pico"] for r in resumen]
        res = max(r["res"] for r in resumen)
        print(f"  diferencia de f_pico: {max(fs_) - min(fs_):.2f} Hz "
              f"({'MENOR' if max(fs_) - min(fs_) <= 2 * res else 'MAYOR'} que 2x la resolucion = {2 * res:.2f} Hz)")

    if a.png and resumen:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, (ax, ax2) = plt.subplots(1, 2, figsize=(11, 4.2))
        for r in resumen:
            n = min(len(x["f"]) for x in r["sel"])
            amp = np.mean([x["amp"][:n] for x in r["sel"]], axis=0)
            nombre = os.path.basename(r["ruta"])
            ax.plot(r["sel"][0]["f"][:n], amp, lw=1.5, label=f"{nombre} (pico {r['f_pico']:.1f} Hz)")
            filas = analizar(r["ruta"], a.banda_pico, a.banda_rms)
            ax2.plot([x["c"] + 1 for x in filas], [x["rms_e"] for x in filas], "o-", ms=4, label=nombre)
        ax.axvspan(a.banda_rms[0], a.banda_rms[1], color="0.92", zorder=0)
        ax.set_xlim(0, 20); ax.set_xlabel("frecuencia (Hz)"); ax.set_ylabel("amplitud de e (N)")
        ax.set_title(f"Espectro de e, media de pisadas >= {a.desde}"); ax.grid(alpha=0.3); ax.legend(fontsize=7)
        ax2.set_xlabel("pisada"); ax2.set_ylabel(f"RMS de e en {a.banda_rms[0]:g}-{a.banda_rms[1]:g} Hz (N)")
        ax2.set_title("RMS en banda vs pisada"); ax2.grid(alpha=0.3); ax2.legend(fontsize=7)
        fig.tight_layout(); fig.savefig(a.png, dpi=140)
        print(f"\nfigura: {a.png}")


if __name__ == "__main__":
    sys.exit(main())
