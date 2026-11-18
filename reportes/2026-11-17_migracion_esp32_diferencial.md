# Reporte: migración del ADS1256 a ESP32 dedicado + entrada diferencial, y cableado físico

## Objetivo
Decidir y dejar lista (firmware, lector, esquema) una ruta alternativa de lectura del ADS1256 —host ESP32
dedicado en vez de SPI directo desde el RPi, entrada diferencial AIN1/AIN0 en vez de single-ended—, a pedido
de Luis, quien reporta haber probado antes esta combinación con mejor resultado. Cubre del 2026-11-08 (cierre
del reporte `2026-11-08_fix_firmware_run_set_vel.md`) al 2026-11-17.

## Metodología
1. Restaurar y validar el firmware original del ESP32 de motores (versión de `platform` de PlatformIO sin
   fijar causaba binarios no reproducibles entre máquinas — ver `2026-11-10_restauracion_firmware_original.md`).
2. Medir el lazo de Fz con contacto real sobre la arquitectura vigente en ese momento (RPi lee el ADS1256
   directo por SPI) para agotar esa ruta antes de cambiarla.
3. Diagnosticar por qué el ADS1256 seguía cayéndose con el servo en marcha; decidir protecciones (independientes
   del host que lee el SPI).
4. Revisar en Amazon el ADC del producto final (AD7606, 8 canales simultáneos) — hilo aparte, sin bloquear Fz.
5. A pedido de Luis (2026-11-17), examinar el código ya probado de `platformIO_medicion_sensores_v1.zip` y
   decidir la migración a ESP32 dedicado + diferencial; regenerar el esquema; dejar firmware y scripts
   preparados sin hardware disponible en la sesión.
6. Verificar el esquema conexión por conexión (pedido explícito de Luis) antes de que él cableara.
7. Luis cablea físicamente según el esquema (mismo día).

## Resultado
- **Firmware restaurado y validado:** `platform = espressif32 @ 7.0.1` reproduce el binario original
  (mismo `esp-idf: v4.4.7`, mismos hash de `bootloader.bin`/`partitions.bin`). Parche v3 (watchdog dentro del
  ISR del eje continuo) pasa la regresión 5/5 con esa versión, con la misma latencia que el original
  (`GET_POSITION` 4.97 ms).
- **Primer `SET_VEL` real en el eje Y, en el aire:** ±2.5 y 5 mm, contador y watchdog (32 pasos = 400×80 ms)
  como esperado; Luis confirma visualmente que velocidad positiva sube Y.
- **Incidente corregido:** el lazo de Fz movía el eje X en vez de Y (el eje se mandaba como texto `"Y"`, el
  firmware hace `atoi("Y")=0`=X). Corregido con una guarda que exige el eje como entero 0/1/2 en
  `control/lazo_fz_tiempo_real.py` (`ClienteVelocidadESP32._cmd` y `.set_vel`).
- **3 corridas reales del lazo de Fz con contacto: ninguna llegó a tocar la plataforma.** Abortos por ruido
  del ADC en reposo (σ≈5 N, 5× lo normal), discrepancia sin explicar entre el contador del ESP32 y lo ordenado,
  y caída del ADS1256 (registros en 0, DRDY fijo en alto).
- **Hallazgo clave (en el aire, sin contacto):** con el servo Y en marcha, Fz se corre entre −10 y +43 N
  sincronizado con el movimiento (no proporcional a la velocidad) y 27–32 N persisten tras parar; el ADS1256
  se cae después de sesiones CON movimiento, no al solo abrir el puerto. Figura:
  `reportes/figuras/2026-11-10_fuerza_vs_velocidad_y_aire.png`.
- **Hipótesis principal (sin confirmar):** el cable RPi↔ESP32 no lleva VBUS, solo GND compartido — si el
  servo/freno perturba esa tierra al conmutar corriente, la diferencia se monta sobre la señal USB. El corte
  de los 4 puertos USB (2026-11-10, 16:57) fue un evento aparte; no se confirmó relación con las caídas del ADC.
- **Protecciones ①–⑤ decididas con Luis** (100 Ω en SPI; regulador 3.3 V propio para PDWN, alimentado de la
  misma fuente externa de 5 V; 1 kΩ en la entrada diferencial AIN0/AIN1; R5 2.2 Ω + C1 100 µF + C2 100 nF en
  la entrada de 5 V; GND de fuente/ADC/AMTI/ESP32 en un solo punto físico).
