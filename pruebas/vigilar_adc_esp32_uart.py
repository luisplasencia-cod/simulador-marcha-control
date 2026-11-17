"""Vigila la ruta ESP32->UART2->RPi del ADS1256 (en reposo, sin ESP32 de motores ni servo).
NO PROBADO EN HARDWARE (escrito sin RPi ni ESP32 disponibles, 2026-11-17). Version UART del
`vigilar_adc.py` original (que lee el ADS1256 directo por SPI); aqui no hay SPI que vigilar,
asi que "caido" se define como: silencio del puerto serie por mas de --timeout segundos.

Objetivo de esta prueba (paso 6 del esquema, CLAUDE.md 2026-11-17): ver si cambiar el host del
ADS1256 de RPi a ESP32 realmente reduce las caidas, o si siguen pasando igual (lo que
confirmaria que la causa es analogica/de alimentacion, no de a quien lee el SPI).

Uso: python vigilar_adc_esp32_uart.py --puerto /dev/ttyUSB1 --minutos 20
"""
import sys, os, time, subprocess, argparse, statistics as st
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(R, "herramientas"))
import serial
from en_vivo import EnVivo

ap = argparse.ArgumentParser()
ap.add_argument("--puerto", required=True, help="confirmar cual de los dos ESP32 es ANTES de correr")
ap.add_argument("--minutos", type=float, default=20.0)
ap.add_argument("--timeout", type=float, default=2.0, help="segundos de silencio del puerto para contarlo como caida")
a = ap.parse_args()

ev = EnVivo("Vigilante del ADC via ESP32+UART2 (en reposo)")
sal = open(os.path.join(R, "pruebas/resultados", time.strftime("vigilar_adc_esp32_uart_%Y%m%d_%H%M%S.csv")), "w", buffering=1)
sal.write("hora,estado,muestras_s,fz_n_mediana,nota\n")

ser = serial.Serial(a.puerto, 115200, timeout=0.1)
time.sleep(2.5)
ser.reset_input_buffer()

buf = b""
caidas = 0
fin = time.monotonic() + a.minutos * 60
t_ultimo_dato = time.monotonic()
caido = False

while time.monotonic() < fin:
    t0 = time.monotonic()
    valores = []
    while time.monotonic() - t0 < 1.0:
        chunk = ser.read(256)
        if chunk:
            buf += chunk
            t_ultimo_dato = time.monotonic()
            if caido:
                caido = False
                ev.escribir("OK", 0, 0, "ADC RECUPERADO (volvieron datos por UART)")
                sal.write(f"{time.strftime('%H:%M:%S')},RECUPERADO,,,volvieron datos\n")
            while b"<" in buf and b">" in buf:
                i = buf.index(b"<"); j = buf.index(b">", i)
                crudo = buf[i + 1:j]; buf = buf[j + 1:]
                try:
                    valores.append(float(crudo.decode("ascii")))
                except (ValueError, UnicodeDecodeError):
                    continue
        elif not caido and time.monotonic() - t_ultimo_dato > a.timeout:
            caido = True
            caidas += 1
            msg = f"sin datos por UART hace {a.timeout:g} s (caida #{caidas})"
            print(time.strftime("%H:%M:%S"), "CAIDO", msg, flush=True)
            ev.escribir("CAIDO", 0, 0, "ABORT? " + msg)
            sal.write(f"{time.strftime('%H:%M:%S')},CAIDO,,,{msg}\n")
    if valores:
        m = st.median(valores)
        ev.escribir("OK", m, 0, f"{len(valores)} muestras/s  Fz_med={m:+.1f} N  caidas={caidas}")
        sal.write(f"{time.strftime('%H:%M:%S')},OK,{len(valores)},{m:.2f},\n")

ev.cerrar("fin del vigilante")
ser.close()
print(f"fin: {caidas} caidas en {a.minutos:g} min")
