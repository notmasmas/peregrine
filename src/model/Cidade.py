# Implementado por Sarah Meireles
# Correção da Entrega 2: Adicionado return type hint
# Correção da Entrega 2: Consertando importação circular

# Os imports atuais são utilizados apenas para type hinting
# Então eles são importados dentro de um bloco TYPE_CHECKING para evitar problemas de importação circular.
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.model.PasseioTuristico import PasseioTuristico

class Cidade:
    def __init__(
        self,
        id: int | None = None,
        nome: str = "",
        passeios: list[PasseioTuristico] | None = None,
    ) -> None:
        self._id = id
        self._nome = nome
        self._passeios = passeios if passeios is not None else []