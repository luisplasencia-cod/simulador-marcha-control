# Propuesta de cambio de firmware — reducir el sondeo del puerto serie

**OPCIONAL. Decisión de Luis (2026-11-03): no se modifica el firmware.** **No aplicado, no compilado, no probado** (sin PlatformIO en el RPi). Se aplica y flashea **desde la laptop**.

`reducir_polling_rx.patch` cambia `vTaskDelay(pdMS_TO_TICKS(5))` por 1 ms en `communication_rx()` (`communication.h`). El sondeo de 5 ms estaba en dos esperas: primer byte y bytes siguientes del mismo mensaje. Por eso el RTT medido (5.97 ms) es casi todo sondeo.

Ver también `Codigo ESP32 MOV/CAMBIOS_PENDIENTES_DESDE_RPI.md` (el archivo que lee la sesión de la laptop).

Aplicar (desde la raíz del repo, en la laptop): `git apply control/firmware/reducir_polling_rx.patch`

Resultado esperado (hipótesis, por verificar): RTT de `PING` de ≈ 6 ms a ≈ 2–3 ms (1 ms de sondeo + ≈ 0.95 ms de transmisión serial a 115200). Verificar con `pruebas/medir_latencia_ping_pong.py` antes y después y documentar. Cuidado: tarea `auxiliar_task` (prioridad 2) y la de motores comparten núcleo 1; revisar que el sondeo a 1 ms no afecte la generación de pasos antes de usarlo en movimiento.

¿Hace falta? Según la simulación, no es obligatorio a Kp≈10, pero baja ≈ 3–5 ms de latencia y da margen si se pide Kp≥20.

---

# Propuesta de cambio de firmware — velocidad continua (control en tiempo real)

**AUTORIZADO por Luis (2026-11-04): sí se puede modificar el firmware para lograr tiempo real.** Revierte la decisión del 2026-11-03 de no tocarlo. **No aplicado, no compilado, NO PROBADO EN HARDWARE** (sin RPi ni ESP32 en esta sesión) — ver protocolo de prueba abajo antes de usarlo con el simulador real.

## Qué agrega
`control_velocidad_continua.patch` agrega un comando nuevo, `SET_VEL:eje:pasos_por_seg_con_signo`, que pone un eje a girar a una velocidad continua (no un movimiento finito de N pasos como `MANUAL`). El RPi lo reenvía a su propio ritmo (ej. cada 10–20 ms) con la velocidad que calcule su lazo de realimentación de Fz/Fy; **el ESP32 no corre ningún lazo de control, solo obedece la velocidad pedida**. `pasos_por_seg = 0` detiene ese eje.

**No se tocó nada de `MANUAL`, `GOTO` ni de la ejecución de trayectorias (`RUN`) — son código aparte.** Lo que sí se tocó, porque es compartido: `axis_isr_common` (rama nueva para modo continuo, la rama existente de movimiento finito queda igual), `axis_stop` (una línea, limpia la bandera de modo continuo), `axis_move_steps` y `all_axes_finished` (un chequeo más, para que un movimiento finito nunca arranque encima de un eje en modo continuo), y el `RUN` de trayectoria (rechaza si algún eje está en modo continuo).

## Por qué hay que tener cuidado (riesgos reales, no teóricos)

