# Implementado por Sarah Meireles

from model.Viajante import Viajante

class Reserva:
    def __init__(
        self,
        titular: Viajante,
        id: int | None = None,
        nome: str = "",
        preco: float = 0.0,
    ):
        self._id = id
        self._nome = nome
        self._preco = preco
        self._titular = titular