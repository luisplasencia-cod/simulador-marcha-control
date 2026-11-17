# Punto de entrada para Claude en el Raspberry Pi

Si acabas de llegar a este repo en el RPi: lee esto completo antes de hacer nada.
Contexto completo y siempre actualizado: `CLAUDE.md` (la entrada con fecha más reciente es la vigente).
Reescrito el 2026-11-17 desde la laptop, **sin RPi**: nada de este plan se ha ejecutado.

**Regla de orden (Luis):** todo es sobre Fz (eje vertical). No se toca Fy ni sagital en lazo cerrado
hasta que Fz quede probado en el simulador real.

## 0. CAMBIO DE ARQUITECTURA DECIDIDO EL 2026-11-17 — léelo antes de seguir cualquier plan viejo

El ADS1256 deja de leerse directo por SPI desde el RPi. Ahora lo lee un **ESP32 nuevo, dedicado
solo a esto** (no el de motores), con entrada **diferencial** (AIN1 señal, AIN0 referencia, en
vez de AIN0/AINCOM single-ended), y se lo pasa al RPi por **UART2** (no SPI, no USB del ESP32 de
motores). Motivo de Luis: ya había probado antes un ESP32+ADS1256 así y "funcionaba mejor"
(**impresión suya, sin número medido en el repo** — pendiente de medir y confirmar aquí).

**Importante: este cambio de host NO ataca la causa de las caídas del ADC si es analógica o de
alimentación** — es independiente de quién lee el SPI. Las protecciones ①-⑤ (abajo) siguen
aplicando igual, porque protegen al chip, no al host.

- Esquema completo: `esquemas/amti_ads1256_rpi/salida/esquema_protecciones_ads1256.png`.
- Firmware ya corregido (un solo cambio: escala 1.7631→1.7665), listo para compilar:
  `control/firmware/lectura_ads1256_esp32_diferencial/`.
- Lector del lado RPi (NO probado): `pruebas/leer_ads1256_fz_esp32_uart.py`.
- Vigilante de caídas para esta ruta (NO probado): `pruebas/vigilar_adc_esp32_uart.py`.
- El lector directo anterior (`pruebas/leer_ads1256_fz.py`, validado contra el AMTI real el
  2026-11-03, RMSE 1.89 N) queda **sin usarse en esta ruta** — su validación NO se traslada
  automáticamente al nuevo camino, hay que repetirla (Fase 4 abajo).

## 1. Qué traer y confirmar al llegar

- Luis ya cableó el ADS1256 al ESP32 nuevo en diferencial, según el esquema — **confirmar
  visualmente contra el esquema antes de energizar**, no asumir que quedó igual a lo dibujado.
- `git pull` primero.
- Vas a tener **dos ESP32 conectados por USB**: el de motores y este nuevo de lectura.
  **Identificar cuál es cuál antes de tocar nada** — `dmesg` o `ls /dev/ttyUSB*`, desconectar uno
  a la vez si hace falta. Flashear o abrir el puerto equivocado puede mover motores sin querer
  (ya pasó el 2026-11-10 con el eje X) o interrumpir el control.

## 2. Plan en orden

### Fase A — Compilar y flashear el ESP32 de lectura (sin el otro ESP32 conectado, para no confundirlos)

```
cd control/firmware/lectura_ads1256_esp32_diferencial
# antes de compilar: fijar una version exacta de platform en platformio.ini (ver su comentario,
# mismo motivo que Codigo ESP32 MOV/: binarios no reproducibles si no se fija)
pio run
esptool.py --port /dev/ttyUSBx read_flash 0x0 0x400000 respaldo_antes_de_flashear.bin  # SIEMPRE antes de flashear
pio run -t upload --upload-port /dev/ttyUSBx
```

Después: abrir `pio device monitor` (o cualquier monitor serie) en el puerto de ESTE ESP32 y
confirmar que llegan líneas de depuración por Bluetooth (`BT.println`, cada 500 muestras) — eso
ya dice que el ADS1256 respondió y el ESP32 está leyendo. No mover nada del simulador en esta fase.

### Fase B — Primera lectura desde el RPi

```
python pruebas/leer_ads1256_fz_esp32_uart.py --puerto /dev/ttyUSBx --n 1000 --salida lecturas_fz_esp32_prueba1.csv
```

Revisar: ¿da cerca de 1000 muestras/s? ¿Fz en reposo da un offset estable (para tarar), con ruido
razonable (compara contra σ≈0.85 N del lector directo anterior, como referencia, no como exigencia)?
Si faltan muchas muestras o el ruido es raro, parar aquí y reportarlo — no seguir a la Fase C.

### Fase C — Vigilar caídas, SIN tocar protecciones todavía

