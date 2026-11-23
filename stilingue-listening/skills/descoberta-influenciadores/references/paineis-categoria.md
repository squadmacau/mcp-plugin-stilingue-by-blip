# Painéis de categoria da Stilingue

Painéis pré-montados pela Stilingue para análise de categoria, com coleta dedicada e contínua. Para descobrir influenciadores, eles são **melhores que o Radar** em três pontos:
- trazem o **ranking de influenciadores do painel**, com seguidores, nº de posts, gênero inferido, verificado e as marcas/categorias que cada perfil cita;
- os posts trazem **visualizações de vídeo** e **quais grupos (marcas) cada post cita**;
- o filtro por grupo deixa recortar por **marca**, **concorrente** ou **categoria**.

Use sempre que a marca ou a categoria do pedido existir num deles. O Radar continua valendo para categorias fora dos painéis, para o panorama e para descobrir micros por subnicho.

> Interno: os IDs abaixo dão acesso aos painéis. Enquanto a leitura depender da sessão do usuário, só funciona para quem tem acesso a eles (ver "Acesso" no fim). Nunca mostre IDs ao usuário: fale o nome do painel.

## Catálogo

| Painel | account_id | universe_id | Status | Desde | Como os grupos são organizados |
|---|---|---|---|---|---|
| Beleza | 6319210817388544 | 5020479211962368 | Coletando | 2018 | `[M]` 35 marcas (Natura, Boticário, Avon, L'Oréal, Sallve, Creamy, Princípia, La Roche-Posay, Vichy, Lola, Salon Line…) · `[C]` Maquiagem, Rosto (skincare), Corpo, Cabelo, Unha, Perfumaria · temas Tipos de Pele, Preocupação, Tratamentos |
| Alimentos & Bebidas | 6345830647988224 | 5379940754391040 | Coletando | 2021 | `[M]` fabricante e `[P]` produtos de ~45 empresas (Nestlé, Ambev, Coca-Cola, Cacau Show, Heineken, BRF, Pepsico, 3 Corações, Melitta, Heinz…) · temas Vegano, Diet/Light, Orgânicos, Desejo de compra, Restrições alimentares |
| Finanças | 5457164063997952 | 6168777398157312 | Coletando | 2020 | `BCO` bancos, digitais (Nubank, Inter, C6, PicPay…), `INV` corretoras, `CRD` crédito, `SOL` maquininhas, `BAND` bandeiras · temas Cartão de crédito/débito, Conta |
| Games | 6468481105526784 | 6582004255031296 | Coletando | 2019 | `[C]` consoles (Sony, Microsoft, Nintendo…), `[P]` plataformas (Steam, Roblox, Discord), `[S]` streaming (Twitch, YouTube Gaming), `[D]` publishers · eSports, PC Gamer · tema Streamer |
| Black Friday 2026 | 6608472479891456 | 5152444307472384 | Coletando | 2022 | `[EVT]` Black Friday/Week/Cyber Monday/Esquenta · `[PROD]` 30 categorias de produto (Beleza, Eletrônicos, Moda, Pet, Suplementos…) · temas `[MARCA]` por setor, jornada (intenção de compra, preço, entrega, fraude) |
| Copa do Mundo 2026 | 6246334424023040 | 4845679352348672 | Parado (histórico) | mar/2026 | Seleções · patrocinadores FIFA (`[FP]`, `[PM]`) e da Seleção (`[PBR]`) · transmissoras (`[TR]`) · marcas oportunistas (`[PTR]`) |
| Rock in Rio 2026 | 6039009846362112 | 6602389296513024 | Parado (histórico) | 2018 | Patrocinadores (`[PT]`), apoiadores (`[AP]`), poder público (`[PI]`), transmissoras (`[TR]`) · temas de experiência (filas, ingressos, banheiros…) |

Padrão de nome dos grupos: `[M]` marca, `[C]`/`[CAT]`/`[PROD]` categoria, `[P]` produto, `[EVT]` evento. Em painéis de evento, cada marca tem `-- TENT` (menções), `POSTS` (perfil próprio) e `COMENTÁRIOS`: para influenciadores use o `TENT`. A lista acima é um retrato de nov/2026. Antes de rodar, confirme os grupos com `setup` (`groups_limit` 200, `themes_limit` 5, `tags_limit` 5; a resposta é grande e vai para arquivo).

## Escolher painel e recortes

1. **Pela marca**: procure a marca nos grupos `[M]`/`[PT]`/`[PBR]` dos painéis. Achou → aquele é o painel, e os **concorrentes** são as outras marcas do mesmo setor no painel (confirme a lista com o usuário em uma pergunta).
2. **Pela categoria**: use o grupo `[C]`/`[PROD]` correspondente (skincare = `[C] Rosto`; suplementos = `[PROD] Suplementos` no Black Friday).
3. **Eventos parados** (Copa, Rock in Rio) servem para achar quem já fez ação com patrocinadores e para cases. As janelas precisam cair dentro do período coletado.

## Chamadas (todas com `account_id` + `universe_id`)

| Recorte | Chamada | Arquivo em `raw/` |
|---|---|---|
| Quem fala da marca | `warroom_query path=top_influenciadores groups=<id do grupo da marca> limit=100` | `warroom__<painel>__marca-<slug>.json` |
| Quem fala de cada concorrente | idem, um por concorrente | `warroom__<painel>__conc-<slug>.json` |
| Categoria, só pessoas | idem com `groups=<grupo da categoria> channels=Instagram:YouTube genders=Homem:Mulher` | `warroom__<painel>__cat-<slug>-pessoas.json` |
| Categoria, todos | idem sem `genders` | `warroom__<painel>__cat-<slug>.json` |
| Posts dos candidatos | `warroom_query path=publicacoes uids=<30 uids separados por :> limit=300 projection=text,username,uid,channel,posted_at,likes,comments,shares,videoplays,post_url,sentiment,groups` | `painelposts__<painel>__<n>.json` |

Regras que o teste mostrou:
- `groups` recebe o **id** do grupo (ex.: `[M] Sallve_7103508`), que sai do `setup`.
- `top_influenciadores` aceita **no máximo 30 dias** por chamada. Para 90 dias, rode 3 janelas e salve como `…__marca-x-w1.json`, `-w2`, `-w3`.
- O filtro `genders=Homem:Mulher` remove marcas, mídia e páginas, porque o gênero só é inferido para pessoas. Com ele, o ranking de skincare virou 100 criadores, metade micro. Mas ele também tira criadores com gênero "indefinido", inclusive grandes. Rode os dois recortes.
- Puxe posts dos **~90 primeiros** candidatos (3 lotes de 30 uids), priorizando quem aparece nos recortes de marca e concorrente. Sem posts lidos, o perfil fica com score menor e relação "a confirmar".
- O `limit=300` de publicações corta a lista: quem posta muito pode ocupar o lote. Se um lote voltar com menos de ~20 autores, divida-o.

## Ruído dos grupos de marca: confirme no texto

Grupo de marca é configuração de coleta e pega palavras ambíguas. No teste do painel Beleza:
- `[M] Creamy` trouxe receitas de "creamy cake" e resenhas de perfume "cremoso";
- `[M] Sallve` trouxe "salve" como saudação.

Por isso:
- em `config.json`, `marca_cliente_termos` e `concorrentes` levam **termos específicos** (handle, "marca + skincare", nome de linha), nunca a palavra solta quando ela for ambígua;
- o script só considera relação com a marca quando o **texto** do post confirma. Grupo sem texto confirmado vira alerta de ruído, e perfil sem posts lidos fica com relação "?";
- na curadoria, **cruze sua leitura com os sinais do motor** (`publi_marca`, `cupom_multimarca`, `publi_concorrentes`, alertas) antes de escrever o "por que". O motor lê todos os posts; você lê uma amostra.

## Relação com a marca (o que o script calcula)

| Relação | Regra | Leitura para o cliente |
|---|---|---|
| Parceira atual | publi/cupom da marca num post sem concorrente | Renovar, ampliar, medir |
| Fala da marca | cita a marca sem publi | Collab natural, custo de convencimento baixo |
| Multimarcas | cita marca e concorrentes; ou cupom da marca numa lista com concorrentes | Bom para comparativo e performance, sem exclusividade |
| Fala de concorrente | só concorrentes, sem publi | Oportunidade de conquista |
| (alerta) Publi para concorrente | publi/cupom de concorrente | Não abordar agora; acompanhar o fim do contrato |
| Categoria | nenhuma das marcas | Neutro: avaliar pelo encaixe |

Bônus de quebra: o recorte da própria marca mostra **o elenco atual dela** (no teste: a campanha de lançamento de novembro da Sallve inteira) e o dos concorrentes. Vale um parágrafo na resposta.

## Acesso: o que muda no MCP para clientes sem acesso

Hoje a leitura usa a sessão de quem está logado. Funciona para quem é membro das contas (equipe Stilingue), não para o cliente. Proposta para o servidor MCP:

1. **Catálogo no servidor**: uma lista dos painéis de categoria (nome, ids, setor, status) com uma credencial de serviço só de leitura. Os ids saem do plugin público e ficam no servidor.
2. **Tool nova `categoria_influenciadores`** (ou um parâmetro `painel_categoria` em `warroom_query`), aberta a qualquer usuário logado, que aceita só:
   - `painel` (nome do catálogo), `grupo` (por nome; o servidor resolve o id), `date_range` ≤ 30 dias, `channels`, `genders`, `limit` ≤ 100 → `top_influenciadores`;
   - `uids` (≤ 30) + `projection` restrita → `publicacoes` desses perfis.
   - Nada de `setup` de escrita, SAC, notas internas, `apikey` ou outros `path`.
3. **`list_category_panels`**: devolve nome, setor, status e grupos `[M]`/`[C]` de cada painel, para a skill escolher o painel pelo nome da marca sem precisar de `setup`.
4. **Telemetria** no padrão atual ("MCP TOOL categoria_influenciadores"), para medir o uso por cliente.

Com isso, a skill troca as chamadas `warroom_query`/`setup` deste arquivo pela tool nova, sem mudar o resto do fluxo.
