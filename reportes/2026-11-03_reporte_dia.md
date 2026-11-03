# Reporte del día — 2026-11-03

Continuación de la etapa de control del simulador de marcha (sesión en el Raspberry Pi).

## 1. Estado del RPi
- Luis reparó el RPi tras el incidente del 2026-11-02. Sesión gráfica en **Wayland (`rpd-labwc`)** para recuperar el modo táctil (`/etc/lightdm/lightdm.conf`); el monitor (`herramientas/monitor_gaitsim.py`) abre bien bajo Wayland.
- ADS1256 responde (STATUS=0x30, MUX/ADCON/DRATE leídos de vuelta correctos). **ESP32 de motores: NO conectado hoy** (no hay `/dev/ttyUSB0`).
- **Observación a revisar:** AIN0 (Fz del AMTI) dio −55 mV con 55 mV pico a pico en el diagnóstico (el 2026-11-02 estaba estable en +38.9 mV). Apunta a conexión/estado del AMTI; no resuelto.

## 2. Latencia de adquisición RPi + ADS1256 (Paso 2) — MEDIDA
Sin video (Luis no puede grabarlo), así que se usó un **escalón eléctrico**: GPIO27 del RPi → divisor 10k/10k → AIN1 (vs AINCOM). Mismo reloj (`perf_counter_ns`) para el flanco y para la detección. Script: `pruebas/medir_latencia_gpio_adc.py`; datos: `pruebas/latencia_gpio_adc.csv`.
- Niveles: bajo 47 mV, alto 1613 mV (salto 1.566 V). 1000 SPS.
- n = 200 (100 subidas + 100 bajadas), 0 fallos.

| Punto del escalón | Media | σ | Máx |
|---|---|---|---|
| 50 % | 1.61 ms | 0.28 ms | 2.12 ms |
| 90 % | 2.40 ms | 0.28 ms | 2.90 ms |

- Incluye: filtro digital del ADS1256 + SPI + software Python. Subida y bajada sin diferencia relevante.
- **No incluye** el retardo del amplificador analógico del AMTI (sale del manual AMTI; no medido).
- Incertidumbre de t0: se toma justo antes de `GPIO.output()` (cota superior, decenas de µs).
- Un primer intento tenía un error en el umbral del 90 % de las bajadas (disparaba al 10 %); corregido antes de reportar.
- Conexión del divisor: **temporal** (`esquemas/amti_ads1256_rpi/CONFIGURACION_ACTUAL.md`).

## 3. Cambios de código
- `pruebas/medir_latencia_gpio_adc.py` (nuevo).
- `pruebas/medir_latencia_escalon_amti.py`: `t` se toma después de leer (antes sesgaba hasta 1 ms).

## 4. Latencia acumulada hasta ahora
| Tramo | Valor | Estado |
|---|---|---|
| Amplificador AMTI | — | pendiente (manual) |
| ADS1256 + SPI + Python | 1.6 ms (50 %) / 2.4 ms (90 %) | medido |
| RPi ↔ ESP32 (RTT, incl. polling 5 ms del firmware) | 5.97 ms | medido |
| Cómputo RPi del controlador | — | pendiente |
| Ejecución en ESP32 (comando → motor) | — | pendiente |
Parcial ≈ 8–9 ms. El umbral tolerable lo da la simulación (tiempo real vs ILC); sin él no se concluye.

## Pendiente
1. Simulación de control en tiempo real vs ILC con la latencia como variable (no requiere hardware).
2. Revisar AIN0 inestable (con el monitor abierto).
3. Repetir offset con el plato vacío y calibración con pesas (`pruebas/calibracion_pesas.py`, sin ejecutar); revisar la pérdida de muestras del monitor (≈928/s vs 1000).
4. Retardo del amplificador del AMTI desde el manual.
5. Conectar el ESP32 de motores para el Paso 3 (latencia total).
6. Respuesta de Dante Elías y confirmación de la asesora (sin novedad).

## 5. Simulación de control en tiempo real vs ILC (sin hardware)
**Figura:** [`control/simulacion/rt_vs_ilc_latencia.png`](../control/simulacion/rt_vs_ilc_latencia.png) · código: `control/simulacion/rt_vs_ilc_latencia.py` · números y sensibilidad: `control/simulacion/salida_consola.txt` · notas: `control/simulacion/NOTAS.md` · curva objetivo: `control/referencia_grf/`.

