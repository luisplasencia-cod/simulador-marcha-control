"""Causa de la oscilacion de 6-8 Hz del lazo de Fz (escalera 50-90 kg x10, 2026-11-18) -- SOLO SIMULACION.

Planta (hipotesis, parametros elegidos para dar un modo de ~7 Hz; NO medidos):
  SET_VEL -> retardo d -> servo 1er orden tau -> posicion del motor xm
  xm --(resorte kd + amortiguador cd: cadena/husillo/estructura)--> carro de masa m --> protesis no lineal
  F_protesis = C * x^P (x = compresion, mm), ajustada a la escalera (comp. 23-32 mm a 584-1047 N) y al Ensayo A.
Medicion: ruido blanco 0.75 N + 60 Hz (sigma total 2.6 N, como en el RPi), bloque de 7 muestras frescas a 1 kHz, mediana.
Lazo: copia de las ecuaciones de control/lazo_fz_tiempo_real.py (P + ILC, indice de referencia por iteracion,
saturacion 9000 pasos/s, t del log NOMINAL). ILC: control/ilc/fz_ilc.py REAL (importado, no reimplementado).
Periodo real de cada iteracion: 7 ms (7 muestras frescas) + RTT de SET_VEL (~6 ms) + 0.5 ms -> ~13.5 ms (la interfaz,
con el mismo trabajo por iteracion, mide 13.0 ms de mediana: reportes/datos/2026-11-18_pisadas_3ejes_interfaz).

Uso: python control/simulacion/oscilacion_causa_2026-11-19.py  (imprime tablas, guarda la figura)
"""
import os
import sys

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "ilc"))
from fz_ilc import ControlFzILC  # noqa: E402

PASOS_MM = 80.0
K_ASUMIDO = 26.4
V_MAX = 9000.0
G = 9.81

# ---- planta (hipotesis) ----
K0_PROT, C_PROT, P_PROT = 15.0, 0.0377, 2.98   # F = K0 x + C x^P: 584 N a 20 mm, 1047 N a 26.4 mm (escalera menos F/kd);
                                               # K0 = 15 N/mm = rigidez a carga baja del Ensayo A (plana)
KD = 200.0                        # N/mm, rigidez del accionamiento (cadena+husillo+estructura): SUPUESTA
M = 140.0                         # kg efectivos del carro: elegida para fn ~7 Hz con KD=200 (no medida)
D_S, TAU_S = 0.019, 0.008         # Ensayo B: d 15-23 ms, tau 3-14 ms


def f_prot(x):
    x = np.maximum(x, 0.0)
    return K0_PROT * x + C_PROT * x ** P_PROT


def x_de_f(F):
    lo, hi = 0.0, 100.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if f_prot(mid) < F else (lo, mid)
    return 0.5 * (lo + hi)


def k_tan_prot(F):
    x = x_de_f(max(F, 1.0))
    return K0_PROT + P_PROT * C_PROT * x ** (P_PROT - 1)


class Sim:
    def __init__(self, zeta=0.06, d=D_S, tau=TAU_S, f0=20.0, seed=0, ruido=True, modo=True):
        self.modo = modo
        self.rng = np.random.default_rng(seed)
        self.d, self.tau, self.ruido = d, tau, ruido
        x0 = x_de_f(f0)
        self.xc = x0                                  # compresion de la protesis (mm, + = abajo)
        self.xm = x0 + f0 / KD                        # motor
        self.vm = self.vc = 0.0
        kp0 = k_tan_prot(700.0)
        wn = np.sqrt((KD + kp0) * 1000.0 / M)
        self.cd = 2 * zeta * wn * M / 1000.0          # N/(mm/s)
        self.t = 0.0
        self.cola = [(-1.0, 0.0)]                     # (t_aplica, u pasos/s)
        self.u_act = 0.0
        self.fase60 = self.rng.uniform(0, 2 * np.pi)
        self.dt = 0.0005

    def ordenar(self, u):
        self.cola.append((self.t + self.d, u))

    def paso(self):
        while len(self.cola) > 1 and self.cola[1][0] <= self.t:
            self.cola.pop(0)
        if self.cola[0][0] <= self.t:
            self.u_act = self.cola[0][1]
        v_obj = -self.u_act / PASOS_MM                # mm/s, + = bajar
        self.vm += (v_obj - self.vm) * self.dt / self.tau
        self.xm += self.vm * self.dt
        if not self.modo:                             # accionamiento rigido: sin modo mecanico
            self.xc, self.vc = self.xm - f_prot(self.xc) / KD, self.vm
            self.t += self.dt
            return f_prot(self.xc)
        fd = KD * (self.xm - self.xc) + self.cd * (self.vm - self.vc)
        fp = f_prot(self.xc)
        a = (fd - fp) * 1000.0 / M                    # mm/s^2
        self.vc += a * self.dt
        self.xc += self.vc * self.dt
        self.t += self.dt
        return fp

    def avanzar(self, dur):
        n = max(1, int(round(dur / self.dt)))
        ult = 0.0
        for _ in range(n):
            ult = self.paso()
        return ult

    def leer_bloque(self, n=7):
        vals = []
        for _ in range(n):
            f = self.avanzar(0.001)
            if self.ruido:
                f += self.rng.normal(0, 0.75) + 3.4 * np.sin(2 * np.pi * 60.0 * self.t + self.fase60)
            vals.append(f)
        return float(np.median(vals))


