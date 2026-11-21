# Pie de fibra de carbono: análisis previo a incorporarlo (2026-11-21)

## Objetivo
Dejar documentado lo analizado antes de comprar/ensayar el pie de carbono, para tenerlo en cuenta cuando termine el lazo de Fz.
Estado: solo fotos (`protesis/pie_carbono_01/`), sin datos del fabricante.

## Metodología
Razonamiento sobre lo ya medido en el repo (CLAUDE.md, Ensayo A/B, escalera de carga) + una cuenta de sensibilidad propia.
Nada de esto fue medido con el pie nuevo.

## Resultado
1. **Idoneidad.** Un ESAR de carbono frente a un pie pasivo básico es un contraste fuerte; aumenta la probabilidad de ver diferencias
   en energía absorbida/devuelta y CoP (riesgo previo: Koehler-McNicholas 2017, pies parecidos podrían no discriminarse).
2. **Seguridad.** Se necesita el límite de peso del fabricante antes de acercarse a 80 kg (≈925 N de pico). Hasta entonces, Ensayo A con tope ≈100 N y subida gradual.
3. **Velocidad de Y vs rigidez (cuenta propia, supuestos abajo).** Referencia del repo: 80 kg a x6 con k=20 N/mm → ≈148 mm/s.
   Si el tiempo de apoyo escala con la escala, a x10 → 148·6/10 ≈ 89 mm/s (≈7100 pasos/s) para k=20. Escalando como 1/k:

   | k (N/mm) | v Y a x10, 80 kg (mm/s) | pasos/s |
   |---|---|---|
   | 30 | 59 | 4736 |
   | 26.4 (talón medido) | 67 | 5382 |
   | 23 (plana medida) | 77 | 6177 |
   | 20 | 89 | 7104 |
   | 15.9 | 112 (= techo de trabajo 9000 pasos/s) | 8936 |
   | 12 | 148 | 11840 |
   | 10 | 178 | 14208 |

   Con esos supuestos, un pie con **k efectivo < ≈16 N/mm a carga alta** no alcanzaría 80 kg a x10 con el techo actual (9000 pasos/s).
   Si el pie se endurece con la carga (como el pasivo anterior, 40–88 N/mm a 600–1000 N) la exigencia baja. Solo el Ensayo A lo dirá.
4. **Techo de 9000 pasos/s.** Lo fijamos nosotros por la brusquedad observada sin rampa; no es un límite físico medido. Antes de subirlo conviene una rampa de aceleración.
5. **Protocolo genérico.** El Ensayo A + tabla por prótesis (`control/identificacion/tabla_k_por_protesis.json`) debe quedar escrito como procedimiento
   para cualquier prótesis (otra práctica podría probar una prótesis más barata y más fiel). Falta definir «fidelidad» (error de GRF, CoP, energía devuelta).
6. **Hueco medido por el sistema (propuesta, NO aprobada).** Aproximación lenta con umbral ≈5 N y recorrido máximo fijo; registrar la altura de contacto.
   Cambiaría la regla del 2026-11-05 (hueco remedido por Luis antes de cada corrida) → requiere OK explícito de Luis. Primer uso supervisado.
7. **Calzado.** Posible estudio futuro; mientras tanto, condición fija y anotada.
8. **Orden.** Primero cerrar el lazo de Fz; el pie nuevo entra después (decisión de Luis).

## Limitaciones
- Supuestos de la tabla: k lineal y constante, misma forma de curva Fz(t), duración de apoyo ∝ escala, v ∝ 1/k. No medido con el pie nuevo.
- El 148 mm/s a x6 viene de una simulación con la planta del Ensayo B (k=20 N/mm), no de una medición a 80 kg.
- Significado de las marcas «3» y «23» sin verificar; no hay ficha técnica.

## Fuentes
CLAUDE.md (entradas 2026-11-05 Ensayo A, 2026-11-18 escalera de carga y límite de velocidad, 2026-11-19 ganancia programada, 2026-11-21 pie de carbono),
`reportes/2026-11-18_escalera_10_a_50kg_y_escala.md`, `reportes/2026-11-18_ensayo_B_respuesta_dinamica.md`, Koehler-McNicholas 2017 (DOI sin lectura de Luis confirmada).
