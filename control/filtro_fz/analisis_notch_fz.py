"""Analisis OFFLINE (2026-11-19) de opciones para atenuar la oscilacion de 6-8 Hz en Fz. No toca hardware
ni el lazo. Reporte: reportes/2026-11-19_propuesta_notch_fz_6_8hz.md.
Uso: python control/filtro_fz/analisis_notch_fz.py   (escribe la figura y salida_analisis_notch_fz.txt)
"""
import math
import os
import sys

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from notch_fz import FiltroNotchFz, LimitadorAceleracion  # noqa: E402

RAIZ = os.path.normpath(os.path.join(AQUI, "..", ".."))
FS = 100.0                 # tasa del lazo (DT_CONTROL_S = 10 ms)
PASOS_POR_MM = 80
APOYO_X10 = 6.15           # s (escalera 50-90 kg)
# Medido en la escalera 2026-11-18 (reportes/2026-11-18_escalera_50_a_90kg_x10_y_abortos.md)
ESCALONES = [  # kg, Kp, k aparente N/mm, f osc Hz, osc rms N (ultima pisada, bajada del 1.er pico)
    (60, 8, 28.5, 8.3, 6.8), (70, 5, 27.9, 2.8, 19.9), (80, 5, 31.4, 6.4, 20.4), (90, 5, 33.1, 7.3, 31.0)]
K_ASUMIDO = 26.4           # tabla_k_por_protesis.json (pie_pasivo_1)
T_LAZO_S = (0.020, 0.028)  # retardo efectivo del lazo: Ensayo B 15-23 ms + ~5 ms de muestreo

OPCIONES = [
    ("Notch 7 Hz, angosto (Q=5)", [(7.0, 5.0)], "-"),
    ("Notch 7 Hz, ancho (Q=2)", [(7.0, 2.0)], "--"),
    ("Notch 6–8 Hz centrado (6,93 Hz, Q=3,46)", [(math.sqrt(48), math.sqrt(48) / 2)], "-."),
    ("Dos notches, 6,4 y 8,3 Hz (Q=4)", [(6.4, 4.0), (8.3, 4.0)], ":"),
]

out = []
def p(s=""):
    print(s); out.append(s)

d = np.genfromtxt(os.path.join(RAIZ, "control", "referencia_grf", "referencia_fz_gutenberg.csv"), delimiter=",", skip_header=1)
t = np.arange(0, APOYO_X10, 1 / FS)
def curva_n(kg):
    return np.interp(t / APOYO_X10 * 100, d[:, 0], d[:, 1]) * kg * 9.81

# frecuencia de cruce del termino P: dF/dt = Kp*(k_real/k_asumido)*e  ->  wc = Kp*k_real/k_asumido [rad/s]
p("== Frecuencia de cruce del termino P (modelo integrador + retardo; NO predice la oscilacion de 7 Hz)")
cruces = []
for kg, kp, k, f_osc, a_osc in ESCALONES:
    wc = kp * k / K_ASUMIDO
    cruces.append(wc / (2 * np.pi))
    pm = [90 - math.degrees(wc * T) for T in T_LAZO_S]
    p(f"  {kg} kg Kp {kp}: fc = {wc / 2 / np.pi:.2f} Hz; margen de fase sin filtro {pm[1]:.0f}-{pm[0]:.0f} deg")
fc_min, fc_max = min(cruces), max(cruces)

p("\n== Coherencia: velocidad que el termino P ordena al ver la oscilacion de Fz (v = Kp*e/k_asumido)")
for kg, kp, k, f_osc, a_osc in ESCALONES:
    wc = kp * k / K_ASUMIDO
    T = 0.025
    L = wc / (1j * 2 * np.pi * f_osc) * np.exp(-1j * 2 * np.pi * f_osc * T)
    p(f"  {kg} kg: {a_osc:4.1f} N rms a {f_osc} Hz -> {kp * a_osc / K_ASUMIDO:4.1f} mm/s rms ordenados; "
      f"|L({f_osc} Hz)| = {abs(L):.2f}, |S| = |1/(1+L)| = {abs(1 / (1 + L)):.2f} (modelo integrador + 25 ms)")
p("  (medido: v de Y oscila 2-6 mm/s rms -> la oscilacion de v es el P reaccionando a la de Fz)")

