# Proyecto: Control del Simulador de Marcha (Tesis — Luis Plasencia)

## 📌 REGLA FIJA: toda decisión se guarda aquí, de inmediato
Cada vez que en una conversación se **cierre una decisión** (técnica, de alcance, de título, de prácticas, de plazos, etc.), esta se debe escribir en este archivo (`C:\Control\CLAUDE.md`) **en el mismo turno en que se cierra**, no al final de la sesión y no solo en la memoria auto-gestionada (`C:\Users\chees\.claude\projects\C--Control\memory\`). Razón: la memoria puede fallar en propagarse a sesiones nuevas (ya pasó); este archivo se carga siempre como contexto del proyecto. La memoria auto-gestionada se sigue usando en paralelo (preferencias de trabajo, contexto blando), pero **las decisiones concretas del proyecto viven en este .md, no solo en la memoria**. Si una sección queda desactualizada por una decisión nueva, reescribirla ahí mismo, no solo añadir al final.

**Este archivo se mantiene compacto a propósito (se carga entero en cada sesión → cuesta tokens).** El detalle completo — auditorías de referencias, contraste abstract-por-abstract, búsquedas, razonamiento descartado — vive en [`HISTORIAL.md`](HISTORIAL.md), en el mismo repo git, **sin perderse y leíble con Read cuando se necesite**, pero sin inyectarse solo en cada turno. Aquí solo va: estado vigente, decisiones cerradas (con su motivo en una línea), y lo que falta decidir. Al cerrar una decisión nueva: si es un hecho/estado vigente, va aquí; si es narrativa de cómo se llegó a ella (comparación de papers, etc.), el resumen va aquí y el detalle a `HISTORIAL.md`.

## 🔵 Estado actual / qué hacer si el usuario dice "continuar"
- **Resumen al 2026-10-29 (cierre de sesión):** proyecto = **Etapa 3 del simulador** (etapa 1 = artículo de conferencia, etapa 2 = artículo de revista enviado). Título vigente: *"Control en lazo cerrado de los tres ejes de un simulador de marcha, guiado por la fuerza de reacción del suelo y la presión plantar, para comparar prótesis transtibiales bajo la misma carga de una marcha sana"*. Pendiente de **confirmación de la asesora**.
- **(2026-10-31) Correo enviado a Dante Elías**, encargado del laboratorio: plantea la nueva etapa como posible tema de tesis pidiendo su opinión/alcance, propone apoyo de practicantes DPB4 desde enero, y pregunta por posible extensión del apoyo económico (set-oct ya coordinado con la profesora Victoria, quien está de licencia de maternidad) a nov-dic. **Pendiente de respuesta de Dante.**
- **Documento principal (todo el trabajo vive aquí):** https://claude.ai/artifact/EqD1E8VF5qRtKRfDA7n2Dg — síntesis para la presentación, problema clínico, antecedentes con figuras, vacío, objetivos, 4 preguntas, método (6.1 energía), alcance, riesgos, guion 30s, 36 referencias, anexo con diagrama propio. Ecuaciones/tablas propias → imagen PNG con fondo blanco (matplotlib; scripts en el scratchpad de la sesión 66877456…/out).
- **Próximos pasos útiles:** (1) medir latencia AMTI→Raspberry Pi→ESP32 cuando lleguen IMU/sensor de interfaz/sensores de posición (~mediados nov 2026); (2) simular control en tiempo real vs ILC con la latencia como variable (modelo gray-box); (3) Luis verifica pies pasivos disponibles en el lab; (4) confirmar carga de diseño del simulador con quien hizo el análisis estructural; (5) definir geometría del punto A (CAD) y convención de signos de Fy/θ/ω; (6) conseguir ADC de ≥8 canales; (7) lectura completa de papers por Luis tras la aceptación.
- `paper-search` (OpenAlex) sigue fallando aquí (sin jq en Windows) — usar script Python directo a la API (detalle en `HISTORIAL.md` § Herramientas de búsqueda), ya probado y funciona.
- **Regla de oro:** el usuario lee y decide el enfoque él mismo — nunca redactar síntesis/resúmenes interpretativos/texto de tesis salvo pedido explícito puntual. Por defecto, solo organizar/traer referencias.
- **Preferencia de trabajo (reforzada varias veces):** respuestas cortas, un tema puntual por intercambio, nunca dump de información.

Biomédico, PUCP, Biomechanics and Applied Robotics Research Laboratory.

## Material fuente (en este directorio, repo git desde 2026-10-29)
- `journal_copy.pdf` (= `2026_Intelligent_Service_Robotics_Simulador.pdf`) — artículo de **revista, enviado, aún no aceptado**. Control puramente posicional, GRF con un solo pico (62-67% apoyo). Nombra el control de fuerza en lazo cerrado como future work.
- `conferencia_copy.pdf` — artículo de **conferencia, aceptado, aún no publicado**. Ya leído completo — contiene la arquitectura real del simulador (abajo).
- `HISTORIAL.md` — detalle completo de auditorías/búsquedas/razonamiento descartado (no se carga automáticamente, leer con Read cuando se necesite).

## Arquitectura real del simulador (confirmada, leída del paper de conferencia)
3 ejes **independientemente actuados**, cada uno con su propio motor:
- **Horizontal**: husillo de bolas + servo, ~587 mm de recorrido.
- **Vertical**: husillo + cadena + servo con freno, ~542 mm de recorrido.
- **Sagital**: motor paso a paso + reductor planetario, rango -44° a 47°.
- Control actual: posicional puro, lazo abierto, trayectorias capturadas de sujeto sano (86 kg, 1.74 m) — no amputado.
- Validación funcional publicada: ángulo tibial r=1.00 (apoyo)/0.997 (balanceo); GRF vertical ya muestra doble pico en lazo abierto (r=0.9501) pero sobrestima el pico (157%BW vs ~126%BW esperado) — atribuido a masa añadida + mecánica pasiva de la prótesis, no a error de trayectoria. Paper reporta ~30x más lento que marcha real — **dato viejo: la velocidad vigente es x6** (confirmado por Luis).
- Referencia citada relevante para Bloque 4: McGeehan, Adamczyk, Nichols & Hahn (2022) — efectos de la rigidez de la prótesis en la dinámica de interfaz socket-muñón.

## Decisiones clave (enfoque vigente)
**Título vigente (2026-10-28):** *"Control en lazo cerrado de los tres ejes de un simulador de marcha, guiado por la fuerza de reacción del suelo y la presión plantar, para comparar prótesis transtibiales bajo la misma carga de una marcha sana"*.

**Idea central:** estandarizar el GRF **externo** (mismo objetivo fisiológico para cualquier prótesis montada) para que la lectura del **sensor de interfaz** (futuro, Bloque 4) sea comparación justa y específica por dispositivo. Forzar el GRF **no** fuerza la lectura de interfaz a igualarse entre prótesis (rigidez/amortiguamiento propios median esa relación distinto) — ⚠️ **hipótesis a probar en el simulador, NO confirmada por literatura** (ver `HISTORIAL.md` § Frossard 2019 para el matiz).

**Frase de pitch:** *"Quiero extender el simulador de marcha (ya validado en el paper de conferencia) con un sistema de control que permita reproducir de forma precisa y repetible la fuerza de reacción del suelo característica de la marcha humana, como herramienta de evaluación preclínica de prótesis transtibiales."*

## Arquitectura de control por eje
- Las trayectorias **las generan las fuerzas y la plantilla**, no la trayectoria capturada.
- **Vertical** → controlado con **Fz** (AMTI). Control de fuerza en tiempo real; ILC solo si la latencia medida no lo permite.
- **Horizontal** → controlado con **Fy** (AMTI), mismo esquema. Restricción dura: siempre avanza, nunca retrocede (verificada por sensor de posición horizontal).
- **Sagital** → guiado por la secuencia de zonas de la plantilla de presión (talón→mediopié→antepié); el IMU verifica el ángulo. Trayectoria capturada (r≈1.00) como punto de partida. Cerrar primero Fz y Fy; agregar sagital después (3 lazos acoplados).
- **Sensor de interfaz muñón-prótesis (Bloque 4, Practicante 1)** → nunca se controla, es variable de observación pura.
- Los 3 ejes se ejecutan **simultáneamente** en el mismo ciclo (no secuencial).
- **Objetivo de GRF = doble pico fisiológico de persona sana** (Winter/Perry), no de amputado — coherente con que la trayectoria capturada también es de sujeto sano.

## ✅ Alcance decidido
- **Control (2026-10-27):** control de fuerza en tiempo real sobre Fz y Fy. Falta probar latencia del lazo AMTI→RPi→ESP32 (decide tiempo real vs ILC). Método: (1) simular ambos con la latencia como variable para hallar el retardo máximo tolerable; (2) medir latencia real; (3) implementar el que corresponda; (4) comparar prótesis. Precedentes: Aubin et al. 2012 (lógica difusa sobre GRF vertical), Insam 2021 (hardware-in-the-loop).
- **Prótesis a comparar: 2 distintas, idealmente 3**, incluyendo la prótesis ACTIVA del laboratorio. No se promete generalizar a "cualquier prótesis".
- Entregable de comunicación: presentación de 30s a profesores, como proyecto (no tesis todavía).
- ⚠️ **Riesgos abiertos críticos:** (1) la prótesis activa tiene su propio controlador (máquina de estados); a 6x puede no activarse bien → falta modelo/firmware y si se puede fijar en modo pasivo/manual; (2) GRF objetivo es de persona sana pero la activa inyecta energía — decidir si se compara con el mismo objetivo; (3) Koehler-McNicholas 2017 no halló diferencias significativas en el momento distal del socket entre 3 tobillos (7 sujetos) → el sensor de interfaz podría no discriminar entre prótesis; (4) ILC por sí solo no rechaza perturbaciones dentro del ciclo, requiere planta repetible ciclo a ciclo.
- **Prótesis activa del lab:** NO es modelo comercial — la construyeron compañeros del lab, también opera a x6. Riesgo (1) baja (su controlador ya corre a x6 y es modificable), pero aparece: es prototipo (repetibilidad desconocida), hay que sincronizar su arranque/fase con el simulador, y compararla con pies comerciales equivale a "prototipo vs comerciales", no "qué prótesis conviene".
- Lazo sagital/plantar: dentro del alcance (guiado por plantilla + IMU).

## Instrumentación — estado
- **AMTI**: disponible, integrado con el simulador. Entrega **6 salidas analógicas** (3 fuerzas + 3 momentos) — confirmado por Luis.
- **IMU propio del simulador** (verifica ángulo del motor sagital): en proceso.
- **Sensores de distancia/desplazamiento (X, Y)**: en proceso — instalación en <2 semanas desde 2026-10-27 (vertical y horizontal); usos: medir desplazamiento real (rigidez/energía), comprobar posición comandada, verificar que el eje horizontal solo avance.
- **Sensor de presión plantar**: decidido construir un **arreglo FSR propio** (talón/mediopié/metatarso/dedos), no comprar plantilla comercial (XSENSOR/Tekscan/Moticon/Novel Pedar) — ninguna da salida analógica directa tipo AMTI ni API pública confirmada de streaming en tiempo real. El FSR da voltaje analógico real por sensor, leíble directo por ADC.
- El usuario tiene un XSENSOR Pro Foot & Gait (X4 Sensor Pack) — útil para grabación/análisis general, **no** planeado para el lazo de control. Su IMU integrado es un dispositivo distinto del IMU propio del simulador.
- **Sensor de interfaz muñón-prótesis**: proyecto aparte de Practicante 1, plazo diciembre 2026.
  - Sustituto del muñón (decidido por Luis): plataforma rígida que recibe compresión axial, sin costados ni tejido, conectada a la prótesis con adaptador piramidal; sensor entre plataforma y prótesis.
  - **CONFIRMADO (Luis, 2026-10-27): el sensor mide SOLO fuerza axial** (sin momentos ni cortante).
  - ⚠️ Problema de diseño (análisis propio, por estática, sin fuente publicada): si Fz/Fy se controlan al mismo objetivo y el ángulo sagital es la misma trayectoria fija, la fuerza axial en el pilón ≈ proyección del GRF sobre el eje del pilón + masa×aceleración (pequeña a x6) → casi fijada por el propio control, puede no diferenciar bien entre prótesis. Lo que sí cambia con GRF fijo: trayectoria del centro de presión (AMTI) → momentos en el encaje, y desplazamiento comandado (curva fuerza-deformación, energía). Opciones pendientes de decisión de Luis: (a) mantener sensor axial + analizar CoP y desplazamiento comandado (sin hardware nuevo); (b) sensor multiaxial; (c) estandarizar cinemática en vez de GRF.
  - Pico máximo decidido por Luis: **1500 N** (≈121 kg con pico esperado 126%BW). El proyecto **no hace ensayos de fatiga/durabilidad**; entre 1325 N (dato del paper, 157%BW de 86 kg) y 1500 N, subir de a poco.

## Energía — método decidido (sección 6.1 del doc)
- La energía **NO se calcula en tiempo real**; el control solo usa Fz y Fy. Se grava sincronizado: AMTI (6 canales), posición vertical/horizontal, IMU. Después se calcula CoP (con momentos de AMTI), se derivan velocidades, se integra potencia. Resultado por prótesis: curva de potencia + energía absorbida/devuelta/eficiencia, normalizadas al peso. CoP solo con Fz > 20 N (umbral del artículo de conferencia) para evitar división por Fz≈0.
- **Fórmula (forma publicada, Ray et al. 2018, DOI 10.1186/s12984-018-0347-1):** v_CoP = v_cm + ω×r_CoP; P_UD = F_grf·v_CoP + M_free·ω.
- **Versión del simulador** (sagital y=avance, z=vertical, punto A=unión prótesis-simulador, elaboración propia): v_CoP,y = v_A,y − ω(z_CoP−z_A); v_CoP,z = v_A,z + ω(y_CoP−y_A); P = Fy·v_CoP,y + Fz·v_CoP,z; E_abs=∫P<0, E_dev=∫P>0. M_free se anula (no hay giro vertical).
- Idea clave: **el control fija F igual para todas; la prótesis decide v y ω → las diferencias de energía son de la prótesis.**
- Validación: prueba del bloque rígido de suela curva → P≈0 (detecta errores de signo/ejes/sincronización/geometría de A).
- Formato en el doc (decidido por Luis): (1) qué fórmula se usa; (2) captura SOLO de ecuaciones 1-2 de Ray, sin texto; (3) relación término-por-término con el simulador + ecuación resultante; (4) qué se mide (E_abs, E_dev); (5) una gráfica ya medida (Ray Fig. 2). Sin η ni tabla de sensores adicional.
- η (work ratio) = de Childers & Takahashi 2018 (no de Ray). El sensor de interfaz (solo axial) NO entra en la fórmula de energía; sirve de comprobación: axial ≈ Fz·cosθ + Fy·senθ.
- Justificación del PORQUÉ medir energía (no solo el cómo): Zelik 2011, Childers & Takahashi 2018, Fey/Klute/Neptune 2012, Gardiner 2016 (detalle y DOIs en `HISTORIAL.md` si se necesitan).
- Método con los 3 ejes a la vez (Takahashi/Kepple/Stanhope 2012, DOI 10.1016/j.jbiomech.2012.08.017): P = Fy·vy + Fz·vz + M·ω, M=(xCoP−xA)·Fz−(zCoP−zA)·Fy. La prueba fija de Turner queda solo como validación de la rigidez.
- Limitaciones (2 viñetas, análisis propio): misma base de tiempo AMTI+sensores (resuelto leyendo todo con un ADC de ≥8 canales); bloque rígido → P≈0 detecta errores de signo/geometría.

## Prácticas
- **Solo una práctica formal de 15 semanas**: *"Desarrollo y caracterización de un arreglo de sensores resistivos de fuerza (FSR) para captura de presión plantar en simuladores de marcha protésica."* Cubre: diseño/fabricación/calibración del arreglo FSR con salida analógica; caracterización completa (linealidad, histéresis, repetibilidad, corrección de error por curvatura, ref. Ahmadizadeh & Menon 2019); verificación cruzada con IMU del simulador; integración física con primeras lecturas en marcha real. No diseña el lazo de control sagital.
- **Integración AMTI→Raspberry Pi en tiempo real**: ya no es práctica formal — la hace Luis mismo o un voluntario.
- Diseño/simulación del control vertical+horizontal puede empezar **ya**, independiente de la práctica — nada lo bloquea.
- Timing: entrega teórica marzo/abril 2027; práctica FSR arrancaría ~dic 2026 (15 semanas → mediados marzo 2027). **Resuelto:** esa entrega pide solo teoría/metodología, no datos reales — el calce funciona.

## Vacío de investigación — verificado con búsqueda extensa en OpenAlex
Nadie combina (a) control de GRF en lazo cerrado con plataforma de fuerza real (tipo AMTI) **y** (b) comparar la respuesta de fuerza de interfaz/socket entre **distintos** pies protésicos transtibiales bajo esa condición estandarizada. Antecedente más cercano: **Herlihy et al. 2026** (DOI 10.1088/1873-4030/ae8544) — interfaz socket-muñón, GRF vertical doble-pico, AMTI, pero **confirmado que tampoco cierra el vacío**: su control es lazo abierto con ajuste manual entre pruebas (cita: "the system operated open loop with respect to force during each trial... FAM displacement was adjusted iteratively between trials"), sin ILC ni control automático de lazo cerrado, y sin comparar prótesis distintas (una sola configuración + cadáveres). Útil para citar como "ni el antecedente más reciente (2026) usa control automático de lazo cerrado". Otros antecedentes que estrechan el vacío sin cerrarlo (Thiele 2015, Frossard 2013 transfemoral/rodillas, Chen 2022/2024, Zhang 2025, Guttler 2022, Sudeesh 2024): detalle completo en `HISTORIAL.md` § Auditoría del vacío de investigación.

## Referencias — reglas y estado (detalle completo en `HISTORIAL.md`)
- **Regla fija (2 condiciones):** entra a "fuerte/confirmada" solo si (1) DOI verificado y (2) Luis confirma que la leyó. Sin ambas, queda en "DOI verificado, lectura sin confirmar" — no se usa como respaldo final.
- **Fuerte/confirmada:** Herlihy 2026, `journal_copy.pdf`, `conferencia_copy.pdf`.
- **DOI verificado, lectura sin confirmar:** lista completa (20+ refs: Bó 2021, Wright 2016, Thiele 2015, Frossard 2013/2019, Chen 2022/2024, Aubin 2008/2012, Guo 2018, Hofstad 2004, van der Linde 2004, Fish 2006, Maikos 2026, Paz García 2026, Neumann 2012, Martinez-Villalpando 2007, etc.) — ver `HISTORIAL.md`.
- **Sin DOI, no citar:** Xu Zhen-yi 2014, Chevalier 2015.
- **Formato del doc:** documento (no presentación) — https://claude.ai/artifact/EqD1E8VF5qRtKRfDA7n2Dg. El .pptx (`lamina_respaldo_proyecto.pptx`) es versión anterior.
- **Regla de figuras:** en antecedentes, solo figuras publicadas en los papers citados (nunca dibujadas por Claude); diagramas propios van al final en anexo "elaboración propia".

## Plazos
- **Diciembre 2026:** sensor de interfaz (Practicante 1) instalado; arranque sugerido de la práctica FSR.
- **Marzo/abril 2027:** entrega "teórica" de la tesis (solo diseño+simulación, resuelto que no necesita datos reales).

## Entregables de la tesis (3 niveles)
1. Diseño + simulación del controlador multi-eje (modelo del simulador).
2. Implementación real con AMTI en el lazo (vertical+horizontal), mejora medible (RMSE/correlación/timing) vs. lazo abierto actual.
3. Validación estadística con repeticiones (ICC, CV), como en el paper de revista.

## ¿Se puede meter IA en la tesis?
Sí — antecedente: Raheema et al. 2021, ANFIS+PID para control de fuerza en prótesis transfemoral, mejor que PID solo. Mejora opcional del controlador, a evaluar después de tener el ILC básico funcionando, a decidir con la asesora.

## Arquitectura de hardware
- **Raspberry Pi** = cerebro/alto nivel. Genera/ajusta trayectoria, lee el AMTI. Aquí va la lógica ILC.
- **ESP32** = bajo nivel. Ejecuta STEP/DIR a los motores. No necesita rediseño para el Bloque 1.
- El simulador físico ya está listo para recibir este desarrollo.

## Herramientas de búsqueda
- `paper-search` (OpenAlex): falla en este entorno (sin jq en Windows). No reintentar.
- Alternativa que funciona: script Python directo a la API de OpenAlex (detalle en `HISTORIAL.md`). Reusar este patrón.
- Regla de uso: solo **buscan y organizan referencias**. El usuario lee y decide — no se redactan síntesis salvo pedido explícito.

## Pendiente de definir
- **Respuesta de Dante Elías al correo del 2026-10-31** (opinión/alcance del tema de tesis, DPB4 desde enero, extensión de apoyo económico a nov-dic).
- Confirmación de la asesora sobre el enfoque/título.
- Latencia real del lazo AMTI→RPi→ESP32 (decide tiempo real vs ILC).
- Pies pasivos disponibles para la 2.ª y 3.ª prótesis (Luis lo verifica en el lab).
- Carga de diseño del simulador (el artículo de conferencia no la reporta).
- Geometría del punto A (CAD) y convención de signos de Fy, θ y ω para la fórmula de energía.
- Qué medir para impacto clínico con GRF fijo: propuesta de Claude (rodamiento/CoP, energía absorbida/devuelta, sensor axial como verificación) — falta decisión formal de Luis.
- Si se incluye IA (ANFIS-PID u otra) como parte del controlador o solo como comparación/extensión futura.
- Prótesis activa del lab: cómo sincronizarla con el simulador, si se puede fijar en modo pasivo, su repetibilidad ciclo a ciclo.

## Nota sobre nivel del usuario
Luis recién está aprendiendo control — nociones básicas, no formación previa. Explicar conceptos (ILC, modelos dinámicos, ganancias, etc.) en términos simples, sin asumir vocabulario técnico previo.

## Preferencia de trabajo con Claude
Ir paso a paso: un tema puntual por intercambio, respuestas cortas, sin dump de información. Reforzado varias veces por el usuario.
