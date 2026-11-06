# Punto de entrada para Claude en el Raspberry Pi

Si acabas de llegar a este repo en el RPi (primera vez o retomando): lee esto completo antes de
hacer nada. **Todo lo de abajo es sobre Fz (eje vertical) — no se toca Fy ni sagital hasta que Fz
quede probado funcionando de verdad en el simulador real** (regla de Luis).

## Qué es este repo
Tesis de control del simulador de marcha (Luis Plasencia, PUCP). Contexto completo y SIEMPRE
actualizado del proyecto: `CLAUDE.md` (léelo primero, siempre — tiene fecha en cada entrada, la más
reciente es la vigente). Detalle de auditorías/búsquedas pasadas: `HISTORIAL.md`. Reportes diarios
completos (Objetivo→Metodología→Resultado→Limitaciones→Fuentes): `reportes/`, los más recientes son
`2026-11-04_reporte_dia.md` y `2026-11-05_reporte_dia.md` — léelos antes de los de fechas anteriores.

## Estado al cierre de la sesión de laptop del 2026-11-05 — léelo primero
**Decisión de control para Fz: híbrido RT (tiempo real) + ILC**, no ILC solo (Luis autorizó
modificar el firmware el 2026-11-04, revierte la decisión anterior de no tocarlo). Todo lo de abajo
está diseñado y documentado pero **nada probado en hardware real** — sin RPi en las sesiones del
2026-11-04/05. Ver `control/DECISION_TIPO_CONTROL.md` para la justificación completa.

## Al retomar tras el reinicio del RPi (2026-11-05 ~11:15) — si Luis dice "continuar"
Lee en `CLAUDE.md` las dos entradas del 2026-11-05 ~11:15 (ADC caído + estado). Orden: verificar el ADC (`pruebas/leer_ads1256_fz.py --diagnostico`, monitor cerrado) → probar la subida de trayectoria al ESP32 → investigar el reinicio del ESP32 → ver el filtro en el monitor → capturas de ruido. Pasos/mm (checklist 1) ya está hecho.

## Qué hacer, en orden (checklist para esta sesión del RPi)

1. **Verificar `pasos_por_mm` del eje vertical (barato, primero, sin prótesis).**
   `control/identificacion/PROTOCOLO.md`, "Ensayo 0": mandar un número conocido de pasos al eje
   vertical (`MANUAL`/`GOTO`, firmware actual sin cambios) y medir el desplazamiento real con una
   regla. Debe dar 80 pasos/mm (`control/ilc/fz_ilc.py`, `PASOS_POR_MM_Y`). Si no coincide, **parar
   y avisar** — todo lo de abajo depende de este número.

2. **Aplicar y probar el parche de firmware `SET_VEL` (tiempo real).**
   `control/firmware/control_velocidad_continua.patch` (ya verificado con `git apply --check`, NO
   aplicado). El protocolo de 5 pasos está en `control/firmware/README.md` — **no saltarse pasos**:
   compilar solo → flashear con motores desconectados (osciloscopio/LED en STEP) → probar el
   watchdog (80 ms) → motores conectados, velocidad baja, supervisado → recién ahí integrar con
   `control/ilc/fz_ilc.py`. El firmware se flashea **desde la laptop** (PlatformIO, cable USB ahí) —
   si hace falta un cambio, documentarlo aquí para que la sesión de la laptop lo aplique, no asumir
   que se puede flashear desde el RPi.

3. **Medir la rigidez de contacto `k` (N/mm) con al menos una prótesis.**
   `control/identificacion/PROTOCOLO.md`, "Ensayo A" (necesita el Ensayo 0 ya confirmado). Esto es
   lo único que falta para que `fz_ilc.py` pueda correr con un `rigidez_n_por_mm=` real en vez de
   negarse a generar una trayectoria.

4. **Probar `control/ilc/protocolo_subida_esp32.py` contra el ESP32 real** (nunca probado, se
   escribió leyendo el código del firmware).

5. **Escribir el script del lazo real en el RPi** (no existe todavía — es el siguiente bloque que
   falta). Debe: leer el ADS1256 (ya validado contra el AMTI real, RMSE 1.89 N, r=0.9999 — no repetir
   esa validación), calcular `Kp·e(t)` + la corrección ILC de `fz_ilc.py`, mandar `SET_VEL` por
   `protocolo_subida_esp32.py`, y **loguear cada muestra con el formato de
   `control/telemetria/formato_log.md`** para que el visor funcione sin cambios.

