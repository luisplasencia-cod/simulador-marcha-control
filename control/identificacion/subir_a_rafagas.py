"""Sube el eje Y 'pasos' cuando el USB se cae al abrir el puerto con el eje cargado.
Cada apertura reinicia el ESP32 y el USB se cae ~8 s despues; en esa ventana se mandan tramos MANUAL
(cuenta SOLO los pasos con ack OK). Entre rafagas espera a que el enlace by-id exista y este estable 15 s."""
import os, sys, time, serial
P = "/dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001-if00-port0"
rest = int(sys.argv[1]); TRAMO = int(sys.argv[2]) if len(sys.argv) > 2 else 2400
for rafaga in range(1, 9):
    if rest <= 0: break
    est = 0
    while est < 15:                       # estable 15 s
        est = est + 1 if os.path.exists(P) else 0; time.sleep(1)
    t0 = time.time(); hecho = 0
    try:
        s = serial.Serial(P, 115200, timeout=1.0)          # SIN esperar: se manda el comando YA (la caida llegaba ~1-2 s despues de abrir)
        while rest > 0 and time.time() - t0 < 14:
            d = min(rest, TRAMO); s.write(f"<MANUAL:1:{d}>".encode()); r = s.readline().decode(errors="replace").strip()
            if not r.startswith("OK"): print("  ack", repr(r), flush=True); time.sleep(0.5); continue
            rest -= d; hecho += d; print(f"  rafaga {rafaga}: +{d} OK, pendientes {rest}", flush=True); time.sleep(d / 1600 + 0.3)
        s.close()
    except Exception as e:
        print(f"  rafaga {rafaga} interrumpida: {str(e)[:60]} (hecho {hecho})", flush=True)
    time.sleep(30)   # calma entre rondas: no golpear el puerto durante una tormenta
print("PENDIENTES FINALES:", rest, flush=True)
