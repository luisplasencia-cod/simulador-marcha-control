"""Ejemplo minimo del estilo: lazo cerrado con PID en paralelo, accionador, sistema y sensor.
Es la plantilla para sistemas nuevos: copiar, cambiar nombres, simbolos y ecuaciones.
Uso: python pid_simple.py [carpeta_de_salida]   (por defecto ./salida)
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from bloques import Lienzo, guardar, tabla_ecuaciones, tabla_variables

SALIDA = sys.argv[1] if len(sys.argv) > 1 else "salida"
W, H, FY = 1300, 560, 190          # FY = altura del eje de la fila de adelante

d = Lienzo(W, H)
# entrada, comparador, error y derivacion hacia las tres ramas
d.segs([(10, FY), (88, FY)]); d.txt(14, FY - 24, r"$r(t)$", 21, ha="left")
d.suma("blk_sum", 115, FY, 26)
d.txt(78, FY + 30, "+", 21); d.txt(94, FY + 64, "−", 24)
d.segs([(141, FY), (206, FY)]); d.txt(172, FY - 24, r"$e(t)$", 21)
d.punto(212, FY)
# controlador PID: tres ramas en paralelo dentro de un recuadro punteado
d.recuadro_punteado(240, 40, 320, 300, "Controlador PID")
d.bloque("blk_kp", 270, 62, 160, 56, "Proporcional", r"$K_p$   (1)")
d.bloque("blk_ki", 270, 162, 160, 56, "Integral", r"$K_i$   (1)")
d.bloque("blk_kd", 270, 262, 160, 56, "Derivativo", r"$K_d$   (1)")
d.segs([(212, FY), (212, 90), (268, 90)]); d.segs([(212, FY), (268, FY)]); d.segs([(212, FY), (212, 290), (268, 290)])
d.suma("blk_sum2", 510, FY, 22)
d.segs([(430, 90), (510, 90), (510, FY - 24)]); d.segs([(430, FY), (486, FY)]); d.segs([(430, 290), (510, 290), (510, FY + 24)])
d.txt(530, 140, "+", 20); d.txt(456, FY - 12, "+", 20); d.txt(530, 252, "+", 20)
# camino de adelante: los rotulos de senal van ARRIBA de las cajas (y = FY - 46) para no pisarlas
d.segs([(532, FY), (648, FY)]); d.txt(590, FY - 30, r"$c(t)$", 21)
d.bloque("blk_ac", 650, FY - 30, 150, 60, "Accionador", "(2)")
d.segs([(800, FY), (888, FY)]); d.txt(844, FY - 46, r"$u(t)$", 21)
d.bloque("blk_si", 890, FY - 30, 150, 60, "Sistema", "(3)")
d.segs([(1040, FY), (1100, FY)], flecha=False); d.txt(1070, FY - 30, r"$y(t)$", 21); d.punto(1100, FY)
d.segs([(1100, FY), (1250, FY)])
# realimentacion por abajo: sensor y de vuelta al comparador
d.segs([(1100, FY), (1100, 440), (1042, 440)])
d.bloque("blk_se", 900, 410, 140, 60, "Sensor", "(4)")
d.segs([(900, 440), (115, 440), (115, FY + 28)]); d.txt(500, 416, r"$h(t)$", 21)

hoja = [
    (r"$r(t)$", "referencia (el valor que se quiere)"),
    (r"$e(t)$", "error: $r(t) - h(t)$"),
    (r"$c(t)$", "salida del controlador"),
    (r"$u(t)$", "señal que mueve al sistema"),
    (r"$y(t)$", "variable controlada"),
    (r"$h(t)$", "medida del sensor"),
    None,
    (r"$K_p,\ K_i,\ K_d$", "ganancias proporcional, integral y derivativa"),
    (r"$T_s$", "constante de tiempo del sensor"),
]
ecs = [
    ("(1)", r"$c(t) = K_p\,e(t) + K_i\int_0^t e(\tau)\,d\tau + K_d\,\dfrac{de(t)}{dt}$", "PID", 62),
    ("(2)", r"$u(t) = c(t)$", "Accionador (ideal)", 40),
    ("(3)", r"$\dfrac{dy}{dt} = -\dfrac{y}{\tau} + k\,u$", "Sistema (primer orden)", 62),
    ("(4)", r"$T_s\,\dfrac{dh}{dt} = y - h$", "Sensor", 62),
]
guardar(d.fig, SALIDA, "diagrama")
guardar(tabla_variables(hoja), SALIDA, "leyenda_variables")
guardar(tabla_ecuaciones(ecs, ancho=1000), SALIDA, "ecuaciones")
print("listo:", os.path.abspath(SALIDA))
