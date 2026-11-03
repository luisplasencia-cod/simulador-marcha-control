# control/ — todo lo del diseño del control (Fz, Fy, sagital)

Índice para seguir el orden. Lo medido en hardware sigue en `pruebas/` (rutas referenciadas por `INICIO_RPI.md`); aquí está lo que se diseña/simula con esas mediciones.

| Carpeta / archivo | Qué es | Estado |
|---|---|---|
| `referencia_grf/` | Curva objetivo REAL de Fz y duración del apoyo (Gutenberg, 350 sanos) + scripts reproducibles | verificada |
| `diagramas/` | Diagrama de bloques del lazo simulado (+ leyenda y ecuaciones), estilo skill `diagrama-bloques-control` | hecho 2026-11-03 |
| `simulacion/` | Simulación control en tiempo real vs ILC con la latencia como variable (modelo con supuestos) | hecha 2026-11-03, ver `simulacion/NOTAS.md` |
| `../pruebas/2026-11-02_latencia_amti_rpi_esp32.md` | Plan y resultados de latencia (Paso 1 y 2 medidos; Paso 3 pendiente) | parcial |
| `../pruebas/latencia_*.csv/.png` | Datos crudos de latencia | medido |
| `DECISION_TIPO_CONTROL.md` | Tipo de control propuesto y su justificación | provisional |
| `firmware/` | Parche propuesto para reducir el sondeo RX del ESP32 | no aplicado |
| `../reportes/` | Reportes diarios | al día |

## Latencia medida hasta ahora (insumo de la simulación)
RPi↔ESP32 RTT 5.97 ms · ADS1256+SPI+Python 1.6 ms (50 %) / 2.4 ms (90 %) · falta: amplificador AMTI (manual), cómputo RPi, ejecución ESP32.

**Dónde está la metodología y los resultados:** `../reportes/2026-11-03_reporte_dia.md` (cada tema: objetivo, metodología, resultado, limitaciones, fuentes). Retardo del amplificador AMTI: `../pruebas/calcular_retardo_amti_manual.py`.
