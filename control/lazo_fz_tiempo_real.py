"""Lazo de control de Fz en tiempo real (RT) + ILC entre ciclos -- eje vertical.

*** NO PROBADO EN HARDWARE, NI SIQUIERA EJECUTABLE TODAVIA ***
Escrito sin RPi/ESP32 a mano (2026-11-07), solo contra lo ya documentado:
  - control/ilc/fz_ilc.py (curva objetivo real + ILC + conversion N->pasos)
  - control/firmware/README.md (protocolo SET_VEL:eje:pasos_por_seg_con_signo)
  - control/telemetria/formato_log.md (formato del log)
  - control/identificacion/tabla_k_por_protesis.json (k_asumido por protesis)
  - pruebas/leer_ads1256_fz.py (lectura real del AMTI)

BLOQUEOS CONOCIDOS ANTES DE PODER CORRER ESTO DE VERDAD (no inventar, no esquivar):
  1. El parche `control/firmware/control_velocidad_continua.patch` (comando SET_VEL)
     NO esta compilado ni flasheado. Sin el, el ESP32 no entiende SET_VEL.
  2. RESUELTO 2026-11-08 (leyendo el codigo, no probado en hardware todavia):
     SET_VEL SI responde, igual que cualquier otro comando -- `primary_task`
     en main.cpp es un ciclo `communication_rx -> dispatch -> communication_tx`
     siempre bloqueante; `handle_velocity_command` llena txPacket con OK o BUSY
     como cualquier handler. NO es fire-and-forget. `ClienteVelocidadESP32` de
     abajo ya lee y descarta esa respuesta en cada `set_vel()`. El RTT de esto
     es el mismo que el medido con PING/PONG (mismo mecanismo): ~6 ms (5.97 ms,
     ver reportes/) -- ya cabe dentro de dt_control_s=10 ms, pero falta
     confirmar en banco que no se degrada con el servo en movimiento.
  3. `KP` (ganancia proporcional, 1/s) NO esta elegida/ajustada contra el
     sistema real -- ver control/simulacion/rt_vs_ilc_latencia.py y su
     sensibilidad con el k REAL medido. Usar un valor de PARTIDA conservador
     (ver abajo) y ajustar en banco con motores desconectados primero.
  4. El `dt_control_s` (periodo del bucle) determina cuanto rato pasa entre
     SET_VEL -- debe ser bien menor al watchdog del firmware (80 ms) y menor
     a la latencia total medida (ver reportes/) para que el margen de fase de
     la simulacion siga siendo valido.
  5. La mediana de N muestras del ADC (ver abajo, filtro de errores de bit del
     SPI) usa N=5 porque con el servo vertical en movimiento los errores
     subieron hasta 2.24% (ver CLAUDE.md, 2026-11-05 15:15) -- con mediana de
     3 (usada en el monitor estatico) puede no bastar; AJUSTAR si se mide otra
     cosa en banco.

Diseno del lazo (coincide con control/telemetria/formato_log.md, columnas
r, delta, r_corregida, F_med, e, u):
  - r(t): curva objetivo real de Fz (Gutenberg/Fukuchi), igual que fz_ilc.py.
  - delta_j(t): correccion del ILC, aprendida ciclo a ciclo (igual que fz_ilc.py).
  - r_corregida(t) = r(t) + delta_j(t): lo que persigue el lazo RT este ciclo.
  - F_med(t): Fz medido (AMTI->ADS1256), filtrado con mediana de N muestras.
  - e(t) = r_corregida(t) - F_med(t)  [N]
  - u(t) = KP * e(t) * pasos_por_n   [pasos/s], enviado como SET_VEL cada dt_control_s.
  - Al final de cada ciclo: ilc.registrar_medicion(t_muestras, F_med_muestras)
    actualiza delta para el siguiente ciclo (igual que fz_ilc.py).

Uso previsto (cuando el patch SET_VEL este flasheado y probado en banco):
    python control/lazo_fz_tiempo_real.py --peso_sujeto_n 850 --n_ciclos 10 \\
        --kp 15 --protesis "pie_pasivo_1 (la unica probada hasta ahora)"
    (--kp 15 = recomendacion de partida 2026-11-08, ver reportes/2026-11-08_avance_sin_rpi.md Sec.3;
    re-elegir con control/simulacion/rt_vs_ilc_latencia.py cuando tau_a y la latencia completa
    esten medidas de verdad, no supuestas.)
"""
import argparse
import csv
import os
import sys
import time
from collections import deque
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "ilc"))
from fz_ilc import ControlFzILC, PASOS_POR_MM_Y, cargar_k_asumido  # noqa: E402

