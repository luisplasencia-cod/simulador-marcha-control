"""Simulacion: control de Fz en tiempo real vs ILC, con la latencia del lazo como variable.

ES UN MODELO CON SUPUESTOS, NO UN MODELO IDENTIFICADO DEL SIMULADOR. Los parametros marcados
(SIN MEDIR) no estan medidos; el objetivo es ver COMO escala el error con la latencia y ordenar
que parametros hay que medir/identificar despues. Lo unico medido es la latencia (ver reportes).

Modelo (un eje, Fz, normalizado en %BW):
    servo (SIN MEDIR):  tau_a * dv/dt = u - v          (velocidad del actuador sigue al comando)
    contacto:          dF/dt = k_real * v + d(t)       (F = rigidez efectiva x desplazamiento)
    medicion:          F_med(t) = F(t - T)             (T = latencia total del lazo, la variable)
Metodos:
    RT     : u = Kp*(Fref - F_med)
    RT+FF  : RT + prealimentacion u_ff = dFref/dt / k_est   (k_est != k_real: error de modelo)
    ILC    : RT + Fcmd = Fref + delta_j ; delta_{j+1} = Q[delta_j + gamma*e_j(t+m)]  (cada ciclo)
d(t): perturbacion NO repetible (pulso aleatorio por ciclo) -> ILC no la puede aprender.
Referencia: curva REAL de Fz (media de 350 sujetos sanos, Gutenberg Gait Database, Horst 2021,
DOI 10.1038/s41597-021-01014-6) en ../referencia_grf/referencia_fz_gutenberg.csv (ver extraer_referencia_gutenberg.py).
Ya no hay forma inventada. Duracion del apoyo = 0.615 s medidos en esa misma base x6. Siguen SIN medir: tau_a, k_real -> se barren (sensibilidad), NO son datos.
"""
import os
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

DT = 0.0005
TC = 3.69           # DATO: apoyo medio 0.615 s (Gutenberg, 350 sanos, ../referencia_grf/duracion_apoyo_gutenberg.py) x 6 (factor confirmado por Luis)
TAU_A = 0.02        # SIN MEDIR: valor de partida, se barre (10-50 ms)
K_REAL, K_EST = 0.8, 1.0   # SIN MEDIR: valor de partida, se barre (0.5-1.5); k_est=1 es la rigidez que usa el modelo
KP = 10.0           # ganancia de lazo (1/s)
GAMMA = 0.5


_REF_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "referencia_grf")
# Referencia seleccionable (todas REALES): "gutenberg" (1.40 m/s, 350 sanos, suelo) o "T01".."T08" (Fukuchi 2018, cinta, 24 jovenes).
# 'tc' = duracion del apoyo x 6; 'tc_sens' = tres valores para el barrido de sensibilidad (ver notas de cada fuente).
CFG = {"ref": "gutenberg", "tc": TC, "tc_sens": (2.92, 3.69, 4.76),   # Gutenberg: rango REAL entre sujetos 0.487-0.793 s x 6
       "etiqueta": "Fz media de 350 sanos (Gutenberg, 1.40 m/s)", "sufijo": ""}


def usar_referencia(nombre):
    """Cambia la referencia a una curva real de Fukuchi (T01..T08): apoyo medio x 6 y barrido +-1 DE entre sujetos."""
    import re
    CFG["ref"] = nombre
    for l in open(os.path.join(_REF_DIR, "resumen_velocidad_fukuchi.txt")):
        m = re.match(rf"{nombre}: velocidad ([\d.]+) m/s .*?apoyo ([\d.]+) s \(DE ([\d.]+)\)", l)
        if m:
            v, ap, de = float(m.group(1)), float(m.group(2)), float(m.group(3))
            CFG.update(tc=round(ap * 6, 2), tc_sens=(round((ap - de) * 6, 2), round(ap * 6, 2), round((ap + de) * 6, 2)),
                       etiqueta=f"Fz media de 24 jovenes sanos (Fukuchi, cinta, {v:.2f} m/s)", sufijo=f"_{nombre}")
            return
    raise SystemExit(f"Referencia {nombre} no encontrada en resumen_velocidad_fukuchi.txt")


