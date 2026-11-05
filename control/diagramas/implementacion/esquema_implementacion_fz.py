"""Diagrama de implementacion real (hardware/software) del lazo hibrido RT+ILC para Fz:
AMTI -> ADS1256 -> Raspberry Pi (Kp + ILC) -> USB serial (SET_VEL, propuesto) -> ESP32 -> driver A6-750RS -> servomotor vertical.

Es el diagrama COMPLEMENTARIO al matematico (control/diagramas/diagrama_lazo_hibrido.py):
ese dibuja r(t), e(t), Kp, la planta -- este dibuja DONDE vive cada pieza fisica y por
que cable/protocolo se conecta. NADA de la parte SET_VEL esta probado en hardware real
(parche de firmware sin aplicar -- ver control/firmware/README.md).

Uso: python esquema_implementacion_fz.py [--salida DIR]
"""
import argparse
import os
import schemdraw
import schemdraw.elements as elm

schemdraw.use('matplotlib')
_ap = argparse.ArgumentParser()
_ap.add_argument("--salida", default="salida")
_a = _ap.parse_args()
os.makedirs(_a.salida, exist_ok=True)
OUT = os.path.join(_a.salida, "esquema_implementacion_fz")

RED = '#c62828'
BLUE = '#1565c0'
ORANGE = '#e65100'
GREEN = '#2e7d32'

d = schemdraw.Drawing(show=False)
d.config(unit=3, fontsize=12, lw=1.8)


def text(xy, s, size=9, color='black', halign='left', valign='top'):
    d.add(elm.Label().at(xy).label(s, fontsize=size, color=color, halign=halign, valign=valign))


S = 2.2
H = 3 * 2 * S + 1  # alto comun para alinear bloques de pines

# ---------------- AMTI ----------------
amti = elm.Ic(pins=[
    elm.IcPin(name='Señal Fz', anchorname='FZ', side='right', slot='2/2'),
    elm.IcPin(name='Referencia', anchorname='REF', side='right', slot='1/2'),
], size=(9, H)).at((-46, 8.6)).anchor('FZ')
d.add(amti)
AL = amti.FZ.x - 9.5
text((AL + 4.5, amti.FZ.y + 1.6), 'AMTI Gen5\n(plataforma de fuerza)', size=10, halign='center', valign='bottom')
text((AL + 0.3, amti.REF.y - 0.6),
     'Salida analógica single-ended.\n'
     'Escala Fz: 1.7665 mV/N\n'
     '(OPT SC serie 4306, ganancia 2000)\n'
     'máx. 2000 N → 3.53 V',
     size=9)

# ---------------- ADS1256 ----------------
ads = elm.Ic(pins=[
    elm.IcPin(name='AIN0', anchorname='AIN0', side='left', slot='2/2'),
    elm.IcPin(name='GND (junto a AIN0)', anchorname='AGND', side='left', slot='1/2'),
    elm.IcPin(name='5V', anchorname='V5', side='right', slot='5/5'),
    elm.IcPin(name='SCLK', anchorname='SCLK', side='right', slot='4/5'),
    elm.IcPin(name='DIN', anchorname='DIN', side='right', slot='3/5'),
    elm.IcPin(name='DOUT', anchorname='DOUT', side='right', slot='2/5'),
    elm.IcPin(name='DRDY/CS/PDWN', anchorname='MISC', side='right', slot='1/5'),
], size=(13, H)).at((amti.FZ.x + 9.5, amti.FZ.y)).anchor('AIN0')
d.add(ads)
text((ads.AIN0.x + 6.5, ads.AIN0.y + 1.6), 'ADS1256 (RPi)\nADC 24-bit, SPI0', size=10, halign='center', valign='bottom')
text((ads.AIN0.x + 1.0, ads.MISC.y - 1.0),
     'VREF = 2.5 V (chip ADR03B)\n'
     'Full-scale PGA=1 = 5 V\n'
     '→ 3.53 V del AMTI al 71%',
     size=9)
d.add(elm.Line().at(amti.FZ).right().tox(ads.AIN0))
d.add(elm.Line().at(amti.REF).right().tox(ads.AGND))

