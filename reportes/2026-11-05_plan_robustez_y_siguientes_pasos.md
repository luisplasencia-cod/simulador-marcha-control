# 2026-11-05 — Plan ordenado: robustez de ADC/USB y siguientes pasos hasta el control de Fz

## 1. Dónde estamos (todo lo hecho hasta ahora, con su reporte)
| Tema | Estado | Detalle |
|---|---|---|
| Latencia total del lazo (flanco→ADC→RPi→`MANUAL`→ack) | MEDIDA: 7.945 ms (σ 1.79, n=30) sin AMTI ni cómputo | `2026-11-05_adc_fuente_externa_y_esp32.md` |
| Picos de Fz | = errores de bit del SPI (0.06–0.5 % de muestras); mediana de 3 en el monitor; con Y activo empeora (hasta 2.24 %) | `2026-11-05_picos_fz_y_filtrado.md` |
| Rigidez k | solo PARCIAL: ≈28 N/mm a ≈5° (a ojo), corrida 3 incompleta; sin talón/plana/punta completos | `2026-11-05_ensayo_A_corridas_y_fallos_usb.md` |
| Ángulos y pasos | talón +11.14° (+682 pasos desde ≈5°); punta −37.30° (−4700); plana ≈0° (−555 pasos desde +5°); K = 111.11 pasos/° (gaitsim); signo confirmado por Luis | mismo reporte |
| Herramientas | `ensayo_A_rigidez.py` (aprox. por etapas, subida registrada, reconexión calmada), `visor_ensayo_A.py` (pantalla grande), `rotar_sagital.py`, `comparar_k_por_angulo.py` | `control/identificacion/` |
| Fallos de cadena de medición | ADC cae y revive solo tras CICLAR la alimentación de 5 V; USB del ESP32 se cae al cargar Y | §2–3 |

## 2. ¿Se necesita resistencia o condensador? ¿Sobrecorriente o sobretensión? (análisis, NADA de esto está verificado en esta placa)
**Hechos que sí tenemos:**
- Datos de TI (SBAS288, vía búsqueda web, **verificar en el PDF**): AVDD abs. máx. 6 V; DVDD abs. máx. 3.6 V; las entradas de control (DIN, SCLK, CS, RESET, SYNC/PDWN) soportan hasta 6 V respecto de DGND (D0/CLKOUT y D1–D3 solo DVDD+0.3 V). → El "DIN suelto = 4.6 V" medido el 11-05 NO implica por sí solo daño de entrada; la preocupación previa se rebaja (aún sin identificar el modelo de la placa).
- El ADC revive solo cuando se quita y vuelve la alimentación (antes reiniciando el RPi, que alimentaba el 5 V; ahora ciclando la fuente externa). Un RESET por software/SPI no lo recupera → apunta a que la alimentación del chip/placa cae o hay un estado bloqueado (brownout/latch) que solo se limpia sin tensión.
- Las dos caídas del ADC de hoy coinciden con eventos del USB/servo: 15:47 (21 caídas de USB en la corrida 3); el rail 3V3 de la Pi estuvo sano (3.303 V).
- Medido: errores de bit SPI ×5–9 con el servo vertical activo; no mejoran bajando el reloj.
**Hipótesis ordenadas (por probabilidad según la evidencia, no demostradas):**
1. Perturbación de masa/alimentación al cargar el servo vertical (corriente alta) → rebota GND entre servo, ESP32 y ADC (bucles de tierra: RPi–USB–ESP32–driver y fuente externa–ADC–AMTI).
2. Fuente externa de 5 V del ADC con poco margen o sin desacoplo en la placa (el 5 V del RPi ya había resultado insuficiente antes).
3. Cableado SPI largo y sin trenzar (picos, errores de bit, y la línea DOUT que no se recupera).
4. Sobretensión de entrada analógica por el AMTI: NO probable con el rango documentado (máx 3.53 V de 5 V), pero **no se midió la salida real del AMTI** en fallo/encendido.
**Componentes que se proponen (ingeniería estándar, SIN probar aquí; se aplican de a uno y se mide el efecto):**
- Alimentación del ADC: 100 µF (electrolítico/tantalio) + 100 nF cerámico justo en el conector de 5 V de la placa; cuentas de ferrita en serie con el 5 V; medir el 5 V con multímetro en mín./máx. mientras el servo se carga.
- Tierra: un solo punto en estrella (RPi, placa ADC, referencia del AMTI junto a AIN0, ESP32); no cerrar bucles por el blindaje USB.
- SPI: cables ≤ 15–20 cm, cada señal trenzada con GND; resistencia de 33–100 Ω en serie en SCLK/DIN (lado RPi) y en DOUT (lado placa); no filtrar más (bajar el reloj no ayudó).
- Entrada analógica (si se mide que el AMTI puede pasar de 5 V): 1 kΩ en serie + diodos/TVS al riel.
- ESP32/USB: cable USB corto y bueno con ferrita; alimentar el ESP32 aparte (VIN) dejando el USB solo para datos **solo si se verifica que la placa no retroalimenta**; opción más robusta: aislador USB (galvánico) o hub USB con fuente propia; separar físicamente los cables STEP/DIR de los de potencia del servo.

