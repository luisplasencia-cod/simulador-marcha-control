# ¿Cómo se controlan las prótesis activas de tobillo y qué es "integrarlas" al simulador? (2026-11-26)

Pregunta de Luis: ¿las prótesis actuales (comerciales e investigación) usan trayectorias fijas o señales mioeléctricas (EMG)? Si fuera EMG, la activa del lab necesitaría su algoritmo de EMG y el simulador debería enviarle esas señales para una integración real.
Fuentes: búsqueda web 2026-11-26, leídos solo resúmenes/páginas; **DOI sin verificar y sin lectura de Luis** (no son respaldo final).

## 1. Lo que dice la literatura
- **Ninguna prótesis de pierna comercial usa EMG.** Revisión sistemática con Hargrove como coautor (Ahkami et al. 2023, 121 artículos incluidos): "no commercially available lower limb prosthesis integrates signals from the user's neuromuscular system"; controlar con EMG "remains challenging"; un error puede causar una caída. https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10470657/
- **Las prótesis robóticas se controlan sobre todo de forma autónoma**, con sus propios sensores (Fleming, Stafford, Huang, Hu, J Neural Eng). https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8694273/
- **Esquema dominante: 3 niveles** (Gehlhar et al. 2023, Annual Reviews in Control): alto = estimar tarea y fase de la marcha; medio = calcular el torque deseado; bajo = seguir ese torque. https://pmc.ncbi.nlm.nih.gov/articles/PMC10449377
  - **Máquina de estados + impedancia** (el tobillo se comporta como resorte-amortiguador distinto en cada fase): lo más usado; decenas de parámetros ajustados a mano por persona.
  - **Variable de fase continua** (la fase se estima del ángulo del muslo/pierna): tendencia creciente (Best et al. 2023, IEEE T-RO). https://pmc.ncbi.nlm.nih.gov/articles/PMC10249435
  - **EMG**: investigación, minoría; sin métricas estandarizadas para comparar controladores (revisión JNER 2022, doi 10.1186/s12984-022-01019-1); señales de músculos residuales distintas a las de músculo intacto. Posh et al. 2023 (IEEE TNSRE) comparan impedancia por estados vs control mioeléctrico directo y su combinación (texto no leído).
- **Comercial: Ottobock Empower** (antes BiOM). Ottobock dice que "sensors regulate the intensity of the forward thrust"; una ficha de estudio holandés dice que incluye un modelo neuromuscular de reflejos y compara con un controlador por EMG estudiado aparte → el comercial es por sensores y modelo, no por EMG (no confirmado en documentación técnica). https://www.ottobock.com/en-us/product/1A1-2 · https://onderzoekmetmensen.nl/en/node/56131/pdf
- **Ni trayectorias fijas ni EMG puro:** los controladores reaccionan a lo que miden (carga, ángulos, velocidades). No reproducen una trayectoria grabada.

## 2. Bancos y simuladores que ya probaron prótesis activas
- **Yang 2020 (U. Bath, tesis EngD):** simulador de marcha con ILC extendido sobre la GRF, validado "with passive ankle prostheses and active ankle prostheses"; detectó potencia insuficiente en el empuje, como en pruebas con personas. El resumen no dice cómo se sincronizó la activa (está en el PDF de 30 MB). **Es el antecedente más cercano y ya está como lectura prioritaria.** https://researchportal.bath.ac.uk/en/studentTheses/development-of-a-gait-simulator-for-testing-lower-limb-prostheses/
- **Ficanha et al. 2017 (Michigan Tech):** emulador de marcha para un tobillo activo, control híbrido en lazo cerrado **con detección de eventos cinemáticos** para que los ensayos sean repetibles. https://digitalcommons.mtu.edu/michigantech-p/11815
- **Emulador biarticular (PMC11406492, 2024):** prótesis de tobillo + exoesqueleto de rodilla con controlador externo; ILC baja el error de torque de 6,04 a 0,99 N·m. https://pmc.ncbi.nlm.nih.gov/articles/PMC11406492
- **Caputo & Collins 2013/2014 (CMU):** emulador con motor y control fuera de la prótesis (para probar estrategias con personas). https://www.andrew.cmu.edu/user/shc17/Caputo_2013_ICRA.pdf
- **EMG en banco:** no se halló un banco que reproduzca EMG grabado hacia un tobillo. Lo más cercano: un simulador de señal tipo EMG (WPI 2010) para probar prótesis mioeléctricas de miembro superior, que genera una señal "aproximadamente equivalente", no EMG real. https://users.wpi.edu/~ted/full_text_confer/2010patrick_meklenburg_nebio.pdf

