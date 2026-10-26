from src.exception.CampoInvalidoException import CampoInvalidoException
from src.DAOs.GrupoDAO import GrupoDAO
from src.model.Grupo import Grupo
from src.model.Viajante import Viajante
from src.view.GrupoView import GrupoView
from email_validator import validate_email, EmailNotValidError

class GrupoController:

    def __init__(
        self,
        organizador: Viajante,
    ) -> None:
        self._organizador = organizador
        self._grupo_dao = GrupoDAO()
        self._tela = GrupoView()

    def criar_grupo(self) -> None:
        dados = self._tela.cria_grupo()

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
            self._tela.mostra_mensagem("Deve conter no mínimo um e-mail válido")
            return

        except ValueError as e:
            self._tela.mostra_mensagem(str(e))
            return

        except CampoInvalidoException as e:
            self._tela.mostra_mensagem(str(e))

        else:
            nao_adicionados = self._adicionar_participantes_iniciais(
                grupo, dados["participantes"]
            )
            self._tela.mostra_mensagem("Grupo criado com sucesso.")
            if nao_adicionados:
                self._tela.mostra_mensagem(
                    "Não foi possível adicionar: " + "; ".join(nao_adicionados)
                )

    # ---------- NOVOS MÉTODOS ----------

    def _para_viajante(self, registro) -> Viajante:
        return Viajante(
            id=registro.id,
            nome=registro.nome,
            idade=registro.idade,
            email=registro.email,
            senha=registro.senha,
        )

    def _adicionar_participantes_iniciais(
        self, grupo: Grupo, emails: list[str]
    ) -> list[str]:
        """Adiciona cada e-mail ao grupo recém-criado e devolve os que falharam (com o motivo)."""
        nao_adicionados = []

        for email in emails:
            try:
                registro = self._grupo_dao.adicionar_integrante(grupo.id, email)
            except ValueError as e:
                nao_adicionados.append(f"{email} ({e})")
                continue

            grupo.integrantes.append(self._para_viajante(registro))

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
        """Retorna True se o viajante foi adicionado; False se o fluxo voltou para a tela do grupo."""
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
            registro = self._grupo_dao.adicionar_integrante(grupo.id, email)
        except ValueError as e:
            self._tela.mostra_mensagem(str(e))
            return False

        grupo.integrantes.append(self._para_viajante(registro))
        self._tela.mostra_mensagem("Convite enviado com sucesso")
        return True

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