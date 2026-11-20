import tkinter as tk
from src.control.ViajanteController import ViajanteController
from src.view.InicioView import InicioView


class InicioController:
    def __init__(self, root: tk.Tk) -> None:
        self._viajante_controller = ViajanteController()
        self._tela = InicioView(
            root,
            ao_entrar=self._entrar,
            ao_cadastrar=self._cadastrar,
            ao_sair=root.destroy,
        )

    def _entrar(self, credenciais: dict[str, str]) -> None:
        viajante = self._viajante_controller.validar_credenciais(credenciais)

        if viajante is None:
            self._tela.mostrar_erro("Credenciais inválidas.")
            return

        self._tela.mostrar_sessao(viajante.nome)

    def _cadastrar(self, dados: dict[str, str]) -> None:
        erro = self._viajante_controller.cadastrar_viajante(dados)
        if erro is not None:
            self._tela.mostrar_erro(erro)
            return

        self._tela.mostrar_sucesso("Cadastro realizado com sucesso.")
        self._tela.mostrar_login()