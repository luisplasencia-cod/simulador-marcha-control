"""Lee el canal Fz del AMTI a traves del ADS1256, conectado DIRECTO al RPi por SPI0.

Arquitectura vigente (2026-11-02): el unico ESP32 con este RPi es el de control de
motores. El ADS1256 lo lee el RPi mismo. El firmware `Codigo ESP32 ADS1256/` fue una
prueba aislada y se usa SOLO como referencia de la secuencia de inicializacion
(RESET -> SDATAC -> ADCON -> MUX -> DRATE -> SELFCAL -> SYNC -> WAKEUP -> RDATAC),
que ya funciono en hardware. Esta secuencia esta replicada aqui.

Configuracion (esquemas/amti_ads1256_rpi/CONFIGURACION_ACTUAL.md):
  - Senal Fz -> AIN0, referencia -> AINCOM (pin "GND junto a AIN0"): MUX = 0x08.
    (El firmware de referencia usaba diferencial AIN1/AIN0 con SU cableado; aqui
    es el cableado de ESTE montaje, no mezclar.)
  - VREF = 2.5 V (ADR03B), PGA = 1 -> full-scale = 2*VREF/PGA = 5 V.
  - SPI0: CS=GPIO8, SCLK=GPIO11, MOSI(DIN)=GPIO10, MISO(DOUT)=GPIO9. DRDY=GPIO17.
  - PDWN fijo a 3.3 V. Escala AMTI: 1.7665 mV/N (OPT SC serie 4306, ganancia Fz 2000).

Lectura: modo continuo (RDATAC). Con DRDY en bajo se hacen 3 lecturas de reloj y
listo. El metodo anterior (comando RDATA + bytes de relleno) desplazaba el dato
fuera de la ventana y devolvia siempre 0x000000/0xFFFFFF (0 V / -1 LSB en TODOS
los canales) - corregido 2026-11-02.

Uso:
    python leer_ads1256_fz.py --n 1000 --salida lecturas_fz.csv
    python leer_ads1256_fz.py --diagnostico      # registros + 8 canales
"""
import argparse
import csv
import time

import RPi.GPIO as GPIO
import spidev

# --- Comandos (datasheet ADS1256 Rev K, Table 24) ---
CMD_WAKEUP = 0x00
CMD_SDATAC = 0x0F
CMD_RDATAC = 0x03
CMD_RREG = 0x10
CMD_WREG = 0x50
CMD_SELFCAL = 0xF0
CMD_SYNC = 0xFC
CMD_RESET = 0xFE

REG_STATUS, REG_MUX, REG_ADCON, REG_DRATE, REG_IO = 0x00, 0x01, 0x02, 0x03, 0x04

MUX_AIN0_AINCOM = 0x08  # PSEL=AIN0, NSEL=AINCOM
ADCON_PGA1 = 0x00
DRATE_1000SPS = 0xA1    # 30 kSPS (reset) es demasiado rapido para Python

DRDY_PIN = 17
SPI_HZ = 500_000  # byte = 16 us > t6 (~6.5 us con CLKIN 7.68 MHz): RREG alineado

VREF = 2.5
PGA = 1
FULL_SCALE_V = 2 * VREF / PGA
N_PER_1000N = 1.7665  # V por 1000 N


def to_signed24(b0, b1, b2):
    raw = (b0 << 16) | (b1 << 8) | b2
    return raw - (1 << 24) if raw & 0x800000 else raw


