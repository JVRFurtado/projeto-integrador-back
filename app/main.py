from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine

from app.config import settings

from app.routers import (
    auth,
    frontend,
    cargos,
    departamentos,
    pessoas,
    ramais
)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API Agenda Corporativa"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# ROUTERS
# ==========================================

app.include_router(auth.router)

# compatibilidade frontend antigo
app.include_router(frontend.router)

# api moderna
app.include_router(cargos.router)
app.include_router(departamentos.router)
app.include_router(pessoas.router)
app.include_router(ramais.router)


@app.get("/")
def home():
    return {
        "status": "online"
    }