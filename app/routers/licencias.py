from fastapi import APIRouter, HTTPException, Depends, status
from datetime import datetime, timezone
from bson import ObjectId
from app.core.database import get_db
from app.schemas.schemas import LicenciaCreate, LicenciaUpdate, LicenciaResponse, EstadoLicencia
from app.core.security import get_current_user

router = APIRouter()


def serialize(doc: dict) -> dict:
    doc["id"] = str(doc.pop("_id"))
    return doc


@router.post("/", response_model=LicenciaResponse, status_code=status.HTTP_201_CREATED)
async def crear_licencia(data: LicenciaCreate, current_user: dict = Depends(get_current_user)):
    db = get_db()
    nueva = {
        **data.model_dump(),
        "estado": EstadoLicencia.pendiente,
        "revisor_id": None,
        "puesto_id": None,
        "creado_en": datetime.now(timezone.utc),
    }
    resultado = await db.licencias.insert_one(nueva)
    creada = await db.licencias.find_one({"_id": resultado.inserted_id})
    return serialize(creada)


@router.get("/", response_model=list[LicenciaResponse])
async def listar_licencias(
    estado: str | None = None,
    skip: int = 0,
    limit: int = 20,
    current_user: dict = Depends(get_current_user),
):
    db = get_db()
    filtro = {}
    if estado:
        filtro["estado"] = estado
    cursor = db.licencias.find(filtro).skip(skip).limit(limit)
    licencias = []
    async for doc in cursor:
        licencias.append(serialize(doc))
    return licencias


@router.patch("/{licencia_id}/estado", response_model=LicenciaResponse)
async def actualizar_estado(
    licencia_id: str,
    data: LicenciaUpdate,
    current_user: dict = Depends(get_current_user),
):
    """
    Permite a un funcionario o admin aprobar o rechazar una licencia.
    """
    if current_user.get("rol") not in ("funcionario", "admin"):
        raise HTTPException(status_code=403, detail="No autorizado para esta acción")
    db = get_db()
    try:
        oid = ObjectId(licencia_id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido")

    update = {
        "estado": data.estado,
        "revisor_id": current_user["id"],
        "revisado_en": datetime.now(timezone.utc),
    }
    if data.observacion:
        update["observacion"] = data.observacion

    resultado = await db.licencias.update_one({"_id": oid}, {"$set": update})
    if resultado.matched_count == 0:
        raise HTTPException(status_code=404, detail="Licencia no encontrada")

    doc = await db.licencias.find_one({"_id": oid})
    return serialize(doc)
