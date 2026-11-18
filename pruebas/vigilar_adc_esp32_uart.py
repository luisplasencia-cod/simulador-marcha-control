"""Vigila la ruta ESP32->UART2 del ADS1256 (en reposo, sin ESP32 de motores ni servo).
NO PROBADO EN HARDWARE (escrito sin RPi ni ESP32 disponibles, 2026-11-17; revisado 2026-11-18).
Sirve igual en la laptop (adaptador USB-TTL en GPIO17, --puerto COMx) y en el RPi.

Clasifica cada segundo (antes solo contaba el silencio del puerto, y un ADC que devuelve ceros
o un valor congelado pasaba como "OK"):
  CAIDO      sin datos por UART > --timeout s (DRDY no baja, ESP32 colgado o cable UART suelto)
  CEROS      >= 50 % de lecturas exactamente 0.000 (SPI devuelve ceros: MISO/CS suelto)
  SATURADO   alguna lectura en +-2830 N (= +-5 V de entrada: AIN abierto o fuera de rango)
  CONGELADO  todas las lecturas del segundo identicas (el chip no convierte)
  PICOS      lecturas a > --umbral_pico N de la mediana (errores de bit del SPI, como el 2026-11-05)
  OK         nada de lo anterior
Ver el resumen por USB del propio ESP32 (main.cpp) para saber si el fallo es del ADC o del UART.

Uso: python vigilar_adc_esp32_uart.py --puerto /dev/ttyUSB1 --minutos 30
"""
import sys, os, time, argparse, statistics as st
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(R, "herramientas"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import serial
from leer_ads1256_fz_esp32_uart import extraer_paquetes

SATURACION_N = 5000.0 / 1.7665  # +-5 V de entrada (VREF 2.5 V, PGA 1) = 2830.5 N

ap = argparse.ArgumentParser()
ap.add_argument("--puerto", required=True, help="confirmar cual de los dos ESP32 es ANTES de correr")
ap.add_argument("--minutos", type=float, default=30.0)
ap.add_argument("--timeout", type=float, default=2.0, help="segundos de silencio del puerto para contarlo como caida")
ap.add_argument("--umbral_pico", type=float, default=50.0, help="N de distancia a la mediana para contar un pico")
a = ap.parse_args()

try:  # visor de pantalla del RPi; en la laptop puede no existir la carpeta logs/
    from en_vivo import EnVivo
    os.makedirs(os.path.join(R, "logs"), exist_ok=True)
    ev = EnVivo("Vigilante del ADC via ESP32+UART2 (en reposo)", ruta=os.path.join(R, "logs", "prueba_en_vivo.csv"))
except Exception:
    ev = None

os.makedirs(os.path.join(R, "pruebas", "resultados"), exist_ok=True)
ruta_csv = os.path.join(R, "pruebas", "resultados", time.strftime("vigilar_adc_esp32_uart_%Y%m%d_%H%M%S.csv"))
sal = open(ruta_csv, "w", buffering=1)
sal.write("hora,estado,muestras_s,fz_mediana_n,fz_sd_n,ceros,saturadas,picos,corruptos,nota\n")

ser = serial.Serial(a.puerto, 115200, timeout=0.1)
time.sleep(2.5)
ser.reset_input_buffer()

buf = b""
cuenta = {k: 0 for k in ("CAIDO", "CEROS", "SATURADO", "CONGELADO", "PICOS", "OK")}
fin = time.monotonic() + a.minutos * 60
t_ultimo_dato = time.monotonic()
caido = False


def registrar(estado, n=0, med=0.0, sd=0.0, ceros=0, sat=0, picos=0, corr=0, nota=""):
    hora = time.strftime("%H:%M:%S")
    sal.write(f"{hora},{estado},{n},{med:.2f},{sd:.2f},{ceros},{sat},{picos},{corr},{nota}\n")
    if estado != "OK":
        print(hora, estado, nota or f"n={n} med={med:+.2f} N ceros={ceros} sat={sat} picos={picos}", flush=True)
    if ev:
        ev.escribir(estado, med, 0, f"{n} muestras/s Fz_med={med:+.1f} N {nota}")


while time.monotonic() < fin:
    t0 = time.monotonic()
    valores, corruptos = [], 0
    while time.monotonic() - t0 < 1.0:
        chunk = ser.read(256)
        if chunk:
            buf += chunk
            t_ultimo_dato = time.monotonic()
            if caido:
                caido = False
                registrar("RECUPERADO", nota="volvieron datos por UART")
            v, buf, c = extraer_paquetes(buf)
            valores += v
            corruptos += c
        elif not caido and time.monotonic() - t_ultimo_dato > a.timeout:
            caido = True
            cuenta["CAIDO"] += 1
            registrar("CAIDO", nota=f"sin datos por UART hace {a.timeout:g} s (caida #{cuenta['CAIDO']})")
    if not valores:
        continue
    med = st.median(valores)
    sd = st.pstdev(valores)
    ceros = sum(1 for x in valores if x == 0.0)
    sat = sum(1 for x in valores if abs(x) >= SATURACION_N - 1.0)
    picos = sum(1 for x in valores if abs(x - med) > a.umbral_pico)
    if ceros >= len(valores) / 2:
        estado = "CEROS"
    elif sat:
        estado = "SATURADO"
    elif len(valores) > 10 and max(valores) == min(valores):
        estado = "CONGELADO"
    elif picos:
        estado = "PICOS"
    else:
        estado = "OK"
    cuenta[estado] += 1
    registrar(estado, len(valores), med, sd, ceros, sat, picos, corruptos)

if ev:
    ev.cerrar("fin del vigilante")
ser.close()
print(f"fin ({a.minutos:g} min): " + ", ".join(f"{k}={v}" for k, v in cuenta.items()))
print(f"CSV: {ruta_csv}")
