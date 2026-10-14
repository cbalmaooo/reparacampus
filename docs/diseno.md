# Diseño de ReparaCampus

**Estado:** Diseño de referencia alineado con la estructura de la aplicación actual. Confirmar los cambios contra las SPECS y `database/schema.sql` en cada modificación.

## Partes del sistema

1. **Interfaz:** plantillas HTML en `app/templates/` para inicio de sesión, registro, listados, detalle, historial y tablero.
2. **Rutas HTTP:** `app/auth.py` y `app/rutas_incidencias.py` reciben las solicitudes, comprueban acceso y traducen errores a respuestas HTTP.
3. **Servicios de negocio:** `app/servicios.py` ejecuta operaciones S01–S05 y coordina validaciones y transacciones.
4. **Dominio:** `app/dominio.py` contiene reglas de prioridad, longitudes, opciones permitidas y plazo de reapertura.
5. **Persistencia:** `app/db.py` gestiona SQLite; `database/schema.sql` define tablas, restricciones y triggers; `database/seed.sql` carga las cuentas ficticias.
6. **Historial y tiempo:** `app/historial.py` registra eventos y `app/reloj.py` normaliza fechas y permite usar un reloj fijo en pruebas.

Las rutas deben delegar las reglas de negocio a los servicios. Las escrituras de estado y los eventos asociados deben persistirse en la misma transacción. Los permisos se validan en el servidor, no solo en la interfaz.

## Datos que se guardan

- **Usuarios:** nombre de acceso, hash de contraseña, rol y estado activo.
- **Incidencias:** código, solicitante, ubicación, categoría, descripción, impacto, riesgo, prioridad, estado y fecha de creación.
- **Asignaciones:** incidencia, técnico, coordinador y fecha de asignación.
- **Soluciones:** una fila por propuesta de solución, sin sobrescribir las anteriores.
- **Cierres:** una fila por confirmación de cierre, para conservar todos los cierres y calcular el último.
- **Eventos:** autor, fecha, acción, estado anterior y nuevo, motivo y referencia a la solución cuando corresponda.

## Decisiones tecnológicas

Flask permite mantener el prototipo web en Python con una separación sencilla entre rutas y servicios. SQLite facilita la instalación y el uso de bases temporales en pruebas. Esta decisión responde al alcance académico y no implica que el prototipo esté listo para producción o alta concurrencia.

## Limitaciones conocidas y trabajo pendiente

- El README de la versión revisada registra que los formularios no tenían token CSRF. Debe corregirse y probarse antes de considerar el prototipo endurecido para despliegue.
- La configuración usa un secreto local por defecto si no se define `SECRET_KEY`; debe exigirse una clave de entorno fuera del modo de desarrollo.
- Antes de congelar la entrega, ejecutar la suite sobre el commit final, confirmar el resultado de CI y vincular el SHA y tag exactos.
