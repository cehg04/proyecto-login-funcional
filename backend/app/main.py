from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from .routes import contrasenia_routes
from .routes import usuario_routes, auth_routes
from .routes import documentos_routes
from .routes import entregas_routes
from .utils.dependencies import verificar_sesion

app = FastAPI()

# Routers
app.include_router(usuario_routes.router)
app.include_router(auth_routes.router)
app.include_router(contrasenia_routes.router)
app.include_router(documentos_routes.router)
app.include_router(entregas_routes.router)


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
@app.get("/editar.html", response_class=HTMLResponse)
def muestra_editor(request: Request):
    return templates.TemplateResponse("editar.html", {"request": request})

# RUTAS PARA CARGAR FRAGMENTOS (vistas dinámicas)

@app.get("/register.html", response_class=HTMLResponse)
def mostrar_registro(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/crudusuarios.html", response_class=HTMLResponse)
def crud_usuarios(request: Request):
    return templates.TemplateResponse("crudusuarios.html", {"request": request})

@app.get("/vercontrasenias.html", response_class=HTMLResponse)
def mostrar_contrasenias(request: Request):
    return templates.TemplateResponse("vercontrasenias.html", {"request": request})

@app.get("/contrasenia_completa.html", response_class=HTMLResponse)
def ver_contrasenia(request: Request):
    return templates.TemplateResponse("contrasenia_completa.html", {"request": request})

@app.get("/verentregacompleta.html", response_class=HTMLResponse)
def ver_contrasenia(request: Request):
    return templates.TemplateResponse("verentregacompleta.html", {"request": request})

@app.get("/crearcontrasenia.html", response_class=HTMLResponse)
def crear_contrasenias(request: Request):
    return templates.TemplateResponse("crearcontrasenia.html", {"request": request})

@app.get("/verentregas.html", response_class=HTMLResponse)
def mostrar_gestionentrega(request: Request):
    return templates.TemplateResponse("verentregas.html", {"request": request})

@app.get("/crearentrega.html", response_class=HTMLResponse)
def mostrar_gestionentrega(request: Request):
    return templates.TemplateResponse("crearentrega.html", {"request": request})

@app.get("/crearentregadc.html", response_class=HTMLResponse)
def mostrar_gestionentrega(request: Request):
    return templates.TemplateResponse("crearentregadc.html", {"request": request})

@app.get("/recepcionentrega.html", response_class=HTMLResponse)
def mostrar_recepcion_entrega(request: Request):
    return templates.TemplateResponse("recepcionentrega.html", {"request": request})

@app.get("/verdocumentos.html", response_class=HTMLResponse)
def mostrar_documentos_varios(request: Request):
    return templates.TemplateResponse("verdocumentos.html", {"request": request})

@app.get("/creardocumentos.html", response_class=HTMLResponse)
def mostrar_documentos_varios(request: Request):
    return templates.TemplateResponse("creardocumentos.html", {"request": request})

@app.get("/reportes.html", response_class=HTMLResponse)
def mostrar_reportes(request: Request):
    return templates.TemplateResponse("reportes.html", {"request": request})