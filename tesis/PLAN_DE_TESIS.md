# Plan de tesis — Luis Plasencia (Ing. Biomédica, PUCP)

**ESTE ES EL LUGAR ÚNICO de todo lo de la tesis y las prácticas (decisión de Luis, 2026-11-25).** Lo vigente va arriba; el registro de decisiones y lo pendiente, al final. Cada cambio se anota aquí en el mismo turno.
Reglas: se redacta según `GUIA_REDACCION_TESIS.md`; fuentes = sin lectura de Luis salvo que se diga lo contrario (regla del proyecto: no son respaldo final hasta leerlas); todo es **CANDIDATO hasta que lo vea la asesora**.
Material de apoyo: `VACIOS_Y_RELEVANCIA_CLINICA.md`, `investigacion/01-03`, `PLATAFORMA_INSTRUMENTADA_USO.md`.

---

## 1. Título (candidato)
**Diseño y validación del control de fuerza en tres ejes de un simulador de marcha para comparar prótesis transtibiales bajo carga de marcha sana** (24 palabras)
- Guía §7.1: empieza con sustantivo de acción ("Diseño y validación", tendencia 2024-25), objeto técnico + finalidad "para…" + marca biomédica (prótesis transtibiales), sin siglas ni marcas.
- Reemplaza al del 2026-10-28 (decía "presión plantar", superado por el CoP el 11-19).

## 2. Pregunta de investigación (candidata, NO cerrada)
> **¿Qué diferencias en el movimiento de la pierna, la cuasi-rigidez del tobillo y la energía devuelta presentan un pie protésico transtibial articulado y uno de fibra de carbono cuando un simulador de marcha, con sus tres ejes en lazo cerrado, les impone la misma fuerza de reacción del suelo y el mismo avance del centro de presión de una marcha sana?**

- **Idea central:** si el simulador fija la carga (Fz, Fy y avance del CoP), lo único libre es cómo responde la prótesis → cada pie obliga a los ejes a moverse distinto: esa diferencia es el resultado biomédico.
- Checklist guía §2: es pregunta ✔ · relaciona variables (tipo de pie → descriptores mecánicos) ✔ · medible ✔ · una sola ✔ · se responde con las corridas de Luis, no con las prácticas ✔.
- **Idea a defender** (en lugar de hipótesis, guía §4): con la carga de marcha sana fijada por el control, las diferencias medidas en movimiento, rigidez y energía son atribuibles a la prótesis y no al ensayo.

## 3. Objetivos (candidatos)
**General:** Evaluar las diferencias en el comportamiento mecánico de un pie protésico transtibial articulado y uno de fibra de carbono bajo la carga de una marcha sana, impuesta por un simulador de marcha con control en lazo cerrado de sus tres ejes.

**Específicos:**
1. **Desarrollar** el control integrado en lazo cerrado de los tres ejes del simulador (fuerza vertical, fuerza horizontal y avance del centro de presión), con ganancia adaptada a la rigidez de cada prótesis.
2. **Validar** que la carga impuesta reproduce la de una marcha sana dentro de la variabilidad paso a paso de una persona sana (criterio propuesto en §5) en cada prótesis ensayada.
3. **Caracterizar** en cada pie el movimiento de la pierna, la cuasi-rigidez del tobillo, la forma de rodadura y la energía absorbida y devuelta bajo esa carga.
4. **Comparar** esos descriptores entre los pies, separando las diferencias que superan la repetibilidad del ensayo (mínimo cambio detectable por pie).

Checklist guía §3: infinitivo ✔ · general responde la pregunta ✔ · específicos = metas, no actividades ✔ · ≤ 4 ✔ · en conjunto bastan ✔ · medibles ✔.

## 4. Qué se mide y de dónde sale (sin sensores nuevos obligatorios)
| Resultado | Cómo se obtiene | Uso clínico |
|---|---|---|
| Movimiento de la pierna | ángulo sagital y descenso vertical que el lazo necesita para lograr la carga | cuánto movimiento le exige cada pie al usuario |
| Cuasi-rigidez del tobillo | momento (fuerza × brazo al CoP) vs ángulo sagital | descriptor para clasificar/prescribir pies |
| Forma de rodadura | CoP en el marco de la pierna, arco circular ajustado (umbral 150 N o 10 % Fmáx) | alineación de la prótesis |
| Energía absorbida/devuelta | P = Fy·vy + Fz·vz + M·ω (Takahashi 2012, doi 10.1016/j.jbiomech.2012.08.017), integrada en el apoyo | distingue pie que almacena y devuelve energía |
Validación del cálculo de energía: bloque rígido de suela curva → P ≈ 0.

