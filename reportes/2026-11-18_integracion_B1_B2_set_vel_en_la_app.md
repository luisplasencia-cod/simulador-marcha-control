# Integración, pasos B1–B2: `SET_VEL` dentro de la app de la etapa 2 y su latencia real (2026-11-18, 12:10–12:20)

## Objetivo
Paso B1 y B2 de `PLAN_INTEGRACION_LAZO_Y.md`: agregar `SET_VEL` a la app (`~/Projects/gaitsim-control-fz`, rama `integracion-fz`) respetando su arquitectura, y medir si su capa de comunicación sirve para un lazo de 10 ms con un watchdog de 80 ms en el firmware.

## Metodología
- Leí `protocol.py`, `esp32_controller.py`, `serial_manager.py` y `docs/protocol.md` de la app. Implementé `build_set_velocity()` (eje X/Y/A → 0/1/2, entero, |v| ≤ 1600), `ESP32Controller.set_velocity()` (timeout de respuesta 50 ms y de candado 20 ms), `set_status_polling_enabled()`, y documenté el comando en `docs/protocol.md` (regla 5 de la app).
- Prueba sin hardware `tests/manual_test_set_vel.py` (transporte falso que responde desde otro hilo).
- Pruebas previas de la app que no usan hardware, corridas en la copia y en el ORIGINAL (sin escribir nada: `PYTHONDONTWRITEBYTECODE=1`).
- B2: `tests/manual_test_set_vel_latencia_hw.py` con el puerto real (`/dev/ttyUSB0`, firmware v4), solo `SET_VEL:1:0` (nada se mueve), ritmo ~10 ms por ciclo como el lazo.

## Resultado (medido)
- **Prueba sin hardware: 17/17 OK** (formato y eje numérico; rechaza eje inválido, decimales, `True`, >1600; `OK`→True, `BUSY`→False; sin respuesta corta a los **50 ms** en vez de 3 s; con el candado tomado 500 ms por otro hilo se rinde a los **20 ms**; el sondeo `TRAJ_STATUS` apagado no arranca).
- **Pruebas previas de la app:** `trajectory_loader` y `trajectory_offset` pasan; `trajectory_step_deltas`, `map_validation` y `trajectory_library` **fallan igual en el original** (firmas viejas en las pruebas y una trayectoria `balanceo_v4` que ya no existe) → fallos previos, no causados por este cambio; `run_requires_fresh_ensayo` espera interacción con la interfaz (corta por tiempo). El original quedó intacto (69 cambios de Luis, sin commits).
- **Dos riesgos de diseño encontrados en la app y resueltos:**
  1. **Candado único + timeout de 3 s + sondeo `TRAJ_STATUS` cada 1 s:** una respuesta perdida bloquearía el canal 3 s (más que todo el apoyo a ×6). → `SET_VEL` con timeouts cortos y el sondeo se apaga durante la corrida con lazo.
  2. **El log de tráfico serie** (`LineCappedFileHandler`) relee y reescribe el archivo completo (500 líneas) en cada línea nueva una vez lleno, bajo un candado global y dentro de `send_line`. → `SerialManager.log_hot_path = False` deja de registrar línea por línea solo `<SET_VEL…>` y sus `OK`/`BUSY` (lo demás se sigue registrando; el lazo guarda su telemetría propia).
- **B2, latencia de `SET_VEL` por la capa de la app (n=1000 por corrida, 0 timeouts, 0 respuestas ≠ OK):**

| Registro del tráfico | mediana | p95 | p99 | máx |
|---|---|---|---|---|
| encendido (n=300) | 3.94 ms | 4.33 | 6.60 | **67.2** |
| encendido (n=1000) | 3.94 ms | 4.29 | 6.62 | **19.6** |
| **apagado** (n=1000, ×2) | **3.94 ms** | 4.03 | 4.16–4.19 | **5.5** |

  La capa de la app (hilo lector siempre escuchando) es más rápida que el cliente del script del lazo (≈7 ms, que limpia el buffer y bloquea en `readline`). Con el registro apagado cumple holgado el criterio de B2 (p95 ≤ 10 ms).

## Limitaciones
- Medido con `SET_VEL:1:0` y Y quieto; no con Y moviéndose ni con una trayectoria corriendo (en ese caso llegan además líneas de progreso).
- La medida es el tiempo de la llamada en Python (envío → respuesta), no el tiempo hasta que el motor reacciona.
- Si una respuesta llega después de su timeout, el siguiente `SET_VEL` puede tomarla como suya (mismo tipo `OK`): inofensivo entre `SET_VEL` seguidos, documentado en el código.

## Fuentes
Código: rama `integracion-fz` de `~/Projects/gaitsim-control-fz` (commits `918458e`, el de `log_hot_path`); datos: `pruebas/resultados/set_vel_latencia_app_controller_20261118*.json`.
