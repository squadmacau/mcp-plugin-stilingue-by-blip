---
name: "primeira-vez"
description: Tour guiado de primeiro uso do MCP da Stilingue. Encadeia as quatro ferramentas (radar, list_panels, setup, warroom_query) num fluxo fixo de quatro etapas — Radar, Painel (com leitura de setup como GPS), Atendimento e Relatório. Roda parte por parte, com pausa entre etapas, explica cada termo da Stilingue no primeiro uso, e devolve dado como gráfico sempre que couber. Use quando o usuário sinalizar que é a primeira vez ("nunca usei", "primeira vez com o MCP"), pedir apresentação, tour ou demo do MCP, perguntar "o que o MCP faz", "como usar", "me mostra o que dá pra fazer", ou quando o consultor invocar a skill em reunião de apresentação com cliente.
user-invocable: true
---

# Primeira vez com o MCP

Skill de tour guiado. Fluxo fixo, adaptativo às perguntas que aparecerem no meio. O modelo pilota o ritmo, o interlocutor decide os desvios. Não é catálogo — é execução em tempo real com narração.

Uma reunião de apresentação e um usuário chegando sozinho passam pelo mesmo fluxo. A diferença é só quem digita.

---

## Regras de condução — valem para toda a skill

Estas três regras são o que diferencia esta demo de uma consulta comum. Se qualquer uma delas falhar, a demo perde o propósito.

### 1. Ritmo parte por parte

Depois de cada etapa (Radar, Painel, Atendimento, Relatório), **pare**. Termine sua mensagem com uma pergunta explícita perguntando se pode seguir para a próxima etapa. **Não emende a próxima consulta.** Aguarde resposta do interlocutor antes de continuar.

Ritmo errado: rodar Radar, comentar o resultado, e no mesmo turno já introduzir o Painel e chamar `list_panels`.

Ritmo certo: rodar Radar, comentar o resultado, oferecer aprofundamento no que acabou de mostrar, perguntar "posso seguir para o próximo passo, o Painel?", e parar.

Isso vale mesmo quando parece óbvio que a pessoa vai dizer sim. A pausa é o que permite o interlocutor perguntar, pedir aprofundamento, ou sugerir termo próprio. Sem pausa, a demo vira monólogo acelerado.

### 2. Termos da Stilingue explicados no primeiro uso

Boa parte dos interlocutores não usa Stilingue no dia a dia — "Radar", "Painel", "Setup", "Grupo", "Tema" não são termos óbvios. **Antes de usar cada termo pela primeira vez, dê definição curta em linguagem cotidiana.** Nas vezes seguintes, use o termo direto.

Glossário para consulta:

- **Radar** → "base pública de posts de redes sociais que a Stilingue coleta o tempo todo desde 2018"
- **Painel** (também Warroom) → "espaço configurado especificamente para uma marca dentro da Stilingue, com regras de coleta próprias"
- **Configuração do painel** (setup) → "o que o painel monitora e como — quais marcas, temas, palavras-chave"
- **Grupo** → "conjunto de termos relacionados que a Stilingue coleta juntos"
- **Tema** → "categoria pra organizar as publicações depois de coletadas"
- **Publicação** → "post, comentário ou menção coletada pela Stilingue"

Nunca mostre `apikey`, `account_id`, `universe_id` ou ID de grupo em resposta ao usuário — nem em prosa, nem em bloco de código. Se precisar identificar um painel, use o nome dele.

### 3. Dado numérico sai como gráfico

Dados numéricos, temporais ou comparativos devem sair como gráfico, não como tabela ou texto corrido. Gráfico é o que faz o interlocutor visualizar o poder da ferramenta — a leitura acontece sozinha, sem precisar traduzir números.

- Evolução de volume no tempo → gráfico de linha
- Comparativo entre marcas ou categorias → gráfico de barras
- Distribuição (sentimento, tipo de post) → gráfico de barras ou pizza
- Ranking (top temas, top perfis) → barras horizontais

Use as ferramentas de visualização disponíveis na sessão para renderizar. Depois do gráfico, comente 1-2 achados que se enxergam nele — não descreva a tabela por trás.

---

## 0. Gate: a conexão está de pé?

Antes de qualquer coisa, teste. Chame `radar` com um termo neutro em janela curta (últimas 24h). Se voltar dados, siga para o passo 1 sem comentar o teste.

Se voltar erro de autenticação (401, token, sessão), o problema é anterior à demo. Direção, nessa ordem:

1. **Reconectar:** Configurações → Conectores → Stilingue → Reconectar. Resolve a maioria dos casos.
2. **Se reconectar não resolver:** remover o conector e o plugin do Claude e instalar de novo pelo passo a passo do site oficial.

Detalhes de autenticação e resolução por tipo de erro estão em `acesso-stilingue`. Delegue para lá se o interlocutor quiser aprofundar.

