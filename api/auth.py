from fastapi import APIRouter, HTTPException, Depends, status, Header
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from jose import jwt, JWTError
from pydantic import BaseModel

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

SECRET_KEY = "KEYFIAP2025!*"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
fake_user = {
    "username": "admin",
    "password": "123456"
}

def getCurrentUser(token: str = Header(...)):

    """Validate the token JWT and return the authenticated user"""
    credentials_exception = HTTPException(

        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido ou expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception

        if username != fake_user["username"]:
            raise credentials_exception

        return username

    except JWTError:
        raise credentials_exception

def createAccessToken(data: dict, expires_delta: timedelta | None = None):

    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

router = APIRouter()

@router.post("/login", summary="Obter token de acesso")
def login(form_data: OAuth2PasswordRequestForm = Depends()):

    """Login route"""
    if form_data.username != fake_user["username"] or form_data.password != fake_user["password"]:
        raise HTTPException(status_code=401, detail="Usuário ou senha inválidos")

    access_token = createAccessToken(data={"sub": fake_user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}


class TokenRefreshRequest(BaseModel):
    token: str

@router.post("/refresh", summary="Renovar token de acesso")
def refresh_token(request: TokenRefreshRequest):

    """Refresh token route"""
    try:
        payload = jwt.decode(request.token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username != fake_user["username"]:
            raise HTTPException(status_code=401, detail="Token inválido")

        new_token = createAccessToken(data={"sub": username})
        return {"access_token": new_token, "token_type": "bearer"}

    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")
    
