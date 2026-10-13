# S05 — Consultar incidencias, tablero e historial

**Requisito relacionado:** RF05 (transversal: autenticación y registro de eventos de RF01–RF04)
**Versión:** 1.0
**Estado:** Aprobada
**Autor:** cbalmaooo (v0.1) · Alejandro Borja (cambios v0.2)
**Revisor:** Alejandro Borja
**Fecha:** 2026-10-13

### Historial de versiones
| Versión | Fecha | Autor | Cambio |
|---|---|---|---|
| 0.1 | 2026-10-12 | cbalmaooo | Borrador inicial |
| 0.2 | 2026-10-13 | Alejandro Borja | Correcciones de la revisión v0.1 |
| 1.0 | 2026-10-13 | Alejandro Borja | Aprobación |

## Historia de usuario

Como usuario del sistema, quiero iniciar sesión y consultar las incidencias que me corresponden, con su historial completo. Como coordinador, también quiero un tablero con el estado general, para organizar el mantenimiento y detectar casos críticos pendientes.

## Alcance y exclusiones

**Incluye:**
- Inicio y cierre de sesión con las cinco cuentas ficticias (transversal a S01–S05).
- Listado de incidencias según el rol, con filtros por estado y prioridad.
- Detalle e historial de una incidencia, según permisos.
- Tablero del coordinador: cantidades por estado y prioridad, CRITICA no cerradas y porcentaje de cierre.
- Inmutabilidad del historial.

**Excluye:**
- Registro de usuarios nuevos, recuperación de contraseña y edición de perfiles.
- Exportación de reportes.
- Búsqueda por texto libre.

## Entradas

| Operación | Campo | Tipo | Obligatorio | Valores permitidos |
|---|---|---|---|---|
| Iniciar sesión | usuario | texto | Sí | Cuenta existente |
| Iniciar sesión | contraseña | texto | Sí | — |
| Listar | estado | texto | No | REGISTRADA, ASIGNADA, EN_ATENCION, PENDIENTE_VALIDACION, CERRADA |
| Listar | prioridad | texto | No | CRITICA, ALTA, NORMAL |
| Detalle e historial | incidencia_id | entero o código | Sí | Debe existir y estar permitida |

Identidad y rol se obtienen de la sesión en el servidor.

## Precondiciones y permisos

**Autenticación:**
- Cuentas del seed: SOL01 y SOL02 (solicitantes), COORD01 (coordinador), T01 y T02 (técnicos activos).
- Contraseñas guardadas con un hash apropiado (por ejemplo, `generate_password_hash` de Werkzeug); nunca en texto plano.
- No existe un selector de rol: el rol sale de la cuenta autenticada.

**Visibilidad:**
| Rol | Lista | Detalle e historial | Tablero |
|---|---|---|---|
| Solicitante | Solo las propias | Solo las propias | No |
| Técnico | Solo las asignadas a él (en cualquier estado) | Solo las asignadas a él | No |
| Coordinador | Todas | Todas | Sí |

El servidor comprueba la pertenencia en cada consulta; ocultar enlaces no basta.

## Reglas y proceso

**Listado y filtros:**
1. Aplicar primero la restricción por rol y luego los filtros, combinables (estado y prioridad a la vez).
2. Un valor de filtro no permitido se rechaza con el mensaje "Filtro no válido" y nunca amplía la visibilidad.
3. Si el filtro no tiene coincidencias, se muestra una lista vacía con un mensaje informativo.

**Historial:**
1. Cada creación y transición exitosa de S01–S04 registra autor, fecha UTC, estado anterior, estado nuevo y acción, en la misma transacción que el cambio.
2. Una operación rechazada no registra eventos.
3. El historial incluye soluciones, motivos de rechazo y reapertura, y cierres, en orden cronológico ascendente.
4. No existen rutas para editar ni borrar eventos, soluciones, cierres ni motivos. En la base de datos, triggers de SQLite impiden UPDATE y DELETE sobre esas tablas.

**Tablero:**
1. Cantidades por cada uno de los cinco estados y de las tres prioridades, incluidos los ceros.
2. Lista de incidencias con prioridad CRITICA y estado distinto de CERRADA (código, ubicación, estado y técnico).
3. Porcentaje de cierre = incidencias con estado actual CERRADA ÷ total × 100, con un decimal, redondeo half-up y coma decimal. Con cero incidencias: "0,0 %".
4. Una incidencia reabierta no cuenta como CERRADA; su cierre anterior permanece en el historial.

## Salidas y cambios persistidos

