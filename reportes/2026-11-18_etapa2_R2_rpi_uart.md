# Etapa 2 · R0–R2 en el RPi: ESP32 de lectura por UART2 (2026-11-18)

## Objetivo
Probar por primera vez la ruta ESP32 de lectura → UART2 (GPIO17→pin 10, GND→pin 6) → RPi 5, y comparar el ruido con el de la Etapa 1 (laptop). Criterio de R2 (`INICIO_RPI.md`): σ en el RPi ≈ σ en la laptop (≈ 0.75 N). Plato vacío; no se movió ningún eje ni se abrió `ttyUSB0`.

## Metodología
`pruebas/etapa2_rpi.sh preflight` y `r2 20000` (20 s, puerto `/dev/ttyAMA0`, 115200). Referencia de la laptop: tramo limpio de `pruebas/resultados/visor_fz_20261118_110422.csv` (t = 10–24 s, plato vacío, a 100 muestras/s) → `pruebas/resultados/etapa2/L3_vacio_laptop_t10-24s.csv`. σ robusta = 1.4826·MAD.

## Resultado (medido)
- **UART2 funciona:** 1000 paquetes/s, 0 corruptos, 0 ceros salvo 1 lectura exacta 0.000 (índice 10929 de la corrida 1; no investigada).
- **Ruido peor que en la laptop:** corrida 1 (`R2_lecturas_20261118_111801.csv`): media −2.62 N, **σ 2.67 N (robusta 2.61)** vs laptop σ 0.78 N (robusta 0.82), media −1.78 N.
- **Causa de la diferencia (medido en la misma corrida):** línea de **60 Hz y armónicos** (60 Hz ≈ 2.4 N rms; 120/180/300 Hz entre 0.3 y 0.5 N rms). Quitando esas bandas por FFT, σ baja de 2.67 a **0.74 N** ≈ laptop. El ADC y el UART no son el problema; hay interferencia de red que entra en la configuración del RPi y no en la de la laptop. **Origen NO determinado.**
- **Corrida 2 (`…111911`) contaminada por una fuerza aplicada a mano por Luis** (≈ +80 N entre 10 y 14 s, confirmado por él); no usar para ruido. Fuera de ese evento: mediana −2.4 N, σ robusta 2.60 N, igual que la corrida 1.
- **Defecto propio encontrado y corregido:** los lectores usaban `ser.read(256)`, que bloquea hasta juntar 256 B (~32 ms a ~8 kB/s). La corrida 1 mostró ráfagas de 33 ms (artefacto). Con `read(in_waiting or 1)` (corrida 2): intervalo entre paquetes p50 1.00 ms, p99 1.93 ms, máx 5.6 ms. `LectorFzUART` (lazo de control) tenía el mismo defecto → habría añadido hasta ~32 ms de retraso a Fz (margen calculado para Kp=15: 35 ms). Corregido en R2, vigilante, preflight y `LectorFzUART`; **reprobado después con un puerto falso (pty, 1000 paquetes/s sintéticos):** `LectorFzUART.leer_n()` entrega un bloque de 7 muestras cada p50 7.2 ms / p99 7.4 ms / máx 8.0 ms (esperado 7 ms). Solo el lector; el lazo completo con UART real **no se ha probado**.

## Limitaciones
- El panel "tiempo entre paquetes" de la figura `R2_vs_L3_limpio.png` es de la corrida 1 (lector con el defecto): ignorarlo. El tiempo es el de llegada al RPi, no el de conversión del ADC.
- La referencia de la laptop viene del visor USB a 100/s (decimado por el firmware), no de 1000/s.
- Una sola sesión, 2 corridas; sin comparar con NetForce ni con masas en el RPi (R6 pendiente).
- Qué distingue la laptop del RPi (cargador de la laptop, fuente del RPi, GND compartido, motores/drivers energizados, AMTI) **no se ha probado**: son candidatos, no causas.

## Fuentes
Datos: `pruebas/resultados/etapa2/R2_lecturas_20261118_111801.csv`, `…111911.csv`, `L3_vacio_laptop_t10-24s.csv`; figura `pruebas/resultados/etapa2/figuras/R2_vs_L3_limpio.png`. Plan: `INICIO_RPI.md`; Etapa 1: `reportes/2026-11-18_etapa1_laptop_adc_esp32.md`.

