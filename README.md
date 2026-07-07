# Sistema Web de Trazabilidad – Control de Mermas de Productos Perecibles
# Empresa: Makro, sede Chincha | Año: 2026
# Asignatura: Calidad y Pruebas de Software – UPSJB
# Autores: Contreras Quincho A. | Olivos Castro J. | Valeriano Cuadros N.

## 📁 Estructura del proyecto

```
makro_trazabilidad/
├── main.py                         ← Punto de entrada FastAPI
├── requirements.txt                ← Dependencias Python
├── makro_trazabilidad.db           ← Base de datos SQLite (se crea automáticamente)
├── backend/
│   ├── database/
│   │   └── database.py             ← Configuración SQLite + sesión BD
│   ├── models/
│   │   ├── models.py               ← Modelos SQLAlchemy (Lote, Alerta, Usuario)
│   │   └── motor_alertas.py        ← Lógica de negocio: clasificación de alertas
│   ├── schemas/
│   │   └── schemas.py              ← Validación Pydantic (request/response)
│   └── routers/
│       ├── auth.py                 ← Endpoints: registro y login JWT
│       ├── auth_utils.py           ← Utilidades: hash, tokens, dependencias
│       ├── lotes.py                ← Endpoints CRUD de lotes
│       └── alertas.py              ← Endpoints: alertas activas y dashboard
├── frontend/
│   ├── templates/
│   │   └── index.html              ← Interfaz principal del sistema
│   └── static/
│       ├── css/styles.css          ← Estilos del sistema
│       └── js/app.js               ← Lógica frontend (login, navegación, CRUD)
└── tests/
    └── test_motor_alertas.py       ← Pruebas unitarias con pytest (BVA + equiv.)
```

## 🚀 Instrucciones para ejecutar (VS Code)

### 1. Crear entorno virtual
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Ejecutar el servidor
```bash
uvicorn main:app --reload
```

### 4. Abrir en el navegador
```
http://localhost:8000
```
Credenciales demo: **admin@makro.com** / **admin123**

> ⚠ Primero debes crear el usuario administrador ejecutando:
> ```bash
> python seed.py
> ```

### 5. Ejecutar pruebas unitarias
```bash
pytest tests/ -v --cov=backend --cov-report=term-missing
```

### 6. Ver documentación de la API
```
http://localhost:8000/docs
```

## 📋 Módulos implementados (Avance)
- ✅ Autenticación con JWT (login/registro)
- ✅ Gestión de lotes (CRUD completo)
- ✅ Motor de alertas preventivas (clasificación por días)
- ✅ Dashboard con métricas en tiempo real
- ✅ Pruebas unitarias del motor de alertas (14 casos – BVA)
