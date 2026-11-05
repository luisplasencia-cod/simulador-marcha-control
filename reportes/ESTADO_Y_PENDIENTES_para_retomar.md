# ESTADO Y PENDIENTES — punto de entrada para retomar el trabajo (actualizado 2026-11-05, noche)

> Léelo primero. Resume dónde quedó el rig, qué se midió, qué falta, en qué orden y con qué comandos. Detalle y evidencia: `reportes/2026-11-05_*.md`, `CLAUDE.md`, `control/identificacion/`.

## 1. Estado FÍSICO del simulador al terminar la sesión (verificar con la vista antes de mover nada)
- **Pie montado** con el sustituto del muñón. **Ángulo sagital K ≈ −37.3° (punta)**, llevado por pasos desde un ≈5° puesto a ojo (error del ángulo absoluto desconocido). El ángulo físico se lleva en `control/identificacion/estado_angulo_K.json` (el ESP32 pierde su contador al abrir el puerto). Para volver a 0°: `rotar_sagital.py --a 0` (+4144 pasos).
- **X avanzado en total +20 cm** respecto de donde estaba al girar a la punta (+6, +6, +8 cm; sentido positivo = avance, SIN verificar con el rig). X absoluta y distancia al final de carrera: desconocidas (no se hizo HOME).
- **Eje vertical Y**: vuelve a su altura de partida tras cada corrida (los pasos pendientes de las corridas terminan en 0), ≈21–23 cm sobre la plataforma con el pie en el aire; la altura absoluta respecto de su rango (542 mm) es desconocida.
- **NUNCA mandar `HOME` con la prótesis puesta** (Luis: puede romper un mecanismo). No se hizo HOME hoy.
- **Monitor de Fz**: cerrado (comparte SPI con los ensayos). El visor del ensayo (`visor_ensayo_A.py`) puede seguir abierto en la pantalla de la Pi.
- **ADC (ADS1256)** alimentado con fuente externa de 5 V; cae a veces y solo revive ciclando esa alimentación (ver §4).

## 2. Qué se midió hoy (Ensayo A: rigidez de contacto k, solo eje vertical)
| Condición | Ángulo | Estado | k (N/mm) | Archivos |
|---|---|---|---|---|
| ≈5° (a ojo) | ≈5° | PARCIAL (USB cayó a 116 N, sin subida) | ≈28 | `RAW_en_vivo_corrida3_*` |
| Talón | +11.14° | COMPLETA (105 N, con subida) | **26.4** | `ensayo_A_ang11.14_talon_20261105_160831.*` |
| Plana | 0° | COMPLETA (163 N, con subida, repetida: 23.2 y 23.0) | **23.0** | `ensayo_A_ang0_plana_20261105_162448.*` |
| Punta | −37.3° | COMPLETA (100 N, subida, 0 cortes; con pasos de 2 mm) | **2.4** (≈11× más blanda) | `ensayo_A_ang-37.3_punta_20261105_164410.*` (+`_continuo.csv`) |
Resultado clave hasta ahora: talón y plana son casi iguales en el tramo común 40–100 N (26.3 vs 27.0); la punta es ≈10 veces más blanda (≈2 N/mm): comportamiento muy distinto (probable efecto de palanca/rodadura del antepié, NO verificado). Curvas no lineales e histéresis ≈18–20 %. Todo con desplazamiento ORDENADO (no medido), una pasada por condición, fuerza ≤163 N.

## 3. Estado de la PUNTA y de la comparación de las tres condiciones
**Punta COMPLETA** (`..._164410`, k = 2.42 N/mm, 100 N, 19 puntos de subida, 0 pasos pendientes). Se logró reduciendo comandos (escalones de 2 mm, ≈40 comandos) y NO resolviendo la desconexión: con escalones de 0.2 mm se cortó 6 de 7 veces. **Comparación de las 3 condiciones hecha** (solo corridas completas, una pasada cada una): talón 26.4, plana 23.0, punta 2.4 N/mm; figura `reportes/figuras/2026-11-05_comparacion_k_3condiciones.png`; tabla y limitaciones en `reportes/2026-11-05_ensayo_A_corridas_y_fallos_usb.md` (sección "COMPARACIÓN FINAL").

