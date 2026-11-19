# Protocolo de la próxima sesión en la RPi (copiar y pegar)

Escrito 2026-11-19 en la laptop, **sin RPi: nada de esto está ejecutado.** Flags revisados en el argparse real de
`control/lazo_fz_tiempo_real.py` (líneas 478–502) y `control/escalera_carga.py`. Todos los comandos se corren desde
`~/simulador-marcha-control` con `PY=.venv/bin/python`.

## ⚠️ Antes de empezar: dos hallazgos que cambian el orden
1. **La prueba Kp 3 vs Kp 5 va ANTES del HOME.** El lazo por script abre `/dev/ttyUSB0`, eso reinicia el ESP32 de
   motores y **borra el HOME**. Para el lazo solo en Y el HOME no hace falta (CLAUDE.md, 2026-11-10). Si se hace HOME
   primero, se pierde al correr la prueba. HOME queda para cuando se pase a 3 ejes desde la interfaz (paso 3).
2. **`control/escalera_carga.py` NO sirve para esta prueba:** no tiene `--kp` (el lazo queda en Kp 10, que a 70 kg
   oscila) y fija `--hueco_mm 45 --hueco_remedido` sin medir (eso rompe la regla de remedir el hueco). La escalera de
   la tarde del 11-18 se corrió con `tools/escalera_paso.sh` del repo de la interfaz, no con este script. Aquí se llama
   al lazo directamente.

Reglas que valen en todos los pasos: nunca HOME con prótesis; ejes al ESP32 siempre como ENTERO (0 = X, 1 = Y, 2 = K);
remedir el hueco antes de cada corrida (`--hueco_remedido`); `python -u` para ver la salida en vivo; matar procesos
por PID, nunca `pkill -f`; con la interfaz abierta no correr scripts que abran `/dev/ttyUSB0`.

---

## Paso 1 — Preflight e identificación de los dos ESP32 (Claude, sin mover nada)
```bash
cd ~/simulador-marcha-control && git pull
PY=.venv/bin/python
pruebas/etapa2_rpi.sh preflight            # NO abre /dev/ttyUSB*; revisa uart0-pi5 y escucha ttyAMA0
ls -l /dev/serial/by-id/                   # motores = CP2102 (usb-Silicon_Labs_CP2102_..._0001-if00-port0 -> ttyUSB?)
ls -l /dev/ttyAMA0                         # lectura (ADC) = UART del header GPIO14/15. NO /dev/serial0 (= ttyAMA10)
vcgencmd get_throttled                     # debe ser throttled=0x0
$PY -u pruebas/medir_latencia_ping_pong.py --puerto /dev/ttyUSB0 --n 200 \
    --salida pruebas/resultados/ping_pong_$(date +%Y%m%d)_inicio.csv
```
- **Pasa si:** preflight OK con ≈1000 paquetes/s en `ttyAMA0`; el CP2102 aparece como `ttyUSB0` (si es otro número,
  usar ese en `--puerto_esp32` de aquí en adelante); PING 200/200 con RTT ≈ 6 ms; `throttled=0x0`.
- **Aborta si:** `ttyAMA0` en silencio (ESP32 de lectura sin alimentar o GPIO17→pin 10 suelto: avisar a Luis);
  PING < 200/200 o RTT > 10 ms (revisar cable USB antes de cargar nada).
- Decide: Claude informa; Luis revisa cables si algo falla.

## Paso 1b — Ruido de 60 Hz: filtro nuevo y diagnóstico eléctrico (Claude + Luis, sin mover motores)
Medido el 11-18: σ 2.67 N en el RPi vs 0.78 N en la laptop, por una línea de 60 Hz + armónicos (sin ella σ 0.74 N);
los drivers encendidos y quietos NO la cambian (2.28 N rms). Origen eléctrico sin determinar. **Filtro nuevo en el
lector UART del lazo (2026-11-19, `filtrar_60hz` en `control/lazo_fz_tiempo_real.py`):** mediana deslizante de 5 +
promedio de 17 muestras (≈1 periodo de 60 Hz). En la laptop, con datos sintéticos: σ 2.25 → 0.20 N, sin sesgo,
retardo 4 → 11 ms. **No probado con el ADC real.** Activo por defecto; `--sin_filtro_60hz` vuelve a lo del 11-18.

