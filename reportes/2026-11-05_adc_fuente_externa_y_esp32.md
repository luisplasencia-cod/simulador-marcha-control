# 2026-11-05 (14:40–15:00) — ADC con fuente externa de 5 V, ESP32 conectado, latencia total

## 1. ADS1256 tras poner el 5 V con fuente externa — NO resuelto

**Objetivo:** comprobar si la causa de las caídas del ADS1256 era corriente insuficiente del 5 V del RPi (hipótesis de Luis) y, con el ADC sano, medir la latencia total del lazo.

**Metodología:** (a) `leer_ads1256_fz.py --diagnostico` (3 + 3 + 3 intentos); (b) revisión del log del monitor `logs/monitor_20261105_144227.log` y de `dmesg`/`journalctl -k`; (c) `fuser`/`ps` para ver quién tenía el SPI.

**Resultado (hechos medidos):**
- 14:42–**14:48:20**: el monitor leyó Fz real (≈ −1.8 N de media, rango −3.8…+0.7 N, plato vacío) → el ADC SÍ funcionó con la fuente externa.
- Desde **14:48:20** el monitor lee exactamente 0.0 N / 0.00000 V (n≈1190/línea): el SPI devuelve ceros.
- Con el monitor cerrado (kill por PID 3003; `fuser` no muestra otro proceso con el SPI), el diagnóstico falla 3/3: registros leídos 0/0/0 (a las 14:40, con el monitor corriendo, daba MUX=1 / DRATE=240 = valores de reset).
- `get_throttled`=0x0 (sin subtensión del RPi).
- ESP32 (CP2102) apareció como `/dev/ttyUSB0` a **14:45:39** (dmesg); el PING/PONG corrió 14:46 y terminó 14:46:17. La caída (14:48:20) ocurrió ~2 min después: **no coincide con el PING**.
- **Qué pasó a las 14:48:20 se desconoce** (pendiente: preguntar a Luis qué tocó/conectó en ese momento).
- Patrón a vigilar (correlación, NO causa probada): es la 3.ª vez que el ADC cae con el ESP32 recién conectado por USB / en uso (10:53 y hoy); la 1.ª (11-03) sin registro de ESP32.

**Corrección propia:** a las 14:45 dije que el diagnóstico fallaba "por competir con el monitor" y retiré la hipótesis de fallo del chip. Era **incompleto/incorrecto**: ahora falla también sin monitor. Los fallos de 14:40 sí pudieron deberse al monitor, pero no explican los de ahora.

**Limitaciones:** no se midió el 5 V ni el GND común de la fuente externa; no se sabe si el GND de la fuente está unido al del RPi; no se probó desconectar el USB del ESP32 para ver si el ADC vuelve.

**Fuentes:** logs `logs/monitor_20261105_*.log`, `dmesg`, `journalctl -k`, salida de `leer_ads1256_fz.py --diagnostico`.

## 2. PING/PONG con el ESP32 conectado — OK

**Objetivo:** confirmar el enlace RPi↔ESP32 por USB. **Metodología:** `pruebas/medir_latencia_ping_pong.py`, n=100. **Resultado:** 100/100 válidos, RTT 5.990 ms (σ 0.042, mín 5.848, máx 6.267); igual al 5.97 ms previo; ≈5 ms es el sondeo `vTaskDelay(5ms)` del firmware. CSV: `pruebas/resultados/ping_pong_20261105_esp32_conectado.csv`. **Limitaciones:** solo enlace, no movió motores. **Fuentes:** `communication.h` (firmware), script citado.

## 3. Latencia total del lazo — sin resultado

**Objetivo:** medir con un solo reloj flanco GPIO27 → AIN1 → detección → `MANUAL` al ESP32 → ack `OK`. **Metodología:** script nuevo `pruebas/medir_latencia_lazo_total.py` (mueve el eje sagital K ±40 pasos alternando; aborta antes de mover si GPIO27 no llega a AIN1). **Resultado:** **no se obtuvo número**: el script falló al inicializar el ADS1256 (ver §1); no se movió ningún motor. **Limitaciones previstas del método:** el ack se envía al aceptar el comando, no mide cuándo el motor empieza a girar; no incluye el retardo del amplificador AMTI (supuesto 2–3 ms, ver CLAUDE.md); el divisor GPIO27→AIN1 es temporal y no se verificó que siga cableado. **Fuentes:** `pruebas/medir_latencia_gpio_adc.py`, `pruebas/medir_latencia_comandos.py`.

