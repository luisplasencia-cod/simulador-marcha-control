# Escalera 50-90 kg, 2026-11-18 (copia de control/telemetria/registros/, ignorados por git)
Solo Y en lazo cerrado, pie plano 0 deg, pie_pasivo_1, hueco 30 mm, v_max 9000, x10. Valores leidos de los .meta.txt.
| archivo (hora) | peso N | kp | ciclos | fmax N |
|---|---|---|---|---|
| 152829 | 490.5 (50 kg) | 8 | 6 | 722 |
| 153832 | 588.6 (60 kg) | 8 | 10 | 867 |
| 154240 | 686.7 (70 kg) | 5 | 10 | 1011 |
| 155042 | 784.8 (80 kg) | 5 | 10 | 1156 |
| 155241 | 882.9 (90 kg) | 5 | 10 | 1300 |
(La corrida de 70 kg con Kp 8 que abortó no tiene CSV aqui.)
Columna `t` NOMINAL (i*10 ms), sin t_real: las frecuencias salen ~1.35x altas.
Espectro (control/telemetria/espectro_corrida.py, pisadas >=6, 2026-11-19): f_pico 6.4-7.2 Hz en las 5; RMS e = 4.5 / 13.5 / 3.9 / 9.9 / 16.1 N.
Dato a notar: 70 kg Kp 5 (3.9 N) es mejor que 60 kg Kp 8 (13.5 N) a 7.0 Hz.
