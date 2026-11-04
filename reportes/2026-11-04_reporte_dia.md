# Reporte del día — 2026-11-04

Etapa de control del simulador de marcha (Luis Plasencia). Sesión en la laptop, **sin RPi ni ESP32 a mano**.

**Regla de este reporte:** cada tema trae *Objetivo → Metodología → Resultado → Limitaciones → Fuentes*. Todo dato es **medido**, **tomado de una fuente citada**, **SUPUESTO** (marcado así) o **elección de diseño**.

## Resumen del día
1. **ILC para Fz implementado** (núcleo genérico + Fz + cliente serial), probado con planta sintética, no con hardware (§1).
2. **Firmware: parche de velocidad continua diseñado** (`SET_VEL`), **Luis autoriza modificar el firmware** (revierte la decisión del 2026-11-03) — vuelve a abrir la vía de tiempo real para Fz (§2).
3. **Decisión de tipo de control REABIERTA**: híbrido RT+ILC, con tabla de justificación ventajas/desventajas por opción (§3).
4. **Retardo del amplificador AMTI: SUPUESTO** (no hay número publicado por AMTI; se buscó y se confirma que no existe públicamente) (§4).
5. **Qué parámetro pesa más en el error**: la rigidez de contacto (k), no la velocidad del servo (τ) (§5).
6. **Aclaración de convención de ejes**: Z=vertical ya estaba en `CLAUDE.md` (sección energía); lo que sigue sin confirmar es a qué eje del firmware (X/Y) corresponde físicamente (§6).

**Qué NO se pudo cerrar:** nada de esto se probó en hardware real (sin RPi ni ESP32 en la sesión); falta confirmar qué eje del firmware es el vertical; falta la rigidez de contacto real (sin medir, `control/identificacion/PROTOCOLO.md` no ejecutado); falta la ganancia N→pasos para `control/ilc/fz_ilc.py`.

---

## 1. ILC para Fz

**Objetivo:** tener el control ILC listo para correr en cuanto haya hardware, reusable para Fy y sagital después.

**Metodología:** `control/ilc/ilc_core.py` (ley de aprendizaje genérica, sin saber de Fz ni de pasos) + `control/ilc/fz_ilc.py` (curva real Gutenberg/Fukuchi → corrección ILC → pasos del eje vertical) + `control/ilc/protocolo_subida_esp32.py` (cliente del protocolo `TRAJ_*` ya existente en el firmware).

**Resultado:** autoprueba con planta sintética (ganancia pura, no es el simulador real): el núcleo converge de RMS 6.1 a 0.2 en 15 ciclos; el módulo Fz completo (curva real incluida) converge de 74.7 N a 9.6 N de error en 5 ciclos.

**Limitaciones:** (a) no se sabe qué eje del firmware (X/Y) es el vertical físico — ver §6; (b) la ganancia fuerza→pasos (`pasos_por_n`) depende de la rigidez de contacto, no medida — el script se niega a correr sin ese dato; (c) el cliente serial (`protocolo_subida_esp32.py`) no se probó contra un ESP32 real.

**Fuentes:** código propio, contra `Codigo ESP32 MOV/.../communication.h` y `configurable_motion_data.h` (leídos, no modificados para esto).

## 2. Firmware: velocidad continua (`SET_VEL`)

**Objetivo:** permitir realimentación en tiempo real dentro del ciclo, autorizado por Luis el 2026-11-04 (revierte la decisión del 2026-11-03 de no tocar el firmware).

**Metodología:** parche aditivo (no modifica `MANUAL`/`GOTO`/trayectorias existentes) que agrega un modo de velocidad continua por eje, con watchdog de 80 ms (si el RPi deja de mandar `SET_VEL`, el eje se detiene solo) y protección contra cambiar de dirección con el motor girando (se para primero, se rearma en el siguiente ciclo).

**Resultado:** `control/firmware/control_velocidad_continua.patch`; `git apply --check` confirma que aplica limpio contra el firmware actual. Protocolo de prueba en banco documentado en `control/firmware/README.md` (compilar solo → motores desconectados → probar el watchdog → recién con motores).

**Limitaciones:** **no compilado, no flasheado, no probado en hardware** — no hay RPi ni ESP32 en esta sesión. No se debe usar en el simulador real sin pasar primero por el protocolo de prueba completo.

**Fuentes:** diseño propio, contra el código real del firmware (`main.cpp`, `communication.h`), diff verificado con `git apply --check`.

## 3. Decisión de tipo de control — REABIERTA

**Objetivo:** justificar con ventajas/desventajas por qué el control elegido es el híbrido RT+ILC, no solo con el número de error.

**Metodología:** comparación directa de 4 opciones (RT sola, RT+prealimentación, híbrido RT+ILC, ILC puro sin realimentación) contra los datos ya existentes de `control/simulacion/salida_consola.txt` (Kp=10, τ=20 ms SIN MEDIR, k=0.8 SIN MEDIR, T=10 ms).

**Resultado (tabla completa en `control/DECISION_TIPO_CONTROL.md`):**

