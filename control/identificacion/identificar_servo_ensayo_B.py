"""Identifica (retardo d, constante de tiempo del servo tau, rigidez k) del Ensayo B ajustando el modelo COMPLETO a cada
pulso (bajada + inversion + parada):   v' = (u(t-d) - v)/tau ;  F' = k*v ;  F(0)=F0  con u = -V (baja), +V (sube), 0 (parado).
Los tiempos de cambio de comando salen del propio CSV (primer bloque de cada fase menos un bloque de 7 ms). Modelo de 1er orden
para el servo (SUPUESTO): si el ajuste es malo, el modelo no vale. Uso: identificar_servo_ensayo_B.py <csv>"""
import sys, csv
import numpy as np
PASOS_MM = 80.0
ruta = sys.argv[1]
filas = [r for r in csv.reader(open(ruta)) if r and not r[0].startswith("#") and r[0] != "t_s"]
t = np.array([float(r[0]) for r in filas]); fase = [r[1] for r in filas]; F = np.array([float(r[2]) for r in filas]); vel = np.array([float(r[3]) for r in filas])
BLQ = 0.0072
pul = []   # (v, t_dn, t_up, t_stop, indices)
i = 1
while i < len(fase):
    if fase[i].startswith("baja") and not fase[i - 1].startswith("baja"):
        v = int(fase[i].split("v")[-1]); j = i
        while fase[j].startswith("baja"): j += 1
        k = j
        while fase[k].startswith("sube"): k += 1
        pul.append((v, t[i] - BLQ, t[j] - BLQ, t[k - 1], i)); i = k
    else:
        i += 1

def respuesta_unitaria(tt, tc_dn, tc_up, tc_st, V, d, tau):
    """G(t): integral de la velocidad v (mm) del servo de 1er orden con retardo d; F = F0 + k*G (k en N/mm)."""
    dt = 0.001; tg = np.arange(tt[0] - 0.3, tt[-1] + 0.001, dt)
    xr = tg - d
    u = np.where((xr >= tc_dn) & (xr < tc_up), -V, np.where((xr >= tc_up) & (xr < tc_st), V, 0.0))
    v = np.empty(len(tg)); vc = 0.0; al = dt / tau
    for n in range(len(tg)):
        vc += al * (u[n] - vc); v[n] = vc
    return np.interp(tt, tg, np.cumsum(v) * dt)

def ajustar_pulso(p):
    v, a, b, c, i0 = p; V = v / PASOS_MM        # mm/s ordenados
    m = (t > a - 0.35) & (t < c + 0.30); tt, ff = t[m], F[m]
    mejor = None
    def prueba(d, tau):
        G = respuesta_unitaria(tt, a, b, c, V, d, tau)
        A = np.vstack([np.ones_like(G), G]).T
        sol = np.linalg.lstsq(A, ff, rcond=None)[0]
        e = float(np.sum((A @ sol - ff) ** 2)); return e, sol
    for d in np.arange(0.0, 0.0601, 0.004):
        for tau in (0.005, 0.01, 0.02, 0.03, 0.04, 0.05, 0.065, 0.08, 0.1, 0.13):
            e, sol = prueba(d, tau)
            if mejor is None or e < mejor[0]: mejor = (e, d, tau, sol)
    e0, d0, t0_, _ = mejor                       # refinado alrededor del mejor
    for d in np.arange(max(0, d0 - 0.004), d0 + 0.0041, 0.001):
        for tau in np.linspace(max(0.003, t0_ * 0.7), t0_ * 1.4, 12):
            e, sol = prueba(d, tau)
            if e < mejor[0]: mejor = (e, d, tau, sol)
    e, d, tau, sol = mejor
    return np.array([d, tau, sol[1], sol[0]]), float(np.sqrt(e / len(ff)))

print("vel [pasos/s] | d [ms] | tau [ms] | k [N/mm] | rms ajuste [N]")
por_v = {}
for p in pul:
    th, rms = ajustar_pulso(p)
    por_v.setdefault(p[0], []).append(th)
    print(f"{p[0]:5d}         | {th[0]*1e3:6.1f} | {th[1]*1e3:7.1f}  | {th[2]:7.1f}  | {rms:.2f}")
for v, L in por_v.items():
    A = np.array(L)
    print(f"v={v}: d = {A[:,0].mean()*1e3:.0f} ± {A[:,0].std()*1e3:.0f} ms ; tau = {A[:,1].mean()*1e3:.0f} ± {A[:,1].std()*1e3:.0f} ms ; k = {A[:,2].mean():.1f} ± {A[:,2].std():.1f} N/mm  (n={len(A)}, ± = dispersion entre pulsos)")
