"""Ajuste de rigidez k [N/mm] por tramos de fuerza (compartido por el ensayo y el comparador).
Entrada: listas mm (descenso acumulado) y F (N). Salida: dict banda -> (k, n_puntos). Pendiente por minimos cuadrados."""
BANDAS = [("8-40 N", 8, 40), ("40-100 N", 40, 100), (">100 N", 100, 1e9), ("todo >=8 N", 8, 1e9)]

def pendiente(xs, ys):
    n = len(xs)
    if n < 3: return None
    mx, my = sum(xs) / n, sum(ys) / n
    d = sum((x - mx) ** 2 for x in xs)
    return None if d == 0 else sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / d

def k_por_bandas(mm, F):
    out = {}
    for nombre, lo, hi in BANDAS:
        pts = [(x, y) for x, y in zip(mm, F) if lo <= y < hi]
        k = pendiente([p[0] for p in pts], [p[1] for p in pts])
        out[nombre] = (k, len(pts))
    return out
