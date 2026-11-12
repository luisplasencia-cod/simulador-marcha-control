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
rows_l = ['GPIO11 SCLK', 'GPIO10 MOSI', 'GPIO9 MISO', 'GPIO17 DRDY', 'GPIO8 CE0', '3V3 (sin usar aquí)', 'GND']
pi = elm.Ic(pins=[elm.IcPin(lblsize=F_PIN, name=n, anchorname=f'P{i}', side='left', slot=f'{8 - i}/8') for i, n in enumerate(rows_l)],
            size=(14, H)).at((XR, ads.SCLK.y)).anchor('P0'); d.add(pi)
T((XR + 7, ads.SCLK.y + 2.6), 'Raspberry Pi', size=F_COMP + 4, ha='center', va='bottom')

# --- SPI con R serie ---
xs, xr = ads.SCLK.x, XR - 8
for n in rows_r[:5]:
    y = getattr(ads, n).y
    if n in ('SCLK', 'DIN', 'CS'):
        L((xs, y), (xr - 7, y)); d.add(elm.Resistor().at((xr - 7, y)).to((xr, y)).label('100 Ω', fontsize=F_COMP, color=YEL, loc='top')); L((xr, y), (XR, y))
    else:
        L((xs, y), (XR, y))
tag((xr - 3.5, ads.SCLK.y + 2.4), '①')
T((xs + 15, ads.DOUT.y + 1.1), 'DOUT y DRDY: directos', size=F_NOTE, color=BLUE, ha='center')

# --- PDWN: regulador de 3.3V PROPIO (de la misma fuente externa de 5V), YA NO el 3.3V del RPi ---
yp = ads.PDWN.y
xa, xb = xs + 5, xs + 17
L((xs, yp), (xb, yp))
dot((xa, yp)); d.add(elm.Capacitor().at((xa, yp)).to((xa, yp - 4.5))); T((xa + 1.3, yp - 2.3), '100 nF', size=F_COMP, color=YEL, va='center'); gnd((xa, yp - 4.5))
d.add(elm.Resistor().at((xb, yp)).to((xb, yp - 4.5))); T((xb + 1.3, yp - 2.3), '10 kΩ', size=F_COMP, color=YEL, va='center')
L((xb, yp - 4.5), (xb, yp - 6.5)); T((xb + 0.6, yp - 5.5), '3.3 V', size=F_COMP, color=YEL, va='center')
reg = elm.Ic(pins=[elm.IcPin(lblsize=F_PIN, name='OUT', anchorname='OUT', side='top', slot='1/1'),
                   elm.IcPin(lblsize=F_PIN, name='IN', anchorname='IN', side='left', slot='1/1'),
                   elm.IcPin(lblsize=F_PIN, name='GND', anchorname='RGND', side='bottom', slot='1/1')],
             size=(8, 5)).at((xb, yp - 6.5)).anchor('OUT').theta(0); d.add(reg)
L((reg.IN.x - 4, reg.IN.y), (reg.IN.x, reg.IN.y)); dot((reg.IN.x - 4, reg.IN.y))
T((reg.IN.x - 4.6, reg.IN.y), '5 V de la fuente externa\n(tomar ANTES de R5)', size=F_COMP, color=YEL, ha='right', va='center')
gnd((reg.RGND.x, reg.RGND.y))
T((xb + 5, reg.IN.y), 'Regulador 3.3 V\n(ej. AMS1117-3.3)\n+ sus capacitores\n(ver su hoja)', size=F_COMP, color=YEL, ha='left', va='center')
tag((xs + 11, yp + 1.9), '②')
L((XR - 4, pi.P6.y), (XR, pi.P6.y)); gnd((XR - 4, pi.P6.y))

# --- analogico (sin filtro RC: se evaluo y se descarto, ver nota) ---
AX = ads.AIN0.x - 34
amti = elm.Ic(pins=[elm.IcPin(lblsize=F_PIN, name='Señal Fz', anchorname='SIG', side='right', slot='8/8'),
                    elm.IcPin(lblsize=F_PIN, name='Referencia', anchorname='REF', side='right', slot='7/8')],
              size=(12, H)).at((AX, ads.AIN0.y)).anchor('SIG').theta(0); d.add(amti)
T((AX - 6, ads.AIN0.y + 2.6), 'AMTI (salida Fz)', size=F_COMP + 4, ha='center', va='bottom')
xr1, xr2 = AX + 12, AX + 20
L((AX, ads.AIN0.y), (xr1, ads.AIN0.y))
d.add(elm.Resistor().at((xr1, ads.AIN0.y)).to((xr2, ads.AIN0.y)).label('1 kΩ', fontsize=F_COMP, color=YEL, loc='top'))
L((xr2, ads.AIN0.y), (ads.AIN0.x, ads.AIN0.y))
L((AX, ads.AGND.y), (ads.AGND.x, ads.AGND.y))
T((AX + 1, ads.AIN0.y - 0.5), 'solo resistencia en serie (protección), SIN capacitor', size=F_NOTE, color=BLUE, ha='left')
tag((xr2 + 2.5, ads.AIN0.y + 1.6), '③')

