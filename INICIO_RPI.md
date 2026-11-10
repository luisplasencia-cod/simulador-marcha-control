# Punto de entrada para Claude en el Raspberry Pi

Si acabas de llegar a este repo en el RPi (primera vez o retomando): lee esto completo antes de
hacer nada. **Todo lo de abajo es sobre Fz (eje vertical) — no se toca Fy ni sagital en lazo cerrado
hasta que Fz quede probado funcionando de verdad en el simulador real** (regla de Luis).

## Qué es este repo
Tesis de control del simulador de marcha (Luis Plasencia, PUCP). Contexto completo y SIEMPRE
actualizado del proyecto: `CLAUDE.md` (léelo primero, siempre — tiene fecha en cada entrada, la más
reciente es la vigente). Detalle de auditorías/búsquedas pasadas: `HISTORIAL.md`.

## ⚡ ESTADO ACTUAL (2026-11-10) — hecho SIN RPi desde el último cierre en banco, léelo primero
Reporte consolidado de todo lo avanzado sin hardware: **`reportes/2026-11-08_avance_sin_rpi.md`**
(con figura y tabla). Resumen de lo que cambió desde que el RPi estuvo aquí por última vez:

1. **`control/firmware/control_velocidad_continua.patch` corregido** (2026-11-08): `RUN` (usado por
   X/sagital, trayectoria del montaje 37) ya NO se bloquea por el eje Y en modo `SET_VEL` — antes
   cualquier eje en modo continuo bloqueaba `RUN` para todos, lo que impedía la arquitectura
   objetivo (Y cerrado + X/sagital en `RUN` simultáneo). Verificado con `git apply --check` (aplica
   limpio). **Sigue sin compilar ni flashear.**
2. **`SET_VEL` confirmado que SÍ responde `OK`/`BUSY`** (leyendo `communication.h`/`main.cpp`, no
   asumido): mismo mecanismo bloqueante que `PING`/`PONG`. `control/lazo_fz_tiempo_real.py` ya lee
   y descarta esa respuesta en cada `set_vel()` — **falta confirmar en banco** que no se degrada con
   el servo en movimiento.
3. **`Kp` de partida recomendado: 15 1/s** (antes solo 10 sin justificar), de un barrido en
   `control/simulacion/rt_vs_ilc_latencia.py` contra el `k` real del Ensayo A. Detalle y figura:
   reporte del punto 1, §3. No usar `Kp≥40` sin medir la latencia completa.
4. **Decisión nueva (2026-11-10): el firmware SÍ se puede flashear desde la RPi**, no solo desde la
   laptop — usa el mismo cable USB-serial que ya usa `SET_VEL`/`PING`. **Falta verificar si
   PlatformIO/esptool están instalados aquí**; si no, instalarlos antes de flashear.

## Qué hacer, en orden (checklist para esta sesión del RPi)
Es el mismo checklist de `reportes/2026-11-08_avance_sin_rpi.md` §4 — se repite aquí para no tener
que abrir dos archivos:

1. **USB/tierra del ESP32** — medir la diferencia de tierra Pi↔ESP32 con el servo vertical en
   movimiento (hipótesis principal de las desconexiones USB de noviembre, ver `CLAUDE.md`
   2026-11-06). Si falla USB otra vez, esto es lo primero que se mira.
2. **Compilar y flashear `control_velocidad_continua.patch`** (con el fix de `RUN`/eje Y ya
   aplicado al patch, punto 1 arriba). Protocolo de 5 pasos en `control/firmware/README.md` — no
   saltarse pasos: compilar solo → motores desconectados → probar watchdog → motores conectados a
   velocidad baja, supervisado → integrar. Puede hacerse desde la RPi (punto 4 arriba) o desde la
   laptop como antes — reportar cuál se usó.
3. **Confirmar en banco que `SET_VEL` responde `OK`/`BUSY`** como se dedujo del código (punto 2
   arriba).
4. **Medir el RTT real de `SET_VEL` con el servo vertical en movimiento** (no solo `PING`/`PONG` en
   reposo, que fue 5.97 ms quieto).
5. **Probar el watchdog (80 ms)** — que un eje en `SET_VEL` se detenga solo si el RPi deja de
   mandar comandos.
6. **Medir la constante del servo `tau_a`** (Ensayo B, no hecho todavía — hoy se usa 20 ms SIN
   MEDIR en la simulación).
7. **Medir la latencia completa del lazo** (AMTI + ADC + cómputo RPi + `SET_VEL` + ejecución
   ESP32) — hoy solo hay latencia PARCIAL medida (≈10 ms: RPi↔ESP32 + ADS1256/SPI; falta AMTI real
   y cómputo+ejecución).
8. **Elegir el `Kp` definitivo** contra la latencia completa y `tau_a` ya medidos (re-correr
   `control/simulacion/rt_vs_ilc_latencia.py` con esos datos reales, no los supuestos de hoy).
9. **Correr `control/lazo_fz_tiempo_real.py` por primera vez** — quitar el `SystemExit` del final
   del script recién cuando 1-8 estén hechos (está puesto a propósito para no correrlo antes de
   tiempo).
10. **Integrar con X/sagital**: `RUN` simultáneo con Y en `SET_VEL` (el fix del punto 1 es lo que
    lo permite). Esto es lo último, después de que Fz funcione de verdad solo.

**Solo después de que 1-10 funcionen de verdad (no solo en simulación) se pasa a Fy en lazo
cerrado** — misma arquitectura, otra instancia de `ilc_core.py`, su propia `k` y `pasos_por_mm`.

Si algo de esto queda sin poder confirmarse en esta sesión, anotarlo explícito en un reporte nuevo
(`reportes/<fecha>_reporte_dia.md`) y dejarlo pendiente aquí mismo — no asumir que "ya se vio".

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
**(Actualizado 2026-11-10)** El firmware SÍ se puede flashear desde la RPi (mismo cable USB-serial
que usa `SET_VEL`/`PING`) — antes esta sección decía que solo desde la laptop, ya no aplica.
Verificar primero si PlatformIO/esptool están instalados aquí; si no, instalarlos. Si se flashea
desde la laptop en vez de la RPi, también está bien — reportar cuál se usó y cómo salió.