1. Comprobar el filtro con el ADC real, plato vacío, sin tocarlo (no abre el ESP32 de motores):
   ```bash
   $PY -u pruebas/ruido_60hz_filtro.py --puerto_fz /dev/ttyAMA0 --segundos 20 | tee pruebas/resultados/etapa2/ruido_60hz_filtro_$(date +%H%M%S).txt
   ```
   **Pasa si** σ con filtro ≤ 1.0 N y la media no cambia > 0.3 N. **Si no pasa:** usar `--sin_filtro_60hz` en todo y reportar.
2. Diagnóstico de la causa (una cosa por vez, repitiendo `pruebas/etapa2_rpi.sh r2` 60 s cada vez y anotando la
   amplitud de 60 Hz): (a) RPi alimentado desde otra toma / otra regleta; (b) RPi y amplificador del AMTI en la MISMA
   regleta (si baja: lazo de tierra entre dos tomas); (c) ESP32 de lectura alimentado aparte vs desde el RPi; (d) cable
   GND ESP32-lectura→RPi más corto y lejos del cable del servo. Lo que baje la línea de 60 Hz se deja así y se anota en
   CLAUDE.md. El filtro de software no reemplaza esto: si el ruido entra en el AMTI→ADC, también afecta a Fy/CoP después.
- Decide: Luis cambia tomas/cables; Claude mide y reporta.

## Paso 2 — Prueba Kp 3 vs Kp 5 a la misma carga (Luis autoriza y está en el paro)
**Las 3 corridas A-B-A van con `--sin_filtro_60hz`** (mismas condiciones que el 11-18: así solo cambia Kp). Después,
una 4.ª corrida Kp 5 CON filtro (mismo comando sin ese flag) mide el efecto del filtro sobre la oscilación.
**Carga propuesta: 70 kg a x10.** Es el escalón donde Kp 8 oscilaba (~7 Hz, ±100 N) y Kp 5 completó (informe
`reportes/2026-11-18_escalera_50_a_90kg_x10_y_abortos.md`). Valores calculados como en la escalera:
peso 686.7 N, pico 1.178 × peso = 809 N, tope min(1.25 × pico, 1300) = 1011 N, apoyo 0.615 s × 10 = 6.15 s,
`extra_mm` 46 (1.5 × compresión esperada, mismo valor que la tarde).

**Diseño A-B-A (3 corridas): Kp 5 → Kp 3 → Kp 5.** La oscilación creció con las pisadas y quizás con el tiempo; repetir
Kp 5 al final separa el efecto de Kp de una deriva. 10 pisadas cada una (el ILC arranca de cero en cada corrida).

Preparación (cada corrida): pie plano 0° (por pasos de K, sin girar), prótesis montada, tara con el pie en el aire
(la hace el lazo), **hueco remedido**: como la tarde, medir el contacto con el ADC y dejar el pie a 30 mm sobre él
(`interfaz/tools/medir_hueco.py`; sus flags no se pueden ver desde la laptop → `--help` en la RPi) o Luis lo mide
a mano. Poner ese número en `--hueco_mm`.

