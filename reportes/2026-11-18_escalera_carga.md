# Escalera de carga del lazo de Fz en Y (misma posición, solo vertical) — 2026-11-18

## Objetivo
Subir de a poco desde 6 kg hacia 80 kg (decisión de Luis) en la misma posición (pie plano 0°, X y ángulo quietos), midiendo seguimiento, rigidez real a más carga y picos frente a NetForce, antes de integrarlo con la trayectoria.

## Escalón 10 kg (12:32:42–12:33:22, reloj del RPi)
**Metodología:** `control/lazo_fz_tiempo_real.py --peso_sujeto_n 98.1 --fmax_n 150 --hueco_mm 45 --extra_mm 30 --hueco_remedido --angulo_deg 0 --n_ciclos 3 --v_max 3000 --fuente_fz uart --puerto_fz /dev/ttyAMA0 --ejecutar` (Kp 10, k asumido 26.4 N/mm). Luis con NetForce en cero. Log `control/telemetria/registros/2026-11-18_123242_fz.csv`; salida `pruebas/resultados/etapa2/salidas/escalera_10kg_20261118.txt`; figura `reportes/figuras/2026-11-18_escalera_10kg.png`.
**Resultado (medido):**
- Completó las 3 pisadas sin abortar; contacto a 57.2 mm; Y volvió a su inicio. |u| máx 1027 / 2086 / 1320 pasos/s (bajo el tope de 3000).
- **Error real r−F (RMS): 11.8 → 15.4 → 7.8 N** (10 → 13 → 6.7 % del pico): NO bajó de forma monótona.
- **Picos del ADC:** pico 1 = 114.8 / 117.4 / 122.2 N, valle = 66.6 / 66.8 / 65.0 N, pico 2 = 118.3 / 119.0 / 118.1 N (objetivo 113 / 70 / 116). Zona media (1–3 s) dentro de ±5 N en las tres.
- **Anomalía en la carga inicial (0–0.6 s), no repetible:** en la pisada 1, Fz se quedó plana en ≈25 N durante ≈370 ms mientras el lazo ordenaba bajar (hasta 2086 pasos/s): 8.7 mm de descenso ordenado subieron Fz solo de 29 a 83 N (≈6 N/mm), frente a 4.0 mm → de 19 a 117 N (≈24 N/mm) en la pisada 2 y 4.6 mm → 12 a 86 N en la pisada 0 (que tuvo 120 ms plana). Faltan ≈4–5 mm en la pisada 1. Como no se repite, el ILC aprendió de ella y **sobrecorrigió en la pisada 2** (Fz por encima del objetivo, hasta 122 N, error −20 N en 0.3–0.5 s).
- **Causa NO determinada.** Candidatos (ninguno verificado): holgura mecánica del eje vertical o del adaptador del pie al invertir el sentido (cadena/husillo/pirámide), deslizamiento del pie sobre el plato, comportamiento del firmware al invertir el sentido (pero las tres pisadas empiezan tras una inversión similar, +836 y +944 pasos/s, y solo una muestra el efecto fuerte). Con las 60 N de la mañana el efecto era menor (atraso inicial 110→50 ms).
- **NetForce:** pendiente de lo que Luis leyó.
**Limitaciones:** una corrida de 3 pisadas; el desplazamiento es el ORDENADO (no medido): sin sensor de posición no se puede separar holgura de deslizamiento.
**Qué sigue (propuesta):** repetir 10 kg con más pisadas para ver si la anomalía se repite y con qué frecuencia, y que Luis mire el pie/adaptador y el carro vertical en la carga inicial, antes de subir a 20 kg. No subir de escalón con una anomalía sin entender.

### Observación de Luis tras el primer 10 kg
"con el 10 ha sido correcto y los motores normal … NetForce se ha visto bien": no vio nada anómalo (sin valores numéricos de NetForce).

