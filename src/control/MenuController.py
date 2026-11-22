import tkinter as tk
from typing import Optional
from collections.abc import Callable
from src.model.Viajante import Viajante
from src.model.Grupo import Grupo
from src.view.MenuView import MenuView
from src.view.GrupoDetalheView import GrupoDetalheView
from src.control.AcompanhanteController import AcompanhanteController
from src.control.GrupoController import GrupoController
from src.exception.CampoInvalidoException import CampoInvalidoException


class MenuController:

    def __init__(
        self,
        root: tk.Tk,
        viajante: Viajante,
        ao_sair: Callable[[], None],
    ) -> None:
        self._root = root
        self._viajante_logado: Viajante = viajante
        self._acompanhante_controller: Optional[AcompanhanteController]= None
        self._grupo_controller = GrupoController(viajante)
        self._ao_sair = ao_sair
        self._grupos_por_id: dict[int, Grupo] = {}
        self._tela_grupo: Optional[GrupoDetalheView] = None
        self._tela = MenuView(
            root,
            nome_viajante=viajante.nome,
            ao_criar_grupo=self._criar_grupo,
            ao_listar_grupos=self._listar_grupos,
            ao_abrir_acompanhante=self._abrir_acompanhante,
            ao_listar_convites=self._listar_convites,
            ao_aceitar_convite=self._aceitar_convite,
            ao_rejeitar_convite=self._rejeitar_convite,
            ao_sair=self._sair_do_menu,
            ao_abrir_grupo=self._abrir_grupo,
        )

    def _abrir_acompanhante(self) -> None:
        viajante = self._viajante_logado
        if viajante is None:
            self._tela.mostrar_erro("Faça login antes de abrir a tela de acompanhantes.")
            return

        self._acompanhante_controller = AcompanhanteController(
            self._root, viajante, ao_sair=self._voltar_ao_menu
        )
        self._tela.pack_forget()

    def _voltar_ao_menu(self) -> None:
        self._acompanhante_controller = None
        self._tela.pack(fill=tk.BOTH, expand=True)
        self._tela.mostrar_inicio()

    def _sair_do_menu(self) -> None:
        self._tela.destroy()
        self._ao_sair()

    def _criar_grupo(self, nome: str, participantes: list[str]) -> bool:
        return self._grupo_controller.criar_grupo(
            {"nome": nome, "participantes": participantes},
            mostrar_erro=self._tela.mostrar_erro,
            mostrar_sucesso=self._tela.mostrar_sucesso,
        )
    
    def _abrir_grupo(self, grupo_id: int) -> None:
        grupo = self._grupos_por_id.get(grupo_id)
        if grupo is None:
            self._tela.mostrar_erro("Grupo não encontrado.")
            return

        eh_organizador = grupo.organizador.id == self._viajante_logado.id
        nomes = [f"{grupo.organizador.nome} (organizador)"]
        nomes += [i.nome for i in grupo.integrantes]

        self._tela.pack_forget()
        self._tela_grupo = GrupoDetalheView(
            self._root,
            nome_grupo=grupo.nome,
            participantes=nomes,
            eh_organizador=eh_organizador,
            ao_voltar=self._voltar_do_grupo,
            ao_renomear=lambda nome: self._editar_grupo(grupo.id, nome),
            ao_remover=lambda: self._remover_e_voltar(grupo.id),
            ao_adicionar_acompanhante=self._em_breve,
            ao_abrir_itinerario=self._em_breve,
            ao_abrir_relatorio=self._em_breve,
        )
        
    def _voltar_do_grupo(self) -> None:
        if self._tela_grupo is not None:
            self._tela_grupo.destroy()
            self._tela_grupo = None
        self._tela.pack(fill=tk.BOTH, expand=True)
        self._tela.mostrar_inicio()
    
    def _remover_e_voltar(self, grupo_id: int) -> None:
        if self._remover_grupo(grupo_id):
            self._voltar_do_grupo()
    
    def _em_breve(self) -> None:
        self._tela.mostrar_sucesso("Funcionalidade em desenvolvimento.")
    
    @staticmethod
    def _resumo_grupo(grupo: Grupo) -> dict:
        return {"id": grupo.id, "nome": grupo.nome}

    def _listar_convites(self) -> list[dict]:
        return self._grupo_controller.listar_convites_pendentes()

    def _aceitar_convite(self, convite_id: int) -> bool:
        return self._grupo_controller.aceitar_convite(convite_id)

    def _rejeitar_convite(self, convite_id: int) -> bool:
        return self._grupo_controller.rejeitar_convite(convite_id)

    def _listar_grupos(self) -> tuple[list[dict], list[dict]]:
        grupos = self._grupo_controller.listar_meus_grupos()
        todos = grupos["organizados"] + grupos["participando"]
        self._grupos_por_id = {g.id: g for g in todos}
        return (
            [self._resumo_grupo(g) for g in grupos["organizados"]],
            [self._resumo_grupo(g) for g in grupos["participando"]],
        )

    def _editar_grupo(self, grupo_id: int, nome: str) -> bool:
        try:
            self._grupo_controller.editar_grupo(grupo_id, nome)
        except (CampoInvalidoException, ValueError) as e:
            self._tela.mostrar_erro(str(e))
            return False

        self._tela.mostrar_sucesso("Grupo atualizado com sucesso.")
        return True

    def _remover_grupo(self, grupo_id: int) -> bool:
        try:
            self._grupo_controller.remover_grupo(grupo_id)
        except ValueError as e:
            self._tela.mostrar_erro(str(e))
            return False

        self._tela.mostrar_sucesso("Grupo removido com sucesso.")
        return True
