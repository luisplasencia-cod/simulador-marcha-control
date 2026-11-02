## Clave para decisión
Control difuso de GRF vertical en simulador robótico cadavérico: la trayectoria se actualiza ITERATIVAMENTE entre simulaciones (no en tiempo real), filtrada a 5 Hz. NO reporta ancho de banda ni latencia del lazo de fuerza.

## Resumen de lectura
Leído en el PDF (fuente.pdf). Citas: "A fuzzy logic vGRF controller was developed, which altered tendon forces in real time and iteratively adjusted the robotic trajectory in order to track a target vGRF"; "average root-mean-square error of only 5.6%" (BW); "The x(n) output from the fuzzy logic vGRF controller was filtered with a second-order 5-Hz Butterworth low-pass filter and used to update the R2000 trajectory iteratively between gait simulations"; Fig. 6: salida x(n) "updated iteratively rather than in real time"; placa Bertec "sampling at 600 or 1500 Hz"; controlador PID de tendones en PXI tiempo real.
Búsqueda en el texto de bandwidth/latency/delay/Hz: solo aparecen la tasa de la placa, el filtro de 5 Hz y un retardo electromecánico muscular (no del lazo). Sin dato de latencia máxima tolerable.
(Sin número de página: el PDF se leyó como texto.)

