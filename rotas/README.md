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

## Geração por preferências e tempo

`POST /v1/rotas/gerar` recebe:

```json
{
  "titulo": "Uma tarde de cultura",
  "tempo_disponivel_minutos": 120,
  "categoria_ids": [1, 3],
  "inicio_em": "2026-10-20T14:00:00-03:00"
}
```

O tempo precisa ser inteiro entre 1 e 1440 minutos. `categoria_ids` aceita
de 1 a 100 IDs positivos de categorias ativas, sem repetições; se omitido,
usa as preferências ativas salvas do usuário. Categorias explícitas valem
somente para essa solicitação. Para salvar preferências, usar o endpoint
existente `POST /v1/preferencias/` com `categoria_ids`.

`inicio_em` é opcional e usa o momento da solicitação quando omitido. Datas
explícitas precisam conter fuso horário. Os horários dos locais são
interpretados em `America/Sao_Paulo`. Uma visita precisa caber integralmente
na janela de funcionamento do local ou no período de realização do evento.
Locais com abertura igual ao fechamento são considerados abertos 24 horas.
As janelas são diárias: feriados e exceções não são modelados no catálogo.

O catálogo aceita `duracao_visita_minutos` na criação e edição dos atrativos,
com valor inicial de 30 e limites de 1 a 1440 minutos. A duração deve ser
ajustada ao atrativo pelo responsável pelo catálogo.

A seleção considera atrativos ativos de pelo menos uma das categorias
escolhidas, com coordenadas válidas. A cada parada, prioriza maior afinidade
com as categorias e, em seguida, menor tempo de visita, caminhada e espera;
o ID desempata resultados. A heurística não garante roteiro ótimo. São
incluídas até 100 paradas que caibam no tempo disponível. Caso nenhuma visita
caiba, retorna 400 com mensagem explicativa e não salva roteiro vazio.

O percurso é estimado a pé usando distância geográfica **em linha reta** e
velocidade de 75 metros/minuto, com caminhada e espera arredondadas para cima.
Não há cálculo de ruas, acessibilidade, trânsito, obstáculos nem navegação.
O tempo começa na primeira parada; deslocamento até ela e retorno não são
incluídos. O limite vale para essa estimativa, e não garante a duração real.

A resposta 201 preserva o formato do roteiro e acrescenta `inicio_em`,
`tempo_disponivel_minutos` e `duracao_estimada_minutos`. Cada item acrescenta
`chegada_em`, `saida_em`, `deslocamento_minutos`, `espera_minutos` e
`duracao_visita_minutos`. A chegada antecede uma possível espera; a saída
inclui espera e visita. Esses valores são persistidos como previsão no
momento da geração. Adicionar ou remover paradas manualmente invalida essas
estimativas, que passam a ser nulas; renomear preserva o planejamento.

Ausência de token ou token inválido retorna 401. Formatos inválidos retornam
422; preferências indisponíveis, título em branco ou ausência de opções
compatíveis retornam 400. Geração e salvamento são transacionais.

Antes de executar a versão com geração, aplicar as migrações:
`.venv/bin/python manage.py migrate`.

Executar os testes com `.venv/bin/python manage.py test rotas --noinput`.
O Django cria e remove um banco de testes separado do banco de desenvolvimento.
