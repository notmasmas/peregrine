from exception.CampoInvalidoException import CampoInvalidoException
from model.Grupo import Grupo
from model.Viajante import Viajante
from view.ViajanteView import ViajanteView
from email_validator import validate_email, EmailNotValidError

class ViajanteController:

    def __init__(self, viajante: Viajante) -> None:
        self.__viajante = viajante
        #self.__viajanteDAO
        #self.__grupoDAO
        self.__tela = ViajanteView()

    def criar_grupo(self) -> None:
        dados = self.__tela.cria_grupo()

        try:
            if len(dados["nome"]) == 0 or len(dados["nome"]) > 20:
                raise CampoInvalidoException("Nome de grupo inválido")

            if len(dados["participantes"]) == 0:
                raise CampoInvalidoException("Deve conter no mínimo um e-mail válido")

            for email in dados["participantes"]:
                validate_email(email)

            grupo = Grupo(nome=dados["nome"],
                          organizador=self.__viajante)  # vou criar no BD depois usando o DAO to com sono agora

            self.__viajante.grupos_organizador.append(grupo)

        except EmailNotValidError:
            self.__tela.mostra_mensagem("Deve conter no mínimo um e-mail válido")
            return

        except CampoInvalidoException as e:
            self.__tela.mostra_mensagem(str(e))