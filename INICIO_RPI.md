# Punto de entrada para Claude en el Raspberry Pi

Si acabas de clonar este repo en el RPi y es tu primera vez aquí: lee esto completo antes de hacer nada.

## Qué es este repo
Tesis de control del simulador de marcha (Luis Plasencia, PUCP). Contexto completo del proyecto en `CLAUDE.md` (léelo primero, siempre). Detalle de auditorías/búsquedas pasadas en `HISTORIAL.md`.

## Estado físico ahora mismo (2026-11-02)
AMTI → ADS1256 → RPi, canal Fz, **ya cableado por Luis**. Detalle de conexión, pines y VREF (resuelto: 2.5V, chip ADR03B) en `esquemas/amti_ads1256_rpi/CONFIGURACION_ACTUAL.md` — léelo antes de escribir cualquier script que lea el ADC, para no reinventar ni contradecir lo ya verificado.

RPi↔ESP32: por cable (serial, 115200 baud). El ESP32 corre el firmware de `Codigo ESP32 MOV/platformIO_control_trayectoria_v1/` (control de motores, ya tiene comando `PING`→`PONG` para medir latencia — no inventes un protocolo nuevo, usa `communication.h` como referencia).

## Qué hacer, en orden
1. **Instalar dependencias:** `pip install pyserial matplotlib` (y lo que haga falta para leer el ADS1256 por SPI — todavía no hay script de lectura del ADC en el repo, es el siguiente paso pendiente, no asumas que ya existe).
2. **Medir latencia RPi↔ESP32:** `python pruebas/medir_latencia_ping_pong.py --puerto /dev/ttyUSB0 --n 100` (ajusta el puerto con `ls /dev/tty*` si no es ese). Genera un CSV.
3. **Graficar el resultado:** `python pruebas/graficar_latencia.py --csv latencia_ping_pong.csv`. Genera un PNG (histograma + serie por intento).
4. **Llenar el plan de prueba** en `pruebas/2026-11-02_latencia_amti_rpi_esp32.md` con los resultados — no dejarlo solo en el CSV/PNG, documentar ahí también.
5. **Lectura del ADC (AMTI vía ADS1256):** script listo — `pruebas/leer_ads1256_fz.py` (`pip install spidev RPi.GPIO`, luego `python leer_ads1256_fz.py --n 100`). **No probado en hardware real** (se escribió y verificó la lógica de conversión bit→volts→Newtons en una laptop sin RPi/ADS1256 — revisar primero que el reloj CLKIN de la placa sea el típico 7.68 MHz; si DRDY nunca baja o las lecturas no tienen sentido, ese es el primer sospechoso, ver el AVISO al inicio del script). Con 0 N reales debería dar ~0 N (si no, hay offset de cero pendiente, Paso 4 del plan de latencia).

## Reglas del proyecto (no te las saltes)
- Verificar datos de hardware contra fuente real (datasheet, etiqueta física, medición) — nunca de memoria. Ya hay precedente de esto en el repo, sigue el mismo estándar.
- No redactar síntesis/texto de tesis salvo pedido explícito — Luis decide el enfoque, tú organizas/ejecutas lo técnico.
- Git: commitear y hacer `git push` cuando termines algo con sentido (no cada línea), para que la laptop de Luis vea el avance.

## Firmware del ESP32 — importante
Las actualizaciones al firmware de control de motores (`Codigo ESP32 MOV/.../main.cpp`) se hacen **desde la laptop** (sesión de Claude ahí), no desde aquí — ahí es donde está el cable USB al ESP32 para flashear con PlatformIO. Si necesitas un cambio de firmware, dilo en el commit/push y Luis lo coordina con esa sesión; no asumas que tú vas a flashear el ESP32 desde el RPi.
