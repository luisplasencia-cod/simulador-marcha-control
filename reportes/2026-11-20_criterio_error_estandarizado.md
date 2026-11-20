# Criterio de error estandarizado para el lazo de Fz (2026-11-20) — PROPUESTA

## Objetivo
Reemplazar el umbral "< __ %BW" fijado a mano por un criterio apoyado en métricas estadísticas de la literatura (r, CMC, RMSE), y evaluar con él nuestros datos. Luis dijo "un RMSE menor a 1 y un r casi igual a 1"; **la unidad del RMSE no está dicha y no se supone** (se muestran las tres posibles).

## Metodología
Búsqueda web (WebSearch/WebFetch, Crossref para DOI) el 2026-11-20. Solo se anota lo que se leyó o vio en el resultado; lo que vino de un resumen de buscador se marca. Ninguna fuente fue leída por Luis (regla del proyecto: "DOI verificado, lectura sin confirmar").
Definición en nuestros datos (`herramientas/analizar_pisadas_interfaz.py`): `e = objetivo_N − Fz_N`; `RMSE_N = sqrt(mean(e²))` sobre la pisada; `RMSE_pct_pico = 100·RMSE_N/max(objetivo)`; `r` = Pearson(objetivo, Fz). Conversión a %BW: RMSE_N/(80 kg·9.81 N/kg = 785 N); el pico del objetivo de 80 kg ≈ 950 N (deducido de 11.4 N = 1.2 %), valor aproximado.

## Resultado
**Lo que dice la literatura**
- **r / CMC: sí hay bandas.** Blanco-Coloma 2024 (leído en el texto) usa: pobre 0–0.65, moderado 0.65–0.75, bueno 0.75–0.85, muy bueno 0.85–0.95, excelente 0.95–1, atribuidas a Ferrari 2010 y Yavuzer 2008, y exige CMC "excelente" en el plano sagital. Di Marco 2018 (solo por resumen de buscador, texto no abierto): <0.60 pobre, ≥0.95 excelente. Son bandas para cinemática articular, no GRF: **trasladarlas a Fz es una extrapolación.**
- **RMSE: NO hay umbral estándar universal.** Blanco-Coloma 2024 reporta RMSE sin umbral de aceptación. Para GRF vertical, los estudios de estimación (resumen de buscador, sin DOI verificado) hablan de RMSE ≈ 0.15–0.20 BW (≈6–7 % del rango) como "bueno" y una validación de plataforma de fuerza usó RMSE < 0.20 e ICC > 0.95 como criterio propio. Son criterios de cada estudio.
- **Antecedente de simulador de marcha con ILC:** Aubin, Cowley, Ledoux 2008 (robot paralelo 6 GDL, ILC): el resumen de buscador da RMS de Fz 78.7 N → 9.4 N con ILC (no se abrió el texto; no se pudo confirmar normalización ni condiciones).

**Nuestros datos**
| Caso | RMSE N | % pico | %BW (aprox.) | r |
|---|---|---|---|---|
| Base interfaz 3 ejes, 80 kg | ≈34 (de 3.6 %) | 3.6 | ≈4.4 | 0.988 |
| Solo Y script, con mejora | 11.4 | 1.2 | ≈1.45 | 0.999 |

- r: 0.988 y 0.999 caen en "excelente" (≥0.95) en las dos fuentes.
- RMSE ≈ 0.014–0.044 BW: muy por debajo del 0.15–0.20 BW que se ve en estudios de estimación (comparación no equivalente: aquellos estiman GRF sin control).
- Contra la frase de Luis: si "RMSE < 1" fuera **%pico o %BW**, 3.6 % y 1.2 % **no cumplen**; si fuera en **BW** (fracción), cumplen de sobra. Hay que fijar la unidad.

## PROPUESTA (a decidir por Luis/asesora; no es decisión)
Criterio de pasar a Fy sobre varias pisadas seguidas a 80 kg, 3 ejes: (1) r ≥ 0.95 (banda "excelente"); (2) RMSE normalizado ≤ X con X en **%pico (o %BW)** a elegir; sugerencia de partida ≤ 5 % del pico (cumplida hoy por 3.6 %), con la meta ≤ 2 % apoyada solo en el resultado del script, no en un estándar; (3) repetibilidad: mismas métricas en ≥ 2 series, reportando media ± desviación. Ningún valor de (2) es estándar de la literatura.

## Limitaciones
- Las bandas de r/CMC vienen de cinemática, no de GRF de simulador.
- No se encontró umbral estándar de RMSE ni de r para simuladores de marcha/HIL.
- Varias cifras (Di Marco, estudios GRF, Aubin) vienen de resúmenes de buscador, no del texto; Røislien 2012 no se pudo verificar (no hay DOI confirmado) y se omite; Kadaba 1989 = en realidad Kadaba 1990 (DOI abajo).
- Nuestros números son de una prótesis, una escala (x10), y el 1.2 % no se probó aún en la interfaz.

## Fuentes (todas: lectura de Luis = NO)
| Fuente | DOI | Qué da |
|---|---|---|
| Ferrari, Cutti, Cappello 2010, Gait & Posture 31:540 | 10.1016/j.gaitpost.2010.02.009 | Formulación del CMC (DOI verificado en Crossref; bandas no leídas aquí, solo vía Blanco-Coloma) |
| Blanco-Coloma et al. 2024, Front. Bioeng. Biotechnol. 12 | 10.3389/fbioe.2024.1449698 | Bandas r/CMC (leídas); RMSE sin umbral |
| Di Marco et al. 2018 | 10.1080/23335432.2018.1426496 | CMC <0.60 pobre, ≥0.95 excelente (solo buscador) |
| Kadaba et al. 1990, J Orthop Res | 10.1002/jor.1100080310 | CMC original (solo DOI) |
| Iosa et al. 2014, BioMed Res Int | 10.1155/2014/214156 | Método de ajuste lineal vs r/RMSE/CMC (solo DOI) |
| Aubin, Cowley, Ledoux 2008, IEEE TBME | 10.1109/tbme.2007.908072 | Simulador de marcha con ILC, RMS de Fz (solo buscador) |