## 4. Problemas abiertos de la cadena de medición (bloquean el control de Fz hasta resolverlos)
**PRIORIDAD 1 (decisión de Luis): la desconexión del USB del ESP32 hay que SOLUCIONARLA, no esquivarla.** Documento dedicado con el texto literal de la terminal, cronología (68 cortes, todos `disabled by hub (EMI?)`), datos que acotan la causa, hipótesis y qué verificar: **`reportes/PROBLEMA_PENDIENTE_desconexion_USB_ESP32.md`**; textos literales con conteo: `reportes/evidencia/2026-11-05_errores_terminal_literal.txt`; salidas crudas: `reportes/evidencia/consola/`; kernel: `reportes/evidencia/2026-11-05_dmesg_usb_esp32.txt`. **Los cambios al ESP32 se hacen desde la laptop** (no se tocó el firmware en el RPi).
1. (detalle, ver arriba) **USB del ESP32 se cae** (`usb1-port2: disabled by hub (EMI?)`, 60+ veces hoy; las 61 con ese mensaje). El ESP32 nunca devolvió error. Causas candidatas: EMI/rebote de masa del servo vertical, reinicio del ESP32 por DTR/RTS al abrir el puerto (el firmware bloquea/libera el freno vertical en `setup()`), cable/alimentación USB. Mitigación en software ya hecha (reconexión calmada, reintento, subida sin ADC, `conectar(rapido=True)`, `subir_a_rafagas.py`). **Falta:** cable USB corto con ferrita / hub alimentado / aislador USB; logger de un proceso + `dmesg`; `esp_reset_reason()` en el firmware (autorizado por Luis, se flashea desde la laptop).
2. **ADC (ADS1256)**: errores de bit SPI (0.06–0.5 % de muestras; ×5–9 con el servo vertical activo) → mediana de 3 aplicada; a veces deja de responder y solo vuelve ciclando los 5 V (fuente externa). **Falta:** capacitores/ferrita en el 5 V de la placa, tierra en estrella, cables SPI cortos y trenzados, medir con multímetro; identificar el modelo de la placa. Plan completo: `reportes/2026-11-05_plan_robustez_y_siguientes_pasos.md`.
3. Servo vertical: la velocidad de `MANUAL` es fija en el firmware (1600 pasos/s = 20 mm/s en Y; 3200 pasos/s en K); bajarla exige cambiar el firmware.

## 5. Siguientes pasos, EN ORDEN
1. **Puerta de salud** antes de mover: ADC con 3000 muestras sanas (<0.5 % malas), `PING`→`PONG`, 0 caídas de USB en los últimos 5 min (`journalctl -k | grep -c "disabled by hub"`). Si falla → ciclar 5 V del ADC / revisar cables; no mover nada.
2. **Repetibilidad** (no hecha para talón ni punta; la plana sí: ≈1 %): repetir 2–3 veces cada condición con `repetir_hasta_completa.py` para saber si las diferencias entre ángulos superan la variación entre corridas.
3. **Ángulos adicionales** si hace falta ver la dependencia (p. ej. 5°, −15°, −25°) y **fuerzas mayores** (hasta cargas de marcha ≈ 800 N+, con extremo cuidado; límite de diseño 1500 N): la rigidez a esas cargas no se midió.
4. **Medir el desplazamiento real** (sensores de distancia X/Y aún no instalados) para separar la rigidez del pie de la elasticidad de la estructura.
5. **k → ganancia pasos/N** para `control/ilc/fz_ilc.py` (usar la pendiente de la condición de diseño, elegir con Luis), luego lazo de Fz: ILC primero (firmware actual) y realimentación en tiempo real (`SET_VEL`, parche en `control/firmware/`, NO flasheado ni probado).
6. Integrar **trayectorias de X y sagital** de gaitsim (montaje 37, talla 174 propuesta; `~/Projects/gaitsim-control`, solo lectura) con el control de Fz, tras un HOME **sin pie** y con un script único que mantenga el puerto abierto (el ESP32 pierde su referencia al reiniciarse).
7. Calibración del AMTI con pesas (`pruebas/calibracion_pesas.py`, sin ejecutar); escala 1.7665 mV/N con excitación 10 V + ganancia 2000.

