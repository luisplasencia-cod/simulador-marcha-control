# Identificación de la planta de fuerza vertical — PROTOCOLO PROPUESTO (no ejecutado)

**Estado: borrador para que Luis lo revise. No se ha movido ningún motor. Cada ensayo que mueva el simulador necesita el OK de Luis y el simulador despejado.**

## Objetivo
Obtener con datos reales los dos parámetros que hoy están "sin medir" en la simulación (`control/simulacion/`): (1) la **rigidez de contacto** prótesis–plataforma, `k` (cuánta fuerza cambia por cada mm que se mueve el eje vertical), y (2) la **respuesta del actuador** (servo vertical + driver): retardo y constante de tiempo entre la orden de pasos y el movimiento real. Con eso se diseña el controlador (Kp, ILC) con una planta medida y no supuesta.

## Por qué importan (en simple)
- `k` fija la ganancia entre desplazamiento y fuerza: si la prótesis es más rígida, la misma orden produce más fuerza. **Cada prótesis tiene su propia `k`** (y no es constante: el pie se endurece al cargarse), y es justo lo que se quiere comparar; además la curva fuerza–desplazamiento sirve para la energía absorbida/devuelta (CLAUDE.md, método de energía).
- La respuesta del actuador (y la latencia del ESP32) decide cuánto retardo real tiene el lazo, más allá de la comunicación ya medida.

## Ensayo A — rigidez `k(F)` por prótesis
- **Método:** con la prótesis montada, subir despacio el eje vertical (incrementos pequeños y fijos, con `MANUAL`/`GOTO` existentes o una trayectoria precargada), esperar a que la fuerza se estabilice en cada escalón, y registrar `Fz` (AMTI vía ADS1256 a 1 kHz) y la posición en pasos (`GET_POSITION`). `k` = pendiente fuerza/desplazamiento, por tramos de fuerza.
- **Dato que falta (no verificado):** conversión pasos → mm del eje vertical (paso del husillo, relación electrónica del driver). Obtenerla de la configuración del driver/CAD, o medirla con una regla o con el sensor de desplazamiento cuando se instale. No usar un valor de memoria.
- **Salida:** curva `F(x)` por prótesis y `k` por tramos; si dos prótesis no se distinguen, también es un resultado.

## Ensayo B — respuesta del actuador
- **Método:** órdenes de desplazamiento conocidas (sin carga o con la plataforma libre) y medición del movimiento real (sensor de desplazamiento vertical, cuando esté instalado) frente al tiempo; estimar retardo de arranque y constante de tiempo.
- **Opcional sin cambiar firmware:** leer con un GPIO del RPi la señal STEP del ESP32 (salida de 3.3 V; GND común; resistencia en serie) y medir el tiempo desde que se envía el comando hasta el primer pulso = latencia de ejecución del ESP32. **Requiere cableado de Luis** y revisar que no cargue la línea de los opto-aisladores.

## Seguridad (obligatorio)
- Límite de fuerza de diseño **1500 N** (decidido por Luis); empezar con fuerzas bajas (por ejemplo, unas decenas de N) y subir de a poco.
- Freno del eje vertical y finales de carrera activos; mano en el paro de emergencia; sin personas en el recorrido.
- No usar `HOME` ni movimientos sin que Luis confirme que el simulador está despejado.
- Parar si `Fz` supera el límite acordado o si la lectura del AMTI es anómala (recordar el AIN0 inestable observado hoy: revisar antes).

## Qué necesito de Luis para ejecutarlo
Prótesis montada, simulador despejado, OK explícito por ensayo, conversión pasos→mm (o permiso para medirla), y confirmar si el AMTI está estable con el plato vacío.
