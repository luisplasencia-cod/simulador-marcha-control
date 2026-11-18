"""Lee Fz del ESP32 nuevo (lectura del ADS1256 por SPI, diferencial AIN1/AIN0) por UART2.
NO PROBADO EN HARDWARE (escrito sin RPi ni ESP32 disponibles, 2026-11-17).

Protocolo del firmware (control/firmware/lectura_ads1256_esp32_diferencial/src/main.cpp):
  un paquete de texto "<valor>" por cada lectura del ADC (hasta 1000/s), SIN numero de
  secuencia ni checksum. Este lector resincroniza por los delimitadores '<'/'>' y descarta
  cualquier paquete cortado o con texto corrupto en vez de asumir que siempre llega entero.

Puerto: NO hay un valor por defecto correcto todavia -- hay DOS ESP32 en el sistema (el de
motores y este nuevo de lectura). Identificar cual es cual con `dmesg` o `ls /dev/ttyUSB*`
ANTES de correr esto (ideas: desconectar uno a la vez y ver que puerto desaparece), y pasarlo
con --puerto. Nunca asumir /dev/ttyUSB0.

Uso:
    python leer_ads1256_fz_esp32_uart.py --puerto /dev/ttyUSB1 --n 1000 --salida lecturas_fz_esp32.csv
    (en la laptop, con adaptador USB-TTL en GPIO17: --puerto COMx)
"""
import argparse
import csv
import time

import serial

BAUD = 115200


def extraer_paquetes(buf):
    """Saca todos los "<valor>" completos de buf. Devuelve (valores, resto, n_corruptos).
    Corrige un bug de la version anterior: con buf = b'3.2><4.1' (se empieza a leer a mitad de un
    paquete, lo normal al abrir el puerto) buscaba '>' DESPUES de '<', no lo hallaba y el lector
    se caia con ValueError."""
    valores, corruptos = [], 0
    while True:
        i = buf.find(b"<")
        if i < 0:
            return valores, b"", corruptos
        j = buf.find(b">", i + 1)
        if j < 0:
            return valores, buf[i:], corruptos   # paquete incompleto: esperar el resto
        crudo = buf[i + 1:j]
        buf = buf[j + 1:]
        if b"<" in crudo:                        # '<' perdido dentro: quedarse con el ultimo
            crudo = crudo[crudo.rfind(b"<") + 1:]
            corruptos += 1
        try:
            valores.append(float(crudo.decode("ascii")))
        except (ValueError, UnicodeDecodeError):
            corruptos += 1


def leer_paquetes(ser, n, timeout_s=5.0):
    """Generador de floats; descarta paquetes corruptos en vez de detenerse."""
    buf = b""
    t_ultimo = time.monotonic()
    leidos = 0
    while leidos < n:
        chunk = ser.read(256)
        if chunk:
            buf += chunk
            t_ultimo = time.monotonic()
        elif time.monotonic() - t_ultimo > timeout_s:
            raise TimeoutError(f"Sin datos del ESP32 en {timeout_s} s — revisar cableado UART2/GND o si el ESP32 se colgo")

        valores, buf, _ = extraer_paquetes(buf)
        for valor in valores:
            leidos += 1
            yield valor
            if leidos >= n:
                return


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--puerto", required=True, help="p.ej. /dev/ttyUSB1 — confirmar cual ANTES de correr (hay 2 ESP32)")
    ap.add_argument("--n", type=int, default=1000)
    ap.add_argument("--salida", default="lecturas_fz_esp32.csv")
    a = ap.parse_args()

    ser = serial.Serial(a.puerto, BAUD, timeout=0.1)
    # Por el UART2 (pines del RPi o adaptador USB-TTL) el ESP32 NO se reinicia al abrir el puerto;
    # la espera solo sirve si por error se abre el USB propio del ESP32 (ahi si se reinicia).
    time.sleep(2.5)
    ser.reset_input_buffer()

    filas = []
    t0 = time.perf_counter()
    try:
        for i, fz in enumerate(leer_paquetes(ser, a.n)):
            filas.append([i, round(time.perf_counter() - t0, 6), round(fz, 3)])
    finally:
        ser.close()

    with open(a.salida, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["intento", "t_s", "fz_n"])
        w.writerows(filas)

    if not filas:
        print("0 lecturas validas — nada que reportar (revisar puerto/cableado)")
        return
    n_valores = [r[2] for r in filas]
    dt = filas[-1][1] - filas[0][1] if len(filas) > 1 else 0
    print(f"{len(filas)} lecturas en {dt:.2f} s -> {(len(filas) - 1) / dt:.0f} muestras/s (esperado ~1000, si no se perdieron paquetes)" if dt else f"{len(filas)} lecturas")
    print(f"Fz: min {min(n_valores):.2f}  media {sum(n_valores)/len(n_valores):.2f}  max {max(n_valores):.2f} N")
    print(f"CSV: {a.salida}")
    print("Pendiente (ver CLAUDE.md 2026-11-17): validar esto contra el AMTI real antes de usarlo para el lazo de Fz.")


if __name__ == "__main__":
    main()
