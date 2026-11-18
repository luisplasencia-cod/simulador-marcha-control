# Pisadas con los 3 ejes desde la interfaz (2026-11-18)
X y ángulo en lazo abierto (trayectoria `Control_apoyo_talla170_montaje37`), Y en lazo cerrado de Fz; 75 kg, x10, Kp 5.
Copias de `~/Projects/gaitsim-control/logs/fz/` (esa carpeta NO se sube a GitHub: está en el .gitignore de la interfaz).
Columnas: `t_s, objetivo_N, delta_ilc_N, Fz_N, vel_pasos_s` (vel = SET_VEL de Y en pasos/s, + = subir).

| archivo | hora | qué fue |
|---|---|---|
| 20261118_170511_..._p1.csv | 17:05 | aborto por `SET_VEL ... within 0.05s` (tarde; ver CLAUDE.md de la interfaz) |
| 20261118_172147_..._p1.csv | 17:21 | 1.ª pisada 3 ejes (tarde), RMS 222 N |
| 20261118_175712_..._p1.csv | 17:57 | corrida de 1 pisada (noche), RMS 219.3 N, completada |
| 20261118_175820_..._p1.csv | 17:58 | corrida de 5 pisadas, pisada 1, RMS 219.9 N, completada |
| 20261118_175820_..._p2.csv | 17:58 | pisada 2, ABORTADA a 0.50 s: hueco de 82 ms en el lazo → salto 425→522 N > umbral 69 N |
| log_interfaz_noche.log | 17:49–18:00 | log completo del lanzador (HOME, preparación, pisadas, comandos serie) |

Figura: `reportes/figuras/2026-11-18_noche_pisadas_3ejes.png` (generada con `herramientas/graficar_pisadas_interfaz.py`).
Reporte: `reportes/2026-11-18_noche_cable_nuevo_home_e_interfaz_vigente.md`.
