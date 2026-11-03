"""Curva de Fz (fuerza vertical) vs velocidad de marcha, incluyendo marcha LENTA: Fukuchi 2018.

Fuente: Fukuchi CA, Fukuchi RK, Duarte M. PeerJ 6:e4640 (2018), DOI 10.7717/peerj.4640. Datos Figshare (CC BY 4.0),
DOI 10.6084/m9.figshare.5722711: WBDSascii.zip (archivo 68194516) y WBDSinfo.csv (68504641).
Verificado en el articulo: cinta instrumentada de dos bandas, GRF a 300 Hz, 8 velocidades de cinta (T01..T08 =
40, 55, 70, 85, 100, 115, 130 y 145 % de la velocidad comoda adimensional); archivos de cinta con 15 columnas
(tiempo + Fx,Fy,Fz,COPx,COPy,COPz,Ty de cada banda). La velocidad de cada prueba (m/s) viene en WBDSinfo.csv.
Verificado en los datos: la fuerza VERTICAL es Fy (la suma de las dos bandas ~ peso corporal).

PROCESAMIENTO (decisiones propias, documentadas):
  - filtro pasa-bajos Butterworth 2.o orden de fase cero, 20 Hz (el mismo que usa Gutenberg);
  - apoyo de cada banda = Fy filtrada >= 25 N (mismo umbral que Gutenberg); se aceptan apoyos de 0.3 a 2.0 s;
  - normalizacion por la fuerza vertical media TOTAL (suma de las dos bandas) de la prueba: en marcha estable
    equivale al peso corporal y evita depender de la tara de la cinta (en el sujeto 1 la suma da ~7 % menos que masa x g);
  - cada apoyo se lleva a 101 puntos (0-100 %); se promedia por sujeto y luego entre sujetos.
Uso: python curva_vs_velocidad_fukuchi.py [carpeta_cache]
"""
import csv
import io
import os
import statistics as st
import sys
import urllib.error
import urllib.request
import zipfile

import numpy as np

FS = 300.0
UMBRAL_N = 25.0
URL_ZIP = "https://ndownloader.figshare.com/files/68194516"
URL_INFO = "https://ndownloader.figshare.com/files/68504641"
AQUI = os.path.dirname(os.path.abspath(__file__))
CACHE = sys.argv[1] if len(sys.argv) > 1 else os.path.join(AQUI, "cache_fukuchi")
os.makedirs(CACHE, exist_ok=True)


class RangoHTTP(io.RawIOBase):
    """Archivo remoto de solo lectura por rangos HTTP (abre un ZIP de 687 MB sin bajarlo entero).
    La URL firmada de Figshare/S3 caduca a los pocos minutos: ante un 403 se vuelve a resolver y se reintenta."""
    def __init__(self, url):
        self.orig, self.pos = url, 0
        self._resolver()

    def _resolver(self):
        r = urllib.request.urlopen(urllib.request.Request(self.orig, headers={"Range": "bytes=0-0"}))
        self.url, self.n = r.geturl(), int(r.headers["Content-Range"].split("/")[1])

    def seekable(self): return True
    def readable(self): return True
    def tell(self): return self.pos
    def seek(self, o, w=0):
        self.pos = o if w == 0 else self.pos + o if w == 1 else self.n + o
        return self.pos

    def readinto(self, b):
        if self.pos >= self.n:
            return 0
        fin = min(self.pos + len(b), self.n) - 1
        for intento in range(3):
            try:
                d = urllib.request.urlopen(urllib.request.Request(self.url, headers={"Range": f"bytes={self.pos}-{fin}"})).read()
                break
            except urllib.error.HTTPError:
                if intento == 2:
                    raise
                self._resolver()
        b[:len(d)] = d
        self.pos += len(d)
        return len(d)


info_path = os.path.join(CACHE, "WBDSinfo.csv")
if not os.path.exists(info_path):
    urllib.request.urlretrieve(URL_INFO, info_path)
vel, grupo = {}, {}
with open(info_path, newline="") as f:
    for r in csv.DictReader(f):
        nm = r["FileName"]
        if "walkT" in nm and nm.endswith("grf.txt"):
            try:
                vel[nm] = float(r["GaitSpeed(m/s)"])
            except ValueError:
                continue
            grupo[nm] = r["AgeGroup"]

