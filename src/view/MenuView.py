import tkinter as tk
from collections.abc import Callable


class MenuView(tk.Frame):
    def __init__(
        self,
        master: tk.Misc,
        nome_viajante: str,
        ao_criar_grupo: Callable[[], None],
        ao_selecionar_grupo_para_gerenciar: Callable[[], None],
        ao_sair: Callable[[], None],
    ) -> None:
        super().__init__(master, padx=24, pady=24)
        self._nome_viajante = nome_viajante
        self._ao_criar_grupo = ao_criar_grupo
        self._ao_selecionar_grupo_para_gerenciar = (
            ao_selecionar_grupo_para_gerenciar
        )
        self._ao_sair = ao_sair
        self.pack(fill=tk.BOTH, expand=True)

        container = tk.Frame(self)
        container.pack(fill=tk.BOTH, expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self._telas: dict[str, tk.Frame] = {}
        self._criar_tela_inicial(container)
        self.mostrar_inicio()

    def _criar_tela(self, container: tk.Frame, nome: str) -> tk.Frame:
        tela = tk.Frame(container)
        tela.grid(row=0, column=0, sticky="nsew")
        self._telas[nome] = tela
        return tela

    def _criar_tela_inicial(self, container: tk.Frame) -> None:
        tela = self._criar_tela(container, "inicio")
        tela.grid_columnconfigure(0, weight=1)
        tela.grid_columnconfigure(1, weight=1)
        tela.grid_rowconfigure(2, weight=1)

        tk.Label(tela, text=f"Olá, {self._nome_viajante}!").grid(
            row=0, column=0, sticky=tk.W
        )
        tk.Button(tela, text="Acompanhantes").grid(
            row=0, column=1, sticky=tk.E
        )
        tk.Label(
            tela,
            text="Seus grupos de viagem",
            font=("TkDefaultFont", 18, "bold"),
        ).grid(row=1, column=0, columnspan=2, pady=(32, 12))

        tk.Frame(tela).grid(
            row=2, column=0, columnspan=2, sticky="nsew"
        )
        botoes_esquerda = tk.Frame(tela)
        botoes_esquerda.grid(row=3, column=0, sticky=tk.W, pady=(12, 0))
        tk.Button(
            botoes_esquerda, text="Sair", command=self._ao_sair
        ).pack(side=tk.LEFT)
        tk.Button(
            botoes_esquerda, text="+ Novo", command=self._ao_criar_grupo
        ).pack(side=tk.LEFT, padx=(8, 0))
        tk.Button(
            tela,
            text="Gerenciar grupos",
            command=self._ao_selecionar_grupo_para_gerenciar,
        ).grid(row=3, column=1, sticky=tk.E, pady=(12, 0))

    def _mostrar_tela(self, nome: str) -> None:
        self._telas[nome].tkraise()

    def mostrar_inicio(self) -> None:
        self._mostrar_tela("inicio")
