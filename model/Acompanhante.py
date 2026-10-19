# Implementado por Gustavo de Pinho
# Correção da Entrega 2: Adicionado return type hint
# Correção da Entrega 2: Consertando importação circular

# Os imports atuais são utilizados apenas para type hinting
# Então eles são importados dentro de um bloco TYPE_CHECKING para evitar problemas de importação circular.
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from model.Viajante import Viajante

class Acompanhante:
    def __init__(
      self, 
      id: int, 
      nome: str, 
      viajante_vinculado: Viajante = None
    ) -> None:
        self._id = id
        self._nome = nome
        self._viajante_vinculado = viajante_vinculado
