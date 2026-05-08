from fastapi import (
    Depends,
    HTTPException
)

from fastapi.security import OAuth2PasswordBearer

from jose import (
    jwt,
    JWTError
)

from sqlalchemy.orm import Session

from app.database import get_db

from app.models import Pessoa

from app.config import settings

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):

    try:

        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        user_id = payload.get("sub")

    except JWTError:

        raise HTTPException(
            status_code=401,
            detail="Token inválido"
        )

    user = db.query(Pessoa).filter(
        Pessoa.idpessoa == int(user_id)
    ).first()

    if not user:

        raise HTTPException(
            status_code=401,
            detail="Usuário não encontrado"
        )

    return user