## 5. Criterio de "misma carga" (propuesta, calculada 2026-11-25)
Variabilidad paso a paso de la MISMA persona sana, Fukuchi 2018 (24 jóvenes, cinta, doi 10.7717/peerj.4640), sobre toda la curva de Fz:
- 0,50 m/s: RMSE de un paso vs la media de su sujeto **5,1 %BW** (p25 4,6 · p75 5,5); r **0,991** (p25 0,986); DE de picos 1,8–2,3 %BW; entre personas 4,1 %BW.
- 1,24 m/s: 4,0 %BW; r 0,990.
- **Propuesta:** RMSE ≤ 5 %BW y r ≥ 0,986. Lazo actual: 3 ejes 80 kg 4,4 %BW / r 0,988 (cumple, justo); solo Y mejorado 1,45 %BW / r 0,999.
- Limitación: el ruido propio de la cinta no está separado (podría inflar la cifra).
- **Métrica (2026-11-26): RMSE en %BW** + r complementario; RMSE en N descartado (crece con la carga), %pico/%rango dependen de la forma de la curva. La curva de la interfaz es Gutenberg 1,40 m/s → la referencia de velocidad más cercana en Fukuchi es 1,24 m/s (4,0 %BW mediana, 4,96 p75). Detalle: `reportes/2026-11-26_analisis_normalizacion_rmse.md`.
- Script: `control/referencia_grf/variabilidad_paso_a_paso_fukuchi.py` (+ `.txt`, `.csv`).
- Para "misma carga entre pies" (equivalencia): TOST con margen fijado antes (candidato: MDC de la plataforma ≈ 26–33 N) + SPM para ver dónde difieren las curvas (`investigacion/01`).

## 6. Cómo apoya cada práctica DPB4 a la tesis (versión final, 2026-11-27)
La pregunta NO depende de las prácticas (principio de Luis, 2026-11-25): Luis integra, hace las corridas finales y el análisis; cada práctica aporta una pieza que la tesis usa. **4 prácticas** (se evaluó partir P1 en 2 para sumar un 5.º practicante; Luis decidió quedarse en 4 y dar él más atención directa a P1).

| Práctica | Entrega | Parte de la tesis que apoya | Enfoque biomédico |
|---|---|---|---|
| **P1 — Adquisición multicanal (AD7606) + lazos de Fy y CoP** | Driver AD7606 (6 canales del AMTI); lazo de Fy y lazo sagital guiado por CoP, **cada uno validado por separado**; Fz sigue en su cadena actual hasta validar el AD7606 lado a lado; **entregar ambos lazos en un estado que facilite la integración de los 3 ejes** (código/datos documentados y listos para ensamblar) | **OE1** (2 de los 3 lazos; Luis integra los 3 y corre las pruebas finales) y **OE3** | El avance del CoP (talón→antepié) y la fuerza de frenado/propulsión horizontal son los descriptores que distinguen una marcha protésica deficiente (menor propulsión, inestabilidad) de una sana — no son solo variables de control, son el dato clínico |

**Aclarado (Luis, 2026-11-27): el practicante de P1 NO integra los 3 ejes — su último objetivo es dejar sus 2 lazos listos/documentados para que Luis haga esa integración formal.** Objetivo específico de P1 a agregar en el Word: "(5) Entregar ambos lazos (código, datos, documentación) en un estado que permita su integración directa con el lazo de Fz existente" — no "integrar los 3 ejes", eso es tarea de Luis.
| **P2 — Pie de calibración + rigidez k(F)** | k(F) en barrido continuo (talón a punta) de **exactamente 1 pie articulado + 1 de fibra de carbono**, validado contra un pie de calibración de rigidez conocida | **OE1** (ganancia adaptada a la rigidez) y **OE3/OE4** | Hoy la prescripción clínica de pies se hace sin un criterio objetivo de rigidez comparable (Cochrane CD003978); P2 entrega ese criterio |
| **P3 — Activa: integración en apoyo, solo piso plano** | Sincronía por fase con el simulador (usa Fz, ya de Luis); momento/trabajo del tobillo en el despegue vs. marcha sana pública. **Rampas/escaleras descartadas; sin balanceo; sin mejora del servo transversal** (se deja como limitación documentada, no como entregable) | **Caso adicional** (no entra a la pregunta principal) | Fidelidad del push-off: si el actuador se retrasa ahí, se pierde la ventaja teórica de la prótesis activa frente a una pasiva |
| **P4 — Activa: rediseño mecánico/electrónico** | Adaptador inferior del pie; reducción de masa 5→2-3,5 kg; **documento de especificación del actuador real necesario** (fuerza, velocidad, tamaño, realimentación — NO adquisición ni fabricación, brief para una futura tesis de mecatrónica/electrónica); sensor de corriente (ACS712) como entregable opcional si alcanza el tiempo. Incluye traducir la fuerza del actuador a un peso de paciente equivalente (ver nota de ventaja mecánica abajo) | **Caso adicional** (habilita la carga de prueba de P3) | Representatividad del "paciente simulado": a qué peso corporal corresponde la prueba con el actuador disponible, sin prometer 80-90 kg |

