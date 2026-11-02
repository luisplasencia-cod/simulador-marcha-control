# Punto de entrada para Claude en el Raspberry Pi

Si acabas de clonar este repo en el RPi y es tu primera vez aquí: lee esto completo antes de hacer nada.

## Qué es este repo
Tesis de control del simulador de marcha (Luis Plasencia, PUCP). Contexto completo del proyecto en `CLAUDE.md` (léelo primero, siempre). Detalle de auditorías/búsquedas pasadas en `HISTORIAL.md`.

## Estado físico ahora mismo (2026-11-02)
- **Un solo ESP32 con este RPi: el de control de motores** (`Codigo ESP32 MOV/platformIO_control_trayectoria_v1/`, `PING`→`PONG`, serial 115200, `/dev/ttyUSB0`). Se edita/flashea desde la laptop.
- **ADC: el RPi lee el ADS1256 directo por SPI0** (AMTI Fz → AIN0 vs AINCOM; detalle en `esquemas/amti_ads1256_rpi/CONFIGURACION_ACTUAL.md`). `Codigo ESP32 ADS1256/` es una prueba aislada de otro montaje: solo referencia de la secuencia de init, no está conectado aquí.
- **Verificado en hardware (2026-11-02):** 1000 muestras/s, Fz en reposo ≈ 21.5 N de offset estable (hay que tarar), ruido σ≈0.85 N.

## Bloqueo de las ~17:50 (2026-11-02) — RESUELTO
El ADS1256 dejó de responder (DRDY no bajaba, registros en 0). Tras reiniciar el RPi volvió: `--diagnostico` da STATUS=0x30 y AIN0≈38.9 mV (≈22 N de offset). Causa raíz no determinada; si reaparece: revisar PDWN/RESET/CS/alimentación de la placa antes de tocar código.

## Qué hacer, en orden
1. Entorno: `source .venv/bin/activate` (tiene pyserial, spidev, RPi.GPIO, ttkbootstrap).
2. **Ver el ADC funcionando:** `python pruebas/leer_ads1256_fz.py --n 3000` (resumen + CSV) · `python pruebas/leer_ads1256_fz.py --diagnostico` (registros y 8 canales) · monitor en vivo: `python herramientas/monitor_gaitsim.py` (botón "Poner a cero" para restar el offset).
3. **Probar con carga conocida** (pesas sobre el AMTI) para validar la escala 1.7665 mV/N y el signo; documentar en `pruebas/`.
4. **Latencia RPi↔ESP32 de motores:** `python pruebas/medir_latencia_ping_pong.py --puerto /dev/ttyUSB0 --n 100` y `python pruebas/graficar_latencia.py` (ya medido: RTT 5.97 ms, ver `pruebas/2026-11-02_latencia_amti_rpi_esp32.md`).
5. Pendiente: latencia de adquisición AMTI→RPi (escalón de fuerza conocido) y latencia total del lazo.

## Reglas del proyecto (no te las saltes)
- Verificar datos de hardware contra fuente real (datasheet, etiqueta física, medición) — nunca de memoria. Ya hay precedente de esto en el repo, sigue el mismo estándar.
- No redactar síntesis/texto de tesis salvo pedido explícito — Luis decide el enfoque, tú organizas/ejecutas lo técnico.
- Git: commitear y hacer `git push` cuando termines algo con sentido (no cada línea), para que la laptop de Luis vea el avance.

## Firmware del ESP32 — importante
Las actualizaciones al firmware de control de motores (`Codigo ESP32 MOV/.../main.cpp`) se hacen **desde la laptop** (sesión de Claude ahí), no desde aquí — ahí es donde está el cable USB al ESP32 para flashear con PlatformIO. Si necesitas un cambio de firmware, dilo en el commit/push y Luis lo coordina con esa sesión; no asumas que tú vas a flashear el ESP32 desde el RPi.
