# Reporte del día — 2026-11-19

Etapa de control del simulador de marcha (Luis Plasencia). Sesión en la **laptop, sin RPi ni hardware**: preparación de la próxima sesión en la RPi.

**Regla de este reporte:** cada tema trae *Objetivo → Metodología → Resultado → Limitaciones → Fuentes*. **Todo lo de hoy es simulación, datos sintéticos o diseño: NADA se probó en hardware.** Los supuestos se marcan como tales.

## Resumen del día (léelo primero)
1. `git pull`: la rama `master` ya estaba al día; se integró la rama `claude/eloquent-pasteur-omw641` (regla de Luis: no tocar Fy/CoP hasta que Fz esté listo; orden de lazos Z → Y → sagital por CoP).
2. **Oscilación 6–8 Hz:** el retardo del lazo P no la explica; causa más probable = modo de ~7 Hz dentro del lazo + rigidez de la prótesis mucho mayor a carga alta (§1).
3. **Rigidez desconocida:** el diseño exigía medir `k` a mano por prótesis; se diseñó un estimador en línea, **sin conectar al lazo** (§2).
4. **Ruido de 60 Hz:** filtro de software agregado al lazo (probado solo con datos sintéticos) y diagnóstico eléctrico pendiente (§3).
5. **Bug de tiempo:** el CSV del lazo guardaba tiempo nominal; corregido (§4).
6. **Documentación:** protocolo de la próxima sesión, diagramas actualizados, archivos obsoletos eliminados, dos reglas fijas nuevas (§5–§6).

## 1. Causa de la oscilación de 6–8 Hz
- **Objetivo:** saber por qué el error a 6–8 Hz crece pisada a pisada y con la carga (escalera 50–90 kg del 2026-11-18).
- **Metodología:** simulación con los retardos y τ reales del Ensayo B (T 15–23 ms, τa 3–14 ms) y los Kp usados (8 y 5); luego planta con modo mecánico + el ILC real del proyecto.
- **Resultado:** (a) el margen de fase da 78–87° con cruce en 0.5–0.9 Hz: el retardo solo no explica 6–8 Hz. (b) Con un modo de ~7 Hz y la rigidez estimada a 600–1000 N (67–88 N/mm vs 26.4 de diseño, que solo se midió hasta 105 N) la ganancia real es 2.5–3× la diseñada; la simulación reproduce Kp 8 inestable a 60–70 kg y el crecimiento 12→25 N (rig: 7.9→15 N). (c) El ILC no introduce 6–8 Hz (su filtro deja pasar < 0.001), pero al aprender lleva la fuerza a los picos donde la ganancia es máxima. (d) Mejora propuesta, **no aplicada**: `Kp·min(1, k_asumido/k_tangente)` (202 → 2 N a 70 kg en simulación).
- **Limitaciones:** masa, rigidez del accionamiento y amortiguamiento del modo mecánico son **supuestos**; el modelo no reproduce la amplitud con Kp 5 a 70–90 kg (sim 2 N vs rig 20–31 N): el rig está más cerca de la inestabilidad que el modelo. La k a carga alta es estimada, no medida.
- **Fuentes:** `reportes/2026-11-19_simulacion_hipotesis_resonancia_6_8hz.md`, `reportes/2026-11-19_causa_oscilacion_6_8hz_y_mejoras.md`; scripts en `control/simulacion/`; notch alternativo en `reportes/2026-11-19_propuesta_notch_fz_6_8hz.md` (`control/filtro_fz/notch_fz.py`, no conectado; solo sirve si la oscilación es externa al lazo).

## 2. Identificación de la rigidez k en línea (prótesis desconocida)
- **Objetivo:** que el lazo funcione con cualquier prótesis sin medir su `k` antes (hoy `cargar_k_asumido` lee `tabla_k_por_protesis.json`).
- **Metodología:** simulación con k = 2.4, 23, 33 N/mm y una no lineal, a 50 y 90 kg x10; comparación de precarga, mínimos cuadrados recursivos y ganancia programada.
- **Resultado:** método elegido = precarga automática de 1–3 s tras el contacto + k por percentil 70 de las pendientes de carga (+15 %) + Kp único = 6 1/s; la ganancia real queda en 4.5–5.0 1/s (hoy 4.4–10 según prótesis y carga). Error final 3.7–4.1 % del pico (k fijo: 2.4–4.0 %). Cambiar k dentro de la pisada empeora el error de >3 Hz.
- **Limitaciones:** el percentil es frágil (con 80 un caso duplicó k); depende de un modelo de histéresis no medido; recorrido máximo de la precarga fijado en 80 mm sin medir; con X y K moviéndose k cambiará en el apoyo (no resuelto). **No conectado al lazo ni al diagrama de bloques.**
- **Fuentes:** `reportes/2026-11-19_identificacion_k_en_linea.md`, `control/identificacion/estimador_k_en_linea.py`, `control/simulacion/sim_k_desconocida.py`.

