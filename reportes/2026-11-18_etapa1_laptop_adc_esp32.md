# Reporte: Etapa 1 (laptop) — ADS1256 leído por el ESP32 de lectura, primera prueba real

## Objetivo
Confirmar desde la laptop, antes de pasar a la RPi, que la ruta nueva AMTI → 1 kΩ → ADS1256 (diferencial
AIN1/AIN0) → ESP32 de lectura funciona: el ADC responde, mide a 1000 muestras/s, el signo y la escala de Fz
son correctos y no se cae en reposo. Plan seguido: `INICIO_RPI.md`, Etapa 0 y Etapa 1.

## Metodología
1. **Etapa 0 (Luis):** voltajes medidos con multímetro antes de energizar el resto — "todo correcto" (5 V
   después de R5, PDWN ≈ 3.3 V, VREF ≈ 2.5 V; Luis no dictó los valores numéricos).
2. **Placa:** ESP32 DevKit V1 (módulo WROOM-32, dicho por Luis). `esptool` identifica el chip como
   ESP32-D0WD-V3 rev 3.1, MAC 00:70:07:84:48:50, flash 4 MB. GPIO16/17 libres (no es WROVER).
3. **Respaldo** de la flash completa antes de flashear (4 MB, 380 s):
   `control/firmware/respaldos_flash/esp32_lectura_adc_original_flash_0x0_0x400000_20261118.bin`
   (SHA-256 `bb2a0c57…7195fb`, archivo `.sha256` al lado). Es el firmware que Luis tenía grabado (el del zip
   `platformIO_medicion_sensores_v1`, escala 1.7631).
4. **Flasheo** del firmware del repo (`control/firmware/lectura_ads1256_esp32_diferencial/`,
   `espressif32 @ 7.0.1`, entorno `esp32dev`, Bluetooth encendido) por COM8.
5. **Diagnóstico por USB** (`pruebas/registrar_diag_esp32_usb.py`): informe de arranque + 1 línea por segundo.
6. **Ventana en vivo** nueva (`pruebas/visor_fz_esp32_usb.py`): Fz a 100 muestras/s por el USB, teclas
   `t` tara / `m` marca, registro CSV. Para esto se agregó al firmware una copia `F,<valor>` cada 10 muestras
   **solo por el USB**; el paquete `<valor>` por UART2 hacia la RPi no cambió.
7. **Prueba con masa:** AMTI encendido y conectado, plato vacío → pesa de **2.246 kg** (pesada en una balanza
   "en teoría calibrada", Luis) puesta y quitada 2 veces.
8. **Vigilancia en reposo:** 5 min (Luis pidió acortar de 30 a 5 por tiempo).

## Resultado
- **Arranque:** motivo de reinicio `POWERON`; registros STATUS 0x31 (ID del chip OK), MUX 0x10, ADCON 0x00,
  DRATE 0xA1 → **4/4 OK**. `ADS1256 OK`.
- **Tasa y transmisión:** 1000 muestras/s; período máximo ≈ 1.0–1.5 ms; 0 pérdidas, 0 ceros, 0 saturadas
  (1 pérdida solo en el primer segundo tras arrancar). Tiempo de lectura SPI + envío UART2 ≈ 320 µs de los
  1000 µs disponibles (con Fz pequeña; con Fz ≥ 1000 N los paquetes son más largos, falla F14 sin probar).
- **Ruido en reposo:** σ ≈ 0.70–0.79 N (el lector directo RPi-SPI anterior daba ≈ 0.85 N).
- **Offset en reposo:** ≈ −1.8 a −3.7 N; **deriva −0.65 N en ≈ 100 s** con el plato vacío → tarar antes de
  cada medición.
