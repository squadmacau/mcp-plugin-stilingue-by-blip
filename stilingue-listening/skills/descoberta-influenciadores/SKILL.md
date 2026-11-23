---
name: descoberta-influenciadores
description: Encontra e aprofunda influenciadores (nano, micro, mid, macro, mega e locais) a partir de uma marca ou categoria, usando os painéis de categoria da Stilingue e o Radar — opcionalmente o painel do cliente — e pesquisa online para perfil, brand safety e contato comercial. Diz por que falar com cada um (já é parceiro, fala da marca, fala do concorrente) com ideia de collab. Entrega shortlist explicada no chat e oferece uma Central de Influenciadores em HTML navegável (busca, filtros, perfil completo, parecidos, comparação). Use SEMPRE que pedirem "encontrar/descobrir/mapear influenciadores", "creators de <categoria>", "quem fala de <assunto>", "micro influenciadores", "influenciadores locais/de <cidade>", "perfis parecidos com @fulano", "me conta tudo sobre @fulano", "shortlist para campanha", "central de influenciadores" — mesmo sem citar a Stilingue. NÃO use para medir campanha já veiculada (isso é análise de painel) nem para os canais da própria marca (canais-proprietários).
---

# Descoberta de Influenciadores

Transforma uma **categoria** em uma shortlist de criadores defendível: quem fala do assunto de verdade, com que constância, com que engajamento relativo, quem é parecido com quem, onde a pessoa está e como chegar nela. Funciona para os três pedidos mais comuns: **micro**, **macro** e **locais**.

Esta skill roda **em cima da `fundacao-mcp`**: as regras do Radar (amostra, cobertura por rede, sintaxe booleana, limite de 300 posts por chamada, terminologia) valem integralmente. Se ela ainda não foi carregada na conversa, carregue antes da primeira consulta.

Arquivos desta skill (caminhos relativos à pasta da skill):

| Arquivo | Quando abrir |
|---|---|
| `scripts/build_central.py` | Sempre: agrega, pontua, acha parecidos e gera a Central |
| `assets/central-template.html` | Usado pelo script; não edite por pedido |
| `references/categorias.md` | Ao montar subnichos de uma categoria (biblioteca pronta para 14 categorias) |
| `references/pesquisa-online.md` | Antes da pesquisa online da shortlist (perfil, local, brand safety, contato) |
| `references/paineis-categoria.md` | Sempre que a marca ou a categoria existir num painel de categoria da Stilingue (catálogo, chamadas, ruído dos grupos, relação com a marca) |
| `references/formatos.md` | Ao escrever `config.json` e `curadoria.json` |

---

## 0. Briefing — no máximo duas perguntas

A skill precisa de **uma marca ou uma categoria**. Sem nenhuma das duas, essa é a única pergunta: *"Para qual marca ou categoria você quer encontrar influenciadores?"* Com a marca, a categoria e os concorrentes saem do painel de categoria (ver §2B); confirme os concorrentes numa frase. Com só a categoria, rode sem marca: o "por que" fica no encaixe, sem relação com marca.

Assuma o resto e declare na resposta:

| Item | Padrão se não disserem |
|---|---|
| Período | Últimos 90 dias |
| Porte | Todos, com lentes separadas para micro/nano, mid, macro/mega |
| Região | Brasil; "locais" só se pedirem cidade/estado |
| Marca do cliente e concorrentes | Nenhuma (sem checagem de conflito) |
| Painel | Não usar, a menos que o usuário fale em painel, "minha marca" ou "nosso cliente" |

Pergunte só o que muda o resultado: **a marca e os concorrentes**, quando não der para inferir do painel (para detectar parceiros atuais, quem já fala da marca e quem tem conflito), e, se pedirem locais sem dizer onde, **a cidade**. Não pergunte formato, nem quantos perfis.

## 1. Montar a categoria em subnichos

O ranking do Radar (`trend_users`) devolve **no máximo 10 contas por busca e não pagina**. Uma busca genérica só traz contas grandes, marcas e portais. O que traz micro é **quebrar a categoria em 6 a 9 subnichos estreitos**, cada um com uma busca própria.

1. Abra `references/categorias.md`. Se a categoria estiver lá, parta dos subnichos sugeridos; se não, crie seguindo o mesmo padrão: um subnicho por dor, ingrediente/objeto, formato de conteúdo ou público ("pele oleosa", "k-beauty", "resenhas", "pele madura").
2. Cada busca tem **até 21 termos**, operadores em **MAIÚSCULAS**, termos compostos entre aspas. Nunca use a sintaxe de configuração de painel (`&&`, `-termo`).
3. Monte também uma **busca principal** (o OR dos termos mais fortes de cada subnicho) para panorama e publicações.
4. Valide a principal antes de seguir: `statistics` (volume e mix de canais) e uma amostra de 20 `posts`. Se mais de ~30% da amostra for de outro assunto, ajuste os termos ou use `AND NOT` e valide de novo, uma vez só.