## 3. Ruido de 60 Hz (σ 2.67 N en el RPi vs 0.78 N en la laptop, medido el 11-18)
- **Objetivo:** atenuarlo (Luis: es eléctrico, atenuar donde haga falta).
- **Metodología:** promedio de 17 muestras a ~1000/s (≈1 periodo de 60 Hz) tras mediana deslizante de 5, en `LectorFzUART`; probado con ruido sintético (100 N + 60 Hz de σ 2.6 N + 0.75 N + picos).
- **Resultado:** σ 2.25 → 0.20 N, sin sesgo (media 100.00 N); retardo 4 → 11 ms (+7 ms, resta ≈2° de margen de fase). Activo por defecto; `--sin_filtro_60hz` lo apaga.
- **Limitaciones:** NO probado con el ADC real; el filtro no ataca la causa (origen eléctrico sin determinar) y el retardo extra se suma a un margen estrecho. Diagnóstico de la causa (otra toma/regleta, tierra común con el amplificador del AMTI, cable GND corto) queda para la RPi con Luis.
- **Fuentes:** `control/lazo_fz_tiempo_real.py` (`filtrar_60hz`), `pruebas/ruido_60hz_filtro.py`, `reportes/2026-11-18_etapa2_R2_rpi_uart.md`.

## 4. Cambios de código y datos del lazo
- `--fuente_fz uart --puerto_fz /dev/ttyAMA0` es ahora el defecto (el cableado SPI directo ya no existe); el `.meta.txt` registra `fuente_fz` y `filtro_60hz`.
- **Bug encontrado por simulación:** la columna `t` del CSV era `i·10 ms` (nominal); el periodo real estimado es ~13.5 ms (la interfaz mide 13.0 ms) → las corridas «x10» fueron ≈x13.5 y las frecuencias de los CSV del 11-18 salen ~1.35× altas. Corregido: columna nueva `t_real`. **Contradice** la afirmación del 11-18 de «período real 10.0 ms medido en el log», que venía de la columna nominal.
- Nuevo `control/telemetria/espectro_corrida.py` (pico 3–15 Hz, RMS 5–10 Hz por pisada). Probado con senoides sintéticas (7.00 y 4.07 Hz para 7.0 y 4.0 reales), no con CSV reales.
- Prueba en `--simulado`: 2 ciclos completan, Y vuelve a 0.

## 5. Documentación
- **Protocolo para la RPi:** `reportes/2026-11-19_protocolo_proxima_sesion_rpi.md` (preflight → 60 Hz → Kp 5/3/5 a 70 kg x10 ANTES del HOME → HOME sin prótesis → copiar CSV → bloqueados). Hallazgos: el lazo por script reinicia el ESP32 de motores y borra el HOME; `escalera_carga.py` no sirve para la prueba (sin `--kp`, hueco sin remedir). Tabla de decisión Kp 3 vs 5 corregida según §1.
- **Punto de entrada:** `INICIO_SESION_SIGUIENTE.md` § 00.
- **Diagrama de bloques/ecuaciones** (`control/diagramas/salida/`): bloque (5) filtro de medición, saturación en (3), parámetros medidos (Kp real, τa, k, T). **Sigue siendo el diagrama de la simulación; falta el estimador de k, que se agrega cuando esté integrado y validado.**
- **Esquema eléctrico vigente** (`esquemas/amti_ads1256_rpi/salida/esquema_protecciones_ads1256.png`): solo textos (ya cableado y funcionando; abierto: 60 Hz, R6 con NetForce, 1 kΩ, rango Fz).
- **Eliminados por obsoletos** (recuperables de git): `control/diagramas/implementacion/`, `esquema_amti_ads1256_rpi.*` (2-nov).
- **Reglas fijas nuevas en `CLAUDE.md`:** (1) verificar que un archivo es el vigente ANTES de modificarlo; (2) lo superado se elimina y se anota cuál es el vigente. Origen: rehice un diagrama obsoleto por no comprobar cuál era el vigente.

## Limitaciones generales
Todo es simulación/diseño; ningún cambio se probó con el ADC, el ESP32 ni el servo. Pendiente con Luis: umbral de error (< __ %BW) para pasar a Fy, escala para 80 kg, recorrido máximo de la precarga, diagnóstico eléctrico del 60 Hz.

## Fuentes
`CLAUDE.md` (entradas 2026-11-17/18/19), `reportes/2026-11-18_escalera_50_a_90kg_x10_y_abortos.md`, `reportes/2026-11-18_ensayo_B_respuesta_dinamica.md`, `reportes/2026-11-19_plan_lazos_z_y_cop_ads1256.md`, y los reportes `reportes/2026-11-19_*.md` citados arriba.
