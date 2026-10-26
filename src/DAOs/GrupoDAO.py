from sqlalchemy import select

from src.database import SessionLocal
from src.model.Grupo import Grupo
from src.persistence.models import GrupoRecord, ViajanteRecord


class GrupoDAO:
    def criar(self, grupo: Grupo) -> GrupoRecord:
        if grupo.organizador is None:
            raise ValueError("O grupo precisa ter um organizador.")

        with SessionLocal() as session:
            organizador = session.scalar(
                select(ViajanteRecord).where(
                    ViajanteRecord.email == grupo.organizador.email
                )
            )
            if organizador is None:
                raise ValueError("O organizador não está cadastrado no banco de dados.")

            registro = GrupoRecord(
                nome=grupo.nome,
                sugestoes=grupo.sugestoes,
                organizador=organizador,
            )
            session.add(registro)
            session.commit()
            session.refresh(registro)
            grupo.id = registro.id
            return registro

    def buscar_por_id(self, grupo_id: int) -> GrupoRecord | None:
        with SessionLocal() as session:
            return session.get(GrupoRecord, grupo_id)