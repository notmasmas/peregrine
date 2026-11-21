import smtplib, ssl
import os
from dotenv import load_dotenv
from threading import Thread
from email.message import EmailMessage

load_dotenv()

habilitar_email = False # Manter desativado no desenvolvimento. Se for ativar, preencher variáveis necessárias no .env (SENDER_EMAIL e SENDER_CREDENTIAL)

def setup_email(nome_organizador: str, nome_grupo: str, email_convidado: str):

    msg = EmailMessage()
    msg.set_content(f'Você foi convidado para o grupo {nome_grupo} por {nome_organizador}!\n Entre no Peregrine para aceitar! \U0001F499') # Esse unicode é o emoji de coração azul
    msg["Subject"] = "Convite do Peregrine!"
    msg["From"] = os.getenv("SENDER_EMAIL")
    msg["To"] = email_convidado

    context=ssl.create_default_context()

    with smtplib.SMTP("smtp.gmail.com", port=587) as smtp: # Se for usar outro provedor muda a parte do gmail
        smtp.starttls(context=context)
        smtp.login(msg["From"], os.getenv("SENDER_CREDENTIAL"))
        smtp.send_message(msg)

# Adicionando thread aqui porque esse envio de e-mail é meio lento e bloqueia a tela
def enviar_email(nome_organizador: str, nome_grupo: str, email_convidado: str):
    if habilitar_email:
        thread = Thread(target=setup_email, args=(nome_organizador, nome_grupo, email_convidado))
        thread.start()