**✅ (2026-11-27) Interfaz de la activa VERIFICADA en código (`gait_provider.py`, repo de Gonzalo, solo lectura) — ya no es pendiente de terceros:** la ÚNICA entrada externa es un entero en el tópico ROS2 `/locomotion_mode` (0 = pulso de sincronización de 0.6 s + 4 s de reposo; 1-5 = un modo de marcha — caminata, rampa subida/bajada, escalera subida/bajada —, cada uno reproduce su trayectoria angular ya precargada). La velocidad de reproducción es `TIME_STRETCH_FACTOR = 6.0`, **fija en el código** (línea 11), no un parámetro en caliente — cambiarla es editar esa constante en una COPIA local (misma regla que con el servo: es código de la tesis de Gonzalo, no se toca el repo original).

**Ventaja mecánica del 2SPU-1RU, explicado simple (para el documento de P4):** el mecanismo de la activa tiene 2 actuadores lineales que empujan/jalan una plataforma, y ese movimiento genera el giro del tobillo. La fuerza que da el actuador en línea recta (Newtons) NO es la misma fuerza que el tobillo aguanta contra el suelo (el GRF) — hay una relación geométrica entre ambas, como una palanca: el mismo empuje del actuador da más o menos fuerza en el tobillo según el ángulo del momento y las dimensiones del mecanismo ("el triángulo": `dA, dB, h, e, f`). Esa relación es la "ventaja mecánica". **Por qué hace falta calcularla:** hoy el plan dice "se capa el GRF de prueba a lo que el actuador soporta" sin un número; con este cálculo (a partir de `inverse_kinematics_true.py`, ya disponible) P4 puede entregar algo concreto — ej. "el actuador recomendado sostiene X N en el tobillo, equivalente a Y kg de paciente simulado, en tal rango de ángulos" — en vez de quedarse en la idea sin cifra.
| **Alessandro (plataforma instrumentada, dic 2026, NO es una de las 4)** | Ángulo, desplazamiento y fuerza en la interfaz encaje–muñón | **OE3** (observación, no se controla) | — |

**Restricciones ya cerradas que valen para P3 y P4:** no tocar los 5 parámetros geométricos del mecanismo de la activa (`dA, dB, h, e, f` — "el triángulo" de Gonzalo) sin rehacer su cinemática inversa; P4 no instala el actuador físicamente, solo lo especifica; la escala de tiempo de P3 queda acotada por el actuador FÍSICO presente (222 N/21,1 mm/s), no por lo que recomiende P4.

### Publicaciones candidatas (artículo para congreso internacional, logística a cargo del laboratorio)
Cada practicante redacta solo su sección; Luis es autor de correspondencia (framing, estado del arte, envío). Falta decidir conferencia/fecha objetivo antes de comprometer un cronograma de envío — el cierre técnico (~fines de abril) deja un colchón corto contra la entrega teórica de marzo-mayo 2027, así que el paper es objetivo secundario, después del entregable técnico de cada práctica, no parte del núcleo de horas.

