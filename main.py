import tkinter as tk
from src.control.InicioController import InicioController


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
