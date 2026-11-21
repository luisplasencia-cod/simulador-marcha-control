# Ideas de prácticas futuras que suman a la tesis (2026-11-21)

Estado: **propuestas de análisis, no presentadas ni aprobadas.** Ninguna decidida por Luis. No hay respuesta aún de Dante Elías ni de la asesora.

## Criterios de selección (análisis del 2026-11-21)
- **Aceptación:** una práctica para biomédicos debe hablar de prótesis, marcha o medición; el control es la herramienta, no el título (la profesora aceptó «validación» por esa razón). Un título de control puro puede parecer mecatrónico.
- **Tesis:** no entregar a un practicante un lazo central (Fz, Fy, CoP): diluye el aporte de la tesis y supervisar control exige nivel que Luis aún está desarrollando.
- **Cronograma:** entrega teórica marzo-abril 2027; práctica FSR ~dic 2026. Preferir ideas que no dependan de que el control cerrado esté terminado.
- **Seguridad:** el simulador puede dañar una prótesis (HOME con pie, sobrecarga; pico máx 1500 N). Un practicante que lo opere necesita procedimiento escrito y supervisión (idea 5).

## Propuestas (por orden de recomendación)
| # | Título propuesto | Por qué es biomédica | Depende del control completo | Riesgos / pendientes |
|---|---|---|---|---|
| 1 | *Desarrollo de un protocolo de caracterización mecánica de pies protésicos transtibiales en un simulador de marcha: rigidez, histéresis y energía devuelta* | Caracteriza dispositivos; entregable reutilizable (procedimiento + tabla por prótesis). Generaliza el Ensayo A/B. Permite que otras prácticas prueben prótesis más baratas y más fieles. | No (basta Ensayo A) | Contrastar con normas de ensayo (ISO 10328 / ISO 22675: de memoria, **verificar**). Definir «fidelidad». |
| 2 | *Efecto de la velocidad de ensayo sobre la respuesta mecánica de pies protésicos: ¿es válido simular la marcha a escala lenta?* | Pregunta de validez del método. **Amenaza real a la tesis:** a x10 los materiales viscoelásticos (espuma, elastómeros) pueden comportarse distinto que a marcha real; el carbono, menos (inferencia propia, sin fuente). | No (Ensayo A a varias velocidades) | Rango de velocidades alcanzable por el simulador; sin dato de referencia a velocidad real. |
| 3 | *Validación del control de fuerza de reacción del suelo de un simulador de marcha frente a datos de marcha humana: repetibilidad y concordancia* | Continuación natural de la práctica 1 de Luis (validación). ICC, CV, RMSE/r sobre toda la curva. Referencias: Gutenberg 2021, Fukuchi 2018. | **Sí** (después de cerrar Z, Y y sagital) | Umbral de error aún sin fijar (ver CLAUDE.md). |
| 4 | *Implementación y verificación de un flujo de análisis de potencia y energía de prótesis transtibiales a partir de fuerza y cinemática* | Biomecánica: CoP, P, E_abs/E_dev (método 6.1 de la tesis; validación con bloque rígido P≈0). | Parcial (usa datos grabados) | Más procesamiento de señales que control; falta geometría del punto A y convención de signos. |
| 5 | *Análisis de riesgos y procedimientos de seguridad de un simulador de marcha para ensayo preclínico de prótesis* | Gestión de riesgos (enfoque biomédico regulatorio). Reduce un riesgo real y es condición previa para que un practicante opere el simulador. | No | Casi sin dependencia de hardware. |
| 6 | Efecto del calzado en la respuesta de pies protésicos | Extensión de la 1 (calzado = entrada del protocolo de k). | No | Interesa a Luis como estudio futuro; mantener condición de calzado fija y anotada mientras tanto. |
| 7 | *Estimación en línea de la rigidez de pies protésicos para ajustar el control de fuerza* (única opción «de control») | Control con aplicación clínica. | Sí | **Se solapa con la tesis** (estimador ya preparado en `control/identificacion/estimador_k_en_linea.py`, sin integrar). Solo si se separa claramente: practicante = estimador, Luis = lazo. |

## Recomendación (análisis, no decisión)
Primero 1 y 2 (más aceptables, no esperan al control, la 2 reduce un riesgo de la tesis); 5 como paso previo a que un practicante opere el simulador; 3 cuando el lazo esté cerrado.

## Contexto relacionado
- Pie de fibra de carbono en compra (datos pendientes): `protesis/pie_carbono_01/FICHA.md`, `reportes/2026-11-21_pie_carbono_analisis_previo.md` (un protocolo genérico para cualquier prótesis fue decisión de Luis, 2026-11-21).
- Protocolo de rigidez k(F): `reportes/2026-11-20_protocolo_identificacion_rigidez_estandar.md`.

## Pendiente antes de presentar
Formato que pide el jefe para proponer una práctica (título, objetivo, semanas, entregables); con eso se arma una propuesta de una página por idea elegida.
