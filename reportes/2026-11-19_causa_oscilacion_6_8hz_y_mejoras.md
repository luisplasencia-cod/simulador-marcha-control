# Causa de la oscilación de 6–8 Hz del lazo de Fz y cómo mejorarla — 2026-11-19 (laptop, solo simulación)

## Objetivo
Explicar por qué el lazo de Fz oscila a 6–8 Hz en la escalera 50–90 kg x10 (`reportes/2026-11-18_escalera_50_a_90kg_x10_y_abortos.md`), por qué la oscilación **crece pisada a pisada** y **con la carga**, y qué cambio la quita. Complementa `reportes/2026-11-19_simulacion_hipotesis_resonancia_6_8hz.md` (que descartó el retardo solo con un modelo sin modo mecánico y sin ILC).

## Metodología
1. **Lectura del código real** (`control/ilc/ilc_core.py`, `control/ilc/fz_ilc.py`, bucle de `correr_lazo()` en `control/lazo_fz_tiempo_real.py`) y respuesta en frecuencia del filtro Q real.
2. **Datos reales disponibles en la laptop** (los CSV de la escalera están en `.gitignore`, no están aquí): pisadas 3 ejes desde la interfaz (`reportes/datos/2026-11-18_pisadas_3ejes_interfaz/`, con tiempo real), Ensayo B (`control/identificacion/resultados/ensayoB_ang0_20261118_114209.csv`).
3. **Simulación** `control/simulacion/oscilacion_causa_2026-11-19.py` (correr con `--figura`): SET_VEL → retardo 19 ms → servo 1.er orden 8 ms (Ensayo B) → motor → resorte del accionamiento `KD` = 200 N/mm + amortiguador → carro de masa `M` = 140 kg → prótesis no lineal `F = 15·x + 0.0377·x^2.98` (ajustada a las compresiones de la escalera y a los 15 N/mm de carga baja del Ensayo A). Medición con ruido 0.75 N + 60 Hz (σ ≈ 2.6 N), bloque de 7 muestras frescas, mediana. Bucle = mismas ecuaciones que `correr_lazo()` (índice de referencia por iteración, saturación 9000 pasos/s, `t` del log nominal) con el **ILC real importado** (`ControlFzILC`, sin reimplementar). Iteración real = 7 ms (muestras frescas) + RTT de SET_VEL ~6 ms + 0.5 ms. **`KD`, `M` y el amortiguamiento ζ son supuestos** elegidos para dar un modo de ~7 Hz; se barrió ζ = 0.03–0.20.
4. Lazo linealizado en el pico de la curva (margen de ganancia, pico de sensibilidad) y 10 pisadas en el tiempo a 60/70/90 kg con los Kp usados (8, 8, 5) + variantes de mejora.

## Resultado

### Hallazgos en el código y en los datos (medidos/leídos, no supuestos)
- **El ILC no puede inyectar 6–8 Hz:** el filtro Q real (Hanning de 41 puntos sobre 200) vale **< 0.001 a 6–8 Hz** (0.000 a 7 Hz; 0.33 a 1 Hz). `Q` se aplica a `delta + γ·e` completo cada pisada. Ni el olvido (α = 0.95) ni un Q más ancho cambian la oscilación en la simulación (fig. c, d). **H1 del pedido (el ILC amplifica alta frecuencia) queda descartada como mecanismo directo.**
- **La columna `t` del CSV del lazo es nominal (`i·10 ms`), no medida.** Cada iteración espera 7 muestras frescas (7 ms) y luego la respuesta de SET_VEL (~6 ms) → ≈ 13–14 ms. La interfaz, que hace lo mismo por iteración, mide **13.0 ms de mediana (p95 18.6 ms)** con reloj real. Por lo tanto la afirmación "período real 10.0 ms (mediana del log)" de `reportes/2026-11-18_primer_lazo_cerrado_fz.md` es un artefacto: **las corridas "x10" duraron ≈ 8.3 s de apoyo (≈ x13.5)**. Esto también suma ~7 ms de retardo efectivo (medio período) y cambia la extrapolación de velocidad para 80–90 kg.
- **La referencia se aplica en escalones** (`idx = int(i·n/n_muestras)`): hasta **47 N a 70 kg** (≈ 60 N a 90 kg) cada ~41 ms reales → saltos de comando de hasta ~14 mm/s con Kp 8. Es una excitación **proporcional a la carga**.
- **La rigidez de diseño solo vale a carga baja:** `k_asumido` = 26.4 N/mm (talón) se midió hasta 105 N. Con las compresiones de la escalera, la rigidez **tangente** de la prótesis en el pico estimada es **67–88 N/mm** (60–90 kg), 2.5–3× la de diseño → la ganancia efectiva del lazo en el pico es 2.5–3× la diseñada. (Estimación: compresiones de la escalera calculadas con la 1.ª muestra como contacto; la curva F-x a carga alta no está medida.)

