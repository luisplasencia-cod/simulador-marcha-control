# Figuras antiguas (11-05 a 11-18) con versión clara

Las versiones `_claro.png` están junto a la original (las originales no se tocaron). Las genera `herramientas/figuras_claras_antiguas.py` desde los CSV del repo.
Glosario: **ordenado** = lo que se le pidió al motor (no hay sensor que mida el desplazamiento real); **medido** = lo que leyó el sensor de fuerza. **ILC** = el lazo aprende el error de una pisada y lo corrige en la siguiente. **Kp** (ganancia) = cuánta velocidad se ordena por cada newton de error. **k** = rigidez: newtons por cada mm que baja el eje (mayor = pie más rígido). Ángulo + = talón abajo, − = punta abajo.

| figura (versión clara) | qué muestra | cómo leerla | fecha de la prueba |
|---|---|---|---|
| `2026-11-05_ensayo_A_plana_0deg_k23.0_completa_claro.png` | Pie plano: fuerza vs tiempo y vs descenso del eje (Ensayo A, corrida completa) | La fuerza aparece al tocar (≈213 mm); azul = bajada, rojo = subida; la separación es la histéresis | 2026-11-05 |
| `..._plana_0deg_k23.2_claro.png` | Pie plano, corrida parcial (se cortó el USB a 112 N) | Solo bajada; no completa | 2026-11-05 |
| `..._talon_11.14deg_k26.4_claro.png` | Pie apoyado en el talón | Igual que la anterior | 2026-11-05 |
| `..._punta_-37.3deg_k2.4_completa_claro.png` | Pie apoyado en la punta (pasos de 2 mm) | Pendiente mucho menor: pie ≈11 veces más blando | 2026-11-05 |
| `..._5deg_parcial_k28_claro.png` | Pie a ≈5° (a ojo), corrida parcial | Solo bajada | 2026-11-05 |
| `..._comparacion_k_talon_plana_claro.png` | Curvas fuerza-compresión y k: talón vs plano | Más empinada = más rígido; barras = k | 2026-11-05 |
| `..._comparacion_k_3condiciones_claro.png` | Lo mismo con talón, plano y punta | Idem | 2026-11-05 |
| `2026-11-10_fuerza_vs_velocidad_y_aire_claro.png` | Fz leída sin tocar nada mientras el eje vertical se mueve | Debería ser 0 N; los cambios de hasta ~40 N muestran que el movimiento perturba la medida | 2026-11-10 |
| `control/identificacion/resultados/ensayoB_ang0_20261118_114209_claro.png` | Respuesta de Fz a pulsos cortos del eje con contacto (Ensayo B) | Línea roja = orden; la fuerza empieza a subir ≈15–23 ms después | 2026-11-18 |
| `reportes/escalera/20261118_124639/resumen_claro.png` | Subir de 10 a 50 kg: error, velocidad, compresión y rigidez por escalón | La X roja = corrida abortada (50 kg) | 2026-11-18 |
| `2026-11-18_noche_pisadas_3ejes_claro.png` | Pisadas con los 3 ejes desde la interfaz (75 kg, 10 veces más lento) | Continua = Fz medida, discontinua = objetivo; la pisada 2 se abortó por un hueco de 82 ms del lazo | 2026-11-18 |

## Sin versión clara (falta el dato, la figura original queda sin tocar)
Los CSV de telemetría están ignorados por git y no están en el repo: `2026-11-18_primer_lazo_cerrado_fz`, `..._lazo_8_ciclos`, `..._corrida2_tres_M`, `..._escalera_{10kg…50kg, x6, 6pisadas, abortada}` (por kg), `..._escalera_resumen_10-50kg` (la versión desde `resumen.csv` sí existe, arriba), `reportes/escalera/20261118_rpi/reporte_final/comparacion_grf.png`. Para regenerarlas hay que traer los CSV de la RPi (`control/telemetria/registros/`).
También sin tocar: `2026-11-05_comparacion_k_talon_plana_parcial.png` (no se sabe con seguridad qué corridas parciales usó) y los `ensayo_A_ang*.png` / `RAW_corrida3_*.png` de `control/identificacion/resultados/` (son el visor en vivo de cada intento; las versiones claras de las corridas principales están arriba).
