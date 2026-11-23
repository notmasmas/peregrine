from src.control.CustoController import CustoController
from src.control.ItinerarioController import ItinerarioController
from src.model.Grupo import Grupo

'''
User Cases implementados neste arquivo

Sarah Meireles
UC15: Emitir relatório da viagem
'''

class RelatorioController:
    def __init__(self) -> None:
        self._itinerario_controller = ItinerarioController()
        self._custo_controller = CustoController()

    def emitir(self, grupo: Grupo) -> dict:
        dias = self._itinerario_controller.listar_dias(grupo.id)
        custos = self._custo_controller.dividir_custos(grupo, dias)

        organizador = grupo.organizador
        membros = [organizador.nome] + [
            i.nome for i in grupo.integrantes if i.id != organizador.id
        ]

        dias_relatorio = []
        for numero, (dia, custo) in enumerate(zip(dias, custos["dias"]), start=1):
            dias_relatorio.append({"numero": numero, **dia, **custo})

        return {
            "nome_grupo": grupo.nome,
            "organizador": organizador.nome if organizador else "",
            "membros": membros,
            "acompanhantes": [a.nome for a in grupo.acompanhantes],
            "dias": dias_relatorio,
            "total": custos["total"],
            "por_viajante": custos["por_viajante"],
            "quantidade_dias": len(dias),
            "cidades_visitadas": len({d["cidade"].strip().lower() for d in dias}),
            "data_inicial": dias[0]["data"] if dias else None,
            "data_final": dias[-1]["data"] if dias else None,
        }