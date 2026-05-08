from sqlalchemy.orm import Session

from database import SessionLocal
from models import Pessoa
from security import hash_senha


def criar_admin():
    db: Session = SessionLocal()

    try:
        admin = (
            db.query(Pessoa)
            .filter(Pessoa.idpessoa == 1)
            .first()
        )

        if admin:
            print("ℹ️ Admin já existe")
            return

        novo_admin = Pessoa(
            txnome="Administrador",
            txemail="admin@admin.com",
            txsenha=hash_senha("123456"),
            cargoid=1,
            deptoid=1,
            aotipousuario="admin"
        )

        db.add(novo_admin)
        db.commit()

        print("✅ Admin criado com sucesso")

    except Exception as e:
        print(f"❌ Erro ao criar admin: {e}")

    finally:
        db.close()


if __name__ == "__main__":
    criar_admin()