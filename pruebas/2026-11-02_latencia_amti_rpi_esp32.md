# Prueba de latencia AMTI → RPi → ESP32 — 2026-11-02

Conexión confirmada: RPi↔ESP32 por cable (serial).

## Paso 1 — Latencia de comunicación RPi↔ESP32 (sin AMTI)
**Actualización 2026-11-02:** no hace falta firmware nuevo — el firmware actual (`Codigo ESP32 MOV/platformIO_control_trayectoria_v1`) ya tiene comando `PING`→`PONG` (`communication.h`/`main.cpp`). Script listo: `C:\Control\pruebas\medir_latencia_ping_pong.py` (correr en el RPi: `pip install pyserial` y `python medir_latencia_ping_pong.py --puerto /dev/ttyUSB0 --n 100`).

**⚠️ Hallazgo del código (communication.h):** el ESP32 espera datos seriales con `vTaskDelay(5ms)` mientras no hay nada disponible → hasta **5 ms de latencia de sondeo (polling) propia del firmware** se suma a cada medición. No es latencia del cable; es una limitación de la arquitectura actual del firmware que hay que tener en cuenta al decidir tiempo real vs ILC.

Protocolo confirmado: 115200 baudios; RPi envía `<PING>`; ESP32 responde `PONG\n`.

**Intento 1 (RPi, antes de conectar el ESP32):** sin enlace — el RPi no veía ningún puerto USB-serial; 5/5 timeouts en `/dev/ttyAMA10` (UART de depuración del RPi 5, no era el puerto correcto).

**Medición 2026-11-02 (tras conectar el ESP32 por USB):** el ESP32 aparece como `/dev/ttyUSB0` (puente Silicon Labs CP210x). Comando: `.venv/bin/python pruebas/medir_latencia_ping_pong.py --puerto /dev/ttyUSB0 --n 100`. Datos: `pruebas/latencia_ping_pong.csv`, gráfico `pruebas/latencia_ping_pong.png`. El ESP32 estaba conectado a los motores y el AMTI conectado; solo se envió `<PING>` (no se enviaron comandos de movimiento).

- Protocolo usado (serial/baudrate, etc.): 115200 8N1, `<PING>` → `PONG\n`, USB-serial CP210x
- N válidos: 100 / 100 (0 timeouts)
- RTT medio: 5.974 ms
- Desviación estándar (jitter): 0.185 ms
- Mínimo / máximo: 4.139 / 6.047 ms
- Observaciones: el RTT es casi todo el polling del firmware (`vTaskDelay(5ms)`, hasta 5 ms) más ~1 ms de transmisión serial (6 bytes de ida + 5 de vuelta a 115200 baud ≈ 0.95 ms). Es una lectura consistente con el hallazgo del código, no una verificación independiente: no se separó cuánto aporta cada parte. El tiempo de vuelta del PONG medido incluye además la latencia de USB/driver del lado RPi. Es un RTT; el unidireccional (~3 ms) es solo RTT/2 y asume simetría, que aquí no se cumple (el polling está solo en el lado ESP32).


**Comandos reales (2026-11-02, `pruebas/medir_latencia_comandos.py`, solo lectura, sin mover motores, N=100):** PING 5.36 ms media (un outlier de 106 ms, 99/100 válidos; probable arranque), GET_POSITION 4.93 ms (desv 0.02), TRAJ_STATUS 4.92 ms (desv 0.08). Mismo orden que PING (~5 ms): la latencia con comandos reales equivale al polling del firmware, el procesamiento del comando no añade nada medible. Posición leída `0:0:0` (sin HOME). **No medido todavía:** ack de `MANUAL` (mueve motores; script listo con `--mover`, requiere simulador despejado) ni ejecución de trayectoria.

## Paso 2 — Latencia de adquisición AMTI → RPi
**(2026-11-02, resuelto) El problema de lectura en 0 V era un bug del script** (`RDATA` + bytes de relleno sacaba el dato de la ventana), no del AMTI ni del cableado — corregido en `leer_ads1256_fz.py`, ahora lee bien (ver estado en `CLAUDE.md`).

**(2026-11-03) ADC ya validado contra el AMTI real** por separado (RMSE 1.89 N, error pico a pico 4.03%, ver `pruebas/comparar_amti_vs_ads1256.py`) — eso confirma escala/signo, pero **no es la latencia de adquisición**, son cosas distintas. Esta sección sigue pendiente.

Método: aplicar un escalón de fuerza conocido (golpe seco o carga rápida) y comparar el instante físico vs. el instante en que el RPi registra el cambio en su lectura. Script: `pruebas/medir_latencia_escalon_amti.py` — registra el instante de DETECCIÓN del RPi; para la latencia real falta una referencia física independiente (ver aviso en el script). No reportar un número aquí sin esa referencia.

- Repetición 1: _____ ms
- Repetición 2: _____ ms
- Repetición 3: _____ ms
- (agregar más filas si se hacen más repeticiones)
- Media / desviación: _____ / _____ ms
- Observaciones (ruido, offset, canal usado): _____

## Paso 3 — Latencia total del loop
Total = Paso 2 + cómputo RPi + Paso 1 + ejecución ESP32 (ej. medir con GPIO/LED en el instante que el ESP32 recibe el comando).

- Latencia total medida: _____ ms
- Desviación: _____ ms
- Observaciones: _____

## Paso 4 (si hay tiempo) — Calibración básica AMTI
- Offset en reposo por canal (Fx, Fy, Fz, Mx, My, Mz): _____
- Escala voltaje→fuerza verificada contra hoja de calibración: sí/no — _____
- Signo de cada canal confirmado: _____
- Ruido (varianza en reposo): _____

## Conclusión del día
- ¿Latencia compatible con tiempo real o ILC?: todavía sin umbral ni medición de AMTI→RPi. Solo la comunicación RPi↔ESP32 está medida (~6 ms de RTT, dominado por el polling del firmware, reducible si el firmware dejara de dormir 5 ms). Falta el Paso 2 para opinar sobre el total.
- Pendiente para la siguiente sesión: habilitar SPI (hoy no hay `/dev/spidev*`) y probar `leer_ads1256_fz.py` en hardware real (Pasos 2-4); evaluar con Luis si el polling de 5 ms del firmware se puede reducir (cambio de firmware: solo desde la laptop).
