from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Enum,
    Table
)

from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base

# ---------------- ASSOC TABLES ----------------

ramal_pessoas = Table(
    "ramal_pessoas",
    Base.metadata,

    Column(
        "pessoaid",
        Integer,
        ForeignKey("pessoas.idpessoa"),
        primary_key=True
    ),

    Column(
        "ramalid",
        Integer,
        ForeignKey("ramais_telefonicos.idramal"),
        primary_key=True
    )
)

ramal_depto = Table(
    "ramal_depto",
    Base.metadata,

    Column(
        "deptoid",
        Integer,
        ForeignKey("departamentos.iddepto"),
        primary_key=True
    ),

    Column(
        "ramalid",
        Integer,
        ForeignKey("ramais_telefonicos.idramal"),
        primary_key=True
    )
)

# ---------------- CARGOS ----------------

class Cargo(Base):
    __tablename__ = "cargos"

    idcargo = Column(Integer, primary_key=True)
    txnome = Column(String(100), unique=True)

# ---------------- DEPARTAMENTOS ----------------

class Departamento(Base):
    __tablename__ = "departamentos"

    iddepto = Column(Integer, primary_key=True)

    txnomedepto = Column(String(100), unique=True)

# ---------------- PESSOAS ----------------

class Pessoa(Base):
    __tablename__ = "pessoas"

    idpessoa = Column(Integer, primary_key=True)

    txnome = Column(String(100))
    txemail = Column(String(150), unique=True)
    txsenha = Column(String(255))

    cargoid = Column(
        Integer,
        ForeignKey("cargos.idcargo")
    )

    deptoid = Column(
        Integer,
        ForeignKey("departamentos.iddepto")
    )

    aotipousuario = Column(
        Enum(
            "admin",
            "gestor",
            "padrao",
            name="tipo_usuario"
        ),
        default="padrao"
    )

    departamento = relationship("Departamento")
    cargo = relationship("Cargo")

    ramais = relationship(
        "RamalTelefonico",
        secondary=ramal_pessoas,
        back_populates="pessoas"
    )

# ---------------- RAMAIS ----------------

class RamalTelefonico(Base):
    __tablename__ = "ramais_telefonicos"

    idramal = Column(Integer, primary_key=True)

    nuramal = Column(String(20), unique=True)

    nuvoip = Column(String(50))

    dtedicao = Column(DateTime)

    pessoas = relationship(
        "Pessoa",
        secondary=ramal_pessoas,
        back_populates="ramais"
    )

    departamentos = relationship(
        "Departamento",
        secondary=ramal_depto
    )