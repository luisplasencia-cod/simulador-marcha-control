## Clave para decisión
Base abierta (CC BY 4.0) de GRF y CoP de 350 sanos, ya en múltiplos de peso corporal y normalizada a 101 puntos = 100 % del apoyo: usable directo como referencia. Marcha autoseleccionada, edades 11-64.

## Resumen de lectura
Texto completo vía Europe PMC (PMC8413275). Citas: "Each GRF and COP signal was time-normalized to 101 data points, corresponding to 100% stance phase."; "The GRF signals were normalized to the body weight"; "350 healthy individuals"; licencia CC BY 4.0. No es la curva de Winter: son datos propios de ese laboratorio.


## Verificado y usado (2026-11-03)
- F_V_PRO = fuerza vertical procesada en múltiplos de peso corporal, 101 puntos = 100 % del apoyo (tabla 3 y métodos del artículo). Metadata: SPEED 1=lenta/2=autoseleccionada/3=rápida.
- Curva de referencia calculada: 350 sujetos, 8819 pisadas (SPEED=2, sin plantilla ortopédica; promedio por sujeto y luego media ± DE entre sujetos). Picos 115.4 %BW (22 %) y 117.8 %BW (78 %), valle 71.1 %BW (49 %); DE entre sujetos 11.1 y 9.0 %BW; velocidad de marcha 1.40 ± 0.16 m/s (n=284 con dato). Salida: `control/referencia_grf/referencia_fz_gutenberg.csv`, código `extraer_referencia_gutenberg.py`.
- Es marcha normal, no lenta: el simulador publicó 0.48 m/s con picos ≈ 100 %BW. Qué curva usar de objetivo: decisión de Luis.

## Duración del apoyo (2026-11-03)
Archivo GRF_F_V_RAW_right.csv (Figshare 26576491): señales a 250 Hz recortadas al apoyo con umbral Fz = 25 N (verificado en Métodos del artículo). Misma población y filtro que la curva: apoyo **0.615 s** (DE entre sujetos 0.047; rango 0.487–0.793 s), 350 sujetos, 8819 pisadas → a x6 = 3.69 s. Script `control/referencia_grf/duracion_apoyo_gutenberg.py`.
