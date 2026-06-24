import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch, MagicMock
from app.main import app


@pytest.fixture
def mock_db():
    db = MagicMock()
    db.usuarios.find_one = AsyncMock(return_value=None)
    db.usuarios.insert_one = AsyncMock(return_value=MagicMock(inserted_id="fake_id"))
    db.ambulantes.find_one = AsyncMock(return_value=None)
    db.ambulantes.insert_one = AsyncMock(return_value=MagicMock(inserted_id="fake_id"))
    return db


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


@pytest.mark.asyncio
async def test_health_check(client):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "Gamarra" in data["servicio"]


@pytest.mark.asyncio
async def test_register_usuario(client, mock_db):
    with patch("app.routers.auth.get_db", return_value=mock_db):
        response = await client.post("/api/v1/auth/register", json={
            "email": "test@gamarra.pe",
            "password": "password123",
            "rol": "ambulante",
        })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@gamarra.pe"
    assert data["rol"] == "ambulante"


@pytest.mark.asyncio
async def test_login_credenciales_incorrectas(client, mock_db):
    mock_db.usuarios.find_one = AsyncMock(return_value=None)
    with patch("app.routers.auth.get_db", return_value=mock_db):
        response = await client.post("/api/v1/auth/login", json={
            "email": "noexiste@gamarra.pe",
            "password": "wrong",
        })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_crear_ambulante_sin_token(client):
    response = await client.post("/api/v1/ambulantes/", json={
        "nombre_completo": "Juan Pérez",
        "dni": "12345678",
        "telefono": "987654321",
        "direccion": "Av. Aviación 1234, La Victoria",
    })
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_puestos_geojson_publico(client, mock_db):
    mock_db.puestos.find = MagicMock(return_value=AsyncMock(__aiter__=AsyncMock(return_value=iter([]))))
    with patch("app.routers.puestos.get_db", return_value=mock_db):
        response = await client.get("/api/v1/puestos/mapa")
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "FeatureCollection"
