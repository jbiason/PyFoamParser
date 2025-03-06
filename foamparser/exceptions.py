class UnexpectedToken(Exception):
    def __init__(self, token):
        self.token = token
