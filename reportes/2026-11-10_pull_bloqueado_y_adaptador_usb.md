# 2026-11-10 — Pull bloqueado (sin internet) y cambio de adaptador

## Objetivo
Traer con `git pull` los cambios nuevos (en particular el `main.cpp` del nuevo firmware ESP32) y reportar exactamente qué líneas se borraron, modificaron o agregaron.

## Metodología
`git pull` -> se colgó. Diagnóstico con `ip`, `ping`, `getent`, `ssh -T` con timeout. Procesos `git`/`ssh` colgados terminados por PID.

## Resultado
- **El pull NO se pudo hacer.** La Pi está en `wlan0` 172.20.10.2/28 (gateway 172.20.10.1); `eth0` DOWN.
  - `ping 8.8.8.8` y `ping github.com`: 100 % pérdida. DNS resuelve (140.82.112.3).
  - `ssh git@github.com`: `connect to host github.com port 22: Connection timed out`.
  - Conclusión medida: la red actual no da salida a internet. La causa (datos del hotspot, bloqueo del puerto 22, etc.) NO está determinada.
- Local: rama `master` limpia, igual que `origin/master` según la última referencia conocida (no se pudo hacer fetch, así que no se sabe si hay commits nuevos remotos).
- **Diff de `main.cpp` NO realizado**: el nuevo firmware no está en la Pi. Base local para el diff:
  - Archivo: `Codigo ESP32 MOV/platformIO_control_trayectoria_v1/src/main.cpp`
  - 846 líneas, SHA-256 `25ec7eff3ba83d2765c69a010d733d4fd9a7bdf2fbaae615428cdcb8d4509e2f`, último commit `ade50a7` (2026-11-02).
  - Ninguna otra copia local es más nueva (otras: `~/clonalo/...` 2026-11-02 y `gaitsim-control` de sept.).
- **Dato de Luis (2026-11-10):** quitó el adaptador; se trabaja así hasta que el cable/USB vuelva a desconectarse y entonces se verifica. No indicó cuál adaptador era; no se asume. Referencia: `reportes/PROBLEMA_PENDIENTE_desconexion_USB_ESP32.md`.

## Limitaciones
- No se probó si el ESP32 sigue apareciendo/desconectándose tras quitar el adaptador (no se hizo ninguna prueba hoy).
- Sin internet no se puede confirmar si hay commits remotos.

## Fuentes
Salidas de comandos del 2026-11-10 ~12:50 (ip, ping, ssh). Registro del adaptador: mensaje de Luis.

## Para destrabar el diff
Dar internet a la Pi (otra red / hotspot con datos) y repetir el pull, o pasar el `main.cpp` nuevo por otro medio (scp desde la laptop). Luego: `diff -u` contra la base (guardada arriba) y reporte línea por línea (borradas / modificadas / agregadas).
