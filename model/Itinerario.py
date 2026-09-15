# Implementado por Maria Helena Melo

from datetime import date

from Grupo import Grupo
from Reserva import Reserva


class Itinerario:
    def __init__(self,
            id: int,
            grupo: Grupo,
            programacao: dict = {},
            reservas: list[Reserva] = [],
            data_inicial: date = None,
            valor_total: float = 0.0
    ):
        self._id = id
        self._grupo = grupo
        self._programacao = programacao
        self._reservas = reservas
        self._data_inicial = data_inicial
        self._valor_total = valor_total
