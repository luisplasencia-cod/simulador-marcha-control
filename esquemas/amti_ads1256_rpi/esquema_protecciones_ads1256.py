"""Esquema de las PROPUESTAS para que el ADS1256 no se caiga (2026-11-10). HIPOTESIS NO PROBADAS: valores tipicos de practica
(foros TI E2E, notas de aplicacion sobre ruido de servos), no calculados para esta placa. Estilo de esquema_amti_ads1256_rpi.py.
Uso: python esquema_protecciones_ads1256.py [--salida DIR]   (necesita schemdraw[matplotlib])"""
import argparse, os
import schemdraw
import schemdraw.elements as elm

schemdraw.use('matplotlib')
ap = argparse.ArgumentParser(); ap.add_argument("--salida", default="salida"); a = ap.parse_args()
os.makedirs(a.salida, exist_ok=True)
OUT = os.path.join(a.salida, "esquema_protecciones_ads1256")
RED, BLUE, GREEN, YEL, FG = '#ef5350', '#64b5f6', '#66bb6a', '#ffd54f', 'white'
F_PIN, F_COMP, F_TAG, F_NOTE, F_TIT = 26, 24, 34, 27, 40
d = schemdraw.Drawing(show=False)
d.config(unit=3, fontsize=F_PIN, lw=3, color=FG, bgcolor='black')


def T(xy, s, size=F_NOTE, color=FG, ha='left', va='top'):
    d.add(elm.Label().at(xy).label(s, fontsize=size, color=color, halign=ha, valign=va))


def L(*pts):
    for p, q in zip(pts[:-1], pts[1:]):
        d.add(elm.Line().at(p).to(q))


def dot(p): d.add(elm.Dot().at(p))


def gnd(p): d.add(elm.Ground().at(p))


def tag(xy, n): T(xy, n, size=F_TAG, color=YEL, ha='center', va='center')


H, N = 22, 8
rows_r = ['SCLK', 'DIN', 'DOUT', 'DRDY', 'CS', 'PDWN']
pins = [elm.IcPin(lblsize=F_PIN, name='AIN0', anchorname='AIN0', side='left', slot='8/8'),
        elm.IcPin(lblsize=F_PIN, name='GND (junto a AIN0)', anchorname='AGND', side='left', slot='7/8'),
        elm.IcPin(lblsize=F_PIN, name='5V', anchorname='V5', side='top', slot='1/1'),
        elm.IcPin(lblsize=F_PIN, name='GND', anchorname='DGND', side='bottom', slot='1/1')]
for i, n in enumerate(rows_r):
    pins.append(elm.IcPin(lblsize=F_PIN, name=n, anchorname=n, side='right', slot=f'{8 - i}/8'))
ads = elm.Ic(pins=pins, size=(15, H)).at((0, 0)).anchor('AIN0'); d.add(ads)
T((ads.AIN0.x + 7.5, ads.AIN0.y + 2.6), 'ADS1256 (placa)', size=F_COMP + 4, ha='center', va='bottom')

XR = ads.SCLK.x + 30
rows_l = ['GPIO11 SCLK', 'GPIO10 MOSI', 'GPIO9 MISO', 'GPIO17 DRDY', 'GPIO8 CE0', '3V3 (pin 1)', '3V3 (pin 17)', 'GND']
pi = elm.Ic(pins=[elm.IcPin(lblsize=F_PIN, name=n, anchorname=f'P{i}', side='left', slot=f'{8 - i}/8') for i, n in enumerate(rows_l)],
            size=(14, H)).at((XR, ads.SCLK.y)).anchor('P0'); d.add(pi)
T((XR + 7, ads.SCLK.y + 2.6), 'Raspberry Pi', size=F_COMP + 4, ha='center', va='bottom')

# --- SPI con R serie ---
xs, xr = ads.SCLK.x, XR - 8
for n in rows_r[:5]:
    y = getattr(ads, n).y
    if n in ('SCLK', 'DIN', 'CS'):
        L((xs, y), (xr - 7, y)); d.add(elm.Resistor().at((xr - 7, y)).to((xr, y)).label('47 Ω', fontsize=F_COMP, color=YEL, loc='top')); L((xr, y), (XR, y))
    else:
        L((xs, y), (XR, y))
