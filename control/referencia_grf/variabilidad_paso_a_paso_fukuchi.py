"""Variabilidad PASO A PASO (dentro de cada sujeto) de la Fz de marcha sana: Fukuchi 2018.

Objetivo: dar un numero al criterio "misma carga" = el error del simulador no supera la diferencia que hay
entre dos pasos de la MISMA persona sana. Mismos datos, filtro, umbral e inclusion que
`curva_vs_velocidad_fukuchi.py` (se reutiliza su descarga; ver alli la fuente y las decisiones).

Metricas por sujeto (todas en %BW, sobre TODA la curva de apoyo de 101 puntos, igual que nuestro RMSE):
  - rmse_paso: RMSE de cada paso contra la curva media de ese mismo sujeto -> se toma la mediana por sujeto;
  - de_punto : DE entre pasos en cada % del apoyo, promediada a lo largo del apoyo;
  - r_paso   : correlacion de cada paso con la media del sujeto (mediana por sujeto);
  - DE y CV de los picos 1 y 2 y del valle entre pasos.
Entre sujetos: RMSE de la media de cada sujeto contra la media del grupo (lo que separa a una persona de otra).
Uso: python variabilidad_paso_a_paso_fukuchi.py [carpeta_cache]
"""
import csv
import io
import os
import sys
import threading
import time
import urllib.error
import urllib.request
import zipfile
from concurrent.futures import ThreadPoolExecutor

import numpy as np

FS = 300.0
UMBRAL_N = 25.0
URL_ZIP = "https://ndownloader.figshare.com/files/68194516"
URL_INFO = "https://ndownloader.figshare.com/files/68504641"
AQUI = os.path.dirname(os.path.abspath(__file__))
CACHE = sys.argv[1] if len(sys.argv) > 1 else os.path.join(AQUI, "cache_fukuchi")
os.makedirs(CACHE, exist_ok=True)
COND = ["T01", "T02", "T03", "T05"]   # 40 %, 55 %, 70 % y 100 % de la velocidad comoda


class RangoHTTP(io.RawIOBase):
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
        for intento in range(6):
            try:
                d = urllib.request.urlopen(urllib.request.Request(self.url, headers={"Range": f"bytes={self.pos}-{fin}"})).read()
                break
            except urllib.error.HTTPError:
                if intento == 5:
                    raise
                time.sleep(2 * (intento + 1))
                self._resolver()
        b[:len(d)] = d
        self.pos += len(d)
        return len(d)


info_path = os.path.join(CACHE, "WBDSinfo.csv")
if not os.path.exists(info_path):
    urllib.request.urlretrieve(URL_INFO, info_path)
vel, grupo, masa = {}, {}, {}
with open(info_path, newline="") as f:
    for r in csv.DictReader(f):
        nm = r["FileName"]
        if "walkT" in nm and nm.endswith("grf.txt"):
            try:
                vel[nm] = float(r["GaitSpeed(m/s)"])
            except ValueError:
                continue
            grupo[nm] = r["AgeGroup"]
            masa[nm] = float(r["Mass"])


def filtro_cero_fase(x, fc=20.0, fs=FS):
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


_loc = threading.local()


def _leer_remoto(nm):
    for intento in range(4):
        try:
            if not hasattr(_loc, "zf"):
                _loc.zf = zipfile.ZipFile(io.BufferedReader(RangoHTTP(URL_ZIP), 1 << 20))
            datos = _loc.zf.read("51subjs/" + nm)
            break
        except Exception:
            if hasattr(_loc, "zf"):
                del _loc.zf
            if intento == 3:
                raise
            time.sleep(5 * (intento + 1))
    with open(os.path.join(CACHE, nm), "wb") as g:
        g.write(datos)


faltan = [nm for nm in sorted(vel) if grupo[nm] == "Young" and nm[10:13] in COND
          and (not os.path.exists(os.path.join(CACHE, nm)) or os.path.getsize(os.path.join(CACHE, nm)) == 0)]
if faltan:
    print(f"descargando {len(faltan)} archivos con 3 hilos...", flush=True)
    with ThreadPoolExecutor(3) as ex:
        list(ex.map(_leer_remoto, faltan))

curvas = {c: {} for c in COND}
vels = {c: [] for c in COND}
for nm in sorted(vel):
    sujeto, c = nm[4:6], nm[10:13]
    if c not in COND or grupo[nm] != "Young":
        continue
    d = np.loadtxt(os.path.join(CACHE, nm), skiprows=1)
    fy1, fy2 = d[:, 2], d[:, 9]
    bw = np.mean(fy1 + fy2)
    if np.std(fy1) < 10 or np.std(fy2) < 10 or not (0.85 <= bw / (masa[nm] * 9.81) <= 1.05):
        continue
    vels[c].append(vel[nm])
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
                if 0.3 <= (j - i) / FS <= 2.0:
                    seg = s[i:j]
                    curvas[c].setdefault(sujeto, []).append(
                        np.interp(np.linspace(0, 1, 101), np.linspace(0, 1, len(seg)), seg) / bw * 100)
                i = j
            i += 1