EJE_VERTICAL = "Y"  # CONFIRMADO (ver control/ilc/README.md): Y = vertical = Fz
DT_CONTROL_S = 0.010  # 10 ms -- bien menor al watchdog de 80 ms del firmware; AJUSTAR si hace falta
N_MEDIANA = 5  # filtro de errores de bit SPI con el servo activo (ver bloqueo 5 arriba)


class ClienteVelocidadESP32:
    """Cliente serial del comando SET_VEL (patch control_velocidad_continua.patch).
    *** NO PROBADO: el patch no esta flasheado. *** SET_VEL SI responde (OK o
    BUSY) -- confirmado leyendo communication.h/main.cpp: primary_task es
    siempre communication_rx -> dispatch -> communication_tx, igual que
    cualquier otro comando (MANUAL, GOTO, etc.), handle_velocity_command no es
    la excepcion. set_vel() lee y descarta esa respuesta (si llega BUSY, el eje
    seguia ocupado por otro comando -- no deberia pasar en el lazo normal,
    pero se registra un aviso si pasa). RTT esperado ~6 ms (mismo mecanismo que
    PING/PONG, medido 5.97 ms, ver reportes/) -- VERIFICAR en banco que no se
    degrada con el servo en movimiento antes de confiar en el presupuesto de
    dt_control_s=10 ms."""

    def __init__(self, puerto="/dev/ttyUSB0", baudrate=115200, timeout=0.05):
        import serial  # import tardio: este modulo se puede inspeccionar sin pyserial instalado
        self.ser = serial.Serial(puerto, baudrate, timeout=timeout)
        time.sleep(2.0)  # reset del ESP32 al abrir el puerto (CP2102, ver reportes/)

    def set_vel(self, eje, pasos_por_seg):
        frame = f"<SET_VEL:{eje}:{int(round(pasos_por_seg))}>\n"
        self.ser.write(frame.encode("ascii"))
        resp = self.ser.readline().decode("ascii", errors="replace").strip()
        if resp.startswith("BUSY"):
            print(f"AVISO: SET_VEL eje {eje} respondio BUSY (eje ocupado por otro comando)")
        elif not resp.startswith("OK"):
            print(f"AVISO: SET_VEL eje {eje} respuesta inesperada: {resp!r} (timeout o desync?)")

    def detener(self, eje):
        self.set_vel(eje, 0)

    def cerrar(self):
        self.ser.close()


