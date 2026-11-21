import tkinter as tk
from collections.abc import Callable

from sqlalchemy.exc import SQLAlchemyError

from src.DAOs.AcompanhanteDAO import AcompanhanteDAO
from src.control.ViajanteController import ViajanteController
from src.exception.CampoInvalidoException import CampoInvalidoException
from src.model.Acompanhante import Acompanhante
from src.model.Viajante import Viajante
from src.view.AcompanhanteView import AcompanhanteView


class AcompanhanteController:

    def __init__(
            self,
            root: tk.Tk,
            viajante_responsavel: Viajante,
            ao_sair: Callable[[], None],
        ) -> None:
        self._root = root
        self._ao_sair = ao_sair
        self._viajante_responsavel = viajante_responsavel
        self._acompanhante_dao = AcompanhanteDAO()
        self._viajante_controller = ViajanteController()
        self._tela = AcompanhanteView(
            root,
            viajante_responsavel,
            ao_vincular_acompanhante=self.vincular_acompanhante,
            ao_sair=self._voltar_inicio)
        try:
            self._tela.atualizar_acompanhantes(self.listar_acompanhantes())
        except (SQLAlchemyError, ValueError) as erro:
            self._tela.mostrar_erro(
                f"Não foi possível carregar os acompanhantes: {erro}"
            )

    def listar_acompanhantes(self) -> list[Acompanhante]:
        if self._viajante_responsavel.id is None:
            raise ValueError("O viajante responsável não está cadastrado.")

        acompanhantes = self._acompanhante_dao.listar_por_viajante_id(
            self._viajante_responsavel.id
        )
        self._viajante_responsavel.acompanhantes[:] = acompanhantes
        return acompanhantes

    def vincular_acompanhante(self, dados: dict[str, str]) -> bool:
        nome = dados.get("nome", "").strip()
        try:
            if not nome or len(nome) > 150:
                raise CampoInvalidoException(
                    "Informe um nome com até 150 caracteres."
                )
            if not self._viajante_controller.viajante_existe(
                self._viajante_responsavel
            ):
                raise CampoInvalidoException(
                    "O viajante responsável não está cadastrado."
                )

            acompanhante = Acompanhante(
                nome=nome,
                viajante_vinculado=self._viajante_responsavel,
            )
            self._acompanhante_dao.criar(acompanhante)
            self._viajante_responsavel.acompanhantes.append(acompanhante)
        except CampoInvalidoException as erro:
            self._tela.mostrar_erro(str(erro))
            return False
        except (SQLAlchemyError, ValueError) as erro:
            self._tela.mostrar_erro(
                f"Não foi possível vincular o acompanhante: {erro}"
            )
            return False

        self._tela.mostrar_sucesso("Acompanhante vinculado com sucesso.")
        return True

    def _voltar_inicio(self) -> None:
        self._tela.destroy()
        self._ao_sair()
