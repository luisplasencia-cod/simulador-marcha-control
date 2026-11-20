# Protocolo de la próxima sesión con la RPi (preparado 2026-11-20, desde la laptop, sin hardware)

## Objetivo
Dejar ordenado qué está validado y qué no tras la sesión RPi del 2026-11-19, qué falta para pasar al lazo de Fy (regla fija de Luis), y los pasos exactos, con comandos, de la próxima sesión. Reemplaza como guía a `2026-11-19_protocolo_proxima_sesion_rpi.md` (ya ejecutado en lo que a Kp/60 Hz/HOME se refiere).

## Metodología
Lectura de `2026-11-19_RPi_resumen_sesion.md` y de los reportes `prueba_kp5_kp3_kp5_70kg`, `pruebas_3ejes_cargas_y_trayectorias`, `pisadas_3ejes_interfaz_40kg`, `mejora_anticipacion_y_adelanto_ilc`, `analisis_delta_ilc_interfaz`, más `INICIO_SESION_SIGUIENTE.md` y CLAUDE.md. No se ejecutó nada con hardware ni se recalculó nada: las cifras son las de esos reportes.

## Resultado

### A. Estado real (todo del 2026-11-19, 1 prótesis `pie_pasivo_1`)
**Validado en hardware:**
- Interfaz, tras HOME sin prótesis: 3 ejes (Y cerrado de Fz, X y K abiertos), talla 170, x10, 40/60/75/80 kg, y talla 174 a 80 kg: 31/31 pisadas completas, 0 abortos, 0 cortes USB. RMSE de la última pisada 3.2–4.0 % del pico, r 0.986–0.991; el ILC aprende (pisada 1 ≈ 8.7–10 % → 3.2–4.0 %); a 80 kg se estabiliza desde la pisada 6 (3.6 %, r 0.988). Talla 170 vs 174 casi igual (3.6 vs 3.5 %). (`pruebas_3ejes_cargas_y_trayectorias`)
- Solo Y (script), 80 kg x10, pie plano: base 2.1 %, r 0.996 → con `--ff 0.7 --ilc_adelanto_ms 30`: **1.2 %, r 0.999** (pisadas 6–8; carga inicial 49 → 20 N RMS). (`mejora_anticipacion_y_adelanto_ilc`)
- La oscilación 4.7 Hz (con `t_real`) depende de Kp (Kp 3: amplitud 0.31×, frecuencia 3.58 Hz): la crea el lazo, no es resonancia externa. Kp programado por k(F) la reduce 3–10× sin perder seguimiento (`ganancia_programada_k_vs_carga`).
- Filtro 60 Hz con ADC real: σ 2.63 → 0.24 N. PING 200/200 5.98 ms.
- Arreglo de la base de tiempo del ILC en la interfaz (referencia por tiempo real): pisada 6.00 s, el ILC ya aprende (40 kg: 7.7 → 4.1 %).

**NO validado / sin hacer:**
1. La mejora ff 0.7 + adelanto 30 ms **no se ha probado en la interfaz con hardware** (el 1.2 % es solo Y con el script; en el script la pisada dura 8.1 s, en la interfaz 6.0 s: la rampa es 1.35× más rápida). La cifra de 3 ejes sigue siendo 3.6 %.
2. **Escala:** todo se probó a x10; CLAUDE.md dice x6 vigente. A x6 la velocidad de Y sube (con x10 la velocidad ordenada máx. fue ≈65 mm/s a 80 kg frente al techo de trabajo de 112 mm/s; el cálculo previo para 80 kg a x6 daba ≈116 mm/s, extrapolación no medida). La escala a usar la decide Luis.
3. Criterio de pasar a Fy: el umbral de error se toma de `reportes/2026-11-20_criterio_error_estandarizado.md` (propuesta: r ≥ 0.95 + RMSE normalizado; unidad y valor a decidir por Luis/asesora). Mientras tanto no se toca Fy/CoP.
4. Tabla k(F) solo en pie plano: a 11° (talón) el pie es mucho más blando (400 N tras 60 mm, 2 abortos seguros); Kp programado y ff usan k(F) de plano pero el pie pasa por otros ángulos en la trayectoria.
5. R6: la escala en N de la ruta UART no está validada con pesas contra NetForce (solo confirmación cualitativa de forma y número de ciclos el 11-18; un escalón de 2.246 kg dio +1.8/+3.2 %).
6. Estimador de k en línea (`control/identificacion/estimador_k_en_linea.py`) y notch: diseñados, NO conectados al lazo; no dibujarlos en el diagrama hasta integrarlos.
7. 60 Hz: el filtro funciona pero el origen eléctrico (tomas/tierra) sigue sin diagnosticar con Luis.
8. Fz, desplazamiento y velocidad de Y son ORDENADOS/medidos por el ADC; no hay sensor de posición instalado.
9. Periodo real del lazo ≈13.7 ms (no 10); causa no verificada.
10. Una sola prótesis, 1 serie por condición; no hay repetibilidad entre días ni estadística.
11. Sin explicar: contador del ESP32 conservado al abrir el puerto el 11-19 11:45 (otros días se reiniciaba).

**Estado físico al cerrar (11-19, 11:55):** prótesis montada, pie plano 0° (acomodado a mano por Luis tras el incidente de K), HOME perdido/no verificado, interfaz cerrada. Interfaz en GitHub GAITSIM `main` `0110a13`; `data/positions/inicio.json` sin subir.

