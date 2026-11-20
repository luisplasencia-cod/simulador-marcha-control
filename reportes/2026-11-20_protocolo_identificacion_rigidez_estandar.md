# Protocolo estandar de identificacion de la rigidez k(F) de cualquier protesis/calzado (2026-11-20)

**Propuesta + script de preparacion probado SOLO en simulacion. Nada ejecutado con hardware; nada integrado al lazo ni a la interfaz.**

## Objetivo
Que Kp, `pasos_por_n` y la ganancia programada del lazo de Fz en Y salgan de una medicion estandar de k(F) hecha por el propio sistema, sin medir k a mano ni depender de que protesis sea (o de un calzado blando agregado). Hoy `pasos_por_n = 80/k_asumido` sale de `tabla_k_por_protesis.json` (solo `pie_pasivo_1`) y `--kp_programado` usa una tabla k(F) medida solo en pie plano.

## Metodologia (el protocolo)
**(a) Que se mide y como.** Curva F(z) con la protesis montada, solo Y (X y K quietos), z = descenso ORDENADO (no hay sensor de posicion): carga hasta el pico objetivo y descarga hasta ~5 N.
- Angulo del pie FIJO y anotado (k depende de el: talon 26.4 / plana 23.0 / punta 2.4 N/mm, Ensayo A). Un perfil por angulo/condicion que se vaya a usar.
- Calzado/cubierta: cada configuracion es una entrada nueva (otro `id`).
- Rampa LENTA (2 mm/s = 36-116 N/s con k 18-58 N/mm; literatura 100-200 N/s, ver tabla de respaldo; el Ensayo A fue escalonado) para que el retardo comando->fuerza (~15-23 ms, Ensayo B) pese <0.05 mm.
- Rango: hasta el pico objetivo (80 kg => ~1.15*m*g = ~900 N), **subiendo en escalones de carga** como en las escaleras (p. ej. 10, 20, 40, 60, 80 kg); cada escalon repite la rampa y amplia la curva. La tabla medida llega hoy a ~800 N (k sube 18 -> 58 N/mm con la carga).
- Salida por franjas de 50 N y por sentido: k de carga y de descarga (pendiente por minimos cuadrados, `ajuste_k.pendiente`) e histeresis (1 - energia devuelta/energia de carga; Ensayo A: 18-20 %).
- Independiente de la protesis, sin ajuste manual: (1) tara; (2) aproximacion por tramos con deteccion de contacto (la de `ensayo_A_rigidez.py` y del lazo; el hueco declarado sobreestimo 8-15 mm, la deteccion es la proteccion real); (3) rampa con **tope de fuerza** (del escalon; el aborto llega ~3 N por encima, medido el 11-18) y **tope de recorrido** (propuesta 80 mm, a decidir); (4) abortos: lectura anomala/saltos del ADC, Fz congelada, caida del ESP32, o `demasiado_blanda` (no llega a la fuerza del escalon dentro del recorrido: la punta, 2.4 N/mm, necesitaria 242 mm a 578 N); en todo aborto Y vuelve al inicio.

**(b) De la curva a los parametros del lazo.** Regla vigente: k_usado >= k_real (lazo mas lento, nunca mas agresivo). `k_usado = 1.15 x percentil 70 de k_carga` (metodo Md del reporte 11-19; percentil fragil y no medido); `pasos_por_n = 80/k_usado`; `Kp(F) = Kp*min(1, k_usado/k_carga(F))` (misma forma que `--kp_programado`); Kp base 6 1/s. Se guarda un JSON por protesis/configuracion con: `id`, fecha, angulo, calzado, peso/pico objetivo, hueco, v de rampa, franjas k_carga/k_descarga, histeresis, repetibilidad, `valido`, bloque `lazo` y `origen` (SIMULADO/MEDIDO). Propuesta: ampliar o reemplazar `tabla_k_por_protesis.json` con estas entradas.

**(c) Cuando se repite.** Protesis nueva; calzado/cubierta agregado o cambiado; cambio de angulo del pie; cambio de montaje (adaptador, munon sustituto); y si el Kp efectivo estimado en una corrida se desvia de lo disenado. **Ciclos (cambio 11-20 por la literatura):** 3 ciclos carga-descarga seguidos, el 1.o es de acondicionamiento y se descarta; los otros 2 se analizan (Turner 2022: 6 ciclos, 3 de acondicionamiento; Tacca 2024: 4, ultimos 3; Major 2022: 2, analiza el 2.o). Validez: max |dk|/k_medio por franja entre los 2 ciclos analizados <= **15 % (SIN RESPALDO: la literatura solo da 2.4+-1.3 % en pies duplicados; 15 % es holgado, se afinara con la 1.a corrida real)**; si no, repetir o tomar el k mas rigido. Ademas se reporta `k_lineal_50_pico` (regresion de 50 N al pico, definicion de Turner/Tacca) para comparar con publicaciones. Referencia: repetibilidad del Ensayo A plana ~1 % (23.2 vs 23.0), un solo caso.

