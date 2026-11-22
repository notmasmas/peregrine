import tkinter as tk
from collections.abc import Callable

POR_PAGINA = 3


class GrupoDetalheView(tk.Frame):
    def __init__(
        self,
        master: tk.Misc,
        nome_grupo: str,
        participantes: list[str],
        eh_organizador: bool,
        ao_voltar: Callable[[], None],
        ao_editar: Callable[[], None],
        ao_adicionar_acompanhante: Callable[[], None],
        ao_abrir_itinerario: Callable[[], None],
        ao_abrir_relatorio: Callable[[], None],
    ) -> None:
        super().__init__(master, padx=24, pady=24)
        self._participantes = participantes
        self._pagina = 0
        self.pack(fill=tk.BOTH, expand=True)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Cabeçalho
        cabecalho = tk.Frame(self)
        cabecalho.grid(row=0, column=0, columnspan=2, sticky="ew")
        cabecalho.grid_columnconfigure(1, weight=1)
        tk.Button(cabecalho, text="<", width=3, command=ao_voltar).grid(
            row=0, column=0
        )
        tk.Label(cabecalho, text="Grupo", fg="gray").grid(row=0, column=1)
        if eh_organizador:
            tk.Button(cabecalho, text="✎", width=3, command=ao_editar).grid(
                row=0, column=2
            )

        # Nome do grupo
        tk.Label(
            self, text=nome_grupo, font=("TkDefaultFont", 18, "bold"), wraplength=360
        ).grid(row=1, column=0, columnspan=2, pady=(24, 16))

        # Participantes (uma "linha" por pessoa, POR_PAGINA por página)
        self._area_participantes = tk.Frame(self)
        self._area_participantes.grid(row=2, column=0, columnspan=2, sticky="ew")
        self._area_participantes.grid_columnconfigure(0, weight=1)

        navegacao = tk.Frame(self)
        navegacao.grid(row=3, column=0, columnspan=2, sticky="e", pady=(8, 0))
        self._botao_anterior = tk.Button(
            navegacao, text="<", width=3, command=self._pagina_anterior
        )
        self._botao_anterior.pack(side=tk.LEFT)
        self._botao_proxima = tk.Button(
            navegacao, text=">", width=3, command=self._proxima_pagina
        )
        self._botao_proxima.pack(side=tk.LEFT, padx=(4, 0))

        tk.Button(
            self, text="+ Adicionar acompanhante", command=ao_adicionar_acompanhante
        ).grid(row=4, column=0, columnspan=2, sticky="w", pady=(16, 0))

        # Rodapé
        self.grid_rowconfigure(5, weight=1)
        tk.Button(self, text="Itinerário", command=ao_abrir_itinerario).grid(
            row=6, column=0, sticky="ew", padx=(0, 6), pady=(16, 0)
        )
        tk.Button(self, text="Relatório", command=ao_abrir_relatorio).grid(
            row=6, column=1, sticky="ew", padx=(6, 0), pady=(16, 0)
        )

        self._desenhar_pagina()

    def _desenhar_pagina(self) -> None:
        for filho in self._area_participantes.winfo_children():
            filho.destroy()

        inicio = self._pagina * POR_PAGINA
        for nome in self._participantes[inicio : inicio + POR_PAGINA]:
            tk.Label(
                self._area_participantes,
                text=f"👤  {nome}",
                anchor="w",
                bg="#e8eaed",
                padx=12,
                pady=10,
            ).pack(fill=tk.X, pady=4)

        ultima = (len(self._participantes) - 1) // POR_PAGINA
        self._botao_anterior.config(
            state=tk.NORMAL if self._pagina > 0 else tk.DISABLED
        )
        self._botao_proxima.config(
            state=tk.NORMAL if self._pagina < ultima else tk.DISABLED
        )

    def _pagina_anterior(self) -> None:
        self._pagina -= 1
        self._desenhar_pagina()

    def _proxima_pagina(self) -> None:
        self._pagina += 1
        self._desenhar_pagina()