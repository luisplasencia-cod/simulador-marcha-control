# Uso de la plataforma instrumentada del practicante actual (análisis 2026-11-25)

Plataforma (dato de Luis): mide ÁNGULO, DESPLAZAMIENTO y FUERZA EN LA INTERFAZ encaje–muñón; se integrará al simulador y quedará accesible para las prácticas.
Convención: [C] dato del proyecto · [L] literatura · [I] inferencia. Specs aún desconocidas → NO VERIFICADO (tasa de muestreo, sincronía con el AMTI, ejes, rango, qué ángulo mide).

## 1. En la tesis
- **Desplazamiento medido = el uso más fuerte.** [C] Hoy `k` sale del desplazamiento ORDENADO (contador del ESP32, no prueba movimiento; el 11-18 se "perdieron" ≈4–5 mm por holgura sin explicar). [I] Con desplazamiento medido, `k(F)` es el del pie sin la holgura del banco, y el estimador de `k` en línea (`control/identificacion/estimador_k_en_linea.py`, no conectado) puede alimentar la ganancia programada con datos reales → núcleo de la pregunta de tesis.
- **Ángulo medido.** [C] Hoy el ángulo sagital se estima por pasos y su signo ya falló una vez. [I] Verifica el sagital y permite expresar el CoP en el marco de la pierna (forma de rodadura).
- **Velocidades.** [C] P = Fy·vy + Fz·vz + M·ω (Takahashi 2012). [I] Derivar lo medido amplifica el ruido → la tasa de muestreo es crítica.
- **Fuerza en la interfaz.** [C] Solo observación; chequeo axial ≈ Fz·cosθ + Fy·senθ. [C/I] Con GRF fija, la fuerza axial queda casi fijada por el control → sirve para verificar, no para distinguir prótesis.

## 2. En las prácticas [I]
- **P1:** ángulo para verificar/cerrar el sagital; desplazamiento X para comprobar que el eje horizontal solo avanza. Si las salidas son analógicas, pueden entrar por los 2 canales libres del AD7606 (6 AMTI + 2 = 8) → base de tiempo común resuelta.
- **P2:** desplazamiento medido ESENCIAL: validar contra el pie patrón con desplazamiento ordenado mete la holgura del banco en `k` y anula la validación.
- **P3:** fuerza de interfaz + ángulo muestran el efecto de la energía que inyecta la activa; el ángulo podría ayudar a detectar la fase. Exige misma base de tiempo que el AMTI.

## 3. Literatura
- En contra de que la interfaz distinga pies: Koehler-McNicholas 2017 (PLOS ONE), sin diferencias en torque distal del encaje ni confort entre 3 tobillos. https://pmc.ncbi.nlm.nih.gov/articles/PMC5344385
- A favor, débil (no abiertos): https://pmc.ncbi.nlm.nih.gov/articles/PMC6284521/ · https://www.frontiersin.org/journals/rehabilitation-sciences/articles/10.3389/fresc.2024.1290092/pdf
- Bancos con interfaz: Southampton (McGrath 2017), simulador muñón–encaje con FSR, 850 N uniaxial; la mayoría de simuladores usan acople rígido; ISO 10328 prueba integridad, no interfaz. https://eprints.soton.ac.uk/403881 · https://eprints.soton.ac.uk/480479/2/3257059.pdf
- No se encontró protocolo que combine GRF de marcha estandarizada + carga en la interfaz (Herlihy 2026 lo hace en lazo abierto).

## 4. Riesgos
- Si la plataforma no está lista: la tesis sigue viable con AMTI + desplazamiento ordenado (declarado como limitación); pierden fuerza el `k` real, la energía y la validación de la P2.
- Si no sincroniza con el AMTI: energía y forma de rodadura quedan desalineadas; el control no se afecta (la plataforma solo observa).

## 5. Pedidos concretos al practicante actual
1. Hoja de specs por sensor: modelo, rango, resolución, tasa de muestreo, ejes y signo según la convención del proyecto (Y+ = subir, Fz+ = carga).
2. Tipo de salida: analógica (→ AD7606) o digital con marca de tiempo.
3. Base de tiempo común con AMTI/RPi: pulso de sincronía compartido o marca por pisada.
4. CSV con `t_real`, unidades SI, encabezado con calibración y fecha, compatible con `control/telemetria/`.
5. Calibración documentada con su incertidumbre.
6. Posición del sensor de desplazamiento respecto del punto A del CAD.
7. Lector en Python para la RPi + ejemplo + README en el repo.
8. Pruebas de aceptación: desplazamiento vs 80 pasos/mm; ángulo vs giro conocido de K (±100 pasos ≈ 0.9°); fuerza de interfaz vs Fz con la pierna vertical.
