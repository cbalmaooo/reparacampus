# ReparaCampus

Prototipo web para gestionar incidencias de infraestructura de la Universidad Simón Bolívar.  
Caso del examen de Ingeniería de Software I.

## Versiones

| Componente | Versión |
|---|---|
| Python | 3.12.3 y 3.13.15 en ejecuciones documentadas; 3.14.7 en la corrida local de 154 pruebas |
| Flask | 3.0.3 |
| Werkzeug | 3.0.4 |
| pytest | 8.3.3 |
| SQLite | incluido en Python |

## Estructura

```
specs/          SPECS S01–S05 y preguntas al cliente
docs/           diseño, diagramas, bitácora de IA y evidencias de pruebas
database/       esquema SQL y seed para cinco cuentas ficticias
app/            aplicación Flask (dominio, reloj, base de datos, rutas y servicios)
tests/          pruebas pytest
```

## Instalación desde una copia limpia

Windows (PowerShell):

```powershell
git clone https://github.com/cbalmaooo/reparacampus.git
cd reparacampus
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Linux / macOS:

```sh
git clone https://github.com/cbalmaooo/reparacampus.git
cd reparacampus
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Base de datos y arranque

```sh
flask --app app init-db --seed
flask --app app run
```

La base queda en `instance/reparacampus.sqlite` y persiste entre reinicios. Para empezar desde cero, elimina ese archivo y ejecuta de nuevo `init-db --seed`.

## Cuentas ficticias

| Usuario | Contraseña | Rol |
|---|---|---|
| solicitante1 | Solicitante1*2026 | SOLICITANTE |
| solicitante2 | Solicitante2*2026 | SOLICITANTE |
| coordinador1 | Coordinador1*2026 | COORDINADOR |
| tecnico1 | Tecnico1*2026 | TECNICO |
| tecnico2 | Tecnico2*2026 | TECNICO |

Equivalencias usadas en las SPECS: SOL01 = solicitante1, SOL02 = solicitante2, COORD01 = coordinador1, T01 = tecnico1, T02 = tecnico2. El técnico inactivo T03 solo se usa en pruebas.

## Pruebas

```sh
python -m pytest -v
```

Cada prueba usa su propia base SQLite temporal y no modifica `instance/`. La evidencia del equipo informa 154 pruebas aprobadas para el SHA `5a86ceab602ed174cc0580bb2e6b722c3a9f6db2`; consulta `docs/evidencias/resultado-local-2026-10-13.md`. Para reproducir la verificación sobre la versión final, ejecuta el comando anterior y registra fecha, entorno, resultado y SHA de esa versión.

## Funcionalidades

Implementa autenticación con control de rol, registro y prioridad, asignación a técnico activo, atención y registro de soluciones, confirmación/rechazo/reapertura dentro de 48 horas, filtros, tablero e historial. El flujo de integración se comprueba en las pruebas INT-01 a INT-03.

Rutas principales: `/login`, `/incidencias/`, `/incidencias/<código>`, `/incidencias/nueva`, `/incidencias/mis-reportes`, `/incidencias/por-asignar`, `/incidencias/mis-asignaciones` y `/incidencias/tablero`.

## Limitaciones conocidas

Los formularios no incluyen token CSRF; la cookie `SameSite=Lax` reduce parte de ese riesgo. No se incluyen adjuntos, notificaciones, exportación ni hosting de producción.
