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
    """
    activos: lista de dicts tipo
      {"nombre": "PLC-Linea3", "tipo": "PLC", "fabricante": "Siemens",
       "ubicacion": "Planta 2", "criticidad_negocio": 8}
    Devuelve los ids insertados. Usa la tabla control_evaluations con
    origen='asset_discovery' solo como registro de inventario base
    (evaluación pendiente), no como hallazgo cerrado.
    """
    ids = []
    with engine.begin() as conn:
        for activo in activos:
            row_id = conn.execute(
                text(
                    """INSERT INTO control_evaluations
                       (assessment_id, control_id, estado, criticidad, evidencia, origen)
                       VALUES (:aid, NULL, 'Pendiente de evaluar', :crit, :evidencia, 'asset_discovery')
                       RETURNING id"""
                ),
                {
                    "aid": assessment_id,
                    "crit": activo.get("criticidad_negocio", 5),
                    "evidencia": f"Activo descubierto: {activo.get('nombre')} "
                    f"({activo.get('tipo', 'desconocido')}, {activo.get('fabricante', '-')}) "
                    f"en {activo.get('ubicacion', 'sin ubicación')}",
                },
            ).scalar()
            ids.append(row_id)
    return ids
