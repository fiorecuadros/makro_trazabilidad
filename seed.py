"""
seed.py – Crea el usuario administrador y datos de prueba iniciales.
Ejecutar una sola vez: python seed.py
"""
from datetime import date, timedelta
from backend.database.database import engine, SessionLocal, Base
from backend.models.models import Usuario, Lote, EstadoLote, RolUsuario
from backend.routers.auth_utils import hashear_password

Base.metadata.create_all(bind=engine)

db = SessionLocal()

# ── Usuario admin ──────────────────────────────────────────────────────────
if not db.query(Usuario).filter(Usuario.email == "admin@makro.com").first():
    db.add(Usuario(
        nombre="Administrador Makro",
        email="admin@makro.com",
        hashed_password=hashear_password("admin123"),
        rol=RolUsuario.ADMINISTRADOR
    ))
    db.add(Usuario(
        nombre="Operador Almacén",
        email="operador@makro.com",
        hashed_password=hashear_password("op123"),
        rol=RolUsuario.OPERADOR
    ))
    print("✅ Usuarios creados.")

# ── Lotes de muestra ───────────────────────────────────────────────────────
hoy = date.today()
lotes_demo = [
    ("LOT-001", "Pollo Fresco Bandeja 1kg",    "Carnes y Aves",      120.0, "kg",       "San Fernando S.A.",       hoy - timedelta(3),  hoy + timedelta(2),  "Cámara A – Estante 1", 8.50),
    ("LOT-002", "Leche Entera Gloria 1L",       "Lácteos",            200.0, "unidades", "Gloria S.A.",             hoy - timedelta(5),  hoy + timedelta(5),  "Pasillo B – Estante 2", 3.20),
    ("LOT-003", "Yogur Natural Laive 500g",     "Lácteos",             80.0, "unidades", "Laive S.A.",              hoy - timedelta(2),  hoy + timedelta(1),  "Cámara A – Estante 2", 4.50),
    ("LOT-004", "Lechuga Hidropónica",          "Frutas y Verduras",   50.0, "kg",       "Agro Ica S.A.C.",         hoy - timedelta(1),  hoy + timedelta(6),  "Pasillo C – Estante 1", 2.80),
    ("LOT-005", "Jamón Ahumado Otto Kunz 200g", "Embutidos",           60.0, "unidades", "Otto Kunz S.A.",          hoy - timedelta(4),  hoy + timedelta(15), "Cámara B – Estante 3", 9.90),
    ("LOT-006", "Filete de Merluza 500g",       "Pescados y Mariscos", 40.0, "kg",       "Pesquera Diamante S.A.",  hoy - timedelta(1),  hoy + timedelta(3),  "Cámara A – Estante 3", 12.00),
    ("LOT-007", "Pan de Molde Bimbo",           "Panadería",          100.0, "unidades", "Bimbo del Perú S.A.",     hoy - timedelta(2),  hoy + timedelta(4),  "Pasillo D – Estante 1", 5.50),
    ("LOT-008", "Queso Fresco La Preferida",    "Lácteos",             35.0, "kg",       "Nestlé Perú S.A.",        hoy - timedelta(6),  hoy + timedelta(20), "Cámara B – Estante 1", 18.00),
]

for cod, prod, cat, cant, uni, prov, ingreso, venc, ubic, costo in lotes_demo:
    if not db.query(Lote).filter(Lote.codigo == cod).first():
        db.add(Lote(
            codigo=cod, producto=prod, categoria=cat, cantidad=cant,
            unidad=uni, proveedor=prov, fecha_ingreso=ingreso,
            fecha_vencimiento=venc, ubicacion=ubic,
            estado=EstadoLote.EN_STOCK, costo_unitario=costo
        ))

db.commit()
db.close()
print("✅ Datos de prueba insertados. Ejecuta: uvicorn main:app --reload")
