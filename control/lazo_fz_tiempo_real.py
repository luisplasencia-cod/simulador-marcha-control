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
# SIGNO (2026-11-10): en el firmware, SET_VEL usa la misma convencion que MANUAL:
# signo + sobre Y = SUBIR (medido en el Ensayo 0, <MANUAL:1:4000> = +50 mm hacia arriba).
# Para AUMENTAR la fuerza hay que BAJAR el eje => velocidad NEGATIVA cuando e = r - F > 0.
# Sin este -1 el lazo seria realimentacion POSITIVA (error de fuerza -> sube -> fuerza cae).
SIGNO_ERROR_A_VELOCIDAD = -1
# Saturacion de seguridad de |velocidad| [pasos/s]. ELECCION DE DISEÑO (no medida): 1600 pasos/s
# = 20 mm/s en Y = la velocidad fija que ya usa MANUAL en los ensayos. Bajarla para las primeras corridas.
V_MAX_PASOS_S = 1600
# Sensor "muerto": si las ultimas N_MEDIANA lecturas crudas son IDENTICAS (ruido real sigma~0.9 N, imposible
# que 5 seguidas coincidan), el ADC esta desconectado/congelado (ya paso: 0.0 exacto el 2026-11-05).


PASOS_MM = float(PASOS_POR_MM_Y)
V_RAPIDA = 1600      # pasos/s en la aproximacion lejos del contacto (20 mm/s)
V_LENTA = 400        # pasos/s en los ultimos ZONA_LENTA_MM antes del hueco declarado (5 mm/s)
ZONA_LENTA_MM = 30.0
SALTO_MAX_N = 30.0   # |dF| entre muestras consecutivas filtradas: mas que eso = lectura anomala
F_NEG_MAX_N = -30.0


class ClienteVelocidadESP32:
    """Cliente serial de SET_VEL. PROBADO 2026-11-10 (firmware v3 con espressif32 7.0.1): SET_VEL responde OK,
    RTT ~5.8-6.4 ms, + sube Y (confirmado por Luis), watchdog 80 ms (32 pasos tras un solo SET_VEL).
    Abrir el puerto reinicia el ESP32: se espera 6 s (con 2.5 s se leyo basura de arranque)."""

    def __init__(self, puerto="/dev/ttyUSB0", baudrate=115200, timeout=0.2, espera_arranque_s=6.0):
        import serial  # import tardio: este modulo se puede inspeccionar sin pyserial instalado
        self.ser = serial.Serial(puerto, baudrate, timeout=timeout)
        time.sleep(espera_arranque_s)
        self.ser.reset_input_buffer()
        self.fallos = 0
        if self._cmd("PING") != "PONG" and self._cmd("PING") != "PONG":
            raise RuntimeError("ESP32 no responde PING tras abrir el puerto")

    def _cmd(self, cmd):
        self.ser.reset_input_buffer()
        self.ser.write(f"<{cmd}>".encode("ascii"))
        return self.ser.readline().decode("ascii", errors="replace").strip()

    def set_vel(self, eje, pasos_por_seg):
        resp = self._cmd(f"SET_VEL:{eje}:{int(round(pasos_por_seg))}")
        if resp.startswith("OK"):
            self.fallos = 0
        else:
            self.fallos += 1
            print(f"AVISO: SET_VEL eje {eje} respuesta {resp!r} (fallos seguidos: {self.fallos})")
            if self.fallos >= 3:
                raise RuntimeError("3 respuestas seguidas distintas de OK a SET_VEL: se aborta")
        return resp

    def detener(self, eje):
        return self._cmd(f"SET_VEL:{eje}:0")

    def pos_y(self):
        r = self._cmd("GET_POSITION")  # POSITION:x:y:k, contador de pasos ORDENADOS (no medida)
        return int(r.split(":")[2])

    def subir_pasos(self, pasos):
        """Sube (pasos>0) con MANUAL por tramos de <=800 pasos, igual que la subida gruesa del Ensayo A."""
        while pasos > 0:
            p = min(pasos, 800)
            r = self._cmd(f"MANUAL:1:{p}")
            if not r.startswith("OK"):
                raise RuntimeError(f"MANUAL:1:{p} respondio {r!r}")
            pasos -= p
            time.sleep(p / 1600 + 0.3)

    def cerrar(self):
        self.ser.close()


