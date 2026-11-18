# EMPEZAR AQUÍ — próxima sesión (actualizado 2026-11-18 noche, al cerrar el laboratorio)

Si eres Claude y Luis dijo «continuar»: lee ESTE bloque primero; lo de más abajo (desde «HISTORIA») es de la mañana y queda solo como referencia. **Reglas de Luis: todo se documenta (Objetivo → Metodología → Resultado → Limitaciones → Fuentes), sin suponer ni inventar; horas con `date`; respuestas cortas, un tema por intercambio.**

## 0. DÓNDE TRABAJAR (no confundirse de proyecto)
- **Abrir Claude SIEMPRE en `~/simulador-marcha-control`.** La interfaz vigente se alcanza sin salir de aquí: `./interfaz` → enlace a `~/Projects/gaitsim-control` (rama `main`, repo GitHub `GAITSIM`). Ahí está integrado el lazo de Fz (pantalla «Control de Fz», tara automática, flujo post-HOME, pisadas con 3 ejes). Su estado detallado: `interfaz/CLAUDE.md`.
- **NO ENTRAR:** `~/Projects/gaitsim-control-fz_OBSOLETA_NO_USAR` (copia de la mañana, superada), `~/Projects/gaitsim-control-*backup*`, y las partes de la etapa 2 que no tocan el lazo (matriz de variabilidad, «Ir a Posición Inicial» manual, firmware viejo en `interfaz/firmware/`).
- Datos de las pisadas de la interfaz: `interfaz/logs/fz/*.csv` (NO van a GitHub) → **copiarlos** a `reportes/datos/<fecha>_.../` con un LEEME y graficarlos con `herramientas/graficar_pisadas_interfaz.py` (figura en `reportes/figuras/`, enlazada desde el reporte).

## 0.1 Estado al cerrar (2026-11-18, 18:00)
- **Desconectados por Luis al cerrar:** cable USB RPi↔ESP32 de motores (cable NUEVO desde 17:35) y el ESP32 del ADC. Reconectar ambos al llegar.
- **HOME perdido** (el ESP32 se reinicia al reconectar). Prótesis **montada** (pie en el punto de partida de talla170, ≈10 mm sobre la tara) → **para hacer HOME, Luis DEBE retirarla antes.**
- Último resultado: pisadas 3 ejes (X y ángulo lazo abierto, Y lazo cerrado de Fz; 75 kg, x10, Kp 5) muy repetibles (RMS ≈ 220 N, 25 %) pero sin aprendizaje: la pisada 2 se abortó por un **hueco de 82 ms en el lazo** (detector de saltos), no por el cable. Reporte con figura: `reportes/2026-11-18_noche_cable_nuevo_home_e_interfaz_vigente.md`.

## 0.2 Qué hacer al llegar, EN ORDEN (cada paso con el OK de Luis)
1. Reconectar el ESP32 de motores (USB) y el del ADC; comprobar sin mover: `ls /dev/serial/by-id/`, `dmesg | tail`, ADC por `/dev/ttyAMA0` (≈1000 paquetes/s).
2. Luis retira la prótesis → abrir la interfaz con el lanzador (sección 6): conecta y hace HOME solo. **El lanzador pulsa HOME automáticamente: no abrirlo con la prótesis puesta.**
3. Tras el HOME la interfaz muestra «Prótesis montada» → lista de trayectorias (elegir `Control_apoyo_talla170_montaje37`) → confirmación → tara automática. Luis lo opera en la pantalla táctil.
4. **Antes de más pisadas, arreglar (sin hardware) el hueco del lazo:** que el hilo del lazo no se retrase por el redibujado, o que el detector de saltos use |ΔF|/Δt; probar en simulación (`interfaz/tests/manual_test_b5_*`, `..._b6_*`).
5. Correr 5 pisadas (`fz Control_apoyo_talla170_montaje37 75 10 5`) y ver si el ILC baja el 25 %. Guardar CSV + figura + reporte.
6. Comprobar en hardware que ya no sale el diálogo «Guardar Posición Inicial» tras las pisadas (arreglado hoy, solo probado offscreen).
- Abierto: meseta de Fz a 4.5–6 s (¿rigidez en punta, k = 2.4 N/mm?), delta ILC ≈ 89 N casi constante, 60 Hz en Fz, R6 (pesas vs NetForce), oscilación ~7 Hz a carga alta (prueba Kp 3 vs 5), guardar automáticamente la imagen de las gráficas de la interfaz.
- **Errores que no se repiten (reglas):** el id de trayectoria es el nombre COMPLETO del CSV sin `.csv`; no abrir la copia obsoleta; no abrir `/dev/ttyUSB0` desde otro script con la interfaz abierta; leer el reporte más reciente y `git log` de ambos repos antes de abrir/configurar nada.

---
# HISTORIA (mañana del 2026-11-18; solo referencia)

