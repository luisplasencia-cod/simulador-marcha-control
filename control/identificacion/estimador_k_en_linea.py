"""Identificacion EN LINEA de la rigidez de contacto k (N/mm) del eje vertical, para que el lazo
de Fz funcione con una protesis montada de k DESCONOCIDA (sin Ensayo A previo ni
tabla_k_por_protesis.json).

Por que importa k: en el lazo de control/lazo_fz_tiempo_real.py
    u [pasos/s] = Kp * e [N] * pasos_por_n,   pasos_por_n = PASOS_POR_MM_Y / k_usado
y la planta cumple dF/dt ~= k_real * v [mm/s]. Entonces la ganancia del lazo en el dominio de
fuerza es  Kp_ef = Kp * k_real / k_usado.  Con k_usado fijo (26.4) una protesis 11x mas blanda
(punta 2.4 N/mm) responde 11x mas lento, y una mas rigida es MAS agresiva de lo disenado.
Si k_usado ~ k_real, Kp pasa a ser la constante de tiempo del lazo de fuerza [1/s], igual para
cualquier protesis. Regla de seguridad (decision 2026-11-06): equivocarse hacia k_usado > k_real
(lazo mas lento), nunca hacia k_usado < k_real (mas agresivo).

Piezas (todas sin hardware; probadas en simulacion: control/simulacion/sim_k_desconocida.py):
  EstimadorPrecarga   : rampa corta y lenta tras el contacto (como un Ensayo A automatico de ~1-2 s)
  EstimadorRLS        : minimos cuadrados recursivos con olvido sobre incrementos dF ~ k*dz
  TablaKPorFuerza     : k tangente por franja de fuerza y sentido (carga/descarga), aprendida
                        pisada a pisada (la protesis es NO lineal y con histeresis)
  GananciaSegura      : k_usado = k_estimado*(1+margen), sube al instante y baja despacio
  verificar_factibilidad: con k estimado, ¿alcanzan la velocidad maxima y el recorrido?

NADA de esto esta probado en el simulador real. Ver reportes/2026-11-19_identificacion_k_en_linea.md.
"""
from collections import deque

import numpy as np

PASOS_POR_MM_Y = 80.0   # confirmado (Ensayo 0, 2026-11-05)


class EstimadorPrecarga:
    """Acumula (z_mm descenso ordenado, F_N) durante una rampa LENTA de carga tras el contacto y
    devuelve la rigidez tangente en la parte alta de la rampa (la mas cercana a la zona de trabajo)
    y la secante. Si la rampa llega a `z_max_mm` sin alcanzar F_id -> la protesis es demasiado
    blanda para esta carga (k < F_id / z_max)."""

    def __init__(self, f_id_n, z_max_mm=40.0, f_min_n=8.0):
        self.f_id, self.z_max, self.f_min = f_id_n, z_max_mm, f_min_n
        self.z, self.f = [], []

    def agregar(self, z_mm, f_n):
        """Devuelve 'seguir', 'listo' o 'demasiado_blanda'."""
        self.z.append(z_mm); self.f.append(f_n)
        if f_n >= self.f_id:
            return "listo"
        if self.z and (z_mm - self.z[0]) >= self.z_max:
            return "demasiado_blanda"
        return "seguir"

    def resultado(self):
        z, f = np.asarray(self.z), np.asarray(self.f)
        m = f >= self.f_min
        if m.sum() < 5:
            raise ValueError("precarga con menos de 5 puntos sobre el umbral: no se puede estimar k")
        z, f = z[m], f[m]
        k_sec = (f[-1] - f[0]) / max(z[-1] - z[0], 1e-6)
        alto = f >= f[0] + 0.5 * (f[-1] - f[0])       # mitad superior de la rampa
        if alto.sum() >= 4 and np.ptp(z[alto]) > 0.2:
            k_tan = float(np.polyfit(z[alto], f[alto], 1)[0])
        else:
            k_tan = k_sec
        return {"k_tangente": max(k_tan, k_sec), "k_secante": k_sec, "n": int(m.sum())}


