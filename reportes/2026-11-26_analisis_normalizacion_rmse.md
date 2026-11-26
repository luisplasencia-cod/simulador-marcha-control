# ¿RMSE en newtons o RMSE normalizado? Análisis con los datos ya medidos (2026-11-26, laptop, sin hardware)

## Objetivo
Elegir la métrica de error con la que se dirá "Fz cerrado" (protocolo RPi §0): RMSE en N, o RMSE normalizado (por el peso corporal, el pico, el rango, la media o la DE de la curva), y qué papel tiene r. Comprobarlo con todas las pisadas ya registradas y con la referencia de marcha sana (Fukuchi 2018) calculada en las mismas unidades.

## Metodología
- **Definición común:** e = objetivo − Fz medida sobre TODA la pisada (regla de Luis 2026-11-20); objetivo SIN el delta del ILC. RMSE = √media(e²). Normalizaciones: %BW = RMSE/(m·g); %pico = RMSE/máx(objetivo); %rango = RMSE/(máx−mín); %media = RMSE/media(objetivo); %DE = RMSE/DE(objetivo). r = Pearson(objetivo, Fz).
- **Datos propios (19 series, 18 y 19-nov, `reportes/datos/`):** interfaz 3 ejes a 40/60/75/80 kg (talla 170) y 80 kg talla 174; solo Y: escalera 50–90 kg (11-18), Kp 3/5/8 y Kp programado 60–90 kg (11-19), mejora ff 0,7 + adelanto 30 ms a 80 kg. Se omitió `2026-11-18_pisadas_3ejes_interfaz` (sin peso registrado, series casi todas abortadas). Por serie se toma la mediana de las últimas 3 pisadas (2 si la serie tiene ≤ 4), cuando el ILC ya aprendió.
- **Referencia:** `variabilidad_paso_a_paso_fukuchi.py` ampliado con las mismas normalizaciones (24 jóvenes, cinta; RMSE de cada paso frente a la media del mismo sujeto).
- Script: `control/telemetria/comparar_normalizaciones_rmse.py` → `reportes/figuras/2026-11-26_normalizaciones_rmse.{png,txt,csv}`.

## Resultado
**1. El RMSE en N no sirve como criterio: crece con la carga aunque el lazo funcione igual.** Interfaz 3 ejes: 17,8 N (40 kg) → 33,4 N (80 kg), +66 %; normalizado, el mismo lazo cambia solo +2 % (4,5 → 4,3 %BW). Un umbral en N sería más exigente a 40 kg que a 80 kg y no se puede comparar con marcha sana.

**2. Con una sola curva objetivo, todas las normalizaciones dicen lo mismo:** son la misma cifra multiplicada por una constante (en todas las series el pico del objetivo es 117,8 %BW). %pico = %BW/1,18; %rango ≈ %BW/1,14; %media ≈ %BW·1,20; %DE ≈ %BW·3,6. Ninguna cambia qué serie es mejor ni la dependencia con la carga. La elección importa solo para **comparar con otras curvas o con la referencia**.

**3. Ahí gana %BW:**
| Normalización | Fukuchi 0,50 m/s | Fukuchi 1,24 m/s | Problema |
|---|---|---|---|
| **%BW** | 5,09 | 3,99 | ninguno: es la unidad en que se publican las GRF (Fukuchi, Gutenberg, Horst) y no depende de la forma de la curva |
| %pico | 4,80 | 3,59 | el pico cambia con la velocidad (≈106 %BW lento, ≈111 %BW a 1,24 m/s, 117,8 %BW nuestra curva) |
| %rango | 5,04 | 3,77 | igual que %pico, y nuestro objetivo no parte de 0 N (precarga ≈29 N) |
| %media | 6,43 | 4,82 | depende de la duración de las fases de baja carga |
| %DE | 17,3 | 15,8 | depende de la forma; no se usa en marcha |

