# Figuras del 2026-11-19 en versión clara (`*_claro.png`)

Regeneradas con `herramientas/figuras_claras_2026-11-19.py` a partir de los CSV ya guardados en `reportes/datos/` (sin hardware). Las originales siguen al lado, sin cambios.
Convención: continua = fuerza medida, rayada = objetivo. Error = objetivo − medida (positivo = falta fuerza). Eje vertical "ordenado" = lo mandado al motor (contador), no medido por sensor.

| Figura | Qué muestra | Cómo leerla |
|---|---|---|
| `2026-11-19_mejora_ff_ilc_80kg_20261119_114846_pisadas_claro.png` | 80 kg, con anticipación + adelanto del ILC: 8 pisadas, solo eje vertical | Las 8 curvas de fuerza casi se superponen al objetivo; el error de la pisada 1 (oscura) es el mayor |
| `2026-11-19_mejora_ff_ilc_80kg_20261119_114714_pisadas_claro.png` | Lo mismo, sin mejora (ILC base) | Comparar con la anterior: aquí el error al inicio y al final tarda más pisadas en bajar |
| `2026-11-19_mejora_ff_ilc_80kg_resumen_claro.png` | Sin mejora vs con anticipación + adelanto del ILC | Menor error y correlación más cercana a 1 = mejor; la naranja gana desde la pisada 1 |
| `2026-11-19_analisis_todas_resumen_claro.png` | 40, 60, 75 y 80 kg (talla 170) y 80 kg talla 174, 3 ejes | Izq.: error por pisada; centro: parecido de forma; der.: en qué fase del apoyo falla (más en 0–10 % y 90–100 %) |
| `2026-11-19_pisadas_3ejes_40kg_claro.png` | 40 kg, talla 170, 5 pisadas, 3 ejes | Paneles: fuerza, error, corrección que suma el ILC y tiempo entre muestras del lazo |
| `2026-11-19_espectro_kp5_kp3_kp5_70kg_claro.png` | 70 kg, Kp 5 (alta) vs Kp 3 (baja): ¿cambia la oscilación de 5–10 Hz? | Izq.: frecuencias del error (zona gris = banda sospechosa); der.: tamaño de esa oscilación por pisada |
| `2026-11-19_analisis_{40kg,60kg,75kg,80kg,80kg_talla174}_resumen_claro.png` | Resumen de cada carga por separado | Igual que el resumen conjunto, una sola serie |
| `2026-11-19_analisis_{40kg,60kg,75kg,80kg,80kg_talla174}_<serie>_pisadas_claro.png` y `2026-11-19_analisis_todas_<serie>_pisadas_claro.png` | Pisadas de esa carga/talla: fuerza, error, velocidad y desplazamiento ordenados al eje vertical | Pisada 1 (oscura) a la última (clara): el error de las claras es menor (el ILC aprende) |
| `2026-11-19_analisis_delta_ilc_interfaz_claro.png` | Por qué la corrección del ILC de la interfaz arranca grande | Arriba: el lazo dura 8,27 s y el ILC supone 6 s; abajo: la corrección con tiempo real (azul) difiere de la ideal (naranja) |

Pendiente de aclarar: `2026-11-19_sim_k_desconocida.png` y `2026-11-19_notch_fz_bode.png` no se rehicieron (simulaciones, no estaban en la lista pedida).
