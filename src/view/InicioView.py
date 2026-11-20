# Entrega 3: Implementado por Sarah Meireles
import tkinter as tk
from collections.abc import Callable
from tkinter import messagebox


class InicioView(tk.Frame):
    def __init__(
        self,
        master: tk.Misc,
        ao_entrar: Callable[[dict[str, str]], None],
        ao_cadastrar: Callable[[dict[str, str]], None],
        ao_sair: Callable[[], None],
    ) -> None:
        super().__init__(master, padx=24, pady=24)
        self._ao_entrar = ao_entrar
        self._ao_cadastrar = ao_cadastrar
        self._ao_sair = ao_sair
        self.pack(fill=tk.BOTH, expand=True)

        container = tk.Frame(self)
        container.pack(fill=tk.BOTH, expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self._telas: dict[str, tk.Frame] = {}
        self._criar_tela_inicial(container)
        self._criar_tela_login(container)
        self._criar_tela_cadastro(container)
        self._criar_tela_sessao(container)
        self.mostrar_inicio()

    def _criar_tela(self, container: tk.Frame, nome: str) -> tk.Frame:
        tela = tk.Frame(container)
        tela.grid(row=0, column=0, sticky="nsew")
        self._telas[nome] = tela
        return tela

    def _criar_tela_inicial(self, container: tk.Frame) -> None:
        tela = self._criar_tela(container, "inicio")
        tk.Label(tela, text="Peregrine", font=("TkDefaultFont", 20, "bold")).pack(
            pady=(24, 16)
        )
        tk.Button(tela, text="Entrar", command=self.mostrar_login).pack(
            fill=tk.X, pady=4
        )
        tk.Button(tela, text="Cadastrar viajante", command=self.mostrar_cadastro).pack(
            fill=tk.X, pady=4
        )
        tk.Button(tela, text="Sair", command=self._ao_sair).pack(
            fill=tk.X, pady=(16, 4)
        )

    def _criar_tela_login(self, container: tk.Frame) -> None:
        tela = self._criar_tela(container, "login")
        tk.Label(tela, text="Entrar", font=("TkDefaultFont", 18, "bold")).pack(
            pady=(16, 12)
        )
        tk.Label(tela, text="E-mail").pack(anchor=tk.W)
        self._email_login = tk.Entry(tela)
        self._email_login.pack(fill=tk.X, pady=(0, 8))
        tk.Label(tela, text="Senha").pack(anchor=tk.W)
        self._senha_login = tk.Entry(tela, show="*")
        self._senha_login.pack(fill=tk.X, pady=(0, 12))
        tk.Button(tela, text="Entrar", command=self._enviar_login).pack(
            fill=tk.X, pady=4
        )
        tk.Button(tela, text="Voltar", command=self.mostrar_inicio).pack(
            fill=tk.X, pady=4
        )

    def _criar_tela_cadastro(self, container: tk.Frame) -> None:
        tela = self._criar_tela(container, "cadastro")
        tk.Label(
            tela, text="Cadastrar viajante", font=("TkDefaultFont", 18, "bold")
        ).pack(pady=(8, 8))

        self._campos_cadastro: dict[str, tk.Entry] = {}
        campos = (
            ("nome", "Nome", ""),
            ("email", "E-mail", ""),
            ("senha", "Senha", "*"),
            ("confirmar_senha", "Confirmar senha", "*"),
            ("data_nascimento", "Data de nascimento (dd/mm/aaaa)", ""),
        )
        for chave, rotulo, mascara in campos:
            tk.Label(tela, text=rotulo).pack(anchor=tk.W)
            entrada = tk.Entry(tela, show=mascara)
            entrada.pack(fill=tk.X, pady=(0, 6))
            self._campos_cadastro[chave] = entrada

        tk.Button(tela, text="Cadastrar", command=self._enviar_cadastro).pack(
            fill=tk.X, pady=(6, 4)
        )
        tk.Button(tela, text="Voltar", command=self.mostrar_inicio).pack(
            fill=tk.X, pady=4
        )

    def _criar_tela_sessao(self, container: tk.Frame) -> None:
        tela = self._criar_tela(container, "sessao")
        self._mensagem_sessao = tk.Label(
            tela, font=("TkDefaultFont", 16, "bold"), wraplength=320
        )
        self._mensagem_sessao.pack(pady=(32, 16))
        tk.Label(
            tela,
            text="A próxima etapa é conectar esta tela ao menu de grupos.",
            wraplength=320,
        ).pack(pady=(0, 16))
        tk.Button(tela, text="Voltar ao início", command=self.mostrar_inicio).pack(
            fill=tk.X
        )

    def _mostrar_tela(self, nome: str) -> None:
        self._telas[nome].tkraise()

    def mostrar_inicio(self) -> None:
        self._mostrar_tela("inicio")

    def mostrar_login(self) -> None:
        self._mostrar_tela("login")
        self._email_login.focus_set()

    def mostrar_cadastro(self) -> None:
        self._mostrar_tela("cadastro")
        self._campos_cadastro["nome"].focus_set()

    def mostrar_sessao(self, nome: str) -> None:
        self._mensagem_sessao.config(text=f"Bem-vindo, {nome}!")
        self._mostrar_tela("sessao")

    def mostrar_erro(self, mensagem: str) -> None:
        messagebox.showerror("Peregrine", mensagem, parent=self)

    def mostrar_sucesso(self, mensagem: str) -> None:
        messagebox.showinfo("Peregrine", mensagem, parent=self)

    def _enviar_login(self) -> None:
        email = self._email_login.get().strip().lower()
        senha = self._senha_login.get()
        if not email or not senha:
            self.mostrar_erro("Informe o e-mail e a senha.")
            return
        self._ao_entrar({"email": email, "senha": senha})

    def _enviar_cadastro(self) -> None:
        dados = {
            chave: entrada.get().strip()
            for chave, entrada in self._campos_cadastro.items()
        }
        dados["email"] = dados["email"].lower()
        self._ao_cadastrar(dados)
