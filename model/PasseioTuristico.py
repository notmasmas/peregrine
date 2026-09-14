# Implementado por Maria Helena Melo

from datetime import date

from model import Cidade

class PasseioTuristico:
    def __init__(self,
            id: int,
            nome: str,
            cidade: Cidade,
            preco: float,
            data: date
    ):
        self._id = id
        self._nome = nome
        self._cidade = cidade
        self._preco = preco
        self._data = data
