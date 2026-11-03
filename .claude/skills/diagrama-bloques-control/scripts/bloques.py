"""Biblioteca para dibujar diagramas de bloques de control en blanco y negro, estilo libro de texto,
con tipografia de ecuacion LaTeX (mathtext de matplotlib con fuente Computer Modern).

Uso tipico (ver ../ejemplos/pid_simple.py):

    import sys; sys.path.insert(0, r"<ruta a esta carpeta scripts>")
    from bloques import Lienzo, tabla_variables, tabla_ecuaciones, guardar

    d = Lienzo(1400, 700)
    d.segs([(10, 200), (88, 200)]); d.txt(14, 176, r"$r(t)$", ha="left")
    d.suma("blk_sum", 115, 200, 26)
    d.bloque("blk_pid", 270, 170, 160, 60, "Controlador", r"$K_p$   (2)")
    guardar(d.fig, "salida", "diagrama")

Reglas de estilo que esta biblioteca da por hechas (ver SKILL.md): negro sobre blanco, nombres de bloque en
Arial, matematica en LaTeX, flechas con el nombre de la senal, ecuaciones y variables FUERA de los bloques
(en una leyenda), cada bloque con un numero (n) que remite a su ecuacion.
Las coordenadas son pixeles con el origen arriba a la izquierda (y crece hacia abajo).
"""
import io
import os
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle

PX = 0.72          # 1 px del lienzo = 0.72 pt (la figura se dibuja a 100 dpi)
LW = 2.5 * PX      # grosor de linea de bloques y flechas

# Computer Modern para la matematica (la de LaTeX), Arial para los nombres. svg.fonttype=path convierte el texto
# en trazos: el SVG se ve igual en cualquier equipo y se puede incrustar en una pagina.
plt.rcParams.update({"font.family": "Arial", "mathtext.fontset": "cm", "svg.fonttype": "path",
                     "svg.hashsalt": "bloques", "axes.unicode_minus": False})


class Lienzo:
    """Un diagrama: bloques, sumadores, flechas, puntos de derivacion y textos."""

    def __init__(self, w, h):
        self.w, self.h = w, h
        self.fig = plt.figure(figsize=(w / 100, h / 100), dpi=100)
        self.ax = self.fig.add_axes([0, 0, 1, 1])
        self.ax.set_xlim(0, w); self.ax.set_ylim(h, 0); self.ax.axis("off")
        self.fig.patch.set_facecolor("white")

    def txt(self, x, y, s, size=20, ha="center", va="center", **kw):
        """Texto. Para senales y simbolos usar mathtext: r'$e(t)$', r'$K_p$', r'$\\mathrm{PWM}^{*}$'.
        Varias letras seguidas (nombres de parametros) van en \\mathrm{...} para que salgan rectas, como en LaTeX."""
        return self.ax.text(x, y, s, fontsize=size * PX, ha=ha, va=va, color="black", **kw)

    def segs(self, pts, flecha=True, punteada=False):
        """Poligonal de segmentos rectos; el ultimo lleva punta de flecha si flecha=True."""
        ls = (0, (5, 3.5)) if punteada else "-"
        n = len(pts) - 2 if flecha else len(pts) - 1
        for i in range(n):
            self.ax.plot([pts[i][0], pts[i + 1][0]], [pts[i][1], pts[i + 1][1]], color="black", lw=LW, ls=ls,
                         solid_capstyle="butt")
        if flecha:
            self.ax.annotate("", xy=pts[-1], xytext=pts[-2],
                             arrowprops=dict(arrowstyle="-|>", color="black", lw=LW, mutation_scale=22, shrinkA=0, shrinkB=0))

    def punto(self, x, y):
        """Punto de derivacion: la misma senal se reparte por dos caminos."""
        self.ax.add_patch(Circle((x, y), 5.5, fc="black", ec="black", zorder=5))

    def bloque(self, gid, x, y, w, h, nombre, sub=""):
        """Caja con el nombre (Arial) y, debajo, el simbolo y el numero de su ecuacion, p. ej. r'$K_p$   (2)'.
        gid es el id que queda en el SVG: sirve para marcar el bloque desde una pagina web."""
        r = Rectangle((x, y), w, h, fc="white", ec="black", lw=LW, zorder=3); r.set_gid(gid); self.ax.add_patch(r)
        cy = y + h / 2
        if sub:
            self.txt(x + w / 2, cy - 11, nombre, 21, zorder=4)
            self.txt(x + w / 2, cy + 14, sub, 15, zorder=4)
        else:
            self.txt(x + w / 2, cy, nombre, 21, zorder=4)

    def suma(self, gid, cx, cy, r=26):
        """Circulo sumador. Los signos se ponen aparte con txt(..., '+') y txt(..., '−') junto a cada flecha."""
        c = Circle((cx, cy), r, fc="white", ec="black", lw=LW, zorder=3); c.set_gid(gid); self.ax.add_patch(c)

    def recuadro_punteado(self, x, y, w, h, titulo=None):
        """Agrupa bloques (p. ej. el controlador PID con sus tres ramas)."""
        self.ax.add_patch(Rectangle((x, y), w, h, fc="none", ec="black", lw=LW, ls=(0, (5, 3.5)), zorder=1))
        if titulo:
            self.txt(x + w / 2, y - 17, titulo, 21)


