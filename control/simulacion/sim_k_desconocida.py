"""Simulacion (SIN hardware) del lazo de Fz en Y con protesis de rigidez DESCONOCIDA.
Compara 4 formas de elegir pasos_por_n:
  M0 fijo   : k_asumido = 26.4 N/mm de la tabla + Kp a mano (8 a 50 kg, 5 a 90 kg)  = lo de hoy
  Ma precarga: rampa corta automatica tras el contacto -> k fijo para todas las pisadas
  Mb RLS    : k tangente en linea (minimos cuadrados recursivos) durante las pisadas
  Mc tabla  : precarga para la pisada 1 + k(F, carga/descarga) aprendido pisada a pisada (k varia dentro de la pisada)
  Md        : precarga para la pisada 1; despues de cada pisada, k fijo = el MAS RIGIDO de la rama de
              carga aprendida (F > 10 % del pico) + 15 % (ELEGIDO)
Ma/Mb/Mc usan Kp = 6 1/s en el dominio de fuerza para todas las protesis y cargas (<= la ganancia
efectiva ya corrida en hardware: 50 kg Kp 8 con k~25.5 -> 7.7; 90 kg Kp 5 con k~33 -> 6.3).

Planta (supuestos marcados): retardo comando->movimiento 20 ms (Ensayo B 15-23), servo de 1.er orden
tau 8 ms (Ensayo B 3-14), resorte con histeresis (rama de descarga = (1-h) * rama de carga, h=0.19
~ 18-20 % de energia perdida en el Ensayo A; transicion entre ramas con 2x la rigidez tangente: NO
medido), ruido del ADC 0.75 N + 60 Hz de 2.3 N rms (RPi, 2026-11-18), lectura = mediana de 7
muestras a 1 kHz, control cada 10 ms, saturacion 9000 pasos/s. Protecciones replicadas del lazo:
tope de fuerza min(1.25 pico, 1300 N), detector de saltos max(30 N, 8 % del pico), descenso maximo.

Uso:  python control/simulacion/sim_k_desconocida.py   (escribe figura y tabla en control/simulacion/)
"""
import os
import sys
from collections import deque

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "ilc"))
sys.path.insert(0, os.path.join(AQUI, "..", "identificacion"))
from fz_ilc import ControlFzILC  # noqa: E402
from estimador_k_en_linea import (EstimadorPrecarga, EstimadorRLS, GananciaSegura,  # noqa: E402
                                  TablaKPorFuerza, verificar_factibilidad, PASOS_POR_MM_Y)

DT = 0.001; DT_CTRL = 0.010; RETARDO = 0.020; TAU = 0.008
V_MAX = 9000.0; V_LENTA = 400.0; H = 0.19; FACTOR_TRANS = float(os.environ.get("FACTOR_TRANS", 2.0))
SIGMA = 0.75; A60 = 2.3 * np.sqrt(2)
K_TABLA = 26.4; KP_NORM = 6.0; N_PISADAS = 6; DUR_X10 = 6.15
MARGEN_TABLA = 0.15
PERCENTIL = float(os.environ.get("PERCENTIL", 70))
RECORRIDO_MAX_MM = 80.0   # ELECCION (no medido): tope de compresion permitido tras el contacto


