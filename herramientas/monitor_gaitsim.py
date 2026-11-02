"""Monitor visual: Fz del AMTI (via ADS1256) en vivo + estado y latencia del ESP32.

- Panel izquierdo: Fz [N] en los ultimos 10 s, voltaje crudo, tasa de muestreo,
  boton "Poner a cero" (resta el offset actual) y "Grabar CSV".
- Panel derecho: RTT del ESP32 en vivo (PING + GET_POSITION), posiciones X/Y/K.
  Los botones de movimiento (MANUAL) estan BLOQUEADOS salvo que marques
  "Permitir mover motores".

Si el ADC o el ESP32 no estan disponibles la ventana igual abre y lo avisa.
Solo un programa puede usar el SPI/serial a la vez: cierra otros antes de abrir.
"""
import csv
import os
import queue
import statistics
import sys
import threading
import time
import tkinter as tk

import ttkbootstrap as tb
from collections import deque
ttk = tb  # widgets de ttkbootstrap (aceptan bootstyle)

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "pruebas"))

PUERTO_ESP32 = "/dev/ttyUSB0"
VENTANA_S = 10.0

# ---------------------------------------------------------------- ADC
adc_estado = {"msg": "iniciando...", "ok": False}
adc_buf = deque(maxlen=15000)  # ~15 s a 1000 SPS  # (t, volts, newtons_crudos)
adc_lock = threading.Lock()
adc_stop = threading.Event()


def desde(t_min):
    """Muestras con t > t_min, recorriendo el buffer desde el final (no copia los 15 mil)."""
    with adc_lock:
        out = []
        for d in reversed(adc_buf):
            if d[0] <= t_min:
                break
            out.append(d)
    out.reverse()
    return out


def hilo_adc():
    try:
        import leer_ads1256_fz as m
        adc = m.ADS1256()
    except Exception as e:  # noqa: BLE001
        adc_estado.update(msg=f"ADC no disponible: {e}", ok=False)
        return
    adc_estado.update(msg="ADC OK", ok=True)
    try:
        while not adc_stop.is_set():
            try:
                v = adc.leer_volts()
            except TimeoutError as e:
                adc_estado.update(msg=str(e), ok=False)
                time.sleep(0.2)
                continue
            adc_estado.update(msg="ADC OK", ok=True)
            with adc_lock:
                adc_buf.append((time.monotonic(), v, m.volts_a_newtons(v)))
    finally:
        adc.cerrar()


# ---------------------------------------------------------------- ESP32
esp_estado = {"msg": "conectando...", "ok": False, "pos": (None, None, None)}
esp_rtt = deque(maxlen=2000)  # (t, ms)
esp_cmds = queue.Queue()
esp_stop = threading.Event()


def hilo_esp32():
    try:
        import serial
        ser = serial.Serial()
        ser.port, ser.baudrate, ser.timeout = PUERTO_ESP32, 115200, 0.5
        ser.dtr = False  # no resetear el ESP32 al abrir (perderia la posicion)
        ser.rts = False
        ser.open()
    except Exception as e:  # noqa: BLE001
        esp_estado.update(msg=f"ESP32 no disponible: {e}", ok=False)
        return

    def pedir(cmd):
        ser.reset_input_buffer()
        t0 = time.perf_counter()
        ser.write(f"<{cmd}>".encode())
        r = ser.readline().decode(errors="replace").strip()
        return (time.perf_counter() - t0) * 1000.0, r

    esp_estado.update(msg="ESP32 conectado", ok=True)
    try:
        while not esp_stop.is_set():
            while not esp_cmds.empty():
                cmd = esp_cmds.get()
                _, r = pedir(cmd)
                esp_estado["ultimo"] = f"{cmd} -> {r or 'sin respuesta'}"
            ms, r = pedir("PING")
            if r.startswith("PONG"):
                esp_rtt.append((time.monotonic(), ms))
                esp_estado.update(msg="ESP32 conectado", ok=True)
            else:
                esp_estado.update(msg="ESP32 no responde", ok=False)
            _, r = pedir("GET_POSITION")
            if r.startswith("POSITION"):
                try:
                    esp_estado["pos"] = tuple(int(x) for x in r.split(":")[1:4])
                except ValueError:
                    pass
            time.sleep(0.1)
    finally:
        ser.close()


