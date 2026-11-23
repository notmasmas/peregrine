from collections.abc import Callable

from src.exception.CampoInvalidoException import CampoInvalidoException
from src.DAOs.GrupoDAO import GrupoDAO
from src.model.Acompanhante import Acompanhante
from src.model.Grupo import Grupo
from src.model.Viajante import Viajante
from src.view.GrupoView import GrupoView
from email_validator import validate_email, EmailNotValidError
from src.util.email import enviar_email

class GrupoController:

    def __init__(
        self,
        organizador: Viajante,
    ) -> None:
        self._organizador = organizador
        self._grupo_dao = GrupoDAO()
        self._tela = GrupoView()

    def _validar_nome(self, nome: str) -> None:
        if not 1 <= len(nome) <= 20:
            raise CampoInvalidoException("Nome de grupo inválido")

    # UC03: Criar grupo de viagem (Implementado por Maria Helena Melo)
    
    def criar_grupo(
        self,
        dados: dict | None = None,
        *,
        mostrar_erro: Callable[[str], None] | None = None,
        mostrar_sucesso: Callable[[str], None] | None = None,
    ) -> bool:
        if dados is None:
            dados = self._tela.cria_grupo()

        ao_mostrar_erro = (
            self._tela.mostra_mensagem
            if mostrar_erro is None
            else mostrar_erro
        )
        ao_mostrar_sucesso = (
            self._tela.mostra_mensagem
            if mostrar_sucesso is None
            else mostrar_sucesso
        )

        try:
            self._validar_nome(dados["nome"])

            if len(dados["participantes"]) == 0:
                raise CampoInvalidoException("Deve conter no mínimo um e-mail válido")

            for email in dados["participantes"]:
                validate_email(email)

            grupo = Grupo(nome=dados["nome"],
                          organizador=self._organizador)

            self._grupo_dao.criar(grupo)
            self._organizador.grupos_organizador.append(grupo)

        except EmailNotValidError:
            ao_mostrar_erro("Deve conter no mínimo um e-mail válido")
            return False

        except ValueError as e:
            ao_mostrar_erro(str(e))
            return False

        except CampoInvalidoException as e:
            ao_mostrar_erro(str(e))
            return False

        else:
            nao_adicionados = self._adicionar_participantes_iniciais(
                grupo, dados["participantes"]
            )
            ao_mostrar_sucesso("Grupo criado com sucesso.")
            if nao_adicionados:
                ao_mostrar_erro(
                    "Não foi possível adicionar: " + "; ".join(nao_adicionados)
                )
            return True

    # UC06: Convidar, visualizar e excluir viajantes (Implementado por Gustavo de Pinho)

    def _para_viajante(self, registro) -> Viajante:
        return Viajante(
            id=registro.id,
            nome=registro.nome,
            data_nascimento=registro.data_nascimento,
            email=registro.email,
            senha=registro.senha,
        )

    def _adicionar_participantes_iniciais(
        self, grupo: Grupo, emails: list[str]
    ) -> list[str]:
        """Convida cada e-mail para o grupo recém-criado e devolve os que falharam."""
        nao_adicionados = []

        for email in emails:
            try:
                self._enviar_convite(grupo, email)
            except ValueError as e:
                nao_adicionados.append(f"{email} ({e})")
                continue

        return nao_adicionados

    def _enviar_convite(self, grupo: Grupo, email: str) -> None:
        self._grupo_dao.criar_convite(grupo.id, email, self._organizador.id)
        enviar_email(self._organizador.nome, grupo.nome, email)

    def convidar_integrante(self, grupo: Grupo, email: str) -> None:
        email = email.strip().lower()
        try:
            validate_email(email, check_deliverability=False)
        except EmailNotValidError as erro:
            raise CampoInvalidoException("Informe um e-mail válido.") from erro

        self._enviar_convite(grupo, email)

    def _eh_organizador(self, grupo: Grupo) -> bool:
        return (
            grupo.organizador is not None
            and grupo.organizador.id == self._organizador.id
        )

    def gerenciar_grupo(self, grupo: Grupo) -> None:
        """Tela do grupo: exibe participantes e direciona para adicionar/excluir/voltar."""
        while True:
            try:
                registros = self._grupo_dao.listar_integrantes(grupo.id)
            except ValueError as e:
                self._tela.mostra_mensagem(str(e))
                return

            integrantes = [
                {"id": r.id, "nome": r.nome, "email": r.email} for r in registros
            ]
            opcao = self._tela.exibe_grupo(
                grupo.nome, grupo.organizador.nome, integrantes,
                eh_organizador=self._eh_organizador(grupo),
            )

            if opcao == "0":  # Voltar tela anterior
                return

            if opcao == "1":
                if self.adicionar_integrante(grupo):
                    return  # convite enviado -> fim do fluxo
            elif opcao == "2":
                if self.excluir_integrante(grupo, integrantes):
                    return  # usuário excluído -> fim do fluxo
            else:
                self._tela.mostra_mensagem("Opção inválida.")

    def adicionar_integrante(self, grupo: Grupo) -> bool:
        """Cria um convite pendente; o viajante só entra no grupo após aceitar."""
        if not self._eh_organizador(grupo):
            self._tela.mostra_mensagem(
                "Apenas o organizador do grupo pode adicionar viajantes."
            )
            return False

        try:
            self.convidar_integrante(grupo, self._tela.solicita_email())
        except (CampoInvalidoException, ValueError) as e:
            self._tela.mostra_mensagem(str(e))
            return False

        self._tela.mostra_mensagem("Convite enviado com sucesso")
        return True

    def aceitar_convite(self, convite_id: int) -> bool:
        """Aceita um convite como o viajante atualmente logado."""
        try:
            self._grupo_dao.aceitar_convite(convite_id, self._organizador.id)
        except ValueError as e:
            self._tela.mostra_mensagem(str(e))
            return False

        self._tela.mostra_mensagem("Convite aceito com sucesso.")
        return True

    def rejeitar_convite(self, convite_id: int) -> bool:
        """Rejeita um convite como o viajante atualmente logado."""
        try:
            self._grupo_dao.rejeitar_convite(convite_id, self._organizador.id)
        except ValueError as e:
            self._tela.mostra_mensagem(str(e))
            return False

        self._tela.mostra_mensagem("Convite rejeitado.")
        return True

    def listar_convites_pendentes(self) -> list[dict]:
        """Lista os convites pendentes do viajante logado com o nome do grupo."""
        registros = self._grupo_dao.listar_convites_pendentes(
            self._organizador.id
        )
        return [
            {
                "id": convite.id,
                "nome_grupo": convite.grupo.nome,
            }
            for convite in registros
        ]

    def excluir_integrante(self, grupo: Grupo, integrantes: list[dict]) -> bool:
        """Retorna True se o viajante foi excluído; False se a operação foi cancelada."""
        if not self._eh_organizador(grupo):
            self._tela.mostra_mensagem(
                "Apenas o organizador do grupo pode excluir viajantes."
            )
            return False

        if not integrantes:
            self._tela.mostra_mensagem("O grupo ainda não possui participantes.")
            return False

        escolhido = self._tela.seleciona_participante(integrantes)
        if escolhido is None:
            return False

        if self._tela.solicita_acao_participante(escolhido["nome"]) != "1":
            return False

        if not self._tela.confirma_exclusao():
            self._tela.mostra_mensagem("Operação cancelada.")
            return False

        try:
            self.remover_integrante(grupo, escolhido["id"])
        except ValueError as e:
            self._tela.mostra_mensagem(str(e))
            return False

        self._tela.mostra_mensagem("Usuário excluído do grupo.")
        return True

    def remover_integrante(self, grupo: Grupo, viajante_id: int) -> None:
        acompanhantes_removidos = self._grupo_dao.remover_integrante(
            grupo.id, viajante_id, self._organizador.id
        )
        grupo.integrantes[:] = [i for i in grupo.integrantes if i.id != viajante_id]
        grupo.acompanhantes[:] = [
            a for a in grupo.acompanhantes if a.id not in acompanhantes_removidos
        ]

    def sair_do_grupo(self, grupo: Grupo) -> None:
        if grupo.id is None:
            raise ValueError("Grupo não encontrado.")
        acompanhantes_removidos = self._grupo_dao.sair_do_grupo(
            grupo.id, self._organizador.id
        )
        viajante_id = self._organizador.id
        grupo.integrantes[:] = [
            integrante
            for integrante in grupo.integrantes
            if integrante.id != viajante_id
        ]
        grupo.acompanhantes[:] = [
            acompanhante
            for acompanhante in grupo.acompanhantes
            if acompanhante.id not in acompanhantes_removidos
        ]

    def remover_acompanhante(self, grupo: Grupo, acompanhante_id: int) -> None:
        self._grupo_dao.remover_acompanhante(
            grupo.id, acompanhante_id, self._organizador.id
        )
        grupo.acompanhantes[:] = [
            a for a in grupo.acompanhantes if a.id != acompanhante_id
        ]

    # ---------- GRUPOS DO ORGANIZADOR ----------

    def listar_grupos_organizados(self) -> list[Grupo]:
        registros = self._grupo_dao.listar_por_organizador(self._organizador.id)
        return [self._para_grupo(r) for r in registros]

    def _selecionar_grupo(self) -> Grupo | None:
        grupos = self.listar_grupos_organizados()
        if not grupos:
            self._tela.mostra_mensagem("Você ainda não organiza nenhum grupo.")
            return None

        indice = self._tela.seleciona_grupo([g.nome for g in grupos])
        return grupos[indice] if indice is not None else None

    def selecionar_grupo_para_gerenciar(self) -> None:
        grupo = self._selecionar_grupo()
        if grupo is not None:
            self.gerenciar_grupo(grupo)

    def editar_grupo(self, grupo_id: int, nome: str) -> None:
        self._validar_nome(nome)
        self._grupo_dao.atualizar_nome(grupo_id, self._organizador.id, nome)

        for grupo_organizado in self._organizador.grupos_organizador:
            if grupo_organizado.id == grupo_id:
                grupo_organizado.nome = nome

    def remover_grupo(self, grupo_id: int) -> None:
        self._grupo_dao.remover(grupo_id, self._organizador.id)
        self._organizador.grupos_organizador[:] = [
            g for g in self._organizador.grupos_organizador if g.id != grupo_id
        ]

    def listar_acompanhantes(self, grupo_id: int) -> list[Acompanhante]:
        return [
            Acompanhante(id=registro.id, nome=registro.nome)
            for registro in self._grupo_dao.listar_acompanhantes(
                grupo_id, self._organizador.id
            )
        ]

    def listar_acompanhantes_disponiveis(self, grupo_id: int) -> list[Acompanhante]:
        registros = self._grupo_dao.listar_acompanhantes_disponiveis(
            grupo_id, self._organizador.id
        )
        return [
            Acompanhante(
                id=registro.id,
                nome=registro.nome,
                viajante_vinculado=Viajante(
                    id=registro.viajante_id, nome=registro.viajante_vinculado.nome
                ),
            )
            for registro in registros
        ]

    def adicionar_acompanhantes(self, grupo_id: int, acompanhante_ids: list[int]) -> None:
        self._grupo_dao.adicionar_acompanhantes(
            grupo_id, self._organizador.id, acompanhante_ids
        )
        
    # UC07: Visualizar grupos de viagem (Implementado por Sarah Meireles)
    
    def _para_grupo(self, registro) -> Grupo:
        eh_organizador = registro.organizador_id == self._organizador.id
        if eh_organizador:
            organizador = self._organizador
        elif registro.organizador is not None:
            organizador = self._para_viajante(registro.organizador)
        else:
            organizador = None
            
        return Grupo(
            id=registro.id,
            nome=registro.nome,
            organizador=organizador,
            integrantes=[self._para_viajante(i) for i in registro.integrantes],
            sugestoes=(registro.sugestoes or {}) if eh_organizador else {},
        )
        
    def listar_meus_grupos(self) -> dict[str, list[Grupo]]:
        organizados = self._grupo_dao.listar_por_organizador(self._organizador.id)
        participando = self._grupo_dao.listar_por_participante(self._organizador.id)
        
        return {
            "organizados": [self._para_grupo(r) for r in organizados],
            "participando": [self._para_grupo(r) for r in participando],
        }
