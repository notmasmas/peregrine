# Implementado por Maria Helena Melo
# Correção da Entrega 2: Adicionado return type hint
# Correção da Entrega 2: Consertando importação circular

# Os imports atuais são utilizados apenas para type hinting
# Então eles são importados dentro de um bloco TYPE_CHECKING para evitar problemas de importação circular.
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.model.Grupo import Grupo
    from src.model.Itinerario import Itinerario


class Relatorio:
    def __init__(self,
            id: int,
            grupo: Grupo,
            itinerario: Itinerario,
            gastos: dict = {}
    ) -> None:

        self._id = id
        self._grupo = grupo
        self._itinerario = itinerario
        self._gastos = gastos