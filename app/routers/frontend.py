from fastapi import (
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

    if usuario.aotipousuario == "admin" and user.idpessoa != usuario.idpessoa:
        raise HTTPException(
            status_code=403,
            detail="Você não pode alterar outro admin"
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
            detail="Você não pode excluir sua própria conta"
        )

    usuario = db.query(Pessoa).filter(
        Pessoa.idpessoa == id
    ).first()

    if not usuario:

        raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado"
        )

    if usuario.aotipousuario == "admin":
        raise HTTPException(
            status_code=403,
            detail="Você não pode excluir outro admin"
        )

    links = db.query(RamalPessoa).filter(
        RamalPessoa.pessoaid == usuario.idpessoa
    ).all()

    for link in links:
        db.delete(link)

    db.delete(usuario)

    db.commit()

    return {
        "message": "Usuário removido"
    }
