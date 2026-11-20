from src.view.View import View
import tkinter as tk


class MenuView(View):

    def exibe_menu_principal(self) -> str:
        print("\n=== Menu ===")
        print("1 - Criar grupo")
        print("2 - Gerenciar grupo")
        print("0 - Sair")
        return input("Opção: ").strip()