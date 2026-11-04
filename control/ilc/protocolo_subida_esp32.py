"""Cliente serial del protocolo de trayectoria del firmware actual
(Codigo ESP32 MOV/platformIO_control_trayectoria_v1/src/communication.h).
Sube un ciclo (dt_ms, dx, dy, dk por punto) y lo ejecuta con RUN.

*** NO PROBADO EN HARDWARE *** -- escrito sin RPi ni ESP32 a mano (2026-11-04),
solo contra lo que dice el codigo del firmware (communication.h,
configurable_motion_data.h, main.cpp). Antes de usarlo con el simulador real:
revisar que el framing y los nombres de comando no hayan cambiado, y probarlo
primero con una trayectoria corta e inocua (ej. todo ceros) con el simulador
despejado y alguien listo para cortar la alimentacion de los motores.

Protocolo (de communication.h):
  - Frame RX (RPi -> ESP32): "<COMANDO:p1:p2:...>\\n"
  - Frame TX (ESP32 -> RPi): "COMANDO:p1:p2:...\\n" (sin '<' ni '>')
  - TRAJ_BEGIN:1:N  -> reserva N puntos en el buffer "gait" (modo 1); responde TRAJ_READY
  - TRAJ_POINT:i:dt_ms:dx:dy:dk -> un punto (i = indice 0..N-1); responde ACK:i
  - TRAJ_END -> responde TRAJ_STORED
  - RUN:modo -> ejecuta la trayectoria cargada; responde RUNNING (bloquea hasta
    que el firmware arma el Traj_state, ver main.cpp linea ~618)
  - TRAJ_STATUS -> responde IDLE/ACTIVE/PAUSED/FINISHED (no implementado aqui)
N maximo: 500 (MAX_DATA_LENGTH, configurable_motion_data.h).
"""
import time

try:
    import serial
except ImportError:
    serial = None  # el modulo se puede importar e inspeccionar sin pyserial instalado


class ClienteTrayectoriaESP32:
    def __init__(self, puerto="/dev/ttyUSB0", baudrate=115200, timeout=2.0):
        if serial is None:
            raise RuntimeError("pyserial no esta instalado (pip install pyserial)")
        self.ser = serial.Serial(puerto, baudrate, timeout=timeout)
        time.sleep(2.0)  # reset del ESP32 al abrir el puerto (comun en placas USB-serial)

    def _enviar(self, comando, *params):
        frame = "<" + comando + "".join(f":{p}" for p in params) + ">\n"
        self.ser.write(frame.encode("ascii"))

    def _leer_respuesta(self):
        linea = self.ser.readline().decode("ascii", errors="replace").strip()
        if not linea:
            raise TimeoutError("sin respuesta del ESP32 (timeout)")
        partes = linea.split(":")
        return partes[0], [int(x) for x in partes[1:]]

    def subir_trayectoria(self, dt_ms, dx_pasos, dy_pasos, dk_pasos, modo=1):
        """dt_ms, dx_pasos, dy_pasos, dk_pasos: listas/arrays de la misma
        longitud N <= 500. modo=1 -> buffer 'gait' (el unico que usa RUN hoy,
        ver main.cpp handle_execute_trajectory_command)."""
        n = len(dt_ms)
        if not (n == len(dx_pasos) == len(dy_pasos) == len(dk_pasos)):
            raise ValueError("dt_ms, dx, dy, dk deben tener la misma longitud")
        if n > 500:
            raise ValueError(f"{n} puntos > 500 (MAX_DATA_LENGTH del firmware)")

        self._enviar("TRAJ_BEGIN", modo, n)
        cmd, _ = self._leer_respuesta()
        if cmd != "TRAJ_READY":
            raise RuntimeError(f"esperaba TRAJ_READY, llego {cmd}")

        for i in range(n):
            self._enviar("TRAJ_POINT", i, int(dt_ms[i]), int(dx_pasos[i]), int(dy_pasos[i]), int(dk_pasos[i]))
            cmd, params = self._leer_respuesta()
            if cmd != "ACK" or params[0] != i:
                raise RuntimeError(f"ACK inesperado en punto {i}: {cmd}:{params}")

        self._enviar("TRAJ_END")
        cmd, _ = self._leer_respuesta()
        if cmd != "TRAJ_STORED":
            raise RuntimeError(f"esperaba TRAJ_STORED, llego {cmd}")

    def ejecutar(self, modo=1):
        """RUN: bloquea en el firmware hasta que arranca (vTaskDelay interno);
        aqui el timeout del puerto serial debe ser mayor a esa espera."""
        self._enviar("RUN", modo)
        cmd, _ = self._leer_respuesta()
        if cmd == "ERROR":
            raise RuntimeError("RUN devolvio ERROR (ver limites de carrera o Traj_state != TRAJ_IDLE)")
        if cmd != "RUNNING":
            raise RuntimeError(f"esperaba RUNNING, llego {cmd}")

    def cerrar(self):
        self.ser.close()


if __name__ == "__main__":
    print(__doc__)
    print("Este script no se autoejecuta contra hardware: no hay ESP32 conectado en esta sesion.")
    print("Para probarlo: ClienteTrayectoriaESP32('/dev/ttyUSB0').subir_trayectoria(...) y luego .ejecutar().")
