# Entrega 06 — ReparaCampus

> Documento de trabajo que se completará progresivamente. No marcar funcionalidades, pruebas o revisiones como terminadas sin evidencia verificable. Los campos entre corchetes están pendientes de confirmar.

## Control del documento
- Versión: 0.1 — estructura inicial
- Estado: En construcción
- Repositorio: https://github.com/cbalmaooo/reparacampus
- Tag evaluado: [crear/verificar al cierre]
- SHA exacto: [registrar al congelar la versión]
- Fecha de cierre: [pendiente]

## 1. Portada

**Universidad Simón Bolívar**  
**Programa:** Ingeniería de Sistemas  
**Asignatura:** Ingeniería de Software I  
**Título:** Examen — Entrega 06: ReparaCampus  
**Equipo:** Team Equihire  
**Docente:** Adriana María Iglesias Solano  
**Fecha de entrega:** 13 de octubre de 2026

### Integrantes

| Integrante | Código estudiantil |
|---|---|
| Alejandro Borja | 202511276804 |
| Alejandro Barros | 202511275916 |
| Sebastian Oyaga | 202511270424 |
| Taliana Reyes | 2025511272254 |

> **Pendiente de confirmar:** denominación oficial completa del título del examen/caso y número o código del grupo, si el aula los exige por separado.

## 2. Índice
Generar automáticamente al maquetar el documento final. Incluir secciones, subsecciones y páginas.

## 3. Problema y alcance
### 3.1 Necesidad y contexto
[Describir el problema que resuelve el sistema y a quién afecta.]
### 3.2 Actores y permisos
[Actores, responsabilidades y permisos, contrastados con las SPECS y el código.]
### 3.3 Requisitos
[Requisitos funcionales y no funcionales, con identificadores y referencias.]
### 3.4 Preguntas, respuestas y supuestos
[Referenciar specs/preguntas-cliente.md. Separar respuestas confirmadas de supuestos.]
### 3.5 Límites del prototipo
[Qué incluye la versión evaluada y qué queda fuera.]

## 4. Cinco SPECS

Las especificaciones fuente están en la carpeta `specs/`. Los estados que se muestran aquí corresponden a los encabezados consultados el 13 de octubre de 2026; se deben volver a comprobar al congelar la versión de entrega.

### 4.1 S01 — Registrar una incidencia
- **Requisito relacionado:** RF01 (relación con RF02 y RF05).
- **Versión/estado en la SPEC:** 1.0 — Aprobada.
- **Historia de usuario:** como solicitante, registrar ubicación, descripción, impacto y riesgo para que la universidad pueda priorizar y atender el daño.
- **Alcance clave:** registro autenticado; el servidor genera código, autor, fecha UTC, estado inicial y prioridad; se registra el evento de creación.
- **Criterios verificables:** registro válido con datos generados por servidor; campos obligatorios y valores permitidos; descripción de 20–500 caracteres; ausencia de cambios parciales si falla una validación o transacción; protección frente a datos privilegiados enviados por el cliente.
- **Revisión declarada en la SPEC:** Alejandro Borja; historial de versiones 0.1 (borrador), 0.2 (correcciones) y 1.0 (aprobación), con fechas 12–13 de octubre de 2026.
- **Evidencia previa:** [SPEC S01](../specs/S01-registro.md). Vincular a la revisión/PR o commit exacto cuando se confirme.
- **Código y pruebas:** [pendiente de mapear y ejecutar contra los criterios].

### 4.2 S02 — Priorizar y asignar una incidencia
- **Requisito relacionado:** RF02.
- **Versión/estado en la SPEC:** 0.2 — En revisión.
- **Historia de usuario:** como coordinador, disponer de una prioridad calculada por el sistema y asignar la incidencia a un técnico activo.
- **Reglas clave:** riesgo para personas implica prioridad CRITICA; sin riesgo, impacto ALTO implica ALTA y BAJO implica NORMAL. Solo el coordinador asigna incidencias en estado REGISTRADA a técnicos existentes, activos y con rol TECNICO. La asignación cambia el estado a ASIGNADA y registra el evento en una transacción.
- **Criterios verificables:** comprobar las tres reglas de prioridad, asignación válida y rechazos por rol, estado o técnico inválido/inactivo, sin efectos parciales.
- **Revisión declarada en la SPEC:** Alejandro (MaggLo_1080); el historial registra una revisión/corrección de v0.1 a v0.2 el 13 de octubre de 2026.
- **Evidencia previa:** [SPEC S02](../specs/S02-asignacion.md). Falta adjuntar referencia verificable de la revisión y confirmar la aprobación final.
- **Código y pruebas:** [pendiente de mapear y ejecutar contra los criterios].

### 4.3 S03 — Atender una incidencia y registrar la solución
- **Requisito relacionado:** RF03 (relación con RF04 y RF05).
- **Versión/estado en la SPEC:** 1.0 — Aprobada.
- **Historia de usuario:** como técnico asignado, iniciar la atención y registrar la solución para que el solicitante la revise.
- **Reglas clave:** transición ASIGNADA → EN_ATENCION; solución de 20–800 caracteres desde EN_ATENCION; guardar la solución y pasar a PENDIENTE_VALIDACION. Las soluciones anteriores se conservan y cada transición exitosa deja un evento.
- **Criterios verificables:** solo el técnico asignado puede operar; rechazar estados incompatibles o textos inválidos; fallos sin cambios parciales.
- **Revisión declarada en la SPEC:** Alejandro Borja; historial 0.1, 0.2 y 1.0, con aprobación fechada 13 de octubre de 2026.
- **Evidencia previa:** [SPEC S03](../specs/S03-atencion-solucion.md). Vincular a revisión/PR o commit exacto.
- **Código y pruebas:** [pendiente de mapear y ejecutar contra los criterios].

### 4.4 S04 — Validar o reabrir una incidencia
- **Requisito relacionado:** RF04 (relación con RF03 y RF05).
- **Versión/estado en la SPEC:** 1.0 — Aprobada.
- **Historia de usuario:** como solicitante dueño de la incidencia, confirmar la solución, rechazarla con motivo o reabrir el caso dentro del plazo establecido.
- **Reglas clave:** confirmar PENDIENTE_VALIDACION → CERRADA; rechazar PENDIENTE_VALIDACION → EN_ATENCION; reabrir CERRADA → EN_ATENCION si no han pasado más de 48 horas desde el último cierre. Rechazo y reapertura exigen motivo de 10–300 caracteres. Se conservan soluciones, cierres y eventos anteriores.
- **Criterios verificables:** validar rol y propiedad; validar estado y motivo; comprobar el límite temporal de 48 horas; impedir modificaciones parciales cuando una operación es rechazada.
- **Revisión declarada en la SPEC:** Alejandro Borja; historial 0.1, 0.2 y 1.0, con aprobación fechada 13 de octubre de 2026.
- **Evidencia previa:** [SPEC S04](../specs/S04-validacion-reapertura.md). Vincular a revisión/PR o commit exacto.
- **Código y pruebas:** [pendiente de mapear y ejecutar contra los criterios].

### 4.5 S05 — Consultar incidencias, tablero e historial
- **Requisito relacionado:** RF05; transversal a S01–S04.
- **Versión/estado en la SPEC:** 1.0 — Aprobada.
- **Historia de usuario:** permitir a cada rol consultar las incidencias que le corresponden y su historial; el coordinador consulta un tablero global.
- **Reglas clave:** el solicitante ve sus propias incidencias; el técnico, las asignadas; el coordinador, todas y el tablero. Los filtros de estado y prioridad se combinan. El historial es inmutable. El tablero muestra cantidades por estado y prioridad, incidencias CRITICAS no cerradas y porcentaje de cierre con un decimal.
- **Criterios verificables:** permisos de listado/detalle/tablero; filtros válidos; respuesta sin datos para registros ajenos; historial cronológico e inmutable; cálculo del tablero, incluidos estados/categorías con cero registros.
- **Revisión declarada en la SPEC:** Alejandro Borja; historial 0.1, 0.2 y 1.0, con aprobación fechada 13 de octubre de 2026.
- **Evidencia previa:** [SPEC S05](../specs/S05-consultas-tablero-historial.md). Vincular a revisión/PR o commit exacto.
- **Código y pruebas:** [pendiente de mapear y ejecutar contra los criterios].

