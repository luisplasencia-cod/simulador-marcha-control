# Historial detallado — Control del Simulador de Marcha

Este archivo NO se carga automáticamente como contexto de sesión (a diferencia de `CLAUDE.md`). Contiene el detalle completo de auditorías, contrastes abstract-por-abstract, búsquedas y razonamiento descartado. Léelo con la herramienta Read cuando se necesite el detalle; `CLAUDE.md` tiene el resumen vigente con punteros aquí.

## Contraste de afirmaciones vs. resumen (2026-10-26), para `lamina_respaldo_proyecto.pptx`
- Hofstad 2004: el resumen dice "no hay consenso clínico claro sobre los criterios de prescripción" (NO "no existe criterio objetivo"; corregido la redacción).
- Maikos 2026 y Paz García 2026: las medidas de desempeño no distinguen entre dispositivos (Paz García solo para pies ESR, 10 sujetos K3, marcha plana); biomecánica sí fue sensible en Maikos.
- Aubin 2008 (⚠️ estrecha el vacío): su resumen dice que ya hubo ILC proporcional sobre la GRF vertical con un pie protésico (datos de un amputado transtibial), RMS 35 N tras 6 iteraciones, robot paralelo 6 GDL. El resumen no reporta Fy. Novedad defendible = Fz+Fy simultáneos + comparación entre dispositivos, no "ILC con pie protésico".
- Guo 2018: ni OpenAlex ni Crossref traen resumen; solo el título ("ILC ... sistema de carga electrohidráulico de un simulador de marcha"). Se retiró de la lámina.
- Fish 2006: resumen habla de falta de investigación de resultados y de ECA, perspectiva de aseguradores; NO dice explícitamente "piden medidas objetivas" (ajustada la redacción).
- Koehler-McNicholas 2017: sin diferencias en momento distal del encaje entre 3 tobillos, en pendientes, 7 sujetos (no "marcha libre" general).
- Todo contrastado solo con resúmenes, salvo Herlihy 2026 (texto completo). `validate.py` de la skill no corre bien aquí (error de esquema idéntico en todas las partes, incl. el maestro); el archivo sí abre en PowerPoint y se renderizó sin desbordes.
- Figuras de los papers en la lámina (2026-10-26): el deck tiene 6 láminas (2 y 3 = evidencia visual). Solo se reutilizaron figuras con licencia abierta leída en el propio PDF: Maikos 2026 Fig. 5 (CC0), Koehler-McNicholas 2017 Fig. 4B (CC0), Herlihy 2026 Fig. 6 (CC BY 4.0). NO se usaron figuras de Aubin 2008, Guttler 2022, Neumann 2012, Fish 2006 ni Hofstad 2004 (de pago o sin licencia de reutilización). Insam 2021 y Paz García 2026 (CC BY según OpenAlex) y Zhang 2025 (CC BY) quedan disponibles, pero MDPI devuelve 403 a descargas automáticas: habría que bajarlos desde el navegador. Recortes en el scratchpad (`out/`).