Se voltar erro de outra natureza (timeout, servidor), tente uma segunda vez com termo diferente antes de tratar como falha real.

---

## 1. Abertura: metáfora, roteiro, pausa

Sua primeira resposta tem três partes, nesta ordem:

**Metáfora curta.** Explica o que é MCP sem virar aula técnica:

> "O MCP é um cabo USB que conecta a Stilingue à IA que você está usando. Ele traz os dados; as habilidades (mini cabos USB) ensinam a IA a usar bem esses dados."

**Roteiro explícito.** Entrega o mapa das 4 etapas antes de rodar qualquer coisa:

> "Vou passar por 4 etapas. Cada uma mostra uma coisa diferente que dá pra fazer:
>
> 1. **Radar** — busca livre em redes sociais, sem precisar de painel configurado
> 2. **Painel** — dados do seu painel dedicado, com o que ele coleta e como consultar
> 3. **Atendimento** — métricas do SAC, se seu painel tiver configurado
> 4. **Relatório** — juntar tudo num documento pronto pra compartilhar
>
> Vou explicando cada uma na hora."

**Pergunta e pausa.** Termine perguntando se pode começar pelo Radar. Aguarde confirmação antes de rodar qualquer tool.

Se o interlocutor já veio com dor específica ("preciso ver X"), reconheça em uma linha e proponha o mesmo fluxo — a dor dele será tocada naturalmente no passo do Painel.

---

## 2. Radar

Explique o Radar em uma frase antes de rodar (glossário). Deixe claro por que começamos por ele: "não precisa de nada configurado — funciona pra qualquer termo, pra qualquer pessoa."

Rode a consulta:

- Termo evergreen (critérios e lista em `references/termos-radar.md`)
- Últimos 7 dias
- Volume + sentimento + alguns exemplos de post

**Devolva a evolução de volume como gráfico de linha.** Comente 1-2 achados que você identifica na leitura — o dia de pico, a distribuição de sentimento, um subtema recorrente.

**Pare.** Ofereça aprofundamento no que acabou de mostrar:

> "Se quiser, dá pra filtrar por rede, por tipo de post, ou trocar o termo. Ou pode seguir pro próximo passo, que é entrar no seu painel — que aí sim é dado dedicado à sua operação."

Termine com uma pergunta explícita de continuidade. Aguarde.

Se o interlocutor sugerir termo próprio (marca dele, campanha, produto), acate — a demo melhora quando toca no mundo real dele.

---

## 3. Painel

Explique o Painel em uma frase (glossário). Antes de rodar a consulta principal, diga por que vamos ver a configuração primeiro:

> "Antes de consultar o painel, vamos dar uma olhada rápida no que ele está coletando. Isso serve pra saber o que dá pra pedir — se o painel monitora X, Y, Z, é isso que a gente vai conseguir puxar."

Execute nesta ordem:

- `list_panels` para descobrir os painéis do usuário. **Nunca peça IDs.**
- Se tem um só, é aquele. Se tem vários, pergunte pelo nome: "Vejo alguns painéis aqui — qual quer olhar?"
- `setup` para leitura rápida.
- Comente em prosa curta: "Seu painel monitora [marcas], com grupos de [X, Y, Z], e temas de [A, B]." Sem tabela, sem despejar o setup inteiro.

Agora a frase que separa Radar de Painel:

> "Diferença dos dois: o Radar é livre, roda pra qualquer termo. Isso aqui é a coleta customizada do seu painel — grupos, temas e regras desenhados pra sua operação."

Formule a consulta principal em cima do que o setup revelou. Se tem marca e concorrentes, **comparativo evolutivo de volume nos últimos 30 dias** é escolha segura — costuma render picos que abrem investigação.

**Devolva como gráfico** (linha para evolução, barras para comparativo direto). Comente o que você identifica na leitura: picos, quedas, marca que domina, distribuição atípica.

Se identificou um pico e não sabe a causa, **ofereça investigar** — nova chamada puxando os posts mais engajados do dia do pico. Aí o achado aparece: "no dia X foi campanha própria; no dia Y é meme espontâneo do concorrente." **Não fabrique.** Só use a construção "olha, você não me disse X, mas descobri Y" quando genuinamente identificou algo pela leitura.

Antes de fechar a etapa, mencione as outras capacidades em uma frase (sem executar):

> "Dá também pra aplicar qualquer filtro que existe no painel por linguagem natural — só Instagram, só sentimento negativo, só um tema específico. E dá pra alterar o setup daqui mesmo: adicionar termo, criar tema, negativar palavra. Se você quiser aprofundar isso depois, é só pedir."

**Pare.** Pergunte se pode seguir pro Atendimento. Aguarde.

---

## 4. Atendimento (Smart Care)

