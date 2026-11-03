# Cambios de firmware propuestos desde el RPi (para la sesión de la laptop)

El RPi no flashea el ESP32 (el cable USB está en la laptop), así que aquí quedan los cambios propuestos. **Léelo antes de tocar `communication.h`.** Última actualización: 2026-11-03.

> **DECISIÓN DE LUIS (2026-11-03): NO se modifica el firmware del ESP32** (ha funcionado bien y no quiere afectarlo). Todo lo de abajo es **solo una propuesta opcional, no aplicada, y no es necesaria** para la fase ILC (que usa la interfaz de trayectorias existente). Ver `reportes/2026-11-03_reporte_dia.md` § 9.

## 1. (OPCIONAL) Reducir el sondeo de recepción serial de 5 ms a 1 ms — PROPUESTO, NO APLICADO, NO NECESARIO
- **Dónde:** `platformIO_control_trayectoria_v1/src/communication.h`, función `communication_rx()` (líneas ~129 y ~141): `while(!Serial.available()) {vTaskDelay(pdMS_TO_TICKS(5));}`. Hay **dos** esperas (primer byte y bytes siguientes del mismo mensaje).
- **Por qué:** el RTT RPi↔ESP32 medido es 5.97 ms (σ 0.185, n=100) y es casi todo sondeo (`pruebas/2026-11-02_latencia_amti_rpi_esp32.md`). El sondeo suma latencia al lazo de control de fuerza (`control/DECISION_TIPO_CONTROL.md`).
- **Cambio:** definir `#define RX_POLL_MS 1` y usarlo en ambas esperas. Parche listo: `control/firmware/reducir_polling_rx.patch` → desde la raíz del repo, `git apply control/firmware/reducir_polling_rx.patch`.
- **Estado:** **no compilado ni probado** (el RPi no tiene PlatformIO).
- **Antes de usarlo en movimiento:** `primary_task` (prioridad 1) y `auxiliar_task` (prioridad 2, la que corre las trayectorias) están ambas en el núcleo 1; comprobar que sondear a 1 ms no perturba la generación de pasos (probar sin carga, motores desacoplados).
- **Verificación esperada (hipótesis):** RTT de `PING` de ≈ 6 ms a ≈ 2–3 ms. Medir con `pruebas/medir_latencia_ping_pong.py --puerto /dev/ttyUSB0 --n 100` (en el RPi, ESP32 conectado al RPi) antes y después, y anotar el resultado en `pruebas/2026-11-02_latencia_amti_rpi_esp32.md` y en `reportes/`.
- **Quién decide:** Luis. Si no se aplica, no pasa nada grave: a ganancia de lazo moderada la latencia no domina (ver simulación).

## 2. (Solo si se mide la ejecución en el ESP32 — Paso 3 de latencia) — NO DEFINIDO AÚN
Podría requerir un pin GPIO del ESP32 que cambie de nivel al recibir/ejecutar el comando, cableado a un GPIO del RPi con GND común. No se pide todavía: primero ver si la simulación lo justifica.
