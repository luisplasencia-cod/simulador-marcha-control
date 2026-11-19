"""Diagrama de bloques del lazo de Fz en Y del EQUIPO REAL (control hibrido: P programado + ILC), unidades reales (N, pasos/s).
Actualizado 2026-11-19 contra control/lazo_fz_tiempo_real.py y ~/Projects/gaitsim-control/src/fz/{fz_loop,fz_ilc,ilc_core}.py.
X y angulo (K) van en lazo abierto y NO estan en este diagrama.
Convencion: (n) = controlador (se puede cambiar); (Mn) = modelo de la planta (SIN MEDIR, se supone y se barre).
Uso: python diagrama_lazo_hibrido.py [carpeta_de_salida]
"""
import os
import sys

RAIZ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(RAIZ, ".claude", "skills", "diagrama-bloques-control", "scripts"))
from bloques import Lienzo, guardar, tabla_ecuaciones, tabla_variables
import matplotlib.pyplot as plt
plt.rcParams["font.family"] = "Liberation Sans"   # equivalente metrico de Arial (Arial no esta instalada en el RPi)

SALIDA = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "salida")
W, H, FY = 1400, 560, 240

d = Lienzo(W, H)
# --- ILC (arriba, lineas punteadas: actua entre ciclos, no dentro del ciclo)
d.bloque("blk_ilc", 330, 40, 220, 70, "Aprendizaje ILC", r"$\gamma,\ Q$   (4)")
d.segs([(330, 75), (110, 75), (110, FY - 26)], punteada=True); d.txt(220, 96, r"$\delta(t)$", 20)
d.segs([(70, FY), (70, 25), (440, 25), (440, 40)], punteada=True); d.txt(250, 47, r"$r(t)$", 20)
d.punto(490, 480); d.segs([(490, 480), (490, 112)], punteada=True); d.txt(530, 398, r"$F_{med}(t)$", 20)
# --- referencia, sumador 1 (r + delta)
d.segs([(10, FY), (84, FY)]); d.txt(14, FY - 24, r"$r(t)$", 21, ha="left")
d.punto(70, FY)
d.suma("blk_sum1", 110, FY, 26)
d.txt(76, FY + 30, "+", 21); d.txt(132, FY - 56, "+", 21)
d.segs([(136, FY), (214, FY)]); d.txt(175, FY - 24, r"$r^{*}(t)$", 21)
# --- sumador 2 (error)
d.suma("blk_sum2", 240, FY, 26)
d.txt(204, FY + 30, "+", 21); d.txt(262, FY + 58, "−", 24)
d.segs([(266, FY), (328, FY)]); d.txt(297, FY - 24, r"$e(t)$", 21)
# --- controlador P
d.bloque("blk_kp", 330, FY - 30, 150, 60, "Proporcional", r"$K_p(F)$   (3)")
d.segs([(480, FY), (560, FY)]); d.txt(514, FY - 46, r"$u(t)$", 21)
# --- planta simulada (modelo)
d.recuadro_punteado(535, 140, 660, 200, "Planta real (modelo)")
d.bloque("blk_servo", 560, FY - 30, 140, 60, "Servo", r"$\tau_a$   (M1)")
d.segs([(700, FY), (760, FY)]); d.txt(730, FY - 46, r"$v(t)$", 21)
d.bloque("blk_k", 760, FY - 30, 120, 60, "Rigidez", r"$k(F)$   (M2)")
d.segs([(880, FY), (940, FY)]); d.txt(910, FY - 46, r"$q(t)$", 21)
d.suma("blk_sum3", 966, FY, 26)
d.txt(930, FY + 30, "+", 21); d.txt(986, FY - 60, "+", 21)
d.segs([(966, 100), (966, FY - 26)]); d.txt(1015, 112, r"$d(t)$", 21)
d.segs([(992, FY), (1048, FY)]); d.txt(1024, FY - 40, r"$\dot{F}(t)$", 21)
d.bloque("blk_int", 1050, FY - 30, 130, 60, "Integrador", r"$1/s$   (M3)")
d.segs([(1180, FY), (1260, FY)], flecha=False); d.punto(1260, FY)
d.segs([(1260, FY), (1375, FY)]); d.txt(1325, FY - 30, r"$F(t)$", 21)
# --- realimentacion: medida retrasada por abajo
d.segs([(1260, FY), (1260, 480), (1042, 480)])
d.bloque("blk_ret", 900, 450, 140, 60, "Retardo", r"$T$   (M4)")
d.segs([(900, 480), (800, 480)]); d.txt(850, 456, r"$F_{r}(t)$", 21)
d.bloque("blk_fil", 600, 450, 200, 60, "Filtro de medición", r"$N_m$   (5)")
d.segs([(600, 480), (240, 480), (240, FY + 28)]); d.txt(420, 456, r"$F_{med}(t)$", 21)

