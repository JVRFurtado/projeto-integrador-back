from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Pessoa

from app.dependencies import get_current_user

from app.services.permissions import (
    require_admin,
    require_gestor
)

from app.security import hash_senha

router = APIRouter(
    prefix="/pessoas",
    tags=["Pessoas"]
)


@router.get("/")
def listar_pessoas(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    return db.query(Pessoa).all()


@router.post("/")
def criar_pessoa(
    dados: dict,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    require_gestor(user)

    if (
        user.aotipousuario == "gestor"
        and dados["aotipousuario"] == "admin"
    ):
        raise HTTPException(
            status_code=403,
            detail="Gestor não pode criar admin"
        )

    nova = Pessoa(
        txnome=dados["txnome"],
        txemail=dados["txemail"],
        txsenha=hash_senha(dados["txsenha"]),
        cargoid=dados["cargoid"],
        deptoid=dados["deptoid"],
        aotipousuario=dados["aotipousuario"]
    )

    db.add(nova)

    db.commit()

    db.refresh(nova)

    return nova