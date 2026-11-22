import tkinter as tk
from tkinter import messagebox, simpledialog
from collections.abc import Callable
from dataclasses import dataclass
from functools import partial
from typing import Literal

from src.model.Acompanhante import Acompanhante

POR_PAGINA = 3


@dataclass(frozen=True)
class ParticipanteGrupo:
    id: int | None
    nome: str
    tipo: Literal["organizador", "participante", "acompanhante"]


class GrupoDetalheView(tk.Frame):
    def __init__(
        self,
        master: tk.Misc,
        nome_grupo: str,
        participantes: list[ParticipanteGrupo],
        eh_organizador: bool,
        ao_voltar: Callable[[], None],
        ao_renomear: Callable[[str], bool],
        ao_remover: Callable[[], None],
        ao_convidar_integrante: Callable[[str], None],
        ao_remover_participante: Callable[[ParticipanteGrupo], None],
        ao_adicionar_acompanhante: Callable[[], None],
        ao_abrir_itinerario: Callable[[], None],
        ao_abrir_relatorio: Callable[[], None],
    ) -> None:
        super().__init__(master, padx=24, pady=24)
        self._ao_renomear = ao_renomear
        self._ao_remover = ao_remover
        self._ao_convidar_integrante = ao_convidar_integrante
        self._ao_remover_participante = ao_remover_participante
        self._eh_organizador = eh_organizador
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
            botao_editar = tk.Menubutton(
                cabecalho, text="✎", relief=tk.RAISED, width=3
            )
            menu = tk.Menu(botao_editar, tearoff=0)
            menu.add_command(label="Renomear grupo", command=self._renomear)
            menu.add_command(label="Remover grupo", command=self._remover)
            botao_editar.config(menu=menu)
            botao_editar.grid(row=0, column=2)

        # Nome do grupo
        self._rotulo_nome = tk.Label(
            self, text=nome_grupo, font=("TkDefaultFont", 18, "bold"), wraplength=360
        )
        self._rotulo_nome.grid(row=1, column=0, columnspan=2, pady=(24, 16))

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

        if eh_organizador:
            acoes = tk.Frame(self)
            acoes.grid(row=4, column=0, columnspan=2, sticky="w", pady=(16, 0))
            tk.Button(
                acoes, text="+ Adicionar participante", command=self._convidar_integrante
            ).pack(side=tk.LEFT)
            tk.Button(
                acoes, text="+ Adicionar acompanhante", command=ao_adicionar_acompanhante
            ).pack(side=tk.LEFT, padx=(8, 0))

        # Rodapé
        self.grid_rowconfigure(5, weight=1)
        tk.Button(self, text="Itinerário", command=ao_abrir_itinerario).grid(
            row=6, column=0, sticky="ew", padx=(0, 6), pady=(16, 0)
        )
        tk.Button(self, text="Relatório", command=ao_abrir_relatorio).grid(
            row=6, column=1, sticky="ew", padx=(6, 0), pady=(16, 0)
        )

        self._desenhar_pagina()

    def selecionar_acompanhantes(self, acompanhantes: list[Acompanhante]) -> list[int]:
        if not acompanhantes:
            messagebox.showinfo(
                "Adicionar acompanhantes",
                "Nenhum acompanhante disponível para adicionar a este grupo.",
                parent=self,
            )
            return []

        dialogo = _SelecaoAcompanhantes(self, acompanhantes)
        return dialogo.result or []

    def adicionar_participantes(self, participantes: list[ParticipanteGrupo]) -> None:
        self._pagina = len(self._participantes) // POR_PAGINA
        self._participantes.extend(participantes)
        self._desenhar_pagina()

    def atualizar_participantes(self, participantes: list[ParticipanteGrupo]) -> None:
        self._participantes = participantes
        self._desenhar_pagina()

    def mostrar_erro(self, mensagem: str) -> None:
        messagebox.showerror("Peregrine", mensagem, parent=self)

    def mostrar_sucesso(self, mensagem: str) -> None:
        messagebox.showinfo("Peregrine", mensagem, parent=self)

    def _desenhar_pagina(self) -> None:
        for filho in self._area_participantes.winfo_children():
            filho.destroy()

        ultima = max(0, (len(self._participantes) - 1) // POR_PAGINA)
        self._pagina = min(self._pagina, ultima)
        inicio = self._pagina * POR_PAGINA
        for participante in self._participantes[inicio : inicio + POR_PAGINA]:
            linha = tk.Frame(self._area_participantes, bg="#e8eaed")
            linha.pack(fill=tk.X, pady=4)
            if self._eh_organizador and participante.tipo != "organizador":
                tk.Button(
                    linha,
                    text="×",
                    width=3,
                    command=partial(self._confirmar_remocao_participante, participante),
                ).pack(side=tk.RIGHT, padx=(0, 6))
            nome = participante.nome
            if participante.tipo != "participante":
                nome = f"{nome} ({participante.tipo})"
            tk.Label(
                linha,
                text=f"👤  {nome}",
                anchor="w",
                bg="#e8eaed",
                padx=12,
                pady=10,
            ).pack(side=tk.LEFT, fill=tk.X, expand=True)

        self._botao_anterior.config(
            state=tk.NORMAL if self._pagina > 0 else tk.DISABLED
        )
        self._botao_proxima.config(
            state=tk.NORMAL if self._pagina < ultima else tk.DISABLED
        )

    def _convidar_integrante(self) -> None:
        email = simpledialog.askstring(
            "Adicionar participante", "E-mail do viajante cadastrado", parent=self
        )
        if email is not None:
            self._ao_convidar_integrante(email)

    def _confirmar_remocao_participante(self, participante: ParticipanteGrupo) -> None:
        mensagem = f'Deseja remover "{participante.nome}" do grupo?'
        if participante.tipo == "participante":
            mensagem += "\nOs acompanhantes desse participante também sairão do grupo."
        if messagebox.askyesno(
            "Remover do grupo", mensagem, default=messagebox.NO, parent=self
        ):
            self._ao_remover_participante(participante)

    def _pagina_anterior(self) -> None:
        self._pagina -= 1
        self._desenhar_pagina()

    def _proxima_pagina(self) -> None:
        self._pagina += 1
        self._desenhar_pagina()
        
    def _renomear(self) -> None:
        nome = simpledialog.askstring(
            "Renomear grupo",
            "Novo nome do grupo (1 a 20 caracteres)",
            initialvalue=self._rotulo_nome.cget("text"),
            parent=self,
        )
        if nome is not None and self._ao_renomear(nome.strip()):
            self._rotulo_nome.config(text=nome.strip())

    def _remover(self) -> None:
        if messagebox.askyesno(
            "Remover grupo",
            "Deseja remover este grupo?",
            default=messagebox.NO,
            parent=self,
        ):
            self._ao_remover()


class _SelecaoAcompanhantes(simpledialog.Dialog):
    def __init__(self, master: tk.Misc, acompanhantes: list[Acompanhante]) -> None:
        self._acompanhantes = acompanhantes
        super().__init__(master, title="Adicionar acompanhantes")

    def body(self, master: tk.Misc) -> tk.Listbox:
        tk.Label(master, text="Selecione os acompanhantes para adicionar.").grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 8)
        )
        self._lista = tk.Listbox(
            master, selectmode=tk.MULTIPLE, height=min(len(self._acompanhantes), 8)
        )
        self._lista.grid(row=1, column=0, sticky="nsew")
        barra = tk.Scrollbar(master, command=self._lista.yview)
        barra.grid(row=1, column=1, sticky="ns")
        barra_horizontal = tk.Scrollbar(
            master, orient=tk.HORIZONTAL, command=self._lista.xview
        )
        barra_horizontal.grid(row=2, column=0, sticky="ew")
        self._lista.config(yscrollcommand=barra.set, xscrollcommand=barra_horizontal.set)

        for acompanhante in self._acompanhantes:
            responsavel = acompanhante.viajante_vinculado
            rotulo = acompanhante.nome
            if responsavel is not None:
                rotulo = f"{rotulo} — {responsavel.nome}"
            self._lista.insert(tk.END, rotulo)
        return self._lista

    def buttonbox(self) -> None:
        botoes = tk.Frame(self)
        botoes.pack(pady=(0, 8))
        tk.Button(botoes, text="Cancelar", command=self.cancel).pack(side=tk.LEFT)
        tk.Button(botoes, text="Adicionar", command=self.ok).pack(
            side=tk.LEFT, padx=(8, 0)
        )
        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

    def validate(self) -> bool:
        if not self._lista.curselection():
            messagebox.showerror(
                "Adicionar acompanhantes",
                "Selecione pelo menos um acompanhante.",
                parent=self,
            )
            return False
        return True

    def apply(self) -> None:
        self.result = [
            self._acompanhantes[indice].id for indice in self._lista.curselection()
        ]
