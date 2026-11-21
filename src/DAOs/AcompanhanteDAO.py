from sqlalchemy import select

from src.database import SessionLocal
from src.model.Acompanhante import Acompanhante
from src.persistence.models import AcompanhanteRecord, ViajanteRecord

class AcompanhanteDAO:
    def criar(self, acompanhante: Acompanhante) -> AcompanhanteRecord:
        viajante_vinculado = acompanhante.viajante_vinculado
        if viajante_vinculado is None:
            raise ValueError("O acompanhante precisa ter um responsável.")

        with SessionLocal() as session:
            viajante_responsavel = session.get(
                ViajanteRecord, viajante_vinculado.id
            )
            if viajante_responsavel is None:
                raise ValueError("O organizador não está cadastrado no banco de dados.")

            registro = AcompanhanteRecord(
                nome=acompanhante.nome,
                viajante_vinculado=viajante_responsavel,
            )
            session.add(registro)
            session.commit()
            session.refresh(registro)
            acompanhante.id = registro.id
            return registro

    def listar_por_viajante_id(self, viajante_id: int) -> list[Acompanhante]:
        with SessionLocal() as session:
            registros = session.scalars(
                select(AcompanhanteRecord)
                .where(AcompanhanteRecord.viajante_id == viajante_id)
                .order_by(AcompanhanteRecord.nome)
            ).all()
            return [
                Acompanhante(id=registro.id, nome=registro.nome)
                for registro in registros
            ]