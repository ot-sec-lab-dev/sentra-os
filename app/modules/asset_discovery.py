"""
Asset Discovery
---------------
Punto de entrada para inventario de activos OT/IoMT: puede alimentarse desde
un export de una herramienta de descubrimiento pasivo (Nozomi, Claroty,
Armis...), un CSV manual, o una API.
"""

from sqlalchemy import text
from db import engine


def registrar_activos(assessment_id: int, activos: list[dict]) -> list[int]:

    ids = []

    with engine.begin() as conn:

        for activo in activos:

            # ¿Existe ya este activo?
            existente = None

            if activo.get("ip"):

                existente = conn.execute(
                    text("""
                        SELECT id
                        FROM assets
                        WHERE assessment_id = :assessment_id
                          AND ip = :ip
                    """),
                    {
                        "assessment_id": assessment_id,
                        "ip": activo.get("ip"),
                    },
                ).scalar()

            parametros = {
                "assessment_id": assessment_id,
                "nombre": activo.get("nombre"),
                "tipo": activo.get("tipo"),
                "fabricante": activo.get("fabricante"),
                "modelo": activo.get("modelo"),
                "ip": activo.get("ip"),
                "mac": activo.get("mac"),
                "so": activo.get("sistema_operativo"),
                "firmware": activo.get("firmware"),
                "ubicacion": activo.get("ubicacion"),
                "zona": activo.get("zona_purdue"),
                "criticidad": activo.get("criticidad_negocio", 3),
                "owner": activo.get("owner"),
                "estado": activo.get("estado", "Activo"),
                "last_seen": activo.get("last_seen"),
                "criticidad_negocio": activo.get("criticidad_negocio", 5),
            }

            if existente:

                conn.execute(
                    text("""
                        UPDATE assets
                        SET
                            nombre = :nombre,
                            tipo = :tipo,
                            fabricante = :fabricante,
                            modelo = :modelo,
                            mac = :mac,
                            sistema_operativo = :so,
                            firmware = :firmware,
                            ubicacion = :ubicacion,
                            zona_purdue = :zona,
                            criticidad = :criticidad,
                            owner = :owner,
                            estado = :estado,
                            last_seen = :last_seen,
                            criticidad_negocio = :criticidad_negocio
                        WHERE id = :asset_id
                    """),
                    {
                        **parametros,
                        "asset_id": existente,
                    },
                )

                ids.append(existente)

            else:

                asset_id = conn.execute(
                    text("""
                        INSERT INTO assets
                        (
                            assessment_id,
                            nombre,
                            tipo,
                            fabricante,
                            modelo,
                            ip,
                            mac,
                            sistema_operativo,
                            firmware,
                            ubicacion,
                            zona_purdue,
                            criticidad,
                            owner,
                            estado,
                            last_seen,
                            criticidad_negocio
                        )
                        VALUES
                        (
                            :assessment_id,
                            :nombre,
                            :tipo,
                            :fabricante,
                            :modelo,
                            :ip,
                            :mac,
                            :so,
                            :firmware,
                            :ubicacion,
                            :zona,
                            :criticidad,
                            :owner,
                            :estado,
                            :last_seen,
                            :criticidad_negocio
                        )
                        RETURNING id
                    """),
                    parametros,
                ).scalar()

                ids.append(asset_id)

    return ids