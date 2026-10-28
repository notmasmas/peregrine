from src.exception.CampoInvalidoException import CampoInvalidoException
from src.DAOs.ViajanteDAO import ViajanteDAO
from src.model.Viajante import Viajante
from src.view.ViajanteView import ViajanteView
from email_validator import validate_email, EmailNotValidError
from datetime import datetime, date
from src.util.seguranca import *

class ViajanteController:

    def __init__(self) -> None:
        self._viajante_dao = ViajanteDAO()
        self._tela = ViajanteView()
    
    def _validar_data_nascimento(self, data: str) -> date:
        try:
            nascimento = datetime.strptime(data, "%d/%m/%Y").date()
        except ValueError:
            raise CampoInvalidoException("O usuário deve ter 18 anos ou mais")
        
        return nascimento
    
    def cadastrar_viajante(self) -> None:
        dados = self._tela.cria_viajante()
        
        try:
            if len(dados["nome"]) == 0 or len(dados["nome"]) > 50:
                raise CampoInvalidoException("Nome de usuário inválido")
            
            try:
                validate_email(dados["email"], check_deliverability=False)
            except EmailNotValidError:
                raise CampoInvalidoException("E-mail inválido ou já cadastrado")
            
            if self._viajante_dao.buscar_por_email(dados["email"]) is not None:
                raise CampoInvalidoException("E-mail inválido ou já cadastrado")
            
            if len(dados["senha"]) < 8:
                raise CampoInvalidoException("A senha deve ter no mínimo 8 caracteres")

            if dados["senha"] != dados["confirmar_senha"]:
                raise CampoInvalidoException("As senhas não coincidem")
            
            nascimento = self._validar_data_nascimento(dados["data_nascimento"])
            hoje = date.today()
            
            # diferença entre os anos menos 1 se a pessoa ainda não fez aniversário
            # ou menos 0 se já fez
            idade = hoje.year - nascimento.year - (
                (hoje.month, hoje.day) < (nascimento.month, nascimento.day)
            )
            if idade < 18:
                raise CampoInvalidoException("O usuário deve ter 18 anos ou mais")
            
            senha_criptografada = hash_senha(dados["senha"])

            viajante = Viajante(
                nome=dados["nome"],
                email=dados["email"],
                senha=senha_criptografada,
                data_nascimento=nascimento)

            self._viajante_dao.criar(viajante)

        except CampoInvalidoException as e:
            self._tela.mostra_mensagem(str(e))
        
        else:
            self._tela.mostra_mensagem("Cadastro realizado com sucesso")