"""Protocolo ESTANDAR de identificacion de rigidez k(F) de cualquier protesis/calzado (preparacion).
Ver reportes/2026-11-20_protocolo_identificacion_rigidez_estandar.md.

Modo --simulado (probado, sin hardware): rampa de carga y descarga sobre una planta SINTETICA no lineal
con histeresis, ajuste de k(F) por franjas, histeresis, repetibilidad entre 2 corridas, tabla Kp(F)
y JSON. El modo hardware NO existe aun (aborta): falta integrarlo al lazo/interfaz; no se movio nada.
Reutiliza ajuste_k.pendiente y la regla k_usado >= k_real (GananciaSegura/estimador_k_en_linea).
"""
import argparse, json, sys
from datetime import datetime
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from ajuste_k import pendiente

PASOS_POR_MM_Y = 80.0
V_RAMPA_MM_S = 2.0        # eleccion de diseno: a k=18-58 N/mm da 36-116 N/s (literatura: 100 N/s Tacca 2024, 200 N/s Major 2022,
                          # 100-250 N/s estatico ISO 22675 (copia sin confirmar edicion), 20 mm/s Turner 2022); retardo ~20 ms -> <0.04 mm
ANCHO_N = 50.0            # franja de fuerza
MARGEN = 0.15             # k_usado = k_rigido_carga * 1.15 (como Md)
TOL_REPET = 0.15          # SIN RESPALDO en literatura (Turner 2022: duplicados 2.4+-1.3 %); validar con la 1.a corrida real
N_CICLOS = 3              # 1.o = acondicionamiento (descartado), 2.o y 3.o analizados (Turner 6 ciclos/ultimos 3; Tacca 4/ultimos 3; Major 2/2.o)
F_REF_INI_N = 50.0        # k lineal de 50 N al pico (Turner 2022, Tacca 2024)
MIN_PTS = 5

def planta_sintetica(rng, k0=18.0, k1=0.04, hist=0.18, ruido=0.8):
    """F(z) de carga (z mm de descenso); la descarga baja un `hist` de F. NO es medida."""
    def f_carga(z): return k0 * z + 0.2 * z ** 2      # tangente 18 -> ~50 N/mm a 80 mm (forma NO medida)
    def medir(z, sube):
        f = f_carga(z) * (1 - hist if not sube else 1.0)
        return f + rng.normal(0, ruido)
    return medir

def corrida(medir, f_pico, z_max_mm=80.0, dt=0.01):
    """Rampa a V_RAMPA hasta f_pico (tope de fuerza) o z_max (tope de recorrido), y vuelta. Devuelve z,F,fase."""
    z, zs, fs, fase = 0.0, [], [], []
    estado = "carga"
    while True:
        z += (V_RAMPA_MM_S * dt) * (1 if estado == "carga" else -1)
        f = medir(z, estado == "carga")
        zs.append(z); fs.append(f); fase.append(estado)
        if estado == "carga" and (f >= f_pico or z >= z_max_mm):
            motivo = "pico" if f >= f_pico else "recorrido_max"
            estado = "descarga"
            if motivo == "recorrido_max" and f < 0.5 * f_pico:
                return np.array(zs), np.array(fs), np.array(fase), "demasiado_blanda"
        if estado == "descarga" and (f <= 5.0 or z <= 0):
            return np.array(zs), np.array(fs), np.array(fase), motivo

def k_franjas(z, f, fase, f_pico):
    """k tangente (pendiente de ajuste) por franja de ANCHO_N y sentido."""
    out = []
    for lo in np.arange(10.0, f_pico, ANCHO_N):
        fila = {"f_desde_n": float(lo), "f_hasta_n": float(lo + ANCHO_N)}
        for sent in ("carga", "descarga"):
            m = (fase == sent) & (f >= lo) & (f < lo + ANCHO_N)
            k = pendiente(list(z[m]), list(f[m])) if m.sum() >= MIN_PTS * 5 else None
            fila["k_" + sent] = None if k is None else round(float(abs(k)), 2)
        out.append(fila)
    return out

def k_lineal_50_pico(z, f, fase, f_pico):
    """k de regresion lineal en carga entre 50 N y el pico (definicion de Turner 2022 / Tacca 2024; aqui por minimos cuadrados)."""
    m = (fase == "carga") & (f >= F_REF_INI_N)
    return round(abs(float(pendiente(list(z[m]), list(f[m])))), 2) if m.sum() >= MIN_PTS else None

