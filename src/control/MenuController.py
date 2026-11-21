import tkinter as tk
from collections.abc import Callable
from src.model.Viajante import Viajante
from src.view.MenuView import MenuView


class MenuController:

    def __init__(
        self,
        root: tk.Tk,
        viajante: Viajante,
        ao_sair: Callable[[], None],
    ) -> None:
        self._root = root
        self._viajante_logado: Viajante = viajante
        self._ao_sair = ao_sair
        self._tela = MenuView(
            root,
            nome_viajante=viajante.nome,
            ao_criar_grupo=self._abrir_criacao,
            ao_selecionar_grupo_para_gerenciar=self._abrir_grupos,
            ao_sair=self._voltar_inicio,
        )

    def _voltar_inicio(self) -> None:
        self._tela.destroy()
        self._ao_sair()

    def _abrir_criacao(self) -> None:
        pass

    def _abrir_grupos(self) -> None:
        pass
