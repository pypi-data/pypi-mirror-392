class CWTokenError(Exception):
    def __init__(self, message, response=None):
        self.message = message
        self.response = response
        self.status_code = getattr(response, "status_code", None)
        super().__init__(self.full_message())

    def full_message(self):
        msg = self.message
        if self.response is not None:
            msg += f" | Server responded with status {self.status_code}"
            try:
                error_info = self.response.json()
                msg += f": {error_info["message"]}"  # include snippet
            except Exception:
                pass
        return msg

class AuthenticationError(CWTokenError):
    pass

class QueryError(CWTokenError):
    pass
    
class FetchError(CWTokenError):
    pass