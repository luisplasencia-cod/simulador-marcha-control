# 01 — Criterio de "misma carga" y estadística para comparar pies (búsqueda 2026-11-25)

**Para qué:** definir qué significa "imponer la misma carga" y cómo probarlo con 2–3 pies.
**Estado de las fuentes:** ninguna leída por Luis. Según la regla del proyecto, NO son respaldo final todavía.
**Marcas:** [leí texto] = abrí el texto completo o una sección larga · [leí abstract] = solo el resumen oficial · [solo buscador] = cifra vista en el resultado del buscador, sin abrir la fuente · [dato del repo] = calculado aquí con archivos del proyecto.
**No repito** lo ya hallado en `tesis/VACIOS_Y_RELEVANCIA_CLINICA.md` ni en `reportes/2026-11-20_criterio_error_estandarizado.md` (bandas r/CMC, que no hay umbral estándar de RMSE). Solo corrijo dos datos de esos archivos (ver "Correcciones").
**Acceso:** PMC bloqueó la descarga directa; usé Europe PMC (mismo texto). MDPI y el repositorio del MIT bloquearon la descarga.

---

## A) Normas de ensayo de pies protésicos

### A1. ISO 22675 (ensayo cíclico de todo el apoyo)
- Edición vigente: **ISO 22675:2024 (3.ª ed.)**. La de 2016 está retirada. Hay adopción europea, EN ISO 22675:2025, idéntica. https://www.iso.org/standard/79620.html [leí texto]
- Lo que leí del borrador público (FDIS, cláusulas 1–6): https://cdn.standards.iteh.ai/samples/79620/9a3f6ccb59574c83a3ac8fabee67fdd4/ISO-FDIS-22675.pdf [leí texto]
  - El ensayo simula el apoyo completo, del contacto de talón al despegue.
  - La carga se define con dos perfiles. (1) Perfil de carga: el vector resultante de las fuerzas vertical y A-P (Fz + Fy). (2) Perfil de locomoción: el ángulo de la tibia en el tiempo.
  - La fuerza pulsante Fc(t) tiene dos máximos (F1cmax y F2cmax) y un mínimo intermedio (Fcmin). Es una curva de doble pico.
  - Los "Test Ranges" (R) fijan el perfil de locomoción según el uso previsto del pie.
  - La norma dice que cada pie queda *"free to develop its individual performance under load"*. Es decir, se impone la carga y el pie responde a su manera. Es la misma lógica de la tesis.
  - Define dos conceptos, sin dar cifras en la parte pública. "Exactitud del equipo": con qué exactitud se miden fuerzas, ángulos y frecuencia. "Exactitud del procedimiento": con qué tolerancia se aplican la fuerza y el ángulo, y se controla la frecuencia.
  - Advierte que la norma no sirve para elegir el pie de un paciente.
  - Las cifras están en las cláusulas no públicas (Tablas 8–9: fuerzas, ciclos, ángulos). **No las obtuve.**
- La norma corrige "debilidades" de ISO 10328. Entre ellas, una evolución de la carga poco realista entre los picos de talón y antepié. [leí texto, mismo FDIS]
- Un trabajo de elementos finitos reporta una mesa que gira de −20° a 40° y un pico de 130 %BW (764 N para la categoría de 60 kg). Tabucol et al. 2021, doi 10.3390/app12010097 [solo buscador; MDPI bloqueó el texto]
- ISO/TR 22676 es la guía para diseñar el equipo. Incluye diseños con manivela y el efecto de desviarse del perfil de ángulo. [solo buscador]
- Cómo lo controla un fabricante de equipos. El canal vertical va en lazo cerrado de desplazamiento, con control de la amplitud de los picos y control de fase entre canales. https://www.testresources.net/applications/standards/iso/iso-22675-fatigue-ankle-foot-device-prosthetic-test-equipment [leí texto]
  → En la práctica industrial se controlan **los picos y su momento**, no el error sobre toda la curva.

