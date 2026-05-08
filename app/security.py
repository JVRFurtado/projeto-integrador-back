from passlib.context import CryptContext

from jose import jwt

from datetime import (
    datetime,
    timedelta
)

from app.config import settings

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def hash_senha(senha: str):

    return pwd_context.hash(senha)


def verificar_senha(
    senha: str,
    senha_hash: str
):

    return pwd_context.verify(
        senha,
        senha_hash
    )


def criar_access_token(data: dict):

    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({
        "exp": expire
    })

    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )