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

    relacoes = db.query(RamalPessoa).filter(
        RamalPessoa.pessoaid == pessoa.idpessoa
    ).all()

    for rel in relacoes:

        db.delete(rel)

        ramal = db.query(RamalTelefonico).filter(
            RamalTelefonico.idramal == rel.ramalid
        ).first()

        if ramal:

            deptos = db.query(RamalDepto).filter(
                RamalDepto.ramalid == ramal.idramal
            ).all()

            for d in deptos:
                db.delete(d)

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

    if user.aotipousuario not in [
        "admin",
        "gestor"
    ]:

        raise HTTPException(
            status_code=403,
            detail="Sem permissão"
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

    if user.aotipousuario not in [
        "admin",
        "gestor"
    ]:

        raise HTTPException(
            status_code=403,
            detail="Sem permissão"
        )

    tipo = dados.get("tipo", "padrao")

    # gestor não pode criar admin
    if (
        user.aotipousuario == "gestor"
        and tipo == "admin"
    ):
        raise HTTPException(
            status_code=403,
            detail="Gestor não pode criar admin"
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
        aotipousuario=tipo
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

    if user.aotipousuario not in [
        "admin",
        "gestor"
    ]:

        raise HTTPException(
            status_code=403,
            detail="Sem permissão"
        )

    usuario = db.query(Pessoa).filter(
        Pessoa.idpessoa == id
    ).first()

    if not usuario:

        raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado"
        )

    # gestor não pode alterar admin/gestor
    if (
        user.aotipousuario == "gestor"
        and usuario.aotipousuario in ["admin", "gestor"]
        and usuario.idpessoa != user.idpessoa
    ):
        raise HTTPException(
            status_code=403,
            detail="Gestor não pode alterar admin ou gestor"
        )

    # =========================================
    # VALIDA USERNAME ÚNICO
    # =========================================

    if "username" in dados:

        existe = db.query(Pessoa).filter(
            Pessoa.txusername == dados["username"],
            Pessoa.idpessoa != id
        ).first()

        if existe:

            raise HTTPException(
                status_code=400,
                detail="Username já existe"
            )

        usuario.txusername = dados["username"]

    # =========================================
    # VALIDA EMAIL ÚNICO
    # =========================================

    if "email" in dados:

        existe = db.query(Pessoa).filter(
            Pessoa.txemail == dados["email"],
            Pessoa.idpessoa != id
        ).first()

        if existe:

            raise HTTPException(
                status_code=400,
                detail="Email já existe"
            )

        usuario.txemail = dados["email"]

    # =========================================
    # NOME
    # =========================================

    if "nome" in dados:

        usuario.txnome = dados["nome"]

    # =========================================
    # TIPO
    # =========================================

    if "tipo" in dados:

        # gestor não pode promover admin
        if (
            user.aotipousuario == "gestor"
            and dados["tipo"] == "admin"
        ):
            raise HTTPException(
                status_code=403,
                detail="Gestor não pode promover admin"
            )

        usuario.aotipousuario = dados["tipo"]

    # =========================================
    # SENHA
    # =========================================

    if dados.get("senha"):

        if len(dados["senha"]) < 6:

            raise HTTPException(
                status_code=400,
                detail="Senha deve ter pelo menos 6 caracteres"
            )

        # gestor não pode alterar senha de admin/gestor
        if (
            user.aotipousuario == "gestor"
            and usuario.aotipousuario in ["admin", "gestor"]
            and usuario.idpessoa != user.idpessoa
        ):
            raise HTTPException(
                status_code=403,
                detail="Gestor não pode alterar senha de admin ou gestor"
            )

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

    if user.aotipousuario not in [
        "admin",
        "gestor"
    ]:

        raise HTTPException(
            status_code=403,
            detail="Sem permissão"
        )

    usuario = db.query(Pessoa).filter(
        Pessoa.idpessoa == id
    ).first()

    if not usuario:

        raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado"
        )

    # gestor não pode excluir admin/gestor
    if (
        user.aotipousuario == "gestor"
        and usuario.aotipousuario in ["admin", "gestor"]
    ):
        raise HTTPException(
            status_code=403,
            detail="Gestor não pode excluir admin ou gestor"
        )

    # ninguém pode excluir a própria conta
    if usuario.idpessoa == user.idpessoa:

        raise HTTPException(
            status_code=400,
            detail="Não pode excluir a própria conta"
        )

    # REMOVE RELACIONAMENTOS
    relacoes = db.query(RamalPessoa).filter(
        RamalPessoa.pessoaid == usuario.idpessoa
    ).all()

    for rel in relacoes:

        db.delete(rel)

        ramal = db.query(RamalTelefonico).filter(
            RamalTelefonico.idramal == rel.ramalid
        ).first()

        if ramal:

            deptos = db.query(RamalDepto).filter(
                RamalDepto.ramalid == ramal.idramal
            ).all()

            for d in deptos:
                db.delete(d)

            db.delete(ramal)

    db.delete(usuario)

    db.commit()

    return {
        "message": "Usuário removido"
    }
