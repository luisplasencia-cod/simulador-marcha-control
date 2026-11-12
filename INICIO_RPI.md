# Punto de entrada para Claude en el Raspberry Pi

Si acabas de llegar a este repo en el RPi: lee esto completo antes de hacer nada.
Contexto completo y siempre actualizado: `CLAUDE.md` (la entrada con fecha más reciente es la vigente).
Reescrito el 2026-11-11 desde la laptop, **sin RPi**: el plan de abajo no se ha ejecutado.

**Regla de orden (Luis):** todo es sobre Fz (eje vertical). No se toca Fy ni sagital en lazo cerrado
hasta que Fz quede probado en el simulador real.

## 1. Dónde estamos (2026-11-11)

- **Firmware:** el ESP32 tiene el parche v3 (`SET_VEL`) compilado con `espressif32 @ 7.0.1`. Probado:
  regresión, PING 5.98 ms, `SET_VEL` positivo sube Y, watchdog 32 pasos. El firmware **no es el bloqueo**.
- **Bloqueo real: la medición de fuerza.** El ADS1256 se cae (DRDY fijo en alto, registros en 0).
  Datos de Luis del 2026-11-11: se cae **también sin mover nada**; quitar y poner el 5 V **no siempre**
  lo recupera; su 5 V ya viene de una fuente aparte.
- **Causa: no determinada.** Dos hipótesis, ninguna verificada: (a) contacto o alimentación de PDWN;
  (b) tensión negativa del AMTI en AIN0 (se midió −55 mV en reposo; el chip admite hasta −0.1 V).
- **Cableado del ADC: igual que siempre.** Las protecciones están decididas y dibujadas, no cableadas:
  `esquemas/amti_ads1256_rpi/salida/esquema_protecciones_ads1256.png`.
- **Posición esperada de los ejes** (última orden del 2026-11-10, no medida): X −15 cm, Y +5 cm arriba,
  pie −20°. Los contadores del ESP32 se pierden en cada reinicio: **no confiar en `GET_POSITION`**.
- Reporte de la última sesión: `reportes/2026-11-11_protecciones_decididas_y_seleccion_adc_simultaneo.md`.

## 2. Qué traer (Luis)

| Para | Material |
|---|---|
| Medir | Multímetro, una pesa conocida (p. ej. 2.5 kg) |
| ① SPI | 3 resistencias de 100 Ω |
| ② PDWN | Regulador de 3.3 V (p. ej. módulo AMS1117-3.3) con sus capacitores, 1 resistencia de 10 kΩ, 1 capacitor de 100 nF |
| ③ AIN0 | 1 resistencia de 1 kΩ |
| ④ 5 V | 1 resistencia de 2.2 Ω, 1 capacitor de 100 µF, 1 capacitor de 100 nF |
| ⑤ Tierra | Cable y cautín para unir todas las tierras en un punto |

Los capacitores del regulador dependen del modelo: leer su hoja antes de soldar (valor NO verificado).

## 3. Plan en orden

Cada fase tiene un criterio para pasar a la siguiente. Si no se cumple, se para y se anota en el reporte del día.

### Fase 0 — Llegada (sin mover nada)

1. `git pull`.
2. `ls /dev/ttyUSB*` → el ESP32 debe aparecer. Si no, revisar el cable USB.
3. Luis mira y dice dónde están físicamente X, Y y el pie.

### Fase 1 — Atrapar la caída con el cableado ACTUAL (sin mover nada)

No cablear protecciones todavía: primero hay que saber qué falla, o no se sabrá qué lo arregló.

1. Monitor cerrado. Correr `.venv/bin/python pruebas/vigilar_adc.py --minutos 30`.
2. Cuando marque `CAIDO`, **no reiniciar nada**. Luis mide con el multímetro, respecto a GND de la placa,
   y se anota:

   | Punto | Valor sano esperado | Medido con el ADC caído |
   |---|---|---|
   | 5 V de la placa | ≈ 5.0 V | |
   | 3.3 V de la placa (salida de su regulador) | ≈ 3.3 V | |
   | PDWN | ≈ 3.3 V | |
   | VREF | ≈ 2.5 V | |
   | AIN0 (salida del AMTI) | entre 0 y 3.5 V | |

3. Abrir el CSV `pruebas/resultados/vigilar_adc_<hora>.csv` y mirar la columna `ain0_min_mV` en los
   segundos anteriores a la caída: ¿bajó de −100 mV?

**Qué decide esto:**

| Resultado | Lectura | Qué se cablea primero |
|---|---|---|
| PDWN bajo | El chip se apaga por PDWN | ② |
| 5 V o 3.3 V bajos | Falla de alimentación | ④ |
| AIN0 negativa antes de caer | Entrada fuera de rango | ③ |
| Todo normal | Ninguna hipótesis se confirma | Probar otra placa ADS1256 antes de cablear |

