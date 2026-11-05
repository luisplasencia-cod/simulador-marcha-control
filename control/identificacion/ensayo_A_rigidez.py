"""Ensayo A: rigidez de contacto k(F) del eje vertical (Y) contra la protesis/plataforma AMTI.

BAJA el eje Y (MANUAL signo NEGATIVO = bajar; + = subir, Ensayo 0): aproximacion rapida vigilando
Fz, luego escalones finos hasta fmax_n, y SUBE registrando tambien la subida (histeresis).
Guarda TODO el recorrido (t, fase, mm, F) en un CSV por corrida (nombre con angulo+hora) y en vivo
en logs/ensayo_A_en_vivo.csv para el visor (visor_ensayo_A.py, proceso aparte: no usa SPI ni serial).
Requiere: monitor cerrado (SPI), simulador despejado, hueco remedido, OK de Luis. NUNCA manda HOME.
Protecciones: parada si F > fmax_n, salto > salto_max_n por escalon, sin contacto en hueco+extra, ack != OK,
excepcion/Ctrl+C (siempre intenta subir). pasos/mm = 80 (Ensayo 0). Mediana de 50 muestras por escalon.
"""
import argparse, csv, statistics as st, sys, time
from datetime import datetime
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "pruebas"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ajuste_k import k_por_bandas

PASOS_MM = 80
ap = argparse.ArgumentParser()
ap.add_argument("--puerto", default="/dev/ttyUSB0")
ap.add_argument("--paso_pasos", type=int, default=16, help="16 pasos = 0.2 mm por escalon")
ap.add_argument("--umbral_contacto_n", type=float, default=8.0)
ap.add_argument("--fmax_n", type=float, default=150.0)
ap.add_argument("--salto_max_n", type=float, default=60.0)
ap.add_argument("--hueco_mm", type=float, required=True, help="hueco medido suela-plataforma")
ap.add_argument("--angulo_deg", type=float, required=True, help="angulo sagital FIJO del pie (k depende de el)")
ap.add_argument("--etiqueta", default="", help="ej. talon / planta / dedos")
ap.add_argument("--aprox_margen_mm", type=float, default=30.0)
ap.add_argument("--max_extra_mm", type=float, default=20.0)
ap.add_argument("--asentar_s", type=float, default=0.5)
ap.add_argument("--salida", default=None)
ap.add_argument("--en_vivo", default="logs/ensayo_A_en_vivo.csv")
ap.add_argument("--ejecutar", action="store_true")
ap.add_argument("--hueco_remedido", action="store_true", help="OBLIGATORIO con --ejecutar: hueco medido de nuevo ANTES de ESTA corrida")
a = ap.parse_args()
if not a.ejecutar:
    print(f"PLAN (no ejecuta): angulo {a.angulo_deg} deg {a.etiqueta}; aproximacion rapida en tramos de 50 mm hasta {a.hueco_mm-a.aprox_margen_mm:.0f} mm "
          f"(aborta si F>{a.umbral_contacto_n} N); luego escalones de {a.paso_pasos/PASOS_MM:.2f} mm, tope {a.fmax_n} N, "
          f"descenso maximo {a.hueco_mm+a.max_extra_mm:.0f} mm; sube registrando la histeresis. Agregar --ejecutar --hueco_remedido."); sys.exit(0)
if not a.hueco_remedido:
    sys.exit("Abortado: falta --hueco_remedido (el hueco se mide de nuevo antes de CADA corrida, regla de Luis).")

import serial
from leer_ads1256_fz import ADS1256, volts_a_newtons
sello = datetime.now().strftime("%Y%m%d_%H%M%S")
salida = a.salida or f"control/identificacion/resultados/ensayo_A_ang{a.angulo_deg:g}_{a.etiqueta or 'sin_etiqueta'}_{sello}.csv"
Path(salida).parent.mkdir(parents=True, exist_ok=True); Path(a.en_vivo).parent.mkdir(parents=True, exist_ok=True)
cab = f"# angulo_sagital_deg={a.angulo_deg} etiqueta={a.etiqueta} hueco_mm={a.hueco_mm} fmax_n={a.fmax_n} paso_pasos={a.paso_pasos} inicio={sello}\n"
vivo = open(a.en_vivo, "w", buffering=1); vivo.write(cab); vivo.write("t_s,fase,mm,F_N\n")
filas = []; T0 = time.monotonic()
def reg(fase, mm, F, guardar=True):
    t = round(time.monotonic() - T0, 3); vivo.write(f"{t},{fase},{mm:.3f},{F:.2f}\n")
    if guardar: filas.append([t, fase, round(mm, 3), round(F, 2)])