![Simulación RT vs ILC](../control/simulacion/rt_vs_ilc_latencia.png)

### 5.1 Por qué se hizo
Hay que decidir si el control de fuerza (Fz, Fy) se hace **en tiempo real** (corregir al instante con lo que mide el AMTI) o con **ILC** (aprender de un ciclo de marcha a otro). Lo que inclina la decisión es la **latencia**: el tiempo entre que la fuerza real cambia y el motor recibe una orden basada en esa medición. Ya medí parte (secciones 2 y 4). La simulación responde: **¿cuánta latencia aguanta cada estrategia y qué error de fuerza deja?**

### 5.2 Con qué datos se armó (verificado vs. supuesto)
| Elemento | Valor | Estado |
|---|---|---|
| **Fuerza objetivo** | Fz media de **350 sujetos sanos**, 8819 pisadas, normalizada al peso y a 101 puntos del apoyo. Picos 115.4 %BW (22 % del apoyo) y 117.8 %BW (78 %), valle 71.1 %BW (49 %), marcha autoseleccionada, media 1.40 m/s | **REAL**: Horst et al. 2021, *Gutenberg Gait Database*, Sci Data, DOI 10.1038/s41597-021-01014-6, datos CC0 en Figshare. Procesamiento reproducible en `control/referencia_grf/` |
| Latencia total T | se barre de 0 a 160 ms | variable; **medido hasta ahora ≈ 8–9 ms (parcial)** |
| Servo del eje | 1.er orden, 20 ms | **supuesto sin medir** → se barre 10/20/50 ms |
| Rigidez de contacto | real = 0.8 de la que "cree" el modelo | **supuesto sin medir** → se barre 0.5–1.5 |
| Duración del apoyo | 4 s | **supuesto** (≈ apoyo real × 6) → se barre 3/4/5 s |
| Perturbación (panel d) | pulso de 3 %BW, 0.1 s | supuesto; **sin impacto de talón** |
La curva del artículo propio no se usó (Luis indicó que no está del todo bien). Lo que sigue siendo supuesto se barre y se muestra la sensibilidad en vez de fijar un solo valor.

### 5.3 Términos (en simple)
- **%BW**: fuerza como porcentaje del peso corporal. Error de 10 %BW = 10 % del peso.
- **Error RMS**: tamaño "típico" de la diferencia entre la fuerza pedida y la lograda durante todo el apoyo. Menor = mejor.
- **RT (tiempo real)**: el controlador mira la fuerza medida y corrige al instante, con una ganancia Kp.
- **RT+FF**: igual, más "adelantar" la pendiente de la curva objetivo (prealimentación); depende de conocer bien la rigidez.
- **ILC**: el mismo control más una corrección que se **aprende al terminar cada ciclo** y se aplica en el siguiente.
- **T máx (línea gris)**: el retardo que aguanta el lazo antes de volverse oscilante, con un margen de fase de 45° (criterio de diseño usual).

### 5.4 Cómo leer cada panel y qué se observa
- **(a) Forma de la fuerza con T = 10 ms.** Negra punteada = la curva real que queremos. **ILC (verde) y RT+FF (naranja) la tapan casi por completo. RT solo (rojo) llega tarde** (corrido a la derecha, sobre todo en la subida y en el segundo pico): es el atraso típico de un control que solo reacciona.
- **(b) Error RMS vs latencia** (eje vertical logarítmico: cada raya es 10 veces más). (1) ILC (verde) está ≈ 30 veces debajo de RT (rojo) con T moderado (0.32 vs 10.8 %BW a 10 ms). (2) ILC se mantiene en ≈ 0.3 hasta 40 ms, sube a 0.5 (60 ms), 1.0 (80 ms), 2.9 (100 ms) y **sale del gráfico hacia 130 ms (inestable)**. (3) La línea gris en 60 ms es T máx para Kp=10. (4) **Cuidado con la roja**: baja al subir la latencia hasta ~80 ms; no es que el retardo ayude, es una compensación casual del modelo mientras el lazo pierde margen. Lo mismo explica el mínimo de la naranja en 20 ms.
- **(c) Aprendizaje del ILC.** Cada punto es un ciclo. Con T = 10 ms el error baja de 11.2 %BW (ciclo 1) a 0.32 (ciclo 12); con T = 60 ms baja parecido pero **se estanca en ≈ 0.54**: más latencia deja un error final mayor. ILC necesita ~10 ciclos y solo sirve si el ciclo se repite igual.
- **(d) Con una perturbación que no se repite.** ILC sube un poco (0.6 %BW a 10 ms) y sigue muy por debajo de RT (10.8). **No prueba que ILC rechace perturbaciones reales**: ILC no aprende lo que cambia cada ciclo y aquí solo hay un pulso chico, sin impacto de talón.

