# Escalera de carga 50 → 90 kg (x10, solo Y, pie plano 0°), abortos y oscilación — 2026-11-18 (tarde, RPi)

## Objetivo
Completar la escalera de carga del lazo cerrado de Fz en Y (50 a 90 kg) con la prótesis montada (pie a ~11 cm), comparar cada escalón contra el GRF estándar y encontrar qué falla (pedido de Luis). Solo Y en lazo cerrado; X y ángulo quietos (ángulo en 0): **con ángulo fijo solo se valida Y**, la precisión fina se exige al pasar a los 3 ejes.

## Metodología
- Script del proyecto sin modificar: `control/lazo_fz_tiempo_real.py` (ILC activo, Fz por UART `/dev/ttyAMA0`, SET_VEL v4). Orquestación nueva en el repo de la interfaz: `tools/escalera_paso.sh` (un escalón), `tools/escalera_cadena.sh` (cadena que mide hueco y corre cada escalón, se detiene al primer fallo), `tools/medir_hueco.py`, `tools/reporte_escalera.py`.
- **Escalas (no mezclar):** 10, 20, 30 y 40 kg se corrieron a **x6** (apoyo 3.69 s); 50 kg tuvo un intento a x6 (abortado) y se completó a **x10** (apoyo 6.15 s); 60–90 kg a x10.
- Antes de cada corrida cargada: **tara** con el pie en el aire (offset medido −4.9 a −5.5 N; `medir_hueco.py` rechaza la tara si el ruido pico a pico > 15 N), y el hueco al contacto medido por el ADC (el contador de Y se pierde al abrir el puerto del ESP32: no hace falta HOME). Se deja el pie 30 mm sobre el contacto; `extra_mm = 1.5 × compresión esperada` (25 mm a 50 kg, 39/46/52/59 a 60–90 kg).
- Parámetros: 50 y 60 kg Kp 8; 70, 80 y 90 kg Kp 5 (con Kp 8 a 70 kg el lazo oscilaba y abortó). 10 pisadas por escalón (50 kg: 6). Pico de referencia = 1.178 × peso (curva de Gutenberg escalada); tope de fuerza = min(1.25 × pico, 1300 N). Detector de saltos sin tocar (umbral escalado con la carga).
- Luis tuvo la mano en el paro y NetForce en cero. **No se modificó firmware de ningún ESP32.**

## Resultado (medido)
| kg | escala | Kp | pico GRF N | F máx N | RMS 1.ª → última pisada N | v máx Y mm/s | compresión mm | rigidez aparente N/mm | resultado |
|---|---|---|---|---|---|---|---|---|---|
| 50 | x10 | 8 | 578 | 584 | 30.6 → 10.7 (6 pisadas) | 38 | 22.9 | 25.5 | completado |
| 60 | x10 | 8 | 693 | 724 | 35.5 → 15.6 | 48 | 25.4 | 28.5 | completado |
| 70 | x10 | 5 | 809 | 816 | 60.2 → 20.6 | 46 | 29.3 | 27.9 | completado |
| 80 | x10 | 5 | 924 | 938 | 63.7 → 21.5 | 51 | 29.9 | 31.4 | completado |
| 90 | x10 | 5 | 1040 | 1047 | 68.3 → 27.3 | 56 | 31.6 | 33.1 | completado |

Figura: `escalera/20261118_rpi/reporte_final/comparacion_grf.png` (Fz medida vs GRF estándar, pisada 1 y última, por kg); tabla en `resumen_escalera.md`. La última pisada sigue al GRF; la primera arranca retrasada (el ILC parte de cero en cada corrida). Y volvió a 0 pasos en todas las corridas completadas. Nota: el pico de ~1000 N visto en 80–90 kg es el objetivo (924 y 1040 N), no un error.

