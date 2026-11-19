# Propuesta de filtro de muesca (notch) para la oscilación de 6–8 Hz en Fz — 2026-11-19 (laptop, sin RPi)

**Documento de diseño: nada de esto está conectado al lazo ni probado en hardware.** `control/lazo_fz_tiempo_real.py` no se tocó.

## Objetivo
Evaluar si un filtro de muesca sobre Fz (o suavizar el comando de velocidad) puede atenuar la oscilación de 6–8 Hz vista en la escalera 50–90 kg x10 (`reportes/2026-11-18_escalera_50_a_90kg_x10_y_abortos.md`), y cuánto retardo le cuesta al lazo, cuyo margen depende de un retardo ya medido de 15–23 ms (Ensayo B).

## Metodología
- Tasa del filtro = tasa del lazo: **fs = 100 Hz** (una muestra cada 10 ms = la mediana de bloque de 7 lecturas que entrega `LectorFzUART.leer_n()`). El 7 Hz está muy por debajo de Nyquist (50 Hz) y la mediana de 7 lo deja pasar casi intacto.
- Opciones comparadas (biquads digitales, misma definición que `scipy.signal.iirnotch`, ancho a −3 dB = f0/Q):
  1. Notch 7 Hz, Q = 5 (ancho 1.4 Hz)
  2. Notch 7 Hz, Q = 2 (ancho 3.5 Hz)
  3. Notch 6–8 Hz (6.93 Hz, Q = 3.46)
  4. Dos notches, 6.4 + 8.3 Hz, Q = 4 (los extremos medidos)
  5. Sin filtrar Fz: limitar la aceleración del comando `SET_VEL` (limitador de pendiente).
- Para cada una: pérdida de fase y retardo equivalente (= −fase / 2πf) a 1, 2 y 3 Hz (banda útil del GRF a x10) y en la frecuencia de cruce del término P; atenuación a 6.4 / 7.0 / 7.3 / 8.3 Hz; error que agrega sobre la curva de Gutenberg a 90 kg x10.
- Frecuencia de cruce del P (modelo integrador + retardo): dF/dt = Kp·(k_real/k_asumido)·e → ωc = Kp·k_real/k_asumido, con k aparente medido por escalón y k_asumido = 26.4 N/mm.
- Limitador: aceleración que exige la curva (F''/k con spline cúbico) vs. la de la oscilación; ganancia y atraso de la fundamental simulados.
- Código: `control/filtro_fz/notch_fz.py` (filtro + limitador + autoprueba), `control/filtro_fz/analisis_notch_fz.py` (este análisis); salida completa en `control/filtro_fz/salida_analisis_notch_fz.txt`.

## Resultado
**Cruce del P: 0.84–1.37 Hz** (Kp 5 a 70–90 kg ≈ 0.84–1.00 Hz; Kp 8 a 60 kg 1.37 Hz). Con el modelo integrador + 20–28 ms el margen de fase sin filtro sale 76–84°: **ese modelo NO predice la oscilación de 7 Hz** (la causa la investiga otra tarea).

| Opción | Atraso a 1 Hz | Retardo eq. 1 / 2 / 3 Hz | 6.4 Hz | 7.0 Hz | 7.3 Hz | 8.3 Hz | Error GRF 90 kg |
|---|---|---|---|---|---|---|---|
| Notch 7 Hz, Q=5 | 1.7° | 4.7 / 5.0 / 5.6 ms | −3.5 dB | cero | −8.2 dB | −1.3 dB | 10.5 N |
| Notch 7 Hz, Q=2 | 4.3° | 11.8 / 12.5 / 13.8 ms | −9.5 | cero | −15.6 | −4.9 | 23.9 N |
| **Notch 6–8 Hz (6.93, Q=3.46)** | **2.5°** | **6.9 / 7.3 / 8.2 ms** | **−6.4** | **−23** | **−9.4** | **−2.1** | **14.9 N** |
| 2 notches 6.4 + 8.3, Q=4 | 4.1° | 11.4 / 12.2 / 13.6 ms | cero | −6.6 | −5.7 | cero | 23.3 N |

(Error GRF = máx |filtrada − curva| con pico 1040 N, si se filtrara TODO; ver abajo por qué no debe ser así.) El retardo equivalente en el cruce es prácticamente el mismo que a 1 Hz y **se suma** a los 20–28 ms del lazo.

**Hallazgo de coherencia:** la velocidad que el P ordena al "ver" la oscilación de Fz (v = Kp·e/k_asumido) da 2.1 mm/s rms (60 kg) a 5.9 mm/s rms (90 kg); lo medido fue 2–6 mm/s rms. **La oscilación de la velocidad de Y es el término P reaccionando a la de Fz.** Con el modelo integrador la ganancia de lazo a 7 Hz es |L| ≈ 0.14–0.17 (|S| ≈ 1.14–1.19): la realimentación casi no amplifica a 7 Hz. Por eso un notch solo ayuda si la ganancia REAL a 7 Hz es mayor que la del modelo (p. ej. una resonancia de la estructura/actuador): si la oscilación la sostiene el lazo, el notch corta el eco y la apaga; si la excita otra cosa (saltos del comando, el contacto), el notch **no cambia la fuerza real** y solo la esconde del controlador.

