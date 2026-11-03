# Simulación RT vs ILC con latencia — notas (actualizado 2026-11-03, curva real)

Cómo leer la figura panel por panel: ver reporte `reportes/2026-11-03_reporte_dia.md` § 5.

Script: `rt_vs_ilc_latencia.py` · figura: `rt_vs_ilc_latencia.png` · salida numérica (incluye sensibilidad): `salida_consola.txt`.

## Qué es verificado y qué no
| Elemento | Estado |
|---|---|
| **Fuerza objetivo** | **REAL**: media de 350 sujetos sanos, Gutenberg Gait Database (Horst et al. 2021, DOI 10.1038/s41597-021-01014-6, datos CC0). Picos 115.4 %BW (22 % del apoyo) y 117.8 %BW (78 %), valle 71.1 %BW (49 %); marcha autoseleccionada, media 1.40 m/s. Código: `../referencia_grf/` |
| **Latencia** | **MEDIDA** en parte (RPi↔ESP32 5.97 ms, ADS1256+SPI+Python 1.6–2.4 ms); se barre de 0 a 160 ms |
| Servo del eje (τ = 20 ms) | **SUPUESTO sin medir** → se barre 10/20/50 ms (sensibilidad) |
| Rigidez de contacto (k real = 0.8 del modelo) | **SUPUESTO sin medir** → se barre 0.5/0.8/1.0/1.5 |
| Duración del apoyo (4 s) | **SUPUESTO**: ≈ apoyo real × 6; no hay un dato del simulador → se barre 3/4/5 s |
| Perturbación (pulso 3 %BW) | **SUPUESTO**, sin impacto de talón |

Modelo: servo de 1.er orden → contacto con rigidez efectiva → medición retrasada T. Métodos: RT (realimentación), RT+FF (más prealimentación de la derivada del objetivo, con k estimada 20 % distinta), ILC (realimentación + corrección aprendida ciclo a ciclo).

## Resultados (curva real; Kp=10, τ=20 ms, k real=0.8, apoyo 4 s)
1. **Límite de latencia por estabilidad (analítico, margen de fase ≥ 45°)** según la ganancia de lazo efectiva (= Kp·k real): 5 → 138 ms; 8 → 80 ms; 10 → 60 ms; 15 → 35 ms; 20 → 23 ms; 40 → 6 ms. La tabla de `salida_consola.txt` está calculada con k = 1 (ganancia = Kp).
2. **RT solo-realimentación** (T = 10 ms): RMS 10.8 %BW; por Kp: 5 → 18.0, 10 → 10.8, 20 → 5.5. El error lo domina el atraso por ancho de banda, no la latencia.
3. **RT + prealimentación**: 1.8 %BW a T = 10 ms; empeora al crecer T (4.7 a 60 ms).
4. **ILC**: 11.2 %BW en el ciclo 1 → 0.32 %BW en el ciclo 12 (T = 10 ms); con T = 60 ms se estanca en ≈ 0.54. Error vs T (sin perturbación): 0.3 hasta 40 ms, 0.5 a 60, 1.0 a 80, 2.9 a 100, inestable hacia 130 ms. Con perturbación no repetible (pulso 3 %BW): 0.6 a 10 ms.
5. **Sensibilidad (T = 10 ms)**: en todos los pares τ ∈ {10, 20, 50 ms} × k ∈ {0.5…1.5}, RT queda entre 5.7 y 16.8 %BW e ILC entre 0.2 y 1.3 %BW. Con apoyo de 3 / 4 / 5 s: RT 13.7 / 10.8 / 8.9, ILC 0.8 / 0.3 / 0.2. **La conclusión cualitativa (ILC ≪ RT puro) no depende de un valor único supuesto**; los números absolutos sí.
6. Artefacto: en RT solo-realimentación el RMS baja al subir T hasta ~80 ms (el retardo adelanta la fuerza real y compensa el atraso); no significa que el retardo ayude, el lazo pierde margen.

## Lectura honesta
- No decide por sí sola RT vs ILC: la planta sigue sin identificar (τ, rigidez por prótesis, impacto de talón, fricción/holguras, saturación de velocidad del husillo).
- La referencia es marcha **normal (1.40 m/s)**. El simulador publicó marcha lenta (0.48 m/s) con picos ~100 %BW (propia, Fig. 5c); la amplitud de la fuerza depende de la velocidad. **Qué curva usar como objetivo real del control es decisión de Luis** (pendiente).
- La curva del artículo propio de Luis no se usó porque Luis indicó que no está del todo bien; se basó en literatura internacional.

## Qué hace falta para cerrarlo
1. Identificar τ del servo vertical y rigidez de contacto con ≥ 2 prótesis (escalón + AMTI + sensor de posición).
2. Latencia restante: AMTI (manual), cómputo RPi, ejecución ESP32.
3. Duración real del apoyo en el simulador a x6; definir la velocidad de marcha que representa el objetivo.
4. Repetir con perturbación tipo impacto de talón.
