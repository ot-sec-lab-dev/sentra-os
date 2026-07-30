# Sentra OS — OT Assessment Engine

Motor de evaluación de riesgo OT/IoMT. El flujo de negocio:

```
Cliente → Assessment → Risk Engine → AI Report Builder → Executive Dashboard → Roadmap Generator
```

Por debajo, un único Assessment Engine (FastAPI) orquesta nueve motores especializados:
Asset Discovery, Interview Engine, Questionnaire, Risk Engine, IEC62443 Engine, MITRE Engine,
AI Engine, Report Engine y Roadmap Engine — todos sobre PostgreSQL, con un PDF Builder
(WeasyPrint) al final de la cadena.

## El cambio de fondo: conocimiento, no datos planos

Cada hallazgo se guarda como un objeto completo en `control_evaluations`, no como un booleano:

```json
{
  "control": "IEC62443 SR 5.1",
  "estado": "No implantado",
  "criticidad": 9,
  "evidencia": "El responsable de planta confirma que todos los PLC comparten VLAN con el ERP.",
  "impacto": "Un compromiso en IT podría propagarse directamente a los PLC de línea 3.",
  "quick_win": "Desplegar VLAN dedicada y firewall entre red corporativa y red OT.",
  "coste_estimado": "2000-5000 €",
  "horas": 16
}
```

Ese mismo objeto alimenta el Risk Engine (score), el Roadmap Generator (prioridad y fase)
y el AI Report Builder (narrativa) sin duplicar información en ningún sitio.

## Puesta en marcha

```bash
docker compose up -d --build
```

- API (Assessment Engine): http://localhost:8000/docs
- n8n: http://localhost:5678 (`admin` / `change_me`, cámbialo en `docker-compose.yml`)
- Metabase (Executive Dashboard): http://localhost:3000

Variable de entorno opcional para el AI Engine: `ANTHROPIC_API_KEY` (sin ella, el sistema
funciona igual pero `/report` no incluye resumen ejecutivo generado por IA — usa `?usar_ia=false`).

El catálogo de controles (IEC 62443 y MITRE ATT&CK for ICS, en `seed/`) se carga automáticamente
al arrancar la API. Amplíalo añadiendo entradas a los JSON de `seed/`.

## Flujo probado de extremo a extremo

```bash
# 1. Cliente
curl -X POST http://localhost:8000/clients \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Hospital Ejemplo", "sector": "sanitario"}'
# -> {"client_id": 1}

# 2. Assessment
curl -X POST http://localhost:8000/assessments \
  -H "Content-Type: application/json" \
  -d '{"client_id": 1, "nombre": "Auditoría OT Q3 2026", "alcance": "Red IoMT planta 2"}'
# -> {"assessment_id": 1}

# 3. Interview Engine: registrar un hallazgo (objeto de conocimiento completo)
curl -X POST http://localhost:8000/assessments/1/interview \
  -H "Content-Type: application/json" \
  -d '{
    "framework": "IEC62443", "codigo": "SR 5.1", "estado": "No implantado", "criticidad": 9,
    "evidencia": "Todos los PLC comparten VLAN con el ERP.",
    "impacto": "Un compromiso en IT se propagaría a los PLC de línea 3.",
    "quick_win": "Desplegar VLAN dedicada y firewall red corporativa/OT.",
    "coste_estimado": "2000-5000€", "horas": 16
  }'

# 4. Risk Engine
curl -X POST http://localhost:8000/assessments/1/risk-score

# 5. Roadmap Generator
curl -X POST http://localhost:8000/assessments/1/roadmap

# 6. AI Report Builder (genera resumen ejecutivo + PDF)
curl -X POST "http://localhost:8000/assessments/1/report?usar_ia=true"

# 7. Executive Dashboard (JSON resumen para paneles)
curl http://localhost:8000/assessments/1/dashboard
```

Este flujo está probado con PostgreSQL real: para un hallazgo con criticidad 9 "No implantado"
el Risk Engine calculó correctamente un score de 86.96 (nivel crítico), el Roadmap Generator
clasificó las acciones en fases, y el PDF Builder generó el informe con la plantilla de marca.

## Flujo en n8n

Réplica los pasos 3-6 como nodos HTTP Request encadenados, con un Webhook o Cron como disparador.
Añade un nodo IF tras el paso 4: si `nivel == "crítico"`, deriva a una rama de notificación
urgente (Slack/email a prioridad alta) antes de continuar con el roadmap y el informe.

## Cuestionario en lote

Para cargar muchas respuestas de golpe (ej. un Excel/formulario ya cumplimentado por el cliente),
usa `/assessments/{id}/questionnaire` con una lista de respuestas en el mismo formato que
`/interview`. Los errores individuales no abortan el lote — se devuelven junto a los registros
que sí se guardaron correctamente.

## Asset Discovery

`/assessments/{id}/assets` registra el inventario de activos como base del assessment
(estado "Pendiente de evaluar"), para que Interview Engine y Questionnaire puedan referenciarlos
después con hallazgos concretos por control.

## Estructura del proyecto

```
sentra-os/
├── docker-compose.yml
├── db/init.sql                    # esquema: frameworks, controls, clients, assessments,
│                                   #   control_evaluations, risk_scores, roadmap_items, reports
├── seed/
│   ├── iec62443_controls.json     # catálogo IEC 62443 (ampliable)
│   └── mitre_ics_techniques.json  # catálogo MITRE ATT&CK for ICS (ampliable)
├── templates/report.html          # plantilla del informe, marca Sentra OS
└── app/
    ├── main.py                    # API FastAPI, orquesta todos los módulos
    ├── db.py
    └── modules/
        ├── controls_catalog.py    # base de conocimiento compartida (framework+código -> control)
        ├── asset_discovery.py
        ├── interview_engine.py
        ├── questionnaire.py
        ├── iec62443_engine.py
        ├── mitre_engine.py
        ├── risk_engine.py
        ├── roadmap_engine.py
        ├── ai_engine.py           # única capa que llama a la API de Claude
        └── report_engine.py       # ensambla todo y genera el PDF (WeasyPrint)
```
