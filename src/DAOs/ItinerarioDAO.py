from datetime import date
import math

from sqlalchemy import select, delete, func
from sqlalchemy.orm import Session

from src.database import SessionLocal
from src.persistence.models import (
    GrupoRecord,
    ItinerarioRecord,
    ReservaRecord,
)


class ItinerarioDAO:
    @staticmethod
    def _buscar_grupo(
        session: Session, grupo_id: int, *, bloquear: bool = False
    ) -> GrupoRecord:
        grupo = session.get(GrupoRecord, grupo_id, with_for_update=bloquear)
        if grupo is None:
            raise ValueError("Grupo não encontrado.")
        return grupo

    def _buscar_grupo_do_organizador(
        self, session: Session, grupo_id: int, viajante_id: int, *, bloquear: bool = False
    ) -> GrupoRecord:
        grupo = self._buscar_grupo(session, grupo_id, bloquear=bloquear)
        if viajante_id is None or grupo.organizador_id != viajante_id:
            raise ValueError("Apenas o organizador pode realizar esta ação.")
        return grupo

    def listar_programacao(self, grupo_id: int) -> dict:
        with SessionLocal() as session:
            itinerario = session.scalar(
                select(ItinerarioRecord).where(
                    ItinerarioRecord.grupo_id == grupo_id
                )
            )
            if itinerario is None:
                return {}
            programacao = itinerario.programacao
            if not isinstance(programacao, dict):
                raise ValueError("A programação do itinerário está inválida.")
            return dict(programacao)

    def adicionar_dia(
        self,
        grupo_id: int,
        viajante_id: int,
        data: date,
        cidade: str,
        passeio: str,
        reservas: list[tuple[str, float, int]],
    ) -> None:
        with SessionLocal() as session:
            grupo = self._buscar_grupo_do_organizador(
                session, grupo_id, viajante_id, bloquear=True
            )
            self._validar_reservas(grupo, reservas)

            itinerario = session.scalar(
                select(ItinerarioRecord)
                .where(ItinerarioRecord.grupo_id == grupo_id)
                .with_for_update()
            )
            if itinerario is None:
                itinerario = ItinerarioRecord(grupo_id=grupo_id)
                session.add(itinerario)
                session.flush()

            if not isinstance(itinerario.programacao, dict):
                raise ValueError("A programação do itinerário está inválida.")
            programacao = dict(itinerario.programacao)
            data_iso = data.isoformat()
            if data_iso in programacao:
                raise ValueError("Já existe um dia cadastrado para esta data.")

            programacao[data_iso] = {"cidade": cidade, "passeio": passeio}
            itinerario.programacao = programacao
            if itinerario.data_inicial is None or data < itinerario.data_inicial:
                itinerario.data_inicial = data

            for nome, preco, titular_id in reservas:
                session.add(
                    ReservaRecord(
                        nome=nome,
                        preco=preco,
                        titular_id=titular_id,
                        itinerario_id=itinerario.id,
                        data=data,
                    )
                )
            self._recalcular_total(session, itinerario)
            session.commit()

    def editar_dia(
        self,
        grupo_id: int,
        viajante_id: int,
        data_original: date,
        data_nova: date,
        cidade: str,
        passeio: str,
        reservas: list[tuple[str, float, int]],
    ) -> None:
        with SessionLocal() as session:
            grupo = self._buscar_grupo_do_organizador(
                session, grupo_id, viajante_id, bloquear=True
            )
            self._validar_reservas(grupo, reservas)

            itinerario = session.scalar(
                select(ItinerarioRecord)
                .where(ItinerarioRecord.grupo_id == grupo_id)
                .with_for_update()
            )
            if itinerario is None or not isinstance(itinerario.programacao, dict):
                raise ValueError("Itinerário não encontrado.")

            programacao = dict(itinerario.programacao)
            data_original_iso = data_original.isoformat()
            data_nova_iso = data_nova.isoformat()
            detalhes = programacao.get(data_original_iso)
            if not isinstance(detalhes, dict):
                raise ValueError("O dia selecionado não foi encontrado.")
            if data_nova_iso != data_original_iso and data_nova_iso in programacao:
                raise ValueError("Já existe um dia cadastrado para esta data.")

            del programacao[data_original_iso]
            programacao[data_nova_iso] = {
                **detalhes,
                "cidade": cidade,
                "passeio": passeio,
            }
            itinerario.programacao = programacao
            itinerario.data_inicial = min(
                date.fromisoformat(data) for data in programacao
            )
            
            session.execute(
                delete(ReservaRecord).where(
                    ReservaRecord.itinerario_id == itinerario.id,
                    ReservaRecord.data == data_original,
                )
            )

            for nome, preco, titular_id in reservas:
                session.add(
                    ReservaRecord(
                        nome=nome,
                        preco=preco,
                        titular_id=titular_id,
                        itinerario_id=itinerario.id,
                        data=data_nova,
                    )
                )
            self._recalcular_total(session, itinerario)
            session.commit()

    def remover_dias(
        self, grupo_id: int, viajante_id: int, datas: set[date]
    ) -> None:
        with SessionLocal() as session:
            self._buscar_grupo_do_organizador(
                session, grupo_id, viajante_id, bloquear=True
            )
            itinerario = session.scalar(
                select(ItinerarioRecord)
                .where(ItinerarioRecord.grupo_id == grupo_id)
                .with_for_update()
            )
            if itinerario is None:
                raise ValueError("Itinerário não encontrado.")
            if not isinstance(itinerario.programacao, dict):
                raise ValueError("A programação do itinerário está inválida.")

            programacao = dict(itinerario.programacao)
            datas_iso = {data.isoformat() for data in datas}
            if not datas_iso.issubset(programacao):
                raise ValueError("Um dos dias selecionados não foi encontrado.")
            for data in datas_iso:
                del programacao[data]

            itinerario.programacao = programacao
            itinerario.data_inicial = (
                min(date.fromisoformat(data) for data in programacao)
                if programacao
                else None
            )
            
            session.execute(
                delete(ReservaRecord).where(
                    ReservaRecord.itinerario_id == itinerario.id,
                    ReservaRecord.data.in_(datas),
                )
            )
            self._recalcular_total(session, itinerario)
            session.commit()

    def sugerir_dia(
        self,
        grupo_id: int,
        viajante_id: int,
        data: date,
        cidade: str,
        passeio: str,
        reservas: list[tuple[str, float, int]],
    ) -> None:
        with SessionLocal() as session:
            grupo = self._buscar_grupo(session, grupo_id, bloquear=True)
            autor = next(
                (membro for membro in grupo.integrantes if membro.id == viajante_id), None
            )
            if autor is None or grupo.organizador_id == viajante_id:
                raise ValueError("Apenas participantes do grupo podem enviar sugestões.")

            titulares = self._validar_reservas(grupo, reservas)
            sugestao = {
                "autor": autor.nome,
                "data": data.isoformat(),
                "cidade": cidade,
                "passeio": passeio,
                "reservas": [
                    {"nome": nome, "preco": preco, "titular": titulares[titular_id]}
                    for nome, preco, titular_id in reservas
                ],
            }
            sugestoes = self._sugestoes_itinerario(grupo)
            grupo.sugestoes = {
                **(grupo.sugestoes or {}),
                "itinerario": [*sugestoes, sugestao],
            }
            session.commit()

    def listar_sugestoes(self, grupo_id: int, viajante_id: int) -> list[dict]:
        with SessionLocal() as session:
            grupo = self._buscar_grupo_do_organizador(session, grupo_id, viajante_id)
            return list(reversed(self._sugestoes_itinerario(grupo)))

    @staticmethod
    def _sugestoes_itinerario(grupo: GrupoRecord) -> list[dict]:
        sugestoes = grupo.sugestoes or {}
        if not isinstance(sugestoes, dict):
            raise ValueError("As sugestões do grupo estão inválidas.")
        itinerarios = sugestoes.get("itinerario", [])
        if not isinstance(itinerarios, list):
            raise ValueError("As sugestões de itinerário estão inválidas.")
        return itinerarios

    @staticmethod
    def _validar_reservas(
        grupo: GrupoRecord, reservas: list[tuple[str, float, int]]
    ) -> dict[int, str]:
        if not reservas:
            return {}

        titulares = {integrante.id: integrante.nome for integrante in grupo.integrantes}
        if grupo.organizador is not None:
            titulares[grupo.organizador.id] = grupo.organizador.nome
        for nome, preco, titular_id in reservas:
            if not nome.strip():
                raise ValueError("Informe o nome de todas as reservas.")
            if not math.isfinite(preco) or preco < 0:
                raise ValueError("Informe um preço válido para cada reserva.")
            if titular_id not in titulares:
                raise ValueError("O titular da reserva deve ser um participante do grupo.")
        return titulares
            
    # UC14: Dividir custos da viagem entre membros do grupo (Implementado por Sarah Meireles)
    @staticmethod
    def _recalcular_total(session, itinerario: ItinerarioRecord) -> None:
        session.flush() # enviar comandos SQL pendentes para o banco
        itinerario.valor_total = session.scalar(
            select(func.coalesce(func.sum(ReservaRecord.preco), 0.0)).where(
                ReservaRecord.itinerario_id == itinerario.id
            )
        )
    
    def listar_reservas_por_dia(self, grupo_id: int) -> dict[str, list[dict]]:
        with SessionLocal() as session:
            reservas = session.scalars(
                select(ReservaRecord)
                .join(ItinerarioRecord, ReservaRecord.itinerario_id == ItinerarioRecord.id)
                .where(
                    ItinerarioRecord.grupo_id == grupo_id,
                    ReservaRecord.data.is_not(None)
                )
                .order_by(ReservaRecord.id)
            )
            resultado: dict[str, list[dict]] = {}
            for reserva in reservas:
                resultado.setdefault(reserva.data.isoformat(), []).append(
                    {
                        "nome": reserva.nome,
                        "preco": reserva.preco,
                        "titular_id": reserva.titular_id,
                    }
                )
            return resultado