- **Paper A (insignia): Fz (ya cerrado por Luis) + P1 (Fy, CoP).** "Control en lazo cerrado de la fuerza de reacción del suelo y el centro de presión en un simulador de marcha" — cubre el vacío ya identificado (nadie combina lazo cerrado de GRF con plataforma real tipo AMTI).
- **Paper B (independiente): P2.** "Validación de un protocolo continuo de rigidez para prótesis transtibiales con un pie de calibración de rigidez conocida" — autocontenido, no depende de que A o C cierren.
- **Paper C (conjunto): P3 + P4.** "Viabilidad de integración de una prótesis activa a un simulador de marcha y requerimientos de actuador" — cubre el vacío de sincronizar el controlador propio de una activa con un banco externo, incluso si el resultado es parcial/negativo (documentar por qué no alcanza y qué se necesitaría).

**Decisión de alcance (Claude, por delegación de Luis 2026-11-25): la activa (P3/P4) NO entra en la pregunta principal de la tesis; es caso adicional.** Motivo: si entra a la pregunta, la tesis dependería de que P3 funcione (contra el principio de que ninguna práctica puede ser la respuesta), y la activa es un prototipo con repetibilidad desconocida que inyecta energía (la comparación bajo el mismo objetivo de marcha sana es discutible). Si P3 entrega la sincronización, se reporta como extensión (pasivas vs. activa), reforzando el aporte biomédico sin poner en riesgo la tesis principal.

**Integración de la activa — contexto (detalle completo: `investigacion/04_control_protesis_activas_e_integracion.md`):** ninguna prótesis de pierna comercial usa EMG; se controlan con sus propios sensores. La activa del lab se mueve con trayectorias predefinidas, sin sensor que las actualice. Integración real = el simulador impone carga/movimiento y la prótesis detecta su fase sola; señal de sincronía desde la RPi como respaldo. El simulador NO puede hacer apoyo y balanceo seguidos (restricción de espacio) — motivo adicional, aparte del de alcance de horas, para que P3 quede solo en apoyo.

## 7. Justificación (5 criterios de Sampieri, guía §5)
- **Conveniencia:** da un ensayo preclínico repetible con la carga de una persona sana, hoy inexistente para comparar pies.
- **Relevancia social:** Perú — 485 211 personas con dificultad para caminar (Censo 2017); ≈ 8000 amputaciones por diabetes al año (MINSA); en el INR la causa no traumática es 54,7 % y el nivel transtibial es el único predictor de rehabilitación exitosa (Quezada 2024). OMS: solo 5–15 % de quienes necesitan prótesis en países de ingresos bajos y medios la consiguen.
- **Implicaciones prácticas:** la prescripción de pies se hace sin evidencia objetiva (Cochrane CD003978; Highsmith 2016); elegir entre pie barato y caro es una decisión real → la tesis da datos mecánicos comparables (NO beneficio clínico: eso exige estudios con pacientes).
- **Valor teórico (vacío):** no se halló comparación articulado vs fibra de carbono en el mismo banco con la misma carga impuesta; el antecedente más cercano (Herlihy 2026, doi 10.1088/1873-4030/ae8544) trabaja en lazo abierto con una sola configuración.
- **Utilidad metodológica:** el método de ensayo cambia la rigidez medida hasta 24 % y 2 de 5 métodos no distinguen pies (Starker 2026, doi 10.1088/1873-4030/ae33ba) → un ensayo con carga de marcha sana impuesta en lazo cerrado y adaptado a la rigidez es un aporte de método. Novedad parcial: la ganancia adaptada a la rigidez ya existe en otros bancos (Hinton 1997; patente US 11,691,280; Yang 2020 con ILC — **leer Yang 2020 completo, prioridad**).

## 8. Alcance y limitaciones
- Plano sagital (lo coronal de los pies no se capta: Womac/Neptune/Klute).
- Velocidad reducida (×10): resultados "cuasi-dinámicos"; la rigidez puede cambiar ≈ +9,8 % de 0,5 a 3 Hz (Lecomte 2022); la forma de rodadura tolera marcha lenta (Hansen 2000). Se declara.
- 2 pies pasivos (articulado y fibra de carbono; modelos por confirmar) + la activa como caso adicional. Unidad de análisis = el pie: no se generaliza a "todos los pies"; se usa CV, SEM y MDC por pie (ICC no tiene sentido con 2–3 pies).
- Pasos por condición: n ≈ (1,96/k)² → 16 pasos para k = 0,5; 62 para k = 0,25.
- Carga: sujeto de 80 kg; pico máximo 1500 N; sin fatiga/durabilidad.
- Curva objetivo: base pública de marcha sana; **el lazo abierto no se usa en la tesis** (decisión 2026-11-25).

