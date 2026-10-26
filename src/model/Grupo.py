# Implementado por Gustavo de Pinho
# Correção da Entrega 2: Adicionado return type hint
# Correção da Entrega 2: Consertando importação circular

# Os imports atuais são utilizados apenas para type hinting
# Então eles são importados dentro de um bloco TYPE_CHECKING para evitar problemas de importação circular.
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.model.Acompanhante import Acompanhante
    from src.model.Itinerario import Itinerario
    from src.model.Viajante import Viajante

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

    @property
    def id(self) -> int | None:
        return self._id

    @id.setter
    def id(self, value: int | None) -> None:
        self._id = value

    @property
    def nome(self) -> str:
        return self._nome

    @property
    def organizador(self) -> Viajante | None:
        return self._organizador

    @property
    def integrantes(self) -> list[Viajante]:
        return self._integrantes

    @property
    def acompanhantes(self) -> list[Acompanhante]:
        return self._acompanhantes

    @property
    def itinerario(self) -> Itinerario | None:
        return self._itinerario

    @property
    def sugestoes(self) -> dict:
        return self._sugestoes