# ---------------- RASPBERRY PI ----------------
rpi = elm.Ic(pins=[
    elm.IcPin(name='SPI0 (GPIO 8/9/10/11)', anchorname='SPI', side='left', slot='3/3'),
    elm.IcPin(name='DRDY = GPIO17', anchorname='DRDY', side='left', slot='2/3'),
    elm.IcPin(name='3.3V = PDWN', anchorname='V33', side='left', slot='1/3'),
    elm.IcPin(name='USB (ESP32)', anchorname='USB', side='right', slot='1/1'),
], size=(16, H)).at((ads.V5.x + 9.0, ads.V5.y)).anchor('SPI')
d.add(rpi)
RL = rpi.SPI.x - 0.5
RR = rpi.USB.x + 0.5
text(((RL + RR) / 2, rpi.SPI.y + 1.6), 'RASPBERRY PI\n(el "cerebro": calcula Kp·e(t) y el ILC)', size=10, halign='center', valign='bottom')
text((RL + 0.4, rpi.V33.y - 0.6),
     'Corre:\n'
     '• lectura ADS1256 (SPI, 1000 SPS)\n'
     '• control/ilc/fz_ilc.py (ILC ciclo a ciclo)\n'
     '• Kp·e(t) en tiempo real -- NUEVO,\n'
     '  requiere el parche SET_VEL (abajo)\n'
     '• control/ilc/protocolo_subida_esp32.py\n'
     '  (TRAJ_* -- ya existe, SIN probar)\n\n'
     'Nada de esto corrió nunca contra el\n'
     'ESP32 real ni el ADS1256 real en esta\n'
     'sesión (sin RPi disponible).',
     size=9, color=RED)
for a, b in ((rpi.SPI, ads.SCLK), (rpi.DRDY, ads.MISC), (rpi.V33, ads.MISC)):
    pass  # las 3 lineas de arriba se resumen en una sola linea de bus abajo
d.add(elm.Line().at(ads.SCLK).right().tox(rpi.SPI))
d.add(elm.Line().at(ads.DOUT).right(1.0).up(0.6).right().tox(rpi.DRDY))
d.add(elm.Line().at(ads.MISC).right(0.5).down(0.6).right().tox(rpi.V33))

# ---------------- CABLE SERIAL (lo nuevo) ----------------
d.add(elm.Line().at(rpi.USB).right(2.0))
d.add(elm.Arrow().right(2.4).label('USB serie, 115200 baud\n(protocolo de texto <CMD:p1:p2>)', loc='top', fontsize=9, ofst=0.3))
text((rpi.USB.x + 3.0, rpi.USB.y - 1.1),
     'Tramas que ya existen: PING/PONG, GET_POSITION,\n'
     'TRAJ_BEGIN/POINT/END, RUN/PAUSE/ABORT.\n\n'
     'NUEVO (propuesto, NO aplicado):\n'
     'SET_VEL:eje:pasos_por_seg_con_signo\n'
     '→ OK / BUSY / ERROR. pasos_por_seg=0 detiene.\n'
     'Watchdog: 80 ms sin SET_VEL → el eje se para solo.',
     size=9, color=ORANGE)

# ---------------- ESP32 ----------------
esp = elm.Ic(pins=[
    elm.IcPin(name='USB (Serial0)', anchorname='USB', side='left', slot='1/1'),
    elm.IcPin(name='GPIO19 = Y_STEP', anchorname='STEP', side='right', slot='3/3'),
    elm.IcPin(name='GPIO21 = Y_DIR', anchorname='DIR', side='right', slot='2/3'),
    elm.IcPin(name='GPIO18 = Y_BRAKE', anchorname='BRAKE', side='right', slot='1/3'),
], size=(14, H)).at((rpi.USB.x + 11.0, rpi.USB.y)).anchor('USB')
d.add(esp)
EL = esp.USB.x - 0.5
ER = esp.STEP.x + 0.5
text(((EL + ER) / 2, esp.USB.y + 1.6), 'ESP32\n(platformIO_control_trayectoria_v1)', size=10, halign='center', valign='bottom')
text((EL + 0.4, esp.BRAKE.y - 0.6),
     'Hoy (firmware actual): obedece MANUAL/\n'
     'GOTO/trayectorias -- movimientos finitos\n'
     'por eje, sin velocidad continua.\n\n'
     'Con el parche SET_VEL (propuesto):\n'
     'axis_set_velocity() genera pasos a\n'
     'frecuencia variable; para primero el eje\n'
     'si cambia de sentido (no invierte DIR\n'
     'con el motor girando).\n\n'
     'Eje Y = vertical = Fz (confirmado en\n'
     'hardware_config.h, comentario del pin\n'
     'Y_DIR_SETUP_US). LIMIT_Y_MIN=GPIO34,\n'
     'LIMIT_Y_MAX=GPIO35 (no dibujados aquí).',
     size=9)
d.add(elm.Line().at(rpi.USB).right().tox(esp.USB))

# ---------------- DRIVER A6-750RS ----------------
drv = elm.Ic(pins=[
    elm.IcPin(name='PUL+/PUL−', anchorname='PUL', side='left', slot='3/3'),
    elm.IcPin(name='DIR+/DIR−', anchorname='DIR', side='left', slot='2/3'),
    elm.IcPin(name='Encoder (interno, 17-bit)', anchorname='ENC', side='left', slot='1/3'),
    elm.IcPin(name='U/V/W + encoder', anchorname='MOT', side='right', slot='1/1'),
], size=(14, H)).at((esp.STEP.x + 11.0, esp.STEP.y)).anchor('PUL')
d.add(drv)
text((drv.PUL.x + 7.0, drv.PUL.y + 1.6), 'DRIVER A6-750RS\n(STEPPERONLINE, Pulso/Dir)', size=10, halign='center', valign='bottom')
text((drv.MOT.x - 6.5, drv.ENC.y - 0.6),
     'Lazo de velocidad/posición CERRADO\n'
     'dentro del driver (su propio encoder) --\n'
     'el ESP32 solo manda pulsos, no sabe la\n'
     'posición real salvo que la pida.\n\n'
     'Alimentación de potencia (220 VAC) y freno:\n'
     'ya cableados y funcionando -- fuera de\n'
     'alcance de este diagrama (ver foto real).',
     size=9)
