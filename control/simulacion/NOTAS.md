# Simulación RT vs ILC con latencia — notas (actualizado 2026-11-03)

**La metodología, los datos (verificado vs. no medido), los resultados, cómo leer cada panel y las limitaciones están en `reportes/2026-11-03_reporte_dia.md` § 7.** Este archivo solo indica qué hay en la carpeta.

- `rt_vs_ilc_latencia.py` — simulación; `rt_vs_ilc_latencia.png` — figura; `salida_consola.txt` — números (barrido de latencia, T máx analítico, sensibilidad).
- Datos de entrada **verificados**: curva de Fz y duración del apoyo (Gutenberg Gait Database, Horst 2021, DOI 10.1038/s41597-021-01014-6) en `../referencia_grf/`; factor x6 confirmado por Luis; latencia medida (`pruebas/`).
- **NO medido** (se barre, no se afirma): constante del servo τ y rigidez de contacto. **Elecciones de diseño** (no datos): Kp, γ y filtro del ILC, perturbación de 3 %BW, margen de fase 45°.
- Reproducir: `source .venv/bin/activate && python control/simulacion/rt_vs_ilc_latencia.py`.
