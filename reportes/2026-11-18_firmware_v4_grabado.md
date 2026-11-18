# Firmware v4 del ESP32 de motores: grabado y probado sin trayectoria (2026-11-18, 12:03–12:08)

## Objetivo
Fase A del plan (`PLAN_INTEGRACION_LAZO_Y.md`): grabar el firmware v4 (único cambio vs v3: `SET_VEL` del eje Y permitido durante `RUN`) y comprobar que todo lo demás se comporta igual que v3. Autorizado por Luis (cambiar el firmware de motores documentando y reportando).

## Metodología
1. Compilación: `espressif32 @ 7.0.1` (core 2.0.17, IDF v4.4.7), PlatformIO 6.2.0 en `~/pio_venv` (+ `esptool 4.11.0`), núcleo `~/pio_core_scratch`. Control: v3 recompilado da 284192 B como el v3 grabado (SHA distinto: `7ed40d…` vs `ba6c29…`, causa no investigada).
2. Respaldo previo: `esptool read_flash 0 0x80000` → `control/firmware/respaldos_flash/flash_0x0_0x80000_20261118_1203.bin` (SHA-256 `125d7ec2…9d94`). **La zona 0x10000 del respaldo es byte a byte `binarios/v3_7.0.1/firmware.bin`** → lo grabado antes era exactamente v3.
3. Grabación: `write_flash 0x1000 bootloader 0x8000 partitions 0x10000 firmware` de `binarios/v4_7.0.1/` (hash verificado por esptool en las 3 zonas). Espera de 4 s.
4. Regresión sin movimiento (`control/firmware/prueba_regresion_sin_movimiento.py`), latencia (`pruebas/medir_latencia_ping_pong.py` n=200; `pruebas/medir_latencia_comandos.py` n=100, mismo método que el 11-10), y A4: `control/firmware/prueba_v4_set_vel_y_aire.py` (Y sube 1 mm y vuelve, en el aire, pie a ≈57 mm del contacto).

## Resultado (medido)
- **Regresión: TODO OK** — `PING`→`PONG`, `TRAJ_STATUS`→`IDLE`, `SET_VEL:1:0`→`OK`, `SET_VEL:9:0`→`BUSY`, posición sin cambio (`0:0:0` tras el reinicio). `pruebas/resultados/regresion_firmware_v4_20261118.json`.
- **Latencia igual que antes:** PING mediana **5.994 ms** (n=200; firmware anterior 5.994 ms); `GET_POSITION` **4.925 ms** (v3 el 11-10: 4.970), `TRAJ_STATUS` 4.912 ms. Con el cliente del lazo (`reset_input_buffer`+`readline`): `GET_POSITION` y `SET_VEL:1:0` ≈ 7.0 ms (p95 7.06), 0/100 respuestas inesperadas — es otro método, no comparable con el 4.925. En `medir_latencia_comandos.py` el primer PING tras abrir el puerto dio 105.7 ms y uno de 100 no respondió (arranque del ESP32). Datos: `pruebas/resultados/ping_pong_20261118_firmware_v4.csv`, `latencia_comandos_firmware_v4_20261118.{csv,txt}`.
- **A4:** Y subió 81 pasos (esperado 80 ≈ 1 mm) y volvió a 0; 58/58 `SET_VEL` con `OK`; RTT máx 7.1 ms. `pruebas/resultados/prueba_v4_set_vel_y_aire_20261118.json`.

## Limitaciones
- **No probado lo único que cambia en v4:** `SET_VEL` de Y *durante* `RUN`. Requiere `HOME` (solo sin prótesis, con Luis) → paso D2 del plan.
- El desplazamiento es el contado por el firmware, no medido con regla.
- Incidente menor mío: `medir_latencia_comandos.py` sobrescribe `pruebas/latencia_comandos.csv` (archivo con historia en git); restaurado con `git checkout` y la medición nueva guardada aparte.
- Restaurar v3 si hiciera falta: `binarios/v3_7.0.1/` (mismo comando de grabación) o el respaldo de hoy.

## Fuentes
`control/firmware/README.md` § v4, `control/firmware/control_velocidad_continua_v4.patch`, `PLAN_INTEGRACION_LAZO_Y.md`.
