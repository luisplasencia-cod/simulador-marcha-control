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

## 6. Cómo apoya cada práctica DPB4 a la tesis
La pregunta NO depende de las prácticas (principio de Luis, 2026-11-25): Luis integra, hace las corridas finales y el análisis; cada práctica aporta una pieza que la tesis usa.
| Práctica | Entrega | Parte de la tesis que apoya |
|---|---|---|
| **1. Adquisición multicanal (AD7606) + lazos de Fy y CoP** | 6 canales del AMTI a la vez; lazos de fuerza horizontal y sagital guiado por CoP; GRF por eje vs bases públicas | **OE1** (2 de los 3 lazos que Luis integra) y **OE3** (canales para momento, rigidez, energía) |
| **2. Pie patrón + rigidez k(F) de las prótesis** | k(F) de cada pie pasivo con protocolo validado contra rigidez conocida | **OE1** (ganancia adaptada a la rigidez) y **OE3/OE4** (rigidez independiente para contrastar) |
| **3. Prótesis activa + sincronización con el simulador** | la activa operando dentro del simulador, su k medida | **Caso adicional** (ver decisión abajo): mismo protocolo, pasivas vs activa |
| **Alessandro (plataforma instrumentada, dic 2026)** | ángulo, desplazamiento y fuerza en la interfaz encaje–muñón | **OE3** (movimiento y energía medidos, no estimados de los pasos del motor); interfaz = observación |

**Títulos y objetivos candidatos (propuesta 2026-11-26, falta OK de Luis; base para el Word de DPB4):**
- **P1.** *Implementación de la adquisición multicanal y del control en lazo cerrado de la fuerza horizontal y del centro de presión de un simulador de marcha para prótesis transtibiales.* General: implementar la adquisición multicanal de la plataforma de fuerza y el control en lazo cerrado de Fy y del avance del CoP. OE: (1) adquirir a la vez los 6 canales (3 fuerzas, 3 momentos) y calcular el CoP en tiempo real; (2) desarrollar el lazo de Fy con avance siempre hacia adelante; (3) desarrollar el control sagital guiado por la progresión del CoP; (4) validar Fy y el CoP generados **cada uno por separado**, contra bases públicas de marcha sana. **Aclarado (Luis, 2026-11-26): el practicante desarrolla y valida cada lazo por separado; integrar los 3 ejes (Fz+Fy+sagital) a la vez en una sola corrida, y las corridas finales que cuentan como resultado de tesis, las ejecuta Luis** (mismo principio ya cerrado el 2026-11-25: la tesis no depende de que las prácticas den la respuesta final).
- **P2.** *Diseño de un pie patrón de rigidez conocida y validación de un protocolo para medir la rigidez de prótesis transtibiales en un simulador de marcha.* General: validar el protocolo k(F) con un pie patrón. OE: (1) diseñar y fabricar el pie patrón y verificar su rigidez en un ensayo independiente; (2) cuantificar el error del protocolo frente a esa rigidez; (3) medir k(F) de 2–3 prótesis pasivas en talón, planta y antepié, con su repetibilidad; (4) establecer la tabla de rigidez por prótesis que usa el lazo de control.
- **P3 (rehecha 2026-11-26 con datos de Luis + enfoque biomédico).** *Integración de una prótesis transtibial activa a un simulador de marcha para evaluar su función de tobillo en cada fase de la marcha.* General: evaluar si la activa reproduce la función del tobillo sano (empuje en el despegue, despeje del pie en el balanceo) integrándola al simulador con entradas sincronizadas por fase. OE: (1) caracterizar simulador y activa y las entradas que esta necesita (inicio, tiempo, fase); (2) implementar la entrega sincronizada por fase (apoyo y balanceo por separado) y el registro común prótesis–plataforma; (3) evaluar en el apoyo ángulo, momento, relación momento–ángulo y trabajo neto del tobillo en el despegue frente a una base pública de marcha sana que el practicante elige y justifica (datos propios solo si se registran documentados; no las trayectorias actuales del simulador); (4) evaluar en el balanceo el despeje del pie (dorsiflexión) frente al tobillo sano, y la sincronía y repetibilidad en ambas fases. Nota: el trabajo (∫M dθ) no depende de la escala de tiempo; la potencia pico sí (a x10 sale 10× menor) → se compara trabajo, la potencia se reporta reescalada con la advertencia. El momento necesita el CoP: AD7606 de la P1 si está listo, si no, exportación de NetForce (solo observación, no entra a un lazo).
  - **Datos de Luis (2026-11-26):** el simulador NO puede hacer apoyo y balanceo seguidos (el espacio solo da para uno u otro) → se ensaya por fase. La activa del lab se mueve con **trayectorias predefinidas, sin sensor que las actualice** (no es máquina de estados; corrige lo anotado antes). Las entradas exactas que necesita: pendiente de la info del grupo. La comparación activa vs pasivas queda para Luis (última prueba de la tesis, si se alcanza).

