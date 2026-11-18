# Cable USB nuevo, HOME desde la interfaz vigente y orden de los repos — 2026-11-18 (noche, RPi)

## Objetivo
Retomar tras el reinicio de la RPi y el cambio de cable USB RPi↔ESP32 de motores (Luis), dejar el simulador calibrado (HOME sin prótesis) en la interfaz VIGENTE y continuar la prueba de 3 ejes (X y ángulo en lazo abierto, Y en lazo cerrado de Fz) donde quedó a las 17:21. Dejar documentado qué repo/interfaz se usa, para evitar confusiones en sesiones futuras (pedido de Luis).

## Metodología
1. Sin mover nada: `dmesg`, `vcgencmd get_throttled`, flujo UART del ADC (`/dev/ttyAMA0`, 2 s), 200 PING/PONG (`pruebas/medir_latencia_ping_pong.py`).
2. **Error mío (17:41):** abrí la copia OBSOLETA `~/Projects/gaitsim-control-fz` (siguiendo `INICIO_SESION_SIGUIENTE.md`, escrito de mañana) y pulsé HOME por software. Luis la mandó cerrar (cerrada por PID) y reinició el ESP32 → ese HOME quedó cortado.
3. Se identificó la interfaz vigente por evidencia: commits de la tarde en `~/Projects/gaitsim-control` (`main`, 15:56–17:35) y la transcripción de la sesión de la tarde (corrió desde ese directorio, `~/.claude/projects/-home-simgaitlibra-Projects-gaitsim-control/`). Su lanzador con canal de control se había perdido de `/tmp` con el reinicio: se reconstruyó desde la transcripción y se guardó en el repo: `herramientas/lanzar_interfaz_control.py` (puerto por id del CP2102; comandos en `logs/interfaz_cmd.txt`).
4. 17:49:56: interfaz vigente abierta con el lanzador; conectó (PING OK) y pulsó HOME (sin prótesis, OK de Luis).

## Resultado (medido)
- Cable nuevo: PING/PONG 200/200, RTT 5.992 ms (σ 0.108, máx 7.40) = igual que antes. `throttled=0x0`. ADC por UART ≈1000 paquetes/s. CSV: `pruebas/resultados/ping_pong_20261118_cable_nuevo.csv`.
- `cp210x ttyUSB0: failed set request 0x12 status: -110` aparece al abrir el puerto; ya salía 207 veces el 11-05 (no es del cable nuevo; no corta).
- **HOME OK 17:49:56 → 17:51:38:** `READY:24557:42397:-5000:5545`, posición tras HOME `16557:26397:545`. Log: `logs/interfaz_20261118_174943.log`.
- **Durante el HOME hubo un corte por EMI, pero en el bus del TECLADO** (`usb usb1-port2: disabled by hub (EMI?)`, bus 1 = HID); **el ESP32 (bus 3, cp210x) no se cortó.**

## Limitaciones
- Un solo HOME con el cable nuevo; que el cable evite los cortes con el servo Y cargado aún no está probado (los cortes de la tarde ocurrieron también sin carga).
- El EMI sigue presente (afectó al teclado): el cable nuevo no elimina la causa, como mucho la tolera.
- El arreglo `TRAJ_STATUS` tras la pisada (commit `f7345ae` de la interfaz) sigue sin probarse en hardware.

## Orden de los repos (para no confundirse)
- `~/simulador-marcha-control` (este repo): scripts de control, pruebas, firmware, reportes, `CLAUDE.md` de la tesis.
- `~/Projects/gaitsim-control` (`main`): **interfaz vigente**, con el lazo de Fz integrado; su estado detallado en su `CLAUDE.md`.
- `~/Projects/gaitsim-control-fz` (`integracion-fz`): **OBSOLETA**, no abrir.
- Instrucciones de uso: `INICIO_SESION_SIGUIENTE.md` (aviso al inicio y § 6).

## Fuentes
`logs/interfaz_20261118_174943.log`, `dmesg` (RPi, arranque 17:36), `git log` de ambos repos, `~/Projects/gaitsim-control/CLAUDE.md` (bloque «Primera pisada con los 3 ejes»).