**(d) Pasos (hardware, cuando exista).**
1. OK explicito de Luis; protesis montada en el angulo elegido (K en pasos chicos mirando el sentido; **nunca HOME con protesis**); un solo dueno del puerto del ESP32 (monitor cerrado o la pantalla del lazo de la interfaz).
2. Luis **remide el hueco** suela->plataforma antes de CADA corrida y lo ingresa.
3. Comando (hoy solo el modo simulado existe): `python control/identificacion/protocolo_rigidez_estandar.py --id <id> --angulo_deg <grados> --calzado <txt> --peso_kg 80 --hueco_mm <medido> --hueco_remedido --salida <json>`; con `--simulado` se ensaya el flujo sin hardware.
4. Luis junto al paro; escalones de carga crecientes; abortar ante cualquier anomalia.
5. Repetir una 2.a vez, comprobar la tolerancia, guardar el JSON.

## Resultado
Script `control/identificacion/protocolo_rigidez_estandar.py` con `--simulado` (ahora 3 ciclos, descarta el 1.o), reejecutado 11-20: planta sintetica (18 N/mm creciente, histeresis 18 %, ruido 0.8 N, 80 kg => 902 N). Recupera histeresis 0.181, repetibilidad entre 2 ciclos 1.7 %, k_lineal_50_pico 25.7, `valido=true`, `k_usado` 32.8 N/mm, `pasos_por_n` 2.44, Kp 6 en todas las franjas. Sin `--simulado` aborta sin tocar nada. Valida la logica de calculo, NO la fisica.

| Estado | Que |
|---|---|
| Probado en hardware | Ensayo A (talon/plana/punta, 2026-11-05, 1 pasada, hasta <=163 N, escalonado, histeresis 18-20 %); k dinamica vs carga 18 -> 58 N/mm solo pie plano, X ~ -3 cm (2026-11-19, hasta ~800 N, ventanas de 150 ms); Ensayo B (retardo, tau del servo); tope de fuerza |
| Solo simulacion | estimador de k en linea (precarga, Md); este script |
| NO verificado | rampa lenta continua con protesis real; k a >800 N; k con 2.a protesis o calzado blando; efecto de X/K moviendose (k cambia con la fase del apoyo); tolerancia 15 %; percentil 70 y margen 15 %; recorrido max 80 mm; z ordenado = z real |


## Respaldo en literatura de cada valor propuesto (revision 2026-11-20)
**Honestidad de lectura:** Claude no leyo ningun PDF completo; los protocolos de las 3 primeras fuentes salen del texto de acceso abierto obtenido por WebFetch (resumido por un modelo auxiliar: cifras citadas, no releidas a mano). **Todas: lectura sin confirmar por Luis.** ISO 22675 NO se leyo (de pago); sus cifras vienen de una copia escaneada en Scribd, edicion sin confirmar.

