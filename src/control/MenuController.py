import tkinter as tk
from typing import Optional
from collections.abc import Callable
from src.model.Viajante import Viajante
from src.view.MenuView import MenuView
from src.control.AcompanhanteController import AcompanhanteController
from src.control.GrupoController import GrupoController


class MenuController:

    def __init__(
        self,
        root: tk.Tk,
        viajante: Viajante,
        ao_sair: Callable[[], None],
    ) -> None:
        self._root = root
        self._viajante_logado: Viajante = viajante
        self._acompanhante_controller: Optional[AcompanhanteController]= None
        self._grupo_controller = GrupoController(viajante)
        self._ao_sair = ao_sair
        self._tela = MenuView(
            root,
            nome_viajante=viajante.nome,
            ao_criar_grupo=self._criar_grupo,
            ao_selecionar_grupo_para_gerenciar=self._abrir_grupos,
            ao_abrir_acompanhante=self._abrir_acompanhante,
            ao_sair=self._sair_do_menu,
        )

    def _abrir_acompanhante(self) -> None:
        viajante = self._viajante_logado
        if viajante is None:
            self._tela.mostrar_erro("Faça login antes de abrir a tela de acompanhantes.")
            return

        self._acompanhante_controller = AcompanhanteController(
            self._root, viajante, ao_sair=self._voltar_ao_menu
        )
        self._tela.pack_forget()

    def _voltar_ao_menu(self) -> None:
        self._acompanhante_controller = None
        self._tela.pack(fill=tk.BOTH, expand=True)
        self._tela.mostrar_inicio()

    def _sair_do_menu(self) -> None:
        self._tela.destroy()
        self._ao_sair()

    def _criar_grupo(self, nome: str, participantes: list[str]) -> bool:
        return self._grupo_controller.criar_grupo(
            {"nome": nome, "participantes": participantes},
            mostrar_erro=self._tela.mostrar_erro,
            mostrar_sucesso=self._tela.mostrar_sucesso,
        )

    def _abrir_grupos(self) -> None:
        pass