```bash
HUECO=30   # <-- REEMPLAZAR por el hueco medido ANTES de CADA corrida
for KP in 5 3 5; do
  echo "=== Kp $KP — hueco $HUECO mm — Luis: ¿hueco remedido y paro a mano? ==="; read -r -p "Escribe SI: " r; [ "$r" = SI ] || break
  $PY -u control/lazo_fz_tiempo_real.py --peso_sujeto_n 686.7 --fmax_n 1011 --n_ciclos 10 \
      --duracion_apoyo_s 6.15 --kp $KP --v_max 9000 --extra_mm 46 \
      --hueco_mm $HUECO --hueco_remedido --angulo_deg 0 \
      --fuente_fz uart --puerto_fz /dev/ttyAMA0 --puerto_esp32 /dev/ttyUSB0 --sin_filtro_60hz --ejecutar \
      2>&1 | tee pruebas/resultados/kp${KP}_70kg_x10_$(date +%H%M%S).txt
  read -r -p "Luis: remedir hueco, cambiar HUECO=... en la shell y Enter" _
done
```
(El bucle es una ayuda; si el hueco cambia entre corridas, correr cada `lazo_fz_tiempo_real.py` a mano con su valor.)

- **Aborta (lo hace el script solo):** tope de fuerza, salto anómalo, descenso > hueco + extra, contador ≠ ordenado,
  silencio del UART. Tras cualquier aborto: Y vuelve solo; si no vuelve (pasó 2 veces el 11-18 con cortes USB), Luis
  alivia con subidas supervisadas de 10–20 mm y se mira `dmesg | tail -20` por `disabled by hub (EMI?)`.
- **Si Kp 3 no llega al GRF** (error grande, no oscila): es esperable (menos ganancia = más lento); la corrida sirve
  igual para el espectro. No subir Kp para "arreglarla".
- Decide: Luis autoriza cada corrida; Claude lee el resultado.

### Cómo medir la oscilación y cómo decidir
Cada corrida escribe `control/telemetria/registros/<fecha>_<hora>_fz.csv` (la salida imprime la ruta) con columnas
`t, ciclo, r, delta, r_corregida, F_med, e, u, y_mm, v_mm_s`, a 100 Hz (lazo de 10 ms) + su `.meta.txt` (trae `kp=`).

**Script de espectro: `control/telemetria/espectro_corrida.py` (HECHO en la laptop, 2026-11-19; probado SOLO con
CSV sintéticos de frecuencia conocida: detecta 7.00 Hz y 4.07 Hz con senoides de 7.0 y 4.0 Hz, RMS 14.07 N vs 14.14 N
real; NO probado con CSV reales del lazo).** Señal `e = r_corregida − F_med` y `v_mm_s`, por pisada, sin tendencia,
Hann; pico en 3–15 Hz, RMS en 5–10 Hz; tabla por pisada + métrica (pisadas ≥ 6) + diferencia de frecuencia vs 2×
resolución + figura (espectros superpuestos y RMS vs pisada):

```bash
python -u control/telemetria/espectro_corrida.py <kp5_a>.csv <kp3>.csv <kp5_b>.csv --desde 6 --png reportes/figuras/2026-XX-XX_espectro_kp3_vs_kp5.png
```
Antes de la prueba nueva, correrlo sobre los 5 CSV de la escalera del 11-18 (sección 4) y comparar con las
frecuencias del reporte (60 kg 8.3 Hz, 80 kg 6.4 Hz, 90 kg 7.3 Hz): si no coinciden, revisar el script antes de decidir nada.

**Métrica:** media de RMS 5–10 Hz de `r − F_med` en las pisadas 6–10 (ILC ya avanzado). Kp 5 = promedio de las dos
corridas Kp 5; si esas dos difieren > 25 %, hay deriva → la comparación no es concluyente, repetir.

| Resultado | Lectura |
|---|---|
| Frecuencia del pico **igual** y amplitud Kp3/Kp5 **entre 0.8 y 1.25** | Resonancia externa al lazo (no depende de Kp). Remedio: notch sobre Fz o suavizar el comando (5b). |
| Frecuencia **casi igual** pero amplitud Kp3/Kp5 **< 0.5** (baja 2–4×, lo que predice la simulación 5d) | **Modo mecánico DENTRO del lazo con poco margen** (ganancia real 2.5–3× la diseñada a carga alta). Remedio: bajar Kp a carga alta, `Kp·min(1, k_asumido/k_tangente)` (5a/5d); un notch solo no basta. |
| Frecuencia **cambia** claramente (> 2× resolución) con Kp | La crea el polo del lazo con el retardo. Remedio: menos Kp, o Kp(k) en línea. |
| Cualquier otro caso (amplitud Kp3/Kp5 entre 0.5 y 0.8, o ambiguo) | No concluyente: repetir con otra carga (p. ej. 90 kg, donde la amplitud es mayor). |

