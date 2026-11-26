# 02 — Novedad del control adaptado a la rigidez y efecto de ensayar 10× más lento

Búsqueda web del 2026-11-25. Complementa `tesis/VACIOS_Y_RELEVANCIA_CLINICA.md` (no repite Herlihy 2026 como lazo abierto, Aubin 2012 como difuso ni Insam 2021; aquí solo se agregan datos nuevos de esos trabajos).

**Etiquetas:** [leí texto/abstract] = abrí el texto completo, una parte o el abstract. [solo resultado del buscador] = el dato sale de un resumen del buscador; no lo abrí. **Ninguna fuente está leída por Luis**: según la regla del proyecto, ninguna es respaldo final todavía. "Inferencia" = conclusión mía, no de la fuente.

---

## A. ¿Es nuevo un control de fuerza que se adapta a la rigidez del espécimen?

### A1. Antecedentes más cercanos

| # | Trabajo | Qué hace | En qué se parece | En qué se diferencia | Etiqueta |
|---|---|---|---|---|---|
| 1 | **Hinton 1997**, Instron, ASTM STP 1303, doi 10.1520/STP11544S | PID adaptativo en máquinas de ensayo de materiales. Ajusta los términos del PID todo el tiempo según la rigidez medida en tiempo real. En fatiga, cuando la rigidez cambia de golpe en cada inversión, **recuerda la rigidez del ciclo anterior**. | Es casi la misma idea: ganancia según rigidez medida, más memoria entre ciclos (parecido a ganancia programada + ILC). | Probetas de material, no prótesis. No impone una curva de marcha. | [leí texto/abstract] |
| 2 | **Patentes Instron** US 5,511,431 (estimador de rigidez que corrige la ganancia) y US 8,151,650 "Stiffness Based Tuning" (calcula todas las ganancias de un solo parámetro de rigidez, medido con una rampa en zona elástica) | Ajuste de ganancias por rigidez del espécimen, comercial. | Igual principio. Además, la rampa de medición se parece a la precarga del estimador de k propuesto. | Ajuste antes del ensayo (8,151,650), no durante la pisada. | [solo resultado del buscador] |
| 3 | **Cleveland Clinic, patente US 11,691,280 B2** (Colbrunn, Nagle, Gillespie; prioridad 2020, concedida 2023) | Control híbrido fuerza/posición en robot KUKA para columna. La rigidez de la columna es no lineal: una ganancia buena en zona rígida es lenta en zona blanda, y una buena en zona blanda desestabiliza en zona rígida. Cambian la ganancia proporcional durante la trayectoria según la zona de rigidez. Mencionan como opción calcular la rigidez del entorno en tiempo real. | **Es el mismo problema que el de la tesis** (oscilación con k alto, lentitud con k bajo) y la misma solución (ganancia por zona de rigidez). | Columna cadavérica, no prótesis ni GRF de marcha. No hallé resultados publicados con números. | [leí texto/abstract] (parte del texto de la patente) |
| 4 | **Bell et al. 2013**, J Biomech 46(10):1663, doi 10.1016/j.jbiomech.2013.04.007 | Control "híbrido" en robot para columna que se adapta a la respuesta carga-desplazamiento del espécimen. | Se adapta al espécimen. | Momentos puros en columna; no curva de GRF. | [leí texto/abstract] |
| 5 | **Aubin, Whittaker & Ledoux 2012**, IEEE T-RO 28(1):246, doi 10.1109/TRO.2011.2164958 | Dato nuevo para la tesis: las funciones de pertenencia del controlador difuso se diseñaron **no lineales a propósito para acomodar la rigidez no lineal del pie cadavérico** (error grande → asumen zona blanda → corrección grande; error chico → zona rígida → corrección chica). Esa parte es **iterativa entre pisadas**, no en tiempo real. Error final de vGRF 5.6 %BW (antes, por prueba y error, 30 %BW). | Considera la rigidez no lineal del espécimen al dar la ganancia. | La rigidez **no se mide**: se supone a partir del tamaño del error. La regla es fija, no se ajusta a cada pie. Pie cadavérico, no prótesis. | [leí texto/abstract] (texto completo) |
| 6 | **Aubin, Cowley & Ledoux 2008**, IEEE TBME 55(3):1237, doi 10.1109/TBME.2007.908072 | ILC proporcional para la vGRF, con **pie protésico**, robot paralelo de 6 GDL, apoyo de 1.5 s. Los resúmenes dan cifras distintas: 35 N RMS tras 6 iteraciones, o 78.7 → 9.4 N. Sin verificar. | ILC de vGRF con prótesis. | Una sola prótesis. No adapta la ganancia a la rigidez (según los resúmenes). | [solo resultado del buscador] |
| 7 | **Yang 2020**, tesis EngD, Univ. of Bath (dir. Iravani, Plummer, Pan), https://researchportal.bath.ac.uk/en/studentTheses/development-of-a-gait-simulator-for-testing-lower-limb-prostheses/ | Simulador hidráulico: un robot de pierna con pie protésico persigue la GRF de una persona. Usa "Extended ILC" (EILC). Validado en suelo fijo y móvil, con **tobillos pasivos y activos**. Detectó cambios chicos de ajuste en la prótesis. | **Es el antecedente más cercano al conjunto de la tesis** (GRF en lazo cerrado + prótesis pasivas y activas). No estaba en `VACIOS_...md`. | El abstract no dice nada de adaptar la ganancia a la rigidez, ni la velocidad del ensayo, ni cuántas prótesis distintas se compararon. Hay que leer el texto completo (PDF en CORE: https://core.ac.uk/download/370406896.pdf; a mí me dio error 403). | [leí texto/abstract] (solo el abstract) |
| 8 | **Chevalier et al. 2017**, IFAC-PapersOnLine 50(1):12210, doi 10.1016/j.ifacol.2017.08.2339 (UGent Knee Rig) | Su control por modelo exige identificar cada rodilla nueva, lo que toma tiempo. Proponen adaptar las ganancias a partir de datos para cada espécimen. | Ganancias distintas por espécimen, ajustadas en forma automática. | Rodilla cadavérica, control de movimiento. No hallé que hablen de rigidez. | [solo resultado del buscador] |
| 9 | **Chevalier, Verstraete & Loccufier 2022**, IEEE SMC, doi 10.1109/SMC53654.2022.9945319 | Agregan control de GRF al UGent Knee Rig. | Control de GRF en un simulador de rodilla. | No pude leer el método. | [solo resultado del buscador] |
| 10 | **Richter & Simon 2014**, J Dyn Sys Meas Control 136(3), doi 10.1115/1.4026342; **Davis 2013**, tesis Cleveland State | Robot de cadera para probar prótesis transfemorales sobre una cinta. Control robusto de movimiento ante la fuerza de contacto. Davis: seguir bien la trayectoria no basta para dar la GRF de una persona sana; optimizar las referencias bajó el error de GRF 62 %. | Prótesis, objetivo de GRF de persona sana. | Ajusta referencias por optimización entre corridas; no adapta la ganancia a la rigidez. | [solo resultado del buscador] |
| 11 | **Noble et al. 2010**, J Biomech Eng, doi 10.1115/1.4000851 (Cleveland Clinic) | Robot para articulaciones cadavéricas: lógica pseudo-difusa iterativa y control híbrido en tiempo real para reproducir la carga fisiológica. | Iterativo + tiempo real. | No adapta a la rigidez (según el resumen). | [solo resultado del buscador] |

