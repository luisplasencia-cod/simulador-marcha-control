"""Repite el Ensayo A hasta obtener una corrida COMPLETA: motivo 'fmax alcanzada (OK)', subida registrada y 0 pasos pendientes.
Se DETIENE (no reintenta) si queda algun paso sin subir o si el ADC/USB no estan sanos. Pausa calmada entre intentos.
Uso: repetir_hasta_completa.py --max_intentos 5 -- <argumentos de ensayo_A_rigidez.py>"""
import argparse, glob, os, subprocess, sys, time
ap = argparse.ArgumentParser(); ap.add_argument("--max_intentos", type=int, default=5); ap.add_argument("--pausa_s", type=float, default=30.0)
a, resto = ap.parse_known_args(); resto = [x for x in resto if x != "--"]
aqui = os.path.dirname(os.path.abspath(__file__))
for i in range(1, a.max_intentos + 1):
    print(f"=== intento {i}/{a.max_intentos} ===", flush=True)
    p = subprocess.run([sys.executable, os.path.join(aqui, "ensayo_A_rigidez.py"), *resto, "--ejecutar"], capture_output=True, text=True)
    out = p.stdout + p.stderr; open(f"/tmp/claude-1000/intento_{i}.txt", "w").write(out)
    csv = next((l.split("CSV:")[1].strip() for l in out.splitlines() if l.startswith("CSV:")), None)
    pend = next((l.split(":")[1].strip() for l in out.splitlines() if l.startswith("pasos pendientes")), "?")
    ok = "Motivo de parada: fmax alcanzada (OK)" in out
    nsub = sum(1 for l in open(csv) if ",sube," in l) if csv and os.path.exists(csv) else 0
    print(f"  fmax_ok={ok} subida_puntos={nsub} pendientes={pend} csv={csv}", flush=True)
    for l in out.splitlines():
        if l.startswith("  todo") or l.startswith("  8-40") or l.startswith("  40-100") or l.startswith("  >100"): print(l, flush=True)
    if pend != "0": print("PARADA: quedaron pasos sin subir -> revisar a mano. No se reintenta.", flush=True); sys.exit(2)
    if ok and nsub >= 5: print(f"COMPLETA en el intento {i}: {csv}", flush=True); sys.exit(0)
    time.sleep(a.pausa_s)
print("No se logro una corrida completa en los intentos permitidos.", flush=True); sys.exit(1)
