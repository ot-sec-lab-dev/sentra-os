"""
Risk Engine
-----------
Calcula el score de riesgo de un assessment a partir de los objetos de
conocimiento (control_evaluations), no de valores planos. El peso de cada
hallazgo combina su criticidad de negocio con el grado de implantación
del control: un control crítico no implantado pesa mucho más que uno
crítico ya parcialmente cubierto.
"""

import json
from sqlalchemy import text
from db import engine

PESO_ESTADO = {
    "No implantado": 1.0,
    "Parcial": 0.5,
    "Implantado": 0.0,
}


def calcular_riesgo(assessment_id: int) -> dict:
    with engine.begin() as conn:
        rows = conn.execute(
            text(
                """SELECT ce.criticidad, ce.estado, f.nombre
                   FROM control_evaluations ce
                   LEFT JOIN controls c ON ce.control_id = c.id
                   LEFT JOIN frameworks f ON c.framework_id = f.id
                   WHERE ce.assessment_id = :aid AND ce.control_id IS NOT NULL"""
            ),
            {"aid": assessment_id},
        ).fetchall()

        if not rows:
            raise ValueError("No hay control_evaluations para calcular riesgo")

        total_ponderado = 0.0
        total_maximo = 0.0
        por_framework: dict[str, dict] = {}

        for criticidad, estado, framework in rows:
            peso = PESO_ESTADO.get(estado, 0.5)  # estado desconocido -> mitad de peso
            total_ponderado += criticidad * peso
            total_maximo += criticidad

            fw_key = framework or "sin_framework"
            por_framework.setdefault(fw_key, {"ponderado": 0.0, "maximo": 0.0})
            por_framework[fw_key]["ponderado"] += criticidad * peso
            por_framework[fw_key]["maximo"] += criticidad

        score = round((total_ponderado / total_maximo) * 100, 2) if total_maximo else 0.0

        desglose = {
            fw: round((v["ponderado"] / v["maximo"]) * 100, 2) if v["maximo"] else 0.0
            for fw, v in por_framework.items()
        }

        if score >= 70:
            nivel = "crítico"
        elif score >= 45:
            nivel = "alto"
        elif score >= 20:
            nivel = "medio"
        else:
            nivel = "bajo"

        score_id = conn.execute(
            text(
                """INSERT INTO risk_scores (assessment_id, score, nivel, desglose)
                   VALUES (:aid, :score, :nivel, CAST(:desglose AS JSONB)) RETURNING id"""
            ),
            {"aid": assessment_id, "score": score, "nivel": nivel, "desglose": json.dumps(desglose)},
        ).scalar()

    return {"score_id": score_id, "score": score, "nivel": nivel, "desglose_por_framework": desglose}
