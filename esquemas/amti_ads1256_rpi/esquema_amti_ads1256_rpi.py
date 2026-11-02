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
    elm.IcPin(name='Señal Fz', anchorname='SIG', side='right', slot='7/7'),
    elm.IcPin(name='Referencia', anchorname='REF', side='right', slot='6/7'),
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
    elm.IcPin(name='GND (junto a AIN0)', anchorname='GND0', side='left', slot='6/7'),
    elm.IcPin(name='(AIN1-7 + GND: 7 pares similares, libres)', anchorname='LIBRES', side='left', slot='4/7'),
    elm.IcPin(name='5V', anchorname='V5', side='right', slot='8/8'),
    elm.IcPin(name='GND', anchorname='DGND', side='right', slot='7/8'),
    elm.IcPin(name='SCLK', anchorname='SCLK', side='right', slot='6/8'),
    elm.IcPin(name='DIN', anchorname='DIN', side='right', slot='5/8'),
    elm.IcPin(name='DOUT', anchorname='DOUT', side='right', slot='4/8'),
    elm.IcPin(name='DRDY', anchorname='DRDY', side='right', slot='3/8'),
    elm.IcPin(name='CS', anchorname='CS', side='right', slot='2/8'),
    elm.IcPin(name='PDWN', anchorname='PDWN', side='right', slot='1/8'),
], size=(AD_W, H)).at((AD_X, amti.SIG.y)).anchor('AIN0')
d.add(ads)
AD_CX = AD_X + AD_W / 2
text((AD_CX, ads.AIN0.y + 1.6), 'ADS1256 (placa generica, 8 canales single-ended)\nPines leidos de la etiqueta FISICA de la placa\npor Luis, 2026-11-02 (no de datasheet generico)', size=10, halign='center', valign='bottom', color=GREEN)
text((AD_X - 7.0, ads.LIBRES.y - 2.6),
     'Single-ended: señal -> AINx,\n'
     'retorno -> el GND junto a ese AINx\n'
     '(segun la etiqueta de ESTA placa).\n'
     'Si tu AMTI tiene un cable de\n'
     'referencia aparte, va a ese GND.\n\n'
     'GND comun: este GND (analogico,\n'
     'junto a AIN0), el GND digital de la\n'
     'placa y el GND del RPi deben ser\n'
     'el mismo nodo electrico.',
     size=9, halign='left', color=BLUE)
text((AD_CX, ads.PDWN.y - 4.2),
     'VREF de esta placa: NO SE VE UN PIN VREF APARTE en lo que reportaste.\n'
     'Puede ser referencia interna fija (no accesible) o un test point sin etiqueta.\n'
     'POR VERIFICAR: revisar si hay un punto de prueba VREF en la placa, o buscar\n'
     'el modelo exacto impreso en el circuito para confirmar su VREF de fabrica.',
     size=9, halign='center', color=RED)

d.add(elm.Line().at(amti.SIG).right().tox(ads.AIN0))
d.add(elm.Line().at(amti.REF).right().tox(ads.GND0))

# ---------------- RASPBERRY PI (derecha) ----------------
RPI_X = ads.V5.x + 9.0
RPI_W = 13
rpi = elm.Ic(pins=[
    elm.IcPin(name='5V', anchorname='V5', side='left', slot='8/8'),
    elm.IcPin(name='GND', anchorname='GND', side='left', slot='7/8'),
    elm.IcPin(name='GPIO11 = SCLK (SPI0_SCLK)', anchorname='SCLK', side='left', slot='6/8'),
    elm.IcPin(name='GPIO10 = DIN (SPI0_MOSI)', anchorname='MOSI', side='left', slot='5/8'),
    elm.IcPin(name='GPIO9 = DOUT (SPI0_MISO)', anchorname='MISO', side='left', slot='4/8'),
    elm.IcPin(name='GPIO17 = DRDY', anchorname='DRDY', side='left', slot='3/8'),
    elm.IcPin(name='GPIO8 = CS (SPI0_CE0)', anchorname='CS', side='left', slot='2/8'),
], size=(RPI_W, H)).at((RPI_X, ads.V5.y)).anchor('V5')
d.add(rpi)
text((RPI_X + RPI_W / 2, rpi.V5.y + 1.6), 'Raspberry Pi', size=10, halign='center', valign='bottom')
text((RPI_X + 0.3, ads.PDWN.y - 4.0),
     'GPIO8/9/10/11 (SPI0): FIJOS por\n'
     'hardware en cualquier RPi de 40\n'
     'pines — no dependen de tu placa.\n'
     'GPIO17 para DRDY: elegido por\n'
     'Michael (libre, sin conflicto). Si ya\n'
     'usas GPIO17 para otra cosa, cambiar\n'
     'aqui y en el software.\n'
     'Confirmar numeracion fisica con el\n'
     'comando "pinout" en el propio RPi.',
     size=9, color=RED)

