from uuid import uuid4

from src.DAOs.ViajanteDAO import ViajanteDAO
from src.control.MenuController import MenuController
from src.model.Viajante import Viajante


def initialize_database() -> None:
    from src.database import Base, engine
    import src.persistence.models

    Base.metadata.create_all(engine)


def main() -> None:
    initialize_database()

    # isso aqui depois vai ser substituído pelo controlador de viajante
    viajante = Viajante(
        nome="Viajante de teste",
        idade=30,
        email=f"viajante{uuid4().hex[:8]}@gmail.com", # isso aqui é pra não dar conflito de e-mail repetido já que e-mail é UNIQUE no BD
        senha="senha-apenas-para-teste",
    )
    ViajanteDAO().criar(viajante)

    # viajante extra apenas para testar "adicionar viajante" em um grupo
    convidado = Viajante(
        nome="Convidado de teste",
        idade=25,
        email=f"convidado{uuid4().hex[:8]}@gmail.com",
        senha="senha-apenas-para-teste",
    )
    ViajanteDAO().criar(convidado)
    print(f"E-mail do convidado para testes: {convidado.email}")

    MenuController(viajante).iniciar()


if __name__ == "__main__":
    main()
