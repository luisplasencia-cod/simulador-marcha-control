# Punto de entrada para Claude en el Raspberry Pi

Si acabas de clonar este repo en el RPi y es tu primera vez aquí: lee esto completo antes de hacer nada.

## Qué es este repo
Tesis de control del simulador de marcha (Luis Plasencia, PUCP). Contexto completo del proyecto en `CLAUDE.md` (léelo primero, siempre). Detalle de auditorías/búsquedas pasadas en `HISTORIAL.md`.

## Estado físico ahora mismo (2026-11-02)
**Hay 2 ESP32 distintos, no confundir:**
1. **ESP32 de control de motores** (`Codigo ESP32 MOV/platformIO_control_trayectoria_v1/`) — mueve los 3 ejes, tiene `PING`→`PONG` para medir latencia. RPi↔este ESP32: por cable serial, 115200 baud.
2. **ESP32 dedicado al ADC** (`Codigo ESP32 ADS1256/platformIO_medicion_sensores_v1/`) — **arquitectura corregida hoy**: el RPi **no** lee el ADS1256 directo por SPI/GPIO. Este ESP32 lee el AMTI vía ADS1256 por su propio SPI (pines del ESP32: CS=32, DRDY=33, SCLK=27, MISO=25, MOSI=26) y manda el valor de fuerza ya calculado al RPi por UART2 (115200 baud), paquete `<fuerza_N>`. El `esquemas/amti_ads1256_rpi/CONFIGURACION_ACTUAL.md` y `pruebas/leer_ads1256_fz.py` (RPi lee el ADS1256 directo) quedan **obsoletos/no usar** salvo que Luis confirme que ese cableado directo también existe en paralelo — por defecto, usar el ESP32 dedicado.
   - **Diferencia de cableado importante:** este firmware usa MUX diferencial AIN1(+)/AIN0(−); lo documentado antes era single-ended AIN0 vs AINCOM/GND. Son dos conexiones físicas distintas al ADS1256, no mezclar.
   - Sensibilidad usada aquí: 1.7631 mV/N (antes se usaba 1.7 V/1000N, redondeado).

## Qué hacer, en orden
1. **Instalar dependencias:** `pip install pyserial matplotlib`.
2. **Confirmar que el ESP32 dedicado al ADC ya tiene el firmware flasheado:** `Codigo ESP32 ADS1256/platformIO_medicion_sensores_v1/` — si Luis aún no lo flasheó, ese paso lo hace él o la laptop (PlatformIO, cable USB), no el RPi. El RPi solo necesita el puerto serial de este ESP32 conectado para el Paso 5.
3. **Medir latencia RPi↔ESP32 (el de motores):** `python pruebas/medir_latencia_ping_pong.py --puerto /dev/ttyUSB0 --n 100` (ajusta el puerto con `ls /dev/tty*` si no es ese). Genera un CSV.
3. **Graficar el resultado:** `python pruebas/graficar_latencia.py --csv latencia_ping_pong.csv`. Genera un PNG (histograma + serie por intento).
4. **Llenar el plan de prueba** en `pruebas/2026-11-02_latencia_amti_rpi_esp32.md` con los resultados — no dejarlo solo en el CSV/PNG, documentar ahí también.
5. **Lectura de Fz (AMTI vía ADS1256, por el ESP32 dedicado):** `pip install pyserial`, luego `python pruebas/leer_fz_esp32_ads1256.py --puerto /dev/ttyUSB1 --n 200` (ajustar puerto; es un puerto serial distinto al del ESP32 de motores — dos cables USB/UART separados). **No probado en hardware real.** Con 0 N reales debería dar ~0 N (si no, hay offset de cero pendiente). Si necesitas leer el ADS1256 directo por SPI del RPi en vez de por el ESP32 dedicado, existe `pruebas/leer_ads1256_fz.py`, pero verifica primero con Luis cuál cableado es el vigente — no asumas los dos a la vez.

## Reglas del proyecto (no te las saltes)
- Verificar datos de hardware contra fuente real (datasheet, etiqueta física, medición) — nunca de memoria. Ya hay precedente de esto en el repo, sigue el mismo estándar.
- No redactar síntesis/texto de tesis salvo pedido explícito — Luis decide el enfoque, tú organizas/ejecutas lo técnico.
- Git: commitear y hacer `git push` cuando termines algo con sentido (no cada línea), para que la laptop de Luis vea el avance.

## Firmware del ESP32 — importante
Las actualizaciones al firmware de control de motores (`Codigo ESP32 MOV/.../main.cpp`) se hacen **desde la laptop** (sesión de Claude ahí), no desde aquí — ahí es donde está el cable USB al ESP32 para flashear con PlatformIO. Si necesitas un cambio de firmware, dilo en el commit/push y Luis lo coordina con esa sesión; no asumas que tú vas a flashear el ESP32 desde el RPi.
