# Identificación en línea de la rigidez k para el lazo de Fz (prótesis de k desconocida) — 2026-11-19 (laptop, sin RPi)

**Solo simulación. Nada de esto está probado en el simulador real ni conectado al lazo.**

## Objetivo
Que el lazo de Fz en Y funcione con cualquier prótesis montada cuya rigidez de contacto `k` no se conoce, midiéndola en el momento en vez de leerla de `control/identificacion/tabla_k_por_protesis.json` (que exige un Ensayo A previo por prótesis), y que Kp deje de elegirse a mano por escalón de carga.

## Por qué hace falta (análisis)
El lazo manda `u = Kp · e · pasos_por_n` con `pasos_por_n = 80 / k_usado`, y la planta cumple `dF/dt ≈ k_real · v`. La ganancia que realmente ve la fuerza es **`Kp_ef = Kp · k_real / k_usado`** [1/s]. Con `k_usado` fijo en 26.4:
- una prótesis más rígida (33 N/mm) queda más agresiva de lo diseñado; una más blanda (2.4) responde 11× más lento;
- si la prótesis se endurece con la carga (Ensayo A y escalera de ayer: secante ≈25.5 N/mm a 578 N, ≈33.1 a 1040 N), `Kp_ef` sube con el peso. Eso explica por qué hubo que bajar Kp de 8 a 5 entre 60 y 90 kg — aunque la oscilación de 6–8 Hz de 70 kg NO queda explicada por esto (otro análisis, otro reporte).

Si `k_usado ≈ k_real`, Kp pasa a ser una sola constante de tiempo del lazo de fuerza, igual para toda prótesis y carga. Regla vigente (2026-11-06): equivocarse hacia `k_usado > k_real` (más lento), nunca al revés.

## Metodología
- Módulo nuevo `control/identificacion/estimador_k_en_linea.py` (con autoprueba sintética): `EstimadorPrecarga`, `EstimadorRLS`, `TablaKPorFuerza`, `GananciaSegura`, `verificar_factibilidad`.
- Simulación `control/simulacion/sim_k_desconocida.py`. Planta: retardo 20 ms (Ensayo B: 15–23), servo de 1.er orden τ 8 ms (Ensayo B: 3–14), resorte con histéresis (rama de descarga = 0.81 × rama de carga ≈ 19 % de energía perdida, Ensayo A: 18–20 %; **cruce entre ramas con 2× la rigidez tangente: supuesto, no medido**), ruido 0.75 N + 60 Hz de 2.3 N rms (RPi), lectura = mediana de 7 a 1 kHz, control cada 10 ms, saturación 9000 pasos/s, ILC real del proyecto (`ControlFzILC`), y las protecciones del lazo (tope `min(1.25·pico, 1300 N)`, saltos `max(30 N, 8 % pico)`, descenso máximo).
- Prótesis: lineal 2.4 / 23 / 33 N/mm y una no lineal (tangente 12 → 42 N/mm; secante 26.7 N/mm a 578 N y 30.7 a 1040 N, cercana a la escalera real). Cargas 50 y 90 kg a x10 (apoyo 6.15 s), 6 pisadas.
- Métodos:
  - **M0 (hoy):** k fijo 26.4 + Kp a mano (8 a 50 kg, 5 a 90 kg).
  - **Ma:** precarga automática tras el contacto: bajar a 5 mm/s hasta `F_id = min(0.15·pico, 150 N)` (tope 40 mm), volver a ~10 N; k = tangente de la mitad alta de la rampa; fijo toda la corrida.
  - **Mb:** Ma + mínimos cuadrados recursivos (olvido 0.98) sobre `ΔF = k·Δz(t−20 ms)` durante las pisadas.
  - **Mc:** Ma para la pisada 1 + tabla k(F, carga/descarga) aprendida pisada a pisada, consultada en cada instante.
  - **Md:** Ma para la pisada 1; tras cada pisada, k fijo = percentil 70 de las pendientes de **carga** con F > 10 % del pico, +15 %.
  - Ma–Md con **Kp = 6 1/s** para todo (≤ la ganancia efectiva ya corrida en hardware: 50 kg 7.7, 90 kg 6.3). Todos con margen hacia el lado lento (Ma/Mb +30 %, Mc/Md +15 %).
