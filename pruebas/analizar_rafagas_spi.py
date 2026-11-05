"""Captura N muestras, cuenta rafagas de muestras malas (|V-mediana|>0.05 V) y prueba filtros
CAUSALES sobre los datos crudos: mediana de 3, mediana de 5. Monitor cerrado."""
import sys, statistics as st
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import leer_ads1256_fz as m
N = 30000
adc = m.ADS1256(); v = [adc.leer_volts() for _ in range(N)]; adc.cerrar()
med = st.median(v); K = 1000 / 1.7665
mala = [abs(x - med) > 0.05 for x in v]
runs = []; c = 0
for b in mala:
    if b: c += 1
    elif c: runs.append(c); c = 0
if c: runs.append(c)
print(f"{N} muestras, {sum(mala)} malas ({100*sum(mala)/N:.2f} %), rafagas={len(runs)}, longitud max={max(runs) if runs else 0}, "
      f"aisladas(len1)={sum(1 for r in runs if r==1)}, len2={sum(1 for r in runs if r==2)}, >=3={sum(1 for r in runs if r>=3)}")
ok = [x for x, b in zip(v, mala) if not b]
print(f"sigma de las buenas = {st.pstdev(ok)*K:.2f} N")
for w in (3, 5):
    f = [st.median(v[max(0, i-w+1):i+1]) for i in range(w-1, N)]
    peor = max(abs(x - med) for x in f) * K
    resid = sum(1 for x in f if abs(x - med) > 0.05)
    print(f"mediana causal de {w}: retardo {(w-1)/2:.0f} ms, muestras aun malas {resid}/{len(f)}, peor desviacion {peor:.1f} N, sigma={st.pstdev(f)*K:.2f} N")
print(f"sin filtrar: peor desviacion {max(abs(x-med) for x in v)*K:.0f} N")