class EstimadorRLS:
    """k tangente por RLS escalar sobre incrementos: dF(t) = k * dz(t - d), con dz = descenso
    ORDENADO (lo que se manda con SET_VEL; no hay sensor de posicion) retrasado `retardo_s`
    (Ensayo B: 15-23 ms). Solo actualiza si |dz| > dz_min_mm (excitacion suficiente)."""

    def __init__(self, k0, dt_s=0.010, retardo_s=0.020, ventana=5, olvido=0.98, dz_min_mm=0.5,
                 k_min=0.5, k_max=300.0):
        self.k, self.P = float(k0), 100.0
        self.olvido, self.dz_min, self.k_min, self.k_max = olvido, dz_min_mm, k_min, k_max
        self.n_ret = max(0, int(round(retardo_s / dt_s)))
        self.ventana = ventana
        self.z_hist = deque(maxlen=self.n_ret + ventana + 1)
        self.f_hist = deque(maxlen=ventana + 1)

    def actualizar(self, z_ordenado_mm, f_n):
        self.z_hist.append(z_ordenado_mm); self.f_hist.append(f_n)
        if len(self.z_hist) < self.z_hist.maxlen or len(self.f_hist) < self.f_hist.maxlen:
            return self.k
        zl = list(self.z_hist)
        dz = zl[-1 - self.n_ret] - zl[-1 - self.n_ret - self.ventana]
        df = self.f_hist[-1] - self.f_hist[0]
        if abs(dz) < self.dz_min:
            return self.k
        g = self.P * dz / (self.olvido + dz * self.P * dz)
        self.k = min(self.k_max, max(self.k_min, self.k + g * (df - dz * self.k)))
        self.P = (self.P - g * dz * self.P) / self.olvido
        return self.k


