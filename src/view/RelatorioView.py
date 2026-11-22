# UC15: Emitir relatório de viagem (Implementado por Sarah Meireles)

import tkinter as tk
from collections.abc import Callable

FUNDO_CARTAO = "#e8eaed"


def _reais(valor: float) -> str:
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


class RelatorioView(tk.Frame):
    def __init__(
        self,
        master: tk.Misc,
        relatorio: dict,
        ao_voltar: Callable[[], None],
    ) -> None:
        super().__init__(master, padx=24, pady=24)
        self.pack(fill=tk.BOTH, expand=True)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        tk.Button(self, text="<", width=3, command=ao_voltar).grid(
            row=0, column=0, sticky=tk.W
        )

        area = tk.Frame(self)
        area.grid(row=1, column=0, sticky="nsew", pady=(12, 0))
        area.grid_rowconfigure(0, weight=1)
        area.grid_columnconfigure(0, weight=1)
        canvas = tk.Canvas(area, highlightthickness=0)
        canvas.grid(row=0, column=0, sticky="nsew")
        barra = tk.Scrollbar(area, orient=tk.VERTICAL, command=canvas.yview)
        barra.grid(row=0, column=1, sticky="ns")
        canvas.configure(yscrollcommand=barra.set)

        self._conteudo = tk.Frame(canvas)
        janela = canvas.create_window((0, 0), window=self._conteudo, anchor="nw")
        self._conteudo.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=(0, 0, e.width, e.height)),
        )
        canvas.bind(
            "<Configure>", lambda e: canvas.itemconfigure(janela, width=e.width)
        )

        self._montar(relatorio)

    def _texto(self, texto: str, **opcoes) -> None:
        tk.Label(
            self._conteudo, text=texto, wraplength=340, justify=tk.CENTER, **opcoes
        ).pack(fill=tk.X, pady=2)

    def _secao(self, titulo: str) -> None:
        self._texto(titulo, fg="gray", font=("TkDefaultFont", 12, "bold"))

    @staticmethod
    def _linhas_viajantes(pai: tk.Misc, por_viajante: list[dict]) -> None:
        for v in por_viajante:
            tk.Label(
                pai,
                text=f"     {v['nome']} ({v['cotas']} cota(s)): {_reais(v['valor'])}",
                anchor="w",
                justify=tk.LEFT,
                bg=FUNDO_CARTAO,
            ).pack(fill=tk.X)

    def _montar(self, r: dict) -> None:
        self._texto(r["nome_grupo"], font=("TkDefaultFont", 18, "bold"))
        self._texto(f"Organizador: {r['organizador']}")
        self._texto(f"Membros: {', '.join(r['membros']) or '(nenhum)'}")
        self._texto(f"Acompanhantes: {', '.join(r['acompanhantes']) or '(nenhum)'}")

        tk.Frame(self._conteudo, height=12).pack()
        self._secao("Itinerário")
        if not r["dias"]:
            self._texto("Nenhum dia adicionado ao itinerário.")

        for dia in r["dias"]:
            cartao = tk.Frame(self._conteudo, bg=FUNDO_CARTAO, padx=12, pady=8)
            cartao.pack(fill=tk.X, pady=4)
            tk.Label(
                cartao,
                text=f"Dia {dia['numero']} ({dia['data']}): {dia['cidade']} | {dia['passeio']}",
                font=("TkDefaultFont", 10, "bold"),
                anchor="w",
                justify=tk.LEFT,
                wraplength=320,
                bg=FUNDO_CARTAO,
            ).pack(fill=tk.X)

            for reserva in dia["reservas"]:
                tk.Label(
                    cartao,
                    text=f"• {reserva['nome']}: {_reais(reserva['total'])}",
                    anchor="w",
                    justify=tk.LEFT,
                    wraplength=320,
                    bg=FUNDO_CARTAO,
                ).pack(fill=tk.X, pady=(4, 0))

            tk.Label(
                cartao,
                text=f"Total do dia: {_reais(dia['total'])}",
                font=("TkDefaultFont", 10, "bold"),
                anchor="w",
                justify=tk.LEFT,
                bg=FUNDO_CARTAO,
            ).pack(fill=tk.X, pady=(8, 0))
            self._linhas_viajantes(cartao, dia["por_viajante"])

        tk.Frame(self._conteudo, height=12).pack()
        self._secao("Dados")
        self._texto(f"Valor total: {_reais(r['total'])}")
        for v in r["por_viajante"]:
            self._texto(f"{v['nome']} ({v['cotas']} cota(s)): {_reais(v['valor'])}")
        self._texto(f"Quantidade de dias: {r['quantidade_dias']}")
        self._texto(f"Cidades visitadas: {r['cidades_visitadas']}")
        self._texto(f"Data inicial: {r['data_inicial'] or '-'}")
        self._texto(f"Data final: {r['data_final'] or '-'}")