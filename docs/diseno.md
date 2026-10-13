# Diseño de ReparaCampus

**Estado:** Aprobado por el equipo; falta registrar revisor, fecha y observaciones.  
**Tecnologías propuestas:** Python, Flask y SQLite

## Partes del sistema

1. **Interfaz:** pantallas para iniciar sesión, registrar incidencias y consultar reportes.
2. **Reglas del sistema:** comprueba permisos, calcula prioridades y controla los cambios de estado.
3. **Base de datos:** guarda usuarios, incidencias, asignaciones, soluciones e historial.

La aplicación será un solo sistema Flask organizado en esas tres partes. Las reglas se comprobarán en el servidor, aunque la solicitud venga de una pantalla.

## Datos que necesitamos guardar

- **Usuarios:** nombre de acceso, contraseña guardada de forma segura, rol y si la cuenta está activa.
- **Incidencias:** código, solicitante, ubicación, categoría, descripción, impacto, riesgo para personas, prioridad, estado y fecha de creación.
- **Asignaciones:** incidencia, técnico asignado y coordinador que hizo la asignación.
- **Soluciones:** incidencia, técnico, texto de la solución y fecha. Se guarda cada solución, aunque luego sea rechazada.
- **Eventos:** quién hizo cada acción, cuándo, qué acción realizó, estado anterior y nuevo, y motivo si corresponde. Los eventos de cierre anteriores se conservan después de reabrir.

## Reglas que debe cumplir el servidor

- Solo el solicitante dueño puede confirmar, rechazar o reabrir su incidencia.
- La reapertura solo se permite hasta 48 horas después del último cierre y requiere motivo de 10 a 300 caracteres.
- Cada operación inválida se rechaza sin cambiar estado, solución ni historial.
- Toda operación válida y transición de estado se guarda con su actor y fecha; los eventos y las soluciones anteriores no se editan ni se eliminan.
- El porcentaje de cierre se calcula con incidencias cuyo estado actual es CERRADA; por ello, una reapertura reduce el porcentaje y deja intacto el evento de cierre previo.

## Revisión del diseño

El equipo confirmó que revisó y aprobó este diseño. Para completar la evidencia del examen se debe registrar:

- **Revisor:** por registrar
- **Fecha:** por registrar
- **Decisión:** aprobado por el equipo
- **Observaciones:** por registrar

## Decisión tecnológica

Usaremos Flask para el servidor porque permite construir el prototipo con Python y mantener las reglas del sistema en un solo lugar. Usaremos SQLite para guardar la información en un archivo, lo que facilita ejecutar y entregar el proyecto sin instalar un servidor de base de datos.

Una alternativa sería PostgreSQL, que permite manejar mejor varios usuarios trabajando al mismo tiempo, pero requiere configurar un servicio adicional. Para este prototipo académico, Flask y SQLite son suficientes y más sencillos de ejecutar. Si el sistema se usara en producción con muchos usuarios, habría que evaluar una base de datos como PostgreSQL.
