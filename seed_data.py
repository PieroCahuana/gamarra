"""
Script para poblar MongoDB con datos de prueba.
Ejecutar: python seed_data.py
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone, date, timedelta
import bcrypt

import os
from dotenv import load_dotenv

# Cargar variables del entorno
load_dotenv()

MONGO_URI = os.getenv("MONGODB_URI")
DB_NAME = "gamarra_db"


async def seed():
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]

    await db.usuarios.drop()
    await db.ambulantes.drop()
    await db.licencias.drop()
    await db.puestos.drop()

    print("🌱 Sembrando datos de prueba...")

    # Usuarios
    def hash_pw(pw): return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()

    usuarios = [
        {"email": "juan.perez@gamarra.pe",     "password_hash": hash_pw("pass1234"), "rol": "ambulante",   "creado_en": datetime.now(timezone.utc)},
        {"email": "maria.flores@gamarra.pe",    "password_hash": hash_pw("pass1234"), "rol": "ambulante",   "creado_en": datetime.now(timezone.utc)},
        {"email": "funcionario@muni.gob.pe",    "password_hash": hash_pw("func1234"), "rol": "funcionario", "creado_en": datetime.now(timezone.utc)},
        {"email": "admin@plataforma.pe",        "password_hash": hash_pw("adm1234!"), "rol": "admin",       "creado_en": datetime.now(timezone.utc)},
    ]
    result = await db.usuarios.insert_many(usuarios)
    uid_juan, uid_maria = str(result.inserted_ids[0]), str(result.inserted_ids[1])
    print(f"  ✅ {len(usuarios)} usuarios insertados")

    # Puestos (con coordenadas reales de Gamarra, La Victoria)
    puestos = [
        {"codigo": "GAL-A-001", "galeria": "Gamarra Gold", "ubicacion_geo": {"type": "Point", "coordinates": [-77.0165, -12.0664]}, "estado": "disponible", "area_m2": 6.5},
        {"codigo": "GAL-A-002", "galeria": "Gamarra Gold", "ubicacion_geo": {"type": "Point", "coordinates": [-77.0168, -12.0662]}, "estado": "disponible", "area_m2": 5.0},
        {"codigo": "GAL-B-001", "galeria": "Galería El Rey", "ubicacion_geo": {"type": "Point", "coordinates": [-77.0172, -12.0670]}, "estado": "ocupado",    "area_m2": 8.0},
        {"codigo": "GAL-B-002", "galeria": "Galería El Rey", "ubicacion_geo": {"type": "Point", "coordinates": [-77.0175, -12.0668]}, "estado": "disponible", "area_m2": 4.5},
    ]
    result_p = await db.puestos.insert_many(puestos)
    pid_001 = str(result_p.inserted_ids[0])
    print(f"  ✅ {len(puestos)} puestos insertados")

    # Ambulantes
    ambulantes = [
        {"usuario_id": uid_juan,  "nombre_completo": "Juan Carlos Pérez López",  "dni": "12345678", "telefono": "987654321", "direccion": "Jr. Gamarra 123, La Victoria", "estado": "activo",   "creado_en": datetime.now(timezone.utc)},
        {"usuario_id": uid_maria, "nombre_completo": "María Elena Flores Quispe", "dni": "87654321", "telefono": "912345678", "direccion": "Av. Aviación 456, La Victoria", "estado": "activo",   "creado_en": datetime.now(timezone.utc)},
    ]
    result_a = await db.ambulantes.insert_many(ambulantes)
    aid_juan = str(result_a.inserted_ids[0])
    print(f"  ✅ {len(ambulantes)} ambulantes insertados")

    # Licencias
    hoy = datetime.now(timezone.utc)
    licencias = [
        {
            "ambulante_id": aid_juan,
            "tipo": "temporal",
            "estado": "aprobada",
            "fecha_inicio": hoy.strftime("%Y-%m-%d"),
            "fecha_vencimiento": (hoy + timedelta(days=90)).strftime("%Y-%m-%d"),
            "documentos_urls": ["https://storage.azure.com/docs/dni_juan.pdf"],
            "puesto_id": pid_001,
            "revisor_id": str(result.inserted_ids[2]),
            "creado_en": hoy,
        },
        {
            "ambulante_id": str(result_a.inserted_ids[1]),
            "tipo": "temporal",
            "estado": "pendiente",
            "fecha_inicio": hoy.strftime("%Y-%m-%d"),
            "fecha_vencimiento": (hoy + timedelta(days=90)).strftime("%Y-%m-%d"),
            "documentos_urls": [],
            "puesto_id": None,
            "revisor_id": None,
            "creado_en": hoy,
        },
    ]
    await db.licencias.insert_many(licencias)
    print(f"  ✅ {len(licencias)} licencias insertadas")

    # Índice geoespacial para puestos
    await db.puestos.create_index([("ubicacion_geo", "2dsphere")])
    print("  ✅ Índice 2dsphere creado en puestos.ubicacion_geo")

    print("\n🎉 Seed completado. Base de datos lista para pruebas.")
    client.close()


if __name__ == "__main__":
    asyncio.run(seed())