## 1. Dónde quedó el rig (verificar a ojo antes de mover nada)
- **Prótesis acoplada**, pie **plano ≈ 0°** (por pasos de K, no medido), **X y K quietos**. Eje **Y de vuelta en su posición inicial** (contador relativo 0 tras cada corrida; el contador absoluto del firmware no es posición física). La planta del pie está a ≈ 57 mm del contacto (Luis midió «7 cm del suelo»).
- **ESP32 de motores:** firmware **v4** grabado (`SET_VEL` de Y permitido durante `RUN`); abrir su puerto lo reinicia y pierde el HOME (hoy no hay HOME: no hace falta para el lazo en una posición). Puerto `/dev/ttyUSB0` (único USB-serie visible).
- **ADC:** ESP32 de lectura (ADS1256 diferencial) → UART2 → `/dev/ttyAMA0` (NO `/dev/serial0`). Ese ESP32 está **alimentado por el USB de la laptop de Luis**: la laptop no debe suspenderse y nada debe abrir su COM8 (`C:\PB2\display\server.py` lo toma solo).
- **NetForce:** Luis lo usa como referencia visual (ponerlo en cero antes de cada corrida). Solo se lee **Fz** del AMTI por el ADC.
- **Reglas de seguridad:** **NUNCA `HOME` con la prótesis puesta** (Luis la retira, hace HOME, la vuelve a montar con la app abierta); ejes siempre como ENTERO (0=X, 1=Y, 2=K); `+` = subir en Y; Fz `+` = carga; un solo dueño del puerto del ESP32 de motores; matar procesos por PID, nunca `pkill -f`; antes de flashear respaldar la flash; `python -u` si se vigila la salida; avisar a Luis ANTES de cada corrida con carga (NetForce en cero, paro a mano) y esperar su OK.

## 2. Qué está hecho y validado en hardware (2026-11-18)
UART del ADC (R0–R5), Ensayo B (retardo ≈ 15–23 ms, tau ≈ 3–14 ms), lazo cerrado de Fz en Y con contacto, repetible, ILC converge (8 pisadas: 8.4 → 3.2 N a 60 N), tope de fuerza verificado, firmware v4, **escalera de carga 10/20/30/40 kg completa** (error final 3–4 % del pico; velocidad de Y hasta 57 mm/s; picos dentro de ±2 %), 50 kg abortó por el detector de saltos (corregido). Detalle: `reportes/2026-11-18_*.md`, `HISTORIAL.md` § 2026-11-18, figuras en `reportes/figuras/` y `reportes/escalera/20261118_124639/`.

> ⚠️ **CÓMO SE TRABAJA HOY (léase primero, 2026-11-18 noche):**
> - **Dos repos, dos sesiones de Claude.** Este repo (`~/simulador-marcha-control`) = scripts de control, pruebas, firmware y REPORTES. La interfaz del simulador = `~/Projects/gaitsim-control` (rama `main`): es la app de la etapa 2, pero **en ella se integró el lazo de Fz de este proyecto** (pantalla «Control de Fz», tara automática, flujo post-HOME, 1.ª pisada 3 ejes 17:21). La sesión de la tarde del 2026-11-18 corrió DESDE ese directorio (transcripción en `~/.claude/projects/-home-simgaitlibra-Projects-gaitsim-control/`); su estado detallado está en el `CLAUDE.md` de ese repo.
> - **La copia `~/Projects/gaitsim-control-fz` (rama `integracion-fz`) está OBSOLETA: no abrirla.** (17:41 la abrí por error y mandé HOME desde ella.)
> - **Para abrir y OPERAR la interfaz desde Claude:** `herramientas/lanzar_interfaz_control.py` (de este repo; ver la sección 6). Abre la interfaz vigente a pantalla completa, conecta, **pulsa HOME solo** (¡nunca con prótesis!) y luego obedece comandos escritos en `logs/interfaz_cmd.txt`: `preparar <trayectoria>`, `fz <trayectoria> <kg> <escala> <pisadas>`, `detener`, `estado`. Log en `logs/interfaz_<fecha>.log`. El ESP32 se reinicia al abrir el puerto: con la interfaz abierta NO correr scripts que abran `/dev/ttyUSB0`.
> - **Antes de abrir/configurar algo:** mirar `git log` de AMBOS repos y el reporte más reciente por hora; el documento de inicio puede estar atrasado respecto de lo hecho después.

## 3. Decisiones de Luis vigentes
Varias pisadas seguidas tras un solo HOME, reutilizando el flujo de la app de la etapa 2 (punto inicial, regreso y repetición); talla **174**; escala **×6**; peso objetivo **80 kg** subiendo de a poco (10→20→…→90); visible en vivo en la pantalla del RPi y todo en el reporte; techo de velocidad de Y **9000 pasos/s** (12 000 fue brusco); autorizado modificar firmware de motores si se documenta; **la escala de tiempo para 80–90 kg la decide Luis** (cálculo: ×12 para 80 kg, ×14 para 90 kg, ver `reportes/2026-11-18_escalera_10_a_50kg_y_escala.md`).