p("\n== Costo y beneficio de cada notch (fs = 100 Hz, aplicado a la Fz del termino P)")
p(f"  {'opcion':34s} {'fase@1Hz':>8s} {'ret@1Hz':>8s} {'ret@2Hz':>8s} {'ret@3Hz':>8s} | {'6.4Hz':>6s} {'7.0Hz':>6s} {'7.3Hz':>6s} {'8.3Hz':>6s} | {'err GRF':>8s}")
p(f"  {'':34s} {'deg':>8s} {'ms':>8s} {'ms':>8s} {'ms':>8s} | {'dB':>6s} {'dB':>6s} {'dB':>6s} {'dB':>6s} | {'N max':>8s}")
curva90 = curva_n(90)
filas = []
for nombre, secc, ls in OPCIONES:
    nf = FiltroNotchFz(secc, FS)
    fase1 = -math.degrees(np.angle(nf.respuesta(1.0)[0]))
    ret = nf.retardo_equivalente_ms([1.0, 2.0, 3.0])
    att = 20 * np.log10(np.abs(nf.respuesta([6.4, 7.0, 7.3, 8.3])) + 1e-12)
    nf.reset(curva90[0])
    y = np.array([nf.filtrar(v) for v in curva90])
    err = np.max(np.abs(y - curva90))
    ret_c = nf.retardo_equivalente_ms([fc_min, fc_max])
    filas.append((nombre, secc, ls, ret_c))
    p(f"  {nombre:34s} {fase1:8.1f} {ret[0]:8.1f} {ret[1]:8.1f} {ret[2]:8.1f} | {att[0]:6.1f} {max(att[1], -60):6.1f} {att[2]:6.1f} {att[3]:6.1f} | {err:8.1f}")
p("  (ret = retardo puro equivalente a la perdida de fase; err GRF = max|filtrada - curva| en 90 kg x10, pico 1040 N)")
p("\n  Retardo equivalente en la frecuencia de cruce (se SUMA al retardo del lazo, 20-28 ms):")
for nombre, _, _, ret_c in filas:
    p(f"    {nombre:34s} {ret_c[0]:.1f} ms @ {fc_min:.2f} Hz ... {ret_c[1]:.1f} ms @ {fc_max:.2f} Hz")

p("\n== Alternativa: NO filtrar Fz, limitar la aceleracion del comando SET_VEL")
p("  Aceleracion que exige SEGUIR la curva (a = F''/k), a x10, sin la correccion del ILC:")
from scipy.interpolate import CubicSpline  # derivadas suaves (la interpolacion lineal infla F'')
amax_ref = {}
tt_fino = np.linspace(0, APOYO_X10, 6000)
for kg, kp, k, f_osc, a_osc in ESCALONES:
    cs = CubicSpline(d[:, 0] / 100 * APOYO_X10, d[:, 1] * kg * 9.81)
    v = cs(tt_fino, 1) / k                   # mm/s
    a = np.abs(cs(tt_fino, 2) / k)           # mm/s^2
    amax_ref[kg] = np.percentile(a, 99)
    p(f"    {kg} kg: v max {np.abs(v).max():5.1f} mm/s, a mediana {np.median(a):4.0f}, p99 {amax_ref[kg]:4.0f}, "
      f"max {a.max():4.0f} mm/s^2 (p99 = {amax_ref[kg] * PASOS_POR_MM:6.0f} pasos/s^2; los maximos estan en la carga inicial y el despegue)")
p("  Aceleracion de la oscilacion observada (v de Y 2-6 mm/s rms a ~7 Hz): "
  f"{2 * np.pi * 7 * 2 * math.sqrt(2):.0f}-{2 * np.pi * 7 * 6 * math.sqrt(2):.0f} mm/s^2 pico")
p("  Hoy el comando cambia en ESCALON cada 10 ms y el firmware no tiene rampa: cualquier salto de v es")
p("  aceleracion 'infinita' para el servo -> excita la estructura en todo el espectro.")

# funcion descriptiva del limitador (simulada): ganancia/fase de la fundamental
def df_limitador(a_max_mm_s2, f_hz, v_amp_mm_s):
    n = int(FS * 20)
    tt = np.arange(n) / FS
    vin = v_amp_mm_s * np.sin(2 * np.pi * f_hz * tt)
    lim = LimitadorAceleracion(a_max_mm_s2 * PASOS_POR_MM, 1 / FS)
    vout = np.array([lim.limitar(x * PASOS_POR_MM) for x in vin]) / PASOS_POR_MM
    m = tt >= 10
    ref = np.exp(-1j * 2 * np.pi * f_hz * tt[m])
    h = (vout[m] @ ref) / (vin[m] @ ref)
    return abs(h), -math.degrees(np.angle(h))

