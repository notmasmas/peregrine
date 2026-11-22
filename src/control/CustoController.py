# UC14: Dividir custos da viagem entre membros do grupo (Implementado por Sarah Meireles)

from src.DAOs.CustoDAO import CustoDAO
from src.model.Grupo import Grupo


class CustoController:
    def __init__(self) -> None:
        self._custo_dao = CustoDAO()

    def dividir_custos(self, grupo: Grupo, dias: list[dict]) -> dict:
        organizador = grupo.organizador
        membros = [organizador] + [
            i for i in grupo.integrantes if i.id != organizador.id
        ]
        ids = {m.id for m in membros}
        
        responsaveis = [
            r for r in self._custo_dao.listar_responsaveis_acompanhantes(grupo.id)
            if r in ids
        ]
        cotas_por_membro = {m.id: 1 + responsaveis.count(m.id) for m in membros}
        total_cotas = max(1, sum(cotas_por_membro.values()))
        
        def dividir(centavos:int) -> dict:
            por_cota = -(-centavos // total_cotas) # arredonda centavos para cima
            return {
                    "total": centavos / 100,
                    "por_pessoa": por_cota / 100,
                    "por_viajante": [
                        {
                            "nome": m.nome,
                            "cotas": cotas_por_membro[m.id],
                            "valor": por_cota * cotas_por_membro[m.id] / 100,
                        }
                        for m in membros
                    ],
                }
            
        dias_calculados = []
        total_geral = 0
        for dia in dias:
            total_dia = 0
            reservas = []
            for r in dia.get("reservas", []):
                centavos = round(r["preco"] * 100)
                total_dia += centavos
                reservas.append({"nome": r["nome"], **dividir(centavos)})
            total_geral += total_dia
            dias_calculados.append({**dividir(total_dia), "reservas": reservas})

        return {"cotas": total_cotas, **dividir(total_geral), "dias": dias_calculados}