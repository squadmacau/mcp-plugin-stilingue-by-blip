# Formatos dos arquivos da pasta de trabalho

```
central-<categoria>/
  config.json
  curadoria.json            (opcional, mas sempre preencha os primeiros ~60)
  raw/
    statistics.json         radar data_type=statistics (busca principal)
    linechart.json          radar data_type=linechart (busca principal)
    trend__<slug>.json      radar data_type=trend_users, um por subnicho
    lookup__NN.json         radar data_type=trend_users com handles em OR
    posts__<janela>__<k>.json  radar data_type=posts (janela w1…w4, página p1/p2)
    warroom__<painel>__<recorte>.json   top_influenciadores de painel (recorte: marca-x, conc-x, cat-x, cat-x-pessoas)
    painelposts__<painel>__<n>.json     publicacoes por uids (lotes de 30) com projection
  candidatos.md / lookups.md   saída do prepare
  out/data.json / out/central.html   saída do build
```

O `<slug>` do `trend__` deve ser **igual** à chave do subnicho em `config.json` → `subnichos`. É assim que o script sabe em qual ranking cada perfil apareceu.

## config.json

```json
{
  "categoria": "Skincare",
  "titulo": "Central de Influenciadores · Skincare",
  "objetivo": "Micro e locais para lançamento de protetor solar no Nordeste",
  "periodo": {"inicio": "2026-08-24", "fim": "2026-11-22"},
  "marca_cliente": "Marca X",
  "marca_cliente_termos": ["marcax", "@marcax", "marca x skincare"],
  "concorrentes": {"Concorrente A": ["concorrentea", "@concorrentea", "da concorrente a"], "Concorrente B": ["concorrenteb"]},
  "cidades": ["Recife", "Salvador", "Fortaleza"],
  "subnichos": {
    "acne-e-oleosidade": ["pele oleosa", "pele acneica", "acne", "ácido salicílico", "cravos"],
    "k-beauty": ["k-beauty", "skincare coreano", "cosméticos coreanos"]
  },
  "rotulos": {"acne-e-oleosidade": "Acne e oleosidade", "k-beauty": "K-beauty"},
  "queries": [{"nome": "Categoria (principal)", "query": "skincare OR \"rotina de pele\" OR ..."}],
  "notas": ["Qualquer ressalva desta análise que o cliente precise ler."],
  "max_perfis": 200,
  "tema": {"primaria": "#1e6bf1", "acento": "#00d3e4", "escura": "#081536", "media": "#0d2a78"}
}
```

- `subnichos`: os termos servem para **marcar** o subnicho de cada post (casamento sem acento, `termo*` = prefixo). Use termos distintivos. Um termo genérico da categoria inteira ("skincare") marca tudo e apaga a diferença entre subnichos.
- `marca_cliente_termos` / `concorrentes`: confirmam no texto a relação com a marca (parceira, fala da marca, multimarcas, fala de concorrente). Use **termos específicos**: handle, nome + categoria, nome de linha. A palavra solta, se ambígua ("creamy", "salve"), traz ruído. `concorrentes` aceita lista simples ou `{nome: [termos]}`.
- `fonte`: texto livre exibido no cabeçalho (ex.: "Painel de categoria Beleza (Stilingue) + Radar").
- `tema`: só quando o cliente pedir a própria identidade visual. Sem `tema` = Stilingue by Blip.
- `max_perfis`: teto da Central. Perfis com curadoria entram sempre.

## curadoria.json

Chave = a mesma de `candidatos.md` (`canal:handle`, minúsculo, ex.: `instagram:skindam_`, `youtube:dra. marina hayashida`).

```json
{
  "instagram:fulana": {
    "tipo": "criador",
    "destaque": true,
    "resumo": "Rotinas de skincare coreano por queixa, com links de produtos (modelo afiliado).",
    "por_que": "Indica a marca espontaneamente em rotinas de pele oleosa e fala com quem compra coreano — collab soaria natural.",
    "ideia_collab": "Rotina coreana em passos com a marca no lugar dos importados.",
    "bio": "Texto da bio, se você leu numa fonte pública.",
    "seguidores": 48200, "seguidores_fonte": "HypeAuditor (22/11/2026)",
    "local": {"cidade": "Recife", "uf": "PE", "confianca": "confirmado", "fonte": "bio no perfil público via Heepsy"},
    "subnichos": ["k-beauty", "acne-e-oleosidade"],
    "contatos": [
      {"tipo": "email", "valor": "parcerias@fulana.com.br", "rotulo": "E-mail comercial da bio", "fonte": "https://…", "verificado_em": "2026-11-23"},
      {"tipo": "agencia", "valor": "Agência Y — https://agenciay.com.br/contato", "fonte": "https://…", "verificado_em": "2026-11-23"}
    ],
    "redes": [{"rede": "TikTok", "url": "https://www.tiktok.com/@fulana", "seguidores": 120000}],
    "parcerias": [{"marca": "Marca Z", "quando": "out/2026", "nota": "post identificado como #publi", "fonte": "https://… (link do post)", "conflito": false}],
    "brand_safety": [
      {"item": "Identificação de publicidade", "status": "ok", "nota": "usa #publi nas parcerias", "fonte": "https://…"},
      {"item": "Polêmicas recentes", "status": "ok", "nota": "nada encontrado em busca de notícias (nov/2026)"}
    ],
    "fontes": [{"titulo": "Perfil no HypeAuditor", "url": "https://…"}],
    "alertas": ["Texto livre de alerta adicional, se houver"]
  },
  "instagram:pagina-de-memes": {"tipo": "agregador"},
  "instagram:receita-com-hashtag": {"excluir": true}
}
```

Campos aceitos em `contatos[].tipo`: `email`, `site`, `agencia`, `assessoria`, `media_kit`, `formulario`, `linktree`, `whatsapp_comercial`, `telefone_comercial`, `dm`. Telefone/WhatsApp só quando publicado como **comercial** pelo próprio criador ou agência.

`brand_safety[].status`: `ok`, `atencao`, `risco`, `nao_verificado`.

Tudo é opcional. Campo vazio aparece na Central como "a confirmar", nunca como dado inventado.
