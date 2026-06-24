from fastapi import APIRouter, HTTPException, status
from datetime import datetime, timezone
from app.core.database import get_db
from app.schemas.schemas import UsuarioCreate, LoginRequest, TokenResponse
from app.core.security import hash_password, verify_password, create_access_token

router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def registrar_usuario(data: UsuarioCreate):
    db = get_db()
    existente = await db.usuarios.find_one({"email": data.email})
    if existente:
        raise HTTPException(status_code=400, detail="El email ya está registrado")

    nuevo = {
        "email": data.email,
        "password_hash": hash_password(data.password),
        "rol": data.rol,
        "creado_en": datetime.now(timezone.utc),
    }
    resultado = await db.usuarios.insert_one(nuevo)
    return {"id": str(resultado.inserted_id), "email": data.email, "rol": data.rol}


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest):
    db = get_db()
    usuario = await db.usuarios.find_one({"email": data.email})
    if not usuario or not verify_password(data.password, usuario["password_hash"]):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    token = create_access_token({
        "sub": str(usuario["_id"]),
        "rol": usuario["rol"],
        "email": usuario["email"],
    })
    return {"access_token": token, "token_type": "bearer", "rol": usuario["rol"]}
