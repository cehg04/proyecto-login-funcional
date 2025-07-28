from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from .routes import usuario_routes, auth_routes
from .utils.dependencies import verificar_sesion

app = FastAPI()

# Routers
app.include_router(usuario_routes.router)
app.include_router(auth_routes.router)

# CORS para permitir peticiones desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Puedes restringir esto a ["http://localhost:8000"] en producción
    allow_methods=["*"],
    allow_headers=["*"]
)

# Montaje de archivos estáticos
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Directorio de plantillas
templates = Jinja2Templates(directory="frontend/templates")

# RUTAS DE TEMPLATES PRINCIPALES

# Página de login (página principal)
@app.get("/", response_class=HTMLResponse)
def mostrar_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Panel de inicio (requiere sesión)
@app.get("/inicio.html", response_class=HTMLResponse)
def mostrar_inicio(request: Request, sesion: str = Depends(verificar_sesion)):
    return templates.TemplateResponse("inicio.html", {"request": request, "sesion": sesion})

# Cargar el menú lateral centralizado (menu.html)
@app.get("/menu", response_class=HTMLResponse)
def mostrar_menu(request: Request):
    return templates.TemplateResponse("menu.html", {"request": request})
# Fragmento de inicio (para cargar en el menú)
@app.get("/fragmento_inicio.html", response_class=HTMLResponse)
def fragmento_inicio(request: Request):
    return templates.TemplateResponse("fragmento_inicio.html", {"request": request})

# RUTAS PARA CARGAR FRAGMENTOS (vistas dinámicas)

@app.get("/register.html", response_class=HTMLResponse)
def mostrar_registro(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/crudusuarios.html", response_class=HTMLResponse)
def crud_usuarios(request: Request):
    return templates.TemplateResponse("crudusuarios.html", {"request": request})

@app.get("/contrasenias.html", response_class=HTMLResponse)
def mostrar_contrasenias(request: Request):
    return templates.TemplateResponse("contrasenias.html", {"request": request})

@app.get("/gestionentrega.html", response_class=HTMLResponse)
def mostrar_gestionentrega(request: Request):
    return templates.TemplateResponse("gestionentrega.html", {"request": request})

@app.get("/recepcionentrega.html", response_class=HTMLResponse)
def mostrar_recepcion_entrega(request: Request):
    return templates.TemplateResponse("recepcionentrega.html", {"request": request})

@app.get("/documentosvarios.html", response_class=HTMLResponse)
def mostrar_documentos_varios(request: Request):
    return templates.TemplateResponse("documentosvarios.html", {"request": request})

@app.get("/reportes.html", response_class=HTMLResponse)
def mostrar_reportes(request: Request):
    return templates.TemplateResponse("reportes.html", {"request": request})