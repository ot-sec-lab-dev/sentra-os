# 🛡️ Sentra OS

> AI-powered OT Security Assessment Platform for Industrial Control Systems (ICS)

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-REST_API-green)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791)
![IEC62443](https://img.shields.io/badge/IEC_62443-Compliant-orange)
![MITRE ATT%26CK ICS](https://img.shields.io/badge/MITRE-ATT%26CK_ICS-red)

---

# Overview

Sentra OS is an OT Cybersecurity Assessment Platform designed to automate industrial cybersecurity assessments based on IEC 62443 and MITRE ATT&CK ICS.

The platform allows cybersecurity consultants and OT security teams to perform structured assessments, calculate risk levels, generate remediation roadmaps and produce executive reports automatically.

---

# Key Features

- IEC 62443 Assessment Engine
- MITRE ATT&CK ICS Mapping
- Risk Scoring Engine
- Executive Report Generation
- AI Executive Summary (Claude AI)
- Roadmap Generator
- REST API
- Docker Deployment
- PostgreSQL Database

---

# Platform Architecture

```
                +-----------------------+
                |      Web Client       |
                +-----------+-----------+
                            |
                            |
                     REST API (FastAPI)
                            |
        +-------------------+-------------------+
        |                   |                   |
        |                   |                   |
Assessment Engine    Risk Engine      Report Engine
        |                   |                   |
        +-------------------+-------------------+
                            |
                     PostgreSQL Database
                            |
                  IEC62443 / MITRE Data
```

---

# Technology Stack

- Python 3.12
- FastAPI
- PostgreSQL
- SQLAlchemy
- Docker
- Docker Compose
- Jinja2
- Anthropic Claude API
- HTML Reporting

---

# Assessment Workflow

1. Create Assessment
2. Import Assets
3. Execute Interview
4. Calculate Risk Score
5. Generate Roadmap
6. Generate Executive Report
7. Export HTML / PDF

---

# Current Status

## Completed

- IEC62443 Engine
- Risk Engine
- Roadmap Engine
- HTML Reports
- Docker Deployment
- PostgreSQL Integration

## In Progress

- PDF Generation
- AI Executive Summary
- Authentication
- Dashboard
- Multi-user Support

---

# API Endpoints

| Endpoint | Description |
|----------|-------------|
| POST /assessments | Create Assessment |
| POST /interview | Execute Assessment |
| POST /risk-score | Calculate Risk |
| POST /report | Generate Report |

---

# Repository Structure

```
app/
    main.py
    modules/
    requirements.txt

db/
seed/
templates/

docker-compose.yml
README.md
```

---

# Future Roadmap

- Authentication
- Multi-Tenant Support
- Dashboard
- Asset Discovery
- Vulnerability Correlation
- PDF Reports
- Compliance Dashboards
- Multi-framework Support

---

# Author

Cybersecurity Engineer specialized in:

- OT Cybersecurity
- Industrial Control Systems
- IEC 62443
- MITRE ATT&CK ICS
- Threat Intelligence
- Risk Assessment
- Docker Infrastructure

---

# License

MIT License
