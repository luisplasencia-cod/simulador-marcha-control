"""Muestra un PNG en la pantalla del RPi (ventana ajustada al tamano de pantalla).

Uso (desde SSH/terminal de Claude):  python herramientas/mostrar_figura.py ruta.png [ruta2.png ...]
Con varias imagenes: flechas izq/der para cambiar. Esc o q cierra. Click tambien cierra.
Sin PIL: usa PhotoImage de Tk (PNG) con reduccion entera (subsample) si no cabe.
"""
import os
import sys
import tkinter as tk

os.environ.setdefault("XDG_RUNTIME_DIR", "/run/user/%d" % os.getuid())
os.environ.setdefault("WAYLAND_DISPLAY", "wayland-0")
if not os.environ.get("DISPLAY"):
    os.environ["DISPLAY"] = ":1"  # Xwayland de la sesion labwc

rutas = sys.argv[1:]
if not rutas:
    sys.exit(__doc__)

root = tk.Tk()
root.title("Figura - " + os.path.basename(rutas[0]))
sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
root.geometry(f"{sw}x{sh}+0+0")
root.configure(bg="white")
lbl = tk.Label(root, bg="white")
lbl.pack(expand=True, fill="both")
idx = [0]
ref = [None]


def mostrar():
    img = tk.PhotoImage(file=rutas[idx[0]])
    f = max(1, -(-img.width() // sw), -(-img.height() // (sh - 40)))
    if f > 1:
        img = img.subsample(f, f)
    ref[0] = img
    lbl.configure(image=img)
    root.title(f"Figura {idx[0]+1}/{len(rutas)} - {os.path.basename(rutas[idx[0]])}")


def mover(d):
    idx[0] = (idx[0] + d) % len(rutas)
    mostrar()


root.bind("<Left>", lambda e: mover(-1))
root.bind("<Right>", lambda e: mover(1))
for k in ("<Escape>", "q"):
    root.bind(k, lambda e: root.destroy())
lbl.bind("<Button-1>", lambda e: root.destroy())
mostrar()
root.mainloop()
