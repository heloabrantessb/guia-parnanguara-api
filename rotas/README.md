# Roteiros

Todas as operações em `/v1/rotas/` exigem `Authorization: Bearer <token>`.
O proprietário é sempre o usuário autenticado.

## Criação manual

`POST /v1/rotas/` recebe:

```json
{"titulo": "Passeio pelo Centro", "atrativo_ids": [3, 1, 8]}
```

Os atrativos precisam existir e estar ativos. A lista aceita até 100 IDs
positivos, sem repetições. As paradas são salvas na ordem enviada, numeradas
a partir de 1. O título é aparado e deve ter entre 1 e 255 caracteres.

Retorna 201 com o roteiro e seus itens. Lista inválida ou título em branco
retorna 400; formato inválido retorna 422; ausência de autenticação retorna
401. A criação é transacional: falhas não deixam roteiro parcialmente salvo.
Omitir `atrativo_ids` continua criando um roteiro vazio para compatibilidade.

Executar os testes com `.venv/bin/python manage.py test rotas --noinput`.
O Django cria e remove um banco de testes separado do banco de desenvolvimento.
