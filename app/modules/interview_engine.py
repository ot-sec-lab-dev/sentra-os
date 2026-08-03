"""
Interview Engine
-----------------
Convierte las respuestas de una entrevista con el cliente (responsable OT,
mantenimiento, IT...) en objetos de conocimiento completos. A diferencia de
Questionnaire (respuestas cerradas), aquí se espera texto libre que el
auditor ya ha interpretado en campo — por eso los campos evidencia/impacto
suelen venir ya redactados por el consultor, y quick_win puede quedar vacío
para que lo complete AI Engine más adelante.
"""

from modules.iec62443_engine import registrar_hallazgo as registrar_iec62443
from modules.mitre_engine import registrar_hallazgo as registrar_mitre

REGISTRADORES = {
    "IEC62443": registrar_iec62443,
    "MITRE-ATTCK-ICS": registrar_mitre,
}


def registrar_respuesta_entrevista(assessment_id: int, respuesta: dict) -> int:
    """
    respuesta: {
      "framework": "IEC62443", "codigo": "SR 5.1",
      "estado": "No implantado", "criticidad": 9,
      "evidencia": "El responsable de planta confirma que...",
      "impacto": "...", "coste_estimado": "...", "horas": 12
    }
    """
    framework = respuesta["framework"]
    if framework not in REGISTRADORES:
        raise ValueError(f"Framework no soportado por Interview Engine: {framework}")

    return REGISTRADORES[framework](
        assessment_id,
        respuesta["codigo"],
        estado=respuesta["estado"],
        criticidad=respuesta["criticidad"],
        evidencia=respuesta.get("evidencia", ""),
        impacto=respuesta.get("impacto", ""),
        quick_win=respuesta.get("quick_win", ""),
        coste_estimado=respuesta.get("coste_estimado", ""),
        horas=respuesta.get("horas"),
        origen="entrevista",
        asset_id=respuesta.get("asset_id"),
    )
