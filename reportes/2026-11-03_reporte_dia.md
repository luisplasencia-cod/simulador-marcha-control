# Reporte del día — 2026-11-03

Continuación de la etapa de control del simulador de marcha (sesión en el Raspberry Pi).

## 1. Estado del RPi
- Luis reparó el RPi tras el incidente del 2026-11-02. Sesión gráfica en **Wayland (`rpd-labwc`)** para recuperar el modo táctil (`/etc/lightdm/lightdm.conf`); el monitor (`herramientas/monitor_gaitsim.py`) abre bien bajo Wayland.
- ADS1256 responde (STATUS=0x30, MUX/ADCON/DRATE leídos de vuelta correctos). **ESP32 de motores: NO conectado hoy** (no hay `/dev/ttyUSB0`).
- **Observación a revisar:** AIN0 (Fz del AMTI) dio −55 mV con 55 mV pico a pico en el diagnóstico (el 2026-11-02 estaba estable en +38.9 mV). Apunta a conexión/estado del AMTI; no resuelto.

## 2. Latencia de adquisición RPi + ADS1256 (Paso 2) — MEDIDA
Sin video (Luis no puede grabarlo), así que se usó un **escalón eléctrico**: GPIO27 del RPi → divisor 10k/10k → AIN1 (vs AINCOM). Mismo reloj (`perf_counter_ns`) para el flanco y para la detección. Script: `pruebas/medir_latencia_gpio_adc.py`; datos: `pruebas/latencia_gpio_adc.csv`.
- Niveles: bajo 47 mV, alto 1613 mV (salto 1.566 V). 1000 SPS.
- n = 200 (100 subidas + 100 bajadas), 0 fallos.

| Punto del escalón | Media | σ | Máx |
|---|---|---|---|
| 50 % | 1.61 ms | 0.28 ms | 2.12 ms |
| 90 % | 2.40 ms | 0.28 ms | 2.90 ms |

- Incluye: filtro digital del ADS1256 + SPI + software Python. Subida y bajada sin diferencia relevante.
- **No incluye** el retardo del amplificador analógico del AMTI (sale del manual AMTI; no medido).
- Incertidumbre de t0: se toma justo antes de `GPIO.output()` (cota superior, decenas de µs).
- Un primer intento tenía un error en el umbral del 90 % de las bajadas (disparaba al 10 %); corregido antes de reportar.
- Conexión del divisor: **temporal** (`esquemas/amti_ads1256_rpi/CONFIGURACION_ACTUAL.md`).

## 3. Cambios de código
- `pruebas/medir_latencia_gpio_adc.py` (nuevo).
- `pruebas/medir_latencia_escalon_amti.py`: `t` se toma después de leer (antes sesgaba hasta 1 ms).

## 4. Latencia acumulada hasta ahora
| Tramo | Valor | Estado |
|---|---|---|
| Amplificador AMTI | — | pendiente (manual) |
| ADS1256 + SPI + Python | 1.6 ms (50 %) / 2.4 ms (90 %) | medido |
| RPi ↔ ESP32 (RTT, incl. polling 5 ms del firmware) | 5.97 ms | medido |
| Cómputo RPi del controlador | — | pendiente |
| Ejecución en ESP32 (comando → motor) | — | pendiente |
Parcial ≈ 8–9 ms. El umbral tolerable lo da la simulación (tiempo real vs ILC); sin él no se concluye.

## Pendiente
1. Simulación de control en tiempo real vs ILC con la latencia como variable (no requiere hardware).
2. Revisar AIN0 inestable (con el monitor abierto).
3. Repetir offset con el plato vacío y calibración con pesas (`pruebas/calibracion_pesas.py`, sin ejecutar); revisar la pérdida de muestras del monitor (≈928/s vs 1000).
4. Retardo del amplificador del AMTI desde el manual.
5. Conectar el ESP32 de motores para el Paso 3 (latencia total).
6. Respuesta de Dante Elías y confirmación de la asesora (sin novedad).
