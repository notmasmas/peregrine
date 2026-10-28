# Implementado por Gustavo de Pinho
# Correção da Entrega 2: Adicionado return type hint
# Correção da Entrega 2: Consertando importação circular

# Os imports atuais são utilizados apenas para type hinting
# Então eles são importados dentro de um bloco TYPE_CHECKING para evitar problemas de importação circular.
from __future__ import annotations
from typing import TYPE_CHECKING
from datetime import date

if TYPE_CHECKING:
    from src.model.Acompanhante import Acompanhante
    from src.model.Grupo import Grupo

class Viajante:
    def __init__(
        self,
        id: int = None,
        nome: str = "",
        data_nascimento: date = None,
        email: str = "",
        senha: str = "",
        acompanhantes: list[Acompanhante] = None,
        grupos_organizador: list[Grupo] = None,
        grupos_participante: list[Grupo] = None,
    ) -> None:
        self._id = id
        self._nome = nome
        self._data_nascimento = data_nascimento
        self.__email = email
        self.__senha = senha
        self._acompanhantes = acompanhantes if acompanhantes is not None else []
        self._grupos_organizador = grupos_organizador if grupos_organizador is not None else []
        self._grupos_participante = grupos_participante if grupos_participante is not None else []

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @property
    def nome(self):
        return self._nome

    @property
    def data_nascimento(self):
        return self._data_nascimento

    @property
    def email(self):
        return self.__email

    @property
    def senha(self):
        return self.__senha

    @property
    def acompanhantes(self):
        return self._acompanhantes

    @property
    def grupos_organizador(self):
        return self._grupos_organizador

    @property
    def grupos_participante(self):
        return self._grupos_participante