### 4.6 Observaciones transversales
- Las SPECS describen transacciones atómicas: un rechazo no debe dejar cambios parciales en estado, asignación, soluciones, cierres o historial.
- Los roles y la identidad deben verificarse en el servidor; ocultar botones en la interfaz no constituye control de acceso suficiente.
- No se considera cerrada la validación de una SPEC hasta enlazar sus criterios con código y pruebas ejecutadas.
- La evidencia de revisión previa debe ser verificable (PR, commit, revisión registrada o acta); el historial de versiones dentro del Markdown, por sí solo, no reemplaza automáticamente esa evidencia.
## 5. Diseño
### 5.1 Componentes y arquitectura
[Diagrama legible y explicación de responsabilidades.]
### 5.2 Modelo de datos
[Diagrama consistente con database/schema.sql; explicar entidades, relaciones, claves y restricciones. Revisar docs/modelo-datos.md.]
### 5.3 UML de estados
[Diagrama, explicación de estados, transiciones y condiciones. Revisar docs/diagrama-estados.md.]
### 5.4 UML de secuencia
[Diagrama de un flujo relevante y explicación de participantes y mensajes. Revisar docs/diagrama-secuencia-rechazo.md u otro si corresponde.]
### 5.5 Decisión tecnológica
[Justificar las tecnologías según requisitos, alcance y restricciones del equipo.]

## 6. IA e implementación
### 6.1 Herramientas y versiones
| Herramienta/modelo | Versión/identificador | Uso | Evidencia |
|---|---|---|---|
| [Completar con datos reales] | | | |
### 6.2 Cuatro intervenciones de IA
Para cada intervención registrar objetivo/contexto, prompt real, salida relevante, decisión humana (aceptada/modificada/rechazada y por qué), verificación realizada y artefactos/commits.
- Intervención 1: [documentar con evidencia real]
- Intervención 2: [documentar con evidencia real]
- Intervención 3: [documentar con evidencia real]
- Intervención 4: [documentar con evidencia real]
### 6.3 Evidencia de implementación S01–S05
[Para cada funcionalidad: archivos/rutas, comportamiento, decisión humana, pruebas ejecutadas y evidencia. No declarar cumplimiento sin validación.]

## 7. Validación
### 7.1 Matriz de trazabilidad
| Requisito/criterio | SPEC | Archivo/componente | Prueba | Evidencia | Estado |
|---|---|---|---|---|---|
| [Completar desde los requisitos reales] | | | | | Pendiente |
### 7.2 Matriz SPEC/código
| SPEC | Criterio de aceptación | Código relacionado | Prueba | Resultado verificado |
|---|---|---|---|---|
| S01 | [Completar] | | | Pendiente |
| S02 | [Completar] | | | Pendiente |
| S03 | [Completar] | | | Pendiente |
| S04 | [Completar] | | | Pendiente |
| S05 | [Completar] | | | Pendiente |
### 7.3 Diez pruebas automatizadas
Registrar diez casos reales y reproducibles, con datos, esperado y observado.
| ID | Escenario/datos | Resultado esperado | Resultado observado | Evidencia |
|---|---|---|---|---|
| T01–T10 | [Completar una fila por caso] | | | |
### 7.4 Tres pruebas de integración
| ID | Componentes | Preparación/datos | Esperado | Observado | Evidencia |
|---|---|---|---|---|---|
| I01–I03 | [Completar una fila por prueba] | | | | |
### 7.5 Hallazgos, correcciones y regresión
[Defectos, impacto, corrección, commit y pruebas de regresión ejecutadas.]
### 7.6 Resumen de ejecución
- Comando: [registrar]
- Entorno/versiones: [registrar]
- Fecha: [registrar]
- Ejecutadas/aprobadas/fallidas/omitidas: [solo tras ejecutar]
- Archivo de salida: [ruta bajo docs/evidencias/]