class TablaKPorFuerza:
    """k tangente por franja de fuerza (ancho `ancho_n`) y sentido (+1 carga, -1 descarga),
    aprendida al final de cada pisada con los datos de esa pisada. Antes de tener datos de una
    franja devuelve `k_defecto`. Consulta conservadora: maximo de la franja actual y la siguiente
    hacia donde va la fuerza."""

    def __init__(self, k_defecto, ancho_n=50.0, f_max_n=1500.0, dt_s=0.010, retardo_s=0.020,
                 ventana=5, dz_min_mm=0.3, mezcla=0.5):
        self.k_def, self.ancho, self.mezcla = float(k_defecto), ancho_n, mezcla
        nb = int(np.ceil(f_max_n / ancho_n)) + 1
        self.tabla = {+1: np.full(nb, np.nan), -1: np.full(nb, np.nan)}
        self.n_ret = max(0, int(round(retardo_s / dt_s))); self.ventana = ventana; self.dz_min = dz_min_mm

    def _bin(self, f):
        return int(min(len(self.tabla[1]) - 1, max(0, f // self.ancho)))

    def aprender_pisada(self, z_ordenado_mm, f_n):
        z, f = np.asarray(z_ordenado_mm, float), np.asarray(f_n, float)
        r, w = self.n_ret, self.ventana
        if len(z) < r + w + 2:
            return
        dz = z[w:len(z) - r] - z[:len(z) - r - w]
        df = f[r + w:] - f[r:len(f) - w]
        fm = 0.5 * (f[r + w:] + f[r:len(f) - w])
        ok = np.abs(dz) >= self.dz_min
        nuevas = {+1: {}, -1: {}}
        self.ultima_carga = [(fmi, dfi / dzi) for dzi, dfi, fmi in zip(dz[ok], df[ok], fm[ok]) if dzi > 0 and dfi > 0]
        for dzi, dfi, fmi in zip(dz[ok], df[ok], fm[ok]):
            k = dfi / dzi
            if k <= 0:
                continue                      # ruido o cruce de rama: no es una rigidez
            nuevas[1 if dzi > 0 else -1].setdefault(self._bin(fmi), []).append(k)
        for s in (1, -1):
            for b, ks in nuevas[s].items():
                if len(ks) < 3:
                    continue
                kn = float(np.median(ks))
                v = self.tabla[s][b]
                self.tabla[s][b] = kn if np.isnan(v) else (1 - self.mezcla) * v + self.mezcla * kn

    def k_rigido_carga(self, f_desde_n, percentil=80.0):
        """k de la corrida: percentil alto de las pendientes de CARGA de la ultima pisada con
        F > f_desde_n (la zona de trabajo). Percentil y no maximo: el maximo lo dominan los cruces
        de rama de la histeresis y el ruido. None si no hay datos suficientes."""
        ks = [k for f, k in getattr(self, "ultima_carga", []) if f > f_desde_n]
        return float(np.percentile(ks, percentil)) if len(ks) >= 10 else None

    def consultar(self, f_n, sentido):
        s = 1 if sentido >= 0 else -1
        b = self._bin(f_n)
        vecina = min(len(self.tabla[s]) - 1, b + 1) if s > 0 else max(0, b - 1)
        vals = [v for v in (self.tabla[s][b], self.tabla[s][vecina]) if not np.isnan(v)]
        return max(vals) if vals else self.k_def


class GananciaSegura:
    """k_usado a partir de un k estimado: margen hacia el lado lento, sube al instante, baja a lo
    sumo `bajada_por_s` (fraccion por segundo), y nunca sale de [k_min, k_max]."""

    def __init__(self, k_inicial, margen=0.3, bajada_por_s=0.5, k_min=1.0, k_max=200.0):
        self.margen, self.bajada, self.k_min, self.k_max = margen, bajada_por_s, k_min, k_max
        self.k_usado = min(k_max, max(k_min, k_inicial * (1 + margen)))

    def actualizar(self, k_estimado, dt_s):
        cand = min(self.k_max, max(self.k_min, k_estimado * (1 + self.margen)))
        if cand >= self.k_usado:
            self.k_usado = cand
        else:
            self.k_usado = max(cand, self.k_usado * (1 - self.bajada * dt_s))
        return self.k_usado

    def pasos_por_n(self):
        return PASOS_POR_MM_Y / self.k_usado


def verificar_factibilidad(k_secante, k_tangente, pico_n, max_dr_dt_n_s, v_max_pasos_s, recorrido_max_mm,
                           duracion_apoyo_s):
    """Con el k de la precarga: compresion esperada al pico (con el k MAS BLANDO = peor caso de
    recorrido) y velocidad de Y que exige la curva (idem). Devuelve dict con 'ok', avisos, y la
    duracion de apoyo minima para no saturar al 80 % de v_max."""
    k_blando = min(k_secante, k_tangente)
    compresion = pico_n / k_blando
    v_req = max_dr_dt_n_s / k_blando                    # mm/s
    v_max_mm = v_max_pasos_s / PASOS_POR_MM_Y
    avisos = []
    if compresion > recorrido_max_mm:
        avisos.append(f"compresion esperada {compresion:.0f} mm > recorrido maximo {recorrido_max_mm:.0f} mm")
    if v_req > 0.8 * v_max_mm:
        avisos.append(f"velocidad exigida {v_req:.0f} mm/s > 80 % de v_max ({0.8 * v_max_mm:.0f} mm/s)")
    dur_min = duracion_apoyo_s * v_req / (0.8 * v_max_mm)
    return {"ok": not avisos, "avisos": avisos, "compresion_mm": compresion, "v_req_mm_s": v_req,
            "duracion_apoyo_min_s": max(duracion_apoyo_s, dur_min), "extra_mm_sugerido": 1.5 * compresion}


if __name__ == "__main__":
    # Autoprueba con datos SINTETICOS (no valida nada fisico): resorte lineal 23 N/mm con ruido.
    rng = np.random.default_rng(0)
    est = EstimadorPrecarga(f_id_n=90.0)
    z = 0.0
    while True:
        z += 5.0 * 0.010                                  # 5 mm/s, 10 ms
        if est.agregar(z, 23.0 * z + 8.0 + rng.normal(0, 1.0)) != "seguir":
            break
    r = est.resultado()
    assert abs(r["k_tangente"] - 23.0) < 3.0 and abs(r["k_secante"] - 23.0) < 3.0, r
    blando = EstimadorPrecarga(f_id_n=90.0, z_max_mm=20.0)
    z, est_b = 0.0, None
    while est_b is None or est_b == "seguir":
        z += 0.05; est_b = blando.agregar(z, 2.4 * z + rng.normal(0, 1.0))
    assert est_b == "demasiado_blanda"

    rls = EstimadorRLS(k0=10.0)
    t = np.arange(0, 4, 0.010)
    zt = 10 * (1 - np.cos(2 * np.pi * 0.5 * t))           # 0-20 mm
    for i in range(len(t)):
        zret = zt[max(0, i - 2)]                          # la fuerza llega 20 ms tarde
        k_hat = rls.actualizar(zt[i], 30.0 * zret + rng.normal(0, 1.0))
    assert abs(k_hat - 30.0) < 3.0, k_hat

    tab = TablaKPorFuerza(k_defecto=26.4)
    zz = np.linspace(0, 30, 300); ff = 15 * zz + 0.4 * zz ** 2  # tangente 15 -> 39 N/mm
    tab.aprender_pisada(np.r_[zz, zz[::-1]], np.r_[ff, ff[::-1]])
    k_bajo, k_alto = tab.consultar(100, +1), tab.consultar(500, +1)
    assert k_alto > k_bajo, (k_bajo, k_alto)

    g = GananciaSegura(20.0, margen=0.3)
    assert abs(g.k_usado - 26.0) < 1e-9
    g.actualizar(10.0, 0.010); assert g.k_usado > 25.0      # baja despacio
    g.actualizar(40.0, 0.010); assert abs(g.k_usado - 52.0) < 1e-9   # sube al instante

    fac = verificar_factibilidad(2.4, 2.4, 578, 1100, 9000, 80, 6.15)
    assert not fac["ok"]
    print("autoprueba OK:", {k: round(v, 2) for k, v in r.items()}, f"RLS k={k_hat:.2f}",
          f"tabla k(100 N)={k_bajo:.1f} k(500 N)={k_alto:.1f}", "| 2.4 N/mm a 50 kg:", fac["avisos"])