- Las consultas no modifican datos.
- Inicio de sesión exitoso: sesión con identidad y rol, y redirección a la vista de su rol. Cierre de sesión: la sesión se invalida y las rutas protegidas vuelven a pedir inicio de sesión.
- Todo texto de usuario se muestra escapado; no se ejecuta como HTML ni como script.

## Errores y efectos que deben evitarse

| Situación | Respuesta esperada | Efecto prohibido |
|---|---|---|
| Credenciales incorrectas | "Usuario o contraseña incorrectos", sin indicar cuál falla | Crear sesión |
| Sin sesión en una ruta protegida | Redirigir a inicio de sesión | Mostrar datos |
| Solicitante consulta una incidencia ajena | "Incidencia no encontrada" | Revelar datos o su existencia |
| Técnico consulta una incidencia no asignada | "Incidencia no encontrada" | Revelar datos |
| Rol distinto de coordinador accede al tablero | Rechazo por falta de permiso | Mostrar cifras globales |
| Filtro con valor no permitido | "Filtro no válido" | Ampliar visibilidad |
| Intento de editar o borrar el historial | Rechazo (ruta inexistente o método no permitido) | Modificar eventos |
| Operación fallida en S01–S04 | Sin evento | Historial engañoso |

## Criterios de aceptación

### AC-S05-01 — Inicio y cierre de sesión
**Dado** que existen las cinco cuentas del seed con contraseñas en hash
**Cuando** SOL01 inicia sesión con su contraseña correcta y luego cierra sesión
**Entonces** accede a su vista de solicitante; tras cerrar sesión, las rutas protegidas lo redirigen al inicio de sesión. Con una contraseña incorrecta no se crea sesión y se muestra "Usuario o contraseña incorrectos".

### AC-S05-02 — Contraseñas en hash
**Dado** que se cargó el seed
**Cuando** se consulta la tabla de usuarios en la base de datos
**Entonces** ninguna contraseña está en texto plano y cada una verifica correctamente con la función de hash.

### AC-S05-03 — Solicitante consulta las propias
**Dado** que SOL01 tiene INC-0001 e INC-0002, y SOL02 tiene INC-0003
**Cuando** SOL01 consulta la lista
**Entonces** ve solo INC-0001 e INC-0002.

### AC-S05-04 — Solicitante intenta leer una incidencia ajena
**Dado** que INC-0003 pertenece a SOL02
**Cuando** SOL01 solicita el detalle o el historial de INC-0003
**Entonces** el sistema responde "Incidencia no encontrada" y no muestra ningún dato de INC-0003.

### AC-S05-05 — Técnico consulta sus asignaciones
**Dado** que INC-0001 está asignada a T01, INC-0002 a T02 e INC-0003 sigue REGISTRADA
**Cuando** T01 consulta la lista y luego el detalle de INC-0002
**Entonces** la lista muestra solo INC-0001 y el detalle de INC-0002 responde "Incidencia no encontrada".

### AC-S05-06 — Coordinador consulta todas
**Dado** que existen INC-0001, INC-0002 e INC-0003 de distintos solicitantes
**Cuando** COORD01 consulta la lista
**Entonces** ve las tres incidencias.

### AC-S05-07 — Filtros individuales y combinados
**Dado** que existen INC-0001 (REGISTRADA, CRITICA), INC-0002 (ASIGNADA, CRITICA) e INC-0003 (REGISTRADA, NORMAL)
**Cuando** COORD01 filtra por estado REGISTRADA; luego por prioridad CRITICA; luego por REGISTRADA y CRITICA a la vez
**Entonces** obtiene {INC-0001, INC-0003}, después {INC-0001, INC-0002} y por último {INC-0001}.

### AC-S05-08 — Filtros respetan permisos
**Dado** que INC-0001 (CRITICA) es de SOL01 e INC-0004 (CRITICA) es de SOL02
**Cuando** SOL01 filtra por prioridad CRITICA
**Entonces** ve solo INC-0001.

### AC-S05-09 — Filtro inválido
**Dado** que SOL01 inició sesión
**Cuando** filtra por estado "BORRADA" o por prioridad "URGENTE"
**Entonces** el sistema responde "Filtro no válido" y no muestra incidencias fuera de sus permisos.

