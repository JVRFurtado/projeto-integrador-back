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
        "role": user.aotipousuario
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
            "id": pessoa_id,
            "ramalid": r.idramal,
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

    existe_usuario = db.query(Pessoa).filter(
        Pessoa.txusername == username
    ).first()

    if existe_usuario:
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
# ALTERAR CONTATO
# =====================================================

@router.put("/pessoas/{id}")
def atualizar_contato(
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

    pessoa = db.query(Pessoa).filter(
        Pessoa.idpessoa == id
    ).first()

    if not pessoa:

        raise HTTPException(
            status_code=404,
            detail="Contato não encontrado"
        )

    if dados.get("nome"):
        pessoa.txnome = dados["nome"]

    if dados.get("departamento"):

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

        pessoa.deptoid = depto.iddepto

        ramal_pessoa = db.query(RamalPessoa).filter(
            RamalPessoa.pessoaid == pessoa.idpessoa
        ).first()

        if ramal_pessoa:

            ramal_depto = db.query(RamalDepto).filter(
                RamalDepto.ramalid == ramal_pessoa.ramalid
            ).first()

            if ramal_depto:
                ramal_depto.deptoid = depto.iddepto

    if dados.get("ramal"):

        ramal_pessoa = db.query(RamalPessoa).filter(
            RamalPessoa.pessoaid == pessoa.idpessoa
        ).first()

        if ramal_pessoa:

            ramal = db.query(RamalTelefonico).filter(
                RamalTelefonico.idramal == ramal_pessoa.ramalid
            ).first()

            if ramal:
                ramal.nuramal = dados["ramal"]

    db.commit()

    return {
        "message": "Contato atualizado"
    }


# =====================================================
# DELETAR CONTATO
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

    pessoa = db.query(Pessoa).filter(
        Pessoa.idpessoa == id
    ).first()

    if not pessoa:

        raise HTTPException(
            status_code=404,
            detail="Contato não encontrado"
        )

    ramal_links = db.query(RamalPessoa).filter(
        RamalPessoa.pessoaid == pessoa.idpessoa
    ).all()

    for link in ramal_links:

        ramal_id = link.ramalid

        db.delete(link)

        ramal_depto = db.query(RamalDepto).filter(
            RamalDepto.ramalid == ramal_id
        ).all()

        for rd in ramal_depto:
            db.delete(rd)

        ramal = db.query(RamalTelefonico).filter(
            RamalTelefonico.idramal == ramal_id
        ).first()

        if ramal:
            db.delete(ramal)

    db.delete(pessoa)

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
# CRIAR USUÁRIO
# =====================================================

@router.post("/usuarios/")
def criar_usuario(
    dados: dict,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    if user.aotipousuario != "admin":

        raise HTTPException(
            status_code=403,
            detail="Apenas admin"
        )

    existe_username = db.query(Pessoa).filter(
        Pessoa.txusername == dados["username"]
    ).first()

    if existe_username:

        raise HTTPException(
            status_code=400,
            detail="Username já existe"
        )

    existe_email = db.query(Pessoa).filter(
        Pessoa.txemail == dados["email"]
    ).first()

    if existe_email:

        raise HTTPException(
            status_code=400,
            detail="Email já existe"
        )

    cargo = db.query(Cargo).first()

    depto = db.query(Departamento).first()

    if not cargo:

        cargo = Cargo(txnome="Funcionário")

        db.add(cargo)

        db.commit()

        db.refresh(cargo)

    if not depto:

        depto = Departamento(txnomedepto="TI")

        db.add(depto)

        db.commit()

        db.refresh(depto)

    novo = Pessoa(
        txnome=dados["nome"],
        txusername=dados["username"],
        txemail=dados["email"],
        txsenha=hash_senha(dados["senha"]),
        cargoid=cargo.idcargo,
        deptoid=depto.iddepto,
        aotipousuario=dados["tipo"]
    )

    db.add(novo)

    db.commit()

    db.refresh(novo)

    return {
        "message": "Usuário criado"
    }


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
        usuario.aotipousuario == "admin"
        and user.idpessoa != usuario.idpessoa
    ):

        raise HTTPException(
            status_code=403,
            detail="Não é permitido alterar senha de outro admin"
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

    if user.idpessoa == id:

        raise HTTPException(
            status_code=400,
            detail="Você não pode excluir seu próprio usuário"
        )

    usuario = db.query(Pessoa).filter(
        Pessoa.idpessoa == id
    ).first()

    if not usuario:

        raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado"
        )

    ramal_links = db.query(RamalPessoa).filter(
        RamalPessoa.pessoaid == usuario.idpessoa
    ).all()

    for link in ramal_links:
        db.delete(link)

    db.delete(usuario)

    db.commit()

    return {
        "message": "Usuário removido"
    }