### Lazo linealizado en el pico (d efectivo 29 ms = 19 + 13.5/2 + 3.5)
| caso | gan. efectiva (1/s) | sin modo: margen | modo 7 Hz ζ 0.10: margen / pico sensibilidad | lo observado en el rig |
|---|---|---|---|---|
| 60 kg Kp 8 | 15 | 2.95 | **0.89** (inestable en el pico) | completó, 8.3 Hz, crecía 7.9→15 N |
| 70 kg Kp 8 | 16 | 2.78 | **0.84** (inestable) | **abortó a ~7 Hz** (salto 83 N) |
| 70 kg Kp 5 | 10 | 4.45 | 1.34 / ×4.5 a 5.9 Hz | completó, oscila |
| 90 kg Kp 5 | 11 | 4.04 | 1.23 / ×5.6 a 6.0 Hz | completó, 31 N rms |
| 70 kg Kp 3 | 6 | 7.41 | 2.24 / ×2.0 a 6.1 Hz | (prueba propuesta) |

**Solo retardo no basta** (márgenes 2.8–4.5, amplifica ≤1.7×): para explicar el aborto de Kp 8 hace falta un modo mecánico/del servo cerca de 7 Hz dentro del lazo. Con ese modo, la fase llega a −180° a **5.7–6.0 Hz**, el margen cae con Kp y con la carga, y Kp 8 a 60–70 kg queda inestable *en los picos* (donde la prótesis es más rígida), estable en el resto del apoyo: ráfagas en los picos, como se vio ("en la bajada del primer pico").

### Simulación temporal, 10 pisadas, modo ζ = 0.10 (fig. c, d)
- **El ILC converge como en el rig:** 70 kg Kp 5, RMS r−F **57 → 21 N** (rig: 60.2 → 20.6 N). La parte lenta del modelo está bien calibrada.
- **Reproduce el crecimiento pisada a pisada:** 60 kg Kp 8, error 3–15 Hz **12 → 25 N (×2.2)** (rig: 7.9 → 15 N, ×1.9). Mecanismo: el ILC no mete 7 Hz, pero **al converger lleva F a los picos reales** (la pisada 1 llega tarde y baja), justo donde la rigidez tangente y por lo tanto la ganancia efectiva son máximas → el lazo pasa más tiempo en la zona sin margen. **70 kg Kp 8 abortaría en la pisada 1** (rig: abortó).
- **No reproduce** la amplitud de Kp 5 a 70–90 kg (sim ≈ 2 N, rig 20–31 N): en el rig la ganancia a carga alta es mayor que en el modelo (rigidez que sube más rápido o modo menos amortiguado). Ver limitaciones.

### Mejoras probadas (error en 3–15 Hz en la pisada 10; RMS r−F en la pisada 10)
| variante | 60 kg Kp 8 | 70 kg Kp 8 | 90 kg Kp 5 |
|---|---|---|---|
| actual | 25 N / 31 N | **202 N, aborta** | 2 N / 26 N |
| r y delta interpolados (misma velocidad) | 17 / 21 | 110, aborta | — |
| rampa de aceleración 1000 mm/s² (en el RPi) | 13 / 23 | 59, aborta | 2 / 29 |
| rampa 400 mm/s² | 14 / 31 | 24 / 48 | 2 / **52** (sigue peor) |
| ILC con olvido 0.95 / Q más ancho | 23 / 29 ; 20 / 27 | ~200, aborta | 2 / 24–31 |
| **Kp programado por la rigidez tangente** (`Kp·min(1, k_asumido/k_tangente(r))`) | **2 / 14** | **2 / 16** | 2 / 30 |

**Recomendación (por evidencia en simulación):** la mejora que quita la oscilación en todos los casos **y** mejora el seguimiento es **bajar la ganancia donde la prótesis es más rígida**: `Kp_efectivo = Kp · min(1, k_asumido / k_tangente(F))`. Es exactamente la regla del 2026-11-06 ("nunca más agresivo que lo diseñado") aplicada a la rigidez **real a carga alta**, que hoy no se conoce. Se necesita la curva `k_tangente(F)` de cada prótesis hasta la carga objetivo — la puede dar el estimador de k en línea que está diseñando otro agente, o un Ensayo A hasta ~1000 N. Complementos baratos: interpolar `r` y `delta` (quita los escalones de hasta 47–60 N; reduce la excitación a la mitad en la pisada 1) y una rampa suave (≈1000 mm/s²; con 400 mm/s² se pierde seguimiento a 90 kg). Cambiar el ILC (olvido, Q) no sirve para esto.

