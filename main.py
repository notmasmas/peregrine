import tkinter as tk
from src.control.InicioController import InicioController

'''
Gustavo de Pinho
UC04: Editar e remover grupos de viagem
UC06: Convidar, visualizar e excluir viajantes
UC10: Adicionar acompanhante ao grupo de viagem
UC12: Sugerir mudanças no itinerário
UC13: Aprovar sugestão de alteração

Maria Helena Melo
UC02: Efetuar login
UC03: Criar grupo de viagem
UC05: Entrar ou sair de um grupo de viagem
UC08: Enviar notificação de convite de um grupo por e-mail
UC09: Vincular acompanhante à conta
UC11: Criar e alterar itinerário de viagem

Sarah
UC01: Cadastrar viajantes
UC07: Visualizar grupos de viagem
UC14: Dividir custos de viagem entre membros do grupo
UC15: Emitir relatório da viagem
'''


def initialize_database() -> None:
    from src.database import Base, engine

    Base.metadata.create_all(engine)


def main() -> None:
    initialize_database()
    root = tk.Tk()
    root.title("Peregrine")
    root.geometry("420x480")
    root.minsize(360, 420)
    InicioController(root)
    root.mainloop()


if __name__ == "__main__":
    main()
