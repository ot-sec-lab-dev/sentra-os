"""
AI Engine
---------
Único módulo que llama a un LLM (Claude, vía API de Anthropic). Su trabajo
NO es decidir el riesgo — eso lo hace Risk Engine con reglas auditables.
Su trabajo es redactar: convertir los objetos de conocimiento ya calculados
en prosa ejecutiva, y opcionalmente proponer quick_win/impacto cuando el
consultor no los ha rellenado en campo.

Requiere la variable de entorno ANTHROPIC_API_KEY.
"""

import os
import json
from anthropic import Anthropic

MODEL = "claude-sonnet-4-6"

_client = None


def _get_client() -> Anthropic:
    global _client
    if _client is None:
        _client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _client


def generar_resumen_ejecutivo(cliente_nombre: str, score: float, nivel: str, hallazgos: list[dict]) -> str:
    """
    hallazgos: lista de control_evaluations relevantes (los de mayor
    criticidad, ya filtrados fuera de este módulo) con sus campos
    codigo/nombre/estado/criticidad/impacto.
    """
    top_hallazgos = sorted(hallazgos, key=lambda h: h["criticidad"], reverse=True)[:5]

    prompt = f"""Eres un consultor senior de ciberseguridad OT/IoMT. Redacta un resumen
ejecutivo de 3-4 párrafos (en español, tono profesional, sin tecnicismos innecesarios)
para el informe de auditoría de "{cliente_nombre}".

Score de riesgo global: {score}/100 (nivel: {nivel}).

Los 5 hallazgos de mayor criticidad son:
{json.dumps(top_hallazgos, ensure_ascii=False, indent=2)}

El resumen debe: (1) situar el nivel de riesgo global, (2) mencionar los 2-3
hallazgos más relevantes en términos de impacto de negocio, (3) cerrar con
una recomendación general sobre por dónde empezar. No uses listas ni
markdown, solo párrafos de texto corrido."""

    response = _get_client().messages.create(
        model=MODEL,
        max_tokens=800,
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(block.text for block in response.content if block.type == "text")


def completar_hallazgo(hallazgo: dict) -> dict:
    """
    Si el consultor no ha rellenado impacto y/o quick_win en campo, se los
    propone la IA a partir de la evidencia y el control. El resultado debe
    revisarse antes de publicarse — es una propuesta, no una verdad cerrada.
    """
    if hallazgo.get("impacto") and hallazgo.get("quick_win"):
        return hallazgo

    prompt = f"""Control: {hallazgo.get('codigo')} - {hallazgo.get('nombre')}
Estado: {hallazgo.get('estado')} (criticidad {hallazgo.get('criticidad')}/10)
Evidencia observada: {hallazgo.get('evidencia', 'no especificada')}

Responde SOLO con un JSON de esta forma, sin texto adicional ni backticks:
{{"impacto": "1-2 frases sobre la consecuencia de negocio si no se corrige",
  "quick_win": "1 acción concreta y accionable de remediación rápida"}}"""

    response = _get_client().messages.create(
        model=MODEL,
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}],
    )
    texto = "".join(block.text for block in response.content if block.type == "text")

    try:
        propuesta = json.loads(texto)
    except json.JSONDecodeError:
        propuesta = {"impacto": "", "quick_win": ""}

    hallazgo["impacto"] = hallazgo.get("impacto") or propuesta.get("impacto", "")
    hallazgo["quick_win"] = hallazgo.get("quick_win") or propuesta.get("quick_win", "")
    return hallazgo
