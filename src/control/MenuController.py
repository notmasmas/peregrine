import tkinter as tk
from typing import Optional
from collections.abc import Callable

from sqlalchemy.exc import SQLAlchemyError

from src.model.Acompanhante import Acompanhante
from src.model.Viajante import Viajante
from src.model.Grupo import Grupo
from src.view.MenuView import MenuView
from src.view.GrupoDetalheView import GrupoDetalheView, ParticipanteGrupo
from src.control.AcompanhanteController import AcompanhanteController
from src.control.GrupoController import GrupoController
from src.control.ItinerarioController import ItinerarioController
from src.exception.CampoInvalidoException import CampoInvalidoException
from src.view.ItinerarioView import ItinerarioView


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
        self._itinerario_controller = ItinerarioController()
        self._ao_sair = ao_sair
        self._grupos_por_id: dict[int, Grupo] = {}
        self._tela_grupo: Optional[GrupoDetalheView] = None
        self._tela_itinerario: Optional[ItinerarioView] = None
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

        try:
            grupo.acompanhantes[:] = self._grupo_controller.listar_acompanhantes(grupo_id)
        except ValueError as erro:
            self._tela.mostrar_erro(str(erro))
            return
        except SQLAlchemyError:
            self._tela.mostrar_erro("Não foi possível carregar os acompanhantes do grupo.")
            return

        organizador = grupo.organizador
        eh_organizador = (
            organizador is not None and organizador.id == self._viajante_logado.id
        )
        self._tela.pack_forget()
        self._tela_grupo = GrupoDetalheView(
            self._root,
            nome_grupo=grupo.nome,
            participantes=self._participantes_do_grupo(grupo),
            eh_organizador=eh_organizador,
            ao_voltar=self._voltar_do_grupo,
            ao_renomear=lambda nome: self._editar_grupo(grupo.id, nome),
            ao_remover=lambda: self._remover_e_voltar(grupo.id),
            ao_convidar_integrante=lambda email: self._convidar_integrante(grupo, email),
            ao_remover_participante=lambda item: self._remover_participante(grupo, item),
            ao_adicionar_acompanhante=lambda: self._adicionar_acompanhantes(grupo),
            ao_abrir_itinerario=lambda: self._abrir_itinerario(grupo),
            ao_abrir_relatorio=self._em_breve,
            ao_sair_do_grupo=lambda: self._sair_do_grupo(grupo),
        )

    def _abrir_itinerario(self, grupo: Grupo) -> None:
        tela_grupo = self._tela_grupo
        if tela_grupo is None:
            return
        if grupo.id is None:
            tela_grupo.mostrar_erro("Grupo não encontrado.")
            return
        grupo_id = grupo.id

        try:
            dias = self._itinerario_controller.listar_dias(grupo_id)
        except ValueError as erro:
            tela_grupo.mostrar_erro(str(erro))
            return
        except SQLAlchemyError:
            tela_grupo.mostrar_erro("Não foi possível carregar o itinerário do grupo.")
            return

        tela_grupo.pack_forget()
        self._tela_itinerario = ItinerarioView(
            self._root,
            nome_grupo=grupo.nome,
            dias=dias,
            ao_voltar=self._voltar_do_itinerario,
            participantes=self._participantes_reserva(grupo),
            pode_adicionar=(
                grupo.organizador is not None
                and grupo.organizador.id == self._viajante_logado.id
            ),
            ao_adicionar=lambda dados: self._adicionar_dia_itinerario(
                grupo_id, dados
            ),
            ao_editar=lambda data_original, dados: self._editar_dia_itinerario(
                grupo_id, data_original, dados
            ),
            ao_remover=lambda datas: self._remover_dias_itinerario(
                grupo_id, datas
            ),
        )

    @staticmethod
    def _participantes_reserva(grupo: Grupo) -> list[tuple[int, str]]:
        viajantes = ([grupo.organizador] if grupo.organizador is not None else [])
        viajantes.extend(grupo.integrantes)
        participantes: list[tuple[int, str]] = []
        ids_adicionados: set[int] = set()
        for viajante in viajantes:
            if viajante.id is not None and viajante.id not in ids_adicionados:
                participantes.append((viajante.id, viajante.nome))
                ids_adicionados.add(viajante.id)
        return participantes

    def _adicionar_dia_itinerario(self, grupo_id: int, dados: dict) -> bool:
        tela = self._tela_itinerario
        if tela is None:
            return False
        viajante_id = self._viajante_logado.id
        if viajante_id is None:
            tela.mostrar_erro("Faça login antes de adicionar ao itinerário.")
            return False
        try:
            self._itinerario_controller.adicionar_dia(
                grupo_id, viajante_id, dados
            )
        except ValueError as erro:
            tela.mostrar_erro(str(erro))
            return False
        except SQLAlchemyError:
            tela.mostrar_erro("Não foi possível adicionar o dia ao itinerário.")
            return False
        return True

    def _editar_dia_itinerario(
        self, grupo_id: int, data_original: str, dados: dict
    ) -> bool:
        tela = self._tela_itinerario
        if tela is None:
            return False
        try:
            self._itinerario_controller.editar_dia(
                grupo_id, data_original, dados
            )
        except ValueError as erro:
            tela.mostrar_erro(str(erro))
            return False
        except SQLAlchemyError:
            tela.mostrar_erro("Não foi possível editar o dia do itinerário.")
            return False
        return True

    def _remover_dias_itinerario(
        self, grupo_id: int, datas: list[str]
    ) -> bool:
        tela = self._tela_itinerario
        if tela is None:
            return False
        try:
            self._itinerario_controller.remover_dias(grupo_id, datas)
        except ValueError as erro:
            tela.mostrar_erro(str(erro))
            return False
        except SQLAlchemyError:
            tela.mostrar_erro("Não foi possível remover os dias do itinerário.")
            return False
        return True

    def _voltar_do_itinerario(self) -> None:
        if self._tela_itinerario is not None:
            self._tela_itinerario.destroy()
            self._tela_itinerario = None
        if self._tela_grupo is not None:
            self._tela_grupo.pack(fill=tk.BOTH, expand=True)

    @staticmethod
    def _itens_acompanhantes(acompanhantes: list[Acompanhante]) -> list[ParticipanteGrupo]:
        return [ParticipanteGrupo(a.id, a.nome, "acompanhante") for a in acompanhantes]

    def _participantes_do_grupo(self, grupo: Grupo) -> list[ParticipanteGrupo]:
        organizador = grupo.organizador
        participantes = [
            ParticipanteGrupo(integrante.id, integrante.nome, "participante")
            for integrante in grupo.integrantes
            if organizador is None or integrante.id != organizador.id
        ]
        if organizador is not None:
            participantes.insert(
                0, ParticipanteGrupo(organizador.id, organizador.nome, "organizador")
            )
        return participantes + self._itens_acompanhantes(grupo.acompanhantes)

    def _convidar_integrante(self, grupo: Grupo, email: str) -> None:
        tela = self._tela_grupo
        if tela is None:
            return

        try:
            self._grupo_controller.convidar_integrante(grupo, email)
        except (CampoInvalidoException, ValueError) as erro:
            tela.mostrar_erro(str(erro))
            return
        except SQLAlchemyError:
            tela.mostrar_erro("Não foi possível enviar o convite.")
            return

        tela.mostrar_sucesso("Convite criado. O participante entrará no grupo após aceitar.")

    def _remover_participante(self, grupo: Grupo, item: ParticipanteGrupo) -> None:
        tela = self._tela_grupo
        if tela is None or item.id is None or item.tipo == "organizador":
            return

        try:
            if item.tipo == "acompanhante":
                self._grupo_controller.remover_acompanhante(grupo, item.id)
            else:
                self._grupo_controller.remover_integrante(grupo, item.id)
        except ValueError as erro:
            tela.mostrar_erro(str(erro))
            return
        except SQLAlchemyError:
            tela.mostrar_erro("Não foi possível remover do grupo.")
            return

        tela.atualizar_participantes(self._participantes_do_grupo(grupo))

    def _sair_do_grupo(self, grupo: Grupo) -> None:
        tela = self._tela_grupo
        if tela is None:
            return
        try:
            self._grupo_controller.sair_do_grupo(grupo)
        except ValueError as erro:
            tela.mostrar_erro(str(erro))
            return
        except SQLAlchemyError:
            tela.mostrar_erro("Não foi possível sair do grupo.")
            return

        tela.mostrar_sucesso("Você saiu do grupo.")
        self._voltar_do_grupo()

    def _adicionar_acompanhantes(self, grupo: Grupo) -> None:
        tela = self._tela_grupo
        if tela is None or grupo.id is None:
            return

        try:
            disponiveis = self._grupo_controller.listar_acompanhantes_disponiveis(grupo.id)
            ids = tela.selecionar_acompanhantes(disponiveis)
            if not ids:
                return
            self._grupo_controller.adicionar_acompanhantes(grupo.id, ids)
        except ValueError as erro:
            tela.mostrar_erro(str(erro))
            return
        except SQLAlchemyError:
            tela.mostrar_erro("Não foi possível adicionar os acompanhantes ao grupo.")
            return

        selecionados = set(ids)
        adicionados = [
            acompanhante for acompanhante in disponiveis
            if acompanhante.id in selecionados
        ]
        grupo.acompanhantes.extend(adicionados)
        tela.adicionar_participantes(self._itens_acompanhantes(adicionados))
        
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

        grupo = self._grupos_por_id.get(grupo_id)
        if grupo is not None:
            grupo.nome = nome
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
