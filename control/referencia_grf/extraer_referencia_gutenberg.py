"""Curva de referencia de Fz (fuerza vertical) para el control: Gutenberg Gait Database.

Fuente: Horst F, Slijepcevic D, Simak M, Schollhorn WI. Sci Data 8:232 (2021),
DOI 10.1038/s41597-021-01014-6. Datos Figshare (CC0), coleccion 10.6084/m9.figshare.c.5311538.
Verificado en el articulo: F_V_PRO = fuerza vertical procesada, en multiplos del peso corporal,
normalizada a 101 puntos = 100 % del apoyo; marcha nivelada a velocidad autoseleccionada.
Columnas de metadata (tabla 4 del articulo): SPEED 1=lenta 2=autoseleccionada 3=rapida;
ORTHOPEDIC_INSOLE 0=sin plantilla; SHOD_CONDITION 0=descalzo 1=zapato normal 2=ortopedico.

Procedimiento (sin ajustes manuales): filtro HC (todos los de la base son sanos), SPEED y plantilla
configurables; promedio por SUJETO (todas sus pisadas) y luego media +- DE ENTRE sujetos.

Uso:  python extraer_referencia_gutenberg.py [carpeta_con_csv] [clase_velocidad 1|2|3]   (si faltan, se descargan de Figshare)
"""
import csv
import os
import statistics as st
import sys
import urllib.request

URL = {"GRF_F_V_PRO_right.csv": 26576493, "GRF_metadata.csv": 26576495, "GRF_walking_speed.csv": 26576497}
carpeta = sys.argv[1] if len(sys.argv) > 1 else "datos_gutenberg"
CLASE = sys.argv[2] if len(sys.argv) > 2 else "2"   # 1=lenta, 2=autoseleccionada (por defecto), 3=rapida
os.makedirs(carpeta, exist_ok=True)
for nombre, fid in URL.items():
    ruta = os.path.join(carpeta, nombre)
    if not os.path.exists(ruta):
        urllib.request.urlretrieve(f"https://ndownloader.figshare.com/files/{fid}", ruta)

meta = {}
with open(os.path.join(carpeta, "GRF_metadata.csv")) as f:
    for r in csv.DictReader(f):
        meta[(r["DATASET_ID"], r["SUBJECT_ID"], r["SESSION_ID"])] = r

vel = {}
with open(os.path.join(carpeta, "GRF_walking_speed.csv")) as f:
    for r in csv.DictReader(f):
        try:
            v = float(r["WALKING_SPEED"])
            if v == v:  # descarta NaN (velocidad no medida en datasets 6, 8 y 10)
                vel[(r["DATASET_ID"], r["SUBJECT_ID"], r["SESSION_ID"], r["TRIAL_ID"])] = v
        except ValueError:
            pass

SPEED_CLASE, INSOLE = CLASE, "0"   # clase de velocidad elegida, sin plantilla ortopedica
por_sujeto, vels, sujeto_info = {}, {}, {}
with open(os.path.join(carpeta, "GRF_F_V_PRO_right.csv")) as f:
    rd = csv.reader(f)
    cab = next(rd)
    for fila in rd:
        d, s, ses, tr = fila[:4]
        m = meta.get((d, s, ses))
        if not m or m["CLASS_LABEL"] != "HC" or m["SPEED"] != SPEED_CLASE or m["ORTHOPEDIC_INSOLE"] != INSOLE:
            continue
        try:
            y = [float(v) for v in fila[4:]]
        except ValueError:
            continue
        if len(y) != 101 or any(v != v for v in y):
            continue
        k = (d, s)
        por_sujeto.setdefault(k, []).append(y)
        sujeto_info[k] = (float(m["BODY_MASS"]) if m["BODY_MASS"] not in ("", "NaN") else None)
        if (d, s, ses, tr) in vel:
            vels.setdefault(k, []).append(vel[(d, s, ses, tr)])

if not por_sujeto:
    sys.exit(f"Sin datos para SPEED={CLASE}: en esta base los sanos solo estan en la clase 2 (autoseleccionada).")
medias = [[st.mean(col) for col in zip(*ys)] for ys in por_sujeto.values()]
n = len(medias)
media = [st.mean(c) for c in zip(*medias)]
de = [st.stdev(c) for c in zip(*medias)]
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "referencia_fz_gutenberg.csv" if CLASE == "2" else f"referencia_fz_gutenberg_speed{CLASE}.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["pct_apoyo", "Fz_BW_media", "Fz_BW_DE_entre_sujetos"])
    for i in range(101):
        w.writerow([i, f"{media[i]:.5f}", f"{de[i]:.5f}"])

pk1 = max(range(0, 50), key=lambda i: media[i]); pk2 = max(range(50, 101), key=lambda i: media[i])
vl = min(range(pk1, pk2), key=lambda i: media[i])
vm = [st.mean(v) for v in vels.values()]
print(f"sujetos={n}  pisadas={sum(len(v) for v in por_sujeto.values())}  filtro: SPEED={SPEED_CLASE}, sin plantilla ortopedica")
print(f"velocidad de marcha por sujeto: media {st.mean(vm):.2f} m/s, DE {st.stdev(vm):.2f}, rango {min(vm):.2f}-{max(vm):.2f} (n={len(vm)} con dato)")
print(f"1er pico {media[pk1]*100:.1f} %BW al {pk1} % del apoyo | valle {media[vl]*100:.1f} %BW al {vl} % | 2do pico {media[pk2]*100:.1f} %BW al {pk2} %")
print(f"DE entre sujetos en picos: {de[pk1]*100:.1f} y {de[pk2]*100:.1f} %BW | Fz(0 %)={media[0]*100:.1f} %BW, Fz(100 %)={media[100]*100:.1f} %BW")
