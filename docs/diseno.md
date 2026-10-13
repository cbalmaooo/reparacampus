# Diseño de ReparaCampus

**Versión de diseño:** 2.0  
**Estado:** actualizado para describir la arquitectura implementada en la rama principal. La revisión de este cambio queda registrada en el pull request #20.  
**Tecnologías:** Python, Flask, SQLite, HTML/CSS y pytest.

## Componentes

1. **Interfaz web:** plantillas HTML y CSS para autenticación, registro, asignación, atención, validación, consultas, historial y tablero.
2. **Autenticación y rutas:** Flask mantiene la sesión y protege las rutas por rol; las rutas validan la petición y llaman a los servicios.
3. **Dominio y servicios:** las reglas de prioridad, permisos, estados, plazo de reapertura y transacciones se ejecutan en el servidor.
4. **Persistencia:** SQLite almacena usuarios, incidencias, asignaciones, soluciones, cierres y eventos. Las claves foráneas, restricciones y triggers apoyan la integridad y la conservación del historial.
5. **Pruebas:** pytest usa una base SQLite independiente para comprobar reglas, permisos, persistencia y los recorridos de integración.

## Modelo de datos

El modelo completo de entidades, relaciones, claves y restricciones se encuentra en [modelo-datos.md](modelo-datos.md) y en `database/schema.sql`. Las entidades principales son usuarios, incidencias, asignaciones, soluciones, cierres y eventos. Cada cierre y cada solución se conserva como registro histórico; el último cierre se obtiene de la tabla `cierres`.

## Flujo y permisos

El solicitante registra incidencias y valida soluciones de sus propios reportes. El coordinador asigna una incidencia registrada a un técnico activo y puede consultar el tablero global. El técnico asignado inicia la atención y registra soluciones. Los permisos se verifican en el servidor en cada operación; una acción inválida no debe dejar cambios parciales ni eventos.

Los estados son `REGISTRADA`, `ASIGNADA`, `EN_ATENCION`, `PENDIENTE_VALIDACION` y `CERRADA`. El diagrama de estados documenta el rechazo y la reapertura dentro de las 48 horas; el diagrama de secuencia muestra el rechazo de una solución. Ambos se incluyen en `docs/diagramas/`.

## Decisión tecnológica

Se eligió Flask porque permite mantener rutas y reglas de negocio en un prototipo pequeño y ejecutable con Python. SQLite guarda los datos en un archivo, simplifica la instalación desde una copia limpia y permite pruebas aisladas. PostgreSQL sería una alternativa para una instalación multiusuario de producción, pero añadiría configuración y un servicio de base de datos que no son necesarios para el alcance del examen. La aplicación se mantiene como monolito modular para reducir complejidad y separar interfaz, reglas y persistencia.