- **ADC del producto final: AD7606 elegido** (8 canales simultáneos, 16 bits); Reland (`amazon.com/dp/B0CLJGDZ4Y`)
  y Teyleten (`amazon.com/dp/B0FMFT1M9X`) resultaron ser la misma placa bajo distinto vendedor — sin comprar
  todavía, decisión pendiente de cierre con Luis.
- **2026-11-17 — decisión de arquitectura:** ADS1256 pasa de SPI directo (RPi) a un ESP32 nuevo y dedicado
  (distinto del de motores), entrada diferencial AIN1/AIN0 (rechaza mejor el ruido de modo común del servo
  que single-ended, aunque sigue siendo 1 sola lectura de Fz, no "dos canales a la vez"), transmitida al RPi
  por UART2 (protocolo `"<valor>"`, sin ACK). Firmware base: `platformIO_medicion_sensores_v1.zip` (código
  que Luis reporta ya probado antes), copiado a `control/firmware/lectura_ads1256_esp32_diferencial/` con un
  único cambio de código: la escala `FORCE_SENSITIVITY_MV_PER_N` de 1.7631f a 1.7665f (el MUX diferencial ya
  coincidía). Scripts nuevos del lado RPi: `pruebas/leer_ads1256_fz_esp32_uart.py`,
  `pruebas/vigilar_adc_esp32_uart.py` — ninguno probado en hardware. `INICIO_RPI.md` reescrito con el plan
  en fases A–G.
- **Esquema regenerado y verificado conexión por conexión** (pedido explícito de Luis): se encontró y corrigió
  un pin suelto (3V3 del ESP32, sin cable ni nota) y se agregó una nota aclarando que la alimentación de la
  placa (VIN/USB) es aparte de la fuente de 5 V externa del ADC, no dibujada. Commit `f49ca8f`.
- **Luis confirma haber cableado físicamente** la arquitectura completa del esquema (ESP32 + diferencial +
  protecciones ①–⑤) el mismo día. **No reporta haberlo energizado ni probado.**

## Limitaciones
- El cambio de host (RPi→ESP32) **no ataca la causa de las caídas del ADC si es analógica o de alimentación**
  — es independiente de quién lee el SPI; se hace por preferencia/experiencia previa de Luis, no como arreglo
  verificado. La hipótesis de tierra compartida por USB sigue sin confirmarse con medición directa.
  - **Dato que vuelve a aplicar sin cambios, porque las protecciones no son del host:** las protecciones ①-⑤
    (sección 3 de `INICIO_RPI.md`) protegen al chip, no dependen de si lee el RPi o el ESP32.
- Firmware, lector UART y vigilante nuevos: **cero pruebas en hardware** (sin RPi disponible en la sesión que
  los escribió). La validación RMSE/correlación contra el AMTI (hecha el 2026-11-03 para el lector directo,
  1.89 N) **no se traslada** a esta ruta.
- El cableado físico reportado por Luis **no fue verificado por mí** (sin acceso a hardware en esta sesión):
  pendiente confirmar pin por pin contra el esquema, y en particular que el regulador 3.3 V propio de PDWN
  (protección ②) esté armado como un circuito completo (IN/OUT/GND + 10 kΩ + 100 nF), no solo un cable.
- `control/lazo_fz_tiempo_real.py` y `herramientas/monitor_gaitsim.py` siguen leyendo por el camino SPI
  directo antiguo — adaptarlos a la ruta UART es la Fase G, todavía no hecha.
- La decisión de compra del AD7606 (AMTI de producto final) no se cerró; nada comprado.

## Fuentes
- Código base de la ruta UART: `C:\Users\chees\Downloads\platformIO_medicion_sensores_v1.zip` (aportado por
  Luis, "ya probado antes"; sin reporte de latencia medido en el repo — impresión de Luis, no dato).
- `esquemas/amti_ads1256_rpi/CONFIGURACION_ACTUAL.md` (confirma que los pines "GND junto a AINx" son AINCOM).
- `reportes/2026-11-10_restauracion_firmware_original.md` (detalle completo de la restauración de firmware,
  primer SET_VEL real, e intentos del lazo de Fz).
- `reportes/2026-11-10_limite_sclk_ads1256.md`, `2026-11-10_protecciones_ads1256_foros_y_sustituto_ferrita.md`,
  `2026-11-11_protecciones_decididas_y_seleccion_adc_simultaneo.md` (diagnóstico y protecciones del ADS1256,
  selección del AD7606).
- `esquemas/amti_ads1256_rpi/salida/esquema_protecciones_ads1256.png` (esquema vigente, commits `a93a344`
  y `f49ca8f`).
- `CLAUDE.md`, entradas fechadas 2026-11-17 (decisión de arquitectura, cableado físico confirmado por Luis).
