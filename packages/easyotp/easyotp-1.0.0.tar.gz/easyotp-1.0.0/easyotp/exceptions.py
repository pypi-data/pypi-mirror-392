class EasyOTPError(Exception):
    def __init__(self, message: str, request_id: str = None, status_code: int = None):
        self.message = message
        self.request_id = request_id
        self.status_code = status_code
        super().__init__(self.message)

    def __str__(self):
        if self.request_id:
            return f"{self.message} (request_id: {self.request_id})"
        return self.message


class AuthenticationError(EasyOTPError):
    pass


class InsufficientCreditsError(EasyOTPError):
    pass


class APIKeyDisabledError(EasyOTPError):
    pass


class RateLimitError(EasyOTPError):
    def __init__(self, message: str, request_id: str = None, retry_after: int = None):
        self.retry_after = retry_after
        super().__init__(message, request_id, status_code=429)


class ValidationError(EasyOTPError):
    pass


class NotFoundError(EasyOTPError):
    pass


class ServerError(EasyOTPError):
    pass

