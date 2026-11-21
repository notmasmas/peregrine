# Implementado por Sarah Meireles
# Correção da Entrega 2: Adicionado return type hint
# Correção da Entrega 2: Consertando importação circular

# Os imports atuais são utilizados apenas para type hinting
# Então eles são importados dentro de um bloco TYPE_CHECKING para evitar problemas de importação circular.
from __future__ import annotations
from typing import TYPE_CHECKING
from src.model.StatusConvite import StatusConvite

if TYPE_CHECKING:
    from src.model.Grupo import Grupo
    from src.model.Viajante import Viajante

class Convite:
    def __init__(
        self,
        destinatario: Viajante,
        remetente: Viajante,
        id: int | None = None,
        status: StatusConvite = StatusConvite.PENDENTE,
        grupo: Grupo | None = None,
    ) -> None:
        self._id = id
        self._destinatario = destinatario
        self._remetente = remetente
        self._status = status
        self._grupo = grupo

    @property
    def id(self) -> int | None:
        return self._id

    @property
    def destinatario(self) -> Viajante:
        return self._destinatario

    @property
    def remetente(self) -> Viajante:
        return self._remetente

    @property
    def status(self) -> StatusConvite:
        return self._status

    @property
    def grupo(self) -> Grupo | None:
        return self._grupo

    def aceitar(self) -> None:
        self._status = StatusConvite.ACEITO

    def rejeitar(self) -> None:
        self._status = StatusConvite.REJEITADO