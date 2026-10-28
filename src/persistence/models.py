from datetime import date

from sqlalchemy import Date, Float, ForeignKey, Integer, JSON, String, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


grupos_participantes = Table(
    "grupos_participantes",
    Base.metadata,
    Column("grupo_id", ForeignKey("grupos.id"), primary_key=True),
    Column("viajante_id", ForeignKey("viajantes.id"), primary_key=True),
)

grupos_acompanhantes = Table(
    "grupos_acompanhantes",
    Base.metadata,
    Column("grupo_id", ForeignKey("grupos.id"), primary_key=True),
    Column("acompanhante_id", ForeignKey("acompanhantes.id"), primary_key=True),
)


class ViajanteRecord(Base):
    __tablename__ = "viajantes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    data_nascimento: Mapped[date | None] = mapped_column(Date, nullable=True)
    email: Mapped[str] = mapped_column(String(320), nullable=False, unique=True)
    senha: Mapped[str] = mapped_column(String(150), nullable=False)

    acompanhantes: Mapped[list["AcompanhanteRecord"]] = relationship(
        back_populates="viajante_vinculado"
    )
    grupos_organizador: Mapped[list["GrupoRecord"]] = relationship(
        back_populates="organizador"
    )
    grupos_participante: Mapped[list["GrupoRecord"]] = relationship(
        secondary=grupos_participantes,
        back_populates="integrantes",
    )
    reservas: Mapped[list["ReservaRecord"]] = relationship(
        back_populates="titular"
    )


class GrupoRecord(Base):
    __tablename__ = "grupos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    sugestoes: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    organizador_id: Mapped[int | None] = mapped_column(
        ForeignKey("viajantes.id"),
        nullable=True,
    )

    organizador: Mapped["ViajanteRecord | None"] = relationship(
        back_populates="grupos_organizador"
    )
    integrantes: Mapped[list["ViajanteRecord"]] = relationship(
        secondary=grupos_participantes,
        back_populates="grupos_participante",
    )
    acompanhantes: Mapped[list["AcompanhanteRecord"]] = relationship(
        secondary=grupos_acompanhantes,
        back_populates="grupos",
    )
    itinerario: Mapped["ItinerarioRecord | None"] = relationship(
        back_populates="grupo",
        uselist=False,
    )


class AcompanhanteRecord(Base):
    __tablename__ = "acompanhantes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    viajante_id: Mapped[int | None] = mapped_column(
        ForeignKey("viajantes.id"),
        nullable=True,
    )

    viajante_vinculado: Mapped["ViajanteRecord | None"] = relationship(
        back_populates="acompanhantes"
    )
    grupos: Mapped[list["GrupoRecord"]] = relationship(
        secondary=grupos_acompanhantes,
        back_populates="acompanhantes",
    )


class ItinerarioRecord(Base):
    __tablename__ = "itinerarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    grupo_id: Mapped[int] = mapped_column(
        ForeignKey("grupos.id"),
        nullable=False,
        unique=True,
    )
    programacao: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    data_inicial: Mapped[date | None] = mapped_column(Date, nullable=True)
    valor_total: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    grupo: Mapped["GrupoRecord"] = relationship(back_populates="itinerario")
    reservas: Mapped[list["ReservaRecord"]] = relationship(
        back_populates="itinerario"
    )


class ReservaRecord(Base):
    __tablename__ = "reservas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    preco: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    titular_id: Mapped[int] = mapped_column(
        ForeignKey("viajantes.id"),
        nullable=False,
    )
    itinerario_id: Mapped[int | None] = mapped_column(
        ForeignKey("itinerarios.id"),
        nullable=True,
    )

    titular: Mapped["ViajanteRecord"] = relationship(back_populates="reservas")
    itinerario: Mapped["ItinerarioRecord | None"] = relationship(
        back_populates="reservas"
    )
