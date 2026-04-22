from fastapi import FastAPI, HTTPException, Depends, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base

from passlib.context import CryptContext
from pydantic import BaseModel, validator

from jose import JWTError, jwt
from datetime import datetime, timedelta

from dotenv import load_dotenv
import os

load_dotenv()

# ---------------- CONFIG ----------------
DATABASE_URL = os.getenv("DATABASE_URL")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# ---------------- DB ----------------
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# ---------------- MODELOS ----------------
class Pessoa(Base):
    __tablename__ = "pessoas"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, unique=True, index=True)
    senha_hash = Column(String)
    aotipousuario = Column(String, default="padrao")

class Ramal(Base):
    __tablename__ = "ramais"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String)
    departamento = Column(String)
    ramal = Column(String)

# ---------------- SEGURANÇA ----------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def hash_senha(senha: str):
    return pwd_context.hash(senha)

def verificar_senha(senha: str, senha_hash: str):
    return pwd_context.verify(senha, senha_hash)

def normalizar_username(nome: str):
    return nome.strip().lower()

# ---------------- JWT ----------------
def criar_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def criar_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# ---------------- SCHEMAS ----------------
class UsuarioCreate(BaseModel):
    nome: str
    senha: str
    tipo: str = "padrao"

    @validator("senha")
    def validar_senha(cls, v):
        if len(v) < 6:
            raise ValueError("Senha deve ter no mínimo 6 caracteres")
        return v

    @validator("nome")
    def normalizar_nome(cls, v):
        return v.strip().lower()

class UsuarioUpdate(BaseModel):
    nome: str | None = None
    senha: str | None = None
    tipo: str | None = None

    @validator("senha")
    def validar_senha(cls, v):
        if v and len(v) < 6:
            raise ValueError("Senha deve ter no mínimo 6 caracteres")
        return v

class RamalUpdate(BaseModel):
    nome: str
    departamento: str
    ramal: str

# ---------------- APP ----------------
app = FastAPI()