## R3 — vigilante del ADC por UART, 10 min en reposo (2026-11-18, 11:20:29–11:30:30)
**Objetivo:** criterio de paso de la Etapa 2: 0 fallas del ADC/UART en reposo. **Duración acortada de 30 a 10 min por pedido de Luis (falta de tiempo):** el 30 era un número del plan, no una exigencia técnica; 10 min da evidencia más débil (las caídas históricas ocurrían unas pocas veces al día, y 10 min pueden no verlas).
**Metodología:** `pruebas/etapa2_rpi.sh r3 30`, detenido con SIGINT por PID a los 600 s; figura generada del CSV (`pruebas/resultados/etapa2/figuras/r3_vigilar_adc_esp32_uart_20261118_112031.png`, mostrada en la pantalla del RPi). Plato vacío, sin ejes en movimiento, ESP32 de motores sin abrir.
**Resultado (medido):** 600 s registrados; **0 CAIDO, 0 CEROS, 0 SATURADO, 0 CONGELADO**; 597 OK + 3 PICOS. Muestras/s entre 1000 y 1010 todos los segundos. Fuera de la intervención manual, mediana Fz estable (−2.41 N al inicio, −2.45 N al final: deriva −0.04 N en ~9 min), σ dentro de 1 s ≈ 2.6 N (la del 60 Hz, ver arriba).
**Intervención manual (Luis, confirmado por él):** fuerzas sobre el plato ≈ 11:24:59–11:25:08 (~10 s, Fz hasta ≈60 N). Excluidas del criterio.
**Limitaciones:** (1) 10 min, no 30. (2) El vigilante etiqueta PICOS por distancia a la mediana de cada segundo: una carga **sostenida** sale como OK (solo 3 de los ~10 s de intervención salieron PICOS) → "OK" ≠ "plato en reposo". Para este criterio (caídas/ceros/congelado/saturado) no afecta. (3) No cubre el caso crítico histórico: caídas **con el servo Y en marcha** (R5).

## R4 y R5 — ESP32 de motores conectado, motores encendidos, servo Y en el aire (2026-11-18, ~11:34–11:37)
**Objetivo:** ver si la ruta nueva (ESP32 de lectura + UART) resiste lo que tiraba al ADC: el servo vertical en marcha (el 2026-11-10 con SPI directo: Fz entre −10 y +43 N sincronizada con el servo y luego caída del ADS1256). **Estado:** pie en 0° con 7 cm entre la planta y el suelo/plato (medido por Luis), prótesis acoplada; Luis autorizó el movimiento.
**Metodología:** `GET_POSITION` y `PING` por el único puerto USB-serie (`ttyUSB0` = ESP32 de motores; el de lectura va por UART2 desde la laptop). R2 de 20 s con los drivers encendidos y quietos. R5 = `pruebas/etapa2_rpi.sh r5`: Y baja y sube a 400/800/1600 pasos/s (0.5 s, ≤10 mm, neto 0), Fz por UART con tara, ADC iniciado antes de abrir el ESP32.
**Resultado (medido):**
- `PING`→`PONG`; `GET_POSITION` → `POSITION:0:4500:0`; `TRAJ_STATUS` → `IDLE`. **El contador de Y NO arrancó en 0 (4500) tras abrir el puerto; la causa no se investigó.** No es posición física.
- **R2 con motores encendidos y quietos:** σ 2.63 N, 60 Hz 2.28 N rms: igual que sin ellos (2.4 N). Los drivers encendidos no cambian la interferencia de 60 Hz.
- **R5: con Y en el aire a 400/800/1600 pasos/s, la mediana de Fz en movimiento quedó entre −0.3 y +0.3 N (mín −4.2, máx +2.9 N) y tras parar entre −0.4 y +0.5 N; sin corrimiento sostenido y sin caída del ADC.** El contador volvió a 4500. Datos: `pruebas/resultados/fuerza_vs_velocidad_y_uart_20261118_113657.json`, `pruebas/resultados/etapa2/R5_*.txt`.
**Defecto propio corregido antes de mover:** el retorno de seguridad de R5 y el lazo suponían contador Y = 0 al inicio. Con 4500, `verificar_contador` habría abortado en el primer chequeo y un aborto a mitad de descenso no habría devuelto Y. Ahora `ClienteVelocidadESP32` guarda `y0` al conectar y todo (control, verificación, retorno) usa `pos_y_rel()`. Probado en simulación y en R5 real (contador final = inicial).
**Limitaciones:** una sola corrida, ≤10 mm, en el aire; **el desplazamiento es el ordenado, no medido (solo cuenta pasos)**; el 2026-11-10 las caídas aparecieron tras *sesiones* con movimiento, así que una corrida limpia NO prueba que desaparecieron; el cableado cambió varias cosas a la vez (lectura por ESP32, entrada diferencial, protecciones ①-⑤, 5 V externo) y no sé cuál de ellas importó; 60 Hz sin explicar.
