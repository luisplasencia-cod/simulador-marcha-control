# control/ilc/ — ILC ciclo a ciclo para Fz (y luego Fy, sagital)

Decisión cerrada 2026-11-04 (ver `../DECISION_TIPO_CONTROL.md`): el control que
se implementa ahora es **ILC ciclo a ciclo**, no realimentación en tiempo real
dentro del ciclo. No es una elección de desempeño — es consecuencia directa de
que el firmware del ESP32 no se toca (decisión de Luis) y no tiene un comando
de velocidad/posición continuo, solo trayectorias precargadas (`RUN`) de hasta
500 puntos. La realimentación en tiempo real queda fuera de alcance mientras
esa decisión de firmware se mantenga.

## Piezas (en orden, cada una se probó sola sin hardware)

| Archivo | Qué hace | Probado |
|---|---|---|
| `ilc_core.py` | Ley de aprendizaje ILC, genérica (no sabe de Fz, de pasos ni de ESP32) | autoprueba con planta sintética, pasa |
| `fz_ilc.py` | Curva objetivo real de Fz (Gutenberg/Fukuchi) → correge con el núcleo ILC → convierte a pasos del eje vertical | autoprueba con planta sintética, pasa — **la conversión N→pasos no está validada con hardware** |
| `protocolo_subida_esp32.py` | Cliente serial del protocolo `TRAJ_BEGIN/TRAJ_POINT/TRAJ_END/RUN` ya existente en el firmware | **NO probado en hardware** (sin RPi ni ESP32 en esta sesión) |

## Lo que falta para correrlo de verdad (no inventado, pendiente de hardware)

1. ~~Qué eje del firmware (X o Y) es el vertical (Fz) físico~~ — **CONFIRMADO (2026-11-04), verificado en el código fuente, no es solo recuerdo de Luis:** `hardware_config.h` comenta `X_DIR_SETUP_US` como *"Required by the horizontal motor driver datasheet"* y `Y_DIR_SETUP_US` como *"Required by the vertical motor driver datasheet"*. **Y = vertical (Fz), X = horizontal (Fy), K = sagital.** No hay eje "Z" en el firmware.
2. **`pasos_por_n`**: la ganancia fuerza→pasos del eje vertical. `PASOS_POR_MM_Y = 80 pasos/mm` CONFIRMADO (2026-11-05). La **rigidez de contacto** (`k`, N/mm) YA SE MIDIÓ (Ensayo A, 2026-11-05, una prótesis, 3 condiciones de pie): talón 26.4, plana 23.0, punta 2.4 N/mm (`../identificacion/ESTADO_Y_PENDIENTES_para_retomar.md`, no es una rampa pareja — talón/plana casi iguales, caída fuerte solo cerca de la punta).
   **Plan progresivo (decisión cerrada 2026-11-06, no es solo un dato suelto):**
   - **Etapa 1 (primera prueba del lazo, ahora):** `rigidez_n_por_mm` FIJA = caso conservador (punta, 2.4 N/mm) → `pasos_por_n ≈ 33.3`. Prioriza estabilidad en todo el rango de apoyo sobre desempeño óptimo en talón/plana.
   - **Etapa 2 (después de validar la Etapa 1):** ganancia variable en tiempo real usando el CoP del AMTI (de los momentos) para interpolar entre los 3 `k` medidos — ahí se aprovecha la caída real cerca de la punta en vez de cargar siempre el peor caso. Pendiente: más puntos de `k` cerca del antepié (la caída no está caracterizada en detalle) y la función CoP→ganancia.
   - **Multi-prótesis:** `fz_ilc.py` ya acepta `rigidez_n_por_mm=` como parámetro (no hardcodeado). Falta una tabla simple por prótesis (JSON, una fila por prótesis con su `k` conservador medido) para que agregar una prótesis nueva sea solo repetir el Ensayo A, sin tocar código.
3. **Probar `protocolo_subida_esp32.py` contra el ESP32 real** antes de confiar en él — se escribió leyendo el código del firmware, no se ejecutó contra hardware.

## Cómo sigue (una vez que Fz funcione)

Misma arquitectura para Fy: otra instancia de `ILCController` (ya genérico),
otra curva objetivo (Fy real, aún no se definió cuál — pendiente), su propia
ganancia fuerza→pasos del eje horizontal, subida por el mismo
`protocolo_subida_esp32.py` pero al eje X o Y que corresponda. El eje sagital
(ángulo, guiado por la plantilla de presión) es un lazo distinto, no de fuerza
— no reutiliza `fz_ilc.py`, pero sí puede reutilizar `ilc_core.py` si conviene
un ILC también sobre el ángulo. Los tres ejes se ejecutan en el mismo ciclo del
simulador (ver CLAUDE.md), así que subir las tres trayectorias (dx, dy, dk) en
el mismo `TRAJ_POINT` — por eso `fz_ilc.py` ya devuelve `dz_pasos` en el array
correcto para encajar ahí, no en un mensaje aparte.