hoja = [
    (r"$r(t)$", "fuerza vertical objetivo [N] = %BW/100 · m · g (curva de Gutenberg)"),
    (r"$\delta(t)$", "corrección aprendida por el ILC [N]"),
    (r"$r^{*}(t)$", "objetivo corregido [N]: $r(t)+\\delta(t)$"),
    (r"$e(t)$", "error del lazo [N]: $r^{*}(t)-F_{med}(t)$"),
    (r"$u(t)$", "orden de velocidad de Y [pasos/s] (+ = subir)"),
    (r"$v(t)$", "velocidad de Y [pasos/s] (80 pasos = 1 mm)"),
    (r"$q(t)$", "ritmo de cambio de fuerza por el movimiento [N/s]: $-k(F)\\,v(t)/80$"),
    (r"$d(t)$", "perturbación [N/s]"),
    (r"$\dot{F}(t)$", "ritmo de cambio de la fuerza [N/s]"),
    (r"$F(t)$", "fuerza vertical real [N] (0 = tara en el aire)"),
    (r"$F_{r}(t)$", "fuerza real retrasada $T$ [N] (sin filtrar)"),
    (r"$F_{med}(t)$", "fuerza medida y filtrada [N] (entra al lazo y al ILC)"),
    None,
    (r"$K_p(F)$", "ganancia programada: $K_p\\,\\min(1,\\,k_{asum}/k(F))$, $k_{asum}=26{,}4$ N/mm"),
    (r"$\gamma,\ Q$", "ILC real: ganancia 0,5; Hann 10 % del ciclo; adelanto $m=0$"),
    (r"$\tau_a$", "constante del servo (MEDIDA, Ensayo B: 3–14 ms, poco determinada)"),
    (r"$k(F)$", "rigidez medida [N/mm] (pie plano): 18 (<200 N); 35 (300); 48 (500); 54 (700)"),
    (r"$N_m$", "mediana de 7 muestras nuevas (≈7 ms a 1 kHz); filtro 60 Hz apagado"),
    (r"$T$", "retardo comando a Fz (MEDIDO 15–23 ms; el filtro (5) suma ≈ 7 ms)"),
    None,
    (r"$\mathrm{prot.}$", "tope de fuerza, detector de saltos (∝ Δt), límite de descenso: detienen Y"),
]
ecs = [
    ("(1)", r"$r^{*}(t) = r(t) + \delta_j(t)$", "Objetivo corregido (ciclo $j$)", 40),
    ("(2)", r"$e(t) = r^{*}(t) - F_{med}(t)$", "Error del lazo", 40),
    ("(3)", r"$u(t) = \mathrm{sat}\left[-K_p(F)\,e(t)\,p\right],\ \ p=80/26{,}4\ \mathrm{pasos/N},\ \ |u| \leq 9000\ \mathrm{pasos/s}$", "Proporcional programado con saturación (+ = subir Y)", 40),
    ("(4)", r"$\delta_{j+1}(t) = Q\left[\delta_j(t) + \gamma\,\varepsilon_j(t+m)\right],\ \ \varepsilon_j(t)=r(t)-F_{med}(t)$", "ILC (entre ciclos)", 40),
    ("(5)", r"$F_{med}(t) = \mathrm{med}_{N_m}\left[F_r(t-i\,\Delta t)\right]_{i=0}^{N_m-1},\ \ N_m=7$", "Filtro de medición (mediana de bloque)", 50),
    ("(M1)", r"$\tau_a\,\dfrac{dv}{dt} = u - v$", "Servo (primer orden)", 62),
    ("(M2)", r"$q(t) = -k(F)\,v(t)/80$", "Rigidez de contacto (no lineal; 80 pasos/mm)", 40),
    ("(M3)", r"$F(t) = \int_0^t \left[q(\tau) + d(\tau)\right]d\tau$", "Integrador (suma de $q$ y $d$)", 64),
    ("(M4)", r"$F_{r}(t) = F(t - T)$", "Retardo de medición (el filtro (5) va aparte)", 40),
]
guardar(d.fig, SALIDA, "diagrama")
guardar(tabla_variables(hoja), SALIDA, "leyenda_variables")
guardar(tabla_ecuaciones(ecs, ancho=1100), SALIDA, "ecuaciones")
print("listo:", SALIDA)
