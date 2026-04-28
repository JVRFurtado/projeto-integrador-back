from fastapi import FastAPI, HTTPException, Depends, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base

from passlib.context import CryptContext
from pydantic import BaseModel

from jose import JWTError, jwt
from datetime import datetime, timedelta

import os

# ---------------- CONFIG ----------------
DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY", "secret")
ALGORITHM = "HS256"

# ---------------- DB ----------------
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# ---------------- MODELOS ----------------
class Cargo(Base):
    __tablename__ = "cargos"
    idcargo = Column(Integer, primary_key=True)
    txnome = Column(String)

class Departamento(Base):
    __tablename__ = "departamentos"
    iddepto = Column(Integer, primary_key=True)
    txnomedepto = Column(String)

class Pessoa(Base):
    __tablename__ = "pessoas"

    idpessoa = Column(Integer, primary_key=True)
    txnome = Column(String)
    txemail = Column(String)
    txsenha = Column(String)

    cargoid = Column(Integer, ForeignKey("cargos.idcargo"))
    deptoid = Column(Integer, ForeignKey("departamentos.iddepto"))

    aotipousuario = Column(String, default="padrao")

class RamalTelefonico(Base):
    __tablename__ = "ramais_telefonicos"

    idramal = Column(Integer, primary_key=True)
    nuramal = Column(String)

class RamalPessoa(Base):
    __tablename__ = "ramal_pessoas"

    pessoaid = Column(Integer, ForeignKey("pessoas.idpessoa"), primary_key=True)
    ramalid = Column(Integer, ForeignKey("ramais_telefonicos.idramal"), primary_key=True)

class RamalDepto(Base):
    __tablename__ = "ramal_depto"

    deptoid = Column(Integer, ForeignKey("departamentos.iddepto"), primary_key=True)
    ramalid = Column(Integer, ForeignKey("ramais_telefonicos.idramal"), primary_key=True)

# ---------------- SEGURANÇA ----------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def hash_senha(senha: str):
    return pwd_context.hash(senha)

def verificar_senha(senha: str, senha_hash: str):
    return pwd_context.verify(senha, senha_hash)

# ---------------- JWT ----------------
def criar_access_token(data: dict):
    expire = datetime.utcnow() + timedelta(minutes=30)
    data.update({"exp": expire})
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

# ---------------- APP ----------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
    user = db.query(Pessoa).filter(Pessoa.txnome == nome).first()
    if not user or not verificar_senha(senha, user.txsenha):
        return None
    return user

@app.post("/token")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = autenticar(db, form.username, form.password)

    if not user:
        raise HTTPException(status_code=401, detail="Login inválido")

    return {
        "access_token": criar_access_token({"sub": user.txnome}),
        "refresh_token": criar_access_token({"sub": user.txnome}),
        "token_type": "bearer"
    }

def get_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        nome = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401)

    user = db.query(Pessoa).filter(Pessoa.txnome == nome).first()
    if not user:
        raise HTTPException(status_code=401)

    return user

@app.get("/users/me")
def me(user: Pessoa = Depends(get_user)):
    return {"nome": user.txnome, "role": user.aotipousuario}

# ---------------- CONTATOS  ----------------

@app.get("/pessoas/")
def listar_contatos(db: Session = Depends(get_db), user: Pessoa = Depends(get_user)):
    resultado = []

    ramais = db.query(RamalTelefonico).all()

    for r in ramais:
        pessoa_link = db.query(RamalPessoa).filter_by(ramalid=r.idramal).first()
        depto_link = db.query(RamalDepto).filter_by(ramalid=r.idramal).first()

        pessoa = db.query(Pessoa).filter_by(idpessoa=pessoa_link.pessoaid).first() if pessoa_link else None
        depto = db.query(Departamento).filter_by(iddepto=depto_link.deptoid).first() if depto_link else None

        resultado.append({
            "id": r.idramal,
            "nome": pessoa.txnome if pessoa else "",
            "departamento": depto.txnomedepto if depto else "",
            "ramal": r.nuramal
        })

    return resultado

