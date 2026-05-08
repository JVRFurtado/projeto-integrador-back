from database import SessionLocal
from models import (
    Pessoa,
    Cargo,
    Departamento
)

from auth import hash_senha

def criar_cargo_padrao(db):
    cargo = (
        db.query(Cargo)
        .filter(
            Cargo.txnome == "Administrador"
        )
        .first()
    )

    if not cargo:
        cargo = Cargo(
            txnome="Administrador"
        )

        db.add(cargo)
        db.commit()
        db.refresh(cargo)

    return cargo

def criar_departamento_padrao(db):
    departamento = (
        db.query(Departamento)
        .filter(
            Departamento.txnomedepto == "TI"
        )
        .first()
    )

    if not departamento:
        departamento = Departamento(
            txnomedepto="TI"
        )

        db.add(departamento)
        db.commit()
        db.refresh(departamento)

    return departamento

def criar_admin():
    db = SessionLocal()

    try:

        existe = (
            db.query(Pessoa)
            .filter(
                Pessoa.txemail == "admin@admin.com"
            )
            .first()
        )

        if existe:
            print("ℹ️ Admin já existe")
            print(f"🆔 ID: {existe.idpessoa}")
            return

        cargo = criar_cargo_padrao(db)

        departamento = criar_departamento_padrao(db)

        admin = Pessoa(
            txnome="Administrador",
            txemail="admin@admin.com",
            txsenha=hash_senha("123456"),
            cargoid=cargo.idcargo,
            deptoid=departamento.iddepto,
            aotipousuario="admin"
        )

        db.add(admin)

        db.commit()

        db.refresh(admin)

        print("✅ Admin criado")
        print(f"🆔 Login ID: {admin.idpessoa}")
        print("🔑 Senha: 123456")

    finally:
        db.close()

if __name__ == "__main__":
    criar_admin()