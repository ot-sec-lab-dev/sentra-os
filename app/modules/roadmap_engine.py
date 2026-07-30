"""
Roadmap Engine
--------------
Convierte los hallazgos (control_evaluations con estado != 'Implantado')
en un roadmap por fases: Quick win (bajo esfuerzo, alta criticidad),
Medio plazo y Largo plazo. La prioridad dentro de cada fase es
criticidad descendente y, en empate, horas ascendente (lo más rápido
de resolver primero).
"""

from sqlalchemy import text
from db import engine


def _clasificar_fase(criticidad: int, horas: int | None) -> str:
    horas = horas if horas is not None else 999
    if criticidad >= 7 and horas <= 8:
        return "Quick win"
    if horas <= 40:
        return "Medio plazo"
    return "Largo plazo"


def generar_roadmap(assessment_id: int) -> list[dict]:
    with engine.begin() as conn:
        rows = conn.execute(
            text(
                """SELECT ce.id, c.codigo, c.nombre, ce.criticidad, ce.horas,
                          ce.coste_estimado, ce.quick_win
                   FROM control_evaluations ce
                   JOIN controls c ON ce.control_id = c.id
                   WHERE ce.assessment_id = :aid AND ce.estado != 'Implantado'"""
            ),
            {"aid": assessment_id},
        ).fetchall()

        items = []
        for ce_id, codigo, nombre, criticidad, horas, coste, quick_win in rows:
            fase = _clasificar_fase(criticidad, horas)
            titulo = quick_win or f"Remediar {codigo} — {nombre}"
            items.append(
                {
                    "control_evaluation_id": ce_id,
                    "fase": fase,
                    "titulo": titulo,
                    "criticidad": criticidad,
                    "horas": horas,
                    "coste_estimado": coste,
                }
            )

        orden_fase = {"Quick win": 0, "Medio plazo": 1, "Largo plazo": 2}
        items.sort(key=lambda i: (orden_fase[i["fase"]], -i["criticidad"], i["horas"] or 999))

        conn.execute(text("DELETE FROM roadmap_items WHERE assessment_id = :aid"), {"aid": assessment_id})

        for prioridad, item in enumerate(items, start=1):
            conn.execute(
                text(
                    """INSERT INTO roadmap_items
                       (assessment_id, control_evaluation_id, fase, prioridad, titulo, horas, coste_estimado)
                       VALUES (:aid, :ceid, :fase, :prioridad, :titulo, :horas, :coste)"""
                ),
                {
                    "aid": assessment_id,
                    "ceid": item["control_evaluation_id"],
                    "fase": item["fase"],
                    "prioridad": prioridad,
                    "titulo": item["titulo"],
                    "horas": item["horas"],
                    "coste": item["coste_estimado"],
                },
            )
            item["prioridad"] = prioridad

    return items
