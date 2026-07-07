from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite — no requiere instalación, ideal para desarrollo y avance del proyecto
DATABASE_URL = "sqlite:///./makro_trazabilidad.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Necesario solo para SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependencia que provee la sesión de BD a cada endpoint."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
