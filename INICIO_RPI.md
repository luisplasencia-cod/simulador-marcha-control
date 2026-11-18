# Plan de prueba del ADC (ESP32 + UART) — primero LAPTOP, después RPi

Si acabas de llegar a este repo (laptop o RPi): lee esto completo antes de hacer nada.
Contexto completo: `CLAUDE.md` (la entrada con fecha más reciente es la vigente).
Reescrito el 2026-11-18 desde la laptop.

## ▶ ESTADO AL 2026-11-18 (tarde) — EMPEZAR AQUÍ EN LA RPi
- **Etapa 0 y Etapa 1 (laptop) HECHAS.** El ADC funciona por el ESP32 de lectura: 4/4 registros OK,
  1000 muestras/s, ruido σ ≈ 0.75 N, signo correcto, escala +2–3 % con una pesa de 2.246 kg (sin comparar
  con NetForce todavía). Detalle y números: `reportes/2026-11-18_etapa1_laptop_adc_esp32.md`.
- **El ESP32 de lectura YA TIENE el firmware final grabado.** En la RPi **no hay que compilar ni flashear
  nada** (la Fase A vieja ya no aplica). Respaldo del firmware anterior en
  `control/firmware/respaldos_flash/esp32_lectura_adc_original_flash_0x0_0x400000_20261118.bin`.
- **No hecho en la laptop:** L4 (UART2, no había adaptador USB-TTL) y la vigilancia larga (solo 5 min).
  La ruta UART2 se prueba por primera vez en la RPi (R1–R3).
- **Siguiente:** Etapa 2 desde **R0** (abajo). Cables a reconectar en la RPi (Luis los desconectó para la
  laptop): **GPIO17 del ESP32 → pin 10 del RPi (GPIO15 RXD)** y **GND del ESP32 → pin 6 del RPi (GND)**.
  El TX del RPi NO se conecta. **Decisión de Luis (2026-11-18): el ESP32 de lectura SIGUE alimentado por el USB
  de la LAPTOP** (no por la RPi). Consecuencias: (1) en la laptop NADA puede abrir COM8 durante la prueba
  (abrirlo reinicia el ESP32 y corta ≈2 s el UART a la RPi) — ojo con `C:\PB2\display\server.py`, que arranca
  solo con la laptop y toma COM8; (2) la laptop no debe suspenderse; (3) GND de laptop, ESP32, RPi y ADC quedan
  unidos: si el ruido en la RPi sale peor que σ ≈ 0.75 N, repetir con la laptop a batería.
- **Ojo:** el ESP32 de lectura también aparece como `/dev/ttyUSBx` si se enchufa por USB a la RPi. **No
  abrir ese puerto por error creyendo que es el de motores** (y viceversa): identificar con
  `ls -l /dev/serial/by-id/` desenchufando uno a la vez.
- **Por el USB del ESP32 sale diagnóstico** (`F,<valor>` a 100/s + resumen por segundo). En la RPi no hace
  falta, pero si algo falla en R2 se puede ver con `pruebas/registrar_diag_esp32_usb.py --puerto /dev/ttyUSBx`
  para saber si el problema es del ADC (sale ERROR/ALERTA ahí) o del cable UART (ahí todo OK).

**Regla de orden (Luis):** todo es sobre Fz (eje vertical). **Escalonado:** primero se confirma
en la LAPTOP que el ADC sensa bien (ESP32 por USB, sin RPi, sin motores); recién con eso
aprobado se pasa al RPi. Cada etapa tiene un criterio de paso: si no se cumple, **parar y
diagnosticar ahí**, no seguir a la siguiente (así una falla se detecta donde nace).

## 0. Arquitectura vigente (2026-11-17)

AMTI → 1 kΩ en AIN1 y AIN0 → ADS1256 (diferencial, AIN1 señal, AIN0 referencia) → SPI →
**ESP32 de lectura (nuevo, dedicado)** → UART2 (GPIO17, 115200, paquetes `<valor>`) → RPi.
El ESP32 de motores es OTRO ESP32 distinto. Luis ya cableó todo según
`esquemas/amti_ads1256_rpi/salida/esquema_protecciones_ads1256.png`, **con las protecciones ①-⑤
incluidas** (no energizado ni probado; cableado no verificado por Claude).

