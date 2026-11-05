# control/diagramas/referencias/ — fotos reales del servo A6-750RS / A6M80-750H2

Pedido por Luis (2026-11-05): fotos reales del servomotor del eje vertical, para que el diagrama
de implementación (`../implementacion/esquema_implementacion_fz.py`) sea más fiel a lo que hay en
el lab, no solo cajas genéricas.

## Lo que se encontró

Buscando el modelo que cita `reportes/2026-11-03_reporte_dia.md` (A6M80-750H2·1-M17, driver
A6-750RS), se encontró el manual de instalación de ese kit en manuals.plus
(https://manuals.plus/asin/B0DPW52QHZ.pdf) — **marca STEPPERONLINE, no Panasonic**, pese a que el
nombre "A6" sigue la misma convención de Panasonic MINAS A6 (no es el mismo fabricante).

- `a6-750rs_a6m80-750h2a1-m17_real.png` — foto real del manual: el driver A6-750RS (azul, con
  display M/▲/▼/◀◀/S) y el motor **A6M80-750H2A1-M17** (negro, brida cuadrada, conector circular de
  encoder). **Este es el modelo HORIZONTAL (sin freno)**, no el vertical — ver corrección abajo.
- `a6_familia_750w-2500w_ejemplo.png` — foto de catálogo de un kit A6 de 2500 W (otro modelo de
  potencia, mismo diseño físico) de la tienda oficial OMC-StepperOnline, para contexto de cómo se
  ve la familia completa (varios ángulos del driver y el motor). El diseño físico es el mismo para
  el motor vertical (B1), solo cambia el sufijo B1 (con freno integrado) en vez de A1.

## Freno del motor vertical — RESUELTO (2026-11-05, estaba mal en la primera versión de esta nota)

**Confusión de esta sesión:** al buscar fotos, se encontró el manual del modelo **A1** (sin freno)
y se asumió por error que era el del eje vertical, generando una "discrepancia" que en realidad no
existe. **El artículo de conferencia (`conferencia_copy.pdf`) ya lo dice explícito:**

> "...an A6M80-750H2A1-M17 servomotor" para el eje **horizontal**.
> "...an A6M80-750H2B1-M17 servomotor **with a holding brake**" para el eje **vertical**.
> "...the vertical-axis motor incorporates a built-in electromagnetic brake to prevent unintended
> displacement when the system is powered down, a dedicated switching circuit was implemented to
> control the brake release and engagement during operation."

Es decir: **horizontal = A1 (sin freno), vertical = B1 (con freno integrado)** — el sufijo A1/B1 del
nombre del modelo ya codifica la diferencia, igual que en los demás kits de la familia OMC-StepperOnline
(sufijo "B" = variante con freno). El circuito que enciende/apaga el freno ya está implementado en el
hardware real del simulador (no es parte de este trabajo). `Y_BRAKE_PIN` (GPIO18) en
`hardware_config.h` es justamente ese control.

## Fuentes
- Manual del kit horizontal (A1, sin freno), fotos de referencia: manuals.plus/asin/B0DPW52QHZ.pdf
  (STEPPERONLINE A6 Series 750W AC Servo Motor Kit Instruction Manual) — búsqueda web 2026-11-05.
- Foto de catálogo A6 2500 W: omc-stepperonline.com (tienda oficial) — búsqueda web 2026-11-05.
- **Modelo vertical (B1, con freno) y circuito de freno: `conferencia_copy.pdf`, artículo de
  conferencia aceptado, sección de hardware electrónico** (ya leído completo en sesiones previas;
  no se había cruzado con el modelo exacto hasta ahora).
- `Y_BRAKE_PIN`, `Y_BRAKE_LOCKED`/`RELEASED`: `Codigo ESP32 MOV/platformIO_control_trayectoria_v1/src/hardware_config.h` (leído del código fuente).