A_LIM = 3 * max(amax_ref.values())
p(f"\n  Limite probado: a_max = {A_LIM:.0f} mm/s^2 (3x la p99 de la curva de 90 kg; {A_LIM * PASOS_POR_MM:.0f} pasos/s^2)")
for f_hz, vamp in [(1.0, 56), (7.0, 2 * math.sqrt(2)), (7.0, 6 * math.sqrt(2)), (7.0, 15)]:
    g, ph = df_limitador(A_LIM, f_hz, vamp)
    p(f"    entrada {vamp:5.1f} mm/s pico a {f_hz:.0f} Hz -> ganancia {g:.2f}, atraso {ph:5.1f} deg")
p("  -> con ese limite la oscilacion observada pasa casi entera (no satura); para recortarla hay que bajar a_max")
for a_test in (150, 100):
    g, ph = df_limitador(a_test, 7.0, 6 * math.sqrt(2))
    g1, ph1 = df_limitador(a_test, 1.0, 56)
    p(f"     a_max {a_test} mm/s^2: 7 Hz (8.5 mm/s pico) ganancia {g:.2f} atraso {ph:.0f} deg; "
      f"1 Hz a 56 mm/s ganancia {g1:.2f} atraso {ph1:.0f} deg")

with open(os.path.join(AQUI, "salida_analisis_notch_fz.txt"), "w", encoding="utf-8") as fh:
    fh.write("\n".join(out) + "\n")

# ---------- figura ----------
f = np.logspace(-1, np.log10(49), 800)
colores = ["#2a6fdb", "#d1495b", "#2e7d32", "#7b3fa0"]
fig, ax = plt.subplots(3, 1, figsize=(11, 12), sharex=True)
for (nombre, secc, ls, _), col in zip(filas, colores):
    nf = FiltroNotchFz(secc, FS)
    h = nf.respuesta(f)
    ax[0].semilogx(f, 20 * np.log10(np.abs(h) + 1e-6), ls, color=col, lw=2, label=nombre)
    ax[1].semilogx(f, -np.degrees(np.unwrap(np.angle(h))), ls, color=col, lw=2)
    fb = f[f < 5.5]
    ax[2].semilogx(fb, nf.retardo_equivalente_ms(fb), ls, color=col, lw=2)
for a in ax:
    a.axvspan(6.4, 8.3, color="#f4a261", alpha=0.25, lw=0)
    a.axvspan(fc_min, fc_max, color="#888888", alpha=0.20, lw=0)
    a.axvspan(0.1, 3.0, color="#a8dadc", alpha=0.18, lw=0)
    a.grid(True, which="both", color="#dddddd", lw=0.6)
ax[0].set_ylim(-45, 3)
ax[0].set_ylabel("Ganancia del filtro (dB)\n(0 = pasa igual, −40 = casi eliminado)", fontsize=11)
ax[0].set_title("Filtro notch para la fuerza vertical (muestreo 100 Hz): propuesta, NO conectada al lazo\nLectura clave: el notch angosto (azul) quita la banda de 6–8 Hz con solo ~5 ms de retardo; los anchos suman 7–12 ms", fontsize=11)
ax[0].legend(loc="lower left", fontsize=10, frameon=True)
ax[0].text(9.0, -30,"Oscilación medida\n6,4–8,3 Hz", fontsize=10, color="#9c4a00")
ax[1].set_ylabel("Atraso de fase (grados)\n(positivo = atraso)", fontsize=11)
ax[1].set_ylim(-95, 95)
ax[1].text(fc_min * 1.02, 70, f"Frecuencia de cruce del\nlazo: {fc_min:.2f}–{fc_max:.2f} Hz", fontsize=10, color="#444444")
ax[1].text(0.12, 70, "Banda útil de la fuerza\nde marcha a x10 (< 3 Hz)", fontsize=10, color="#1d6f78")
ax[2].set_ylabel("Retardo que añade el filtro (ms)\n(se suma a los 20–28 ms del lazo)", fontsize=11)
ax[2].set_xlabel("Frecuencia (Hz)", fontsize=11)
fig.text(0.5, 0.005, "Notch = filtro que elimina una banda estrecha de frecuencias. Q = qué tan angosto es (mayor Q = más angosto). Es un cálculo del filtro, no una medición.", ha="center", fontsize=9)
ax[2].set_ylim(0, 20)
fig.tight_layout(rect=(0, 0.02, 1, 1))
dest = os.path.join(RAIZ, "reportes", "figuras", "2026-11-19_notch_fz_bode_claro.png")
fig.savefig(dest, dpi=150, facecolor="white")
print("figura:", dest)