# ---------------------------------------------------------------- Graficos en Canvas
def dibujar(canvas, pts, ymin_fijo=None, ymax_fijo=None, unidad="", color="#00bc8c"):
    canvas.delete("all")
    w, h = canvas.winfo_width(), canvas.winfo_height()
    mi, md, ms_, mb = 55, 10, 10, 22
    canvas.create_rectangle(mi, ms_, w - md, h - mb, outline="#555")
    if len(pts) < 2:
        canvas.create_text(w / 2, h / 2, text="sin datos", fill="#777")
        return
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    x0, x1 = xs[0], max(xs[-1], xs[0] + 1e-6)
    lo = min(ys) if ymin_fijo is None else ymin_fijo
    hi = max(ys) if ymax_fijo is None else ymax_fijo
    if hi - lo < 1e-9:
        lo, hi = lo - 1, hi + 1
    pad = (hi - lo) * 0.08
    lo, hi = lo - pad, hi + pad

    def px(x):
        return mi + (x - x0) / (x1 - x0) * (w - mi - md)

    def py(y):
        return ms_ + (hi - y) / (hi - lo) * (h - ms_ - mb)

    for k in range(5):
        yv = lo + (hi - lo) * k / 4
        canvas.create_line(mi, py(yv), w - md, py(yv), fill="#303030")
        canvas.create_text(mi - 4, py(yv), text=f"{yv:.1f}", anchor="e", fill="#aaa", font=("TkDefaultFont", 8))
    if lo < 0 < hi:
        canvas.create_line(mi, py(0), w - md, py(0), fill="#777", dash=(3, 3))
    canvas.create_text(mi + 2, h - 10, text=f"{x1 - x0:.0f} s", anchor="w", fill="#aaa", font=("TkDefaultFont", 8))
    canvas.create_text(w - md, h - 10, text=unidad, anchor="e", fill="#aaa", font=("TkDefaultFont", 8))
    paso = max(1, len(pts) // (w * 2))  # decimar para no saturar el canvas
    coords = []
    for x, y in pts[::paso]:
        coords += [px(x), py(y)]
    canvas.create_line(*coords, fill=color, width=2)


# ---------------------------------------------------------------- GUI
class App(tb.Window):
    def __init__(self):
        super().__init__(themename="darkly")
        self.title("Monitor Simulador de Marcha - Fz AMTI + ESP32")
        self.geometry("1100x640")
        self.offset_n = 0.0
        self.grabando = None  # (archivo, writer)
        self.ultimo_grabado = 0.0
        self._abrir_log()

        izq = ttk.LabelFrame(self, text="AMTI - Fz (ADS1256 directo, AIN0)")
        der = ttk.LabelFrame(self, text="ESP32 - latencia y posicion")
        izq.pack(side="left", fill="both", expand=True, padx=6, pady=6)
        der.pack(side="left", fill="both", expand=True, padx=6, pady=6)

        self.lbl_fz = ttk.Label(izq, text="--- N", font=("TkDefaultFont", 40, "bold"), bootstyle="success")
        self.lbl_fz.pack(pady=(8, 0))
        self.lbl_adc = ttk.Label(izq, text="")
        self.lbl_adc.pack()
        self.cv_fz = tk.Canvas(izq, bg="#1e1e1e", highlightthickness=0, height=330)
        self.cv_fz.pack(fill="both", expand=True, padx=6, pady=6)
        fb = ttk.Frame(izq)
        fb.pack(pady=4)
        ttk.Button(fb, text="Poner a cero (tara)", command=self.tara, bootstyle="info").pack(side="left", padx=4)
        self.btn_rec = ttk.Button(fb, text="Grabar CSV", command=self.toggle_rec)
        self.btn_rec.pack(side="left", padx=4)
        self.lbl_rec = ttk.Label(izq, text="")
        self.lbl_rec.pack()

        self.lbl_esp = ttk.Label(der, text="", font=("TkDefaultFont", 11))
        self.lbl_esp.pack(pady=(8, 0))
        self.lbl_rtt = ttk.Label(der, text="RTT: --- ms", font=("TkDefaultFont", 28, "bold"), bootstyle="warning")
        self.lbl_rtt.pack()
        self.lbl_stats = ttk.Label(der, text="")
        self.lbl_stats.pack()
        self.cv_rtt = tk.Canvas(der, bg="#1e1e1e", highlightthickness=0, height=200)
        self.cv_rtt.pack(fill="both", expand=True, padx=6, pady=6)
        self.lbl_pos = ttk.Label(der, text="Pos (pasos)  X: -   Y: -   K: -", font=("TkDefaultFont", 11))
        self.lbl_pos.pack()

        mf = ttk.LabelFrame(der, text="Movimiento manual (MANUAL)")
        mf.pack(fill="x", padx=6, pady=6)
        self.permitir = tk.BooleanVar(value=False)
        ttk.Checkbutton(mf, text="Permitir mover motores (simulador libre y despejado)",
                        variable=self.permitir, command=self.actualizar_botones).pack(anchor="w")
        self.pasos = tk.IntVar(value=40)
        fr = ttk.Frame(mf)
        fr.pack(pady=2)
        ttk.Label(fr, text="Pasos:").pack(side="left")
        ttk.Spinbox(fr, from_=1, to=500, textvariable=self.pasos, width=6).pack(side="left", padx=4)
        self.botones = []
        for eje, nombre in enumerate(("X", "Y", "K")):
            for signo, t in ((-1, "-"), (1, "+")):
                b = ttk.Button(fr, text=f"{nombre}{t}", width=4,
                               command=lambda e=eje, s=signo: self.mover(e, s))
                b.pack(side="left", padx=1)
                self.botones.append(b)
        self.btn_stop = ttk.Button(mf, text="PARAR (MANUAL_STOP)", command=self.parar, bootstyle="danger")
        self.btn_stop.pack(pady=2)  # siempre habilitado
        self.lbl_ultimo = ttk.Label(mf, text="")
        self.lbl_ultimo.pack()
        self.actualizar_botones()

        threading.Thread(target=hilo_adc, daemon=True).start()
        threading.Thread(target=hilo_esp32, daemon=True).start()
        self.after(100, self.refrescar)
        self.protocol("WM_DELETE_WINDOW", self.cerrar)

    def _abrir_log(self):
        d = os.path.join(AQUI, "..", "logs")
        os.makedirs(d, exist_ok=True)
        ruta = os.path.join(d, f"monitor_{time.strftime('%Y%m%d_%H%M%S')}.log")
        self.log = open(ruta, "w", buffering=1)  # linea a linea: legible mientras corre
        enlace = os.path.join(d, "monitor_latest.log")
        if os.path.islink(enlace) or os.path.exists(enlace):
            os.remove(enlace)
        os.symlink(os.path.basename(ruta), enlace)
        self.t_log = time.monotonic()
        self.estado_prev = None
        self.ultimo_cmd = None
        self.log.write("# t_wall | n_muestras | Fz_N min/media/max (crudos, sin tara) | V media | RTT_ms | pos XYK | estado\n")
        self.evento("inicio del monitor")

    def evento(self, texto):
        self.log.write(f"{time.strftime('%H:%M:%S')} EVENTO {texto}\n")

    def escribir_log(self, ahora, rtts):
        n = [d for d in desde(self.t_log) if d[0] <= ahora]
        self.t_log = ahora
        estado = f"{adc_estado['msg']} / {esp_estado['msg']}"
        if estado != self.estado_prev:
            self.evento(f"estado: {estado}")
            self.estado_prev = estado
        cmd = esp_estado.get("ultimo")
        if cmd and cmd != self.ultimo_cmd:
            self.evento(f"comando ESP32: {cmd}")
            self.ultimo_cmd = cmd
        if n:
            fz = [d[2] for d in n]
            v = statistics.mean(d[1] for d in n)
            fzs = f"{min(fz):.1f}/{statistics.mean(fz):.1f}/{max(fz):.1f}"
        else:
            fzs, v = "-", float("nan")
        rtt = f"{rtts[-1][1]:.2f}" if rtts else "-"
        x, y, k = esp_estado["pos"]
        self.log.write(f"{time.strftime('%H:%M:%S')} n={len(n)} Fz={fzs} V={v:+.5f} RTT={rtt} pos={x},{y},{k}\n")

    def actualizar_botones(self):
        for b in self.botones:
            b.state(["!disabled"] if self.permitir.get() else ["disabled"])

    def mover(self, eje, signo):
        if self.permitir.get():
            esp_cmds.put(f"MANUAL:{eje}:{signo * int(self.pasos.get())}")
            self.evento(f"boton mover eje={eje} signo={signo} pasos={self.pasos.get()}")

    def parar(self):
        esp_cmds.put("MANUAL_STOP")
        self.evento("boton PARAR")

    def tara(self):
        ult = desde(time.monotonic() - 1.0)  # ultimo segundo
        if len(ult) >= 50:
            self.offset_n = statistics.median(p[2] for p in ult)  # mediana: ignora glitches
            self.evento(f"tara: offset = {self.offset_n:.2f} N")

    def toggle_rec(self):
        if self.grabando:
            self.grabando[0].close()
            self.lbl_rec.config(text=f"Guardado: {self.grabando[2]}")
            self.grabando = None
            self.btn_rec.config(text="Grabar CSV")
        else:
            ruta = os.path.expanduser(f"~/lecturas_fz_{time.strftime('%Y%m%d_%H%M%S')}.csv")
            f = open(ruta, "w", newline="")
            w = csv.writer(f)
            w.writerow(["t_s", "volts", "newtons_crudos", "newtons_tarados"])
            self.grabando = (f, w, ruta)
            self.ultimo_grabado = time.monotonic()
            self.btn_rec.config(text="Detener grabacion")
            self.lbl_rec.config(text=f"Grabando en {ruta}")

    def refrescar(self):
        ahora = time.monotonic()
        datos = desde(ahora - VENTANA_S)
        nuevos = desde(self.ultimo_grabado) if self.grabando else []
        if self.grabando and nuevos:
            for t, v, n in nuevos:
                self.grabando[1].writerow([f"{t:.6f}", f"{v:.6f}", f"{n:.3f}", f"{n - self.offset_n:.3f}"])
            self.ultimo_grabado = nuevos[-1][0]
        if datos:
            n_act = datos[-1][2] - self.offset_n
            self.lbl_fz.config(text=f"{n_act:8.1f} N")
            t_span = max(datos[-1][0] - datos[0][0], 1e-6)
            tasa = len(datos) / t_span
            self.lbl_adc.config(text=f"{adc_estado['msg']}  |  {datos[-1][1]:+.4f} V  |  {tasa:.0f} muestras/s")
            dibujar(self.cv_fz, [(d[0], d[2] - self.offset_n) for d in datos], unidad="N")
        else:
            self.lbl_fz.config(text="--- N")
            self.lbl_adc.config(text=adc_estado["msg"])
            dibujar(self.cv_fz, [])

        rtts = [r for r in esp_rtt if r[0] >= ahora - 30]
        self.lbl_esp.config(text=esp_estado["msg"])
        if rtts:
            v = [r[1] for r in rtts]
            self.lbl_rtt.config(text=f"RTT: {v[-1]:.2f} ms")
            self.lbl_stats.config(text=f"media {statistics.mean(v):.2f}  max {max(v):.2f}  (ultimos 30 s, n={len(v)})")
            dibujar(self.cv_rtt, rtts, ymin_fijo=0, unidad="ms", color="#f39c12")
        else:
            dibujar(self.cv_rtt, [])
        x, y, k = esp_estado["pos"]
        self.lbl_pos.config(text=f"Pos (pasos)  X: {x}   Y: {y}   K: {k}")
        self.lbl_ultimo.config(text=esp_estado.get("ultimo", ""))
        self.escribir_log(ahora, rtts)
        self.after(100, self.refrescar)

    def cerrar(self):
        adc_stop.set()
        esp_stop.set()
        if self.grabando:
            self.grabando[0].close()
        time.sleep(0.3)
        self.evento("monitor cerrado")
        self.log.close()
        self.destroy()


if __name__ == "__main__":
    App().mainloop()