| Valor/decision propuesto | Fuente (DOI) | Lo que dice | Estado |
|---|---|---|---|
| Ciclos y acondicionamiento (3 ciclos, descartar el 1.o) | Turner 2022, PLoS ONE, 10.1371/journal.pone.0268136 | 6 ciclos carga-descarga; los 3 primeros acondicionamiento, se promedian los 3 ultimos | RESPALDADO (cambiado de 2 corridas analizadas a 3 ciclos) |
| idem | Tacca 2024, Front. Rehabil. Sci., 10.3389/fresc.2024.1290092 | 4 ciclos, se analizan los ultimos 3 | RESPALDADO |
| idem | Major 2022, PLoS ONE, 10.1371/journal.pone.0262910 | 2 ciclos, se analiza el 2.o; 5 ensayos por combinacion pie-calzado | RESPALDADO |
| Rampa lenta, 2 mm/s (= 36-116 N/s aqui) | Tacca 2024; Major 2022; Turner 2022; ISO 22675 (Scribd) | 100 N/s; 200 N/s; 20 mm/s cuasi-estatico; estatico 100-250 N/s | PARCIAL: lo usual es 100-200 N/s o 20 mm/s; 2 mm/s queda por debajo (mas lento = conservador, el retardo del lazo no pesa). Se mantiene; Major reconoce que su rampa es mas lenta que la marcha |
| Pico de carga (1.15 BW, ~900 N a 80 kg) | Tacca 2024; Major 2022 | tope 1.3 BW (talon/mediopie) y 1.0 BW (antepie) del peso maximo del rango; Major 1230 N | RESPALDADO como no excesivo: 1.15 BW queda dentro de lo que se ensaya en pies |
| Precarga / inicio del rango | Tacca: 4-6 N de precarga; Turner: minimo 50 N mantenido; Major: precarga 100 N | rangos distintos segun laboratorio | La deteccion de contacto del proyecto es compatible; **sin valor unico respaldado** (eleccion de diseno) |
| k como pendiente de 50 N al pico y dependencia de F | Turner 2022; Tacca 2024 | regresion lineal de 50 N al peso objetivo; Turner: k bajo vs alto difiere 28-94 %; Tacca: ajuste cuadratico R2 1.00 vs lineal 0.95 | RESPALDA que k depende de F (nuestra k(F) 18->58) y la definicion `k_lineal_50_pico` (anadida). Sugerencia: ajustar tambien cuadratico (no implementado) |
| Franjas de 50 N para k(F) | - | ningun trabajo usa franjas de 50 N; usan 2 puntos o ajuste cuadratico | SIN RESPALDO en literatura -> eleccion de diseno, validar en banco: comparar k por franjas con la derivada de un ajuste cuadratico en datos reales |
| Histeresis = energia perdida / almacenada | Tacca 2024; Major 2022 (energia devuelta/almacenada, trapecios) | misma definicion que la nuestra | RESPALDADO (definicion). Magnitud tipica: una cita secundaria dice 5-15 % en pies ESR, no verificada; nuestras medidas 18-20 % (con munon sustituto/calzado) no son comparables |
| Calzado = entrada nueva | Major 2017, 10.1177/0309364617706749 (solo resumen secundario); Major 2022; Turner 2022 | el calzado cambia rigidez e histeresis; Turner uso un zapato estandar + pelicula de baja friccion | RESPALDADO. Nuevo: considerar pelicula de baja friccion bajo la suela (no usada hoy; cortante no medido) |
| Angulo del pie fijo y un perfil por angulo | Turner/Tacca/Major; ISO 22675/22676 (Scribd) | ensayo a talon -15 deg, mediopie 0, antepie +20 deg (edicion sin confirmar) | RESPALDADO el principio; nuestros angulos (talon +11, punta -37 deg, otra convencion) son los del apoyo real, no los de la norma |
| Tolerancia de repetibilidad 15 % | Turner 2022 | pies duplicados: diferencia 2.4+-1.3 % en k lineal | SIN RESPALDO como umbral (la literatura no define tolerancia). 2-3 % es alcanzable; Ensayo A propio 1 % (n=1). Validar: fijar la tolerancia como ~3x la dispersion observada en las primeras corridas reales |
| Recorrido maximo 80 mm | - | Major no fija limite de desplazamiento | SIN RESPALDO -> proteccion propia; validar: calcular z(900 N) = suma de dF/k con `tabla_k_por_protesis.json` y fijarlo en ese valor + margen tras la 1.a corrida |
| Percentil 70 + margen 15 % para k_usado | Volpe & Khosla 1993, 10.1109/9.262033 (solo abstract, NO leido) | la estabilidad del control de fuerza explicito depende de la rigidez del entorno | SIN RESPALDO numerico -> eleccion de diseno. Validar: barrido en simulacion (`sim_k_desconocida.py`) y en banco con k_usado/k_real en [0.5, 2] y margen de fase |
| Kp(F) = Kp*min(1, k_usado/k(F)) | idem; Auton. Robots 2021, 10.1007/s10514-021-09970-z (solo titulo, NO leido) | estimar rigidez de contacto y usarla para sintonizar el control | PARCIAL: la idea (adaptar ganancia a la rigidez estimada) viene de la literatura; los numeros no. Validar en banco |
| Estimador de k en linea / precarga automatica | solo titulos (Auton. Robots 2021; ICAR 2013, 10.1109/icar.2013.6766499) | - | SIN RESPALDO leido -> pendiente de lectura; hoy solo simulacion |
| Tope de fuerza con aborto ~3 N por encima; `demasiado_blanda` | medido 11-18 (propio) | - | Propio del sistema, no de literatura |

No hallados / no usados como respaldo: Hansen/Childers (roll-over, rigidez efectiva de tobillo), Klute 2001 (J Rehabil Res Dev 38(3):299-307, sin DOI ni texto accesible), Sam/Bouchard. Major 2011 (10.1016/j.jbiomech.2011.07.016) es un modelo de propiedades, no un protocolo de ensayo.

## Que parametros del lazo dependen de la protesis y como detectarlos
| Parametro | Depende de la protesis? | Como se detecta en el protocolo |
|---|---|---|
| k(F) (rigidez de carga) | SI (pie, calzado, angulo, montaje; 2.4-58 N/mm medido) | pendiente por franja y `k_lineal_50_pico` de los 2 ciclos analizados |
| Histeresis | SI (calzado, amortiguador); medida 18-20 % | 1 - energia devuelta/almacenada por ciclo |
| k de descarga | SI | pendiente de la rama de descarga por franja (el lazo aun no la usa) |
| Kp(F) y `pasos_por_n` | Derivados de k(F): cambian con la protesis, no son propiedad suya | salen de `tabla_lazo` (k_usado) |
| Amortiguamiento y modo ~7 Hz | PROBABLE (supuesto del reporte 11-19, no medido) | NO lo detecta este protocolo cuasi-estatico: requiere ensayo dinamico (escalon/barrido o Ensayo B repetido con la protesis) |
| Angulo del pie | Condicion de ensayo, no propiedad | se fija y anota; un perfil por angulo |
| Retardo comando->Fz (~15-23 ms), tau del servo (3-14 ms) | NO (eje y electronica) | Ensayo B; se repite solo si cambia el hardware |
| 80 pasos/mm de Y, tope de velocidad, filtro de Fz, ruido 60 Hz | NO | ya medidos |
| Repetibilidad del ciclo | SI (prototipo vs comercial) | diferencia entre ciclos analizados |

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