### B. Pendientes priorizados (qué falta para poder pasar a Fy)
1. **(Requiere la RPi) Tras aplicar las mejoras en la interfaz, volver a probar 40 → 60 → 80 kg y comparar contra el criterio (r y RMSE). Validar en la interfaz (3 ejes) ff 0.7 + adelanto 30 ms** a 40 → 60 → 80 kg, 5–10 pisadas (ya son el defecto de la pantalla). Medir con `analizar_pisadas_interfaz.py`.
2. **Umbral de error según `reportes/2026-11-20_criterio_error_estandarizado.md`** y **escala** (x10 probado; x6 pedido; ver A.2). Con eso queda definido el criterio.
3. **Repetibilidad (requiere la RPi):** repetir la serie de 80 kg ≥ 2 veces y documentarlo (otro arranque, idealmente otro día) y reportar dispersión de RMSE/r.
4. **HOME + 3 ejes a 80 kg** con la mejora, como un flujo continuo (HOME sin prótesis → montar → trayectoria → varias pisadas).
5. **R6** (pesas vs NetForce) y **60 Hz** (diagnóstico eléctrico con Luis).
6. k(F) por ángulo (al menos talón y punta) si el error por fases lo exige.
7. Opcional: usar en el script la misma base de tiempo real que la interfaz; integrar el estimador de k.

## Pasos de la sesión, en orden (cada movimiento con el OK de Luis)

**Frase exacta para la RPi:** `continuar: git pull, lee reportes/2026-11-20_protocolo_proxima_sesion_rpi.md y sigue sus pasos en orden; no muevas nada sin mi OK.`

1. `cd ~/simulador-marcha-control && git pull`. Leer este protocolo y `reportes/2026-11-19_RPi_resumen_sesion.md`. Confirmar con Luis: escala (x10 o x6) y umbral de error. Luis despeja el carro.
2. Sin mover: `pruebas/etapa2_rpi.sh preflight`; `ls /dev/serial/by-id/`; `dmesg | tail`; PING/PONG (`pruebas/medir_latencia_ping_pong.py`); ADC por `/dev/ttyAMA0` ≈1000 paquetes/s. No ejecutar scripts de hardware solo para ver flags (incidente `medir_hueco.py --help`).
3. **Luis retira la prótesis** y dice OK explícito de HOME. Abrir el lanzador (pulsa HOME solo; NO abrirlo con la prótesis puesta):
   `cd ~/Projects/gaitsim-control && XDG_RUNTIME_DIR=/run/user/$(id -u) WAYLAND_DISPLAY=wayland-0 nohup venv/bin/python -u ~/simulador-marcha-control/herramientas/lanzar_interfaz_control.py > ~/simulador-marcha-control/logs/interfaz_$(date +%Y%m%d_%H%M%S).log 2>&1 &`
4. Luis monta la prótesis, acepta en la pantalla táctil (trayectoria `Control_apoyo_talla170_montaje37`, tara automática). Si el pie no está a 0°, ajuste de K en pasos chicos (±100) con Luis mirando el sentido: tras HOME el signo de K NO es el de las notas del 11-10 (incidente 11:45).
5. Series 3 ejes por el canal de comandos (`echo '<cmd>' > ~/simulador-marcha-control/logs/interfaz_cmd.txt`), formato `fz <trayectoria_id> <kg> <escala> <n_pisadas>`: `fz Control_apoyo_talla170_montaje37 40 10 5`, luego 60, luego 80 (10 pisadas); sustituir la escala si Luis decide otra. Subir de carga solo si la anterior completó sin abortar. Abortar ante cualquier aviso de Luis.
6. Análisis: copiar CSV de `interfaz/logs/fz/` a `reportes/datos/<fecha>_pisadas_3ejes_interfaz_<kg>kg/` (con LEEME; los CSV de logs no van a git) y
   `python herramientas/analizar_pisadas_interfaz.py --salida reportes/figuras/<fecha>_analisis_<kg>kg "reportes/datos/<carpeta>/*.csv"`.
   Comparar con la base 3.6 % / r 0.988 (80 kg, 3 ejes sin mejora).
7. Repetir 80 kg (repetibilidad). Si procede, R6: `pruebas/calibracion_pesas.py --masas ...` y 60 Hz (`pruebas/ruido_60hz_filtro.py`) con Luis.
8. Cierre: reporte (Objetivo → Metodología → Resultado → Limitaciones → Fuentes), commit y push, actualizar CLAUDE.md e `INICIO_SESION_SIGUIENTE.md`. Antes de apagar la RPi: `sync`.

Reglas que siguen valiendo: nunca HOME con prótesis; ejes siempre enteros (0=X, 1=Y, 2=K); id de trayectoria = nombre del CSV sin `.csv`; no abrir `/dev/ttyUSB0` desde otro script con la interfaz abierta; no abrir la copia obsoleta; horas con `date`; no tocar Fy/CoP hasta cumplir el criterio.

## Limitaciones
Documento hecho solo con lectura de reportes (sin repetir cálculos ni ver los CSV); los comandos `fz ...` y las rutas se tomaron de los reportes e `INICIO_SESION_SIGUIENTE.md`, no se ejecutaron; la sintaxis exacta de `calibracion_pesas.py` y `analizar_pisadas_interfaz.py` se verificó solo por sus argparse.

## Fuentes
`reportes/2026-11-19_RPi_resumen_sesion.md`, `reportes/2026-11-19_{prueba_kp5_kp3_kp5_70kg,pruebas_3ejes_cargas_y_trayectorias,pisadas_3ejes_interfaz_40kg,mejora_anticipacion_y_adelanto_ilc,analisis_delta_ilc_interfaz,ganancia_programada_k_vs_carga}.md`, `INICIO_SESION_SIGUIENTE.md` (§ 0.2, § 6), CLAUDE.md (reglas 2026-11-19).


**Todo lo que requiera la RPi (repetibilidad 80 kg, re-prueba 40→60→80 kg con las mejoras, comparación contra el criterio) queda PENDIENTE hasta tenerla.**
