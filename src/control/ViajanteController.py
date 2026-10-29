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

    # UC01: Cadastrar viajante (Implementado por Sarah Meireles)
    
    def _validar_nome(self, nome: str) -> None:
        if len(nome) == 0 or len(nome) > 50:
            raise CampoInvalidoException("Nome de usuário inválido")
        
    def _validar_email(self, email: str) -> None:
        try:
            validate_email(email, check_deliverability=False)
        except EmailNotValidError:
            raise CampoInvalidoException("E-mail inválido ou já cadastrado")
        
    def _validar_senha(self, senha: str) -> None:
        if len(senha) < 8:
            raise CampoInvalidoException("A senha deve ter no mínimo 8 caracteres")
        
    def _validar_confirmar_senha(self, senha: str, confirmar_senha: str) -> None:
        if senha != confirmar_senha:
            raise CampoInvalidoException("As senhas não coincidem")
        
    def _validar_data_nascimento(self, data: str) -> date:
        try:
            nascimento = datetime.strptime(data, "%d/%m/%Y").date()
        except ValueError:
            raise CampoInvalidoException("O usuário deve ter 18 anos ou mais")
        
        hoje = date.today()   
        idade = hoje.year - nascimento.year - (
            (hoje.month, hoje.day) < (nascimento.month, nascimento.day)
        )
        if idade < 18:
            raise CampoInvalidoException("O usuário deve ter 18 anos ou mais")

        return nascimento
    
    def cadastrar_viajante(self) -> None:
        dados = self._tela.cria_viajante()
        
        try:
            self._validar_nome(dados["nome"])
            
            self._validar_email(dados["email"])
            
            if self._viajante_dao.buscar_por_email(dados["email"]) is not None:
                raise CampoInvalidoException("E-mail inválido ou já cadastrado")
            
            self._validar_senha(dados["senha"])
            
            self._validar_confirmar_senha(dados["senha"], dados["confirmar_senha"])
            
            nascimento = self._validar_data_nascimento(dados["data_nascimento"])
            
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