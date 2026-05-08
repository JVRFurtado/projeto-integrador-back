from fastapi import HTTPException

def require_admin(user):
    if user.aotipousuario != "admin":
        raise HTTPException(
            403,
            "Acesso negado"
        )

def require_gestor_or_admin(user):
    if user.aotipousuario not in [
        "admin",
        "gestor"
    ]:
        raise HTTPException(
            403,
            "Acesso negado"
        )

def gestor_cannot_manage_admin(
    current_user,
    target_user
):
    if (
        current_user.aotipousuario == "gestor"
        and target_user.aotipousuario == "admin"
    ):
        raise HTTPException(
            403,
            "Gestor não pode gerenciar admin"
        )