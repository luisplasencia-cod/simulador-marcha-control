"""Cuenta muestras corruptas (errores de bit) del ADS1256 vs velocidad del reloj SPI.
Una muestra es 'mala' si |V - mediana| > 0.05 V (~28 N) con el plato en reposo. Monitor cerrado."""
import sys, time, statistics as st
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import leer_ads1256_fz as m
N = 5000
for hz in [int(x) for x in sys.argv[1:]] or [1000000, 500000, 250000, 100000]:
    m.SPI_HZ = hz
    try:
        adc = m.ADS1256()
    except Exception as e:
        print(f"{hz:>8} Hz: init falla ({e})"); continue
    v = [adc.leer_volts() for _ in range(N)]; adc.cerrar()
    med = st.median(v); mal = [x for x in v if abs(x - med) > 0.05]
    buenos = [x for x in v if abs(x - med) <= 0.05]
    print(f"{hz:>8} Hz: malas {len(mal)}/{N} ({100*len(mal)/N:.2f} %), sigma buenas={st.pstdev(buenos)*1000/1.7665:.2f} N, ejemplos(V)={[round(x,3) for x in mal[:4]]}", flush=True)
