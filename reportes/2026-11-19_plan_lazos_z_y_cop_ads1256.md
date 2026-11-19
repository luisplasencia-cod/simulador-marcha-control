# Plan: lazos Z → Y → CoP con el ADS1256 actual (mientras llega el AD7606)

Fecha: 2026-11-19. Documento de planificación: **nada de esto está ejecutado ni medido.**

## Objetivo
Avanzar los lazos horizontal (Fy) y sagital (CoP) sin esperar al AD7606, leyendo los
canales del AMTI uno por uno con el ADS1256 que ya funciona (ruta ESP32 → UART → RPi,
validada el 2026-11-18 solo con Fz), y dejar pruebas repetibles para comparar después
contra el AD7606.

## Decisión de partida (Luis, 2026-11-19)
- Orden: **Z (Fz) → Y/horizontal (Fy) → sagital guiado por el CoP del AMTI**.
- El CoP sale de las salidas analógicas del AMTI. Forma general (plataforma tipo AMTI,
  a confirmar en el manual/certificado del equipo de este lab, signos y ejes incluidos):
  `CoP_x = (−My − Fx·dz) / Fz`, `CoP_y = (Mx − Fy·dz) / Fz`, con `dz` = altura de la
  superficie sobre el origen eléctrico (dato del certificado: **NO verificado**).
  Mz no hace falta para el CoP. Solo con Fz > 20 N (umbral del artículo de conferencia).
- ⚠️ Notación: los ejes del AMTI (x, y) no tienen por qué coincidir con los del proyecto
  (y = avance, z = vertical). Fijar el mapeo AMTI → simulador antes de usar Fy.

## Restricciones conocidas (análisis propio, sin medir)
1. **Entradas:** el ADS1256 tiene 8 entradas → máx. 4 pares diferenciales. Fz + Fy en
   diferencial cabe; los 5 canales del CoP no: parte (o todos) en single-ended contra AINCOM.
2. **Tasa por canal:** al conmutar el MUX el ADS1256 necesita asentarse; la tasa por
   canal cae mucho respecto de 1000/s con 1 canal. Medir, no asumir (hoja SBAS288, tabla
   de throughput con multiplexado: por leer).
3. **UART:** a 115200 baud con 1 canal ya se estimó ≈87 % de ocupación con Fz ≥ 1000 N →
   para 2–5 canales subir baudios (p. ej. 921600, verificar en el RPi 5 `ttyAMA0`) y/o
   paquete binario con número de secuencia y checksum.
4. **Desfase entre canales:** las muestras no son simultáneas (fracción de ms). A x6 las
   señales son lentas, así que probablemente sea despreciable — **verificar** comparando
   con el AD7606 cuando llegue.
5. **Cableado:** hoy solo Fz llega al ADC. Hay que llevar Fy (y luego Fx, Mx, My) desde el
   amplificador del AMTI, con las mismas protecciones (1 kΩ en serie por entrada).
6. Ruido de 60 Hz (σ ≈ 2.3–2.7 N en el RPi, origen sin determinar) afecta a todos los canales.

## Metodología por fases
**Fase Z (en curso):** cerrar Fz con trayectoria + HOME en la interfaz; decidir escala para
80 kg (límite de velocidad de Y). No depende del ADC nuevo.

**Fase Y-1 (2 canales, ADS1256):**
1. Firmware del ESP32 de lectura: alternar MUX Fz/Fy, paquete con ambos + secuencia; subir baudios.
2. Medir: tasa por canal, pérdidas, ruido por canal, diafonía (carga solo vertical → ¿se ve en Fy?).
3. Calibrar Fy con fuerza horizontal conocida vs NetForce.
4. Recién entonces: lazo de Fy en X (restricción: X solo avanza).

**Fase CoP-1 (5 canales, ADS1256):**
1. Leer Fx, Fy, Fz, Mx, My (single-ended donde haga falta); medir tasa y ruido.
2. Validar CoP: masa conocida colocada en puntos conocidos del plato → error de CoP vs
   posición real y vs NetForce.
3. Diseñar el lazo sagital con la progresión del CoP.

**Fase AD7606 (cuando llegue):** repetir exactamente Y-1 y CoP-1 y comparar (tasa, ruido,
desfase, error de CoP). Decidir con datos si el AD7606 hace falta para el lazo o solo para
el registro de energía.

## Criterios de paso (propuestos, a fijar por Luis)
- Y-1: 0 pérdidas en 10 min, tasa por canal ≥ __ /s, diafonía < __ N.
- CoP-1: error de CoP < __ mm con masa conocida.

## Limitaciones
- Plan sin ejecutar; todos los números de rendimiento están por medir.
- Fórmula y signos del CoP por confirmar con la documentación del AMTI de este lab.

## Fuentes
- CLAUDE.md (estado 2026-11-18: ruta ESP32 + ADS1256 + UART, R2–R5, lazo de Fz).
- `reportes/2026-11-18_etapa2_R2_rpi_uart.md` (ocupación de UART, 60 Hz).
- Hoja del ADS1256 (TI SBAS288): por leer para la tasa con multiplexado.