def histeresis(z, f, fase):
    """Fraccion de la energia de carga no devuelta (area entre ramas / area de carga)."""
    c, d = fase == "carga", fase == "descarga"
    e_c = np.trapezoid(f[c], z[c]); e_d = np.trapezoid(f[d][::-1], z[d][::-1]) if d.sum() > 1 else np.nan
    return float(1 - abs(e_d) / abs(e_c)) if e_c else float("nan")

def repetibilidad(a, b):
    """Maximo |dk|/k_medio sobre franjas de carga comunes."""
    r = [abs(x["k_carga"] - y["k_carga"]) / (0.5 * (x["k_carga"] + y["k_carga"]))
         for x, y in zip(a, b) if x["k_carga"] and y["k_carga"]]
    return max(r) if r else float("nan")

def tabla_lazo(franjas, kp=6.0):
    """k_usado (fijo por pisada) y Kp(F)=Kp*min(1,k_usado/k(F)) por franja, como --kp_programado."""
    ks = [x["k_carga"] for x in franjas if x["k_carga"]]
    k_rig = float(np.percentile(ks, 70))
    k_usado = (1 + MARGEN) * k_rig
    return {"k_usado_n_mm": round(k_usado, 2), "pasos_por_n": round(PASOS_POR_MM_Y / k_usado, 3), "kp_base": kp,
            "kp_por_franja": [{"f_desde_n": x["f_desde_n"], "kp": round(kp * min(1.0, k_usado / x["k_carga"]), 2)}
                              for x in franjas if x["k_carga"]]}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", required=True); ap.add_argument("--angulo_deg", type=float, required=True)
    ap.add_argument("--calzado", default="ninguno")
    ap.add_argument("--peso_kg", type=float, default=80.0)
    ap.add_argument("--hueco_mm", type=float, default=None)
    ap.add_argument("--hueco_remedido", action="store_true")
    ap.add_argument("--salida", default=None)
    ap.add_argument("--simulado", action="store_true")
    a = ap.parse_args()
    if not a.simulado:
        sys.exit("Modo hardware NO implementado (falta integrarlo al lazo/interfaz; ver el reporte, seccion 'Que falta'). "
                 "Nada se movio.")
    f_pico = 1.15 * a.peso_kg * 9.81          # pico Gutenberg ~115 %BW; la carga se sube por escalones en hardware
    rng = np.random.default_rng(1)
    runs = []
    for _ in range(N_CICLOS):
        z, f, fase, motivo = corrida(planta_sintetica(rng), f_pico)
        if motivo == "demasiado_blanda":
            sys.exit("ABORTA: no llega a la fuerza objetivo dentro del recorrido maximo")
        runs.append((k_franjas(z, f, fase, f_pico), histeresis(z, f, fase), motivo, k_lineal_50_pico(z, f, fase, f_pico)))
    runs = runs[1:]                      # se descarta el ciclo de acondicionamiento
    rep = repetibilidad(runs[0][0], runs[1][0])
    valido = rep <= TOL_REPET
    reg = {"id": a.id, "fecha": datetime.now().isoformat(timespec="seconds"), "angulo_deg": a.angulo_deg,
           "calzado": a.calzado, "peso_objetivo_kg": a.peso_kg, "f_pico_n": round(f_pico, 1),
           "hueco_mm": a.hueco_mm, "v_rampa_mm_s": V_RAMPA_MM_S, "n_ciclos": N_CICLOS, "k_lineal_50_pico_n_mm": runs[0][3], "origen": "SIMULADO",
           "k_franjas_corrida1": runs[0][0], "histeresis_energia": round(runs[0][1], 3),
           "repetibilidad_max_dk_rel": round(rep, 3), "tolerancia": TOL_REPET, "valido": bool(valido),
           "lazo": tabla_lazo(runs[0][0])}
    s = json.dumps(reg, indent=1, ensure_ascii=False)
    if a.salida: Path(a.salida).write_text(s, encoding="utf-8")
    print(s)
    return 0 if valido else 1

if __name__ == "__main__":
    sys.exit(main())
