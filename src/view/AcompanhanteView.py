import tkinter as tk
from collections.abc import Callable
from tkinter import messagebox

from src.model.Acompanhante import Acompanhante
from src.model.Viajante import Viajante


class AcompanhanteView(tk.Frame):
    def __init__(
        self,
        master: tk.Misc,
        viajante_logado: Viajante,
        ao_vincular_acompanhante: Callable[[dict[str, str]], bool],
        ao_sair: Callable[[], None],
    ) -> None:
        super().__init__(master, padx=24, pady=24)
        self._viajante_logado = viajante_logado
        self._ao_vincular_acompanhante = ao_vincular_acompanhante
        self._ao_sair = ao_sair
        self.pack(fill=tk.BOTH, expand=True)

        container = tk.Frame(self)
        container.pack(fill=tk.BOTH, expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self._telas: dict[str, tk.Frame] = {}
        self._criar_tela_inicial(container)
        self.mostrar_inicio()
        self.atualizar_acompanhantes(viajante_logado.acompanhantes)

    def _criar_tela(self, container: tk.Frame, nome: str) -> tk.Frame:
        tela = tk.Frame(container)
        tela.grid(row=0, column=0, sticky="nsew")
        self._telas[nome] = tela
        return tela

    def _criar_tela_inicial(self, container: tk.Frame) -> None:
        tela = self._criar_tela(container, "inicio")
        tela.grid_columnconfigure(0, weight=1)
        tela.grid_rowconfigure(2, weight=1)

        cabecalho = tk.Frame(tela)
        cabecalho.grid(row=0, column=0, sticky="ew")
        cabecalho.grid_columnconfigure(1, weight=1)
        tk.Button(cabecalho, text="Voltar", command=self._ao_sair).grid(
            row=0, column=0, sticky=tk.W
        )
        tk.Label(
            tela,
            text=f"Acompanhantes de {self._viajante_logado.nome}",
            font=("TkDefaultFont", 18, "bold"),
        ).grid(row=1, column=0, sticky=tk.W, pady=(24, 8))

        lista_container = tk.Frame(tela)
        lista_container.grid(row=2, column=0, sticky="nsew")
        lista_container.grid_rowconfigure(0, weight=1)
        lista_container.grid_columnconfigure(0, weight=1)
        self._lista_acompanhantes = tk.Listbox(lista_container)
        self._lista_acompanhantes.grid(row=0, column=0, sticky="nsew")
        scrollbar = tk.Scrollbar(
            lista_container,
            orient=tk.VERTICAL,
            command=self._lista_acompanhantes.yview,
        )
        scrollbar.grid(row=0, column=1, sticky="ns")
        self._lista_acompanhantes.configure(yscrollcommand=scrollbar.set)
        self._mensagem_vazia = tk.Label(
            lista_container, text="Nenhum acompanhante cadastrado."
        )
        self._mensagem_vazia.grid(row=0, column=0, sticky="nsew")
        self._lista_acompanhantes.grid_remove()

        tk.Label(tela, text="Nome do acompanhante").grid(
            row=3, column=0, sticky=tk.W, pady=(16, 4)
        )
        formulario = tk.Frame(tela)
        formulario.grid(row=4, column=0, sticky="ew")
        formulario.grid_columnconfigure(0, weight=1)
        self._entrada_nome = tk.Entry(formulario)
        self._entrada_nome.grid(row=0, column=0, sticky="ew")
        self._entrada_nome.bind("<Return>", self._enviar_acompanhante)
        tk.Button(
            formulario,
            text="Adicionar",
            command=self._enviar_acompanhante,
        ).grid(row=0, column=1, padx=(8, 0))

    def _mostrar_tela(self, nome: str) -> None:
        self._telas[nome].tkraise()

    def mostrar_inicio(self) -> None:
        self._mostrar_tela("inicio")

    def atualizar_acompanhantes(
        self, acompanhantes: list[Acompanhante]
    ) -> None:
        self._lista_acompanhantes.delete(0, tk.END)
        if not acompanhantes:
            self._lista_acompanhantes.grid_remove()
            self._mensagem_vazia.grid(row=0, column=0, sticky="nsew")
            return

        self._mensagem_vazia.grid_remove()
        self._lista_acompanhantes.grid()
        for acompanhante in acompanhantes:
            self._lista_acompanhantes.insert(tk.END, acompanhante.nome)

    def mostrar_erro(self, mensagem: str) -> None:
        messagebox.showerror("Peregrine", mensagem, parent=self)

    def mostrar_sucesso(self, mensagem: str) -> None:
        messagebox.showinfo("Peregrine", mensagem, parent=self)

    def _enviar_acompanhante(self, event: tk.Event | None = None) -> None:
        if event is not None:
            event.widget.focus_set()
        nome = self._entrada_nome.get().strip()
        if self._ao_vincular_acompanhante({"nome": nome}):
            self._entrada_nome.delete(0, tk.END)
            self._entrada_nome.focus_set()
            self.atualizar_acompanhantes(
                self._viajante_logado.acompanhantes
            )
