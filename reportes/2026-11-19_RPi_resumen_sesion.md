# Resumen de la sesión en la RPi — 2026-11-19 (10:30–11:55)
Lazo cerrado de Fz en el eje vertical (Y) con X y ángulo (K) en lazo abierto. Cada tema tiene su reporte con Objetivo → Metodología → Resultado → Limitaciones → Fuentes; aquí el hilo y las figuras para presentar.

## Resultado principal
**A 80 kg (x10, solo Y, pie plano): RMSE 1.2 % del pico, correlación r = 0.999** (base del día: 2.1 %, r 0.996; inicio del día en 3 ejes desde la interfaz: 3.6 %, r 0.988). El ILC ahora aprende en la interfaz (antes no).

## Línea de tiempo
| hora | qué | resultado | reporte |
|---|---|---|---|
| 10:34 | Preflight, PING, filtro 60 Hz con ADC real | PING 200/200 5.98 ms; σ 2.63 → 0.24 N | — |
| 10:39–10:45 | Kp 5 → 3 → 5 a 70 kg (solo Y) | la oscilación depende de Kp (no es resonancia externa); f real 4.7 Hz | `2026-11-19_prueba_kp5_kp3_kp5_70kg.md` |
| 10:47–10:59 | Rigidez vs carga + Kp programado (60/70/80/90 kg) | k 18 → 58 N/mm; oscilación 3–10× menor sin perder seguimiento | `2026-11-19_ganancia_programada_k_vs_carga.md` |
| 11:00–11:07 | Interfaz: Kp programado, detector de saltos ∝ Δt, referencia por tiempo real (el ILC no aprendía) | simulación OK | `2026-11-19_analisis_delta_ilc_interfaz.md` |
| 11:08–11:09 | HOME sin prótesis (OK de Luis) | OK, 89 s | — |
| 11:12–11:39 | 3 ejes desde la interfaz: 40/60/75/80 kg, tallas 170/174 | 31/31 pisadas, 0 abortos; 80 kg 3.6 %, r 0.988; error en carga inicial | `2026-11-19_pisadas_3ejes_interfaz_40kg.md`, `2026-11-19_pruebas_3ejes_cargas_y_trayectorias.md` |
| 11:18 | Diagrama de bloques/ecuaciones/notación alineados con el lazo real | — | `control/diagramas/salida/` |
| 11:47–11:50 | Anticipación de rampa + adelanto ILC (solo Y, 80 kg) | **RMSE 2.1 → 1.2 %, r 0.996 → 0.999** | `2026-11-19_mejora_anticipacion_y_adelanto_ilc.md` |

## Figuras para presentar
- `reportes/figuras/2026-11-19_mejora_ff_ilc_80kg_20261119_114846_pisadas.png` — mejor resultado: Fz vs objetivo, error, velocidad y desplazamiento de Y.
- `reportes/figuras/2026-11-19_mejora_ff_ilc_80kg_resumen.png` — A vs B: RMSE y r por pisada, RMSE por fase.
- `reportes/figuras/2026-11-19_analisis_todas_resumen.png` — 3 ejes, todas las cargas.
- `reportes/figuras/2026-11-19_analisis_80kg_20261119_113006_pisadas.png` — 3 ejes, 80 kg, 10 pisadas.
- `reportes/figuras/2026-11-19_pisadas_3ejes_40kg.png`, `reportes/figuras/2026-11-19_espectro_kp5_kp3_kp5_70kg.png`.
- `control/diagramas/salida/diagrama.png`, `ecuaciones.png`, `leyenda_variables.png` — lazo real.

## Incidentes (errores míos, documentados)
1. 10:35 `interfaz/tools/medir_hueco.py --help` ignoró el flag y bajó Y <0.5 s (≤3 mm, sin contacto). Regla: no ejecutar scripts de hardware para ver flags.
2. 11:45 giré K −1233 pasos suponiendo el signo de una nota del 11-10: fue hacia el talón y llegó al final de carrera (contador −5012, mín. −5000); Luis indicó que físicamente no giró (bloqueado por el final de carrera); se devolvió el contador (+868) y Luis acomodó el pie a 0° a mano. Regla: tras HOME el signo de K no es el de las notas; giro chico con Luis mirando.
3. Prueba en talón (11.1°): 2 abortos seguros por límite de descenso (a 11° el pie dio solo 400 N tras 60 mm: mucho más blando que en plano).
Dato: al abrir el puerto a las 11:45 el ESP32 NO se reinició (contador conservado), a diferencia de días previos: causa no investigada.

## Pendiente (en orden)
1. **Validar en la interfaz, con hardware, la mejora (ff 0.7 + adelanto 30 ms)** con 3 ejes (requiere HOME sin prótesis): la pisada allí dura 6.0 s (script 8.1 s) → rampa 1.35× más rápida.
2. Tabla k(F) por ángulo: en talón el pie es mucho más blando; la ganancia programada y la anticipación usan k(F) de plano.
3. R6: calibración con pesas vs NetForce (la escala en N de la ruta UART no está validada).
4. Diagnóstico eléctrico del 60 Hz con Luis (tomas/tierra).
5. Hacer que el script use la misma base de tiempo real que la interfaz.
6. ✅ Interfaz subida a GitHub (GAITSIM main `0110a13`: mejoras `84b2413` + taras del día). Solo queda sin seguimiento `data/positions/inicio.json` (no se subió).
7. Umbral de error para pasar a Fy (< __ %BW): lo fija Luis; los resultados de hoy (1.2 % solo Y, 3.6 % 3 ejes antes de la mejora) sirven de base.
