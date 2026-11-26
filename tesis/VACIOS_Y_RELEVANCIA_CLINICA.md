# Vacíos de investigación y relevancia clínica (búsquedas 2026-11-25)

Material para el planteamiento del problema, la justificación y el estado del arte de la tesis.
**Estado de las referencias:** encontradas por búsqueda web; **sin lectura de Luis** → según la regla del proyecto, NO son respaldo final hasta que él las lea (y se verifique el DOI). Lo marcado "inferencia" no lo afirman las fuentes.

> **⚠️ CORRECCIONES (2026-11-25, informe `investigacion/03_...md`, sin verificar por Luis):** (a) doi 10.1177/0309364620917838 sería Ernst 2020 (plano frontal), NO la revisión META Arc → META Arc = **Wernke et al. 2022, doi 10.1177/20556683221123330** (informe 01); además Aubin 2008 = 35 N RMS tras 6 iteraciones, no "78.7 → 9.4 N" (corrige `reportes/2026-11-20_criterio_error_estandarizado.md`); (b) PMC4342001 = Gard 2011 y NO trae el dato "SACH de 28 cm actúa como <20 cm" (§3) → buscar la fuente real; (c) par.nsf 10251699 es el trabajo LLTE de Olesnavage, no de cuasi-rigidez (§3); (d) §3 queda DEMASIADO FUERTE: ISO 22675 + ISO/TS 16955 ya imponen carga + ángulo de tibia en máquina y calculan longitud efectiva, rigidez y energía. Lo nuevo es la GRF de marcha sana impuesta en lazo cerrado y adaptada a la rigidez (Fz/Fy separados + CoP de 6 canales).

## 1. Prescripción de pies protésicos: sin evidencia objetiva (respalda la relevancia clínica)
- Cochrane CD003978 (Hofstad 2004, act. 2010): no hay evidencia para criterios precisos de prescripción de mecanismos tobillo-pie. https://cochranelibrary.com/cdsr/doi/10.1002/14651858.CD003978.pub2/pdf/CDSR/CD003978/CD003978_abstract.pdf
- Highsmith et al., JRRD 2016: no se pueden dar recomendaciones clínicas por falta de evidencia de alta calidad; muestras pequeñas. https://typeset.io/pdf/prosthetic-interventions-for-people-with-transtibial-3yc25mixce.pdf
- Frontiers in Rehabilitation Sciences 2023: la prescripción se rige por el juicio del equipo; estudios contradictorios; faltan medidas objetivas. doi 10.3389/fresc.2023.1235693
- Müller 2019 (rev. sistemática, potencia de despegue SACH/ESR/motorizados): elegir pie es difícil por confusores — condición del usuario, alineación, encaje; muestras demasiado chicas para un modelo multifactorial. https://pmc.ncbi.nlm.nih.gov/articles/PMC6863538
- Protocolo Cochrane (Vanicek, actualización): se prescribe por costo o juicio clínico; faltan protocolos claros. https://pmc.ncbi.nlm.nih.gov/articles/PMC8762647
- Gardiner 2016 (metaanálisis, 10 estudios): ESR algo más eficiente que SACH, efecto pequeño (costo de transporte 97,3 %). https://salford-repository.worktribe.com/output/1408903
- Niveles K (CMS): clasifican a la persona, no prescriben pie; K3 sin restricción de pie. https://www.cms.gov/Medicare/Coverage/Determinationprocess/Downloads/Llp_Consensus_Document.pdf
- Inferencia: los ensayos cruzados con 2–3 semanas de habituación mezclan adaptación del usuario con efecto del pie.

## 2. El ensayo mecánico es más objetivo que el análisis de marcha con personas
- Revisión de ensayos mecánicos (Prosthetics and Orthotics International 2020; estudio META Arc con ISO 16955 + AOPA): más objetivo y reproducible que el análisis de marcha para clasificar pies. doi 10.1177/0309364620917838
- MIT (preprint Research Square 2021), misma idea. https://www.gear.mit.edu/s/2021-Research-Square-preprint.pdf

## 3. Descriptores clínicos del pie: NINGUNO se mide bajo carga de marcha dinámica estandarizada (vacío central)
- Forma de rodadura (roll-over shape), Hansen & Childress: trayectoria del CoP en el marco de la pierna; explica por qué cada pie necesita otra alineación. https://experts.umn.edu/en/publications/prosthetic-foot-roll-over-shapes-with-implications-for-alignment-/
- Longitud efectiva del pie (de la forma de rodadura): mucho menor que la nominal (SACH de 28 cm actúa como <20 cm); arco más corto → menor momento de dorsiflexión y mayor 1.er pico de GRF vertical en la pierna sana. https://pmc.ncbi.nlm.nih.gov/articles/PMC4342001
- Cuasi-rigidez de tobillo: pendiente momento–ángulo. https://par.nsf.gov/servlets/purl/10251699
- La forma sola no basta: pies con forma de rodadura idéntica dan cinemáticas distintas. https://www.gear.mit.edu/s/2023-JBE.pdf
- Hallazgo de la búsqueda: los descriptores se miden en ensayos cuasi-estáticos o con sujetos; ningún marco los mide bajo GRF dinámica de marcha estandarizada ni los convierte en clase funcional para prescribir.
- **Conexión con la tesis:** el simulador tendrá CoP (AMTI) + ángulo sagital → puede medir forma de rodadura, longitud efectiva, rigidez y energía de cada pie bajo la misma carga de marcha sana.