### A2. ISO 10328 (ensayo estructural; pruebas separadas de talón y antepié)
| Parámetro | Valor | Fuente |
|---|---|---|
| Nivel P5 (hasta 100 kg) | cíclico de 50 a 1330 N | Falbriard 2022 [leí texto] |
| Ángulos | antepié −20° / talón +15° en esa convención; otros textos dicen 20°/15° | Falbriard 2022 [leí texto]; Wernke 2022 [leí texto] |
| Ciclos | 2 × 10⁶ | Falbriard 2022 [leí texto] |
| Frecuencia usada | 2 Hz (Falbriard); 1 Hz en otros estudios | Falbriard [leí texto]; [solo buscador] para 1 Hz |
| Regla de frecuencia | ≤1 Hz con componentes no metálicos, ≤10 Hz si todo es metálico | revisión 1993, https://www.oandplibrary.org/poi/1993_03_180.asp [solo buscador] |
- Falbriard et al. 2022, PLoS ONE, doi 10.1371/journal.pone.0266656 [leí texto].
  - Su máquina aplicó 114–1320 N en vez de 50–1330 N, por el límite de carrera.
  - Lo reportaron como desviación y no dieron tolerancia.
  - **Lo que muestra:** se acepta reportar la desviación de la carga, pero no hay un % de tolerancia publicado.
- Jensen & Treichl 2007, doi 10.1080/03093640701210986 [leí abstract]: 1132 ensayos ISO 10328 en 21 modelos de pie de países de bajos ingresos. Ninguno pasó el protocolo más estricto.

### A3. ISO/TS 16955 (rigidez, energía y otros parámetros)
- Usa el sistema de coordenadas y las configuraciones de ISO 22675. Los ensayos están definidos para un pie de 26 cm y una persona de 70 kg. https://standards.iteh.ai/catalog/standards/iso/1435ef47-3ddd-440a-b0dc-341ef37c9a5c/iso-ts-16955-2016 [solo buscador]
- Calcula rigidez, brazo de palanca, longitud efectiva del pie y energía (integral de fuerza × desplazamiento). [solo buscador, misma fuente]
- Hay una 2.ª edición en borrador (ISO/CD 16955). https://www.iso.org/standard/92244.html [solo buscador]
- En el ensayo dinámico, la plataforma rota de −20° (contacto de talón) a +40° (despegue). Usa una celda de carga de 6 ejes a 1000 Hz. Wernke et al. 2022, doi 10.1177/20556683221123330 [leí texto]

### A4. Guía AOPA (Prosthetic Foot Project, 2010)
- Talón a 15°, quilla a 20°. Carga de 1246 N bajo control de fuerza. Wernke 2022 [leí texto]
- Umbral de energía para pie "dinámico": quilla >75 % y talón >82 %. Wernke 2022 [leí texto]
- Una copia secundaria dice 1230 N y ≥25 mm de desplazamiento. No coincide con 1246 N. [solo buscador, Scribd; sin verificar]
- El PDF oficial de AOPA (aopanet.org) da error 404 hoy.

### A5. Hallazgo clave: el método de ensayo cambia el resultado
- Starker et al. 2026, Med. Eng. Phys. 147:035002, doi 10.1088/1873-4030/ae33ba [leí abstract].
  - Comparan 5 métodos (AOPA, ISO 10328, ISO 22675, ISO 16955 y pie angulado) en 3 pies.
  - La cuasi-rigidez de talón y antepié cambia **hasta 24 %** según el método. Los autores dicen que eso equivale a ≈2 categorías de rigidez.
  - Las fuerzas A-P cambian hasta 161 %.
  - **2 de los 5 métodos no distinguieron entre los pies.**
  - Piden reportar el método, la alineación, la carga y la forma del bloque de talón.

**Conclusión A:** las normas imponen **niveles de fuerza (picos), ángulos y número de ciclos**. No encontré, en texto público, una tolerancia del tipo "la fuerza debe seguir la curva con error < X %". Esa cifra podría estar en las cláusulas pagadas de ISO 22675/10328. No la verifiqué.

---

## B) Fidelidad de la GRF en otros simuladores

