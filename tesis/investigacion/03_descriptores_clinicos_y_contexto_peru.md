# 03 — Descriptores clínicos del pie protésico y contexto Perú/LatAm (búsqueda 2026-11-25)

**Estado:** fuentes halladas por búsqueda web, **sin lectura de Luis** → no son respaldo final (regla del proyecto).
**Marcas:** [T] = leí texto completo o parte del texto · [A] = leí solo el abstract/resumen · [B] = solo resultado del buscador (no abierto).
[I] = inferencia mía, no lo dice la fuente. No repito lo ya puesto en `tesis/VACIOS_Y_RELEVANCIA_CLINICA.md` ni en `tesis/PLATAFORMA_INSTRUMENTADA_USO.md`.

---

## 0. Hallazgo que cambia el planteamiento (leer primero)

**Ya existe un ensayo normado que impone carga + ángulo de tibia y calcula descriptores: ISO 22675 + ISO/TS 16955.**
- ISO 22675 (vigente 2024): máquina que aplica un perfil de fuerza estandarizado (resultante de la GRF vertical y A-P) sincronizado con un perfil de ángulo de tibia, con una placa que bascula. https://www.iso.org/standard/79620.html [A, vista previa del FDIS]
- ISO/TS 16955:2016 usa esa máquina para calcular: rigidez ΔF/Δs, brazo de palanca l = M/F (equivale a la posición del CoP), **longitud efectiva del pie** con placa basculante (Δl = l2 − l1), rango de contacto completo y **energía** ∫F·ds. Prueba de rodadura: fuerza aplicada entre −15° y +20° de placa, en 600 ms ± 10 %. Talón/antepié: pico 824 N (120 % de 70 kg); mediopié 1373 N; carga/descarga en 1 s. Pie de referencia: talla 26, usuario de 70 kg. Avisa que con F < 10 % de F máx el cálculo es ruidoso. https://cdn.standards.iteh.ai/samples/69821/e91e59077017403bb8b4d2db7331d2db/ISO-TS-16955-2016.pdf [T, vista previa pública]
- **Consecuencia:** la frase "ningún descriptor se mide bajo carga impuesta" (sección 3 de `VACIOS_Y_RELEVANCIA_CLINICA.md`) es **demasiado fuerte**. Lo que sí sigue sin precedente hallado: imponer la **GRF medida de marcha sana** (Fz y Fy por separado, doble pico real) **en lazo cerrado y adaptada a la rigidez** de cada pie, en 3 ejes, y medir los descriptores en esa misma corrida. [I]

**Correcciones a atribuciones de `VACIOS_Y_RELEVANCIA_CLINICA.md`** (no edité ese archivo; lo dejo anotado para que Luis decida):
- doi 10.1177/0309364620917838 es **Ernst, Altenburg & Schmalz 2020**, "Characterizing adaptations of prosthetic feet in the frontal plane" (pies en pendiente lateral), no una revisión META Arc. [A, Europe PMC]
- PMC4342001 es **Gard et al. 2011** (amputados bilaterales con y sin tobillo Multiflex). El dato "SACH de 28 cm funciona como <20 cm" no sale de ese artículo; el buscador lo atribuye a un documento de patente USPTO. [T]
- https://par.nsf.gov/servlets/purl/10251699 es **Olesnavage et al.**, demostración experimental del marco LLTE, no un artículo de cuasi-rigidez. [T]

---

## A. Procedimiento de cálculo de cada descriptor

