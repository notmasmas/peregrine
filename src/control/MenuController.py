from src.control.GrupoController import GrupoController
from src.model.Viajante import Viajante
from src.view.MenuView import MenuView


class MenuController:

    def __init__(self, viajante: Viajante) -> None:
        self._viajante = viajante
        self._grupo_controller = GrupoController(viajante)
        self._tela = MenuView()

    def iniciar(self) -> None:
        while True:
            opcao = self._tela.exibe_menu_principal()

            if opcao == "1":
                self._grupo_controller.criar_grupo()
            elif opcao == "2":
                self._grupo_controller.selecionar_grupo_para_gerenciar()
            elif opcao == "0":
                return
            else:
                self._tela.mostra_mensagem("Opção inválida.")