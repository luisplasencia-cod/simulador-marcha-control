# Punto de entrada para Claude en el Raspberry Pi

Si acabas de clonar este repo en el RPi y es tu primera vez aquí: lee esto completo antes de hacer nada.

## Qué es este repo
Tesis de control del simulador de marcha (Luis Plasencia, PUCP). Contexto completo del proyecto en `CLAUDE.md` (léelo primero, siempre). Detalle de auditorías/búsquedas pasadas en `HISTORIAL.md`.

## Estado físico ahora mismo (2026-11-03)
- **Un solo ESP32 con este RPi: el de control de motores** (`Codigo ESP32 MOV/platformIO_control_trayectoria_v1/`, `PING`→`PONG`, serial 115200, `/dev/ttyUSB0`). Se edita/flashea desde la laptop.
- **ADC: el RPi lee el ADS1256 directo por SPI0** (AMTI Fz → AIN0 vs AINCOM; detalle en `esquemas/amti_ads1256_rpi/CONFIGURACION_ACTUAL.md`). `Codigo ESP32 ADS1256/` es una prueba aislada de otro montaje: solo referencia de la secuencia de init, no está conectado aquí.
- **ADC YA VALIDADO contra el AMTI real (2026-11-03):** se comparó una grabación directa del AMTI (software NetForce, `.bsf`→`.txt`) contra `lecturas_fz_20261102_175759.csv` del ADS1256 — RMSE 1.89 N, error pico a pico 4.03% (picos ~400 N), correlación r=0.9999. Ver `pruebas/comparar_amti_vs_ads1256.py` y el PNG. **Ya no hace falta repetir la validación de escala/signo del Paso 3 del plan de latencia — está hecha.**
- 1000 muestras/s confirmado, Fz en reposo ≈21.5 N de offset estable (hay que tarar — botón "Poner a cero" en el monitor), ruido σ≈0.85 N.

## Qué hacer, en orden — PRIORIDAD: Paso 2 del plan de latencia
Luis ya está sentado con el AMTI y puede aplicar cargas físicas. **Lo único que falta para decidir tiempo real vs. ILC es la latencia de adquisición AMTI→RPi (Paso 2) y la latencia total del lazo (Paso 3)** — el Paso 1 (comunicación RPi↔ESP32, RTT 5.97 ms) ya está medido y documentado en `pruebas/2026-11-02_latencia_amti_rpi_esp32.md`.

1. Entorno: `source .venv/bin/activate` (tiene pyserial, spidev, RPi.GPIO, ttkbootstrap).
2. **Paso 2 — latencia de adquisición, script nuevo:** `python pruebas/medir_latencia_escalon_amti.py --umbral_n 30 --n_eventos 10` mientras Luis aplica y retira carga sobre el AMTI repetidamente. **Lee el aviso al inicio del script antes de correrlo**: el script solo registra el instante en que el RPi DETECTA el cambio (reloj de pared); no mide la latencia absoluta por sí solo porque no hay un disparador físico independiente conectado al AMTI. Para la latencia real hace falta una referencia externa (ej. video del instante de pisar + pantalla con la hora del sistema visible, o un golpe audible). Si no se consigue esa referencia en esta sesión, documenta el log de cruces igual (sirve para ver consistencia/jitter) pero **no inventes un número de latencia sin esa referencia**.
3. **Llenar el Paso 2 del plan** en `pruebas/2026-11-02_latencia_amti_rpi_esp32.md` con lo que salga (reales, no estimados).
4. **Paso 3 — latencia total del lazo:** solo si el Paso 2 ya tiene un número real. Total = Paso 1 + Paso 2 + cómputo RPi + ejecución ESP32 (ver método en el plan).

## Retomar tras el reinicio del 2026-11-03 (lee esto primero)
1. Se cambió la sesión a Wayland (`rpd-labwc`) para recuperar el modo táctil. **Verifica:** `echo $XDG_SESSION_TYPE`, que no haya cursor de mouse y que `squeekboard` aparezca. Abre el monitor (`herramientas/monitor_gaitsim.py`) y confirma que funciona; si no, revierte `/etc/lightdm/lightdm.conf` a `rpd-x`.
2. Luis NO puede grabar video → el Paso 2 se hace con **escalón eléctrico GPIO→ADS1256** (ver `CLAUDE.md`, entrada 2026-11-03). Falta que Luis confirme AIN1/AINCOM y GPIO libre (propuesto GPIO27) en la etiqueta física. Luego escribir `pruebas/medir_latencia_gpio_adc.py` (revisar antes cómo `leer_ads1256_fz.py` elige canal). **No inventar** el retardo del amplificador del AMTI: sale del manual.
3. AIN0 estaba en −29 mV con 58 mV p-p (ayer +38.9 mV estable): Luis estaba conectando el AMTI; re-verificar con `python pruebas/leer_ads1256_fz.py --diagnostico`.
4. Si se usa `medir_latencia_escalon_amti.py`, mover `t = time.time()` a después de `leer_volts()`.

## Reglas del proyecto (no te las saltes)
- Verificar datos de hardware contra fuente real (datasheet, etiqueta física, medición) — nunca de memoria. Ya hay precedente de esto en el repo, sigue el mismo estándar.
- No redactar síntesis/texto de tesis salvo pedido explícito — Luis decide el enfoque, tú organizas/ejecutas lo técnico.
- Git: commitear y hacer `git push` cuando termines algo con sentido (no cada línea), para que la laptop de Luis vea el avance.

## Skill de diagramas de control (2026-11-03)
Se agregó `.claude/skills/diagrama-bloques-control/` al repo — dibuja diagramas de bloques de control (lazo cerrado, PID, etc.) en estilo libro de texto con ecuaciones en LaTeX, para cuando se diseñe/documente el controlador RT/ILC. Es una skill de proyecto (Claude Code la detecta sola al estar en `.claude/skills/` dentro del repo); no hace falta instalar nada aparte.

## Firmware del ESP32 — importante
Las actualizaciones al firmware de control de motores (`Codigo ESP32 MOV/.../main.cpp`) se hacen **desde la laptop** (sesión de Claude ahí), no desde aquí — ahí es donde está el cable USB al ESP32 para flashear con PlatformIO. Si necesitas un cambio de firmware, dilo en el commit/push y Luis lo coordina con esa sesión; no asumas que tú vas a flashear el ESP32 desde el RPi.

## Cambios de firmware propuestos
Los cambios al firmware que se piden desde el RPi quedan documentados en `Codigo ESP32 MOV/CAMBIOS_PENDIENTES_DESDE_RPI.md` (la sesión de la laptop los lee ahí). Hoy: reducir el sondeo RX de 5 a 1 ms (no aplicado).
