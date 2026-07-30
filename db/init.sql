-- ============================================================
-- Sentra OS — OT Assessment Engine
-- Esquema v2: el conocimiento vive a nivel de control, no de
-- valores booleanos sueltos. Cada evaluación de control es una
-- unidad de conocimiento completa y reutilizable.
-- ============================================================

CREATE TABLE IF NOT EXISTS frameworks (
    id SERIAL PRIMARY KEY,
    nombre TEXT UNIQUE NOT NULL          -- 'IEC62443', 'MITRE-ATTCK-ICS'
);

-- Catálogo de controles: la base de conocimiento reutilizable
-- entre TODOS los clientes y evaluaciones.
CREATE TABLE IF NOT EXISTS controls (
    id SERIAL PRIMARY KEY,
    framework_id INTEGER REFERENCES frameworks(id),
    codigo TEXT NOT NULL,                 -- 'SR 5.1', 'T0816'
    nombre TEXT NOT NULL,
    descripcion TEXT,
    UNIQUE (framework_id, codigo)
);

CREATE TABLE IF NOT EXISTS clients (
    id SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL,
    sector TEXT,                          -- 'sanitario', 'ferroviario', ...
    created_at TIMESTAMP DEFAULT now()
);

-- Un assessment es una auditoría/engagement concreto sobre un cliente
CREATE TABLE IF NOT EXISTS assessments (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES clients(id),
    nombre TEXT NOT NULL,                 -- 'Auditoría OT Q3 2026'
    alcance TEXT,                         -- descripción del alcance/activos cubiertos
    estado TEXT DEFAULT 'en_curso',
    created_at TIMESTAMP DEFAULT now()
);

-- ============================================================
-- LA PIEZA CLAVE: conocimiento estructurado por control evaluado.
-- No es "true/false" — es un hallazgo completo con evidencia,
-- impacto de negocio, quick win propuesto y coste estimado.
-- ============================================================
CREATE TABLE IF NOT EXISTS control_evaluations (
    id SERIAL PRIMARY KEY,
    assessment_id INTEGER REFERENCES assessments(id),
    control_id INTEGER REFERENCES controls(id),
    estado TEXT NOT NULL,                 -- 'Implantado' / 'Parcial' / 'No implantado'
    criticidad INTEGER NOT NULL CHECK (criticidad BETWEEN 1 AND 10),
    evidencia TEXT,                       -- qué se observó / de dónde sale el hallazgo
    impacto TEXT,                         -- consecuencia de negocio si no se corrige
    quick_win TEXT,                       -- acción concreta de remediación rápida
    coste_estimado TEXT,                  -- rango orientativo ('bajo', '2-5k€', etc.)
    horas INTEGER,                        -- esfuerzo estimado de remediación
    origen TEXT,                          -- 'entrevista' / 'cuestionario' / 'asset_discovery'
    created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS risk_scores (
    id SERIAL PRIMARY KEY,
    assessment_id INTEGER REFERENCES assessments(id),
    score NUMERIC(5,2) NOT NULL,
    nivel TEXT NOT NULL,
    desglose JSONB,                       -- score por framework / por dominio
    calculated_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS roadmap_items (
    id SERIAL PRIMARY KEY,
    assessment_id INTEGER REFERENCES assessments(id),
    control_evaluation_id INTEGER REFERENCES control_evaluations(id),
    fase TEXT NOT NULL,                   -- 'Quick win', 'Medio plazo', 'Largo plazo'
    prioridad INTEGER NOT NULL,
    titulo TEXT NOT NULL,
    horas INTEGER,
    coste_estimado TEXT
);

CREATE TABLE IF NOT EXISTS reports (
    id SERIAL PRIMARY KEY,
    assessment_id INTEGER REFERENCES assessments(id),
    resumen_ejecutivo TEXT,                -- narrativa generada por el AI Engine
    pdf_path TEXT,
    generated_at TIMESTAMP DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_ce_assessment ON control_evaluations(assessment_id);
CREATE INDEX IF NOT EXISTS idx_ce_control ON control_evaluations(control_id);
CREATE INDEX IF NOT EXISTS idx_roadmap_assessment ON roadmap_items(assessment_id);
