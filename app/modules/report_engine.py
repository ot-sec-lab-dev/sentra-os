"""
Report Engine / PDF Builder
----------------------------
Punto de ensamblaje final: toma lo que ya han producido Risk Engine,
Roadmap Engine y (opcionalmente) AI Engine, y los vuelca en la plantilla
HTML de marca "Sentra OS", generando el PDF con WeasyPrint.
Este módulo no calcula nada — solo lee y presenta.
"""

import os
from datetime import datetime

from sqlalchemy import text
from jinja2 import Environment, FileSystemLoader

try:
    from weasyprint import HTML
    PDF_AVAILABLE = True
except Exception:
    PDF_AVAILABLE = False

from db import engine

OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "/app/output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

jinja_env = Environment(loader=FileSystemLoader("templates"))


def generar_informe(assessment_id: int, resumen_ejecutivo: str = "") -> dict:
    with engine.begin() as conn:
        assessment = conn.execute(
            text(
                """SELECT a.id, a.nombre, a.alcance, cl.nombre, cl.sector
                   FROM assessments a JOIN clients cl ON a.client_id = cl.id
                   WHERE a.id = :aid"""
            ),
            {"aid": assessment_id},
        ).fetchone()
        if assessment is None:
            raise ValueError("assessment no encontrado")
        _, assessment_nombre, alcance, cliente_nombre, sector = assessment

        risk = conn.execute(
            text(
                """SELECT score, nivel, desglose FROM risk_scores
                   WHERE assessment_id = :aid ORDER BY calculated_at DESC LIMIT 1"""
            ),
            {"aid": assessment_id},
        ).fetchone()
        if risk is None:
            raise ValueError("no hay risk_score calculado; ejecuta Risk Engine primero")
        score, nivel, desglose = risk

        hallazgos = conn.execute(
            text(
                """SELECT c.codigo, c.nombre, ce.estado, ce.criticidad, ce.evidencia,
                          ce.impacto, ce.quick_win, ce.coste_estimado, ce.horas
                   FROM control_evaluations ce
                   JOIN controls c ON ce.control_id = c.id
                   WHERE ce.assessment_id = :aid
                   ORDER BY ce.criticidad DESC"""
            ),
            {"aid": assessment_id},
        ).fetchall()

        roadmap = conn.execute(
            text(
                """SELECT fase, prioridad, titulo, horas, coste_estimado
                   FROM roadmap_items WHERE assessment_id = :aid ORDER BY prioridad"""
            ),
            {"aid": assessment_id},
        ).fetchall()

        template = jinja_env.get_template("report.html")
        html_content = template.render(
            cliente_nombre=cliente_nombre,
            sector=sector,
            assessment_nombre=assessment_nombre,
            alcance=alcance,
            score=score,
            nivel=nivel,
            desglose=desglose,
            resumen_ejecutivo=resumen_ejecutivo,
            hallazgos=[
                dict(
                    codigo=h[0], nombre=h[1], estado=h[2], criticidad=h[3],
                    evidencia=h[4], impacto=h[5], quick_win=h[6],
                    coste_estimado=h[7], horas=h[8],
                )
                for h in hallazgos
            ],
            roadmap=[
                dict(fase=r[0], prioridad=r[1], titulo=r[2], horas=r[3], coste_estimado=r[4])
                for r in roadmap
            ],
            fecha=datetime.now().strftime("%d/%m/%Y %H:%M"),
        )

        # Temporalmente generamos siempre HTML para validar el motor de informes
        filename = f"sentra_os_informe_{assessment_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.html"
        pdf_path = os.path.join(OUTPUT_DIR, filename)

        with open(pdf_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        report_id = conn.execute(
            text(
                """INSERT INTO reports (assessment_id, resumen_ejecutivo, pdf_path)
                   VALUES (:aid, :resumen, :path) RETURNING id"""
            ),
            {
                "aid": assessment_id,
                "resumen": resumen_ejecutivo,
                "path": pdf_path,
            },
        ).scalar()

    return {
        "report_id": report_id,
        "pdf_path": pdf_path,
    }