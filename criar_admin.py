from main import SessionLocal, Pessoa, Cargo, Departamento, hash_senha

def main():
    db = SessionLocal()

    try:
        # ---------------- GARANTIR CARGO ----------------
        cargo = db.query(Cargo).first()
        if not cargo:
            cargo = Cargo(txnome="Admin")
            db.add(cargo)
            db.commit()
            db.refresh(cargo)
            print("✔ Cargo criado")

        # ---------------- GARANTIR DEPARTAMENTO ----------------
        depto = db.query(Departamento).first()
        if not depto:
            depto = Departamento(txnomedepto="TI")
            db.add(depto)
            db.commit()
            db.refresh(depto)
            print("✔ Departamento criado")

        # ---------------- VERIFICAR ADMIN ----------------
        existe = db.query(Pessoa).filter(Pessoa.txnome == "admin").first()

        if not existe:
            admin = Pessoa(
                txnome="admin",
                txemail="admin@admin.com",
                txsenha=hash_senha("123456"),
                cargoid=cargo.idcargo,
                deptoid=depto.iddepto,
                aotipousuario="admin"
            )

            db.add(admin)
            db.commit()

            print("✅ Admin criado com sucesso!")
        else:
            print("ℹ️ Admin já existe")

    finally:
        db.close()

if __name__ == "__main__":
    main()