**Decisión práctica 3 (Claude, por delegación de Luis 2026-11-25):** la activa NO entra en la pregunta; es un **caso adicional del alcance**. Motivo: si entra a la pregunta, la tesis dependería de que la práctica 3 funcione (contra el principio) y la activa es un prototipo (repetibilidad desconocida, inyecta energía → la comparación con el mismo objetivo de marcha sana es discutible). Si la práctica 3 entrega la sincronización, se ensaya con el mismo protocolo y se reporta como extensión (pasivas vs activa), lo que refuerza el aporte biomédico sin poner en riesgo la tesis.

**Integración de la activa (análisis 2026-11-26, `investigacion/04_control_protesis_activas_e_integracion.md`):** ninguna prótesis de pierna comercial usa EMG; se controlan con sus propios sensores (máquina de estados o variable de fase). Integración real = el simulador impone movimiento y carga y la prótesis detecta sus fases sola (nivel A); señal de sincronía desde la RPi como respaldo (nivel B). EMG emulado (nivel C): fuera de la práctica 3, idea futura. Riesgo: a x10 hay que reescalar los umbrales de velocidad y tiempo de su máquina de estados. Pendiente: confirmar con el grupo cómo controla hoy la activa. **Idea final (propuesta): integración "por la física"**, igual para cualquier activa: el simulador reproduce lo que sus sensores miden en una persona (carga, avance del CoP, ángulos, movimiento de la pierna). Faltan: fase de balanceo (hoy solo apoyo) y tiempo real (a x10 velocidades y tiempos salen 10× distintos; solo sirve con prótesis de umbrales ajustables). Detalle §3b del análisis 04.

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
- **2026-11-26** Docs de la activa leídos (`investigacion/04` §3b-ter): ROS 2 en RPi 5, PID de posición sobre CSV, única entrada `/locomotion_mode`; actuadores de 222 N (riesgo con la carga). Se evaluó partir la P3 en dos (integración/balanceo y apoyo bajo carga). **Luis: la P3 queda como UNA sola práctica por ahora; se divide solo si se vuelve necesario.**

