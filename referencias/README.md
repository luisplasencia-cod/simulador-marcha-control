# Convención de la carpeta `referencias/`

Cada referencia leída vive en su propia subcarpeta, dentro de la categoría que le corresponda:

- `01_vacio_investigacion/`
- `02_control_fuerza_grf/`
- `03_energia/`
- `04_interfaz_protesis/`
- `05_otros/`

## Estructura de cada referencia

```
<categoria>/Apellido_Año/
    fuente.pdf      (si se consiguió el PDF)
    fuente.md       (si no hay PDF: link + DOI)
    notas.md        (extracto puntual: qué se usó, página, cita textual corta, figuras relevantes)
    fig_X.png       (figura extraída del paper, si aplica — nunca dibujada por Claude)
```

`notas.md` es un extracto, no una síntesis interpretativa (regla del proyecto: el usuario lee y decide el enfoque). El PDF es para que Luis lo lea — Claude lo abre una sola vez para extraer y después trabaja solo con `notas.md` (así no se re-lee el PDF completo cada sesión, eso gasta tokens de más). Formato con dos partes separadas:

```
## Clave para decisión
(1-3 líneas máx: qué cierra/confirma/cambia esto para el proyecto — lo mínimo
que Luis necesita para decidir algo, sin tener que abrir el PDF)

## Resumen de lectura
(extracto más completo: metodología, resultado puntual, cita textual corta con
página — para cuando Luis quiera más detalle sin abrir el PDF)

## Figura
fig_1.png — qué muestra (una línea, solo descriptiva)
```

Esta carpeta es la fuente de material (PDFs, extractos, figuras). El razonamiento/comparación entre referencias sigue en `HISTORIAL.md`; el estado vigente de qué referencia está confirmada sigue en `CLAUDE.md`. Las categorías (01-05) no son fijas: si aparece un tema nuevo que no calza, se agrega una carpeta nueva sin problema.
