# Protocolo estandar de identificacion de la rigidez k(F) de cualquier protesis/calzado (2026-11-20)

**Propuesta + script de preparacion probado SOLO en simulacion. Nada ejecutado con hardware; nada integrado al lazo ni a la interfaz.**

## Objetivo
Que Kp, `pasos_por_n` y la ganancia programada del lazo de Fz en Y salgan de una medicion estandar de k(F) hecha por el propio sistema, sin medir k a mano ni depender de que protesis sea (o de un calzado blando agregado). Hoy `pasos_por_n = 80/k_asumido` sale de `tabla_k_por_protesis.json` (solo `pie_pasivo_1`) y `--kp_programado` usa una tabla k(F) medida solo en pie plano.

## Metodologia (el protocolo)
**(a) Que se mide y como.** Curva F(z) con la protesis montada, solo Y (X y K quietos), z = descenso ORDENADO (no hay sensor de posicion): carga hasta el pico objetivo y descarga hasta ~5 N.
- Angulo del pie FIJO y anotado (k depende de el: talon 26.4 / plana 23.0 / punta 2.4 N/mm, Ensayo A). Un perfil por angulo/condicion que se vaya a usar.
- Calzado/cubierta: cada configuracion es una entrada nueva (otro `id`).
- Rampa LENTA (propuesta 2 mm/s; el Ensayo A fue escalonado) para que el retardo comando->fuerza (~15-23 ms, Ensayo B) pese <0.05 mm.
- Rango: hasta el pico objetivo (80 kg => ~1.15*m*g = ~900 N), **subiendo en escalones de carga** como en las escaleras (p. ej. 10, 20, 40, 60, 80 kg); cada escalon repite la rampa y amplia la curva. La tabla medida llega hoy a ~800 N (k sube 18 -> 58 N/mm con la carga).
- Salida por franjas de 50 N y por sentido: k de carga y de descarga (pendiente por minimos cuadrados, `ajuste_k.pendiente`) e histeresis (1 - energia devuelta/energia de carga; Ensayo A: 18-20 %).
- Independiente de la protesis, sin ajuste manual: (1) tara; (2) aproximacion por tramos con deteccion de contacto (la de `ensayo_A_rigidez.py` y del lazo; el hueco declarado sobreestimo 8-15 mm, la deteccion es la proteccion real); (3) rampa con **tope de fuerza** (del escalon; el aborto llega ~3 N por encima, medido el 11-18) y **tope de recorrido** (propuesta 80 mm, a decidir); (4) abortos: lectura anomala/saltos del ADC, Fz congelada, caida del ESP32, o `demasiado_blanda` (no llega a la fuerza del escalon dentro del recorrido: la punta, 2.4 N/mm, necesitaria 242 mm a 578 N); en todo aborto Y vuelve al inicio.

**(b) De la curva a los parametros del lazo.** Regla vigente: k_usado >= k_real (lazo mas lento, nunca mas agresivo). `k_usado = 1.15 x percentil 70 de k_carga` (metodo Md del reporte 11-19; percentil fragil y no medido); `pasos_por_n = 80/k_usado`; `Kp(F) = Kp*min(1, k_usado/k_carga(F))` (misma forma que `--kp_programado`); Kp base 6 1/s. Se guarda un JSON por protesis/configuracion con: `id`, fecha, angulo, calzado, peso/pico objetivo, hueco, v de rampa, franjas k_carga/k_descarga, histeresis, repetibilidad, `valido`, bloque `lazo` y `origen` (SIMULADO/MEDIDO). Propuesta: ampliar o reemplazar `tabla_k_por_protesis.json` con estas entradas.

**(c) Cuando se repite.** Protesis nueva; calzado/cubierta agregado o cambiado; cambio de angulo del pie; cambio de montaje (adaptador, munon sustituto); y si el Kp efectivo estimado en una corrida se desvia de lo disenado. Validez: dos corridas seguidas con max |dk|/k_medio por franja <= **15 % (PROPUESTA mia, la decide Luis)**; si no, repetir o tomar el k mas rigido. Referencia: repetibilidad del Ensayo A plana ~1 % (23.2 vs 23.0), un solo caso.

