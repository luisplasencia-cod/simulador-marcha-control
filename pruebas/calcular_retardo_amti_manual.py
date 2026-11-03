"""Retardo del amplificador AMTI Gen 5 (salida analogica) calculado desde sus especificaciones.

FUENTE (manual en referencias/amti_manual/AMTI_Gen5_User_Manual.pdf):
  - p.55, sec. 10 "Technical Specifications": filtro anti-aliasing 1000 Hz pasa-bajos Butterworth de 2 polos;
    filtro de reconstruccion de la salida analogica 1000 Hz pasa-bajos Butterworth de 3 polos; DAC 16 bit.
  - p.12, sec. 2.5: "The analog output amplifier provides continuous output with a 2 kHz refresh rate".
  - p.12, sec. 2.1: sobremuestreo y procesamiento digital de senal (SIN dar su retardo).
METODO: retardo de grupo a baja frecuencia de cada filtro (derivada numerica de la fase de los polos de
Butterworth) + retardo medio de un retenedor de orden cero a 2 kHz (medio periodo). El retardo del
sobremuestreo/DSP interno NO esta en el manual -> NO se incluye: el resultado es una COTA INFERIOR.
"""
import numpy as np


def butter_polos(n, fc):
    wc = 2 * np.pi * fc
    k = np.arange(1, n + 1)
    return wc * np.exp(1j * np.pi * (2 * k + n - 1) / (2 * n))


def retardo_grupo(n, fc, f):
    """Retardo de grupo [s] de un Butterworth de n polos y frecuencia de corte fc, a la frecuencia f [Hz]."""
    p = butter_polos(n, fc)
    h = lambda w: np.prod(1.0 / (1j * w - p))
    w, dw = 2 * np.pi * f, 1e-3
    fase = lambda w_: np.unwrap([np.angle(h(w_ - dw)), np.angle(h(w_ + dw))])
    ph = fase(w)
    return -(ph[1] - ph[0]) / (2 * dw)


if __name__ == "__main__":
    FC = 1000.0
    f_dac = 2000.0
    print("Retardo de grupo [ms] (Butterworth 1 kHz) a distintas frecuencias de la senal:")
    print(" f [Hz] | 2 polos (anti-aliasing) | 3 polos (reconstruccion)")
    for f in (1, 10, 50, 100, 200):
        print(f" {f:6d} | {retardo_grupo(2, FC, f)*1e3:23.4f} | {retardo_grupo(3, FC, f)*1e3:24.4f}")
    aa, rec = retardo_grupo(2, FC, 1) * 1e3, retardo_grupo(3, FC, 1) * 1e3
    print(f"\nAnalitico (DC): 2 polos = sqrt(2)/wc = {np.sqrt(2)/(2*np.pi*FC)*1e3:.4f} ms ; 3 polos = 2/wc = {2/(2*np.pi*FC)*1e3:.4f} ms")
    print(f"Retenedor DAC 2 kHz: medio = {0.5/f_dac*1e3:.3f} ms (rango 0 a {1/f_dac*1e3:.3f} ms)")
    tot = aa + rec + 0.5 / f_dac * 1e3
    print(f"\nCOTA INFERIOR del retardo analogico del AMTI (sin sobremuestreo/DSP interno, no especificado) = {tot:.2f} ms "
          f"(= {aa:.3f} + {rec:.3f} + {0.5/f_dac*1e3:.3f})")