origins = [
    "https://jvrfurtado.github.io",
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

# ---------------- DB DEP ----------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------- AUTH ----------------
def autenticar(db: Session, nome: str, senha: str):
    nome = normalizar_username(nome)
    user = db.query(Pessoa).filter(Pessoa.nome == nome).first()

    if not user or not verificar_senha(senha, user.senha_hash):
        return None

    return user

@app.post("/token")
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = autenticar(db, form.username, form.password)

    if not user:
        raise HTTPException(status_code=401, detail="Login inválido")

    return {
        "access_token": criar_access_token({"sub": user.nome}),
        "refresh_token": criar_refresh_token({"sub": user.nome}),
        "token_type": "bearer"
    }

@app.post("/refresh")
def refresh(token: str = Form(...)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")

        if not username:
            raise HTTPException(status_code=401, detail="Token inválido")

    except JWTError:
        raise HTTPException(status_code=401, detail="Refresh inválido")

    return {
        "access_token": criar_access_token({"sub": username})
    }

def get_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")

        if not username:
            raise HTTPException(status_code=401, detail="Token inválido")

    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

    user = db.query(Pessoa).filter(Pessoa.nome == username).first()

    if not user:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")

    return user

@app.get("/users/me")
def me(user: Pessoa = Depends(get_user)):
    return {"nome": user.nome, "role": user.aotipousuario}

# ---------------- RAMAIS ----------------
@app.post("/pessoas/")
def criar_ramal(
    nome: str = Form(...),
    departamento: str = Form(...),
    ramal: str = Form(...),
    db: Session = Depends(get_db),
    user: Pessoa = Depends(get_user)
):
    if user.aotipousuario != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado")

    if not nome or not ramal:
        raise HTTPException(status_code=400, detail="Campos obrigatórios")

    novo = Ramal(nome=nome, departamento=departamento, ramal=ramal)

    db.add(novo)
    db.commit()
    db.refresh(novo)

    return novo

@app.get("/pessoas/")
def listar_ramal(
    db: Session = Depends(get_db),
    user: Pessoa = Depends(get_user)
):
    return db.query(Ramal).all()

@app.put("/pessoas/{id}")
def atualizar_ramal(
    id: int,
    dados: RamalUpdate,
    db: Session = Depends(get_db),
    user: Pessoa = Depends(get_user)
):
    if user.aotipousuario != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado")

    obj = db.query(Ramal).filter(Ramal.id == id).first()

    if not obj:
        raise HTTPException(status_code=404, detail="Ramal não encontrado")

    obj.nome = dados.nome
    obj.departamento = dados.departamento
    obj.ramal = dados.ramal

    db.commit()
    db.refresh(obj)

    return obj

@app.delete("/pessoas/{id}")
def deletar_ramal(
    id: int,
    db: Session = Depends(get_db),
    user: Pessoa = Depends(get_user)
):
    if user.aotipousuario != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado")

    obj = db.query(Ramal).filter(Ramal.id == id).first()

    if not obj:
        raise HTTPException(status_code=404, detail="Ramal não encontrado")

    db.delete(obj)
    db.commit()

    return {"msg": "Removido"}

# ---------------- USUÁRIOS ----------------
@app.post("/usuarios/")
def criar_usuario(
    dados: UsuarioCreate,
    db: Session = Depends(get_db),
    user: Pessoa = Depends(get_user)
):
    if user.aotipousuario != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado")

    nome = normalizar_username(dados.nome)

    if db.query(Pessoa).filter(Pessoa.nome == nome).first():
        raise HTTPException(status_code=400, detail="Usuário já existe")

    novo = Pessoa(
        nome=nome,
        senha_hash=hash_senha(dados.senha),
        aotipousuario=dados.tipo
    )

    db.add(novo)
    db.commit()
    db.refresh(novo)

    return novo

@app.get("/usuarios/")
def listar_usuarios(
    db: Session = Depends(get_db),
    user: Pessoa = Depends(get_user)
):
    if user.aotipousuario != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado")

    return db.query(Pessoa).all()

@app.put("/usuarios/{id}")
def atualizar_usuario(
    id: int,
    dados: UsuarioUpdate,
    db: Session = Depends(get_db),
    user: Pessoa = Depends(get_user)
):
    if user.aotipousuario != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado")

    obj = db.query(Pessoa).filter(Pessoa.id == id).first()

    if not obj:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    if obj.id == user.id and dados.tipo and dados.tipo != "admin":
        raise HTTPException(status_code=400, detail="Você não pode remover seu próprio admin")

    if dados.nome:
        obj.nome = normalizar_username(dados.nome)

    if dados.senha:
        obj.senha_hash = hash_senha(dados.senha)

    if dados.tipo:
        if obj.aotipousuario == "admin" and dados.tipo != "admin":
            total_admins = db.query(Pessoa).filter(Pessoa.aotipousuario == "admin").count()
            if total_admins <= 1:
                raise HTTPException(status_code=400, detail="Último admin não pode ser removido")

        obj.aotipousuario = dados.tipo

    db.commit()
    db.refresh(obj)

    return obj

@app.delete("/usuarios/{id}")
def deletar_usuario(
    id: int,
    db: Session = Depends(get_db),
    user: Pessoa = Depends(get_user)
):
    if user.aotipousuario != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado")

    obj = db.query(Pessoa).filter(Pessoa.id == id).first()

    if not obj:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    if obj.id == user.id:
        raise HTTPException(status_code=400, detail="Você não pode excluir a si mesmo")

    if obj.aotipousuario == "admin":
        total_admins = db.query(Pessoa).filter(Pessoa.aotipousuario == "admin").count()
        if total_admins <= 1:
            raise HTTPException(status_code=400, detail="Último admin não pode ser removido")

    db.delete(obj)
    db.commit()

    return {"msg": "Removido"}