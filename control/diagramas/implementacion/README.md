# control/diagramas/implementacion/ — diagrama de implementación real (Fz)

Complementario a `../diagrama_lazo_hibrido.py` (el matemático: $r(t)$, $e(t)$, $K_p$, la planta).
Este dibuja **dónde vive cada pieza física** y por qué cable/protocolo se conecta: AMTI → ADS1256
→ Raspberry Pi (ahí corren $K_p \cdot e(t)$ y el ILC) → cable USB serie con `SET_VEL` (propuesto)
→ ESP32 → driver A6-750RS → servomotor vertical A6M80-750H2B1-M17 (con freno integrado, confirmado en `conferencia_copy.pdf` — distinto del horizontal, A6M80-750H2A1-M17, sin freno).

Generar: `python esquema_implementacion_fz.py` → `salida/esquema_implementacion_fz.png` (+ `.svg`).

**Nada de la parte RPi→ESP32 con `SET_VEL` está probado en hardware** — el diagrama documenta la
arquitectura propuesta, con esa parte marcada en naranja/rojo, no algo verificado funcionando.
Fotos reales del driver/motor usadas de referencia: `../referencias/`.
