"""Analisis (2026-11-19): la resonancia 6-8 Hz vista en la escalera 50-90 kg (x10)
es resonancia del propio lazo (margen de fase/ganancia) o no?

NO ejecuta en hardware. Usa el modelo de planta de `rt_vs_ilc_latencia.py` (servo de
1er orden tau_a + integrador de rigidez k) con los parametros REALES medidos hoy
(2026-11-18), no los supuestos (SIN MEDIR) que trae ese script por defecto:

  - Retardo total T y tau_a del servo: Ensayo B (reportes/2026-11-18_ensayo_B_respuesta_dinamica.md)
    T = 15-23 ms (comando->Fz), tau_a = 3-14 ms (NO los 20 ms supuestos antes).
  - Rigidez dinamica |k| = 17.7-19.5 N/mm (Ensayo B) vs k_asumido = talon = 26.4 N/mm
    (Etapa 1, 2026-11-06) -> ratio k_real/k_asumido = 0.68-0.74.
  - Kp REALMENTE usado por escalon (reportes/2026-11-18_escalera_50_a_90kg_x10_y_abortos.md):
    Kp=8 en 50-60 kg, Kp=5 en 70-90 kg.

Metodo: lazo abierto L(jw) = Kp * k_ratio * e^{-jwT} / (jw (1 + jw*tau_a)), unitario en
la misma normalizacion que `margen_fase_Tmax` de rt_vs_ilc_latencia.py (no reescala a N
reales: el objetivo es ver DONDE cae el pico de resonancia en frecuencia, no su amplitud
absoluta en N). Closed-loop F/Fref = L/(1+L). Se barre w y se busca (a) el pico de
|F/Fref| (resonancia) y su frecuencia, (b) el margen de fase/ganancia, (c) si es inestable
(|L|=1 con fase <=-180 grados).
"""
import os
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# reusa el modelo/parametros ya existentes del script oficial, sin modificarlo
import rt_vs_ilc_latencia as base  # noqa: E402


def loop_L(w, kp, tau, T, k_ratio):
    jw = 1j * w
    return kp * k_ratio * np.exp(-jw * T) / (jw * (1 + jw * tau))


def analizar(kp, tau, T, k_ratio, w_max_hz=30, n=200000):
    w = np.linspace(1e-2, 2 * np.pi * w_max_hz, n)
    L = loop_L(w, kp, tau, T, k_ratio)
    clt = L / (1 + L)  # F/Fref
    mag = np.abs(clt)
    i_pico = np.argmax(mag)
    f_pico_hz = w[i_pico] / (2 * np.pi)
    mag_pico = mag[i_pico]
    mag_dc = np.abs(loop_L(1e-3, kp, tau, T, k_ratio) / (1 + loop_L(1e-3, kp, tau, T, k_ratio)))
    # margen de ganancia/fase clasicos sobre L
    magL = np.abs(L)
    i_gc = np.argmin(np.abs(magL - 1))  # cruce de ganancia (|L|=1)
    f_gc_hz = w[i_gc] / (2 * np.pi)
    fase_en_gc = np.angle(L[i_gc], deg=True)
    pm = 180 + fase_en_gc  # margen de fase
    inestable = pm < 0
    return dict(f_pico_hz=f_pico_hz, mag_pico=mag_pico, mag_dc=mag_dc, pico_sobre_dc=mag_pico / mag_dc,
                f_gc_hz=f_gc_hz, pm_deg=pm, inestable=inestable, w=w, mag=mag)