class ILCConOlvido:
    """Envoltorio SIN tocar control/ilc: delta <- Q(alfa*delta + gamma*e). alfa=1 es el ILC actual."""

    def __init__(self, ilc, alfa=1.0):
        self.ilc, self.alfa = ilc, alfa

    def actualizar(self, e):
        if self.alfa < 1.0:
            self.ilc.delta = self.alfa * self.ilc.delta
        return self.ilc.actualizar(e)


def correr(kg, kp, pisadas=10, zeta=0.06, periodo="real", interp=False, a_max=None, alfa=1.0,
           gamma=None, ancho_q=None, seed=0, ruido=True, d=D_S, tau=TAU_S, dur_apoyo=6.15, modo=True, kp_sched=False):
    """Replica el bucle de correr_lazo(). Opciones de mejora: interp (r y delta interpolados por tiempo REAL),
    a_max (limite de aceleracion del comando, mm/s^2, aplicado en el RPi), alfa (olvido del ILC), gamma/ancho_q."""
    peso = kg * G
    ctrl = ControlFzILC(peso, duracion_s=dur_apoyo, rigidez_n_por_mm=K_ASUMIDO)
    if gamma is not None:
        ctrl.ilc.gamma = gamma
    if ancho_q is not None:
        ctrl.ilc.ancho_q = int(ancho_q)
    ilc_w = ILCConOlvido(ctrl.ilc, alfa)
    pasos_por_n = PASOS_MM / K_ASUMIDO
    sim = Sim(zeta=zeta, seed=seed, ruido=ruido, d=d, tau=tau, modo=modo)
    rng = np.random.default_rng(seed + 100)
    n_muestras = int(round(dur_apoyo / 0.010))
    salto_max = max(30.0, 0.08 * 1.178 * peso)
    res = []
    u_prev = 0.0
    previa = sim.leer_bloque() - 0.0
    for p in range(pisadas):
        T, F, E, U, TREAL, ER = [], [], [], [], [], []
        t0 = sim.t
        max_salto = 0.0
        i = 0
        while (sim.t - t0 < dur_apoyo) if interp else (i < n_muestras):
            t_rel = i * 0.010
            i_act = i
            i += 1
            if interp:
                s = min((sim.t - t0) / dur_apoyo, 0.999999) * ctrl.n
                j = int(s); fr = s - j; j2 = min(j + 1, ctrl.n - 1)
                r = (ctrl.ref_n[j] * (1 - fr) + ctrl.ref_n[j2] * fr)
                dl = ctrl.ilc.delta[j] * (1 - fr) + ctrl.ilc.delta[j2] * fr
                t_reg = sim.t - t0
            else:
                idx = int(i_act * ctrl.n / n_muestras)
                r, dl = ctrl.ref_bw[idx] / 100.0 * peso, ctrl.ilc.delta[idx]
                t_reg = t_rel
            f = sim.leer_bloque()                       # 7 ms
            max_salto = max(max_salto, abs(f - previa)); previa = f
            e = (r + dl) - f
            kp_i = kp
            if kp_sched:   # ganancia programada con la rigidez tangente (ORACULO del modelo: en el rig vendria del estimador)
                kt = k_tan_prot(max(r + dl, 20.0)); ks = kt * KD / (KD + kt)
                kp_i = kp * min(1.0, K_ASUMIDO / ks)      # nunca mas agresivo que lo disenado
            u = max(-V_MAX, min(V_MAX, -kp_i * e * pasos_por_n))
            if a_max is not None:
                du = a_max * PASOS_MM * 0.0135           # pasos/s por iteracion
                u = max(u_prev - du, min(u_prev + du, u))
            u_prev = u
            sim.ordenar(u)
            if periodo == "real":
                resto = max(0.001, rng.normal(0.0060, 0.0015)) + 0.0005   # RTT de SET_VEL + overhead [s]
            else:
                resto = max(0.0, 0.010 - 0.007)
            sim.avanzar(resto)
            T.append(t_reg); F.append(f); E.append(e); U.append(u); TREAL.append(sim.t - t0); ER.append(r - f)
        sim.ordenar(0.0)
        t_malla = np.linspace(0, dur_apoyo, ctrl.n, endpoint=False)
        ilc_w.actualizar(ctrl.ref_n - np.interp(t_malla, np.array(T), np.array(F)))
        res.append(metricas(np.array(TREAL), np.array(E), np.array(U), max_salto, salto_max, peso, np.array(ER)))
    return res


