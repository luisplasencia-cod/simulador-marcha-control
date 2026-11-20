# Figuras del 2026-11-19 listas para presentar (`*_claro.png`)

Cada figura lleva título con la prueba y su condición, una "lectura clave" en una frase, ejes con unidad, leyenda en lenguaje común y una nota al pie con las abreviaturas. Las originales siguen al lado, sin cambios.
Generadores: `herramientas/figuras_claras_2026-11-19.py` (desde `reportes/datos/`, sin hardware) y, para las simulaciones, `control/simulacion/sim_k_desconocida.py`, `oscilacion_causa_2026-11-19.py --figura`, `analisis_resonancia_2026-11-19.py` y `control/filtro_fz/analisis_notch_fz.py`.
Convención: continua gruesa = fuerza medida; rayada fina = objetivo. Error = objetivo − medida (positivo = falta fuerza). Eje vertical "ordenado" = lo mandado al motor (contado, no medido). **RMSE y r se calculan sobre toda la curva de Fz de la pisada, no solo en los picos** (decisión de Luis 2026-11-20).
**Glosario:** RMSE = error cuadrático medio (N); r = correlación de forma (1 = idéntica); ILC = aprendizaje pisada a pisada; Kp = ganancia del lazo; pisada = un apoyo del pie.

## Mediciones (hardware)
| Figura | Qué prueba | Cómo leerla | Lectura clave |
|---|---|---|---|
| `2026-11-19_pisadas_3ejes_40kg_claro.png` | 40 kg, talla 170, x10, 5 pisadas, 3 ejes | 4 paneles: fuerza, error, corrección del ILC, tiempo entre muestras | RMSE 31 N (pisada 1) → 17 N (pisada 5) |
| `2026-11-19_analisis_{40kg,60kg,75kg,80kg,80kg_talla174}_<serie>_pisadas_claro.png` y `..._todas_<serie>_pisadas_claro.png` (misma figura por carga; 10 archivos) | Pisadas de cada carga/talla: fuerza, error, velocidad y desplazamiento ordenados | Pisada 1 (oscura) a la última (clara) | El error baja pisada a pisada (p. ej. 75 kg: 77 → 34 N) |
| `2026-11-19_analisis_{40kg,60kg,75kg,80kg,80kg_talla174}_resumen_claro.png` | Resumen de una carga | RMSE, r y error por fase del apoyo | La lectura clave de cada una trae su RMSE inicial → final |
| `2026-11-19_analisis_todas_resumen_claro.png` | 40, 60, 75, 80 kg (talla 170) y 80 kg talla 174 | Izq.: RMSE por pisada; centro: r; der.: error por fase | Última pisada entre 17 y 34 N; falla más en 0–10 % y 90–100 % del apoyo |
| `2026-11-19_mejora_ff_ilc_80kg_20261119_114714_pisadas_claro.png` | 80 kg, solo eje vertical, sin mejora (ILC base) | 4 paneles de pisadas | RMSE baja de 76 a 20 N |
| `2026-11-19_mejora_ff_ilc_80kg_20261119_114846_pisadas_claro.png` | 80 kg con anticipación + adelanto del ILC | Igual | RMSE baja de 25 a 12 N |
| `2026-11-19_mejora_ff_ilc_80kg_resumen_claro.png` | Sin mejora vs con mejora | Naranja = con mejora | Con mejora el error es menor y r ≈ 0,999 desde la pisada 2 |
| `2026-11-19_espectro_kp5_kp3_kp5_70kg_claro.png` | 70 kg, x10, 10 pisadas: Kp 5 vs Kp 3 | Izq.: frecuencias del error (gris = banda 5–10 Hz); der.: oscilación por pisada | Kp 3: ≈1,4 N rms; Kp 5: ≈4,2 N rms |
| `2026-11-19_analisis_delta_ilc_interfaz_claro.png` | Por qué el ILC de la interfaz arranca con una corrección grande | Arriba: el apoyo real dura 8,27 s y el ILC supone 6 s | Error visto 220 N rms en vez de 89 N |

## Simulaciones / cálculos (sin hardware; no son mediciones)
| Figura | Qué prueba | Cómo leerla | Lectura clave |
|---|---|---|---|
| `2026-11-19_sim_k_desconocida_claro.png` | Control de fuerza con rigidez de prótesis desconocida (50 y 90 kg, 3 prótesis) | Arriba: curvas a 90 kg; abajo: ganancia efectiva por método vs línea de diseño (6 1/s) | Rigidez fija supera la ganancia de diseño en 5 de 6 casos; "precarga + rigidez aprendida" en ninguno |
| `2026-11-19_oscilacion_causa_claro.png` | Posible causa de la oscilación 6–8 Hz (modo mecánico SUPUESTO, no medido) | (a) filtro del ILC, (b) margen de estabilidad, (c)(d) mejoras posibles | Programar Kp según la rigidez es lo que más reduce la oscilación (en simulación) |
| `2026-11-19_resonancia_6_8hz_claro.png` | ¿El modelo lineal del lazo predice la resonancia? | (a) respuesta en frecuencia, (b) frecuencia de resonancia vs constante del servo | No: el modelo no tiene pico de resonancia |
| `2026-11-19_notch_fz_bode_claro.png` | Filtro notch propuesto (NO conectado al lazo) | Ganancia, fase y retardo vs frecuencia | El notch angosto elimina 6–8 Hz con ≈5 ms de retardo; los anchos suman 7–12 ms |

No se rehizo `control/diagramas/salida/` (diagramas de bloques/ecuaciones, no gráficas de resultados). Las figuras de 11-05 a 11-18 se documentan en `LEEME_figuras_antiguas.md`.
