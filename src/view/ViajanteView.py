from src.view.View import View

from getpass import getpass


class ViajanteView(View):

    def cria_viajante(self) -> dict:
        valores_input = {
            "nome": input("Nome: ").strip(),
            "email": input("E-mail: ").strip().lower(),
            "senha": getpass("Senha: "),
            "confirmar_senha": getpass("Confirmar senha: "),
            "data_nascimento": input("Data de nascimento (dd/mm/aaaa): ").strip()
        }

        return valores_input
