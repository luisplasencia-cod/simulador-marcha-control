# PROBLEMA PENDIENTE (PRIORIDAD 1): desconexión del USB del ESP32 durante los ensayos

> Decisión de Luis (2026-11-05): **lo que falla es la desconexión; hay que solucionarla, no esquivarla.** Documentado con el texto literal de la terminal para verificarlo después. **Los cambios al ESP32 se hacen desde la laptop (no desde este RPi): aquí NO se tocó el firmware.** Evidencia cruda: `reportes/evidencia/` (kernel, consola, errores literales).

## 1. Síntoma
Con el ESP32 conectado por USB al RPi (adaptador CP2102, `idVendor=10c4 idProduct=ea60`), el puerto serie desaparece sin previo aviso mientras se ejecuta el Ensayo A (movimientos `MANUAL` del eje vertical Y). Pyserial devuelve `Input/output error`; el adaptador reaparece al instante con otro número de dispositivo y otro nombre (`ttyUSB0` ↔ `ttyUSB1`). **El ESP32 nunca envió un error**: todas las respuestas fueron `OK`; al abrir el puerto no imprime nada (0 bytes en 3 s) y responde `PONG` a `<PING>`.
**Magnitud hoy:** **68 desconexiones** en el registro del kernel entre las 14:40 y las 16:45; **68 de 68 con el mensaje `disabled by hub (EMI?)`**. 9 de 12 corridas del Ensayo A desde las 16:05 se cortaron.

## 2. LO QUE APARECE EN LA TERMINAL (literal)
### 2.1 Kernel (`journalctl -k`), un evento completo (16:30:14)
```
Nov 05 16:30:14 gaitsim-control kernel: usb usb1-port2: disabled by hub (EMI?), re-enabling...
Nov 05 16:30:14 gaitsim-control kernel: usb 1-2: USB disconnect, device number 63
Nov 05 16:30:14 gaitsim-control kernel: cp210x ttyUSB0: failed set request 0x7 status: -19
Nov 05 16:30:14 gaitsim-control kernel: cp210x ttyUSB0: failed set request 0x12 status: -19
Nov 05 16:30:14 gaitsim-control kernel: cp210x ttyUSB0: failed set request 0x0 status: -19
Nov 05 16:30:14 gaitsim-control kernel: cp210x ttyUSB0: cp210x converter now disconnected from ttyUSB0
Nov 05 16:30:14 gaitsim-control kernel: cp210x 1-2:1.0: device disconnected
Nov 05 16:30:14 gaitsim-control kernel: usb 1-2: new full-speed USB device number 64 using xhci-hcd
Nov 05 16:30:14 gaitsim-control kernel: usb 1-2: New USB device found, idVendor=10c4, idProduct=ea60, bcdDevice= 1.00
Nov 05 16:30:14 gaitsim-control kernel: usb 1-2: New USB device strings: Mfr=1, Product=2, SerialNumber=3
Nov 05 16:30:14 gaitsim-control kernel: usb 1-2: Product: CP2102 USB to UART Bridge Controller
Nov 05 16:30:14 gaitsim-control kernel: usb 1-2: Manufacturer: Silicon Labs
Nov 05 16:30:14 gaitsim-control kernel: usb 1-2: SerialNumber: 0001
Nov 05 16:30:14 gaitsim-control kernel: cp210x 1-2:1.0: cp210x converter detected
Nov 05 16:30:14 gaitsim-control kernel: usb 1-2: cp210x converter now attached to ttyUSB1
```
Conteo de líneas por tipo (14:40–16:45): `usb usb1-port2: disabled by hub (EMI?), re-enabling...` ×68; `usb 1-2: USB disconnect, device number N` ×68; `cp210x ttyUSBn: failed set request 0x7 status: -19` ×68, `... 0x12 status: -19` ×68, `... 0x0 status: -19` ×68; `cp210x converter now disconnected from ttyUSBn` ×68. Códigos: `status: -19` = ENODEV (el dispositivo ya no existe). Todo el registro: `reportes/evidencia/2026-11-05_dmesg_usb_esp32.txt`.
### 2.2 Python/pyserial (consola del ensayo), textos literales y veces
```
error(5, 'Input/output error')                                  (~27 veces)   [errno 5 = EIO]
Could not configure port: (5, 'Input/output error')             (1)
[Errno 71] Protocol error                                       (1)           [errno 71 = EPROTO]
could not open port /dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001-if00-port0:
  [Errno 2] could not open port ...: No such file or directory  (1)           [errno 2 = ENOENT: el enlace by-id desaparece mientras se re-enumera]
termios.error: (5, 'Input/output error')                         (1, en reset_input_buffer de un script suelto)
```
Mensajes del propio script que aparecen en la terminal cuando ocurre un corte:
```
Motivo de parada: excepcion: error(5, 'Input/output error') -> subiendo 222.6 mm
subida fina interrumpida: error(5, 'Input/output error')
ERROR subida gruesa: error(5, 'Input/output error') -> reconectando
  esperando que el USB reaparezca (1/10)
  puerto no disponible ((5, 'Input/output error')); reintento 2/10
no se pudo reconectar: RuntimeError('puerto serie irrecuperable')
pasos pendientes de subir: 0
```
Los 32 textos de error distintos con su número de apariciones: `reportes/evidencia/2026-11-05_errores_terminal_literal.txt`. Las salidas completas de cada corrida: `reportes/evidencia/consola/*.txt`.
### 2.3 Errores del ADC que coinciden en el tiempo (no del ESP32)
```
El ADS1256 no devolvio lo escrito: leido={'ADCON': 0, 'MUX': 1, 'DRATE': 240} esperado={'ADCON': 0, 'MUX': 8, 'DRATE': 161}   (también leido 0/0/0, MUX 8 DRATE 40, ...; ×17)
TimeoutError('DRDY no bajo a tiempo - revisar cableado/VREF/CLKIN')   (×2)
OSError: [Errno 9] Bad file descriptor      (al cerrar el ADC tras fallar en la corrida 3)
```