## 4. Pie articulado vs. fibra de carbono en el mismo banco y misma carga: no encontrado
- Womac, Neptune & Klute: 5 fabricantes, rigidez/energía muy no lineales en sagital y coronal; un protocolo solo sagital no capta lo coronal (**limitación a declarar**: el simulador trabaja en el plano sagital). https://sites.utexas.edu/neptune/wp-content/uploads/sites/6031/2020/07/poi433.pdf
- META Arc: limitación declarada = pies de conveniencia, de largo y rigidez distintos → piden comparaciones equiparadas. doi 10.1177/0309364620917838
- Estudio 2025 multiaxial vs eje único vs SACH, con sujetos (no banco); protocolo no confirmado. https://iasj.rdd.edu.iq/journals/uploads/2025/08/25/eae0909475459b6ab66a1245314c0166.pdf
- No se encontró comparación articulado vs fibra de carbono en el mismo simulador bajo la misma carga impuesta.

## 5. Contexto social (Perú / países de ingresos bajos y medios)
- OMS: solo 5–15 % de quienes necesitan prótesis en estos países acceden a una; estándares OMS-ISPO 2017. https://www.who.int/publications/i/item/9789241512480
- ISO 10328 no considera factores ambientales/socioculturales; muchos pies locales no pasan la ISO y aun así duran años. https://opedge.com/iso-testing-may-not-detect-wear-in-sach-foot/
- Pie SACH de caucho natural ≈16 USD, no completó la batería ISO. https://pmc.ncbi.nlm.nih.gov/articles/PMC6453060
- Perú: INR "Adriana Rebaza Flores" estudió amputados 2018–2019 (cifras no obtenidas) https://revistas.upch.edu.pe/index.php/RMH/article/download/5761/5807/19406 ; tesis PUCP estima ≈S/ 12 500 una prótesis robótica transtibial https://repositorio.pucp.edu.pe/index/handle/123456789/181388 . Sin datos oficiales MINSA/EsSalud/CONADIS hallados.
- SACH como opción básica en la región (SENADIS Chile; estudio colombiano: poca energía almacenada). https://www.redalyc.org/journal/2913/291376231006/291376231006.pdf

## 5b. Costo: ¿vale la pena la fibra de carbono? y pie barato equivalente (idea de Luis, 2026-11-25)
- Precios (fuentes no académicas, sin Perú): SACH ≈80–100 USD (Walmart; scienceinsights); ESR de carbono ≈5 000–15 000 USD (guía de consumo) / "miles de dólares" (investigación); articulado: sin precio hallado ("algo más caro que SACH", OUHSC). Catálogos Ottobock/Össur no publican precios. → **Pedir cotizaciones locales en Perú.** https://scienceinsights.org/how-much-does-a-prosthetic-foot-cost-prices-insurance/
- **No hay evaluación económica formal (costo-utilidad) de los pies ESR.** En marcha, consumo de O₂ y eficiencia similares entre pies; en carrera el ESR sí mejora. https://link.springer.com/doi/10.1186/s12984-019-0508-x · ESR prescritos ≈30 años con evidencia limitada (JRRD) https://pmc.ncbi.nlm.nih.gov/articles/PMC4302415
- SACH es el pie más usado del mundo (barato, fácil de fabricar). https://www.gear.mit.edu/s/2021-Research-Square-preprint.pdf
- **Pies baratos que replican a caros:** MIT GEAR (Olesnavage, Winter): métrica LLTE (error de trayectoria de la pierna bajo una GRF típica CALCULADA vs marcha sana), pie de nylon 6/6 <100 USD, objetivo igualar al Jaipur Foot. https://www.gear.mit.edu/s/2018-JMD.pdf · https://www.gear.mit.edu/s/2023-JMD.pdf · https://par.nsf.gov/servlets/purl/10407971 — Duke: impreso 3D + fibra de carbono, energía similar al Renegade MX https://scholars.duke.edu/individual/pub1331391 — Polimi 2024: compuesto impreso 3D guiado por rigidez https://re.public.polimi.it/retrieve/7e84203d-cefb-4f11-9316-01b8c7ea89b3/1-s2.0-S0263822324001818-main.pdf — NCT06938087: impreso 3D vs Pro-Flex XC con ISO-TS 16955.
- **Vacío: nadie usó un simulador de marcha con carga estandarizada IMPUESTA para validar que un pie barato equivale a uno caro** (validaciones existentes: cuasi-estáticas ISO-TS 16955, Chatillon, clínicas o captura de movimiento; LLTE usa GRF calculada, no impuesta). Patente USPTO 10537283 = solo concepto.
- Cuidado al redactar: diferencia MECÁNICA medida ≠ beneficio CLÍNICO. La tesis puede decir qué diferencia mecánica hay por el precio; "vale la pena" para el paciente exige estudios con personas (fuera de alcance).

## 6. Vacíos de las búsquedas anteriores del mismo día (prácticas)
- Sin pie patrón de rigidez conocida para calibrar bancos (JNER 2023, doi 10.1186/s12984-023-01126-7).
- Sin método estandarizado de energía en banco; el montaje cambia el resultado (63–100 % de eficiencia para un mismo pie).
- Sin antecedente de sincronizar el controlador propio de una prótesis activa con un banco externo.
- Detalle en el chat del 2026-11-25 y en la entrada de las 3 prácticas de `CLAUDE.md`.
