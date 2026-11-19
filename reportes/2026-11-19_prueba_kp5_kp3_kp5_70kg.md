# Prueba Kp 5 → Kp 3 → Kp 5, 70 kg x10, solo Y cerrado (2026-11-19, 10:39–10:45)
## Objetivo
Separar si la oscilación de Fz a 6–8 Hz (escalera del 11-18) es resonancia externa al lazo o la crea el lazo, cambiando solo Kp (protocolo `2026-11-19_protocolo_proxima_sesion_rpi.md`, paso 2).
## Metodología
`control/lazo_fz_tiempo_real.py`, 686.7 N (pico 809), tope 1011 N, 10 pisadas, apoyo 6.15 s, v_max 9000, extra 46 mm, pie plano 0° (por pasos), prótesis montada, `--sin_filtro_60hz`, Fz por UART. Antes: X retrocedido 3 cm (MANUAL:0:−1200, pedido de Luis, centrar el pie en la plataforma). Hueco declarado por Luis 40 mm; contacto real a 32.6 / 33.0 / ~31 mm. Luis autorizó cada corrida. Métrica: RMS 5–10 Hz de e = r_corregida − F_med, pisadas 6–10 (`espectro_corrida.py`, usa `t_real`).
## Resultado
| corrida | Kp | f_pico | RMS e 5–10 Hz | RMS error total pisada 10 |
|---|---|---|---|---|
| 103942 | 5 | 4.69 Hz | 4.50 N | 20.7 N |
| 104134 | 3 | 3.58 Hz | 1.40 N | 24.7 N |
| 104323 | 5 | 4.69 Hz | 4.53 N | 20.7 N |
- Las dos corridas Kp 5 coinciden (4.50 vs 4.53 N): no hay deriva, la comparación es válida.
- Kp 3 baja la amplitud a 0.31× (tabla: < 0.5) y la frecuencia cambia 1.11 Hz (> 2× resolución 0.25 Hz): **no es resonancia externa; la amplitud depende de la ganancia del lazo**, coherente con "modo dentro del lazo con poco margen" (5d). No distingue entre ese caso y "la crea el polo del lazo con el retardo".
- Con Kp 3 el error total no mejora (24.7 vs 20.7 N): más lento, como se esperaba.
- Frecuencias reales: con `t_real` el pico a Kp 5 es 4.7 Hz, no 6–8 (los CSV del 11-18 usan tiempo nominal, ×1.35; 6.35/1.35 = 4.7 coincide con la corrida de 70 kg Kp 5 del 11-18).
## Limitaciones
Una carga, una prótesis, 1 corrida por Kp; el pico de Kp 3 (3.58 Hz) está cerca del borde de la banda 3–15 Hz; no se midió la rigidez real a carga alta ni se probó el notch; error total ≈20 N (≈2.5 % del pico) no ha bajado con las pisadas tanto como en simulación. Incidente previo: `medir_hueco.py --help` movió Y <0.5 s (ver CLAUDE/memoria).
## Fuentes
`control/telemetria/registros/2026-11-19_{103942,104134,104323}_fz.csv` (copia en `reportes/datos/2026-11-19_kp3_vs_kp5_70kg/`), `reportes/figuras/2026-11-19_espectro_kp5_kp3_kp5_70kg.png`, `reportes/2026-11-19_causa_oscilacion_6_8hz_y_mejoras.md`.
