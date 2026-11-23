# UC14: Dividir custos da viagem entre membros do grupo (Implementado por Sarah Meireles)

from sqlalchemy import select

from src.database import SessionLocal
from src.persistence.models import AcompanhanteRecord, grupos_acompanhantes


class CustoDAO:
    def listar_responsaveis_acompanhantes(self, grupo_id: int) -> list[int]:
        with SessionLocal() as session:
            return list(
                session.scalars(
                    select(AcompanhanteRecord.viajante_id)
                    .join(
                        grupos_acompanhantes,
                        grupos_acompanhantes.c.acompanhante_id == AcompanhanteRecord.id,
                    )
                    .where(
                        grupos_acompanhantes.c.grupo_id == grupo_id,
                        AcompanhanteRecord.viajante_id.is_not(None),
                    )
                )
            )