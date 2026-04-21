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

# ================= ENV =================
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")

if not DATABASE_URL:
    raise Exception("DATABASE_URL não definida")

if not SECRET_KEY:
    raise Exception("SECRET_KEY não definida")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# ================= DB =================
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

# ================= MODELOS =================
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

Base.metadata.create_all(bind=engine)

# ================= APP =================
app = FastAPI()

# ================= CORS =================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://jvrfurtado.github.io",
        "https://jvrfurtado.github.io/projeto-integrador"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= SECURITY =================
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def hash_senha(senha: str):
    return pwd_context.hash(senha)


def verificar_senha(senha: str, hash_: str):
    return pwd_context.verify(senha, hash_)


def normalizar(nome: str):
    return nome.strip().lower()

# ================= JWT =================
def criar_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ================= SCHEMAS =================
class UsuarioCreate(BaseModel):
    nome: str
    senha: str
    tipo: str = "padrao"

    @validator("senha")
    def senha_valida(cls, v):
        if len(v) < 6:
            raise ValueError("Senha deve ter no mínimo 6 caracteres")
        return v

    @validator("nome")
    def nome_formatado(cls, v):
        return v.strip().lower()


class RamalUpdate(BaseModel):
    nome: str
    departamento: str
    ramal: str


# ================= DB DEP =================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ================= AUTH =================
def autenticar(db: Session, nome: str, senha: str):
    nome = normalizar(nome)
    user = db.query(Pessoa).filter(Pessoa.nome == nome).first()

    if not user or not verificar_senha(senha, user.senha_hash):
        return None

    return user


@app.post("/token")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = autenticar(db, form.username, form.password)

    if not user:
        raise HTTPException(status_code=401, detail="Login inválido")

    access_token = criar_token(
        {"sub": user.nome},
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    refresh_token = criar_token(
        {"sub": user.nome},
        timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
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

    new_token = criar_token(
        {"sub": username},
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {"access_token": new_token}


def get_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
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


# ================= RAMAIS =================
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

    novo = Ramal(nome=nome, departamento=departamento, ramal=ramal)
    db.add(novo)
    db.commit()
    db.refresh(novo)

    return novo


@app.get("/pessoas/")
def listar(db: Session = Depends(get_db), user: Pessoa = Depends(get_user)):
    return db.query(Ramal).all()


@app.put("/pessoas/{id}")
def atualizar(id: int, dados: RamalUpdate, db: Session = Depends(get_db), user: Pessoa = Depends(get_user)):
    if user.aotipousuario != "admin":
        raise HTTPException(status_code=403)

    obj = db.query(Ramal).filter(Ramal.id == id).first()

    if not obj:
        raise HTTPException(status_code=404)

    obj.nome = dados.nome
    obj.departamento = dados.departamento
    obj.ramal = dados.ramal

    db.commit()
    return obj


@app.delete("/pessoas/{id}")
def deletar(id: int, db: Session = Depends(get_db), user: Pessoa = Depends(get_user)):
    if user.aotipousuario != "admin":
        raise HTTPException(status_code=403)

    obj = db.query(Ramal).filter(Ramal.id == id).first()

    if not obj:
        raise HTTPException(status_code=404)

    db.delete(obj)
    db.commit()

    return {"msg": "Removido"}