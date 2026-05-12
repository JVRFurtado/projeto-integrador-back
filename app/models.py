from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Enum,
    ForeignKey
)

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Cargo(Base):
    __tablename__ = "cargos"

    idcargo = Column(Integer, primary_key=True)
    txnome = Column(String(100), unique=True, nullable=False)
    dtcadcargo = Column(DateTime, server_default=func.now())


class Departamento(Base):
    __tablename__ = "departamentos"

    iddepto = Column(Integer, primary_key=True)
    txnomedepto = Column(String(100), unique=True, nullable=False)
    dtcaddepto = Column(DateTime, server_default=func.now())


class Pessoa(Base):
    __tablename__ = "pessoas"

    idpessoa = Column(Integer, primary_key=True)

    txnome = Column(String(100), nullable=False)

    txusername = Column(
        String(50),
        unique=True,
        nullable=False
    )

    txemail = Column(
        String(150),
        unique=True,
        nullable=False
    )

    txsenha = Column(String(255), nullable=False)

    cargoid = Column(
        Integer,
        ForeignKey("cargos.idcargo")
    )

    deptoid = Column(
        Integer,
        ForeignKey("departamentos.iddepto")
    )

    aotipousuario = Column(
        Enum("admin", "gestor", "padrao"),
        default="padrao",
        nullable=False
    )

    dtcadpessoa = Column(
        DateTime,
        server_default=func.now()
    )

    dtedicaopessoa = Column(DateTime)

    cargo = relationship("Cargo")

    departamento = relationship("Departamento")

class RamalTelefonico(Base):
    __tablename__ = "ramais_telefonicos"

    idramal = Column(Integer, primary_key=True)

    nuramal = Column(String(20), unique=True, nullable=False)

    nuvoip = Column(String(50))

    dtedicao = Column(DateTime)

    dtcadramal = Column(DateTime, server_default=func.now())


class RamalPessoa(Base):
    __tablename__ = "ramal_pessoas"

    pessoaid = Column(
        Integer,
        ForeignKey(
            "pessoas.idpessoa",
            ondelete="CASCADE"
        ),
        primary_key=True
    )

    ramalid = Column(
        Integer,
        ForeignKey(
            "ramais_telefonicos.idramal",
            ondelete="CASCADE"
        ),
        primary_key=True
    )

    dtcadramalpessoa = Column(
        DateTime,
        server_default=func.now()
    )


class RamalDepto(Base):
    __tablename__ = "ramal_depto"

    deptoid = Column(
        Integer,
        ForeignKey(
            "departamentos.iddepto",
            ondelete="CASCADE"
        ),
        primary_key=True
    )

    ramalid = Column(
        Integer,
        ForeignKey(
            "ramais_telefonicos.idramal",
            ondelete="CASCADE"
        ),
        primary_key=True
    )

    dtcadramaldepto = Column(
        DateTime,
        server_default=func.now()
    )
