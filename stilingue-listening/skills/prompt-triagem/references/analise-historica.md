# Análise do histórico de classificação

## 1. Identidade e taxonomia

Use apenas o Warroom do cliente selecionado. Radar não tem as anotações do painel e não substitui esta fonte.

1. Descubra a conta e o painel com `list_panels`. Se houver mais de um painel compatível, confirme pelo nome; não misture clientes ou painéis.
2. Leia `setup` com `account_id` e `universe_id`. Pagine grupos, temas e tags independentemente, com `groups_limit`/`groups_skip`, `themes_limit`/`themes_skip` e `tags_limit`/`tags_skip`. Se a resposta atingir o limite, continue até esgotar.
3. Registre nomes exatos, hierarquias que a fonte explicitar, descrições disponíveis e automações ativas/pausadas. Os descritores de setup são amostras, não a regra completa.
4. Obtenha a `apikey` correspondente ao mesmo painel para `warroom_query`, conforme o contrato disponível. Não suponha que `universe_id` seja a apikey, nem que uma apikey dê acesso ao setup.

Tags não têm descritores próprios; temas classificam publicações já coletadas; grupos definem coleta. Grupo não é uma anotação a ser inventada pelo prompt.

Nomes são evidência de vocabulário, não de regra. Não deduza o significado de uma sigla, exclusividade entre tags, hierarquia ou condição de aplicação só pela nomenclatura.

Para evitar repetir o setup inteiro, escolha limites de página eficientes dentro do schema real, registre os offsets concluídos e avance só as listas ainda incompletas. Reutilize o inventário enquanto painel e configuração forem os mesmos; se houver indicação de mudança, atualize-o. Não peça `temasetopicos` se o setup já resolveu a estrutura.

## 2. Janela de seis meses

- Fixe o instante final da consulta e o fuso usado pelo conector. Subtraia **seis meses de calendário**, ajustando para o último dia válido do mês de destino quando necessário. Não use 180 dias nem seis blocos de 30 dias como equivalentes.
- Consulte com datas explícitas em `YYYYMMDDHHmm:YYYYMMDDHHmm`; não envie `last_days` junto, pois ele sobrescreve `date_range`.
- Divida a janela em segmentos de até 30 dias, respeitando a semântica de limites da ferramenta. Inclua os trechos parciais inicial/final; não deixe lacunas. Se extremos inclusivos se sobrepuserem, deduplique publicações por `pid` e não some agregados sobrepostos.
- Registre a cobertura por mês de calendário. Se o painel nasceu há menos de seis meses ou há lacunas de coleta, diga qual intervalo está realmente disponível. Nunca complete o histórico com Radar ou dados de outro cliente.
- Datas de publicação não são datas de anotação. O resultado mostra publicações desse período com as classificações disponíveis na consulta, não necessariamente as regras vigentes quando foram publicadas.

## 3. Panorama quantitativo

Primeiro obtenha os agregados necessários de cada segmento com `warroom_query`, sempre com a mesma apikey e os filtros de negócio acordados. Consolide-os antes de planejar a amostra qualitativa; a tabela não significa executar todos os paths para cada rótulo e segmento:

| `path` | Finalidade |
| --- | --- |
| `estatisticas` | Total de publicações e composição da base |
| `sentimento_tags` | Uso observado de tags |
| `sentimento_temas` | Uso observado de temas |
| `temasetopicos` | Complementar a estrutura temática, quando necessário |
| `publicacoes` | Só depois dos agregados, para preencher lacunas de evidência textual |

Use `annotated=true` apenas em consultas explicitamente voltadas à base anotada. Não o aplique ao total usado como denominador. Esse filtro, sozinho, não garante que uma publicação tenha uma tag ou um tema específico.

Antes de consolidar, confira a unidade de contagem, os campos retornados e eventuais limites dos rankings. Não trate ranking truncado como inventário completo: ajuste o limite ou pagine se suportado; use o setup para identificar os rótulos ainda não cobertos e consulte-os individualmente quando necessário. Não use limites crescentes às cegas se o schema não os documentar.

