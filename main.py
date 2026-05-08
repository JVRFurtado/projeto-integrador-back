# main.py

from datetime import datetime, timedelta
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from jose import JWTError, jwt
import hashlib

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DateTime
)

from sqlalchemy.orm import (
    sessionmaker,
    declarative_base,
    Session
)

import os

# =========================================================
# DATABASE
# =========================================================

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./test.db"
)

# Corrige URL mysql do Railway
if DATABASE_URL.startswith("mysql://"):
    DATABASE_URL = DATABASE_URL.replace(
        "mysql://",
        "mysql+pymysql://",
        1
    )

print("DATABASE_URL:", DATABASE_URL)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

# =========================================================
# JWT / AUTH
# =========================================================

SECRET_KEY = "123456789"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token"
)

# =========================================================
# MODELS
# =========================================================

class Cargo(Base):
    __tablename__ = "cargos"

    idcargo = Column(
        Integer,
        primary_key=True,
        index=True
    )

    txnome = Column(
        String(100),
        nullable=False
    )

    dtcadcargo = Column(
        DateTime,
        default=datetime.utcnow
    )


class Usuario(Base):
    __tablename__ = "usuarios"

    idusuario = Column(
        Integer,
        primary_key=True,
        index=True
    )

    nome = Column(
        String(100),
        nullable=False
    )

    email = Column(
        String(150),
        unique=True,
        nullable=False
    )

    senha = Column(
        String(255),
        nullable=False
    )

    dtcadusuario = Column(
        DateTime,
        default=datetime.utcnow
    )

# =========================================================
# CREATE TABLES
# =========================================================

Base.metadata.create_all(bind=engine)

# =========================================================
# FASTAPI
# =========================================================

app = FastAPI(
    title="Projeto Integrador API"
)

# =========================================================
# DEPENDENCY
# =========================================================

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

# =========================================================
# SECURITY
# =========================================================

def gerar_hash(senha):
    return hashlib.sha256(
        senha.encode()
    ).hexdigest()

def verificar_senha(
    senha,
    hash_senha
):
    return gerar_hash(senha) == hash_senha

def criar_token(data: dict):
    dados = data.copy()

    expire = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    dados.update({
        "exp": expire
    })

    return jwt.encode(
        dados,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

# =========================================================
# SCHEMAS
# =========================================================

class UsuarioCreate(BaseModel):
    nome: str
    email: EmailStr
    senha: str


class UsuarioResponse(BaseModel):
    idusuario: int
    nome: str
    email: EmailStr

    class Config:
        from_attributes = True

# =========================================================
# INIT ADMIN
# =========================================================

def criar_admin():

    db = SessionLocal()

    try:

        admin = db.query(Usuario).filter(
            Usuario.email == "admin@admin.com"
        ).first()

        if admin:
            print("ℹ️ Admin já existe")
            return

        novo_admin = Usuario(
            nome="Administrador",
            email="admin@admin.com",
            senha=gerar_hash("123456")
        )

        db.add(novo_admin)
        db.commit()

        print("✅ Admin criado")

    finally:
        db.close()


criar_admin()

# =========================================================
# ROUTES
# =========================================================

@app.get("/")
def root():
    return {
        "mensagem": "API funcionando"
    }


@app.post(
    "/usuarios",
    response_model=UsuarioResponse
)
def criar_usuario(
    usuario: UsuarioCreate,
    db: Session = Depends(get_db)
):

    existe = db.query(Usuario).filter(
        Usuario.email == usuario.email
    ).first()

    if existe:
        raise HTTPException(
            status_code=400,
            detail="Email já cadastrado"
        )

    novo_usuario = Usuario(
        nome=usuario.nome,
        email=usuario.email,
        senha=gerar_hash(usuario.senha)
    )

    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)

    return novo_usuario


@app.post("/token")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    usuario = db.query(Usuario).filter(
        Usuario.email == form_data.username
    ).first()

    if not usuario:
        raise HTTPException(
            status_code=401,
            detail="Usuário inválido"
        )

    if not verificar_senha(
        form_data.password,
        usuario.senha
    ):
        raise HTTPException(
            status_code=401,
            detail="Senha inválida"
        )

    access_token = criar_token({
        "sub": usuario.email
    })

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@app.get("/usuarios")
def listar_usuarios(
    db: Session = Depends(get_db)
):

    usuarios = db.query(Usuario).all()

    return usuarios