## Auditoría completa del doc (2026-10-27) — correcciones hechas tras contrastar con las fuentes
- Maikos 2026: en su discusión (p. 11) el Timed Up and Go sí difirió entre dispositivos, pero por debajo del cambio mínimo detectable → el doc dice "casi no distinguen", no "no distinguen".
- Zhang 2025 estrecha más el vacío: su Fig. 2 muestra muñón simulado + encaje + celda de carga entre encaje y pilón sobre banco de doble pico. En su Fig. 3 la celda de carga va a la adquisición de datos; la fuerza se ajusta por posición de placas (no lazo cerrado sobre GRF). Diferencia defendible: ILC de Fz+Fy con plataforma de fuerza + comparación entre dispositivos.
- Nuevas referencias verificadas en Crossref: Aubin et al. 2012 (DOI 10.1109/TRO.2011.2164958, control difuso de la GRF vertical) y Winter 2009 (libro, DOI 10.1002/9780470549148, referencia del GRF objetivo). Perry (Gait Analysis) no tiene DOI de libro → no se cita.
- Frossard 2019 Fig. 1 (CC BY) reemplaza al diagrama de puntos de Maikos en el problema clínico: transductor entre encaje y tobillo, fuerza en el eje largo del muñón con doble pico, posible vínculo con daño de piel y lesiones de espalda/cadera/rodilla.
- Simuladores con figura en el doc (solo referencias citadas y con licencia): simulador propio [L] (Figs. 1 y 3, uso interno), Herlihy [5] Fig. 1, Insam [6] Figs. 6a y 2, Zhang [7] Figs. 2 y 3. Aubin y Guttler sin figura (de pago).
- Contradicción identificada entonces (ya resuelta en sesión posterior, ver CLAUDE.md "Revisión crítica"): "solo ILC, sin capa de tiempo real" chocaba con el plan B de tiempo real si el ILC no converge en 20 iteraciones.

## Auditoría del vacío de investigación — antecedentes de banco (2026-10-26)
Búsquedas solo en OpenAlex (palabras clave sobre título/abstract) + "citado por" desde Insam 2021 y Aubin 2008. PubMed devolvió 0 (consultas largas, reintentar con términos cortos); Semantic Scholar dio error 429 (límite de tasa).
- Zhang, Xu, Gan, Song 2025 (DOI 10.1016/j.bbe.2025.10.004, OA): aparatos de carga cíclica de doble pico para prótesis de miembro inferior (talón y antepié con dos placas), fuerza controlada ajustando posiciones de placas y carrera del actuador; enfoque de durabilidad vs ISO 10328 sinusoidal.
- Guttler, Poliakov, Pakhaliuk 2022 (DOI 10.1109/edm55285.2022.9855100): banco-simulador de marcha Gough-Stewart (6 actuadores) para probar pies, rodillas y prótesis transtibiales/transfemorales, incl. ISO 10328; plantea probar prótesis activas con el banco como "humano".
- Sudeesh, Shunmugam, Sujatha 2024 (DOI 10.1016/j.medengphy.2024.104254): simulador compacto, solo 3 GDL sagitales, suficientes para probar rodillas; hardware-in-the-loop.
- Kist et al. 2023 (DOI 10.1007/978-3-031-36694-9_5, OA; sin abstract en OpenAlex): sustructuración híbrida en tiempo real hacia pruebas de pies protésicos (grupo de Insam/Rixen). Contenido NO verificado.
- Kampouris et al. 2023 (DOI 10.1007/978-3-031-44097-7_16): "Biomimetic Rig for Simulating Human Gait Cycles"; sin abstract, NO verificado.
- Fuentes nuevas para el pitch de 30s: Maikos 2026 (DOI 10.1371/journal.pone.0352644, ensayo cruzado multisitio, 91 amputados, 3 tipos de dispositivo ESR/articulado/motorizado); Insam 2021 (DOI 10.3390/app11209492, primer hardware-in-the-loop de pie protésico en banco, co-simulación VPP); Richter 2014 (DOI 10.1016/j.apm.2014.06.006, contenido NO verificado, sin abstract en OpenAlex); Fiumalbi 2022 (DOI 10.3390/s22051731) y Tian 2019 (DOI 10.1109/tmech.2019.2911685), solo abstracts, sustentan riesgo de reconocimiento de fase en prótesis motorizadas.

