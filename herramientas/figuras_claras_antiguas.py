#!/usr/bin/env python3
"""Regenera con titulos/ejes/leyendas en espanol claro (sufijo _claro.png) figuras antiguas (11-05, 11-10, 11-18)
a partir de los CSV que SI estan en el repo. Las originales no se tocan. Uso: python3 herramientas/figuras_claras_antiguas.py"""
import os, sys, csv
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
R = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RES = os.path.join(R, "control", "identificacion", "resultados")
FIG = os.path.join(R, "reportes", "figuras")
sys.path.insert(0, os.path.join(R, "control", "identificacion"))
from ajuste_k import k_por_bandas

NOTA_ENS = "Desplazamiento ordenado = lo que se le pidió al motor (no hay sensor que lo mida)."
FASES = {"base": "reposo", "aprox": "aproximación rápida", "aprox_mov": "aproximación rápida", "medio": "tramo medio (1 mm)",
         "medio_mov": "tramo medio (1 mm)", "fino": "bajada fina (pasos pequeños)", "fino_mov": "bajada fina (pasos pequeños)",
         "sube": "subida (descarga)", "adc_recupera": "recuperación del sensor"}
COL = {"aproximación rápida": "gray", "tramo medio (1 mm)": "tab:green", "bajada fina (pasos pequeños)": "tab:blue", "subida (descarga)": "tab:red"}


def guardar(fig, ruta):
    fig.savefig(ruta, dpi=110, facecolor="white"); plt.close(fig); print("ok", ruta)


def claro(nombre):
    return os.path.join(FIG, nombre.replace(".png", "_claro.png"))


def leerA(f):
    cab, t, fase, mm, F = "", [], [], [], []
    for l in open(f):
        if l.startswith("# angulo"): cab = l[2:].strip()
        elif l.startswith("#") or l.startswith("t_s"): continue
        else:
            p = l.strip().split(",")
            if len(p) == 4:
                t.append(float(p[0])); fase.append(FASES.get(p[1], p[1])); mm.append(float(p[2])); F.append(float(p[3]))
    return cab, np.array(t), np.array(fase), np.array(mm), np.array(F)


def fig_ensayoA(csv_nombre, titulo, salida, quedan=None):
    cab, t, fase, mm, F = leerA(os.path.join(RES, csv_nombre))
    fig, (a, b) = plt.subplots(1, 2, figsize=(13, 5.6), facecolor="white")
    a.plot(t, F, "k", lw=.8)
    a.set(xlabel="Tiempo desde el inicio del ensayo [s]", ylabel="Fuerza vertical Fz [N] (sensor puesto en cero antes)", title="Fuerza en el tiempo")
    for nom in dict.fromkeys(fase):
        if nom in ("reposo", "recuperación del sensor"): continue
        m = fase == nom
        b.plot(mm[m], F[m], ".", ms=3, color=COL.get(nom, "tab:purple"), label=nom)
    b.set(xlabel="Descenso acumulado del eje vertical [mm]\n(desplazamiento ordenado al motor, no medido)", ylabel="Fuerza vertical Fz [N]", title="Fuerza según cuánto bajó el eje")
    lo = mm[F > 3]
    if len(lo): b.set_xlim(max(lo.min() - 12, 0), lo.max() + 3)
    for x in (a, b): x.grid(alpha=.3)
    b.legend(fontsize=9, loc="upper left")
    fig.suptitle(titulo + "\nEnsayo de rigidez (Ensayo A): el eje vertical baja de a poco hasta que el pie toca la plataforma y se mide cuánta fuerza aparece", fontsize=11)
    fig.text(.5, .01, NOTA_ENS + (" " + quedan if quedan else ""), ha="center", fontsize=8.5)
    fig.tight_layout(rect=(0, .04, 1, .9)); guardar(fig, claro(salida))


def curva(csv_nombre):
    cab, t, fase, mm, F = leerA(os.path.join(RES, csv_nombre))
    baj = sorted((m, v) for m, v, ph in zip(mm, F, fase) if ph.startswith("bajada fina") and v >= 0)
    sub = sorted((m, v) for m, v, ph in zip(mm, F, fase) if ph.startswith("subida"))
    k = k_por_bandas([p[0] for p in baj], [p[1] for p in baj])["todo >=8 N"][0]
    c0 = next((m for m, v in baj if v >= 3.0), baj[0][0])
    return baj, sub, k, c0