## 3. Qué significa para la activa del lab y el simulador (análisis propio)
**Integración real = que el controlador de la prótesis reciba en el simulador las mismas entradas que recibiría en una persona.** Qué entradas son depende de cómo controla la prótesis:

| Nivel | Qué hace el simulador | Cuándo aplica | Realismo / riesgo |
|---|---|---|---|
| **A. Autónoma (mecánica)** | Impone movimiento de la pierna (3 ejes) y carga; la prótesis detecta sus fases con sus sensores | Prótesis con máquina de estados o variable de fase (lo comercial y casi toda la investigación) | El más realista; es lo que hacen Yang 2020 y Ficanha 2017 |
| **B. Guiada** | La RPi le manda una señal de fase/sincronía | Si a x10 la prótesis no detecta bien sus fases | Más simple; la detección de fase deja de ser de la prótesis (declararlo) |
| **C. EMG emulado** | Generar o reproducir EMG hacia la prótesis | Solo si la prótesis se controla por EMG | Sin precedente hallado para tobillo en banco; EMG de muñón distinto al sano; a x10 habría que estirar 10× la señal; exige implementar antes el control por EMG en la prótesis |

- **Lo que hay registrado:** CLAUDE.md dice que la activa del lab tiene **su propio controlador de máquina de estados**, ya corre a x6 y es modificable → corresponde el **nivel A**, con B como respaldo. No hace falta EMG.
- **Riesgo técnico concreto de la escala (inferencia):** las transiciones de una máquina de estados suelen usar umbrales de carga, ángulo y velocidad angular. A x10 la carga es la real (umbrales de fuerza valen), los ángulos son los mismos, pero **las velocidades angulares y los tiempos de cada fase cambian 10×** → los umbrales de velocidad y de tiempo hay que reescalarlos. El empuje motorizado a x10 también cambia (potencia = torque × velocidad: misma energía en 10× más tiempo).
- **Si el lab quiere EMG:** es un proyecto aparte (algoritmo, entrenamiento por persona, seguridad), casi otra tesis; no entra en la práctica 3. Queda como idea futura.

## 3b. Qué RECIBE una prótesis activa y qué tiene que reproducir el simulador para cualquiera (análisis propio, 2026-11-26)
Idea (Luis): integración que sirva para la activa del lab y para cualquier activa existente o futura; EMG = idea futura.
Una prótesis activa no recibe "órdenes": **mide con sus sensores lo que le pasa físicamente** y su controlador decide. Si el simulador reproduce físicamente lo que una persona le hace a la prótesis, cualquier prótesis funciona sin cables ni código a medida (integración "por la física").