if __name__ == "__main__":
    # Ensayo B: T y tau_a medidos; k dinamico vs k_asumido (talon, Etapa 1)
    K_ASUMIDO = 26.4  # N/mm, talon (+11.14 deg), decision Etapa 1 (2026-11-06); = base.K_ASUMIDO_ETAPA1 pero ese nombre solo existe dentro del bloque __main__ de rt_vs_ilc_latencia.py, no se puede importar
    K_DIN_RANGO = (17.7, 19.5)         # N/mm, Ensayo B
    T_RANGO = (0.015, 0.023)           # s, Ensayo B
    TAU_RANGO = (0.003, 0.014)         # s, Ensayo B (NO los 20 ms supuestos)
    CASOS = [("50-60 kg (Kp=8)", 8), ("70-90 kg (Kp=5)", 5)]

    print("Rigidez dinamica Ensayo B vs k_asumido (talon, Etapa 1 = 26.4 N/mm):")
    for k in K_DIN_RANGO:
        print(f"  k_din={k:4.1f} N/mm -> ratio={k/K_ASUMIDO:.3f}")

    print("\n=== Peor caso y mejor caso de cada escalon (T, tau, k_ratio combinados en los extremos) ===")
    print(f"{'caso':<20} {'T[ms]':>6} {'tau[ms]':>8} {'k_ratio':>8} | {'f_pico[Hz]':>10} {'pico/DC':>8} {'f_gc[Hz]':>9} {'PM[deg]':>8} {'estable?':>9}")
    filas = []
    for nombre, kp in CASOS:
        for T in T_RANGO:
            for tau in TAU_RANGO:
                for k_din in K_DIN_RANGO:
                    ratio = k_din / K_ASUMIDO
                    r = analizar(kp, tau, T, ratio)
                    filas.append((nombre, kp, T, tau, ratio, r))
                    print(f"{nombre:<20} {T*1e3:6.1f} {tau*1e3:8.1f} {ratio:8.3f} | "
                          f"{r['f_pico_hz']:10.2f} {r['pico_sobre_dc']:8.2f} {r['f_gc_hz']:9.2f} "
                          f"{r['pm_deg']:8.1f} {'NO' if r['inestable'] else 'si':>9}")

    # Resumen: rango de f_pico y si crece el pico (amplitud relativa) al pasar de Kp=8 a Kp=5
    import itertools
    f_picos_por_caso = {}
    pico_rel_por_caso = {}
    for nombre, kp in CASOS:
        fs = [r["f_pico_hz"] for (n_, kp_, T, tau, ratio, r) in filas if n_ == nombre]
        ps = [r["pico_sobre_dc"] for (n_, kp_, T, tau, ratio, r) in filas if n_ == nombre]
        f_picos_por_caso[nombre] = (min(fs), max(fs))
        pico_rel_por_caso[nombre] = (min(ps), max(ps))

    print("\n=== Resumen ===")
    for nombre, kp in CASOS:
        fmin, fmax = f_picos_por_caso[nombre]
        pmin, pmax = pico_rel_por_caso[nombre]
        print(f"{nombre}: f_pico en [{fmin:.2f}, {fmax:.2f}] Hz ; sobreimpulso resonante pico/DC en [{pmin:.2f}, {pmax:.2f}]")

    # Figura: |F/Fref| vs frecuencia para los 2 casos, usando el PUNTO MEDIO de cada rango medido
    fig, ax = plt.subplots(1, 2, figsize=(15, 6.2))
    T_mid, tau_mid = np.mean(T_RANGO), np.mean(TAU_RANGO)
    colores = {"50-60 kg (Kp=8)": "tab:blue", "70-90 kg (Kp=5)": "tab:red"}
    for nombre, kp in CASOS:
        for k_din, ls in zip(K_DIN_RANGO, ("-", "--")):
            ratio = k_din / K_ASUMIDO
            r = analizar(kp, tau_mid, T_mid, ratio)
            ax[0].plot(r["w"] / (2 * np.pi), 20 * np.log10(r["mag"] / r["mag_dc"]), ls, color=colores[nombre],
                       label=f"{nombre.replace('Kp=', 'Kp ')}, rigidez dinámica {k_din} N/mm")
    ax[0].axvspan(6, 8, color="gray", alpha=0.2, label="Banda de oscilación observada (6–8 Hz)")
    ax[0].set_xlim(0, 20); ax[0].set_xlabel("Frecuencia (Hz)", fontsize=11); ax[0].set_ylabel("Fuerza medida / fuerza objetivo,\nrelativa a frecuencia 0 (dB)", fontsize=11)
    ax[0].set_title(f"(a) Respuesta en frecuencia del lazo cerrado\nretardo T={T_mid*1e3:.1f} ms, constante del servo={tau_mid*1e3:.1f} ms (punto medio, Ensayo B)", fontsize=11)
    ax[0].legend(fontsize=9, loc="upper right"); ax[0].grid(alpha=0.3)

    # (b) f_pico vs tau_a, para los 2 extremos de T, Kp=8 y Kp=5, k_ratio medio
    k_ratio_medio = np.mean(K_DIN_RANGO) / K_ASUMIDO
    taus_plot = np.linspace(TAU_RANGO[0], TAU_RANGO[1], 20)
    for nombre, kp in CASOS:
        for T, ls in zip(T_RANGO, ("-", "--")):
            fs = [analizar(kp, tau, T, k_ratio_medio)["f_pico_hz"] for tau in taus_plot]
            ax[1].plot(taus_plot * 1e3, fs, ls, color=colores[nombre], label=f"{nombre.replace('Kp=', 'Kp ')}, retardo {T*1e3:.0f} ms")
    ax[1].axhspan(6, 8, color="gray", alpha=0.2, label="Banda de oscilación observada (6–8 Hz)"); ax[1].text(8.5, 3.0, "Todas las curvas valen 0 Hz:\nel modelo NO tiene pico de resonancia", ha="center", fontsize=11, color="darkred")
    ax[1].set_xlabel("Constante de tiempo del servo (ms)", fontsize=11); ax[1].set_ylabel("Frecuencia del pico de resonancia (Hz)", fontsize=11)
    ax[1].set_title("(b) Frecuencia de resonancia según la constante del servo", fontsize=11)
    ax[1].legend(fontsize=9, loc="upper left"); ax[1].grid(alpha=0.3)
    fig.suptitle("¿El modelo lineal del lazo cerrado explica la oscilación de 6–8 Hz? No: no predice ningún pico de resonancia\n(modelo con los retardos y la rigidez medidos en el Ensayo B)", fontsize=12)
    fig.text(0.5, 0.005, "T = retardo total del lazo; Kp = ganancia del lazo; rigidez dinámica = N de fuerza por mm (Ensayo B). Es un cálculo con el modelo, no una medición.", ha="center", fontsize=9)
    fig.tight_layout(rect=(0, 0.03, 1, 0.93))
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "reportes", "figuras", "2026-11-19_resonancia_6_8hz_claro.png")
    fig.savefig(out, dpi=130)
    print(f"\nFigura guardada: {out}")
