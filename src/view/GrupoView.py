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