Si en 30 min no se cae: repetir con el AMTI cargado y descargado a mano (sin motores) y anotarlo.
Aviso: las columnas `ain0_*` de `vigilar_adc.py` se agregaron el 2026-11-11 en la laptop y **no se han
ejecutado**; solo se comprobó que el archivo no tiene errores de sintaxis.

### Fase 2 — Cablear protecciones (ADC y AMTI apagados)

Orden propuesto, en dos tandas, para poder saber qué ayudó:

1. **Tanda A:** ②, ④ y ⑤ (PDWN, 5 V y tierra). Repetir `vigilar_adc.py --minutos 30`.
2. **Tanda B:** ③ y ①. Antes y después de poner el 1 kΩ de ③, leer la pesa conocida: si la lectura
   baja, el 1 kΩ atenúa la señal y hay que retirarlo (la impedancia de salida del AMTI no está medida).

Antes de energizar: revisar el bloque "ANTES DE ENERGIZAR" del esquema.

**Criterio para pasar:** 30 min en reposo sin ninguna caída.

### Fase 3 — Con el servo vertical (necesita el OK de Luis en ese momento)

1. `pruebas/fuerza_vs_velocidad_y.py` con Y en el aire. El 2026-11-10 Fz se movía entre −10 y +43 N
   sin contacto y el ADC se caía después.
2. **Criterio para pasar:** el ADC no se cae y la fuerza en el aire queda dentro del ruido de reposo
   (σ ≈ 1–2 N). Si no, el lazo con contacto sigue bloqueado: revisar cables lejos del servo.

### Fase 4 — Primer lazo de Fz con contacto (necesita el OK de Luis)

1. Pie en plana (0°). Luis mide el hueco suela–plataforma con el pie ya en ese ángulo.
2. Sin `--ejecutar` primero, para leer el plan que imprime:
   `control/lazo_fz_tiempo_real.py --hueco_remedido --hueco_mm <medido> --angulo_deg 0 --peso_sujeto_n 100 --fmax_n 150`
3. Con `--ejecutar` solo si el plan es correcto y Luis está junto al paro de emergencia.

### Después (no antes)

Medir la constante de tiempo del servo (hoy 20 ms supuestos), la latencia completa, elegir `Kp`
(partida: 15 1/s), e integrar X y sagital con `RUN`.

## 4. Reglas que no se saltan

- **Nunca `HOME` con la prótesis montada.** Si hace falta, avisar a Luis: él quita el pie y lo habilita.
- **Ningún movimiento sin el OK de Luis en ese momento.**
- Ejes al ESP32 siempre como **entero**: 0 = X, 1 = Y, 2 = K. Nunca letras (`"Y"` mueve X).
- Antes de flashear: `esptool read_flash` de respaldo, y medir latencia después.
- Compilar firmware solo con `espressif32 @ 7.0.1`.
- Iniciar el ADC antes de abrir el ESP32. Abrir el puerto reinicia el ESP32 y borra su contador.
- El monitor (`herramientas/monitor_gaitsim.py`) no puede estar abierto junto a otra prueba que use el ADC.
- Toda prueba escribe en el visor en vivo (`herramientas/en_vivo.py`).
- Nunca `pkill -f` / `pgrep -f` con el patrón en la misma línea: matar por PID.
- No suponer nada: dato medido, con fuente, o marcado NO VERIFICADO.
- Reporte por sesión en `reportes/` (Objetivo → Metodología → Resultado → Limitaciones → Fuentes),
  decisiones en `CLAUDE.md` en el mismo turno, `sync` antes de apagar el RPi.
- Git: `git fetch` y `git log origin/master -1` antes de cada commit; `git push` al cerrar algo con sentido.

## 5. Mapa rápido

- Arquitectura: AMTI → ADS1256 (SPI0) → RPi → USB serie 115200 (`SET_VEL`) → ESP32 → driver A6-750RS →
  servo vertical A6M80-750H2B1-M17 (con freno).
- Pines del ADC: `esquemas/amti_ads1256_rpi/CONFIGURACION_ACTUAL.md`.
- Firmware y binarios: `control/firmware/` (`README.md`, `binarios/original_laptop/`, `binarios/v3_7.0.1/`).
- Rigidez medida (Ensayo A): talón 26.4, plana 23.0, punta 2.4 N/mm. Ganancia de la primera prueba: la del talón.
- ADC del producto final (aparte, no bloquea Fz): AD7606 elegido, sin comprar; su esquema de conexiones está pendiente.
