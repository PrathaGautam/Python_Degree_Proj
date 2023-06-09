
import jwt
from jwt import PyJWTError
from fastapi import HTTPException
from datetime import datetime, timedelta

SECRET_KEY = "0e2147c1325fcea774ea8bcb866111c6b0c773a6"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 45


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str):
    print(token)
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except PyJWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid access token, {e}")
