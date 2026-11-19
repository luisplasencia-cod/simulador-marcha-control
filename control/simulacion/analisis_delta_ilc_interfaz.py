"""Analisis de datos YA guardados (sin hardware): por que el ILC de la interfaz empieza con delta~89 N y no aprende.
Lee reportes/datos/2026-11-18_pisadas_3ejes_interfaz/ y reportes/datos/2026-11-19_kp3_vs_kp5_70kg/; importa el ILC de
~/Projects/gaitsim-control (solo lectura). Genera reportes/figuras/2026-11-19_analisis_delta_ilc_interfaz.png"""
import sys, numpy as np
sys.path.insert(0, '/home/simgaitlibra/Projects/gaitsim-control')
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from src.fz.fz_ilc import ControlFzILC
D = 'reportes/datos/'
a = np.genfromtxt(D+'2026-11-18_pisadas_3ejes_interfaz/20261118_175820_Control_apoyo_talla170_montaje37_p1.csv', delimiter=',', names=True)
b = np.genfromtxt(D+'2026-11-18_pisadas_3ejes_interfaz/20261118_175820_Control_apoyo_talla170_montaje37_p2.csv', delimiter=',', names=True)
s = np.genfromtxt(D+'2026-11-19_kp3_vs_kp5_70kg/2026-11-19_103942_fz.csv', delimiter=',', names=True)
rms = lambda x: float(np.sqrt(np.mean(np.square(x))))
dur = 6.0; n = len(a['t_s'])
def ilc_con(t_axis):
    c = ControlFzILC(75*9.81, duracion_s=dur, rigidez_n_por_mm=26.4)
    tm = np.linspace(0, dur, c.n, endpoint=False)
    e = c.ref_n - np.interp(tm, t_axis, a['Fz_N']); c.ilc.actualizar(e)
    return c, tm, e
c_real, tm, e_real = ilc_con(a['t_s'])                    # lo que hace la interfaz (t real)
c_nom, _, e_nom = ilc_con(np.arange(n)*0.010)             # lo que hace el script (t nominal = indice)
e_fila = a['objetivo_N'] - a['Fz_N']
print('periodo medio interfaz', np.mean(np.diff(a['t_s'])), 'duracion real', a['t_s'][-1])
print('RMS ILC (t real)', rms(e_real), 'RMS ILC (t nominal)', rms(e_nom), 'RMS fila a fila', rms(e_fila))
print('delta[0] t real', c_real.ilc.delta[0], 'nominal', c_nom.ilc.delta[0], 'p2 CSV', b['delta_ilc_N'][0])
print('delta rango t real', c_real.ilc.delta.min(), c_real.ilc.delta.max(), 'nominal', c_nom.ilc.delta.min(), c_nom.ilc.delta.max())
print('delta p2 CSV 0..0.5s', b['delta_ilc_N'].min(), b['delta_ilc_N'].max(), 'tiempo p2', b['t_s'][-1])
fig, ax = plt.subplots(2, 2, figsize=(13, 8))
ax[0,0].plot(a['t_s'], a['objetivo_N'], label='objetivo (indexado por muestra)'); ax[0,0].plot(a['t_s'], a['Fz_N'], label='Fz medida')
ax[0,0].axvline(6.0, color='k', ls='--', label='6.0 s = duracion que usa el ILC y la trayectoria X/K')
ax[0,0].set_title('Interfaz, pisada 1 (17:58): el lazo dura 8.27 s, no 6.0 s'); ax[0,0].legend(fontsize=7); ax[0,0].set_xlabel('t real [s]'); ax[0,0].set_ylabel('N')
ax[0,1].plot(tm, e_real, label=f'error que ve el ILC (t real) RMS {rms(e_real):.0f} N'); ax[0,1].plot(tm, e_nom, label=f'error con t = indice*10 ms RMS {rms(e_nom):.0f} N')
ax[0,1].set_title('Error que recibe el ILC'); ax[0,1].legend(fontsize=7); ax[0,1].set_xlabel('t [s]')
ax[1,0].plot(tm, c_real.ilc.delta, label='delta con t real (lo de la interfaz)'); ax[1,0].plot(tm, c_nom.ilc.delta, label='delta con t = indice')
ax[1,0].plot(b['t_s'], b['delta_ilc_N'], 'k.', ms=3, label='delta guardado en pisada 2 (0-0.5 s)')
ax[1,0].set_title('delta para la pisada 2'); ax[1,0].legend(fontsize=7); ax[1,0].set_xlabel('t [s]')
for c in (0, 1, 9):
    m = s['ciclo'] == c; ax[1,1].plot(s['t'][m], s['delta'][m], label=f'script 19-nov, ciclo {c}')
ax[1,1].set_title('delta del script (Kp5 70 kg): tambien arranca plano y grande'); ax[1,1].legend(fontsize=7); ax[1,1].set_xlabel('t nominal [s]')
plt.tight_layout(); plt.savefig('reportes/figuras/2026-11-19_analisis_delta_ilc_interfaz.png', dpi=110)
