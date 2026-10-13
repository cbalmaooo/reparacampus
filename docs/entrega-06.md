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

> **Corte de revisión documental:** 13 de octubre de 2026. Esta matriz se construye contrastando las SPECS, los módulos consultados y el README de la rama. No representa una ejecución reciente de pruebas. Los resultados observados deben completarse con una corrida real antes de congelar la entrega.

### 7.1 Matriz de trazabilidad requisito → SPEC → código → prueba

| Requisito / comportamiento | SPEC y criterio relacionado | Código identificado en la rama | Prueba/evidencia localizada | Estado de trazabilidad |
|---|---|---|---|---|
| Registrar incidencia con sesión de solicitante y campos permitidos | S01; AC-S01-01 a AC-S01-11 | `app/rutas_incidencias.py`: `crear()`; `app/servicios.py`: `registrar_incidencia()`; `app/dominio.py`: validadores | `tests/test_dominio.py`: `test_descripcion_limites`, `test_descripcion_recorta_espacios`, `test_opciones_y_riesgo`; `tests/test_schema.py`: `test_ubicacion_no_permitida`; `tests/test_auth.py`: `test_sin_sesion_redirige_a_login` | Parcial: cubre reglas y restricciones, falta prueba integrada de creación completa |
| Generar código, autor, fecha, estado inicial, prioridad y evento en una transacción | S01; criterios de persistencia y atomicidad | `app/servicios.py`: `registrar_incidencia()`; `app/historial.py`: `registrar_evento()`; `app/db.py`: `transaccion()` | No se localizó en la evidencia histórica una prueba del flujo completo que compruebe juntos código, estado, evento y rollback | Pendiente de prueba integrada |
| Calcular prioridad según riesgo e impacto | S02; AC-S02-01 a AC-S02-04 | `app/dominio.py`: `calcular_prioridad()`; `app/servicios.py`: llamada desde `registrar_incidencia()` | `tests/test_dominio.py`: `test_prioridad` (cuatro combinaciones parametrizadas) y `test_prioridad_impacto_invalido` | Código y pruebas unitarias identificados; falta ejecución de la versión actual |
| Asignar solo como coordinador a un técnico existente, activo, en incidencia REGISTRADA | S02; criterios de permiso, estado y técnico activo | `app/rutas_incidencias.py`: `asignar()`; `app/servicios.py`: `asignar_incidencia()`, `listar_tecnicos_activos()` | `tests/test_auth.py`: `test_rol_no_permitido_recibe_403`, `test_tecnico_inactivo_no_inicia_sesion`; `tests/test_schema.py`: `test_reasignacion_bloqueada_por_la_base` (restricción de persistencia, no sustituye el flujo) | Parcial: faltan pruebas directas de la operación de asignación y sus rechazos |
| Cambiar a ASIGNADA y registrar evento sin cambios parciales | S02; criterio de atomicidad | `app/servicios.py`: `asignar_incidencia()`; `app/db.py`: `transaccion()`; `app/historial.py` | No se ha confirmado en esta revisión una prueba ejecutada que compruebe conjuntamente estado, asignación y evento | Pendiente de evidencia de prueba |
| Iniciar atención y registrar solución de 20–800 caracteres | S03; AC-S03-* | `app/dominio.py` contiene `validar_solucion()`; no se ha identificado servicio/ruta S03 en el código consultado | `tests/test_dominio.py`: `test_solucion_limites` cubre solo la regla pura | Parcial en dominio; flujo funcional pendiente según README |
| Confirmar, rechazar o reabrir; motivo de 10–300 caracteres y plazo máximo de 48 h | S04; AC-S04-* | `app/dominio.py`: `validar_motivo()`, `dentro_de_plazo_reapertura()`; no se ha identificado servicio/ruta S04 en el código consultado | `tests/test_dominio.py` cubre límites del motivo y regla temporal; no demuestra el flujo persistente | Parcial en dominio; flujo funcional pendiente según README |
| Autenticación, hash de contraseñas y cierre de sesión | S05; AC-S05-01 y AC-S05-02 | `app/auth.py`; `app/__init__.py`; `database/seed.sql` | `tests/test_auth.py`: `test_login_correcto_y_vista_de_rol`, `test_logout_invalida_la_sesion`, `test_contrasena_incorrecta_no_crea_sesion`, `test_usuario_inexistente_mismo_mensaje`, `test_cuenta_desactivada_pierde_la_sesion`; `tests/test_seed.py`: `test_contrasena_en_hash_y_verificable`; `tests/test_schema.py`: `test_seed_cinco_cuentas_con_hash` | Casos identificados en archivos; falta ejecución de la versión actual |
| Listado por rol, detalle, filtros combinados, tablero e historial completo | S05; AC-S05-03 a AC-S05-18 | No se identificaron rutas/servicios de consulta, tablero ni detalle en los módulos consultados | No se confirmó evidencia de integración para estas consultas | Pendiente de implementación/verificación según README |
| Historial inmutable y ausencia de eventos en operaciones rechazadas | S05; AC-S05-10 a AC-S05-12 | `app/historial.py`, `database/schema.sql` | `tests/test_schema.py`: `test_historial_y_cierres_inmutables` y `test_accion_de_evento_no_permitida` prueban restricciones de base; falta verificar ausencia de evento tras rechazos de los flujos completos | Parcial: hay pruebas de restricciones SQL; falta prueba integrada de rechazo sin evento |

