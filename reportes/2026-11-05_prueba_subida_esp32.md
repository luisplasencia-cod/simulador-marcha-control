# Prueba de subida de trayectoria al ESP32 (2026-11-05)

## Objetivo
Probar en hardware real `control/ilc/protocolo_subida_esp32.py` (solo carga en RAM, sin mover motores) y medir cuanto tarda subir una trayectoria.

## Metodologia
- Revision previa del script: `subir_trayectoria()` solo envia TRAJ_BEGIN, TRAJ_POINT, TRAJ_END. `ejecutar()` (RUN) NO se llamo. No se envio RUN/GOTO/MANUAL/SET_VEL.
- Firmware (main.cpp ~556-595): esos tres comandos solo escriben en arreglos RAM (gait_dt_ms, gait_dx/dy/dk_steps) y responden; no mueven nada.
- /dev/ttyUSB0 libre (fuser sin procesos), 115200 baud. Trayectorias de ceros, dt=10 ms, N = 10, 100, 500; 3 repeticiones cada una; tiempo con time.perf_counter. Script de prueba en el scratchpad (no en el repo).

## Resultado
| N | tiempo total | por mensaje (N+2) |
|---|---|---|
| 10 | 84.0-84.3 ms | 7.00 ms |
| 100 | 714.0 ms | 7.00 ms |
| 500 (maximo) | 3513.9 ms | 7.00 ms |
- Sin errores: todas las respuestas fueron TRAJ_READY, ACK:i correcto, TRAJ_STORED.
- Subir un ciclo completo de 500 puntos tarda ~3.5 s; es lineal (~7.0 ms por punto, extremadamente constante).
- Sin bytes de arranque pendientes al abrir (0 bytes tras 2 s de espera).

## Limitaciones
- Solo trayectorias de ceros; no se verifico que el ESP32 almacene los valores correctamente (no hay comando de lectura de vuelta usado) - NO VERIFICADO.
- RUN no probado. Los ~7 ms/punto son consistentes con ida y vuelta + sondeo RX del firmware (~5 ms, ver CLAUDE.md), no se desglosó.
- Implicacion: recargar 500 puntos entre ciclos (ILC) cuesta ~3.5 s; relevante frente al apoyo de 3.7-6.4 s a x6 (solo si se hace durante el ciclo).

## Fuentes
- `control/ilc/protocolo_subida_esp32.py`; `Codigo ESP32 MOV/platformIO_control_trayectoria_v1/src/main.cpp` (handle_receive_trajectory_command); mediciones de esta sesion.
