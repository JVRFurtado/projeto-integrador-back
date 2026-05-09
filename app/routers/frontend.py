from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from app.database import get_db

from app.models import (
    Pessoa,
    Departamento,
    RamalTelefonico,
    RamalPessoa,
    RamalDepto,
    Cargo
)

from app.dependencies import get_current_user

from app.security import hash_senha

router = APIRouter(
    tags=["Frontend Legacy"]
)

# =====================================================
# USERS ME
# =====================================================

@router.get("/users/me")
def me(
    user: Pessoa = Depends(get_current_user)
):

    return {
        "nome": user.txnome,
        "role": user.aotipousuario,
        "id": user.idpessoa
    }


# =====================================================
# LISTAR CONTATOS
# =====================================================

@router.get("/pessoas/")
def listar_contatos(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    ramais = db.query(RamalTelefonico).all()

    resultado = []

    for r in ramais:

        pessoa_nome = ""

        pessoa_link = db.query(RamalPessoa).filter(
            RamalPessoa.ramalid == r.idramal
        ).first()

        pessoa_id = None

        if pessoa_link:

            pessoa = db.query(Pessoa).filter(
                Pessoa.idpessoa == pessoa_link.pessoaid
            ).first()

            if pessoa:
                pessoa_nome = pessoa.txnome
                pessoa_id = pessoa.idpessoa

        departamento_nome = ""

        depto_link = db.query(RamalDepto).filter(
            RamalDepto.ramalid == r.idramal
        ).first()

        if depto_link:

            depto = db.query(Departamento).filter(
                Departamento.iddepto == depto_link.deptoid
            ).first()

            if depto:
                departamento_nome = depto.txnomedepto

        resultado.append({
            "id": r.idramal,
            "pessoa_id": pessoa_id,
            "nome": pessoa_nome,
            "departamento": departamento_nome,
            "ramal": r.nuramal
        })

    return resultado


# =====================================================
# CRIAR CONTATO
# =====================================================

@router.post("/pessoas/")
def criar_contato(
    dados: dict,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    if user.aotipousuario not in [
        "admin",
        "gestor"
    ]:

        raise HTTPException(
            status_code=403,
            detail="Sem permissão"
        )

    depto = db.query(Departamento).filter(
        Departamento.txnomedepto == dados["departamento"]
    ).first()

    if not depto:

        depto = Departamento(
            txnomedepto=dados["departamento"]
        )

        db.add(depto)

        db.commit()

        db.refresh(depto)

    existe_ramal = db.query(RamalTelefonico).filter(
        RamalTelefonico.nuramal == dados["ramal"]
    ).first()

    if existe_ramal:

        raise HTTPException(
            status_code=400,
            detail="Ramal já existe"
        )

    ramal = RamalTelefonico(
        nuramal=dados["ramal"]
    )

    db.add(ramal)

    db.commit()

    db.refresh(ramal)

    cargo = db.query(Cargo).first()

    if not cargo:

        cargo = Cargo(
            txnome="Funcionário"
        )

        db.add(cargo)

        db.commit()

        db.refresh(cargo)

    username = dados["nome"].lower().replace(" ", "")
    email = f"{username}@temp.com"

    existe_user = db.query(Pessoa).filter(
        Pessoa.txusername == username
    ).first()

    if existe_user:

        username = f"{username}{ramal.idramal}"
        email = f"{username}@temp.com"

    pessoa = Pessoa(
        txnome=dados["nome"],
        txusername=username,
        txemail=email,
        txsenha=hash_senha("123456"),
        cargoid=cargo.idcargo,
        deptoid=depto.iddepto,
        aotipousuario="padrao"
    )

    db.add(pessoa)

    db.commit()

    db.refresh(pessoa)

    rp = RamalPessoa(
        pessoaid=pessoa.idpessoa,
        ramalid=ramal.idramal
    )

    rd = RamalDepto(
        deptoid=depto.iddepto,
        ramalid=ramal.idramal
    )

    db.add(rp)
    db.add(rd)

    db.commit()

    return {
        "message": "Contato criado"
    }


# =====================================================
# EDITAR CONTATO
# =====================================================

@router.put("/pessoas/{id}")
def editar_contato(
    id: int,
    dados: dict,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    if user.aotipousuario not in [
        "admin",
        "gestor"
    ]:

        raise HTTPException(
            status_code=403,
            detail="Sem permissão"
        )

    ramal = db.query(RamalTelefonico).filter(
        RamalTelefonico.idramal == id
    ).first()

    if not ramal:

        raise HTTPException(
            status_code=404,
            detail="Contato não encontrado"
        )

    ramal.nuramal = dados["ramal"]

    pessoa_link = db.query(RamalPessoa).filter(
        RamalPessoa.ramalid == ramal.idramal
    ).first()

    if pessoa_link:

        pessoa = db.query(Pessoa).filter(
            Pessoa.idpessoa == pessoa_link.pessoaid
        ).first()

        if pessoa:
            pessoa.txnome = dados["nome"]

    depto_link = db.query(RamalDepto).filter(
        RamalDepto.ramalid == ramal.idramal
    ).first()

    if depto_link:

        depto = db.query(Departamento).filter(
            Departamento.iddepto == depto_link.deptoid
        ).first()

        if depto:
            depto.txnomedepto = dados["departamento"]

    db.commit()

    return {
        "message": "Contato atualizado"
    }


# =====================================================
# REMOVER CONTATO
# =====================================================

@router.delete("/pessoas/{id}")
def deletar_contato(
    id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    if user.aotipousuario not in [
        "admin",
        "gestor"
    ]:

        raise HTTPException(
            status_code=403,
            detail="Sem permissão"
        )

    ramal = db.query(RamalTelefonico).filter(
        RamalTelefonico.idramal == id
    ).first()

    if not ramal:

        raise HTTPException(
            status_code=404,
            detail="Contato não encontrado"
        )

    pessoa_link = db.query(RamalPessoa).filter(
        RamalPessoa.ramalid == id
    ).first()

    if pessoa_link:

        pessoa = db.query(Pessoa).filter(
            Pessoa.idpessoa == pessoa_link.pessoaid
        ).first()

        db.delete(pessoa_link)

        if pessoa:
            db.delete(pessoa)

    depto_link = db.query(RamalDepto).filter(
        RamalDepto.ramalid == id
    ).first()

    if depto_link:
        db.delete(depto_link)

    db.delete(ramal)

    db.commit()

    return {
        "message": "Contato removido"
    }


# =====================================================
# LISTAR USUÁRIOS
# =====================================================

@router.get("/usuarios/")
def listar_usuarios(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    if user.aotipousuario != "admin":

        raise HTTPException(
            status_code=403,
            detail="Apenas admin"
        )

    usuarios = db.query(Pessoa).all()

    return [
        {
            "id": u.idpessoa,
            "nome": u.txnome,
            "username": u.txusername,
            "email": u.txemail,
            "aotipousuario": u.aotipousuario
        }
        for u in usuarios
    ]


# =====================================================
# ALTERAR USUÁRIO
# =====================================================

@router.put("/usuarios/{id}")
def alterar_usuario(
    id: int,
    dados: dict,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    if user.aotipousuario != "admin":

        raise HTTPException(
            status_code=403,
            detail="Apenas admin"
        )

    usuario = db.query(Pessoa).filter(
        Pessoa.idpessoa == id
    ).first()

    if not usuario:

        raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado"
        )

    if (
        usuario.aotipousuario == "admin" and
        usuario.idpessoa != user.idpessoa
    ):

        raise HTTPException(
            status_code=403,
            detail="Não pode alterar outro admin"
        )

    if dados.get("senha"):

        usuario.txsenha = hash_senha(
            dados["senha"]
        )

    db.commit()

    return {
        "message": "Usuário atualizado"
    }


# =====================================================
# REMOVER USUÁRIO
# =====================================================

@router.delete("/usuarios/{id}")
def deletar_usuario(
    id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    if user.aotipousuario != "admin":

        raise HTTPException(
            status_code=403,
            detail="Apenas admin"
        )

    usuario = db.query(Pessoa).filter(
        Pessoa.idpessoa == id
    ).first()

    if not usuario:

        raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado"
        )

    if usuario.idpessoa == user.idpessoa:

        raise HTTPException(
            status_code=403,
            detail="Você não pode apagar sua própria conta"
        )

    if usuario.aotipousuario == "admin":

        raise HTTPException(
            status_code=403,
            detail="Não pode remover outro admin"
        )

    ramais = db.query(RamalPessoa).filter(
        RamalPessoa.pessoaid == usuario.idpessoa
    ).all()

    for r in ramais:
        db.delete(r)

    db.delete(usuario)

    db.commit()

    return {
        "message": "Usuário removido"
    }