def fig_comparacion(items, salida, titulo):
    col = ["tab:blue", "tab:red", "tab:green"]
    fig, (a, b) = plt.subplots(1, 2, figsize=(13, 5.6), facecolor="white", gridspec_kw={"width_ratios": [1.6, 1]})
    ks, nom = [], []
    for j, (csvn, etq) in enumerate(items):
        baj, sub, k, c0 = curva(csvn)
        a.plot([m - c0 for m, v in baj], [v for m, v in baj], "o-", ms=3.5, color=col[j], label=f"{etq}: k = {k:.1f} N/mm (bajada)")
        if sub: a.plot([m - c0 for m, v in sub], [v for m, v in sub], "--", color=col[j], lw=1)
        ks.append(k); nom.append(etq.replace(" (", "\n("))
    a.plot([], [], "k--", lw=1, label="línea discontinua = subida (descarga)")
    a.set(xlabel="Cuánto bajó el eje desde que el pie tocó la plataforma [mm]\n(desplazamiento ordenado al motor, no medido)", ylabel="Fuerza vertical Fz [N]",
          title="Fuerza según cuánto se comprime el pie")
    a.legend(fontsize=9, loc="upper left"); a.grid(alpha=.3)
    b.bar(range(len(ks)), ks, color=col[:len(ks)])
    for j, v in enumerate(ks): b.text(j, v, f"{v:.1f}", ha="center", va="bottom")
    b.set_xticks(range(len(ks))); b.set_xticklabels(nom, fontsize=9)
    b.set(ylabel="Rigidez k [N/mm]\n(fuerza por cada mm de descenso, ajuste recto con F ≥ 8 N)", title="Rigidez del pie según su ángulo")
    b.grid(alpha=.3, axis="y")
    fig.suptitle(titulo + "\nEnsayo de rigidez (Ensayo A), una sola pasada por ángulo del pie (prototipo)", fontsize=11)
    fig.text(.5, .01, "k grande = pie rígido (mucha fuerza por poco descenso). Ángulo + = talón abajo, − = punta abajo. " + NOTA_ENS, ha="center", fontsize=8.5)
    fig.tight_layout(rect=(0, .04, 1, .9)); guardar(fig, claro(salida))


# ---------- 11-05 Ensayo A ----------
fig_ensayoA("ensayo_A_ang0_plana_20261105_162448.csv", "Rigidez del pie plano (0°): fuerza vs descenso del eje vertical (corrida completa)", "2026-11-05_ensayo_A_plana_0deg_k23.0_completa.png")
fig_ensayoA("ensayo_A_ang0_plana_20261105_161228.csv", "Rigidez del pie plano (0°): fuerza vs descenso del eje vertical (corrida parcial, se cortó a 112 N)", "2026-11-05_ensayo_A_plana_0deg_k23.2.png", "Corrida incompleta: se cortó la conexión USB.")
fig_ensayoA("ensayo_A_ang11.14_talon_20261105_160831.csv", "Rigidez del pie apoyado en el talón (+11,1°): fuerza vs descenso del eje vertical", "2026-11-05_ensayo_A_talon_11.14deg_k26.4.png")
fig_ensayoA("ensayo_A_ang-37.3_punta_20261105_164410.csv", "Rigidez del pie apoyado en la punta (−37,3°): fuerza vs descenso del eje vertical", "2026-11-05_ensayo_A_punta_-37.3deg_k2.4_completa.png", "Aquí los pasos fueron de 2 mm (en las otras, 0,2 mm).")
fig_ensayoA("RAW_en_vivo_corrida3_20261105_154553.csv", "Rigidez del pie a ≈5° (ángulo a ojo): fuerza vs descenso del eje vertical (corrida parcial)", "2026-11-05_ensayo_A_5deg_parcial_k28.png", "Corrida incompleta (sin subida), datos en vivo.")
fig_comparacion([("ensayo_A_ang11.14_talon_20261105_160831.csv", "talón (+11,1°)"), ("ensayo_A_ang0_plana_20261105_162448.csv", "plano (0°)")],
                "2026-11-05_comparacion_k_talon_plana.png", "Rigidez del pie: talón vs plano")
fig_comparacion([("ensayo_A_ang11.14_talon_20261105_160831.csv", "talón (+11,1°)"), ("ensayo_A_ang0_plana_20261105_162448.csv", "plano (0°)"),
                 ("ensayo_A_ang-37.3_punta_20261105_164410.csv", "punta (−37,3°)")],
                "2026-11-05_comparacion_k_3condiciones.png", "Rigidez del pie según su ángulo: talón, plano y punta")

