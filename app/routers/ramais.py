from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db

from app.models import RamalTelefonico

from app.dependencies import get_current_user

from app.services.permissions import (
    require_gestor
)

router = APIRouter(
    prefix="/ramais",
    tags=["Ramais"]
)


@router.get("/")
def listar_ramais(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    return db.query(
        RamalTelefonico
    ).all()


@router.post("/")
def criar_ramal(
    dados: dict,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    require_gestor(user)

    ramal = RamalTelefonico(
        nuramal=dados["nuramal"],
        nuvoip=dados.get("nuvoip")
    )

    db.add(ramal)

    db.commit()

    db.refresh(ramal)

    return ramal