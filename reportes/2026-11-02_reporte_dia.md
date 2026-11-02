# Reporte del día — 2026-11-02

Resumen de lo avanzado hoy en la etapa de control del simulador de marcha, para presentar hasta donde se llegó.

## 1. Organización del proyecto
- Repo publicado en GitHub: https://github.com/luisplasencia-cod/simulador-marcha-control
- Carpeta `referencias/` creada con convención por tema (01_vacio_investigacion, 02_control_fuerza_grf, 03_energia, 04_interfaz_protesis, 05_otros, 06_grf_referencia) — cada referencia con fuente (PDF o link) y notas extraídas (clave para decisión + resumen de lectura).
- `INICIO_RPI.md` creado — punto de entrada para que una sesión de Claude en el Raspberry Pi sepa qué hacer sin que Luis tenga que re-explicar el contexto.

## 2. Búsqueda bibliográfica (ejecutada hoy)
- **Vacío de investigación:** sigue sin cerrarse. Nuevo antecedente cercano: Fine et al. 2026 (DOI 10.1088/1873-4030/aebb30) — simulador cuasi-estático transtibial, no automático de lazo cerrado de GRF; texto completo pendiente de descarga (paywall).
- **Ancho de banda / latencia máxima tolerable para control de fuerza:** no encontrado en la literatura revisada (Aubin 2008/2012, Insam 2021).
- **GRF de referencia:** se corrigió un dato sin respaldo (el "~126%BW esperado" no tenía fuente verificada). La curva propia del simulador (marcha lenta, 0.48 m/s) muestra picos de 97.4%BW y 102.5%BW. Datasets externos de acceso abierto identificados como respaldo: Horst 2021 (350 sujetos sanos) y Fukuchi 2018 (42 sujetos).

## 3. Conexión física AMTI → ADS1256 → Raspberry Pi
- **Ya cableada por Luis.**
- Pines reales confirmados leyendo la etiqueta física de la placa (no genéricos): señal Fz → AIN0, referencia → GND (junto a AIN0); lado digital 5V/GND/SCLK/DIN/DOUT/DRDY/CS/PDWN.
- GPIO del Raspberry Pi asignados: SCLK→GPIO11, DIN→GPIO10, DOUT→GPIO9, CS→GPIO8 (fijos por hardware SPI0 de cualquier RPi), DRDY→GPIO17, PDWN atado fijo a +3.3V (no a un GPIO, para que nunca quede en power-down).
- **VREF identificado:** chip ADR03B (Analog Devices, precisión ±0.1%) = 2.5V nominal. Full-scale con PGA=1 = 5V; los 3.4V máximos del AMTI (escala 1.7V/1000N, máx. 2000N) quedan al 68% del rango, sin riesgo de saturar.
- Esquema completo: `esquemas/amti_ads1256_rpi/salida/esquema_amti_ads1256_rpi.png` (+ `.svg`), registro de configuración en `esquemas/amti_ads1256_rpi/CONFIGURACION_ACTUAL.md`.

## 4. Prueba de latencia RPi↔ESP32
- Firmware del ESP32 revisado: ya tenía un comando `PING`→`PONG` listo para medir latencia — no se modificó el firmware.
- **Hallazgo del código:** el firmware espera datos seriales con un sondeo (`vTaskDelay(5ms)`) → hasta 5 ms de latencia propia del firmware se suma a cualquier medición, independiente del cable.
- Scripts listos y probados (con datos sintéticos, no en el RPi real todavía):
  - `pruebas/medir_latencia_ping_pong.py` — mide RTT, guarda CSV.
  - `pruebas/graficar_latencia.py` — grafica histograma + serie temporal del RTT.
- Plan de ejecución documentado en `pruebas/2026-11-02_latencia_amti_rpi_esp32.md`.

## Pendiente para continuar
1. Correr `medir_latencia_ping_pong.py` en el Raspberry Pi real y documentar el resultado.
2. Escribir el script de lectura del ADS1256 (AMTI) — todavía no existe.
3. Con la latencia medida, avanzar a la Fase 3: decidir tiempo real vs. ILC.
4. Identificar modelo exacto de la placa ADS1256 (no crítico, VREF ya resuelto por el chip identificado).
5. Respuesta de Dante Elías y confirmación de la asesora (pendientes desde antes, sin novedad hoy).

## Anexo — sesión en el Raspberry Pi (2026-11-02)
- `git pull` hecho; entorno `.venv` creado (matplotlib instalado; pyserial ya presente). `.venv/` añadido a `.gitignore`.
- **Latencia RPi↔ESP32 medida** (ESP32 ya conectado, `/dev/ttyUSB0`): 100/100 válidos, RTT medio 5.974 ms, desv. 0.185 ms, mín/máx 4.139/6.047 ms. Dominado por el polling de 5 ms del firmware. Detalle en `pruebas/2026-11-02_latencia_amti_rpi_esp32.md`, datos en `pruebas/latencia_ping_pong.csv/.png`. (Un primer intento antes de conectar el ESP32 dio 0 respuestas.)
- **SPI deshabilitado** en el RPi (`dtparam=spi=on` comentado) → hay que activarlo antes de leer el ADS1256.
- Firmware del ESP32: sin cambios; se edita/flashea solo desde la laptop.
