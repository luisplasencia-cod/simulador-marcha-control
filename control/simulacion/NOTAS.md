# Simulación RT vs ILC con latencia — notas (actualizado 2026-11-08)

**(2026-11-08) Barrido de `Kp` → recomendación de partida: 15 1/s.** Ver `reportes/2026-11-08_avance_sin_rpi.md` §3 y figura `barrido_kp_2026-11-08.png`. `Kp=15` da 3.5× de margen de fase sobre la latencia parcial ya medida (10 ms); `Kp≥40` se queda sin margen. Re-ejecutar este barrido cuando `tau_a` y la latencia completa estén medidas (hoy ambos son supuestos).

**(2026-11-07) `k_real` ya NO es solo un barrido inventado (0.5-1.5): se agregó una tabla con el `k`
REAL medido en el Ensayo A (talón 26.4, plana 23.0, punta 2.4 N/mm, 2026-11-05, 1 prótesis), usando
`k_asumido` = talón (la elección conservadora de la Etapa 1, ver `reportes/2026-11-06_analisis_ganancia_fz_conservadora.md`).
**Resultado clave:** con esa ganancia fija, ningún pie se vuelve inestable (confirma que la elección
conservadora es correcta), pero en la punta el ILC pasa de 0.45%BW de error (talón) a **11.9%BW**
(~26x peor) — el aprendizaje ciclo a ciclo del ILC no compensa bien un desajuste de ganancia tan
grande (ratio 0.091). Confirma que la Etapa 2 (ganancia variable por CoP) no es un "nice to have":
sin ella, el control es malo en la punta incluso con muchos ciclos de ILC. Ver salida completa en
`salida_consola.txt`, sección "Con k REAL medido", y la figura `rt_vs_ilc_k_real_medido.png`
(barras de error RMS por condición de pie, 3 valores de `tau_a` sin medir).

**La metodología, los datos (verificado vs. no medido), los resultados, cómo leer cada panel y las limitaciones están en `reportes/2026-11-03_reporte_dia.md` § 7.** Este archivo solo indica qué hay en la carpeta.

- `rt_vs_ilc_latencia.py` — simulación; `rt_vs_ilc_latencia.png` — figura; `salida_consola.txt` — números (barrido de latencia, T máx analítico, sensibilidad).
- Datos de entrada **verificados**: curva de Fz y duración del apoyo (Gutenberg Gait Database, Horst 2021, DOI 10.1038/s41597-021-01014-6) en `../referencia_grf/`; factor x6 confirmado por Luis; latencia medida (`pruebas/`).
- **NO medido** (se barre, no se afirma): constante del servo τ y rigidez de contacto. **Elecciones de diseño** (no datos): Kp, γ y filtro del ILC, perturbación de 3 %BW, margen de fase 45°.
- Reproducir: `source .venv/bin/activate && python control/simulacion/rt_vs_ilc_latencia.py`.

- Con la curva lenta real (Fukuchi T01, 0.50 m/s): `python control/simulacion/rt_vs_ilc_latencia.py T01` (salida `rt_vs_ilc_latencia_T01.png` y `salida_consola_T01.txt`); resultados en el reporte § 7.7.
