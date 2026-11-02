# Configuración actual — AMTI → ADS1256 → Raspberry Pi

Esquema: `salida/esquema_amti_ads1256_rpi.png` (generado por `esquema_amti_ads1256_rpi.py`).

## Estado (2026-11-02)
- Conectado hoy: solo el canal **Fz** del AMTI.
- AMTI entrega salida single-ended: 1 cable de señal + 1 cable de referencia.
- Escala medida por Luis: **1.7 V por cada 1000 N**, máximo **2000 N → 3.4 V**.
- ADC: **ADS1256** (8 canales, 24 bit). Modelo exacto de la placa breakout: **por confirmar**.

## Conexión analógica (verificada contra datasheet TI ADS1256 Rev K)
| AMTI | → | ADS1256 |
|---|---|---|
| Señal Fz | → | AIN0 |
| Referencia | → | AINCOM |

AINCOM no necesita ir a GND (confirmado en datasheet).

## Pendiente de verificar antes de energizar
1. **VREFP−VREFN real de la placa** (medir con multímetro). Con PGA=1, full-scale = ±2·VREF; se necesita VREF ≥ 1.7 V para no saturar con los 3.4 V máximos.
2. **Mapeo de pines ADS1256↔GPIO del Raspberry Pi** — depende del modelo exacto de la placa breakout. El esquema lo dibuja solo por función (CS, DRDY, MISO, MOSI, SCLK), no por número de pin físico.
3. Modelo exacto de la placa ADS1256 que tiene Luis.

## Historial de cambios
- 2026-11-02: primera versión del esquema, a partir de datos verificados del datasheet TI ADS1256 Rev K (SBAS288K) y la escala de AMTI medida por Luis en el lab.
