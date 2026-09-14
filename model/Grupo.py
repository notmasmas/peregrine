# Implementado por Gustavo de Pinho

from model.Acompanhante import Acompanhante
from model.Viajante import Viajante
from model.Itinerario import Itinerario

class Grupo:
    def __init__(
        self,
        id: int = None,
        organizador: Viajante = None,
        integrantes: list[Viajante] = None,
        acompanhantes: list[Acompanhante] = None,
        itinerario: Itinerario = None,
    ):
        self._id = id
        self._organizador = organizador
        self._integrantes = integrantes if integrantes is not None else []
        self._acompanhantes = acompanhantes if acompanhantes is not None else []
        self._itinerario = itinerario