for a, b in ((ads.V5, rpi.V5), (ads.DGND, rpi.GND), (ads.SCLK, rpi.SCLK), (ads.DIN, rpi.MOSI),
             (ads.DOUT, rpi.MISO), (ads.DRDY, rpi.DRDY), (ads.CS, rpi.CS)):
    d.add(elm.Line().at(a).right().tox(b))

# PDWN: NO va a un GPIO, se ata fijo a +3.3V para que nunca quede en bajo (power-down) al arrancar
d.push()
d.add(elm.Line().at(ads.PDWN).right(2.0))
d.add(elm.Vdd().label('+3.3V (RPi)', fontsize=10))
d.pop()
text((ads.PDWN.x + 2.4, ads.PDWN.y - 1.2),
     'PDWN atado FIJO a 3.3V (no es GPIO):\n'
     'asi queda en ALTO siempre, incluso\n'
     'antes de que arranque tu script.',
     size=9, color=RED)


# ---------------- TITULO Y NOTAS ----------------
TOP = amti.SIG.y + 4.0
text((AM_L, TOP), 'Conexion AMTI (Fz) -> ADS1256 -> Raspberry Pi', size=16)
text((AM_L, TOP - 1.0), 'LADO ANALOGICO (AMTI + entrada ADS1256)', size=10, color=BLUE)
text((RPI_X, TOP - 1.0), 'LADO DIGITAL (SPI, 3.3 V)', size=10, color=GREEN)

NY = ads.PDWN.y - 6.0
text((AM_L, NY),
     'ANTES DE ENERGIZAR (con multimetro, todo apagado):\n'
     '1. VREF de esta placa: NO IDENTIFICADO como pin aparte. Full-scale single-ended = 2*VREF/PGA; con PGA=1 se necesita\n'
     '   VREF >= 1.7 V para que los 3.4 V maximos del AMTI no saturen. Buscar el modelo exacto de la placa o un punto de\n'
     '   prueba VREF antes de confiar en que no satura. NO conectar la senal del AMTI hasta confirmar esto.\n'
     '2. Senal Fz del AMTI -> AIN0. Referencia del AMTI -> el GND que esta junto a AIN0 en la placa (NO el GND de 5V/logica,\n'
     '   salvo que confirmes que son el mismo nodo internamente).\n'
     '3. PDWN -> atado fijo a +3.3V del RPi (NO a un GPIO), para que quede en ALTO siempre, incluso antes de correr el script.\n'
     '4. GPIO8/9/10/11 son SPI0 fijo por hardware del RPi (CS/DOUT/DIN/SCLK). GPIO17 para DRDY: eleccion de Michael, no es\n'
     '   fijo — cambiar en el esquema y en el software si prefieres otro. Confirmar con "pinout" en el propio RPi.\n'
     '5. Todo GND (analogico y digital de la placa) al mismo GND que el RPi.\n'
     '6. Verificar en software que PGA=1 (o el valor que corresponda) antes de la primera lectura, para no saturar ni perder resolucion.',
     size=10, color=RED)

text((AM_L, NY - 7.2),
     'FUENTES DE CADA DATO:\n'
     '• Full-scale = 2*VREF/PGA y la logica de single-ended (senal + retorno comun): datasheet TI ADS1256 "Very Low Noise\n'
     '  24-Bit ADC" Rev K (SBAS288K), leido directamente del PDF el 2026-11-02 — esto es del CHIP, aplica a cualquier placa.\n'
     '• Nombres y orden de pines de ESTA placa (AIN0/GND por canal; 5V, GND, SCLK, DIN, DOUT, DRDY, CS, PDWN): leidos\n'
     '  directamente de la etiqueta fisica de la placa por Luis, 2026-11-02 — no es generico, es la placa real en mano.\n'
     '• Escala 1.7 V/1000 N, maximo 2000 N (3.4 V): medicion/dato propio de Luis en el lab, NO de hoja del AMTI.\n'
     '• VREF real de esta placa: NO VERIFICADO — no se identifico un pin VREF en la etiqueta; pendiente confirmar si es\n'
     '  referencia interna fija o si hay un punto de prueba, y el modelo exacto de la placa.\n'
     '• Mapeo de los 8 pines digitales a GPIO especificos del Raspberry Pi: NO DEFINIDO AUN — lo elige Luis en el software.',
     size=10)

d.save(OUT + '.png', dpi=170, transparent=False)
d.save(OUT + '.svg', transparent=False)
print('ok')