## 4. Qué sigue, EN ORDEN (cada paso con el OK de Luis)
1. **Preflight (sin mover):** `pruebas/etapa2_rpi.sh preflight` → debe decir «LISTO».
2. **Retomar la escalera desde 50 kg** (decisión pendiente de Luis entre «50→70 kg a ×6» o «directo a 80/90 con ×12/×14»; mi recomendación: lo primero). Comando: `.venv/bin/python -u control/escalera_carga.py --si --pesos 50,60,70 --escala 6` (abre el visor en vivo, guarda en `reportes/escalera/<fecha>/` gráficas de fuerza, error, desplazamiento y velocidad de Y y una tabla; se detiene al primer aborto). Para 80/90 kg: `--pesos 80 --escala 12` y `--pesos 90 --escala 14`. Luis lee NetForce (picos y valle, **con números**: aún no hay una validación en N contra NetForce).
3. **Analizar** cada escalón (rigidez aparente, velocidad, oscilaciones; ver hipótesis del 50 kg).
4. **Integración con la interfaz de la etapa 2** (`~/Projects/gaitsim-control-fz`, rama `integracion-fz`, también subida a GitHub): hecho B1–B3 (`SET_VEL` en la app, latencia 3.9 ms, `src/fz/` con el lazo, probado en simulación). Falta B4 (enviar la trayectoria con **columna Y constante**), B5 (máquina de estados del flujo con lazo), B6 (pantalla «Control de Fz» con peso en kg y gráficas en vivo), luego Fase C (Ensayo A a −10/−20/−30°, pesas vs NetForce) y Fase D (sesión con HOME **sin pie**, trayectoria X/K con Y en lazo cerrado). Ver `PLAN_INTEGRACION_LAZO_Y.md`.

## 5. Abierto / sin explicar (no ocultar)
- **60 Hz** en Fz (σ 2.6 N, 2.4 N rms a 60 Hz; no lo causan los drivers quietos): origen sin determinar; prueba barata pendiente: laptop a batería.
- **Calibración en N contra NetForce:** solo validada la forma (3 «M»); falta leer magnitudes y pesas conocidas.
- **Anomalía del 10 kg (pisada 1):** Fz plana ≈ 370 ms al cargar; no se repitió en 9 pisadas; causa sin determinar.
- **Aborto de 50 kg:** salto de 39 N; ruido vs transitorio mecánico indistinguible; el umbral ahora escala con la carga (decisión de diseño, no medida).
- **Velocidad alta sin rampa:** 12 000 pasos/s fue brusco (Luis); el firmware no tiene rampa de aceleración (se podría suavizar desde el RPi); no se midió si el servo sigue el salto.
- **Contador de Y arranca en 4500 (no 0) tras abrir el puerto:** causa sin investigar (usar siempre `pos_y_rel()`).
- **«7 cm del suelo»:** no se sabe si es el suelo del laboratorio o la superficie del plato.
- Firmware v3 recompilado da SHA distinto al grabado (mismo tamaño): reproducibilidad exacta sin demostrar.
- Sin respuesta: Dante Elías y la asesora; AD7606 (módulo Reland) pedido/decidido pero sin esquema ni lector.

## 6. Comandos útiles
- Estado/arranque: `pruebas/etapa2_rpi.sh preflight`; ADC en vivo y resultados: `pruebas/etapa2_rpi.sh r2|r3|r5`.
- Lazo manual: `control/lazo_fz_tiempo_real.py --peso_sujeto_n <N> --fmax_n <1.25×pico> --hueco_mm 45 --extra_mm 60 --hueco_remedido --angulo_deg 0 --n_ciclos 6 --v_max <pasos/s> [--duracion_apoyo_s 0.615×escala] --fuente_fz uart --puerto_fz /dev/ttyAMA0 --ejecutar` (sin `--ejecutar` solo imprime el plan).
- Graficar una corrida: `control/telemetria/graficar_corrida.py <csv> --titulo "…" --salida x.png --mostrar`.
- Firmware: binarios en `control/firmware/binarios/` (v3, v4, original); respaldos en `control/firmware/respaldos_flash/`; restaurar con `esptool` (ver `control/firmware/README.md`).
- Interfaz VIGENTE operada por Claude: `cd ~/Projects/gaitsim-control && XDG_RUNTIME_DIR=/run/user/$(id -u) WAYLAND_DISPLAY=wayland-0 nohup venv/bin/python -u ~/simulador-marcha-control/herramientas/lanzar_interfaz_control.py > ~/simulador-marcha-control/logs/interfaz_$(date +%Y%m%d_%H%M%S).log 2>&1 &` → comandos: `echo 'estado' > ~/simulador-marcha-control/logs/interfaz_cmd.txt`. Cerrar: `kill <PID>`. Manual (Luis): `cd ~/Projects/gaitsim-control && ./venv/bin/python main.py`. ~~Copia `gaitsim-control-fz`~~: OBSOLETA.
