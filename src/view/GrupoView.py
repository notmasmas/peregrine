from src.view.View import View


class GrupoView(View):

    def cria_grupo(self) -> dict:
        valores_input = {"nome": input("Nome do grupo: "), "participantes": []}

        print("Participantes")
        while True:
            valores_input["participantes"].append(input("E-mail: "))
            continua = True if input("Adicionar mais? S/N ").upper() == "S" else False

            if not continua:
                break

        return valores_input

    def exibe_grupo(self, nome: str, organizador: str, integrantes: list[dict]) -> str:
        print(f"\nGrupo: {nome}")
        print(f"Organizador: {organizador}")
        print("Participantes:")
 
        if not integrantes:
            print("  (nenhum participante)")
        for numero, integrante in enumerate(integrantes, start=1):
            print(f"  {numero}. {integrante['nome']} - {integrante['email']}")
 
        print("\n1 - Adicionar viajante")
        print("2 - Selecionar participante")
        print("0 - Voltar")
        return input("Opção: ").strip()
 
    def solicita_email(self) -> str:
        return input("E-mail do viajante: ").strip()
 
    def seleciona_participante(self, integrantes: list[dict]) -> dict | None:
        escolha = input("Número do participante (0 para cancelar): ").strip()
 
        if escolha == "0":
            return None
        if not escolha.isdigit() or not 1 <= int(escolha) <= len(integrantes):
            self.mostra_mensagem("Participante inválido.")
            return None
 
        return integrantes[int(escolha) - 1]
 
    def solicita_acao_participante(self, nome: str) -> str:
        print(f"\nParticipante selecionado: {nome}")
        print("1 - Excluir viajante")
        print("0 - Voltar")
        return input("Opção: ").strip()
 
    def confirma_exclusao(self) -> bool:
        resposta = input("Você tem certeza que deseja excluir este usuário? S/N ")
        return resposta.strip().upper() == "S"
 
    # ---------- LISTAGEM E SELEÇÃO DE GRUPOS ----------
 
    def exibe_grupos(self, nomes: list[str]) -> None:
        print("\nMeus grupos:")
        for numero, nome in enumerate(nomes, start=1):
            print(f"  {numero}. {nome}")
 
    def seleciona_grupo(self, nomes: list[str]) -> int | None:
        self.exibe_grupos(nomes)
        escolha = input("Número do grupo (0 para voltar): ").strip()
 
        if escolha == "0":
            return None
        if not escolha.isdigit() or not 1 <= int(escolha) <= len(nomes):
            self.mostra_mensagem("Grupo inválido.")
            return None
 
        return int(escolha) - 1