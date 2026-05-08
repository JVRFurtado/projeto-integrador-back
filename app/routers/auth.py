from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from fastapi.security import (
    OAuth2PasswordRequestForm
)

from sqlalchemy.orm import Session

from app.database import get_db

from app.models import Pessoa

from app.security import (
    verificar_senha,
    criar_access_token
)

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


@router.post("/login")
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    try:
        user_id = int(form.username)

    except:
        raise HTTPException(
            status_code=401,
            detail="ID inválido"
        )

    user = db.query(Pessoa).filter(
        Pessoa.idpessoa == user_id
    ).first()

    if not user:

        raise HTTPException(
            status_code=401,
            detail="Usuário inválido"
        )

    if not verificar_senha(
        form.password,
        user.txsenha
    ):

        raise HTTPException(
            status_code=401,
            detail="Senha inválida"
        )

    token = criar_access_token({
        "sub": str(user.idpessoa)
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "usuario": {
            "id": user.idpessoa,
            "nome": user.txnome,
            "tipo": user.aotipousuario
        }
    }