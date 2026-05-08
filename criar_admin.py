from app.database import SessionLocal

from app.models import (
    Pessoa,
    Cargo,
    Departamento
)

from app.security import hash_senha


def criar_admin():

    db = SessionLocal()

    cargo = db.query(Cargo).first()

    if not cargo:

        cargo = Cargo(
            txnome="Administrador"
        )

        db.add(cargo)

        db.commit()

        db.refresh(cargo)

    depto = db.query(Departamento).first()

    if not depto:

        depto = Departamento(
            txnomedepto="TI"
        )

        db.add(depto)

        db.commit()

        db.refresh(depto)

    existe = db.query(Pessoa).filter(
        Pessoa.txemail == "admin@admin.com"
    ).first()

    if existe:
        print("Admin já existe")
        return

    admin = Pessoa(
        txnome="Administrador",
        txusername="admin",
        txemail="admin@admin.com",
        txsenha=hash_senha("123456"),
        cargoid=cargo.idcargo,
        deptoid=depto.iddepto,
        aotipousuario="admin"
    )

    db.add(admin)

    db.commit()

    db.refresh(admin)

    print("===================================")
    print("ADMIN CRIADO")
    print(f"ID LOGIN: {admin.idpessoa}")
    print("SENHA: 123456")
    print("===================================")


if __name__ == "__main__":
    criar_admin()
