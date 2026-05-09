from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db

from app.models import (
    Pessoa,
    Cargo,
    Departamento
)

from app.dependencies import get_current_user

from app.services.permissions import (
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

    cargo = db.query(Cargo).first()

    depto = db.query(Departamento).first()

    nova = Pessoa(
        txnome=dados["nome"],
        txusername=dados["username"],
        txemail=dados["email"],
        txsenha=hash_senha(dados["senha"]),
        cargoid=cargo.idcargo,
        deptoid=depto.iddepto,
        aotipousuario=dados["tipo"]
    )

    db.add(nova)

    db.commit()

    db.refresh(nova)

    return nova
