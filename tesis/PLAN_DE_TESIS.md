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

## Pendiente
- **Luis:** decidir umbral (§5); confirmar la pregunta y objetivos; conseguir Yang 2020 completo (biblioteca PUCP: SEPRODOC no menciona tesis → preguntar a biblio@pucp.edu.pe), ISO 22675:2024, documento IETSI EsSalud, lineamientos oficiales de tesis FCI; modelos de los pies; datos de la activa; specs de la plataforma de Alessandro; rol de Máximo; cotizaciones en Perú; leer las fuentes.
- **Luis → Claude: compartir la información de la prótesis activa del lab** (cómo detecta las fases, qué sensores y umbrales, si acepta señal externa, planes de EMG; preguntas en `investigacion/04` §4).
- **Asesora:** título, pregunta, objetivos.
- **Abierto:** curva objetivo (Gutenberg vs Fukuchi a ×10); margen Δ de equivalencia; objetivo secundario de velocidad ×10 (opcional).
- **Siguiente:** redactar las 3 prácticas en el formato Word de DPB4, alineadas con §6.
- Enlaces biblioteca PUCP: https://biblioteca.pucp.edu.pe (bases con credenciales del campus virtual) · catálogo https://pucp.ent.sirsi.net/client/es_ES/campus/search/advanced · SEPRODOC https://biblioteca.pucp.edu.pe/servicios/provision-documentos (tesistas, 10 artículos/año, pedidos hasta 14-dic-2026).
