from src.control.MenuController import MenuController
from src.control.ViajanteController import ViajanteController
from src.view.InicioView import InicioView
from src.DAOs.ViajanteDAO import ViajanteDAO
from src.model.Viajante import Viajante


class InicioController:

    def __init__(self) -> None:
        self._viajante_dao = ViajanteDAO()
        self._viajante_controller = ViajanteController()
        self._tela = InicioView()

    def iniciar(self) -> None:
        while True:
            opcao = self._tela.exibe_menu_inicial()

            if opcao == "1":
                self._viajante_controller.cadastrar_viajante()
            elif opcao == "2":
                self._entrar()
            elif opcao == "0":
                return
            else:
                self._tela.mostra_mensagem("Opção inválida.")
    
    def _entrar(self) -> None:
        # login provisório, caso de uso ainda não implementado, está apenas para testar o fluxo do sistema
        email = self._tela.solicita_email_login()
        registro = self._viajante_dao.buscar_por_email(email)

        if registro is None:
            self._tela.mostra_mensagem("Nenhum viajante cadastrado com esse e-mail.")
            return

        viajante = Viajante(
            id=registro.id,
            nome=registro.nome,
            data_nascimento=registro.data_nascimento,
            email=registro.email,
            senha=registro.senha,
        )
        MenuController(viajante).iniciar()