## 6. Qué necesito de Luis para seguir
Modelo y corriente de la fuente de 5 V del ADC; qué pasó a las 15:47 (primera tormenta de USB) y si cambió algo físico entre corridas; confirmar el sentido físico de X (+ = avance) y de K (+ = hacia talón, ya confirmado); autorizar el cambio de firmware (`esp_reset_reason()`, velocidad de `MANUAL`) y el cambio de cable/aislador USB; decidir qué condición de pie es la de diseño para el control; cuál curva de Fz objetivo usar a x6 (Gutenberg 2021 vs Fukuchi 2018); sensor de desplazamiento; pies pasivos adicionales para la 2.ª/3.ª prótesis.

## 7. Cómo reproducir una corrida (comandos)
```bash
cd ~/simulador-marcha-control
# 0) puerta de salud (§5.1). Monitor de Fz CERRADO (comparte SPI/serial).
# 1) visor en la pantalla de la Pi (matar el anterior por PID, no por patrón):
.venv/bin/python control/identificacion/visor_ensayo_A.py &
# 2) (si cambió el ángulo) girar K: pasos = grados*111.11, estado en control/identificacion/estado_angulo_K.json
.venv/bin/python control/identificacion/rotar_sagital.py --a <grados>
# 3) medir el hueco (punto más bajo del pie → plataforma) y correr hasta completa:
.venv/bin/python control/identificacion/repetir_hasta_completa.py --max_intentos 4 -- \
   --hueco_mm <medido> --max_extra_mm 50 --angulo_deg <°> --etiqueta <nombre> --fmax_n 100 --asentar_s 0.5 --hueco_remedido
# 4) comparar corridas completas:
.venv/bin/python control/identificacion/comparar_k_por_angulo.py <csv1> <csv2> <csv3> --png comparacion.png
# Si el eje queda cargado y el USB cae: control/identificacion/subir_a_rafagas.py <pasos> 4000
```
**Reglas fijas:** nunca HOME con prótesis; el hueco se mide antes de cada corrida (`--hueco_remedido`); matar procesos por PID, nunca por patrón; el firmware se edita/flashea desde la laptop; todo dato medido con su fuente, lo no medido marcado NO VERIFICADO.

## Cierre de la sesión (2026-11-05, ≈16:50 hora real; las horas de algunos títulos intermedios de los reportes eran estimaciones adelantadas: vale el orden de `git log`)
- **Hecho hoy:** latencia total del lazo medida (7.9 ms hasta el ack, sin AMTI ni cómputo); picos de Fz = errores de bit SPI + mediana de 3; **Ensayo A completo en 3 condiciones de pie** (talón 26.4, plana 23.0, punta 2.4 N/mm) con curvas, histéresis, comparación y figuras; herramientas (`control/identificacion/`); diagnóstico y documentación del problema de desconexión USB.
- **Estado físico al cerrar:** pie en **−37.3°** (punta), **X +20 cm** acumulados desde el giro a la punta, eje Y arriba (altura de partida, 0 pasos pendientes), sin carga; ESP32 conectado; ADC alimentado con la fuente externa; monitor de Fz cerrado; visor del ensayo abierto en la pantalla de la Pi. **Antes de volver a mover:** puerta de salud (§5.1) y medir el hueco.
- **Falta (en orden de importancia):** (1) **resolver la desconexión USB/EMI** (documento dedicado) con cambios en la laptop + cambios físicos; (2) repetibilidad de talón y punta y más pasadas; (3) medir el desplazamiento real y adquirir también Fy (a −37° hay cortante); (4) cargas de marcha (≥800 N) y condición de diseño para el control; (5) k → ganancia pasos/N → ILC de Fz → `SET_VEL`; (6) trayectorias X/sagital con HOME sin pie; (7) calibración del AMTI y robustez del ADC (capacitores, tierra, cableado).