tag((xr - 3.5, ads.SCLK.y + 2.4), '①')
T((xs + 15, ads.DOUT.y + 1.1), 'DOUT y DRDY: directos', size=F_NOTE, color=BLUE, ha='center')

# --- PDWN ---
yp, y17 = ads.PDWN.y, pi.P6.y
xa, xb = xs + 5, xs + 17
L((xs, yp), (XR, yp))
dot((xa, yp)); d.add(elm.Capacitor().at((xa, yp)).to((xa, yp - 4.5))); T((xa + 1.3, yp - 2.3), '100 nF', size=F_COMP, color=YEL, va='center'); gnd((xa, yp - 4.5))
dot((xb, yp)); d.add(elm.Resistor().at((xb, yp)).to((xb, y17))); T((xb + 1.3, (yp + y17) / 2), '10 kΩ', size=F_COMP, color=YEL, va='center')
L((xb, y17), (XR, y17))
tag((xs + 11, yp + 1.9), '②')
L((XR - 4, pi.P7.y), (XR, pi.P7.y)); gnd((XR - 4, pi.P7.y))

# --- analogico ---
AX = ads.AIN0.x - 34
amti = elm.Ic(pins=[elm.IcPin(lblsize=F_PIN, name='Señal Fz', anchorname='SIG', side='right', slot='8/8'),
                    elm.IcPin(lblsize=F_PIN, name='Referencia', anchorname='REF', side='right', slot='7/8')],
              size=(12, H)).at((AX, ads.AIN0.y)).anchor('SIG'); d.add(amti)
T((AX - 6, ads.AIN0.y + 2.6), 'AMTI (salida Fz)', size=F_COMP + 4, ha='center', va='bottom')
xr1, xr2 = AX + 5, AX + 13
L((AX, ads.AIN0.y), (xr1, ads.AIN0.y))
d.add(elm.Resistor().at((xr1, ads.AIN0.y)).to((xr2, ads.AIN0.y)).label('1 kΩ', fontsize=F_COMP, color=YEL, loc='top'))
xn = xr2 + 4
L((xr2, ads.AIN0.y), (ads.AIN0.x, ads.AIN0.y)); dot((xn, ads.AIN0.y))
L((AX, ads.AGND.y), (ads.AGND.x, ads.AGND.y)); dot((xn, ads.AGND.y))
d.add(elm.Capacitor().at((xn, ads.AIN0.y)).to((xn, ads.AGND.y))); T((xn + 1.3, (ads.AIN0.y + ads.AGND.y) / 2), '100 nF', size=F_COMP, color=YEL, va='center')
tag((xn - 4, ads.AIN0.y + 2.0), '③')

# --- alimentacion ---
yt = ads.V5.y + 9
xv = ads.V5.x
x0 = xv - 30
d.add(elm.SourceV().at((x0, yt - 5.5)).to((x0, yt))); T((x0 - 1.3, yt - 2.75), '5 V ext.', size=F_COMP, ha='right', va='center'); gnd((x0, yt - 5.5))
d.add(elm.Resistor().at((x0, yt)).to((x0 + 9, yt)).label('R5 1–2.2 Ω', fontsize=F_COMP, color=YEL, loc='top'))
xn5 = x0 + 14
L((x0 + 9, yt), (xn5, yt)); dot((xn5, yt))
d.add(elm.Capacitor(polar=True).at((xn5, yt)).to((xn5, yt - 5))); T((xn5 - 1.3, yt - 2.5), 'C1 100 µF', size=F_COMP, color=YEL, ha='right', va='center'); gnd((xn5, yt - 5))
xn6 = xn5 + 9
L((xn5, yt), (xn6, yt)); dot((xn6, yt))
d.add(elm.Capacitor().at((xn6, yt)).to((xn6, yt - 5))); T((xn6 + 1.3, yt - 2.5), 'C2 100 nF', size=F_COMP, color=YEL, va='center'); gnd((xn6, yt - 5))
L((xn6, yt), (xv, yt), (xv, ads.V5.y))
tag((x0 + 4.5, yt + 2.6), '④')
gnd((ads.DGND.x, ads.DGND.y)); tag((ads.DGND.x + 2.6, ads.DGND.y - 1.2), '⑤')

