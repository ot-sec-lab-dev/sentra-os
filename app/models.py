from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
)
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True)

    assessment_id = Column(Integer)

    nombre = Column(Text, nullable=False)

    tipo = Column(Text)

    fabricante = Column(Text)

    modelo = Column(Text)

    ip = Column(Text)

    mac = Column(Text)

    sistema_operativo = Column(Text)

    firmware = Column(Text)

    ubicacion = Column(Text)

    zona_purdue = Column(Integer)

    criticidad = Column(Integer)

    owner = Column(Text)

    estado = Column(Text)

    last_seen = Column(DateTime)

    criticidad_negocio = Column(Integer)

    created_at = Column(DateTime, server_default=func.now())


class AssetBaseline(Base):
    __tablename__ = "asset_baselines"

    id = Column(Integer, primary_key=True)

    asset_id = Column(
        Integer,
        ForeignKey("assets.id"),
        nullable=False,
    )

    baseline_name = Column(String, nullable=False)

    expected_value = Column(Text)

    current_value = Column(Text)

    compliance = Column(Boolean, default=False)

    ultima_actualizacion = Column(
        DateTime,
        server_default=func.now(),
    )