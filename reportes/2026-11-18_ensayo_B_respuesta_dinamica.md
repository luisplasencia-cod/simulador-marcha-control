# Ensayo B — respuesta dinámica del eje vertical CON contacto (2026-11-18, 11:42)

## Objetivo
Medir lo que faltaba para cerrar el lazo de Fz: el **retardo comando→fuerza** (ESP32 + servo/mecánica + AMTI + ADS1256 + UART, todo junto), la **constante de tiempo del servo** (`tau_a`, que la simulación había supuesto en 20 ms SIN medir) y la **rigidez dinámica** (para contrastar con el Ensayo A estático).

## Metodología
`control/identificacion/ensayo_B_respuesta_dinamica.py` (nuevo): tara → aproximación lenta con detección de contacto (5 bloques seguidos > 8 N) → por cada velocidad {200, 400} pasos/s (2.5 y 5 mm/s), 3 repeticiones: quieto 0.5 s, baja 0.2 s, sube 0.23 s, quieto. Pie en **0° (plana, por pasos de K, no medido)**, prótesis acoplada con sustituto de muñón, Fz por UART (ESP32 de lectura), tope 60 N, **hueco declarado 45 mm a propósito conservador** (Luis midió 7 cm "del suelo"; no sé si el "suelo" es el del laboratorio o la superficie del plato AMTI, así que casi todo el descenso fue lento). Y volvió a su posición inicial (contador relativo 0). Datos: `control/identificacion/resultados/ensayoB_ang0_20261118_114209.csv`; figura `…114209.png`.
Dos análisis: (1) ajuste rampa con retardo a la bajada (`ajustar`); (2) ajuste del modelo completo `v'=(u(t−d)−v)/tau`, `F'=k·v` a cada pulso incluyendo inversión y parada (`identificar_servo_ensayo_B.py`; retardo y tau por rejilla, k y offset por mínimos cuadrados). El método (1) se validó antes con datos sintéticos con el ruido real (error ±5–12 ms por pulso).

## Resultado (medido)
- **Contacto a 57.2 mm de descenso** (el hueco declarado de 70 mm sobreestimó ≈13 mm, como en sesiones anteriores). Fz base en contacto 18.8 N.
- **Retardo comando→Fz (ajuste de rampa): 14–22 ms a 400 pasos/s (media 17 ms); 16–48 ms a 200 pasos/s** (a 200 pasos/s la señal es débil frente al ruido: la dispersión es ruido, no otro retardo).
- **Modelo completo:** retardo d = 15 ± 8 ms (400) y 23 ± 8 ms (200); **tau_a = 10 ± 5 ms (400) y ≈3.5 ms (200, en el límite inferior de la rejilla)** → `tau_a` es pequeña (≤ ~14 ms), NO los 20 ms supuestos ni los 40–50 ms que yo estimé al principio de forma apresurada (de un solo rasgo del dato: el pico de Fz llegó ~50 ms después de ordenar la inversión; el ajuste completo lo explica con retardo + inercia pequeña). Error del ajuste ≈ 1.9 N ≈ nivel del ruido.
- **Rigidez dinámica |k| = 17.7 ± 0.4 N/mm (400) y 19.5 ± 0.8 N/mm (200).** Con rampa simple: 16.1 y 19.0. **Convención:** con v>0 = subir, Fz aumenta al bajar, por eso el ajuste da k negativo; aquí se reporta el valor absoluto. Frente al Ensayo A (plana 23.0 N/mm global; ≈15 N/mm en la zona de baja carga de su curva no lineal) es consistente con la zona de carga baja (18–30 N), no idéntico.
- **Lo que implica para Kp (modelo de `control/simulacion/rt_vs_ilc_latencia.py`, margen de fase 45°):** con `tau_a` 5–15 ms, T máx tolerable = Kp 10: 65–74 ms; Kp 15: 39–48 ms; Kp 20: 26–35 ms; Kp 25: 19–27 ms. Latencia efectiva estimada del lazo ≈ 20–28 ms (d medido + ~5 ms de retardo de muestreo: **corrección posterior** — el ciclo real del lazo dura 10.0 ms (medido en `reportes/2026-11-18_primer_lazo_cerrado_fz.md`), no 13–14 ms como escribí aquí al principio). → **Kp = 15 queda con margen estrecho (1.3–2×), Kp = 10 con 2–3×. Propuesta (decisión de diseño, no medida): primera corrida cerrada con Kp = 10.** La ganancia efectiva además se escala por k_real/k_asumido (17.7–19.5 vs 26.4 del talón ≈ 0.7).

## Limitaciones
- Una sola corrida (6 pulsos), un ángulo (0°), una prótesis, una carga baja (18–30 N); las velocidades son las ORDENADAS, no medidas, y el desplazamiento no se midió con regla.
- `tau_a` poco determinada (3.5–14 ms entre pulsos/velocidades); el modelo del servo es de 1.er orden (supuesto). El retardo tiene dispersión de ±8 ms entre pulsos.
- Sin medir todavía: la latencia del lazo completo corriendo (cómputo RPi + ciclo real), el retardo a velocidades altas (≥800 pasos/s) y a otros ángulos, y la zona de carga alta (la rigidez cambia con la carga).
- El retardo medido incluye el sondeo del firmware (~5 ms): es un punto donde modificar el firmware de motores podría ganar margen (autorizado por Luis el 2026-11-18, no hecho).

## Fuentes
Datos y scripts: `control/identificacion/ensayo_B_respuesta_dinamica.py`, `graficar_ensayo_B.py`, `identificar_servo_ensayo_B.py`; Ensayo A: `reportes/2026-11-05_ensayo_A_corridas_y_fallos_usb.md`; simulación: `control/simulacion/rt_vs_ilc_latencia.py`.