class Resorte:
    """F(x) con histeresis. x = compresion [mm] (descenso desde el contacto)."""

    def __init__(self, tipo, k=None):
        self.tipo, self.k = tipo, k
        self.F = 0.0
        if tipo == "no_lineal":   # tangente k0 -> k1 al comprimir; secante ~25 N/mm a 578 N, ~32 a 1040 N
            self.k0, self.k1, self.x0 = 12.0, 42.0, 14.0

    def f_carga(self, x):
        if x <= 0: return 0.0
        if self.tipo == "lineal": return self.k * x
        return self.k1 * x - (self.k1 - self.k0) * self.x0 * (1 - np.exp(-x / self.x0))

    def k_tan(self, x):
        if self.tipo == "lineal": return self.k
        return self.k1 - (self.k1 - self.k0) * np.exp(-max(x, 0) / self.x0)

    def paso(self, x, dx):
        kt = FACTOR_TRANS * self.k_tan(x)
        if x <= 0:
            self.F = 0.0
        elif dx >= 0:
            self.F = min(self.F + kt * dx, self.f_carga(x))
        else:
            self.F = max(self.F + kt * dx, (1 - H) * self.f_carga(x))
        self.F = max(self.F, 0.0)
        return self.F

    def k_local(self, x, dx):
        """(rigidez tangente REAL en este instante, en_transicion_entre_ramas)."""
        if x <= 0: return 0.0, False
        if dx >= 0:
            if self.F >= self.f_carga(x) - 1e-6: return self.k_tan(x), False
            return FACTOR_TRANS * self.k_tan(x), True
        if self.F <= (1 - H) * self.f_carga(x) + 1e-6: return (1 - H) * self.k_tan(x), False
        return FACTOR_TRANS * self.k_tan(x), True


class Planta:
    def __init__(self, resorte, rng):
        self.r, self.rng = resorte, rng
        self.x = 0.0; self.v = 0.0; self.t = 0.0
        self.cola = deque([0.0] * int(round(RETARDO / DT)))
        self.adc = deque(maxlen=7)
        self.k_loc = 0.0; self.trans = False

    def avanzar(self, u_pasos_s, segundos):
        """u = velocidad ordenada de DESCENSO [pasos/s]. Devuelve la lectura (mediana de 7)."""
        for _ in range(int(round(segundos / DT))):
            self.cola.append(u_pasos_s / PASOS_POR_MM_Y)
            v_cmd = self.cola.popleft()
            self.v += (v_cmd - self.v) * DT / TAU
            dx = self.v * DT
            self.x += dx
            F = self.r.paso(self.x, dx)
            self.k_loc, self.trans = self.r.k_local(self.x, dx)
            self.t += DT
            self.adc.append(F + self.rng.normal(0, SIGMA) + A60 * np.sin(2 * np.pi * 60 * self.t))
        return float(np.median(self.adc))


