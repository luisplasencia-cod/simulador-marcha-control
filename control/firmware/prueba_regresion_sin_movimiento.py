"""Regresion del firmware SIN MOVER NINGUN EJE (2026-11-10).

Objetivo: comprobar que, tras flashear el parche SET_VEL (v1/v2), el firmware sigue
comportandose igual que el original en lo que NO usa SET_VEL, y que SET_VEL responde
como se espera -- enviando SOLO comandos que no generan movimiento.

Comandos que manda (ninguno mueve un eje):
  PING                -> PONG
  GET_POSITION        -> posiciones (deben ser iguales antes y despues)
  TRAJ_STATUS         -> IDLE
  SET_VEL:1:0         -> OK   (velocidad 0 = "parar", eje parado: no hace nada)  [solo parche]
  SET_VEL:9:0         -> BUSY (eje inexistente; el codigo responde BUSY, no ERROR) [solo parche]
  GET_POSITION        -> igual que el primero

NUNCA manda SET_VEL con velocidad distinta de 0, ni MANUAL, GOTO, RUN, HOME.
Abrir el puerto reinicia el ESP32 (DTR/RTS): es el comportamiento conocido del rig, no un
movimiento ordenado (el contador de posicion vuelve a 0).

Uso:  .venv/bin/python control/firmware/prueba_regresion_sin_movimiento.py [--sin_set_vel]
  --sin_set_vel : para el firmware ORIGINAL (no tiene SET_VEL).
"""
import argparse
import json
import sys
import time

import serial

ap = argparse.ArgumentParser()
ap.add_argument("--puerto", default="/dev/ttyUSB0")
ap.add_argument("--sin_set_vel", action="store_true")
ap.add_argument("--salida", default="")
a = ap.parse_args()

ser = serial.Serial(a.puerto, 115200, timeout=1.0)
time.sleep(2.5)  # reinicio por apertura del puerto
ser.reset_input_buffer()


def pedir(cmd):
    ser.reset_input_buffer()
    ser.write(f"<{cmd}>".encode())
    return ser.readline().decode(errors="replace").strip()


resultados, ok_total = [], True


def chequeo(nombre, cmd, esperado_prefijo):
    global ok_total
    r = pedir(cmd)
    ok = r.startswith(esperado_prefijo)
    ok_total &= ok
    resultados.append({"prueba": nombre, "cmd": cmd, "respuesta": r, "esperado": esperado_prefijo, "ok": ok})
    print(f"[{'OK ' if ok else 'MAL'}] {cmd:<14} -> {r!r}  (esperado: {esperado_prefijo!r})")
    return r


chequeo("ping", "PING", "PONG")
pos0 = pedir("GET_POSITION")
print(f"      posicion inicial: {pos0!r}")
chequeo("trayectoria_idle", "TRAJ_STATUS", "IDLE")
if not a.sin_set_vel:
    chequeo("set_vel_cero_eje_parado", "SET_VEL:1:0", "OK")
    chequeo("set_vel_eje_invalido", "SET_VEL:9:0", "BUSY")
pos1 = pedir("GET_POSITION")
mov = pos0 != pos1
ok_total &= not mov
resultados.append({"prueba": "posicion_sin_cambio", "antes": pos0, "despues": pos1, "ok": not mov})
print(f"[{'OK ' if not mov else 'MAL'}] posicion sin cambio: {pos0!r} -> {pos1!r}")
ser.close()

if a.salida:
    with open(a.salida, "w") as f:
        json.dump({"ok_total": ok_total, "resultados": resultados}, f, indent=1)
print("\nRESULTADO:", "TODO OK" if ok_total else "HAY FALLAS")
sys.exit(0 if ok_total else 1)