Pines ADS1256↔ESP32: CS=GPIO32, DRDY=GPIO33, SCLK=GPIO27, DOUT(MISO)=GPIO25, DIN(MOSI)=GPIO26.

### Qué cambió en el código el 2026-11-18 (revisión previa a la prueba)

- **Firmware** (`control/firmware/lectura_ads1256_esp32_diferencial/`, compila en
  `espressif32 @ 7.0.1`, ya fijada): antes, si el ADC no respondía al arrancar, el ESP32 se
  **colgaba en silencio** (`while(DRDY==HIGH);` sin límite) — imposible distinguir "ADC mal
  cableado" de "UART mal cableado". Ahora: espera máx. 1 s, imprime el error por el **USB del
  ESP32** y reintenta cada 2 s; relee los registros (STATUS/MUX/ADCON/DRATE) y dice cuál sale
  MAL; imprime el motivo del último reinicio (detecta BROWNOUT); y **una línea CSV por segundo**:
  `t_s,n,fz_media,fz_sd,fz_min,fz_max,periodo_max_us,perdidas,ceros,saturadas,elapsed_max_us`.
  El paquete `<valor>` por UART2 **no cambió**. Entorno extra `sin_bt` (sin Bluetooth) para
  comparar ruido.
- **Lector** `pruebas/leer_ads1256_fz_esp32_uart.py`: tenía un **bug que lo hacía caerse** casi
  siempre al abrir el puerto (si el primer trozo era `3.2><4.1`, lanzaba `ValueError`).
  Corregido y probado con casos sintéticos.
- **Vigilante** `pruebas/vigilar_adc_esp32_uart.py`: solo contaba "silencio del puerto"; un ADC
  devolviendo **ceros, valores congelados o saturados** pasaba como OK. Ahora clasifica
  CAIDO / CEROS / SATURADO / CONGELADO / PICOS / OK por segundo.
- **Nuevo** `pruebas/registrar_diag_esp32_usb.py`: guarda el diagnóstico del USB del ESP32 (para
  la etapa laptop; no necesita adaptador).
- **Nuevo** `pruebas/visor_fz_esp32_usb.py`: ventana en vivo de Fz por el USB del ESP32 (tara, marcas,
  registro CSV). Sirve también en la RPi si hay pantalla.

---

## ETAPA 0 — Sin energía (multímetro, 15 min)

| # | Qué medir | Criterio de paso |
|---|---|---|
| 0.1 | Continuidad de cada cable contra el esquema, pin por pin (incluye DIN/DOUT, que se confunden fácil) | Todos coinciden |
| 0.2 | Resistencia 5 V ↔ GND en la placa del ADC, y 3.3 V del regulador de PDWN ↔ GND | > 100 Ω (no corto) |
| 0.3 | Valores de las resistencias montadas: 100 Ω (SCLK/DIN/CS), 1 kΩ (AIN0 y AIN1), 2.2 Ω (R5) | ±5 % |
| 0.4 | Regulador de PDWN: patas IN / GND / OUT según su hoja (el orden cambia entre modelos) | Coincide con la hoja del modelo exacto |
| 0.5 | GND de fuente, ADC, AMTI y ESP32 llegan al mismo punto físico (⑤) | Continuidad entre los 4 |
| 0.6 | Marca del módulo del ESP32: **WROOM** (OK) o **WROVER** (en WROVER GPIO16/17 son de la PSRAM → el UART2 de GPIO17 no sirve) | WROOM |

## ETAPA 1 — LAPTOP (ESP32 por su USB; sin RPi, sin ESP32 de motores, sin mover nada)

**L1. Solo la fuente de 5 V del ADC** (ESP32 sin USB, AMTI apagado). Si la fuente tiene límite de
corriente, ponerlo bajo (~100 mA). Medir: 5 V a la entrada y después de R5 (≈ 5 V − 0.02 V);
salida del regulador ≈ 3.3 V; **PDWN ≈ 3.3 V**; VREF ≈ 2.5 V (ADR03); corriente ≈ 10 mA (medida
el 2026-11-11). Si algo falla → apagar y revisar ese tramo.