## 3. Cronología de cortes (kernel, hora local, por minuto)
15:43 (x1), 15:46 (x10), 15:47 (x21), 16:05 (x4), 16:11 (x1), 16:13 (x1), 16:15 (x3), 16:16 (x3), 16:17 (x1), 16:18 (x1), 16:19 (x4), 16:20 (x4), 16:21 (x4), 16:22 (x2), 16:30 (x1), 16:34 (x1), 16:35 (x1), 16:36 (x1), 16:38 (x2), 16:40 (x1), 16:42 (x1)

## 4. Datos medidos que acotan la causa (HECHOS)
- Cada corte lleva `disabled by hub (EMI?)`: lo detecta el **hub USB de la Pi (puerto 2)**, es un error de la capa física del USB, no un error del protocolo del ESP32.
- **Se cortó con carga baja (12–14 N) y SIN carga** (100 mm de descenso, aproximación): no depende de la fuerza alta.
- **Relación con las aperturas del puerto:** entre las 16:18 y las 16:22, 14 cortes cada ≈15 s = el periodo de mis ráfagas de reapertura; al dejar de abrir el puerto, **0 cortes en 45 s**. El CP2102 sube DTR/RTS al abrirse y reinicia el ESP32; el firmware (`setup()` en `main.cpp`) ejecuta `brake_init(Y_BRAKE_PIN, Y_BRAKE_LOCKED); delay(500); ... brake_set(Y_BRAKE_PIN, Y_BRAKE_RELEASED); delay(500);` → **cada reinicio cicla el freno del eje vertical**.
- **Relación con el movimiento del servo vertical:** el único corte con hora exacta del registro de eventos (`logs/ensayo_A_eventos.csv`) ocurrió **0.3 s después de un comando `fino -16`** (durante el movimiento). n = 1: indicio, no prueba.
- **Riesgo por comando:** en 12 corridas, 9 se cortaron tras 1–106 comandos de movimiento y 3 no se cortaron con 65, 87 y 272 comandos → ≈ **9 cortes en ≈ 800 comandos ≈ 1 % por comando** (estimación gruesa). Corridas con más comandos tienen más probabilidad de cortarse.
- **La punta del pie es la parte más deformable (k ≈ 2.4 N/mm, ≈ 11 veces más blanda que talón/plana):** con escalones de 0.2 mm necesitaba 150–270 comandos para llegar a 70–100 N y se cortó en 6 de 7 intentos; **con escalones de 2 mm (≈ 40 comandos) salió completa al primer intento sin cortes**. Es decir, la dificultad de la punta es en buena parte *más comandos = más oportunidades de corte*, no una propiedad del pie.
- Con carga alta (≥ 100 N, 127 N) también hubo cortes y tormentas (21 cortes en 1 minuto a las 15:47; 14 entre las 16:18–16:22 inducidas por mis reaperturas).
- Rieles de la Pi sanos en todo momento: `vcgencmd get_throttled` = 0x0; 3V3_SYS = 3.303 V, 1V8 = 1.800 V.
- Tras cada tormenta el ESP32 respondió normalmente (`PONG`, `OK`) y el eje no se movió por sí solo (el freno/servo sostuvo hasta 127 N durante ≈2 min).

