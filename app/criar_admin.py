from database import SessionLocal
from models import Pessoa, Cargo, Departamento
from security import hash_senha


def criar_admin():
    db = SessionLocal()

    try:
        cargo = db.query(Cargo).first()

        if not cargo:
            cargo = Cargo(txnome="Administrador")
            db.add(cargo)
            db.commit()
            db.refresh(cargo)

        departamento = db.query(Departamento).first()

        if not departamento:
            departamento = Departamento(
                txnomedepto="TI"
            )

            db.add(departamento)
            db.commit()
            db.refresh(departamento)

        existe = (
            db.query(Pessoa)
            .filter(Pessoa.idpessoa == 1)
            .first()
        )

        if existe:
            print("ℹ️ Admin já existe")
            return

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

        print("✅ Admin criado")

    finally:
        db.close()


if __name__ == "__main__":
    criar_admin()