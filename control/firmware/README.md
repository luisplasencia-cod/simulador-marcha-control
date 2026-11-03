# Propuesta de cambio de firmware — reducir el sondeo del puerto serie

**No aplicado, no compilado, no probado** (sin PlatformIO en el RPi). Se aplica y flashea **desde la laptop**.

`reducir_polling_rx.patch` cambia `vTaskDelay(pdMS_TO_TICKS(5))` por 1 ms en `communication_rx()` (`communication.h`). El sondeo de 5 ms estaba en dos esperas: primer byte y bytes siguientes del mismo mensaje. Por eso el RTT medido (5.97 ms) es casi todo sondeo.

Aplicar (desde la raíz del repo, en la laptop): `git apply control/firmware/reducir_polling_rx.patch`

Resultado esperado (hipótesis, por verificar): RTT de `PING` de ≈ 6 ms a ≈ 2–3 ms (1 ms de sondeo + ≈ 0.95 ms de transmisión serial a 115200). Verificar con `pruebas/medir_latencia_ping_pong.py` antes y después y documentar. Cuidado: tarea `auxiliar_task` (prioridad 2) y la de motores comparten núcleo 1; revisar que el sondeo a 1 ms no afecte la generación de pasos antes de usarlo en movimiento.

¿Hace falta? Según la simulación, no es obligatorio a Kp≈10, pero baja ≈ 3–5 ms de latencia y da margen si se pide Kp≥20.
