from fastapi import APIRouter, HTTPException, Depends, status
from datetime import datetime, timezone
from bson import ObjectId
from app.core.database import get_db
from app.schemas.schemas import AmbulanteCreate, AmbulanteResponse
from app.core.security import get_current_user

router = APIRouter()


def serialize_ambulante(doc: dict) -> dict:
    doc["id"] = str(doc.pop("_id"))
    return doc


@router.post("/", response_model=AmbulanteResponse, status_code=status.HTTP_201_CREATED)
async def crear_ambulante(data: AmbulanteCreate, current_user: dict = Depends(get_current_user)):
    db = get_db()
    # Verificar DNI único
    existente = await db.ambulantes.find_one({"dni": data.dni})
    if existente:
        raise HTTPException(status_code=400, detail="Ya existe un ambulante con ese DNI")

    nuevo = {
        **data.model_dump(),
        "usuario_id": current_user["id"],
        "estado": "activo",
        "creado_en": datetime.now(timezone.utc),
    }
    resultado = await db.ambulantes.insert_one(nuevo)
    creado = await db.ambulantes.find_one({"_id": resultado.inserted_id})
    return serialize_ambulante(creado)


@router.get("/", response_model=list[AmbulanteResponse])
async def listar_ambulantes(skip: int = 0, limit: int = 20, current_user: dict = Depends(get_current_user)):
    db = get_db()
    cursor = db.ambulantes.find().skip(skip).limit(limit)
    ambulantes = []
    async for doc in cursor:
        ambulantes.append(serialize_ambulante(doc))
    return ambulantes


@router.get("/{ambulante_id}", response_model=AmbulanteResponse)
async def obtener_ambulante(ambulante_id: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    try:
        doc = await db.ambulantes.find_one({"_id": ObjectId(ambulante_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido")
    if not doc:
        raise HTTPException(status_code=404, detail="Ambulante no encontrado")
    return serialize_ambulante(doc)


@router.put("/{ambulante_id}", response_model=AmbulanteResponse)
async def actualizar_ambulante(
    ambulante_id: str,
    data: AmbulanteCreate,
    current_user: dict = Depends(get_current_user),
):
    db = get_db()
    try:
        oid = ObjectId(ambulante_id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido")

    await db.ambulantes.update_one({"_id": oid}, {"$set": data.model_dump()})
    doc = await db.ambulantes.find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Ambulante no encontrado")
    return serialize_ambulante(doc)
