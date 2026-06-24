from fastapi import APIRouter, HTTPException, Depends, status
from bson import ObjectId
from app.core.database import get_db
from app.schemas.schemas import PuestoCreate, PuestoResponse
from app.core.security import get_current_user

router = APIRouter()


def serialize(doc: dict) -> dict:
    doc["id"] = str(doc.pop("_id"))
    return doc


@router.post("/", response_model=PuestoResponse, status_code=status.HTTP_201_CREATED)
async def crear_puesto(data: PuestoCreate, current_user: dict = Depends(get_current_user)):
    if current_user.get("rol") not in ("funcionario", "admin"):
        raise HTTPException(status_code=403, detail="No autorizado")
    db = get_db()
    existente = await db.puestos.find_one({"codigo": data.codigo})
    if existente:
        raise HTTPException(status_code=400, detail="Código de puesto ya existe")
    nuevo = {**data.model_dump(), "estado": "disponible"}
    resultado = await db.puestos.insert_one(nuevo)
    creado = await db.puestos.find_one({"_id": resultado.inserted_id})
    return serialize(creado)


@router.get("/", response_model=list[PuestoResponse])
async def listar_puestos(galeria: str | None = None, estado: str | None = None):
    db = get_db()
    filtro = {}
    if galeria:
        filtro["galeria"] = galeria
    if estado:
        filtro["estado"] = estado
    cursor = db.puestos.find(filtro)
    puestos = []
    async for doc in cursor:
        puestos.append(serialize(doc))
    return puestos


@router.get("/mapa")
async def puestos_geojson():
    """Retorna todos los puestos en formato GeoJSON para visualizar en mapa."""
    db = get_db()
    cursor = db.puestos.find()
    features = []
    async for doc in cursor:
        features.append({
            "type": "Feature",
            "geometry": doc["ubicacion_geo"],
            "properties": {
                "id": str(doc["_id"]),
                "codigo": doc["codigo"],
                "galeria": doc["galeria"],
                "estado": doc["estado"],
                "area_m2": doc["area_m2"],
            },
        })
    return {"type": "FeatureCollection", "features": features}