### Repetición 10 kg × 6 pisadas (12:35:13–12:36:08, reloj)
Misma orden con `--n_ciclos 6`. Log `control/telemetria/registros/2026-11-18_123513_fz.csv`; figura `reportes/figuras/2026-11-18_escalera_10kg_6pisadas.png`; salida `pruebas/resultados/etapa2/salidas/escalera_10kg_6pisadas_20261118.txt`.
- **Error real RMS: 11.5 → 6.8 → 5.9 → 5.2 → 4.6 → 4.5 N** (baja monótono; 3.9 % del pico al final). |u| máx ≤ 1319 pasos/s.
- **La anomalía NO se repitió:** tiempo plano (<30 N) al inicio 120 ms en la pisada 0 (como toda primera pisada) y 50–70 ms en las demás; rigidez aparente en la carga inicial 21–25 N/mm (16 en la pisada 0). En total 1 caso fuerte en 9 pisadas a 10 kg; causa sin determinar.
- **Corrección de método:** el "pico" (máximo) y el "valle" (mínimo) de una señal con ruido σ≈2.6 N salen sesgados ±≈2σ (picos 2–4 N sobre el objetivo, valle 4–5 N bajo él en todas las corridas): NO es un error del control; usar el RMS (o un ajuste suavizado) para juzgar.
**Decisión:** pasar a 20 kg (pico 231 N, tope 280 N, v_max 5000, 6 pisadas).

## Escalón 20 kg × 6 pisadas (12:36:34–12:37:29, reloj)
`--peso_sujeto_n 196.2 --fmax_n 280 --n_ciclos 6 --v_max 5000` (resto igual). Log `control/telemetria/registros/2026-11-18_123634_fz.csv`; figura `reportes/figuras/2026-11-18_escalera_20kg.png`; salida `pruebas/resultados/etapa2/salidas/escalera_20kg_20261118.txt`.
- Completó; contacto a 57.5 mm; Y volvió a su inicio.
- **Error real RMS: 21.5 → 10.8 → 8.4 → 7.7 → 7.1 → 7.1 N** (3.1 % del pico de 231 N al final; en % es mejor que 10 kg).
- Picos ≈ 225–236 N (objetivo 226/231; ver nota del sesgo max/min). |u| máx 2206 → 2740 pasos/s (34 mm/s), crece pisada a pisada (el ILC adelanta la acción).
- **Sin anomalía en la carga inicial** (tiempo plano 10–20 ms salvo la pisada 0, 90 ms). Rigidez aparente en la carga inicial **23–28 N/mm** (19.8 en la pisada 0): casi igual que a 10 kg → hasta ≈200 N la prótesis NO se vuelve claramente más rígida.

## Escalón 40 kg — intento 1 ABORTADO por el límite de descenso (12:37:56–12:38:23, reloj)
`--peso_sujeto_n 392.4 --fmax_n 560 --n_ciclos 6 --v_max 9000 --hueco_mm 45 --extra_mm 30`. Log `control/telemetria/registros/2026-11-18_123756_fz.csv`; figura `reportes/figuras/2026-11-18_escalera_40kg_abortada.png`.
- Abortó en la pisada 0 a t = 0.56 s con Fz ≈ 335 N: `descenso 75.0 mm >= maximo 75 mm`. Detuvo el eje y Y volvió a su inicio (contador relativo 0). |u| máx 4057 pasos/s.
- **Causa (entendida): el límite de descenso total (hueco declarado 45 + margen 30 = 75 mm) era chico para esta carga**: contacto a 57.4 mm + compresión ≈ 13 mm hasta 335 N (rigidez aparente 23.8 N/mm) = ≈ 70 mm, y para el pico de 462 N harían falta ≈ 19 mm (≈ 76 mm total). Es la protección actuando como se diseñó, no una falla. El margen de 30 mm se había elegido con cargas bajas.
- **Corrección:** `--extra_mm 60` (límite total 105 mm). Justificación: con 80 kg y ≈ 24 N/mm la compresión sería ≈ 40 mm; el tope de fuerza sigue siendo la protección principal (el pie no puede bajar más sin subir la fuerza). Elección de diseño, no medida.
