"""
Catálogo de controles compartido.

Este módulo es la base de conocimiento reutilizable entre TODAS las
evaluaciones y clientes: los frameworks (IEC 62443, MITRE ATT&CK for ICS)
y sus controles/técnicas se cargan una vez y se referencian por id desde
cada control_evaluation. IEC62443 Engine y MITRE Engine son wrappers finos
sobre esta base, especializados en cada framework.
"""

import json
import os
from sqlalchemy import text

from db import engine

SEED_DIR = os.environ.get("SEED_DIR", "/app/seed")


def cargar_catalogo():
    """Carga los JSON semilla en las tablas frameworks/controls (idempotente)."""
    catalogos = {
        "IEC62443": "iec62443_controls.json",
        "MITRE-ATTCK-ICS": "mitre_ics_techniques.json",
    }

    with engine.begin() as conn:
        for framework_nombre, filename in catalogos.items():
            fw_id = conn.execute(
                text(
                    """INSERT INTO frameworks (nombre) VALUES (:nombre)
                       ON CONFLICT (nombre) DO UPDATE SET nombre = EXCLUDED.nombre
                       RETURNING id"""
                ),
                {"nombre": framework_nombre},
            ).scalar()

            path = os.path.join(SEED_DIR, filename)
            with open(path, encoding="utf-8") as f:
                controles = json.load(f)

            for c in controles:
                conn.execute(
                    text(
                        """INSERT INTO controls (framework_id, codigo, nombre, descripcion)
                           VALUES (:fw, :codigo, :nombre, :descripcion)
                           ON CONFLICT (framework_id, codigo) DO UPDATE
                           SET nombre = EXCLUDED.nombre, descripcion = EXCLUDED.descripcion"""
                    ),
                    {
                        "fw": fw_id,
                        "codigo": c["codigo"],
                        "nombre": c["nombre"],
                        "descripcion": c["descripcion"],
                    },
                )
def normalizar_codigo_control(framework: str, codigo: str) -> str:
    """
    Normaliza identificadores de controles para resolverlos
    independientemente del formato recibido por la API.
    """

    codigo = codigo.upper().strip()

    if framework == "IEC62443":

        # Eliminar prefijo completo IEC62443-3-3-
        codigo = codigo.replace(
            "IEC62443-3-3-",
            ""
        )

        # Convertir IEC62443 SR1.1 -> SR1.1
        codigo = codigo.replace(
            "IEC62443 SR",
            "SR"
        )

        # Convertir SR1.1 -> SR 1.1
        if codigo.startswith("SR") and not codigo.startswith("SR "):
            codigo = codigo.replace(
                "SR",
                "SR ",
                1
            )

    return codigo

def resolver_control_id(framework_nombre: str, codigo: str) -> int | None:

    print("DEBUG ORIGINAL:", framework_nombre, codigo)

    codigo = normalizar_codigo_control(
        framework_nombre,
        codigo
    )

    print("DEBUG NORMALIZADO:", codigo)

    with engine.connect() as conn:
        row = conn.execute(
            text(
                """SELECT c.id FROM controls c
                   JOIN frameworks f ON c.framework_id = f.id
                   WHERE f.nombre = :fw AND c.codigo = :codigo"""
            ),
            {"fw": framework_nombre, "codigo": codigo},
        ).fetchone()
    return row[0] if row else None


def registrar_evaluacion(
    assessment_id: int,
    framework: str,
    codigo: str,
    estado: str,
    criticidad: int,
    evidencia: str = "",
    impacto: str = "",
    quick_win: str = "",
    coste_estimado: str = "",
    horas: int | None = None,
    origen: str = "cuestionario",
) -> int:
    """
    Inserta un objeto de conocimiento completo (control_evaluation).
    Esta es la función central que usan Interview Engine, Questionnaire,
    IEC62443 Engine y MITRE Engine para dejar constancia de un hallazgo
    con todo su contexto, no solo un valor plano.
    """
    control_id = resolver_control_id(framework, codigo)
    if control_id is None:
        raise ValueError(f"Control {codigo} no encontrado en framework {framework}")

    with engine.begin() as conn:
        row_id = conn.execute(
            text(
                """INSERT INTO control_evaluations
                   (assessment_id, control_id, estado, criticidad, evidencia,
                    impacto, quick_win, coste_estimado, horas, origen)
                   VALUES (:aid, :cid, :estado, :crit, :evidencia,
                           :impacto, :quick_win, :coste, :horas, :origen)
                   RETURNING id"""
            ),
            {
                "aid": assessment_id,
                "cid": control_id,
                "estado": estado,
                "crit": criticidad,
                "evidencia": evidencia,
                "impacto": impacto,
                "quick_win": quick_win,
                "coste": coste_estimado,
                "horas": horas,
                "origen": origen,
            },
        ).scalar()
    return row_id


def listar_controles(framework_nombre: str | None = None) -> list[dict]:
    query = """SELECT f.nombre, c.codigo, c.nombre, c.descripcion FROM controls c
               JOIN frameworks f ON c.framework_id = f.id"""
    params = {}
    if framework_nombre:
        query += " WHERE f.nombre = :fw"
        params["fw"] = framework_nombre

    with engine.connect() as conn:
        rows = conn.execute(text(query), params).fetchall()

    return [
        {"framework": r[0], "codigo": r[1], "nombre": r[2], "descripcion": r[3]}
        for r in rows
    ]
