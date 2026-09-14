# Implementado por Maria Helena Melo


from model import Grupo, Itinerario


class Relatorio:
    def __init__(self,
            id: int,
            grupo: Grupo,
            itinerario: Itinerario,
            gastos: dict = {}
    ):

        self._id = id
        self._grupo = grupo
        self._itinerario = itinerario
        self._gastos = gastos