## Revisión crítica (pre-mortem) — razonamiento completo de las decisiones cerradas
- **Timing marzo/abril 2027:** la entrega de ese curso pide solo teoría/metodología, no resultados reales. Ya no es riesgo de cronograma.
- **Integración AMTI→Raspberry Pi en tiempo real:** confirmado que NO es riesgo — Luis la hace él mismo, depende solo de él.
- **Sobrestimación de pico (157%BW vs ~126%BW, dato del paper de conferencia):** se toma solo como referencia de contexto, no como algo que el controlador deba "corregir". El target real sigue siendo el GRF fisiológico doble-pico de bases confirmadas (Winter/Perry), no ese 126%.
- **Validación del ILC con 2 ejes acoplados (Fz+Fy simultáneos):** el antecedente (Aubin 2008) solo probó 1 eje. No hay más literatura que lo resuelva — se vuelve parte del aporte/novedad de la tesis.
- **Velocidad actual del simulador:** confirmado por Luis, ~6x más lento que la marcha real (no el ~30x del paper de conferencia, probablemente de un modo de prueba distinto o el sistema mejoró desde esa publicación). Confirmado también con la cuenta: 20 pruebas de ILC ≈ 2 minutos reales, consistente con 6x.
- **Criterio de salida del ILC:** 20 iteraciones toman ~2 min reales (costo bajísimo) → se corre hasta 20 iteraciones; si no converge, pivota a control de fuerza en tiempo real (PID directo, plan B).
- **¿Es el ILC el método más adecuado?** Evaluado: ILC tiene el antecedente directo más fuerte (Aubin 2008, Guo 2018) pero es conceptualmente más complejo para alguien que recién aprende control. Alternativa más simple: PID en tiempo real sobre error de Fz/Fy (viable porque 6x da margen de cómputo). Decisión: ILC como método principal, PID en tiempo real como plan B si no converge en 20 iteraciones.
- **Modelo dinámico para la simulación del controlador:** evaluado modelo ideal puro (riesgo sim-to-real) vs multicuerpo completo (demasiado trabajo de modelado) vs modelo lumped (1 GDL por eje) con fricción Coulomb+viscosa y backlash explícitos, calibrados con mediciones reales ("gray-box"). Se eligió gray-box: captura efectos no-ideales ya identificados como riesgo real, sin costo de modelar cada pieza desde cero.

## Referencias — categorías de verificación (detalle)

### Regla fija de referencias (2 condiciones)
Toda referencia entra a "literatura fuerte/confirmada" solo si cumple AMBAS: (1) DOI verificado o texto completo confirmado; (2) Luis confirma explícitamente que la leyó. Mientras no haya confirmación de lectura, queda en "DOI verificado, lectura sin confirmar" — no se presenta como respaldo final.

### Acuerdo 2026-10-26: etapa del pitch = solo verificar existencia
Para presentar y plantear la idea basta que Claude verifique que cada referencia existe (DOI resuelve, autor/año/título coinciden). Textos de pago (Neumann 2012, Frossard 2013) se dejan por ahora. Una vez aceptado el proyecto, Luis hace la lectura completa de cada paper; solo entonces pasan a "fuerte/confirmada". En el pitch, citarlas como antecedentes sin atribuirles más de lo que dice su abstract.

Existencia verificada con Crossref (2026-10-26), título/autor/año coinciden: Hofstad 2004, van der Linde 2004, Fish 2006, Maikos 2026, Paz García 2026, Aubin 2008 ("Gait Simulation via a 6-DOF Parallel Robot With Iterative Learning Control"), Guo 2018 ("...electro-hydraulic loading system of a gait simulator", Mechatronics), Herlihy 2026, Insam 2021, Zhang 2025, Guttler 2022, Sudeesh 2024, Koehler-McNicholas 2017, Neumann 2012, Frossard 2013 ("Load applied on bone-anchored transfemoral prosthesis"), Frossard 2019 (título real: "Kinetics of Lower Limb Prosthesis: Automated Detection of Vertical Loading Rate"), Richter 2015 (Crossref lo fecha en 2015, no 2014; contenido sin verificar).

### Literatura fuerte/confirmada (DOI + leída por Luis)
- Herlihy et al. 2026 (DOI 10.1088/1873-4030/ae8544) — leída completa en sesión. Ver detalle del vacío de investigación en `CLAUDE.md`.
- `journal_copy.pdf` y `conferencia_copy.pdf` (papers propios del labo) — leídos completos.