## Pendiente
- **Luis:** decidir umbral (§5); confirmar la pregunta y objetivos; conseguir Yang 2020 completo (biblioteca PUCP: SEPRODOC no menciona tesis → preguntar a biblio@pucp.edu.pe), ISO 22675:2024, documento IETSI EsSalud, lineamientos oficiales de tesis FCI; modelos de los pies; datos de la activa; specs de la plataforma de Alessandro; rol de Máximo; cotizaciones en Perú; leer las fuentes.
- **Luis → Claude: compartir la información de la prótesis activa del lab** (cómo detecta las fases, qué sensores y umbrales, si acepta señal externa, planes de EMG; preguntas en `investigacion/04` §4).
- **✅ (2026-11-26) Notion de la activa LEÍDO (Chrome, cuenta de Luis con acceso):** arquitectura real en 4 nodos ROS 2 modulares (`gait_provider`→`trajectory_calculator`→`trajectory_executor`→`ankle_pid_controller`); el punto de enganche para la integración ya existe (reemplazar `gait_provider` sin tocar el resto). Detalle: `investigacion/04` §3b-quater. **Confirmado por Luis (2026-11-26): Gonzalo NUNCA la probó con carga axial real** (no es que faltara leerlo). **La prótesis armada SÍ se entrega** (físico, aparte de los documentos). **✅ (2026-11-26) Código recibido y revisado: repo privado `github.com/GonzaloOshiro/ankle_2SPU1RU` (invitación aceptada, Luis ya tiene push). 🛑 REGLA (Luis): es SOLO para ver y analizar — nunca escribir/commitear/pushear ahí, aunque haya permiso.** Clonado y leídos `gait_provider.py` y `ankle_pid_controller.py`. Hallazgos clave: (1) el `gait_provider` en producción NO lee Excel: carga 5 CSV precalculados (uno por modo), la única entrada externa es `/locomotion_mode` (entero); (2) **ya existe un "Modo 0" de sincronización**: un pulso corto (8° sagital) + reposo largo, pensado para alinear su propio registro con un IMU externo por reloj no compartido — es el mecanismo que necesitaríamos reusar/ampliar para sincronizar con el simulador; (3) escala de tiempo fija en código: `TIME_STRETCH_FACTOR = 6.0`; (4) PID+FF por actuador con zona muerta y saturación ±100 PWM, ganancias como parámetros ROS 2 (cambiables sin recompilar). Detalle: `investigacion/04` §3b-quinquies (pendiente de escribir con más detalle si se necesita).
- **(2026-11-26) DECISIÓN FINAL (Luis): la P3 se divide en P3 y P4 (NO "P3a/P3b" — cada una completa e independiente, 2 practicantes por lado), cada una con su propio enfoque biomédico y visión de publicación (o conjunta).** Detalle completo (objetivos, medición, instrumentación): `investigacion/04` §3b-septies.
  - **4 focos del equipo de la prótesis (2026-11-26, repartidos entre P3/P4):** (1) adaptador del pie protésico (abajo, no el piramidal de arriba), (2) precisión del servo del plano transversal (hoy error 8-12°), (3) reducir masa de ~5 kg a 2-3.5 kg, (4) actuadores lineales comerciales de mejor densidad energética/fuerza/peso (hoy 222 N, insuficiente para ~80 kg).
  - **P2 (renombrada "pie patrón"→"pie de calibración"):** protocolo k(F) mejorado de 3 ángulos fijos a barrido continuo de talón a punta (toda la fase de apoyo), no una tarea aparte.
  - **P3 — software + control + medición biomecánica, INDEPENDIENTE de la etapa de control del simulador:** traducir las 3 señales del simulador (cerradas o en lazo abierto, lo que haya en ese momento) a las 3 trayectorias angulares de la prótesis; sincronía e interfaz (no existe hoy); mejorar/validar precisión del plano transversal (foco 2); en el apoyo, momento y trabajo del tobillo por dinámica inversa con Fz/Fy/CoP del PROPIO simulador (mismo método ya definido en el proyecto — la tesis en sí aún no se ha hecho —, NO desde el sensor de Alessandro que solo da fuerza axial como comprobación cruzada), comparado con Fukuchi 2018/Gutenberg 2021; en el balanceo, sin fuerza de reacción no hay momento, solo se compara el ángulo ya sensado por el simulador. El "chiste" de usar el mismo método: permite comparar activa vs. pasivas bajo igual medición. Validar ángulos propios del tobillo = ya encargado a otra persona, fuera de alcance.
  - **P4 — rediseño mecánico, 4 objetivos:** (1) adaptador INFERIOR del pie protésico (foco 1, corregido); (2) reducir masa a 2-3.5 kg con enfoque biomédico de masa protésica y gasto energético (foco 3, Zelik 2011/Childers & Takahashi 2018); (3) **comparar actuadores COMERCIALES** (foco 4, no fabricar — entregable garantizado es la comparación/selección, conseguirlo es adicional, fabricar a medida solo si nada comercial cumple); (4) **sensor de corriente (ACS712, en la placa electrónica, no pesa en la estructura) como PRUEBA DE ACEPTACIÓN del actuador elegido en (3)** — calibrado en banco con pesas conocidas (NO con el simulador, que influye mutuamente con la prótesis y no da una carga limpia). Análisis completo de por qué se descartó y luego se reincorporó: `investigacion/04` §3b-septies punto (5).
  - **Pendiente transversal (sin decidir): rol de la plataforma de Alessandro** (ángulo, fuerza axial) en cada frente — tesis principal, P2 con pasivas, P3 con la activa; cualquier prótesis se acopla ahí.
- **Luis (2026-11-26):** (1) enviar a los practicantes el mensaje con las 3 prácticas (texto final en el chat del 2026-11-26) y recoger su elección; (2) dar OK al objetivo "Fz cerrado" del protocolo RPi §0 (umbral de trabajo 5 %BW / r ≥ 0,986, x10, R6 obligatorio); (3) decidir los archivos vacíos sueltos `AIN1`, `NO`, `k_real` en la raíz del repo (borrar o no); (4) decidir si se fusiona la rama remota `claude/pensive-thompson-jitkz1` (11-21, ficha y análisis del pie de fibra de carbono, carpeta `practicas/`); (5) fecha de inicio de las prácticas, si quiere que se anote.
- **⏸ Próxima sesión con la RPi (sin acceso a la RPi por unos días, Luis 2026-11-26; al volver: `git pull` en la RPi y decir «continuar», que lee `INICIO_SESION_SIGUIENTE.md` → protocolo):** solo cerrar Fz siguiendo `reportes/2026-11-20_protocolo_proxima_sesion_rpi.md` §0.
- **Asesora:** título, pregunta, objetivos.
- **Abierto:** curva objetivo (Gutenberg vs Fukuchi a ×10); margen Δ de equivalencia; objetivo secundario de velocidad ×10 (opcional).
- **Siguiente:** redactar las 3 prácticas en el formato Word de DPB4, alineadas con §6.
- Enlaces biblioteca PUCP: https://biblioteca.pucp.edu.pe (bases con credenciales del campus virtual) · catálogo https://pucp.ent.sirsi.net/client/es_ES/campus/search/advanced · SEPRODOC https://biblioteca.pucp.edu.pe/servicios/provision-documentos (tesistas, 10 artículos/año, pedidos hasta 14-dic-2026).
