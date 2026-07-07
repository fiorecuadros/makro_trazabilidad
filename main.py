from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import HTMLResponse

from backend.database.database import engine, Base
from backend.routers import auth, lotes, alertas
from backend.routers import reportes  # ← NUEVO

# Crear todas las tablas al iniciar si no existen
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MermaZero – Sistema de Control de Mermas Makro Chincha",
    description="Control de mermas de productos perecibles. UPSJB – Calidad y Pruebas de Software 2026.",
    version="1.0.0-avance"
)

# Archivos estáticos y templates HTML
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
templates = Jinja2Templates(directory="frontend/templates")

# Registrar routers
app.include_router(auth.router)
app.include_router(lotes.router)
app.include_router(alertas.router)
app.include_router(reportes.router)  # ← NUEVO


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    """Sirve la interfaz principal del sistema."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
def health_check():
    """Endpoint de verificación — usado por el pipeline CI/CD."""
    return {"status": "ok", "sistema": "MermaZero", "version": "1.0.0-avance"}