**Abortos y fallos de la tanda (cada uno con su causa):**
1. **50 kg x6, Kp 10:** salto de 49 N > 46 N (transitorio real, crece con la velocidad) → se bajó a x10 y Kp 8.
2. **50 kg, corrida 2:** corte USB del ESP32 de motores con el pie a ~505 N; se alivió con dos subidas supervisadas.
3. **60 kg, 1.er intento:** `descenso 55 mm >= máximo 55 mm` (extra_mm fijo de 25 mm insuficiente) → `extra_mm` escala con la carga.
4. **70 kg Kp 8:** `lectura anomala (F=769.7 N, previa 852.4 N)`: el lazo oscila a ~7 Hz con picos de ±100 N alrededor del objetivo (hasta 903 N vs 809 N). Abort legítimo; **no se subió el umbral**. Con Kp 5 completó.
5. **80 kg Kp 5 (1.er intento):** pisadas 0–4 bien (RMS 70.7 → 27.9 N) y luego `Input/output error(5)`. dmesg: `usb usb3-port1: disabled by hub (EMI?)` (sin subtensión, `throttled=0x0`). El retorno automático falló y el pie quedó a ~554 N: se alivió con dos subidas supervisadas (20 mm y 10 mm, Fz 551 → 64 → −6.6 N). El ESP32 reinició al reabrir el puerto: HOME perdido. Con el cable verificado por Luis, el 2.º intento de 80 kg y el 90 kg completaron sin cortes.

**Oscilación (análisis de las telemetrías):** error a >3 Hz en valor absoluto crece ~2.5× en 10 pisadas (60 kg: 7.9 → 15 N rms; 70 kg: 7.2 → 19.9 N) pese a que el filtro Q del ILC (Hanning, corte ≈1 Hz) ya existe: **no es falta de filtro**. En la bajada del primer pico, última pisada: 60 kg 8.3 Hz / 6.8 N; 70 kg 2.8 Hz / 19.9 N; 80 kg 6.4 Hz / 20.4 N; 90 kg 7.3 Hz / 31.0 N rms (≈2.5–3 % del pico, ∝ carga). La velocidad de Y también oscila (2–6 mm/s rms).

## Limitaciones
- **Causa de la oscilación sin confirmar.** Hipótesis: resonancia estructural/del actuador excitada por el lazo (amplitud ∝ carga, frecuencia 6–8 Hz). Prueba propuesta que respeta el ILC: misma carga con dos Kp (3 y 5); si la amplitud a ~7 Hz no cambia, es resonancia (remedio: filtro de muesca sobre Fz o perfil de velocidad más suave). Pendiente del OK de Luis. Luis exige que el lazo no oscile con ningún material (residual limb más blando/rígido, silicona 30).
- Kp 5 a 70–90 kg y Kp 8 a 50–60 kg no es una comparación controlada (dos cosas cambian con la carga); 10 pisadas por escalón, una corrida por escalón.
- Solo ángulo 0 y pie pasivo `pie_pasivo_1`; 10–40 kg a x6 y 50–90 kg a x10 no son comparables en velocidad. Compresión/rigidez calculadas con la primera muestra como contacto (aproximación).
- El corte USB (EMI en el cable/hub) sigue siendo causa probable pero no demostrada de ambos cortes; el cable ya fue verificado por Luis y no hubo cortes después. Mitigación por probar sin carga: abrir el puerto con DTR/RTS apagados para no reiniciar el ESP32.
- HOME perdido en el ESP32 tras aliviar el pie: repetirlo SIN prótesis montada antes de la fase de 3 ejes.

## Fuentes
- Salidas: `escalera/20261118_rpi/*_salida.txt`; telemetría `control/telemetria/registros/2026-11-18_{152829,153832,154240,155042,155241}_fz.csv` (+ `.meta.txt`).
- Repo de la interfaz (`~/Projects/gaitsim-control`): `tools/escalera_*.sh`, `tools/medir_hueco.py`, `tools/reporte_escalera.py`, `logs/escalera_cadena*.log`, commits 3e307b1…6590d8b; `CLAUDE.md` (bloque de escalera).
- Informes previos: `2026-11-18_escalera_10_a_50kg_y_escala.md`, `PROBLEMA_PENDIENTE_desconexion_USB_ESP32.md`.