**4. r es complementario, no suficiente.** r no cambia si la fuerza sale escalada o desplazada (F = a·objetivo + b da r = 1). En nuestros datos r casi no discrimina: 0,985–0,999 en todas las series, mientras el RMSE va de 1,4 a 4,9 %BW. Sirve para detectar un error de FORMA o de tiempo; el nivel de fuerza lo vigila el RMSE.

**5. Datos propios en %BW (mediana de las últimas pisadas):**
| Ensayo | %BW | r |
|---|---|---|
| Interfaz 3 ejes 40 / 60 / 75 / 80 kg | 4,53 / 3,85 / 4,87 / 4,26 | 0,987 / 0,991 / **0,985** / 0,988 |
| Interfaz 3 ejes 80 kg talla 174 | 4,30 | 0,988 |
| Solo Y escalera 50–90 kg (11-18) | 2,28–3,03 | 0,994–0,997 |
| Solo Y Kp programado 60–90 kg (11-19) | 2,23–2,68 | 0,996–0,997 |
| Solo Y 80 kg base → con ff 0,7 + adelanto 30 ms | 2,50 → **1,44** | 0,996 → 0,999 |

- **Repetición disponible (solo Y, 70 kg, Kp 5, dos corridas):** 2,90 vs 2,92 %BW, r 0,995 vs 0,995 → diferencia 0,4 %. Única repetición; no cubre 3 ejes ni otro día.
- La escalera de 11-18 sube +25 % de 50 a 90 kg, pero allí Kp cambió (8 → 5) sin ganancia programada: el efecto de la carga está confundido con el de Kp.

**6. Hallazgo: la curva objetivo es la de Gutenberg (marcha a 1,40 m/s).** El pico de 117,8 %BW de todas las series coincide con el 2.º pico de Gutenberg 2021 (inferido del dato, no leído del código de la interfaz). La velocidad de Fukuchi más cercana es 1,24 m/s → variabilidad paso a paso 4,0 %BW (p75 4,96) y r 0,990 (p25 0,986).

## Conclusión / propuesta
- **Métrica principal: RMSE en %BW** sobre toda la pisada. Se reporta también en N (ingeniería) y en %pico (para comparar con reportes anteriores, que usan %pico: %BW = 1,18 × %pico con esta curva).
- **Complemento: r ≥ 0,986.**
- **Umbral de trabajo para cerrar Fz: se mantiene 5 %BW.** Con la curva rápida (Gutenberg) 5 %BW es el p75 de la variabilidad paso a paso a 1,24 m/s (y la mediana a 0,50 m/s): está dentro de lo que varía una persona sana entre pasos. El umbral final de la tesis se decide después.
- Con eso, hoy: interfaz 3 ejes cumple el RMSE en todas las cargas (máx. 4,87 a 75 kg) pero 75 kg queda en r 0,985 < 0,986; la mejora ff/ILC (1,44 %BW solo Y) daría margen amplio si se repite en la interfaz.

## Limitaciones
- Una prótesis (`pie_pasivo_1`), una curva, escala x10, un solo día por condición; una sola repetición.
- Las series de la interfaz tienen 4–10 pisadas: la "estabilizada" de 60 y 75 kg sale de 2 pisadas.
- Escalera 11-18 con `t` nominal (no afecta al RMSE: muestras uniformes) y Kp distinto entre cargas.
- Fukuchi: la cinta añade su propio ruido (no separado). Su RMSE es paso vs media del mismo sujeto; el nuestro, pisada vs objetivo: misma idea (desviación de la curva buscada), no idénticos.
- La identificación de la curva como Gutenberg es inferida del pico.

## Fuentes
Fukuchi et al. 2018, PeerJ, doi 10.7717/peerj.4640 (datos públicos, procesados aquí; lectura de Luis: NO). Gutenberg 2021 (referencia de la curva, ver `control/referencia_grf/`). Reporte previo: `reportes/2026-11-20_criterio_error_estandarizado.md`. Datos: `reportes/datos/` (carpetas listadas arriba).