### A1. Forma de rodadura (roll-over shape, ROS)
| Paso | Qué dice la literatura | Fuente |
|---|---|---|
| Definición | Trayectoria del CoP expresada en un marco fijo a la pierna (tibia/encaje/pilón). Es el "balancín" efectivo del sistema tobillo-pie. | Hansen, Childress & Knox 2004, Clin Biomech, doi 10.1016/j.clinbiomech.2003.12.001 [A] |
| Ventana | Desde el contacto del talón hasta el contacto del talón opuesto. Koehler-McNicholas 2018 usa solo el apoyo simple (despegue del pie contrario → contacto del talón contrario). | Hansen 2004 [A]; Wang & Hansen 2010, doi 10.1016/j.jbiomech.2010.04.036 [A]; Koehler-McNicholas 2018, doi 10.1371/journal.pone.0202884 [T] |
| Umbral de fuerza | 150 N por la incertidumbre del CoP a fuerza baja (Koehler 2018). ISO/TS 16955: cuidado si F < 10 % de F máx. Hansen: umbral no hallado en lo leído. | Koehler 2018 [T]; ISO/TS 16955 [T] |
| Ajuste | Arco circular por mínimos cuadrados no lineales (ecuación del arco inferior de un círculo). Salidas: radio, largo del arco, desplazamiento hacia adelante del centro. Hay un método alternativo más robusto (Bapat & Myers 2022). | Gard 2011 [T]; Bapat & Myers 2022, doi 10.1016/j.medengphy.2022.103756 [A] |
| Normalización | Radio dividido por la altura del sujeto (Koehler 2018) o por la longitud de la pierna. PROST 2026: normalizar por altura no reduce la variabilidad en sanos. | Koehler 2018 [T]; Reichsbouscher & Solav 2026 (preprint), doi 10.64898/2026.11.05.764655 [A] |
| Banco sin personas | Hansen 2000: 2 métodos cuasi-estáticos + 1 dinámico dan formas similares (Flexwalk, Quantum, SACH, SAFE). Sam 2004: 11 pies de países de bajos ingresos con técnica cuasi-estática. Curtze 2009: aparato tipo péndulo invertido que emula el peso corporal. Donahue 2025: banco propio; el radio baja al subir la carga. | Hansen 2000, doi 10.1080/03093640008726549 [A]; Sam 2004, doi 10.1080/03093640408726698 [A]; Curtze 2009, doi 10.1016/j.jbiomech.2009.04.009 [A]; Donahue 2025, doi 10.1097/pxr.0000000000000411 [A] |

**Errores típicos:** cambia con la alineación (Hansen 2008, doi 10.1080/03093640802366158 [A]); con el calzado (Curtze 2009 [A]; Major 2022, doi 10.1371/journal.pone.0262910 [T]); con la carga (Donahue 2025 [A]); con el umbral y la ventana elegidos (Koehler 2018 [T]); con la calibración del punto de aplicación de la plataforma (List 2017: la calibración in situ bajó el RMSE del CoP hasta ≈60 %, doi 10.1016/j.gaitpost.2017.07.111 [A]).

**En el simulador [I]:** CoP del AMTI → restar la posición del punto A (ejes X, Y) → rotar por el ángulo sagital θ → ajuste de arco. La rodadura queda **ligada a la trayectoria de θ impuesta**: con θ fijo de una trayectoria, la ROS describe al pie bajo esa cinemática, no la que elegiría un usuario.

### A2. Longitud efectiva del pie (EFL) y su razón (EFLR)
- Hansen, Sam & Childress 2004 (J Prosthet Orthot 16(2):41-45, doi 10.1097/00008526-200404000-00002) [A]: el pie se rueda **a mano sobre una plataforma de fuerza con fuerza constante ≈ peso del usuario**; EFL = distancia del talón al CoP (marco del pie) al ángulo de pierna que corresponde al contacto del talón opuesto; EFLR = EFL / largo del pie.
- Gard 2011 [T]: EFL = del talón al punto más anterior de la ROS.
- ISO/TS 16955 [T]: longitud efectiva con placa basculante, Δl = l2 − l1 con l = M/F.
- **Error típico:** depende del ángulo que se elija como "contacto opuesto" y del punto final de la ROS [I].