| Simulador (fuente) | Muestra / condición | Métrica de fidelidad de la GRF | Valor | Marca |
|---|---|---|---|---|
| Sharkey & Hamel 1998, doi 10.1016/s0268-0033(98)00003-5 | 5 pies cadavéricos | fuerzas de tendón; picos de GRF | tendones dentro del 10 % de lo programado; pico vertical 110 %BW, "similar" a sanos | [leí abstract] |
| Aubin, Cowley, Ledoux 2008, doi 10.1109/tbme.2007.908072 | **pie protésico**, 1 transtibial, apoyo de 1.5 s, ILC proporcional | RMS de vGRF tras 6 iteraciones | **35 N** | [leí abstract] |
| Aubin, Whittaker, Ledoux 2012, doi 10.1109/TRO.2011.2164958 | 6 pies cadavéricos × 3 corridas finales, 75 %BW, apoyo de 2.7 s, control difuso | RMS de vGRF; magnitud y tiempo de los picos; valle; integral | **5.6 %BW**; picos sin diferencia significativa; valle 5.9 % más bajo; integral con 2.0 % de diferencia; versión anterior por ensayo y error: 30 %BW | [leí texto] |
| Whittaker et al. 2011, doi 10.1016/j.gaitpost.2011.02.011 | mismo robot, 18 corridas | RMS de vGRF | 5.9 %BW | [leí abstract] |
| Jackson et al. 2011, doi 10.1115/1.4003869 | robot, 10 posturas estáticas | banda de ±1 DE in vivo | vGRF dentro de ±1 DE | [leí abstract, parcial] |
| Natsakis et al. 2012, doi 10.1186/1757-1146-5-S1-O42 | 4 cadáveres × 5, apoyo de 0.8 s | RMS frente a in vivo | 22 % | [leí abstract] |
| Natsakis et al. 2015, doi 10.1016/j.jbiomech.2014.11.044 | 10 cadáveres, apoyo de 1 s, "control inercial" | R² y pendiente frente a 15 sanos | R² 0.956, pendiente 1.004 | [leí abstract] |
| Natsakis et al. 2015b, doi 10.1186/s13047-015-0081-x | repetibilidad antes/después de un cambio | R² entre repeticiones | GRF R² > 0.92 en los 3 ejes | [leí texto] |
| Wang et al. 2020, doi 10.1177/0954411920938902 | 6 cadáveres, apoyo de 5 s, PID + ILC | CMC de repetibilidad | GRF CMC > 0.89 | [leí abstract] |
| Baxter et al. 2016, doi 10.1002/jor.23169 | 5 cadáveres, entradas de sanos | correlación cruzada de cinemática | r 0.57–0.87; variabilidad in vitro ≈ in vivo | [leí abstract] |
| Herlihy et al. 2026, doi 10.1088/1873-4030/ae8544 | prótesis rígida (16 corridas) + 2 cadáveres (7) | pico de vGRF, cociente pico/valle, simetría entre picos, tasas de carga y descarga, contra controles con Kruskal–Wallis | pico 656.5 ± 80.0 N frente a 646.4 ± 43.1 N (p 0.892). Umbrales propios: pico > 640 N, pico/valle 1.25, simetría > 90 %, ±2.5 kN/s. **No reporta RMSE ni r de la vGRF** | [leí texto, parcial] |
| Insam et al. 2021, doi 10.3390/app11209492 | HIL de un pie, amputado simulado (modelo VPP) | solo cualitativa | reproduce la marcha cualitativamente, no cuantitativamente | [solo buscador] |
| Yang 2020, tesis de doctorado en ingeniería, Univ. de Bath | robot hidráulico, ILC extendido para la GRF, tobillos **pasivos y activos** | no visto | detecta cambios pequeños en la prótesis | [leí abstract] https://researchportal.bath.ac.uk/en/studentTheses/development-of-a-gait-simulator-for-testing-lower-limb-prostheses/ |
| Lecomte et al. 2021, doi 10.3390/app11125318 | máquina de rodadura frente a usuarios transtibiales | correlación | "buena" en terreno plano | [solo buscador] |

**Qué se reporta, en resumen:**
1. RMSE en %BW (o N) sobre todo el apoyo.
2. Magnitud y tiempo de cada pico y del valle.
3. Integral (impulso).
4. Tasas de carga.
5. Cociente pico/valle.
6. r, R² o CMC, sobre todo para la **repetibilidad**.

**Umbral aceptado:** ningún grupo da uno universal.
- Aubin 2012 y Herlihy 2026 usan "sin diferencia significativa frente a sujetos sanos".
- Aubin 2012 también usa "dentro de ±1 DE in vivo".

**Nuestros números, comparados (comparación no equivalente):**
- RMSE de 1.45 a 4.4 %BW, frente a 5.6–5.9 %BW, el mejor valor cadavérico hallado.
- Hay tres diferencias. Ellos trabajan con cadáver y tendones a 75 %BW. Su apoyo dura 2.7 s; el nuestro, ≈6 s. Su planta es otra.
- Aubin 2008 es el único caso con **pie protésico**: 35 N RMS. No hallé la normalización en %BW.