```
python pruebas/vigilar_adc_esp32_uart.py --puerto /dev/ttyUSBx --minutos 30
```

**Esto decide el siguiente paso:**

| Resultado | Qué significa | Siguiente paso |
|---|---|---|
| 0 caídas en 30 min | El cambio de host ayudó (o la causa real nunca estuvo en el RPi) | Repetir con el servo en marcha (Fase F) antes de confiar del todo |
| Se cae igual que antes | La causa NO es el host — es analógica o de alimentación, como ya se sospechaba | Cablear protecciones ①②③④⑤ (sección 3) antes de seguir |

### Fase D — Cablear protecciones (solo si la Fase C mostró caídas)

Mismo orden de dos tandas que ya estaba decidido: primero ②④⑤ (PDWN, 5 V, tierra), repetir la
Fase C; después ③① (protección de AIN0/AIN1, SPI). Detalle de cada protección: sección 3.

### Fase E — Validar contra el AMTI real

Repetir algo parecido a `pruebas/comparar_amti_vs_ads1256.py` (que validó el lector directo el
2026-11-03, RMSE 1.89 N) pero usando `leer_ads1256_fz_esp32_uart.py` como fuente de datos. No
confiar en esta ruta para el lazo de Fz sin esto.

### Fase F — Servo Y en el aire

Adaptar `pruebas/fuerza_vs_velocidad_y.py` para leer de la nueva ruta UART en vez del lector SPI
directo, y repetir la prueba del 2026-11-10 (en el aire, sin contacto, vigilando si Fz se corre o
el ADC se cae con el servo en marcha).

### Fase G — Primer lazo de Fz con contacto

`control/lazo_fz_tiempo_real.py` todavía lee con `leer_ads1256_fz.py` (SPI directo) — **hay que
adaptarlo a leer de `leer_ads1256_fz_esp32_uart.py` antes de usarlo**, eso no está hecho. Recién
después, mismo procedimiento ya documentado: pie en plana, hueco remedido, `--peso_sujeto_n 100
--fmax_n 150`.

## 3. Protecciones del ADS1256 (independientes del host, ver esquema completo)

① 100 Ω en serie en SCLK/DIN/CS. ② PDWN con regulador 3.3 V propio (de la fuente externa de 5 V,
no del host). ③ 1 kΩ en serie en AMBAS líneas diferenciales (AIN0 y AIN1). ④ R5 2.2 Ω + 100 µF +
100 nF en la entrada de 5 V. ⑤ GND de fuente externa, ADC, AMTI y ESP32 en un solo punto físico.
Nada de esto cableado todavía.

## 4. Reglas que no se saltan

- **Nunca `HOME` con la prótesis montada.** Si hace falta, avisar a Luis.
- **Ningún movimiento sin el OK de Luis en ese momento.**
- Ejes al ESP32 de motores siempre como **entero**: 0 = X, 1 = Y, 2 = K. Nunca letras.
- Antes de flashear cualquier ESP32: `esptool read_flash` de respaldo, y medir latencia después.
- El monitor (`herramientas/monitor_gaitsim.py`) sigue usando el lector SPI directo — adaptarlo
  también a la nueva ruta si se sigue usando (pendiente, no hecho).
- No suponer nada: dato medido, con fuente, o marcado NO VERIFICADO.
- Reporte por sesión en `reportes/`, decisiones en `CLAUDE.md` en el mismo turno, `sync` antes
  de apagar el RPi.
- Git: `git fetch` y `git log origin/master -1` antes de cada commit; `git push` al cerrar algo.
- Nunca `pkill -f` / `pgrep -f` con el patrón en la misma línea: matar por PID.

## 5. Mapa rápido

- Arquitectura: AMTI → ADS1256 (diferencial AIN1/AIN0) → **ESP32 de lectura** (SPI) →
  **UART2 → RPi** → cómputo del lazo → USB serie 115200 (`SET_VEL`) → **ESP32 de motores** →
  driver A6-750RS → servo vertical A6M80-750H2B1-M17 (con freno). Son DOS ESP32 distintos.
- Pines ADS1256↔ESP32 de lectura: CS=GPIO32, DRDY=GPIO33, SCLK=GPIO27, MISO=GPIO25, MOSI=GPIO26.
- UART2 ESP32→RPi: GPIO17 (TX), 115200 8N1, protocolo `"<valor>"` sin ACK.
- Rigidez medida (Ensayo A): talón 26.4, plana 23.0, punta 2.4 N/mm. Ganancia de la primera prueba: la del talón.
- ADC del producto final (aparte, no bloquea Fz): AD7606 elegido, sin comprar; su esquema de conexiones sigue pendiente.
