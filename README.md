# ReparaCampus

Prototipo para gestionar incidencias de infraestructura de la Universidad Simón Bolívar.
Examen SDD + IA · Ingeniería de Software I.

## Versiones

| Componente | Versión |
|---|---|
| Python | 3.12 o 3.13 (probado en 3.12.3 y 3.13.15) |
| Flask | 3.0.3 |
| Werkzeug | 3.0.4 |
| pytest | 8.3.3 |
| SQLite | incluido en Python |

## Estructura

```
specs/          SPECS S01–S05 y preguntas al cliente
docs/           diseño, diagramas, bitácora de IA y evidencias de pruebas
database/schema.sql   esquema de la base de datos
database/seed.sql     cinco cuentas ficticias
app/            aplicación Flask (dominio, reloj, base de datos, rutas)
tests/          pruebas pytest
```

## Instalación (copia limpia)

Windows (PowerShell):

```
git clone <URL-del-repositorio>
cd reparacampus
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Linux / macOS:

```
git clone <URL-del-repositorio>
cd reparacampus
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Base de datos y arranque

```
flask --app app init-db --seed
flask --app app run
```

La base queda en `instance/reparacampus.sqlite` y persiste entre reinicios.
Para empezar desde cero, borre ese archivo y vuelva a ejecutar `init-db --seed`.

## Cuentas ficticias

| Usuario | Contraseña | Rol |
|---|---|---|
| solicitante1 | Solicitante1*2026 | SOLICITANTE |
| solicitante2 | Solicitante2*2026 | SOLICITANTE |
| coordinador1 | Coordinador1*2026 | COORDINADOR |
| tecnico1 | Tecnico1*2026 | TECNICO |
| tecnico2 | Tecnico2*2026 | TECNICO |

Equivalencia con los ejemplos de las SPECS: SOL01 = solicitante1, SOL02 = solicitante2,
COORD01 = coordinador1, T01 = tecnico1, T02 = tecnico2. El técnico inactivo T03
existe solo en la base de prueba.

## Pruebas

```
python -m pytest -v
```

Cada prueba usa su propia base SQLite temporal; no toca `instance/`.
Para guardar evidencia: `python -m pytest -v > docs/evidencias/pytest-AAAA-MM-DD.txt`
y registrar el SHA con `git rev-parse HEAD`.

## Estado y limitaciones conocidas

- Implementado: autenticación con control de rol, S01 (registrar), S02 (asignar),
  S03 (atender y solucionar), S04 (confirmar, rechazar y reabrir en 48 h),
  S05 (listados con filtros, detalle con historial y tablero), pruebas de integración
  INT-01 a INT-03.
- Rutas principales: `/login`, `/incidencias/` (lista y filtros), `/incidencias/<código>`
  (detalle e historial), `/incidencias/nueva`, `/incidencias/mis-reportes`,
  `/incidencias/por-asignar`, `/incidencias/mis-asignaciones`, `/incidencias/tablero`.
- Limitación conocida: los formularios no tienen token CSRF (mitigado en parte con
  la cookie `SameSite=Lax`). No se requieren adjuntos, notificaciones ni hosting.