---

## C) La variabilidad natural como criterio de "misma carga"

**Sí hay antecedentes que usan esta lógica:**
- **Aubin 2012** [leí texto] la usa de dos formas.
  - Exactitud: la vGRF media in vitro cae dentro de ±1 DE de la media in vivo en casi todo el apoyo.
  - Precisión: la variabilidad entre corridas del mismo pie fue **menor que la variabilidad dentro del mismo sujeto** in vivo (su Fig. 8).
  - Es el antecedente más directo para el criterio.
- Baxter 2016: la variabilidad in vitro es parecida a la in vivo (en cinemática). [leí abstract]
- Jackson 2011: dentro de ±1 DE. [leí abstract]

**Cuánto varía la GRF en personas sanas:**
| Dato | Valor | Fuente |
|---|---|---|
| DE entre sujetos, Gutenberg (350 sanos, velocidad autoseleccionada) | 11.1 %BW (1.er pico), 10.0 (valle), 9.0 (2.º pico); media sobre la curva 8.5 %BW | [dato del repo] `control/referencia_grf/referencia_fz_gutenberg.csv` |
| DE entre sujetos en los picos, Fukuchi (24 jóvenes) | 0.50 m/s: 3.4 / 1.7 %BW; 1.24 m/s: 7.7 / 7.1 %BW | [dato del repo] `control/referencia_grf/resumen_velocidad_fukuchi.txt` |
| Variabilidad de los picos de Fz entre pasos (35 pasos seguidos, 10 sanos, cinta) | **crece con la velocidad** (sin cifras en el abstract) | Masani et al. 2002, doi 10.1152/japplphysiol.00969.2000 [leí abstract] |
| Error de medición de la plataforma de fuerza, misma sesión (20 jóvenes, 2 bloques de 5 pasos) | 1.er pico: SEM 12 N, diferencia mínima detectable 33 N (≈4.5 %). 2.º pico: SEM 9 N, MDD 26 N (≈3.5 %). ICC 0.986–0.992 | Mulligan & Milner 2025, doi 10.1371/journal.pone.0339481 [leí texto] |
| Coeficiente de repetibilidad de los picos (95 %) | ±53 a ±63 N | estudio de fiabilidad en hombres sanos (ResearchGate 298715040) [solo buscador] |
| Pasos para una media estable | 10 pasos no consecutivos | Hamill & McNiven 1990, citado en JSSM 2007 [solo buscador] |
| La cinética varía más que la cinemática | cualitativo | Winter 1984, doi 10.1016/0167-9457(84)90005-8 [solo buscador] |

**Lectura (inferencia mía, no la afirma ninguna fuente):**
- Nuestro RMSE (1.45–4.4 %BW) es menor que la DE entre sujetos de Gutenberg (≈8.5–11 %BW).
- En cambio, se parece a la DE de Fukuchi a 0.50 m/s (1.7–3.4 %BW). El criterio depende de **qué curva y qué velocidad** se usen de referencia (sigue pendiente de Luis).
- Ojo: comparar el RMSE de toda la curva con la DE en los picos mezcla métricas distintas.
- La comparación justa sería otra. Primero, calcular el RMSE entre **pasos consecutivos de una misma persona sana**. Las bases Fukuchi tienen 858 apoyos a 0.50 m/s. Luego usar ese valor como techo del error del simulador. **No está hecho;** es una propuesta.
- No encontré cifras publicadas del CV paso a paso de los picos de Fz en sanos que pueda citar con texto leído.

---

## D) Estadística para comparar 2–3 pies en banco

**1. Unidad de análisis = el pie, no el paso.**
- Con 2–3 pies, 100 pasos de cada uno no son 100 muestras del "modelo de pie". Hacerlo sería pseudorreplicación. Hurlbert 1984, doi 10.2307/1942661 [solo DOI verificado]
- Los pasos repetidos miden la **precisión** del banco sobre esa unidad.
- Atenuante: Turner et al. 2022 halló que dos pies del mismo modelo difieren ≈2.4 % en rigidez lineal. doi 10.1371/journal.pone.0268136 [leí texto, resumen de la página]

