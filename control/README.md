# control/ — todo lo del diseño del control (Fz, Fy, sagital)

Índice para seguir el orden. Lo medido en hardware sigue en `pruebas/` (rutas referenciadas por `INICIO_RPI.md`); aquí está lo que se diseña/simula con esas mediciones.

| Carpeta / archivo | Qué es | Estado |
|---|---|---|
| `referencia_grf/` | Curva objetivo REAL de Fz y duración del apoyo (Gutenberg, 350 sanos) + scripts reproducibles | verificada |
| `diagramas/` | Diagrama de bloques matemático del lazo simulado (+ leyenda y ecuaciones), estilo skill `diagrama-bloques-control` | hecho 2026-11-03 |
| `diagramas/implementacion/` | Diagrama de implementación real (hardware/software): AMTI→ADS1256→RPi→`SET_VEL`→ESP32→driver→motor | hecho 2026-11-05, nada probado en hardware |
| `diagramas/referencias/` | Fotos reales del servo A6-750RS; freno del motor vertical (B1) confirmado en `conferencia_copy.pdf` | 2026-11-05 |
| `simulacion/` | Simulación control en tiempo real vs ILC con la latencia como variable (modelo con supuestos) | hecha 2026-11-03, ver `simulacion/NOTAS.md` |
| `../pruebas/2026-11-02_latencia_amti_rpi_esp32.md` | Plan y resultados de latencia (Paso 1 y 2 medidos; Paso 3 pendiente) | parcial |
| `../pruebas/latencia_*.csv/.png` | Datos crudos de latencia | medido |
| `DECISION_TIPO_CONTROL.md` | Tipo de control para Fz: REABIERTA, objetivo híbrido RT+ILC (Luis autorizó tocar firmware); Fy abierto | reabierta 2026-11-04 |
| `ilc/` | Implementación del ILC para Fz (núcleo genérico + Fz + subida al ESP32) | núcleo y Fz probados en planta sintética; subida al ESP32 sin probar en hardware |
| `telemetria/` | Formato de log + visor en vivo de $r^*(t)$, $F_{med}(t)$, $e(t)$, $u(t)$, $\delta(t)$ | probado con datos sintéticos; falta el script del lazo real en el RPi |
| `firmware/` | Parche de velocidad continua `SET_VEL` (tiempo real) + parche opcional de sondeo RX | `SET_VEL` diseñado y verificado con `git apply --check`, no compilado/flasheado |
| `../reportes/` | Reportes diarios | al día |

## Latencia medida hasta ahora (insumo de la simulación)
RPi↔ESP32 RTT 5.97 ms · ADS1256+SPI+Python 1.6 ms (50 %) / 2.4 ms (90 %) · falta: amplificador AMTI (manual), cómputo RPi, ejecución ESP32.

**Dónde está la metodología y los resultados:** `../reportes/2026-11-03_reporte_dia.md` (cada tema: objetivo, metodología, resultado, limitaciones, fuentes). Retardo del amplificador AMTI: `../pruebas/calcular_retardo_amti_manual.py`.
