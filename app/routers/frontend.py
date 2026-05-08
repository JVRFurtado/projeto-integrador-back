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

        if pessoa_link:

            pessoa = db.query(Pessoa).filter(
                Pessoa.idpessoa == pessoa_link.pessoaid
            ).first()

            if pessoa:
                pessoa_nome = pessoa.txnome

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

    # ==========================================
    # DEPARTAMENTO
    # ==========================================

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

    # ==========================================
    # RAMAL
    # ==========================================

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

    # ==========================================
    # CARGO PADRÃO
    # ==========================================

    cargo = db.query(Cargo).first()

    if not cargo:

        cargo = Cargo(
            txnome="Funcionário"
        )

        db.add(cargo)

        db.commit()

        db.refresh(cargo)

    # ==========================================
    # PESSOA
    # ==========================================

    email_fake = f"{dados['nome'].lower().replace(' ', '.')}@temp.com"

    pessoa = Pessoa(
        txnome=dados["nome"],
        txemail=email_fake,
        txsenha=hash_senha("123456"),
        cargoid=cargo.idcargo,
        deptoid=depto.iddepto,
        aotipousuario="padrao"
    )

    db.add(pessoa)

    db.commit()

    db.refresh(pessoa)

    # ==========================================
    # VÍNCULOS
    # ==========================================

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

    if user.aotipousuario != "admin":

        raise HTTPException(
            status_code=403,
            detail="Apenas admin"
        )

    ramal = db.query(RamalTelefonico).filter(
        RamalTelefonico.idramal == id
    ).first()

    if not ramal:

        raise HTTPException(
            status_code=404,
            detail="Contato não encontrado"
        )

    # ==========================================
    # RAMAL
    # ==========================================

    existe_ramal = db.query(RamalTelefonico).filter(
        RamalTelefonico.nuramal == dados["ramal"],
        RamalTelefonico.idramal != id
    ).first()

    if existe_ramal:

        raise HTTPException(
            status_code=400,
            detail="Ramal já existe"
        )

    ramal.nuramal = dados["ramal"]

    # ==========================================
    # PESSOA
    # ==========================================

    pessoa_link = db.query(RamalPessoa).filter(
        RamalPessoa.ramalid == id
    ).first()

    if pessoa_link:

        pessoa = db.query(Pessoa).filter(
            Pessoa.idpessoa == pessoa_link.pessoaid
        ).first()

        if pessoa:

            pessoa.txnome = dados["nome"]

    # ==========================================
    # DEPARTAMENTO
    # ==========================================

    depto_link = db.query(RamalDepto).filter(
        RamalDepto.ramalid == id
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
# DELETAR CONTATO
# =====================================================

@router.delete("/pessoas/{id}")
def deletar_contato(
    id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    if user.aotipousuario != "admin":

        raise HTTPException(
            status_code=403,
            detail="Apenas admin"
        )

    ramal = db.query(RamalTelefonico).filter(
        RamalTelefonico.idramal == id
    ).first()

    if not ramal:

        raise HTTPException(
            status_code=404,
            detail="Contato não encontrado"
        )

    db.query(RamalPessoa).filter(
        RamalPessoa.ramalid == id
    ).delete()

    db.query(RamalDepto).filter(
        RamalDepto.ramalid == id
    ).delete()

    db.delete(ramal)

    db.commit()

    return {
        "message": "Contato removido"
    }


# =====================================================
# USUÁRIOS
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

    existe = db.query(Pessoa).filter(
        Pessoa.txemail == f"{dados['nome']}@temp.com"
    ).first()

    if existe:

        raise HTTPException(
            status_code=400,
            detail="Usuário já existe"
        )

    cargo = db.query(Cargo).first()
    depto = db.query(Departamento).first()

    novo = Pessoa(
        txnome=dados["nome"],
        txemail=f"{dados['nome']}@temp.com",
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
# ALTERAR SENHA
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

    db.delete(usuario)

    db.commit()

    return {
        "message": "Usuário removido"
    }