**Limitador de aceleración (no filtrar Fz):** descartado como filtro. A x10 la curva misma exige 260–335 mm/s² (p99) y hasta 414–535 mm/s² en la carga inicial y el despegue; la oscilación medida pide 124–373 mm/s² pico. **No hay un límite que recorte la oscilación sin deformar la curva** (con 150 mm/s² la oscilación baja a 0.51× pero una señal de 1 Hz de 56 mm/s también baja a 0.54× con 47° de atraso — eso sí desestabiliza). Además el limitador en la RPi solo acota el tamaño de cada escalón de 10 ms: el comando sigue siendo una escalera y el firmware salta a cada v sin rampa. Suavizar de verdad el perfil requiere una **rampa en el firmware** (interpolar dentro de los 10 ms), no un filtro en la RPi.

**Propuesta (si las mediciones de abajo confirman que el lazo sostiene la oscilación):** notch 6–8 Hz (6.93 Hz, Q ≈ 3.5), **solo en la Fz que entra al término P**; ~7 ms de retardo equivalente en el cruce (2.5° a 1 Hz), −6 a −23 dB entre 6.4 y 7.3 Hz. Si la frecuencia resulta estable y angosta, bajar a Q = 5 (4.7 ms). Q = 2 o dos notches cuestan ~12 ms: demasiado frente a 20–28 ms de lazo.
- El **ILC, el tope de fuerza, el detector de saltos y el registro** siguen con la Fz **sin filtrar**: así el filtro no esconde lo que protegen, y el ILC corrige el atraso del notch (lleva la Fz real, no la filtrada, a la referencia). Si además se quisiera quitar el 7 Hz del error del ILC, filtrarlo entre ciclos con fase cero (`filtfilt`) no cuesta retardo — pero el filtro Q (Hanning, ≈1 Hz) del ILC ya lo atenúa.
- `reset(F_actual)` al empezar la fase cerrada (sin transitorio de arranque).

## Limitaciones
- **La frecuencia exacta no está confirmada:** 6.4–8.3 Hz según la carga (y 2.8 Hz a 70 kg, dentro de la banda útil del GRF: ahí ningún notch sirve). El notch 6–8 Hz atenúa poco a 8.3 Hz (−2.1 dB): el caso de 60 kg quedaría casi sin tocar.
- **Si es resonancia mecánica excitada desde fuera del lazo, filtrar la medición la oculta sin quitarla**: la fuerza sobre la prótesis seguiría oscilando, lo que importa para comparar prótesis. Toda evaluación debe mirar la Fz sin filtrar.
- Modelo de lazo simplificado (integrador + retardo, k lineal, sin la dinámica del servo ni de la estructura); números de oscilación de una corrida por escalón; frecuencias de la "bajada del primer pico, última pisada".
- La pérdida de fase calculada asume tasa fija de 100 Hz (medido 10.0 ms; jitter no modelado).

## Qué medir en la RPi para decidir
1. **Espectro de la Fz cruda** de las telemetrías del 2026-11-18 (`control/telemetria/registros/2026-11-18_{152829,153832,154240,155042,155241}_fz.csv`, solo existen en el disco de la RPi): frecuencia del pico por carga y si sube con k (una resonancia estructural va como √(k/m)).
2. **Kp 3 vs Kp 5 a la misma carga** (prueba ya propuesta): si la amplitud a ~7 Hz no cambia → excitada desde fuera (notch inútil, ir a rampa de firmware/perfil más suave); si baja con Kp → la sostiene el lazo (notch útil).
3. **Prueba en lazo abierto con contacto**: carga constante, un escalón de `SET_VEL` sin realimentación; si "suena" a ~7 Hz es mecánica.
4. Si se conecta el notch: comparar el espectro de la Fz **sin filtrar** antes/después, no solo la filtrada.

## Fuentes
- `reportes/2026-11-18_escalera_50_a_90kg_x10_y_abortos.md` (frecuencias, amplitudes, Kp, k aparente por escalón).
- `reportes/2026-11-18_ensayo_B_respuesta_dinamica.md` (retardo 15–23 ms, tau 3–14 ms).
- `control/lazo_fz_tiempo_real.py` (DT_CONTROL_S = 10 ms, N_BLOQUE = 7, `LectorFzUART`), `control/identificacion/tabla_k_por_protesis.json` (k_asumido 26.4 N/mm).
- `control/referencia_grf/referencia_fz_gutenberg.csv` (curva objetivo).
- Diseño del biquad: definición de `scipy.signal.iirnotch` (verificado numéricamente en la autoprueba).
- Figura: `reportes/figuras/2026-11-19_notch_fz_bode.png`.
