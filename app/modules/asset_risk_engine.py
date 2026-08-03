"""
Asset Risk Engine
-----------------
Calcula el riesgo individual de cada activo descubierto.
"""

from sqlalchemy import text
from db import engine


def calcular_riesgo_activos(assessment_id: int):

    resultados = []

    with engine.begin() as conn:

        activos = conn.execute(
            text(
                """
                SELECT
                    id,
                    nombre,
                    criticidad_negocio,
                    zona_purdue
                FROM assets
                WHERE assessment_id = :aid
                """
            ),
            {"aid": assessment_id},
        ).fetchall()

        for activo in activos:

            asset_id = activo.id
            nombre = activo.nombre
            criticidad = activo.criticidad_negocio or 5
            zona = activo.zona_purdue or 0

            riesgo = criticidad * 10

            if zona <= 1:
                riesgo += 20
            elif zona == 2:
                riesgo += 10

            riesgo = min(riesgo, 100)

            resultados.append(
                {
                    "asset_id": asset_id,
                    "nombre": nombre,
                    "risk_score": riesgo,
                }
            )

    return resultados