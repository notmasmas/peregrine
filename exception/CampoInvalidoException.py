from view.View import View


class CampoInvalidoException(Exception):

    def __init__(self, mensagem: str) -> None:
        super().__init__(mensagem)
