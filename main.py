from uuid import uuid4

from src.DAOs.GrupoDAO import GrupoDAO
from src.DAOs.ViajanteDAO import ViajanteDAO
from src.control.GrupoController import GrupoController
from src.model.Viajante import Viajante
from src.view.GrupoView import GrupoView


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

    controller = GrupoController(viajante)
    controller.criar_grupo()

    grupo = viajante.grupos_organizador[-1]
    grupo_salvo = GrupoDAO().buscar_por_id(grupo.id)
    if grupo_salvo is None or grupo_salvo.organizador_id != viajante.id:
        raise RuntimeError("O grupo não foi persistido corretamente.")

    print(
        "Persistência verificada: "
        f"viajante id={viajante.id}, grupo id={grupo.id}"
    )

if __name__ == "__main__":
    main()