def picos(m):
    p1 = int(np.argmax(m[:50])); p2 = 50 + int(np.argmax(m[50:])); v = p1 + int(np.argmin(m[p1:p2 + 1]))
    return p1, v, p2


def q(x):
    x = np.asarray(x)
    return f"mediana {np.median(x):.3f} (p25 {np.percentile(x, 25):.3f}, p75 {np.percentile(x, 75):.3f}, p90 {np.percentile(x, 90):.3f})"


filas, lineas = [], []
for c in COND:
    if not curvas[c]:
        continue
    medias_suj = {}
    rm_s, de_s, r_s, sdp1, sdv, sdp2, cvp1, cvp2, npasos = [], [], [], [], [], [], [], [], []
    norm = {"pico": [], "rango": [], "media": [], "de": []}
    for suj, lst in curvas[c].items():
        C = np.array(lst)
        if len(C) < 5:
            continue
        m = C.mean(axis=0); medias_suj[suj] = m
        p1, v, p2 = picos(m)
        rm = np.sqrt(np.mean((C - m) ** 2, axis=1))
        rr = [np.corrcoef(ci, m)[0, 1] for ci in C]
        rm_s.append(np.median(rm)); r_s.append(np.median(rr)); de_s.append(np.mean(C.std(axis=0, ddof=1)))
        # el mismo RMSE con otras normalizaciones (2026-11-26): % del pico, % del rango, % de la media y / DE de la curva media
        norm["pico"].append(np.median(rm) / m.max() * 100); norm["rango"].append(np.median(rm) / (m.max() - m.min()) * 100)
        norm["media"].append(np.median(rm) / m.mean() * 100); norm["de"].append(np.median(rm) / m.std() * 100)
        # picos de cada paso buscados en una ventana de +-10 % alrededor del pico de la media
        P1 = np.array([ci[max(0, p1 - 10):p1 + 11].max() for ci in C])
        P2 = np.array([ci[max(0, p2 - 10):min(101, p2 + 11)].max() for ci in C])
        V = np.array([ci[max(0, v - 10):min(101, v + 11)].min() for ci in C])
        sdp1.append(P1.std(ddof=1)); sdp2.append(P2.std(ddof=1)); sdv.append(V.std(ddof=1))
        cvp1.append(P1.std(ddof=1) / P1.mean() * 100); cvp2.append(P2.std(ddof=1) / P2.mean() * 100)
        npasos.append(len(C))
    G = np.array(list(medias_suj.values())); mg = G.mean(axis=0)
    entre = np.sqrt(np.mean((G - mg) ** 2, axis=1))
    lineas += [f"{c} ({np.mean(vels[c]):.2f} m/s): {len(rm_s)} sujetos, {sum(npasos)} pasos (mediana {int(np.median(npasos))} por sujeto)",
               f"  PASO A PASO (misma persona):",
               f"    RMSE de un paso vs la media de su sujeto [%BW]: {q(rm_s)}",
               f"    DE entre pasos promediada en el apoyo [%BW]:   {q(de_s)}",
               f"    r de un paso vs la media de su sujeto:         {q(r_s)}",
               f"    mismo RMSE en % del pico de la media:          {q(norm['pico'])}",
               f"    mismo RMSE en % del rango (max-min):           {q(norm['rango'])}",
               f"    mismo RMSE en % de la media de la curva:       {q(norm['media'])}",
               f"    mismo RMSE / DE de la curva media [%]:         {q(norm['de'])}",
               f"    DE pico 1 / valle / pico 2 [%BW]: {np.median(sdp1):.2f} / {np.median(sdv):.2f} / {np.median(sdp2):.2f} (medianas)",
               f"    CV pico 1 / pico 2 [%]: {np.median(cvp1):.2f} / {np.median(cvp2):.2f} (medianas)",
               f"  ENTRE PERSONAS: RMSE de la media de un sujeto vs la media del grupo [%BW]: {q(entre)}", ""]
    filas.append([c, f"{np.mean(vels[c]):.2f}", len(rm_s), sum(npasos), f"{np.median(rm_s):.3f}", f"{np.percentile(rm_s, 75):.3f}",
                  f"{np.median(de_s):.3f}", f"{np.median(r_s):.4f}", f"{np.median(sdp1):.3f}", f"{np.median(sdv):.3f}",
                  f"{np.median(sdp2):.3f}", f"{np.median(entre):.3f}",
                  *[f"{np.median(norm[k]):.3f}" for k in ("pico", "rango", "media", "de")]])

with open(os.path.join(AQUI, "variabilidad_paso_a_paso_fukuchi.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["cond", "vel_m_s", "sujetos", "pasos", "rmse_paso_mediana_BW", "rmse_paso_p75_BW", "de_punto_mediana_BW",
                "r_paso_mediana", "de_pico1_BW", "de_valle_BW", "de_pico2_BW", "rmse_entre_sujetos_mediana_BW",
                "rmse_pct_pico", "rmse_pct_rango", "rmse_pct_media", "rmse_pct_de"])
    w.writerows(filas)
txt = "\n".join(lineas)
open(os.path.join(AQUI, "variabilidad_paso_a_paso_fukuchi.txt"), "w", encoding="utf-8").write(txt)
print(txt)
