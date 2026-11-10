# 2026-11-10 — Firmware ESP32: qué líneas de `main.cpp` se agregaron / modificaron / borraron

## Objetivo
Reportar exactamente qué cambia en `main.cpp` (y `communication.h`) con el "nuevo firmware" (parche de velocidad continua `SET_VEL`), y revisar el parche antes de compilar/flashear.

## Metodología
1. `git pull --rebase --autostash` (2026-11-10 ~12:55, internet de nuevo disponible): 9 commits nuevos, sin conflictos. **El `main.cpp` del repo NO cambió en esos commits** (el hash sigue `25ec7eff…9e2f`, 846 líneas); el "nuevo firmware" vive solo como parche: `control/firmware/control_velocidad_continua.patch` (corregido 2026-11-08, fix de `RUN`).
2. Se aplicó el parche (`git apply --check` OK, `git apply` OK) a una COPIA en el scratchpad y se hizo `diff` contra el original. Nada se tocó en `Codigo ESP32 MOV/` ni en el ESP32.
3. Los números salen del `diff`, no de leer el parche a ojo. Diffs completos guardados en `control/firmware/diff_exacto/`.

## Resultado — parche v1 (el del repo, tal cual)
| Archivo | Líneas antes | Después | Agregadas | Borradas |
|---|---|---|---|---|
| `main.cpp` | 846 | 1009 | **169** | **6** |
| `communication.h` | 186 | 192 | **6** | **0** |

Números de línea: "antes" = `main.cpp` original; "después" = con el parche aplicado.

### `main.cpp` — bloque por bloque (15 bloques)
| # | Antes (línea) | Después (líneas) | Tipo | Qué es |
|---|---|---|---|---|
| 1 | tras 31 | 32–37 (+6) | AGREGADO | `struct Axis`: campos `volatile int continuous_mode` y `volatile unsigned long last_vel_update_ms` + comentario |
| 2 | tras 36 | 43–47 (+5) | AGREGADO | `#define VEL_WATCHDOG_TIMEOUT_MS 80` + comentario |
| 3 | tras 43 | 55–81 (+27) | AGREGADO | `axis_isr_common`: rama `if (ax.continuous_mode){…return;}` (pulso sin cuenta de pasos; solo `stop_requested` lo detiene, siempre con STEP en bajo) |
| 4 | 94 | 132 | **MODIFICADA** | `timerStop(ax.timer);    ` → `timerStop(ax.timer);` (solo se quitan espacios finales; sin efecto funcional) |
| 5 | tras 96 | 135 (+1) | AGREGADO | `axis_stop`: `ax.continuous_mode = 0;` |
| 6 | tras 125 | 165–166 (+2) | AGREGADO | init del eje: `continuous_mode = 0; last_vel_update_ms = 0;` |
| 7 | 171–172 | 212–214 | **MODIFICADAS** (2→3) | `axis_move_steps`: comentario reemplazado y condición `if (ax.steps_remaining != 0)` → `if (ax.steps_remaining != 0 \|\| ax.continuous_mode)` |
| 8 | tras 212 | 255–313 (+59) | AGREGADO | función nueva `axis_set_velocity()` |
| 9 | 216 | 317–319 | **MODIFICADA** (1→3) | `all_axes_finished()`: ahora exige también `!axis_x/y/k.continuous_mode` |
| 10 | tras 512 | 616–643 (+28) | AGREGADO | función nueva `handle_velocity_command()` (comando `SET_VEL`) |
| 11 | 602 | 733–738 | **MODIFICADA** (1→6) | `RUN`: `if (Traj_state != TRAJ_IDLE)` → `if (Traj_state != TRAJ_IDLE \|\| axis_x.continuous_mode \|\| axis_k.continuous_mode)` + 5 líneas de comentario (excluye Y a propósito) |
| 12 | tras 723 | 860–863 (+4) | AGREGADO | despachador de comandos: rama `else if (strcmp(rxPacket.command, SET_VEL)==0)` |
| 13 | tras 784 | 925–942 (+18) | AGREGADO | función nueva `revisar_watchdog_velocidad()` |
| 14 | tras 786 | 945–946 (+2) | AGREGADO | `auxiliar_task`: llamada a `revisar_watchdog_velocidad();` + línea en blanco |
| 15 | 795 | 955–958 | **MODIFICADA** (1→4) | `vTaskDelay(pdMS_TO_TICKS(100))` → `vTaskDelay(pdMS_TO_TICKS(20))` + 3 líneas de comentario |

**Líneas BORRADAS de `main.cpp` (las 6, textuales):** 94 (`timerStop(ax.timer);    `, versión con espacios), 171 (`// Verifiy if the requested axis is moving`), 172 (`if (ax.steps_remaining != 0){`), 216 (`return axis_x.steps_remaining == 0 && axis_y… && axis_k…;`), 602 (`if (Traj_state != TRAJ_IDLE){`), 795 (`vTaskDelay(pdMS_TO_TICKS(100));`). Todas se reemplazan (ninguna es borrado puro).