class ADS1256:
    def __init__(self, bus=0, device=0, mux=MUX_AIN0_AINCOM, drate=DRATE_1000SPS):
        self.mux, self.drate = mux, drate
        self.spi = spidev.SpiDev()
        self.spi.open(bus, device)
        self.spi.max_speed_hz = SPI_HZ
        self.spi.mode = 0b01  # CPOL=0, CPHA=1
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(DRDY_PIN, GPIO.IN)
        self._init_chip()

    # -- bajo nivel
    def _cmd(self, c):
        self.spi.xfer2([c])
        time.sleep(0.00002)

    def _wreg(self, reg, value):
        self.spi.xfer2([CMD_WREG | reg, 0x00, value])
        time.sleep(0.00002)

    def rreg(self, reg):
        """Lee un registro (solo en modo SDATAC). Dato en el 4.o byte (comprobado en hardware)."""
        return self.spi.xfer2([CMD_RREG | reg, 0x00, 0x00, 0x00])[-1]

    def _wait_drdy(self, timeout_s=1.0):
        t0 = time.monotonic()
        while GPIO.input(DRDY_PIN) == 1:
            if time.monotonic() - t0 > timeout_s:
                raise TimeoutError("DRDY no bajo a tiempo - revisar cableado/VREF/CLKIN")
            time.sleep(0.0001)

    def _wait_drdy_alto_bajo(self, timeout_s=2.0):
        """Espera a que DRDY suba y vuelva a bajar (fin de una calibracion/sync)."""
        t0 = time.monotonic()
        while GPIO.input(DRDY_PIN) == 0 and time.monotonic() - t0 < 0.05:
            time.sleep(0.0001)  # tras el comando DRDY sube; si ya estaba bajo, no esperar de mas
        self._wait_drdy(timeout_s)

    # -- inicializacion (misma secuencia que el firmware de referencia)
    def _init_chip(self):
        # Si un programa anterior se cerro sin cerrar() el chip sigue en RDATAC y solo acepta
        # SDATAC: mandarlo primero (varias veces) y recien despues RESET.
        for _ in range(3):
            self._cmd(CMD_SDATAC)
        self._cmd(CMD_RESET)
        time.sleep(0.1)  # el reset interno tarda ~8 ms; DRDY no es confiable justo despues
        self._cmd(CMD_SDATAC)
        self._wreg(REG_ADCON, ADCON_PGA1)
        self._wreg(REG_MUX, self.mux)
        self._wreg(REG_DRATE, self.drate)
        # Verificar que el SPI realmente responde (detecta MISO/CS mal conectado)
        leido = {"ADCON": self.rreg(REG_ADCON), "MUX": self.rreg(REG_MUX), "DRATE": self.rreg(REG_DRATE)}
        esperado = {"ADCON": ADCON_PGA1, "MUX": self.mux, "DRATE": self.drate}
        if leido != esperado:
            raise RuntimeError(f"El ADS1256 no devolvio lo escrito: leido={leido} esperado={esperado}")
        self._cmd(CMD_SELFCAL)
        self._wait_drdy_alto_bajo(2.0)
        self._cmd(CMD_SYNC)
        time.sleep(0.00001)
        self._cmd(CMD_WAKEUP)
        self._cmd(CMD_RDATAC)  # modo continuo: a partir de aqui NO se aceptan RREG/WREG
        self._wait_drdy(1.0)

    # -- lectura
    def leer_codigo(self):
        self._wait_drdy()
        b = self.spi.xfer2([0x00, 0x00, 0x00])
        return to_signed24(*b)

    def leer_volts(self):
        return self.leer_codigo() * FULL_SCALE_V / (1 << 23)

    def cambiar_mux(self, mux):
        """Cambia de canal (solo diagnostico): sale de RDATAC, escribe, sincroniza y vuelve."""
        self._cmd(CMD_SDATAC)
        self._wreg(REG_MUX, mux)
        self._cmd(CMD_SYNC)
        time.sleep(0.00001)
        self._cmd(CMD_WAKEUP)
        self._cmd(CMD_RDATAC)
        self.mux = mux
        self.leer_codigo()  # descarta la conversion de transicion
        self.leer_codigo()

    def cerrar(self):
        try:
            self._cmd(CMD_SDATAC)
        finally:
            self.spi.close()
            GPIO.cleanup()


def volts_a_newtons(v):
    return v * 1000.0 / N_PER_1000N


def diagnostico():
    adc = ADS1256()
    try:
        adc._cmd(CMD_SDATAC)
        print("Registros (STATUS, MUX, ADCON, DRATE):",
              [hex(adc.rreg(r)) for r in (REG_STATUS, REG_MUX, REG_ADCON, REG_DRATE)])
        adc._cmd(CMD_RDATAC)
        print("Canales vs AINCOM (100 muestras c/u). Canal con senal real: media != 0 y ruido de varios uV:")
        for ch in range(8):
            adc.cambiar_mux((ch << 4) | 0x08)
            v = [adc.leer_volts() for _ in range(100)]
            m = sum(v) / len(v)
            print(f"  AIN{ch}: media {m*1000:+10.4f} mV   pico-pico {(max(v)-min(v))*1e6:8.1f} uV")
    finally:
        adc.cerrar()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=100)
    ap.add_argument("--salida", default="lecturas_fz.csv")
    ap.add_argument("--diagnostico", action="store_true")
    a = ap.parse_args()
    if a.diagnostico:
        diagnostico()
        raise SystemExit

    adc = ADS1256()
    filas = []
    t0 = time.perf_counter()
    try:
        for i in range(a.n):
            v = adc.leer_volts()
            filas.append([i, round(time.perf_counter() - t0, 6), round(v, 6), round(volts_a_newtons(v), 3)])
    finally:
        adc.cerrar()

    with open(a.salida, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["intento", "t_s", "volts", "newtons"])
        w.writerows(filas)
    n = [r[3] for r in filas]
    dt = filas[-1][1] - filas[0][1]
    print(f"{len(filas)} lecturas en {dt:.2f} s -> {(len(filas)-1)/dt:.0f} muestras/s (esperado ~1000)")
    print(f"Fz: min {min(n):.2f}  media {sum(n)/len(n):.2f}  max {max(n):.2f} N")
    print(f"CSV: {a.salida}")
    print("Con 0 N reales, Fz debe estar cerca de 0 (si no, hay offset de cero pendiente de tarar).")
