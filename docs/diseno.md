# Diseño de ReparaCampus

**Estado:** Borrador  
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
- **Eventos:** quién hizo cada acción, cuándo, qué acción realizó, estado anterior y nuevo, y motivo si corresponde.

## Decisiones pendientes de revisión

El equipo debe confirmar que este diseño coincide con las SPECS revisadas antes de implementar la base de datos.

## Decisión tecnológica

Usaremos Flask para el servidor porque permite construir el prototipo con Python y mantener las reglas del sistema en un solo lugar. Usaremos SQLite para guardar la información en un archivo, lo que facilita ejecutar y entregar el proyecto sin instalar un servidor de base de datos.

Una alternativa sería PostgreSQL, que permite manejar mejor varios usuarios trabajando al mismo tiempo, pero requiere configurar un servicio adicional. Para este prototipo académico, Flask y SQLite son suficientes y más sencillos de ejecutar. Si el sistema se usara en producción con muchos usuarios, habría que evaluar una base de datos como PostgreSQL.