Ojo: el criterio de amplitud solo no basta — una resonancia mecánica también se amplifica más con más Kp. **El criterio
fuerte es la frecuencia:** si cambia con Kp, es del lazo; si queda fija, es de la estructura. Decide: Claude analiza,
Luis decide el remedio.

## Paso 3 — HOME SIN prótesis (solo con OK explícito de Luis en ese momento)
Solo si después se va a probar 3 ejes desde la interfaz. El HOME se perdió el 2026-11-18 (el ESP32 se reinició al
reabrir el puerto tras aliviar el pie a 80 kg).
1. Luis **retira la prótesis**, despeja el carro, manos fuera. Claude no lanza nada hasta leer "OK HOME" de Luis.
2. Cerrar cualquier script que tenga `/dev/ttyUSB0` abierto (`ps aux | grep lazo_fz`, matar por PID).
3. Abrir la interfaz vigente (pulsa HOME sola al conectar):
```bash
cd ~/Projects/gaitsim-control && XDG_RUNTIME_DIR=/run/user/$(id -u) WAYLAND_DISPLAY=wayland-0 \
  nohup venv/bin/python -u ~/simulador-marcha-control/herramientas/lanzar_interfaz_control.py \
  > ~/simulador-marcha-control/logs/interfaz_$(date +%Y%m%d_%H%M%S).log 2>&1 &
echo $!   # anotar el PID
echo 'estado' > ~/simulador-marcha-control/logs/interfaz_cmd.txt
```
- **Pasa si:** el log muestra HOME terminado (Y → X → K), sin alarma del driver.
- **Aborta si:** alarma o ruido del servo → Luis al paro; no reintentar sin entender la causa.
- Después: Luis monta la prótesis **con la interfaz abierta** (si se cierra, se pierde el HOME). A partir de aquí,
  nada de scripts sobre `/dev/ttyUSB0`.

## Paso 4 — Traer los CSV de telemetría a la laptop (Claude, antes de cerrar)
Los CSV están ignorados por git (`control/telemetria/registros/.gitignore` → `*.csv`); sin ellos la laptop no puede
analizar nada. `reportes/datos/` **no** está ignorado y ya tiene precedente (`reportes/datos/2026-11-18_pisadas_3ejes_interfaz/`, 373 KB).
```bash
D=reportes/datos/$(date +%Y-%m-%d)_kp3_vs_kp5_70kg
mkdir -p $D
cp control/telemetria/registros/$(date +%Y-%m-%d)_*_fz.csv control/telemetria/registros/$(date +%Y-%m-%d)_*_fz.meta.txt $D/
cp pruebas/resultados/kp*_70kg_x10_*.txt $D/
# + los 5 CSV de la escalera 50-90 kg del 11-18 (no se pueden reanalizar sin ellos):
mkdir -p reportes/datos/2026-11-18_escalera_50_90kg_x10
for h in 152829 153832 154240 155042 155241; do cp control/telemetria/registros/2026-11-18_${h}_fz.* reportes/datos/2026-11-18_escalera_50_90kg_x10/; done
du -sh $D reportes/datos/2026-11-18_escalera_50_90kg_x10     # revisar tamaño (10 pisadas a 100 Hz ≈ 0.5 MB por corrida)
```
Escribir un `LEEME.md` en cada carpeta (qué corrida, Kp, hueco, quién la autorizó), luego `git add` de esas carpetas,
commit y push. Si alguna carpeta pasa de ~20 MB, no subirla: `scp` a la laptop en su lugar.