def referencia(n):
    """Fz objetivo en %BW (curva real de 101 puntos interpolada a n muestras, 0 % -> 100 % del apoyo)."""
    p = np.arange(n) / n
    if CFG["ref"] == "gutenberg":
        d = np.genfromtxt(os.path.join(_REF_DIR, "referencia_fz_gutenberg.csv"), delimiter=",", skip_header=1)
        return np.interp(p, d[:, 0] / 100.0, d[:, 1] * 100.0)
    d = np.genfromtxt(os.path.join(_REF_DIR, "curva_vs_velocidad_fukuchi.csv"), delimiter=",", names=True)
    return np.interp(p, d["pct_apoyo"] / 100.0, d[f"{CFG['ref']}_Fz_BW_media"] * 100.0)


def suavizar(x, n):  # filtro de fase cero (Q del ILC)
    w = np.hanning(n); w /= w.sum()
    pad = np.r_[x[::-1][-n:], x, x[::-1][:n]]
    return np.convolve(pad, w, "same")[n:-n]


def simular(metodo, T, n_ciclos, kp=KP, perturb=False, seed=0, tau=TAU_A, k_real=K_REAL, tc=None):
    rng = np.random.default_rng(seed)
    tc = CFG["tc"] if tc is None else tc
    n = int(tc / DT)
    ref = referencia(n)
    dref = np.gradient(ref, DT)
    nd = int(round(T / DT))
    delta = np.zeros(n)
    m = int(round((T + 1.0 / kp) / DT))
    F = v = 0.0
    cola = [0.0] * (nd + 1)
    rms, ultimo = [], None
    for j in range(n_ciclos):
        d = np.zeros(n)
        if perturb:
            i0 = int(rng.uniform(0.3, 0.6) * n); d[i0:i0 + int(0.1 / DT)] = rng.choice([-1, 1]) * 30.0
        Ft = np.empty(n)
        for i in range(n):
            cola.append(F); Fm = cola.pop(0)
            fcmd = ref[i] + (delta[i] if metodo == "ILC" else 0.0)
            u = kp * (fcmd - Fm)
            if metodo == "RT+FF":
                u += dref[i] / K_EST
            v += DT * (u - v) / tau
            F += DT * (k_real * v + d[i])
            Ft[i] = F
            if abs(F) > 1e4:
                return np.full(n_ciclos, np.inf), None, ref
        e = ref - Ft
        rms.append(np.sqrt(np.mean(e ** 2)))
        if metodo == "ILC":
            e_adel = np.r_[e[m:], np.zeros(m)]
            delta = suavizar(delta + GAMMA * e_adel, int(0.1 / DT))
        ultimo = Ft
    return np.array(rms), ultimo, ref


def margen_fase_Tmax(kp=KP, tau=TAU_A, pm_deg=45):
    w = np.linspace(1e-3, 200, 200000)
    wgc = w[np.argmin(np.abs(kp / (w * np.sqrt(1 + (w * tau) ** 2)) - 1))]
    return max(0.0, (np.deg2rad(90 - pm_deg) - np.arctan(wgc * tau)) / wgc), wgc


