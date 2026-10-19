# Implementado por Gustavo de Pinho
# Correção da Entrega 2: Adicionado return type hint
# Correção da Entrega 2: Consertando importação circular

# Os imports atuais são utilizados apenas para type hinting
# Então eles são importados dentro de um bloco TYPE_CHECKING para evitar problemas de importação circular.
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from model.Acompanhante import Acompanhante
    from model.Itinerario import Itinerario
    from model.Viajante import Viajante

class Grupo:
    def __init__(
        self,
        id: int = None,
        nome: str = "",
        organizador: Viajante = None,
        integrantes: list[Viajante] = None,
        acompanhantes: list[Acompanhante] = None,
        itinerario: Itinerario = None,
        sugestoes: dict = {}
    ) -> None:
        self._id = id
        self._nome = nome
        self._organizador = organizador
        self._integrantes = integrantes if integrantes is not None else []
        self._acompanhantes = acompanhantes if acompanhantes is not None else []
        self._itinerario = itinerario
        self._sugestoes = sugestoes
