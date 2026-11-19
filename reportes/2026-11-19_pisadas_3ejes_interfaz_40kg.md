# Primeras pisadas con 3 ejes desde la interfaz con los arreglos del 2026-11-19 (40 kg, x10)
## Objetivo
Comprobar en hardware, tras HOME, que el lazo de Fz en Y (X y ángulo en lazo abierto) completa pisadas seguidas y que el ILC aprende, después de: Kp programado, detector de saltos por tiempo real y referencia por tiempo real (reportes/2026-11-19_ganancia_programada_k_vs_carga.md, reportes/2026-11-19_analisis_delta_ilc_interfaz.md).
## Metodología
HOME sin prótesis (OK de Luis, 11:08:12; terminó 11:09:41, `READY:24556:42670:-5000:5544`). Luis montó la prótesis y aceptó el flujo de la pantalla (trayectoria `Control_apoyo_talla170_montaje37`, tara automática: contacto 11:12:23, punto de partida 10 mm arriba y 1 cm atrás). Claude envió `fz ... 40 10 5` por el canal de comandos del lanzador. Pico objetivo 462 N (40 kg), Kp 8 programado. Datos: `reportes/datos/2026-11-19_pisadas_3ejes_interfaz_40kg/`.
## Resultado
| pisada | RMS del ILC | % del pico | RMS fila a fila r−F | F máx | periodo lazo medio / máx |
|---|---|---|---|---|---|
| 1 | 35.4 N | 7.7 % | 30.7 N | 463 | 13.9 / 25 ms |
| 2 | 27.1 | 5.9 | 23.8 | 457 | 13.7 / 24 |
| 3 | 22.3 | 4.8 | 19.8 | 455 | 13.7 / 47 |
| 4 | 20.0 | 4.3 | 17.8 | 453 | 13.6 / 21 |
| 5 | 18.8 | 4.1 | 17.2 | 458 | 13.8 / 28 |
- 5 pisadas completas sin abortos; el ILC baja el error pisada a pisada (por primera vez en la interfaz; el 11-18 noche no aprendió y la pisada 2 abortó).
- La duración de cada pisada es 6.00–6.01 s (antes ≈8.3 s con la referencia por índice): arreglo de la base de tiempo confirmado. El RMS del ILC ahora coincide con el r−F fila a fila (18.8 vs 17.2 N).
- Máximo hueco del lazo 47 ms (antes 82 ms); sin aborto por saltos.
- Error restante concentrado en la carga inicial (0–0.6 s: +100 → −60 N) y baja en 4–5 s (≈−10 N). El periodo del lazo sigue ≈13.7 ms (no 10).
## Limitaciones
Una sola carga (40 kg), una prótesis, un ángulo/trayectoria; 5 pisadas no prueban convergencia total; X y ángulo en lazo abierto, Fz sin validar contra NetForce (R6); no se comparó contra el sensor de posición (ordenada, no medida); Kp programado calibrado con la prótesis plana a 0°, aquí el pie pasa por ángulos distintos (k cambia por ángulo, Ensayo A); causa de los 13.7 ms no verificada. Cambios de la interfaz sin commit.
## Fuentes
`reportes/datos/2026-11-19_pisadas_3ejes_interfaz_40kg/`, `reportes/figuras/2026-11-19_pisadas_3ejes_40kg.png`, `logs/interfaz_*.log` del 11-19 11:08.