class LectorFzFiltrado:
    """Envuelve pruebas/leer_ads1256_fz.ADS1256: tara (Fz=0 sin contacto) + mediana causal de N_MEDIANA muestras
    (los picos son errores de bit del SPI, aislados; CLAUDE.md 2026-11-05). Fz > 0 = carga (convencion del Ensayo A)."""

    def __init__(self, n_mediana=N_MEDIANA):
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pruebas"))
        from leer_ads1256_fz import ADS1256, volts_a_newtons  # import tardio: requiere RPi.GPIO/spidev
        self._volts_a_newtons = volts_a_newtons
        self.adc = ADS1256()
        self.buffer = deque(maxlen=n_mediana)
        self.f0 = 0.0

    def tarar(self, n=200):
        """Offset del ADC con el eje QUIETO y sin contacto (deriva ~10 N entre corridas: se tara en cada una)."""
        muestras = sorted(self._volts_a_newtons(self.adc.leer_volts()) for _ in range(n))
        self.f0 = muestras[len(muestras) // 2]
        return self.f0, muestras[len(muestras) // 20], muestras[-len(muestras) // 20]

    def leer_n(self):
        n = self._volts_a_newtons(self.adc.leer_volts())
        self.buffer.append(n)
        if len(self.buffer) == self.buffer.maxlen and len(set(self.buffer)) == 1:
            raise RuntimeError(f"Sensor de Fz congelado/desconectado: {self.buffer.maxlen} lecturas identicas "
                               f"({n:.2f} N). Se aborta y se detiene el eje.")
        return sorted(self.buffer)[len(self.buffer) // 2] - self.f0

    def cerrar(self):
        self.adc.cerrar()


class _PlantaSimulada:
    """SOLO para --simulado (probar la logica sin hardware): pie con rigidez k en contacto a `contacto_mm` de descenso."""

    def __init__(self, k_n_mm=25.0, contacto_mm=60.0, offset_n=-40.0):
        self.k, self.contacto_mm, self.offset_n = k_n_mm, contacto_mm, offset_n
        self.descenso_mm, self.contador, self.t = 0.0, 0, time.monotonic()
        self.v = 0.0

    def avanzar(self):
        t = time.monotonic()
        self.descenso_mm += -self.v * (t - self.t) / PASOS_MM   # v>0 sube
        self.contador += int(round(self.v * (t - self.t)))
        self.t = t

    def fuerza(self):
        self.avanzar()
        return self.k * max(0.0, self.descenso_mm - self.contacto_mm)


class ESP32Simulado:
    def __init__(self, planta): self.p = planta
    def set_vel(self, eje, v): self.p.avanzar(); self.p.v = v; return "OK"
    def detener(self, eje): self.p.avanzar(); self.p.v = 0.0; return "OK"
    def pos_y(self): self.p.avanzar(); return self.p.contador
    def subir_pasos(self, pasos): self.p.descenso_mm -= pasos / PASOS_MM; self.p.contador += pasos
    def cerrar(self): pass


class LectorSimulado:
    def __init__(self, planta, n_mediana=N_MEDIANA):
        import random
        self.p, self.rnd, self.f0 = planta, random.Random(1), 0.0
        self.buffer = deque(maxlen=n_mediana)

    def tarar(self, n=200):
        self.f0 = self.p.offset_n
        return self.f0, self.f0 - 1, self.f0 + 1

    def leer_n(self):
        n = self.p.fuerza() + self.p.offset_n + self.rnd.gauss(0, 0.9)
        self.buffer.append(n)
        return sorted(self.buffer)[len(self.buffer) // 2] - self.f0

    def cerrar(self): pass


def correr_lazo(peso_sujeto_n, n_ciclos, kp, protesis, fmax_n, hueco_mm, referencia="gutenberg",
                puerto_esp32="/dev/ttyUSB0", carpeta_log="control/telemetria/registros", v_max=V_MAX_PASOS_S,
                umbral_contacto_n=8.0, extra_mm=20.0, simulado=False, angulo_deg=None):
    k_asumido = cargar_k_asumido(protesis)
    pasos_por_n = PASOS_POR_MM_Y / k_asumido
    ctrl = ControlFzILC(peso_sujeto_n, duracion_s=3.69, rigidez_n_por_mm=k_asumido, referencia=referencia)

    marca = f"{datetime.now():%Y-%m-%d_%H%M%S}" + ("_SIM" if simulado else "")
    nombre_log = os.path.join(carpeta_log, f"{marca}_fz.csv")
    os.makedirs(carpeta_log, exist_ok=True)
    with open(nombre_log.replace(".csv", ".meta.txt"), "w") as m:
        m.write(f"peso_sujeto_n={peso_sujeto_n} n_ciclos={n_ciclos} kp={kp} protesis={protesis} k_asumido={k_asumido} "
                f"pasos_por_n={pasos_por_n:.3f} fmax_n={fmax_n} hueco_mm={hueco_mm} angulo_deg={angulo_deg} "
                f"v_max={v_max} umbral_contacto_n={umbral_contacto_n} extra_mm={extra_mm} simulado={simulado}\n")

    if simulado:
        planta = _PlantaSimulada(contacto_mm=hueco_mm - 5.0)   # el hueco declarado sobreestima 5 mm (como paso en el ensayo real)
        esp32, lector = ESP32Simulado(planta), LectorSimulado(planta)
    else:
        esp32, lector = ClienteVelocidadESP32(puerto_esp32), LectorFzFiltrado()

    descenso_mm = 0.0   # integral de la velocidad ORDENADA (no medida) desde el inicio
    motivo = "completado"
    try:
        f0, p5, p95 = lector.tarar()
        print(f"Tara: f0 = {f0:.2f} N (p5 {p5:.2f}, p95 {p95:.2f}). Debe estar SIN contacto y el eje quieto.")
        if p95 - p5 > 15.0:
            raise RuntimeError(f"Tara inestable (p5-p95 = {p95 - p5:.1f} N): ADC con errores, se aborta antes de mover")

        # ---- APROXIMACION: descenso con SET_VEL hasta detectar contacto (F > umbral) ----
        print(f"Aproximando: rapido {V_RAPIDA / PASOS_MM:.0f} mm/s hasta {hueco_mm - ZONA_LENTA_MM:.0f} mm, "
              f"luego {V_LENTA / PASOS_MM:.0f} mm/s; descenso maximo {hueco_mm + extra_mm:.0f} mm.")
        t_prev, previa = time.monotonic(), 0.0
        while True:
            if descenso_mm >= hueco_mm + extra_mm:
                raise RuntimeError("sin contacto en el descenso maximo")
            v = V_RAPIDA if descenso_mm < hueco_mm - ZONA_LENTA_MM else V_LENTA
            esp32.set_vel(EJE_VERTICAL, -v)
            ahora = time.monotonic(); descenso_mm += v * (ahora - t_prev) / PASOS_MM; t_prev = ahora
            f = lector.leer_n()
            if f < F_NEG_MAX_N or abs(f - previa) > SALTO_MAX_N:
                raise RuntimeError(f"lectura anomala en la aproximacion (F={f:.1f} N, previa {previa:.1f})")
            previa = f
            if f > umbral_contacto_n:
                esp32.detener(EJE_VERTICAL)
                print(f"CONTACTO a {descenso_mm:.1f} mm de descenso (hueco declarado {hueco_mm:.0f}): F = {f:.1f} N")
                break
            time.sleep(DT_CONTROL_S)
        time.sleep(0.3)

        # ---- LAZO CERRADO + ILC ----
        with open(nombre_log, "w", newline="") as f_csv:
            w = csv.writer(f_csv)
            w.writerow(["t", "ciclo", "r", "delta", "r_corregida", "F_med", "e", "u"])
            previa = lector.leer_n()
            for ciclo in range(n_ciclos):
                t_muestras, f_muestras = [], []
                t_ciclo0 = time.monotonic()
                t_prev = t_ciclo0
                n_muestras = int(round(ctrl.duracion_s / DT_CONTROL_S))
                for i in range(n_muestras):
                    t_rel = i * DT_CONTROL_S
                    idx = int(i * ctrl.n / n_muestras)
                    r_n = ctrl.ref_bw[idx] / 100.0 * peso_sujeto_n
                    delta_n = ctrl.ilc.delta[idx]  # correccion del ciclo anterior
                    r_corregida = r_n + delta_n

                    f_med = lector.leer_n()
                    if f_med > fmax_n:
                        raise RuntimeError(f"Fuerza {f_med:.1f} N > tope {fmax_n:.1f} N")
                    if f_med < F_NEG_MAX_N or abs(f_med - previa) > SALTO_MAX_N:
                        raise RuntimeError(f"lectura anomala (F={f_med:.1f} N, previa {previa:.1f} N)")
                    previa = f_med
                    e = r_corregida - f_med
                    u_pasos_s = SIGNO_ERROR_A_VELOCIDAD * kp * e * pasos_por_n
                    u_pasos_s = max(-v_max, min(v_max, u_pasos_s))
                    esp32.set_vel(EJE_VERTICAL, u_pasos_s)
                    ahora = time.monotonic(); descenso_mm += -u_pasos_s * (ahora - t_prev) / PASOS_MM; t_prev = ahora
                    if descenso_mm >= hueco_mm + extra_mm:
                        raise RuntimeError(f"descenso {descenso_mm:.1f} mm >= maximo {hueco_mm + extra_mm:.0f} mm")

                    w.writerow([f"{t_rel:.4f}", ciclo, f"{r_n:.2f}", f"{delta_n:.2f}",
                                f"{r_corregida:.2f}", f"{f_med:.2f}", f"{e:.2f}", f"{u_pasos_s:.1f}"])
                    f_csv.flush()
                    t_muestras.append(t_rel)
                    f_muestras.append(f_med)

                    espera = t_ciclo0 + (i + 1) * DT_CONTROL_S - time.monotonic()
                    if espera > 0:
                        time.sleep(espera)

                esp32.detener(EJE_VERTICAL)
                rms = ctrl.registrar_medicion(t_muestras, f_muestras)
                print(f"ciclo {ciclo}: RMS error = {rms:.2f} N  (descenso ordenado acumulado {descenso_mm:.1f} mm)")
    except BaseException as e:
        motivo = f"ABORTADO: {e!r}"
        print(motivo)
    finally:
        try:
            esp32.detener(EJE_VERTICAL)
            neto = esp32.pos_y()  # contador de pasos ordenados (no medido): neto<0 = quedo mas abajo que al inicio
            print(f"Retorno: contador Y = {neto} pasos -> subiendo {-neto} pasos")
            if neto < 0:
                esp32.subir_pasos(-neto)
            print(f"Contador Y final: {esp32.pos_y()} (debe ser ~0)")
        except BaseException as e2:
            print(f"!!! NO SE PUDO RETORNAR EL EJE AUTOMATICAMENTE ({e2!r}): SUBIRLO A MANO / con MANUAL")
        for obj in (esp32, lector):
            try: obj.cerrar()
            except Exception: pass
        print("Motivo de cierre:", motivo, "| log:", nombre_log)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--peso_sujeto_n", type=float, required=True,
                    help="escala de la curva objetivo [N]; para las primeras corridas usar valores BAJOS (p. ej. 100)")
    ap.add_argument("--n_ciclos", type=int, default=3)
    ap.add_argument("--kp", type=float, default=15.0,
                     help="ganancia proporcional [1/s]. Default 15 = recomendacion de partida 2026-11-08 "
                          "(reportes/2026-11-08_avance_sin_rpi.md Sec.3); re-elegir con la latencia completa medida.")
    ap.add_argument("--fmax_n", type=float, required=True, help="tope de fuerza [N] (obligatorio): lo supera -> se detiene y retorna")
    ap.add_argument("--hueco_mm", type=float, required=True, help="hueco suela->plataforma, MEDIDO por Luis para ESTA corrida")
    ap.add_argument("--hueco_remedido", action="store_true", help="confirma que el hueco se midio de nuevo antes de esta corrida")
    ap.add_argument("--angulo_deg", type=float, default=None, help="angulo sagital del pie (se registra; k depende de el)")
    ap.add_argument("--v_max", type=float, default=V_MAX_PASOS_S, help="saturacion de |velocidad| [pasos/s] en el lazo")
    ap.add_argument("--umbral_contacto_n", type=float, default=8.0)
    ap.add_argument("--extra_mm", type=float, default=20.0, help="descenso maximo = hueco + extra")
    ap.add_argument("--protesis", default="pie_pasivo_1 (la unica probada hasta ahora)")
    ap.add_argument("--referencia", default="gutenberg")
    ap.add_argument("--puerto_esp32", default="/dev/ttyUSB0")
    ap.add_argument("--simulado", action="store_true", help="planta y ESP32 simulados: prueba la logica SIN hardware")
    ap.add_argument("--ejecutar", action="store_true", help="sin esto solo imprime el plan y sale (no abre puertos)")
    a = ap.parse_args()
    k_as = cargar_k_asumido(a.protesis)
    print(f"PLAN: escala {a.peso_sujeto_n:.0f} N (pico ~{117.8 / 100 * a.peso_sujeto_n:.0f} N), {a.n_ciclos} ciclos, Kp={a.kp}, "
          f"k_asumido={k_as} N/mm -> {PASOS_POR_MM_Y / k_as:.2f} pasos/N, tope {a.fmax_n} N, hueco {a.hueco_mm} mm "
          f"(descenso max {a.hueco_mm + a.extra_mm:.0f} mm), v_max {a.v_max} pasos/s, simulado={a.simulado}")
    if not a.ejecutar:
        raise SystemExit("Modo PLAN: no se ejecuto nada. Agregar --ejecutar (y --hueco_remedido en real).")
    if not a.simulado and not a.hueco_remedido:
        raise SystemExit("Falta --hueco_remedido: el hueco se mide de nuevo antes de CADA corrida (regla de Luis).")
    correr_lazo(a.peso_sujeto_n, a.n_ciclos, a.kp, a.protesis, a.fmax_n, a.hueco_mm, a.referencia, a.puerto_esp32,
                v_max=a.v_max, umbral_contacto_n=a.umbral_contacto_n, extra_mm=a.extra_mm, simulado=a.simulado,
                angulo_deg=a.angulo_deg)
