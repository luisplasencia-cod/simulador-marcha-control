# Imágenes de ejemplo del estilo (dadas por el usuario el 30-10-2026)

Copias en `../assets/referencias_estilo/` (`1.png` a `5.png`). Son material de referencia del usuario para fijar el estilo; no se redistribuyen.

| # | Qué muestra | Qué se adopta |
|---|---|---|
| 1 | Lazo cerrado clásico: `r(t)` entra a un sumador (+/−), `e(t)`, punto de derivación a tres ramas en paralelo (Proporcional, Integral, Derivativo) dentro de un recuadro punteado "Controlador PID", sumador, `c(t)`, Accionador, `u(t)`, Sistema, `y(t)` con punto, Sensor y `h(t)` volviendo por abajo. Título arriba a la derecha. Todo en Arial, blanco y negro. | La estructura completa del lazo, los nombres de señales (`r, e, c, u, y, h`), el PID en paralelo con recuadro punteado, la medida por abajo, la letra Arial para los nombres. |
| 2 | PID autoajustable: bloque de controlador `Gr(z⁻¹)`, planta `Gp(z⁻¹)`, perturbación `e(t)` que entra por un sumador a la salida, un bloque estimador (MMCR) que recibe `u` y la salida y devuelve `P̂(t)` al controlador. | Una perturbación entra por un sumador con su signo; un bloque que observa señales y actúa sobre otro se dibuja con flechas rectas. |
| 3 | Regulación de velocidad: sumadores en cadena con `+` y `−`, "Controlador inteligente", "Servo Piloto" con `1/(1+sT_P)²`, servomotor con `1/(1+sT_G)` y límites de apertura, realimentación con `R_p`. | Una función de transferencia muy corta puede ir dentro de la caja; los límites (saturación) se rotulan junto al bloque. |
| 4 | Linealización por realimentación: sumadores anidados, bloques `K_d`, `K_p`, `K_i`, derivada `dy/dt`, integral `∫(y_d − y)dt`, cálculos de `Δy`, `Δẏ` rotulados sobre las flechas. | Los rótulos de señal van sobre las flechas, en matemática; las ramas del PID pueden dibujarse como bloques de ganancia. |
| 5 | Detalle de un PID con funciones de transferencia `1/(T_i p)`, `T_d p / (α_d T_d p + 1)`, filtro `1/(τ_f p + 1)`, sumadores con `+` y `−`, `e(t)` y `y(t)`. | La matemática en tipografía de ecuación LaTeX con subíndices y fracciones; el filtro de la derivada como bloque. |

Pedido explícito del usuario sobre las ecuaciones: deben verse en formato de ecuación LaTeX, y las variables y ecuaciones deben poder entenderse en un caption de la figura. Por eso las
cajas llevan el símbolo y el número, y la matemática completa va en la leyenda.

## Cómo quedó aplicado en el sistema NEMA (control de presión de una cámara con bomba y válvula)

Ver `../assets/ejemplo_control_presion/`: `diagrama_control.png`, `leyenda_variables.png`, `ecuaciones.png`. Detalles de ese diagrama que sirven de modelo:

- Camino de adelante: Σ → PID en paralelo (recuadro punteado) → Saturación (2) → Zona muerta (3) → Rampa (4) → Bomba (M1) → Cámara (M2) → punto `p(t)`.
- Camino de vuelta: Sensor (M3) → Filtro (1) → `y(t)` hasta el sumador; de `y(t)` sale la rama de ventilación (5) y de `p_m(t)` la protección (6).
- La válvula actúa sobre la cámara, no sobre el lazo principal: su línea rodea el dibujo por abajo, por la derecha y por arriba y entra a la cámara desde arriba.
- Números: del `(1)` al `(6)` para el firmware, `(M1)` a `(M3)` para el modelo de la planta, que es solo un supuesto de la simulación.
