# Prueba de latencia AMTI → RPi → ESP32 — 2026-11-02

Conexión confirmada: RPi↔ESP32 por cable (serial).

## Paso 1 — Latencia de comunicación RPi↔ESP32 (sin AMTI)
**Actualización 2026-11-02:** no hace falta firmware nuevo — el firmware actual (`Codigo ESP32 MOV/platformIO_control_trayectoria_v1`) ya tiene comando `PING`→`PONG` (`communication.h`/`main.cpp`). Script listo: `C:\Control\pruebas\medir_latencia_ping_pong.py` (correr en el RPi: `pip install pyserial` y `python medir_latencia_ping_pong.py --puerto /dev/ttyUSB0 --n 100`).

**⚠️ Hallazgo del código (communication.h):** el ESP32 espera datos seriales con `vTaskDelay(5ms)` mientras no hay nada disponible → hasta **5 ms de latencia de sondeo (polling) propia del firmware** se suma a cada medición. No es latencia del cable; es una limitación de la arquitectura actual del firmware que hay que tener en cuenta al decidir tiempo real vs ILC.

Protocolo confirmado: 115200 baudios; RPi envía `<PING>`; ESP32 responde `PONG\n`.

- Protocolo usado (serial/baudrate, etc.): _____
- RTT medio: _____ ms
- Desviación estándar (jitter): _____ ms
- Mínimo / máximo: _____ / _____ ms
- Observaciones: _____

## Paso 2 — Latencia de adquisición AMTI → RPi
Método: aplicar un escalón de fuerza conocido (golpe seco o carga rápida) y comparar el instante físico vs. el instante en que el RPi registra el cambio en su lectura.

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
- ¿La latencia total parece compatible con control en tiempo real, o apunta a necesitar ILC? (sin umbral formal aún, es solo impresión inicial): _____
- Pendiente para la siguiente sesión: _____
