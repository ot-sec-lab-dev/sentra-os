from sqlalchemy import text
from db import engine


def registrar_baseline(asset_id: int, baseline: dict):

    with engine.begin() as conn:

        baseline_id = conn.execute(
            text("""
                INSERT INTO asset_baselines
                (
                    asset_id,
                    baseline_name,
                    expected_value,
                    current_value,
                    compliance
                )
                VALUES
                (
                    :asset_id,
                    :baseline_name,
                    :expected_value,
                    :current_value,
                    :compliance
                )
                RETURNING id
            """),
            {
                "asset_id": asset_id,
                "baseline_name": baseline["baseline_name"],
                "expected_value": baseline.get("expected_value"),
                "current_value": baseline.get("current_value"),
                "compliance": baseline.get("compliance", False),
            },
        ).scalar()

    return baseline_id


def obtener_baselines(asset_id: int):

    with engine.begin() as conn:

        rows = conn.execute(
            text("""
                SELECT *
                FROM asset_baselines
                WHERE asset_id = :asset_id
                ORDER BY id
            """),
            {"asset_id": asset_id},
        ).mappings().all()

    return rows