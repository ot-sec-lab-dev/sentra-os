"""
Asset Discovery
---------------
Punto de entrada para inventario de activos OT/IoMT: puede alimentarse desde
un export de una herramienta de descubrimiento pasivo (Nozomi, Claroty,
Armis...), un CSV manual, o una API. Aquí no se decide nada de riesgo —
solo se deja constancia de qué activos existen y con qué metadatos, para
que Interview Engine y Questionnaire puedan referenciarlos al generar
evaluaciones de control.
"""

from db import engine
from sqlalchemy import text


def registrar_activos(assessment_id: int, activos: list[dict]) -> list[int]:

    ids = []

    with engine.begin() as conn:

        for activo in activos:

            asset_id = conn.execute(

                text(
                    """
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
                        criticidad
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
                        :criticidad
                    )
                    RETURNING id
                    """
                ),

                {
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
                },

            ).scalar()

            ids.append(asset_id)

    return ids
