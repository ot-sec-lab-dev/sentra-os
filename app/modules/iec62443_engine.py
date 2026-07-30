"""
IEC62443 Engine
---------------
Capa especializada sobre controls_catalog para el framework IEC 62443.
Aísla al resto del sistema de tener que conocer el nombre exacto del
framework y permite en el futuro añadir validaciones propias de la
norma (ej. requisitos que solo aplican a ciertos SL - Security Levels).
"""

from modules.controls_catalog import registrar_evaluacion, listar_controles

FRAMEWORK = "IEC62443"


def catalogo() -> list[dict]:
    return listar_controles(FRAMEWORK)


def registrar_hallazgo(assessment_id: int, codigo: str, **kwargs) -> int:
    return registrar_evaluacion(assessment_id, FRAMEWORK, codigo, **kwargs)