**2. Protocolos de repetición usados:**
- Turner 2022: 6 ciclos por pie y ángulo. Los 3 primeros son de acondicionamiento y se promedian los 3 últimos. [leí texto]
  - Este protocolo ya está en el protocolo k(F) del proyecto (no lo repito).
- Aubin 2012: 3 corridas "de aprendizaje" + 1 final, con 45 s de reposo. 3 series por pie; las corridas también acondicionan el tejido. [leí texto]

**3. Fiabilidad: qué índice usar.**
- **ICC** exige variación *entre objetos*. Con 2–3 pies no tiene sentido para compararlos. Solo sirve con muchas unidades o con sujetos.
  - Bandas: <0.5 pobre, 0.5–0.75 moderada, 0.75–0.9 buena, >0.9 excelente. Hay que reportar la forma de ICC usada. Koo & Li 2016, doi 10.1016/j.jcm.2016.02.012 [leí abstract]
- Para cada pie conviene otro conjunto:
  - **CV** entre pasos.
  - **SEM**.
  - **Diferencia mínima detectable**: MDC = 1.96·√2·SEM. Weir 2005, doi 10.1519/15184.1 [leí abstract]; la fórmula está aplicada en Mulligan 2025 [leí texto].
- Regla para estudios con personas: ≈50 participantes y ≥3 intentos. Hopkins 2000, doi 10.2165/00007256-200030010-00001 [solo buscador]. **No aplica tal cual a un banco.**

**4. Tamaño de muestra (número de pasos) por precisión, no por potencia.**
- Media de una métrica (RMSE, pico): la semiamplitud del IC 95 % es E ≈ 1.96·s/√n. Por tanto n ≈ (1.96/k)², con E = k·s.
  - k = 0.5 (precisión de media DE): n ≈ 16 pasos.
  - k = 0.25: n ≈ 62 pasos.
  - Es aritmética. Falta medir s (la DE entre pasos del banco).
- DE dentro del pie: IC ≈ ±1.96·s/√(2n(m−1)), con n unidades y m repeticiones. Bland, https://www-users.york.ac.uk/~mb55/meas/sizerep.htm [leí texto]
  - Con 1 pie y m = 20 pasos: ±32 % sobre la DE. Con m = 50: ±20 % (cálculo mío con esa fórmula).
  - Aviso: el ejemplo numérico de la página (n = 386 con m = 2) no cuadra con su propia fórmula. Uso solo la fórmula.

**5. Equivalencia frente a diferencia.**
- "Misma carga" es una **afirmación de equivalencia**. Un p > 0.05 en una prueba de diferencia NO prueba igualdad.
- Lo que corresponde es **TOST**: dos pruebas t unilaterales contra un margen ±Δ fijado **antes** del ensayo. Lakens 2017, doi 10.1177/1948550617697177 [leí abstract]
  - Si no hay un margen teórico, Lakens sugiere usar el efecto más chico que el estudio puede detectar.
- Candidatos para Δ (propuesta mía; ninguno es estándar):
  - (a) La MDC de la plataforma de fuerza: ≈26–33 N, 3.5–4.5 % del pico (Mulligan 2025).
  - (b) La variabilidad paso a paso de un sano (por calcular, sección C).
  - (c) El umbral propuesto el 2026-11-20 (≤5 % del pico).
- Para comparar curvas enteras: **SPM 1D** (paquete `spm1d`). Pataky 2012, doi 10.1080/10255842.2010.527837 [leí abstract]
  - SPM busca diferencias. No encontré una versión de equivalencia ya establecida para curvas de GRF.
  - Salida práctica: TOST sobre métricas escalares (RMSE, picos, impulso) + SPM para mostrar dónde difieren las curvas.
- Estructura que sale de esto (inferencia):
  - (i) **Equivalencia de la entrada:** la Fz impuesta es equivalente entre pies (TOST).
  - (ii) **Diferencia de la salida:** desplazamiento, energía o CoP difieren entre pies más que la MDC.
  - Esta es la lógica "misma carga, distinta respuesta" de ISO 22675.
- Modelos usados por otros: mixtos con el pie como efecto aleatorio (Aubin 2012, Turner 2022); Kruskal–Wallis + Dunn–Šidák (Herlihy 2026). Con 2–3 pies, un efecto aleatorio "pie" no se puede estimar bien (inferencia).

---

## Qué cambia para la pregunta de tesis

