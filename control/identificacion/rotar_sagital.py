"""Gira el eje sagital K a un angulo objetivo, solo por serial (NO usa ADC ni mueve Y/X).
Convencion de gaitsim (leida de su codigo, solo lectura): paso positivo = angulo positivo, 111.11 pasos/grado.
El ESP32 pierde su contador al abrir el puerto, asi que el angulo FISICO se lleva en un archivo de estado
(estado_angulo_K.json): angulo_deg estimado. Se actualiza SOLO tras un movimiento con todos los ack OK.
Uso: rotar_sagital.py --a 11.14        (angulo objetivo)   |  --delta_pasos 682   |  --plan (no mueve)
Limites de seguridad: rango fisico del rig -5000..+5400 pasos (-45.0..+48.6 deg) respecto de la horizontal."""
import argparse, json, sys, time
from pathlib import Path
import serial
PASOS_DEG = 5000 / 45.0          # 111.11 (gaitsim STEPS_PER_DEG_ANGLE)
AMIN, AMAX = -45.0, 48.6
ESTADO = Path(__file__).with_name("estado_angulo_K.json")
PUERTO = "/dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001-if00-port0"
ap = argparse.ArgumentParser()
ap.add_argument("--a", type=float, help="angulo objetivo [deg]")
ap.add_argument("--delta_pasos", type=int)
ap.add_argument("--plan", action="store_true")
ap.add_argument("--tramo", type=int, default=600, help="pasos por MANUAL (<=)")
a = ap.parse_args()
est = json.loads(ESTADO.read_text()) if ESTADO.exists() else {"angulo_deg": 5.0, "fuente": "a ojo (Luis, 2026-11-05)"}
ang0 = est["angulo_deg"]
delta = a.delta_pasos if a.delta_pasos is not None else round((a.a - ang0) * PASOS_DEG)
ang1 = ang0 + delta / PASOS_DEG
print(f"angulo estimado actual {ang0:.2f} deg -> objetivo {ang1:.2f} deg: {delta:+d} pasos ({delta/PASOS_DEG:+.2f} deg)")
if not (AMIN + 1.0 <= ang1 <= AMAX - 1.0):
    sys.exit(f"Abortado: {ang1:.2f} deg queda a <1 deg del limite fisico ({AMIN}..{AMAX}).")
if a.plan: sys.exit(0)
s = serial.Serial(PUERTO, 115200, timeout=2.0); time.sleep(2.0); s.reset_input_buffer()
hecho = 0
try:
    while hecho != delta:
        d = max(-a.tramo, min(a.tramo, delta - hecho))
        s.reset_input_buffer(); s.write(f"<MANUAL:2:{d}>".encode()); r = s.readline().decode(errors="replace").strip()
        if not r.startswith("OK"): raise RuntimeError(f"ack {r!r}")
        hecho += d; time.sleep(abs(d) / 3200 + 0.3)
        print(f"  K {hecho:+d}/{delta:+d} pasos", flush=True)
finally:
    s.close()
    ang_real = ang0 + hecho / PASOS_DEG
    ESTADO.write_text(json.dumps({"angulo_deg": round(ang_real, 3), "fuente": f"estimado por pasos desde {est['fuente']}; ultimo movimiento {hecho:+d} pasos",
                                  "actualizado": time.strftime("%Y-%m-%d %H:%M:%S")}, indent=1))
    print(f"estado guardado: angulo estimado = {ang_real:.2f} deg (hecho {hecho:+d} de {delta:+d} pasos)")