d.add(elm.Line().at(esp.STEP).right().tox(drv.PUL))
d.add(elm.Line().at(esp.DIR).right().tox(drv.DIR))
d.add(elm.Line().at(esp.BRAKE).right(1.0).down(1.4).right().tox(drv.ENC))

# ---------------- MOTOR ----------------
MX = drv.MOT.x + 4.0
d.add(elm.Line().at(drv.MOT).right().tox((MX, drv.MOT.y)))
d.add(elm.Motor().right(3.0).label('A6M80-750H2A1-M17\n750 W, 3000 rpm, 2.39 Nm\n17-bit encoder absoluto\neje VERTICAL (husillo+cadena)', loc='bottom', fontsize=9, ofst=0.5))

# ---------------- TITULO ----------------
TOP = amti.FZ.y + 4.6
text((AL, TOP), 'Implementación real del lazo Fz: AMTI → ADS1256 → RPi → (SET_VEL) → ESP32 → driver → servomotor vertical', size=15)
text((AL, TOP - 1.0), 'Todo lo de la izquierda del ESP32 corre en software (RPi); todo lo de la derecha es hardware ya instalado.', size=10, color=BLUE)

# ---------------- NOTA ROJA GENERAL ----------------
NY = amti.REF.y - 6.0
text((AL, NY),
     'ESTADO (2026-11-05): este diagrama documenta una ARQUITECTURA PROPUESTA, no algo verificado funcionando.\n'
     '• AMTI→ADS1256→RPi: cableado físicamente por Luis (2026-11-02), lectura por SPI funcionando en el RPi, pero sin probar junto con el ESP32 en esta sesión (sin RPi a mano).\n'
     '• RPi→ESP32 con SET_VEL: el comando y el parche de firmware existen solo como diseño + .patch verificado con "git apply --check" -- NO compilado, NO flasheado, NO probado.\n'
     '• ESP32→driver→motor: hardware existente del simulador, ya funciona con MANUAL/GOTO/trayectorias (sin cambios de esta propuesta).',
     size=10, color=RED)

text((AL, NY - 3.2),
     'FUENTES DE CADA DATO:\n'
     '• AMTI escala, ADS1256 pines y VREF: esquemas/amti_ads1256_rpi/CONFIGURACION_ACTUAL.md (medido/verificado por Luis y Michael, 2026-11-02).\n'
     '• Pines Y_STEP/Y_DIR/Y_BRAKE, LIMIT_Y_*: Codigo ESP32 MOV/platformIO_control_trayectoria_v1/src/hardware_config.h (leído del código fuente).\n'
     '• Protocolo serie (PING, TRAJ_*, etc.): Codigo ESP32 MOV/.../communication.h (leído del código fuente).\n'
     '• SET_VEL, watchdog 80 ms: control/firmware/control_velocidad_continua.patch (diseño propio, NO aplicado ni probado).\n'
     '• Modelo y specs del driver/motor (A6-750RS / A6M80-750H2A1-M17): manual STEPPERONLINE A6 Series 750W AC Servo Motor Kit (buscado en internet 2026-11-05,\n'
     '  ver control/diagramas/referencias/README.md) -- marca STEPPERONLINE, no Panasonic (corrige una suposición informal anterior en HISTORIAL.md).\n'
     '• "Eje Y = vertical": CONFIRMADO por comentario del código fuente (ver control/ilc/README.md), no por memoria de Luis.',
     size=9)

text((AL, NY - 8.0),
     'DISCREPANCIA A VERIFICAR (no resuelta aquí): el manual del kit STEPPERONLINE A6-RS750H2A1-M17 que se encontró en internet NO menciona freno en\n'
     'el motor A6M80-750H2A1-M17 -- pero el firmware SÍ maneja un freno por software (Y_BRAKE_PIN = GPIO18, Y_BRAKE_LOCKED/RELEASED). Puede ser que el\n'
     'motor real instalado sea una variante con freno no listada en el manual genérico encontrado, o que el freno sea una pieza mecánica aparte controlada\n'
     'por ese GPIO vía relé. No se puede confirmar sin ver la etiqueta física del motor del simulador -- queda pendiente de Luis.',
     size=9, color=ORANGE)

d.save(OUT + '.png', dpi=170)
d.save(OUT + '.svg')
print('ok')
