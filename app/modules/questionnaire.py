"""
Questionnaire
-------------
Ingesta de un cuestionario completo de una sola vez (ej. rellenado por el
cliente en un formulario o Excel). Mismo modelo de conocimiento que
Interview Engine, pero pensado para lotes: recibe una lista de respuestas
y las registra todas, devolviendo qué falló y qué no sin abortar el lote
completo por un único error.
"""

from modules.interview_engine import REGISTRADORES


def registrar_cuestionario(assessment_id: int, respuestas: list[dict]) -> dict:
    ok, errores = [], []

    for respuesta in respuestas:
        framework = respuesta.get("framework")
        registrador = REGISTRADORES.get(framework)
        if registrador is None:
            errores.append({"respuesta": respuesta, "error": f"framework desconocido: {framework}"})
            continue
        try:
            eval_id = registrador(
                assessment_id,
                respuesta["codigo"],
                estado=respuesta["estado"],
                criticidad=respuesta["criticidad"],
                evidencia=respuesta.get("evidencia", ""),
                impacto=respuesta.get("impacto", ""),
                quick_win=respuesta.get("quick_win", ""),
                coste_estimado=respuesta.get("coste_estimado", ""),
                horas=respuesta.get("horas"),
                origen="cuestionario",
            )
            ok.append(eval_id)
        except Exception as e:
            errores.append({"respuesta": respuesta, "error": str(e)})

    return {"registrados": ok, "errores": errores}