@app.post("/pessoas/")
def criar_contato(
    nome: str = Form(...),
    departamento: str = Form(...),
    ramal: str = Form(...),
    db: Session = Depends(get_db),
    user: Pessoa = Depends(get_user)
):
    if user.aotipousuario != "admin":
        raise HTTPException(status_code=403)

    depto = db.query(Departamento).filter_by(txnomedepto=departamento).first()
    if not depto:
        depto = Departamento(txnomedepto=departamento)
        db.add(depto)
        db.commit()
        db.refresh(depto)

    pessoa = db.query(Pessoa).filter_by(txnome=nome).first()
    if not pessoa:
        raise HTTPException(status_code=404, detail="Pessoa não encontrada")

    novo_ramal = RamalTelefonico(nuramal=ramal)
    db.add(novo_ramal)
    db.commit()
    db.refresh(novo_ramal)

    db.add(RamalPessoa(pessoaid=pessoa.idpessoa, ramalid=novo_ramal.idramal))
    db.add(RamalDepto(deptoid=depto.iddepto, ramalid=novo_ramal.idramal))

    db.commit()

    return {"msg": "Criado"}

@app.put("/pessoas/{id}")
def atualizar_contato(
    id: int,
    dados: dict,
    db: Session = Depends(get_db),
    user: Pessoa = Depends(get_user)
):
    if user.aotipousuario != "admin":
        raise HTTPException(status_code=403)

    ramal = db.query(RamalTelefonico).filter_by(idramal=id).first()
    if not ramal:
        raise HTTPException(status_code=404)

    ramal.nuramal = dados.get("ramal", ramal.nuramal)
    db.commit()

    return {"msg": "Atualizado"}

@app.delete("/pessoas/{id}")
def deletar_contato(
    id: int,
    db: Session = Depends(get_db),
    user: Pessoa = Depends(get_user)
):
    if user.aotipousuario != "admin":
        raise HTTPException(status_code=403)

    ramal = db.query(RamalTelefonico).filter_by(idramal=id).first()
    if not ramal:
        raise HTTPException(status_code=404)

    db.delete(ramal)
    db.commit()

    return {"msg": "Removido"}

# ---------------- USUÁRIOS ----------------

class UsuarioCreate(BaseModel):
    nome: str
    senha: str
    tipo: str = "padrao"

@app.post("/usuarios/")
def criar_usuario(
    dados: UsuarioCreate,
    db: Session = Depends(get_db),
    user: Pessoa = Depends(get_user)
):
    if user.aotipousuario != "admin":
        raise HTTPException(status_code=403)

    novo = Pessoa(
        txnome=dados.nome,
        txemail=f"{dados.nome}@fake.com",
        txsenha=hash_senha(dados.senha),
        cargoid=1,
        deptoid=1,
        aotipousuario=dados.tipo
    )

    db.add(novo)
    db.commit()

    return novo

@app.get("/usuarios/")
def listar_usuarios(db: Session = Depends(get_db), user: Pessoa = Depends(get_user)):
    if user.aotipousuario != "admin":
        raise HTTPException(status_code=403)

    return db.query(Pessoa).all()

@app.put("/usuarios/{id}")
def atualizar_usuario(
    id: int,
    dados: dict,
    db: Session = Depends(get_db),
    user: Pessoa = Depends(get_user)
):
    if user.aotipousuario != "admin":
        raise HTTPException(status_code=403)

    obj = db.query(Pessoa).filter_by(idpessoa=id).first()
    if not obj:
        raise HTTPException(status_code=404)

    if dados.get("senha"):
        obj.txsenha = hash_senha(dados["senha"])

    db.commit()
    return obj

@app.delete("/usuarios/{id}")
def deletar_usuario(
    id: int,
    db: Session = Depends(get_db),
    user: Pessoa = Depends(get_user)
):
    if user.aotipousuario != "admin":
        raise HTTPException(status_code=403)

    obj = db.query(Pessoa).filter_by(idpessoa=id).first()
    if not obj:
        raise HTTPException(status_code=404)

    db.delete(obj)
    db.commit()

    return {"msg": "Removido"}

# ---------------- STARTUP ----------------
@app.on_event("startup")
def startup():
    db = SessionLocal()

    try:
        if not db.query(Cargo).first():
            db.add(Cargo(txnome="Admin"))

        if not db.query(Departamento).first():
            db.add(Departamento(txnomedepto="TI"))

        db.commit()

        if not db.query(Pessoa).filter(Pessoa.txnome == "admin").first():
            admin = Pessoa(
                txnome="admin",
                txemail="admin@admin.com",
                txsenha=hash_senha("123456"),
                cargoid=1,
                deptoid=1,
                aotipousuario="admin"
            )
            db.add(admin)
            db.commit()

            print("Admin criado!")

    finally:
        db.close()