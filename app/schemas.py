from pydantic import (
    BaseModel,
    EmailStr,
    field_validator
)

from typing import Optional
from datetime import datetime


# =========================================================
# AUTH
# =========================================================

class Token(BaseModel):
    access_token: str
    token_type: str


# =========================================================
# CARGOS
# =========================================================

class CargoBase(BaseModel):
    txnome: str

    @field_validator("txnome")
    @classmethod
    def validar_nome(cls, v: str):

        v = v.strip()

        if len(v) < 2:
            raise ValueError(
                "Nome do cargo inválido"
            )

        return v


class CargoCreate(CargoBase):
    pass


class CargoUpdate(BaseModel):
    txnome: Optional[str] = None

    @field_validator("txnome")
    @classmethod
    def validar_nome(cls, v):

        if v is None:
            return v

        v = v.strip()

        if len(v) < 2:
            raise ValueError(
                "Nome do cargo inválido"
            )

        return v


class CargoResponse(CargoBase):
    idcargo: int
    dtcadcargo: datetime

    class Config:
        from_attributes = True


# =========================================================
# DEPARTAMENTOS
# =========================================================

class DepartamentoBase(BaseModel):
    txnomedepto: str

    @field_validator("txnomedepto")
    @classmethod
    def validar_nome(cls, v: str):

        v = v.strip()

        if len(v) < 2:
            raise ValueError(
                "Nome do departamento inválido"
            )

        return v


class DepartamentoCreate(DepartamentoBase):
    pass


class DepartamentoUpdate(BaseModel):
    txnomedepto: Optional[str] = None

    @field_validator("txnomedepto")
    @classmethod
    def validar_nome(cls, v):

        if v is None:
            return v

        v = v.strip()

        if len(v) < 2:
            raise ValueError(
                "Nome do departamento inválido"
            )

        return v


class DepartamentoResponse(DepartamentoBase):
    iddepto: int
    dtcaddepto: datetime

    class Config:
        from_attributes = True


# =========================================================
# PESSOAS
# =========================================================

class PessoaBase(BaseModel):

    txnome: str

    txemail: EmailStr

    cargoid: int

    deptoid: int

    aotipousuario: str = "padrao"

    @field_validator("txnome")
    @classmethod
    def validar_nome(cls, v: str):

        v = v.strip()

        if len(v) < 3:
            raise ValueError(
                "Nome inválido"
            )

        return v


class PessoaCreate(PessoaBase):

    txsenha: str

    @field_validator("txsenha")
    @classmethod
    def validar_senha(cls, v: str):

        if len(v) < 6:
            raise ValueError(
                "Senha deve ter no mínimo 6 caracteres"
            )

        return v


class PessoaUpdate(BaseModel):

    txnome: Optional[str] = None

    txemail: Optional[EmailStr] = None

    txsenha: Optional[str] = None

    cargoid: Optional[int] = None

    deptoid: Optional[int] = None

    aotipousuario: Optional[str] = None

    @field_validator("txsenha")
    @classmethod
    def validar_senha(cls, v):

        if v is None:
            return v

        if len(v) < 6:
            raise ValueError(
                "Senha deve ter no mínimo 6 caracteres"
            )

        return v


class PessoaResponse(BaseModel):

    idpessoa: int

    txnome: str

    txemail: str

    cargoid: int

    deptoid: int

    aotipousuario: str

    dtcadpessoa: datetime

    class Config:
        from_attributes = True


# =========================================================
# RAMAIS
# =========================================================

class RamalBase(BaseModel):

    nuramal: str

    nuvoip: Optional[str] = None

    @field_validator("nuramal")
    @classmethod
    def validar_ramal(cls, v: str):

        v = v.strip()

        if len(v) < 2:
            raise ValueError(
                "Ramal inválido"
            )

        return v


class RamalCreate(RamalBase):
    pass


class RamalUpdate(BaseModel):

    nuramal: Optional[str] = None

    nuvoip: Optional[str] = None


class RamalResponse(RamalBase):

    idramal: int

    dtcadramal: datetime

    dtedicao: Optional[datetime]

    class Config:
        from_attributes = True


# =========================================================
# RAMAL PESSOAS
# =========================================================

class RamalPessoaCreate(BaseModel):

    pessoaid: int

    ramalid: int


# =========================================================
# RAMAL DEPTO
# =========================================================

class RamalDeptoCreate(BaseModel):

    deptoid: int

    ramalid: int