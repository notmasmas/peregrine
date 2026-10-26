from src.exception.CampoInvalidoException import CampoInvalidoException
from src.DAOs.GrupoDAO import GrupoDAO
from src.model.Grupo import Grupo
from src.model.Viajante import Viajante
from src.view.GrupoView import GrupoView
from email_validator import validate_email, EmailNotValidError

class GrupoController:

    def __init__(
        self,
        organizador: Viajante,
    ) -> None:
        self._organizador = organizador
        self._grupo_dao = GrupoDAO()
        self._tela = GrupoView()

    def criar_grupo(self) -> None:
        dados = self._tela.cria_grupo()

        try:
            if len(dados["nome"]) == 0 or len(dados["nome"]) > 20:
                raise CampoInvalidoException("Nome de grupo inválido")

            if len(dados["participantes"]) == 0:
                raise CampoInvalidoException("Deve conter no mínimo um e-mail válido")

            for email in dados["participantes"]:
                validate_email(email)

            grupo = Grupo(nome=dados["nome"],
                          organizador=self._organizador)

            self._grupo_dao.criar(grupo)
            self._organizador.grupos_organizador.append(grupo)

        except EmailNotValidError:
            self._tela.mostra_mensagem("Deve conter no mínimo um e-mail válido")
            return

        except ValueError as e:
            self._tela.mostra_mensagem(str(e))
            return

        except CampoInvalidoException as e:
            self._tela.mostra_mensagem(str(e))