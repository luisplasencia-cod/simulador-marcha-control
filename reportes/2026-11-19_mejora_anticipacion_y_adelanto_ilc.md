# Anticipación de la rampa + adelanto del ILC: RMSE 2.1 → 1.2 % a 80 kg (2026-11-19, 11:47–11:50)
## Objetivo
Bajar el error de la carga inicial (0–10 % del apoyo), que era el piso del controlador en las pruebas de 3 ejes (`reportes/2026-11-19_pruebas_3ejes_cargas_y_trayectorias.md`).
## Metodología
`control/lazo_fz_tiempo_real.py` (solo Y, pie plano 0° acomodado por Luis tras el incidente de K, prótesis montada, 80 kg x10, Kp 5 programado, 8 pisadas, hueco declarado 30 mm, contacto real 35.7 mm, sin filtro 60 Hz). A = base; B = `--ff 0.7` (u += −0.7·(dr*/dt)·80/k(r*), dr*/dt pasado a tiempo real con el periodo medido) + `--ilc_adelanto_ms 30` (m = 1 punto de la malla del ILC). Análisis con `herramientas/analizar_pisadas_interfaz.py`.
## Resultado (pisadas 6–8)
| | RMSE | % pico | r | RMSE 0–10 % | 10–30 % | 90–100 % |
|---|---|---|---|---|---|---|
| A base | 19.6 N | 2.1 % | 0.996 | 49 N | 14 N | 21 N |
| **B mejora** | **11.4 N** | **1.2 %** | **0.999** | **20 N** | **10 N** | **12 N** |
- Pisada 1: 75.7 → 25.3 N (la anticipación funciona desde el primer ciclo, sin aprender).
- Converge en 3 pisadas (B: 10.6 N en la 3.ª); queda un sesgo de ≈+14 N en 70–90 % (Fz algo por debajo en el 2.º pico).
- Llevado a la interfaz (`src/fz/fz_loop.py`, defecto de la pantalla ff 0.7 / 30 ms, commit local `84b2413` en `~/Projects/gaitsim-control` main, sin push); simulación de la interfaz con ff: 3.56 → 1.86 N, pruebas b5/b6 TODO OK.
## Limitaciones
1 corrida por condición, 1 prótesis, 1 pose (plana), solo Y; **el script indexa la referencia por muestra → su pisada dura 8.1 s, la interfaz (tiempo real) 6.0 s: la rampa es 1.35× más rápida en la interfaz y la mejora NO está probada allí en hardware**; k(F) de la tabla medida solo en plano (en talón 11° el pie es mucho más blando: 400 N tras 60 mm, ver incidente); ff y m elegidos, no barridos.
## Fuentes
`reportes/datos/2026-11-19_mejora_ff_ilc_80kg/{A_base,B_ff07_m30}/`, `reportes/figuras/2026-11-19_mejora_ff_ilc_80kg_*`, `pruebas/resultados/{A_base,B_ff07_m30}_80kg_*.txt`.
