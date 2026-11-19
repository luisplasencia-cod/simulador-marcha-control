"""Filtro de muesca (notch) para Fz y limitador de aceleracion para SET_VEL -- PROPUESTA, NO conectada al lazo.

Contexto: reportes/2026-11-19_propuesta_notch_fz_6_8hz.md (oscilacion de 6-8 Hz en la escalera 50-90 kg).
Pensado para correr a la tasa del lazo (fs = 100 Hz, una muestra = la mediana de bloque que entrega
LectorFzUART.leer_n() cada 10 ms). Sin dependencias fuera de numpy (scipy solo en la autoprueba, si existe).

Reglas si algun dia se conecta (ver el reporte):
  - Filtrar SOLO la senal que entra al termino proporcional (tiempo real). El tope de fuerza, el detector de
    saltos y el registro deben seguir usando la Fz SIN filtrar (si no, el filtro esconde lo que protege).
  - El error del ILC se puede filtrar entre ciclos con fase cero (filtfilt): ahi el notch no cuesta retardo.
  - Llamar a reset(f_actual) al empezar la fase cerrada para no meter un transitorio de arranque.

Uso:
    nf = FiltroNotchFz(secciones=[(7.0, 3.5)], fs_hz=100.0)
    nf.reset(f_med_inicial)
    f_para_p = nf.filtrar(f_med)          # una vez por ciclo de control
Autoprueba:  python control/filtro_fz/notch_fz.py
"""
import math

import numpy as np


def coef_notch(f0_hz, q, fs_hz):
    """Biquad notch digital (misma definicion que scipy.signal.iirnotch): ganancia 1 en DC y en Nyquist,
    cero exacto en f0, ancho de banda a -3 dB = f0/q exacto. Devuelve (b, a) con a[0] = 1."""
    if not 0 < f0_hz < fs_hz / 2:
        raise ValueError(f"f0 = {f0_hz} Hz fuera de (0, fs/2 = {fs_hz / 2} Hz)")
    if q <= 0:
        raise ValueError("q debe ser > 0")
    w0 = 2 * math.pi * f0_hz / fs_hz
    bw = w0 / q
    g = 1.0 / (1.0 + math.tan(bw / 2))
    c = math.cos(w0)
    b = g * np.array([1.0, -2 * c, 1.0])
    a = np.array([1.0, -2 * g * c, 2 * g - 1])
    return b, a


class FiltroNotchFz:
    """Cascada de notches de 2.o orden, causal, muestra a muestra (forma directa II transpuesta)."""

    def __init__(self, secciones=((7.0, 3.5),), fs_hz=100.0):
        self.fs_hz = fs_hz
        self.secciones = [tuple(s) for s in secciones]
        self._coef = [coef_notch(f0, q, fs_hz) for f0, q in self.secciones]
        self._z = [[0.0, 0.0] for _ in self._coef]

    def reset(self, x0=0.0):
        """Estado de regimen para entrada constante x0 (salida = x0, sin transitorio)."""
        for i, (b, a) in enumerate(self._coef):
            z2 = (b[2] - a[2]) * x0
            z1 = (b[1] - a[1]) * x0 + z2
            self._z[i] = [z1, z2]

    def filtrar(self, x):
        y = float(x)
        for (b, a), z in zip(self._coef, self._z):
            u = y
            y = b[0] * u + z[0]
            z[0] = b[1] * u - a[1] * y + z[1]
            z[1] = b[2] * u - a[2] * y
        return y

    def respuesta(self, f_hz):
        """Respuesta en frecuencia compleja H(e^jw) de la cascada en las frecuencias f_hz (array)."""
        f = np.atleast_1d(np.asarray(f_hz, dtype=float))
        zinv = np.exp(-1j * 2 * np.pi * f / self.fs_hz)
        h = np.ones_like(zinv)
        for b, a in self._coef:
            h *= (b[0] + b[1] * zinv + b[2] * zinv ** 2) / (a[0] + a[1] * zinv + a[2] * zinv ** 2)
        return h

    def retardo_equivalente_ms(self, f_hz):
        """Retardo puro que produciria la misma perdida de fase en f_hz: -fase / (2*pi*f), en ms."""
        f = np.atleast_1d(np.asarray(f_hz, dtype=float))
        return -np.unwrap(np.angle(self.respuesta(f))) / (2 * np.pi * f) * 1000