- Métrica principal: `Kp_ef` (mediana sobre la rama, sin cruces), además del RMS por pisada (% del pico), el error a más de 3 Hz y el p95 de `Kp_ef` incluidos los cruces de rama.

## Resultado (simulado)
Tabla completa: `control/simulacion/sim_k_desconocida_tabla.md`. Figura: `reportes/figuras/2026-11-19_sim_k_desconocida.png`.

| caso | Kp_ef M0 (hoy) | Ma | Mb | Mc | **Md** | RMS última pisada M0 → Md (% pico) |
|---|---|---|---|---|---|---|
| 50 kg, 23 N/mm | 7.0 | 4.7 | 4.8 | 5.0 | **4.9** | 3.1 → 3.7 |
| 50 kg, 33 N/mm | 10.0 | 4.7 | 4.9 | 5.2 | **5.0** | 2.4 → 3.7 |
| 50 kg, no lineal | 9.3 | 7.2 | 5.8 | 5.2 | **4.5** | 2.8 → 4.1 |
| 90 kg, 23 N/mm | 4.4 | 4.6 | 4.7 | 4.9 | **4.6** | 4.0 → 3.9 |
| 90 kg, 33 N/mm | 6.2 | 4.6 | 4.8 | 5.0 | **4.9** | 3.2 → 3.7 |
| 90 kg, no lineal | 6.6 | 7.0 | 5.6 | 5.1 | **4.6** | 3.4 → 4.1 |
| 2.4 N/mm, 50 kg | aborta en la pisada 1 (descenso máx.) | aborta ANTES de mover el lazo: compresión esperada 242 mm > 80 mm | | | | |
| 2.4 N/mm, 90 kg | aborta en la pisada 1 | aborta en la precarga: no llega a 150 N en 40 mm | | | | |

1. **Hoy (M0) la agresividad real varía 4.4 → 10 1/s (×2.3) según prótesis y carga.** Con Md queda en 4.5–5.0 en todos los casos (≤ el diseño 6/1.15 = 5.2): cumple la regla de seguridad para cualquier k probado.
2. **Ma (solo precarga) no basta con una prótesis que se endurece:** mide k a carga baja y a carga alta queda un 17–20 % más agresiva que lo diseñado (7.0–7.2 vs 6). Md lo corrige desde la pisada 2.
3. **Mb (RLS) y Mc (tabla) se descartan:** cambiar k dentro de la pisada añade error rápido — a 90 kg el error >3 Hz pasa de 2.4–2.8 N (Ma/Md) a 3.2–4.8 N (Mb/Mc). Con la oscilación de 6–8 Hz sin explicar, no conviene un lazo con ganancia variable dentro del ciclo.
4. **Costo:** Md es algo más lento que M0 con prótesis rígidas (RMS final 3.7–4.1 % vs 2.4–4.0 %); el ILC compensa casi todo. La precarga suma 1.1–3.0 s por corrida.
5. **La comprobación previa detiene la prótesis demasiado blanda antes de cerrar el lazo**, en vez de dejar que aborte a mitad de pisada con carga.
6. **Sensibilidad (cruce de ramas 1.2× / 2× / 3×, no medido):** Md quedó en 4.3–5.0 1/s en los tres casos. Con percentil 80 en vez de 70, un caso (90 kg, 23 N/mm) saltó a k 50 N/mm (lazo el doble de lento): **el percentil es frágil y está elegido con un modelo de histéresis no medido**.