6. **Ver el lazo correr con `control/telemetria/visor_en_vivo.py`** (probado solo con datos
   sintéticos hasta ahora — `python visor_en_vivo.py --ultimo` con pantalla, o `--guardar` sin
   pantalla). Si aparece el salto pequeño y repetible en cada frontera de ciclo que se vio con datos
   sintéticos, no es necesariamente un bug del RPi — ver la nota en `control/telemetria/README.md`.

7. **Validar el híbrido RT+ILC — DOS comparaciones distintas, no una sola (aclarado 2026-11-06 con Luis):**
   (a) **RMSE/correlación contra la curva de referencia PUBLICADA** (Gutenberg 2021 o Fukuchi 2018,
   la misma que ya usa `curva_objetivo_fz()` en `control/ilc/fz_ilc.py`) — esta es la comparación
   **publicable**, porque se mide contra datos de marcha sana reales, no contra uno mismo.
   (b) **RMSE/correlación contra el lazo abierto actual** (como en el artículo de conferencia) — sirve
   como referencia interna para mostrar cuánto mejoró el control nuevo respecto al anterior, pero
   **NO es publicable por sí sola**: comparar contra el propio lazo abierto no demuestra nada frente a
   una fuente externa, solo que se mejoró respecto a lo que había antes. Reportar ambas, nunca solo (b).
   El cierre real de la Etapa 3 para Fz exige (a); (b) es complementaria.

**Solo después de que 1-7 funcionen de verdad (no solo en simulación) se pasa a Fy y sagital** —
misma arquitectura, otra instancia de `ilc_core.py`, su propia `k` y `pasos_por_mm`.

## Arquitectura física (para no perderse)
AMTI → ADS1256 (SPI0 del RPi) → RPi (corre todo el cálculo) → USB serie 115200 baud (`SET_VEL`,
nuevo) → ESP32 (`Codigo ESP32 MOV/platformIO_control_trayectoria_v1/`) → driver A6-750RS → servomotor
vertical **A6M80-750H2B1-M17, con freno integrado** (no A1 — ese es el horizontal, sin freno).
Diagrama completo con pines reales: `control/diagramas/implementacion/`. Mapeo de ejes del firmware
**confirmado**: `Y` = vertical = Fz, `X` = horizontal = Fy, `K` = sagital — no hay eje "Z".

## Estado del hardware de medición (ya resuelto, no repetir)
- **ADS1256 ya validado contra el AMTI real** (2026-11-03): RMSE 1.89 N, correlación r=0.9999 contra
  grabación directa del AMTI (software NetForce). Ver `pruebas/comparar_amti_vs_ads1256.py`.
- 1000 muestras/s confirmado; Fz en reposo ≈21.5 N de offset (tarar); ruido σ≈0.85 N.
- Pines AMTI→ADS1256→RPi: `esquemas/amti_ads1256_rpi/CONFIGURACION_ACTUAL.md`.
- Latencia parcial medida: RPi↔ESP32 RTT 5.97 ms, ADS1256+SPI 1.6-2.4 ms. Falta: amplificador AMTI
  (SUPUESTO ≈2-3 ms, ver `CLAUDE.md`) y ejecución ESP32. Sigue muy por debajo del techo de ~130 ms
  donde el híbrido se desestabiliza (simulación) — no es lo que bloquea avanzar.

## Reglas del proyecto (no te las saltes)
- Verificar datos de hardware contra fuente real (datasheet, etiqueta física, medición, código
  fuente) — nunca de memoria. Si algo no se puede verificar, decirlo explícito, no inventar.
- No redactar síntesis/texto de tesis salvo pedido explícito — Luis decide el enfoque, tú organizas/
  ejecutas lo técnico.
- Reportes: Objetivo → Metodología → Resultado → Limitaciones → Fuentes, uno por sesión en `reportes/`.
- Toda decisión cerrada se escribe en `CLAUDE.md` en el mismo turno en que se cierra.
- Git: `git fetch`/`git log origin/master` antes de cada commit; commitear y `git push` cuando
  termines algo con sentido (no cada línea), para que la laptop de Luis vea el avance.
- Ningún ensayo que mueva motores o cargue el simulador sin el OK explícito de Luis y el simulador
  despejado — ver "Seguridad" en `control/identificacion/PROTOCOLO.md` y el protocolo de prueba en
  `control/firmware/README.md`.
- Nunca `pkill -f`/`pgrep -f` con el patrón en la propia línea de comando: matar por PID.

## Firmware del ESP32 — importante
El firmware se edita/flashea **desde la laptop** (PlatformIO, cable USB ahí), no desde el RPi. Si
necesitas un cambio, documéntalo en el commit/push (o en `Codigo ESP32 MOV/CAMBIOS_PENDIENTES_DESDE_RPI.md`
si es puntual) y Luis lo coordina con esa sesión — no asumas que vas a flashear el ESP32 desde aquí.
