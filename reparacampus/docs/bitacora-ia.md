# Bitácora de IA

Herramienta: Claude (Anthropic), interfaz web claude.ai. Modelo: Claude Opus 5.5.
Se registran intervenciones relevantes; no se copian conversaciones completas.

---

## Intervención 1 · Especificación y revisión

- **Fecha / autor:** 2026-10-13 · Alejandro Borja
- **Historia y SPEC / versión:** S04 v0.1 → v1.0
- **Objetivo y contexto:** revisar S04 contra el enunciado (RF04, RF05, reglas que no pueden cambiarse) antes de aprobarla.
- **Prompt o instrucción:** se entregó el texto de S04 v0.1 y se pidió revisarla y corregirla con la plantilla del examen.
- **Respuesta relevante:** señaló que no existía un registro de cierres ni definición de "último cierre", que el límite de 48 h no precisaba el instante posterior ni el reloj inyectable, y que faltaban eventos completos, recorte de espacios y el ciclo de doble cierre.
- **Decisión humana y justificación:** [COMPLETAR: qué aceptaste, qué cambiaste o descartaste y por qué]
- **Error o limitación, si existe:** [COMPLETAR o "Ninguno detectado"]
- **Corrección y verificación:** [COMPLETAR: cómo comprobaste cada hallazgo contra el enunciado]
- **Archivo / commit / prueba:** specs/S04-validacion-reapertura.md · [SHA]

---

## Intervención 2 · Código

- **Fecha / autor:** 2026-10-13 · Alejandro Borja
- **Historia y SPEC / versión:** S01–S05 v1.0 (reglas compartidas)
- **Objetivo y contexto:** implementar solo las reglas de dominio puras, el reloj inyectable y la conexión transaccional, sin rutas ni interfaz.
- **Prompt o instrucción:** "Empecemos con el código", con las SPECS aprobadas como contexto.
- **Respuesta relevante:** app/dominio.py, app/reloj.py, app/db.py, app/__init__.py y tests/test_dominio.py (19 pruebas).
- **Decisión humana y justificación:** [COMPLETAR]
- **Error o limitación, si existe:** [COMPLETAR]
- **Corrección y verificación:** [COMPLETAR: resultado de pytest en tu equipo]
- **Archivo / commit / prueba:** [SHA] · tests/test_dominio.py

---

## Intervención 3 · Diseño de datos y pruebas

- **Fecha / autor:** 2026-10-13 · Alejandro Borja
- **Historia y SPEC / versión:** S04 v1.0, S05 v1.0
- **Objetivo y contexto:** revisar schema.sql y seed.sql contra las SPECS aprobadas.
- **Prompt o instrucción:** se entregaron schema.sql y seed.sql para revisión.
- **Respuesta relevante:** detectó que la columna ultimo_cierre_en impedía conservar todos los cierres (RF04) y que los hashes del seed no correspondían a contraseñas conocidas. Propuso la tabla cierres, restricciones adicionales y triggers, y regeneró el seed con contraseñas documentadas.
- **Decisión humana y justificación:** [COMPLETAR]
- **Error o limitación, si existe:** hashes originales no verificables (hallazgo real de la revisión).
- **Corrección y verificación:** [COMPLETAR: tests/test_schema.py y tests/test_seed.py en tu equipo]
- **Archivo / commit / prueba:** db/schema.sql, db/seed.sql · [SHA]

---

## Intervención 4 · Revisión o pruebas

[Pendiente: registrar en una etapa posterior, por ejemplo la revisión de un PR o las pruebas de integración.]
