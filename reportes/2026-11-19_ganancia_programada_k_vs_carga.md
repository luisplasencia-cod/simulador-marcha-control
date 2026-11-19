# Rigidez dinamica vs carga y ganancia programada del lazo de Fz (2026-11-19, 10:40-10:55)
## Objetivo
Comprobar si la oscilacion del lazo viene de que la protesis se endurece con la carga (ganancia real del lazo > la disenada) y, si es asi, corregirla con Kp programado, probandolo con la protesis montada (solo Y) antes del HOME.
## Metodologia
1) k dinamica = dF/d(descenso ordenado) en ventanas de 150 ms con >=1.5 mm de recorrido, mediana por bin de fuerza, pisadas >=3, de los CSV de hoy y de la escalera del 11-18. 2) `--kp_programado` en `control/lazo_fz_tiempo_real.py`: Kp_ef = Kp*min(1, k_asumido(26.4)/k(F)), k(F) interpolada de la tabla medida (100 N:19.5, 300:34.5, 500:48, 700:54 N/mm, constante sobre 700). 3) Misma condicion que la prueba A-B-A (X -3 cm, pie plano, hueco 40 mm, apoyo 6.15 s, Kp 5, sin filtro 60 Hz), Luis autorizo.
## Resultado
- k dinamica sube con la carga: <200 N 18-21; 200-400 N 25-35; 400-600 N 35-49; 600-800 N 40-58 N/mm (hoy mas alta que el 11-18). A 600-800 N es ~2x el k de diseno (26.4), no los 67-88 N/mm de la simulacion.
- 70 kg: Kp5 fijo RMS 5-10 Hz 4.50 / 4.53 N; Kp3 1.40 N (error total pisada 10: 24.7 N); **Kp5 programado 1.43 N con error total 20.8 N** (= Kp5 fijo 20.7 N).
- 90 kg: **Kp5 programado 1.59 N, error total 25.0 N, completo sin abortar** (Kp5 fijo del 11-18: 16.05 N).
- 60 kg (Kp 8 programado, el Kp que propone la pantalla): RMS 5-10 Hz 1.86 N, error total 14.3 N, completo (Kp 8 fijo del 11-18: 13.52 N).
- Portado a la interfaz (`~/Projects/gaitsim-control` main, `src/fz/fz_loop.py` + `fz_control_screen.py`, SIN commit, simulacion `manual_test_fz_loop_sim.py` TODO OK; la pantalla lo activa siempre).
- La oscilacion se reduce ~3x (70 kg) y ~10x (90 kg) sin perder seguimiento. Tiempo real: pico 3.3 Hz (no 6-8: los CSV viejos usan tiempo nominal).
## Limitaciones
Tabla medida solo para pie_pasivo_1, plana 0 deg, X ~ -3 cm; descenso ordenado (no medido por sensor); k a >800 N casi sin datos (se mantiene constante); 1 corrida por condicion; comparacion con el 11-18 a 90 kg cruza dias y X distinto (la repeticion de 70 kg Kp5 coincide: 4.5 vs 3.9 N); sin segunda protesis ni otros angulos (k cambia por angulo, Ensayo A); el valor de ~3.3 Hz esta cerca del borde de la banda de pico. NO esta aun en la interfaz (`interfaz/src/fz/`).
## Fuentes
CSV en `reportes/datos/2026-11-19_kp3_vs_kp5_70kg/`; `reportes/2026-11-19_prueba_kp5_kp3_kp5_70kg.md`; `reportes/2026-11-19_causa_oscilacion_6_8hz_y_mejoras.md` (mejora 5a).