## Pendiente
1. Luis: qué se hizo a las 14:48:20; medir 5 V de la placa y verificar GND común fuente–RPi–placa.
2. Desconectar el USB del ESP32 y reiniciar el RPi: ¿el ADC vuelve? (descarta/confirma la correlación).
3. Con el ADC sano: correr `pruebas/medir_latencia_lazo_total.py` y reabrir el monitor con `--con-esp32`.

## Actualización 14:50 — causa de la caída de las 14:48:20
Luis informó que el ADC "se había desconectado" (un cable) y lo reconectó. Verificado: el monitor reabierto a las 14:49 (`logs/monitor_20261105_144923.log`) vuelve a leer Fz ≈ −2.5 N, plato vacío; un pico de −188.7 N a las 14:50:04 coincide con manipulación (no verificado). **Esto sustituye la sospecha de correlación con el USB del ESP32** (§1) como explicación de esta caída. No se sabe qué cable fue. Pendiente: asegurar el conexionado (tercera caída con síntomas de contacto) y decidir si la fuente externa es necesaria probando sin ella con cableado firme. Nota de proceso: mi script falló con 'GPIO busy' porque el monitor (PID 3371, reabierto 14:49) tenía el GPIO17; cerrar el monitor por PID antes de medir.

## Resultado 14:55 — latencia total del lazo MEDIDA (hasta el ack del ESP32)
**Objetivo:** latencia flanco eléctrico → ADC → RPi → comando al ESP32 → ack, con un solo reloj. **Metodología:** `pruebas/medir_latencia_lazo_total.py --n 30` (GPIO27 → divisor → AIN1; detección al 50 % del escalón; `<MANUAL:2:±40>` al sagital K, alternando signo; 1 s entre eventos). Niveles: bajo 52.8 mV, alto 1617.7 mV. **Resultado (n=30, 30/30 con `OK`, sin otras respuestas):**

| Tramo | media | σ | mín | p95 | máx |
|---|---|---|---|---|---|
| adquisición (flanco→detección) | 1.619 ms | 0.288 | 1.139 | 2.056 | 2.106 |
| comando (detección→ack OK) | 6.325 ms | 1.794 | 3.258 | 8.973 | 9.846 |
| **TOTAL (flanco→ack)** | **7.945 ms** | 1.791 | 4.398 | 10.478 | 11.535 |

CSV: `pruebas/resultados/latencia_lazo_total.csv`. El tramo de adquisición coincide con el 1.61 ms (50 %) medido el 11-03. El tramo de comando tiene más σ que el PING/PONG (0.042 ms): incluye el ack de `MANUAL` (el firmware lo responde tras procesarlo) además del sondeo de 5 ms; no se separó cuánto es cada cosa. **Movimiento realizado (autorizado por Luis):** sagital K ±40 pasos × 30 eventos, alternando → neto 0 pasos; el ESP32 se reinicia al abrir el puerto, así que su contador parte de 0 (no se leyó la posición).
**Limitaciones:** (1) el ack no es el instante en que el motor empieza a girar (sin sensor para medirlo); (2) no incluye el retardo del amplificador AMTI (SUPUESTO 2–3 ms, no medido) ni el cómputo de un controlador real (aquí es ~0); (3) escalón eléctrico de 3.3 V, no una señal de fuerza; (4) MANUAL del firmware original, no `SET_VEL` (que no está flasheado); (5) n=30, una sola sesión; (6) un lazo real mandaría en continuo, no con 1 s de pausa. **Lectura:** total medido 7.9 ms (p95 10.5, máx 11.5) + AMTI supuesto 2–3 ms → ≈ 10–14 ms hasta el ack; sigue muy por debajo del techo de ~130 ms donde la simulación mostró inestabilidad del híbrido, **pero esa comparación hereda los supuestos de la simulación**.
