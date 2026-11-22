from sqlalchemy import Select, select
from sqlalchemy.orm import Session, selectinload

from src.database import SessionLocal
from src.model.Grupo import Grupo
from src.persistence.models import (
    AcompanhanteRecord,
    ConviteRecord,
    GrupoRecord,
    ViajanteRecord,
)

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

    def _buscar_para_alteracao(
        self, session: Session, grupo_id: int, organizador_id: int, *, bloquear: bool = True
    ) -> GrupoRecord:
        grupo = session.get(GrupoRecord, grupo_id, with_for_update=bloquear)
        if grupo is None:
            raise ValueError("Grupo não encontrado.")
        if organizador_id is None or grupo.organizador_id != organizador_id:
            raise ValueError("Apenas o organizador pode alterar este grupo.")
        return grupo

    def atualizar_nome(self, grupo_id: int, organizador_id: int, nome: str) -> None:
        with SessionLocal() as session:
            grupo = self._buscar_para_alteracao(session, grupo_id, organizador_id)
            grupo.nome = nome
            session.commit()

    def remover(self, grupo_id: int, organizador_id: int) -> None:
        with SessionLocal() as session:
            grupo = self._buscar_para_alteracao(session, grupo_id, organizador_id)
            session.delete(grupo)
            session.commit()

    def listar_integrantes(self, grupo_id: int) -> list[ViajanteRecord]:
        with SessionLocal() as session:
            grupo = session.get(GrupoRecord, grupo_id)
            if grupo is None:
                raise ValueError("Grupo não encontrado.")
            # list() força o carregamento dos integrantes antes de fechar a sessão
            return list(grupo.integrantes)

    @staticmethod
    def _ids_membros(grupo: GrupoRecord) -> set[int]:
        membros_ids = {integrante.id for integrante in grupo.integrantes}
        if grupo.organizador_id is not None:
            membros_ids.add(grupo.organizador_id)
        return membros_ids

    def listar_acompanhantes(
        self, grupo_id: int, viajante_id: int
    ) -> list[AcompanhanteRecord]:
        with SessionLocal() as session:
            grupo = session.get(GrupoRecord, grupo_id)
            if grupo is None:
                raise ValueError("Grupo não encontrado.")
            if viajante_id not in self._ids_membros(grupo):
                raise ValueError("Apenas membros do grupo podem acessar seus acompanhantes.")
            return sorted(grupo.acompanhantes, key=lambda a: (a.nome, a.id))

    def _consulta_acompanhantes_disponiveis(
        self, grupo_id: int, membros_ids: set[int]
    ) -> Select[tuple[AcompanhanteRecord]]:
        return select(AcompanhanteRecord).where(
            AcompanhanteRecord.viajante_id.in_(membros_ids),
            ~AcompanhanteRecord.grupos.any(GrupoRecord.id == grupo_id),
        )

    def listar_acompanhantes_disponiveis(
        self, grupo_id: int, organizador_id: int
    ) -> list[AcompanhanteRecord]:
        with SessionLocal() as session:
            grupo = self._buscar_para_alteracao(
                session, grupo_id, organizador_id, bloquear=False
            )
            consulta = self._consulta_acompanhantes_disponiveis(
                grupo_id, self._ids_membros(grupo)
            )
            consulta = consulta.options(
                selectinload(AcompanhanteRecord.viajante_vinculado).load_only(
                    ViajanteRecord.nome
                )
            ).order_by(AcompanhanteRecord.nome, AcompanhanteRecord.id)
            return list(session.scalars(consulta))

    def adicionar_acompanhantes(
        self, grupo_id: int, organizador_id: int, acompanhante_ids: list[int]
    ) -> None:
        ids = set(acompanhante_ids)
        if not ids:
            raise ValueError("Selecione pelo menos um acompanhante.")

        with SessionLocal() as session:
            grupo = self._buscar_para_alteracao(session, grupo_id, organizador_id)
            consulta = self._consulta_acompanhantes_disponiveis(
                grupo_id, self._ids_membros(grupo)
            )
            acompanhantes = list(
                session.scalars(consulta.where(AcompanhanteRecord.id.in_(ids)))
            )
            if len(acompanhantes) != len(ids):
                raise ValueError(
                    "A seleção contém acompanhantes que já estão no grupo "
                    "ou que não estão vinculados a um membro."
                )

            grupo.acompanhantes.extend(acompanhantes)
            session.commit()
 
    def remover_acompanhante(
        self, grupo_id: int, acompanhante_id: int, organizador_id: int
    ) -> None:
        with SessionLocal() as session:
            grupo = self._buscar_para_alteracao(session, grupo_id, organizador_id)
            acompanhante = session.get(AcompanhanteRecord, acompanhante_id)
            if acompanhante is None or acompanhante not in grupo.acompanhantes:
                raise ValueError("O acompanhante não faz parte deste grupo.")

            grupo.acompanhantes.remove(acompanhante)
            session.commit()

    def adicionar_integrante(
        self, grupo_id: int, email: str, remetente_id: int
    ) -> ViajanteRecord:
        return self.criar_convite(grupo_id, email, remetente_id).destinatario

    def criar_convite(
        self,
        grupo_id: int,
        email: str,
        remetente_id: int,
    ) -> ConviteRecord:
        with SessionLocal() as session:
            grupo = self._buscar_para_alteracao(session, grupo_id, remetente_id)
 
            viajante = session.scalar(
                select(ViajanteRecord).where(ViajanteRecord.email == email)
            )
            if viajante is None:
                raise ValueError("Não existe viajante cadastrado com esse e-mail.")
 
            if viajante.id == grupo.organizador_id or viajante in grupo.integrantes:
                raise ValueError("Este viajante já faz parte do grupo.")
 
            convite_existente = session.scalar(
                select(ConviteRecord).where(
                    ConviteRecord.grupo_id == grupo_id,
                    ConviteRecord.destinatario_id == viajante.id,
                    ConviteRecord.status == "Pendente",
                )
            )
            if convite_existente is not None:
                raise ValueError("Já existe um convite pendente para este viajante.")

            convite = ConviteRecord(
                grupo=grupo,
                destinatario=viajante,
                remetente_id=remetente_id,
                status="Pendente",
            )
            session.add(convite)
            session.commit()
            session.refresh(convite)
            # Mantém os dados do destinatário disponíveis depois de fechar a sessão.
            _ = convite.destinatario
            session.expunge(convite)
            return convite

    def convidar_integrante(
        self,
        grupo_id: int,
        email: str,
        remetente_id: int,
    ) -> ConviteRecord:
        return self.criar_convite(grupo_id, email, remetente_id)

    def aceitar_convite(self, convite_id: int, destinatario_id: int) -> None:
        with SessionLocal() as session:
            convite = session.get(ConviteRecord, convite_id)
            if convite is None:
                raise ValueError("Convite não encontrado.")
            if convite.destinatario_id != destinatario_id:
                raise ValueError("Este convite pertence a outro viajante.")
            if convite.status != "Pendente":
                raise ValueError("Este convite não está mais pendente.")

            grupo = session.get(GrupoRecord, convite.grupo_id)
            destinatario = session.get(ViajanteRecord, convite.destinatario_id)
            if grupo is None or destinatario is None:
                raise ValueError("Não foi possível aceitar o convite.")
            if destinatario not in grupo.integrantes:
                grupo.integrantes.append(destinatario)
            convite.status = "Aceito"
            session.commit()

    def rejeitar_convite(self, convite_id: int, destinatario_id: int) -> None:
        with SessionLocal() as session:
            convite = session.get(ConviteRecord, convite_id)
            if convite is None:
                raise ValueError("Convite não encontrado.")
            if convite.destinatario_id != destinatario_id:
                raise ValueError("Este convite pertence a outro viajante.")
            if convite.status != "Pendente":
                raise ValueError("Este convite não está mais pendente.")
            convite.status = "Rejeitado"
            session.commit()

    def listar_convites_pendentes(self, destinatario_id: int) -> list[ConviteRecord]:
        with SessionLocal() as session:
            convites = list(
                session.scalars(
                    select(ConviteRecord).where(
                        ConviteRecord.destinatario_id == destinatario_id,
                        ConviteRecord.status == "Pendente",
                    )
                )
            )
            for convite in convites:
                _ = convite.grupo
                _ = convite.remetente
            session.expunge_all()
            return convites
 
    def remover_integrante(
        self, grupo_id: int, viajante_id: int, organizador_id: int
    ) -> set[int]:
        with SessionLocal() as session:
            grupo = self._buscar_para_alteracao(session, grupo_id, organizador_id)
            if viajante_id == grupo.organizador_id:
                raise ValueError("O organizador não pode ser excluído do grupo.")
 
            viajante = session.get(ViajanteRecord, viajante_id)
            if viajante is None or viajante not in grupo.integrantes:
                raise ValueError("O viajante não faz parte deste grupo.")
 
            acompanhantes = [
                a for a in grupo.acompanhantes if a.viajante_id == viajante_id
            ]
            ids_removidos = {acompanhante.id for acompanhante in acompanhantes}
            for acompanhante in acompanhantes:
                grupo.acompanhantes.remove(acompanhante)
            grupo.integrantes.remove(viajante)
            session.commit()
            return ids_removidos

    def sair_do_grupo(self, grupo_id: int, viajante_id: int) -> set[int]:
        with SessionLocal() as session:
            grupo = session.get(GrupoRecord, grupo_id, with_for_update=True)
            if grupo is None:
                raise ValueError("Grupo não encontrado.")
            if grupo.organizador_id == viajante_id:
                raise ValueError("O organizador não pode sair do próprio grupo.")

            viajante = session.get(ViajanteRecord, viajante_id)
            if viajante is None or viajante not in grupo.integrantes:
                raise ValueError("Você não faz parte deste grupo.")

            acompanhantes = [
                acompanhante
                for acompanhante in grupo.acompanhantes
                if acompanhante.viajante_id == viajante_id
            ]
            ids_removidos = {acompanhante.id for acompanhante in acompanhantes}
            for acompanhante in acompanhantes:
                grupo.acompanhantes.remove(acompanhante)
            grupo.integrantes.remove(viajante)
            session.commit()
            return ids_removidos
 
    def listar_por_organizador(self, organizador_id: int) -> list[GrupoRecord]:
        with SessionLocal() as session:
            return list(
                session.scalars(
                    select(GrupoRecord)
                    .where(GrupoRecord.organizador_id == organizador_id)
                    .options(
                        selectinload(GrupoRecord.organizador),
                        selectinload(GrupoRecord.integrantes),
                        # selectinload busca organizador e integrantes e guarda no GrupoRecord antes da conexão com o banco fechar
                    )
                    .order_by(GrupoRecord.id)
                )
            )
            
    def listar_por_participante(self, viajante_id: int) -> list[GrupoRecord]:
        with SessionLocal() as session:
            return list(
                session.scalars(
                    select(GrupoRecord)
                    .join(GrupoRecord.integrantes)
                    .where(ViajanteRecord.id == viajante_id)
                    .options(
                        selectinload(GrupoRecord.organizador),
                        selectinload(GrupoRecord.integrantes),
                    )
                    .order_by(GrupoRecord.id)
                )
            )