| Opción | RMS último ciclo (%BW) | Ventaja | Desventaja |
|---|---|---|---|
| RT sola | 11.54 | Reacciona dentro del ciclo a lo no repetible; no se desestabiliza con latencia alta | Error alto, no mejora con el tiempo |
| RT + prealimentación | 2.00 | Mejor en latencia media | Necesita la rigidez de la prótesis de antemano; peor que RT sola a latencia alta |
| **Híbrido RT+ILC** | **0.40** | No necesita conocer la rigidez de antemano (variable que el proyecto quiere dejar libre); ~29x menos error | Techo de latencia (~130 ms); ~10-12 ciclos para aprender; exige firmware sin validar |
| ILC puro sin realimentación | — | — | Descartado: inseguro, no reacciona a mitad de pisada |

**Conclusión:** el argumento central no es "menos error" — es que el híbrido es el único que no exige calibrar la rigidez por prótesis.

**Limitaciones:** la simulación usa τ y k sin medir (se barren, no son datos); el techo de latencia (~130 ms) no incluye la latencia real completa (cómputo RPi + ejecución ESP32, sin medir).

**Fuentes:** `control/simulacion/rt_vs_ilc_latencia.py` + `salida_consola.txt` (datos de entrada: curva Gutenberg, Horst 2021, DOI 10.1038/s41597-021-01014-6).

## 4. Retardo del amplificador AMTI — SUPUESTO

**Objetivo:** tener un número para la latencia total del lazo.

**Metodología:** búsqueda web (2026-11-04) de un valor publicado por AMTI para el Gen 5; no se encontró ninguno. Se usa un valor supuesto por analogía: 0.79 ms calculados de los filtros analógicos del manual + ~1.5 ms supuestos por analogía con el retardo de un ADC de instrumentación sobremuestreado a tasa similar (el ADS1256 real midió 1.6–2.4 ms a 1000 SPS).

**Resultado:** AMTI ≈ 2–3 ms, **SUPUESTO, no verificado con AMTI, no medido con referencia física**.

**Limitaciones:** este número no se usó para decidir el tipo de control (esa decisión depende del firmware, no de la latencia); solo se usa para documentar la latencia total parcial.

**Fuentes:** búsqueda web (sin resultado AMTI-específico), `pruebas/calcular_retardo_amti_manual.py`.

## 5. Qué parámetro pesa más en el error (pregunta de Luis)

**Objetivo:** aclarar cuál parámetro de la planta influye más en el error de seguimiento (Luis preguntó por "los parámetros que pesen más", no por pasos de motor).

**Metodología:** leer el barrido de sensibilidad ya corrido en `control/simulacion/salida_consola.txt` (T=10 ms, Kp=10).

**Resultado:** con τ fijo en 20 ms, variar k (rigidez) de 0.5 a 1.5 mueve el error de RT de 16.52 a 6.32 %BW (10.2 puntos). Con k fijo en 1.0, variar τ de 10 a 50 ms lo mueve de 9.20 a 10.47 (1.27 puntos). **La rigidez de contacto pesa ~8x más que la constante de tiempo del servo** en este barrido.

**Limitaciones:** es sensibilidad dentro de un modelo con supuestos (τ, k no medidos), no una medición en hardware real.

**Fuentes:** `control/simulacion/salida_consola.txt` (sección "SENSIBILIDAD a parametros NO medidos").

## 6. Convención de ejes: Z=vertical vs. eje del firmware

**Objetivo:** aclarar una confusión de terminología señalada por Luis.

**Resultado:** "Z=vertical" ya es la convención establecida en `CLAUDE.md` (sección de energía, "sagital y=avance, z=vertical") — no es un error nuevo ni de Luis ni de esta sesión. Lo que sigue sin confirmar es **distinto**: a cuál de los ejes `X`/`Y` del firmware del ESP32 (que usa esos nombres genéricos, no "Z") está cableado físicamente el motor vertical. Son dos preguntas separadas; la primera está resuelta, la segunda no.

**Pendiente:** confirmar físicamente (mirando el simulador) cuál motor (X o Y del firmware) es el vertical, antes de usar `control/ilc/fz_ilc.py` o el parche `SET_VEL` contra hardware real. **Pista de Luis (2026-11-04, "me parece", no confirmado): Y = vertical, X = horizontal.**

## Mapa de lo producido hoy

| Carpeta | Contenido |
|---|---|
| `reportes/` | este reporte |
| `control/ilc/` | núcleo ILC, módulo Fz, cliente serial (sin probar en hardware) |
| `control/firmware/` | `control_velocidad_continua.patch` + protocolo de prueba en banco (no aplicado, no flasheado) |
| `control/DECISION_TIPO_CONTROL.md` | decisión reabierta + tabla de justificación |
| `CLAUDE.md` | estado actualizado (decisión reabierta, AMTI supuesto) |

**Para la próxima sesión (RPi o laptop):** confirmar qué eje del firmware es el vertical; medir la rigidez de contacto (`control/identificacion/PROTOCOLO.md`); seguir el protocolo de prueba del parche de firmware antes de flashearlo.