Uma resposta reutilizável de agregado cobre todos os rótulos que ela efetivamente contém naquele segmento; não repita `estatisticas`, `sentimento_tags` ou `sentimento_temas` para cada tag/tema. Não some volume de anotações como total de posts. Se uma resposta já fornecer o mesmo total e unidade de forma verificável, reutilize em vez de chamar outro path apenas para obter o mesmo número.

Apresente por rótulo: família (tag/tema), nome exato, volume observado quando disponível, meses com ocorrência e canais. Declare o denominador de qualquer percentual. Uma publicação pode ter vários rótulos: somar frequências de tags/temas não produz o total de publicações nem percentuais necessariamente somam 100%.

Não transforme o cruzamento de sentimento em regra de sentimento. Aqui ele serve para localizar exemplos e contrastes.

## 4. Amostra qualitativa estratificada

Comece com lotes pequenos, por exemplo 5 publicações por chamada, para as lacunas que restarem após aproveitar os exemplos já retornados. Aprofunde apenas se faltarem casos independentes, contraste, diversidade temporal ou exemplos reservados. **Nunca solicite mais de 300 publicações por chamada.** Prefira agregados para medir volume; não baixe o semestre inteiro.

Use um mapa de cobertura por rótulo: evidências independentes, períodos/canais observados, contrastes, casos reservados e dúvidas. Se o retorno trouxer múltiplos rótulos verificáveis, registre a evidência para todos eles sem novas chamadas. Não use esse reaproveitamento para presumir ausência de rótulos omitidos pelo retorno.

Não execute uma grade exaustiva de chamadas por rótulo × todas as fatias × todos os canais. Mantenha os agregados dos seis meses e procure exemplos qualitativos em períodos/canais distintos conforme a ocorrência e as lacunas do mapa. Ao atender os critérios de sustentação e revisão de um rótulo, pare sua coleta; priorize os ainda não resolvidos, sem reduzir silenciosamente o inventário ou a cobertura temporal.

Se `projection` suportar campos selecionáveis no contrato real, peça apenas texto, identificador, data, canal, rótulos e contexto/link necessários. Não peça autoria detalhada, imagens e engajamento sem necessidade para a regra. Se a projeção não estiver documentada ou omitir a anotação necessária, mantenha o retorno suportado; não invente campos nem considere a redução local equivalente à redução no servidor.

- Use `tags` ou `themes` para buscar um rótulo de cada vez; assim não dependa de uma interpretação implícita de AND/OR em listas separadas por `:`.
- Distribua exemplos pelos meses com ocorrência, canais e casos frequentes/raros. Não use apenas `hot` ou posts mais engajados; alterne recortes temporais e ordenação por data.
- Deduplique por `pid` e agrupe cópias/quase duplicatas para que uma campanha ou resposta repetida não pareça evidência independente. Não altere os totais agregados originais; informe separadamente a deduplicação da amostra.
- Inclua publicações com rótulos vizinhos e casos sem o rótulo em análise. Ausência de anotação **não é negativo confirmado**: pode ser falta de revisão, automação ou taxonomia incompleta. Use como contraste para inspeção, não como verdade absoluta.
- Não exclua autoria proprietária, spam, canais ou tipos de interação silenciosamente. Preserve o escopo que o trial vai receber; se algum filtro for necessário, declare-o e mantenha-o em todas as consultas comparáveis.

Evite varrer páginas de cópias: se um lote não acrescentar exemplos independentes, mude o período ou a ordenação permitida em vez de repetir a mesma busca. Se continuar sem evidência suficiente, registre a limitação e use o fluxo de dúvida, não uma coleta indefinida. Timeout/erro deve seguir a recuperação do conector, sem criar um segundo ciclo de retries concorrente com o automático.

### Gate obrigatório: texto e anotação juntos

Para cada exemplo, confirme texto, `pid`, data, canal quando disponível e tags/temas aplicados.

O retorno padrão de `publicacoes` documenta texto e metadados, mas **não garante os campos de tags/temas**. Antes de usar `projection`, descubra no contrato real da ferramenta quais campos são suportados; não invente nomes de campo. Se faltarem rótulos:

1. Para o rótulo usado como filtro, a própria consulta é evidência de associação, desde que a semântica do filtro esteja confirmada.
2. Para coocorrências e outras anotações, solicite um export autorizado com texto, identificador, data e rótulos, ou outra fonte de leitura disponível e documentada.
3. Não infira rótulos de um post a partir de rankings agregados e não trate metadados ausentes como listas vazias.

Se não for possível associar texto às classificações, pare a inferência. Entregue o diagnóstico e solicite a fonte faltante, sem fabricar um prompt supostamente aprendido.

## 5. Das observações às regras

Monte uma matriz de evidências antes de redigir:

Mantenha-a compacta no registro da sessão, sem reproduzir textos completos nem imprimi-la a cada rodada de aprovação.

| Campo | Conteúdo |
| --- | --- |
| Rótulo | Família e nome literal no painel |
| Aplicar quando | Condição semântica observada no texto/contexto disponível |
| Não aplicar quando | Fronteira com rótulos próximos e ambiguidades |
| Evidências | Identificadores, datas e pequenos trechos minimizados |
| Coocorrência | Outros rótulos realmente verificados nos mesmos posts |
| Estabilidade | Meses/canais em que a regra se sustenta; mudanças e exceções |
| Origem | Manual, automação ou desconhecida, somente se a fonte informar |
| Revisão do usuário | Não solicitada (expresso), confirmada, corrigida, excluída ou Não sei; critério exato e justificativa quando fornecida |
| Decisão | Incluir no trial, hipótese para revisão ou fora do escopo |

Distinga três coisas: **configurado no painel**, **observado nas publicações** e **inferido como regra**.

Uma regra inferida do histórico apta ao trial precisa de exemplos independentes, contraste com casos próximos e coerência ao longo da cobertura disponível. Um único caso ou só o título do rótulo não basta. Aumente a amostra se a fronteira não estiver clara; se continuar ambígua, siga a revisão do modo escolhido na skill. Sem definição explícita do usuário, restrinja ao trecho sustentado ou deixe a regra fora do prompt e explique a pendência. Não sei não resolve a ambiguidade.

Uma definição explícita do usuário pode estabelecer a regra de negócio para o trial, mesmo divergindo do histórico; registre essa origem e a divergência sem reescrever a evidência. Ela não dispensa nome cadastrado, contexto disponível nem revisão de exemplos. Aprovar uma regra não aprova automaticamente suas combinações ou exclusividades.

Não transforme coocorrência em dependência automática. Só imponha exclusividade, precedência ou aplicação conjunta se houver definição confirmada ou evidências claras, sem contradições relevantes.

Casos especiais:

- **Tags operacionais** (respondido, encaminhado, responsável, SLA): não deduza estado interno ou ação executada a partir do texto do consumidor.
- **Temas por descritor e tags automáticas:** o histórico pode reproduzir regras antigas ou erros. Não o chame de gabarito humano.
- **Campanhas sazonais e taxonomia alterada:** separe a validade temporal. Não perpetue campanha encerrada só porque teve muito volume.
- **Rótulo raro, desativado ou sem uso observado:** não invente definição nem elimine silenciosamente. Liste fora do escopo com a justificativa.
- **Publicação sem texto/contexto suficiente:** não invente conteúdo de imagem, áudio, vídeo ou conversa anterior.

## 6. Verificação antes da entrega

Separe uma parte dos exemplos **antes** de extrair as regras, priorizando dados recentes e diversidade de rótulos. Mantenha duplicatas e quase duplicatas no mesmo conjunto.

Revise o prompt contra essa amostra reservada: rótulos indevidos, omissões, conflitos, necessidade de contexto e nomes fora da taxonomia. Ajuste regras com falhas e use exemplos ainda não utilizados para nova checagem, se houver.

Confira todos os rótulos incluídos, não só as tags mais frequentes. Informe quais temas/tags tiveram exemplos lidos e quais só apareceram em agregados ou em definições do usuário. Não anuncie dez temas “com evidência suficiente” se apenas três tiveram evidência qualitativa e os demais não têm definição confirmada. Se faltar amostra para a revisão de algum rótulo, identifique-o como não verificado ou retire-o do escopo.