### A3. Cuasi-rigidez del tobillo
- Shamaei, Sawicki & Dollar 2013 (PLoS ONE, doi 10.1371/journal.pone.0059935) [T]: pendiente del mejor ajuste lineal de la curva momento–ángulo, por fase (dorsiflexión, flexión dual, plantiflexión). Modelos con altura y peso: error medio 13–30 %.
- Starker et al. 2026 (Med Eng Phys, doi 10.1088/1873-4030/ae33ba) [A]: 5 métodos de máquina en 3 pies (SACH, K2, ESR) difieren hasta **24 %** (≈2 categorías de pie); la cuasi-rigidez del tobillo derivada difiere hasta 19 % (talón) y 55 % (antepié); 2 de 5 métodos no distinguieron los pies. → **no hay método único; hay que declarar cuál se usa.**
- Prieto et al. 2023 (doi 10.1016/j.medengphy.2023.104053) [A]: la rigidez dinámica tiene varios tramos lineales; un solo número la simplifica.
- **En el simulador [I]:** momento de la GRF respecto de un eje de tobillo definido (real en el pie articulado; virtual en el de carbono) vs ángulo del pilón respecto del suelo. Exige fijar ese eje en el CAD (punto aún pendiente en el proyecto). Es distinta de la rigidez vertical k (N/mm) que ya mide el Ensayo A.