if __name__ == "__main__":
    if len(sys.argv) > 1:
        usar_referencia(sys.argv[1])
    Ts = np.array([0, 5, 10, 20, 40, 60, 80, 100, 130, 160]) / 1000
    NC = 12
    res = {"RT": [], "RT+FF": [], "ILC": [], "ILC+pert": [], "RT+pert": []}
    for T in Ts:
        res["RT"].append(simular("RT", T, 3)[0][-1])
        res["RT+FF"].append(simular("RT+FF", T, 3)[0][-1])
        res["ILC"].append(simular("ILC", T, NC)[0][-1])
        res["RT+pert"].append(np.mean(simular("RT", T, 6, perturb=True, seed=1)[0][2:]))
        res["ILC+pert"].append(np.mean(simular("ILC", T, NC, perturb=True, seed=1)[0][-4:]))
    tmax, wgc = margen_fase_Tmax()
    print("Latencia maxima con margen de fase >= 45 grados (analitico, tau_a=20 ms):")
    for kp in (2, 5, 10, 20, 40, 80):
        t, w = margen_fase_Tmax(kp)
        print(f"   Kp={kp:3d} 1/s -> ancho de banda de lazo {w/(2*np.pi):5.2f} Hz, T max = {t*1e3:6.1f} ms")
    print(f"Kp={KP} 1/s, tau={TAU_A*1e3:.0f} ms: wgc={wgc:.1f} rad/s; T max con margen de fase 45 deg = {tmax*1e3:.0f} ms")
    print(f"Referencia: {CFG['etiqueta']}; apoyo x6 = {CFG['tc']} s")
    print("RMS del error [%BW] (referencia pico ~100 %BW), ultimo ciclo:")
    print("T[ms] " + " ".join(f"{k:>9}" for k in res))
    for i, T in enumerate(Ts):
        print(f"{T*1e3:5.0f} " + " ".join(("  inestable" if not np.isfinite(res[k][i]) else f"{res[k][i]:9.2f}") for k in res))
    for k in res:
        res[k] = [x if np.isfinite(x) else np.nan for x in res[k]]

    print("\nSENSIBILIDAD a parametros NO medidos (T=10 ms, Kp=10): RMS ultimo ciclo [%BW] RT / ILC")
    print("  tau_a[ms]  k_real |   RT    ILC")
    for tau in (0.01, 0.02, 0.05):
        for kr in (0.5, 0.8, 1.0, 1.5):
            r1 = simular("RT", 0.010, 3, tau=tau, k_real=kr)[0][-1]
            r2 = simular("ILC", 0.010, NC, tau=tau, k_real=kr)[0][-1]
            f = lambda x: "inestable" if not np.isfinite(x) else f"{x:6.2f}"
            print(f"  {tau*1e3:8.0f}  {kr:6.1f} | {f(r1):>9} {f(r2):>9}")
    print("SENSIBILIDAD a la duracion del apoyo (tau=20 ms, k=0.8, T=10 ms): RMS RT / ILC")
    for tc in CFG["tc_sens"]:
        print(f"  apoyo {tc:.2f} s | {simular('RT', 0.010, 3, tc=tc)[0][-1]:6.2f} {simular('ILC', 0.010, NC, tc=tc)[0][-1]:6.2f}")
    fig, ax = plt.subplots(2, 2, figsize=(11, 8))
    p = np.arange(int(CFG["tc"] / DT)) / int(CFG["tc"] / DT) * 100
    for met, c in (("RT", "tab:red"), ("RT+FF", "tab:orange"), ("ILC", "tab:green")):
        r, F, ref = simular(met, 0.010, NC if met == "ILC" else 3)
        ax[0, 0].plot(p, F, c, label=met)
    ax[0, 0].plot(p, ref, "k--", label="objetivo"); ax[0, 0].set_title("(a) Fz con T = 10 ms (ultimo ciclo)")
    ax[0, 0].set_xlabel("% del apoyo"); ax[0, 0].set_ylabel("%BW"); ax[0, 0].legend()
    for k, c, ls in (("RT", "tab:red", "-"), ("RT+FF", "tab:orange", "-"), ("ILC", "tab:green", "-")):
        ax[0, 1].plot(Ts * 1e3, res[k], c, ls=ls, marker="o", label=k)
    ax[0, 1].axvline(tmax * 1e3, color="gray", ls=":"); ax[0, 1].text(tmax * 1e3, 60, " T max (PM 45°)", fontsize=8)
    ax[0, 1].set_yscale("log"); ax[0, 1].set_ylim(0.1, 100); ax[0, 1].set_title("(b) Error RMS vs latencia (sin perturbacion)")
    ax[0, 1].set_xlabel("latencia total T [ms]"); ax[0, 1].set_ylabel("RMS [%BW]"); ax[0, 1].legend()
    for T, c in ((0.010, "tab:green"), (0.060, "tab:purple")):
        ax[1, 0].plot(range(1, NC + 1), simular("ILC", T, NC)[0], c, marker="o", label=f"ILC, T={T*1e3:.0f} ms")
    ax[1, 0].set_yscale("log"); ax[1, 0].set_title("(c) Aprendizaje ILC: error por ciclo"); ax[1, 0].set_xlabel("ciclo"); ax[1, 0].set_ylabel("RMS [%BW]"); ax[1, 0].legend()
    for k, c in (("RT+pert", "tab:red"), ("ILC+pert", "tab:green")):
        ax[1, 1].plot(Ts * 1e3, res[k], c, marker="o", label=k.replace("+pert", ""))
    ax[1, 1].set_yscale("log"); ax[1, 1].set_ylim(0.1, 100); ax[1, 1].set_title("(d) Con perturbacion no repetible (pulso 3 %BW)"); ax[1, 1].set_xlabel("latencia total T [ms]"); ax[1, 1].set_ylabel("RMS [%BW]"); ax[1, 1].legend()
    fig.suptitle(f"Objetivo REAL: {CFG['etiqueta']}. Planta SIN MEDIR (tau_a=20 ms, k real=0.8, valores de partida que se barren); apoyo {CFG['tc']:.2f} s (x6)", fontsize=9)
    fig.tight_layout(); fig.savefig(f"control/simulacion/rt_vs_ilc_latencia{CFG['sufijo']}.png", dpi=130)
