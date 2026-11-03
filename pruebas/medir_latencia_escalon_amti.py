"""Paso 2 del plan de latencia (pruebas/2026-11-02_latencia_amti_rpi_esp32.md):
latencia de ADQUISICION AMTI -> RPi, usando un escalon de fuerza real (pisar o
soltar un peso sobre el AMTI), no la tasa de muestreo del ADC (eso ya esta
confirmado: 1000 Hz exactos, ver leer_ads1256_fz.py).

Que mide este script: el instante (reloj de pared, time.time()) en que el
RPi DETECTA que Fz cruzo un umbral, leyendo continuamente via ADS1256. Cada
cruce se imprime en vivo y se guarda en un CSV.

Lo que este script NO mide por si solo: el instante FISICO real del escalon
(el AMTI no tiene un disparador externo conectado). Para estimar la latencia
real hace falta una referencia independiente del instante fisico - ej. grabar
en video el momento de pisar/soltar junto con la pantalla del RPi mostrando
la hora del sistema (sincronizada por NTP), o un golpe audible capturado en
el mismo video que el log. Sin esa referencia, lo unico que se puede reportar
es el log de cruces de este script (que SI sirve para ver consistencia/jitter
entre repeticiones), no un numero de latencia absoluta verificado - no
inventar un numero si falta esa referencia.

Uso:
    python medir_latencia_escalon_amti.py --umbral_n 30 --n_eventos 10
"""
import argparse
import csv
import time

from leer_ads1256_fz import ADS1256, volts_a_newtons


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--umbral_n", type=float, default=30.0,
                     help="cuantos N sobre el offset en reposo cuentan como 'escalon detectado'")
    ap.add_argument("--n_eventos", type=int, default=10, help="cuantos cruces (subida+bajada) registrar")
    ap.add_argument("--salida", default="latencia_escalon_amti.csv")
    a = ap.parse_args()

    adc = ADS1256()
    print("Calculando offset en reposo (2 s, no tocar el AMTI)...")
    muestras_reposo = [volts_a_newtons(adc.leer_volts()) for _ in range(2000)]
    offset = sum(muestras_reposo) / len(muestras_reposo)
    print(f"Offset en reposo: {offset:.2f} N. Umbral de deteccion: {offset + a.umbral_n:.2f} N")
    print("Aplica/retira la carga cuando quieras. Ctrl+C para terminar antes.\n")

    eventos = []
    arriba = False
    try:
        while len(eventos) < a.n_eventos:
            t = time.time()
            f = volts_a_newtons(adc.leer_volts()) - offset
            cruzo_arriba = f > a.umbral_n
            if cruzo_arriba and not arriba:
                print(f"[SUBIDA]  t={t:.6f}  Fz={f:.1f} N")
                eventos.append(["subida", t, f])
                arriba = True
            elif not cruzo_arriba and arriba and f < a.umbral_n * 0.5:
                print(f"[BAJADA]  t={t:.6f}  Fz={f:.1f} N")
                eventos.append(["bajada", t, f])
                arriba = False
    except KeyboardInterrupt:
        pass
    finally:
        adc.cerrar()

    with open(a.salida, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["tipo", "t_wall_clock", "fz_sobre_offset_n"])
        w.writerows(eventos)
    print(f"\n{len(eventos)} eventos guardados en: {a.salida}")
    print("Recuerda: esto es el instante de DETECCION del RPi, no la latencia absoluta.")
    print("Para la latencia real falta una referencia fisica independiente (ver aviso arriba del script).")


if __name__ == "__main__":
    main()
