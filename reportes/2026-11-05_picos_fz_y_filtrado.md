# 2026-11-05 — Picos espurios de Fz: son errores de bit del SPI; filtro de mediana de 3

**Objetivo:** explicar por qué el monitor muestra picos (hasta ±2830 N con el plato vacío) y definir un filtrado adecuado para el lazo de control.

**Metodología:** (1) análisis de ventanas de 0.1 s en `logs/monitor_20261105_144227.log` y `..._144923.log` (min/media/max de Fz); (2) `pruebas/prueba_errores_spi.py`: 5000 muestras por velocidad de reloj SPI, muestra "mala" = |V−mediana|>0.05 V (~28 N), plato en reposo; (3) `pruebas/analizar_rafagas_spi.py`: 30000 muestras crudas (500 kHz), conteo de ráfagas y prueba de medianas causales sobre los mismos datos. (Un agente delegado falló por error de API sin producir resultados; el análisis lo hice yo.)

**Resultado:**
- 27 % (log 14:42) y 40 % (log 14:49) de las ventanas de 0.1 s tienen una muestra a >15 N de la media.
- Los valores de los picos son **potencias de 2 del código de 24 bits**: ±2830.4 N = fondo de escala (2²³, 5 V/1.7665 mV/N); −1415.2 N = 2²²; −353.8 N = 2²⁰; −66.6 ≈ 2¹⁷+2¹⁶; −111 ≈ 2¹⁸+2¹⁶; −188.7 ≈ 2¹⁹+2¹⁵ → patrón típico de **bits erróneos en la palabra leída por SPI**, no ruido analógico (el ruido normal es σ≈0.9 N).
- Tasa de muestras malas vs. reloj SPI (n=5000): 1 MHz 0.06 %, 500 kHz 0.30 %, 250 kHz 0.50 %; a 100 kHz el chip no devolvió lo escrito en la inicialización. Bajar el reloj **no** mejora (empeora). 0.3 % de muestras × ~110 muestras/ventana ≈ 28 % de ventanas: consistente con lo observado.
- Con 30000 muestras: 74 malas (0.25 %), **todas aisladas** (74 ráfagas de longitud 1, ninguna de 2 o más). Sin filtrar, peor desviación 453 N.
- Mediana causal de 3: 0/29998 muestras malas, peor desviación 2.7 N, σ 0.55 N, retardo 1 ms (1 muestra). Mediana de 5: 0 malas, peor 2.0 N, σ 0.44 N, retardo 2 ms.
- **Aplicado:** mediana de 3 en `herramientas/monitor_gaitsim.py` (hilo del ADC; afecta también lo que graba el monitor). El filtro IIR visual de 10 Hz (retardo 15.9 ms) enmascaraba esto pero no lo corregía, y es demasiado lento para el lazo.

**Recomendación para el lazo de control:** mediana causal de 3 sobre el dato crudo (+1 ms), después, si hace falta, media móvil corta; no usar IIR de 10 Hz en el lazo (retardo ≈ 16 ms, ver `control/filtro_fz/salida_analisis_filtro_fz.txt`). Esto suma ≈1 ms a los ~8 ms de latencia medida.

**Limitaciones:** (1) causa raíz del error de bit **no determinada** (candidatos sin discriminar: cableado SPI largo/flojo —la 3.ª falla de contacto de hoy—, falta de GND común con la fuente externa de 5 V, acoplamiento del ESP32/USB); (2) medido solo con plato vacío y sin motores en marcha: la tasa puede subir con motores activos; (3) 74 eventos en una sola captura; (4) la mediana sirve solo mientras los errores sigan aislados (si aparecen ráfagas de ≥2 hay que reparar el cableado, no filtrar); (5) el umbral de 0.05 V para "mala" es elección mía; (6) la mediana atenúa picos de fuerza reales de 1 muestra (a x6 no existen: la curva objetivo tiene contenido <4 Hz).
**Experimento que falta:** repetir `prueba_errores_spi.py` con cables SPI más cortos / GND común verificado / ESP32 desconectado, y con motores moviéndose.
**Fuentes:** logs del monitor, `pruebas/prueba_errores_spi.py`, `pruebas/analizar_rafagas_spi.py`, `control/filtro_fz/salida_analisis_filtro_fz.txt`.

## Verificación en vivo (15:07, monitor reabierto con `--con-esp32`)
`logs/monitor_20261105_150704.log`, 209 ventanas de 0.1 s tras el filtro: **2 ventanas aún con mínimo < −15 N** (peor −69.4 N), frente a 27–40 % antes. Residual ≈ 1 %: la mediana de 3 no elimina todo en vivo (posible ráfaga de ≥2 muestras corruptas, no caracterizada porque esta captura solo guarda min/media/max por ventana). Ruido normal: mín/máx de ventana ≈ −3.7…−0.8 N. El ESP32 ya aparece en el monitor: RTT 7.75 ms (GET_POSITION/PING del monitor), pos=0,0,0 (contador reiniciado al abrir el puerto). Conclusión: mejora grande, no resuelto de raíz; mantener la mediana de 5 como alternativa si el residual molesta en el lazo y reparar el cableado SPI.

## Prueba con motores (15:15, `pruebas/errores_spi_con_motores.py`, 20000 muestras por condición, 500 kHz, plato vacío, sin prótesis)
| Condición | malas | ráfagas | long. máx | ráfagas ≥2 | σ de las buenas |
|---|---|---|---|---|---|
| quieto (inicio) | 52 (0.26 %) | 51 | 2 | 1 | 0.93 N |
| sagital K ±40 pasos | 70 (0.35 %) | 70 | 1 | 0 | 0.94 N |
| eje Y ±400 pasos (5 mm, solo hacia arriba y vuelta) | 288 (1.44 %) | 281 | **3** | 6 | **1.86 N** |
| quieto (final, DESPUÉS de mover Y) | 448 (2.24 %) | 446 | 2 | 2 | **2.17 N** |

**Lectura (hechos):** el sagital no cambia nada. El eje vertical Y sube los errores ~5× y el ruido normal (σ) se duplica, y **no vuelve a lo anterior al detenerse** (2.24 % y 2.17 N, aún peor). Aparecen ráfagas de 3 muestras: la mediana de 3 ya no basta (quita ráfagas de 1; de 2 en el mejor caso no). **Hipótesis NO verificada:** el servo/driver vertical queda energizado (¿freno liberado, servo habilitado?) tras el primer movimiento y su ruido de conmutación se acopla a SPI/entrada analógica; otra posibilidad es una deriva en el tiempo independiente del motor (no se descartó: no hubo un 2.º control "quieto" sin haber movido Y). **Implicación para el control de Fz:** la condición de operación es con Y activo, es decir justo la peor; hace falta reparar el acoplamiento (GND común, cables SPI/analógicos cortos y trenzados/blindados, alejarlos del cable del servo) y, mientras tanto, usar mediana de 5 o 7 (retardo 2–3 ms) — no probadas sobre estos datos porque el script solo guardó el conteo. **Pendiente:** repetir con Y activo guardando los datos crudos para elegir el filtro con evidencia.