## 9. Viabilidad y calendario
- Ya logrado: lazo de Fz cerrado con prótesis real, 40–80 kg, 31/31 pisadas con 3 ejes (Y cerrado, X y sagital abiertos), 80 kg 4,4 %BW / r 0,988.
- Luis cierra el lazo vertical con umbral fijo ≈ diciembre 2026.
- **Marzo–mayo 2027:** entrega teórica (diseño + simulación + metodología, sin datos reales).
- **2.º semestre 2027:** pruebas de la tesis (pruebas previas permitidas antes).

## 10. Metodología (esqueleto)
1. Modelo y simulación del lazo de 3 ejes (planta con k(F) medido, latencia medida ≈ 22–30 ms efectiva).
2. Implementación e integración de los 3 lazos (insumos: prácticas 1 y 2).
3. Validación de la carga contra la variabilidad paso a paso (§5), por pie.
4. Corridas finales: cada pie, ≥ 16 pasos por condición, mismo protocolo; cálculo de descriptores (§4).
5. Comparación entre pies (MDC, TOST, SPM).

---

## Registro de decisiones (tesis y prácticas)
- **2026-10-28** Título "Control en lazo cerrado de los tres ejes… presión plantar…" → superado (ver 2026-11-25).
- **2026-11-19** Orden de los lazos Fz → Fy → sagital guiado por CoP del AMTI (reemplaza la plantilla de presión).
- **2026-11-25** 3 prácticas DPB4, sin 4.ª: (1) multicanal + Fy/CoP, (2) pie patrón + k(F), (3) activa + sincronización. Luis guía de manera informal (no puede ser asesor formal) y ejecuta las corridas finales.
- **2026-11-25** Principio: pregunta y objetivos no pueden depender de que las prácticas den la respuesta.
- **2026-11-25** El lazo abierto no se usa en la tesis por ahora (trayectorias experimentales no documentadas).
- **2026-11-25** Practicante actual = Alessandro (Félix Tello): plataforma instrumentada (ángulo, desplazamiento, fuerza en la interfaz).
- **2026-11-25** Prótesis pasivas disponibles: pie articulado y pie de fibra de carbono (+ posiblemente la activa).
- **2026-11-25** Calendario: teoría mar–may 2027; pruebas 2.º semestre 2027.
- **2026-11-25** La pregunta no se cierra: abierta a modificación según la investigación.
- **2026-11-25** Luis: la pregunta se había ido al control → se reorienta a lo biomédico; los resultados salen del movimiento multieje en lazo cerrado (no de un CoP solo registrado en NetForce, que no entra al lazo).
- **2026-11-25** Práctica 3 = caso adicional, fuera de la pregunta (motivo en §6).
- **2026-11-25** Umbral de misma carga calculado (§5): propuesta, falta decisión de Luis/asesora.
- **2026-11-25** Título candidato nuevo (§1).
- **2026-11-26** Práctica 3 (integración de la activa) es INDEPENDIENTE de la tesis: la tesis no la toca por ahora; si se alcanza, entra al final como última prueba (caso adicional). Integración "por la física" como idea final; **EMG no se descarta: es línea en investigación, idea futura** (`investigacion/04`).
- **2026-11-26** Próxima sesión RPi = solo cerrar Fz (Y cerrado, X y sagital abiertos, 80 kg, repetible bajo el umbral). Fy, sagital por CoP y AD7606 quedan para después, en la práctica 1.
- **2026-11-26** Docs de la activa leídos (`investigacion/04` §3b-ter): ROS 2 en RPi 5, PID de posición sobre CSV, única entrada `/locomotion_mode`; actuadores de 222 N (riesgo con la carga). Se evaluó partir la P3 en dos (integración/balanceo y apoyo bajo carga). **Luis: la P3 queda como UNA sola práctica por ahora; se divide solo si se vuelve necesario.** → **SUPERADO el mismo día: P3 se divide en P3 (software/medición) y P4 (mecánica/electrónica) → 4 prácticas: P1 lazos Fy/CoP, P2 pie de calibración, P3 y P4 activa (§6).**
- **2026-11-26** Regla: las prácticas viven SOLO en §6 de este archivo; `investigacion/04` es apoyo de investigación (p. ej. actuadores de la P4), no define prácticas. Alessandro no es una de las 4 prácticas.

