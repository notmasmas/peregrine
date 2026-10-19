# inicializando o repositório no Git e Github

from datetime import date

from model.Acompanhante import Acompanhante
from model.Cidade import Cidade
from model.Convite import Convite
from model.Grupo import Grupo
from model.Itinerario import Itinerario
from model.PasseioTuristico import PasseioTuristico
from model.Relatorio import Relatorio
from model.Reserva import Reserva
from model.StatusConvite import StatusConvite
from model.Viajante import Viajante

# Implementado por Maria Helena Melo
# Teste de criação de objetos das classes do modelo
def main() -> None:
    viajante = Viajante(id=1, nome="Teste", email="teste@teste.com")
    acompanhante = Acompanhante(id=1, nome="Acompanhante teste", viajante_vinculado=viajante)
    grupo = Grupo(
        id=1,
        nome="Grupo teste",
        organizador=viajante,
        integrantes=[viajante],
        acompanhantes=[acompanhante],
    )
    itinerario = Itinerario(id=1, grupo=grupo)
    cidade = Cidade(id=1, nome="Cidade teste")
    passeio = PasseioTuristico(
        id=1,
        nome="Passeio teste",
        cidade=cidade,
        preco=10.0,
        data=date.today(),
    )
    convite = Convite(
        destinatario=viajante,
        remetente=viajante,
        id=1,
        status=StatusConvite.PENDENTE,
    )
    reserva = Reserva(titular=viajante, id=1, nome="Reserva teste", preco=10.0)
    relatorio = Relatorio(id=1, grupo=grupo, itinerario=itinerario)

    print("Passou :)")

if __name__ == "__main__":
    main()
