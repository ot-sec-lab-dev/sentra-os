from sqlalchemy import text
from db import engine


def obtener_dashboard_activos(assessment_id: int):

    with engine.begin() as conn:

        rows = conn.execute(
            text(
                """
                SELECT
                    a.id,
                    a.nombre,
                    a.tipo,
                    a.criticidad_negocio,
                    a.zona_purdue,

                    COUNT(ab.id) AS total_baselines,

                    SUM(
                        CASE
                            WHEN ab.compliance = TRUE THEN 1
                            ELSE 0
                        END
                    ) AS baselines_ok,

                    SUM(
                        CASE
                            WHEN ab.compliance = FALSE THEN 1
                            ELSE 0
                        END
                    ) AS baselines_fallidos

                FROM assets a

                LEFT JOIN asset_baselines ab
                    ON ab.asset_id = a.id

                WHERE a.assessment_id = :aid

                GROUP BY
                    a.id,
                    a.nombre,
                    a.tipo,
                    a.criticidad_negocio,
                    a.zona_purdue

                ORDER BY
                    a.criticidad_negocio DESC,
                    a.nombre
                """
            ),
            {"aid": assessment_id},
        ).fetchall()

    resultado = []

    for r in rows:

        riesgo = (r.criticidad_negocio or 5) * 10

        if (r.zona_purdue or 0) <= 1:
            riesgo += 20
        elif r.zona_purdue == 2:
            riesgo += 10

        riesgo = min(riesgo, 100)

        resultado.append(
            {
                "asset_id": r.id,
                "nombre": r.nombre,
                "tipo": r.tipo,
                "criticidad": r.criticidad_negocio,
                "zona_purdue": r.zona_purdue,
                "risk_score": riesgo,
                "total_baselines": r.total_baselines,
                "baselines_ok": r.baselines_ok or 0,
                "baselines_fallidos": r.baselines_fallidos or 0,
            }
        )

    return resultado