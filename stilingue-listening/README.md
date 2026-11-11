# Stilingue Social Listening — Plugin para Claude

Plugin oficial da **Stilingue by Blip** que conecta o Claude à maior plataforma de social listening do Brasil. Com ele, o Claude consulta dados reais de redes sociais — buzz, sentimento, tendências, influenciadores e atendimento (SAC) — direto das APIs da Stilingue, com a metodologia de análise que nossos especialistas usam no dia a dia.

## O que é a Stilingue

A Stilingue é a plataforma de social listening e SAC 2.0 da Blip. Ela monitora publicações públicas em Instagram, X/Twitter, Facebook, YouTube, TikTok, LinkedIn, portais de notícias e blogs, e organiza tudo em três produtos que este plugin cobre:

| Produto | O que é | Ferramenta MCP |
| --- | --- | --- |
| **Radar** (Mar Aberto) | Busca em tempo real em toda a base pública da Stilingue (~5,8 bi de posts desde 2018). Não precisa de painel configurado. | `radar` |
| **Warroom** (Listening proprietário) | Painéis dedicados do cliente, com coleta customizada, Grupos, Temas, Tags e 22 visões analíticas (sentimento, influenciadores, séries temporais, imprensa etc.). | `warroom_query` |
| **Setup de painel** | A configuração do painel em si: canais coletados, Grupos, Temas, Tags, regras de automação e limites de uso — com leitura crítica de consultoria. | `setup` |
| **Smartcare** (SAC 2.0) | Métricas de atendimento: status de conversas, SLAs (TMR/TMT), voz do cliente. Acessado via `warroom_query` com parâmetros de SAC. | `warroom_query` (`sac_type`, `status`) |

## O que vem no plugin

- **Conector MCP remoto** — servidor hospedado pela Stilingue que expõe as ferramentas `radar`, `warroom_query` e `setup` (todas somente leitura: o plugin não publica, não responde e não altera nada nos seus painéis).
- **Skill `fundacao-mcp`** — camada de fundação do MCP: ensina o Claude a escolher a fonte certa (Radar vs Warroom), qualificar pedidos vagos antes de consultar, interpretar ausência de dado corretamente, aplicar boas práticas analíticas (contaminação, normalização, comparação) e usar a terminologia certa da Stilingue. Inclui referências detalhadas de parâmetros e os 22 `paths` do Warroom, mais um guia de discovery e uma matriz de cobertura de coleta por rede.
- **Skill `setup-conexao`** — guia o usuário na primeira conexão e na resolução de erros de autenticação.
- **Skill `blip-design-system`** — identidade visual oficial da Blip (cores, tipografia Nunito Sans, componentes, ilustrações, UI kit do Blip Desk) para qualquer artefato visual que o Claude gerar a partir dos dados da Stilingue.
- **Skill `one-page-report`** — monta relatórios executivos de uma página em HTML autocontido (pronto pra PDF/impressão/e-mail), a partir de dados do Radar, Warroom ou Smartcare. Pergunta se deve usar o tema Stilingue by Blip ou um tema personalizado com a cara da marca do cliente.
- **Skill [`prompt-triagem`](./skills/prompt-triagem/SKILL.md)** — analisa os últimos seis meses de tags e temas aplicados no painel selecionado e propõe um prompt inicial para trial do agente de triagem. Usa exemplos reais para inferir critérios de classificação, explicita lacunas e entrega um texto editável para revisão e uso na ferramenta, sem alterar o painel nem ativar o agente.

## Como conectar

### Pré-requisito

Ser cliente Stilingue by Blip com credenciais ativas na plataforma (as mesmas de `app.stilingue.com.br`). Não é cliente? Fale com o time comercial da Blip.

### Instalação

