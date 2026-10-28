from sqlalchemy import select

from src.database import SessionLocal
from src.model.Grupo import Grupo
from src.persistence.models import GrupoRecord, ViajanteRecord

# Implementado por Maria Helena Melo

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

    def listar_integrantes(self, grupo_id: int) -> list[ViajanteRecord]:
        with SessionLocal() as session:
            grupo = session.get(GrupoRecord, grupo_id)
            if grupo is None:
                raise ValueError("Grupo não encontrado.")
            # list() força o carregamento dos integrantes antes de fechar a sessão
            return list(grupo.integrantes)
 
    def adicionar_integrante(self, grupo_id: int, email: str) -> ViajanteRecord:
        with SessionLocal() as session:
            grupo = session.get(GrupoRecord, grupo_id)
            if grupo is None:
                raise ValueError("Grupo não encontrado.")
 
            viajante = session.scalar(
                select(ViajanteRecord).where(ViajanteRecord.email == email)
            )
            if viajante is None:
                raise ValueError("Não existe viajante cadastrado com esse e-mail.")
 
            if viajante.id == grupo.organizador_id or viajante in grupo.integrantes:
                raise ValueError("Este viajante já faz parte do grupo.")
 
            grupo.integrantes.append(viajante)
            session.commit()
            session.refresh(viajante)
            return viajante
 
    def remover_integrante(self, grupo_id: int, viajante_id: int) -> None:
        with SessionLocal() as session:
            grupo = session.get(GrupoRecord, grupo_id)
            if grupo is None:
                raise ValueError("Grupo não encontrado.")
 
            if viajante_id == grupo.organizador_id:
                raise ValueError("O organizador não pode ser excluído do grupo.")
 
            viajante = session.get(ViajanteRecord, viajante_id)
            if viajante is None or viajante not in grupo.integrantes:
                raise ValueError("O viajante não faz parte deste grupo.")
 
            grupo.integrantes.remove(viajante)
            session.commit()
 
    def listar_por_organizador(self, organizador_id: int) -> list[GrupoRecord]:
        with SessionLocal() as session:
            return list(
                session.scalars(
                    select(GrupoRecord)
                    .where(GrupoRecord.organizador_id == organizador_id)
                    .order_by(GrupoRecord.id)
                )
            )