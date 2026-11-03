## Clave para decisión
Base abierta de 42 sanos (jóvenes y mayores), overground y cinta a varias velocidades, con curvas GRF promedio normalizadas a 101 puntos del ciclo. Útil para elegir velocidad de referencia.

## Resumen de lectura
Texto completo vía Europe PMC (PMC5922232). Cita: "The ASCII files provide the ensemble average data for each participant throughout the full gait cycle (101 time-normalized points)" incl. GRF. No verificado: si la GRF viene en %BW o N (revisar archivos), ni la licencia.


## Verificado y usado (2026-11-03)
- Cinta instrumentada de dos bandas, GRF a 300 Hz; 8 velocidades de cinta T01–T08 (40–145 % de la velocidad cómoda adimensional); velocidad real de cada prueba en `WBDSinfo.csv`. Fuerza vertical = `Fy` (verificado: suma de bandas ≈ peso).
- Se leyó `WBDSascii.zip` (687 MB) por rangos HTTP; solo T01, T02, T03, T05, T08. Solo grupo joven (24): el grupo mayor tiene archivos de cinta incoherentes (ver reporte 2026-11-03 § 5b).
- Resultado a 0.50 m/s (T01): picos 104.2 y 100.5 %BW, valle 98.2 %BW (meseta ≈ 100 %BW), apoyo 1.071 s. Script `control/referencia_grf/curva_vs_velocidad_fukuchi.py`, salida `curva_vs_velocidad_fukuchi.csv` y `resumen_velocidad_fukuchi.txt`.