1. **Cambiar de dirección con el motor girando.** El código original solo cambia `DIR` con el eje parado (primer paso de un movimiento nuevo). En modo continuo, si el RPi pide invertir el sentido, el patch **no** cambia `DIR` al vuelo — primero detiene el eje (espera a que `STEP` esté en bajo, como ya hace `axis_stop`) y recién en el siguiente `SET_VEL` arranca con la nueva dirección. Esto cuesta como máximo un período de control (~10–20 ms) pero evita invertir el driver a mitad de un pulso, que sí podría perder pasos o dañar el driver.
2. **Watchdog obligatorio.** Un eje en modo continuo no tiene cuenta de pasos para detenerse solo — si el RPi se cuelga, el link serial se cae, o el cálculo de la fuerza se traba, el motor seguiría girando indefinidamente sin esto. El patch agrega `revisar_watchdog_velocidad()` en `auxiliar_task` (corre cada 20 ms): si un eje en modo continuo no recibe `SET_VEL` en `VEL_WATCHDOG_TIMEOUT_MS` (80 ms), se detiene solo. **El RPi debe reenviar `SET_VEL` a un ritmo claramente menor a 80 ms** — si el lazo de control real corre más lento que eso, subir el timeout, no bajarlo.
3. **Límites de carrera.** `SET_VEL` revisa el límite en la dirección pedida antes de arrancar/cambiar — igual que `axis_move_steps` — pero **no** revisa continuamente mientras ya está girando; el límite físico lo para igual (`isr_limit()` llama a `axis_stop()` para los tres ejes, y ahora `axis_stop` también limpia `continuous_mode`), así que el límite sigue siendo la última red de seguridad, no `SET_VEL`.
4. **No se decidió todavía el eje real.** Falta confirmar (ver `control/ilc/README.md`) cuál de X/Y del firmware es el vertical (Fz) antes de mandarle `SET_VEL` de verdad.
5. **✅ CORREGIDO 2026-11-08 (antes bloqueo, encontrado 2026-11-07): el parche rechazaba `RUN` si CUALQUIER eje estaba en modo continuo, no solo el que usa la trayectoria.** `handle_execute_trajectory_command` tenía `if (Traj_state != TRAJ_IDLE || axis_x.continuous_mode || axis_y.continuous_mode || axis_k.continuous_mode)`. Para la arquitectura objetivo (Y con `SET_VEL` en tiempo real = Fz lazo cerrado, X/sagital con la trayectoria preestablecida del montaje 37 vía `RUN`, simultáneos, X/sagital en lazo abierto por ahora), eso bloqueaba `RUN` mientras Y estaba activo — justo lo opuesto de lo necesario. **Corrección aplicada al patch** (`control_velocidad_continua.patch`, aún no flasheado): la condición ya solo verifica `axis_x.continuous_mode || axis_k.continuous_mode` (sin `axis_y`) — X y K se siguen bloqueando entre sí y con `RUN` igual que antes; Y queda libre de correr en `SET_VEL` mientras `RUN` mueve X/K. Verificado con `git apply --check`, aplica limpio. **Sigue sin compilar ni flashear.** Detalle: `reportes/2026-11-08_fix_firmware_run_set_vel.md`.

## Protocolo de prueba (en orden, no saltarse pasos)

1. **Compilar solo.** `pio run` en la laptop con el patch aplicado, sin flashear — confirma que compila.
2. **Flashear con los motores DESCONECTADOS del driver** (o el driver sin alimentación de potencia, solo lógica). Probar `SET_VEL` por serial manual, un eje a la vez, velocidades bajas, y confirmar con un osciloscopio o LED en el pin STEP que el pulso tiene el período esperado y que `DIR` no cambia a mitad de pulso.
3. **Probar el watchdog:** mandar un `SET_VEL` y dejar de mandar nada más — confirmar que el eje se detiene solo en ≈80 ms (medir con el LED/osciloscopio, no de oído).
4. **Con motores conectados, simulador despejado de personas**, un eje a la vez, velocidad baja, alguien con la mano en la alimentación de los motores listo para cortarla.
5. Recién después: integrar con `control/ilc/fz_ilc.py` / un lazo de realimentación real.

Aplicar (desde la raíz del repo, en la laptop): `git apply control/firmware/control_velocidad_continua.patch` (ya verificado con `git apply --check`, aplica limpio contra el firmware actual).

---

# Análisis: ¿es `SET_VEL` lo mejor posible, o hay una arquitectura mejor? (2026-11-05)

**Autorización ampliada de Luis (2026-11-05):** no solo "agregar un comando" al firmware actual
(que solo recibe trayectorias y las ejecuta) — autoriza analizar y cambiar lo que haga falta del
firmware/arquitectura de comunicación para lograr el mejor tiempo real posible, no quedarse en el
parche mínimo por default. Esto se guarda acá porque es una autorización de alcance, no solo una
decisión técnica.

