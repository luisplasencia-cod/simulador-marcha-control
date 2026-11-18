"""Preflight de la ETAPA 2 (RPi) del ADC con ESP32 de lectura + UART. SOLO LEE: no mueve ejes, no abre /dev/ttyUSB*
(abrirlo reinicia el ESP32 de motores), no manda nada por el UART. Escucha /dev/ttyAMA0 unos segundos.
Escrito 2026-11-18 para acortar la Etapa 2 (R0-R2 de INICIO_RPI.md). Sin ESP32 de lectura conectado solo puede decir
'sin datos': eso NO distingue cable suelto, ESP32 sin flashear, ESP32 sin energia o UART mal habilitado.
Uso: python3 pruebas/etapa2_preflight.py [--puerto /dev/ttyAMA0] [--escuchar 3]"""
import argparse, os, re, subprocess, sys, statistics as st, time

R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

res = []   # (estado, item, detalle)


def ok(i, d=""): res.append(("OK", i, d))
def mal(i, d=""): res.append(("MAL", i, d))
def aviso(i, d=""): res.append(("AVISO", i, d))


def sh(cmd):
    try:
        return subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10).stdout.strip()
    except Exception as ex:
        return f"<error {ex!r}>"


ap = argparse.ArgumentParser()
ap.add_argument("--puerto", default="/dev/ttyAMA0")
ap.add_argument("--escuchar", type=float, default=3.0, help="segundos de escucha del UART")
a = ap.parse_args()

# R0: modelo y configuracion del UART
modelo = sh("tr -d '\\0' < /proc/device-tree/model")
(ok if "Pi 5" in modelo else aviso)("modelo", modelo + ("" if "Pi 5" in modelo else " (el plan esta escrito para Pi 5: revisar R0)"))
cfg = sh("cat /boot/firmware/config.txt")
(ok if re.search(r"^\s*dtoverlay=uart0-pi5", cfg, re.M) else mal)("config.txt: dtoverlay=uart0-pi5", "habilita el UART0 en GPIO14/15")
cmd = sh("cat /boot/firmware/cmdline.txt")
(mal if re.search(r"console=(serial0|ttyAMA)", cmd) else ok)("cmdline.txt sin consola serie", cmd if "console=" in cmd else "sin console=serial")
if os.path.exists(a.puerto):
    ok("existe " + a.puerto)
else:
    mal("existe " + a.puerto, "overlay no cargado: falta reiniciar tras editar config.txt")
alias = os.path.realpath("/dev/serial0")
if os.path.basename(alias) != os.path.basename(a.puerto):
    aviso("/dev/serial0 -> " + alias, f"NO es el UART del header en Pi 5: usar {a.puerto} (no serial0)")
pc = sh("pinctrl get 14,15 2>&1")
if "ERROR" in pc or "not found" in pc or not pc:
    aviso("funcion de GPIO14/15", "pinctrl no disponible")
else:
    (ok if "TXD0" in pc and "RXD0" in pc else mal)("GPIO14/15 = TXD0/RXD0", pc.replace("\n", " | "))
dueños = sh(f"fuser {a.puerto} 2>&1")
(mal if dueños else ok)("nadie mas usa " + a.puerto, dueños or "libre")

# USB: identificar sin abrir
usb = sh("ls -l /dev/serial/by-id/ 2>/dev/null | tail -n +2")
if usb:
    ok("puertos USB-serie (SIN abrir)", usb.replace("\n", " | "))
else:
    aviso("puertos USB-serie", "ninguno visible (ESP32 de motores desconectado o USB caido)")
thr = sh("vcgencmd get_throttled")
(ok if thr.endswith("0x0") else aviso)("alimentacion del RPi", thr)
ok("hora / uptime", sh("date '+%F %T'") + " | " + sh("uptime -p"))

# R1/R2 en seco: escuchar el UART
n_pkt = 0
if os.path.exists(a.puerto) and not dueños:
    try:
        import serial
        from leer_ads1256_fz_esp32_uart import extraer_paquetes, BAUD
        ser = serial.Serial(a.puerto, BAUD, timeout=0.1)
        ser.reset_input_buffer()
        buf, val, corr, t0 = b"", [], 0, time.monotonic()
        while time.monotonic() - t0 < a.escuchar:
            ch = ser.read(512)
            if ch:
                v, buf, c = extraer_paquetes(buf + ch)
                val += v
                corr += c if isinstance(c, int) else len(c)
        ser.close()
        n_pkt = len(val)
        if n_pkt == 0:
            mal("el ESP32 de lectura transmite", f"0 paquetes en {a.escuchar:.0f} s: ver F17 de INICIO_RPI.md "
                "(TX GPIO17 del ESP32 -> pin 10, GND comun al pin 6, ESP32 con energia y firmware cargado)")
        else:
            tasa = n_pkt / a.escuchar
            med, sd = st.median(val), (st.pstdev(val) if len(val) > 1 else 0.0)
            (ok if 800 <= tasa <= 1100 else aviso)("tasa de paquetes", f"{tasa:.0f}/s (esperado ~1000)")
            (ok if corr == 0 else aviso)("paquetes corruptos", str(corr))
            ok("Fz en reposo", f"mediana {med:+.2f} N, sigma {sd:.2f} N (referencia: L3 en la laptop, NO comparable hasta tener L3)")
            if sd == 0.0:
                aviso("Fz congelada", "todas las lecturas iguales: ADC sin convertir")
            if sum(1 for x in val if x == 0.0) >= 0.5 * n_pkt:
                mal("Fz = 0.000 exacto", "SPI devolviendo ceros (MISO/CS suelto en el ESP32 de lectura)")
    except Exception as ex:
        mal("escucha UART", repr(ex))

print("=" * 72)
for est, i, d in res:
    print(f"[{est:5s}] {i}" + (f"\n         {d}" if d else ""))
print("=" * 72)
m = sum(1 for r in res if r[0] == "MAL")
print("RESULTADO:", "LISTO para R2" if m == 0 and n_pkt > 0 else f"{m} item(s) MAL: corregir antes de R2")
sys.exit(1 if m else 0)
