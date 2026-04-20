import os
from main import SessionLocal, Pessoa, hash_senha

def main():
    db = SessionLocal()

    try:
        existe = db.query(Pessoa).filter(Pessoa.nome == "admin").first()

        if not existe:
            admin = Pessoa(
                nome="admin",
                senha_hash=hash_senha("123456"),
                aotipousuario="admin"
            )
            db.add(admin)
            db.commit()
            print("✅ Admin criado!")
        else:
            print("ℹ️ Admin já existe")

    finally:
        db.close()

    try:
        script_path = os.path.abspath(__file__)
        os.remove(script_path)
        print("🗑️ Script removido automaticamente")
    except Exception as e:
        print("Erro ao remover script:", e)

if __name__ == "__main__":
    main()