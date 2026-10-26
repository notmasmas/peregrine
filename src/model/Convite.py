# Implementado por Sarah Meireles
# Correção da Entrega 2: Adicionado return type hint
# Correção da Entrega 2: Consertando importação circular

# Os imports atuais são utilizados apenas para type hinting
# Então eles são importados dentro de um bloco TYPE_CHECKING para evitar problemas de importação circular.
from __future__ import annotations
from typing import TYPE_CHECKING
from src.model.StatusConvite import StatusConvite

if TYPE_CHECKING:
    from src.model.Viajante import Viajante

class Convite:
    def __init__(
        self,
        destinatario: Viajante,
        remetente: Viajante,
        id: int | None = None,
        status: StatusConvite = StatusConvite.PENDENTE,
    ) -> None:
        self._id = id
        self._destinatario = destinatario
        self._remetente = remetente
        self._status = status