def fz(adc, n=50):
    return st.median(volts_a_newtons(adc.leer_volts()) for _ in range(n))

ser = serial.Serial(a.puerto, 115200, timeout=2.0); time.sleep(2.0); ser.reset_input_buffer()
adc = ADS1256(); f0 = 0.0; bajados = 0; motivo = "?"
def mover(p, fase):
    """Manda MANUAL y mientras se mueve registra Fz continua (~50 Hz) para el visor en vivo."""
    global bajados
    ser.reset_input_buffer(); ser.write(f"<MANUAL:1:{p}>".encode())
    r = ser.readline().decode(errors="replace").strip()
    if not r.startswith("OK"): raise RuntimeError(f"ack inesperado: {r!r}")
    bajados -= p  # p negativo = baja
    fin = time.monotonic() + abs(p) / 1600 + a.asentar_s
    while time.monotonic() < fin:
        reg(fase + "_mov", bajados / PASOS_MM, fz(adc, 10) - f0, guardar=False)

try:
    f0 = fz(adc, 200); print(f"Fz base = {f0:.2f} N; angulo {a.angulo_deg} deg; hueco {a.hueco_mm} mm; archivo: {salida}")
    reg("base", 0.0, 0.0)
    hueco_pasos = int((a.hueco_mm - a.aprox_margen_mm) * PASOS_MM)
    while bajados + 4000 <= hueco_pasos:
        mover(-4000, "aprox"); f = fz(adc, 20) - f0; reg("aprox", bajados / PASOS_MM, f)
        print(f"[aprox] {bajados/PASOS_MM:6.1f} mm  F = {f:6.2f} N", flush=True)
        if f > a.umbral_contacto_n: raise RuntimeError("contacto ANTES de lo esperado en la aproximacion")
    previa = None
    while True:
        if bajados / PASOS_MM >= a.hueco_mm + a.max_extra_mm: motivo = "sin contacto en descenso maximo"; break
        mover(-a.paso_pasos, "fino"); f = fz(adc) - f0; reg("fino", bajados / PASOS_MM, f)
        print(f"bajado {bajados/PASOS_MM:6.2f} mm  F = {f:7.2f} N", flush=True)
        if f > a.fmax_n: motivo = "fmax alcanzada (OK)"; break
        if previa is not None and f - previa > a.salto_max_n: motivo = "salto de fuerza excesivo"; break
        if f < -30: motivo = "fuerza negativa anomala"; break
        previa = f
except BaseException as e:
    motivo = f"excepcion: {e!r}"
finally:
    print("Motivo de parada:", motivo, "-> subiendo", bajados / PASOS_MM, "mm")
    try:
        f = fz(adc, 20) - f0
        while bajados > 0 and f > a.umbral_contacto_n / 2:   # subida fina mientras haya contacto (histeresis)
            mover(a.paso_pasos, "sube"); f = fz(adc, 20) - f0; reg("sube", bajados / PASOS_MM, f)
        while bajados > 0:
            mover(min(bajados, 800), "sube2")
    except BaseException as e:
        print("ERROR al subir:", repr(e))
    print("pasos pendientes de subir:", bajados)
    vivo.write(f"# fin motivo={motivo} pendientes={bajados}\n"); vivo.close(); adc.cerrar(); ser.close()

with open(salida, "w", newline="") as f:
    f.write(cab.rstrip("\n") + f" motivo={motivo} pendientes={bajados}\n")
    w = csv.writer(f); w.writerow(["t_s", "fase", "mm", "F_N"]); w.writerows(filas)
fino = [r for r in filas if r[1] == "fino"]
print("k por tramos de fuerza (bajada):")
for nom, (k, n) in k_por_bandas([r[2] for r in fino], [r[3] for r in fino]).items():
    print(f"  {nom:<11} k = {'%.2f N/mm' % k if k is not None else 'n/d':<14} (n={n})")
print("CSV:", salida)