Cheque exemplos sintéticos contra os critérios literais do prompt. Uma pergunta sobre atuação em uma cidade, por exemplo, não pode receber uma tag em um critério e perdê-la no exemplo idêntico. Sinais genéricos como “me chama no direct” ou “meu imóvel” não comprovam, sozinhos, profissão ou propriedade; mensagens como “enviei agora” podem depender do contexto e não são automaticamente irrelevantes.

### Protocolo de consistência e regressão

Antes de entregar cada versão, confronte decisões registradas, critérios finais e saídas esperadas. A revisão deve buscar tanto rótulos adicionados indevidamente quanto rótulos omitidos.

| Cenário a revisar | O que precisa ser consistente |
| --- | --- |
| Correspondência clara | Todos os rótulos exigidos pelos critérios aparecem na saída |
| Ausência de correspondência | Listas vazias, sem categoria inventada |
| Informação insuficiente sobre o autor | “Moro no imóvel”, “saí do apartamento”, “meu imóvel” ou “me chama no direct”, isoladamente, não provam vínculo de locação, propriedade ou profissão |
| Contexto de conversa incompleto | “Enviei agora” ou “ok” não são irrelevantes por definição; use só a condição sustentada pelo contexto recebido |
| Fronteira entre rótulos | Mesma condição tem o mesmo tratamento no critério, na exclusão e no exemplo |
| Exclusividade | Uma sigla confirmada ou nomes parecidos não autorizam excluir outro rótulo; teste os critérios separadamente |
| Aplicação conjunta aprovada | Confira um caso dentro do alcance aprovado e outro fora dele; não crie nem omita exceções |
| Problema fora do catálogo parcial | A ausência de tema específico não altera uma regra geral aprovada nem autoriza forçar outro tema |

Use casos pertinentes à taxonomia selecionada. Se um cenário não se aplicar, indique isso em vez de inventar um rótulo para testá-lo. Esses cenários são controles genéricos, não regras de um cliente.

Para cada exemplo incluído no prompt, enumere os rótulos esperados a partir dos critérios e compare com **ambos** os arrays do JSON. Para cada regra alterada ou combinação aprovada, inclua ao menos um caso de aplicação e um de fronteira/abstenção na revisão. Registre a tabela abaixo na sessão; no relatório mostre o balanço e as linhas corrigidas ou limitadas, disponibilizando o restante sob demanda:

| Caso | Critério/decisão e origem | Tags e temas esperados | Resultado da revisão e ajuste |
| --- | --- | --- | --- |
| Identificador ou entrada sintética minimizada | Histórico, definição do usuário ou inferência sustentada | Nomes literais ou listas vazias | Consistente, corrigido ou pendente |

Não fabrique essa tabela como se houvesse execução da LLM do triagem: ela documenta a comparação manual entre o texto e seus exemplos. Se houver linha pendente, resolva ou exclua o trecho conflitante antes de entregar o prompt pronto.

**Mudou o prompt, muda o escopo da revisão.** Reutilizar o histórico não dispensa reavaliar os critérios alterados, seus exemplos e as regras relacionadas. Se reutilizar casos já examinados, descreva como teste de regressão de mesa, não como nova amostra independente. Para avaliar generalização, use casos reservados ainda não utilizados quando disponíveis; sem eles, declare que essa avaliação adicional não foi feita.

Revisão semântica de critérios, decisões e exemplos usa primeiro as evidências disponíveis: não exige novas chamadas MCP por padrão. Reavalie em profundidade os critérios alterados e suas dependências, mantendo a checagem de coerência do conjunto final. Busque mais dados somente se a alteração exigir evidência ainda ausente; não repita toda a análise de seis meses.

Essa revisão é uma simulação de mesa, não uma execução do agente em produção. Não anuncie acurácia, precisão, recall ou “validado no triagem” sem execução real, gabarito revisado e denominadores explícitos. Informe tamanho da amostra, como foi separada e limitações.

Erros de autenticação, permissão, timeout persistente e respostas parciais devem ser explicitados. Reutilize a recuperação documentada no conector; reduza/fatie consultas quando apropriado, sem trocar de cliente ou fonte. Com dados parciais suficientes, entregue somente o escopo sustentado e rotule a entrega como parcial; sem evidência qualitativa suficiente, não entregue um prompt pronto para uso.
