# Plan ordenado: lazo cerrado de Fz en Y + trayectoria X/K, operado desde la interfaz

Escrito el 2026-11-18 a pedido de Luis. Ejecutar **en orden**; cada paso tiene quién lo hace, qué se hace y un **criterio de paso**: si no se cumple, se para ahí y se diagnostica. Detalle técnico y hallazgos: `reportes/2026-11-18_plan_integracion_interfaz_lazo_Y.md`. Todo resultado se documenta en un reporte (Objetivo → Metodología → Resultado → Limitaciones → Fuentes) y en `CLAUDE.md`.

## Cómo se va a ver al final (flujo del operador en la interfaz)
1. **Conectar** → 2. **HOME (SIN pie)** → 3. **Fijar punto inicial** → 4. **Montar el pie** (la app sigue abierta) → 5. **Elegir trayectoria** (talla, montaje 37) y **escala de tiempo ×6** → 6. **Pantalla «Control de Fz»:** peso del sujeto **(kg)**, curva objetivo (%BW), Kp, tope de fuerza, n.º de ciclos, ángulo, hueco medido; la pantalla muestra el pico resultante en N y no deja iniciar si supera el tope o 1500 N → 7. **Iniciar:** aproximación con detección de contacto → `RUN` (X y K siguen la trayectoria, Y en lazo cerrado) → al terminar cada ciclo: Y sube (despegue), X/K vuelven al punto inicial, se repite → 8. **Observar en vivo:** Fz medida vs objetivo, error, velocidad ordenada a Y, posiciones X/Y/ángulo, estado, ciclo, motivo de aborto → 9. **Terminar/abortar:** Y sube siempre a una altura segura.

## Paso a paso

### Fase A — Firmware v4 (Claude; sin mover salvo ≤2.5 mm de Y en el aire)
| # | Qué | Criterio de paso | Estado |
|---|---|---|---|
| A1 | Compilar v4 (`SET_VEL` del eje Y permitido durante `RUN`) | compila; diff vs v3 = solo ese cambio | ✅ 2026-11-18 |
| A2 | Respaldo de flash → grabar v4 → esperar 4 s → regresión (`PING`, `GET_POSITION`, `TRAJ_STATUS`) | todo responde igual que con v3 | ✅ 12:04 (TODO OK; v3 respaldado y verificado byte a byte) |
| A3 | Latencia: PING ×200, `GET_POSITION`, `SET_VEL:1:0` | RTT ≈ 6 ms (como v3), sin respuestas perdidas | ✅ PING 5.994 ms, GET_POSITION 4.925 ms (= v3) |
| A4 | `SET_VEL` de Y en el aire (sube 1 mm y vuelve) | el contador vuelve al inicial | ✅ +81 → 0 pasos, 58/58 OK — reporte `reportes/2026-11-18_firmware_v4_grabado.md` |

### Fase B — Software en la copia `~/Projects/gaitsim-control-fz` (Claude; sin hardware salvo B2)
| # | Qué | Criterio de paso | Estado |
|---|---|---|---|
| B1 | `SET_VEL` en `protocol.py` + `esp32_controller.py` + `docs/protocol.md`; pruebas en `tests/` | pruebas pasan; las existentes siguen pasando | ✅ 17/17; las previas fallan igual en el original (no por esto) |
| B2 | Latencia de `SET_VEL` a través del controlador de la app (puerto abierto por la app, `SET_VEL:1:0`, nada se mueve) | p95 ≤ 10 ms; si no, el lazo usa un acceso propio de baja latencia al mismo puerto | ✅ mediana 3.94 / p99 4.2 / máx 5.5 ms con `log_hot_path=False` (con el log encendido: máx 19–67 ms) |
| B3 | `src/controllers/fz_loop.py` (sin Qt): lector Fz por UART, P + ILC, tope, detección de contacto, aborto, retorno a `y0`, log. **La duración del ciclo sale de la trayectoria × la escala de tiempo** (talla 174: 0.61 s × 6 = 3.66 s), y la curva objetivo se estira a esa duración | en simulación reproduce lo del lazo actual (RMS que baja ciclo a ciclo) |
| B4 | Envío de la trayectoria con **columna Y constante** (regla del firmware v4) | verificado en los `TRAJ_POINT` enviados: dY = 0 en todos |
| B5 | Máquina de estados: flujo «corrida con lazo de Fz» (precondiciones: HOME hecho, trayectoria cargada con Y plana, ADC OK, parámetros válidos; PAUSE/ABORT detienen el lazo y suben Y) | pruebas de transiciones pasan; no se puede iniciar sin cumplir las precondiciones |
| B6 | Pantalla «Control de Fz» con entradas (peso en kg, etc.) y gráficas en vivo (pyqtgraph) | se ve bien en la pantalla del RPi con datos simulados; **Luis la revisa** |