def correr(metodo, resorte, kg, rng):
    peso = kg * 9.81
    pico = 1.178 * peso
    fmax = min(1.25 * pico, 1300.0)
    salto = max(30.0, 0.08 * pico)
    ctrl = ControlFzILC(peso, duracion_s=DUR_X10, rigidez_n_por_mm=K_TABLA)
    ref = ctrl.ref_bw / 100.0 * peso
    max_dr = np.max(np.abs(np.diff(ref))) / (DUR_X10 / ctrl.n)
    pl = Planta(resorte, rng)
    z = 0.0                     # descenso ORDENADO desde el contacto [mm] (lo que sabe la RPi)
    info = {"metodo": metodo, "kg": kg, "aborto": "", "rms": [], "hf": [], "agresividad": [], "kp_ef_rama": [], "sat": 0.0,
            "k_final": np.nan, "t_ident_s": 0.0, "avisos": []}

    # contacto: bajar lento hasta F > 8 N (5 seguidas), como el lazo real
    seg = 0
    while seg < 5:
        f = pl.avanzar(V_LENTA, DT_CTRL); z += V_LENTA * DT_CTRL / PASOS_POR_MM_Y
        seg = seg + 1 if f > 8.0 else 0
    pl.avanzar(0.0, 0.3)

    if metodo == "M0":
        kp = 8.0 if kg <= 60 else 5.0
        gan = None; k_fijo = K_TABLA
        extra = 1.5 * pico / 23.0                          # como la escalera de hoy (k ~23 supuesto)
    else:
        kp = KP_NORM
        t0 = pl.t
        est = EstimadorPrecarga(f_id_n=min(0.15 * pico, 150.0), z_max_mm=40.0)
        estado = "seguir"
        while estado == "seguir":
            f = pl.avanzar(V_LENTA, DT_CTRL); z += V_LENTA * DT_CTRL / PASOS_POR_MM_Y
            estado = est.agregar(z, f)
        # volver a ~umbral de contacto
        while f > 10.0:
            f = pl.avanzar(-V_LENTA, DT_CTRL); z -= V_LENTA * DT_CTRL / PASOS_POR_MM_Y
        pl.avanzar(0.0, 0.2)
        info["t_ident_s"] = pl.t - t0
        if estado == "demasiado_blanda":
            info["aborto"] = "precarga: demasiado blanda (no llego a F_id en 40 mm)"
            return info
        r = est.resultado()
        fac = verificar_factibilidad(r["k_secante"], r["k_tangente"], pico, max_dr, V_MAX, RECORRIDO_MAX_MM, DUR_X10)
        info["avisos"] = fac["avisos"]; info["k_precarga"] = r["k_tangente"]
        if fac["compresion_mm"] > RECORRIDO_MAX_MM:
            info["aborto"] = "factibilidad: " + "; ".join(fac["avisos"])
            return info
        extra = min(fac["extra_mm_sugerido"], RECORRIDO_MAX_MM)
        gan = GananciaSegura(r["k_tangente"], margen=0.3)
        rls = EstimadorRLS(k0=r["k_tangente"]) if metodo == "Mb" else None
        tab = TablaKPorFuerza(k_defecto=r["k_tangente"]) if metodo in ("Mc", "Md") else None
        if metodo in ("Mc", "Md"):
            # la precarga ya da puntos de carga en la franja baja
            tab.aprender_pisada(est.z, est.f)

    z_lim = z + extra
    previa = pl.avanzar(0.0, DT_CTRL)
    n_m = int(round(DUR_X10 / DT_CTRL))
    u = 0.0; n_sat = 0; n_tot = 0
    for p in range(N_PISADAS):
        tm, fm, zm, agres, rama = [], [], [], [], []
        for i in range(n_m):
            idx = int(i * ctrl.n / n_m)
            rc = ref[idx] + ctrl.ilc.delta[idx]
            f = pl.avanzar(u, DT_CTRL)
            if f > fmax:
                info["aborto"] = f"pisada {p + 1}: F {f:.0f} > tope {fmax:.0f} N"; return _cerrar(info, gan)
            if abs(f - previa) > salto:
                info["aborto"] = f"pisada {p + 1}: salto {abs(f - previa):.0f} > {salto:.0f} N"; return _cerrar(info, gan)
            previa = f
            e = rc - f
            if metodo == "M0":
                k_us = k_fijo
            elif metodo in ("Ma", "Md"):
                k_us = gan.k_usado
            elif metodo == "Mb":
                k_us = gan.actualizar(rls.actualizar(z, f), DT_CTRL)
            else:
                sentido = 1 if e > 0 else -1
                k_us = min(gan.k_max, max(gan.k_min, tab.consultar(f, sentido) * (1 + MARGEN_TABLA)))
                gan.k_usado = k_us
            u = kp * e * PASOS_POR_MM_Y / k_us
            if abs(u) >= V_MAX:
                n_sat += 1
            u = max(-V_MAX, min(V_MAX, u))
            n_tot += 1
            z += u * DT_CTRL / PASOS_POR_MM_Y
            if z >= z_lim:
                info["aborto"] = f"pisada {p + 1}: descenso {z:.0f} mm >= limite {z_lim:.0f} mm"; return _cerrar(info, gan)
            if pl.k_loc > 0 and f > 0.1 * pico:
                agres.append(kp * pl.k_loc / k_us)          # Kp efectivo en el dominio de fuerza [1/s]
                if not pl.trans:
                    rama.append(kp * pl.k_loc / k_us)
            tm.append(i * DT_CTRL); fm.append(f); zm.append(z)
        u = 0.0
        err = ref - np.interp(np.linspace(0, DUR_X10, ctrl.n, endpoint=False), tm, fm)
        info["rms"].append(float(np.sqrt(np.mean(err ** 2))) / pico * 100)
        e_t = np.interp(tm, np.linspace(0, DUR_X10, ctrl.n, endpoint=False), err)
        espectro = np.fft.rfft(e_t - np.mean(e_t)); fr = np.fft.rfftfreq(len(e_t), DT_CTRL)
        info["hf"].append(float(np.sqrt(np.sum(np.abs(espectro[fr > 3]) ** 2) * 2) / len(e_t)))
        info["agresividad"].append(float(np.percentile(agres, 95)) if agres else np.nan)
        info["kp_ef_rama"].append(float(np.median(rama)) if rama else np.nan)
        ctrl.registrar_medicion(tm, fm)
        if metodo in ("Mc", "Md"):
            tab.aprender_pisada(zm, fm)
        if metodo == "Md":
            gan.k_usado = max(gan.k_min, min(gan.k_max, k_max_carga(tab, pico) * (1 + MARGEN_TABLA)))
        info["ultima"] = (np.array(tm), np.array(fm), ref.copy())
    info["sat"] = n_sat / max(n_tot, 1) * 100
    return _cerrar(info, gan)


