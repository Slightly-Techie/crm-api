
from jose import jwt, JWTError
from datetime import datetime, timedelta

from api.api_models.user_sign_up import TokenData
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')


ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * settings.ACCESS_TOKEN_EXPIRE_DAYS

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

def create_access_token(data: dict):
  to_encode = data.copy()
  expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
  to_encode.update({"exp": expire})

  encoded_jwt = jwt.encode(to_encode, settings.SECRET, algorithm=ALGORITHM)
  return encoded_jwt


def get_access_token(sub: str):
    token = create_access_token({"sub": sub})
    return token

def verify_token(token: str, credential_exception ):
  try:
    payload = jwt.decode(token, settings.SECRET, algorithms=ALGORITHM)
    sub = payload.get('sub')
    if sub is None:
      raise credential_exception 
    token_data = TokenData(sub=sub)
  except JWTError:
    raise credential_exception
  
  return token_data

