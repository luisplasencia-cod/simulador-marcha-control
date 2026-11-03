---
name: diagrama-bloques-control
description: Dibuja diagramas de bloques de sistemas de control (lazo cerrado, PID, planta, sensor, filtro, ventilación, protecciones) en blanco y negro, estilo libro de texto, con las variables y ecuaciones en tipografía LaTeX dentro de una leyenda (caption) de la figura, no dentro de los bloques. Entrega diagrama, leyenda de variables y ecuaciones numeradas como SVG y PNG, listos para un documento o una página. Usar siempre que el usuario pida un diagrama de bloques, un lazo de control, "bloques con ecuaciones", un esquema de un PID o de cualquier sistema realimentado, ecuaciones en formato LaTeX para una figura, o que "se vea como en las fotos de ejemplo", aunque no diga la palabra "skill" ni "bloques".
---

# Diagrama de bloques de control, estilo libro de texto

Todo lo de esta skill vive en esta carpeta (ver `README.md`): biblioteca, plantillas, referencias de estilo y ejemplos. No hay copias en los proyectos.

Este es el estilo que el usuario eligió con cinco imágenes de ejemplo (ver `references/estilo.md` y `assets/referencias_estilo/`):
blanco y negro, cajas simples con el nombre, flechas con el nombre de la señal, círculos sumadores con signos, puntos de derivación,
recuadro punteado para el controlador PID, y todo lo matemático en tipografía de ecuación LaTeX. Las ecuaciones y las variables **no van dentro
de los bloques**: van en la leyenda de la figura, para que el dibujo se lea de un vistazo y la matemática se estudie aparte.

## Por qué este estilo

El usuario es nuevo en control y necesita entender qué hace cada bloque y de dónde sale cada símbolo. Un diagrama con ecuaciones dentro de las cajas
se vuelve ilegible; separar el dibujo de la leyenda deja cada cosa en su sitio, y el número `(n)` de cada bloque lo une con su ecuación.
Los diagramas de color o con texto largo dentro de los bloques ya se probaron y se descartaron.

## Qué entregar (siempre las tres piezas)

| Pieza | Contenido | Archivo |
|---|---|---|
| Figura | bloques, flechas, señales; cada bloque con su símbolo y el número `(n)` de su ecuación | `diagrama.svg` y `.png` |
| Variables | tabla de símbolos con su significado y unidad, parámetros aparte | `leyenda_variables.svg` y `.png` |
| Ecuaciones | numeradas `(1)`, `(2)`…; las del modelo del sistema con `(M1)`, `(M2)`… | `ecuaciones.svg` y `.png` |

Y un pie de figura de texto: "Figura N. …" que explique la convención (círculo = suma con signos, punto = derivación, recuadro punteado = grupo,
`(n)` = ecuación del mismo número). Ese pie va como texto editable bajo las imágenes, no dentro de ellas.

## Cómo hacerlo

1. **Entender el sistema.** Listar señales (nombre, qué es, unidad), bloques y el orden del lazo. Preguntar solo lo que no se pueda deducir.
2. **Partir de la plantilla.** Copiar `ejemplos/pid_simple.py` a la carpeta de trabajo y editarlo. Usa `scripts/bloques.py` (clase `Lienzo`,
   `tabla_variables`, `tabla_ecuaciones`, `guardar`, `svg_en_linea`). Para un caso grande con ventilación, protecciones y modelo de la planta,
   ver `ejemplos/control_presion_completo.py` (el sistema real de este usuario: bomba, válvula y sensor de presión).
3. **Ejecutar y mirar el resultado.** Correr el script y abrir los PNG con Read: revisar que ningún rótulo pise una caja o una línea, que ninguna
   flecha cruce un bloque y que todo el texto quepa. Corregir y repetir. Es la única forma fiable: matplotlib no avisa de solapes.
4. **Entregar** los archivos y, si el destino es un Google Doc o una página, seguir "Dónde se inserta".

## Reglas de estilo (el contrato)

- **Colores:** solo negro sobre blanco. El color solo se permite en una página interactiva para marcar un bloque (rojo), nunca en el archivo entregado.
- **Tipografía:** nombres de bloque y textos en Arial; símbolos y ecuaciones en LaTeX (mathtext, fuente Computer Modern). Los nombres de
  parámetros de varias letras van rectos: `$\mathrm{TAU}$`, `$\mathrm{PWM}^{*}$`. Letras sueltas, en cursiva: `$e(t)$`, `$K_p$`.
- **Bloques:** una caja por función, con el nombre en grande y, debajo, el símbolo del parámetro y el número `(n)`, p. ej. `$K_p$   (2)`.
  Una función de transferencia muy corta (como `1/(1+sT)`) puede ir dentro de la caja, como en las imágenes de ejemplo; una ecuación larga, nunca.
- **Señales:** cada flecha lleva su nombre en matemática (`$r(t)$`, `$e(t)$`, `$u(t)$`, `$y(t)$`, `$h(t)$` o los del sistema). La referencia entra por
  la izquierda y la medida vuelve por abajo hasta el sumador con signo `−`.
