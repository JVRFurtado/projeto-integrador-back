from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from database import get_db
from models import Pessoa
from security import SECRET_KEY, ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(401, "Token inválido")

    except JWTError:
        raise HTTPException(401, "Token inválido")

    user = (
        db.query(Pessoa)
        .filter(Pessoa.idpessoa == int(user_id))
        .first()
    )

    if not user:
        raise HTTPException(401, "Usuário não encontrado")

    return user


def require_admin(user=Depends(get_current_user)):
    if user.aotipousuario != "admin":
        raise HTTPException(403, "Acesso negado")

    return user


def require_gestor_or_admin(user=Depends(get_current_user)):
    if user.aotipousuario not in ["admin", "gestor"]:
        raise HTTPException(403, "Acesso negado")

    return user