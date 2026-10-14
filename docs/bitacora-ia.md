# Bitácora de IA

Herramienta y modelo declarados en el registro previo: Claude (Anthropic), interfaz web claude.ai; modelo indicado: “Claude Opus 5.5”. **Pendiente de verificación por el equipo:** confirmar que el nombre del modelo y las fechas coinciden con el historial real de uso. Esta bitácora resume intervenciones relevantes; no sustituye las conversaciones ni la revisión humana.

> Regla de integridad: no completar decisiones humanas, prompts literales, resultados de pruebas ni autorías por inferencia. Los campos marcados como pendientes deben ser confirmados por quien realizó la intervención.

---

## Intervención 1 · Especificación y revisión

- **Fecha / autor registrados:** 2026-10-13 · Alejandro Borja.
- **Historia y SPEC / versión:** S04 v0.1 → v1.0.
- **Objetivo y contexto registrados:** revisar S04 contra el enunciado (RF04, RF05 y reglas que no pueden cambiarse) antes de aprobarla.
- **Prompt o instrucción registrada:** se entregó el texto de S04 v0.1 y se pidió revisarla y corregirla con la plantilla del examen. El texto literal del prompt no está conservado aquí.
- **Respuesta relevante registrada:** se identificaron la falta de registro de cierres y de definición del “último cierre”, la precisión del límite de 48 horas, el reloj inyectable, los eventos, el recorte de espacios y el ciclo de doble cierre.
- **Decisión humana y justificación:** **pendiente de completar por Alejandro Borja** con lo que realmente aceptó, modificó o descartó.
- **Error o limitación:** no hay evidencia suficiente en esta bitácora para declarar “ninguno”.
- **Corrección y verificación:** asociar cada hallazgo con el criterio de aceptación y la prueba correspondiente; el responsable debe confirmar qué comprobó.
- **Archivo / commit / prueba:** `specs/S04-validacion-reapertura.md`; SHA y pruebas de esa intervención pendientes de verificar.

---

## Intervención 2 · Código

- **Fecha / autor registrados:** 2026-10-13 · Alejandro Borja.
- **Historia y SPEC / versión:** S01–S05 v1.0 (reglas compartidas).
- **Objetivo y contexto registrados:** implementar reglas de dominio, reloj inyectable y conexión transaccional, inicialmente sin rutas ni interfaz.
- **Prompt o instrucción registrada:** “Empecemos con el código”, con las SPECS aprobadas como contexto. Confirmar el texto exacto en el historial original si se exige literalidad.
- **Respuesta relevante registrada:** `app/dominio.py`, `app/reloj.py`, `app/db.py`, `app/__init__.py` y `tests/test_dominio.py`.
- **Decisión humana y justificación:** **pendiente de completar por el autor**.
- **Error o limitación:** **pendiente de completar por el autor**; no inferirlo.
- **Corrección y verificación:** registrar el comando ejecutado, entorno y salida real de las pruebas. El resultado histórico de CI se documenta en `docs/entrega-06.md`, sección 7, pero no prueba por sí solo qué verificó la persona durante esta intervención.
- **Archivo / commit / prueba:** SHA original pendiente de verificar; `tests/test_dominio.py`.

---

## Intervención 3 · Diseño de datos y pruebas

- **Fecha / autor registrados:** 2026-10-13 · Alejandro Borja.
- **Historia y SPEC / versión:** S04 v1.0, S05 v1.0.
- **Objetivo y contexto registrados:** revisar `schema.sql` y `seed.sql` contra las SPECS aprobadas.
- **Prompt o instrucción registrada:** se entregaron `schema.sql` y `seed.sql` para revisión; el texto literal no se conserva en esta bitácora.
- **Respuesta relevante registrada:** el registro previo indica que se detectó que una sola columna `ultimo_cierre_en` no permitía conservar todos los cierres y que los hashes originales del seed no se podían asociar a contraseñas conocidas. Se propuso la tabla `cierres`, restricciones, triggers y credenciales de demostración documentadas.
- **Decisión humana y justificación:** **pendiente de completar por el autor**.
- **Error o limitación:** el registro previo identifica los hashes originales como no verificables. Confirmar el commit que corrigió el problema.
- **Corrección y verificación:** asociar `tests/test_schema.py` y `tests/test_seed.py` con su ejecución real y guardar el resultado.
- **Archivo / commit / prueba:** el registro previo menciona `database/schema.sql` y `database/seed.sql`; confirmar SHA exacto.

---

## Intervención 4 · Revisión documental del repositorio

- **Fecha:** 2026-10-13.
- **Herramienta/modelo de esta intervención:** ChatGPT, GPT-6.
- **Objetivo:** revisar consistencia entre la documentación de entrega, el estado de las SPECS, el diagrama del modelo de datos y los documentos de diseño.
- **Instrucción resumida:** el usuario pidió ejecutar en GitHub las correcciones y pendientes previamente identificados para el repositorio ReparaCampus.
- **Hallazgos comprobados:** `docs/entrega-06.md` decía que S02 estaba en versión 0.2 y en revisión, mientras que `specs/S02-asignacion.md` declara versión 1.0 aprobada; `docs/modelo-datos.md` describía una columna `ultimo_cierre_en` y omitía la entidad `CIERRE`, mientras que el esquema y el informe describen registros de cierre separados.
- **Cambios propuestos en la rama:** `docs/modelo-datos.md`, `docs/diseno.md`, `docs/diagrama-estados.md`, `docs/diagrama-secuencia-rechazo.md` y correcciones puntuales a `docs/entrega-06.md`. Rama: `fix/pendientes-entrega-06`.
- **Decisión humana:** pendiente; el equipo debe revisar los cambios y aceptar, modificar o rechazar cada uno antes de integrar.
- **Limitación:** no se ejecutó la aplicación ni la suite de pruebas durante esta intervención. No afirmar que el código está corregido o que CI pasó por estos cambios documentales.
- **Verificación siguiente:** revisar el diff, ejecutar `python -m pytest -v` en una copia limpia y comprobar el resultado de GitHub Actions en la rama/PR.
- **Evidencia de commits:** `docs/modelo-datos.md` — `37a3294a3d281f983b3ce7bfcbc5e720de1a0fdd`; `docs/diseno.md` — `4676c5d89e4b41d723d2dd99da08ee829c7ab8ce`; `docs/diagrama-estados.md` — `d8e1d47b8031e6650779ec65e47f3bf25a0f140e`; `docs/diagrama-secuencia-rechazo.md` — `6d36253e47d5d1ed16ccde46630aee916e623185`; `docs/entrega-06.md` — `a7aaea932d44d978cef1150bccafb8a9cc443d38`.

---

## Pendientes humanos para cerrar la bitácora

- Confirmar el modelo exacto de la herramienta usada en las intervenciones 1–3 y sus fechas.
- Completar las decisiones humanas, errores/limitaciones y verificaciones a partir de la experiencia real de cada autor.
- Recuperar los prompts originales si la rúbrica requiere texto literal; no reconstruirlos como si fueran transcripciones.
- Asociar las intervenciones originales con los SHA reales y los resultados de pruebas correspondientes.
- Documentar la revisión del equipo sobre los cambios de esta rama antes de integrarlos.
