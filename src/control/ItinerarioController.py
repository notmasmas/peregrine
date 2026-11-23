from datetime import date

from src.DAOs.ItinerarioDAO import ItinerarioDAO


class ItinerarioController:
    def __init__(self) -> None:
        self._itinerario_dao = ItinerarioDAO()

    def listar_dias(self, grupo_id: int) -> list[dict[str, str]]:
        programacao = self._itinerario_dao.listar_programacao(grupo_id)
        reservas_por_dia = self._itinerario_dao.listar_reservas_por_dia(grupo_id)
        if not isinstance(programacao, dict) or any(
            not isinstance(data, str) for data in programacao
        ):
            raise ValueError("A programação do itinerário está inválida.")

        dias = []
        for data in sorted(programacao):
            detalhes = programacao[data]
            if not isinstance(detalhes, dict):
                raise ValueError("A programação do itinerário está inválida.")

            try:
                data_formatada = date.fromisoformat(data).strftime("%d/%m/%Y")
            except ValueError as erro:
                raise ValueError(
                    f"A data {data!r} no itinerário está inválida."
                ) from erro

            passeio = detalhes.get("passeio")
            cidade = detalhes.get("cidade")
            if not isinstance(passeio, str) or not isinstance(cidade, str):
                raise ValueError(
                    f"O passeio e a cidade de {data_formatada} são obrigatórios."
                )

            dias.append(
                {
                    "data": data_formatada,
                    "passeio": passeio,
                    "cidade": cidade,
                    "reservas": reservas_por_dia.get(data, []),
                }
            )

        return dias

    def adicionar_dia(
        self, grupo_id: int, viajante_id: int, dados: dict
    ) -> None:
        data, cidade, passeio, reservas = self._normalizar_dia(dados)
        self._itinerario_dao.adicionar_dia(
            grupo_id, viajante_id, data, cidade, passeio, reservas
        )

    def sugerir_dia(self, grupo_id: int, viajante_id: int, dados: dict) -> None:
        data, cidade, passeio, reservas = self._normalizar_dia(dados)
        self._itinerario_dao.sugerir_dia(
            grupo_id, viajante_id, data, cidade, passeio, reservas
        )

    def listar_sugestoes(self, grupo_id: int, viajante_id: int) -> list[dict]:
        sugestoes = self._itinerario_dao.listar_sugestoes(grupo_id, viajante_id)
        try:
            return [
                {
                    **sugestao,
                    "data": date.fromisoformat(sugestao["data"]).strftime("%d/%m/%Y"),
                }
                for sugestao in sugestoes
            ]
        except (KeyError, TypeError, ValueError) as erro:
            raise ValueError("Há uma sugestão de itinerário com data inválida.") from erro

    def editar_dia(
        self, grupo_id: int, viajante_id: int, data_original: str, dados: dict
    ) -> None:
        try:
            data_anterior = date.fromisoformat(data_original)
        except ValueError as erro:
            raise ValueError("A data do dia selecionado está inválida.") from erro

        data, cidade, passeio, reservas = self._normalizar_dia(dados)
        self._itinerario_dao.editar_dia(
            grupo_id,
            viajante_id,
            data_anterior,
            data,
            cidade,
            passeio,
            reservas,
        )

    def remover_dias(self, grupo_id: int, viajante_id: int, datas: list[str]) -> None:
        if not datas:
            raise ValueError("Selecione pelo menos um dia para remover.")
        try:
            dias = {date.fromisoformat(data) for data in datas}
        except ValueError as erro:
            raise ValueError("Uma das datas selecionadas está inválida.") from erro
        self._itinerario_dao.remover_dias(grupo_id, viajante_id, dias)

    @staticmethod
    def _normalizar_dia(
        dados: dict,
    ) -> tuple[date, str, str, list[tuple[str, float, int]]]:
        data = dados.get("data")
        cidade = dados.get("cidade")
        passeio = dados.get("passeio")
        reservas = dados.get("reservas")

        if not isinstance(data, str):
            raise ValueError("Informe uma data válida para o itinerário.")
        try:
            data_viagem = date.fromisoformat(data)
        except ValueError as erro:
            raise ValueError("Informe uma data válida para o itinerário.") from erro

        if not isinstance(cidade, str) or not cidade.strip():
            raise ValueError("Informe a cidade.")
        if not isinstance(passeio, str) or not passeio.strip():
            raise ValueError("Informe o passeio turístico.")
        if not isinstance(reservas, list):
            raise ValueError("Os dados das reservas estão inválidos.")

        reservas_validadas = []
        for reserva in reservas:
            if not isinstance(reserva, dict):
                raise ValueError("Os dados da reserva estão inválidos.")

            nome = reserva.get("nome")
            preco = reserva.get("preco")
            nome_vazio = nome is None or (
                isinstance(nome, str) and not nome.strip()
            )
            preco_vazio = preco is None or (
                isinstance(preco, str) and not preco.strip()
            )
            if nome_vazio and preco_vazio:
                continue

            titular_id = reserva.get("titular_id")
            if (
                not isinstance(nome, str)
                or not nome.strip()
                or not isinstance(preco, (int, float))
                or isinstance(preco, bool)
                or not isinstance(titular_id, int)
                or isinstance(titular_id, bool)
            ):
                raise ValueError("Os dados da reserva estão inválidos.")
            reservas_validadas.append((nome.strip(), float(preco), titular_id))

        if data_viagem < date.today():
            raise ValueError("A data escolhida não pode ser anterior à data de hoje!")

        return (
            data_viagem,
            cidade.strip(),
            passeio.strip(),
            reservas_validadas,
        )