**L2. Flashear y ver el arranque, con las entradas CORTOCIRCUITADAS** (AMTI desconectado, un cable
uniendo el lado AMTI de las dos 1 kΩ). Así se prueba el ADC solo, sin el AMTI de por medio.
```
cd control/firmware/lectura_ads1256_esp32_diferencial
esptool.py --port COMx read_flash 0x0 0x400000 respaldo_esp32_lectura.bin   # SIEMPRE antes
pio run -e esp32dev -t upload --upload-port COMx
python ../../../pruebas/registrar_diag_esp32_usb.py --puerto COMx --minutos 2
```
Criterio: 4 registros `OK`, `ADS1256 OK`, `n` ≈ 1000/s, `perdidas`=`ceros`=`saturadas`=0,
`fz_media` ≈ 0 N (pocos N de offset), `fz_sd` pequeño (anotar: es el **piso de ruido del ADC**).

**L3. AMTI conectado, plato vacío, amplificador en la configuración vigente** (excitación 10 V,
ganancia 2000, zero setpoint 0 — si cambia, la escala cambia, incidente 2026-11-05).
Criterio: offset estable; `fz_sd` del orden del lector directo anterior (σ≈0.85 N, referencia, no
exigencia). **Signo:** poner una masa conocida (2.5 kg → +24.5 N): Fz debe SUBIR; si baja, AIN0 y
AIN1 están invertidos. **Escala:** 3–4 masas conocidas, 5 s cada una, comparar con NetForce →
recta medida vs real. Se espera un error de ganancia de ~1 % (ver falla F11): se corrige con la
pendiente medida, no se supone.

**L4. UART2 en la laptop (solo si hay adaptador USB-TTL de 3.3 V).** Conectar SOLO: GPIO17 del
ESP32 → RX del adaptador, y GND ↔ GND. **No** conectar el TX del adaptador; jumper en 3.3 V.
```
python pruebas/leer_ads1256_fz_esp32_uart.py --puerto COMy --n 5000 --salida pruebas/resultados/uart_laptop.csv
```
Criterio: ≈1000 muestras/s, mismos valores que el resumen del USB. Sin adaptador: esta prueba se
hace en el RPi (R2), que es el mismo camino.

**L5. Vigilancia 30 min en reposo** (`registrar_diag_esp32_usb.py --minutos 30`, y el vigilante si
hay adaptador). Criterio: 0 `ALERTA`, 0 `perdidas`, 0 `ceros`. Luego 10 min con
`pio run -e sin_bt -t upload` y comparar `fz_sd` con/sin Bluetooth. Si se puede, una corrida con
la laptop **a batería** y otra **con cargador** (lazo de tierra, F22).

**✅ Pasar al RPi solo si L2–L5 cumplen.** Anotar los números (offset, σ, pendiente) en un reporte:
son la referencia contra la que se compara en el RPi.

## ETAPA 2 — RPi (mismo ESP32 de lectura, ya validado)

**Atajo (2026-11-18): `pruebas/etapa2_rpi.sh preflight | r2 [N] | r3 [MIN] | r5 [vels]`** — revisa R0/R1 solo, guarda cada
salida en `pruebas/resultados/etapa2/` y NO corre R2 si el preflight está en MAL. Puerto por defecto **`/dev/ttyAMA0`**
(variable `PUERTO_FZ`). Ninguno probado aún con el ESP32 de lectura conectado.
**Visualización (2026-11-18):** `r2`/`r3`/`r5` abren solos el visor en vivo en la pantalla del RPi (`herramientas/visor_pruebas.py`,
se cierra por PID al terminar). Al terminar `r2` y `r3` sale la figura de resultados (`pruebas/graficar_etapa2.py`, PNG en
`pruebas/resultados/etapa2/figuras/`); `r5` deja el estado final como figura. **Para el criterio de R2 ("σ en el RPi ≈ σ en L3"):**
`CONTRA=<csv de L3 de la laptop> pruebas/etapa2_rpi.sh r2` superpone ambas corridas (mismo formato `intento,t_s,fz_n`). La figura
da σ normal y **σ robusta (MAD)**: usar la robusta para comparar, porque unos pocos picos de error de bit (como el 2026-11-05)
inflan σ sin cambiar el ruido típico. Probado con datos sintéticos y un puerto falso (pty), no con el ESP32 real.