### Cambios propuestos para `control/lazo_fz_tiempo_real.py` (NO aplicados; los integra el orquestador)
1. **Registrar el tiempo real**: columna nueva `t_real = time.monotonic() - t_ciclo0` en el CSV (y en el `.meta.txt` la mediana/p95 del período). Sin esto ningún análisis de frecuencia ni de velocidad del rig es fiable.
2. **Kp programado** (requiere `k_tangente(F)`): `kp_i = kp * min(1.0, k_asumido / k_tan(r_corregida))` antes de calcular `u_pasos_s`; registrar `kp_i` en el CSV.
3. **Interpolación lineal** de `ctrl.ref_bw` y `ctrl.ilc.delta` entre puntos de la malla (en vez de `idx = int(...)`).
4. **Rampa opcional** `--a_max_mm_s2` (por defecto apagada): `du_max = a_max·80·dt_real`; limitar `u` respecto del anterior.
5. Decidir con Luis si el índice de la referencia pasa a tiempo real (apoyo de verdad x10, ≈ 35 % más rápido que lo corrido el 11-18 → más velocidad de Y) o se declara la escala real (≈ x13.5).

### Qué prueba en la RPi confirma (en orden)
1. **Ensayo B a carga alta, lazo ABIERTO** (lo decisivo): con el pie precargado a ~500–900 N (sin lazo, con `MANUAL`), pulsos chicos de SET_VEL (±1–2 mm) y mirar si Fz **suena a 6–8 Hz** tras cada parada. Si suena: existe el modo (da `fn` y ζ reales) y se mide además la rigidez tangente a carga alta. Si no suena a ninguna carga: el modo no es mecánico y hay que buscar otra fuente de fase (p. ej. el período real/jitter).
2. **Kp 3 vs Kp 5 a 70 kg** (protocolo `reportes/2026-11-19_protocolo_proxima_sesion_rpi.md`). Predicción de este modelo: **la amplitud a ~6 Hz baja 2–4× con Kp 3 y la frecuencia casi no cambia (5.9 → 6.1 Hz, ≤ 2× la resolución)**. ⚠️ Con la tabla de decisión actual del protocolo eso se leería como "la excita el lazo"; según este análisis la lectura correcta es "modo dentro del lazo con poco margen" — la conclusión práctica es la misma (bajar la ganancia en carga alta), pero no es una "resonancia pasiva" que un notch resuelva solo.
3. Medir el período real del lazo (punto 1 de los cambios) en esa misma sesión.

## Limitaciones
- `KD`, `M` y ζ del modo **no están medidos**: se eligieron para dar ~7 Hz. La masa efectiva (140 kg con KD = 200 N/mm) es plausible solo si el eje vertical carga más que la prótesis (carro, eje horizontal, motor sagital) — **no verificado**; con KD = 100 N/mm bastarían ~90 kg.
- La curva de la prótesis a carga alta sale de 5 compresiones de corridas distintas con la 1.ª muestra como contacto; la rigidez tangente (67–88 N/mm) es una estimación.
- El modelo no reproduce la amplitud de Kp 5 a 70–90 kg (2 N vs 20–31 N): el rig está más cerca de la inestabilidad de lo que el modelo dice; la conclusión cualitativa (ganancia en carga alta) se mantiene, los números no.
- Solo una prótesis, ángulo 0°, sin histéresis ni holgura en el modelo (la anomalía de 4–5 mm "perdidos" del 11-18 a 10 kg no se modeló). La mejora "Kp programado" usa la rigidez del modelo (oráculo); en el rig depende de cómo se estime.
- Los CSV de la escalera no están en la laptop: no se pudo medir el espectro real ni comprobar el período en esas corridas.

## Fuentes
- Código: `control/ilc/ilc_core.py`, `control/ilc/fz_ilc.py`, `control/lazo_fz_tiempo_real.py` (`correr_lazo`).
- Datos: `reportes/2026-11-18_escalera_50_a_90kg_x10_y_abortos.md`, `reportes/escalera/20261118_rpi/70kg_x10_kp8_salida.txt`, `reportes/datos/2026-11-18_pisadas_3ejes_interfaz/` (período 13.0 ms), `control/identificacion/resultados/ensayoB_ang0_20261118_114209.csv`, `reportes/2026-11-18_ensayo_B_respuesta_dinamica.md`, `reportes/2026-11-06_analisis_ganancia_fz_conservadora.md`.
- Simulación y figura: `control/simulacion/oscilacion_causa_2026-11-19.py` (`--figura`), `control/simulacion/oscilacion_causa_2026-11-19.png`.