## Pendiente
- **Luis:** decidir umbral (§5); confirmar la pregunta y objetivos; conseguir Yang 2020 completo (biblioteca PUCP: SEPRODOC no menciona tesis → preguntar a biblio@pucp.edu.pe), ISO 22675:2024, documento IETSI EsSalud, lineamientos oficiales de tesis FCI; modelos de los pies; datos de la activa; specs de la plataforma de Alessandro; rol de Máximo; cotizaciones en Perú; leer las fuentes.
- **Luis → Claude: compartir la información de la prótesis activa del lab** (cómo detecta las fases, qué sensores y umbrales, si acepta señal externa, planes de EMG; preguntas en `investigacion/04` §4).
- **✅ (2026-11-26) Notion de la activa LEÍDO (Chrome, cuenta de Luis con acceso):** arquitectura real en 4 nodos ROS 2 modulares (`gait_provider`→`trajectory_calculator`→`trajectory_executor`→`ankle_pid_controller`); el punto de enganche para la integración ya existe (reemplazar `gait_provider` sin tocar el resto). Detalle: `investigacion/04` §3b-quater. **Confirmado por Luis (2026-11-26): Gonzalo NUNCA la probó con carga axial real** (no es que faltara leerlo). **La prótesis armada SÍ se entrega** (físico, aparte de los documentos). **✅ (2026-11-26) Código recibido y revisado: repo privado `github.com/GonzaloOshiro/ankle_2SPU1RU` (invitación aceptada, Luis ya tiene push). 🛑 REGLA (Luis): es SOLO para ver y analizar — nunca escribir/commitear/pushear ahí, aunque haya permiso.** Clonado y leídos `gait_provider.py` y `ankle_pid_controller.py`. Hallazgos clave: (1) el `gait_provider` en producción NO lee Excel: carga 5 CSV precalculados (uno por modo), la única entrada externa es `/locomotion_mode` (entero); (2) **ya existe un "Modo 0" de sincronización**: un pulso corto (8° sagital) + reposo largo, pensado para alinear su propio registro con un IMU externo por reloj no compartido — es el mecanismo que necesitaríamos reusar/ampliar para sincronizar con el simulador; (3) escala de tiempo fija en código: `TIME_STRETCH_FACTOR = 6.0`; (4) PID+FF por actuador con zona muerta y saturación ±100 PWM, ganancias como parámetros ROS 2 (cambiables sin recompilar). Detalle: `investigacion/04` §3b-quinquies (pendiente de escribir con más detalle si se necesita).
- **Pendiente transversal (sin decidir): rol de la plataforma de Alessandro** (ángulo, fuerza axial) en cada frente — tesis principal, P2 con pasivas, P3 con la activa; cualquier prótesis se acopla ahí.
- **Luis (2026-11-26):** (1) enviar a los practicantes el mensaje con las 4 prácticas (P1–P4, §6) (texto final en el chat del 2026-11-26) y recoger su elección; (2) dar OK al objetivo "Fz cerrado" del protocolo RPi §0 (umbral de trabajo 5 %BW / r ≥ 0,986, x10, R6 obligatorio); (3) decidir los archivos vacíos sueltos `AIN1`, `NO`, `k_real` en la raíz del repo (borrar o no); (4) decidir si se fusiona la rama remota `claude/pensive-thompson-jitkz1` (11-21, ficha y análisis del pie de fibra de carbono, carpeta `practicas/`); (5) fecha de inicio de las prácticas, si quiere que se anote.
- **⏸ Próxima sesión con la RPi (sin acceso a la RPi por unos días, Luis 2026-11-26; al volver: `git pull` en la RPi y decir «continuar», que lee `INICIO_SESION_SIGUIENTE.md` → protocolo):** solo cerrar Fz siguiendo `reportes/2026-11-20_protocolo_proxima_sesion_rpi.md` §0.
- **Asesora:** título, pregunta, objetivos.
- **Abierto:** curva objetivo (Gutenberg vs Fukuchi a ×10); margen Δ de equivalencia; objetivo secundario de velocidad ×10 (opcional).
- **Siguiente:** redactar las 3 prácticas en el formato Word de DPB4, alineadas con §6.
- Enlaces biblioteca PUCP: https://biblioteca.pucp.edu.pe (bases con credenciales del campus virtual) · catálogo https://pucp.ent.sirsi.net/client/es_ES/campus/search/advanced · SEPRODOC https://biblioteca.pucp.edu.pe/servicios/provision-documentos (tesistas, 10 artículos/año, pedidos hasta 14-dic-2026).
