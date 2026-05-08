from database import SessionLocal
from models import Pessoa
from auth import hash_senha

db = SessionLocal()

admin = db.query(Pessoa).filter(
    Pessoa.txemail == "admin@admin.com"
).first()

if not admin:

    novo = Pessoa(
        txnome="Administrador",
        txemail="admin@admin.com",
        txsenha=hash_senha("123456"),
        cargoid=1,
        deptoid=1,
        aotipousuario="admin"
    )

    db.add(novo)
    db.commit()

    print("Admin criado")