| Lo que mide la prótesis (sensor típico) | Qué lo produce en el simulador | ¿Sirve hoy a x10? |
|---|---|---|
| Carga en el pilón / fuerza del suelo (celda de carga, galgas, corriente del motor) | Lazo de Fz (y Fy) | **Sí** (la fuerza es real) |
| Avance del apoyo talón → antepié (sensores de suela, torque del tobillo) | Sagital guiado por el CoP (práctica 1) | **Sí** |
| Ángulo del tobillo (encoder) | Respuesta de la propia prótesis bajo la carga | **Sí** |
| Inclinación de la pierna (IMU) | Eje sagital K | **Sí** |
| Velocidad angular y aceleración de la pierna (IMU) | Movimiento de los 3 ejes | **No**: 10× menor velocidad, 100× menor aceleración |
| Tiempos de cada fase (temporizadores) | Duración de la pisada | **No**: 10× más largos |
| Fase de balanceo sin carga (el pie en el aire, reinicia la máquina de estados) | Hoy no: las trayectorias son solo de APOYO | **Falta** |
| Botones / app de modo | Manual | Sí |
| EMG | — | Idea futura |

**Consecuencias:**
1. **El simulador ya cubre la parte que no depende del tiempo** (carga, avance del CoP, ángulos).
2. **Falta el ciclo completo**: apoyo + balanceo (subir el pie, avanzar, volver a contactar). Sin balanceo, una activa no recorre sus estados.
3. **La escala x10 es el límite para "cualquier prótesis":** un controlador que estima la velocidad de marcha o usa umbrales de velocidad/tiempo (p. ej., el Empower ajusta el empuje a la velocidad; inferencia, sin documentación técnica) verá una marcha 10× más lenta y responderá como tal. Con la activa del lab se pueden reescalar sus umbrales (es modificable); con una comercial, no. Para que valga para cualquier prótesis hace falta tiempo real (x1) o, mientras tanto, declararlo y usar prótesis con parámetros ajustables.
4. **Canal digital opcional** (no obligatorio): señal de sincronía/fase y marca de tiempo desde la RPi, para registrar junto al AMTI y como respaldo si un prototipo no detecta sus fases.

## 3b-bis. Dato real de la activa del lab (Luis, 2026-11-26)
- Se mueve con **trayectorias predefinidas, sin sensor que las actualice** (no reacciona a la carga). → Hoy sus "entradas" son de tiempo: cuándo arrancar, a qué escala de tiempo y qué trayectoria (apoyo o balanceo). La integración actual = **sincronizar el arranque de su trayectoria con la fase del simulador** (nivel B de la tabla).
- **El simulador no puede hacer apoyo y balanceo seguidos** (espacio) → ensayos por fase, separados.
- La integración "por la física" (§3b) sigue siendo la idea final para prótesis con sensores (comerciales o una versión futura de la del lab).

## 3c. EMG: no descartado, en investigación (2026-11-26)
- La literatura lo trata como **línea abierta y prometedora**, no como algo fallido: el control autónomo funciona en marcha cíclica, pero no sabe lo que la persona QUIERE hacer (subir escaleras, cambiar de ritmo, ponerse de puntas); el EMG da esa intención (control "volitivo").
- Lo más probable a futuro (opinión, coincide con trabajos recientes): **control híbrido** = autónomo por fases + EMG que modula (Posh et al. 2023, impedancia por estados + mioeléctrico directo; https://arxiv.org/pdf/2309.15955 control volitivo híbrido con variable de fase). Con interfaz neural quirúrgica, el grupo de Herr reporta marcha más natural (Song et al. 2024, Nature Medicine; no leído aquí).
- Barreras actuales: señal del muñón poco fiable (sudor, desplazamiento de electrodos, fatiga), entrenamiento por persona, seguridad (un error = caída), sin métricas estándar para comparar.
- Para el simulador: una prótesis con EMG necesitaría además un canal de EMG emulado (nivel C). Queda como idea futura, compatible con la integración "por la física" (se suma, no la reemplaza).

## 4. Para preguntar al grupo de la activa
1. ¿Cómo detecta hoy las fases (qué sensores: carga, encoder, IMU) y con qué umbrales?
2. ¿Esos umbrales dependen del tiempo o de la velocidad (afectados por x10)?
3. ¿Acepta una señal externa de fase/sincronía?
4. ¿Hay planes de control por EMG? ¿Quién lo haría?
