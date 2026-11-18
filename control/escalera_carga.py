"""Escalera de carga del lazo de Fz en Y (pedido de Luis, 2026-11-18): 10, 20, ... 90 kg en la MISMA posición (pie plano,
X y ángulo quietos), para encontrar el límite (velocidad, compresión, tope) o lo que falle. Cada escalón es una corrida del
lazo validado (`control/lazo_fz_tiempo_real.py`, Kp 10, Fz por UART), como subproceso, idéntica a las corridas manuales.
- Visor en vivo en la pantalla del RPi (herramientas/visor_pruebas.py): Fz, desplazamiento ORDENADO de Y y fase.
- Por escalón: log CSV (con y_mm y v_mm_s), salida de texto y figura (fuerza, error, desplazamiento y velocidad de Y).
- Al final: tabla (CSV + Markdown) y figura resumen (error, velocidad máx., compresión y rigidez vs peso).
- Se DETIENE al primer aborto (ese es el límite encontrado). Tope de fuerza = min(1.25 × pico, 1300 N); límite estructural
  decidido por Luis: 1500 N. Velocidad máx. de Y = 9000 pasos/s (112 mm/s; 12000 fue brusco).
Uso: .venv/bin/python control/escalera_carga.py [--pesos 10,20,...] [--n_ciclos 6] [--pausa_s 5]  (pide escribir SI)"""
import argparse, csv, os, re, subprocess, sys, time
import numpy as np

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = os.path.join(R, ".venv", "bin", "python")
ap = argparse.ArgumentParser()
ap.add_argument("--pesos", default="10,20,30,40,50,60,70,80,90")
ap.add_argument("--n_ciclos", type=int, default=6)
ap.add_argument("--v_max", type=int, default=9000)
ap.add_argument("--pausa_s", type=float, default=5.0)
ap.add_argument("--si", action="store_true", help="no preguntar (Luis ya autorizó)")
ap.add_argument("--simulado", action="store_true", help="prueba del script sin hardware (planta simulada del lazo)")
a = ap.parse_args()
pesos = [float(x) for x in a.pesos.split(",")]
assert a.v_max <= 9000
marca = time.strftime("%Y%m%d_%H%M%S")
dir_out = os.path.join(R, "reportes", "escalera", marca + ("_SIM" if a.simulado else ""))
os.makedirs(dir_out, exist_ok=True)
print(f"ESCALERA {pesos} kg, {a.n_ciclos} pisadas, v_max {a.v_max}. Pie plano, solo Y. Salidas: {dir_out}")
if not a.si and input("Escribe SI para empezar: ").strip() != "SI":
    sys.exit("cancelado")

