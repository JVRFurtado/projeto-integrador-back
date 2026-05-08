from sqlalchemy.orm import joinedload

from models import (
    Pessoa,
    RamalTelefonico
)

def listar_ramais(db):
    return (
        db.query(RamalTelefonico)
        .options(
            joinedload(RamalTelefonico.pessoas),
            joinedload(RamalTelefonico.departamentos)
        )
        .all()
    )

def listar_usuarios(db):
    return db.query(Pessoa).all()