def metricas(t, e, u, max_salto, salto_max, peso, e_ref):
    fs = 100.0
    tu = np.arange(t[0], t[-1], 1 / fs)
    y = np.interp(tu, t, e)
    y = y - np.polyval(np.polyfit(tu, y, 1), tu)
    w = np.hanning(len(y))
    amp = 2 * np.abs(np.fft.rfft(y * w)) / w.sum()
    f = np.fft.rfftfreq(len(y), 1 / fs)
    b = (f >= 3) & (f <= 15)
    rms_b = np.sqrt(np.sum((amp[b] / np.sqrt(2)) ** 2) / 1.5)
    i = np.argmax(amp[b])
    return dict(rms=float(np.sqrt(np.mean(e_ref ** 2))),   # r - F, como imprime el lazo (sin delta)
 rms_3_15=float(rms_b), f_pico=float(f[b][i]),
                v_rms=float(np.std(np.diff(u)) / PASOS_MM), salto=max_salto, aborta=max_salto > salto_max,
                pico=1.178 * peso, dur=float(t[-1]))


def fila(nombre, res):
    r1, rN = res[0], res[-1]
    ab = [i + 1 for i, r in enumerate(res) if r["aborta"]]
    return (f"{nombre:<46s} RMS {r1['rms']:6.1f}->{rN['rms']:6.1f} N | 3-15 Hz {r1['rms_3_15']:5.1f}->{rN['rms_3_15']:5.1f} N "
            f"({100 * rN['rms_3_15'] / rN['pico']:.1f}% pico) f {rN['f_pico']:.1f} Hz | salto max {max(r['salto'] for r in res):5.0f} N"
            f"{'  ABORTARIA en pisada ' + str(ab[0]) if ab else ''} | apoyo real {rN['dur']:.2f} s")


def lineal(kp_eff, zeta, d=D_S + 0.0135 / 2 + 0.0035, tau=TAU_S, F=800.0, modo=True):
    """Lazo lineal alrededor de F. Devuelve margen de ganancia, frecuencia de fase -180, pico de sensibilidad
    |1/(1+L)| y su frecuencia (lo que amplifica ruido/escalones: un lazo estable con pico alto 'oscila')."""
    kp_t = k_tan_prot(F)
    w = np.linspace(0.5, 150, 60000)
    s = 1j * w
    if modo:
        wn = np.sqrt((KD + kp_t) * 1000.0 / M)
        cd = 2 * zeta * wn * M / 1000.0
        G_mec = kp_t * (KD + cd * s) / (M / 1000.0 * s ** 2 + cd * s + KD + kp_t)
    else:
        wn = np.nan
        G_mec = kp_t * KD / (KD + kp_t) * np.ones_like(s)
    L = kp_eff / K_ASUMIDO * np.exp(-s * d) / (1 + s * tau) / s * G_mec
    ph = np.unwrap(np.angle(L))
    i = np.argmin(np.abs(ph + np.pi))
    S = np.abs(1 / (1 + L))
    j = np.argmax(S)
    return dict(mg=1 / abs(L[i]), f180=w[i] / (2 * np.pi), fn=wn / (2 * np.pi), kt=kp_t, s_max=S[j], f_s=w[j] / (2 * np.pi),
                k_eff=kp_eff * (kp_t * KD / (KD + kp_t)) / K_ASUMIDO)


if __name__ == "__main__":
    print("== Lazo lineal en el pico de la curva (d efectivo = d + T/2 + 3.5 ms = %.0f ms) ==" % (1000 * (D_S + 0.0135 / 2 + 0.0035)))
    for modo, z in ((False, 0), (True, 0.06), (True, 0.10)):
        for kg, kp in ((60, 8), (70, 8), (70, 5), (90, 5), (70, 3), (90, 3)):
            r = lineal(kp, z, F=1.178 * kg * G, modo=modo)
            print(f"  {'modo 7 Hz z=%.2f' % z if modo else 'SIN modo (rigido) ':<18s} {kg} kg Kp {kp}: k_tan {r['kt']:4.0f} N/mm, "
                  f"ganancia efectiva {r['k_eff']:5.1f} 1/s, fase -180 a {r['f180']:.1f} Hz, margen ganancia {r['mg']:4.2f}, "
                  f"pico sensibilidad {r['s_max']:5.1f} a {r['f_s']:.1f} Hz")


