"""Duracion de la fase de apoyo (s) en marcha sana, de la MISMA base y filtro que la curva de Fz.

Fuente: Gutenberg Gait Database (Horst et al. 2021, DOI 10.1038/s41597-021-01014-6), archivo
GRF_F_V_RAW_right.csv. Verificado en el articulo (Metodos): las senales se submuestrearon a 250 Hz y
para los datos RAW el apoyo se recorto con un umbral de Fz = 25 N; cada fila = una pisada con sus
muestras de apoyo (el resto del vector es NaN).
=> duracion del apoyo = (numero de muestras no-NaN) / 250 Hz (resolucion 4 ms; apoyo definido con Fz >= 25 N).
Mismo filtro que la curva: SPEED=2 (autoseleccionada), sin plantilla ortopedica, todos HC.
Procedimiento: media por sujeto y luego media +- DE entre sujetos.
Uso: python duracion_apoyo_gutenberg.py [carpeta_con_csv]  (descarga lo que falte de Figshare)
"""
import csv
import os
import statistics as st
import sys
import urllib.request

FS = 250.0
URL = {"GRF_F_V_RAW_right.csv": 26576491, "GRF_metadata.csv": 26576495, "GRF_walking_speed.csv": 26576497}
carpeta = sys.argv[1] if len(sys.argv) > 1 else "datos_gutenberg"
os.makedirs(carpeta, exist_ok=True)
for n, fid in URL.items():
    r = os.path.join(carpeta, n)
    if not os.path.exists(r):
        urllib.request.urlretrieve(f"https://ndownloader.figshare.com/files/{fid}", r)

meta = {}
with open(os.path.join(carpeta, "GRF_metadata.csv")) as f:
    for r in csv.DictReader(f):
        meta[(r["DATASET_ID"], r["SUBJECT_ID"], r["SESSION_ID"])] = r
vel = {}
with open(os.path.join(carpeta, "GRF_walking_speed.csv")) as f:
    for r in csv.DictReader(f):
        v = float(r["WALKING_SPEED"]) if r["WALKING_SPEED"] not in ("", "NaN") else float("nan")
        if v == v:
            vel[(r["DATASET_ID"], r["SUBJECT_ID"], r["SESSION_ID"], r["TRIAL_ID"])] = v

dur, spd, trials = {}, {}, []
with open(os.path.join(carpeta, "GRF_F_V_RAW_right.csv")) as f:
    rd = csv.reader(f)
    next(rd)
    for fila in rd:
        d, s, ses, tr = fila[:4]
        m = meta.get((d, s, ses))
        if not m or m["CLASS_LABEL"] != "HC" or m["SPEED"] != "2" or m["ORTHOPEDIC_INSOLE"] != "0":
            continue
        n = sum(1 for v in fila[4:] if v not in ("", "NaN", "nan"))
        if n < 30:
            continue
        dur.setdefault((d, s), []).append(n / FS)
        trials.append(n / FS)
        if (d, s, ses, tr) in vel:
            spd.setdefault((d, s), []).append(vel[(d, s, ses, tr)])

por_sujeto = [st.mean(v) for v in dur.values()]
vs = [st.mean(v) for v in spd.values()]
print(f"sujetos={len(por_sujeto)}  pisadas={len(trials)}")
print(f"duracion del apoyo por sujeto: media {st.mean(por_sujeto):.3f} s, DE entre sujetos {st.stdev(por_sujeto):.3f} s, "
      f"rango {min(por_sujeto):.3f}-{max(por_sujeto):.3f} s")
q = sorted(trials)
print(f"por pisada: mediana {st.median(trials):.3f} s, p5 {q[int(.05*len(q))]:.3f}, p95 {q[int(.95*len(q))]:.3f}")
print(f"velocidad de marcha (sujetos con dato, n={len(vs)}): {st.mean(vs):.2f} +- {st.stdev(vs):.2f} m/s")
M = st.mean(por_sujeto)
print(f"x6 (factor confirmado por Luis): apoyo = {6*M:.2f} s (rango entre sujetos {6*min(por_sujeto):.2f}-{6*max(por_sujeto):.2f} s)")
