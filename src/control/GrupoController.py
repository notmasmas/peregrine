from collections.abc import Callable

from src.exception.CampoInvalidoException import CampoInvalidoException
from src.DAOs.GrupoDAO import GrupoDAO
from src.model.Grupo import Grupo
from src.model.Viajante import Viajante
from src.model.Convite import Convite
from src.model.StatusConvite import StatusConvite
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
            if len(dados["nome"]) == 0 or len(dados["nome"]) > 20:
                raise CampoInvalidoException("Nome de grupo inválido")

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
                registro = self._grupo_dao.criar_convite(
                    grupo.id,
                    email,
                    self._organizador.id,
                )
                Convite(
                    id=registro.id,
                    destinatario=self._para_viajante(registro.destinatario),
                    remetente=self._organizador,
                    grupo=grupo,
                    status=StatusConvite.PENDENTE,
                )
                enviar_email(self._organizador.nome, grupo.nome, email)
            except ValueError as e:
                nao_adicionados.append(f"{email} ({e})")
                continue

        return nao_adicionados

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
                grupo.nome, grupo.organizador.nome, integrantes
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

        email = self._tela.solicita_email()

        try:
            validate_email(email)
        except EmailNotValidError:
            self._tela.mostra_mensagem(
                "e-mail inserido é inválido - Por favor insira um endereço válido."
            )
            return False

        try:
            registro = self._grupo_dao.criar_convite(
                grupo.id,
                email,
                self._organizador.id,
            )
            Convite(
                id=registro.id,
                destinatario=self._para_viajante(registro.destinatario),
                remetente=self._organizador,
                grupo=grupo,
                status=StatusConvite.PENDENTE,
            )
            enviar_email(self._organizador.nome, grupo.nome, email)
        except ValueError as e:
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
            self._grupo_dao.remover_integrante(grupo.id, escolhido["id"])
        except ValueError as e:
            self._tela.mostra_mensagem(str(e))
            return False

        grupo.integrantes[:] = [i for i in grupo.integrantes if i.id != escolhido["id"]]
        self._tela.mostra_mensagem("Usuário excluído do grupo.")
        return True

    # ---------- GRUPOS DO ORGANIZADOR ----------

    def _buscar_grupos(self) -> list[Grupo]:
        registros = self._grupo_dao.listar_por_organizador(self._organizador.id)
        return [
            Grupo(
                id=r.id,
                nome=r.nome,
                organizador=self._organizador,
                sugestoes=r.sugestoes,
            )
            for r in registros
        ]

    def selecionar_grupo_para_gerenciar(self) -> None:
        grupos = self._buscar_grupos()
        if not grupos:
            self._tela.mostra_mensagem("Você ainda não organiza nenhum grupo.")
            return

        indice = self._tela.seleciona_grupo([g.nome for g in grupos])
        if indice is None:
            return

        self.gerenciar_grupo(grupos[indice])