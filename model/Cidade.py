# Implementado por Sarah Meireles

from model.PasseioTuristico import PasseioTuristico

class Cidade:
    def __init__(
        self,
        id: int | None = None,
        nome: str = "",
        passeios: list[PasseioTuristico] | None = None,
    ):
        self._id = id
        self._nome = nome
        self._passeios = passeios if passeios is not None else []