**Lectura de la matriz:** “código identificado” no significa que el requisito esté aprobado ni que haya pasado una prueba. Las reglas puras de S03/S04 están presentes, pero no sustituyen los flujos completos de servicio, rutas, persistencia y permisos. El README consultado declara S03–S05 e INT-01 a INT-03 pendientes; actualizar esa declaración solo después de verificar la implementación real.

### 7.2 Matriz SPEC → artefactos de implementación

| SPEC | Artefactos de implementación consultados | Pruebas localizadas | Brecha principal antes de marcar “cumplida” |
|---|---|---|---|
| S01 — Registro | `app/rutas_incidencias.py`, `app/servicios.py`, `app/dominio.py`, `app/historial.py`, `app/db.py`, `database/schema.sql` | `tests/test_dominio.py`, `tests/test_auth.py` | Ejecutar y citar pruebas de ruta/servicio, datos persistidos y rollback ante error |
| S02 — Asignación | `app/rutas_incidencias.py`, `app/servicios.py`, `app/db.py`, `app/historial.py`, `database/schema.sql` | `tests/test_dominio.py`, `tests/test_auth.py` | Probar coordinador, estado no permitido, técnico inexistente/inactivo y consistencia estado-asignación-evento |
| S03 — Atención/solución | `app/dominio.py` (validación de solución); servicio/ruta no identificados en esta revisión | `tests/test_dominio.py` (`test_solucion_limites`) | Implementar/verificar inicio de atención y persistencia de soluciones/eventos |
| S04 — Validación/reapertura | `app/dominio.py` (motivo y ventana de 48 h); servicio/ruta no identificados en esta revisión | `tests/test_dominio.py` (motivo/plazo) | Implementar/verificar confirmar, rechazar, reabrir, propiedad del solicitante, último cierre y transacciones |
| S05 — Consultas/tablero/historial | `app/auth.py`, `app/historial.py`, `database/schema.sql` | `tests/test_auth.py`; pruebas de consulta no identificadas | Implementar/verificar listado, detalle, filtros, tablero, permisos por registro e inmutabilidad |

### 7.3 Casos automatizados: entradas, esperado y observado

Los casos siguientes son una **lista mínima de validación propuesta**, no resultados afirmados. Tras ejecutar `python -m pytest -v`, reemplazar “Pendiente de ejecutar” por el resultado observado, añadir el identificador/nombre real de la prueba y guardar la salida íntegra en `docs/evidencias/`.

