# ¿Sirven las protecciones propuestas para el ADS1256? Foros y sustituto de la ferrita — 2026-11-10

## Objetivo
Evaluar si cada componente del esquema `esquemas/amti_ads1256_rpi/salida/esquema_protecciones_ads1256.png` ataca la falla observada (ADC "caído": DRDY fijo en alto, registros en 0, solo se recupera quitando y poniendo el 5 V), y proponer un reemplazo de la ferrita, que Luis no tiene.

## Metodología
3 búsquedas web (solo resúmenes de resultados, no se abrieron los hilos ni la hoja SBAS288K) + análisis propio. Lo marcado "propio" es cálculo mío, no de una fuente.

## Resultado
Ningún foro encontrado describe nuestro caso exacto con una solución confirmada. Lo que dicen:
- DRDY fijo en alto = el chip no convierte: sin alimentación, RESET o PDWN en bajo, o sin reloj (cristal). Un ingeniero de TI pide sondear XTAL/CLKIN. Una tierra flotante entre MCU y ADC también detiene los datos.
- Leer 0x00 en registros se reportó con el chip sin reloj/reset correctos.
- Los hilos no tratan condensadores de desacople como causa ni como solución.

Veredicto por componente (de mayor a menor utilidad probable):
1. **PDWN soldado + pull-up a otro 3V3 (+100 nF): útil, es lo que mejor encaja con el síntoma** (PDWN bajo = DRDY alto y registros inútiles). Barato y también sirve de diagnóstico. Sigue siendo hipótesis: no se midió PDWN con el ADC caído.
2. **Desacople del 5 V (100 µF + 100 nF) y GND en un punto: plausible**, porque las caídas ocurren tras mover el servo (caída de 5 V / ruido de tierra). Sin evidencia de foro; solo lógica. Medir el 5 V en el módulo con el servo en marcha antes de decidir.
3. **RC 1 kΩ + 100 nF en AIN0: no ataca la caída.** La hoja dice que a menudo basta un RC simple en la entrada y, con buffer, la impedancia de entrada es ≈80 MΩ, así que 1 kΩ no carga. Un foro advierte que sobre 3–5 kΩ el ruido de la resistencia ya pesa. Ayuda contra ruido captado por el cable analógico, no contra el cuelgue ni contra los errores de bit del SPI (esos son digitales). Prioridad baja. Propio: fc = 1.6 kHz, retardo ≈0.1 ms, despreciable.
4. **47 Ω en SCLK/DIN/CS: beneficio dudoso.** Con cables cortos y 500 kHz los rebotes son despreciables (propio). Limita corriente si hubiera sobretensión. Prioridad baja; no tengo fuente que lo respalde.

## Sustituto de la ferrita (propuesto, NO probado)
Una fuente sugiere usar la ferrita junto a una resistencia pequeña en serie o en filtro T/Pi; otra, que un RC de primer orden no tiene resonancia (una ferrita/inductor + 100 µF sí puede resonar).
- **Opción A (recomendada, sin comprar nada): resistencia en serie de 1–2.2 Ω + C1 100 µF + C2 100 nF pegados al módulo.** Propio: 2.2 Ω con 100 µF → fc ≈ 720 Hz; 1 Ω → ≈1.6 kHz. Caída = I·R; **la corriente de la placa NO está medida**: medirla antes (con 50 mA serían 0.11 V con 2.2 Ω). Comprobar que el 5 V en el módulo siga ≥4.75 V (límite AVDD de la hoja, según el propio esquema).
- **Opción B: ferrita "casera":** los cilindros de ferrita de cables USB/cargadores viejos (o un toroide): pasar el par 5 V + GND por dentro varias vueltas. Sirve para ruido de alta frecuencia; no ayuda con caídas lentas de tensión.
- **Opción C (la que ya funcionó el 2026-11-05): fuente externa de 5 V** para el módulo, con GND común. Elimina la hipótesis de corriente/caída del 5 V del RPi.

## Lista de compras (criterio propio; ninguna fuente lo confirma)
1. Condensadores 100 µF y 100 nF; resistencias 1 Ω, 2.2 Ω, 10 kΩ, 47 Ω (céntimos).
2. **Otra placa ADS1256 igual, de repuesto:** separa "placa dañada" de "causa externa".
3. Fuente de 5 V externa (aislada si se puede) para el ADC: funcionó el 2026-11-05.
4. Cable de par trenzado apantallado para AIN0 (malla a tierra en un solo extremo).
5. Solo si lo anterior falla: aislador SPI de 4 canales (ningún foro encontrado trató servos con aisladores; es lógica mía) y aislador/hub USB alimentado para el ESP32 (68 cortes USB, problema aparte).
- **No comprar** otro ADC (ADS1261/1263): un hilo de TI dice que el ADS1261 tiene la mitad de ruido, pero la falla es cuelgue, no ruido.
- Nota de foro: en la placa Waveshare un usuario halló 1.2 MHz como reloj SPI más rápido confiable (bytes perdidos a veces); coherente con nuestros errores de bit.
- Luis acepta la resistencia pequeña en lugar de ferrita (opción A).

## Orden sugerido (todo con ejes quietos)
1. Con el ADC caído, medir 5 V, 3.3 V, VREF (2.5 V) y PDWN: decide cuál hipótesis vale.
2. Si PDWN o el 3.3 V están bajos: soldar PDWN, pull-up, C de 100 nF.
3. Si el 5 V cae con el servo: opción A o C.
4. AIN0 y 47 Ω solo si sigue habiendo ruido/errores tras lo anterior.

## Limitaciones
No se leyeron los hilos completos ni la hoja SBAS288K; ninguna fuente confirma que estas protecciones eviten la caída. Cristal de la placa sin verificar. Corriente de la placa sin medir.

## Fuentes
- https://e2e.ti.com/support/data-converters-group/data-converters/f/data-converters-forum/881888/ads1256-ads1256-drdy-not-going-low
- https://e2e.ti.com/support/data-converters-group/data-converters/f/data-converters-forum/855591/ads1256-ads1256
- https://e2e.ti.com/support/data-converters-group/data-converters/f/data-converters-forum/72423/ads1256-analog-input-external-filter-requirements
- https://e2e.ti.com/support/data-converters-group/data-converters/f/data-converters-forum/468722/ads1256-input-protection
- https://e2e.ti.com/support/data-converters-group/data-converters/f/data-converters-forum/295854/ads1256-input-impedance-and-biasing
- https://www.allaboutcircuits.com/technical-articles/choosing-and-using-ferrite-beads/
- https://www.eevblog.com/forum/eda/filtering-power-supplies-using-ferrite-bead/
