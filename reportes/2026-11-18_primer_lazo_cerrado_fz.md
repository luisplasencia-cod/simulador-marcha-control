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
