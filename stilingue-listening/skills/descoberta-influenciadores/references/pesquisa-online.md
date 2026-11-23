# Pesquisa online da shortlist

Objetivo: completar o que o Radar não tem (bio, cidade, outras redes, agência, parcerias, polêmicas, contato), **sempre com fonte**. Faça só para a shortlist (8 a 15 perfis): é caro e não escala.

## Ordem por perfil (pare quando tiver o necessário)

1. **Handle exato + nome**: `"<handle>"` e `"<Nome>" <categoria>`. Perfis micro quase não aparecem em busca genérica. Por isso o passo 2 existe.
2. **Páginas públicas de perfil em agregadores**: busque `<handle> hypeauditor`, `<handle> heepsy`, `<handle> modash`, `<handle> favikon`, `<handle> motionapp`, `<handle> creatorsjet`. Essas páginas costumam mostrar bio (com cidade, e-mail comercial ou "parcerias via direct"), seguidores e taxa de engajamento **segundo a ferramenta**. Cite a ferramenta como fonte e não misture os números dela com os do Radar sem avisar.
3. **Site, link na bio, media kit**: Linktree, site próprio, "mídia kit", "anuncie", "parcerias". Página de contato do próprio criador = melhor fonte de contato.
4. **Representação**: "agenciado por", "assessoria", "@agência" na bio, roster de agências de influência. Agência é contato comercial legítimo e frequentemente o certo para mid/macro/mega.
5. **YouTube**: a aba "Sobre" do canal mostra links e um botão de e-mail comercial protegido por captcha. **Não contorne.** Registre `{"tipo": "dm", "valor": "E-mail comercial disponível na aba Sobre do canal (requer clique)", "fonte": "<url do canal>"}`.
6. **Imprensa e reputação**: `"<Nome>" polêmica`, `"<Nome>" processo`, `"<Nome>" cancelamento`, `"<Nome>" entrevista`. Sem resultado relevante: registre "nada encontrado em busca de notícias (<mês/ano>)", com status `ok`. Não liste o que não encontrou como se fosse certeza.
7. **Parcerias**: no Radar, `posts` com `"<handle>"` mostra marcas que citam o criador (perfil `gênero = Marca` no texto costuma ser parceria). Nos posts dele, #publi, "parceria paga", "recebidos" e @ de marcas. Fonte = link do post.

Não abra instagram.com nem tiktok.com direto (pedem login e costumam bloquear). Use as fontes acima. Não baixe nem embuta fotos.

## Locais

- Listas por cidade e nicho: busque `top <nicho> instagram influencers <cidade>`, `influenciadora <nicho> <cidade>`, `influenciadora <gentílico> <nicho>` (recifense, soteropolitana, mineira…). Heepsy, Modash e Collabstr publicam páginas por cidade com bio e @.
- Imprensa local: colunas sociais e de comportamento ("influenciadora pernambucana…").
- Veículos e shoppings locais que aparecem no Radar repostam criadores da cidade: os @ citados nos posts deles são pistas.
- Valide cada achado no Radar com lotes de `trend_users` (handles em OR). Só entra com métricas quem tem posts da categoria na base; os demais entram com seguidores da fonte externa e "A confirmar" nas métricas.
- `confianca: "confirmado"` exige bio, site ou imprensa dizendo a cidade.

## Brand safety: checklist mínimo por perfil

| Item | Como checar | Status típico |
|---|---|---|
| Conflito com concorrente | `cita_concorrentes` no data.json + parcerias recentes | `atencao` se parceria nos últimos 6 meses |
| Dono de marca na categoria | Bio, imprensa, agregadores | `atencao` (conflito estrutural) |
| Identificação de publicidade | #publi/"parceria paga" nos posts patrocinados | `ok` / `atencao` se faz publi sem identificar |
| Polêmicas e processos | Busca de notícias (passo 6) | `ok` / `atencao` / `risco` |
| Público infantil e adolescente | Conteúdo voltado a menores | `atencao`: o Guia do CONAR (ed. 2026) endureceu as regras |
| Saúde e medicina | Especialista com CRM/CRF e promessas de resultado | `atencao`: médicos seguem as regras de publicidade do CFM |
| Setores regulados | Bebida alcoólica, apostas, medicamentos, finanças | `atencao`: regras próprias de cada setor |
| Autenticidade | Alerta de engajamento muito fora do grupo | `nao_verificado`: pedir prints das métricas ao criador |
| Saturação | Alta proporção de publis na amostra | `atencao` |

## Contato: política (LGPD e bom senso)

- Só contato **profissional publicado** pelo próprio criador ou por quem o representa, para proposta comercial.
- Nunca: telefone pessoal, endereço, dados de família, e-mail deduzido, contato de fonte que vazou dados.
- Cada contato com `fonte` e `verificado_em`. Contato velho (mais de 6 meses) deve ser reverificado.
- Sem contato público: registre o caminho ("mensagem pelo perfil", "via agência X").
- A Central lembra o cliente de respeitar pedidos de não contato.
