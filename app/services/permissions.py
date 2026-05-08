from fastapi import HTTPException


def require_admin(user):

    if user.aotipousuario != "admin":

        raise HTTPException(
            status_code=403,
            detail="Apenas admin"
        )


def require_gestor(user):

    if user.aotipousuario not in [
        "admin",
        "gestor"
    ]:

        raise HTTPException(
            status_code=403,
            detail="Sem permissão"
        )