**R0. (Pi 5, YA APLICADO el 2026-11-18, verificado por el preflight):** `dtoverlay=uart0-pi5` en `/boot/firmware/config.txt`,
sin `console=serial0` en `cmdline.txt`, reiniciado; `pinctrl get 14,15` → TXD0/RXD0. **En Pi 5 `/dev/serial0` apunta a
`ttyAMA10` (UART de depuración, NO el header): el puerto del ESP32 de lectura es `/dev/ttyAMA0`.** (El paso
`raspi-config → Serial` y la nota del mini-UART de Pi 3/4 NO aplican.)

**R1. Solo el ESP32 de lectura** (ESP32 de motores DESCONECTADO). GPIO17 del ESP32 → pin 10 del RPi
(GPIO15 RXD); GND → pin 6. El TX del RPi no se conecta. Luego `pruebas/etapa2_rpi.sh preflight` → debe dar
~1000 paquetes/s y Fz en reposo.

**R2.** `pruebas/etapa2_rpi.sh r2` (= `leer_ads1256_fz_esp32_uart.py --puerto /dev/ttyAMA0 --n 5000`) →
offset y σ iguales a L3 (± lo razonable). Si empeoran: el problema lo trae el RPi (tierra/fuente).

**R3.** `pruebas/etapa2_rpi.sh r3 30` (= `vigilar_adc_esp32_uart.py --puerto /dev/ttyAMA0 --minutos 30`) → 0 fallas.

**R4. Conectar el ESP32 de motores (sin mover nada)** e identificar sus puertos con
`ls -l /dev/serial/by-id/` (nombres fijos; `ttyUSBn` se renumera — pasó 60 veces el 2026-11-05).
Repetir R3 10 min: ¿enchufar el otro ESP32 cambia algo?

**R5. Servo Y en el aire** (con OK de Luis en ese momento): `pruebas/etapa2_rpi.sh r5` (ya adaptado:
`fuerza_vs_velocidad_y.py --fuente_fz uart --puerto_fz /dev/ttyAMA0`; pide escribir SI antes de mover; sin probar en hardware)
repite la prueba del 2026-11-10. El vigilante (R3) usa el MISMO puerto, así que no pueden correr a la vez: el script de R5
ya registra la Fz antes/durante/después, y la caída se ve como silencio (aborta con 'Sin muestras nuevas de Fz por UART'). Esta es la prueba
que de verdad dice si la nueva ruta resolvió las caídas.

**R6. Validar contra el AMTI/NetForce** (RMSE, como el 2026-11-03 con 1.89 N).

**R7. Lazo de Fz con contacto:** `control/lazo_fz_tiempo_real.py --fuente_fz uart --puerto_fz /dev/ttyAMA0 [--signo_fz -1]`
(ya adaptado 2026-11-18, probado solo con pty falso y `--simulado`). El signo de Fz se confirma en L3 (masa conocida sube Fz).
Pie en plana, hueco remedido, `--peso_sujeto_n 100 --fmax_n 150`.

---

## 1. Catálogo de fallas posibles (qué se ve → dónde mirar)

