"""Ensayo A: rigidez de contacto k(F) del eje vertical (Y) contra la protesis/plataforma AMTI.

BAJA el eje Y en incrementos pequenos (signo NEGATIVO = bajar; + = subir, Ensayo 0), mide Fz
(mediana de ~50 muestras del ADS1256 tras asentar) en cada escalon, detecta el contacto y
sigue hasta fmax_n; luego SUBE de vuelta lo bajado. Registra pasos vs Fz y ajusta k.
Requiere: monitor cerrado, simulador despejado, OK de Luis. Sin --ejecutar solo simula el plan.

Protecciones: parada si F > fmax_n, si un solo escalon sube F > salto_max_n, si no hay
contacto tras max_descenso_mm, si el ack no es OK, ante cualquier excepcion/Ctrl+C (siempre
intenta subir lo bajado). pasos/mm = 80 (Ensayo 0).
"""
import argparse, csv, statistics as st, sys, time
from pathlib import Path
import serial
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "pruebas"))
from leer_ads1256_fz import ADS1256, volts_a_newtons

PASOS_MM = 80
ap = argparse.ArgumentParser()
ap.add_argument("--puerto", default="/dev/ttyUSB0")
ap.add_argument("--paso_pasos", type=int, default=16, help="16 pasos = 0.2 mm por escalon")
ap.add_argument("--umbral_contacto_n", type=float, default=8.0)
ap.add_argument("--fmax_n", type=float, default=150.0)
ap.add_argument("--salto_max_n", type=float, default=60.0)
ap.add_argument("--hueco_mm", type=float, required=True, help="hueco medido suela-plataforma (23 cm = 230)")
ap.add_argument("--angulo_deg", type=float, required=True, help="angulo sagital FIJO del pie durante el ensayo (la rigidez depende de el)")
ap.add_argument("--aprox_margen_mm", type=float, default=30.0, help="la aproximacion rapida se detiene a hueco-margen")
ap.add_argument("--max_extra_mm", type=float, default=20.0, help="descenso maximo total = hueco + extra")
ap.add_argument("--asentar_s", type=float, default=0.5)
ap.add_argument("--salida", default="control/identificacion/resultados/ensayo_A_rigidez.csv")
ap.add_argument("--ejecutar", action="store_true")
a = ap.parse_args()
if not a.ejecutar:
    print(f"PLAN (no ejecuta): angulo {a.angulo_deg} deg; aproximacion rapida en tramos de 50 mm hasta {a.hueco_mm-a.aprox_margen_mm:.0f} mm "
          f"(abortando si F>{a.umbral_contacto_n} N); luego escalones de {a.paso_pasos/PASOS_MM:.2f} mm, contacto a +{a.umbral_contacto_n} N, "
          f"tope {a.fmax_n} N, descenso maximo total {a.hueco_mm+a.max_extra_mm:.0f} mm. Agregar --ejecutar."); sys.exit(0)

def fz(adc, n=50):
    return st.median(volts_a_newtons(adc.leer_volts()) for _ in range(n))

ser = serial.Serial(a.puerto, 115200, timeout=2.0); time.sleep(2.0); ser.reset_input_buffer()
def mover(p):
    ser.reset_input_buffer(); ser.write(f"<MANUAL:1:{p}>".encode())
    r = ser.readline().decode(errors="replace").strip()
    if not r.startswith("OK"): raise RuntimeError(f"ack inesperado: {r!r}")
    time.sleep(abs(p) / 1600 + a.asentar_s)

adc = ADS1256(); bajados = 0; filas = []; motivo = "?"
try:
    f0 = fz(adc, 200); print(f"Fz base (sin contacto) = {f0:.2f} N; angulo {a.angulo_deg} deg; hueco {a.hueco_mm} mm")
    hueco_pasos = int((a.hueco_mm - a.aprox_margen_mm) * PASOS_MM); tocado = False
    while bajados + 4000 <= hueco_pasos:  # aproximacion rapida: tramos de 50 mm, vigilando Fz
        mover(-4000); bajados += 4000
        f = fz(adc, 20) - f0
        print(f"[aprox] bajado {bajados/PASOS_MM:6.1f} mm  F = {f:6.2f} N", flush=True)
        if f > a.umbral_contacto_n: motivo = "contacto ANTES de lo esperado en aproximacion"; tocado = True; break
    if tocado: raise RuntimeError(motivo)
    while True:
        if bajados / PASOS_MM >= a.hueco_mm + a.max_extra_mm: motivo = "sin contacto en descenso maximo"; break
        mover(-a.paso_pasos); bajados += a.paso_pasos
        f = fz(adc) - f0; filas.append([bajados, round(bajados / PASOS_MM, 3), round(f, 2)])
        print(f"bajado {bajados/PASOS_MM:6.2f} mm  F = {f:7.2f} N", flush=True)
        if f > a.fmax_n: motivo = "fmax alcanzada (OK)"; break
        if len(filas) > 1 and f - filas[-2][2] > a.salto_max_n: motivo = "salto de fuerza excesivo"; break
        if f < -30: motivo = "fuerza negativa anomala"; break
except BaseException as e:
    motivo = f"excepcion: {e!r}"
finally:
    print("Motivo de parada:", motivo, "-> subiendo", bajados / PASOS_MM, "mm")
    rest = bajados
    while rest > 0:
        d = min(rest, 800)
        try: mover(d); rest -= d
        except Exception as e: print("ERROR al subir:", e); break
    print("pasos pendientes de subir:", rest)
    adc.cerrar(); ser.close()

Path(a.salida).parent.mkdir(parents=True, exist_ok=True)
with open(a.salida, "w", newline="") as f:
    f.write(f"# angulo_sagital_deg={a.angulo_deg} hueco_mm={a.hueco_mm} fmax_n={a.fmax_n} paso_pasos={a.paso_pasos} motivo={motivo}\n")
    w = csv.writer(f); w.writerow(["pasos_bajados", "mm", "F_N"]); w.writerows(filas)
cont = [r for r in filas if r[2] >= a.umbral_contacto_n]
if len(cont) >= 3:
    xs = [r[1] for r in cont]; ys = [r[2] for r in cont]; mx = st.mean(xs); my = st.mean(ys)
    k = sum((x-mx)*(y-my) for x, y in zip(xs, ys)) / sum((x-mx)**2 for x in xs)
    print(f"k (ajuste lineal sobre {len(cont)} puntos con F>={a.umbral_contacto_n} N) = {k:.2f} N/mm")
else:
    print("puntos insuficientes para ajustar k")
