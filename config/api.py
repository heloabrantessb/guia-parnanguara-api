from ninja import NinjaAPI
from usuarios.router import router as usuarios_router

api = NinjaAPI(
    title="PGuaTur API",
    version="1.0.0",
    description="API do Guia Turístico de Paranaguá-PR",
    docs_url="/docs",
)

api.add_router("/usuarios", usuarios_router)