### 5.5 Sensibilidad (lo que no está medido)
A T = 10 ms, barriendo servo (10/20/50 ms) × rigidez (0.5–1.5): RT queda entre **5.7 y 16.8 %BW** e ILC entre **0.2 y 1.3 %BW**. Con apoyo de 3/4/5 s: RT 13.7/10.8/8.9, ILC 0.8/0.3/0.2. Es decir, **ILC ≪ RT puro en todos los casos probados**, aunque los valores absolutos dependen de lo no medido.

### 5.6 Qué se puede y qué no se puede decir
**Se puede decir (curva real, planta supuesta y barrida):**
- La latencia pone un **techo al ancho de banda** del tiempo real: ganancia de lazo 10 → T máx 60 ms; 15 → 35 ms; 20 → 23 ms; 40 → 6 ms.
- Con la latencia medida hoy (≈ 8–9 ms parcial) y Kp=10, **la latencia no domina el error de RT**; lo domina el ancho de banda (Kp=5: 18.0 %BW, Kp=10: 10.8, Kp=20: 5.5).
- ILC reduce el error repetible a ≈ 0.3 %BW en ~12 ciclos y tolera latencia hasta ~60 ms con error < 1 %BW.

**NO se puede decir todavía:**
- Que ILC sea mejor que tiempo real en el simulador real: faltan el servo y la rigidez por prótesis, el impacto de talón, la fricción/holguras.
- Un límite de latencia del simulador real (sale de los supuestos).
- Una latencia total: faltan el amplificador del AMTI (manual), el cómputo del RPi y la ejecución del ESP32.
- Qué curva usar como objetivo final: la de Gutenberg es marcha normal (1.40 m/s), mientras el simulador publicó marcha lenta (0.48 m/s, picos ≈ 100 %BW). **Decisión pendiente de Luis.**

**Para cerrarlo:** identificar el servo vertical y la rigidez de contacto, medir la latencia restante, fijar la duración real del apoyo a x6 y repetir.

### 5.7 Cómo explicarlo en 30 segundos
"Usé la curva real de fuerza vertical de 350 personas sanas y simulé un lazo de fuerza variando la latencia. El control en tiempo real llega tarde a la curva (≈ 11 %BW de error); el ILC la sigue casi exacto (≈ 0.3 %BW) después de unos 10 ciclos y aguanta bastante retardo. Con la latencia que medí (≈ 8–9 ms) el retardo no es el problema principal. La planta del simulador la supuse y la barrí; lo siguiente es medir el servo y la rigidez reales para confirmarlo."

## 6. Tipo de control — propuesta provisional
Detalle y justificación en [`control/DECISION_TIPO_CONTROL.md`](../control/DECISION_TIPO_CONTROL.md). **Propuesta:** control híbrido por eje (Fz, Fy) = realimentación de fuerza en tiempo real como base + ILC ciclo a ciclo encima. Se apoya en la simulación (§ 5, con supuestos) y en la latencia medida; **no está cerrada**: faltan servo y rigidez reales, la latencia restante y la confirmación de la asesora.

## 7. Firmware del ESP32 — propuesta (no aplicada)
`communication_rx()` espera con `vTaskDelay(5 ms)` en **dos** sitios (primer byte y bytes siguientes del mensaje), por eso el RTT de 5.97 ms es casi todo sondeo. Parche propuesto (sondeo de 1 ms) en `control/firmware/reducir_polling_rx.patch`, explicación en `control/firmware/README.md`. **No compilado ni probado**; se aplica y flashea desde la laptop y se mide de nuevo con `medir_latencia_ping_pong.py`.
