# Simulación RT vs ILC con latencia — notas (2026-11-03)

Script: `rt_vs_ilc_latencia.py` · figura: `rt_vs_ilc_latencia.png` · salida numérica: `salida_consola.txt`.

## ⚠️ Qué es y qué NO es
Modelo **con supuestos**, no identificado del simulador real: servo de 1.er orden (τ=20 ms), contacto con rigidez efectiva (k real = 0.8 del modelo), ciclo de 4 s (≈x6), referencia de doble pico **sintética** (picos 97.4 y 102.5 %BW al 19 y 45 %, de la curva propia del simulador; la forma intermedia es inventada), perturbación = pulso de 3 %BW. Sirve para ver **cómo escala el error con la latencia** y qué parámetros hay que medir; **no decide por sí solo** tiempo real vs ILC.

## Resultados (bajo esos supuestos)
1. **Límite de latencia por estabilidad (analítico, margen de fase ≥ 45°):** depende de la ganancia del lazo. Kp=5 → 138 ms; Kp=10 → 60 ms; Kp=20 → 23 ms; Kp=40 → 6 ms; Kp=80 → 0 ms. La latencia **limita cuánto ancho de banda de lazo se puede pedir** (Kp=20 ≈ 3 Hz).
2. **Tiempo real solo-realimentación** (Kp=10, T=10 ms): error RMS ≈ 9 %BW, dominado por el atraso por ancho de banda, **no** por la latencia (a Kp=5: 17, Kp=10: 9.2, Kp=20: 4.4 %BW). Subir Kp reduce el error pero acerca el límite del punto 1.
3. **RT + prealimentación de la derivada de la referencia** (usa k estimada, 20 % de error): RMS 1.4 %BW a T=10 ms, empeora al crecer T (3.5 a 60 ms).
4. **ILC** (realimentación Kp=10 + corrección aprendida por ciclo): RMS ≈ 0.3 %BW tras ~10 ciclos y casi insensible a T hasta ~100 ms (0.28 → 0.92); con perturbación no repetible 0.5–1.5 %BW. Se vuelve inestable hacia T ≈ 130 ms (el adelanto `m` y la ganancia del ILC no se re-sintonizaron: no es un límite fino).
5. Artefacto a tener presente: en RT solo-realimentación el RMS **baja** al subir T hasta ~100 ms (el retardo adelanta la fuerza real y compensa el atraso). No significa que el retardo ayude: el lazo pierde margen de fase.

## Lectura honesta
- Con la latencia hoy medida (~8–9 ms parcial, quizá 15–30 ms con cómputo y ejecución del ESP32), **la latencia no es el factor dominante** si el lazo se diseña a Kp≈10; sí lo sería si se exige Kp≥20–40.
- El resultado depende de supuestos no medidos: τ del servo, rigidez de contacto (según prótesis, y varía durante la pisada), impacto de talón (no modelado), fricción/holguras, saturación de velocidad del husillo. **No concluir RT vs ILC** hasta identificarlos.
- Perturbación realista (impacto de talón, rigidez que cambia con la prótesis) es lo que favorecería RT sobre ILC; aquí solo se probó un pulso pequeño.

## Qué hace falta para cerrarlo
1. Identificar τ del servo vertical y rigidez de contacto con la prótesis (escalón de velocidad + AMTI + sensor de posición vertical, cuando estén instalados).
2. Latencia restante: AMTI (manual), cómputo RPi, ejecución ESP32 (Paso 3, requiere ESP32 conectado).
3. Repetir el barrido con parámetros medidos y perturbación de impacto.
