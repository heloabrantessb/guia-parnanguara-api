# Guia Parnanguara API

O Guia Parnanguara API é o backend de um sistema de guia turístico para a cidade de Paranaguá. Ele fornece a infraestrutura necessária para gerenciar atrativos turísticos, eventos, perfis de usuários e rotas personalizadas.

O projeto foi construído utilizando Python, Django e Django Ninja, garantindo uma arquitetura modular, tipada e com documentação automatizada (OpenAPI/Swagger).

## Arquitetura e Módulos

O sistema é dividido em aplicações independentes (apps) para garantir baixo acoplamento:

- Usuarios: Gerenciamento de perfis, registro e autenticação segura via JWT.
- Categorias: Cadastro de categorias (ex: Museus, Parques, Praias).
- Atrativos: Core do catálogo, utilizando herança de banco de dados para diferenciar Locais (físicos) de Eventos (temporais).
- Midia: Gerenciamento de uploads de imagens dos atrativos.
- Rotas: Sistema para que turistas criem seus próprios roteiros, ordenando atrativos em uma sequência lógica.
- Preferencias: Mapeamento dos interesses dos usuários cruzados com as categorias disponíveis.

## Tecnologias Utilizadas

- Python
- Django
- Django Ninja (Roteamento e Schemas)
- PostgreSQL (Banco de Dados)
- Docker (Para orquestração do banco de dados local)
- uv (Gerenciamento de pacotes e ambientes virtuais)

## Como executar o projeto localmente

1. Certifique-se de ter o Docker e a ferramenta `uv` instalados.
2. Inicie o banco de dados PostgreSQL:
   ```bash
   docker-compose up -d
   ```
3. Instale as dependências e ative o ambiente:
   ```bash
   uv sync
   ```
4. Execute as migrações do banco de dados:
   ```bash
   uv run manage.py migrate
   ```
5. Inicie o servidor de desenvolvimento:
   ```bash
   uv run manage.py runserver
   ```

A documentação interativa da API estará disponível em: `http://localhost:8000/api/docs`.

## Visão Geral da API (Endpoints Principais)

A API foi projetada de forma RESTful, organizada pelo prefixo `/api/v1/`. Alguns dos principais endpoints incluem:

- **Autenticação e Usuários:**
  - `POST /api/v1/usuarios/registro` - Criação de conta.
  - `POST /api/v1/usuarios/login` - Obtenção de Token JWT.
  - `GET /api/v1/usuarios/perfil` - Recuperação dos dados do usuário autenticado.

- **Catálogo de Turismo:**
  - `GET /api/v1/categorias` - Listagem de categorias.
  - `GET /api/v1/atrativos/locais` - Busca de locais turísticos físicos.
  - `GET /api/v1/atrativos/eventos` - Busca de eventos com data de início e fim.
  - `POST /api/v1/atrativos/{id}/imagens` - Upload de fotos para o catálogo.

- **Experiência do Turista:**
  - `GET /api/v1/rotas` - Visualização do roteiro salvo.
  - `POST /api/v1/rotas` - Criação e gestão do roteiro personalizado.
  - `POST /api/v1/preferencias` - Registro dos interesses (categorias favoritas) do turista.

## Estrutura de Pastas do Projeto

O projeto segue a estrutura padrão do Django, dividida em módulos focados em domínios específicos de negócio:

```text
guia-parnanguara-api/
├── config/             # Configurações globais (settings.py, urls.py, api.py)
├── usuarios/           # App de gestão de perfis e autenticação
├── categorias/         # App de taxonomia e classificação
├── atrativos/          # App central (Locais, Eventos e Mídia)
├── rotas/              # App de roteirização turística e ordenação
├── docs/               # Documentação técnica do projeto (análises e decisões)
├── manage.py           # Entrypoint do Django para comandos CLI
├── docker-compose.yml  # Definição dos containers de banco de dados
└── pyproject.toml / uv.lock # Dependências e configuração do projeto em Python
```

## Testes Automatizados

O projeto possui uma suíte de testes que verifica a integridade das rotas, autenticação, modelos e relacionamentos. Para rodar todos os testes automatizados, certifique-se de que o banco de dados (Docker) esteja ativo e execute:

```bash
uv run manage.py test
```
