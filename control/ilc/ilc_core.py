"""Nucleo del ILC (Iterative Learning Control), independiente de la planta y del eje.

Qué es: la ley de aprendizaje ciclo-a-ciclo sola, sin saber nada de steppers, de
fuerza en N ni de AMTI. Entra un error (referencia - medido) de un ciclo completo,
sale la correccion que se le suma a la referencia del siguiente ciclo. Lo usa
fz_ilc.py (ya escrito) y lo reusaran Fy y el eje sagital mas adelante con la
MISMA clase, solo cambiando el eje que la llama.

Ley: delta_{j+1} = Q[ delta_j + gamma * e_j(t + m) ]
  - e_j(t+m): el error se adelanta m muestras (compensa que la correccion de hoy
    actua con el retardo del lazo, no instantaneamente). m se da en muestras,
    no en ms, para no mezclar esta clase con ninguna fuente de tiempo real.
  - Q: filtro de fase cero (ventana Hanning) que evita que el aprendizaje
    amplifique ruido de alta frecuencia ciclo a ciclo (robustez del ILC, no
    rapidez de respuesta).
Parametros de diseño (gamma, ancho de Q, m): elegidos, no medidos. Los de
partida vienen de control/simulacion/rt_vs_ilc_latencia.py (GAMMA=0.5, Q con
ventana de 0.1 s) porque ahi se probaron contra la curva real; se ajustan con
el simulador real cuando haya hardware.
"""
import numpy as np


class ILCController:
    def __init__(self, n_puntos, gamma=0.5, ancho_q_muestras=None, m_adelanto=0):
        """n_puntos: muestras por ciclo. ancho_q_muestras: ventana del filtro Q
        (por defecto 10% del ciclo, como en la simulacion). m_adelanto: muestras
        que se adelanta el error antes de usarlo (0 si no se conoce la latencia
        en muestras de este ciclo; se ajusta con pruebas reales)."""
        self.n = n_puntos
        self.gamma = gamma
        self.m = int(m_adelanto)
        self.ancho_q = int(ancho_q_muestras) if ancho_q_muestras else max(1, n_puntos // 10)
        self.delta = np.zeros(n_puntos)
        self.historial_rms = []

    def _filtro_q(self, x):
        n = self.ancho_q
        w = np.hanning(2 * n + 1)
        w /= w.sum()
        pad = np.r_[x[::-1][-n:], x, x[::-1][:n]]
        return np.convolve(pad, w, "same")[n:-n]

    def actualizar(self, error_ciclo):
        """error_ciclo: array de n_puntos muestras (referencia - medido) de UN
        ciclo ya completo. Devuelve la nueva delta (correccion a sumar a la
        referencia del SIGUIENTE ciclo, mismas unidades que error_ciclo)."""
        error_ciclo = np.asarray(error_ciclo, dtype=float)
        if error_ciclo.shape[0] != self.n:
            raise ValueError(f"error_ciclo tiene {error_ciclo.shape[0]} muestras, se esperaban {self.n}")
        self.historial_rms.append(float(np.sqrt(np.mean(error_ciclo ** 2))))
        e_adel = np.r_[error_ciclo[self.m:], np.zeros(self.m)] if self.m else error_ciclo
        self.delta = self._filtro_q(self.delta + self.gamma * e_adel)
        return self.delta.copy()

    def referencia_corregida(self, referencia_base):
        """referencia_base (n_puntos) + la correccion aprendida hasta ahora."""
        referencia_base = np.asarray(referencia_base, dtype=float)
        if referencia_base.shape[0] != self.n:
            raise ValueError(f"referencia_base tiene {referencia_base.shape[0]} muestras, se esperaban {self.n}")
        return referencia_base + self.delta

    def reiniciar(self):
        """Pone la correccion aprendida en cero (ej. al cambiar de protesis:
        la rigidez cambia, lo aprendido para la anterior no vale)."""
        self.delta = np.zeros(self.n)
        self.historial_rms = []


if __name__ == "__main__":
    # Autoprueba minima (sin planta real): el error debe bajar ciclo a ciclo
    # ante una referencia fija con un sesgo constante y una planta tipo ganancia.
    rng = np.random.default_rng(0)
    n = 200
    ref = 100 * np.sin(np.linspace(0, np.pi, n)) ** 2  # forma de un pico, sin unidades reales
    ganancia_planta = 0.9  # "la planta" solo para la autoprueba: medido = (ref+delta)*ganancia
    ilc = ILCController(n, gamma=0.5)
    rms_ciclos = []
    for _ in range(15):
        medido = ilc.referencia_corregida(ref) * ganancia_planta
        error = ref - medido
        rms_ciclos.append(float(np.sqrt(np.mean(error ** 2))))
        ilc.actualizar(error)
    print("RMS por ciclo (debe decrecer y estabilizarse):", [f"{x:.3f}" for x in rms_ciclos])
    assert rms_ciclos[-1] < rms_ciclos[0] * 0.1, "el ILC no esta aprendiendo: revisar gamma/filtro"
    print("OK: autoprueba del nucleo ILC pasa (planta sintetica, no es validacion con hardware real).")
