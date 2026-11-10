# Límite de velocidad del SPI (SCLK) del ADS1256 — 2026-11-10

## Objetivo
Comprobar si el reloj SPI que usamos (500 kHz) puede estar causando las caídas o los errores de bit del ADS1256, dado que Luis recordó que la hoja de datos advierte problemas por encima de ≈1.7 MHz.

## Metodología
- Revisión del código: `pruebas/leer_ads1256_fz.py` (`SPI_HZ = 500_000`, pausas entre comandos).
- Búsqueda web (modo estándar, 2 consultas). **Solo se leyeron los resúmenes de los resultados; no se abrió la hoja de datos del ADS1256.**

## Resultado
- **Nuestro reloj:** 500 kHz en el código; pruebas del 2026-11-05 con el chip a 50 kHz, 250 kHz, 500 kHz y 1 MHz. Los 2 MHz se probaron solo en loopback del RPi (sin la placa).
- **Regla encontrada:** periodo mínimo de SCLK = 4·t(CLKIN) → SCLK máx = fCLKIN/4. Con cristal de 7.68 MHz: **1.92 MHz** (foro TI E2E y MathWorks; la tabla de tiempos vista es de la hoja del **ADS1257**, pariente cercano, no del ADS1256). Luis recordaba ≈1.7 MHz: mismo orden, valor exacto **NO verificado**.
- **t6 (comando→dato):** 50·t(CLKIN) ≈ 6.5 µs (ADS1257; mismo valor citado para el ADS1256 en foros). Con 500 kHz un byte dura 16 µs: se cumple.
- **Cristal de nuestra placa:** el código asume 7.68 MHz por un comentario; **no se verificó el marcado del cristal en la placa**.
- **Conclusión sobre las fallas:** 500 kHz está por debajo del límite. El estado "caído" (DRDY fijo en alto, registros 0) ocurrió igual a 50 kHz y 500 kHz, así que no es un problema de velocidad. Los errores de bit medidos (0.06 % a 1 MHz, 0.30 % a 500 kHz, 0.50 % a 250 kHz) crecen al BAJAR el reloj: tampoco los explica un SCLK alto. Un foro de TI reporta que bajar el reloj le dio datos correctos a un usuario, pero otra respuesta dice que la velocidad sola puede no ser la causa.

## Limitaciones
- Hoja de datos del ADS1256 (SBAS288K) no leída directamente; cifras de foros y de la hoja del ADS1257.
- Cristal de la placa sin verificar; sin osciloscopio sobre SCLK/DRDY.

## Fuentes
- https://ti.com/document-viewer/ADS1257/datasheet (tabla de tiempos, ADS1257)
- https://www.ti.com/lit/SBAS288 (hoja del ADS1256, a leer)
- https://www.mathworks.com/matlabcentral/answers/379265-raspberry-pi-interface-with-ads1256
- https://e2e.ti.com/support/data-converters-group/data-converters/f/data-converters-forum/888837/ads1256-best-performance-method-for-delta-sigma-ad
- https://github.com/Habraken/WaveShare-ADS1256
