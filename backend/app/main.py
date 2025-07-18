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

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Static and templates
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
templates = Jinja2Templates(directory="frontend/templates")

# referencia hacia el login
@app.get("/", response_class=HTMLResponse)
def mostrar_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# referencia hacia el registro
@app.get("/fragmentos/register.html", response_class=HTMLResponse)
def mostrar_registro(request: Request):
    return templates.TemplateResponse("fragmentos/register.html", {"request": request})

# referencia hacia el menu principañ
@app.get("/menu.html", response_class=HTMLResponse)
def mostrar_menu(request: Request):
    return templates.TemplateResponse("menu.html", {"request": request})

# referencia hacia el crud de usuarios
@app.get("/fragmentos/crudusuarios.html", response_class=HTMLResponse)
def crud_usuarios(request: Request):
    return templates.TemplateResponse("fragmentos/crudusuarios.html", {"request": request})