# ---------- 11-10 fuerza vs velocidad ----------
f = os.path.join(R, "pruebas", "resultados", "fuerza_vs_velocidad_y_20261110_en_vivo.csv")
fil = [l.strip().split(",", 4) for l in open(f) if not l.startswith("#")]
fil = [r for r in fil if r[1] not in ("inicio", "tara", "retorno")]
t = np.array([float(r[0]) for r in fil]); F = np.array([float(r[2]) for r in fil]); v = np.array([float(r[3]) for r in fil]); ph = [r[1] for r in fil]
fig, (a, b) = plt.subplots(2, 1, figsize=(12, 7.5), sharex=True, facecolor="white", gridspec_kw={"height_ratios": [2, 1]})
a.plot(t, F, "k", lw=.8)
a.set(ylabel="Fuerza vertical Fz [N]\n(el pie NO toca nada)", title="Fuerza que lee la plataforma")
b.plot(t, v / 80, color="tab:blue")
b.set(ylabel="Velocidad ordenada al eje [mm/s]\n(+ sube, − baja)", xlabel="Tiempo [s]")
ini = [0] + [i for i in range(1, len(ph)) if ph[i] != ph[i - 1]] + [len(ph)]
for i, j in zip(ini[:-1], ini[1:]):
    n = ph[i]
    c = "#dde8ff" if n == "reposo" else "#e8dcff" if n == "tras parar" else "#fde2e2" if n.startswith("baja") else "#e0f5e4"
    for x in (a, b): x.axvspan(t[i], t[min(j, len(t) - 1)], color=c, alpha=.8, lw=0)
for x in (a, b): x.grid(alpha=.3)
fig.suptitle("¿El movimiento del eje vertical altera la lectura de fuerza? (prueba en el aire, sin contacto)\n"
             "Si todo estuviera bien, Fz se quedaría en 0 N aunque el eje se mueva. Fondo: azul = eje quieto, rojo = baja, verde = sube, violeta = después de parar.", fontsize=10.5)
fig.text(.5, .005, "Velocidad en mm/s = pasos/s ÷ 80 (80 pasos por mm). Velocidad ordenada, no medida.", ha="center", fontsize=8.5)
fig.tight_layout(rect=(0, .02, 1, .92)); guardar(fig, claro("2026-11-10_fuerza_vs_velocidad_y_aire.png"))

# ---------- 11-18 Ensayo B ----------
fb = os.path.join(RES, "ensayoB_ang0_20261118_114209.csv")
filas = [r for r in csv.reader(open(fb)) if r and not r[0].startswith("#") and r[0] != "t_s" and len(r) >= 4 and not r[1].startswith("400 dur")]
t = np.array([float(r[0]) for r in filas]); fase = [r[1] for r in filas]; F = np.array([float(r[2]) for r in filas])
ini = [i for i in range(1, len(fase)) if fase[i].startswith("baja") and not fase[i - 1].startswith("baja")]
vels = sorted({int(fase[i].split("v")[-1]) for i in ini})
fig, ax = plt.subplots(1, len(vels), figsize=(6.5 * len(vels), 5.6), facecolor="white", squeeze=False)
for a, vv in zip(ax[0], vels):
    n = 0
    for i in [j for j in ini if fase[j].endswith(f"v{vv}")]:
        n += 1; tc = t[i] - 0.0072; m = (t - tc > -0.4) & (t - tc < 0.55)
        a.plot((t[m] - tc) * 1000, F[m], lw=.9, alpha=.8, label=f"pulso {n}")
    a.axvline(0, color="r"); a.axvline(200, color="gray", ls=":")
    a.set(title=f"Orden de bajar a {vv / 80:.1f} mm/s durante 0,2 s",
          xlabel="Tiempo desde la orden [ms]\n(rojo = se da la orden; gris = termina el pulso y el eje sube)", ylabel="Fuerza vertical Fz [N]")
    a.grid(alpha=.3); a.legend(fontsize=8)
fig.suptitle("Respuesta del contacto a pequeños pulsos del eje vertical (Ensayo B), pie plano 0°, 3 pulsos por velocidad\n"
             "Sirve para medir el retardo entre la orden y el aumento de fuerza (≈15–23 ms) y la rigidez dinámica (≈18–20 N/mm)", fontsize=11)
fig.tight_layout(rect=(0, 0, 1, .9))
guardar(fig, os.path.join(RES, "ensayoB_ang0_20261118_114209_claro.png"))

# ---------- 11-18 escalera 10-50 kg (resumen.csv) ----------
rows = list(csv.DictReader(open(os.path.join(R, "reportes", "escalera", "20261118_124639", "resumen.csv"))))
kg = [float(r["kg"]) for r in rows]; ab = [r["motivo"].startswith("ABORT") for r in rows]
fig, ax = plt.subplots(2, 2, figsize=(13, 8), facecolor="white")


