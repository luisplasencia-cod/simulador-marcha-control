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
| `visor_en_vivo.py` | Lee el CSV mientras otro proceso lo escribe y grafica 3 tiras: $r^*(t)$ vs $F_{med}(t)$, $e(t)$, $u(t)$ y $\delta(t)$ | lectura/parseo verificado contra el CSV sintético; **la ventana gráfica (TkAgg) no se abrió en esta sesión** — sin pantalla disponible para confirmarlo visualmente |

## Cómo probarlo ahora (sin RPi)

```bash
# Terminal 1: genera datos como si el lazo estuviera corriendo
python generar_datos_sinteticos.py --en-vivo --ciclos 12

# Terminal 2 (en paralelo): el visor
python visor_en_vivo.py --ultimo
```

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
