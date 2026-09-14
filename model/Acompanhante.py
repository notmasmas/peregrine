# Implementado por Gustavo de Pinho

from model.Viajante import Viajante

class Acompanhante:
    def __init__(
      self, 
      id: int, 
      nome: str, 
      viajante_vinculado: Viajante = None
    ):
        self._id = id
        self._nome = nome
        self._viajante_vinculado = viajante_vinculado