### A4. Energía absorbida/devuelta y eficiencia
- Takahashi, Kepple & Stanhope 2012 (doi 10.1016/j.jbiomech.2012.08.017) [A]: modelo de segmento deformable unificado (UD); no necesita definir tobillo; diferencias vs modelo anatómico de 1.4–4 % en trabajo.
- Ray, Wurdeman & Takahashi 2018 (doi 10.1186/s12984-018-0347-1) [A]: con el UD, el trabajo positivo de la prótesis sube 6.1 % tras 3 semanas de adaptación (22 sujetos, K3+). → **en personas, la energía mezcla pie y estrategia de carga del usuario.**
- Childers & Takahashi 2018 (Sci Rep, doi 10.1038/s41598-018-23705-8) [A]: más energía devuelta → más impulso del CoM y menor colisión en la pierna sana (5 sujetos).
- Banco: Major 2022 [T] y Donahue 2025 [A] integran fuerza–desplazamiento (trapecios) en máquina de ensayos a contacto inicial, apoyo medio y apoyo final.
- **Errores típicos:** derivar posiciones amplifica ruido; desfase entre fuerza y cinemática; CoP ruidoso con Fz baja; el montaje cambia mucho el resultado (ya anotado en VACIOS §6); fricción del banco puede inflar la histéresis (crítica a Geil, en un PhD de Bournemouth, https://eprints.bournemouth.ac.uk/22507/1/HAWKINS,%20James%20Richard_Ph.D._2015.pdf [B]).

### A5. Señales y frecuencias necesarias
| Señal | Para qué | Dato publicado |
|---|---|---|
| Fx, Fy, Fz, Mx, My (Mz) | CoP, momento en el tobillo, potencia | Plataforma AMTI a 1200 Hz (Koehler 2018 [T]) |
| Ángulo sagital del pilón | Marco de la pierna (ROS), cuasi-rigidez | Cámaras a 120 Hz (Koehler 2018 [T]) |
| Desplazamiento X, Y del punto A | Velocidad del punto A → energía | ISO/TS 16955 exige sensor de desplazamiento junto al sensor de fuerza [T] |
| Base de tiempo común | Todo lo anterior | — |

[I] A 10× más lento el contenido en frecuencia de la GRF baja 10×; 1000 muestras/s sobra. Lo crítico es la **sincronía** y el **filtrado antes de derivar**, no la tasa.
[I] Velocidad lenta: Hansen 2000 halló ROS cuasi-estática ≈ dinámica, y Sam 2004 dice que los pies pueden modelarse como cuasi-estáticos en marcha (frecuencias naturales altas, amortiguamiento bajo). Esto **apoya** medir ROS/EFL a 10×. La **energía/histéresis** puede depender de la velocidad (espumas, caucho del SACH); ISO usa 0.6–1 s por carga y nuestro apoyo dura ≈6 s → declarar como limitación.

### A6. ¿Se midió alguno en un simulador con GRF impuesta (sin personas)?
- **Sí, en forma normada y cuasi-estática:** ISO/TS 16955 (EFL, rigidez, energía con perfil de carga + placa basculante) [T]; Hansen 2000 y 2004 (carga ≈ peso constante) [A]; Curtze 2009 (péndulo invertido) [A]; Donahue 2025 (banco de rodadura) [A].
- **Con GRF de marcha sana en lazo cerrado y adaptada a la rigidez: no encontrado.** Herlihy 2026 (ya en CLAUDE.md) es lazo abierto.

### A7. Valores típicos publicados
| Descriptor | Valor | Condición | Fuente |
|---|---|---|---|
| Radio ROS / altura | 0.156–0.183 (media 0.170) | 9 pies ESR de alta actividad, 3 usuarios | Koehler 2018 [T] |
| Radio ROS / altura | 0.24–0.26 → 0.17–0.18 con tobillo Multiflex | Seattle Lightfoot II, 17 bilaterales | Gard 2011 [T] |
| Radio ROS tobillo-pie sano | mediana 410 mm (RIC 238 mm) | 249 personas, 4 bases | PROST 2026 [A] |
| Radio frontal (medio-lateral) | promedio 102 mm | varios pies, péndulo | van Hal 2021, doi 10.1016/j.jbiomech.2021.110610 [A] |
| EFLR | 0.63–0.81 (fisiológico 0.83) | 15 pies clínicos de los 90 | Hansen 2004 JPO [A] |
| EFLR | 0.65–0.71 | Seattle Lightfoot II, sube con la velocidad | Gard 2011 [T] |
| Forma de pies de países de bajos ingresos | parecida al SACH; falta apoyo de antepié ("caída" al final) | 11 pies | Sam 2004 [A] |
| Cuasi-rigidez tobillo sano | 201–685 N·m/rad (fase de dorsiflexión) | valores usados por diseñadores | Shamaei 2013 [T] |
| Cuasi-rigidez tobillo sano | 352–479 N·m/rad (0.75–1.5 m/s) | rango que imita una prótesis de rigidez variable | Rogers-Bradley 2024, doi 10.1038/s41598-024-67230-3 [A] |
| Pies ESR pasivos | más rígidos que el tobillo sano, sobre todo a baja velocidad | — | Rogers-Bradley 2024 [A] |
| Restitución de energía (banco) | 82 % (nuevo) → 90 % (tras fatiga) pie bajo costo ICRC; 87 % K3 comercial; 93 % K4 | compresión, 5 ciclos | Falbriard 2022, doi 10.1371/journal.pone.0266656 [T] |
| Restitución de energía (banco) | SACH devuelve menos que pies ajustables en apoyo final; un pie bajó de 73 % a 55 % con calzado/alineación | máquina de ensayos | Major 2022 [T] |
| Retorno de energía apoyo final (marcha) | 0.094–0.215 J/kg | 9 pies ESR, 3 usuarios | Koehler 2018 [T] |
| Retorno en carrera | SACH 31 %, Seattle 52 %, Flex-Foot 84 % (Czerniecki) | citado en revisión | Rahnama et al. 2024, https://frontiersin.org/journals/rehabilitation-sciences/articles/10.3389/fresc.2024.1402114/pdf [B] |
| Tobillo hidráulico añadido | baja el retorno de energía hasta 18 %; ROS no lineal con la carga | pie ESR + tobillo | Donahue 2025 [A] |

**Pie articulado vs fibra de carbono, mismos descriptores, mismo banco: no encontrado.** Lo más cercano: añadir un tobillo articulado/hidráulico achica el radio (Gard 2011) y baja la energía devuelta (Donahue 2025).

---

## B. Relevancia clínica (una línea por descriptor)
| Descriptor | Decisión clínica que informa | Evidencia en pacientes |
|---|---|---|
| Forma de rodadura | **Alineación**: explica por qué cada pie pide otra alineación; un algoritmo basado en ROS alineó igual que protesistas. | Hansen 2000 [A]; Hansen 2003, doi 10.1080/03093640308726664 [A] |
| Largo del arco / EFL | **Elección de pie**: arco más corto → menos momento de dorsiflexión y mayor 1.er pico de GRF en la pierna sana (14 usuarios TT). | Hansen 2006, doi 10.1080/03093640600816982 [A] |
| EFL (diseño) | Largo de pie ≈29 % de la pierna minimiza el costo metabólico; el radio casi no influye (8 sanos con botas). | Adamczyk & Kuo 2013, doi 10.1242/jeb.082347 [A] |
| Cuasi-rigidez | **Prescripción por categoría de rigidez** (peso/actividad); talón más rígido → menos retorno de energía, mayor tasa de carga y momento de rodilla. | Adamczyk 2017, doi 10.1016/j.humov.2017.04.005 [A]; Starker 2026 [A] |
| Energía / eficiencia | **Nivel K** (ESR para K3+); más retorno → más impulso y menos colisión en la pierna sana, pero efecto metabólico pequeño. | Childers & Takahashi 2018 [A]; Gardiner 2016 (en VACIOS) |
| ROS frontal / adaptación | Selección para terreno irregular (pies con dedos partidos se adaptan mejor). | Ernst 2020 [A] |

Nota: Koehler 2018 [T] estima que harían falta ≈11 usuarios para detectar diferencia de radio entre dos pies en clínica → argumento para medirlo en banco.

---

## C. Contexto Perú y Latinoamérica

### C1. Cifras de Perú
| Dato | Valor | Fuente |
|---|---|---|
| Personas con discapacidad (Censo 2017) | 3 209 261; dificultad para moverse/caminar 485 211 (15.1 %) | INEI, https://m.inei.gob.pe/prensa/noticias/en-el-pais-existen-3-millones-209-mil-261-personas-con-discapacidad-11687/ [B] (otra presentación INEI da 3 051 612; diferencia sin explicar) |
| ENEDIS 2012 | 1 575 000 con discapacidad; 932 000 con limitación para moverse/caminar o usar brazos/piernas | INEI, https://www.inei.gob.pe/media/MenuRecursivo/noticias/np-178-2013.pdf [B] |
| **Personas con amputación (cifra nacional)** | **No encontrada** (ni INR, CONADIS, MINSA ni EsSalud) | — |
| Amputaciones por diabetes | ≈8000 al año (estimación MINSA, sin metodología visible) | https://www.gob.pe/institucion/minsa/noticias/585421-minsa-brinda-recomendaciones-para-prevenir-el-pie-diabetico [B] |
| INR 2002–2007 | 570 amputados; 78.1 % miembro inferior; nivel más frecuente arriba de rodilla (53.9 %) | Farro et al. 2012, Rev Méd Hered 23(4):240-3, doi 10.20453/rmh.v23i4.845 [B] |
| Causa a nivel nacional | 54.7 % no traumática; angiopatía diabética 42.3 % (citando Farro 2012) | Quezada & Montalvo 2024, Rev Méd Hered, doi 10.20453/rmh.v35i3.5761 [T] |
| INR 2018–2019 (muestra de 70 con prótesis) | 81.4 % varones, edad media 48.8 años; vascular-endocrino 51.4 %, traumática 42.9 %; nivel transtibial = único predictor de rehabilitación exitosa (OR 2.84) | Quezada & Montalvo 2024 [T] |
| INR 2020 | 278 amputados atendidos; 92.4 % miembro inferior; 42.3 % con diabetes (cita el protocolo INR 2021) | Huacac 2024, proyecto UPCH, https://repositorio.upch.edu.pe/bitstreams/a85c1315-b627-49e5-9b91-7bc1d1d6301f/download [T] |
| **Proporción transtibial en Perú** | **No encontrada** como cifra nacional. El proyecto UPCH cita 48 % transfemoral / 45 % transtibial, pero de una referencia no peruana. | Huacac 2024 [T] |

### C2. Acceso, costo y financiamiento
- **EsSalud:** IETSI tiene un documento técnico "Prescripción de prótesis de miembro inferior" (mayores de 16 años, recomendaciones basadas en evidencia). No pude abrir el texto. https://repositorioslatinoamericanos.uchile.cl/handle/2250/6449611 [B] → **conseguirlo: es el criterio oficial de prescripción en Perú.**
- **EsSalud, vía de solicitud:** existe una plantilla de pedido de prótesis/órtesis que cita la Ley 26790 y la Ley 29973 (no es norma). https://modelo.pe/modelos/solicitud-de-cobertura-de-protesis-ortesis-o-ayuda-biomecanica-ante-essalud.md [B]
- **SIS:** no encontré norma que confirme que financie prótesis de miembro inferior. Pendiente: revisar el PEAS y el tarifario SIS.
- **Policía:** Mininter asignó S/ 21.2 millones para prótesis y ayudas a policías con discapacidad (2026). https://elperuano.pe/noticia/291714-mininter-garantiza-s212-millones-para-protesis-y-ayudas-biomedicas-a-policias-con-discapacidad [B]
- **Costo de una prótesis transtibial comercial en Perú:** no encontrado. Referencias sueltas: robótica PUCP ≈S/ 12 500 (ya en VACIOS); prótesis de miembro superior S/ 2000–25 000 (Andina, no comparable) https://andina.pe/agencia/noticia-startup-peruana-usa-inteligencia-artificial-la-fabricacion-protesis-a-bajo-costo-1027075.aspx [B].
- **Barrera del sector:** el fundador peruano de Horus Prosthetics menciona burocracia y falta de regulación del sector ortopédico. https://infomercado.pe/horus-prosthetics-este-ingeniero-peruano-fundo-una-startup-que-crea-protesis-accesibles-desde-alemania-para-latinoamerica/ [B]

### C3. Tesis y desarrollos peruanos
| Trabajo | Qué es | Fuente |
|---|---|---|
| PUCP: mecanismo 2 GDL para prótesis robótica transtibial | diseño + modelo dinámico, sin ensayo en banco | https://tesis.pucp.edu.pe/repositorio/handle/20.500.12404/20608 [B] |
| PUCP: prótesis transtibial con mecanismo paralelo 2SPU-RU | validación cinemática | https://alicia.concytec.gob.pe/vufind/index.php/Record/RPUC_7c0ed959b9d590e95b273d11425c09b5 [B] |
| PUCP: "Diseño conceptual de un módulo de ensayos para prótesis transtibial" | sensores de fuerza + IMU; dice que la norma no cubre esa verificación | solo snippet del buscador, enlace no confirmado [B] |
| PUCP: "Diseño y validación funcional del sistema mecánico de un pie" | simulación, fatiga, pruebas de carga | https://tesis.pucp.edu.pe/bitstreams/916243da-55f7-472b-8e4e-72414ef97132/download [B, acceso bloqueado] |
| USAT: prótesis transtibial de fibra de vidrio E + poliéster | estabilidad estática | https://alicia.concytec.gob.pe/vufind/Record/USAT_c29b9888164d9fc8a000bc62de153f11 [B] |
| UTEC: prototipo transtibial para marcha normal | prototipo | https://cris.utec.edu.pe/es/publications/design-of-a-transtibial-prosthesis-prototype-for-normal-walking-b/ [B] |
- **Fabricantes/laboratorios peruanos de pies protésicos:** no encontrados (solo startups de miembro superior). El INR tiene un departamento de amputados (Quezada 2024 [T]); si tiene taller propio de prótesis, no lo confirmé.
- **No hallé ninguna tesis peruana con banco de ensayo dinámico que imponga GRF.** [B, búsqueda limitada]

### C4. Latinoamérica (si no hay dato de Perú)
- Brasil: 102 056 amputaciones en el SUS (2011–2016), ≈70 % en personas con diabetes. https://pmc.ncbi.nlm.nih.gov/articles/PMC7372145 [B]
- México (IMSS): amputaciones mayores en diabéticos ≈101 (2004) → 111 por 100 000 (2013). https://revistamedica.imss.gob.mx/index.php/revista_medica/article/view/388/1073 [B]
- Mundo: 57.7 millones viven con amputación traumática (GBD 2017); causas: caídas 36.2 %, tránsito 15.7 %. McDonald et al. 2021, Prosthet Orthot Int, https://pubmed.ncbi.nlm.nih.gov/33274665/ [B]. Cifra para Perú: consultar la herramienta GBD (no hecho).
- Egipto (análogo de país de ingresos medios): propuesta de localizar la fabricación de pies compuestos; eligen el ESR. Elgamsy 2023, doi 10.1038/s41598-023-44008-7 [A]

---

## Qué cambia para la pregunta de tesis

**Refuerza:**
- Los descriptores sí tienen uso clínico concreto (alineación, elección de pie, nivel K) y medirlos con personas exige muchas, mezcla la adaptación del usuario (Ray 2018) y ≈11 sujetos por comparación (Koehler 2018).
- La ROS y la EFL toleran bien la velocidad lenta (Hansen 2000; Sam 2004) → el 10× no las invalida.
- Los métodos de banco difieren hasta 24 % (Starker 2026) → una carga **fisiológica y repetible** tiene valor.
- En Perú la causa principal es diabética y el nivel transtibial es el que mejor se rehabilita (Quezada 2024) → relevancia local del pie transtibial.

**Debilita:**
- ISO 22675 + ISO/TS 16955 ya imponen un perfil de carga y ángulo de tibia normado y calculan EFL, rigidez y energía. La novedad no puede ser "carga impuesta"; debe ser **GRF de marcha sana real, en lazo cerrado, adaptada a la rigidez, con Fz y Fy separados y CoP de 6 canales**. [I]
- La rodadura medida depende de la trayectoria de θ impuesta; hay que declararlo.

**¿Descriptores como variable dependiente?** [I] Recomiendo que **no sean la variable dependiente principal**, por el principio de Luis (el aporte propio es el control). Mejor:
- **VD principal:** error de seguimiento de la GRF (RMSE, r) y su igualdad entre pies de distinta rigidez.
- **VD secundaria:** repetibilidad (ICC, CV) de ROS, EFL, cuasi-rigidez y energía medidas bajo esa carga. Así el control "habilita" la medición clínica sin que la tesis dependa de que los pies salgan distintos.

**Redacciones alternativas (borradores, decide Luis con la asesora):**
1. "¿En qué medida un control en lazo cerrado de la GRF, adaptado a la rigidez de cada prótesis, impone la misma carga de marcha sana a pies transtibiales de distinta rigidez, y con qué repetibilidad permite medir bajo esa carga su forma de rodadura, longitud efectiva, cuasi-rigidez y energía?"
2. Dos preguntas: (P1) la actual, sobre el error de la GRF impuesta; (P2) "Bajo la misma GRF impuesta, ¿qué diferencias repetibles muestran un pie articulado y uno de fibra de carbono en forma de rodadura, longitud efectiva, cuasi-rigidez y energía?"
3. (Opcional, más riesgo: exige comparar con datos ISO de otros) "¿Difieren los descriptores medidos bajo GRF fisiológica en lazo cerrado de los que entrega el protocolo ISO/TS 16955 para los mismos pies?"

---

## No encontrado
- Umbral de fuerza y procedimiento exacto de Hansen (texto completo de Hansen 2000/2004 no abierto).
- Radios de ROS de SACH/Quantum/SAFE en Hansen 2000 y Curtze 2009 (solo abstracts).
- Valores de cuasi-rigidez (N·m/rad) de pies pasivos comerciales concretos.
- Comparación articulado vs fibra de carbono en el mismo banco con los mismos descriptores.
- Cualquier medición de descriptores bajo GRF de marcha sana en lazo cerrado.
- Número de personas con amputación en Perú; proporción transtibial nacional; cifras de EsSalud o CONADIS.
- Si el SIS financia prótesis de miembro inferior; precio comercial de una prótesis transtibial en Perú.
- Fabricantes o laboratorios peruanos de pies protésicos; texto del documento IETSI de prescripción.
- Fórmula y signos del CoP del AMTI específicos del modelo del lab (sigue pendiente en el proyecto).