**La refuerza:**
- ISO 22675 tiene la misma filosofía: carga estandarizada y el pie responde libremente.
- Starker 2026 muestra que el método decide el resultado (hasta 24 %, y 2 de 5 métodos no distinguen pies). Eso justifica estandarizar la carga dinámica.
- Aubin 2012 da un criterio con antecedente: error menor que la variabilidad del propio sujeto.

**La obliga a precisar:**
1. **"Misma carga" hay que definirla en números.** Propuesta: métrica + margen + prueba. Por ejemplo, RMSE y picos dentro de ±Δ, probado por TOST, con Δ elegido antes de las pruebas.
2. **Alcance de "carga":** ISO 22675 impone el vector resultante (Fz + Fy) y el ángulo de tibia. Hoy solo se cierra Fz. Mientras Fy no esté en lazo cerrado, "misma carga" = misma Fz.
3. **Velocidad:** las normas cíclicas trabajan a ≈1–2 Hz; nosotros, 10 veces más lento.
   - Aubin atribuye a la baja velocidad la falta de vGRF justo tras el contacto de talón.
   - Un pie articulado con topes de goma (viscoelástico) puede responder distinto a baja velocidad (inferencia).
   - Conviene que la pregunta diga "a velocidad reducida".
4. **"En qué medida"** encaja bien con un resultado de exactitud (RMSE, picos) + repetibilidad (CV, MDC) por pie.

**Redacciones alternativas (para que Luis y su asesora decidan):**
- A (exactitud + criterio biológico): "¿Con qué exactitud y repetibilidad un control en lazo cerrado de la fuerza de reacción del suelo, que se adapta a la rigidez de cada prótesis, impone la curva de carga de una marcha sana —dentro de la variabilidad paso a paso de una persona sana— a prótesis transtibiales de distinta rigidez, a velocidad reducida?"
- B (equivalencia explícita): "¿Logra un control en lazo cerrado de la fuerza de reacción del suelo, adaptado a la rigidez de cada prótesis, imponer una carga equivalente (dentro de un margen predefinido) a prótesis transtibiales de distinta rigidez?"
- C (entrada igual, salida distinta): A o B + "...y bajo esa carga común, ¿qué diferencias mecánicas presentan las prótesis?"
  - Cuidado con el principio de Luis del 2026-11-25: la segunda parte no debe depender de las prácticas. Solo vale si la medición de desplazamiento y energía la hace el propio lazo.

---

## Correcciones a datos ya anotados en el proyecto
- **Aubin 2008:** el reporte del 2026-11-20 dice "RMS de Fz 78.7 → 9.4 N" (tomado del buscador). El abstract oficial dice **35 N tras 6 iteraciones**, con un pie protésico y apoyo de 1.5 s. [leí abstract]
- **META Arc:** `VACIOS_Y_RELEVANCIA_CLINICA.md` lo cita con doi 10.1177/0309364620917838. Según Crossref, ese DOI es **Ernst et al. 2020**, "Characterizing adaptations of prosthetic feet in the frontal plane". El estudio META Arc con AOPA + ISO 16955 es **Wernke et al. 2022, doi 10.1177/20556683221123330** [leí texto]. No edité ese archivo.

## No encontrado
- Cifras de ISO 22675:2024: tolerancias de fuerza y ángulo, frecuencia, número de ciclos, forma exacta de Fc(t). Están en las cláusulas pagadas.
- Cifras de "exactitud del equipo/procedimiento" de ISO 10328.
- Cualquier norma o artículo con una tolerancia de seguimiento **sobre toda la curva** de GRF (RMSE < X %).
- CV paso a paso de los picos de Fz en sanos con texto leído. Masani 2002 lo calcula, pero no abrí sus tablas.
- Un banco de prótesis con GRF en lazo cerrado que compare **varios pies** y reporte RMSE en %BW + r. Aubin 2008 usa un solo pie; Herlihy 2026, una prótesis rígida; Yang 2020 no muestra cifras en el abstract.
- Una prueba de equivalencia aplicada a curvas completas de GRF (versión de equivalencia de SPM).
- El texto completo de Insam 2021, Lecomte 2021, Tabucol 2021 (MDPI bloqueado) y de la tesis del MIT sobre un equipo ISO 22675 (Liang 2019, https://dspace.mit.edu/handle/1721.1/123211; descarga bloqueada).
