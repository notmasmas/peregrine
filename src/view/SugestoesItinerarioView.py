import tkinter as tk
from collections.abc import Callable


class SugestoesItinerarioView(tk.Frame):
    def __init__(
        self,
        master: tk.Misc,
        sugestoes: list[dict],
        ao_voltar: Callable[[], None],
    ) -> None:
        super().__init__(master, padx=24, pady=24)
        self.pack(fill=tk.BOTH, expand=True)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        cabecalho = tk.Frame(self)
        cabecalho.grid(row=0, column=0, sticky="ew")
        cabecalho.grid_columnconfigure(1, weight=1)
        tk.Button(cabecalho, text="<", width=3, command=ao_voltar).grid(
            row=0, column=0, sticky=tk.W
        )
        tk.Label(
            cabecalho, text="Sugestões de itinerário", font=("TkDefaultFont", 14, "bold")
        ).grid(row=0, column=1)

        if not sugestoes:
            tk.Label(self, text="Nenhuma sugestão recebida.").grid(
                row=1, column=0, sticky=tk.N, pady=(24, 0)
            )
            return

        area = tk.Frame(self)
        area.grid(row=1, column=0, sticky="nsew", pady=(16, 0))
        area.grid_rowconfigure(0, weight=1)
        area.grid_columnconfigure(0, weight=1)
        canvas = tk.Canvas(area, highlightthickness=0)
        canvas.grid(row=0, column=0, sticky="nsew")
        barra = tk.Scrollbar(area, orient=tk.VERTICAL, command=canvas.yview)
        barra.grid(row=0, column=1, sticky="ns")
        canvas.configure(yscrollcommand=barra.set)

        lista = tk.Frame(canvas)
        janela = canvas.create_window((0, 0), window=lista, anchor="nw")
        lista.bind(
            "<Configure>",
            lambda evento: canvas.configure(
                scrollregion=(0, 0, evento.width, evento.height)
            ),
        )
        canvas.bind(
            "<Configure>",
            lambda evento: canvas.itemconfigure(janela, width=evento.width),
        )

        for sugestao in sugestoes:
            self._adicionar_cartao(lista, sugestao)

    @staticmethod
    def _adicionar_cartao(lista: tk.Frame, sugestao: dict) -> None:
        cartao = tk.Frame(lista, bg="#e8eaed")
        cartao.pack(fill=tk.X, pady=(0, 8))
        detalhes = tk.Frame(cartao, bg="#e8eaed", padx=12, pady=8)
        titulo = f"{sugestao['data']} · {sugestao['cidade']}\nSugerido por {sugestao['autor']}"

        def alternar_detalhes() -> None:
            if detalhes.winfo_manager():
                detalhes.pack_forget()
                botao.config(text=f"▸ {titulo}")
            else:
                detalhes.pack(fill=tk.X)
                botao.config(text=f"▾ {titulo}")

        botao = tk.Button(
            cartao, text=f"▸ {titulo}", command=alternar_detalhes,
            anchor=tk.W, justify=tk.LEFT, wraplength=252,
        )
        botao.pack(fill=tk.X)

        tk.Label(
            detalhes, text=sugestao["passeio"], wraplength=252, anchor=tk.W,
            justify=tk.LEFT, bg="#e8eaed", font=("TkDefaultFont", 10, "bold"),
        ).pack(fill=tk.X)

        for reserva in sugestao["reservas"]:
            preco = f"R$ {reserva['preco']:.2f}".replace(".", ",")
            tk.Label(
                detalhes,
                text=f"{reserva['nome']} · {preco}\nTitular {reserva['titular']}",
                wraplength=252, anchor=tk.W, justify=tk.LEFT, bg="#e8eaed",
            ).pack(fill=tk.X, pady=(6, 0))
