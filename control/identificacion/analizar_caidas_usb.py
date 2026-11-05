"""Cruza las caidas del USB (kernel, 'disabled by hub (EMI?)') con los eventos del ensayo (logs/ensayo_A_eventos.csv):
para cada caida: tiempo desde el ultimo comando MANUAL, si cayo MIENTRAS el eje se movia (cmd .. cmd+duracion) o en reposo.
Uso: analizar_caidas_usb.py [--desde 'YYYY-MM-DD HH:MM:SS']"""
import argparse, csv, subprocess, re
ap = argparse.ArgumentParser(); ap.add_argument("--desde", default="2026-11-05 16:36:00"); ap.add_argument("--eventos", default="logs/ensayo_A_eventos.csv"); a = ap.parse_args()
out = subprocess.run(["journalctl", "-k", "-o", "short-unix", "--since", a.desde, "--no-pager"], capture_output=True, text=True).stdout
caidas = [float(l.split()[0]) for l in out.splitlines() if "disabled by hub (EMI" in l]
ev = [(float(r[0]), r[1], r[2]) for r in csv.reader(open(a.eventos)) if r and r[0].replace(".", "", 1).isdigit()]
cmds = [(t, d) for t, e, d in ev if e == "cmd"]
print(f"{len(caidas)} caidas desde {a.desde}; {len(cmds)} comandos en {a.eventos}")
mov = rep = 0
for c in caidas:
    prev = [(t, d) for t, d in cmds if t <= c]
    if not prev: print(f"  caida {c:.1f}: antes del primer comando registrado"); continue
    t, d = prev[-1]; pasos = abs(int(d.split()[-1])); dur = pasos / 1600 + 0.5
    estado = "DURANTE MOVIMIENTO" if c - t <= dur else "en reposo/espera"
    mov += estado.startswith("DURANTE"); rep += not estado.startswith("DURANTE")
    print(f"  caida {c:.1f}: {c-t:5.1f} s despues del comando [{d}] (mov dura ~{dur:.1f} s) -> {estado}")
print(f"RESUMEN: {mov} durante movimiento, {rep} en reposo/espera")