### AC-S05-10 — Historial completo y ordenado
**Dado** que INC-0001 se registró, se asignó, se inició, recibió la solución S1, fue rechazada con motivo, recibió la solución S2, se confirmó y se reabrió con motivo
**Cuando** SOL01 consulta su historial
**Entonces** ve los eventos REGISTRAR, ASIGNAR, INICIAR_ATENCION, REGISTRAR_SOLUCION, RECHAZAR, REGISTRAR_SOLUCION, CONFIRMAR y REABRIR en orden cronológico, cada uno con autor, fecha UTC, estado anterior y nuevo, junto con S1, S2, ambos motivos y el cierre.

### AC-S05-11 — Operación fallida sin evento
**Dado** que INC-0001 está ASIGNADA a T01 y tiene 2 eventos
**Cuando** T02 intenta iniciar su atención y el sistema lo rechaza
**Entonces** el historial de INC-0001 sigue con exactamente 2 eventos.

### AC-S05-12 — Historial inmutable
**Dado** que INC-0001 tiene eventos en su historial
**Cuando** cualquier usuario envía una petición para editar o borrar un evento, o se ejecuta UPDATE o DELETE sobre la tabla de eventos
**Entonces** la operación se rechaza y los eventos permanecen idénticos.

### AC-S05-13 — Tablero restringido
**Dado** que SOL01 o T01 inició sesión
**Cuando** accede al tablero
**Entonces** el sistema rechaza el acceso por falta de permiso y no muestra cifras.

### AC-S05-14 — Tablero vacío
**Dado** que no hay incidencias
**Cuando** COORD01 consulta el tablero
**Entonces** todas las cantidades son 0, la lista de CRITICA no cerradas está vacía y el porcentaje es "0,0 %".

### AC-S05-15 — Tablero con datos
**Dado** que hay cuatro incidencias: INC-0001 CERRADA y CRITICA, INC-0002 EN_ATENCION y CRITICA, INC-0003 REGISTRADA y ALTA, e INC-0004 ASIGNADA y NORMAL
**Cuando** COORD01 consulta el tablero
**Entonces** ve CERRADA 1, EN_ATENCION 1, REGISTRADA 1, ASIGNADA 1, PENDIENTE_VALIDACION 0; CRITICA 2, ALTA 1, NORMAL 1; solo INC-0002 entre las CRITICA no cerradas; y un porcentaje de "25,0 %".

### AC-S05-16 — Reapertura reduce el porcentaje
**Dado** el escenario de AC-S05-15
**Cuando** SOL01 reabre INC-0001 dentro del plazo y COORD01 consulta el tablero
**Entonces** el porcentaje es "0,0 %", INC-0001 aparece entre las CRITICA no cerradas y su historial conserva el cierre anterior.

### AC-S05-17 — Redondeo
**Dado** que hay 3 incidencias y 1 está CERRADA
**Cuando** COORD01 consulta el tablero
**Entonces** el porcentaje es "33,3 %"; con 16 incidencias y 1 CERRADA, es "6,3 %" (half-up).

### AC-S05-18 — Texto parecido a HTML en consultas
**Dado** que INC-0001 tiene la descripción "<b>Fuga</b> en baño" y un motivo con `<script>`
**Cuando** se muestran en la lista, el detalle o el historial
**Entonces** aparecen literalmente, escapados, sin interpretarse ni ejecutarse.

## Diseño y tareas vinculadas a cada AC

**Diseño:**
- Autenticación con sesión de Flask, `generate_password_hash` y `check_password_hash` de Werkzeug, y un decorador `login_requerido(roles)`.
- Repositorio `listar_incidencias(usuario_sesion, estado=None, prioridad=None)` que aplica la visibilidad en la consulta SQL, no en la plantilla.
- Servicio `obtener_detalle(incidencia_id, usuario_sesion)` que devuelve "no encontrada" si la incidencia no existe o no está permitida.
- Servicio `calcular_tablero()` con `Decimal` y `ROUND_HALF_UP`; formato con coma decimal.
- Triggers SQLite `BEFORE UPDATE` y `BEFORE DELETE` en eventos, soluciones y cierres.
- Plantillas con autoescape activo.

| Tarea | Descripción | AC cubiertos |
|---|---|---|
| T-S05-01 | Inicio y cierre de sesión con hash y seed | 01, 02 |
| T-S05-02 | Listado con visibilidad por rol en SQL | 03, 05, 06 |
| T-S05-03 | Detalle e historial con control de pertenencia | 04, 05 |
| T-S05-04 | Filtros combinables y validación de valores | 07, 08, 09 |
| T-S05-05 | Vista de historial ordenado con soluciones, motivos y cierres | 10 |
| T-S05-06 | Triggers de inmutabilidad y ausencia de rutas de edición | 11, 12 |
| T-S05-07 | Tablero restringido con cantidades, críticas y porcentaje | 13, 14, 15, 16, 17 |
| T-S05-08 | Escapado en todas las vistas | 18 |
| T-S05-09 | Pruebas unitarias e integración | 01–18 |