def filtro_cero_fase(x, fc=20.0, fs=FS):
    """Butterworth 2.o orden pasa-bajos (bilineal), aplicado hacia adelante y hacia atras (fase cero), con relleno por reflexion."""
    w = np.tan(np.pi * fc / fs); k = np.sqrt(2) * w; n = 1.0 / (1 + k + w * w)
    b0 = w * w * n; b1 = 2 * b0; b2 = b0; a1 = 2 * (w * w - 1) * n; a2 = (1 - k + w * w) * n

    def una_pasada(y):
        out = np.empty_like(y); x1 = x2 = y1 = y2 = y[0]
        for i, v in enumerate(y):
            o = b0 * v + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2
            out[i] = o; x2, x1, y2, y1 = x1, v, y1, o
        return out

    pad = 150
    z = np.r_[2 * x[0] - x[pad:0:-1], x, 2 * x[-1] - x[-2:-pad - 2:-1]]
    z = una_pasada(z)[::-1]
    z = una_pasada(z)[::-1]
    return z[pad:-pad]


zf = None
cond = [f"T{c:02d}" for c in range(1, 9)]
curvas = {c: {} for c in cond}       # cond -> sujeto -> lista de curvas (101,)
duras = {c: {} for c in cond}        # cond -> sujeto -> lista de duraciones (s)
vels = {c: {} for c in cond}
for nm in sorted(vel):
    sujeto = nm[4:6]
    c = nm[10:13]
    ruta = os.path.join(CACHE, nm)
    if not os.path.exists(ruta) or os.path.getsize(ruta) == 0:
        if zf is None:
            zf = zipfile.ZipFile(io.BufferedReader(RangoHTTP(URL_ZIP), 1 << 20))
        datos = zf.read("51subjs/" + nm)      # primero se lee completo y recien despues se escribe
        with open(ruta, "wb") as g:
            g.write(datos)
    d = np.loadtxt(ruta, skiprows=1)
    fy1, fy2 = d[:, 2], d[:, 9]
    bw = np.mean(fy1 + fy2)
    for fy in (fy1, fy2):
        s = filtro_cero_fase(fy)
        on = s >= UMBRAL_N
        i = 1
        while i < len(s) - 1:
            if on[i] and not on[i - 1]:
                j = i
                while j < len(s) - 1 and on[j]:
                    j += 1
                if on[j]:
                    break
                dur = (j - i) / FS
                if 0.3 <= dur <= 2.0:
                    seg = s[i:j]
                    curvas[c].setdefault(sujeto, []).append(np.interp(np.linspace(0, 1, 101), np.linspace(0, 1, len(seg)), seg) / bw)
                    duras[c].setdefault(sujeto, []).append(dur)
                i = j
            i += 1
    vels[c].setdefault(sujeto, []).append(vel[nm])

salida_csv = os.path.join(AQUI, "curva_vs_velocidad_fukuchi.csv")
resumen = []
medias = {}
for c in cond:
    suj = [np.mean(v, axis=0) for v in curvas[c].values()]
    if not suj:
        continue
    m = np.mean(suj, axis=0) * 100
    medias[c] = m
    sd = np.std(suj, axis=0, ddof=1) * 100
    pk1 = int(np.argmax(m[:50])); pk2 = 50 + int(np.argmax(m[50:])); vl = pk1 + int(np.argmin(m[pk1:pk2]))
    dur = [np.mean(v) for v in duras[c].values()]
    sp = [np.mean(v) for v in vels[c].values()]
    resumen.append(f"{c}: velocidad {np.mean(sp):.2f} m/s (DE {np.std(sp, ddof=1):.2f}); sujetos={len(suj)}; apoyos={sum(len(v) for v in curvas[c].values())}; "
                   f"apoyo {np.mean(dur):.3f} s (DE {np.std(dur, ddof=1):.3f}); 1er pico {m[pk1]:.1f} %BW ({pk1} %), valle {m[vl]:.1f} %BW ({vl} %), "
                   f"2do pico {m[pk2]:.1f} %BW ({pk2} %); DE entre sujetos en picos {sd[pk1]:.1f}/{sd[pk2]:.1f}")
with open(salida_csv, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["pct_apoyo"] + [f"{c}_Fz_BW_media" for c in medias])
    for i in range(101):
        w.writerow([i] + [f"{medias[c][i] / 100:.5f}" for c in medias])
txt = "\n".join(resumen)
open(os.path.join(AQUI, "resumen_velocidad_fukuchi.txt"), "w").write(txt + "\n")
print(txt)
