"""Registro en vivo para el visor de pantalla (herramientas/visor_pruebas.py).
Uso en una prueba:   ev = EnVivo(); ev.escribir("baja 400", F_N, y_pasos, "BAJANDO Y a 5 mm/s")
Formato (una fila por muestra): t_s,fase,F_N,y_pasos,mensaje   (el mensaje no lleva comas)."""
import time
RUTA = "logs/prueba_en_vivo.csv"


class EnVivo:
    def __init__(self, titulo="", ruta=RUTA):
        self.t0 = time.monotonic()
        self.f = open(ruta, "w", buffering=1)
        self.f.write(f"# {titulo}\n")

    def escribir(self, fase, F, y_pasos, mensaje=""):
        self.f.write(f"{time.monotonic() - self.t0:.3f},{fase},{F:.2f},{int(y_pasos)},{mensaje.replace(',', ';')}\n")

    def cerrar(self, mensaje="FIN"):
        try:
            self.f.write(f"# {mensaje}\n"); self.f.close()
        except Exception:
            pass
