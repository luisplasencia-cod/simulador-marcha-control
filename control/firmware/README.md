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

## Protocolo de prueba (en orden, no saltarse pasos)

1. **Compilar solo.** `pio run` en la laptop con el patch aplicado, sin flashear — confirma que compila.
2. **Flashear con los motores DESCONECTADOS del driver** (o el driver sin alimentación de potencia, solo lógica). Probar `SET_VEL` por serial manual, un eje a la vez, velocidades bajas, y confirmar con un osciloscopio o LED en el pin STEP que el pulso tiene el período esperado y que `DIR` no cambia a mitad de pulso.
3. **Probar el watchdog:** mandar un `SET_VEL` y dejar de mandar nada más — confirmar que el eje se detiene solo en ≈80 ms (medir con el LED/osciloscopio, no de oído).
4. **Con motores conectados, simulador despejado de personas**, un eje a la vez, velocidad baja, alguien con la mano en la alimentación de los motores listo para cortarla.
5. Recién después: integrar con `control/ilc/fz_ilc.py` / un lazo de realimentación real.

Aplicar (desde la raíz del repo, en la laptop): `git apply control/firmware/control_velocidad_continua.patch` (ya verificado con `git apply --check`, aplica limpio contra el firmware actual).
