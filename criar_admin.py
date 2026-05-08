from database import SessionLocal, engine, Base
from models import Cargo, Departamento, Pessoa
from security import hash_senha

Base.metadata.create_all(bind=engine)


def criar_admin():
    db = SessionLocal()

    try:
        cargo = db.query(Cargo).filter(
            Cargo.txnome == "Administrador"
        ).first()

        if not cargo:
            cargo = Cargo(
                txnome="Administrador"
            )

            db.add(cargo)
            db.commit()
            db.refresh(cargo)

            print("✅ Cargo criado")

        depto = db.query(Departamento).filter(
            Departamento.txnomedepto == "TI"
        ).first()

        if not depto:
            depto = Departamento(
                txnomedepto="TI"
            )

            db.add(depto)
            db.commit()
            db.refresh(depto)

            print("✅ Departamento criado")

        admin = db.query(Pessoa).filter(
            Pessoa.txemail == "admin@admin.com"
        ).first()

        if not admin:
            novo_admin = Pessoa(
                txnome="Administrador",
                txemail="admin@admin.com",
                txsenha=hash_senha("123456"),
                cargoid=cargo.idcargo,
                deptoid=depto.iddepto,
                aotipousuario="admin"
            )

            db.add(novo_admin)
            db.commit()

            print("✅ Admin criado")
            print("📧 Login: admin@admin.com")
            print("🔑 Senha: 123456")

        else:
            print("ℹ️ Admin já existe")

    except Exception as e:
        db.rollback()
        print("❌ Erro:", str(e))

    finally:
        db.close()


if __name__ == "__main__":
    criar_admin()