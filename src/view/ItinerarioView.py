import tkinter as tk
from collections.abc import Callable
from datetime import date, datetime
import math
from tkinter import messagebox, ttk


class ItinerarioView(tk.Frame):
    def __init__(
        self,
        master: tk.Misc,
        nome_grupo: str,
        dias: list[dict[str, str]],
        ao_voltar: Callable[[], None],
        participantes: list[tuple[int, str]],
        ao_adicionar: Callable[[dict], bool],
        ao_editar: Callable[[str, dict], bool],
        ao_remover: Callable[[list[str]], bool],
        pode_adicionar: bool,
    ) -> None:
        super().__init__(master, padx=24, pady=24)
        self.pack(fill=tk.BOTH, expand=True)
        self._dias = list(dias)
        self._participantes = participantes
        self._pode_adicionar = pode_adicionar
        self._ao_adicionar = ao_adicionar
        self._ao_editar = ao_editar
        self._ao_remover = ao_remover
        self._modo_edicao = False
        self._selecao_dias: dict[str, tk.BooleanVar] = {}
        self._data_original: str | None = None
        self._reservas: list[
            tuple[tk.Entry, tk.Entry, ttk.Combobox]
        ] = []
        self._tela_inicial = tk.Frame(self)
        self._tela_inicial.pack(fill=tk.BOTH, expand=True)
        self._tela_inicial.grid_columnconfigure(0, weight=1)
        self._tela_inicial.grid_rowconfigure(2, weight=1)
        self._tela_criacao = tk.Frame(self)

        cabecalho = tk.Frame(self._tela_inicial)
        cabecalho.grid(row=0, column=0, sticky="ew")
        cabecalho.grid_columnconfigure(1, weight=1)
        tk.Button(cabecalho, text="<", width=3, command=ao_voltar).grid(
            row=0, column=0, sticky=tk.W
        )
        self._botao_editar_modo = tk.Button(
            cabecalho,
            text="✎",
            width=3,
            command=self._alternar_modo_edicao,
        )
        self._botao_editar_modo.grid(row=0, column=2, sticky=tk.E)

        tk.Label(
            self._tela_inicial,
            text=nome_grupo,
            font=("TkDefaultFont", 18, "bold"),
            wraplength=360,
            justify=tk.CENTER,
        ).grid(row=1, column=0, sticky="ew", pady=(24, 16))

        lista_dias = tk.Frame(self._tela_inicial)
        lista_dias.grid(row=2, column=0, sticky="nsew")
        lista_dias.grid_rowconfigure(0, weight=1)
        lista_dias.grid_columnconfigure(0, weight=1)
        canvas = tk.Canvas(lista_dias, highlightthickness=0)
        canvas.grid(row=0, column=0, sticky="nsew")
        barra = tk.Scrollbar(
            lista_dias, orient=tk.VERTICAL, command=canvas.yview
        )
        barra.grid(row=0, column=1, sticky="ns")
        canvas.configure(yscrollcommand=barra.set)

        area_dias = tk.Frame(canvas)
        janela = canvas.create_window((0, 0), window=area_dias, anchor="nw")
        area_dias.bind(
            "<Configure>",
            lambda evento: canvas.configure(
                scrollregion=(0, 0, evento.width, evento.height)
            ),
        )
        canvas.bind(
            "<Configure>",
            lambda evento: canvas.itemconfigure(janela, width=evento.width),
        )
        area_dias.grid_columnconfigure(0, weight=1)
        self._area_dias = area_dias

        self._acoes_normais = tk.Frame(self._tela_inicial)
        self._acoes_normais.grid(
            row=3, column=0, sticky="ew", pady=(12, 0)
        )
        if self._pode_adicionar:
            tk.Button(
                self._acoes_normais,
                text="+ Adicionar ao itinerário",
                command=self._mostrar_criacao,
            ).pack(side=tk.LEFT)
        tk.Button(self._acoes_normais, text="Sugestões").pack(
            side=tk.RIGHT if self._pode_adicionar else tk.LEFT,
            fill=tk.X,
            expand=True,
            padx=(8, 0) if self._pode_adicionar else 0,
        )
        self._acoes_edicao = tk.Frame(self._tela_inicial)
        self._acoes_edicao.grid(
            row=3, column=0, sticky="ew", pady=(12, 0)
        )
        self._acoes_edicao.grid_columnconfigure(0, weight=1)
        self._acoes_edicao.grid_columnconfigure(1, weight=1)
        self._botao_remover = tk.Button(
            self._acoes_edicao,
            text="Remover",
            command=self._remover_selecionados,
            state=tk.DISABLED,
        )
        self._botao_remover.grid(row=0, column=0, sticky="ew", padx=(0, 4))
        self._botao_editar_dia = tk.Button(
            self._acoes_edicao,
            text="Editar",
            command=self._editar_selecionado,
            state=tk.DISABLED,
        )
        self._botao_editar_dia.grid(row=0, column=1, sticky="ew", padx=(4, 0))
        self._acoes_edicao.grid_remove()
        self._criar_tela_criacao()
        self.atualizar_dias(dias)

    def atualizar_dias(self, dias: list[dict[str, str]]) -> None:
        self._dias = list(dias)
        self._selecao_dias.clear()
        for filho in self._area_dias.winfo_children():
            filho.destroy()

        if not dias:
            tk.Label(
                self._area_dias, text="Nenhum dia adicionado ao itinerário."
            ).grid(row=0, column=0, sticky="n", pady=8)
            self._atualizar_botoes_edicao()
            return

        for indice, dia in enumerate(dias):
            linha = tk.Frame(self._area_dias)
            linha.grid(row=indice, column=0, sticky="ew", pady=4)
            coluna_cartao = 0
            data_iso = self._data_iso(dia)
            if self._modo_edicao:
                variavel = tk.BooleanVar(master=self, value=False)
                self._selecao_dias[data_iso] = variavel
                tk.Checkbutton(
                    linha,
                    variable=variavel,
                    command=self._atualizar_botoes_edicao,
                ).grid(row=0, column=0, padx=(0, 4))
                coluna_cartao = 1

            item = tk.Frame(linha, bg="#e8eaed", padx=12, pady=8)
            item.grid(row=0, column=coluna_cartao, sticky="ew")
            linha.grid_columnconfigure(coluna_cartao, weight=1)
            item.grid_columnconfigure(0, weight=1)
            tk.Label(
                item,
                text=dia["data"],
                font=("TkDefaultFont", 11, "bold"),
                anchor="w",
                bg="#e8eaed",
            ).grid(row=0, column=0, sticky="ew")
            tk.Label(
                item, text=dia["passeio"], anchor="w", bg="#e8eaed"
            ).grid(row=1, column=0, sticky="ew")
            tk.Label(
                item, text=dia["cidade"], anchor="w", bg="#e8eaed"
            ).grid(row=2, column=0, sticky="ew")
        self._atualizar_botoes_edicao()

    @staticmethod
    def _data_iso(dia: dict[str, str]) -> str:
        return datetime.strptime(dia["data"], "%d/%m/%Y").date().isoformat()

    def _alternar_modo_edicao(self) -> None:
        self._modo_edicao = not self._modo_edicao
        self._botao_editar_modo.config(
            relief=tk.SUNKEN if self._modo_edicao else tk.RAISED
        )
        if self._modo_edicao:
            self._acoes_normais.grid_remove()
            self._acoes_edicao.grid()
        else:
            self._acoes_edicao.grid_remove()
            self._acoes_normais.grid()
        self.atualizar_dias(self._dias)

    def _atualizar_botoes_edicao(self) -> None:
        selecionados = sum(
            variavel.get() for variavel in self._selecao_dias.values()
        )
        self._botao_remover.config(
            state=tk.NORMAL if selecionados else tk.DISABLED
        )
        self._botao_editar_dia.config(
            state=tk.NORMAL if selecionados == 1 else tk.DISABLED
        )

    def _selecionados(self) -> list[str]:
        return [
            data
            for data, variavel in self._selecao_dias.items()
            if variavel.get()
        ]

    def _remover_selecionados(self) -> None:
        datas = self._selecionados()
        if not datas or not messagebox.askyesno(
            "Remover dias",
            f"Deseja remover {len(datas)} dia(s) do itinerário?",
            default=messagebox.NO,
            parent=self,
        ):
            return
        if not self._ao_remover(datas):
            return

        datas_removidas = set(datas)
        self.atualizar_dias(
            [dia for dia in self._dias if self._data_iso(dia) not in datas_removidas]
        )

    def _editar_selecionado(self) -> None:
        datas = self._selecionados()
        if len(datas) != 1:
            return
        dia = next(dia for dia in self._dias if self._data_iso(dia) == datas[0])
        self._mostrar_criacao(dia)

    def _mostrar_criacao(self, dia: dict[str, str] | None = None) -> None:
        self._data_original = None
        self._limpar_formulario()
        if dia is not None:
            data = datetime.strptime(dia["data"], "%d/%m/%Y").date()
            self._data_original = data.isoformat()
            self._entrada_data.insert(0, dia["data"])
            self._entrada_cidade.insert(0, dia["cidade"])
            self._entrada_passeio.insert(0, dia["passeio"])
            
            reservas = dia.get("reservas", [])
            if reservas:
                for filho in self._area_reservas.winfo_children():
                    filho.destroy() # destrói bloco vazio no começo
                self._reservas.clear()
                ids = [id_ for id_, _ in self._participantes]
                for reserva in reservas:
                    self._adicionar_reserva()
                    nome, preco, titular = self._reservas[-1]
                    nome.insert(0, reserva["nome"])
                    preco.insert(0, f"{reserva['preco']:.2f}".replace(".", ","))
                    if reserva["titular_id"] in ids:
                        titular.current(ids.index(reserva["titular_id"]))

        self._tela_inicial.pack_forget()
        self._tela_criacao.pack(fill=tk.BOTH, expand=True)

    def _mostrar_inicio(self) -> None:
        self._tela_criacao.pack_forget()
        self._tela_inicial.pack(fill=tk.BOTH, expand=True)

    def _limpar_formulario(self) -> None:
        self._entrada_data.delete(0, tk.END)
        self._entrada_cidade.delete(0, tk.END)
        self._entrada_passeio.delete(0, tk.END)
        for reserva in self._area_reservas.winfo_children():
            reserva.destroy()
        self._reservas.clear()
        self._adicionar_reserva()

    def _criar_tela_criacao(self) -> None:
        self._tela_criacao.grid_columnconfigure(0, weight=1)
        self._tela_criacao.grid_rowconfigure(1, weight=1)

        cabecalho = tk.Frame(self._tela_criacao)
        cabecalho.grid(row=0, column=0, sticky="ew")
        cabecalho.grid_columnconfigure(1, weight=1)
        tk.Button(
            cabecalho, text="<", width=3, command=self._mostrar_inicio
        ).grid(row=0, column=0, sticky=tk.W)

        formulario = tk.Frame(self._tela_criacao)
        formulario.grid(row=1, column=0, sticky="nsew", pady=(16, 8))
        formulario.grid_rowconfigure(0, weight=1)
        formulario.grid_columnconfigure(0, weight=1)
        self._canvas_criacao = tk.Canvas(formulario, highlightthickness=0)
        self._canvas_criacao.grid(row=0, column=0, sticky="nsew")
        barra = tk.Scrollbar(
            formulario,
            orient=tk.VERTICAL,
            command=self._canvas_criacao.yview,
        )
        barra.grid(row=0, column=1, sticky="ns")
        self._canvas_criacao.configure(yscrollcommand=barra.set)

        self._conteudo_criacao = tk.Frame(self._canvas_criacao)
        janela = self._canvas_criacao.create_window(
            (0, 0), window=self._conteudo_criacao, anchor="nw"
        )
        self._conteudo_criacao.bind(
            "<Configure>",
            lambda evento: self._canvas_criacao.configure(
                scrollregion=(0, 0, evento.width, evento.height)
            ),
        )
        self._canvas_criacao.bind(
            "<Configure>",
            lambda evento: self._canvas_criacao.itemconfigure(
                janela, width=evento.width
            ),
        )
        self._conteudo_criacao.grid_columnconfigure(0, weight=1)

        self._entrada_data = self._adicionar_campo("Dia", 0)
        self._entrada_cidade = self._adicionar_campo("Cidade", 2)
        self._entrada_passeio = self._adicionar_campo(
            "Passeio turístico", 4
        )
        tk.Label(
            self._conteudo_criacao,
            text="Reserva",
            font=("TkDefaultFont", 11, "bold"),
        ).grid(row=6, column=0, sticky=tk.W, pady=(16, 4))

        self._area_reservas = tk.Frame(self._conteudo_criacao)
        self._area_reservas.grid(row=7, column=0, sticky="ew")
        self._area_reservas.grid_columnconfigure(0, weight=1)
        tk.Button(
            self._conteudo_criacao,
            text="Adicionar mais uma reserva",
            command=self._adicionar_reserva,
        ).grid(row=8, column=0, sticky=tk.W, pady=(8, 0))
        if not self._participantes:
            tk.Label(
                self._conteudo_criacao,
                text="O grupo não possui participantes disponíveis para titular.",
                wraplength=340,
                justify=tk.LEFT,
            ).grid(row=9, column=0, sticky=tk.W, pady=(8, 0))

        tk.Button(
            self._tela_criacao,
            text="Adicionar no Itinerário",
            command=self._enviar_criacao,
        ).grid(row=2, column=0, sticky="ew", pady=(8, 0))
        self._adicionar_reserva()

    def _adicionar_campo(self, titulo: str, linha: int) -> tk.Entry:
        tk.Label(self._conteudo_criacao, text=titulo).grid(
            row=linha, column=0, sticky=tk.W, pady=(8, 4)
        )
        entrada = tk.Entry(self._conteudo_criacao)
        entrada.grid(row=linha + 1, column=0, sticky="ew")
        return entrada

    def _adicionar_reserva(self) -> None:
        indice = len(self._reservas)
        reserva = tk.Frame(self._area_reservas, bg="#e8eaed", padx=8, pady=6)
        reserva.grid(row=indice, column=0, sticky="ew", pady=4)
        reserva.grid_columnconfigure(0, weight=1)
        tk.Label(
            reserva,
            text=f"Reserva {indice + 1}",
            font=("TkDefaultFont", 10, "bold"),
            bg="#e8eaed",
        ).grid(row=0, column=0, sticky=tk.W)
        tk.Label(reserva, text="Nome da reserva", bg="#e8eaed").grid(
            row=1, column=0, sticky=tk.W, pady=(4, 2)
        )
        entrada_nome = tk.Entry(reserva)
        entrada_nome.grid(row=2, column=0, sticky="ew")
        tk.Label(reserva, text="Preço da reserva", bg="#e8eaed").grid(
            row=3, column=0, sticky=tk.W, pady=(4, 2)
        )
        entrada_preco = tk.Entry(reserva)
        entrada_preco.grid(row=4, column=0, sticky="ew")
        tk.Label(reserva, text="Titular da reserva", bg="#e8eaed").grid(
            row=5, column=0, sticky=tk.W, pady=(4, 2)
        )
        titular = ttk.Combobox(
            reserva,
            state="readonly" if self._participantes else "disabled",
            values=[nome for _, nome in self._participantes],
        )
        titular.grid(row=6, column=0, sticky="ew")
        if self._participantes:
            titular.current(0)
        self._reservas.append((entrada_nome, entrada_preco, titular))

    def _enviar_criacao(self) -> None:
        data_texto = self._entrada_data.get().strip()
        try:
            data = datetime.strptime(data_texto, "%d/%m/%Y").date()
        except ValueError:
            self.mostrar_erro("Informe uma data válida no formato DD/MM/AAAA.")
            return

        cidade = self._entrada_cidade.get().strip()
        passeio = self._entrada_passeio.get().strip()
        if not cidade or not passeio:
            self.mostrar_erro("Informe a cidade e o passeio turístico.")
            return

        reservas = []
        for entrada_nome, entrada_preco, titular in self._reservas:
            nome = entrada_nome.get().strip()
            preco_texto = entrada_preco.get().strip().replace(",", ".")
            if not nome and not preco_texto:
                continue
            if not nome or not preco_texto:
                self.mostrar_erro("Preencha o nome e o preço de cada reserva.")
                return

            try:
                preco = float(preco_texto)
            except ValueError:
                self.mostrar_erro("Informe um preço válido para cada reserva.")
                return
            if not math.isfinite(preco) or preco < 0:
                self.mostrar_erro("Informe um preço válido para cada reserva.")
                return
            if not self._participantes:
                self.mostrar_erro(
                    "O grupo precisa ter um participante para titular a reserva."
                )
                return

            indice_titular = titular.current()
            if not 0 <= indice_titular < len(self._participantes):
                self.mostrar_erro("Selecione o titular de cada reserva.")
                return
            titular_id, _ = self._participantes[indice_titular]
            reservas.append(
                {"nome": nome, "preco": preco, "titular_id": titular_id}
            )

        dados = {
            "data": data.isoformat(),
            "cidade": cidade,
            "passeio": passeio,
            "reservas": reservas,
        }
        if self._adicionar_dia(dados):
            self._data_original = None
            self._limpar_formulario()
            self._mostrar_inicio()
            if self._modo_edicao:
                self._alternar_modo_edicao()

    def _adicionar_dia(self, dados: dict) -> bool:
        if self._data_original is None:
            sucesso = self._ao_adicionar(dados)
        else:
            sucesso = self._ao_editar(self._data_original, dados)
        if not sucesso:
            return False

        data = date.fromisoformat(dados["data"])
        dia_atualizado = {
            "data": data.strftime("%d/%m/%Y"),
            "passeio": dados["passeio"],
            "cidade": dados["cidade"],
            "reservas": dados["reservas"],
        }
        dias_atualizados = [
            dia
            for dia in self._dias
            if self._data_iso(dia) != self._data_original
        ]
        dias_atualizados.append(dia_atualizado)
        dias_atualizados.sort(
            key=lambda dia: datetime.strptime(dia["data"], "%d/%m/%Y").date()
        )
        self.atualizar_dias(dias_atualizados)
        return True

    def mostrar_erro(self, mensagem: str) -> None:
        messagebox.showerror("Peregrine", mensagem, parent=self)