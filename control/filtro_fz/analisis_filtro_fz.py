"""Analisis OFFLINE del filtro para Fz (2026-11-05). No toca hardware.
Entradas: curva de referencia (Gutenberg) y parametros de ruido medidos (ver reportes/2026-11-05_ruido_fz.md).
Calcula: contenido espectral util a x6, y para cada filtro causal candidato: retardo de grupo,
ruido residual (blanco, ASD medida) y error de seguimiento sobre la curva de referencia.
Uso: .venv/bin/python control/filtro_fz/analisis_filtro_fz.py
"""
import numpy as np
FS = 1000.0
ASD = 0.040   # N/rtHz, MEDIDO en reposo (pruebas/lecturas_fz_20261102_175759.csv, tramos quietos), plano 4-200 Hz
SIG0 = 0.84   # N rms en reposo sin filtrar (mismo CSV); 0.80 N en los logs del 11-05 post-correccion
BW_N = 86 * 9.81  # N; 86 kg = masa del sujeto del articulo de conferencia (referencia, NO la carga de ensayo)
d = np.genfromtxt('control/referencia_grf/referencia_fz_gutenberg.csv', delimiter=',', skip_header=1)
curva = d[:, 1]
def curva_x6(T_apoyo):
    t = np.arange(0, T_apoyo, 1 / FS)
    return t, np.interp(t / T_apoyo * 100, d[:, 0], curva)

print("== 1) Contenido espectral de la curva objetivo (estirada a x6), cola de ceros hasta 60 s")
for T in (3.69, 6.43):
    t, y = curva_x6(T)
    Y = np.abs(np.fft.rfft(np.r_[y, np.zeros(60000 - len(y))])) ** 2
    f = np.fft.rfftfreq(60000, 1 / FS)
    e = np.cumsum(Y[1:]) / Y[1:].sum()   # sin la componente DC exacta
    print(f"  apoyo {T:.2f} s: f(99%) = {f[1:][np.searchsorted(e,0.99)]:.2f} Hz, f(99.9%) = {f[1:][np.searchsorted(e,0.999)]:.2f} Hz, "
          f"f(99.99%) = {f[1:][np.searchsorted(e,0.9999)]:.2f} Hz; pendiente max = {np.abs(np.diff(y)).max()*FS*100:.1f} %BW/s = {np.abs(np.diff(y)).max()*FS*BW_N:.0f} N/s")

def ma(x, N): return np.convolve(x, np.ones(N) / N)[:len(x)]
def iir1(x, fc):
    a = 1 - np.exp(-2 * np.pi * fc / FS); y = np.empty_like(x); s = x[0]
    for i, u in enumerate(x): s += a * (u - s); y[i] = s
    return y
def but2(x, fc):  # Butterworth 2.o orden, bilineal con prewarp
    K = np.tan(np.pi * fc / FS); q = np.sqrt(2); n = 1 / (1 + q * K + K * K)
    b = np.array([K * K, 2 * K * K, K * K]) * n; a1 = 2 * (K * K - 1) * n; a2 = (1 - q * K + K * K) * n
    y = np.zeros_like(x); x1 = x2 = y1 = y2 = x[0]
    for i, u in enumerate(x):
        v = b[0] * u + b[1] * x1 + b[2] * x2 - a1 * y1 - a2 * y2
        x2, x1, y2, y1 = x1, u, y1, v; y[i] = v
    return y
filtros = []
for N in (5, 10, 20): filtros.append((f"MA {N} muestras", lambda x, N=N: ma(x, N), (N - 1) / 2 / FS * 1e3, FS / (2 * N)))
for fc in (5, 10, 20, 40): filtros.append((f"IIR 1er orden fc={fc} Hz", lambda x, fc=fc: iir1(x, fc), 1e3 / (2 * np.pi * fc), np.pi / 2 * fc))
for fc in (5, 10, 20, 40): filtros.append((f"Butterworth 2o fc={fc} Hz", lambda x, fc=fc: but2(x, fc), np.sqrt(2) * 1e3 / (2 * np.pi * fc), np.pi / 4 / np.sin(np.pi / 4) * fc))

print("\n== 2) Filtros causales: retardo de grupo a baja frecuencia, ruido residual, error sobre la curva (apoyo 3.69 s, el mas rapido)")
t, y = curva_x6(3.69); y = np.r_[np.full(1000, y[0]), y, np.full(1000, y[-1])] * BW_N  # relleno con el valor del borde (sin escalon artificial)
rng = np.random.default_rng(0)
print(f"  {'filtro':28s} {'retardo ms':>10s} {'sigma ruido N':>13s} {'dism.':>6s} {'err pico N (sin ruido)':>22s} {'err/pico %':>10s}")
for nom, fn, ret, enbw in filtros:
    sig = ASD * np.sqrt(enbw)  # ruido blanco -> rms
    out = fn(y)
    err = np.abs(out - y)[1000:].max()   # contra la curva SIN retardar (lo que ve el lazo); el relleno inicial ya esta asentado
    print(f"  {nom:28s} {ret:10.2f} {sig:13.3f} {SIG0/sig:5.1f}x {err:22.2f} {100*err/y.max():10.2f}")
print("  (err pico = max|filtrada - curva original| incluye el retardo; MA: retardo exacto (N-1)/2 muestras; IIR1: 1/(2*pi*fc); But2: sqrt2/(2*pi*fc))")