### `communication.h` — 1 bloque
| Antes | Después | Tipo | Qué es |
|---|---|---|---|
| tras 59 | 60–65 (+6) | AGREGADO | `#define SET_VEL "SET_VEL"` + comentario del protocolo |

Cambio de comportamiento heredado que conviene tener presente: el `vTaskDelay` de `auxiliar_task` baja de 100 a 20 ms (afecta cuánto tarda en arrancar una trayectoria tras `RUN`: hasta 20 ms en vez de hasta 100 ms).

## Hallazgos de la revisión (críticos primero)
1. **🔴 Bloqueo real (verificado leyendo el código): con el parche v1, `RUN` queda colgado si Y está en `SET_VEL`.** El bloque 9 hace que `all_axes_finished()` exija `!axis_y.continuous_mode`; pero los bucles de espera de las trayectorias (`while(!all_axes_finished())`, líneas 346, 403 y 460 del original) lo usan. Con Y en modo continuo (lazo de Fz) nunca da verdadero → la trayectoria se traba en el primer punto. Eso **anula el fix del 2026-11-08** (permitir `RUN` con Y continuo): `RUN` arrancaba pero no avanzaba. No probado en hardware: es deducción del código.
   - **Corrección propuesta = parche v2** (`control/firmware/control_velocidad_continua_v2.patch`, **no flasheado, no compilado todavía**): función nueva `trajectory_axes_finished()` (igual pero ignorando el modo continuo de Y) usada en esos 3 bucles; `all_axes_finished()` se mantiene para `MANUAL`/`GOTO`.
   - Cuenta del v2 contra el original: `main.cpp` 1020 líneas (**183** agregadas, **9** borradas; es decir, +14 y −3 respecto de v1: 11 líneas de función/comentario en el bloque 9 y 3 líneas modificadas en los bucles); `communication.h` igual que v1. Bloques distintos de v1: `216→317–330` (función nueva anexada), `346→460`, `403→517`, `460→574` (`all_axes_finished` → `trajectory_axes_finished`). Los demás bloques mantienen su contenido pero sus líneas "después" se corren (ver `diff_exacto/main_cpp_v2.diff`).
2. **🟠 El comentario de `communication.h` no coincide con el código.** Dice que `SET_VEL` responde `ERROR` con parámetros inválidos; el código (`handle_velocity_command`, bloque 10) responde `BUSY` en TODO rechazo (`ok = 0`: eje inexistente, velocidad negativa, dirección inválida, final de carrera). Un `BUSY` no distingue "reintenta" de "parámetro mal". El RPi debe tratar `BUSY` como "no aplicado", no como "ocupado transitorio".
3. **🟠 Trayectoria que lleve pasos en Y con Y en modo continuo:** `axis_move_steps` descarta Y en silencio (`return`). Correcto para el montaje 37 (Y fijo), pero si algún CSV trae `dy ≠ 0` esos pasos se pierden sin aviso.
4. **🟡 Límites de la ISR continua:** a velocidades muy bajas el semiperiodo es largo y `stop_requested` solo se atiende en el siguiente flanco de bajada (a 20 pasos/s ≈ 25 ms de latencia de parada; a 1 paso/s, 0.5 s). Para el lazo de Fz con velocidades de decenas–cientos de pasos/s es aceptable; no se midió.
5. **🟡 `platformio.ini`:** `upload_port = COM10` (Windows) y `platform = espressif32` sin versión: desde la Pi hay que pasar `--upload-port /dev/ttyUSB0`, y una versión nueva del core de Arduino-ESP32 (3.x) cambió la API de timers (`timerAlarmWrite`/`timerStart` ya no existen): puede no compilar. Ver sección de compilación abajo.

## Limitaciones
- Ni v1 ni v2 se probaron en hardware. v1 "aplica limpio" ≠ "funciona".
- El diff se hizo contra el `main.cpp` del repo (SHA-256 `25ec7eff3ba83d2765c69a010d733d4fd9a7bdf2fbaae615428cdcb8d4509e2f`). Si la laptop de Luis tiene un `main.cpp` distinto sin subir al repo, este reporte no lo cubre.
- Los comportamientos del hallazgo 1 y 4 son deducidos del código, no observados.

## Fuentes
`control/firmware/control_velocidad_continua.patch`; `Codigo ESP32 MOV/platformIO_control_trayectoria_v1/src/{main.cpp,communication.h}` (commit `ade50a7`); `reportes/2026-11-08_fix_firmware_run_set_vel.md`; `control/firmware/diff_exacto/*`.
