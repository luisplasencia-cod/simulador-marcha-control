# Primer lazo cerrado de Fz en Y con contacto real (2026-11-18, 11:45)

## Objetivo
Cerrar el lazo de fuerza vertical (Fz) con la prótesis apoyada, con **X y el ángulo (K) en lazo abierto, quietos**, y ver si Fz sigue la curva objetivo (Gutenberg, doble pico) y si el ILC mejora de un ciclo al siguiente. Primera corrida con contacto real de `control/lazo_fz_tiempo_real.py`.

## Metodología
`lazo_fz_tiempo_real.py --peso_sujeto_n 60 --fmax_n 100 --hueco_mm 45 --extra_mm 30 --hueco_remedido --angulo_deg 0 --kp 10 --n_ciclos 3 --fuente_fz uart --puerto_fz /dev/ttyAMA0 --ejecutar`. Carga de prueba BAJA a propósito (escala 60 N, pico de referencia 70.7 N, apoyo 3.69 s = x6), pie en 0° (plana, por pasos de K, no medido), prótesis acoplada con sustituto de muñón, tope 100 N, hueco declarado conservador (45 mm; Luis midió 7 cm "del suelo"), Fz por UART (ESP32 de lectura) con mediana de bloque de 7 muestras, tara previa, `k_asumido` = 26.4 N/mm (el más rígido medido → 3.03 pasos/N), `Kp = 10` (recomendado por el Ensayo B, no 15). Log: `control/telemetria/registros/2026-11-18_114517_fz.csv`; figura `reportes/figuras/2026-11-18_primer_lazo_cerrado_fz.png`.

## Resultado (medido)
- **Completó los 3 ciclos sin abortar**, sin saturar la velocidad (|u| máx ≈ 900 de 1600 pasos/s), F máx 72.7–77.4 N (tope 100 N). Contacto a 57.4 mm de descenso (el hueco declarado sobreestimó ≈12 mm). **Y volvió exactamente a su posición inicial** (contador relativo 0). X y K no se movieron.
- **Error real contra el objetivo (`r − F`, calculado del log): RMS 8.54 → 5.83 → 4.71 N** (12.1 % → 8.2 % → 6.7 % del pico). El resumen que imprime el lazo da 8.97 → 6.12 → 5.01 N (interpola a su propia malla); uso las del log por poder reproducirlas. `delta` del ILC crece de 0 a 9.5 y 15.9 N (el ILC aprende). El log guarda `e = r_corregida − F` (error respecto a la referencia ya corregida por el ILC), que NO baja: es normal, no es el error de seguimiento real.
- El lazo reproduce la forma de doble pico: en la zona media (1–3 s) el error es del orden del ruido (±5 N; σ de medición ≈ 2.6 N por el 60 Hz).
- **Dónde está el error que queda:** (1) **carga inicial** (0–0.5 s): F llega tarde (atraso aparente respecto a r: 110 → 70 → 50 ms por ciclo), error hasta +20 N; (2) **descarga final** (3.3–3.7 s): F baja más lento que la referencia, error −20 a −30 N, que **persiste entre ciclos**; (3) en el ciclo 0 hay un **transitorio puntual** en t ≈ 0.8 s (F cae a 40 N, e +30 N), no reaparece en los ciclos 1–2, **causa no investigada**. Hipótesis (NO verificada) del error en las rampas: un lazo con ganancia proporcional sobre una planta integradora deja un error proporcional a la pendiente de la referencia; el ILC lo va reduciendo ciclo a ciclo, y 3 ciclos no alcanzan a converger.
- **Corrección de un dato mío:** el período real del lazo es **10.0 ms** (mediana del log), no 13–14 ms como estimé en el reporte del Ensayo B: mientras `SET_VEL` espera su respuesta (~6 ms) el hilo lector ya acumula las muestras del bloque.

## Limitaciones
- Carga baja (pico ≈ 71 N, no una carga fisiológica de 700–1500 N); una prótesis, un ángulo (0°), una corrida de 3 ciclos, `Kp = 10` sin barrido.
- **X y K quietos: NO es la marcha completa;** la trayectoria acoplada (montaje 37) no se ha corrido (exige HOME, prohibido con prótesis, y la tarea quedó pendiente).
- Fz sin validar contra NetForce con masas en esta ruta (R6 pendiente; el escalón con pesa en la laptop dio +1.8 / +3.2 %). Nota: Luis tenía NetForce abierto; si registró los picos durante esta corrida, comparar con ≈ 71–77 N.
- La rigidez del contacto cambia con la carga (Ensayo A: no lineal); la ganancia efectiva a cargas mayores será distinta.
- El sondeo del firmware de motores (~5 ms) sigue en el camino del comando.

## Fuentes
Log y figura citados arriba; Ensayo B: `reportes/2026-11-18_ensayo_B_respuesta_dinamica.md`; objetivo: `control/referencia_grf/` (Gutenberg 2021).

