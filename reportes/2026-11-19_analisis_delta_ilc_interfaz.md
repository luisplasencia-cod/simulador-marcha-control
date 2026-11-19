# Análisis: delta ILC ≈ 89 N y falta de aprendizaje en el lazo de la interfaz (datos 2026-11-18)

## Objetivo
Explicar con datos ya guardados (sin hardware, sin tocar código) (1) de dónde sale el delta ≈ 89 N de la pisada 2 de la interfaz, (2) por qué el RMS no baja pisada a pisada allí mientras sí baja (57→21 N) en el lazo por script del 19-nov, (3) si hay diferencia de lógica entre `fz_loop.py` y `control/lazo_fz_tiempo_real.py`.

## Metodología
Se releyeron `ilc_core.py`, `fz_ilc.py`, `fz_loop.py` (interfaz) y `lazo_fz_tiempo_real.py` (script). Se reprodujo el ILC offline con `ControlFzILC` alimentado con el CSV de la pisada 1 (17:58:20, 75 kg, x10 → duración 6.0 s, Kp 5) y se comparó con el delta guardado en la pisada 2. Script: `control/simulacion/analisis_delta_ilc_interfaz.py`; figura: `reportes/figuras/2026-11-19_analisis_delta_ilc_interfaz.png`.

## Resultado
1. **El delta no es un offset ni la tara.** Reproduciendo el ILC con el CSV de la pisada 1 salen delta[0] = 88.367 N (el CSV de la pisada 2 trae 88.36767) y RMS que el ILC ve = 219.9 N (la interfaz reportó 219.9). Es decir, la lógica del ILC se reprodujo exacta. El delta completo NO es constante: va de +161 a −228 N en los 6 s; en el CSV solo se ve el tramo 0–0.5 s (88.4 a 90.0 N) porque la pisada 2 abortó a 0.50 s, y el filtro Q (ventana ±0.6 s con relleno reflejado) hace que el arranque sea casi plano. El valor grande viene de un error enorme que el ILC "ve" (punto 2). El script también arranca planos y grandes (delta[0] = 58 N en el ciclo 1 y 160 N en el ciclo 9, corrida 103942), así que lo plano al inicio es propio del filtro.
2. **Causa del no-aprendizaje: base de tiempo inconsistente.** El lazo de la interfaz tarda 13.8 ms por muestra (medio; script: 13.2 ms), no los 10 ms de `dt_s`. El bucle recorre `n_muestras = 600` índices (referencia indexada por muestra), así que la pisada real dura **8.27 s, no 6.0 s**. Luego `pz.t` guarda tiempo REAL y `registrar_medicion(pz.t, pz.F)` interpola F sobre una malla de 0–6.0 s: se compara r(t) contra una Fz estirada ×1.38 y se descartan los últimos 2.3 s. Resultado: el ILC ve RMS 220 N, pero el error real fila a fila (r−F, misma muestra) de esa pisada es **85.4 N** (≈10 % del pico 867 N). Con eje de tiempo nominal (t = índice·10 ms) el ILC vería 89 N y un delta de −83 a +80 N en vez de −228 a +161. El ILC aprende, por tanto, sobre una señal desalineada: no puede converger. Además, X y ángulo siguen la trayectoria en tiempo real a 6.0 s, mientras Y recorre su referencia en 8.27 s: Y y X/K quedan desfasados (efecto propio de la interfaz, no medido en otros ejes).
3. **Diferencia de lógica entre interfaz y script (verificada en código):** ambos indexan la referencia por muestra (`idx = i*n/n_muestras`) y ambos tardan ~13 ms/muestra (script: 615 muestras en 8.10 s en lugar de 6.14 s). La diferencia es solo la base de tiempo que se entrega al ILC: el script usa `t_rel = i*DT_CONTROL_S` (nominal, consistente con el índice) → el error que ve el ILC es el error real y baja 57→21 N; la interfaz usa `time.monotonic()-t0` (real) → error falso y sin aprendizaje. Otras diferencias menores: la interfaz tiene `kp_programado=True` fijo y umbral de salto proporcional al tiempo real; no explican el RMS.

## Limitaciones
- Solo hay una pisada completa con delta = 0 (la de 17:58); no hay datos de una 2.ª pisada completa de la interfaz, así que "no aprende" se demuestra por reproducción del ILC, no por corrida repetida.
- No se verificó qué causa los 13.8 ms/muestra (lectura UART por bloques + SET_VEL ≈ 4–6 ms, redibujado de la interfaz): NO VERIFICADO.
- Con eje de tiempo nominal la referencia sigue 1.38× más lenta que la trayectoria X/K en la interfaz; eso no lo arregla el cambio propuesto.
- El delta del script y de la interfaz se compararon con distinto peso/Kp/ciclos (70 kg Kp 5 vs 75 kg Kp 5).

## Fuentes
`reportes/datos/2026-11-18_pisadas_3ejes_interfaz/` (CSV p1 y p2 de 17:58:20, LEEME); `reportes/datos/2026-11-19_kp3_vs_kp5_70kg/` (2026-11-19_103942_fz.csv y `kp5_70kg_x10_103942.txt`); `~/Projects/gaitsim-control/src/fz/{ilc_core,fz_ilc,fz_loop}.py` (líneas de `pisada()` y `registrar_medicion`); `control/lazo_fz_tiempo_real.py` líneas 440–484; `control/simulacion/analisis_delta_ilc_interfaz.py`.

## Conclusión
- El delta ≈ 89 N es el inicio plano del delta filtrado (88.37 N reproducido exacto), no un offset ni la tara.
- El ILC de la interfaz recibe un error falso (220 N vs 85 N real) porque pasa tiempo real a una referencia indexada por muestra; el lazo corre a 13.8 ms/muestra, no 10, y la pisada dura 8.27 s en vez de 6.0.
- El script del 19-nov no falla porque usa tiempo nominal (índice·dt): mismo bug de periodo, pero ILC alineado.
- Propuesta (no aplicada): en `FzLoop.pisada()` guardar `pz.t.append(i * self.p.dt_s)` (o interpolar F sobre `t_ref = idx·duracion/n`) para el ILC, conservando el tiempo real aparte para telemetría. Mejor aún: hacer que la referencia avance con tiempo real (`idx = int(t_rel/duracion*n)`, terminar a `t_rel >= duracion`) para que Y siga sincronizado con X/K; luego repetir 2–3 pisadas y comprobar que el RMS del ILC coincide con el r−F fila a fila.
