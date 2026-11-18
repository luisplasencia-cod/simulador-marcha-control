"""Ensayo B: RESPUESTA DINAMICA del eje vertical (Y) CON CONTACTO — retardo comando->fuerza y rigidez dinamica.
Escrito 2026-11-18. PROBADO SOLO EN SIMULACION hasta que se corra en hardware.

Que mide (con la prótesis apoyada, pie en un ángulo fijo):
  - RETARDO de lazo: desde que se ordena SET_VEL hasta que Fz empieza a cambiar. Incluye ESP32 (sondeo del firmware +
    generación de pulsos), servo/mecánica, amplificador AMTI, ADS1256, UART y el bloque de 7 muestras. Es el retardo que
    el diseño del lazo necesitaba y que hasta hoy solo se había supuesto/sumado por partes.
  - PENDIENTE dF/dt por velocidad, y de ahí la rigidez dinámica k_din = (dF/dt)/(v/PASOS_MM) [N/mm], para contrastar con
    el Ensayo A (estático: plana 23.0, talón 26.4 N/mm).
Secuencia: tara -> aproximación con detección de contacto (igual que el lazo) -> pulsos: por cada velocidad v, REPS veces:
  quieto 0.5 s -> baja a v durante T s -> sube a v durante T s (vuelve al punto) -> quieto 0.5 s. Retorno a y0 al final.
Modelo ajustado a cada pulso de bajada: F(t) = b + s*max(0, t - t_cmd - d), buscando d en 0..120 ms (rejilla de 2 ms).
Seguridad: tope --fmax_n (aborta y sube si se supera), descenso máximo = hueco + extra, verificación del contador cada 0.5 s,
  nunca HOME, ejes como ENTEROS (Y = 1), + = subir, Fz + = carga. Sin --ejecutar solo imprime el plan.
Limitaciones que el resultado NO resuelve: el tiempo de la muestra es el de FIN del bloque de 7 muestras (±3.5 ms); el retardo
  del ajuste tiene la incertidumbre del ruido (σ≈2.6 N con 60 Hz); k_din mezcla la rigidez de contacto con el seguimiento real
  del servo (la velocidad es la ORDENADA, no la medida); una prótesis y un ángulo por corrida."""
import argparse, csv, os, sys, time
import numpy as np

R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
sys.path.insert(0, os.path.join(R, "control"))
sys.path.insert(0, os.path.join(R, "herramientas"))
import lazo_fz_tiempo_real as L

EJE = L.EJE_VERTICAL      # ENTERO 1
PASOS_MM = float(L.PASOS_MM)


