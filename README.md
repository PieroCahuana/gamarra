# Plataforma Gamarra — API de Formalización de Ambulantes

Sistema para el registro, licenciamiento y mapeo de puestos de vendedores ambulantes del emporio textil Gamarra, La Victoria - Lima, Perú.

## Stack tecnológico

| Componente | Tecnología |
|---|---|
| Backend | FastAPI 0.115 + Python 3.12 |
| Base de datos | MongoDB Atlas (Motor async) |
| Autenticación | JWT / Azure AD B2C |
| Contenedor | Docker |
| CI/CD | GitHub Actions |
| Nube | Azure Container Apps |
| Registry | Azure Container Registry (ACR) |

## Estructura del proyecto

```
gamarra-api/
├── app/
│   ├── main.py              # Punto de entrada FastAPI
│   ├── core/
│   │   ├── database.py      # Conexión MongoDB Atlas
│   │   └── security.py      # JWT y hashing
│   ├── routers/
│   │   ├── auth.py          # Registro y login
│   │   ├── ambulantes.py    # CRUD ambulantes
│   │   ├── licencias.py     # Flujo de aprobación
│   │   └── puestos.py       # Mapa GeoJSON
│   └── schemas/
│       └── schemas.py       # Modelos Pydantic
├── tests/
│   └── test_main.py         # Pruebas pytest
├── .github/
│   └── workflows/
│       └── ci-cd.yml        # Pipeline CI/CD
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── seed_data.py             # Datos de prueba
```

## Ejecutar en local

```bash
# 1. Clonar y entrar al proyecto
git clone https://github.com/<usuario>/gamarra-api.git
cd gamarra-api

# 2. Copiar variables de entorno
cp .env.example .env
# Editar .env con tu MONGODB_URI y SECRET_KEY

# 3. Levantar con Docker Compose
docker-compose up --build

# 4. Sembrar datos de prueba
python seed_data.py

# 5. Acceder a la documentación interactiva
open http://localhost:8000/docs
```

## Ejecutar pruebas

```bash
pip install -r requirements.txt
pytest tests/ -v --cov=app
```

## Estrategia de branching (Git Flow simplificado)

```
main          → Producción (protegida, solo merge via PR)
  └─ develop  → Integración continua
       ├─ feature/US-01-registro-ambulante
       ├─ feature/US-02-subir-documentos
       └─ feature/US-04-aprobacion-licencias
```

- Cada historia de usuario tiene su propia rama `feature/`
- Los commits siguen Conventional Commits: `feat:`, `fix:`, `test:`, `chore:`
- Los Pull Requests requieren: 1 aprobación + pipeline verde

## Variables de entorno requeridas

```env
MONGODB_URI=mongodb+srv://usuario:password@cluster.mongodb.net/
DB_NAME=gamarra_db
SECRET_KEY=tu-clave-secreta-segura-de-32-chars
```

## Endpoints principales

| Método | Ruta | Descripción |
|---|---|---|
| POST | /api/v1/auth/register | Registrar usuario |
| POST | /api/v1/auth/login | Obtener JWT |
| POST | /api/v1/ambulantes/ | Crear perfil ambulante |
| GET | /api/v1/ambulantes/ | Listar ambulantes |
| POST | /api/v1/licencias/ | Solicitar licencia |
| PATCH | /api/v1/licencias/{id}/estado | Aprobar/rechazar |
| GET | /api/v1/puestos/mapa | GeoJSON para mapa |
| GET | /health | Health check |

## Despliegue en Azure

El pipeline CI/CD en `.github/workflows/ci-cd.yml` realiza automáticamente:
1. Ejecuta pruebas (`pytest`)
2. Construye imagen Docker
3. Sube imagen a Azure Container Registry
4. Despliega en Azure Container Apps
5. Verifica el health check del endpoint