## 5. Hipótesis (NO verificadas), ordenadas
1. **Perturbación electromagnética/de masa del servo vertical y su freno** acoplada al cable USB o a la masa común (el mensaje del hub dice literalmente `EMI?`).
2. **Reinicio del ESP32 por DTR/RTS al abrir el puerto** con el servo energizado (freno bloqueado→liberado) que genera otro pico → bucle autosostenido.
3. **Alimentación USB del ESP32** (caída de VBUS cuando la placa activa STEP/DIR/freno) o cable USB de mala calidad/sin ferrita.
4. **Bucle de tierra** RPi–USB–ESP32–drivers y fuente externa del ADC–AMTI.

## 6. QUÉ VERIFICAR / HACER (desde la laptop y en el rig) — no hecho aún
**Firmware del ESP32 (se edita y flashea desde la laptop; autorizado por Luis):** (a) imprimir `esp_reset_reason()` y un contador de reinicios al arrancar (y exponerlo en `GET_POSITION`/`TRAJ_STATUS`) para saber si el ESP32 se reinicia solo por brownout (`Brownout detector was triggered` / `rst:0x..`) cuando el USB cae; (b) revisar que abrir el puerto no reinicie la placa (condensador en EN o deshabilitar el auto-reset por DTR/RTS) ; (c) valorar no bloquear/liberar el freno vertical en cada `setup()` si se reinicia en caliente; (d) velocidad de `MANUAL` (1600 pasos/s en Y) como variable de prueba.
**Hardware/rig:** cable USB corto con ferrita; hub USB con fuente propia o aislador USB; probar el otro puerto USB 2 de la Pi (el enlace `by-id` no cambia); alejar el cable USB de los de potencia del servo; medir con multímetro/osciloscopio 5 V del ESP32 y masa durante un paso con carga; registrar con un logger de un solo proceso que mantenga el puerto abierto (para ver lo que imprima el ESP32) en paralelo con `journalctl -kf`.
**Criterio de éxito sugerido:** repetir el Ensayo A (plana, `--paso_pasos 16`, ≈90 comandos) 10 veces seguidas con **0 cortes**, y 30 min de movimientos de Y sin una sola línea `disabled by hub`.
**Cómo reproducir/medir en el RPi:** `journalctl -k -o short-unix --since '<hora>' | grep -c 'disabled by hub (EMI'` antes y después; `control/identificacion/analizar_caidas_usb.py` cruza cada corte con el último comando (usa `logs/ensayo_A_eventos.csv`); mitigaciones de software ya hechas pero que NO eliminan la causa: reconexión calmada, reintento en fase fina, subida sin ADC, `conectar(rapido=True)`, `subir_a_rafagas.py`.
