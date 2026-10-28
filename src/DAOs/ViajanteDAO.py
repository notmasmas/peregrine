from sqlalchemy import select

from src.database import SessionLocal
from src.model.Viajante import Viajante
from src.persistence.models import ViajanteRecord


class ViajanteDAO:
    def criar(self, viajante: Viajante) -> ViajanteRecord:
        with SessionLocal() as session:
            viajante_record = ViajanteRecord(
                nome=viajante.nome,
                email=viajante.email,
                data_nascimento=viajante.data_nascimento,
                senha=viajante.senha,
            )
            session.add(viajante_record)
            session.commit()
            session.refresh(viajante_record)
            viajante.id = viajante_record.id
            return viajante_record

    def buscar_por_id(self, viajante_id: int) -> ViajanteRecord | None:
        with SessionLocal() as session:
            return session.get(ViajanteRecord, viajante_id)
    
    def buscar_por_email(self, viajante_email: str) -> ViajanteRecord | None:
        with SessionLocal() as session:
            return session.scalar(
                select(ViajanteRecord).where(ViajanteRecord.email == viajante_email)
            )