## Paso 5 — Resultados de otros agentes (se llenan antes de la sesión)
### 5a. Estimador de k en línea
Reporte: `reportes/2026-11-19_identificacion_k_en_linea.md`; código `control/identificacion/estimador_k_en_linea.py`
(autoprueba OK, **NO conectado al lazo**, solo simulación). Método: precarga automática de 1–3 s tras el contacto
(5 mm/s hasta 15 % del pico, máx 150 N) da k para la pisada 1; luego k = percentil 70 de las pendientes de carga
+15 %; Kp único = 6 1/s. En simulación la ganancia real queda en 4.5–5.0 1/s para toda prótesis/carga (hoy 4.4–10).
**No se prueba en esta sesión** (el lazo no lo usa aún; no se conecta hasta que el paso 2 aclare la oscilación y Luis
lo apruebe). Para validarlo en la RPi después: comparar k de la precarga con el Ensayo A (23 N/mm), medir histéresis
con los CSV del lazo, corrida 50 kg automática vs k fijo, y una 2.ª prótesis. Luis debe fijar el recorrido máximo de
la precarga (se usó 80 mm sin medir). Advertencia: el percentil 70 es frágil (con 80 un caso duplicó k).

### 5b. Filtro notch / suavizado del comando
Reporte: `reportes/2026-11-19_propuesta_notch_fz_6_8hz.md`; código `control/filtro_fz/notch_fz.py` (autoprueba OK,
**NO conectado al lazo**). **No se prueba en esta sesión salvo que el paso 2 diga "la excita el lazo".** En ese caso:
notch centrado en 6.93 Hz, Q ≈ 3.5, aplicado SOLO a la Fz que entra al término P (ILC, tope de fuerza, detector de
saltos y log siguen sin filtrar); cuesta ≈7 ms / 2.5° a 1 Hz; atenúa −6 a −23 dB en 6.4–7.3 Hz pero solo −2.1 dB a
8.3 Hz. Si el paso 2 dice "resonancia mecánica", el notch NO sirve (escondería la oscilación del controlador mientras
la fuerza real sobre la prótesis sigue oscilando). Limitar la aceleración de `SET_VEL` desde el RPi tampoco sirve: la
curva a x10 ya exige 260–535 mm/s² y la oscilación 124–373 mm/s²; una rampa real tendría que ir en el firmware.

### 5c. Simulación de la resonancia
Reporte: `reportes/2026-11-19_simulacion_hipotesis_resonancia_6_8hz.md`. Con los retardos/τ reales del Ensayo B y los
Kp usados (8 y 5): margen de fase 78–87°, cruce en 0.5–0.9 Hz → **el retardo del lazo P NO explica 6–8 Hz ni su
crecimiento con la carga.** Ese modelo no tiene modo mecánico ni ILC, así que no descarta esas dos causas: la análisis
de causa raíz (5d) las evalúa. No cambia la carga ni los Kp del paso 2.