### Fase C — Mediciones que faltan (Claude + Luis; pie montado, sin HOME)
| # | Qué | Por qué | Criterio |
|---|---|---|---|
| C1 | **Ensayo A a −10°, −20°, −30°** (rigidez k por ángulo) | durante el apoyo el pie gira de +11° a −37°; k cae de 26 a 2.4 N/mm cerca de la punta y solo tenemos 3 ángulos. Con k fijo el lazo responderá muy lento en el segundo pico | curva k(ángulo) con 6 puntos |
| C2 | R6: pesas conocidas en el plato, **Luis lee NetForce** y yo leo el ADC | validar la escala en N (hoy solo validado en forma: las 3 "M") | diferencia ≤ 3 % (criterio propuesto) |
| C3 | (opcional) 60 Hz: laptop a batería y repetir R2 | el 60 Hz suma ≈2.4 N de ruido | σ baja o no |

### Fase D — Sesión integrada con Luis
| # | Quién | Qué | Criterio de paso |
|---|---|---|---|
| D1 | **Luis** | Retira el pie, manos fuera, recorrido despejado, **dice OK** → HOME desde la interfaz | `READY:xmax:ymax:amin:amax` |
| D2 | Claude + Luis | **Sin pie**: trayectoria X/K (Y plana) a ×6 en el aire, con Y en `SET_VEL` durante el `RUN` | `RUN` completa; `SET_VEL` responde `OK` durante el `RUN` (valida v4) |
| D3 | **Luis** | Monta el pie **sin cerrar la app** (si el ESP32 se reinicia se pierde el HOME) y mide el hueco | hueco medido |
| D4 | Claude + Luis | Corrida integrada: 6 kg (60 N) × 1 ciclo → 3 → 8; luego subir el peso de a poco (10 → 20 → 40 kg …) con tope; Luis mira NetForce y **lee los picos** | sin abortos inesperados; error que baja ciclo a ciclo; picos ADC ≈ NetForce |
| D5 | Claude | Reporte de la sesión | — |

## Decisiones de Luis (2026-11-18, 12:25)
- HOME: retira la prótesis antes; la vuelve a montar después, con la app abierta. ✅
- Talla **174**, escala **×6**. ✅
- Peso objetivo **80 kg** (picos ≈ 906/925 N). Se llega **subiendo de a poco**: 6 → 10 → 20 → 40 → 60 → 80 kg, cada escalón con su criterio (sin abortos inesperados, error estable, picos ADC ≈ NetForce). ✅
- **Visibilidad y reporte:** Fz del AMTI y el movimiento de los motores (X, Y, ángulo) en vivo en la pantalla y en el reporte posterior. ✅ — hoy: solo Fz del AMTI está cableado al ADC; el movimiento que se puede mostrar es el contado por el firmware (sin sensores de desplazamiento todavía).
- Estructura: **varias pisadas seguidas y automáticas tras UN solo HOME**; punto de inicio, parámetros, regreso y repetición = **los de la app de la etapa 2** (el lazo se monta sobre ese flujo). ✅ 12:30

