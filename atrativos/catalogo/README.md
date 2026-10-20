# Catálogo inicial de Paranaguá

Consulta às fontes: **20/10/2026**. Este é um recorte inicial urbano de oito
atrativos reais, e não um inventário completo do município. O arquivo
`paranagua.json` guarda as fontes de cada registro. As descrições foram
redigidas para o aplicativo, sem copiar textos integrais das fontes.

## Popular o banco

Com PostgreSQL disponível e as migrações aplicadas:

```bash
.venv/bin/python manage.py popular_atrativos
```

O comando cria somente os locais ausentes e as categorias necessárias,
em uma única transação. Um nome já cadastrado, inclusive sem acentos ou com
variação de caixa/espaços, é preservado. Também preserva atrativos desativados,
registros do tipo base, imagens, categorias e edições manuais. Não atualiza
os registros existentes nem elimina dados. Executá-lo novamente não duplica
os registros. Não cria usuários, eventos ou roteiros.

## Critérios dos dados

- Endereços e contexto: Secretaria Municipal de Cultura e Turismo de Paranaguá;
  para o museu, cadastro Visite Museus/IBRAM e UFPR.
- Coordenadas: Visite Museus, ProgrameViagem e OpenStreetMap/Mapcarta, conforme
  indicado individualmente. São referências geográficas, não entradas
  georreferenciadas nem garantia de precisão de navegação.
- A coordenada da estação deriva de dados dos colaboradores OpenStreetMap,
  disponibilizados sob [ODbL](https://www.openstreetmap.org/copyright).
- Durações de visita são estimativas editoriais para planejamento, não
  durações oficiais.
- Igrejas, estação e museu: esta carga propõe **visita externa**, porque não
  há representação de calendário semanal no modelo atual. A janela 09h–18h
  é uma sugestão diurna de planejamento, não horário oficial de acesso
  interno, nem confirmação de que um prédio está aberto.
- Fonte e passarela: contemplação externa com a mesma janela diurna sugerida.
- Mercado do Café: a fonte municipal informa seg.–sáb. 09h–18h e dom. 09h–12h.
  O cadastro usa a interseção conservadora 09h–12h em todos os dias. O consumo
  no mercado é pago à parte.
- O preço zero se refere à visita externa ou circulação no mercado; não
  representa gratuidade de serviços, passeios, ingressos internos ou consumo.
- O museu já existente no banco não é alterado por essas convenções. Quando
  criado por este comando em banco vazio, contempla visita externa; visita
  interna é informada pela UFPR como de terça a domingo, 08h–20h.
- Não foram inventadas datas de eventos, tarifas do aquário nem horários de
  visitação interna. Fotos não são importadas; a carga preserva as existentes.
- Funcionamento, obras e acesso podem mudar. Revalidar as fontes antes de
  publicar o catálogo para turistas.

## Verificação

```bash
.venv/bin/python manage.py test atrativos.tests.test_popular_atrativos --noinput
```

A listagem está em `GET /v1/locais/`; categorias em `GET /v1/categorias/`.
A geração de roteiros continua exigindo login.
