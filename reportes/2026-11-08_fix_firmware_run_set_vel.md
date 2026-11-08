# Fix firmware: `RUN` ya no se bloquea por el eje Y en modo `SET_VEL`

**Sesión:** laptop, sin RPi/ESP32. Corrige un bloqueo encontrado el 2026-11-07 en el mismo patch de velocidad continua.

## Objetivo
Permitir la arquitectura objetivo: eje **Y (vertical, Fz) en lazo cerrado** vía `SET_VEL` en tiempo real, **simultáneo** con **X (horizontal) y K (sagital) en lazo abierto** siguiendo la trayectoria preestablecida del montaje 37 vía `RUN`. Por ahora solo el eje vertical cierra lazo; X y sagital siguen en lazo abierto hasta que Fz quede terminado y probado en hardware (regla de secuencia del proyecto: no se pasa al siguiente eje sin cerrar el anterior).

## Metodología
Se revisó el código real del patch (`control/firmware/control_velocidad_continua.patch`, función `handle_execute_trajectory_command`, el manejador de `RUN`). La condición de rechazo era:
```c
if (Traj_state != TRAJ_IDLE || axis_x.continuous_mode || axis_y.continuous_mode || axis_k.continuous_mode){
```
Como `SET_VEL` pone `axis_y.continuous_mode = 1` mientras el lazo de Fz está corriendo, cualquier intento de `RUN` (necesario para mover X/sagital por la trayectoria) se rechazaba con `ERROR` todo ese tiempo — bloqueando exactamente el escenario que se necesita.

## Resultado
Se angostó la condición para excluir `axis_y`:
```c
if (Traj_state != TRAJ_IDLE || axis_x.continuous_mode || axis_k.continuous_mode){
  // NO se incluye axis_y: la arquitectura objetivo corre Y en SET_VEL
  // (control de Fz en tiempo real) AL MISMO TIEMPO que RUN mueve X/K
  // (trayectoria preestablecida del montaje 37) -- fix 2026-11-08
  // X y K si se siguen bloqueando entre si y con RUN, igual que antes.
```
- X y K siguen protegidos igual que antes: si cualquiera de los dos está en modo continuo, o ya hay una trayectoria corriendo, `RUN` se sigue rechazando — esto no cambió.
- Y queda excluido de la condición: con Y en `SET_VEL`, `RUN` ya puede arrancar y mover X/K normalmente.
- Nada más del patch se tocó: `axis_isr_common`, `axis_stop`, `axis_move_steps`, `all_axes_finished`, el watchdog (80 ms) y la protección de cambio de dirección quedan igual.
- Verificado con `git apply --check control/firmware/control_velocidad_continua.patch` → aplica limpio contra el firmware actual (sin conflictos).

## Limitaciones
- **No compilado ni flasheado.** Esto es un cambio de texto del patch, no una prueba de hardware.
- No se verificó en código que `axis_move_steps` (usado por `RUN` para mover X/K paso a paso) maneje bien el caso de que Y esté siendo generado por la ISR en modo continuo al mismo tiempo que X/K corren en modo trayectoria — ambos comparten `axis_isr_common` y el mux de ejes (`axes_mux`), que ya estaba diseñado para esto, pero no hay prueba real que lo confirme.
- Sigue pendiente todo el protocolo de prueba de `SET_VEL` (compilar → motores desconectados → watchdog → motores conectados un eje a la vez) antes de probar X/K + Y simultáneos — ver `control/firmware/README.md`, sección "Protocolo de prueba".

## Fuentes
- `control/firmware/control_velocidad_continua.patch` (texto del patch, editado en esta sesión).
- `control/firmware/README.md` (bloqueo original documentado 2026-11-07, ahora marcado corregido).