def figura(ruta):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(2, 2, figsize=(12, 8.5))
    # (a) filtro Q real del ILC
    ctrl = ControlFzILC(687.0, 6.15, rigidez_n_por_mm=K_ASUMIDO)
    nq = ctrl.ilc.ancho_q
    w = np.hanning(2 * nq + 1); w /= w.sum()
    f = np.linspace(0.05, 10, 400)
    for dur, et in ((6.15, "malla nominal (x10)"), (615 * 0.0135, "malla real (iteracion 13.5 ms)")):
        Ts = dur / ctrl.n
        H = [abs(np.sum(w * np.exp(-2j * np.pi * fi * Ts * np.arange(-nq, nq + 1)))) for fi in f]
        ax[0, 0].semilogy(f, np.maximum(H, 1e-5), label=et)
    ax[0, 0].axvspan(6, 8, color="0.9"); ax[0, 0].set_ylim(1e-4, 2)
    ax[0, 0].set_xlabel("frecuencia (Hz)"); ax[0, 0].set_ylabel("|Q|")
    ax[0, 0].set_title("(a) Filtro Q del ILC real: no deja pasar 6-8 Hz"); ax[0, 0].legend(fontsize=8); ax[0, 0].grid(alpha=.3)
    # (b) margen de ganancia vs ganancia efectiva
    kps = np.linspace(1, 10, 40)
    for modo, z, et in ((False, 0, "sin modo (solo retardo 29 ms)"), (True, 0.10, "modo 7 Hz, zeta 0.10"), (True, 0.15, "modo 7 Hz, zeta 0.15")):
        x, y = [], []
        for kp in kps:
            r = lineal(kp, z, F=1.178 * 70 * G, modo=modo)
            x.append(r["k_eff"]); y.append(r["mg"])
        ax[0, 1].plot(x, y, label=et)
    for kg, kp in ((60, 8), (70, 8), (70, 5), (90, 5)):
        r = lineal(kp, 0.10, F=1.178 * kg * G)
        ax[0, 1].plot(r["k_eff"], r["mg"], "ko", ms=4)
        ax[0, 1].annotate(f"{kg} kg Kp{kp}", (r["k_eff"], r["mg"]), fontsize=7, xytext=(3, 3), textcoords="offset points")
    ax[0, 1].axhline(1, color="r", lw=1); ax[0, 1].set_ylim(0, 6)
    ax[0, 1].set_xlabel("ganancia efectiva en el pico = Kp * k_tangente / k_asumido (1/s)")
    ax[0, 1].set_ylabel("margen de ganancia"); ax[0, 1].legend(fontsize=8); ax[0, 1].grid(alpha=.3)
    ax[0, 1].set_title("(b) Lazo lineal en el pico: <1 = inestable (a ~5.7 Hz)")
    # (c),(d) crecimiento pisada a pisada y mejoras
    for k, (kg, kp) in enumerate(((60, 8), (70, 8))):
        a = ax[1, k]
        for nombre, kw in (("actual", {}), ("r/delta interpolados", dict(interp=True, dur_apoyo=8.37)),
                           ("rampa 1000 mm/s2", dict(a_max=1000)), ("rampa 400 mm/s2", dict(a_max=400)),
                           ("ILC olvido 0.95", dict(alfa=0.95)), ("Kp programado por k_tan", dict(kp_sched=True))):
            res = correr(kg=kg, kp=kp, pisadas=10, zeta=0.10, **kw)
            a.plot(range(1, 11), [r["rms_3_15"] for r in res], "o-", ms=3, label=nombre)
        a.set_yscale("log"); a.set_xlabel("pisada"); a.set_ylabel("RMS del error en 3-15 Hz (N)")
        a.set_title(f"({'cd'[k]}) {kg} kg x10, Kp {kp}, modo 7 Hz zeta 0.10"); a.grid(alpha=.3); a.legend(fontsize=7)
    fig.suptitle("Oscilacion 6-8 Hz: simulacion con modo mecanico + ILC real (hipotesis, parametros del modo NO medidos)", fontsize=10)
    fig.tight_layout(); fig.savefig(ruta, dpi=130)
    print("figura:", ruta)


if __name__ == "__main__" and "--figura" in sys.argv:
    figura(os.path.join(AQUI, "oscilacion_causa_2026-11-19.png"))
