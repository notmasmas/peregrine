# Implementado por Maria Helena Melo
# Correção da Entrega 2: Adicionado return type hint
# Correção da Entrega 2: Consertando importação circular

# Os imports atuais são utilizados apenas para type hinting
# Então eles são importados dentro de um bloco TYPE_CHECKING para evitar problemas de importação circular.
from __future__ import annotations
from typing import TYPE_CHECKING

from datetime import date

if TYPE_CHECKING:
    from src.model.Cidade import Cidade

class PasseioTuristico:
    def __init__(self,
            id: int,
            nome: str,
            cidade: Cidade,
            preco: float,
            data: date
    ) -> None:
        self._id = id
        self._nome = nome
        self._cidade = cidade
        self._preco = preco
        self._data = data
