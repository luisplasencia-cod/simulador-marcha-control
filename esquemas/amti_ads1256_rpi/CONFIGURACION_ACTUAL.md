# Configuración actual — AMTI → ADS1256 → Raspberry Pi

Esquema: `salida/esquema_amti_ads1256_rpi.png` (generado por `esquema_amti_ads1256_rpi.py`).

## Estado (2026-11-02)
- Conectado hoy: solo el canal **Fz** del AMTI.
- AMTI entrega salida single-ended: 1 cable de señal + 1 cable de referencia.
- Escala (Luis, 2026-11-02): **1.7665 mV/N** (AMTI OPT SC serie 4306, ganancia Fz 2000), máximo **2000 N → 3.53 V** (antes 1.7 mV/N; la diferencia es 3.9 %). A verificar con pesas conocidas.
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

## Pendiente
1. Modelo exacto de la placa ADS1256 (fabricante/vendedor) — no crítico ya, VREF resuelto por chip identificado.

## Historial de cambios
- 2026-11-02: primera versión del esquema, a partir de datos verificados del datasheet TI ADS1256 Rev K (SBAS288K) y la escala de AMTI medida por Luis en el lab.
- 2026-11-02 (misma sesión, actualización): reemplazados los pines genéricos del chip por los pines reales leídos de la etiqueta física de la placa de Luis (AIN0/GND por canal; 5V, GND, SCLK, DIN, DOUT, DRDY, CS, PDWN). Se retiró la suposición de AINCOM/VREFP/VREFN como pines expuestos — esta placa no los muestra así.