class LectorFzFiltrado:
    """Envuelve pruebas/leer_ads1256_fz.ADS1256 con mediana causal de N_MEDIANA
    muestras (ver CLAUDE.md 2026-11-05 ~16:00: los picos son errores de bit del
    SPI, aislados, la mediana los elimina sin agregar retardo relevante)."""

    def __init__(self, n_mediana=N_MEDIANA):
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pruebas"))
        from leer_ads1256_fz import ADS1256, volts_a_newtons  # import tardio: requiere RPi.GPIO/spidev
        self._volts_a_newtons = volts_a_newtons
        self.adc = ADS1256()
        self.buffer = deque(maxlen=n_mediana)

    def leer_n(self):
        v = self.adc.leer_volts()
        n = self._volts_a_newtons(v)
        self.buffer.append(n)
        return sorted(self.buffer)[len(self.buffer) // 2]

    def cerrar(self):
        self.adc.cerrar()


def correr_lazo(peso_sujeto_n, n_ciclos, kp, protesis, referencia="gutenberg",
                 puerto_esp32="/dev/ttyUSB0", carpeta_log="control/telemetria/registros"):
    k_asumido = cargar_k_asumido(protesis)
    pasos_por_n = PASOS_POR_MM_Y / k_asumido
    ctrl = ControlFzILC(peso_sujeto_n, duracion_s=3.69, rigidez_n_por_mm=k_asumido, referencia=referencia)

    nombre_log = os.path.join(carpeta_log, f"{datetime.now():%Y-%m-%d_%H%M%S}_fz.csv")
    os.makedirs(carpeta_log, exist_ok=True)

    esp32 = ClienteVelocidadESP32(puerto_esp32)
    lector = LectorFzFiltrado()
    try:
        with open(nombre_log, "w", newline="") as f_csv:
            w = csv.writer(f_csv)
            w.writerow(["t", "ciclo", "r", "delta", "r_corregida", "F_med", "e", "u"])

            for ciclo in range(n_ciclos):
                t_muestras, f_muestras = [], []
                t_ciclo0 = time.monotonic()
                n_muestras = int(round(ctrl.duracion_s / DT_CONTROL_S))
                for i in range(n_muestras):
                    t_rel = i * DT_CONTROL_S
                    r_bw = ctrl.ref_bw[int(i * ctrl.n / n_muestras)]
                    r_n = r_bw / 100.0 * peso_sujeto_n
                    delta_n = ctrl.ilc.delta[int(i * ctrl.n / n_muestras)]  # correccion del ciclo anterior
                    r_corregida = r_n + delta_n

                    f_med = lector.leer_n()
                    e = r_corregida - f_med
                    u_pasos_s = kp * e * pasos_por_n
                    esp32.set_vel(EJE_VERTICAL, u_pasos_s)

                    w.writerow([f"{t_rel:.4f}", ciclo, f"{r_n:.2f}", f"{delta_n:.2f}",
                                f"{r_corregida:.2f}", f"{f_med:.2f}", f"{e:.2f}", f"{u_pasos_s:.1f}"])
                    f_csv.flush()
                    t_muestras.append(t_rel)
                    f_muestras.append(f_med)

                    t_objetivo = t_ciclo0 + (i + 1) * DT_CONTROL_S
                    espera = t_objetivo - time.monotonic()
                    if espera > 0:
                        time.sleep(espera)

                esp32.detener(EJE_VERTICAL)
                rms = ctrl.registrar_medicion(t_muestras, f_muestras)
                print(f"ciclo {ciclo}: RMS error = {rms:.2f} N")
    finally:
        esp32.detener(EJE_VERTICAL)
        esp32.cerrar()
        lector.cerrar()


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--peso_sujeto_n", type=float, required=True)
    ap.add_argument("--n_ciclos", type=int, default=5)
    ap.add_argument("--kp", type=float, default=15.0,
                     help="ganancia proporcional [1/s]. Default 15 = recomendacion de partida "
                          "2026-11-08 (ver reportes/2026-11-08_avance_sin_rpi.md Sec.3 y "
                          "control/simulacion/barrido_kp_2026-11-08.png); re-elegir cuando tau_a "
                          "y la latencia completa esten medidas, no solo supuestas.")
    ap.add_argument("--protesis", default="pie_pasivo_1 (la unica probada hasta ahora)")
    ap.add_argument("--referencia", default="gutenberg")
    ap.add_argument("--puerto_esp32", default="/dev/ttyUSB0")
    a = ap.parse_args()
    print(__doc__)
    raise SystemExit(
        "Este script NO se autoejecuta: el comando SET_VEL no esta flasheado en el firmware "
        "todavia (ver bloqueo 1 en el docstring). Cuando lo este y se haya probado en banco "
        "(control/firmware/README.md, protocolo de prueba), quitar este SystemExit."
    )
