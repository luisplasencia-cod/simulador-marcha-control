# 2026-11-10 — Prueba de comunicación con el ESP32 (firmware ORIGINAL, adaptador quitado)

## Objetivo
Con autorización de Luis (solo comunicación; ningún movimiento), comprobar que el ESP32 responde y dejar una línea base de RTT y de cortes USB tras quitar el adaptador.

## Metodología
- `control/firmware/prueba_regresion_sin_movimiento.py --sin_set_vel` (PING, GET_POSITION, TRAJ_STATUS; compara posición antes/después).
- `pruebas/medir_latencia_comandos.py --n 100` (solo lectura, sin `--mover`).
- Conteo de cortes con `journalctl -k | grep "disabled by hub"` antes/después. ADC desconectado por Luis; no se usó.
- Hora: 2026-11-10 ~13:00. Firmware en el ESP32: el original (no se ha flasheado nada).

## Resultado
- Regresión: PING→PONG OK; TRAJ_STATUS→IDLE OK; posición `0:0:0` antes y después (sin cambio). TODO OK. JSON: `pruebas/resultados/regresion_firmware_original_2026-11-10.json`.
- RTT (n=100 c/u; CSV `pruebas/resultados/latencia_comandos_2026-11-10_sin_adaptador.csv`):
  | Comando | Válidos | Media | σ | Mín–Máx |
  |---|---|---|---|---|
  | PING (régimen estable, intentos ≥4) | 96 | 4.365 ms | 0.514 | 3.86–5.94 |
  | GET_POSITION | 100 | 4.939 ms | 0.029 | 4.84–5.12 |
  | TRAJ_STATUS | 100 | 4.924 ms | 0.313 | 2.80–7.01 |
- Los intentos PING 2 (sin respuesta, timeout 1 s) y 3 (107 ms) ocurrieron justo tras el reinicio del ESP32 al abrir el puerto: efecto de arranque, no de régimen estable.
- Cortes USB `disabled by hub (EMI?)` en el journal del kernel: **0** antes y **0** después (y 0 en los 30 min previos).

## Limitaciones
- Ventana corta (~1 min de uso del puerto, 2 aperturas): que no haya cortes ahora NO demuestra que el adaptador fuera la causa; sin el servo vertical en movimiento (el caso donde fallaba) no se ejercitó el escenario de falla. Verificar cuando vuelva a desconectarse, como pidió Luis.
- El RTT de PING aquí (4.4 ms) difiere del 5.97 ms medido con otro script el 2026-11-03/05; los scripts y su manejo de timeout/lectura son distintos. No se concluye cambio real.
- Nota: el journal del kernel llegaba a ≥68 cortes el 11-05; el arranque de la Pi de hoy lo reinicia (conteo solo desde el arranque actual).

## Fuentes
Salidas de los scripts citados (2026-11-10 ~13:00).
