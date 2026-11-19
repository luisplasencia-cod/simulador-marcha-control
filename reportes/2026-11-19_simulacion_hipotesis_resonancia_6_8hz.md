# ¿El margen de fase del lazo de Fz explica la resonancia de 6-8 Hz? — simulación (laptop, sin RPi)

Fecha: 2026-11-19. Documento de análisis: no se ejecutó nada en hardware, no hay RPi en esta sesión.

## Objetivo
La escalera de carga 50-90 kg (x10) mostró una oscilación de 6-8 Hz que crece con la carga
(`reportes/2026-11-18_escalera_50_a_90kg_x10_y_abortos.md`), con una hipótesis sin confirmar:
resonancia estructural/del actuador excitada por el propio lazo. Antes de pedirle a Luis la
prueba en hardware (misma carga, Kp 3 vs 5), comprobar con el modelo de planta ya existente
(`control/simulacion/rt_vs_ilc_latencia.py`) si el margen de fase/ganancia del lazo, con los
retardos y Kp REALES de ayer, ya predice por sí solo una resonancia cerca de 6-8 Hz.

## Metodología
Script nuevo: `control/simulacion/analisis_resonancia_2026-11-19.py` (no modifica
`rt_vs_ilc_latencia.py`, solo importa su módulo). Modelo (el mismo del script oficial):
servo de 1er orden (constante `tau_a`) en serie con un integrador de rigidez (`dF/dt = k·v`),
realimentado con retardo `T` en la medición. Lazo abierto `L(jω) = Kp·k_ratio·e^{-jωT} / (jω(1+jωτ_a))`;
cerrado `F/Fref = L/(1+L)`. Se barre `ω` y se busca el pico de `|F/Fref|` (resonancia) y su
frecuencia, el cruce de ganancia y el margen de fase.

**Parámetros usados (todos medidos ayer, no inventados):**
- `T` (retardo comando→Fz) = 15-23 ms (Ensayo B, `reportes/2026-11-18_ensayo_B_respuesta_dinamica.md`).
- `τ_a` (constante del servo) = 3-14 ms (Ensayo B; **no** los 20 ms supuestos que trae por defecto el script oficial).
- `k_din` = 17.7-19.5 N/mm (Ensayo B) vs `k_asumido` = 26.4 N/mm (talón, decisión Etapa 1,
  2026-11-06) → `k_ratio` = 0.67-0.74.
- `Kp` real por escalón (`reportes/2026-11-18_escalera_50_a_90kg_x10_y_abortos.md`): 8 en 50-60 kg, 5 en 70-90 kg.

Se barrieron las 16 combinaciones extremas (2 Kp × 2 T × 2 τ_a × 2 k_ratio) y una figura con
el punto medio de cada rango.

## Resultado
**El modelo NO predice ninguna resonancia cerca de 6-8 Hz — de hecho no predice resonancia
en absoluto con estos parámetros.** En las 16 combinaciones: pico de `|F/Fref|` = DC (relación
pico/DC = 1.00 en todas, sin sobreimpulso en frecuencia) y margen de fase 78-87° (lejísimos de
los 45° donde empezaría a asomar un pico). El cruce de ganancia (`|L|=1`) cae en **0.5-0.9 Hz**
(Kp=5 → ≈0.53-0.59 Hz; Kp=8 → ≈0.85-0.94 Hz) — un orden de magnitud por debajo de la banda
observada (6-8 Hz). Con Kp y retardos reales, el ancho de banda del lazo es demasiado bajo para
que el propio lazo (vía margen de fase comido por el retardo) pueda generar o amplificar una
oscilación a 6-8 Hz: a esa frecuencia el lazo ya atenúa, no amplifica.

Tampoco aparece dependencia de la carga en este mecanismo: cambiar `k_ratio` de 0.67 a 0.74
(60→90 kg) apenas mueve el cruce de ganancia (0.85→0.94 Hz con Kp=8) y no cambia que
pico/DC siga en 1.00. El crecimiento de amplitud con la carga que se midió ayer **no** se
explica por este mecanismo (ganancia de lazo) — tendría que venir de otro lado (fuerza real
mayor a resonancia estructural fija, o del propio actuador/mecánica bajo más carga).

Figura: `control/simulacion/resonancia_6_8hz_2026-11-19.png` (panel a: respuesta en
frecuencia, banda 6-8 Hz sombreada, completamente plana ahí; panel b: frecuencia del pico de
resonancia vs τ_a — no hay pico que mostrar en el rango simulado, confirma lo anterior).

**Veredicto honesto: esta simulación NO explica el fenómeno.** Descarta (dentro de este modelo
lineal simplificado) que el margen de fase del lazo tal como está hoy sea la causa — refuerza,
por eliminación, la hipótesis ya escrita en el reporte de la escalera: algo estructural
(mecánico, del actuador/husillo/cadena) que vibra a 6-8 Hz independientemente del Kp usado, y
que el lazo solo "excita" al moverse, no que el lazo lo genere por su propia dinámica de control.

## Limitaciones
- Modelo lineal de 1 solo eje con servo de 1er orden + integrador puro — no tiene ningún modo
  mecánico de 6-8 Hz porque no se modeló ninguna masa/resorte estructural (husillo, cadena,
  acoplamientos, backlash). Es coherente con el resultado (no puede predecir algo que no está
  en el modelo) pero no es una prueba de que no exista: es evidencia de que el mecanismo de
  "margen de fase del lazo de control" específicamente NO alcanza, no de que la estructura esté
  sana.
- `τ_a` sigue siendo de 1 solo Ensayo B (1 corrida, carga baja, plana 0°): el rango 3-14 ms
  usado aquí es el reportado, no una distribución estadística.
- No se modeló el muestreo discreto real (periodo de lazo medido = 10.0 ms, `DT_CONTROL_S`)
  ni cuantización de pasos — ambos podrían, en principio, introducir contenido de alta
  frecuencia que este modelo continuo no captura; no evaluado.
- El filtro Hanning del ILC (ya existente, confirmado que no es la causa en el reporte de la
  escalera) no se incluyó en este análisis de margen de fase porque actúa ciclo a ciclo
  (corrección `delta`), no dentro de un ciclo — no cambia esta conclusión.
- No valida ni descarta la prueba propuesta por Luis (misma carga, Kp 3 vs 5): sigue siendo la
  forma de confirmar en hardware si la frecuencia no cambia con Kp (lo que apoyaría
  resonancia estructural). Esta simulación es consistente con ese resultado esperado (aquí
  tampoco aparece dependencia relevante de Kp en el rango 5-8), pero no lo reemplaza.

## Fuentes
- `reportes/2026-11-18_escalera_50_a_90kg_x10_y_abortos.md` (oscilación medida, Kp por escalón).
- `reportes/2026-11-18_ensayo_B_respuesta_dinamica.md` (T, τ_a, k_din medidos).
- CLAUDE.md (2026-11-06, `k_asumido` = talón = 26.4 N/mm, decisión Etapa 1).
- `control/simulacion/rt_vs_ilc_latencia.py` (modelo de planta reutilizado, sin modificar).
- `control/simulacion/analisis_resonancia_2026-11-19.py` (script nuevo de este análisis).
