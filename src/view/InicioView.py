# Entrega 3: Implementado por Sarah Meireles

from src.view.View import View


class InicioView(View):

    def exibe_menu_inicial(self) -> str:
        print("\n=== Peregrine ===")
        print("1 - Cadastrar usuário")
        print("2 - Entrar")
        print("0 - Sair")
        return input("Opção: ").strip()
    
    # login provisório, caso de uso ainda não implementado, está apenas para testar o fluxo do sistema
    def solicita_email_login(self) -> str:
        return input("\nE-mail: ").strip().lower()