| ID | Entrada / condición | Resultado esperado | Resultado observado | Estado |
|---|---|---|---|---|
| UT-01 | Descripción de 20 caracteres | Aceptada tras recortar espacios | Pendiente de ejecutar | Pendiente |
| UT-02 | Descripción de 19 caracteres | Rechazada por longitud; sin persistencia | Pendiente de ejecutar | Pendiente |
| UT-03 | Riesgo=true e impacto=BAJO | Prioridad CRITICA | Pendiente de ejecutar | Pendiente |
| UT-04 | Riesgo=false e impacto=ALTO | Prioridad ALTA | Pendiente de ejecutar | Pendiente |
| UT-05 | Técnico intenta iniciar sesión con cuenta inactiva | Acceso rechazado | Pendiente de ejecutar | Pendiente |
| UT-06 | Asignación por usuario distinto de COORDINADOR | Rechazo 403; ningún cambio | Pendiente de ejecutar | Pendiente; comprobar prueba específica |
| UT-07 | Solución con 19 caracteres | Regla de dominio la rechaza | Pendiente de ejecutar | Pendiente |
| UT-08 | Motivo con 9 caracteres | Regla de dominio lo rechaza | Pendiente de ejecutar | Pendiente |
| UT-09 | Reapertura exactamente a las 48 horas | Regla temporal la acepta | Pendiente de ejecutar | Pendiente |
| UT-10 | Porcentaje de cierre con total cero | “0,0 %” | Pendiente de ejecutar | Pendiente |

### 7.4 Pruebas de integración requeridas

Las tres pruebas de integración siguientes deben recorrer rutas y base de datos real de prueba (SQLite temporal); probar funciones puras por separado no basta.

| ID | Flujo integrado | Preparación y acción | Resultado esperado | Resultado observado |
|---|---|---|---|---|
| INT-01 | S01: registro | Iniciar sesión como solicitante y enviar formulario válido; consultar incidencia y eventos en la base de prueba | Se crea una incidencia con código/autor/fecha/estado/prioridad definidos por el servidor y un evento REGISTRAR; datos y evento quedan juntos | Pendiente de ejecutar |
| INT-02 | S02: asignación | Crear incidencia REGISTRADA; iniciar sesión como coordinador y asignar un técnico activo | Estado ASIGNADA, registro de asignación y evento ASIGNAR; intento inválido no deja cambios | Pendiente de ejecutar |
| INT-03 | Transacción/seguridad | Intentar una operación no autorizada o provocar fallo controlado dentro de una operación de escritura | Respuesta de rechazo; estado, asignación, soluciones/cierres y eventos conservan su estado previo | Pendiente de ejecutar; elegir y documentar el fallo controlado sin alterar datos reales |

### 7.5 Ejecución, hallazgos y regresión

**Evidencia histórica encontrada en el repositorio:** `docs/evidencias/pytest-2026-10-13.txt` registra `31 passed in 6.54s`, con Python 3.13.15 y pytest 8.3.3 en Windows. Sin embargo, la lista de pruebas de esa salida no incluye `tests/test_auth.py`, aunque ese archivo existe en la rama consultada. El archivo tampoco indica el SHA probado. Por estas dos razones, se conserva como evidencia histórica y no se atribuye a la versión actual de esta rama.

Registrar la ejecución final con estos datos:
- **Comando:** `python -m pytest -v`
- **Fecha y entorno:** [completar con datos de la corrida real].
- **Resultado:** [número de pruebas aprobadas/fallidas/omitidas; no inferirlo del historial].
- **Evidencia versionada:** `docs/evidencias/pytest-AAAA-MM-DD.txt`.
- **Commit/SHA probado:** [SHA exacto del código ejecutado].
- **Hallazgos y correcciones:** [ID, descripción, cambio/commit y nueva prueba].
- **Regresión:** volver a ejecutar la suite completa después de cada corrección y conservar la salida final. Comparar contra la corrida anterior e indicar pruebas añadidas, corregidas o que dejaron de pasar.


### 7.6 Ejecución automática en GitHub Actions

Se añadió el flujo `.github/workflows/tests.yml` en esta rama para ejecutar `python -m pytest -v` con Python 3.12 al actualizar la rama de trabajo o abrir/actualizar un pull request hacia `main`. Enlace: [flujo de pruebas](.github/workflows/tests.yml).

**Estado del flujo:** pendiente de confirmar el resultado en la pestaña Actions o en los checks del [pull request #16](https://github.com/cbalmaooo/reparacampus/pull/16). La existencia del archivo de configuración no demuestra que la suite haya pasado; registrar el enlace de la corrida y su resultado cuando GitHub la reporte.

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
