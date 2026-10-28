import bcrypt

def hash_senha(senha: str) -> str:
    return bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

# função para o futuro, quando o caso de uso de login for implementado
def verifica_senha(senha: str, hash_bd: str) -> bool:
    return bcrypt.checkpw(senha.encode("utf-8"), hash_bd.encode("utf-8"))