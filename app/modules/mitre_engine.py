"""
MITRE Engine
------------
Capa especializada sobre controls_catalog para MITRE ATT&CK for ICS.
Mismo patrón que IEC62443 Engine: aquí se podrían añadir en el futuro
relaciones técnica -> táctica, o cruces con IEC62443 Engine para mostrar
qué controles mitigan qué técnicas.
"""

from modules.controls_catalog import registrar_evaluacion, listar_controles

FRAMEWORK = "MITRE-ATTCK-ICS"


def catalogo() -> list[dict]:
    return listar_controles(FRAMEWORK)


def registrar_hallazgo(assessment_id: int, codigo: str, **kwargs) -> int:
    return registrar_evaluacion(assessment_id, FRAMEWORK, codigo, **kwargs)