**Resultado del análisis: se consideraron 3 arquitecturas, se mantiene `SET_VEL` (la ya diseñada),
con las otras dos documentadas como mejora futura SI la latencia llega a ser el problema real** (hoy
no lo es — ver conclusión).

| Opción | Cómo funciona | Ventaja | Desventaja | Fuente del dato |
|---|---|---|---|---|
| **A. `SET_VEL` (la diseñada, §arriba)** | RPi manda velocidad por paso/dirección cada 10-20 ms; el ESP32 solo genera el tren de pulsos; el driver A6-750RS cierra su propio lazo de posición/velocidad con su encoder interno | No requiere tocar el cableado ni reconfigurar el driver; mantiene intacta la lógica de seguridad que ya funciona (límites, freno, homing); ya diseñada, con patch verificado | Pasa por el ESP32 (≈6 ms de RTT medido RPi↔ESP32, antes de llegar al driver); discretizado al ritmo de actualización serial | `control_velocidad_continua.patch`; RTT medido en `pruebas/` |
| **B. RS485 directo RPi→driver** | El RPi habla RS485 directo al A6-750RS en modo Velocidad (el driver lo soporta: manual confirma "Communication: Pulse/RS485/Analog", "Velocity Control Mode"); el ESP32 queda fuera del lazo de Fz, solo maneja límites/homing/freno/sagital | Elimina el salto RPi→ESP32→driver completo; el lazo de velocidad del propio driver es más rápido que generar pulsos por software | **No hay protocolo detallado a mano** — el manual que se encontró dice "refer to the detailed programming manual" para los parámetros RS485, que no se descargó; cablear RS485 nuevo (adaptador USB-RS485 en el RPi); **hay que rediseñar la seguridad**: hoy el ESP32 ve los límites de carrera antes de mover nada — si el RPi manda velocidad directo al driver, los límites tendrían que llegarle también al driver por otra vía (o duplicar la lógica), para no perder esa protección | Manual STEPPERONLINE A6, §5-6 (instalación, no el manual de parámetros) |
| **C. Analógico (DAC) ESP32→driver** | El ESP32 deja de generar pulsos para este eje y en cambio escribe un voltaje (DAC) proporcional a la velocidad deseada al driver en modo Analógico (también soportado) | El ESP32 ya tiene 2 DAC de 8 bits integrados (GPIO25/26) — no hace falta hardware nuevo para probarlo | Sigue pasando por el mismo salto RPi→ESP32 que la opción A (no gana latencia ahí); 8 bits = 256 escalones, posiblemente muy grueso para el control de fuerza; igual exige reconfigurar el driver a modo Analógico (sin protocolo de parámetros a mano, mismo problema que B) | Specs del ESP32 (DAC de fábrica); manual STEPPERONLINE A6, §5-6 |

**Conclusión (por qué se mantiene A):** la latencia que de verdad importa para la decisión de
control es el techo de ~130 ms donde el híbrido RT+ILC se desestabiliza (`DECISION_TIPO_CONTROL.md`,
tabla de comparación). La latencia total medida hoy (parcial, ≈10 ms: RPi↔ESP32 + ADS1256+SPI;
faltan AMTI y ejecución ESP32) está muy por debajo de ese techo — **sobra margen**, así que no hay
urgencia real de eliminar los ~6 ms que agrega el salto por el ESP32 (opción B) a costa de rediseñar
la seguridad de límites de carrera sin la documentación del protocolo RS485 en mano. La opción A
(`SET_VEL`) ya resuelve el problema real (el firmware actual no tiene NINGÚN comando de velocidad
continua) sin ese riesgo. **Si más adelante la latencia medida completa (con AMTI y ejecución ESP32
incluidos) se acerca al techo de 130 ms, ahí sí vale la pena retomar la opción B** — se deja
documentada acá para no tener que redescubrirla.

**Qué falta para reabrir la opción B si hace falta:** conseguir el manual de parámetros/protocolo
RS485 del A6-750RS (STEPPERONLINE, no el manual de instalación que ya se tiene); un adaptador
USB-RS485 para el RPi; diseñar cómo los límites de carrera siguen protegiendo sin pasar por el ESP32.
