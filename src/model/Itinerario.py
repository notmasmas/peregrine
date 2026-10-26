# Implementado por Maria Helena Melo
# Correção da Entrega 2: Adicionado return type hint
# Correção da Entrega 2: Consertando importação circular

# Os imports atuais são utilizados apenas para type hinting
# Então eles são importados dentro de um bloco TYPE_CHECKING para evitar problemas de importação circular.
from __future__ import annotations
from typing import TYPE_CHECKING

from datetime import date

if TYPE_CHECKING:
    from src.model.Grupo import Grupo
    from src.model.Reserva import Reserva


class Itinerario:
    def __init__(self,
            id: int,
            grupo: Grupo,
            programacao: dict = {},
            reservas: list[Reserva] = [],
            data_inicial: date = None,
            valor_total: float = 0.0
    ) -> None:
        self._id = id
        self._grupo = grupo
        self._programacao = programacao
        self._reservas = reservas
        self._data_inicial = data_inicial
        self._valor_total = valor_total