| # | Falla | Cómo se ve | Qué hacer |
|---|---|---|---|
| F1 | Corto 5 V–GND o fuente invertida | Fuente en límite, placa caliente | Etapa 0.2 antes de energizar |
| F2 | Regulador de PDWN mal armado | PDWN ≠ 3.3 V → chip apagado → `ERROR: DRDY no bajo tras RESET` | L1, hoja del regulador |
| F3 | Falta 5 V en la placa / R5 abierta | Igual que F2 | L1 |
| F4 | DIN/DOUT intercambiados, MISO suelto, R de 100 Ω abierta | `registros ... MAL` (todo 0x00 o 0xFF) | Etapa 0.1 |
| F5 | CS y DRDY intercambiados | `ERROR: DRDY ...` | Etapa 0.1 |
| F6 | GND sin unir en el punto único | σ grande, valores que derivan | Etapa 0.5 |
| F7 | AIN0/AIN1 invertidos | Al poner peso Fz BAJA | L3 (no daña: invertir cables o signo) |
| F8 | Entrada abierta (1 kΩ o borne suelto) | `saturadas` > 0 o valores erráticos | L2/L3 |
| F9 | Fz negativa < ≈ −57 N (AIN1 < AGND − 0.1 V, límite de la hoja SBAS288) | Lectura recortada/errónea en negativo | Mantener zero setpoint del AMTI; no confiar en Fz muy negativa |
| F10 | Amplificador AMTI con otra excitación/ganancia | Escala ≈ 8× (incidente 2026-11-05) | L3 con masa conocida |
| F11 | Error de ganancia por las 1 kΩ en serie frente a la impedancia de entrada del ADS1256 sin buffer (del orden de 150 kΩ con PGA 1 según la hoja — **NO VERIFICADO**) | Fz ≈ 1 % menor que NetForce | L3: calibrar la pendiente con masas |
| F12 | ESP32 WROVER | Nada por UART2 aunque el USB diga OK | Etapa 0.6 |
| F13 | ESP32 con alimentación débil (USB, picos de la radio Bluetooth) | `Ultimo reinicio: BROWNOUT`, reinicios | Otro cable/puerto USB, entorno `sin_bt` |
| F14 | UART2 a 115200 casi lleno: con Fz ≥ 1000 N cada paquete son 10 bytes → 87 % de la capacidad | `elapsed_max_us` alto, `perdidas` > 0 al cargar | Si pasa: subir baudios (decisión de Luis, cambia ambos lados) |
| F15 | El ADC se cae con la prueba en marcha | `ALERTA: 0 muestras en 1 s` cada segundo (el firmware NO reinicia el ADC solo) | Anotar qué se hacía; reset con botón EN del ESP32; ver si recupera |
| F16 | Paquetes corruptos por el UART | `corruptos` > 0 en el vigilante | Cable corto, GND junto al TX; en RPi usar PL011 |
| F17 | UART del RPi sin habilitar o con consola serie encima | Nada o basura en `/dev/ttyAMA0` | R0 |
| F18 | Adaptador USB-TTL a 5 V con su TX al GPIO16 | Puede dañar el ESP32 | L4: solo RX y GND, jumper 3.3 V |
| F19 | Confundir el ESP32 de lectura con el de motores | Abrir el de motores lo reinicia (freno bloquea/libera); flashear el equivocado | Identificar por `by-id` y desconectando uno; nunca `ttyUSB0` a ciegas |
| F20 | `ttyUSBn` cambia de número tras una desconexión | Script abre otro dispositivo | Usar `/dev/serial/by-id/...` |
| F21 | Perturbación de GND por el servo (hipótesis principal del 2026-11-06) | Fz se corre y/o cae solo con Y en marcha | R5; medir GND con el servo en marcha |
| F22 | Lazo de tierra de la laptop con cargador | σ distinto con/sin cargador | L5 |

## 2. Reglas que no se saltan

- **Nunca `HOME` con la prótesis montada.** Si hace falta, avisar a Luis.
- **Ningún movimiento sin el OK de Luis en ese momento.**
- Ejes al ESP32 de motores siempre como **entero**: 0 = X, 1 = Y, 2 = K. Nunca letras.
- Antes de flashear cualquier ESP32: `esptool read_flash` de respaldo, y medir después.
- `herramientas/monitor_gaitsim.py` sigue con el lector SPI directo — adaptarlo si se usa.
- No suponer nada: dato medido, con fuente, o marcado NO VERIFICADO.
- Reporte por sesión en `reportes/`, decisiones en `CLAUDE.md` en el mismo turno, `sync` antes de apagar el RPi.
- Git: `git fetch` y `git log origin/master -1` antes de cada commit; `git push` al cerrar algo.
- Nunca `pkill -f` / `pgrep -f` con el patrón en la misma línea: matar por PID.

## 3. Mapa rápido

- Rigidez medida (Ensayo A): talón 26.4, plana 23.0, punta 2.4 N/mm. Ganancia de la primera prueba: la del talón.
- Pendiente (aparte): `lazo_fz_tiempo_real.py` y el monitor aún leen por SPI directo.
- ADC del producto final (aparte, no bloquea Fz): AD7606 (Reland, pedido); esquema AD7606↔RPi pendiente.
