# Implementado por Gustavo de Pinho
# Correção da Entrega 2: Adicionado return type hint
# Correção da Entrega 2: Consertando importação circular

# Os imports atuais são utilizados apenas para type hinting
# Então eles são importados dentro de um bloco TYPE_CHECKING para evitar problemas de importação circular.
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.model.Viajante import Viajante

class Acompanhante:
    def __init__(
      self,
      id: int | None = None,
      nome: str = "",
      viajante_vinculado: Viajante | None = None,
    ) -> None:
        self._id = id
        self._nome = nome
        self._viajante_vinculado = viajante_vinculado

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
    def viajante_vinculado(self) -> Viajante | None:
        return self._viajante_vinculado
