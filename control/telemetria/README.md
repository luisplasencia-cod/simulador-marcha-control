# control/telemetria/ — visor en vivo del lazo Fz

Responde a lo que pidió Luis (2026-11-04/05): ver las variables del control en vivo mientras
el lazo corre en el RPi, con los mismos nombres del diagrama matemático
(`control/diagramas/diagrama_lazo_hibrido.py`). **Probado solo con datos sintéticos** — no hay
RPi en esta sesión, y el script que corre el lazo de verdad **todavía no existe** (ver abajo).

## Piezas (en orden, cada una probada sola)

| Archivo | Qué hace | Probado |
|---|---|---|
| `formato_log.md` | Define las columnas del CSV de telemetría (una fila por muestra de control) | — (es documentación) |
| `generar_datos_sinteticos.py` | Genera un CSV con ese formato, reusando la física de `../simulacion/rt_vs_ilc_latencia.py` | corrido, produce 22 140 filas en 3 ciclos, error baja ciclo a ciclo como se espera del ILC |
| `visor_en_vivo.py` | Lee el CSV mientras otro proceso lo escribe y grafica 3 tiras: $r^*(t)$ vs $F_{med}(t)$, $e(t)$, $u(t)$ y $\delta(t)$ | sin pantalla disponible en esta sesión para la ventana interactiva (TkAgg); se agregó `--guardar archivo.gif` (backend Agg, no necesita pantalla) y SÍ se probó — `visor_fz_sintetico.gif` (enviado a Luis 2026-11-05) muestra el ILC convergiendo sobre 12 ciclos sintéticos |

## Cómo probarlo ahora (sin RPi)

**Con pantalla (ventana interactiva):**
```bash
# Terminal 1: genera datos como si el lazo estuviera corriendo
python generar_datos_sinteticos.py --en-vivo --ciclos 12

# Terminal 2 (en paralelo): el visor
python visor_en_vivo.py --ultimo
```

**Sin pantalla (lo que se probó en esta sesión, laptop sin entorno gráfico):**
```bash
python generar_datos_sinteticos.py --ciclos 12     # escribe todo de una vez, no --en-vivo
python visor_en_vivo.py --ultimo --guardar visor.gif --ventana-s 6 --fps 8 --cuadros 70
```
Esto NO es "en vivo" de verdad (el archivo ya está completo cuando el visor lo lee) — es la
manera de confirmar que el render se ve bien sin tener una pantalla a mano. Con datos reales del
RPi creciendo en vivo, usar la primera forma (sin `--guardar`).

## Bug real encontrado y corregido (2026-11-05)

La primera versión de `generar_datos_sinteticos.py` usaba $e(t) = r^*(t) - F_{med}(t)$ (el error
contra la referencia YA corregida) para actualizar $\delta$. Eso es un error: la ecuación (4) del
diagrama (`../diagramas/diagrama_lazo_hibrido.py`) dice que el ILC se actualiza con
$\varepsilon_j(t) = r(t) - F(t)$ — el error contra la referencia **base**, sin corregir. Usar $e(t)$
ahí crea una realimentación positiva: $\delta$ crecía sin límite (de 0 a más de 170 %BW en 12
ciclos) en vez de converger. Corregido: ahora se usa una señal `epsilon` separada (no se guarda en
el CSV, solo alimenta la actualización de $\delta$) y el error de seguimiento converge igual que en
`../simulacion/rt_vs_ilc_latencia.py` (RMS $\approx$ 13 → 0.6 %BW en 12 ciclos, mismo orden que los
12.0 → 0.4 %BW validados ahí). **Nota menor, no resuelta:** el GIF muestra un salto pequeño y
repetible en $e(t)$/$u(t)$ exactamente en cada frontera de ciclo — no diverge, pero no se investigó
la causa exacta (probablemente desalineación de un sample entre la cola de retardo y el adelanto
$m$ del ILC al reiniciar el índice de ciclo). No afecta la conclusión de que el ILC converge.

## Lo que falta para usarlo de verdad (no inventado, pendiente de hardware)

**El bloque que falta es el más importante: no existe todavía un script que corra el lazo real
en el RPi** (lea el ADS1256, calcule $K_p \cdot e(t)$, mande `SET_VEL` por el `protocolo_subida_esp32.py`,
y escriba cada muestra al CSV con este formato). Hoy `control/ilc/` solo tiene el cálculo, no el
bucle que lo ejecuta contra hardware. Ese script es el siguiente paso natural cuando haya RPi, y
debe escribir al CSV con `formato_log.md` para que este visor funcione sin cambios.

Además:
1. El parche de firmware `SET_VEL` (`control/firmware/control_velocidad_continua.patch`) tiene que
   estar aplicado, compilado y probado en banco antes de que `u(t)` sea una orden real al motor.
2. `u(t)` queda en pasos/s en el log — convertir a N necesita `pasos_por_n` (sin medir).
3. `visor_en_vivo.py` usa `matplotlib.use("TkAgg")` para ventana interactiva; si el RPi corre sin
   entorno gráfico (headless), cambiar a `Agg` y guardar frames periódicos con `savefig` en vez de
   `plt.show()` — no se hizo esa variante todavía porque no se sabe si el RPi tendrá pantalla conectada.
