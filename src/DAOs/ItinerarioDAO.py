from datetime import date
import math

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.database import SessionLocal
from src.persistence.models import (
    GrupoRecord,
    ItinerarioRecord,
    ReservaRecord,
)


class ItinerarioDAO:
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
            grupo = session.scalar(
                select(GrupoRecord)
                .where(GrupoRecord.id == grupo_id)
                .options(selectinload(GrupoRecord.integrantes))
            )
            if grupo is None:
                raise ValueError("Grupo não encontrado.")
            if grupo.organizador_id != viajante_id:
                raise ValueError(
                    "Apenas o dono do grupo pode adicionar dias ao itinerário."
                )

            titulares_validos = {integrante.id for integrante in grupo.integrantes}
            if grupo.organizador_id is not None:
                titulares_validos.add(grupo.organizador_id)

            for nome, preco, titular_id in reservas:
                if not nome.strip():
                    raise ValueError("Informe o nome de todas as reservas.")
                if not math.isfinite(preco) or preco < 0:
                    raise ValueError("Informe um preço válido para cada reserva.")
                if titular_id not in titulares_validos:
                    raise ValueError(
                        "O titular da reserva deve ser um participante do grupo."
                    )

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
            itinerario.valor_total += sum(preco for _, preco, _ in reservas)

            for nome, preco, titular_id in reservas:
                session.add(
                    ReservaRecord(
                        nome=nome,
                        preco=preco,
                        titular_id=titular_id,
                        itinerario_id=itinerario.id,
                    )
                )

            session.commit()

    def editar_dia(
        self,
        grupo_id: int,
        data_original: date,
        data_nova: date,
        cidade: str,
        passeio: str,
        reservas: list[tuple[str, float, int]],
    ) -> None:
        with SessionLocal() as session:
            grupo = session.scalar(
                select(GrupoRecord)
                .where(GrupoRecord.id == grupo_id)
                .options(selectinload(GrupoRecord.integrantes))
            )
            if grupo is None:
                raise ValueError("Grupo não encontrado.")

            titulares_validos = {integrante.id for integrante in grupo.integrantes}
            if grupo.organizador_id is not None:
                titulares_validos.add(grupo.organizador_id)
            for nome, preco, titular_id in reservas:
                if not nome.strip():
                    raise ValueError("Informe o nome de todas as reservas.")
                if not math.isfinite(preco) or preco < 0:
                    raise ValueError("Informe um preço válido para cada reserva.")
                if titular_id not in titulares_validos:
                    raise ValueError(
                        "O titular da reserva deve ser um participante do grupo."
                    )

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
            itinerario.valor_total += sum(preco for _, preco, _ in reservas)

            for nome, preco, titular_id in reservas:
                session.add(
                    ReservaRecord(
                        nome=nome,
                        preco=preco,
                        titular_id=titular_id,
                        itinerario_id=itinerario.id,
                    )
                )

            session.commit()

    def remover_dias(self, grupo_id: int, datas: set[date]) -> None:
        with SessionLocal() as session:
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
            session.commit()