### DOI verificado, lectura sin confirmar (no usar como respaldo final todavía)
- Bó, Casas, Cucho-Padín, Hayashibe & Elías 2021 (DOI 10.3390/app112311095) — estrategias de control para simulador de marcha tipo Stewart-Gough.
- Wright, Macefield, van Schaik & Tapson 2016 (DOI 10.3389/fnins.2016.00312) — review de control en lazo cerrado para neuroprótesis.
- Thiele et al. 2015, Frossard et al. 2013 (DOI 10.1682/jrrd.2012.04.0062), Chen et al. 2022/2024 (DOI 10.3390/app12030986, 10.1007/s42979-023-02485-7), Aubin et al. 2008 (DOI 10.1109/tbme.2007.908072), Guo et al. 2018 (DOI 10.1016/j.mechatronics.2018.07.011) — todas con DOI, pendiente confirmación de lectura.
- Hofstad 2004, van der Linde 2004, Fish 2006, Maikos 2026, Paz García 2026 (justificación clínica) — DOI verificados, pendiente confirmación de lectura.
- Frossard, Jones, Stewart, Leggat, Schuetz et al. 2019 (DOI 10.3390/prosthesis1010004, open access) — texto completo leído por Claude. Para verificar tú: Introducción, PDF pág. 3 (estudios que validaron la medición directa con celda de carga: fuerzas y momentos comparables a los de plataforma de fuerza + dinámica inversa) y PDF pág. 2 (la dinámica inversa es sensible a las propiedades inerciales de los componentes protésicos). Es una afirmación de introducción, cualitativa, apoyada en referencias de ese grupo.
- Neumann, Yalamanchili et al. 2012 (DOI 10.1177/0309364612436408, Prosthet Orthot Int, NO open access) — solo abstract leído: un transductor triaxial entre encaje y pilón detectó diferencias de carga entre pies protésicos de distinto diseño (gráficas fuerza resultante vs momento resultante), en 4 amputados caminando libre. Es la evidencia más cercana de que las diferencias entre pies aparecen en fuerza+momento; pero con marcha libre (el GRF también cambia), no con GRF estandarizado. Falta texto completo (acceso institucional).
- Martinez-Villalpando & Herr 2007 (DOI 10.1109/iembs.2007.4353386) — solo abstract: el GRF vertical se estimó con sensores embebidos en la prótesis (análisis estático) con correlación >0.94 respecto al laboratorio.
- Descargados pero NO usados como evidencia (solo revisión parcial): Hashimoto 2023 (DOI 10.1038/s41598-023-27438-1) y Klute 2024 (DOI 10.3389/fresc.2024.1354144), sobre momentos de reacción en el encaje y alineación.

### Sin DOI (no citar bajo ninguna circunstancia hasta conseguirlo)
- Xu Zhen-yi 2014 — "A multi-axis motion and force control system for dynamic foot biomechanical simulator" (OpenAlex ID W2361481705, sin DOI, probable revista china sin DOI indexado). Describe ILC multi-eje (5 DOF) en un simulador biomecánico de pie, validado en Simulink con una prótesis. Relevante porque podría matizar el argumento de "probar ILC con 2 ejes acoplados = parte de la novedad".
- Chevalier et al. 2015 ("Closed-loop identification of a multivariable dynamic knee rig") — probable IFAC-PapersOnLine, buscar DOI ahí.

## Justificación clínica — detalle de fuentes
- Hofstad et al. 2004 (Cochrane, DOI 10.1002/14651858.cd003978.pub2) y van der Linde et al. 2004 (DOI 10.1682/jrrd.2003.06.0102): no hay consenso clínico / hay vacíos de evidencia en criterios de prescripción de pie protésico.
- Fish 2006 (DOI 10.1097/00008526-200601001-00017): desde aseguradoras, pide explícitamente medidas objetivas de calidad/función protésica.
- Maikos et al. 2026 (DOI 10.1371/journal.pone.0352644) y Paz García et al. 2026 (DOI 10.3390/prosthesis8030023): evidencia muy reciente de que las pruebas funcionales estándar son insensibles a diferencias entre pies protésicos, mientras que los parámetros biomecánicos sí lo son.

