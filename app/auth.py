from pydantic import BaseModel, field_validator

# ---------------- LOGIN ----------------

class UsuarioLogin(BaseModel):
    username: str
    password: str

# ---------------- USERS ----------------

class UsuarioCreate(BaseModel):
    nome: str
    email: str
    senha: str
    cargoid: int
    deptoid: int
    tipo: str = "padrao"

    @field_validator("senha")
    def validar_senha(cls, v):
        if len(v) < 6:
            raise ValueError(
                "Senha deve ter no mínimo 6 caracteres"
            )
        return v

class UsuarioUpdate(BaseModel):
    senha: str | None = None
    tipo: str | None = None

# ---------------- RAMAIS ----------------

class RamalCreate(BaseModel):
    nome: str
    departamento: str
    ramal: str

class RamalUpdate(RamalCreate):
    pass