## 8. Riesgos
Documentar cuatro riesgos concretos, causas, impactos, controles verificables, responsables y evidencias.
| ID | Riesgo/causa | Impacto | Control | Responsable | Evidencia | Estado |
|---|---|---|---|---|---|---|
| R01 | [Completar] | | | | | Pendiente |
| R02 | [Completar] | | | | | Pendiente |
| R03 | [Completar] | | | | | Pendiente |
| R04 | [Completar] | | | | | Pendiente |

## 9. Entrega reproducible
### 9.1 Repositorio y versión
- URL: https://github.com/cbalmaooo/reparacampus
- Tag requerido: release-examen [crear y verificar al cierre]
- SHA exacto: [registrar después de congelar la versión]
- Fecha de congelación: [pendiente]
### 9.2 Instalación y requisitos
[Versiones requeridas, entorno virtual y dependencias. Mantener el procedimiento completo en README.md.]
### 9.3 Configuración y arranque
[Variables necesarias y comando confirmado; nunca incluir secretos.]
### 9.4 Base de datos y seed
[Pasos exactos para inicializar y cargar datos ficticios; comprobar reproducibilidad.]
### 9.5 Cuentas ficticias
| Rol | Usuario ficticio | Credencial de demostración | Método de generación/restablecimiento |
|---|---|---|---|
| [Completar] | | | |
No incluir cuentas reales, contraseñas reales, tokens ni claves.
### 9.6 Comandos de pruebas
- Suite automatizada: [comando confirmado]
- Integración: [comando confirmado]
- Resultado esperado: [basado en ejecución real]
### 9.7 Limitaciones conocidas
[Limitaciones reproducibles de la versión exacta entregada.]

## 10. Contribuciones y cierre
### 10.1 Contribuciones
| Integrante y código | Tareas | Artefactos/commits | Revisión realizada | Resultado/evidencia |
|---|---|---|---|---|
| [Integrante 1] | | | | |
| [Integrante 2] | | | | |
[Agregar filas según el equipo real.]
### 10.2 Conclusión
[Cumplimiento real, resultados de pruebas, limitaciones y pendientes.]
### 10.3 Aceptación del equipo
[Registrar la aceptación acordada por los integrantes según las instrucciones del curso.]

## 11. Referencias y anexos
- Repositorio: https://github.com/cbalmaooo/reparacampus
- Especificaciones: carpeta specs/
- Documentación técnica y fuentes consultadas: [título, autor/entidad, versión/fecha y enlace]
- Anexos: solo los pertinentes, mencionados en el documento.

---

## Lista de comprobación antes de exportar
- [ ] Portada con todos los datos del equipo.
- [ ] Índice automático, páginas y títulos numerados.
- [ ] Cinco SPECS completas y evidencia de revisión previa.
- [ ] Diagramas legibles y coherentes con código y SQL.
- [ ] Cuatro intervenciones reales de IA con decisiones y verificaciones humanas.
- [ ] Evidencia de implementación de S01–S05.
- [ ] Diez pruebas automatizadas y tres de integración ejecutadas; esperado y observado registrados.
- [ ] Hallazgos y regresión documentados.
- [ ] Cuatro riesgos con responsables, controles y evidencias.
- [ ] README con instalación, arranque, seed, cuentas ficticias y pruebas.
- [ ] Tag release-examen y SHA verificados.
- [ ] Contribuciones basadas en trabajo y commits reales.
- [ ] PDF A4, márgenes de 2,5 cm, fuente 11–12 pt e interlineado 1,15.
- [ ] Texto seleccionable, enlaces activos y figuras/tablas numeradas.
- [ ] PDF revisado de principio a fin, sin secretos ni datos reales sensibles.