1. Instale o plugin pelo diretório de plugins do Claude (Cowork / Claude Code) ou adicione o conector Stilingue pelo diretório de conectores no Claude.ai.
2. Na primeira ativação, o Claude abre a **página de login da Stilingue** no seu navegador.
3. Entre com seu **usuário e senha da Stilingue**. Pronto — o Radar já funciona.
4. Para consultar um **painel** (Warroom/Setup/Smartcare), tenha em mãos a **apikey do painel** (ID numérico, disponível no Warroom em Configurações → Integrações → API). Basta informá-la ao Claude na conversa, ou pedir que ele pergunte.

### Como funciona a autenticação (e por que é segura)

O conector implementa **OAuth 2.1 com Authorization Code + PKCE**:

1. O Claude direciona você para a página de autorização hospedada pela Stilingue (`/oauth/authorize`).
2. Você faz login numa página web comum — **sua senha nunca passa pelo chat, nunca é vista pelo modelo e nunca é armazenada pelo conector**.
3. O servidor da Stilingue valida suas credenciais diretamente com a plataforma (server-to-server) e emite um código de autorização de uso único (validade de 5 minutos).
4. O Claude troca esse código por um token de acesso opaco com validade de **24 horas**, renovado automaticamente via refresh token por até 30 dias — nunca além da validade da sua sessão real na Stilingue.
5. Toda chamada às ferramentas exige esse token (`Authorization: Bearer`). Sessão expirada = o Claude reabre o fluxo de login sozinho.

Tokens podem ser revogados a qualquer momento pela Stilingue, e o acesso respeita exatamente as permissões da sua conta na plataforma.

## Exemplos de uso

- "O que estão falando da minha marca essa semana?" → panorama com volume, sentimento, evolução, exemplos de posts e principais vozes.
- "Compara o buzz da campanha X com o da concorrente Y em junho" → comparação lado a lado com mesma janela de tempo e mesma métrica.
- "Meu painel está bem configurado?" (com a apikey) → auditoria do setup: grupos com baixa cobertura, automações pausadas, saúde dos limites de coleta.
- "Como está o SLA do meu SAC este mês?" → status de conversas, TMR/TMT, gargalos.
- "Cria um prompt inicial de triagem para este cliente com base nas tags e temas dos últimos seis meses" → seleção do painel, análise do histórico e prompt para trial, com critérios e ressalvas.

### Prompt inicial de triagem

Invoque `/prompt-triagem` ou peça um prompt para iniciar o trial do agente de triagem. A skill usa `list_panels` e `setup` para identificar o painel e a taxonomia, e `warroom_query` para analisar o uso das anotações nos últimos seis meses de calendário.

É necessário acesso ao setup e à leitura das publicações do mesmo painel. Se as ferramentas não fornecerem texto associado às tags/temas aplicados, a skill solicita um export autorizado com esses dados; rankings ou nomes de rótulos isolados não bastam para inferir regras.

O resultado é uma proposta inicial, não um gabarito nem uma configuração publicada: inclui o prompt para copiar no campo de instruções customizadas do triagem, a evidência que sustenta as regras e um roteiro de teste. O escopo padrão é só tags e temas, sem resposta pública/privada nem alteração de sentimento/status. Teste primeiro em **curadoria**, com revisão humana: instruções de prompt não são uma trava técnica de publicação.

O cliente pode revisar e alterar o texto depois na ferramenta. O histórico pode incluir automações e classificações inconsistentes; a skill não promete reproduzir todas as anotações nem medir acurácia sem um teste real.

## Privacidade e dados

- O conector acessa **apenas dados que sua conta Stilingue já pode ver** na plataforma.
- Todas as ferramentas são **somente leitura**.
- Credenciais nunca transitam pelo chat; apenas tokens opacos de curta duração.
- Política de privacidade: [Plataforma](https://stilingue.com.br/politica-de-privacidade-plataforma/) · [Site](https://stilingue.com.br/politica-de-privacidade-site/)

## Suporte

- Documentação da API Stilingue: https://docs-stilingue.blip.ai
- Suporte a clientes: suporte.sti@blip.ai

## Licença

MIT