## 2. Coleta (Radar)

Uma vantagem a usar: o Instagram do Radar vem da **Central de Influenciadores da Stilingue** (perfis cadastrados, com autoria identificada). Ou seja, a base de Instagram já é um pool de criadores e páginas, não de pessoas comuns. YouTube e X entram por texto; TikTok não está no Radar.

Crie a pasta de trabalho `./central-<categoria>/` com `raw/` dentro. **Todo resultado vai para arquivo em `raw/`**, com o nome abaixo. Quando a ferramenta salvar um resultado grande em arquivo, copie esse arquivo; quando vier inline, grave o JSON exatamente como veio. Nunca retranscreva dados de cabeça.

| Chamada | `data_type` | Arquivo |
|---|---|---|
| Busca principal, período todo | `statistics` | `raw/statistics.json` |
| Busca principal, período todo | `linechart` | `raw/linechart.json` |
| Cada subnicho, período todo | `trend_users` | `raw/trend__<slug-do-subnicho>.json` |
| Busca principal em **4 janelas** do período (ex.: 4 blocos de ~3 semanas), `limit` 300 | `posts` | `raw/posts__w1__p1.json` … `raw/posts__w4__p1.json` |
| Opcional: 2ª página da janela mais recente (`offset` 300) | `posts` | `raw/posts__w4__p2.json` |

Por que em janelas: os posts vêm ordenados por relevância (`hot`), que favorece o recente. Sem fatiar, 600 posts cobrem só os últimos dias, e a constância do criador fica invisível.

**Painel do cliente (opcional).** Se o usuário tiver painel da categoria/marca (use `list_panels`; nunca peça IDs), rode `warroom_query` com `path=top_influenciadores` (limit 100) e salve como `raw/warroom__top.json`. Esse ranking traz seguidores, verificado, gênero inferido, grupos e um score de influência do painel. Ele serve para achar **quem já fala da marca do cliente**, o candidato mais barato de ativar. Não use `path=aaa` com limit alto: a resposta é gigante.

## 2B. Painéis de categoria da Stilingue (fonte preferencial)

A Stilingue mantém painéis de categoria (Beleza, Alimentos & Bebidas, Finanças, Games, Black Friday, Copa do Mundo 2026, Rock in Rio 2026) com coleta dedicada e grupos por marca e por categoria. Abra `references/paineis-categoria.md`: tem o catálogo, as chamadas e os nomes de arquivo. Se a marca ou a categoria estiver lá:

1. Rode o ranking de influenciadores do painel em 4 recortes: **marca**, **cada concorrente**, **categoria só pessoas** e **categoria todos** (janelas de até 30 dias).
2. Puxe as publicações dos ~90 primeiros candidatos por `uids`, em lotes de 30. Elas trazem visualizações de vídeo e as marcas citadas em cada post.
3. O Radar entra como complemento: panorama (`statistics`, `linechart`) e subnichos para micros que o painel não pegou.

**Ruído:** grupo de marca do painel pega palavras ambíguas ("creamy" em receita, "salve" como saudação). Use termos específicos em `marca_cliente_termos` e `concorrentes`; o script só aceita relação com a marca confirmada no texto do post.

## 3. Preparar e completar seguidores

```bash
python3 <pasta-da-skill>/scripts/build_central.py prepare ./central-<categoria>
```

Gera `candidatos.md` (ranking preliminar com a chave de cada perfil) e `lookups.md`. Os autores que postam com frequência mas não estavam nos rankings chegam **sem seguidores**. `lookups.md` traz lotes de 4 handles em OR. Rode cada lote com `radar` `data_type=trend_users` no mesmo período e salve como `raw/lookup__NN.json`. Isso devolve os seguidores de quem aparece e também **quem cita esses perfis** (outros criadores, agências). Essas contas viram candidatas novas e sinal de rede para os parecidos. Rode até 10 lotes; o resto fica "A confirmar".

## 4. Curadoria — sua leitura, não a heurística

O script classifica o tipo de perfil por padrões de nome, e erra. Para os **~60 primeiros** de `candidatos.md`, leia 2 ou 3 textos de posts de cada um (direto dos arquivos em `raw/`, com código) e escreva `curadoria.json` (formato em `references/formatos.md`):