def ajustar(t, f, t_cmd, T):
    """Mejor (d, s, b) del modelo rampa con retardo. t relativo a t_cmd. Devuelve dict o None si hay pocos datos."""
    m = (t >= -0.3) & (t <= T + 0.02)
    tt, ff = t[m], f[m]
    if len(tt) < 20 or (tt < 0).sum() < 5:
        return None
    mejor = None
    for d in np.arange(0.0, 0.1201, 0.002):
        x = np.clip(tt - d, 0, None)
        A = np.vstack([np.ones_like(x), x]).T
        sol, res, *_ = np.linalg.lstsq(A, ff, rcond=None)
        e = float(np.sum((A @ sol - ff) ** 2))
        if mejor is None or e < mejor[0]:
            mejor = (e, d, float(sol[1]), float(sol[0]))
    e, d, s, b = mejor
    return {"d_ms": d * 1000, "s_n_s": s, "b_n": b, "rms_n": float(np.sqrt(e / len(tt)))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hueco_mm", type=float, required=True, help="planta->plato medido por Luis AHORA (mm)")
    ap.add_argument("--hueco_remedido", action="store_true", help="confirma que el hueco se midio de nuevo para esta corrida")
    ap.add_argument("--angulo_deg", type=float, required=True, help="angulo del pie (queda en el CSV)")
    ap.add_argument("--fmax_n", type=float, default=60.0, help="tope de Fz: si se supera, aborta y sube")
    ap.add_argument("--vels", default="200,400", help="velocidades de bajada [pasos/s] separadas por coma")
    ap.add_argument("--dur_s", type=float, default=0.2, help="duracion de cada pulso")
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--extra_mm", type=float, default=20.0)
    ap.add_argument("--umbral_contacto_n", type=float, default=8.0)
    ap.add_argument("--fuente_fz", choices=["spi", "uart"], default="uart")
    ap.add_argument("--puerto_fz", default="/dev/ttyAMA0")
    ap.add_argument("--puerto_esp32", default="/dev/ttyUSB0")
    ap.add_argument("--signo_fz", type=float, default=1.0, choices=[1.0, -1.0])
    ap.add_argument("--simulado", action="store_true")
    ap.add_argument("--ejecutar", action="store_true")
    a = ap.parse_args()
    vels = [int(x) for x in a.vels.split(",")]
    if any(v <= 0 or v > 800 for v in vels):
        raise SystemExit("--vels: solo positivas y <= 800 pasos/s (10 mm/s)")
    maxF = max(vels) / PASOS_MM * 23.0 * a.dur_s   # estimacion con k=23 N/mm (plana), NO medida para este ensayo
    print(f"PLAN: hueco {a.hueco_mm:.0f} mm, angulo {a.angulo_deg}, vels {vels} pasos/s ({[round(v/PASOS_MM,1) for v in vels]} mm/s), "
          f"pulso {a.dur_s} s x {a.reps}, tope {a.fmax_n} N. Subida de Fz esperada por pulso (k=23 N/mm supuesto): hasta ~{maxF:.0f} N sobre el contacto.")
    if not a.hueco_remedido and not a.simulado:
        raise SystemExit("Falta --hueco_remedido: el hueco se mide DE NUEVO antes de cada corrida (regla de Luis).")
    if not a.ejecutar and not a.simulado:
        print("(sin --ejecutar: solo plan, no se movio nada)"); return

    os.makedirs(os.path.join(R, "pruebas", "resultados"), exist_ok=True)
    marca = time.strftime("%Y%m%d_%H%M%S") + ("_SIM" if a.simulado else "")
    ruta = os.path.join(R, "control", "identificacion", "resultados", f"ensayoB_ang{a.angulo_deg:g}_{marca}.csv")
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    from en_vivo import EnVivo
    os.makedirs(os.path.join(R, "logs"), exist_ok=True)
    ev = EnVivo("Ensayo B: respuesta dinamica con contacto", ruta=os.path.join(R, "logs", "prueba_en_vivo.csv"))

    lector = esp32 = None
    motivo = "completado"
    filas = []          # t, fase, F, vel_ordenada, y_rel
    pulsos = []         # (v, rep, t_cmd, T)
    t0 = time.monotonic()
    descenso_mm = 0.0
    try:
        if a.simulado:
            planta = L._PlantaSimulada(contacto_mm=a.hueco_mm - 5.0)
            esp32, lector = L.ESP32Simulado(planta), L.LectorSimulado(planta)
        else:
            ev.escribir("inicio", 0, 0, "CONECTANDO: ADC primero, luego ESP32 (se reinicia al abrir)")
            lector = L.LectorFzUART(a.puerto_fz, signo=a.signo_fz) if a.fuente_fz == "uart" else L.LectorFzFiltrado()
            esp32 = L.ClienteVelocidadESP32(puerto=a.puerto_esp32)
        ev.escribir("tara", 0, 0, "TARA: eje quieto y sin contacto")
        f0, p5, p95 = lector.tarar()
        print(f"Tara f0={f0:.2f} N (p5 {p5:.2f}, p95 {p95:.2f})")
        if p95 - p5 > 15.0:
            raise RuntimeError(f"tara inestable ({p95 - p5:.1f} N)")

        def muestra(fase, vel):
            f = lector.leer_n()
            t = time.monotonic() - t0
            filas.append((t, fase, f, vel, esp32_y_rel_cache[0]))
            ev.escribir(fase, f, esp32_y_rel_cache[0], f"{fase} v={vel}")
            if f > a.fmax_n:
                raise RuntimeError(f"Fz {f:.1f} N > tope {a.fmax_n} N")
            if f < L.F_NEG_MAX_N:
                raise RuntimeError(f"Fz {f:.1f} N anomala")
            return f, t

        esp32_y_rel_cache = [0]

        def verificar(esperado_mm):
            real = esp32.pos_y_rel(); esp32_y_rel_cache[0] = real
            esperado = -esperado_mm * PASOS_MM
            if abs(real - esperado) > 0.25 * abs(esperado) + 150:
                raise RuntimeError(f"contador {real} no sigue lo ordenado {esperado:.0f}")

        # ---- aproximacion (mismo criterio que el lazo) ----
        t_prev, seguidas, ult_chk = time.monotonic(), 0, time.monotonic()
        while True:
            if descenso_mm >= a.hueco_mm + a.extra_mm:
                raise RuntimeError("sin contacto en el descenso maximo")
            v = L.V_RAPIDA if descenso_mm < a.hueco_mm - L.ZONA_LENTA_MM else L.V_LENTA
            esp32.set_vel(EJE, -v)
            ahora = time.monotonic(); descenso_mm += v * (ahora - t_prev) / PASOS_MM; t_prev = ahora
            f, _ = muestra("aproximando", -v)
            if time.monotonic() - ult_chk > 0.5:
                verificar(descenso_mm); ult_chk = time.monotonic()
            seguidas = seguidas + 1 if f > a.umbral_contacto_n else 0
            if seguidas >= 5:
                esp32.detener(EJE)
                print(f"CONTACTO a {descenso_mm:.1f} mm de descenso (hueco declarado {a.hueco_mm:.0f}): F={f:.1f} N")
                break
            time.sleep(L.DT_CONTROL_S)
        t_fin = time.monotonic()
        while time.monotonic() - t_fin < 0.6:
            muestra("contacto", 0)
        base_contacto = float(np.median([x[2] for x in filas[-40:]]))
        print(f"Fz base en contacto: {base_contacto:.1f} N")

        # ---- pulsos ----
        for v in vels:
            for rep in range(a.reps):
                t_q = time.monotonic()
                while time.monotonic() - t_q < 0.5:
                    muestra(f"quieto v{v}", 0)
                t_cmd = time.monotonic() - t0
                pulsos.append((v, rep, t_cmd, a.dur_s))
                tp = time.monotonic(); desc0 = descenso_mm
                while time.monotonic() - tp < a.dur_s:
                    esp32.set_vel(EJE, -v)
                    muestra(f"baja v{v}", -v)
                    ahora = time.monotonic(); descenso_mm += v * (ahora - t_prev) / PASOS_MM; t_prev = ahora
                tp = time.monotonic()
                while time.monotonic() - tp < a.dur_s + 0.03:
                    esp32.set_vel(EJE, +v)
                    muestra(f"sube v{v}", +v)
                    ahora = time.monotonic(); descenso_mm -= v * (ahora - t_prev) / PASOS_MM; t_prev = ahora
                esp32.detener(EJE)
                t_prev = time.monotonic()
                verificar(descenso_mm)
        t_q = time.monotonic()
        while time.monotonic() - t_q < 0.5:
            muestra("quieto final", 0)
    except BaseException as ex:
        motivo = f"ABORTADO: {ex!r}"
        print(motivo)
    finally:
        try:
            if esp32:
                esp32.detener(EJE)
                neto = esp32.pos_y_rel()
                print(f"Retorno: Y respecto al inicio = {neto} pasos -> subiendo {-neto}" if neto < 0 else f"Y respecto al inicio = {neto} pasos")
                if neto < 0:
                    esp32.subir_pasos(-neto)
                print(f"Y final respecto al inicio: {esp32.pos_y_rel()} pasos (debe ser ~0)")
        except BaseException as e2:
            print(f"!!! NO SE PUDO RETORNAR Y AUTOMATICAMENTE ({e2!r}): subirlo con MANUAL")
        for o in (esp32, lector):
            try: o.cerrar()
            except Exception: pass
        ev.cerrar(motivo)
        with open(ruta, "w", newline="") as fcsv:
            w = csv.writer(fcsv)
            w.writerow([f"# angulo_deg={a.angulo_deg} hueco_mm={a.hueco_mm} fmax_n={a.fmax_n} vels={a.vels} dur_s={a.dur_s} signo_fz={a.signo_fz} fuente={a.fuente_fz} motivo={motivo}"])
            w.writerow(["t_s", "fase", "F_N", "vel_ordenada_pasos_s", "y_rel_pasos"])
            w.writerows(filas)
        print("CSV:", ruta)

    # ---- analisis ----
    if filas and pulsos:
        t = np.array([x[0] for x in filas]); F = np.array([x[2] for x in filas])
        print("\nvel [pasos/s] (mm/s) | rep | retardo [ms] | pendiente [N/s] | k_din [N/mm] | rms ajuste [N]")
        res = {}
        for v, rep, tc, T in pulsos:
            r = ajustar(t - tc, F, tc, T)
            if not r:
                print(f"{v:5d} rep{rep}: datos insuficientes"); continue
            k = r["s_n_s"] / (v / PASOS_MM)
            res.setdefault(v, []).append((r["d_ms"], r["s_n_s"], k))
            print(f"{v:5d} ({v/PASOS_MM:4.1f}) | {rep} | {r['d_ms']:6.0f} | {r['s_n_s']:8.1f} | {k:7.1f} | {r['rms_n']:.2f}")
        for v, lst in res.items():
            d, s, k = (np.array(x) for x in zip(*lst))
            print(f"v={v}: retardo {d.mean():.0f} ms (min {d.min():.0f}, max {d.max():.0f}), k_din {k.mean():.1f} N/mm (min {k.min():.1f}, max {k.max():.1f}), n={len(lst)}")


if __name__ == "__main__":
    main()
