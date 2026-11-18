# Plan: integrar el lazo cerrado de Fz en Y con la interfaz de la etapa 2 (`gaitsim-control`) — 2026-11-18

## Objetivo (pedido de Luis, 2026-11-18)
Completar el lazo para probarlo con una **trayectoria** (X y ángulo K en lazo abierto, Y en lazo cerrado de Fz) y operarlo todo desde la interfaz que ya existe: **HOME → fijar punto inicial → iniciar → ejecutar**, observando todo en vivo en la interfaz, integrado con el proyecto de la etapa 2 (`~/Projects/gaitsim-control`).

## Lo que encontré (leído, no probado)
**La interfaz ya tiene** (PySide6, pantalla táctil, arquitectura por capas con reglas duras en su `CLAUDE.md`): conexión+PING, `HOME`, movimiento manual, posición inicial (`initial_position_session`), carga y envío de trayectorias CSV (`TRAJ_BEGIN/POINT/END`), `RUN/PAUSE/RESUME/ABORT`, tara de contacto, matriz de variabilidad, mapa de calibración. Estados: `DISCONNECTED→HOMING→IDLE→RECEIVING_TRAJECTORY→RUNNING→PAUSED`. Conversión: Y 800 pasos/cm (= 80 pasos/mm, coincide con lo medido), X 400 pasos/cm, ángulo ≈111.11 pasos/°. Trayectorias en `data/trajectories/` (montaje 37, tallas 160–180; CSV `Tiempo; X_cm; Y_cm; Ángulo`). Su firmware es el MISMO que el nuestro (`platformIO_control_trayectoria`).
**Lo que NO tiene y hay que agregar:** (1) el comando `SET_VEL` (ni en `protocol.py` ni en `docs/protocol.md`); (2) el lazo de Fz y la lectura del ADC (UART `/dev/ttyAMA0`); (3) una vista en vivo de Fz/referencia/error/u/posiciones; (4) coordinar el arranque del lazo con `RUN`.

## Problemas bloqueantes que descubrí en el firmware (parche v3 ya grabado)
1. **`SET_VEL` se rechaza con `BUSY` mientras hay una trayectoria activa** (**resuelto en v4, compilado 2026-11-18, no grabado**: ver `control/firmware/README.md` § v4) (`handle_velocity_command`: `if (Traj_state != TRAJ_IDLE) → BUSY`). Contradice el objetivo (Y en `SET_VEL` **a la vez** que `RUN` mueve X/K). Con el firmware actual el lazo de Y NO puede correr durante una trayectoria. Hay que permitir `SET_VEL` del eje Y (eje 1) mientras `Traj_state` es RUNNING/PAUSED.
2. **Las trayectorias traen columna Y.** *Actualizado tras leer el código:* `axis_move_steps` ya **ignora** movimientos finitos sobre un eje en modo continuo, así que mientras Y está en `SET_VEL` los deltas de Y se descartan. Pero si Y se detiene (velocidad 0 o watchdog) sale del modo continuo y el siguiente delta de Y SÍ lo movería → **la RPi debe enviar la trayectoria con la columna Y constante (deltas = 0)**; no hace falta otro cambio de firmware para esto.
3. **`SET_VEL` y `RUN` exigen estados distintos:** `RUN` solo desde `IDLE` tras `HOME`; el ESP32 se reinicia (y pierde el HOME y sus contadores) cada vez que se abre su puerto serie → **la interfaz debe ser la ÚNICA dueña del puerto durante toda la sesión** (nuestros scripts no pueden correr a la vez) y no cerrarlo entre HOME y la corrida.
Cambios de firmware autorizados por Luis (2026-11-18) con la condición de documentar y reportar; mis reglas: respaldar la flash antes de grabar, compilar con `espressif32 @ 7.0.1`, medir latencia, comportamiento idéntico al original sin `SET_VEL`. Opcional con el mismo flasheo: sondeo RX de 5→1 ms (el sondeo suma ≈5 ms al retardo del lazo).