### A2. Conclusión de A

- **El principio de control no es nuevo.** Ajustar la ganancia de un lazo de fuerza a la rigidez medida del espécimen existe desde 1997 en máquinas de ensayo (Hinton; Instron), y se usa por zonas de rigidez en robots para columna (patente Cleveland Clinic 2023). La memoria entre ciclos (ILC) para la GRF con prótesis también existe (Aubin 2008; Yang 2020).
- **Lo que no encontré:** un simulador de marcha o banco de prótesis que (1) ajuste la ganancia del lazo de fuerza **durante la pisada** según la rigidez **medida de cada prótesis**, k(F), (2) combinado con ILC, y (3) evaluado en **varias prótesis de distinta rigidez** con el error de seguimiento reportado por prótesis.
- **Veredicto: parcialmente nuevo.** El aporte es la **transferencia y validación** de un principio conocido a un problema que no lo había usado (imponer la GRF de marcha sana a prótesis de distinta rigidez). No es un "control nuevo".
- **Riesgo:** Yang 2020 (Bath) puede estar más cerca de lo que parece. Si compara varias prótesis con su EILC, el vacío "control de GRF en lazo cerrado + comparar prótesis" de `CLAUDE.md` se achica. El vacío de la **interfaz socket–muñón** no queda tocado (Yang no la menciona en el abstract). **Leer Yang 2020 completo es prioridad.**

