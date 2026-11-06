"""Mapa de calor de la rigidez de contacto k (N/mm) medida en el Ensayo A
(2026-11-05, una protesis, 3 condiciones de pie: talon, plana, punta).

SOLO 3 puntos medidos -- la interpolacion entre ellos es LINEAL, puramente
visual, NO es un dato medido. Se marca explicitamente en la figura.

Fuente de los valores: control/identificacion/ESTADO_Y_PENDIENTES_para_retomar.md
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

# (angulo_deg, k_N_por_mm, etiqueta) -- angulo: + = hacia talon, - = hacia punta (K_POSITIVE_DIR=0, confirmado)
puntos = [(-37.3, 2.4, "Punta"), (0.0, 23.0, "Plana"), (11.14, 26.4, "Talon")]
angulos = np.array([p[0] for p in puntos])
ks = np.array([p[1] for p in puntos])

# Grilla fina solo para la franja de color (interpolacion lineal entre los 3 puntos medidos)
grilla = np.linspace(angulos.min(), angulos.max(), 400)
k_interp = np.interp(grilla, angulos, ks)

fig, ax = plt.subplots(figsize=(9, 3.2), dpi=150)

cmap = LinearSegmentedColormap.from_list("rigidez", ["#2166ac", "#67a9cf", "#fdae61", "#b2182b"])
franja = np.tile(k_interp, (2, 1))
im = ax.imshow(franja, extent=[grilla.min(), grilla.max(), 0, 1], aspect="auto",
               cmap=cmap, vmin=ks.min(), vmax=ks.max())

# Marcar los 3 puntos REALMENTE medidos (lineas verticales + anotacion)
for ang, k, etiqueta in puntos:
    ax.axvline(ang, color="black", linewidth=1.2, linestyle="--")
    ax.annotate(f"{etiqueta}\n{ang:+.1f}°\nk={k:.1f} N/mm", xy=(ang, 1.0),
                xytext=(ang, 1.28), ha="center", va="bottom", fontsize=9,
                annotation_clip=False)

ax.set_xlabel("Angulo sagital del pie (°)  [+ = hacia talon, − = hacia punta]")
ax.set_yticks([])
ax.set_title("Rigidez de contacto k medida (Ensayo A, 2026-11-05, 1 protesis, 3 condiciones)\n"
             "Franja de color = interpolacion LINEAL entre los 3 puntos medidos (NO es dato medido)",
             fontsize=10)
cbar = fig.colorbar(im, ax=ax, pad=0.02)
cbar.set_label("k (N/mm)")

plt.tight_layout()
salida = "control/identificacion/resultados/mapa_calor_k_2026-11-06.png"
plt.savefig(salida)
print(f"Guardado: {salida}")
