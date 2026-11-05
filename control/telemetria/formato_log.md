# Formato del log de telemetría del lazo Fz

Un solo archivo CSV por sesión de control, con una fila por muestra de control (no por ciclo).
El script real del lazo en el RPi (**no existe todavía**, ver `README.md` de esta carpeta) debe
escribir una fila por cada paso de su bucle de control, con buffer de escritura chico para que el
visor pueda leer filas casi en cuanto se escriben (no esperar a cerrar el archivo).

## Columnas (en este orden, con encabezado)

| Columna | Unidad | Qué es | Corresponde a (diagrama matemático) |
|---|---|---|---|
| `t` | s | tiempo desde el inicio del ensayo | — |
| `ciclo` | entero | número de ciclo de marcha (0, 1, 2…) | índice $j$ del ILC |
| `r` | %BW o N | referencia base (curva objetivo de Fz) | $r(t)$ |
| `delta` | %BW o N | corrección aprendida por el ILC para este punto del ciclo | $\delta_j(t)$ |
| `r_corregida` | %BW o N | `r + delta` — lo que de verdad se persigue este ciclo | $r^*(t) = r(t) + \delta_j(t)$ |
| `F_med` | %BW o N | fuerza medida (AMTI→ADS1256), ya retardada por el lazo real | $F_{med}(t) = F(t-T)$ |
| `e` | %BW o N | error | $e(t) = r^*(t) - F_{med}(t)$ |
| `u` | pasos/s | señal de control enviada como `SET_VEL` | $u(t) = K_p \cdot e(t)$ |

Unidades de `r`/`delta`/`r_corregida`/`F_med`/`e`: **%BW**, igual que en `control/simulacion/` y en
`DECISION_TIPO_CONTROL.md`, para poder comparar directo con esos números. `u` queda en pasos/s porque
es literalmente el parámetro que manda `SET_VEL:eje:pasos_por_seg_con_signo` — convertir a N o a %BW
necesitaría la ganancia `pasos_por_n` (sin medir, ver `control/ilc/README.md`), así que no se inventa.

## Reglas
- **Una fila por muestra de control**, no por ciclo — si el lazo corre a 100 Hz, ~370 filas por ciclo de 3.69 s.
- **Flush después de cada fila** (o cada pocas filas) — el visor lee el archivo mientras otro proceso lo escribe.
- **Nombre de archivo:** `control/telemetria/registros/<fecha>_<hhmmss>_fz.csv` (carpeta `registros/` no versionada en detalle, solo `.gitkeep`).
- El visor no asume que el archivo ya existe al arrancar — espera a que aparezca.
