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
2. **`pasos_por_n`**: la ganancia fuerza→pasos del eje vertical. Depende de la rigidez de contacto (no medida — `../identificacion/PROTOCOLO.md`, no ejecutado) y de los pasos/mm del husillo vertical (no verificados en este repo). Sin esto, `fz_ilc.py` se niega a correr (no hay valor por defecto a propósito).
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
