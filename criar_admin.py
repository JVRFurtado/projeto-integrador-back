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

if __name__ == "__main__":
    main()