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
- **Defecto propio encontrado y corregido:** los lectores usaban `ser.read(256)`, que bloquea hasta juntar 256 B (~32 ms a ~8 kB/s). La corrida 1 mostró ráfagas de 33 ms (artefacto). Con `read(in_waiting or 1)` (corrida 2): intervalo entre paquetes p50 1.00 ms, p99 1.93 ms, máx 5.6 ms. `LectorFzUART` (lazo de control) tenía el mismo defecto → habría añadido hasta ~32 ms de retraso a Fz (margen calculado para Kp=15: 35 ms). Corregido en R2, vigilante, preflight y `LectorFzUART`; el lazo con la fuente UART **no se ha vuelto a probar** tras el cambio.

## Limitaciones
- El panel "tiempo entre paquetes" de la figura `R2_vs_L3_limpio.png` es de la corrida 1 (lector con el defecto): ignorarlo. El tiempo es el de llegada al RPi, no el de conversión del ADC.
- La referencia de la laptop viene del visor USB a 100/s (decimado por el firmware), no de 1000/s.
- Una sola sesión, 2 corridas; sin comparar con NetForce ni con masas en el RPi (R6 pendiente).
- Qué distingue la laptop del RPi (cargador de la laptop, fuente del RPi, GND compartido, motores/drivers energizados, AMTI) **no se ha probado**: son candidatos, no causas.

## Fuentes
Datos: `pruebas/resultados/etapa2/R2_lecturas_20261118_111801.csv`, `…111911.csv`, `L3_vacio_laptop_t10-24s.csv`; figura `pruebas/resultados/etapa2/figuras/R2_vs_L3_limpio.png`. Plan: `INICIO_RPI.md`; Etapa 1: `reportes/2026-11-18_etapa1_laptop_adc_esp32.md`.