def _lienzo_tabla(w, h):
    fig = plt.figure(figsize=(w / 100, h / 100), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, w); ax.set_ylim(h, 0); ax.axis("off")
    fig.patch.set_facecolor("white")
    return fig, ax


def tabla_variables(filas, titulo="Variables y parámetros", ancho=980, col2=285, alto_fila=31):
    """Leyenda de variables. filas = [(simbolo_latex, descripcion), ...]; None dibuja una linea de separacion.
    El simbolo va en mathtext (r'$u^{*}(t)$') y la descripcion en Arial; dentro de la descripcion se puede
    mezclar mathtext: 'error: $r(t) - y(t)$'."""
    fig, ax = _lienzo_tabla(ancho, 60 + alto_fila * len(filas))
    ax.text(14, 22, titulo, fontsize=19 * PX, ha="left", va="center", weight="bold")
    y = 58
    for fila in filas:
        if fila is None:
            ax.plot([14, ancho - 14], [y - 6, y - 6], color="black", lw=1.0 * PX); y += 10; continue
        simbolo, desc = fila
        ax.text(14, y, simbolo, fontsize=19 * PX, ha="left", va="center")
        ax.text(col2, y, desc, fontsize=16 * PX, ha="left", va="center")
        y += alto_fila
    fig.set_size_inches(ancho / 100, y / 100); ax.set_ylim(y, 0)
    return fig


def tabla_ecuaciones(filas, ancho=1180):
    """Ecuaciones numeradas. filas = [(numero, latex, nombre, alto[, nota]), ...].
    numero: '(1)', '(M1)' o '' para continuar la ecuacion anterior; alto en px (36-40 sin fraccion, 62 con fraccion);
    nombre: etiqueta en cursiva a la derecha; nota: texto en Arial pegado al final de la ecuacion, con acentos
    (los acentos NO funcionan dentro de \\mathrm, por eso van aqui y no dentro del latex).
    Usar decimales con coma dentro de matematica asi: 0{,}5."""
    fig, ax = _lienzo_tabla(ancho, 40 + sum(f[3] for f in filas))
    rend = fig.canvas.get_renderer()
    y = 20
    for num, eq, nombre, h, *nota in filas:
        cy = y + h / 2
        if num:
            ax.text(14, cy, num, fontsize=19 * PX, ha="left", va="center")
        t = ax.text(80, cy, eq, fontsize=21 * PX, ha="left", va="center")
        if nota:
            x1 = t.get_window_extent(rend).x1
            ax.text(x1 + 14, cy, "(" + nota[0] + ")", fontsize=17 * PX, ha="left", va="center")
        if nombre:
            ax.text(ancho - 14, cy, nombre, fontsize=15 * PX, ha="right", va="center", style="italic")
        y += h
    return fig


def guardar(fig, carpeta, nombre, dpi=300):
    """Escribe carpeta/nombre.svg y carpeta/nombre.png (PNG a 300 dpi: bueno para un documento)."""
    os.makedirs(carpeta, exist_ok=True)
    fig.savefig(os.path.join(carpeta, nombre + ".svg"), facecolor="white")
    fig.savefig(os.path.join(carpeta, nombre + ".png"), dpi=dpi, facecolor="white")
    plt.close(fig)


def svg_en_linea(fig, id_svg="diagSvg", etiqueta="Diagrama de bloques", estilo_extra=""):
    """SVG listo para pegar dentro de un HTML (ancho 100 %). Cada bloque con gid queda como <g id="gid">,
    asi una hoja de estilo puede marcarlo: #diagSvg .hl path { stroke: #e11d48 !important; stroke-width: 4px !important }."""
    buf = io.StringIO()
    fig.savefig(buf, format="svg", facecolor="white")
    s = buf.getvalue()
    s = s[s.index("<svg"):]
    s = re.sub(r'<svg ([^>]*?)width="[^"]*" height="[^"]*"', r'<svg id="%s" \1' % id_svg, s, count=1)
    return s.replace("<svg id=", '<svg style="width:100%%;height:auto;display:block;background:#fff;%s" role="img" '
                     'aria-label="%s" id=' % (estilo_extra, etiqueta), 1)