# --- titulo y leyenda ---
TOP = yt + 7
T((AX - 8, TOP), 'PROPUESTAS contra la caída del ADS1256 — HIPÓTESIS, NO PROBADAS', size=F_TIT)
T((AX - 8, TOP - 2.6), 'Valores típicos de práctica (foros TI E2E, notas de aplicación sobre ruido de servos); no calculados para esta placa.', size=F_NOTE, color=RED)
y0 = ads.DGND.y - 5
T((AX - 8, y0),
  '①  47 Ω en serie en SCLK, DIN y CS, cerca del RPi: amortiguan rebotes.   DOUT y DRDY van directos.\n'
  '②  PDWN: cable a 3V3 (pin 1) SOLDADO + 10 kΩ a OTRO 3V3 (pin 17) = dos caminos independientes. 100 nF a GND filtra picos.\n'
  '③  AIN0: 1 kΩ + 100 nF, fc = 1/(2π·1 kΩ·100 nF) ≈ 1.6 kHz (la marcha necesita < 100 Hz). Verificar la impedancia de salida del AMTI (no medida).\n'
  '④  Entrada de 5 V: R5 de 1–2.2 Ω en serie (reemplaza la ferrita, que no hay) + C1 100 µF + C2 100 nF pegados al módulo. fc ≈ 720 Hz con 2.2 Ω.\n'
  '     Caída = I·R5: MEDIR la corriente de la placa (no medida). AVDD debe estar entre 4.75 y 5.25 V (datasheet): medirlo en el módulo con el servo en marcha.\n'
  '⑤  GND de fuente externa, ADC, AMTI y RPi unidos en UN solo punto (estrella). Cable del AMTI blindado (malla a GND en un solo extremo)\n'
  '     y ≥ 30 cm de separación del cable del servo y del freno.',
  size=F_NOTE, color=YEL)
T((AX - 8, y0 - 9.5),
  'ORDEN SUGERIDO:  (0) con el ADC caído, medir con multímetro: 5 V de entrada, 3.3 V del regulador (AMS1117), VREF (ADR03B, debe dar 2.5 V) y PDWN (≈3.3 V).\n'
  '(1) ② PDWN: cable soldado + pull-up a otro 3V3.   (2) ④ R5 + C1/C2 en la entrada de 5 V.   (3) ⑤ GND en un solo punto, cables cortos.\n'
  '(4) ① resistencias en serie y ③ filtro RC en AIN0.   (5) Si persiste el error con el servo en marcha: alimentación AISLADA (DC-DC aislado) y/o aislador digital en SPI.',
  size=F_NOTE, color=GREEN)
T((AX - 8, y0 - 15.5),
  'CORRECCIÓN a lo dicho antes: un pull-up de PDWN al MISMO cable de 3V3 no protege si ese cable se suelta; por eso va a otro pin de 3V3 (pin 17).',
  size=F_NOTE, color=RED)
T((AX - 8, y0 - 19.5),
  'LISTA DE COMPRAS (criterio propio, ninguna fuente lo confirma):  1) 100 µF, 100 nF, resistencias 1 Ω, 2.2 Ω, 10 kΩ, 47 Ω.   2) OTRA placa ADS1256 igual (separa placa dañada de causa externa).\n'
  '3) Fuente de 5 V externa (aislada si se puede) para el ADC: funcionó el 2026-11-05.   4) Cable de par trenzado apantallado para AIN0.\n'
  '5) Solo si lo anterior falla: aislador SPI de 4 canales y aislador/hub USB alimentado para el ESP32.   NO comprar otro ADC (ADS1261/1263): la falla es cuelgue, no ruido.',
  size=F_NOTE, color=GREEN)
d.save(OUT + '.png', dpi=100, transparent=False); d.save(OUT + '.svg', transparent=False)
print("guardado", OUT + ".png")