- **Masa 2.246 kg** (esperado 21.97 N con g = 9.7827 m/s² de Lima; 22.03 N con g estándar):

  | | Vacío antes | Con pesa | Escalón | vs esperado (g Lima) |
  |---|---|---|---|---|
  | Ciclo 1 | −1.830 N | 20.274 N | 22.37 N | +1.8 % |
  | Ciclo 2 | −2.369 N | 20.256 N | 22.68 N | +3.2 % |

  **Signo correcto** (Fz sube al cargar). El valor con carga repite (20.27 vs 20.26 N); la diferencia entre
  escalones viene de la deriva del vacío. Datos: `pruebas/resultados/visor_fz_20261118_110422.csv`.
- **Vigilancia 5 min en reposo (298 s registrados):** **0 caídas**, 0 alertas, 0 pérdidas, 0 ceros, 0 saturadas;
  1000–1001 muestras/s todos los segundos; σ 0.68–0.89 N; media −2.37 a −2.74 N (deriva del vacío); período
  máximo 1.38 ms; lectura + envío UART2 máx. 0.49 ms. Datos: `pruebas/resultados/diag_esp32_usb_20261118_110831.txt`.

### Incidente: el puerto COM8 daba "acceso denegado" (≈1 h perdida)
- **Causa real:** `C:\PB2\display\server.py`, otro proyecto de Luis que arranca solo con la laptop, busca
  cualquier ESP32 con chip CP210x (por defecto COM8) y lo mantiene abierto, reconectándose. Estaba corriendo
  en cada intento fallido (procesos iniciados 2026-11-17 08:05, 2026-11-18 10:08 y 10:50). Detenerlo por PID
  resolvió el problema de inmediato.
- **Errores míos en el camino (para no repetirlos):**
  1. `pnputil /disable-device` sin permisos de administrador "no hizo nada" según su salida, pero **sí dejó el
     CP210x deshabilitado** (código 22) y sobrevivió al reinicio; Luis tuvo que rehabilitarlo a mano.
  2. Dije que era un problema de permisos de mi sesión: falso (la ventana propia de Luis daba lo mismo).
  3. Atribuí el bloqueo a **Fortinet** y Luis lo **desinstaló**. Lo más probable es que **no era la causa**:
     el puerto abrió tras ese reinicio solo porque `server.py` todavía no había arrancado. **Si Luis usa la VPN
     de Fortinet, puede reinstalarla.**
- **Regla para la próxima vez:** si un COM está ocupado, buscar primero procesos con `serial`/`COM` en su línea
  de comando (`Get-CimInstance Win32_Process`) y revisar `C:\PB2\display\server.py`.

## Limitaciones
- **Una sola masa** → no se verificó la linealidad. El +2–3 % de escala no se puede atribuir todavía: puede ser
  el amplificador AMTI, la balanza, g o la deriva del cero. **Falta comparar con NetForce** con la misma pesa
  (si NetForce también marca ≈ 22.5 N, la ruta del ADC está bien). Mi predicción previa de ≈ −1 % por las
  resistencias de 1 kΩ **no se cumplió**.
- **Paso L4 (UART2 en la laptop) no hecho:** no hay adaptador USB-TTL. La ruta UART2 se prueba recién en la RPi.
- La vigilancia fue de 5 min (el plan pedía 30) y **en reposo**: no dice nada sobre caídas con el servo en
  marcha, que es donde fallaba antes (prueba R5 en la RPi).
- No se probó el entorno `sin_bt` (ruido sin Bluetooth).
- Los voltajes de la Etapa 0 los midió Luis y reportó "correcto" sin cifras.

## Fuentes
- Plan: `INICIO_RPI.md` (Etapas 0–2, catálogo de fallas).
- Firmware: `control/firmware/lectura_ads1256_esp32_diferencial/src/main.cpp`.
- Datos: `pruebas/resultados/diag_esp32_usb_20261118_110040.txt` (arranque + 1 min),
  `pruebas/resultados/visor_fz_20261118_110422.csv` (prueba con masa),
  `pruebas/resultados/diag_esp32_usb_20261118_11*.txt` (vigilancia 5 min).
- g en Lima ≈ 9.7827 m/s² (valor aproximado por latitud ≈ 12° S y nivel del mar, **no medido**).