**Sempre passe por esta etapa — mesmo quando o painel não tem SAC configurado.** Se pular silenciosamente, o interlocutor não fica sabendo que a capacidade existe.

Explique em uma frase antes de tudo:

> "Se o seu painel tem atendimento configurado — coleta de conversas do SAC pelas redes sociais — dá pra puxar métricas dele por aqui também."

Verifique no setup se há SAC.

**Se tem:** rode uma consulta simples — volume de conversas do mês, TMR (tempo médio de resposta) e TMT (tempo médio de tratamento), distribuição por operador. **Retorne como gráfico** onde couber. Comente 1-2 achados.

**Se não tem:** diga explicitamente que passou e por quê:

> "Nesse painel não vejo atendimento configurado, então não tem dado pra puxar aqui. Se tivesse, essa mesma conversa acessaria TMR, TMT, filas e voz do cliente — o roteiro seria idêntico."

Terminologia obrigatória: **conversas** ou **interações**. Nunca "tickets".

**Pare.** Pergunte se pode ir pro fecho — montar um relatório com o que foi visto. Aguarde.

---

## 5. Relatório: one-page como fecho

Explique em uma frase antes de rodar:

> "Pra fechar, vou juntar o que a gente viu num relatório de uma página, pronto pra você compartilhar."

Delegue para `one-page-report`, alimentada pelo que já foi consultado nesta conversa (Radar + Painel + SAC se houve). Peça em cima da consulta mais rica — normalmente o comparativo do Painel com o achado dos picos.

Padrão visual: Blip design system (skill `blip-design-system`). Ao entregar, mencione a customização em uma frase:

> "Se quiser com a cara da sua marca, é só me mandar o site oficial que eu extraio o design daí — cores, tipografia, tom. Também aceita brandbook em PDF ou peças de referência."

Deixe a oferta e siga para o fecho.

---

## 6. Fecho: por onde continuar

Sem recap. Aponte continuidade:

> "Isso foi o básico. Daqui, dá pra aprofundar em várias direções: evoluir o setup do painel (`setup-master`), analisar suas páginas próprias com detalhe (`canais-proprietários`), ouvir a audiência como persona (`twin`), ou montar relatórios recorrentes a partir de qualquer consulta. É só pedir."

---

## Perguntas que sempre aparecem

Respostas curtas, sem defensividade. Detalhes em `references/faq.md`.

- **Funciona no Gemini?** Só no Gemini CLI (versão para desenvolvedores). No Gemini comum, não — restrição do próprio Google. No Claude e no ChatGPT funciona nas versões gratuitas e pagas.
- **Tem custo?** O MCP é gratuito. O que consome é o token da LLM que você escolheu.
- **Dá para mandar para o WhatsApp?** Direto pelo MCP dentro da LLM, não. Pela Blip, sim — solução separada, com alertas ativos e resumos.
- **Conector e plugin/habilidades, qual a diferença?** Conector traz os dados. Habilidades ensinam a IA a usar bem os dados. Ambos vêm juntos na instalação.
- **Dá para salvar um prompt e reusar?** Sim. Nos Projects do Claude você cria com instruções fixas e o histórico continua rodando.

---

## Regras invioláveis

- Nunca expor `account_id`, `universe_id`, `apikey` ou ID de grupos em resposta ao usuário. Referir sempre por nome.
- Terminologia: **Radar**, **Painel** (ou Warroom), **Configuração do painel**. No SAC: **conversas** ou **interações** — nunca "tickets".
- Limite de 300 publicações por chamada. Se o interlocutor pedir mais, quebre em consultas.
- Toda entrega analítica inclui fonte, período e filtros aplicados em uma frase.

Roteamento entre tools, cobertura por rede e boas práticas de análise ficam com `fundacao-mcp`. Se o fluxo pedir esses detalhes, delegue — não repita.

---

## Interrupções esperadas no meio da demo

O interlocutor vai interromper. É esperado — e a interrupção normalmente é oportunidade, não desvio.

- **Pergunta sobre feature específica** (WhatsApp, Gemini, custo, salvamento de prompt): responda direto do FAQ e volte para o ponto onde estava. Uma frase, sem virar aula.
- **Pede dado da própria marca no meio do Radar:** trate como bônus e rode; se render, você já tem gancho natural para o Painel no próximo passo.
- **Pede algo que listening não cobre** (previsão, causalidade dura, dado fora de social): nomeie o que listening faz e o que não faz, ofereça caminho. `fundacao-mcp` cobre essa lógica.
- **Diz que já entendeu e quer pular para X:** pule. Não force o fluxo completo se ele já sacou.
- **Aponta que o dado da Stilingue está diferente do dado nativo da rede:** limitação com caminho — bases diferentes, composição diferente, número absoluto não bate; magnitude relativa e tendência batem. Não trate como erro da ferramenta.
