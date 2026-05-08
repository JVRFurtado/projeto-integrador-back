from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db

from app.models import (
    Pessoa,
    Departamento,
    RamalTelefonico,
    RamalPessoa
)

from app.dependencies import get_current_user

from app.security import hash_senha

router = APIRouter(
    tags=["Frontend"]
)