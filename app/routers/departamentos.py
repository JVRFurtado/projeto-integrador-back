from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from app.database import get_db

from app.models import Departamento

from app.schemas import (
    DepartamentoCreate,
    DepartamentoUpdate,
    DepartamentoResponse
)

from app.dependencies import get_current_user

from app.services.permissions import (
    require_gestor
)

router = APIRouter(
    prefix="/departamentos",
    tags=["Departamentos"]
)


# =========================================================
# LISTAR
# =========================================================

@router.get(
    "/",
    response_model=list[DepartamentoResponse]
)
def listar_departamentos(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    return db.query(Departamento).all()


# =========================================================
# BUSCAR POR ID
# =========================================================

@router.get(
    "/{iddepto}",
    response_model=DepartamentoResponse
)
def buscar_departamento(
    iddepto: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    departamento = db.query(
        Departamento
    ).filter(
        Departamento.iddepto == iddepto
    ).first()

    if not departamento:
        raise HTTPException(
            status_code=404,
            detail="Departamento não encontrado"
        )

    return departamento


# =========================================================
# CRIAR
# =========================================================

@router.post(
    "/",
    response_model=DepartamentoResponse
)
def criar_departamento(
    dados: DepartamentoCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    require_gestor(user)

    existe = db.query(
        Departamento
    ).filter(
        Departamento.txnomedepto == dados.txnomedepto
    ).first()

    if existe:
        raise HTTPException(
            status_code=400,
            detail="Departamento já existe"
        )

    novo = Departamento(
        txnomedepto=dados.txnomedepto
    )

    db.add(novo)

    db.commit()

    db.refresh(novo)

    return novo


# =========================================================
# ATUALIZAR
# =========================================================

@router.put(
    "/{iddepto}",
    response_model=DepartamentoResponse
)
def atualizar_departamento(
    iddepto: int,
    dados: DepartamentoUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    require_gestor(user)

    departamento = db.query(
        Departamento
    ).filter(
        Departamento.iddepto == iddepto
    ).first()

    if not departamento:
        raise HTTPException(
            status_code=404,
            detail="Departamento não encontrado"
        )

    if dados.txnomedepto:

        existe = db.query(
            Departamento
        ).filter(
            Departamento.txnomedepto == dados.txnomedepto,
            Departamento.iddepto != iddepto
        ).first()

        if existe:
            raise HTTPException(
                status_code=400,
                detail="Já existe um departamento com esse nome"
            )

        departamento.txnomedepto = dados.txnomedepto

    db.commit()

    db.refresh(departamento)

    return departamento


# =========================================================
# DELETAR
# =========================================================

@router.delete("/{iddepto}")
def deletar_departamento(
    iddepto: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    require_gestor(user)

    departamento = db.query(
        Departamento
    ).filter(
        Departamento.iddepto == iddepto
    ).first()

    if not departamento:
        raise HTTPException(
            status_code=404,
            detail="Departamento não encontrado"
        )

    db.delete(departamento)

    db.commit()

    return {
        "message": "Departamento removido"
    }