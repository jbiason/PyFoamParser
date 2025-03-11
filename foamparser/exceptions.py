class FoamError(Exception):
    pass


class UnexpectedTokenError(FoamError):
    def __init__(self, token):
        self.token = token


class InvalidRootElementError(FoamError):
    pass
