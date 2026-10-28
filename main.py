from src.control.InicioController import InicioController


def initialize_database() -> None:
    from src.database import Base, engine

    Base.metadata.create_all(engine)


def main() -> None:
    initialize_database()
    InicioController().iniciar()


if __name__ == "__main__":
    main()
