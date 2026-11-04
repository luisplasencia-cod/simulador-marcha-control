"""ILC para Fz (eje vertical) usando el nucleo generico (ilc_core.py) + la curva
objetivo real (control/referencia_grf/) + el formato de trayectoria del firmware
actual (gait_dt_ms/gait_dx/dy/dk_steps, max 500 puntos, protocolo TRAJ_* -- ver
Codigo ESP32 MOV/.../communication.h y configurable_motion_data.h).

QUE RESUELVE: pasar de "error de Fz medido en un ciclo" a "la trayectoria de
pasos del eje vertical para el siguiente ciclo", para subirla con RUN sin tocar
el firmware (asi lo decidio Luis). Esto es ILC ciclo a ciclo, no un lazo en
tiempo real dentro del ciclo (el firmware no acepta un comando continuo).

NO RESUELTO, pendiente de hardware (marcado explicitamente, no se adivina):
1. EJE: a qué de X/Y del firmware corresponde el vertical (Fz) físico. El
   firmware no lo dice (son X/Y genéricos) y CLAUDE.md da rangos (horizontal
   587 mm, vertical 542 mm) que no bastan para distinguirlos por los límites de
   HOMING del firmware (son límites de búsqueda, no el recorrido). VERIFICAR
   FÍSICAMENTE antes de usar este módulo con hardware real -- se deja como
   parámetro (`EJE_VERTICAL`) para no hardcodear una suposición.
2. GANANCIA fuerza->paso (`PASOS_POR_N`): no hay rigidez de contacto medida
   (control/identificacion/PROTOCOLO.md, no ejecutado). Sin ella no se puede
   convertir una correccion de Fz en N a una correccion de posicion en pasos de
   forma correcta. Aqui se deja como parametro explicito con valor None por
   defecto -- el script se niega a generar una trayectoria real si no se le da
   un valor (evita inventar un numero). Se puede estimar groseramente a partir
   de la curva fuerza-deformacion informal si Luis la tiene, o medirla con el
   protocolo de identificacion cuando haya hardware.
3. Pasos/mm del eje vertical: tampoco esta en este repo (revisar husillo/motor
   real). Necesario junto con (2) para ir de N a pasos.
"""
import os
import sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ilc_core import ILCController

_REF_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "referencia_grf")
MAX_DATA_LENGTH = 500  # firmware: configurable_motion_data.h


def curva_objetivo_fz(referencia="gutenberg", n_puntos=200):
    """Fz objetivo en %BW, n_puntos muestras sobre todo el apoyo. Curvas REALES
    (ver control/referencia_grf/), no inventadas."""
    p = np.arange(n_puntos) / n_puntos
    if referencia == "gutenberg":
        d = np.genfromtxt(os.path.join(_REF_DIR, "referencia_fz_gutenberg.csv"), delimiter=",", skip_header=1)
        return np.interp(p, d[:, 0] / 100.0, d[:, 1] * 100.0)
    d = np.genfromtxt(os.path.join(_REF_DIR, "curva_vs_velocidad_fukuchi.csv"), delimiter=",", names=True)
    return np.interp(p, d["pct_apoyo"] / 100.0, d[f"{referencia}_Fz_BW_media"] * 100.0)


class ControlFzILC:
    """Une el nucleo ILC con la curva objetivo y la conversion a pasos del eje
    vertical. Uso por ciclo:
        ctrl = ControlFzILC(peso_sujeto_n=..., pasos_por_n=..., duracion_s=...)
        puntos = ctrl.siguiente_trayectoria()      # para subir al ESP32
        ... correr el ciclo real, medir Fz con el AMTI/ADS1256 ...
        ctrl.registrar_medicion(t_medido_s, fz_medido_n)   # actualiza el ILC
    """

    def __init__(self, peso_sujeto_n, pasos_por_n, duracion_s, referencia="gutenberg",
                 n_puntos=200, gamma=0.5, dt_min_ms=5):
        if pasos_por_n is None:
            raise ValueError(
                "pasos_por_n es obligatorio y NO tiene valor por defecto: depende de la rigidez de "
                "contacto (no medida, ver control/identificacion/PROTOCOLO.md) y de los pasos/mm del "
                "eje vertical (no verificados en este repo). No se inventa este numero.")
        self.peso_n = peso_sujeto_n
        self.pasos_por_n = pasos_por_n
        self.duracion_s = duracion_s
        self.n = n_puntos
        self.dt_ms = max(dt_min_ms, int(round(duracion_s * 1000 / n_puntos)))
        self.ref_bw = curva_objetivo_fz(referencia, n_puntos)  # %BW
        self.ref_n = self.ref_bw / 100.0 * self.peso_n
        self.ilc = ILCController(n_puntos, gamma=gamma)
        self._t_ultimo_ciclo = None
        self._fz_ultimo_ciclo = None

    def siguiente_trayectoria(self):
        """Devuelve (dt_ms, dz_pasos): arrays listos para TRAJ_POINT, con la
        correccion ILC ya sumada a la referencia de fuerza y convertida a pasos
        relativos del eje vertical. dz_pasos es DELTA entre muestras (lo que
        pide el firmware), no posicion absoluta."""
        if self.n > MAX_DATA_LENGTH:
            raise ValueError(f"{self.n} puntos > MAX_DATA_LENGTH={MAX_DATA_LENGTH} del firmware")
        f_obj_n = self.ilc.referencia_corregida(self.ref_n)
        pasos_abs = np.round(f_obj_n * self.pasos_por_n).astype(int)
        dz = np.diff(np.r_[0, pasos_abs])
        dt = np.full(self.n, self.dt_ms, dtype=int)
        return dt, dz

    def registrar_medicion(self, t_medido_s, fz_medido_n):
        """t_medido_s, fz_medido_n: arrays del ciclo que acaba de correr (del
        AMTI/ADS1256, timestamps propios, no necesariamente a dt_ms exacto).
        Interpola a la malla del ILC y actualiza delta para el siguiente ciclo."""
        t_malla = np.linspace(0, self.duracion_s, self.n, endpoint=False)
        fz_interp = np.interp(t_malla, t_medido_s, fz_medido_n)
        error_n = self.ref_n - fz_interp
        self.ilc.actualizar(error_n)
        return float(self.ilc.historial_rms[-1])


if __name__ == "__main__":
    # Autoprueba SOLO del cableado (curva real + nucleo + conversion a pasos),
    # con una planta sintetica (ganancia pura) -- NO valida pasos_por_n real.
    peso_n, pasos_por_n, duracion_s = 850.0, 50.0, 3.69  # pasos_por_n de EJEMPLO, no medido
    ctrl = ControlFzILC(peso_n, pasos_por_n, duracion_s, n_puntos=200)
    t_malla = np.linspace(0, duracion_s, 200, endpoint=False)
    for ciclo in range(5):
        dt, dz = ctrl.siguiente_trayectoria()
        assert len(dt) == len(dz) == 200
        fz_medido = np.cumsum(dz) / pasos_por_n * 0.9  # planta sintetica: 90% de la fuerza comandada
        rms = ctrl.registrar_medicion(t_malla, fz_medido)
        print(f"ciclo {ciclo}: RMS error = {rms:.2f} N")
    print("OK: cableado curva->ILC->pasos funciona. pasos_por_n es de EJEMPLO, no medido -- no usar en hardware real.")
