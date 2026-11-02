"""Esquema: AMTI (salida Fz) -> ADS1256 -> Raspberry Pi, para el simulador de marcha (tesis Luis Plasencia).
Pinout, regla de AINCOM y rangos: datasheet TI ADS1256 Rev K (SBAS288K), leido y verificado el 2026-11-02.
Mapeo de pines ADS1256<->RPi: POR VERIFICAR (depende de la placa breakout exacta que tiene Luis).
Uso: python esquema_amti_ads1256_rpi.py [--salida DIR]      (necesita: pip install "schemdraw[matplotlib]")
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
OUT = os.path.join(_a.salida, "esquema_amti_ads1256_rpi")
RED, BLUE, GREEN, FG = '#ef5350', '#64b5f6', '#66bb6a', 'white'

d = schemdraw.Drawing(show=False)
d.config(unit=3, fontsize=12, lw=1.8, color=FG, bgcolor='black')


def text(xy, s, size=9, color=FG, halign='left', valign='top'):
    d.add(elm.Label().at(xy).label(s, fontsize=size, color=color, halign=halign, valign=valign))


S = 2.0
H = 7 * S  # alto comun AMTI / ADS1256 / RPi (pines alineados)

# ---------------- AMTI (sensor, izquierda) ----------------
AM_W = 11
amti = elm.Ic(pins=[
    elm.IcPin(name='Señal Fz', anchorname='SIG', side='right', slot='2/2'),
    elm.IcPin(name='Referencia', anchorname='REF', side='right', slot='1/2'),
], size=(AM_W, H)).at((-16, 10)).anchor('SIG')
d.add(amti)
AM_L = amti.SIG.x - (AM_W + 0.5)
text((AM_L + AM_W / 2, amti.SIG.y + 1.6), 'AMTI\namplificador de fuerza\n(salida analogica, canal Fz)', size=10, halign='center', valign='bottom')
text((AM_L + 0.4, amti.SIG.y - 0.6),
     'Escala (medida por Luis en el lab):\n'
     '1.7 V por cada 1000 N\n'
     'Maximo: 2000 N -> 3.4 V\n'
     '(dato propio, no de hoja de AMTI)',
     size=10)

# ---------------- ADS1256 (centro) ----------------
AD_X = amti.SIG.x + 9.0
AD_W = 15
ads = elm.Ic(pins=[
    elm.IcPin(name='AIN0', anchorname='AIN0', side='left', slot='7/7'),
    elm.IcPin(name='AINCOM', anchorname='AINCOM', side='left', slot='6/7'),
    elm.IcPin(name='AVDD', anchorname='AVDD', side='left', slot='5/7'),
    elm.IcPin(name='AGND', anchorname='AGND', side='left', slot='4/7'),
    elm.IcPin(name='VREFP', anchorname='VREFP', side='left', slot='3/7'),
    elm.IcPin(name='VREFN', anchorname='VREFN', side='left', slot='2/7'),
    elm.IcPin(name='(AIN1-7: libres)', anchorname='LIBRES', side='left', slot='1/7'),
    elm.IcPin(name='DVDD', anchorname='DVDD', side='right', slot='7/7'),
    elm.IcPin(name='DGND', anchorname='DGND', side='right', slot='6/7'),
    elm.IcPin(name='CS', anchorname='CS', side='right', slot='5/7'),
    elm.IcPin(name='DRDY', anchorname='DRDY', side='right', slot='4/7'),
    elm.IcPin(name='DOUT', anchorname='DOUT', side='right', slot='3/7'),
    elm.IcPin(name='DIN', anchorname='DIN', side='right', slot='2/7'),
    elm.IcPin(name='SCLK', anchorname='SCLK', side='right', slot='1/7'),
], size=(AD_W, H)).at((AD_X, amti.SIG.y)).anchor('AIN0')
d.add(ads)
AD_CX = AD_X + AD_W / 2
text((AD_CX, ads.AIN0.y + 1.6), 'ADS1256 (24 bit, 8 canales single-ended)\nplaca exacta de Luis: POR VERIFICAR', size=10, halign='center', valign='bottom', color=RED)
text((AD_X - 0.3, ads.LIBRES.y - 1.4),
     'Single-ended: señal -> AINx,\n'
     'comun -> AINCOM.\n'
     'AINCOM NO necesita ir a GND\n'
     '(puede ser la referencia propia\n'
     'del AMTI) — datasheet pag. con\n'
     '"use AINCOM as common input".',
     size=9, halign='left', color=BLUE)

d.add(elm.Line().at(amti.SIG).right().tox(ads.AIN0))
d.add(elm.Line().at(amti.REF).right().tox(ads.AINCOM))

# VREFP/VREFN -> fuente de referencia (en la propia placa; valor POR VERIFICAR)
d.push()
d.add(elm.Line().at(ads.VREFP).left(1.6))
d.add(elm.Dot())
text((ads.VREFP.x - 1.8, ads.VREFP.y - 0.1), 'VREF: valor exacto\nPOR VERIFICAR\n(medir VREFP-VREFN\ncon multimetro)', size=9, halign='right', color=RED)
d.pop()

# ---------------- RASPBERRY PI (derecha) ----------------
RPI_X = ads.DVDD.x + 9.0
RPI_W = 13
rpi = elm.Ic(pins=[
    elm.IcPin(name='5V / 3V3 (ver placa)', anchorname='V5', side='left', slot='7/7'),
    elm.IcPin(name='GND', anchorname='GND', side='left', slot='6/7'),
    elm.IcPin(name='CS (SPI_CE)', anchorname='CS', side='left', slot='5/7'),
    elm.IcPin(name='DRDY (GPIO libre)', anchorname='DRDY', side='left', slot='4/7'),
    elm.IcPin(name='MISO (SPI_SDI)', anchorname='MISO', side='left', slot='3/7'),
    elm.IcPin(name='MOSI (SPI_SDO)', anchorname='MOSI', side='left', slot='2/7'),
    elm.IcPin(name='SCLK (SPI_SCK)', anchorname='SCLK', side='left', slot='1/7'),
], size=(RPI_W, H)).at((RPI_X, ads.DVDD.y)).anchor('V5')
d.add(rpi)
text((RPI_X + RPI_W / 2, rpi.V5.y + 1.6), 'Raspberry Pi', size=10, halign='center', valign='bottom')
text((RPI_X + 0.3, rpi.SCLK.y - 1.4),
     'Numeros de pin/GPIO fisicos:\n'
     'POR VERIFICAR — dependen del\n'
     'modelo exacto de la placa ADS1256\n'
     '(ej. Waveshare u otra). Dibujado\n'
     'solo por funcion. Confirmar con\n'
     'el esquematico de la placa antes\n'
     'de cablear.',
     size=9, color=RED)

for a, b in ((ads.DVDD, rpi.V5), (ads.DGND, rpi.GND), (ads.CS, rpi.CS), (ads.DRDY, rpi.DRDY),
             (ads.DOUT, rpi.MISO), (ads.DIN, rpi.MOSI), (ads.SCLK, rpi.SCLK)):
    d.add(elm.Line().at(a).right().tox(b))

# AVDD/AGND del ADS1256 -> alimentacion analogica + GND comun
d.push()
d.add(elm.Line().at(ads.AVDD).left(1.6))
text((ads.AVDD.x - 1.8, ads.AVDD.y), 'AVDD: alimentacion\nanalogica de la placa\n(ver su documentacion)', size=9, halign='right')
d.pop()
d.add(elm.Line().at(ads.AGND).left(1.6))
d.add(elm.Ground())
text((ads.AGND.x - 1.8, ads.AGND.y - 1.3), 'GND comun:\nAGND = DGND del ADS1256\n= GND del RPi', size=9, halign='right', color=RED)

# ---------------- TITULO Y NOTAS ----------------
TOP = amti.SIG.y + 4.0
text((AM_L, TOP), 'Conexion AMTI (Fz) -> ADS1256 -> Raspberry Pi', size=16)
text((AM_L, TOP - 1.0), 'LADO ANALOGICO (AMTI + entrada ADS1256)', size=10, color=BLUE)
text((RPI_X, TOP - 1.0), 'LADO DIGITAL (SPI, 3.3 V)', size=10, color=GREEN)

NY = amti.REF.y - 5.0
text((AM_L, NY),
     'ANTES DE ENERGIZAR (con multimetro, todo apagado):\n'
     '1. Medir VREFP-VREFN de la placa ADS1256. Full-scale single-ended = 2*VREF/PGA. Con PGA=1 se necesita\n'
     '   VREF >= 1.7 V para que los 3.4 V maximos del AMTI no saturen. NO conectar la senal del AMTI hasta confirmar esto.\n'
     '2. Senal Fz del AMTI -> AIN0. Referencia del AMTI -> AINCOM (NO a GND salvo que la hoja de la placa lo exija).\n'
     '3. Confirmar en la documentacion de TU placa ADS1256 (no en este esquema) el mapeo real de pines a GPIO del RPi\n'
     '   antes de cablear el lado digital — este esquema lo dibuja solo por funcion.\n'
     '4. AGND y DGND del ADS1256 van al mismo GND que el RPi.\n'
     '5. Verificar en software que PGA=1 (o el valor que corresponda) antes de la primera lectura, para no saturar ni perder resolucion.',
     size=10, color=RED)

text((AM_L, NY - 6.4),
     'FUENTES DE CADA DATO:\n'
     '• Pinout ADS1256 (28 pines), regla de AINCOM para single-ended, full-scale = 2*VREF/PGA, rango absoluto de entrada\n'
     '  (AGND-0.1 a AVDD+0.1 con buffer OFF): datasheet TI ADS1256 "Very Low Noise 24-Bit ADC" Rev K (SBAS288K), leido\n'
     '  directamente del PDF el 2026-11-02 (paginas de Terminal Functions, Absolute Maximum Ratings y Analog Input).\n'
     '• Escala 1.7 V/1000 N, maximo 2000 N (3.4 V): medicion/dato propio de Luis en el lab, NO de hoja del AMTI.\n'
     '• VREF real de la placa de Luis: NO VERIFICADO — pendiente medir con multimetro.\n'
     '• Mapeo de pines ADS1256 <-> GPIO del Raspberry Pi: NO VERIFICADO — depende del modelo exacto de la placa breakout;\n'
     '  dibujado aqui solo por funcion (CS, DRDY, MISO, MOSI, SCLK), no como numero de pin fisico.',
     size=10)

d.save(OUT + '.png', dpi=170, transparent=False)
d.save(OUT + '.svg', transparent=False)
print('ok')