def pl(a, key, tit, yl):
    y = [float(r[key]) for r in rows]
    a.plot(kg, y, "o-", color="tab:blue")
    a.plot([k for k, x in zip(kg, ab) if x], [yy for yy, x in zip(y, ab) if x], "rx", ms=12, mew=3, label="corrida abortada")
    a.set(title=tit, xlabel="Masa del sujeto simulado [kg]", ylabel=yl); a.grid(alpha=.3)


pl(ax[0][0], "rms_ultima_pct", "Error de la última pisada (menos es mejor)", "Error RMS [% del pico de fuerza]"); ax[0][0].legend()
pl(ax[0][1], "v_max_mm_s", "Velocidad máxima del eje vertical", "Velocidad [mm/s]")
ax[0][1].axhline(112.5, color="r", ls="--", label="techo permitido (9000 pasos/s)"); ax[0][1].legend()
pl(ax[1][0], "compresion_max_mm", "Compresión máxima del pie (descenso ordenado, no medido)", "Compresión [mm]")
pl(ax[1][1], "rigidez_aparente_N_mm", "Rigidez aparente del pie (fuerza máx ÷ compresión)", "Rigidez [N/mm]")
fig.suptitle("Subir la carga de a poco (10 a 50 kg): pie plano, solo el eje vertical en lazo cerrado de fuerza, 6 pisadas por escalón\n"
             "El ILC (aprende el error de una pisada a otra) deja el error en 3–4 % hasta 40 kg; con 50 kg la corrida se abortó (X roja).", fontsize=11)
fig.tight_layout(rect=(0, 0, 1, .92))
guardar(fig, os.path.join(R, "reportes", "escalera", "20261118_124639", "resumen_claro.png"))

# ---------- 11-18 noche: pisadas con los 3 ejes desde la interfaz ----------
D = os.path.join(R, "reportes", "datos", "2026-11-18_pisadas_3ejes_interfaz")
corr = [("20261118_172147_Control_apoyo_talla170_montaje37_p1.csv", "17:21, pisada 1"),
        ("20261118_175712_Control_apoyo_talla170_montaje37_p1.csv", "17:57, pisada 1"),
        ("20261118_175820_Control_apoyo_talla170_montaje37_p1.csv", "17:58, pisada 1"),
        ("20261118_175820_Control_apoyo_talla170_montaje37_p2.csv", "17:58, pisada 2 (abortada a 0,5 s)")]
fig, ax = plt.subplots(3, 1, figsize=(11, 10), sharex=True, facecolor="white")
for j, (fn, et) in enumerate(corr):
    d = np.genfromtxt(os.path.join(D, fn), delimiter=",", names=True)
    c = f"C{j}"
    ax[0].plot(d["t_s"], d["Fz_N"], color=c, lw=1.3, label=et)
    ax[0].plot(d["t_s"], d["objetivo_N"], "--", color=c, lw=.8, alpha=.6)
    ax[1].plot(d["t_s"], d["objetivo_N"] - d["Fz_N"], color=c, lw=1, label=et)
    ax[2].plot(d["t_s"][1:], np.diff(d["t_s"]) * 1000, color=c, lw=.9, label=et)
ax[0].set(ylabel="Fuerza vertical Fz [N]\n(línea continua = medida, discontinua = objetivo)")
ax[1].set(ylabel="Error = objetivo − medida [N]\n(+ falta fuerza, − sobra)")
ax[2].set(ylabel="Tiempo entre ciclos del lazo [ms]\n(normal ≈ 13 ms)", xlabel="Tiempo dentro de la pisada [s]")
for x in ax: x.grid(alpha=.3); x.legend(fontsize=8)
fig.suptitle("Pisadas con los 3 ejes desde la interfaz: carga de 75 kg, 10 veces más lento que la marcha real\n"
             "Eje vertical en lazo cerrado de fuerza (ganancia Kp = 5); eje horizontal y ángulo del pie siguen la trayectoria sin corrección", fontsize=11)
fig.text(.5, .005, "La pisada 2 se abortó porque el lazo se detuvo 82 ms (salto de fuerza mayor al permitido). Kp = ganancia: cuánta velocidad se ordena por cada newton de error.", ha="center", fontsize=8.5)
fig.tight_layout(rect=(0, .02, 1, .94)); guardar(fig, claro("2026-11-18_noche_pisadas_3ejes.png"))
