class Grupo:
    def __init__(
        self,
        acompanhantes: list["Acompanhante"] = None,
        id: int = None,
        integrantes: list["Viajante"] = None,
        itinerario: "Itinerario" = None,
        organizador: "Viajante" = None,
    ):
        self.acompanhantes = acompanhantes if acompanhantes is not None else []
        self.id = id
        self.integrantes = integrantes if integrantes is not None else []
        self.itinerario = itinerario
        self.organizador = organizador
