from pydantic import BaseModel, EmailStr


class UsuarioCreate(BaseModel):
    txnome: str
    txemail: EmailStr
    txsenha: str
    cargoid: int
    deptoid: int
    aotipousuario: str = "padrao"


class UsuarioUpdate(BaseModel):
    txnome: str | None = None
    txemail: EmailStr | None = None
    txsenha: str | None = None
    cargoid: int | None = None
    deptoid: int | None = None
    aotipousuario: str | None = None


class RamalCreate(BaseModel):
    nuramal: str
    nuvoip: str | None = None
    pessoaid: int
    deptoid: int


class RamalUpdate(BaseModel):
    nuramal: str | None = None
    nuvoip: str | None = None