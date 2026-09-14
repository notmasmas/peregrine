# Implementado por Gustavo de Pinho

from model.Acompanhante import Acompanhante
from model.Grupo import Grupo

class Viajante:
    def __init__(
        self,
        id: int = None,
        nome: str = "",
        email: str = "",
        senha: str = "",
        acompanhantes: list[Acompanhante] = None,
        grupos_organizador: list[Grupo] = None,
        grupos_participante: list[Grupo] = None,
    ):
        self._id = id
        self._nome = nome
        self.__email = email
        self.__senha = senha
        self._acompanhantes = acompanhantes if acompanhantes is not None else []
        self._grupos_organizador = grupos_organizador if grupos_organizador is not None else []
        self._grupos_participante = grupos_participante if grupos_participante is not None else []
