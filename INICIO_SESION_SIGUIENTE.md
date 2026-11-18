# EMPEZAR AQUÍ — próxima sesión en el RPi (escrito el 2026-11-18, tras la sesión de la mañana)

Si eres Claude en una sesión nueva: lee este archivo completo, luego `CLAUDE.md` (las entradas con fecha 2026-11-18 son las vigentes) y `PLAN_INTEGRACION_LAZO_Y.md`. **Regla de Luis: todo se documenta (Objetivo → Metodología → Resultado → Limitaciones → Fuentes), sin suponer ni inventar; las horas se leen con `date`, no se estiman.** Luis lee poco texto: respuestas cortas, un tema por intercambio.

## 1. Dónde quedó el rig (verificar a ojo antes de mover nada)
- **Prótesis acoplada**, pie **plano ≈ 0°** (por pasos de K, no medido), **X y K quietos**. Eje **Y de vuelta en su posición inicial** (contador relativo 0 tras cada corrida; el contador absoluto del firmware no es posición física). La planta del pie está a ≈ 57 mm del contacto (Luis midió «7 cm del suelo»).
- **ESP32 de motores:** firmware **v4** grabado (`SET_VEL` de Y permitido durante `RUN`); abrir su puerto lo reinicia y pierde el HOME (hoy no hay HOME: no hace falta para el lazo en una posición). Puerto `/dev/ttyUSB0` (único USB-serie visible).
- **ADC:** ESP32 de lectura (ADS1256 diferencial) → UART2 → `/dev/ttyAMA0` (NO `/dev/serial0`). Ese ESP32 está **alimentado por el USB de la laptop de Luis**: la laptop no debe suspenderse y nada debe abrir su COM8 (`C:\PB2\display\server.py` lo toma solo).
- **NetForce:** Luis lo usa como referencia visual (ponerlo en cero antes de cada corrida). Solo se lee **Fz** del AMTI por el ADC.
- **Reglas de seguridad:** **NUNCA `HOME` con la prótesis puesta** (Luis la retira, hace HOME, la vuelve a montar con la app abierta); ejes siempre como ENTERO (0=X, 1=Y, 2=K); `+` = subir en Y; Fz `+` = carga; un solo dueño del puerto del ESP32 de motores; matar procesos por PID, nunca `pkill -f`; antes de flashear respaldar la flash; `python -u` si se vigila la salida; avisar a Luis ANTES de cada corrida con carga (NetForce en cero, paro a mano) y esperar su OK.

## 2. Qué está hecho y validado en hardware (2026-11-18)
UART del ADC (R0–R5), Ensayo B (retardo ≈ 15–23 ms, tau ≈ 3–14 ms), lazo cerrado de Fz en Y con contacto, repetible, ILC converge (8 pisadas: 8.4 → 3.2 N a 60 N), tope de fuerza verificado, firmware v4, **escalera de carga 10/20/30/40 kg completa** (error final 3–4 % del pico; velocidad de Y hasta 57 mm/s; picos dentro de ±2 %), 50 kg abortó por el detector de saltos (corregido). Detalle: `reportes/2026-11-18_*.md`, `HISTORIAL.md` § 2026-11-18, figuras en `reportes/figuras/` y `reportes/escalera/20261118_124639/`.

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
- Interfaz de la etapa 2 (copia): `cd ~/Projects/gaitsim-control-fz && ./venv/bin/python main.py` (necesita pantalla). El original `~/Projects/gaitsim-control` NO se toca.
