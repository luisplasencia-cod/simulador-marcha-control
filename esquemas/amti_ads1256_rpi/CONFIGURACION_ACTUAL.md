# Configuración actual — AMTI → ADS1256 → Raspberry Pi

Esquema: `salida/esquema_amti_ads1256_rpi.png` (generado por `esquema_amti_ads1256_rpi.py`).

## Estado (2026-11-02)
- Conectado hoy: solo el canal **Fz** del AMTI.
- AMTI entrega salida single-ended: 1 cable de señal + 1 cable de referencia.
- Escala (Luis, 2026-11-02): **1.7665 mV/N** (AMTI OPT SC serie 4306, ganancia Fz 2000), máximo **2000 N → 3.53 V** (antes 1.7 mV/N; la diferencia es 3.9 %). A verificar con pesas conocidas.
- **(2026-11-05) Configuración del amplificador en NetForce (Luis): Fz excitación 10 V, ganancia 2000, zero setpoint 0 → NetForce muestra *analog scale factor* = 1.7665 mV/N** (coincide con la constante del monitor, `N_PER_1000N`). Incidente del día: el amplificador tenía otra configuración y el monitor leía ≈8–9× de más (200–220 N con 2.5 kg ≈ 24.5 N; NetForce marcaba ≈25 N). Tras fijar 10 V / 2000 y tarar en ambos lados, con 2.5 kg Luis ve monitor ≈ NetForce (comparación visual, **sin ajuste lineal con varias masas todavía**). **La escala solo vale con esta configuración: si alguien cambia excitación o ganancia en NetForce, hay que recalcular.**
- ADC: **ADS1256** (8 canales, 24 bit). Modelo exacto de la placa breakout: **por confirmar**.

## Conexión analógica (pines leídos de la etiqueta física de la placa, por Luis, 2026-11-02)
| AMTI | → | ADS1256 (esta placa) |
|---|---|---|
| Señal Fz | → | AIN0 |
| Referencia | → | GND (el que está junto a AIN0 en la placa) |

La placa expone 8 pares AINx/GND (uno por canal) en un lado, y en el otro: 5V, GND, SCLK, DIN, DOUT, DRDY, CS, PDWN. No se identificó un pin VREF aparte.

## Conexión digital (RPi) — decidido 2026-11-02
| ADS1256 | → | Raspberry Pi |
|---|---|---|
| 5V | → | 5V |
| GND | → | GND |
| SCLK | → | GPIO11 (SPI0_SCLK, fijo por hardware) |
| DIN | → | GPIO10 (SPI0_MOSI, fijo por hardware) |
| DOUT | → | GPIO9 (SPI0_MISO, fijo por hardware) |
| CS | → | GPIO8 (SPI0_CE0, fijo por hardware) |
| DRDY | → | GPIO17 (elegido por Michael; libre, sin conflicto — cambiar aquí y en el software si se prefiere otro) |
| PDWN | → | **+3.3V del RPi directo (NO es un GPIO)** — así queda en ALTO siempre, incluso antes de correr el script |

GPIO8/9/10/11 son el bus SPI0 estándar de cualquier Raspberry Pi de 40 pines — no dependen del modelo de placa ADS1256. Confirmar la numeración física con el comando `pinout` en el propio RPi.

## VREF — resuelto (2026-11-02)
Chip identificado físicamente en la placa por Luis: **ADR03B** (Analog Devices), referencia de precisión, grado B = ±0.1%. Dato de fábrica del ADR03: **2.5V nominal** (confirmado por búsqueda web de la familia ADR01/02/03/06, 2026-11-02).

Full-scale con PGA=1 = 2·VREF/PGA = **5V**. Los 3.4V máximos del AMTI quedan al 68% del rango — sin riesgo de saturar, margen de resolución adecuado.

Los otros 2 chips de la placa, identificados: **AMS1117-3.3** (regulador LDO genérico, alimenta la lógica de 3.3V — NO es la referencia, su tolerancia ±1.5-2% es demasiado imprecisa para eso) y **ADS1256** mismo (el ADC, marcaje "...DB" = empaque SSOP-28). Hay además un chip **"BB OPA 3550A"** (op-amp Burr-Brown/TI, probablemente buffer de la señal de entrada, no afecta esta conclusión).

## Conexión TEMPORAL — prueba de latencia (2026-11-03, hecha por Luis; retirar al terminar las pruebas)
No forma parte de la configuración permanente. Solo sirve para `pruebas/medir_latencia_gpio_adc.py`.
| Origen | → | Destino |
|---|---|---|
| RPi GPIO27 (pin físico 13) | → | R1 = 10 kΩ |
| R1 (otra pata) = nodo del divisor | → | AIN1 (placa ADS1256) |
| Nodo del divisor | → | R2 = 10 kΩ → GND junto a AIN1 (AINCOM) |
Valores reales usados: 10k/10k (Luis). Nivel bajo medido 47 mV, alto 1613 mV (salto 1.566 V). GPIO27 queda además reservado mientras esté armado.

## Pendiente
1. Modelo exacto de la placa ADS1256 (fabricante/vendedor) — no crítico ya, VREF resuelto por chip identificado.

## Historial de cambios
- 2026-11-02: primera versión del esquema, a partir de datos verificados del datasheet TI ADS1256 Rev K (SBAS288K) y la escala de AMTI medida por Luis en el lab.
- 2026-11-02 (misma sesión, actualización): reemplazados los pines genéricos del chip por los pines reales leídos de la etiqueta física de la placa de Luis (AIN0/GND por canal; 5V, GND, SCLK, DIN, DOUT, DRDY, CS, PDWN). Se retiró la suposición de AINCOM/VREFP/VREFN como pines expuestos — esta placa no los muestra así.

## PROPUESTA (2026-11-10, NO implementada ni probada): protecciones contra la caída del ADS1256
Esquema: `salida/esquema_protecciones_ads1256.png` (+ `.svg`), generado por `esquema_protecciones_ads1256.py` (schemdraw, mismo estilo). **Son hipótesis de práctica** (foros TI E2E, notas de aplicación sobre ruido de servos; ver `reportes/2026-11-10_restauracion_firmware_original.md`), con valores típicos no calculados para esta placa:
① 47 Ω en serie en SCLK, DIN y CS (cerca del RPi). ② PDWN: cable a 3V3 (pin 1) soldado + 10 kΩ a OTRO 3V3 (pin 17) + 100 nF a GND (un pull-up al mismo cable de 3V3 no protege si ese cable se suelta). ③ AIN0: 1 kΩ + 100 nF (fc ≈ 1.6 kHz); verificar la impedancia de salida del AMTI (no medida). ④ Entrada de 5 V: ferrita en serie + C1 100 µF + C2 100 nF pegados al módulo; AVDD debe estar en 4.75–5.25 V (medir con el servo en marcha); ferrita según la corriente real de la placa (no medida). ⑤ GND de fuente externa, ADC, AMTI y RPi en un solo punto; cable del AMTI blindado (malla a GND en un extremo) y ≥ 30 cm del cable del servo/freno.
Antes de soldar nada: con el ADC caído, medir 5 V de entrada, 3.3 V del regulador AMS1117, VREF (ADR03B, 2.5 V) y PDWN (≈3.3 V).