# --- alimentacion ---
yt = ads.V5.y + 9
xv = ads.V5.x
x0 = xv - 30
d.add(elm.SourceV().at((x0, yt - 5.5)).to((x0, yt))); T((x0 - 1.3, yt - 2.75), '5 V ext.', size=F_COMP, ha='right', va='center'); gnd((x0, yt - 5.5))
d.add(elm.Resistor().at((x0, yt)).to((x0 + 9, yt)).label('R5 2.2 Ω', fontsize=F_COMP, color=YEL, loc='top'))
xn5 = x0 + 14
L((x0 + 9, yt), (xn5, yt)); dot((xn5, yt))
d.add(elm.Capacitor(polar=True).at((xn5, yt)).to((xn5, yt - 5))); T((xn5 - 1.3, yt - 2.5), 'C1 100 µF', size=F_COMP, color=YEL, ha='right', va='center'); gnd((xn5, yt - 5))
xn6 = xn5 + 9
L((xn5, yt), (xn6, yt)); dot((xn6, yt))
d.add(elm.Capacitor().at((xn6, yt)).to((xn6, yt - 5))); T((xn6 + 1.3, yt - 2.5), 'C2 100 nF', size=F_COMP, color=YEL, va='center'); gnd((xn6, yt - 5))
L((xn6, yt), (xv, yt), (xv, ads.V5.y))
tag((x0 + 4.5, yt + 2.6), '④')
gnd((ads.DGND.x, ads.DGND.y)); tag((ads.DGND.x + 2.6, ads.DGND.y - 1.2), '⑤')
T((ads.DGND.x - 1.5, ads.DGND.y - 0.6), 'PUNTO ÚNICO DE GND:\nsoldar AQUÍ todos los GND', size=F_COMP, color=GREEN, ha='right', va='top')

# --- titulo y leyenda ---
TOP = yt + 7
T((AX - 8, TOP), 'PROTECCIONES DECIDIDAS para el ADS1256 — discutidas parte por parte con Luis, 2026-11-11', size=F_TIT)
T((AX - 8, TOP - 2.6), 'Hipótesis de foros + razonamiento propio; sigue sin confirmarse con medición directa (sin RPi disponible esta sesión).', size=F_NOTE, color=RED)
y0 = ads.DGND.y - 9.5
T((AX - 8, y0),
  '①  100 Ω en serie en SCLK, DIN y CS (antes 47 Ω — TI recomienda ~100 Ω). Rango permitido: 47–220 Ω (a 500 kHz no afecta el tiempo). DOUT y DRDY directos.\n'
  '②  PDWN: 5 V de la fuente externa → IN del regulador; OUT (3.3 V) → resistencia de 10 kΩ → pin PDWN; 100 nF de PDWN a GND; GND del regulador al punto único.\n'
  '     Ya NO depende del 3.3V del RPi: PDWN queda en la misma alimentación que el ADC. El cable del pin 1 del RPi a PDWN se retira.\n'
  '③  AIN0: solo 1 kΩ en serie, como PROTECCIÓN (sin capacitor: el filtro RC se descartó). Motivo: la entrada admite −0.1 V a AVDD+0.1 V (datasheet) y al cortar\n'
  '     el 5 V del ADC con el AMTI encendido entra tensión a un chip apagado; 1 kΩ limita esa corriente a ≈3.5 mA (máx. 10 mA). Impedancia de salida del AMTI: sin medir.\n'
  '④  Entrada de 5 V: R5 = 2.2 Ω en serie (reemplaza la ferrita, que no hay) + C1 100 µF + C2 100 nF pegados al módulo. fc ≈ 720 Hz.\n'
  '     Corriente medida de la placa: ≈10 mA (0.01 A) → caída en R5 ≈ 22 mV, despreciable (AVDD sigue ≈5 V, muy sobre el mínimo de 4.75 V del datasheet).\n'
  '⑤  GND de fuente externa, ADC, AMTI y RPi unidos en UN SOLO PUNTO físico (marcado abajo): soldar todos los cables de tierra ahí, no en varios lugares.\n'
  '     Cable del AMTI blindado (malla a GND en un solo extremo) y ≥ 30 cm de separación del cable del servo y del freno.',
  size=F_NOTE, color=YEL)
T((AX - 8, y0 - 11.5),
  'PENDIENTE (no bloquea cablear esto): con el ADC caído, medir PDWN y el 5V/3.3V de la placa ANTES de reiniciar, para saber si realmente era PDWN o alimentación.\n'
  'Dato ya conocido: quitar y poner el 5V no SIEMPRE arregla la caída (a veces sí, a veces no) — no asumir que es solo un bajón pasajero de tensión.\n'
  'El corte de los 4 puertos USB del RPi (2026-11-10, 16:57) fue un evento APARTE, coincidente con manipulación de cables — NO se confirmó relación con las\n'
  'caídas previas del ADC (esas ya pasaban antes, sin ese evento). No tratar ambos como la misma causa.',
  size=F_NOTE, color=RED)
T((AX - 8, y0 - 20),
  'LISTA DE COMPRAS (criterio propio, ninguna fuente lo confirma):  1) 100 µF, 100 nF, resistencias 100 Ω, 2.2 Ω, 1 kΩ, 10 kΩ; regulador 3.3V (ej. AMS1117-3.3).\n'
  '2) OTRA placa ADS1256 igual (separa placa dañada de causa externa).   3) Cable de par trenzado apantallado para AIN0 (higiene general, no urgente ya sin RC).\n'
  '4) Solo si lo anterior falla: aislador SPI de 4 canales y aislador/hub USB alimentado para el ESP32.   NO comprar otro ADC (ADS1261/1263): la falla es cuelgue, no ruido.',
  size=F_NOTE, color=GREEN)
d.save(OUT + '.png', dpi=100, transparent=False); d.save(OUT + '.svg', transparent=False)
print("guardado", OUT + ".png")
