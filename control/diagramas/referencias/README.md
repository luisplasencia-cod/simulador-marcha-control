# control/diagramas/referencias/ — fotos reales del servo A6-750RS / A6M80-750H2A1-M17

Pedido por Luis (2026-11-05): fotos reales del servomotor del eje vertical, para que el diagrama
de implementación (`../implementacion/esquema_implementacion_fz.py`) sea más fiel a lo que hay en
el lab, no solo cajas genéricas.

## Lo que se encontró

Buscando el modelo exacto que cita `reportes/2026-11-03_reporte_dia.md` (A6M80-750H2A1-M17, driver
A6-750RS), se encontró el manual de instalación del kit en manuals.plus
(https://manuals.plus/asin/B0DPW52QHZ.pdf) — **marca STEPPERONLINE, no Panasonic**, pese a que el
nombre "A6" sigue la misma convención de Panasonic MINAS A6 (no es el mismo fabricante).

- `a6-750rs_a6m80-750h2a1-m17_real.png` — foto real del manual: el driver A6-750RS (azul, con
  display M/▲/▼/◀◀/S) y el motor A6M80-750H2A1-M17 (negro, brida cuadrada, conector circular de
  encoder). Es el kit exacto citado en el reporte, no una aproximación.
- `a6_familia_750w-2500w_ejemplo.png` — foto de catálogo de un kit A6 de 2500 W (otro modelo de
  potencia, mismo diseño físico) de la tienda oficial OMC-StepperOnline, para contexto de cómo se
  ve la familia completa (varios ángulos del driver y el motor).

## Discrepancia encontrada, sin resolver

El manual de este kit **no menciona freno** en el motor A6M80-750H2A1-M17. Pero
`Codigo ESP32 MOV/.../hardware_config.h` define `Y_BRAKE_PIN` (GPIO18) con
`Y_BRAKE_LOCKED`/`Y_BRAKE_RELEASED` — el firmware sí maneja un freno para el eje Y (vertical) por
software. Dos explicaciones posibles, ninguna confirmada:
1. El motor real instalado en el simulador es una variante con freno que no aparece en el manual
   genérico encontrado en internet (los kits A6 de otras potencias sí tienen variantes "con freno",
   código con sufijo "B" en vez de "A" — ver búsqueda).
2. El freno es una pieza mecánica aparte (no integrada al motor) que el GPIO18 controla vía relé.

**No se puede resolver sin ver la etiqueta física del motor del simulador o preguntarle a quien lo
instaló** — queda pendiente de Luis, igual que el resto de `Y_BRAKE_PIN` (ya funciona, nunca se
tocó ni se diseñó en esta sesión).

## Fuentes
- Manual del kit exacto: manuals.plus/asin/B0DPW52QHZ.pdf (STEPPERONLINE A6 Series 750W AC Servo
  Motor Kit Instruction Manual, modelo A6-RS750H2A1-M17) — búsqueda web 2026-11-05.
- Foto de catálogo A6 2500 W: omc-stepperonline.com (tienda oficial) — búsqueda web 2026-11-05.
- `Y_BRAKE_PIN`, `Y_BRAKE_LOCKED`/`RELEASED`: `Codigo ESP32 MOV/platformIO_control_trayectoria_v1/src/hardware_config.h` (leído del código fuente).
