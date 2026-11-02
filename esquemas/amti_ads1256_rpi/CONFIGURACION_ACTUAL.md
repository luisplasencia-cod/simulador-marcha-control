# Configuración actual — AMTI → ADS1256 → Raspberry Pi

Esquema: `salida/esquema_amti_ads1256_rpi.png` (generado por `esquema_amti_ads1256_rpi.py`).

## Estado (2026-11-02)
- Conectado hoy: solo el canal **Fz** del AMTI.
- AMTI entrega salida single-ended: 1 cable de señal + 1 cable de referencia.
- Escala medida por Luis: **1.7 V por cada 1000 N**, máximo **2000 N → 3.4 V**.
- ADC: **ADS1256** (8 canales, 24 bit). Modelo exacto de la placa breakout: **por confirmar**.

## Conexión analógica (pines leídos de la etiqueta física de la placa, por Luis, 2026-11-02)
| AMTI | → | ADS1256 (esta placa) |
|---|---|---|
| Señal Fz | → | AIN0 |
| Referencia | → | GND (el que está junto a AIN0 en la placa) |

La placa expone 8 pares AINx/GND (uno por canal) en un lado, y en el otro: 5V, GND, SCLK, DIN, DOUT, DRDY, CS, PDWN. No se identificó un pin VREF aparte.

## Pendiente de verificar antes de energizar
1. **VREF de esta placa** — no aparece como pin independiente en lo reportado. Puede ser referencia interna fija o un test point sin etiquetar. Con PGA=1, full-scale = 2·VREF; se necesita VREF ≥ 1.7 V para no saturar con los 3.4 V máximos del AMTI. Pendiente: buscar el modelo exacto de la placa (circuito impreso) o un test point VREF.
2. **PDWN debe quedar en ALTO** para operación normal — confirmar si la placa ya lo fuerza así o si hay que cablearlo a 5V/3V3.
3. **Mapeo de los 8 pines digitales a GPIO específicos del Raspberry Pi** — no definido aún, lo elige Luis en el software (anotar aquí apenas se defina).
4. Modelo exacto de la placa ADS1256.

## Historial de cambios
- 2026-11-02: primera versión del esquema, a partir de datos verificados del datasheet TI ADS1256 Rev K (SBAS288K) y la escala de AMTI medida por Luis en el lab.
- 2026-11-02 (misma sesión, actualización): reemplazados los pines genéricos del chip por los pines reales leídos de la etiqueta física de la placa de Luis (AIN0/GND por canal; 5V, GND, SCLK, DIN, DOUT, DRDY, CS, PDWN). Se retiró la suposición de AINCOM/VREFP/VREFN como pines expuestos — esta placa no los muestra así.