- **Sumadores:** círculo vacío con `+` y `−` junto a cada flecha de entrada. **Derivaciones:** punto negro.
- **PID:** tres ramas en paralelo (Proporcional, Integral, Derivativo) dentro de un recuadro punteado titulado "Controlador PID", con un sumador al final.
- **Ramas laterales** (ventilación, protección, anti-windup): cajas más abajo o arriba, con línea punteada si es una acción que no es señal de proceso.
- **Numeración:** `(1)…(n)` para el controlador y sus etapas; `(M1)…` para lo que es modelo del sistema y no código del controlador.
  Así se distingue de un vistazo lo que se puede cambiar de lo que solo se supone.
- **Leyenda de variables:** símbolo a la izquierda, significado y unidad a la derecha; los parámetros en un segundo bloque tras una línea.

## Reglas de diseño aprendidas (evitan los errores que ya ocurrieron)

- Los rótulos de señal sobre flechas cortas van **arriba de las cajas** (a `y = eje − 46`), no al nivel de su borde: ahí chocan con las cajas. Un rótulo
  junto a una línea punteada o a un recuadro se desplaza para no cruzarla.
- Dejar 30–40 px entre cajas consecutivas; si un símbolo largo no cabe (`$\mathrm{PWM}^{*}$`), subirlo en vez de ensanchar el hueco.
- Rutas de realimentación: la medida vuelve por abajo; una acción de otro bloque sobre la planta (p. ej. la válvula) entra rodeando el dibujo por el borde
  derecho y por arriba, para no cruzar la fila de realimentación. Evitar cruces de líneas: si no se puede, que no haya punto en el cruce.
- Lienzo de 1300–1400 px de ancho. Textos de bloque 21 px, subtexto 15 px, señales 20 px. Más pequeño no se lee al insertarlo a 468 pt en un documento.
- Matemática con comas decimales: `0{,}5` (con llaves, si no mathtext deja un espacio tras la coma).
- **Acentos**: no funcionan dentro de `\mathrm{}`. Las palabras con tilde van como texto Arial: en `tabla_ecuaciones` usar el campo `nota`, y en el diagrama,
  texto normal fuera de `$…$` (se puede mezclar: `"¿$y > r + \mathrm{BAND}$?"`).
- Mathtext no admite `\begin{cases}`, matrices ni todos los comandos de LaTeX; si da un error de análisis, simplificar (dos ecuaciones en la misma fila separadas
  por `\qquad` en lugar de `cases`). `\dfrac`, `\frac`, `\min`, `\max`, `\ln`, `\Delta`, `\tau`, `\int`, `\Rightarrow`, `\leq` funcionan.
- El tamaño de cada fila de `tabla_ecuaciones` es a mano: 36–40 px sin fracción, 62 px con fracción.

## Dónde se inserta

- **Página HTML:** `svg_en_linea(fig)` devuelve el SVG para pegarlo en la página (ancho 100 %). Cada bloque con `gid` queda como `<g id="gid">`; con una hoja de estilo
  `#diagSvg .hl path { stroke:#e11d48 !important; stroke-width:4px !important }` se marca el bloque desde JavaScript. La leyenda y las ecuaciones van como `<img src="…svg">`.
  El proyecto NEMA lo hace así (tarjeta 7 de `ble_control.html`): `ejemplos/control_presion_completo.py` trae también el HTML, el CSS y el JavaScript de esa
  integración y se ejecuta con el lanzador `C:\NEMA\esquema\generar_diagrama_bloques.py`.
- **Google Doc:** la API de Docs no crea ecuaciones nativas (solo las lee) y solo inserta imágenes desde una URL pública; Drive no comparte "con el enlace".
  Lo que funcionó (30-10-2026): con Claude in Chrome conectado, abrir el Doc, borrar la imagen vieja, crear con `javascript_tool` un `<input type=file multiple>` en la página,
  subir los PNG con `file_upload` y pegarlos con un `ClipboardEvent('paste')` sobre `iframe.docs-texteventtarget-iframe`, un archivo por párrafo; quitar el input al final.
  Sin Chrome, el usuario las inserta a mano (Insertar → Imagen → Subir desde el equipo). Las imágenes entran a 468 pt de ancho; el texto interno queda pequeño, así que
  conviene que el usuario las agrande o regenerar con letra mayor.
- **Otros destinos:** PNG a 300 dpi para presentaciones o informes; SVG para edición vectorial.

## Referencias de la convención

- K. J. Åström y R. M. Murray, *Feedback Systems* (2.ª ed.), cap. 11 (PID): flechas con el nombre de la señal, sumador con signos, medida de vuelta por abajo.
- Documentación del bloque PID Controller de Simulink: anti-windup por retrocálculo o por límite, filtro, saturación.
- Modelica Standard Library, bloque `LimPID`: error, límite de salida y anti-windup en un lazo.
- Las cinco imágenes de ejemplo del usuario, descritas en `references/estilo.md`.