## Arquitectura propuesta (respeta las reglas duras de `gaitsim-control`)
- `src/communication/protocol.py` + `esp32_controller.py`: agregar `SET_VEL` (llamada corta con timeout) y actualizar `docs/protocol.md` en el mismo cambio.
- `src/controllers/fz_loop.py` (nuevo, SIN Qt): lector de Fz (UART), control proporcional + ILC (reutiliza `control/ilc/fz_ilc.py` y la lógica de `lazo_fz_tiempo_real.py`), tope de fuerza, detección de contacto, aborto, retorno a `y0`, log con el formato de `control/telemetria/formato_log.md`. Corre en hilo propio, habla con el ESP32 SOLO a través de la máquina de estados (regla 1 de la app).
- `SystemStateMachine`: nuevo estado/transición para «corrida con lazo de Fz» (tras `RUN`: arranca el lazo; `PAUSE/ABORT` lo detienen y suben Y; `can_*` actualizados).
- UI: nueva pantalla/panel «Control de Fz» con parámetros: **peso del sujeto en kg** (pedido de Luis 2026-11-18; la referencia está en %BW → F_obj(t) = %BW(t)/100 · m · 9.81; se muestra el pico resultante en N y no se deja iniciar si supera el tope o el límite de 1500 N decidido), curva de referencia, Kp, tope, ciclos, ángulo, hueco, botones del flujo y **gráficas en vivo** (pyqtgraph: Fz vs referencia, error, u, Y/X/ángulo, estado y causa de aborto).
- Latencia: medir la del camino `esp32_controller` de la app (hilo lector, colas) antes de confiar en ella para el lazo de 10 ms; si añade retardo, el lazo usa su propio acceso de baja latencia al mismo transporte.

## Decisión de dónde integrar (Luis delegó, 2026-11-18)
**Copia completa** de `~/Projects/gaitsim-control` en **`~/Projects/gaitsim-control-fz`** (con su `.git` y su `venv`, sin el video fuente crudo de 1.2 GB que el proyecto ya ignora), rama nueva **`integracion-fz`**. El original queda intacto (verificado: mismo commit `8258f45`, mismos 69 cambios sin commitear de Luis). Motivo: no afectar la etapa 2 y poder comparar/descartar. La copia arrastra esos 69 cambios sin commitear del original tal cual.

## Fases (cada una con su criterio de paso; todo documentado)
0. **(hecho hoy)** Lazo de Y validado con contacto real (8 ciclos, ILC converge a ≈3 N) y tope verificado.
1. **Sin hardware:** parche de firmware v4 (puntos 1 y 2 + opcional sondeo 1 ms), compilar, revisar el diff línea por línea. Copia de trabajo de la app + `SET_VEL` en protocolo/controlador + `fz_loop.py` probado con un ESP32 simulado.
2. **Con el ESP32, sin mover ejes:** respaldo de flash, grabar v4, regresión (`PING`, `GET_POSITION`, `TRAJ_STATUS`), latencia, `SET_VEL` con Y quieto.
3. **Interfaz:** pantalla de Fz con gráficas en vivo; prueba con datos simulados y luego con el ADC real (sin mover).
4. **Sesión con Luis (HOME SIN PIE):** HOME → fijar punto inicial → montar el pie → trayectoria X/K con Y en lazo cerrado. Primero con carga baja y el pie en el aire, luego con contacto.

## Riesgos y lo que NO sé
- La prótesis acoplada impide HOME: el orden físico (HOME sin pie → montar el pie → ir al punto inicial) debe ser viable para Luis; **no confirmado**.
- Sincronía: el lazo (ciclo ILC de 3.69 s fijo) debe arrancar con el `RUN`; la duración real del apoyo en el CSV y su alineación con la referencia **no están verificadas**.
- No sé cuánto retardo añade el camino de la app al lazo de 10 ms.
- La referencia de Fz del lazo (Gutenberg, 3.69 s a x6) y la duración de la trayectoria del montaje 37 deben ser consistentes; hoy no lo he comprobado.
- El working tree de `gaitsim-control` tiene cambios sin commitear (CSVs montaje35 borrados, `CLAUDE.md` y posiciones modificados): no editar ahí sin decidir qué hacer con ellos.
