"""Latencia del lazo de punta a punta, UN solo reloj (perf_counter_ns):
escalon electrico GPIO27 -> AIN1 (ADS1256) -> deteccion en RPi (50 % del escalon)
-> comando MANUAL al ESP32 -> ack "OK" de vuelta.

Tramos: t_adq = flanco->deteccion | t_cmd = deteccion->ack OK | t_total = flanco->ack.
NO incluye: retardo del amplificador AMTI (supuesto, ver CLAUDE.md) ni el instante en que el motor
EMPIEZA a girar tras el ack (sin sensor para medirlo; el ack se envia al aceptar el comando).
Mueve el eje indicado (default 2 = sagital K) +/-pasos alternando. Cerrar antes el monitor.
"""
import argparse, csv, random, statistics as st, sys, time
from pathlib import Path
import RPi.GPIO as GPIO
import serial
sys.path.insert(0, str(Path(__file__).resolve().parent))
from leer_ads1256_fz import ADS1256
from medir_latencia_gpio_adc import leer_ahora, nivel_estable, PIN_ESCALON, MUX_AIN1_AINCOM

ap = argparse.ArgumentParser()
ap.add_argument("--n", type=int, default=30)
ap.add_argument("--eje", type=int, default=2)
ap.add_argument("--pasos", type=int, default=40)
ap.add_argument("--puerto", default="/dev/ttyUSB0")
ap.add_argument("--salida", default="pruebas/resultados/latencia_lazo_total.csv")
a = ap.parse_args()

ser = serial.Serial(a.puerto, 115200, timeout=1.0)
time.sleep(2.0)
ser.reset_input_buffer()
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_ESCALON, GPIO.OUT, initial=GPIO.LOW)
adc = ADS1256(mux=MUX_AIN1_AINCOM)
filas = []
try:
    time.sleep(0.2); v_lo = nivel_estable(adc)
    GPIO.output(PIN_ESCALON, GPIO.HIGH); time.sleep(0.2); v_hi = nivel_estable(adc)
    GPIO.output(PIN_ESCALON, GPIO.LOW); time.sleep(0.2)
    print(f"bajo={v_lo*1000:.1f} mV alto={v_hi*1000:.1f} mV")
    if v_hi - v_lo < 0.5:
        sys.exit("GPIO27 no llega a AIN1 (divisor desconectado?). Abortado, no se movio nada.")
    umb = v_lo + 0.5 * (v_hi - v_lo)
    for i in range(a.n):
        time.sleep(random.uniform(0.020, 0.070))
        GPIO.output(PIN_ESCALON, GPIO.LOW); time.sleep(0.1)  # asegurar bajo
        while True:  # drenar lecturas hasta estar en bajo
            if leer_ahora(adc)[0] < umb: break
        ser.reset_input_buffer()
        signo = 1 if i % 2 == 0 else -1
        t0 = time.perf_counter_ns()
        GPIO.output(PIN_ESCALON, GPIO.HIGH)
        td = None
        while td is None:
            v, t = leer_ahora(adc)
            if v > umb: td = t
            elif t - t0 > 100e6: break
        if td is None:
            filas.append([i, "", "", "", "sin_deteccion"]); continue
        ser.write(f"<MANUAL:{a.eje}:{signo * a.pasos}>".encode())
        r = ser.readline(); ta = time.perf_counter_ns()
        resp = r.decode(errors="replace").strip()
        filas.append([i, round((td - t0) / 1e6, 3), round((ta - td) / 1e6, 3), round((ta - t0) / 1e6, 3), resp])
        time.sleep(1.0)  # que termine el movimiento (si no -> BUSY)
finally:
    GPIO.output(PIN_ESCALON, GPIO.LOW); adc.cerrar(); ser.close()

Path(a.salida).parent.mkdir(parents=True, exist_ok=True)
with open(a.salida, "w", newline="") as f:
    w = csv.writer(f); w.writerow(["evento", "adq_ms", "cmd_ms", "total_ms", "respuesta"]); w.writerows(filas)
ok = [r for r in filas if str(r[4]).startswith("OK")]
print(f"validos con OK: {len(ok)}/{len(filas)}; otras respuestas: {sorted({r[4] for r in filas if not str(r[4]).startswith('OK')})}")
for col, nom in ((1, "adq (flanco->deteccion)"), (2, "cmd (deteccion->ack)"), (3, "TOTAL (flanco->ack)")):
    x = [r[col] for r in ok]
    if x:
        xs = sorted(x)
        print(f"{nom:<26} media={st.mean(x):.3f} sigma={st.pstdev(x):.3f} min={xs[0]:.3f} p95={xs[int(.95*(len(xs)-1))]:.3f} max={xs[-1]:.3f} ms")
print("CSV:", a.salida)
