from acompanhante import Acompanhante
from grupo import Grupo
 
 
class Viajante:
    def __init__(
        self,
        acompanhantes: list["Acompanhante"] = None,
        email: str = "",
        grupos_organizador: list["Grupo"] = None,
        grupos_participante: list["Grupo"] = None,
        id: int = None,
        senha: str = "",
    ):
        self.acompanhantes = acompanhantes if acompanhantes is not None else []
        self.email = email
        self.grupos_organizador = grupos_organizador if grupos_organizador is not None else []
        self.grupos_participante = grupos_participante if grupos_participante is not None else []
        self.id = id
        self.senha = senha
