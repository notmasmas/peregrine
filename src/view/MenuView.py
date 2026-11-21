import tkinter as tk
from collections.abc import Callable
from tkinter import messagebox


class MenuView(tk.Frame):
    def __init__(
        self,
        master: tk.Misc,
        nome_viajante: str,
        ao_criar_grupo: Callable[[str, list[str]], bool],
        ao_selecionar_grupo_para_gerenciar: Callable[[], None],
        ao_abrir_acompanhante: Callable[[], None],
        ao_listar_convites: Callable[[], list[dict]],
        ao_aceitar_convite: Callable[[int], bool],
        ao_rejeitar_convite: Callable[[int], bool],
        ao_sair: Callable[[], None],
    ) -> None:
        super().__init__(master, padx=24, pady=24)
        self._nome_viajante = nome_viajante
        self._ao_criar_grupo = ao_criar_grupo
        self._ao_selecionar_grupo_para_gerenciar = (
            ao_selecionar_grupo_para_gerenciar
        )
        self._ao_abrir_acompanhante = ao_abrir_acompanhante
        self._ao_listar_convites = ao_listar_convites
        self._ao_aceitar_convite = ao_aceitar_convite
        self._ao_rejeitar_convite = ao_rejeitar_convite
        self._ao_sair = ao_sair
        self.pack(fill=tk.BOTH, expand=True)

        container = tk.Frame(self)
        container.pack(fill=tk.BOTH, expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self._telas: dict[str, tk.Frame] = {}
        self._criar_tela_inicial(container)
        self._criar_tela_criacao(container)
        self._criar_tela_convites(container)
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
        botoes_direita = tk.Frame(tela)
        botoes_direita.grid(row=0, column=1, sticky=tk.E, pady=(12, 0))
        tk.Button(
            botoes_direita, text="Acompanhantes", command=self._ao_abrir_acompanhante
        ).pack(side=tk.RIGHT)
        tk.Button(
            botoes_direita,
            text="Meus Convites",
            command=self.mostrar_convites,
        ).pack(side=tk.RIGHT, padx=(0, 8))
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
            botoes_esquerda, text="+ Novo", command=self.mostrar_criacao
        ).pack(side=tk.LEFT, padx=(8, 0))
        tk.Button(
            tela,
            text="Gerenciar grupos",
            command=self._ao_selecionar_grupo_para_gerenciar,
        ).grid(row=3, column=1, sticky=tk.E, pady=(12, 0))

    def _criar_tela_criacao(self, container: tk.Frame) -> None:
        tela = self._criar_tela(container, "criar_grupo")
        tela.grid_columnconfigure(0, weight=1)
        tela.grid_rowconfigure(4, weight=1)

        cabecalho = tk.Frame(tela)
        cabecalho.grid(row=0, column=0, sticky="ew")
        cabecalho.grid_columnconfigure(1, weight=1)
        tk.Button(
            cabecalho, text="Voltar", command=self._voltar_da_criacao
        ).grid(row=0, column=0, sticky=tk.W)
        tk.Label(
            cabecalho,
            text="Novo grupo de viagem",
            font=("TkDefaultFont", 18, "bold"),
        ).grid(row=0, column=1, padx=12)

        tk.Label(tela, text="Nome do grupo").grid(
            row=1, column=0, sticky=tk.W, pady=(24, 4)
        )
        self._entrada_nome_grupo = tk.Entry(tela)
        self._entrada_nome_grupo.grid(row=2, column=0, sticky="ew")

        tk.Label(tela, text="Participantes").grid(
            row=3, column=0, sticky=tk.W, pady=(16, 4)
        )
        self._campos_participantes: list[tk.Entry] = []
        self._container_participantes = tk.Frame(tela)
        self._container_participantes.grid(
            row=4, column=0, sticky="new"
        )
        self._botao_adicionar_email: tk.Button | None = None
        self._adicionar_campo_email()

        tk.Button(tela, text="Criar", command=self._enviar_criacao).grid(
            row=5, column=0, sticky=tk.E, pady=(16, 0)
        )

    def _criar_tela_convites(self, container: tk.Frame) -> None:
        tela = self._criar_tela(container, "visualizar_convites")
        tela.grid_columnconfigure(0, weight=1)
        tela.grid_rowconfigure(2, weight=1)

        cabecalho = tk.Frame(tela)
        cabecalho.grid(row=0, column=0, sticky="ew")
        cabecalho.grid_columnconfigure(1, weight=1)
        tk.Button(
            cabecalho, text="Voltar", command=self.mostrar_inicio
        ).grid(row=0, column=0, sticky=tk.W)
        tk.Label(
            tela,
            text="Meus convites",
            font=("TkDefaultFont", 18, "bold"),
        ).grid(row=1, column=0, columnspan=2, pady=(32, 12))

        self._container_convites = tk.Frame(tela)
        self._container_convites.grid(
            row=2, column=0, sticky="nsew", pady=(24, 0)
        )
        self._container_convites.grid_columnconfigure(0, weight=1)


    def _adicionar_campo_email(self) -> None:
        if self._botao_adicionar_email is not None:
            self._botao_adicionar_email.destroy()

        linha = tk.Frame(self._container_participantes)
        linha.pack(fill=tk.X, pady=2)
        linha.grid_columnconfigure(0, weight=1)
        entrada = tk.Entry(linha)
        entrada.grid(row=0, column=0, sticky="ew")
        self._campos_participantes.append(entrada)
        self._botao_adicionar_email = tk.Button(
            linha, text="+", command=self._adicionar_campo_email
        )
        self._botao_adicionar_email.grid(row=0, column=1, padx=(8, 0))

    def _enviar_criacao(self) -> None:
        nome = self._entrada_nome_grupo.get().strip()
        participantes = [
            entrada.get().strip()
            for entrada in self._campos_participantes
            if entrada.get().strip()
        ]
        if self._ao_criar_grupo(nome, participantes):
            self._limpar_formulario_grupo()
            self.mostrar_inicio()

    def _limpar_formulario_grupo(self) -> None:
        self._entrada_nome_grupo.delete(0, tk.END)
        for entrada in self._campos_participantes:
            entrada.master.destroy()
        self._campos_participantes.clear()
        self._botao_adicionar_email = None
        self._adicionar_campo_email()

    def _voltar_da_criacao(self) -> None:
        self._limpar_formulario_grupo()
        self.mostrar_inicio()

    def _mostrar_tela(self, nome: str) -> None:
        self._telas[nome].tkraise()

    def mostrar_inicio(self) -> None:
        self._mostrar_tela("inicio")

    def mostrar_criacao(self) -> None:
        self._mostrar_tela("criar_grupo")
        self._entrada_nome_grupo.focus_set()

    def mostrar_convites(self) -> None:
        self._atualizar_lista_convites()
        self._mostrar_tela("visualizar_convites")

    def _atualizar_lista_convites(self) -> None:
        for widget in self._container_convites.winfo_children():
            widget.destroy()

        convites = self._ao_listar_convites()
        if not convites:
            tk.Label(
                self._container_convites,
                text="Você não possui convites pendentes.",
            ).grid(row=0, column=0, columnspan=2)
            return

        for indice, convite in enumerate(convites):
            linha = tk.Frame(self._container_convites)
            linha.grid(row=indice, column=0, sticky="ew", pady=4)
            linha.grid_columnconfigure(0, weight=1)

            tk.Label(
                linha,
                text=convite["nome_grupo"],
                font=("TkDefaultFont", 11),
            ).grid(row=0, column=0, sticky=tk.W)

            botoes = tk.Frame(linha)
            botoes.grid(row=0, column=1, sticky=tk.E)
            tk.Button(
                botoes,
                text="Aceitar",
                command=lambda convite_id=convite["id"]: self._responder_convite(
                    convite_id, True
                ),
            ).pack(side=tk.LEFT)
            tk.Button(
                botoes,
                text="Rejeitar",
                command=lambda convite_id=convite["id"]: self._responder_convite(
                    convite_id, False
                ),
            ).pack(side=tk.LEFT, padx=(8, 0))

    def _responder_convite(self, convite_id: int, aceitar: bool) -> None:
        sucesso = (
            self._ao_aceitar_convite(convite_id)
            if aceitar
            else self._ao_rejeitar_convite(convite_id)
        )
        if sucesso:
            self._atualizar_lista_convites()

    def mostrar_erro(self, mensagem: str) -> None:
        messagebox.showerror("Peregrine", mensagem, parent=self)

    def mostrar_sucesso(self, mensagem: str) -> None:
        messagebox.showinfo("Peregrine", mensagem, parent=self)