## Otras referencias verificadas con detalle de abstract
- Hansen et al. 2006 (10.1080/03093640600816982: acortar el rodamiento reduce el momento de dorsiflexión y aumenta el primer pico de GRF del miembro sano, 14 usuarios transtibiales).
- Agrawal et al. 2020 (10.1097/JPO.0000000000000334: ningún estudio previo comparó la trayectoria del centro de presión entre diseños de pie dinámico).
- Turner et al. 2022 (10.1371/journal.pone.0268136: hay pocos datos objetivos para elegir la categoría de rigidez y los clínicos dependen del fabricante; 56 pies ensayados; Fig. 5 — "la rigidez medida no siempre sigue el orden de categorías del fabricante").
- Childers & Takahashi 2018 (10.1038/s41598-018-23705-8: más retorno de energía → más propulsión y menos colisión en el miembro sano, 5 sujetos; Tabla 1: Pro-Flex −0,23 J/kg almacenada / 0,16 devuelta / ratio 0,71; Vari-Flex −0,18 / 0,11 / 0,60; diferencia entre pies significativa en almacenada p=0,022 y devuelta p=0,045, NO en work ratio p=0,584).
- Martini et al. 2020 (10.3390/s20051448: plantillas de presión estiman en tiempo real el centro de presión anteroposterior, comparado con plataforma de fuerza).
- Rattanasak et al. 2022 (10.3390/s22114242: plantilla con sensores de presión detecta fases de marcha para controlar una prótesis transtibial, 81,43%).
- Peeters et al. 2013 (10.1177/0954411913490455: simulador que controla la cinemática sagital de la tibia con un modelo que considera la morfología del pie; centro de presión repetible).
- Cudejko et al. 2023 (10.1038/s41598-023-41622-3): plantillas de presión dan trayectoria anteroposterior del centro de presión comparable a plataforma, pero subestiman la fuerza vertical → plantilla sirve para el eje sagital (zonas/progresión), AMTI para Fz y Fy.
- Datasets públicos para objetivos sin captura propia: Gutenberg Gait Database / Horst et al. 2021 (10.1038/s41597-021-01014-6, GRF 3D + CoP, 350 sanos); UNB StepUP-P150 / Larracy et al. 2025 (10.1038/s41597-025-05792-1, presión plantar alta resolución, 150 personas, >200 000 pasos); GaitRec / Horsak et al. 2020 (10.1038/s41597-020-0481-z, GRF de 211 sanos y 2084 pacientes).

## Formato del documento principal — decisión y regla de figuras
- **Formato decidido (2026-10-27): documento, no presentación.** Luis pidió todo en un doc ordenado (ver link en CLAUDE.md). El .pptx (`lamina_respaldo_proyecto.pptx`) queda como versión anterior.
- **Regla de figuras (2026-10-27):** en antecedentes solo se usan figuras y diagramas publicados en los papers citados (nunca dibujados por Claude). Los diagramas propios del proyecto van al final, en un anexo marcado "elaboración propia". El diagrama del lazo ILC se movió al anexo del doc.
- Neumann 2012: abstract confirmado también desde la página de SAGE/Ovid (4 amputados K3–K4, transductor triaxial distal al encaje); texto completo sin leer.

## Herramientas de búsqueda — detalle
- `paper-search` (plugin OpenAlex vía `search.sh`/`paper.sh`): falla en este entorno (`jq: command not found`, no hay jq en git-bash/Windows). No reintentar.
- Alternativa que funciona: script Python (`urllib`, sin dependencias) que pega directo a la API de OpenAlex (`https://api.openalex.org/works?search=...`), guarda JSON en UTF-8 en el scratchpad, se lee con Read. Reusar este patrón para futuras búsquedas.