- `tipo`: `criador`, `especialista` (médico, dermato, nutri, farmacêutico… com conteúdo próprio), `marca`, `midia`, `varejo` ou `agregador` (memes, "vídeos virais", páginas de dicas sem rosto). Só criador e especialista viram candidatos; os demais vão para "Outras vozes".
- `excluir: true` para quem usa a hashtag da categoria fora de contexto (ex.: receita de chocolate com #skincare).
- `resumo`: uma frase sobre **o que a pessoa publica**, escrita a partir dos posts lidos. Nada de adjetivo de marketing nem de suposição sobre a audiência.
- `destaque: true` em até 8 perfis que você defenderia na reunião.
- Sinais que aparecem no texto valem registro: modelo afiliado ("comente QUERO que eu te mando o link"), #publi identificada, marca própria, parceiros citados com @ (vão em `parcerias`, com o link do post como fonte), revenda/venda direta (consultora de marca é conflito).
- `por_que` (para a shortlist): **uma a duas frases** sobre por que a marca deveria procurar essa pessoa, ancoradas em fatos dos posts: o que ela já faz com a marca ou com o concorrente, para quem fala, qual formato funciona. Sem a marca configurada, foque no encaixe com o objetivo.
- `ideia_collab`: um formato concreto que **já existe no conteúdo dela**, adaptado à marca ("comparativo de niacinamida incluindo a marca", "guia de verão vegano com a marca em todos os passos"). Para quem é parceiro do concorrente: "não abordar agora".
- **Cruze com o motor antes de escrever.** `candidatos.md` e `out/data.json` trazem relação com a marca, `publi_marca`, `cupom_multimarca`, `publi_concorrentes` e alertas. O motor lê todos os posts; você lê uma amostra. Se discordar, releia os posts daquele perfil.

O script também gera `motivos` automáticos (parceria atual, fala da marca, conquista, especialista, constância, engajamento relativo, visualizações, conversa, afiliado, porte, recência). Eles aparecem embaixo do seu `por_que`.

## 5. Influenciadores locais

O Radar quase não entrega geolocalização, e buscar `categoria AND cidade` traz sobretudo **veículos, shoppings e rádios locais**. Use esses perfis como contexto (eles costumam repostar criadores da cidade), não como candidatos. O caminho que funciona:

1. **Descobrir fora**: pesquisa online por listas da cidade e do nicho (ver `references/pesquisa-online.md` §Locais).
2. **Validar dentro**: rode os handles encontrados em lotes de `trend_users` (como no §3) e, se houver posts deles na categoria, eles entram com métricas reais.
3. **Marcar a confiança**: `local.confianca = "confirmado"` só com bio, site ou imprensa como fonte. O script marca "provável" sozinho quando a pessoa cita a cidade em ≥2 posts e em ≥30% deles. Nunca apresente provável como confirmado.

Inclua as cidades pedidas em `config.json` → `cidades`, para o script detectar menções.

## 6. Pesquisa online da shortlist

Para os **8 a 15** perfis que vão à shortlist (destaques + melhores de cada lente), siga `references/pesquisa-online.md`: quem é, cidade, outras redes, agência, parcerias recentes, polêmicas, regras do setor e **contato comercial**. Registre tudo em `curadoria.json` com fonte e data.

Regras de contato, inegociáveis:
- Só **contato profissional publicado** pelo próprio criador ou por quem o representa (e-mail comercial da bio, site, media kit, agência, formulário de parceria). Nunca telefone pessoal, endereço, família, nem e-mail "deduzido" por padrão (nome@gmail…).
- Todo contato leva `fonte` (URL) e `verificado_em`.
- Não achou? Diga "contato não localizado publicamente" e indique o caminho: mensagem pelo perfil ou agência. Isso é resposta válida; inventar não é.
- Não contorne captcha (ex.: botão de e-mail do YouTube). Registre "e-mail comercial na aba Sobre do canal" como caminho.

## 7. Gerar e entregar

```bash
python3 <pasta-da-skill>/scripts/build_central.py build ./central-<categoria>
```

Gera `out/data.json` (base para a resposta) e `out/central.html`. Leia o `data.json` com código para escrever a resposta. Não recalcule nada de cabeça.

**Resposta no chat** (sempre, antes de oferecer o HTML):
1. Um parágrafo de panorama: volume da categoria no Radar, onde ela acontece, subnichos com mais criadores.
2. A shortlist em tabelas curtas. **Com marca**, organize por relação: **Já são parceiras** (renovar/ampliar), **Falam da marca** (collab natural), **Falam do concorrente** (conquista), **Novos da categoria** (por porte). **Sem marca**, por porte: **Micro e nano** (até 5), **Mid** (até 3), **Macro e mega** (até 3), **Locais** (se pedido), **Especialistas** (se fizer sentido). Colunas: Perfil · Porte · Seguidores · Por que falar · Ideia de collab · Atenção.
3. Alertas que mudam decisão: publi para concorrente (não abordar agora), dono de marca na categoria, revenda de outra marca, engajamento fora da curva, saturação de publi.
   Com marca, inclua um parágrafo com o **elenco atual** (parceiras detectadas e campanha em curso) da marca e dos concorrentes.
4. Replicabilidade: fonte, período, buscas usadas, o que ficou fora (TikTok, comentários do Instagram, demografia da audiência).
5. Oferta da Central: *"Quer que eu monte a Central de Influenciadores em HTML para o cliente navegar (busca, filtros, perfil completo, parecidos e comparação)?"*

**Central HTML** (quando aceitarem ou pedirem direto):
- Tema: pergunte uma vez, com a palavra "tema", se vai no **tema Stilingue by Blip** (padrão) ou com a cara da marca do cliente. Personalizado = preencha `config.json` → `tema` (`primaria`, `acento`, `escura`, `media`) e rode o `build` de novo.
- Publique `out/central.html` como artefato (publicação a partir de arquivo), com título "Central de Influenciadores · <Categoria>". Sem ferramenta de artefato, envie o arquivo. O HTML é autocontido: sem imagens remotas (avatares são iniciais, por privacidade e porque imagens de CDN expiram), exportação por "Copiar CSV", links abrem o original.
- Na resposta, uma linha sobre o que a Central tem. Não repita o conteúdo.

## 8. Pedidos derivados

**"Me conta tudo sobre @fulano" (central de um influenciador).** Faça o mesmo fluxo em escala menor:
1. `trend_users` com o handle (seguidores + quem cita);
2. `posts` com `"handle" OR "Nome"`: o que se fala dele, quais marcas o citam, imprensa;
3. `posts` da categoria dele, filtrando o autor com código: o conteúdo dele;
4. no painel, `warroom_query` com `uids`, se houver;
5. pesquisa online completa;
6. 3 a 5 subnichos com os termos e hashtags mais característicos dele, para achar parecidos.

Gere a Central com ele em `destaque` e os parecidos ao redor.

**"Mais parecidos com @fulano".** Pegue as hashtags e subnichos dele no `data.json`, crie 3 a 5 buscas novas de subnicho, salve como novos `trend__*.json` e posts, e rode `build` de novo. Os parecidos se recalculam.

**Atualizar uma Central.** Mesma pasta, nova coleta em `raw/` (substitua os arquivos), `build` de novo e republique o mesmo artefato.

## 9. O que nunca fazer

- Afirmar que alguém "fala da marca" ou "é parceiro" só porque o grupo do painel diz. Vale o texto do post.
- Tratar `trend_users` como recomendação. Ele é "quem mais apareceu"; a recomendação é o resultado da curadoria e do score.
- Apresentar número do Radar como absoluto. É amostra: compare perfis entre si. Curtidas são uma fotografia da coleta (posts novos subestimados, antigos congelados).
- Afirmar qualidade de audiência, faixa etária ou % de seguidores falsos. O Radar não mede isso. O que existe é sinal de alerta (engajamento muito fora do grupo), e a recomendação é pedir ao criador prints das métricas da conta.
- Estimar cachê. Se perguntarem, diga que depende de negociação e que referência de mercado precisa de fonte citada.
- Baixar ou embutir foto de criador; inventar link, contato, cidade ou parceria.
- Mostrar `account_id`, `universe_id` ou `apikey`.
- Esquecer a regra do setor: publicidade com influenciador segue o Guia do CONAR (identificação clara, inclusive permuta e afiliado; cuidados redobrados com público infantil), e médicos seguem as regras de publicidade do CFM. Mencione quando a shortlist tiver especialistas de saúde.

## 10. Como explicar o score (para o usuário e para o cliente)

Score de encaixe 0–100, calculado pelo script e comparado **dentro da própria amostra**:

| Componente | Peso | Em uma frase |
|---|---|---|
| Aderência | 30% | Posta sobre a categoria com frequência e ao longo do período, e aparece nos rankings de subnicho |
| Engajamento relativo | 25% | Interações por seguidor comparadas à mediana de perfis do mesmo canal e porte |
| Conversa | 15% | A audiência comenta (não só curte) e o tom é positivo |
| Relevância | 15% | Força das publicações no Radar (rankings + `hot` vs. o mesmo canal), para não punir micro |
| Recência | 15% | Postou sobre a categoria recentemente |

Perfis com 1 ou 2 posts na amostra têm o score reduzido (confiança menor). Com marca configurada, quem já fala dela ganha um bônus pequeno (+6 parceira de fala espontânea, +3 multimarcas), e perfis sem nenhum post no nicho perdem metade do score. Nos painéis, o volume de posts do perfil no ranking conta como aderência mesmo antes de os posts serem lidos. Porte segue as faixas de mercado: nano 1–10 mil, micro 10–100 mil, mid 100–500 mil, macro 500 mil–1 mi, mega +1 mi.
