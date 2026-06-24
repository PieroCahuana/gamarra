from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.database import connect_db, close_db
from app.routers import ambulantes, licencias, puestos, auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    yield
    await close_db()


app = FastAPI(
    title="Plataforma Gamarra - API",
    description="Sistema de formalización de ambulantes del emporio Gamarra",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,        prefix="/api/v1/auth",       tags=["Autenticación"])
app.include_router(ambulantes.router,  prefix="/api/v1/ambulantes",  tags=["Ambulantes"])
app.include_router(licencias.router,   prefix="/api/v1/licencias",   tags=["Licencias"])
app.include_router(puestos.router,     prefix="/api/v1/puestos",     tags=["Puestos"])


@app.get("/health")
async def health_check():
    return {"status": "ok", "servicio": "Plataforma Gamarra"}
