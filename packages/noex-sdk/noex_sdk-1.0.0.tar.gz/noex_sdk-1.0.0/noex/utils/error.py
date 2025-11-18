class NoexError(Exception):
    pass

class ClientError(NoexError):
    def __init__(self, sc, em, rt=None, hd=None):
        self.status_code = sc
        self.error_message = em
        self.response_text = rt
        self.headers = hd
        super().__init__(f"Client error {sc}: {em}")

class ServerError(NoexError):
    def __init__(self, sc, msg):
        self.status_code = sc
        self.message = msg
        super().__init__(f"Server error {sc}: {msg}")

class AuthenticationError(NoexError):
    pass

class WebSocketError(NoexError):
    pass