## Cómo se conectaría a `control/lazo_fz_tiempo_real.py` (no aplicado)
1. L321–323: con un flag nuevo `--k_auto`, no llamar a `cargar_k_asumido`; la tabla queda como respaldo o comparación.
2. Entre L406 y L408 (tras detectar el contacto): fase de **precarga** con `EstimadorPrecarga` (V_LENTA hasta `F_id`, tope 40 mm, mismas protecciones de lectura anómala), volver a ~10 N, `verificar_factibilidad(...)`: aborta si la compresión esperada supera el recorrido permitido; la velocidad es **solo aviso** (con una prótesis que se endurece da falso positivo: 90 kg no lineal avisó 100 mm/s y no saturó nunca). `extra_mm` sale de `1.5 × compresión esperada`, acotado por un recorrido máximo que **debe fijar Luis** (la simulación usó 80 mm, elegido sin medir).
3. L432: `pasos_por_n` → `gan.pasos_por_n()` (`GananciaSegura`), fijo durante cada pisada.
4. Guardar `descenso_mm` por muestra; tras L454 (`registrar_medicion`): `tab.aprender_pisada(z, F)` y `gan.k_usado = 1.15 × tab.k_rigido_carga(0.1·pico, 70)`.
5. `--kp` pasa a significar Kp del lazo de fuerza, un solo valor (6) para toda carga; anotar `k_precarga` y el k de cada pisada en el `.meta.txt`.
6. `ControlFzILC(rigidez_n_por_mm=...)` recibe k de la precarga (solo lo usa `siguiente_trayectoria`, no el lazo en tiempo real; el ILC trabaja en N y no depende de k).

## Limitaciones
- Todo es simulación; la planta tiene supuestos sin medir: cruce de ramas de la histéresis, servo de 1.er orden, sin resonancia (la de 6–8 Hz no se reproduce), sin holgura y sin pérdida de pasos. Se usa el descenso ORDENADO (no hay sensor de posición): si el servo no sigue, k sale mal.
- El percentil 70 y los márgenes (+30 %, +15 %) son elecciones de diseño; el percentil es sensible (ver punto 6).
- Ángulo fijo (pie plano). **Con X y K moviéndose (3 ejes) k cambia a lo largo del apoyo** (punta 2.4 N/mm, 11× más blanda): Md toma el k más rígido y en el despegue el lazo queda lento. Para eso hará falta k por fase del apoyo (aprendible pisada a pisada, porque se repite) o el CoP (Etapa 2, decisión del 2026-11-06). No probado.
- Precarga hasta el 15 % del pico (87 N a 50 kg, 150 N a 90 kg): es carga real sobre la prótesis antes de la pisada. Que sea aceptable lo decide Luis.
- Una semilla de ruido, 6 pisadas y una sola curva (Gutenberg x10).

## Qué falta validar en la RPi
1. La precarga real con el pie pasivo montado: comparar su k con el Ensayo A (plana 23.0 N/mm) y con la rigidez aparente de la escalera.
2. Una corrida a 50 kg con `--k_auto` contra la misma con k fijo: `Kp_ef` estimado, RMS y error >3 Hz.
3. Medir la histéresis real en los cruces de rama con datos del CSV del lazo, para fijar el percentil.
4. Una segunda prótesis (o el mismo pie a otro ángulo) sin tabla previa.

## Fuentes
- `control/lazo_fz_tiempo_real.py` (L321–323, L384–455), `control/ilc/fz_ilc.py`, `control/ilc/ilc_core.py`.
- `reportes/2026-11-18_ensayo_B_respuesta_dinamica.md` (retardo, τ), `reportes/2026-11-05_ensayo_A_corridas_y_fallos_usb.md` (k, histéresis), `reportes/2026-11-18_escalera_50_a_90kg_x10_y_abortos.md` (Kp y rigidez aparente por carga), `reportes/2026-11-18_etapa2_R2_rpi_uart.md` (ruido), `reportes/2026-11-06_analisis_ganancia_fz_conservadora.md` (regla del k rígido).
- Código nuevo: `control/identificacion/estimador_k_en_linea.py`, `control/simulacion/sim_k_desconocida.py` (reproduce todo: `python control/simulacion/sim_k_desconocida.py`; sensibilidad con las variables de entorno `FACTOR_TRANS` y `PERCENTIL`).
