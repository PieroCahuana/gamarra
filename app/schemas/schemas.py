from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import date, datetime
from enum import Enum


class RolUsuario(str, Enum):
    ambulante = "ambulante"
    funcionario = "funcionario"
    admin = "admin"


class EstadoLicencia(str, Enum):
    pendiente = "pendiente"
    en_revision = "en_revision"
    aprobada = "aprobada"
    rechazada = "rechazada"


# ── Ambulante ──────────────────────────────────────────────
class AmbulanteCreate(BaseModel):
    nombre_completo: str = Field(..., min_length=3, max_length=100)
    dni: str = Field(..., min_length=8, max_length=8, pattern=r"^\d{8}$")
    telefono: str = Field(..., min_length=9, max_length=9)
    direccion: str = Field(..., max_length=200)


class AmbulanteResponse(AmbulanteCreate):
    id: str
    usuario_id: str
    estado: str = "activo"
    creado_en: datetime

    class Config:
        from_attributes = True


# ── Licencia ───────────────────────────────────────────────
class LicenciaCreate(BaseModel):
    ambulante_id: str
    tipo: str = Field(..., description="temporal | anual")
    fecha_inicio: date
    fecha_vencimiento: date
    documentos_urls: List[str] = []


class LicenciaUpdate(BaseModel):
    estado: EstadoLicencia
    observacion: Optional[str] = None


class LicenciaResponse(LicenciaCreate):
    id: str
    estado: EstadoLicencia = EstadoLicencia.pendiente
    revisor_id: Optional[str] = None
    puesto_id: Optional[str] = None
    creado_en: datetime

    class Config:
        from_attributes = True


# ── Puesto ─────────────────────────────────────────────────
class UbicacionGeo(BaseModel):
    type: str = "Point"
    coordinates: List[float] = Field(..., description="[longitud, latitud]")


class PuestoCreate(BaseModel):
    codigo: str = Field(..., description="Ej: GAL-A-001")
    galeria: str
    ubicacion_geo: UbicacionGeo
    area_m2: float = Field(..., gt=0)


class PuestoResponse(PuestoCreate):
    id: str
    estado: str = "disponible"


# ── Auth ───────────────────────────────────────────────────
class UsuarioCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    rol: RolUsuario = RolUsuario.ambulante


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    rol: str