### 5d. Causa raíz de la oscilación
Reporte: `reportes/2026-11-19_causa_oscilacion_6_8hz_y_mejoras.md` (SOLO simulación; masa, rigidez del accionamiento y amortiguamiento del modo mecánico son SUPUESTOS, no medidos). Hipótesis más probable: **un modo de ~7 Hz dentro del lazo + rigidez de la prótesis mucho mayor a carga alta** (k diseño 26.4 N/mm solo medido hasta 105 N; estimada con la escalera a 600–1000 N: 67–88 N/mm → ganancia real del lazo 2.5–3× la diseñada, poco margen). El ILC no mete 6–8 Hz (su filtro deja pasar < 0.001), pero al aprender lleva la fuerza a los picos reales donde la ganancia es máxima: por eso crece pisada a pisada. La simulación reproduce Kp 8 inestable a 60–70 kg y el crecimiento 12→25 N (rig: 7.9→15 N); NO reproduce la amplitud con Kp 5 a 70–90 kg (sim 2 N, rig 20–31 N): el rig está más cerca de la inestabilidad que el modelo.
- **Mejora propuesta (no aplicada):** `Kp·min(1, k_asumido/k_tangente)`: en la sim 202 → 2 N a 70 kg y RMS 31 → 14 N a 60 kg; necesita k tangente a carga alta (estimador de k en línea 5a o Ensayo A hasta ~1000 N). Ayudas menores: interpolar la referencia (pisada 1: 12 → 6 N) y rampa ~1000 mm/s² (25 → 13 N). Cambiar el ILC (olvido, Q más ancho) no sirve.
- **⚠️ La tabla de decisión del paso 2 se lee DISTINTO:** el modelo predice que con Kp 3 la amplitud baja 2–4× y la frecuencia casi NO cambia. Eso significa «modo dentro del lazo con poco margen» (la respuesta es bajar la ganancia a carga alta, no solo un notch), NO «resonancia externa». Frecuencia igual + amplitud que baja mucho = esto. Frecuencia igual + amplitud igual (0.8–1.25) sí sería resonancia externa al lazo.
- **⚠️ Hallazgo en el código:** la columna `t` del CSV era NOMINAL (`i·10 ms`); el periodo real estimado es ~13.5 ms (la interfaz mide 13.0 ms) → las corridas «x10» fueron ≈ x13.5 y las frecuencias de los CSV del 11-18 calculadas con `t` salen ~1.35× demasiado altas. **Corregido 2026-11-19:** el CSV ahora trae `t_real` (reloj real) y `espectro_corrida.py` lo usa; probado solo en simulación. Para los CSV viejos, dividir las frecuencias entre ≈1.35 (aproximación).
- **Prueba extra en la RPi (si hay tiempo, con Luis en el paro):** pulsos chicos de SET_VEL con lazo abierto y el pie precargado a 500–900 N; si Fz suena a 6–8 Hz, el modo existe; medir su frecuencia y la rigidez real a carga alta.

## Paso 6 — Bloqueado, fuera de esta sesión
- **Hueco de 82 ms del lazo en la interfaz** (`~/Projects/gaitsim-control`, abortó la pisada 2 de 3 ejes el 11-18 por el
  detector de saltos): se corrige en ese repo, que no está en la laptop. No correr más pisadas de 3 ejes hasta corregirlo.
- **R6, pesas conocidas vs NetForce:** la calibración en N de la ruta UART sigue sin validar (solo hay una masa de
  2.246 kg en la laptop y confirmación cualitativa "3 M" en NetForce). Necesita las pesas y a Luis leyendo NetForce.
- **Ruido de 60 Hz** (σ ≈ 2.3–2.7 N en la RPi vs 0.75 N en la laptop, origen sin determinar): pruebas pendientes con
  laptop a batería, otra toma/fuente, motores apagados.

## Limitaciones
- Nada ejecutado; los valores de carga/tope/extra se calcularon con las mismas fórmulas de la tarde del 11-18.
- `interfaz/tools/medir_hueco.py` no se pudo leer desde la laptop (está en el repo de la interfaz): flags sin verificar.
- El script de espectro está por escribir; sin él el paso 2 deja datos pero no la decisión.
- Una sola carga y una prótesis: el resultado vale para `pie_pasivo_1` plano a 70 kg.

## Fuentes
- `control/lazo_fz_tiempo_real.py` (argparse 478–502, columnas del CSV línea 411), `control/escalera_carga.py`,
  `pruebas/etapa2_rpi.sh`, `pruebas/medir_latencia_ping_pong.py`, `herramientas/lanzar_interfaz_control.py`.
- `reportes/2026-11-18_escalera_50_a_90kg_x10_y_abortos.md`, `control/telemetria/registros/2026-11-18_15*_fz.meta.txt`.
- `CLAUDE.md` (reglas fijas), `INICIO_SESION_SIGUIENTE.md` (cómo operar la interfaz), `.gitignore`.
