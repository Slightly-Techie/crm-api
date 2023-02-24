from fastapi import HTTPException, status


class ValidationError(Exception):
  def __init__(self, error_msg: str, status_code: int):
    super().__init__(error_msg)
    self.status_code = status_code
    self.error_msg = error_msg

class UserNotFoundError(ValidationError):
  pass



class ForbiddenError(HTTPException):
  def __init__(self, status_code: int = status.HTTP_403_FORBIDDEN, detail:str = "User not authorised"):
    super().__init__(status_code, detail)
 