visor = subprocess.Popen([PY, os.path.join(R, "herramientas", "visor_pruebas.py")], cwd=R,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
tabla = []
try:
    for kg in pesos:
        peso_n = kg * 9.81; pico = 1.178 * peso_n; fmax = min(1.25 * pico, 1300.0)
        cmd = [PY, "-u", os.path.join(R, "control", "lazo_fz_tiempo_real.py"), "--peso_sujeto_n", f"{peso_n:.1f}",
               "--fmax_n", f"{fmax:.0f}", "--hueco_mm", "45", "--extra_mm", "60", "--hueco_remedido", "--angulo_deg", "0",
               "--n_ciclos", str(a.n_ciclos), "--v_max", str(a.v_max), "--ejecutar"] + (
               ["--simulado"] if a.simulado else ["--fuente_fz", "uart", "--puerto_fz", "/dev/ttyAMA0"])
        print(f"\n=== {kg:.0f} kg: pico {pico:.0f} N, tope {fmax:.0f} N — {time.strftime('%H:%M:%S')} ===", flush=True)
        salida = os.path.join(dir_out, f"{kg:.0f}kg_salida.txt")
        with open(salida, "w") as fo:
            p = subprocess.run(cmd, cwd=R, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            fo.write(p.stdout)
        txt = p.stdout
        print("\n".join(l for l in txt.splitlines() if l.startswith(("CONTACTO", "ciclo", "ABORT", "Motivo", "Y final"))), flush=True)
        m_log = re.search(r"(control/telemetria/registros/\S+_fz\.csv)", txt)
        m_con = re.search(r"CONTACTO a ([\d.]+) mm", txt)
        motivo = (re.search(r"Motivo de cierre: (.*?) \|", txt) or re.search(r"(.*)$", "sin motivo")).group(1)
        fila = {"kg": kg, "pico_obj_N": round(pico), "tope_N": round(fmax), "motivo": motivo,
                "contacto_mm": float(m_con.group(1)) if m_con else None}
        if m_log and os.path.exists(os.path.join(R, m_log.group(1))):
            log = os.path.join(R, m_log.group(1))
            rows = list(csv.DictReader(open(log)))
            if rows:
                c = np.array([int(r["ciclo"]) for r in rows]); rr = np.array([float(r["r"]) for r in rows])
                F = np.array([float(r["F_med"]) for r in rows]); u = np.array([float(r["u"]) for r in rows])
                y = np.array([float(r["y_mm"]) for r in rows]) if "y_mm" in rows[0] else None
                rms = [float(np.sqrt(np.mean((rr[c == k] - F[c == k]) ** 2))) for k in range(c.max() + 1)]
                fila.update({"pisadas": int(c.max() + 1), "rms_primera_N": round(rms[0], 1), "rms_ultima_N": round(rms[-1], 1),
                             "rms_ultima_pct": round(rms[-1] / pico * 100, 1), "F_max_N": round(float(F.max())),
                             "v_max_mm_s": round(float(abs(u).max()) / 80, 1), "saturado_pct": round(float((abs(u) >= a.v_max - 1).mean() * 100), 1),
                             "log": os.path.relpath(log, R)})
                if y is not None and m_con:
                    comp = -float(y.min()) - float(m_con.group(1))
                    fila["compresion_max_mm"] = round(comp, 1)
                    fila["rigidez_aparente_N_mm"] = round((float(F.max()) - 20.0) / comp, 1) if comp > 0.5 else None
                subprocess.run([PY, os.path.join(R, "control", "telemetria", "graficar_corrida.py"), log, "--titulo",
                                f"Escalera {kg:.0f} kg (pico {pico:.0f} N), Kp 10, v_max {a.v_max}, plana 0 deg, solo Y — {motivo}",
                                "--salida", os.path.join(dir_out, f"{kg:.0f}kg.png")], cwd=R, stdout=subprocess.DEVNULL)
        tabla.append(fila)
        print("   ->", {k: v for k, v in fila.items() if k != "log"}, flush=True)
        if not motivo.startswith("completado"):
            print(f"\n*** ESCALERA DETENIDA en {kg:.0f} kg: {motivo}", flush=True)
            break
        time.sleep(a.pausa_s)
finally:
    try:
        visor.terminate()
    except Exception:
        pass
    claves = ["kg", "pico_obj_N", "tope_N", "contacto_mm", "pisadas", "rms_primera_N", "rms_ultima_N", "rms_ultima_pct", "F_max_N",
              "v_max_mm_s", "saturado_pct", "compresion_max_mm", "rigidez_aparente_N_mm", "motivo", "log"]
    with open(os.path.join(dir_out, "resumen.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=claves); w.writeheader(); [w.writerow({k: fl.get(k) for k in claves}) for fl in tabla]
    with open(os.path.join(dir_out, "resumen.md"), "w") as f:
        f.write("| kg | pico obj. N | tope N | RMS 1.ª → última N (% del pico) | F máx N | v máx Y mm/s | saturado % | compresión mm | rigidez N/mm | motivo |\n|---|---|---|---|---|---|---|---|---|---|\n")
        for fl in tabla:
            f.write(f"| {fl['kg']:.0f} | {fl['pico_obj_N']} | {fl['tope_N']} | {fl.get('rms_primera_N')} → {fl.get('rms_ultima_N')} ({fl.get('rms_ultima_pct')} %) | "
                    f"{fl.get('F_max_N')} | {fl.get('v_max_mm_s')} | {fl.get('saturado_pct')} | {fl.get('compresion_max_mm')} | {fl.get('rigidez_aparente_N_mm')} | {fl['motivo']} |\n")
    ok = [fl for fl in tabla if fl.get("rms_ultima_pct") is not None]
    if ok:
        import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
        kg = [fl["kg"] for fl in ok]
        fig, ax = plt.subplots(2, 2, figsize=(13, 8), facecolor="white")
        ax[0, 0].plot(kg, [fl["rms_ultima_pct"] for fl in ok], "o-"); ax[0, 0].set(title="Error RMS de la última pisada [% del pico]", xlabel="kg")
        ax[0, 1].plot(kg, [fl["v_max_mm_s"] for fl in ok], "o-"); ax[0, 1].axhline(a.v_max / 80, color="r", ls="--", label="techo"); ax[0, 1].legend()
        ax[0, 1].set(title="Velocidad máxima de Y [mm/s]", xlabel="kg")
        ax[1, 0].plot(kg, [fl.get("compresion_max_mm") or np.nan for fl in ok], "o-"); ax[1, 0].set(title="Compresión máx. desde el contacto [mm] (ordenada)", xlabel="kg")
        ax[1, 1].plot(kg, [fl.get("rigidez_aparente_N_mm") or np.nan for fl in ok], "o-"); ax[1, 1].set(title="Rigidez aparente [N/mm]", xlabel="kg")
        for x in ax.flat: x.grid(alpha=.3)
        fig.suptitle(f"Escalera de carga {marca} — lazo de Fz en Y, pie plano, solo vertical", fontsize=12)
        fig.tight_layout(); fig.savefig(os.path.join(dir_out, "resumen.png"), dpi=100, facecolor="white")
        subprocess.Popen([PY, os.path.join(R, "herramientas", "mostrar_figura.py"), os.path.join(dir_out, "resumen.png")] +
                         [os.path.join(dir_out, f"{fl['kg']:.0f}kg.png") for fl in tabla if os.path.exists(os.path.join(dir_out, f"{fl['kg']:.0f}kg.png"))],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    print("\nResumen:", os.path.join(dir_out, "resumen.md"))