class LimitadorAceleracion:
    """Limita el cambio de la velocidad ordenada entre ciclos: |v[k] - v[k-1]| <= a_max * dt.
    No lineal: sin retardo mientras no satura; cuando satura agrega atraso que depende de la amplitud
    (puede CREAR un ciclo limite en lazo cerrado) -- ver el reporte antes de usarlo."""

    def __init__(self, a_max_pasos_s2, dt_s=0.010, v0=0.0):
        if a_max_pasos_s2 <= 0:
            raise ValueError("a_max debe ser > 0")
        self.dv_max = a_max_pasos_s2 * dt_s
        self.v = float(v0)
        self.saturo = 0

    def limitar(self, v_pedida):
        dv = v_pedida - self.v
        if abs(dv) > self.dv_max:
            dv = math.copysign(self.dv_max, dv)
            self.saturo += 1
        self.v += dv
        return self.v


def _autoprueba():
    import os
    fs = 100.0
    ok = True

    def chk(cond, msg):
        nonlocal ok
        print(("  OK   " if cond else "  FALLA ") + msg)
        ok &= bool(cond)

    print("== Autoprueba notch_fz.py")
    nf = FiltroNotchFz([(7.0, 3.5)], fs)
    chk(abs(abs(nf.respuesta(1e-6)[0]) - 1) < 1e-9, "ganancia en DC = 1")
    chk(20 * np.log10(abs(nf.respuesta(7.0)[0]) + 1e-15) < -100, "cero en 7.0 Hz (< -100 dB)")
    try:
        from scipy.signal import iirnotch, freqz
        bs, as_ = iirnotch(7.0, 3.5, fs=fs)
        _, hs = freqz(bs, as_, worN=[1.0, 3.0, 6.4, 8.3], fs=fs)
        hm = nf.respuesta([1.0, 3.0, 6.4, 8.3])
        chk(np.max(np.abs(hs - hm)) < 1e-9, "coincide con scipy.signal.iirnotch (misma definicion de Q)")
    except ImportError:
        print("  (scipy no disponible: se salta la comparacion)")

    # senal: curva de Gutenberg 90 kg a x10 (apoyo 6.15 s) + 31 N rms a 7.3 Hz (lo medido a 90 kg)
    ref = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "referencia_grf", "referencia_fz_gutenberg.csv")
    d = np.genfromtxt(ref, delimiter=",", skip_header=1)
    t = np.arange(0, 6.15, 1 / fs)
    curva = np.interp(t / 6.15 * 100, d[:, 0], d[:, 1]) * 90 * 9.81
    osc = 31 * math.sqrt(2) * np.sin(2 * np.pi * 7.3 * t)
    nf.reset(curva[0])
    y = np.array([nf.filtrar(v) for v in curva + osc])
    nf.reset(curva[0])
    y0 = np.array([nf.filtrar(v) for v in curva])
    residual = y - y0
    m = t > 1.0
    rms_res = np.sqrt(np.mean(residual[m] ** 2))
    chk(rms_res < 31 * 0.35, f"7.3 Hz de 31 N rms -> {rms_res:.1f} N rms residual (lineal: superposicion exacta)")
    err = np.max(np.abs(y0 - curva))
    print(f"       error agregado sobre la curva sin oscilacion: max {err:.1f} N (pico {curva.max():.0f} N)")

    nf.reset(500.0)
    chk(abs(nf.filtrar(500.0) - 500.0) < 1e-9, "reset(x0): sin transitorio con entrada constante")

    lim = LimitadorAceleracion(12000, 0.010)
    v = [lim.limitar(9000) for _ in range(10)]
    chk(abs(v[0] - 120) < 1e-9 and abs(v[-1] - 1200) < 1e-9, "limitador: 120 pasos/s por ciclo a 12000 pasos/s^2")
    print("RESULTADO:", "TODO OK" if ok else "HAY FALLAS")
    return ok


if __name__ == "__main__":
    raise SystemExit(0 if _autoprueba() else 1)
