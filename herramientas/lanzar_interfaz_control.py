"""Recuperado 2026-11-18 de la sesión de la tarde (se perdió del /tmp al reiniciar). Opera la interfaz VIGENTE ~/Projects/gaitsim-control.
Interfaz REAL a pantalla completa + canal de control por archivo (para que Claude opere los diálogos y deje registro).
Al arrancar: conecta y pulsa HOME. Tras el HOME NO muestra el diálogo de trayectoria: espera comandos en CMD.
Comandos (una línea en CMD; se ejecuta y se borra):
  preparar <tid>                         -> X 20 cm + ángulo del CSV + tara automática (sin diálogo; el OK se pide por chat)
  fz <tid> <peso_kg> <escala> <pisadas>  -> carga parámetros en la pantalla Fz y pulsa Iniciar (confirmación ya dada)
  detener                                -> botón Detener de la pantalla Fz
  estado                                 -> registra estado, posición y textos
Todo queda en el log (stdout)."""
import os, sys, time
sys.path.insert(0, "/home/simgaitlibra/Projects/gaitsim-control")
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from src.ui.main_window import MainWindow
from src.ui.style import APP_STYLESHEET
from src.ui.theme_manager import ThemeManager

CMD = "/home/simgaitlibra/simulador-marcha-control/logs/interfaz_cmd.txt"
app = QApplication(sys.argv)
tm = ThemeManager(); app.setStyleSheet(APP_STYLESHEET()); tm.theme_changed.connect(lambda _n: app.setStyleSheet(APP_STYLESHEET()))
w = MainWindow(serial_port="/dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001-if00-port0", theme_manager=tm); w.showFullScreen()
cs, fz, sm = w._connection_screen, w._fz_control_screen, w._bridge.state_machine
def log(m): print(time.strftime("%H:%M:%S"), m, flush=True)

# Los diálogos los resuelve Claude por comando (con el OK de Luis en el chat): nada modal bloquea la interfaz.
cs._prompt_initial_position_setup = lambda: (cs._position_session.reset(),
                                             log("HOME OK: esperando comando 'preparar <trayectoria>'"))
cs._confirm_trial_start = lambda tid: True
fz._confirm_safety = lambda: True

st = {"intentos": 0, "home": False, "txt": {}}
def paso_conexion():
    if sm.controller.is_connected and not st["home"]:
        if sm.can_home():
            st["home"] = True; w._stack.setCurrentIndex(0); log(">>> pulsando Calibrar (Home)"); cs.home_button.click()
        return
    if not sm.controller.is_connected and st["intentos"] < 4:
        st["intentos"] += 1; log(f"conectando (intento {st['intentos']})"); w._connection_status_btn.click()

def vigilar_textos():
    for nombre, lab in (("inicio", cs.status_label), ("fz", fz.status_label), ("fase", fz.phase_label)):
        t = lab.text()
        if st["txt"].get(nombre) != t:
            st["txt"][nombre] = t; log(f"[{nombre}] {t}")

def comandos():
    if not os.path.exists(CMD): return
    linea = open(CMD).read().strip(); os.remove(CMD)
    if not linea: return
    log(f"COMANDO: {linea}"); p = linea.split()
    try:
        if p[0] == "preparar":
            cs._start_trial_preparation(p[1])
        elif p[0] == "fz":
            tid, peso, esc, n = p[1], float(p[2]), float(p[3]), int(p[4])
            w._show_fz_screen_for(tid); fz.peso_spin.setValue(peso); fz.scale_spin.setValue(esc); fz.pisadas_spin.setValue(n)
            log(f"Fz: {tid} {peso} kg x{esc} {n} pisadas, Kp {fz.kp_spin.value()}, tope {fz.fmax_spin.value():.0f} N, "
                f"v_max {fz.vmax_spin.value()}, auto contacto {fz.auto_contact_check.isChecked()}")
            fz.start_button.click()
        elif p[0] == "detener":
            fz.stop_button.click()
        elif p[0] == "estado":
            pos = sm.get_position() if sm.controller.is_connected else None
            log(f"estado {sm.state.name}, homed {sm._homed}, pos {pos}, sesión {cs._position_session.position}")
        else:
            log("comando desconocido")
    except Exception as exc:
        log(f"ERROR del comando: {exc!r}")

w._bridge.state_changed.connect(lambda s: log(f"estado -> {s}"))
w._bridge.device_error.connect(lambda c, m: log(f"ERROR {c}: {m}"))
fz._pisada_done.connect(lambda d: log(f"PISADA {d['n']}: RMS {d['rms']} N, {d['pct']} %, {d['motivo']}"))
t1 = QTimer(); t1.timeout.connect(paso_conexion); QTimer.singleShot(2500, lambda: t1.start(4000))
t2 = QTimer(); t2.timeout.connect(lambda: (vigilar_textos(), comandos())); t2.start(500)
sys.exit(app.exec())
