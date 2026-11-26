# Progressive Automations — catálogo de actuadores con realimentación por potenciómetro, enfoque en carrera de 2" (50 mm)

Nota de alcance: la mayoría de las páginas de producto de progressiveautomations.com y progressiveautomations.ca devolvieron HTTP 429 (Too Many Requests) durante toda la sesión de investigación, incluso tras reintentos espaciados y probando subdominios regionales distintos (en-ch, el, sk-eu, etc.) y el dominio .ca. El PDF de nauticexpo.com dio HTTP 403 (confirma el bloqueo ya reportado antes). Por eso buena parte de lo de abajo viene de fragmentos (snippets) de búsqueda web, no de la página completa — se marca explícitamente dónde pasa esto.

## ¿Cuál es el peso real del PA-01-POT a 112 lb de fuerza, carrera de 2"?

### Takeaway
No se encontró ningún peso publicado para "PA-01 potenciómetro, 112 lb, 2 pulgadas" — y hay evidencia de que esa combinación probablemente **no existe** como configuración de catálogo: la página de producto del PA-01-POT (potenciómetro) lista solo 56 lb y 169 lb como opciones de fuerza, no 112 lb. El dato de peso más cercano y confiable es el del PA-01 **base (sin potenciómetro)** a 2": **1.7 lb** — un proxy, no el modelo exacto pedido.