## Decisiones que necesito de Luis (antes de la Fase D)
1. **Estructura de cada ciclo:** propuesta = contacto → apoyo con lazo → Y sube (despegue, la app ya tiene uno de 5 cm) → X/K vuelven al punto inicial → bajar de nuevo. ¿Correcto?
2. **¿Se puede montar el pie después del HOME con la app abierta?** (HOME con prótesis está prohibido.)
3. **Talla:** propuesta 174 (apoyo 0.61 s ≈ 0.615 s de Gutenberg; el artículo usa 1.74 m).
4. **Escala de tiempo:** la app trae 30× por defecto; la vigente es ×6. ¿Confirmas ×6?

## Diseño de la pisada con lazo de Fz sobre el flujo de la app (B3–B5, 2026-11-18)
Lo que la app YA hace en un ensayo (leído en `trajectory_screen._send_and_check` y `system_state`): una sola trayectoria fusionada = alinear ángulo → (si hay tara) despegue de 1 cm sobre la tara → apoyo desplazado al punto inicial → despegue de 5 cm (`END_LIFT_CM`), validada contra el espacio calibrado y las velocidades máximas; entre ensayos, `safe_return_to_position(inicial, piso)` (sube Y sobre el piso, ángulo a la referencia, mueve X, ángulo objetivo, baja — **X solo se mueve en el ángulo de referencia**, regla mecánica de la app).
**Una pisada con lazo de Fz (se repite N veces tras un HOME):**
1. `safe_return_to_position(punto inicial)` — **tal cual la app** (incluye su regla del ángulo de referencia).
2. Enviar la trayectoria del ensayo **con Y plana** (columna Y = la del punto inicial; sin despegue sobre tara ni despegue final de Y, porque Y la maneja el lazo). Se envía con el pie en el aire.
3. **Aproximación** (lazo, `SET_VEL` de Y en IDLE): baja hasta detectar contacto. Desde la 2.ª pisada baja rápido hasta ≈5 mm sobre la altura de contacto ya medida y lento el resto.
4. `RUN` → X y ángulo siguen la trayectoria; **en el mismo instante arranca la pisada del lazo** (duración = duración del CSV × escala: 0.61 s × 6 = 3.66 s; la curva objetivo se estira a esa duración).
5. Al terminar la pisada (`FINISHED`): el lazo **sube Y 5 cm** (como el despegue de la app) y para Y.
6. El ILC actualiza su corrección y vuelve a 1.
**Abortos:** tope de fuerza, lectura anómala, ADC sin datos, `SET_VEL` sin respuesta, descenso máximo → `PAUSE`/`ABORT` de la trayectoria (para X/ángulo), `SET_VEL` 0 y subir Y.
**Código:** módulos sin Qt en `src/fz/` de la copia (ILC y curva objetivo copiados del repo de control con su commit de origen; lector del ADC por UART; `fz_loop.py` = aproximación/pisada/subida; `fz_ensayo.py` = la secuencia de N pisadas usando la máquina de estados de la app). La pantalla Qt solo muestra y lanza.
**Lo que se ve en vivo y queda en el reporte:** Fz medida vs objetivo, error, velocidad ordenada a Y, posición X/Y/ángulo (contada por el firmware, vía `TRAJ_PROGRESS`), pisada y estado; log CSV por pisada + figura final.

## Riesgos conocidos
- k cambia con el ángulo durante la trayectoria (C1): con la ganancia fija de la Etapa 1 el seguimiento del segundo pico (despegue) será pobre; el ILC compensa en parte lo repetible.
- El retardo que añade la capa de comunicación de la app no está medido (B2).
- Con X moviéndose 35 cm durante el apoyo, el punto de contacto recorre el plato: no se ha probado el lazo con el pie desplazándose.
- El 60 Hz y la calibración en N siguen abiertos.