## Repetición con NetForce a la vista (2026-11-18, 11:50:41–11:51:22)
**Objetivo:** comprobar repetibilidad y tener una validación independiente de Fz con NetForce (que Luis observaba, en cero antes de empezar). **Metodología:** misma orden exacta que la corrida 1 (Kp 10, 3 ciclos, escala 60 N, plana 0°, tope 100 N, hueco declarado 45 mm). Log `control/telemetria/registros/2026-11-18_115042_fz.csv`; salida en `pruebas/resultados/etapa2/salidas/lazo_cerrado_run2_20261118_115042.txt`.
**Resultado (medido):**
- Completó sin abortar; contacto a 57.5 mm (corrida 1: 57.4); Y volvió a su inicio (contador relativo 0).
- **Error real r−F (del log), corrida 2 vs corrida 1:** ciclo 0: 8.09 vs 8.54 N; ciclo 1: 5.52 vs 5.83 N; ciclo 2: 4.66 vs 4.71 N → **repetible dentro de ~5 %**, con la misma mejora ciclo a ciclo.
- **Picos y valle medidos por el ADC (N):** pico 1 = 71.2 / 74.8 / 74.4, valle = 39.0 / 38.8 / 38.6, pico 2 = 72.8 / 73.7 / 74.4 (referencia 70.7 / 42.7 / 70.7). Los picos quedan 1–4 N sobre la referencia y el valle ≈ 4 N (≈ 9 %) bajo ella.
- **NetForce (Luis, a ojo, mensaje textual: "si lo vi son 3 como emes"):** vio 3 ondas en forma de "M" = 3 ciclos de doble joroba, coherente con lo medido por el ADC. **Solo confirmación cualitativa (forma y número de ciclos): Luis no registró magnitudes, así que la escala en N sigue sin validarse contra NetForce.**
**Limitaciones:** (1) no hay valores de NetForce → no se valida la calibración (el +1.8/+3.2 % de la laptop viene de una sola pesa); (2) una sola configuración (71 N de pico, plana 0°); (3) mi aviso "contacto" no llegó: la salida de Python iba a archivo con buffer y la línea de contacto apareció al final (usar `python -u` al lanzar en segundo plano); Luis igualmente vio la corrida.

## Imagen de las 3 "M" (corrida 2) y pruebas de seguridad/convergencia (2026-11-18, 11:52–11:54)
**Objetivo:** (a) dejar la imagen medida por el ADC de lo que Luis vio en NetForce; (b) comprobar en hardware la protección de tope de fuerza; (c) ver si el ILC converge con más ciclos. **Metodología:** `control/telemetria/graficar_corrida.py` (nuevo) sobre los logs; mismas condiciones que la corrida 1 (Kp 10, escala 60 N, plana 0°, X y K quietos, hueco declarado 45 mm), salvo lo indicado. Salidas guardadas en `pruebas/resultados/etapa2/salidas/`.
**Resultados (medidos):**
- **Imagen 3 "M":** `reportes/figuras/2026-11-18_corrida2_tres_M.png` (3 ciclos de doble joroba medidos por el ADC; coincide con lo que Luis vio en NetForce). Se ve que **Fz no vuelve a 0 entre ciclos** (baja a ≈10–20 N al final y empieza en ≈15 N): el lazo mantiene el contacto continuo, a diferencia de la marcha real donde Fz llega a 0 en el balanceo.
- **Prueba de tope (`--fmax_n 40`, pico pedido 71 N):** abortó con `Fuerza 42.9 N > tope 40.0 N`, detuvo el eje y **devolvió Y exactamente a su inicio** (contador relativo 0). **Primera verificación en hardware real del aborto por fuerza.** El aborto llega ≈ 3 N por encima del tope (detección sobre el bloque de 7 muestras, ciclo de 10 ms): al fijar un tope hay que dejar ese margen. Salida: `salidas/prueba_seguridad_tope40N_20261118.txt`.
- **8 ciclos:** RMS real (r−F, del log) 8.35 → 5.79 → 4.81 → 4.12 → 3.36 → 3.25 → 3.10 → 3.23 N: **converge a ≈ 3.1–3.3 N a partir del ciclo 4–5** (≈ 4.4 % del pico; σ de medición ≈ 2.6 N). Error medio en la carga inicial (0.1–0.5 s): +11.8 → +0.2 N; en la descarga final (3.3–3.7 s): −14.9 → −1.2 N; zona media ≈ 0 en todos los ciclos; `delta` del ILC se satura en ≈ 25 N (converge). Figura `reportes/figuras/2026-11-18_lazo_8_ciclos.png`; salida `salidas/lazo_cerrado_8ciclos_20261118.txt`; log `control/telemetria/registros/2026-11-18_115317_fz.csv`. La hipótesis anterior ("el error de las rampas persistente se debe a que 3 ciclos no convergen") queda **apoyada** por estos datos.
**Limitaciones:** carga baja (71 N), una prótesis/ángulo, sin perturbaciones externas (el ILC no corrige lo que no se repite: ver `control/DECISION_TIPO_CONTROL.md`), X y K quietos; el plateau de ≈3 N es el nivel del ruido, no necesariamente el límite del control; lo probado del tope es un solo caso (subida de fuerza lenta).
