# Escalera de carga 10 → 50 kg (x6, solo Y, pie plano 0°) y escala de tiempo para 80–90 kg — 2026-11-18

## Objetivo
Subir la carga del lazo de Fz en Y de a poco para encontrar el límite (velocidad, compresión, tope o lo que falle), con visor en vivo en la pantalla del RPi y todo registrado (pedido de Luis).

## Metodología
`control/escalera_carga.py` (10, 20, … 90 kg; 6 pisadas por peso; se detiene al primer aborto): una corrida del lazo validado por peso (Kp 10, Fz por UART, k asumido 26.4 N/mm, `--extra_mm 60`, tope de fuerza = 1.25 × pico, v_max 9000 pasos/s), como subproceso. Visor en vivo (`herramientas/visor_pruebas.py`): Fz, desplazamiento ORDENADO de Y y fase. Lanzada 12:46:38 con OK de Luis (NetForce en cero, paro a mano). Datos: `reportes/escalera/20261118_124639/` (CSV, salida y PNG por peso + `resumen.md/.csv/.png`); logs en `control/telemetria/registros/2026-11-18_1246*_fz.csv … 125043_fz.csv` (columnas nuevas `y_mm`, `v_mm_s`); copias de las figuras en `reportes/figuras/2026-11-18_escalera_*`.

## Resultado (medido)
| kg | pico obj. N | RMS 1.ª → última (% del pico) | F máx N | v máx Y mm/s | compresión mm | rigidez aparente N/mm | resultado |
|---|---|---|---|---|---|---|---|
| 10 | 116 | 11.7 → 4.7 N (4.0 %) | 119 | 17.3 | 7.2 | 13.8 | completado |
| 20 | 231 | 21.8 → 7.1 (3.1 %) | 235 | 32.9 | 13.3 | 16.2 | completado |
| 30 | 347 | 30.4 → 9.8 (2.8 %) | 352 | 43.2 | 18.0 | 18.5 | completado |
| 40 | 462 | 39.2 → 14.2 (3.1 %) | 471 | 56.8 | 23.0 | 19.5 | completado |
| 50 | 578 | 68.9 (11.9 %, 1 pisada parcial) | 584 | 72.4 | 25.9 | 21.8 | **ABORTADO** a t = 1.09 s de la pisada 0 |
- Del 10 al 40 kg: error final 3–4 % del pico, sin saturar la velocidad, picos dentro de ±2 % del objetivo, Y vuelve a su inicio en todas, NetForce "se ha visto bien" (Luis, sin valores). La velocidad de Y crece ≈ lineal con la carga (1.42–1.73 mm/s por kg a x6); la rigidez aparente sube con la carga (14 → 22 N/mm; es compresión ORDENADA, no medida).
- **Aborto en 50 kg:** `lectura anomala (F=529.8 N, previa 569.0 N)` = |ΔF| de 39 N entre bloques > el umbral fijo de 30 N. **No fue un límite físico:** (1) el umbral de 30 N venía calibrado con ≈60 N de carga; el ruido entre bloques crece con la fuerza (|ΔF| p99 = 6.7 / 9.2 / 15.4 N a 10 / 20 / 40 kg; máx 16 / 16 / 22 N); (2) la caída máxima que el movimiento ordenado puede producir en 10 ms (≈ k·v·dt = 22 N/mm × 23 mm/s × 10 ms ≈ 5 N; 16 N a la velocidad máxima del tramo) es mucho menor que 39 N → fue un pico de ruido/lectura o un transitorio mecánico, **no distinguibles con estos datos**. En el log la fuerza oscila alrededor de la referencia en t≈1.0–1.1 s (Fz de 499 a 584 N en 50 ms mientras la velocidad ordenada cambia de −12 a +26 mm/s): con k más alta a esta carga (aparente 22 vs 26.4 asumido, razón 0.83 frente a 0.52 a 10 kg) la ganancia efectiva del lazo es mayor y el margen menor (hipótesis, no verificada). Protecciones actuaron como se diseñó: el lazo se detuvo, Y subió y volvió a su inicio.
- **Corrección hecha:** el umbral de salto ahora escala con la carga: `max(30 N, 8 % × 1.178 × peso)` (50 kg: 46 N; 80 kg: 74 N; 90 kg: 83 N). Elección de diseño, NO medida.

## Escala de tiempo necesaria para 80–90 kg (cálculo, extrapolación)
La velocidad de Y necesaria es ∝ 1/escala. Con la tendencia medida a x6 (≈1.45 mm/s por kg) la carga de 80 kg exigiría ≈116 mm/s y la de 90 kg ≈130 mm/s, por encima del techo de trabajo de 112 mm/s (12 000 pasos/s = 150 mm/s se notó brusco, Luis). Escala y duración de apoyo para quedar dentro de una velocidad objetivo:
| kg | v a x6 | ≤ 57 mm/s (máx. validada) | ≤ 80 mm/s | ≤ 112 mm/s (techo) |
|---|---|---|---|---|
| 60 | 87 | x9.2 (5.6 s) | x6.5 (4.0 s) | x4.7 |
| 70 | 102 | x10.7 (6.6 s) | x7.6 (4.7 s) | x5.4 |
| 80 | 116 | **x12.2 (7.5 s)** | x8.7 (5.4 s) | x6.2 |
| 90 | 130 | **x13.7 (8.4 s)** | x9.8 (6.0 s) | x7.0 |
**Propuesta:** 60–70 kg a x6 se pueden intentar (87–102 mm/s, bajo el techo pero por encima de lo validado); para **80 y 90 kg usar x12 (apoyo 7.4 s) y x14 (8.6 s)**, que mantienen la velocidad en lo ya validado (≈57 mm/s). Implementado: `--duracion_apoyo_s` en el lazo y `--escala` en `escalera_carga.py`.
**Limitaciones del cálculo:** extrapola una tendencia medida solo hasta 40 kg (50 kg parcial); la rigidez a 60–90 kg no está medida (si sube más, hace falta menos velocidad); no incluye la dinámica del lazo (margen de fase) a carga alta; el significado de una escala mayor (apoyo más lento que el equivalente a x6 acordado) lo decide Luis.