**(d) Pasos (hardware, cuando exista).**
1. OK explicito de Luis; protesis montada en el angulo elegido (K en pasos chicos mirando el sentido; **nunca HOME con protesis**); un solo dueno del puerto del ESP32 (monitor cerrado o la pantalla del lazo de la interfaz).
2. Luis **remide el hueco** suela->plataforma antes de CADA corrida y lo ingresa.
3. Comando (hoy solo el modo simulado existe): `python control/identificacion/protocolo_rigidez_estandar.py --id <id> --angulo_deg <grados> --calzado <txt> --peso_kg 80 --hueco_mm <medido> --hueco_remedido --salida <json>`; con `--simulado` se ensaya el flujo sin hardware.
4. Luis junto al paro; escalones de carga crecientes; abortar ante cualquier anomalia.
5. Repetir una 2.a vez, comprobar la tolerancia, guardar el JSON.

## Resultado
Script `control/identificacion/protocolo_rigidez_estandar.py` con `--simulado`, ejecutado: planta sintetica (18 N/mm creciente, histeresis 18 %, ruido 0.8 N, 80 kg => 902 N). Recupera histeresis 0.181, repetibilidad entre 2 corridas 1.8 %, `valido=true`, `k_usado` 32.8 N/mm, `pasos_por_n` 2.44, Kp 6 en todas las franjas. Sin `--simulado` aborta sin tocar nada. Valida la logica de calculo, NO la fisica.

| Estado | Que |
|---|---|
| Probado en hardware | Ensayo A (talon/plana/punta, 2026-11-05, 1 pasada, hasta <=163 N, escalonado, histeresis 18-20 %); k dinamica vs carga 18 -> 58 N/mm solo pie plano, X ~ -3 cm (2026-11-19, hasta ~800 N, ventanas de 150 ms); Ensayo B (retardo, tau del servo); tope de fuerza |
| Solo simulacion | estimador de k en linea (precarga, Md); este script |
| NO verificado | rampa lenta continua con protesis real; k a >800 N; k con 2.a protesis o calzado blando; efecto de X/K moviendose (k cambia con la fase del apoyo); tolerancia 15 %; percentil 70 y margen 15 %; recorrido max 80 mm; z ordenado = z real |

## Limitaciones
Planta sintetica inventada para ensayar el codigo; los parametros (2 mm/s, franjas 50 N, 15 %, 80 mm, p70+15 %) son elecciones de diseno; k de descarga se mide pero el lazo aun no lo usa; llegar a ~900 N es carga real sobre la protesis (limite de diseno 1500 N) y lo decide Luis; una protesis muy blanda no se puede caracterizar a pico completo.

## Que falta
1. Modo hardware: reutilizar aproximacion/contacto/abortos de `control/lazo_fz_tiempo_real.py` (o una pantalla de `interfaz/src/fz/`) con SET_VEL lento, escalones de carga y registro de z/F; Luis fija el recorrido maximo.
2. Primera corrida real con `pie_pasivo_1` plano: comparar con Ensayo A (23.0) y con la k dinamica del 11-19; medir repetibilidad real y fijar la tolerancia.
3. Probar con calzado blando o 2.a protesis (sin tabla previa) y otros angulos.
4. Conectar el JSON a `cargar_k_asumido` / `--kp_programado` y a la interfaz.
5. **Recordatorio:** agregar el estimador de k al diagrama de bloques (`control/diagramas/diagrama_lazo_hibrido.py`) SOLO cuando este integrado al lazo y validado en la RPi.

## Fuentes
`reportes/2026-11-19_identificacion_k_en_linea.md`, `reportes/2026-11-19_ganancia_programada_k_vs_carga.md`, `control/identificacion/` (PROTOCOLO.md, ensayo_A_rigidez.py, estimador_k_en_linea.py, ajuste_k.py, tabla_k_por_protesis.json), `control/simulacion/sim_k_desconocida.py` (via el reporte 11-19), `reportes/2026-11-05_ensayo_A_corridas_y_fallos_usb.md`, `reportes/2026-11-18_ensayo_B_respuesta_dinamica.md`, CLAUDE.md (reglas HOME, hueco remedido, plan progresivo 11-06). Vigencia: `git log` de `control/identificacion/` (ultimo 9c1b195, 2026-11-19); no se edito ningun archivo existente salvo la linea de pendiente en el protocolo de la proxima sesion.