## 3. Lo que descubrimos del ESP32 (leído del firmware, sin modificar)
- `setup()` hace `brake_init(Y_BRAKE_PIN, LOCKED)` → `delay(500)` → … → `brake_set(Y_BRAKE_PIN, RELEASED)` → `delay(500)`: **cada reinicio del ESP32 bloquea y vuelve a liberar el freno del eje vertical**. `MANUAL` NO toca el freno en cada movimiento (mi hipótesis previa de "freno por escalón" era FALSA: comprobada en `main.cpp`).
- Cada apertura del puerto serie por mi script reinicia el ESP32 (DTR/RTS del CP2102 conectados a EN) → **reabrir el puerto en medio de una tormenta de caídas del USB re-ciclaba el freno vertical con el pie cargado** (≈116 N). Corrección hecha: la reconexión del ensayo ahora espera a que el enlace `by-id` exista y esté estable 4 s y espacia los intentos ≥8 s.
- Todos los ack fueron `OK` (sin `BUSY` ni errores); el ESP32 no imprime nada al abrir (0 bytes en 3 s) y responde `PONG`. Las caídas son del adaptador USB (`cp210x ... -19`, `converter now disconnected`).
- Talón (16:05): el USB cayó 8 veces entre las 16:05:43 y las 16:05:51 justo al tocar (224 mm, 15.7 N). Con la 3.ª corrida (116 N) y la 2.ª (208.6 mm, sin contacto) son 3 corridas con caída; 2 coinciden con carga/contacto.
**Cómo averiguar la causa con los "errores del ESP32" (propuesta):** (a) un registrador de un solo proceso que mantenga el puerto abierto y guarde con hora todo lo que el ESP32 imprima (los reinicios por brownout imprimen `rst:0x..` / `Brownout detector was triggered` por UART0 a 115200); (b) seguir `dmesg` a la vez con la misma base de tiempo; (c) añadir al firmware (autorizado por Luis, se flashea desde la laptop) `esp_reset_reason()` al arrancar y un contador de reinicios en `GET_POSITION`/`TRAJ_STATUS`; (d) con multímetro en mín./máx.: 5 V del ADC, 5 V del ESP32 (pin 5V/VIN) y 3.3 V mientras el servo carga.

## 4. Orden de trabajo cuando el hardware coopere
1. **Puerta de salud (2 min):** init del ADC (≤3 intentos), 3000 muestras con <0.5 % malas, `PING` y un `GET_POSITION`; sin USB caído en los últimos 5 min. Si falla → no mover nada.
2. **Talón (+11.14°)** — repetir hasta obtener una corrida completa (con subida), con visor en la pantalla de la Pi.
3. **Plana (≈0°)** (−1.5° respecto del giro anterior… se recalcula desde `estado_angulo_K.json`) y **punta (−37.3°)**; tras cada giro Luis confirma el hueco; tope de fuerza 100 N en talón/punta.
4. **Comparación** con `comparar_k_por_angulo.py` (curvas alineadas + barras de k) y reporte con tabla y figura.
5. **k → ganancia pasos/N** para `fz_ilc.py` (con la pendiente de la condición de diseño); recién entonces el lazo de Fz (ILC y luego realimentación con `SET_VEL`).
6. En paralelo, **correcciones de hardware** de §2 una a una, midiendo la tasa de errores del ADC y las caídas del USB tras cada cambio.
## 5. Pendientes de Luis
Cuál es la causa del evento de las 15:47 (qué pasó en la fuente de 5 V); modelo y corriente de la fuente externa del ADC; ciclar el 5 V cuando el ADC cae (ya sabe); mediciones con multímetro (5 V ADC, 5 V ESP32); si autoriza el registrador serie y el cambio de firmware para `esp_reset_reason()`; aprobar el cambio de cable/aislador USB.
**Fuentes:** firmware `main.cpp` (setup, brake), `hardware_config.h`; datasheet TI ADS1256 SBAS288 ([resumen de búsqueda](https://www.ti.com/lit/SBAS288), verificar valores en el PDF); consejos genéricos de brownout/USB de [universal-solder](https://www.universal-solder.ca/troubleshooting-esp32-brownout/) y [espboards](https://www.espboards.dev/troubleshooting/issues/power/esp32-power-path-conflict/) (no específicos de este rig).
