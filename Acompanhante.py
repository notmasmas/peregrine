class Acompanhante:
    def __init__(
      self, 
      id: int, 
      nome: str, 
      viajante_vinculado: "Viajante" = None
    ):
        self.id = id
        self.nome = nome
        self.viajante_vinculado = viajante_vinculado
