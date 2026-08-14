from ninja import NinjaAPI
from usuarios.router import router as usuarios_router
from atrativos.routers.categorias import router as categorias_router
from atrativos.routers.locais import router as locais_router
from atrativos.routers.eventos import router as eventos_router
from atrativos.routers.imagens import router as imagens_router
from rotas.router import router as rotas_router
from usuarios.router_preferencias import router as preferencias_router

api = NinjaAPI(
    title="PGuaTur API",
    version="1.0.0",
    description="API do Guia Turístico de Paranaguá-PR",
    docs_url="/docs",
)

api.add_router("/usuarios", usuarios_router)
api.add_router("/categorias", categorias_router)
api.add_router("/locais", locais_router)
api.add_router("/eventos", eventos_router)
api.add_router("/atrativos", imagens_router)
api.add_router("/rotas", rotas_router)
api.add_router("/preferencias", preferencias_router)



