from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy.orm import Session

from database import Base, engine, get_db
from models import (
    Pessoa,
    RamalTelefonico,
    RamalPessoa,
    RamalDepto
)

from schemas import (
    UsuarioCreate,
    UsuarioUpdate,
    RamalCreate,
    RamalUpdate
)

from security import (
    verificar_senha,
    hash_senha,
    criar_access_token,
    criar_refresh_token
)

from dependencies import (
    get_current_user,
    require_admin,
    require_gestor_or_admin
)

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/token")
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = (
        db.query(Pessoa)
        .filter(Pessoa.idpessoa == int(form.username))
        .first()
    )

    if not user:
        raise HTTPException(401, "Usuário inválido")

    if not verificar_senha(form.password, user.txsenha):
        raise HTTPException(401, "Senha inválida")

    return {
        "access_token": criar_access_token({
            "sub": str(user.idpessoa)
        }),
        "refresh_token": criar_refresh_token({
            "sub": str(user.idpessoa)
        }),
        "token_type": "bearer"
    }


@app.get("/users/me")
def me(user=Depends(get_current_user)):
    return {
        "id": user.idpessoa,
        "nome": user.txnome,
        "role": user.aotipousuario
    }


@app.get("/pessoas/")
def listar_ramais(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    resultado = (
        db.query(
            RamalTelefonico.idramal,
            RamalTelefonico.nuramal,
            Pessoa.txnome,
        )
        .join(
            RamalPessoa,
            RamalPessoa.ramalid == RamalTelefonico.idramal
        )
        .join(
            Pessoa,
            Pessoa.idpessoa == RamalPessoa.pessoaid
        )
        .all()
    )

    return resultado


@app.post("/pessoas/")
def criar_ramal(
    dados: RamalCreate,
    db: Session = Depends(get_db),
    user=Depends(require_gestor_or_admin)
):
    novo = RamalTelefonico(
        nuramal=dados.nuramal,
        nuvoip=dados.nuvoip
    )

    db.add(novo)
    db.commit()
    db.refresh(novo)

    rel_pessoa = RamalPessoa(
        pessoaid=dados.pessoaid,
        ramalid=novo.idramal
    )

    rel_depto = RamalDepto(
        deptoid=dados.deptoid,
        ramalid=novo.idramal
    )

    db.add(rel_pessoa)
    db.add(rel_depto)

    db.commit()

    return {"msg": "Ramal criado"}


@app.put("/pessoas/{id}")
def atualizar_ramal(
    id: int,
    dados: RamalUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_gestor_or_admin)
):
    ramal = (
        db.query(RamalTelefonico)
        .filter(RamalTelefonico.idramal == id)
        .first()
    )

    if not ramal:
        raise HTTPException(404, "Ramal não encontrado")

    if dados.nuramal:
        ramal.nuramal = dados.nuramal

    if dados.nuvoip:
        ramal.nuvoip = dados.nuvoip

    db.commit()

    return {"msg": "Atualizado"}


@app.delete("/pessoas/{id}")
def deletar_ramal(
    id: int,
    db: Session = Depends(get_db),
    user=Depends(require_gestor_or_admin)
):
    ramal = (
        db.query(RamalTelefonico)
        .filter(RamalTelefonico.idramal == id)
        .first()
    )

    if not ramal:
        raise HTTPException(404, "Ramal não encontrado")

    db.delete(ramal)

    db.commit()

    return {"msg": "Removido"}