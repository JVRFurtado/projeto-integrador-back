from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from app.database import get_db

from app.models import Cargo

from app.schemas import (
    CargoCreate,
    CargoUpdate,
    CargoResponse
)

from app.dependencies import get_current_user

from app.services.permissions import (
    require_gestor
)

router = APIRouter(
    prefix="/cargos",
    tags=["Cargos"]
)


# =========================================================
# LISTAR
# =========================================================

@router.get(
    "/",
    response_model=list[CargoResponse]
)
def listar_cargos(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    return db.query(Cargo).all()


# =========================================================
# BUSCAR POR ID
# =========================================================

@router.get(
    "/{idcargo}",
    response_model=CargoResponse
)
def buscar_cargo(
    idcargo: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    cargo = db.query(Cargo).filter(
        Cargo.idcargo == idcargo
    ).first()

    if not cargo:
        raise HTTPException(
            status_code=404,
            detail="Cargo não encontrado"
        )

    return cargo


# =========================================================
# CRIAR
# =========================================================

@router.post(
    "/",
    response_model=CargoResponse
)
def criar_cargo(
    dados: CargoCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    require_gestor(user)

    existe = db.query(Cargo).filter(
        Cargo.txnome == dados.txnome
    ).first()

    if existe:
        raise HTTPException(
            status_code=400,
            detail="Cargo já existe"
        )

    novo = Cargo(
        txnome=dados.txnome
    )

    db.add(novo)

    db.commit()

    db.refresh(novo)

    return novo


# =========================================================
# ATUALIZAR
# =========================================================

@router.put(
    "/{idcargo}",
    response_model=CargoResponse
)
def atualizar_cargo(
    idcargo: int,
    dados: CargoUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    require_gestor(user)

    cargo = db.query(Cargo).filter(
        Cargo.idcargo == idcargo
    ).first()

    if not cargo:
        raise HTTPException(
            status_code=404,
            detail="Cargo não encontrado"
        )

    if dados.txnome:

        existe = db.query(Cargo).filter(
            Cargo.txnome == dados.txnome,
            Cargo.idcargo != idcargo
        ).first()

        if existe:
            raise HTTPException(
                status_code=400,
                detail="Já existe um cargo com esse nome"
            )

        cargo.txnome = dados.txnome

    db.commit()

    db.refresh(cargo)

    return cargo


# =========================================================
# DELETAR
# =========================================================

@router.delete("/{idcargo}")
def deletar_cargo(
    idcargo: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    require_gestor(user)

    cargo = db.query(Cargo).filter(
        Cargo.idcargo == idcargo
    ).first()

    if not cargo:
        raise HTTPException(
            status_code=404,
            detail="Cargo não encontrado"
        )

    db.delete(cargo)

    db.commit()

    return {
        "message": "Cargo removido"
    }