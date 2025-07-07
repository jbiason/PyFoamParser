class FoamError(Exception):
    pass


class UnexpectedCharacterError(FoamError):
    def __init__(self, text, position):
        self.text = text
        self.position = position


class UnexpectedTokenError(FoamError):
    def __init__(self, token):
        self.token = token


class InvalidRootElementError(FoamError):
    pass