### Cited Findings
- La página de producto del PA-01-POT (potenciómetro) da como opciones de fuerza 56 lb y 169 lb, no 112 lb: "The PA-01-POT is an IP65 mini linear actuator available in 56 and 169 lbs force options, with Grade 45 steel rod and aluminum housing." — [progressiveautomations.com/products/pa-01-pot](https://www.progressiveautomations.com/products/pa-01-pot) (vía snippet de búsqueda; la página completa no cargó, bloqueada por 429)
- La página del PA-01 base (sin feedback) sí lista 112 lb entre sus opciones de fuerza dinámica, junto con 16, 28, 56, 169 y 225 lbf: "The PA-01 data sheet lists rated loads of 16, 28, 56, 112, 169, and 225 lbf" — [progressiveautomations.com/products/pa-01](https://progressiveautomations.com/products/pa-01) (snippet de búsqueda)
- Peso del PA-01 base (sin potenciómetro), extraído de la tabla de especificaciones del producto: fila "2 in | 6.13 in | 8.13 in | 1.7 lbs" (columnas: carrera, longitud retraída, longitud extendida, peso) — [progressiveautomations.com/products/pa-01-ip65-linear-actuator](https://progressiveautomations.com/products/pa-01-ip65-linear-actuator) (snippet de búsqueda; no se pudo abrir la página completa, 429)
- Otro fragmento de la misma familia da pesos distintos para otras carreras del PA-01 base: 1" → 1.6 lb, 12" → 2.7 lb (no queda claro si es la misma tabla u otra variante/voltaje) — fuente igualmente progressiveautomations.com/products/pa-01 (snippet)
- La página separada "Feedback IP65 Mini Linear Actuator" (que parece ser el modelo con realimentación Hall, listado también como "PA-01" en la sección de productos populares) sí anuncia un rango de fuerza más amplio, 16–225 lb, pero la tabla "Length & Weight" no cargó en ningún intento (contenido recortado/truncado en cada fetch, con o sin offset) — [progressiveautomations.com/en-ch/products/feedback-ip65-mini-linear-actuator](https://www.progressiveautomations.com/en-ch/products/feedback-ip65-mini-linear-actuator)
- Reseller (no fabricante): existe un SKU de 2" de carrera, 150 lb de fuerza, CON potenciómetro, vendido en RobotShop Japón y (aparentemente) RobotShop Canadá bajo el título "2" Stroke 150 lbs Force Linear Actuator with Potentiometer Feedback" — [jp.robotshop.com](https://jp.robotshop.com/en/products/2-stroke-150-lbs-force-linear-actuator-w-potentiometer) (hallado solo como título en snippet de búsqueda; el fetch directo a la página de RobotShop devolvió 404 en los dominios .com y .ca probados, así que no se pudo confirmar el peso ni el fabricante exacto de ese listado)

### Inferences
- Es probable que la línea PA-01 con potenciómetro (PA-01-POT) tenga un conjunto de fuerzas disponibles más restringido (56/169 lb, posiblemente también 225 lb) que la línea base o la línea con sensor Hall (16–225 lb), y que 112 lb simplemente no sea una combinación de catálogo para el potenciómetro — es decir, la pregunta original ("¿cuál es el peso del PA-01-POT a 112 lb?") puede no tener respuesta porque esa variante no se vende.
- El peso de 1.7 lb (≈0.77 kg) a carrera 2" del PA-01 base es el proxy más cercano y razonable para estimar el peso del PA-01-POT a carreras similares, ya que un potenciómetro interno (visto en el despiece del PA-14P, página 6 del datasheet: ítems 50–55, engranaje+brazo+tuerca+arandelas) añade poco peso — pero esto es una inferencia mía, no un dato confirmado por Progressive Automations para la variante POT.

### Gaps
- No se confirmó el peso exacto de ningún actuador Progressive Automations en la combinación exacta "potenciómetro + 112 lb + 2 pulgadas", ni del fabricante ni de un revendedor. El 429 persistente en progressiveautomations.com/.ca y el 403 en nauticexpo.com impidieron leer la hoja de datos completa del PA-01 (que sí existe, según varios snippets, con tabla de especificaciones, dimensiones y gráficas velocidad/corriente vs carga) y la página completa de "Feedback IP65 Mini Linear Actuator".
- No se confirmó si 112 lb existe como opción en NINGUNA variante con feedback (ni potenciómetro ni Hall) del PA-01 — los snippets solo muestran 56/169 (POT) y 16–225 genérico (Hall/base), sin desglose fila por fila.
- No se pudo verificar el listado de RobotShop (150 lb, 2", con potenciómetro) — sería el dato más cercano si se pudiera abrir, pero el fetch directo falló (404) en los dos subdominios probados.

## ¿Qué otras líneas de Progressive Automations con feedback ofrecen opción de carrera de 2"? ¿Fuerza dinámica, velocidad a carga completa y peso de cada una?

### Takeaway
La única línea con feedback de la que se obtuvo una hoja de datos completa y legible es el **PA-14P** (potenciómetro): carreras de 1" a 40" (incluye 2"), fuerzas dinámicas 35/50/75/110/150 lb, velocidades a carga completa de 1.38 a 0.28 in/s según la fuerza — pero su datasheet oficial **no incluye ninguna columna ni tabla de peso**, lo cual es un vacío confirmado, no una omisión mía. Ninguna otra línea (PA-03, PA-04, PA-12, Feedback Heavy Duty, Mini IP65 Hall) pudo revisarse a nivel de tabla completa por los bloqueos de acceso; solo hay fragmentos parciales de búsqueda.

### Cited Findings
- **PA-14P (potenciómetro) — hoja de datos oficial completa, leída en PDF** (fuente: Progressive Automations, `Linear_Actuator_with_Potentiometer_PA-14P.pdf`, alojado en su propio CDN de Shopify, `cdn.shopify.com/s/files/1/0061/7735/7891/files/...`):
  - Carrera: 1" a 40" (tabla de dimensiones página 3 incluye explícitamente la columna "2" para carrera de 2 pulgadas, con A=7.51", B=9.51")
  - Fuerza dinámica / estática (lb): 35/75, 50/100, 75/150, 110/220, 150/300
  - Velocidad sin carga / carga completa (in/sec), válido para las 5 fuerzas: 35 lb → 2.00 / 1.38; 50 lb → 1.14 / 0.83; 75 lb → 0.95 / 0.70; 110 lb → 0.79 / 0.59; 150 lb → 0.37 / 0.28
  - Corriente sin carga/carga completa a 12/24/36/48 VDC: sin carga 1.0/0.5/0.3/0.3 A (todas las fuerzas); carga completa 5.0/2.5/1.7/1.3 A (todas las fuerzas)
  - Tornillo ACME, motor DC con o sin escobillas, carcasa en aluminio 6062, varilla en aluminio o acero inoxidable (personalizable), IP54 (IP65 personalizable), ciclo de trabajo 25% (5 min encendido / 15 min apagado)
  - Potenciómetro: 0–10 kΩ, ±5%, 10 vueltas, conector de 6 pines (señal/GND/+5VDC aparte del motor)
  - **No hay tabla de peso en ninguna de las 7 páginas del datasheet** (confirmado leyendo el PDF completo, no un snippet) — esto es un vacío real de la documentación del fabricante, no una búsqueda fallida.
  - [PDF fuente](https://cdn.shopify.com/s/files/1/0061/7735/7891/files/Linear_Actuator_with_Potentiometer_PA-14P.pdf?11196) — Progressive Automations, directo del fabricante.
- **Feedback IP65 Mini Linear Actuator (PA-01-HALL, sensor Hall, no potenciómetro)**: rango de fuerza 16–225 lb según snippet; en una variante regional se citan específicamente 56 lb a 12 VDC y 169 lb a 24 VDC, ambas a 2" de carrera: "12 VDC / 2 inch / 56 lb", "24 VDC / 2 inch / 169 lb" — [progressiveautomations.com (listado europeo)](https://www.progressiveautomations.com/en-ch/products/feedback-ip65-mini-linear-actuator) (snippet; página completa truncada en cada fetch, tabla de peso no accesible)
- **PA-09 ("Feedback Mini Industrial Actuator")** y **"Mini Industrial Actuator" (mini-medium-force-linear-actuator)**: existen como productos con página propia, pero ningún snippet devolvió sus tablas de fuerza/velocidad/peso ni confirmó si tienen opción de 2" — [progressiveautomations.com/products/feedback-pa-09](https://progressiveautomations.com/products/feedback-pa-09), [progressiveautomations.com/products/mini-medium-force-linear-actuator](https://progressiveautomations.com/products/mini-medium-force-linear-actuator)
- **PA-03**: descrito en un snippet como actuador de 12V, carrera 4"–24", fuerza 200–600 lb, sin mención de feedback ni de opción de 2" — [fuente no identificada con URL exacta, solo snippet de búsqueda]
- **PA-04 (base)**: 24V, carrera 4"–40", fuerza 100–400 lb, sin feedback mencionado — snippet
- **PA-04-HALL / PA-04-HS (feedback Hall)**: descrito como IP66, hasta 900 lb, con un bloque de especificaciones que en un snippet da "12 VDC" y "6 inch stroke" — pero el nombre del modelo varía entre fuentes (PA-04-HS vs PA-04-HALL) y no hay confirmación de una opción de 2" — [progressiveautomations.com (sitio australiano)](https://www.progressiveautomations.com/en-au/products/hall-effect-sensor-actuator) (snippet)
- **PA-12**: no se encontró ninguna fuente (ni oficial ni snippet) que mencione una variante con feedback de este modelo.
- No se encontró evidencia de un producto llamado literalmente "PA-MC1-POT" en ninguna búsqueda realizada.

### Inferences
- De las líneas con feedback de Progressive Automations, el PA-01/PA-01-POT/PA-01-HALL (línea "mini", IP65) es la única con clara opción de carrera de 2" y fuerzas documentadas en ese rango (56–225 lb según fuente); el PA-14P también cubre 2" pero sus fuerzas máximas a esa escala de producto (35–150 lb) son menores que el techo de la línea PA-01 (hasta 225 lb) — es decir, si se busca más fuerza en 2" con feedback, la línea PA-01 (particularmente su variante Hall, no la de potenciómetro) parece el candidato más prometedor por fuerza, aunque su peso no se pudo confirmar.
- El PA-14P es mecánicamente una familia de actuador distinta y más grande que el PA-01 (compárese el despiece de 56 piezas vs. las fotos tipo "mini" del PA-01): es razonable esperar que el PA-14P pese sensiblemente más que el PA-01 a igual carrera, aunque esto no se puede cuantificar sin el dato de peso que falta en su datasheet.

### Gaps
- No se pudo abrir ninguna página ni PDF oficial de PA-03, PA-04 (feedback), PA-09, PA-12 o "Feedback Heavy Duty Linear Actuator" con tabla completa de fuerza/velocidad/peso — todos los intentos de WebFetch a progressiveautomations.com y .ca devolvieron 429 de forma persistente durante toda la sesión (no pareció ser un bloqueo temporal de 60 segundos: reintentos espaciados por varias llamadas siguieron fallando).
- No se pudo confirmar si el PA-04-HALL/HS tiene opción de carrera de 2" (el único dato de carrera visto en snippet, "6 inch", sugiere que no, pero no es una tabla completa).
- "PA-MC1-POT" no se pudo verificar como producto existente ni descartar — ninguna búsqueda lo encontró.

## ¿Algún modelo de Progressive Automations combina ≥294 N, ≥18 mm/s a carga completa, carrera de 2", feedback por potenciómetro, Y un peso confirmado ≤0.86 kg?

### Takeaway
No se pudo confirmar ninguna combinación que cumpla las cuatro condiciones a la vez, principalmente porque el dato de **peso** falta en casi todas las fuentes revisadas (bloqueo de acceso a las páginas y PDFs completos). El candidato más cercano en fuerza/velocidad — PA-14P a 110 lb (489 N) con 0.59 in/s (15 mm/s) a carga completa — no alcanza el umbral de velocidad de 18 mm/s y no tiene peso publicado; a 75 lb (334 N) sí supera 294 N con 0.70 in/s (≈17.8 mm/s), muy cerca de 18 mm/s pero sin dato de peso tampoco.

### Cited Findings
- PA-14P a 110 lb (489 N, por encima de 294 N): velocidad a carga completa 0.59 in/sec = 15.0 mm/s — no alcanza 18 mm/s. — [Datasheet PA-14P, Progressive Automations](https://cdn.shopify.com/s/files/1/0061/7735/7891/files/Linear_Actuator_with_Potentiometer_PA-14P.pdf?11196)
- PA-14P a 75 lb (334 N, por encima de 294 N): velocidad a carga completa 0.70 in/sec = 17.8 mm/s — queda justo debajo de 18 mm/s. — misma fuente
- PA-14P a 150 lb (667 N): velocidad a carga completa 0.28 in/sec = 7.1 mm/s — muy por debajo de 18 mm/s. — misma fuente
- Ninguna fila del PA-14P tiene peso publicado (ver sección anterior) — mismo datasheet, páginas 2–7 completas revisadas.
- El PA-01-HALL a 169 lb (752 N) y 56 lb (249 N) a 2" de carrera existen como configuraciones (snippet, ver arriba), pero no hay dato de velocidad a carga completa ni de peso para ninguna de las dos en ningún snippet obtenido.

### Inferences
- Dado que 294 N (66 lbf) y 18 mm/s son umbrales relativamente modestos para esta familia de actuadores (el PA-14P los cumple o casi los cumple en más de una fila de fuerza), es plausible que SÍ exista una configuración de catálogo de Progressive Automations que cumpla las tres condiciones mecánicas (fuerza, velocidad, carrera 2", feedback), pero la pieza de información que falta sistemáticamente — en cada línea revisada — es el peso. Sin ese dato no se puede afirmar ni descartar que alguna configuración baje de 0.86 kg.

### Gaps
- Peso: dato ausente en el datasheet oficial del PA-14P (confirmado como vacío real del documento) y bloqueado por error 429/403 para PA-01-POT, PA-01-HALL, PA-03, PA-04-HALL, PA-09 y cualquier otra línea. No se logró una sola cifra de peso confirmada por el fabricante para ningún modelo CON feedback a ninguna fuerza — el único peso confirmado de fabricante (1.7 lb / ≈0.77 kg, carrera 2") es del PA-01 **sin** feedback, que es un proxy, no una confirmación de la variante pedida.
- No se pudo contactar ni simular una respuesta de sales@progressiveautomations.com (fuera del alcance de las herramientas de búsqueda web disponibles en esta sesión); si el usuario quiere el dato con certeza, ese es el canal más confiable dado el bloqueo persistente de acceso automatizado al sitio.

## Nota metodológica sobre el bloqueo de acceso

Durante toda la sesión, prácticamente cualquier intento de abrir una página de producto o PDF alojado en progressiveautomations.com o progressiveautomations.ca (incluyendo subdominios regionales como en-ch, el, sk-eu, y el dominio canadiense) devolvió HTTP 429 "Too Many Requests", incluso con reintentos espaciados por varias otras llamadas de búsqueda/fetch intermedias — sugiriendo un bloqueo más persistente que un simple límite de tasa de 60 segundos, posiblemente a nivel de IP/user-agent del servicio de fetch usado en esta sesión. El PDF alojado en pdf.nauticexpo.com devolvió HTTP 403, igual que se reportó antes para esa misma URL. El único contenido completo y legible obtenido directamente del fabricante en esta sesión fue el PDF del PA-14P, alojado en el CDN de Shopify de Progressive Automations (cdn.shopify.com/s/files/1/0061/...), que sí cargó sin bloqueo. Esto sugiere que, si se necesita más documentación oficial, buscar específicamente enlaces a PDFs en ese dominio de CDN (en vez de las páginas de producto o nauticexpo) podría evitar el bloqueo.