def k_max_carga(tab, pico):
    """k de la corrida = el MAS RIGIDO de la rama de carga en la zona de trabajo (F > 10 % del pico)."""
    k = tab.k_rigido_carga(0.1 * pico, PERCENTIL)
    return k if k is not None else tab.k_def


def _cerrar(info, gan):
    info["k_final"] = gan.k_usado if gan else K_TABLA
    return info


def main():
    casos = [("lineal 2.4", Resorte("lineal", 2.4)), ("lineal 23", Resorte("lineal", 23.0)),
             ("lineal 33", Resorte("lineal", 33.0)), ("no lineal 12->42", Resorte("no_lineal"))]
    filas, curvas = [], {}
    for kg in (50, 90):
        for nombre, _ in casos:
            for m in ("M0", "Ma", "Mb", "Mc", "Md"):
                res = Resorte(*([("lineal", float(nombre.split()[1]))][0])) if nombre.startswith("lineal") else Resorte("no_lineal")
                info = correr(m, res, kg, np.random.default_rng(1))
                info["caso"] = nombre
                filas.append(info)
                if "ultima" in info and m in ("M0", "Md"):
                    curvas[(kg, nombre, m)] = info["ultima"]
    lineas = ["| kg | protesis | metodo | RMS pisada 1 -> ultima (% pico) | error >3 Hz ultima (N) | Kp ef. en rama (mediana) 1/s | Kp ef. p95 (con transiciones) 1/s | % saturado | k_usado final N/mm | t ident (s) | resultado / avisos |",
              "|---|---|---|---|---|---|---|---|---|---|---|"]
    for i in filas:
        rms = f"{i['rms'][0]:.1f} -> {i['rms'][-1]:.1f}" if i["rms"] else "-"
        hf = f"{i['hf'][-1]:.1f}" if i["hf"] else "-"
        ag = f"{np.nanmax(i['agresividad']):.1f}" if i["agresividad"] else "-"
        ra = f"{np.nanmedian(i['kp_ef_rama']):.1f}" if i["kp_ef_rama"] else "-"
        res = i["aborto"] or ("completo" + (" (aviso: " + "; ".join(i["avisos"]) + ")" if i["avisos"] else ""))
        lineas.append(f"| {i['kg']} | {i['caso']} | {i['metodo']} | {rms} | {hf} | {ra} | {ag} | {i['sat']:.0f} | "
                      f"{i['k_final']:.1f} | {i['t_ident_s']:.1f} | {res} |")
    tabla = "\n".join(lineas)
    print(tabla)
    with open(os.path.join(AQUI, "sim_k_desconocida_tabla.md"), "w", encoding="utf-8") as f:
        f.write(tabla + "\n")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(16, 9.5))
    gs = fig.add_gridspec(2, 3, height_ratios=[1, 1.1])
    for col, nombre in enumerate(("lineal 23", "lineal 33", "no lineal 12->42")):
        ax = fig.add_subplot(gs[0, col])
        for m, estilo in (("M0", dict(color="#9e9e9e", lw=1.8, label="Rigidez fija 26,4 N/mm (como hoy)")),
                          ("Md", dict(color="#1565c0", lw=1.4, label="Precarga + rigidez alta aprendida (elegido)"))):
            if (90, nombre, m) in curvas:
                t, fz, ref = curvas[(90, nombre, m)]
                ax.plot(t, fz, **estilo)
        ax.plot(np.linspace(0, DUR_X10, len(ref), endpoint=False), ref, color="black", lw=1.2, ls="--", label="Objetivo de fuerza")
        ax.set_title("Carga 90 kg, escala x10, pisada %d\nprótesis %s N/mm" % (N_PISADAS, {"lineal 23": "lineal de 23", "lineal 33": "lineal de 33", "no lineal 12->42": "no lineal de 12 a 42"}[nombre]), fontsize=11)
        ax.set_xlabel("Tiempo dentro del apoyo (s)", fontsize=11); ax.grid(alpha=0.3); ax.tick_params(labelsize=10)
        if col == 0: ax.set_ylabel("Fuerza vertical (N)", fontsize=11); ax.legend(fontsize=10, loc="lower center")
    ax = fig.add_subplot(gs[1, :])
    etiquetas = [(kg, c) for kg in (50, 90) for c in ("lineal 23", "lineal 33", "no lineal 12->42")]
    colores = {"M0": "#9e9e9e", "Ma": "#ef6c00", "Mb": "#6a1b9a", "Mc": "#2e7d32", "Md": "#1565c0"}
    nombres = {"M0": "Rigidez fija (como hoy)", "Ma": "Solo precarga", "Mb": "Estimador recursivo en línea", "Mc": "Tabla rigidez vs fuerza", "Md": "Precarga + rigidez alta aprendida (elegido)"}
    for j, m in enumerate(("M0", "Ma", "Mb", "Mc", "Md")):
        ys = []
        for kg, c in etiquetas:
            fila = next(i for i in filas if i["kg"] == kg and i["caso"] == c and i["metodo"] == m)
            ys.append(np.nanmedian(fila["kp_ef_rama"]) if fila["kp_ef_rama"] else np.nan)
        ax.plot(np.arange(len(etiquetas)) + (j - 2) * 0.12, ys, "o", ms=9, color=colores[m], label=nombres[m])
    ax.axhline(KP_NORM, color="black", lw=1, ls="--")
    ax.text(-0.45, KP_NORM + 0.2, f"Ganancia de diseño: Kp = {KP_NORM:g} 1/s", ha="left", fontsize=10)
    ax.set_xticks(range(len(etiquetas))); ax.set_xticklabels([f"{kg} kg\n" + {"lineal 23": "lineal 23", "lineal 33": "lineal 33", "no lineal 12->42": "no lineal 12 a 42"}[c] + " N/mm" for kg, c in etiquetas], fontsize=10)
    ax.set_ylabel("Ganancia efectiva Kp (1/s)\n= Kp × rigidez real / rigidez usada", fontsize=11)
    ax.set_ylim(0, 13.5); ax.grid(alpha=0.3, axis="y"); ax.legend(fontsize=10, ncol=3, loc="upper left")
    ax.set_title("Qué tan agresivo queda el lazo con cada método (por encima de la línea = más agresivo de lo diseñado)", fontsize=11)
    fig.suptitle("Simulación (sin hardware): control de fuerza vertical cuando no se conoce la rigidez de la prótesis\nCon rigidez fija (gris) el lazo supera su ganancia de diseño en 5 de 6 casos; con precarga + rigidez aprendida (azul), en ninguno", fontsize=12)
    fig.text(0.5, 0.005, "Kp = ganancia del lazo (velocidad ordenada por cada newton de error). Rigidez = N de fuerza por mm que se comprime la prótesis. Supuestos: retardo 20 ms, constante del servo 8 ms, histéresis 19 %, ruido medido en la RPi. Es simulación, no medición.", ha="center", fontsize=9)
    fig.tight_layout(rect=(0, 0.03, 1, 0.955))
    salida = os.path.join(AQUI, "..", "..", "reportes", "figuras", "2026-11-19_sim_k_desconocida_claro.png")
    fig.savefig(salida, dpi=130, facecolor="white")
    print("figura:", os.path.normpath(salida))


if __name__ == "__main__":
    main()
