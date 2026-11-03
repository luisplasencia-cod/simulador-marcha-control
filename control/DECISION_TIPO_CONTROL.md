# Tipo de control para Fz y Fy — propuesta PROVISIONAL (2026-11-03)

**Estado: propuesta con respaldo parcial, NO decisión cerrada.** Pendiente de Luis y de la asesora. Se apoya en la simulación (`simulacion/NOTAS.md`; objetivo = curva real de Gutenberg, planta con supuestos que se barren) y en la latencia medida. Lo marcado *(razonamiento)* es argumento propio, no resultado de la simulación ni de literatura leída.

## Propuesta
**Control híbrido por eje (Fz vertical, Fy horizontal): lazo de realimentación de fuerza en tiempo real (RPi, AMTI) como base + ILC que aprende ciclo a ciclo encima.** No ILC solo, no tiempo real solo.

## Por qué (evidencia y límites)
| # | Argumento | Respaldo |
|---|---|---|
| 1 | El tiempo real **solo** deja un error de seguimiento grande: llega tarde a la curva (≈ 10.8 %BW a Kp=10; 5.5 a Kp=20) | simulación, panel (a)(b) — bajo supuestos |
| 2 | Subir la ganancia para arreglarlo choca con la latencia: T máx 60 ms a Kp=10, 23 ms a Kp=20, 6 ms a Kp=40 | analítico, margen de fase 45° — depende de τ servo supuesto |
| 3 | ILC lleva el error repetible a ≈ 0.3 %BW en ~12 ciclos y tolera latencia hasta ~60 ms con error < 1 %BW (2.9 a 100 ms, inestable hacia 130) | simulación, panel (b)(c) |
| 4 | La marcha simulada **se repite por diseño** (trayectoria capturada, ciclos iguales a x6): es la condición que ILC necesita | CLAUDE.md (arquitectura) |
| 5 | Lo que se compara cambia la planta: cada prótesis tiene rigidez/amortiguamiento distintos. Un control en tiempo real con prealimentación necesita conocer esa rigidez; ILC **aprende sin identificarla** | *(razonamiento)*; la sensibilidad a k se vio solo parcialmente (k real = 0.8 del modelo) |
| 6 | Hace falta realimentación debajo del ILC porque ILC no corrige lo que no se repite dentro del ciclo (riesgo 4 del proyecto) y para estabilizar el lazo | CLAUDE.md riesgo (4); simulación panel (d) (pulso pequeño) |
| 7 | ILC ≪ RT puro se mantiene al barrer servo (10–50 ms), rigidez (0.5–1.5) y apoyo (3–5 s): RT 5.7–16.8 %BW, ILC 0.2–1.3 %BW | simulación, sensibilidad |
| 8 | La latencia medida hoy (≈ 8–9 ms parcial) **no obliga** a abandonar el tiempo real a ganancia moderada | medición + simulación |

## Qué cambiaría la propuesta
- Variabilidad ciclo a ciclo alta (prótesis activa prototipo, holguras) → ILC aprende poco: pesar más el tiempo real + prealimentación.
- Latencia total medida ≫ 30 ms (con cómputo RPi y ESP32) → bajar Kp; el ILC pasa a hacer casi todo el seguimiento.
- Impacto de talón o rigidez que cambia dentro de la pisada → perturbación no repetible: más realimentación, más ganancia, o ILC con filtro más conservador.
- Aprendizaje de ~10 ciclos (≈ 40 s a ciclo de 4 s) inaceptable para el protocolo de ensayo → revisar.

## Restricciones que el control debe respetar (del proyecto)
- Horizontal (Fy): nunca retrocede → saturar la corrección y verificar con el sensor de posición.
- Carga máxima: pico 1500 N (decidido por Luis) → limitar la corrección aprendida.
- Fz, Fy y sagital se ejecutan a la vez en el mismo ciclo; primero Fz y Fy, sagital fijo por ahora.
- Opcional (a decidir con la asesora): ANFIS-PID como mejora de la parte de realimentación, solo después de tener el ILC básico.

## Precedentes (DOI verificado, lectura **sin confirmar** → no usar como respaldo final)
Aubin 2012 (lógica difusa sobre GRF vertical), Insam 2021 (hardware-in-the-loop). Ninguno compara ILC con tiempo real en este tipo de simulador.

## Cómo confirmarlo (en orden)
1. Latencia restante: AMTI (manual), cómputo RPi, ESP32 (Paso 3).
2. Identificar servo vertical y rigidez de contacto con ≥ 2 prótesis.
3. Repetir el barrido de la simulación con esos valores + perturbación de impacto.
4. Probar híbrido en el simulador real (Fz primero) contra el lazo abierto actual (RMSE/correlación, como en el artículo).
