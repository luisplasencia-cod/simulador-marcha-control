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
| Punta | −37.3° | ver §3 | ≈2 (muy blanda) | `ensayo_A_ang-37.3_punta_*` |
Resultado clave hasta ahora: talón y plana son casi iguales en el tramo común 40–100 N (26.3 vs 27.0); la punta es ≈10 veces más blanda (≈2 N/mm): comportamiento muy distinto (probable efecto de palanca/rodadura del antepié, NO verificado). Curvas no lineales e histéresis ≈18–20 %. Todo con desplazamiento ORDENADO (no medido), una pasada por condición, fuerza ≤163 N.

## 3. Estado de la PUNTA y de la comparación de las tres condiciones
(Se completa al final de la sesión: ver sección "Cierre" al final de este archivo.)

## 4. Problemas abiertos de la cadena de medición (bloquean el control de Fz hasta resolverlos)
1. **USB del ESP32 se cae** (`usb1-port2: disabled by hub (EMI?)`, 60+ veces hoy; las 61 con ese mensaje). El ESP32 nunca devolvió error. Causas candidatas: EMI/rebote de masa del servo vertical, reinicio del ESP32 por DTR/RTS al abrir el puerto (el firmware bloquea/libera el freno vertical en `setup()`), cable/alimentación USB. Mitigación en software ya hecha (reconexión calmada, reintento, subida sin ADC, `conectar(rapido=True)`, `subir_a_rafagas.py`). **Falta:** cable USB corto con ferrita / hub alimentado / aislador USB; logger de un proceso + `dmesg`; `esp_reset_reason()` en el firmware (autorizado por Luis, se flashea desde la laptop).
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
