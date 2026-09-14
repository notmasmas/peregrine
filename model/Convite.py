# Implementado por Sarah Meireles

from model.Viajante import Viajante
from model.StatusConvite import StatusConvite

class Convite:
    def __init__(
        self,
        destinatario: Viajante,
        remetente: Viajante,
        id: int | None = None,
        status: StatusConvite = StatusConvite.PENDENTE,
    ):
        self._id = id
        self._destinatario = destinatario
        self._remetente = remetente
        self._status = status