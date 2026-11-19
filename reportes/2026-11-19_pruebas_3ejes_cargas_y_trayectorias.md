# Pruebas 3 ejes desde la interfaz: 40–80 kg y dos trayectorias (2026-11-19, 11:12–11:39)
## Objetivo
Medir con la interfaz vigente (Y lazo cerrado de Fz; X y ángulo en lazo abierto con la trayectoria) cómo cambian RMSE y correlación con la carga, el número de pisadas y la trayectoria, y localizar DÓNDE está el error que queda para saber qué mejorar.
## Metodología
Tras HOME sin prótesis (11:08–11:09, OK de Luis) y prótesis montada, Claude mandó por el canal del lanzador: `fz Control_apoyo_talla170_montaje37` 40, 60, 75 kg (5 pisadas) y 80 kg (10); luego `preparar Control_apoyo_talla174_montaje37` (contacto 27 N, 43 mm abajo) y 80 kg (6 pisadas). x10, Kp programado (8 hasta 60 kg, 5 desde 70), v_max 9000, tara/contacto automáticos. Análisis: `herramientas/analizar_pisadas_interfaz.py` (RMSE, Pearson r, RMSE por fase del apoyo; velocidad y desplazamiento de Y = ORDENADOS por el contador, no medidos).
## Resultado (última pisada de cada serie)
| serie | pisadas | RMSE [N] | % pico | r | RMSE 0–10 % | 70–90 % | 90–100 % |
|---|---|---|---|---|---|---|---|
| 40 kg talla170 | 5 | 17.2 | 3.7 | 0.988 | 44.4 | 10.9 | 11.5 |
| 60 kg talla170 | 5 | 22.5 | 3.2 | 0.991 | 61.3 | 15.0 | 16.2 |
| 75 kg talla170 | 5 | 34.3 | 4.0 | 0.986 | 84.6 | 22.0 | 40.6 |
| 80 kg talla170 | 10 | 33.4 | 3.6 | 0.988 | 85.2 | 25.3 | 25.2 |
| 80 kg talla174 | 6 | 32.8 | 3.5 | 0.989 | 82.4 | 21.2 | 35.3 |
- 31/31 pisadas completas, 0 abortos, 0 cortes USB. El ILC aprende en todas las series (pisada 1 ≈ 8.7–10 % → 3.2–4.0 %).
- A 80 kg el RMSE se estabiliza desde la pisada 6 (3.6–3.7 %): es el piso del controlador actual.
- La trayectoria (talla 170 vs 174) casi no cambia el resultado (3.6 vs 3.5 %).
- **El error que queda está en la carga inicial (0–10 % del apoyo, 82–85 N a 80 kg, no baja con las pisadas):** Fz llega tarde (+140 N a t≈0.2 s) y luego sobrepasa (≈−110 N a t≈0.4–0.5 s); el sobrepaso CRECE con las pisadas. Segundo: la descarga final (90–100 %), Fz por encima del objetivo (baja con las pisadas). La velocidad ordenada máx. ≈65 mm/s, lejos del techo de 112: no es saturación.
## Dónde mejorar (propuesta, no aplicada)
1. Anticipación (feedforward) de la rampa de carga: v_ff = −(dr*/dt)/k(F) en pasos/s, sumada al P: ataca el atraso de 0–10 %.
2. ILC con adelanto m ≈ retardo efectivo del lazo (20–30 ms; hoy m = 0): evita que el ILC agrande el sobrepaso.
3. Probarlo primero en el script (solo Y, sin HOME) y después en la interfaz (requiere reiniciarla = perder HOME).
## Limitaciones
Una prótesis (pie_pasivo_1), una escala (x10; pisada 6.0 s), 1 serie por condición; Fz sin validar contra NetForce con pesas (R6); desplazamiento ordenado, no medido; la gráfica en vivo de la interfaz aún no se exporta sola (el cambio está hecho pero la app corre con el código anterior).
## Fuentes
`reportes/datos/2026-11-19_pisadas_3ejes_interfaz_{40kg,60kg,75kg,80kg,80kg_talla174}/`, `reportes/figuras/2026-11-19_analisis_*` (por serie: `_pisadas.png` con Fz/referencia, error, velocidad y desplazamiento de Y; `_metricas.csv`; `2026-11-19_analisis_todas_resumen.png`), `logs/interfaz_20261119_*.log`.