## Pruebas y resultados esperados

Los resultados esperados se escriben a mano. Se usa una base de prueba independiente, con datos creados en cada prueba.

| Prueba | AC | Entrada | Resultado esperado |
|---|---|---|---|
| P-S05-01 | 01 | Login correcto, logout, ruta protegida | Acceso; luego redirección a login |
| P-S05-02 | 01 | Contraseña incorrecta | Sin sesión; mensaje genérico |
| P-S05-03 | 02 | Leer la columna de contraseña | No coincide con el texto plano; verifica con hash |
| P-S05-04 | 03 | SOL01 lista | {INC-0001, INC-0002} |
| P-S05-05 | 04 | SOL01 pide INC-0003 | "No encontrada"; sin datos |
| P-S05-06 | 05 | T01 lista y pide INC-0002 | {INC-0001}; "No encontrada" |
| P-S05-07 | 07 | Filtros REGISTRADA / CRITICA / ambos | {1,3} / {1,2} / {1} |
| P-S05-08 | 09 | Estado "BORRADA" | "Filtro no válido" |
| P-S05-09 | 11 | T02 inicia INC-0001 de T01 | Sigue con 2 eventos |
| P-S05-10 | 12 | UPDATE directo sobre eventos | Error del trigger; datos idénticos |
| P-S05-11 | 13 | SOL01 abre el tablero | Rechazo |
| P-S05-12 | 14 | Tablero vacío | "0,0 %" |
| P-S05-13 | 15 | Cuatro incidencias, una cerrada | "25,0 %"; cantidades indicadas |
| P-S05-14 | 16 | Reabrir INC-0001 | "0,0 %"; cierre anterior conservado |
| P-S05-15 | 17 | 1 de 3 y 1 de 16 | "33,3 %" y "6,3 %" |
| P-S05-16 | 18 | Descripción con `<b>` | La respuesta contiene `&lt;b&gt;` |
| P-S05-17 | 01–18 | Reinicio de la app con SQLite en archivo | Datos e historial persisten; filtros iguales |
| INT-01 | 10 | Registrar → asignar → iniciar → solución → confirmar (SQLite real) | CERRADA; 5 eventos en orden; tablero con 100,0 % |

## Decisión de revisión

**Revisión de v0.1**
- Revisor: Alejandro Borja
- Fecha: 2026-10-13
- Decisión: Requiere cambios
- Observaciones:
  1. Ninguna SPEC cubría el inicio y cierre de sesión, el hash de contraseñas ni la prohibición del selector de rol, que el examen exige.
  2. No se impedía que un solicitante o un técnico leyeran el detalle o el historial de incidencias ajenas.
  3. Faltaba el escenario de reapertura que reduce el porcentaje y conserva el cierre anterior.
  4. No se definía la regla de redondeo ni el formato con coma decimal.
  5. Faltaban filtros combinados e inválidos, y que los filtros no amplíen la visibilidad.
  6. No se especificaba cómo se garantiza la inmutabilidad del historial ni que una operación fallida no registre eventos.
  7. Faltaban el orden del historial, el escapado de textos y la persistencia tras reinicio.
  8. Plantilla incompleta y criterios sin datos concretos.

**Revisión de v0.2**
- Revisor: Alejandro Borja
- Fecha: 2026-10-13
- Decisión: Aprobada → v1.0
- Observaciones: se verificó, contra RF05, los requisitos de autenticación y persistencia del prototipo y las reglas que no pueden cambiarse, que los ocho hallazgos quedaron resueltos (AC-S05-01 a AC-S05-18, INT-01 y plantilla completa).
- Condiciones: los nombres de acciones de eventos deben coincidir con S01–S04 (REGISTRAR, ASIGNAR, INICIAR_ATENCION, REGISTRAR_SOLUCION, RECHAZAR, CONFIRMAR, REABRIR); los triggers de inmutabilidad deben incluirse en `schema.sql`.
- Nota de trazabilidad: los cambios de v0.2 fueron redactados por el revisor con apoyo de IA (ver bitácora); se solicita la conformidad del autor original.

**Conformidad del autor original**
- Autor: cbalmaooo
- Fecha: 13/10/2026
- Decisión: Cambios Aceptados