---

## B. Escala temporal: ¿qué cambia al ensayar 10× más lento?

### B1. Cuánto cambian rigidez, histéresis y energía con la velocidad (pies protésicos)

| Trabajo | Pie / material | Velocidades probadas | Resultado | Etiqueta |
|---|---|---|---|---|
| **Lecomte 2022**, tesis doctoral, Univ. de Islandia/Össur, https://opinvisindi.is/handle/20.500.11815/2892 (sec. 4.1, Tabla 4-1) | Pro-Flex XC talla 27 **con una capa de espuma sensible a la velocidad agregada a propósito** | 0.5, 1, 2 y 3 Hz (para ellos, 1 Hz ≈ marcha a 3 km/h) | De 0.5 a 3 Hz (6× más rápido): cuasi-rigidez 16.4 → 18.0 N/mm (+9.8 %); desplazamiento máx. −8.3 %; retorno de energía 88.6 → 90.1 %. El pie original sin espuma también se graficó, pero sus números no están en la tabla. | [leí texto/abstract] |
| **van Jaarsveld et al. 1990**, Prosthet Orthot Int 14:117, doi 10.3109/03093649009080337 | 9 pies (SACH, Quantum, Multiflex, uniaxial Otto Bock, etc.) | Carga por escalones de 1 mm; ≈1.5 h por pie. Una corrida extra a la mitad de la velocidad. | A la mitad de la velocidad, la histéresis subió apenas. Los autores **esperan** (no lo midieron) que en la marcha real el pie sea más rígido y absorba menos energía. Por eso dicen que sus datos sirven sobre todo para comparar pies entre sí. | [leí texto/abstract] |
| **Turner et al. 2022**, PLoS ONE, doi 10.1371/journal.pone.0268136 | 56 pies, 5 modelos | 20 mm/s (lo más rápido que permitía su máquina) | No linealidad (rigidez a carga baja vs alta): 28–86 % en antepié, 52–94 % en talón. Los autores admiten: "loading rate used (20 mm/s) is likely slower than physiological". No tratan la viscoelasticidad. | [leí texto/abstract] |
| **Tacca et al. 2024**, Front Rehabil Sci, doi 10.3389/fresc.2024.1290092 | Vari-Flex de perfil bajo, 33 combinaciones | 100 N/s; 4 ciclos (promedian los 3 últimos) | Rigidez curvilínea que sube con la carga. No prueban varias velocidades ni hablan de viscoelasticidad. | [leí texto/abstract] |
| **Klute, Berge & Segal 2004**, J Rehabil Res Dev 41(4):535, doi 10.1682/JRRD.2003.02.0025 | Talones de pies y zapatos | Péndulo de impacto (simula el contacto del talón) | Los pies disipan 33.6–52.6 % de la energía; con zapato, hasta 82.4 %. Modelo: resorte que se endurece + amortiguador que depende de la posición. Velocidad de impacto: no está en el abstract. | [leí texto/abstract] |
| **Bradshaw, Bryant & Zhao 2022**, NACOB (Queen's) | Quilla de Niagara Foot (polímero termoplástico) | Rampa y espera + cíclico | La fuerza se relaja con varias constantes de tiempo: el pie de polímero **sí depende del tiempo**. El modelo QLV predice bien la carga (±7.4 N) y peor la descarga (±14 N), y falla por encima de 15 mm. | [leí texto/abstract] |
| **Starker & Lecomte 2022**, OTWorld (Össur) | Pies de 70–100 kg | Cuasi-estático a ángulo fijo vs rodadura dinámica (ISO/TS 16955) | Lo cuasi-estático diferencia los pies, pero dice poco del talón al rodar. La "rigidez dinámica" de la rodadura concuerda mejor con lo que sienten los usuarios. El mismo pie da valores distintos según el banco (Vari-Flex cat. 4: 42 vs 38 N/mm). | [leí texto/abstract] |
| **Geil 2002**, J Biomech 35(10):1405, doi 10.1016/S0021-9290(02)00169-0 | Pies ESR de tobillo sólido | Modelo resorte + amortiguador | Propone medir rigidez y viscoelasticidad como coeficientes. Sin números. | [solo resultado del buscador] |
| **Smith & Gordon 2017**, Exp Mech 57:953, doi 10.1007/s11340-017-0285-z | TaiLor Made y Renegade | — | Midieron viscoelasticidad; el abstract no da números de velocidad. | [leí texto/abstract] |

**Por material (sin datos de pies enteros a varias velocidades):**
- **Fibra de carbono/epoxi:** en la dirección de la fibra, el módulo casi no cambia con la velocidad de deformación hasta tasas altas. Las propiedades transversales y de corte suben ≈10–20 % entre cuasi-estático y 1 s⁻¹. Fuente: Polymers 2023, doi 10.3390/polym15122711, y otras del mismo resumen. [solo resultado del buscador]. Inferencia: una quilla de carbono a flexión dependería poco de la velocidad, y la parte de caucho/espuma (talón, cosmética, zapato) más.
- **Espumas de poliuretano (talón SACH, cubiertas):** son más duras a mayor velocidad; la energía depende de la densidad, la temperatura y la tasa (Alzoubi et al. 2011, IMECE, doi 10.1115/IMECE2011-62290). [solo resultado del buscador]
- **Pie articulado (topes de caucho):** no encontré datos según la velocidad.

### B2. ¿Cuánto cambia al bajar 10×? (respuesta honesta)

- **No encontré ningún estudio que pruebe el mismo pie a la velocidad real y a 1/10.** No hay una cifra publicada para "10× más lento".
- El dato medido más cercano (Lecomte 2022): con un pie **diseñado para ser sensible a la velocidad**, un cambio de 6× movió la cuasi-rigidez ≈10 % y el retorno de energía ≈1.5 puntos. Un pie de carbono sin espuma debería cambiar menos (inferencia, no medida).
- A x10, el apoyo de 6 s equivale a ≈0.1 Hz (cálculo propio con la equivalencia 1 Hz ≈ 3 km/h de Lecomte). Queda **fuera** del rango probado (0.5–3 Hz): extrapolar no tiene respaldo.
- Hay un mínimo cambio detectable de 7 % en cuasi-rigidez citado de Shepherd & Rouse 2020 [solo resultado del buscador]. Si el efecto de la velocidad fuera del orden del 10 %, estaría cerca de ese umbral (inferencia).
- Los valores cuasi-estáticos publicados (Turner 20 mm/s, Tacca 100 N/s) también son lentos. La tesis no queda peor que la práctica habitual de caracterización. Eso sí: en un ensayo cuasi-estático la histéresis y el impacto del talón se subestiman (van Jaarsveld lo espera; Starker lo muestra para el talón).

### B3. Cómo lo declaran otros simuladores lentos

| Simulador | Duración del apoyo | Cómo lo justifica o declara | Etiqueta |
|---|---|---|---|
| Aubin 2012 (VA Seattle) | 2.7 s (≈4× más lento) | Lo declara como limitación. Cita otros simuladores de 2, 3.2, 10, ≈12, 20 y 60 s. Atribuye a la baja velocidad que la vGRF quede corta justo después del contacto del talón (falta el impulso del impacto). | [leí texto/abstract] |
| Aubin 2008 | 1.5 s | "Más lento que lo fisiológico". | [solo resultado del buscador] |
| Herlihy 2026 | ≈10 % de la velocidad normal (0.10–0.15 m/s) | Lo atribuye a límites mecánicos y de costo, comunes en simuladores cadavéricos. Advierte que piel, liner y encaje son viscoelásticos: sus resultados son "cuasi-dinámicos". La cinemática del tobillo sale más plana. Se presenta como prueba de concepto. | [leí texto/abstract] |
| Whittaker et al. (pie plano, PMC3549316) | 4.09 s (6× más lento) | — | [solo resultado del buscador] |
| Wang et al. 2020, Proc IMechE H, doi 10.1177/0954411920938902 | 5 s | — | [solo resultado del buscador] |
| Nester 2009, J Foot Ankle Res 2:18, doi 10.1186/1757-1146-2-18 | — | Pide aplicar las cargas con la magnitud y la velocidad de la marcha, "o lo más cerca posible". | [leí texto/abstract] |
| Norma ISO/TS 16955 (rodadura) | **600 ms ± 10 %** (velocidad real) | La norma de caracterización de pies sí usa el tiempo real. | [solo resultado del buscador] (resumen de iTeh, no la norma) |

**Lectura:** ir más lento es la norma en los simuladores cadavéricos y se **declara**, no se oculta. El x10 de la tesis está dentro del rango publicado (2–60 s). Herlihy (≈10 %) es el caso más parecido.

---

## C. Argumentos de jurado o revisor y cómo los responden otros

| Objeción posible | Qué hacen otros | Respuesta sugerida (inferencia mía salvo que se cite) |
|---|---|---|
| **"Controlar solo Fz no es la carga completa."** | Aubin 2008 y 2012 y Herlihy 2026 controlan solo la vGRF. ISO 22675 carga con la resultante de la fuerza vertical y la anteroposterior [solo resultado del buscador]. Womac (en VACIOS §4): lo coronal no se capta en un protocolo sagital. | Escribir "componente vertical" en la pregunta, o anunciar el orden Fz → Fy → CoP. Declarar que lo coronal y la torsión quedan fuera. |
| **"Un control lento no representa la marcha."** | Aubin 2012 y Herlihy 2026 lo declaran como limitación y ponen sus resultados en contexto ("cuasi-dinámico"). | Declararlo. Medir la sensibilidad propia: repetir el Ensayo A (k) o una pisada a 2–3 escalas de tiempo (por ejemplo x10, x6, x4 si los motores llegan) e informar cuánto cambian k e histéresis. Citar Lecomte (≈10 % por 6× en un pie sensible a la velocidad) como orden de magnitud. |
| **"Imponer la misma GRF borra lo que distingue a las prótesis."** | En simuladores de rodilla, el control por fuerza (ISO 14243-1) deja que el diseño del implante decida la cinemática; el grupo de Leeds dice que la elección fuerza o desplazamiento depende de la pregunta [solo resultado del buscador]. ISO 22675 e ISO/TS 16955 imponen perfiles de fuerza para comparar pies. | Con la fuerza fija, lo que distingue a la prótesis pasa a la salida: desplazamiento, CoP/forma de rodadura, energía. Es la lógica de `CLAUDE.md` §Energía ("el control fija F; la prótesis decide v y ω"). |
| **"El control adaptativo a la rigidez ya existe."** | Hinton 1997; Instron; patente Cleveland Clinic 2023; Aubin 2012 (difuso no lineal). | Aceptarlo y citarlo. Presentar el aporte como aplicación y validación en prótesis transtibiales, con el beneficio medido (oscilación 3–10× menor, dato propio) frente a la ganancia fija. |
| **"Ya hay simuladores con ILC de GRF con prótesis."** | Aubin 2008; Yang 2020 (Bath, pasivas y activas). | Diferenciar por: adaptación a k(F) de cada prótesis, error informado por prótesis de distinta rigidez, y la interfaz socket–muñón como salida. **Primero leer Yang 2020 para confirmar que no lo hace.** |
| **"El banco no predice lo que vive el usuario."** | Tesis MIT sobre LLTE (DSpace 1721.1/140104): los bancos actuales no bastan para calcular esa métrica [solo resultado del buscador]. Applied Sciences 2021, doi 10.3390/app11125318: buena correlación banco–usuario en llano, peor en bajada [solo resultado del buscador]. | Encuadrar la tesis como ensayo **mecánico preclínico** (ver VACIOS §2 y §5b: diferencia mecánica ≠ beneficio clínico). |

---

## Qué cambia para la pregunta de tesis

**Refuerza:**
- El problema es real y reconocido: la rigidez no lineal del espécimen complica el lazo de fuerza (Aubin 2012, patente Cleveland Clinic, Hinton 1997). La ganancia programada tiene respaldo de principio.
- El x10 está dentro de lo que hacen y declaran los simuladores publicados.

**Debilita:**
- "Un control que se adapta a la rigidez" **no es novedad en sí**. Si la pregunta parece venderlo como nuevo, un revisor que conozca Instron o los robots para columna lo objeta.
- Yang 2020 (Bath) puede achicar el vacío de "control de GRF en lazo cerrado con varias prótesis". Falta leerlo.
- El efecto de bajar 10× la velocidad **no tiene número publicado**: es un vacío que la tesis tendría que medir, o al menos acotar y declarar.

**Sugiere modificar** (propuestas; Luis decide):
1. Precisar qué fuerza y a qué velocidad: "¿En qué medida un control en lazo cerrado de la **componente vertical** de la GRF, con ganancia ajustada a la rigidez medida de cada prótesis, reproduce la curva de una marcha sana **a una décima de la velocidad real** en prótesis transtibiales de distinta rigidez?"
2. Poner la comparación en el centro (así el aporte se mide y no se afirma): "¿Cuánto reduce el error de seguimiento de la GRF vertical, **frente a una ganancia fija**, un control que ajusta su ganancia a la rigidez de cada prótesis transtibial…?"
3. Opcional, pregunta secundaria de validez: "¿Cuánto cambian la rigidez y la histéresis medidas de cada prótesis entre la escala x10 y escalas más rápidas?" Responde la objeción de la velocidad con datos propios.

---

## No encontrado

- Un estudio que pruebe el **mismo pie protésico** a la velocidad real y a 1/10 (ni a 1/6). Tampoco datos según la velocidad para un pie SACH, un pie articulado o un pie de carbono sin modificar.
- Un simulador de marcha o banco de prótesis con **ganancia ajustada en tiempo real a la rigidez medida de cada prótesis**, ni un **estimador de rigidez en línea** en ese contexto (sí existen en ensayo de materiales y en columna).
- El texto completo de Yang 2020: cuántas prótesis comparó, a qué velocidad y si adapta algo a la rigidez.
- Las cifras confirmadas de Aubin 2008 (los resúmenes se contradicen).
- La frecuencia o duración de ciclo exacta de ISO 22675 y el texto de ISO/TS 16955 (solo vi resúmenes).
- Un trabajo que compare prótesis de distinta rigidez reportando el error de seguimiento de la GRF por prótesis.
