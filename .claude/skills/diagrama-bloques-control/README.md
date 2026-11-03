# Diagramas de bloques de control: todo en esta carpeta

**Ubicación (la única):** `C:\Users\chees\.claude\skills\diagrama-bloques-control\`
Para abrirla: pegar esa ruta en el Explorador de archivos, o ejecutar `explorer C:\Users\chees\.claude\skills\diagrama-bloques-control`.

Es una *skill* de usuario: Claude Code la encuentra solo en cualquier proyecto cuando se pide un diagrama de bloques, un lazo de control o
"el estilo de las fotos". No hay que copiarla a cada proyecto.

## Qué hay dentro

| Qué | Dónde | Para qué |
|---|---|---|
| Instrucciones para Claude (el estilo, las reglas) | `SKILL.md` | Es lo que Claude lee. Aquí está el estilo fijado. |
| Biblioteca de dibujo | `scripts/bloques.py` | Funciones: bloque, sumador, flechas, punto, recuadro punteado, tabla de variables, tabla de ecuaciones, guardar SVG y PNG. |
| Plantilla para un sistema nuevo | `ejemplos/pid_simple.py` | Copiarla y cambiar nombres, símbolos y ecuaciones. |
| El diagrama grande de NEMA (control de presión) | `ejemplos/control_presion_completo.py` | Única definición de ese diagrama; se regenera con el lanzador del proyecto. |
| Tus 5 imágenes de ejemplo del estilo y qué se tomó de cada una | `assets/referencias_estilo/` y `references/estilo.md` | Referencia visual. |
| Resultados de ejemplo ya generados | `assets/ejemplo_pid_simple/`, `assets/ejemplo_control_presion/` | Para ver cómo debe quedar. |

## Cómo usarla

- **En un proyecto nuevo:** pedirle a Claude "haz el diagrama de bloques de X con el estilo de la skill". Claude copia `ejemplos/pid_simple.py` a tu proyecto,
  lo adapta, lo ejecuta, revisa las imágenes y te entrega tres piezas: `diagrama`, `leyenda_variables` y `ecuaciones` (SVG y PNG) más el pie de figura.
- **A mano:** `python ejemplos\pid_simple.py MI_CARPETA` genera el ejemplo; editar una copia del archivo para cambiarlo.
- **Control de presión de NEMA:** `python C:\NEMA\esquema\generar_diagrama_bloques.py` regenera las imágenes y la tarjeta 7 de `ble_control.html`.
  Para cambiar ese diagrama se edita `ejemplos/control_presion_completo.py` (aquí), no el lanzador.

## Requisitos

Python con `matplotlib` y la fuente Arial (viene con Windows). La matemática usa la fuente Computer Modern que trae matplotlib; no hace falta instalar LaTeX.

## En otro equipo

Copiar esta carpeta completa a `C:\Users\<usuario>\.claude\skills\`. Nada más depende de rutas de este equipo, salvo el lanzador del proyecto NEMA
(`C:\NEMA\esquema\generar_diagrama_bloques.py`), que apunta a la ruta de arriba.
