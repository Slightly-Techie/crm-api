from fastapi import HTTPException, status


class ValidationError(Exception):
    def __init__(self, error_msg: str, status_code: int):
        super().__init__(error_msg)
        self.status_code = status_code
        self.error_msg = error_msg


class UserNotFoundError(ValidationError):
    pass


class ForbiddenError(HTTPException):
    def __init__(
        self, status_code: int = status.HTTP_403_FORBIDDEN,
        detail: str = "User not authorised"
    ):
        super().__init__(status_code, detail)


class NotFoundError(HTTPException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class ConflictError(HTTPException):
    def __init__(self, detail: str = "Resource already exists"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class BadRequestError(HTTPException):
    def __init__(self, detail: str = "Bad request"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class UnauthorizedError(HTTPException):
    def __init__(self, detail: str = "Invalid Credentials"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class SignupClosedError(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail="Signup is closed")
