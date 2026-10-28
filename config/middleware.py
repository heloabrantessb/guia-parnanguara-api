from django.conf import settings
from django.http import HttpResponse
from django.utils.cache import patch_vary_headers


class CorsPreviaLocalMiddleware:
    """Permite a prévia web local sem liberar outras origens ou a produção."""

    origensPermitidas = {
        "http://localhost:8081", "http://127.0.0.1:8081",
        "http://localhost:8082", "http://127.0.0.1:8082",
    }

    def __init__(self, obterResposta):
        self.obterResposta = obterResposta

    def __call__(self, requisicao):
        origem = requisicao.headers.get("Origin")
        permitePrevia = (
            settings.DEBUG
            and requisicao.path.startswith("/v1/")
            and origem in self.origensPermitidas
        )
        if permitePrevia and requisicao.method == "OPTIONS":
            resposta = HttpResponse(status=204)
        else:
            resposta = self.obterResposta(requisicao)

        if permitePrevia:
            resposta["Access-Control-Allow-Origin"] = origem
            patch_vary_headers(resposta, ["Origin"])
            if requisicao.method == "OPTIONS":
                resposta["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
                resposta["Access-Control-Allow-Headers"] = "Authorization, Content-Type"

        return resposta
