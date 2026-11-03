r"""Diagrama de bloques del control de presion de la camara (bomba + valvula + sensor): el caso grande del proyecto NEMA.
Es la UNICA copia de esta definicion; el lanzador C:\NEMA\esquema\generar_diagrama_bloques.py solo llama a este archivo.

Usa la biblioteca scripts/bloques.py (estilo en blanco y negro, matematica LaTeX, ecuaciones y variables en la leyenda).
Escribe diagrama_control, leyenda_variables y ecuaciones (.svg y .png) en --salida y, si se da --pagina,
reemplaza la tarjeta 7 de esa pagina HTML (figura en linea para marcar el bloque al elegir un campo). Se puede volver a correr.

Uso:
  python control_presion_completo.py --salida DIR                 solo las imagenes
  python control_presion_completo.py --salida DIR --pagina X.html imagenes y tarjeta 7 de la pagina
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from bloques import Lienzo, guardar, svg_en_linea, tabla_ecuaciones, tabla_variables


def diagrama():
    W, H, FY = 1400, 700, 200
    d = Lienzo(W, H)
    # entrada, comparador y derivacion del error
    d.segs([(10, FY), (88, FY)]); d.txt(14, FY - 24, r"$r(t)$", 21, ha="left")
    d.suma("blk_sum", 115, FY, 26)
    d.txt(78, FY + 30, "+", 21); d.txt(94, FY + 64, "−", 24)
    d.segs([(141, FY), (206, FY)]); d.txt(172, FY - 24, r"$e(t)$", 21)
    d.punto(212, FY)
    # controlador PID: tres ramas en paralelo dentro de un recuadro punteado
    d.recuadro_punteado(240, 50, 320, 300, "Controlador PID")
    d.bloque("blk_kp", 270, 72, 160, 56, "Proporcional", r"$K_p$   (2)")
    d.bloque("blk_ki", 270, 172, 160, 56, "Integral", r"$K_i$   (2)")
    d.bloque("blk_kd", 270, 272, 160, 56, "Derivativo", r"$K_d$   (2)")
    d.segs([(212, FY), (212, 100), (268, 100)])
    d.segs([(212, FY), (268, FY)])
    d.segs([(212, FY), (212, 300), (268, 300)])
    d.suma("blk_sum2", 510, FY, 22)
    d.segs([(430, 100), (510, 100), (510, FY - 24)])
    d.segs([(430, FY), (486, FY)])
    d.segs([(430, 300), (510, 300), (510, FY + 24)])
    d.txt(532, 150, "+", 20); d.txt(456, FY - 12, "+", 20); d.txt(532, 262, "+", 20)
    # camino de adelante: limite, zona muerta, rampa, bomba, camara
    d.segs([(532, FY), (608, FY)]); d.txt(585, FY - 30, r"$u^{*}$", 21)
    d.bloque("blk_sat", 610, 170, 120, 60, "Saturación", "(2)")
    d.segs([(730, FY), (778, FY)]); d.txt(754, FY - 46, r"$u$", 21)
    d.bloque("blk_dz", 780, 170, 150, 60, "Zona muerta", r"$\mathrm{MIN}$   (3)")
    d.segs([(930, FY), (968, FY)]); d.txt(949, FY - 48, r"$\mathrm{PWM}^{*}$", 19)
    d.bloque("blk_rp", 970, 170, 90, 60, "Rampa", r"$\mathrm{SLEW}$ (4)")
    d.segs([(1060, FY), (1098, FY)]); d.txt(1079, FY - 48, r"$\mathrm{PWM}$", 19)
    d.bloque("blk_bo", 1100, 170, 90, 60, "Bomba", "(M1)")
    d.segs([(1190, FY), (1228, FY)]); d.txt(1209, FY - 46, r"$F$", 21)
    d.bloque("blk_ca", 1230, 170, 90, 60, "Cámara", "(M2)")
    d.segs([(1320, FY), (1350, FY)], flecha=False); d.txt(1344, FY - 30, r"$p(t)$", 21); d.punto(1350, FY)
    # realimentacion: sensor, filtro, de vuelta al comparador
    d.segs([(1350, FY), (1350, 470), (1292, 470)])
    d.bloque("blk_se", 1150, 440, 140, 60, "Sensor", "(M3)")
    d.segs([(1150, 470), (1062, 470)]); d.txt(1106, 446, r"$p_m(t)$", 20)
    d.bloque("blk_fi", 900, 440, 160, 60, "Filtro", r"$\mathrm{TAU}$   (1)")
    d.segs([(900, 470), (115, 470), (115, FY + 28)]); d.txt(640, 446, r"$y(t)$", 21)
    d.punto(1106, 470); d.punto(640, 470)
    # ventilacion por pulsos de valvula (entra a la camara rodeando el dibujo, sin cruzar la realimentacion)
    d.segs([(640, 470), (640, 570)])
    d.bloque("blk_vt", 520, 570, 240, 60, r"¿$y > r + \mathrm{BAND}$?", "(5)")
    d.segs([(520, 600), (472, 600)]); d.txt(496, 586, "sí", 18)
    d.bloque("blk_pu", 250, 570, 220, 60, "Pulso de válvula", r"$\mathrm{VTAU}$   (5)")
    d.segs([(360, 630), (360, 680), (1388, 680), (1388, 60), (1275, 60), (1275, 168)])
    d.txt(900, 666, "válvula sin energía: vacía la cámara", 15)
    # proteccion
    d.segs([(1106, 470), (1106, 570)])
    d.bloque("blk_mx", 1010, 570, 190, 60, "Protección", r"$\mathrm{MAX}$   (6)")
    d.segs([(1200, 600), (1262, 600)]); d.txt(1232, 586, "OFF", 17)
    return d.fig


VARIABLES = [
    (r"$r(t)$", "objetivo de presión (mbar; la página lo pide en mmHg)"),
    (r"$e(t)$", "error: $r(t) - y(t)$"),
    (r"$u^{*}(t)$", "salida del PID sin limitar"),
    (r"$u(t)$", "salida del PID limitada a 0–100 %"),
    (r"$\mathrm{PWM}^{*}(t)$", "potencia pedida tras saltar la zona muerta (%)"),
    (r"$\mathrm{PWM}(t)$", "potencia que recibe la bomba tras la rampa (%)"),
    (r"$F(t)$", "presión por segundo que aporta la bomba (mbar/s)"),
    (r"$p(t)$", "presión real en la cámara (mbar)"),
    (r"$p_m(t)$", "presión que entrega el sensor: $p$ más ruido $n$ (mbar)"),
    (r"$y(t)$", "presión filtrada; la que ve el control (mbar)"),
    (r"$I$", "integral del error acumulada dentro del PID (%)"),
    None,
    (r"$K_p,\ K_i,\ K_d$", "ganancias proporcional, integral y derivativa"),
    (r"$\mathrm{TAU}$", "constante de tiempo del filtro (s)"),
    (r"$\mathrm{MIN}$", "PWM desde el que la bomba mueve aire: zona muerta (%)"),
    (r"$\mathrm{SLEW}$", "subida máxima del PWM (% por segundo)"),
    (r"$\mathrm{BAND}$", "margen sobre el objetivo antes de ventilar (mbar)"),
    (r"$\mathrm{VTAU}$", "constante de tiempo de vaciado que fija el largo del pulso (s)"),
    (r"$\mathrm{MAX}$", "presión de corte (mbar)"),
    (r"$\Delta t$", "paso de cálculo: 10 ms"),
    (r"$\tau_\ell,\ \tau_v,\ F_0,\ b,\ d_{\min}$", "modelo de la cámara y la bomba (M1, M2); se miden"),
]

ECUACIONES = [
    ("(1)", r"$y_n = y_{n-1} + \dfrac{\Delta t}{\mathrm{TAU} + \Delta t}\,\left(p_{m,n} - y_{n-1}\right)$", "Filtro de la medición", 62),
    ("(2)", r"$e = r - y$", "PID", 36),
    ("", r"$u^{*} = K_p\,e + I - K_d\,\dfrac{dy}{dt}$", "", 62),
    ("", r"$I_n = I_{n-1} + K_i\,e\,\Delta t$", "", 36),
    ("", r"$u = \min\left(100,\ \max\left(0,\ u^{*}\right)\right)$", "", 40),
    ("(3)", r"$\mathrm{PWM}^{*} = \mathrm{MIN} + u\,\dfrac{100 - \mathrm{MIN}}{100}\quad (u > 0{,}5)\qquad \mathrm{PWM}^{*} = 0\quad (u \leq 0{,}5)$", "Zona muerta", 62),
    ("(4)", r"$\mathrm{PWM}_n = \min\left(\mathrm{PWM}^{*},\ \mathrm{PWM}_{n-1} + \mathrm{SLEW}\,\Delta t\right)$", "Rampa de subida", 40),
    ("(5)", r"$y > r + \mathrm{BAND}\ \Rightarrow\ t_{\mathrm{pulso}} = \mathrm{VTAU}\,\ln\dfrac{y}{r}\ ,\quad 10\ \mathrm{ms} \leq t_{\mathrm{pulso}} \leq 100\ \mathrm{ms}$", "Ventilación", 62),
    ("(6)", r"$p_m \geq \mathrm{MAX}\ \Rightarrow\ \mathrm{OFF}$", "Protección", 40),
    ("(M1)", r"$F = F_0 - b\,p\quad (\mathrm{PWM} \geq d_{\min}) \qquad F = 0\quad (\mathrm{PWM} < d_{\min})$", "Bomba (modelo)", 40),
    ("(M2)", r"$\dfrac{dp}{dt} = F - \dfrac{p}{\tau_\ell}\ ;\qquad \dfrac{dp}{dt} = -\dfrac{p}{\tau_v}$", "Cámara (modelo)", 62, "con la válvula abierta"),
    ("(M3)", r"$p_m = p + n$", "Sensor (modelo)", 40),
]


# ---------------------------------------------------------------- integracion con la pagina de NEMA (opcional)
def tarjeta(svg, web):
    return f'''<!-- 7. DIAGRAMA DE BLOQUES -->
<div class="card" id="cardDiag">
  <h2><span class="num">7</span>Diagrama de bloques</h2>
  <div class="help">Al hacer clic en un campo de la tarjeta 5, su bloque se marca en rojo. Las variables y las ecuaciones están en la leyenda de la figura.
    Tipografía de ecuación LaTeX y estilo de libro de texto (Åström y Murray, <i>Feedback Systems</i>); referencias en el documento "Control PID".</div>
  {svg}
  <div class="cap">
    <p><b>Figura 1.</b> Lazo de control de presión de la cámara; se calcula cada Δt = 10 ms en el ESP32. Cada círculo suma las señales con su signo,
      un punto es una derivación de la misma señal, el recuadro punteado es el controlador PID y (n) remite a la ecuación del mismo número.
      Con el equipo conectado manda lo medido; los bloques (M1) a (M3) son el modelo de la simulación, no el firmware.</p>
    <div class="capimgs">
      <img src="{web}/leyenda_variables.svg" alt="Variables y parámetros de la figura 1">
      <img src="{web}/ecuaciones.svg" alt="Ecuaciones de la figura 1">
    </div>
    <div class="capvals"><b>Valores ahora (tarjeta 5):</b> r = <span id="cv_sp"></span> mmHg · Kp = <span id="cv_kp"></span> · Ki = <span id="cv_ki"></span> · Kd = <span id="cv_kd"></span> ·
      TAU = <span id="cv_tau"></span> s · MIN = <span id="cv_min"></span> % · SLEW = <span id="cv_slew"></span> %/s ·
      BAND = <span id="cv_band"></span> mmHg · VTAU = <span id="cv_vtau"></span> s · MAX = <span id="cv_max"></span> mmHg ·
      modelo: τℓ = <span id="cv_tauL"></span> s · τv = <span id="cv_tauV"></span> s · F0 = <span id="cv_F0"></span> · b = <span id="cv_b"></span> · dmin = <span id="cv_dmin"></span> %</div>
  </div>
  <div class="row">
    <a class="dl" href="{web}/diagrama_control.png" download>Descargar la figura (PNG)</a>
    <a class="dl" href="{web}/leyenda_variables.png" download>Variables (PNG)</a>
    <a class="dl" href="{web}/ecuaciones.png" download>Ecuaciones (PNG)</a>
  </div>
</div>

'''


CSS = '''
  .cap { margin-top: 12px; font-size: 0.85rem; }
  .cap p { margin: 0 0 10px; color: var(--text); }
  .capimgs { display: grid; grid-template-columns: 1fr 1.2fr; gap: 12px; align-items: start; }
  @media (max-width: 900px) { .capimgs { grid-template-columns: 1fr; } }
  .capimgs img { width: 100%; height: auto; background: #fff; border-radius: 10px; }
  .capvals { margin-top: 10px; color: var(--muted); }
  .capvals span { color: var(--text); font-weight: 600; }
  a.dl { display: block; text-align: center; background: #2c313c; color: #fff; text-decoration: none; border-radius: 8px; padding: 9px 12px; margin-top: 8px; font-size: 0.9rem; }
  #diagSvg.hl, #diagSvg .hl path { stroke: #e11d48 !important; stroke-width: 4px !important; }
'''

JS = r'''// ---------- diagrama de bloques (tarjeta 7): valores de la leyenda y bloque marcado ----------
(function () {
  const $ = id => document.getElementById(id), set = (id, t) => { const e = $(id); if (e) e.textContent = t; };
  const BLK = { pumpSp: ["blk_sum"], pumpKp: ["blk_kp"], pumpKi: ["blk_ki"], pumpKd: ["blk_kd"], pumpTau: ["blk_fi"], pumpMin: ["blk_dz"],
                pumpSlew: ["blk_rp"], pumpBand: ["blk_vt"], pumpVtau: ["blk_pu"], pumpMax: ["blk_mx"] };
  function diagUpdate() {
    const P = (typeof simPlant === "object") ? simPlant : {};
    for (const [cv, f] of [["sp", "pumpSp"], ["kp", "pumpKp"], ["ki", "pumpKi"], ["kd", "pumpKd"], ["tau", "pumpTau"], ["min", "pumpMin"],
                           ["slew", "pumpSlew"], ["band", "pumpBand"], ["vtau", "pumpVtau"], ["max", "pumpMax"]]) set("cv_" + cv, $(f).value);
    if (P.tauL !== undefined) { set("cv_F0", P.F0); set("cv_b", P.b); set("cv_dmin", P.dmin); set("cv_tauL", P.tauL); set("cv_tauV", P.tauV); }
  }
  window.diagUpdate = diagUpdate;
  function mark(id, on) {
    document.querySelectorAll("#diagSvg .hl").forEach(g => g.classList.remove("hl"));
    if (on) for (const b of BLK[id] || []) { const g = document.getElementById(b); if (g) g.classList.add("hl"); }
  }
  for (const id of Object.keys(BLK)) {
    const el = $(id);
    el.addEventListener("focus", () => mark(id, true));
    el.addEventListener("blur", () => mark(id, false));
    el.addEventListener("input", diagUpdate);
  }
  diagUpdate();
})();
'''


def parchar_pagina(pagina, svg, web):
    s = open(pagina, encoding="utf-8").read()
    a = s.index("<!-- 7. DIAGRAMA DE BLOQUES -->"); b = s.index("<!-- 1. MOTOR -->")
    s = s[:a] + tarjeta(svg, web) + s[b:]
    s = re.sub(r"\n  \.cap \{.*?#diagSvg \.hl path \{[^}]*\}\n", "\n", s, flags=re.S)   # CSS de una corrida anterior
    s = re.sub(r"\n  \.cap \{.*?\.capvals span \{[^}]*\}\n", "\n", s, flags=re.S)
    s = s.replace("</style>", CSS + "</style>", 1)
    a = s.index("// ---------- diagrama de bloques (tarjeta 7)")
    b = s.index('simPreset("guardado");', a)
    s = s[:a] + JS + s[b:]
    open(pagina, "w", encoding="utf-8").write(s)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--salida", default="salida_control_presion", help="carpeta donde se escriben las imagenes")
    ap.add_argument("--pagina", help="ble_control.html: si se da, se reemplaza su tarjeta 7")
    ap.add_argument("--web", default="esquema", help="ruta, vista desde la pagina, de la carpeta de imagenes")
    a = ap.parse_args()
    guardar(tabla_variables(VARIABLES), a.salida, "leyenda_variables")
    guardar(tabla_ecuaciones(ECUACIONES), a.salida, "ecuaciones")
    fig = diagrama()
    svg = svg_en_linea(fig, "diagSvg", "Diagrama de bloques del control de presión", "border-radius:10px")
    guardar(fig, a.salida, "diagrama_control")
    if a.pagina:
        parchar_pagina(a.pagina, svg, a.web)
    print("listo:", os.path.abspath(a.salida), "| pagina:", a.pagina or "(sin tocar)")


main()
