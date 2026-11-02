"""Lee el canal Fz del AMTI a traves del ADS1256, usando la configuracion ya
verificada en esquemas/amti_ads1256_rpi/CONFIGURACION_ACTUAL.md:
  - Senal -> AIN0, referencia -> AINCOM (el pin que en ESTA placa esta
    etiquetado "GND junto a AIN0" - electricamente es el AINCOM del chip).
  - VREF = 2.5V (chip ADR03B identificado en la placa).
  - PGA = 1 -> full-scale = 2*VREF/PGA = 5V.
  - SPI0 por hardware: CS=GPIO8, SCLK=GPIO11, MOSI(DIN)=GPIO10, MISO(DOUT)=GPIO9.
  - DRDY = GPIO17 (entrada, activo en bajo: indica dato nuevo listo).
  - PDWN esta atado FIJO a 3.3V en hardware (no se controla por software).
  - Escala AMTI: 1.7 V por cada 1000 N (medido por Luis), maximo 2000 N -> 3.4 V.

AVISO NO VERIFICADO: la frecuencia del oscilador CLKIN de ESTA placa no se
confirmo (el valor tipico en placas ADS1256 es 7.68 MHz, pero no se midio).
Por eso el script usa un reloj SPI conservador (200 kHz) con bytes de relleno
de sobra para cubrir el retardo t6 del datasheet (50 tCLKIN) con margen,
en vez de calcular el tiempo exacto. Si las lecturas salen inconsistentes o
DRDY nunca baja, confirmar CLKIN y ajustar SPI_HZ/PADDING.

Uso:
    pip install spidev RPi.GPIO
    python leer_ads1256_fz.py --n 100 --salida lecturas_fz.csv
"""
import argparse
import csv
import time

import RPi.GPIO as GPIO
import spidev

# --- Comandos ADS1256 (Table 24 del datasheet TI ADS1256 Rev K, verificados 2026-11-02) ---
CMD_WAKEUP = 0x00
CMD_RDATA = 0x01
CMD_SDATAC = 0x0F
CMD_RREG = 0x10
CMD_WREG = 0x50
CMD_SELFCAL = 0xF0
CMD_RESET = 0xFE

REG_STATUS = 0x00
REG_MUX = 0x01
REG_ADCON = 0x02
REG_DRATE = 0x03

DRDY_PIN = 17  # BCM, GPIO17 (ver esquema)
SPI_HZ = 200_000  # conservador; ver AVISO arriba
PADDING_BYTES = 6  # bytes de relleno tras RDATA antes de leer, para cubrir t6 con margen

VREF = 2.5  # chip ADR03B, confirmado fisicamente en la placa
PGA = 1
FULL_SCALE_V = 2 * VREF / PGA  # 5.0 V
N_PER_1000N = 1.7  # V por cada 1000 N, medido por Luis en el lab


def to_signed24(b0, b1, b2):
    raw = (b0 << 16) | (b1 << 8) | b2
    if raw & 0x800000:
        raw -= 1 << 24
    return raw


class ADS1256:
    def __init__(self, bus=0, device=0):
        self.spi = spidev.SpiDev()
        self.spi.open(bus, device)
        self.spi.max_speed_hz = SPI_HZ
        self.spi.mode = 0b01  # ADS1256 usa SPI modo 1 (CPOL=0, CPHA=1)

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(DRDY_PIN, GPIO.IN)

        self._init_chip()

    def _wreg(self, reg, value):
        self.spi.xfer2([CMD_WREG | reg, 0x00, value])

    def _init_chip(self):
        self.spi.xfer2([CMD_RESET])
        time.sleep(0.01)
        self.spi.xfer2([CMD_SDATAC])
        self._wreg(REG_MUX, 0x08)      # PSEL=AIN0 (0000), NSEL=AINCOM (1000)
        self._wreg(REG_ADCON, 0x00)    # CLK off, SDCS off, PGA=1 (000)
        # DRATE: se deja el valor de reset (F0h, maxima tasa) - no se cambia a proposito
        self.spi.xfer2([CMD_SELFCAL])
        self._wait_drdy(timeout_s=2.0)

    def _wait_drdy(self, timeout_s=1.0):
        t0 = time.monotonic()
        while GPIO.input(DRDY_PIN) == 1:
            if time.monotonic() - t0 > timeout_s:
                raise TimeoutError("DRDY no bajo a tiempo - revisar cableado/VREF/CLKIN")
            time.sleep(0.0005)

    def leer_codigo(self):
        self._wait_drdy()
        resp = self.spi.xfer2([CMD_RDATA] + [0x00] * PADDING_BYTES + [0x00, 0x00, 0x00])
        b0, b1, b2 = resp[-3], resp[-2], resp[-1]
        return to_signed24(b0, b1, b2)

    def leer_volts(self):
        codigo = self.leer_codigo()
        return codigo * FULL_SCALE_V / (1 << 23)

    def cerrar(self):
        self.spi.close()
        GPIO.cleanup()


def volts_a_newtons(v):
    return v * 1000.0 / N_PER_1000N


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=100)
    ap.add_argument("--salida", default="lecturas_fz.csv")
    ap.add_argument("--periodo_s", type=float, default=0.0, help="pausa entre lecturas, 0 = lo mas rapido posible")
    a = ap.parse_args()

    adc = ADS1256()
    filas = []
    try:
        for i in range(a.n):
            t0 = time.perf_counter()
            v = adc.leer_volts()
            n = volts_a_newtons(v)
            filas.append([i, round(v, 6), round(n, 3)])
            print(f"[{i}] {v:.6f} V  ->  {n:.2f} N")
            if a.periodo_s > 0:
                time.sleep(a.periodo_s)
    finally:
        adc.cerrar()

    with open(a.salida, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["intento", "volts", "newtons"])
        w.writerows(filas)
    print(f"\nCSV guardado en: {a.salida}")
    print("IMPORTANTE: con 0 N reales aplicados, 'newtons' deberia estar cerca de 0 (offset en reposo).")
    print("Si no, hay un offset de cero del AMTI/ADS1256 pendiente de restar (calibracion, Paso 4 del plan).")
