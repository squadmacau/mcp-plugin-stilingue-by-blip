# Biblioteca de categorias e subnichos

Ponto de partida. Ajuste ao briefing, **valide no Radar** (`statistics` + amostra de posts) e troque termos que trouxerem ruído. Cada linha vira uma busca de `trend_users` (até 21 termos, operadores em MAIÚSCULAS, compostos entre aspas). A busca principal da categoria é o OR dos 2 ou 3 termos mais fortes de cada subnicho.

Padrão para criar subnichos de uma categoria nova: **dor/necessidade** (pele oleosa, dívidas), **objeto/ingrediente** (retinol, air fryer), **formato** (resenhas, receitas rápidas, unboxing), **público** (pele madura, mães de primeira viagem, iniciantes), **estética/tribo** (k-beauty, clean girl, minimalismo). Evite o termo genérico da categoria dentro dos subnichos.

Termos com risco de ambiguidade estão marcados com ⚠: combine-os com `AND` ou retire. Ao montar a busca, junte os termos da linha com `OR` e ponha entre parênteses os que já têm `AND` — ex.: `"pele negra" AND (skincare OR manchas)` vira `("pele negra" AND (skincare OR manchas)) OR ...`. Em `config.json` → `subnichos`, pode colar os mesmos termos: para marcar o subnicho de cada post o script usa o primeiro termo de cada expressão.

## Skincare
| Subnicho | Termos |
|---|---|
| rotina | "rotina de skincare", "rotina de pele", "rotina noturna", grwm, sérum |
| acne-e-oleosidade | "pele oleosa", "pele acneica", acne, "ácido salicílico", cravos, espinhas |
| k-beauty | "k-beauty", kbeauty, "skincare coreano", "cosméticos coreanos" |
| ativos | niacinamida, retinol, "vitamina c", "ácido hialurônico", peptídeos, pdrn |
| protecao-solar | "protetor solar", "filtro solar", fotoproteção |
| pele-madura | "pele madura", antienvelhecimento, "anti-idade", "linhas de expressão" |
| pele-negra | "pele negra" AND (skincare OR manchas OR hiperpigmentação) |
| resenhas | resenha AND (skincare OR dermocosmético*), "testei o", "vale a pena" AND pele |

## Maquiagem
| Subnicho | Termos |
|---|---|
| tutoriais | "tutorial de maquiagem", "make do dia", "maquiagem fácil", "passo a passo" AND make |
| pele-e-base | base AND (cobertura OR acabamento), corretivo, "pó translúcido" |
| olhos | delineado, sombra AND paleta, "máscara de cílios", rímel |
| boca | batom, gloss, "lip tint", "lip oil" |
| make-acessivel | "make barata", "maquiagem barata", dupe*, "achadinhos de make" |
| pele-madura | "make pele madura", "maquiagem 40+", "maquiagem 50+" |
| make-pele-negra | "make pele negra", "base para pele negra" |

## Cabelo
| Subnicho | Termos |
|---|---|
| cacheados-crespos | cachos, cacheada*, crespo*, "transição capilar", "no poo", "low poo" |
| cronograma | "cronograma capilar", hidratação AND cabelo, nutrição AND cabelo, reconstrução |
| loiras | "cabelo loiro", matizador, descoloração, "loiro platinado" |
| queda-e-crescimento | "queda de cabelo", "crescimento capilar", minoxidil, calvície |
| masculino | barbearia, "corte masculino", barba AND cuidados |

## Moda
| Subnicho | Termos |
|---|---|
| looks-do-dia | "look do dia", lookdodia, ootd, "como combinar" |
| plus-size | "plus size", plussize, "moda plus" |
| moda-masculina | "moda masculina", "estilo masculino", "look masculino" |
| brechó-e-sustentável | brechó, "moda sustentável", "moda circular", garimpo |
| achadinhos | achadinhos AND (roupa OR moda), shein, shopee AND look ⚠ |
| moda-praia | biquíni, "moda praia", maiô |

## Fitness e treino
| Subnicho | Termos |
|---|---|
| musculacao | musculação, hipertrofia, "treino de perna", "treino de glúteo" |
| corrida | corrida AND (treino OR pace OR km), maratona, "meia maratona" |
| treino-em-casa | "treino em casa", "treino sem equipamento", calistenia |
| funcional-crossfit | crossfit, "treino funcional", hiit |
| pilates-yoga | pilates, yoga, alongamento |
| emagrecimento | emagrecimento, "perder peso", "déficit calórico" |

## Alimentação saudável e nutrição
| Subnicho | Termos |
|---|---|
| receitas-fit | "receita fit", "receita saudável", "lanche saudável" |
| proteina | whey, proteína AND receita, "alto em proteína" |
| vegano-vegetariano | vegano, vegetariano, "plant based", "sem carne" |
| low-carb | "low carb", lowcarb, cetogênica, keto |
| nutri-especialistas | nutricionista AND dica*, "reeducação alimentar" |

## Gastronomia e receitas
| Subnicho | Termos |
|---|---|
| receitas-rapidas | "receita fácil", "receita rápida", "almoço rápido" |
| airfryer | "air fryer", airfryer, fritadeira AND receita |
| confeitaria | bolo AND receita, confeitaria, brigadeiro, sobremesa AND receita |
| churrasco | churrasco, picanha, "ponto da carne", parrilla |
| bares-e-restaurantes | "restaurante" AND (dica OR indicação OR "onde comer"), "comer bem em" |
| comida-regional | "comida nordestina", "comida mineira", "comida baiana" |

## Maternidade e infância
| Subnicho | Termos |
|---|---|
| gestacao | gestante, gravidez, gestação, "chá de bebê" |
| bebes | recém-nascido, amamentação, "introdução alimentar", enxoval |
| maternidade-real | "maternidade real", maternar, "mãe de primeira viagem" |
| paternidade | paternidade, "pai presente", "vida de pai" |
| educacao-infantil | "atividades para crianças", brincadeiras AND crianças, "educação infantil" |

Atenção: conteúdo com crianças exige cuidado redobrado (Guia do CONAR, ed. 2026). Sinalize na curadoria.

## Pets
| Subnicho | Termos |
|---|---|
| caes | cachorro AND (dica OR adestramento OR ração), adestramento, tutor* AND cão |
| gatos | gato AND (dica OR comportamento OR ração), "gatos" AND tutor* |
| saude-pet | veterinári*, "saúde pet", vermífugo, castração |
| adocao | adoção AND (cão OR gato OR pet), "adote" AND pet |

## Games
| Subnicho | Termos |
|---|---|
| fps-e-competitivo | valorant, "counter strike", cs2, "free fire", fortnite |
| mobile | "jogos mobile", "free fire", "clash royale" |
| console-e-pc | playstation, xbox, "nintendo switch", "pc gamer" |
| streaming | "live na twitch", streamer, "gameplay ao vivo" |
| retro-e-indie | "jogo indie", "jogos indie", retrô AND games |

## Tecnologia e gadgets
| Subnicho | Termos |
|---|---|
| smartphones | iphone AND (review OR vale), "melhor celular", galaxy AND review |
| reviews-unboxing | unboxing, review AND (notebook OR fone OR celular) |
| ia-e-produtividade | "inteligência artificial" AND dica*, chatgpt, "ferramentas de ia", produtividade |
| casa-inteligente | "casa inteligente", alexa, automação AND casa |
| setup | "setup gamer", "setup de trabalho", "home office" AND setup |

## Finanças pessoais
| Subnicho | Termos |
|---|---|
| investimentos | investimentos, "renda fixa", tesouro AND direto, ações AND dividendos |
| organizacao-financeira | "organização financeira", "planilha de gastos", orçamento AND família |
| dividas | dívidas, endividad*, "sair das dívidas", "nome limpo" |
| cartao-e-milhas | milhas, cashback, "cartão de crédito" AND benefício* |
| empreendedorismo | empreendedor*, "pequeno negócio", mei |

Atenção: conteúdo de investimento tem regras próprias (CVM/ANBIMA). Sinalize na curadoria.

## Viagem e turismo
| Subnicho | Termos |
|---|---|
| viagem-barata | "viajar barato", "passagem barata", promoção AND passagem |
| destinos-nacionais | "viagem pelo Brasil", nordeste AND viagem, "pousada" AND dica |
| internacional | intercâmbio, "viagem internacional", mochilão |
| viagem-em-familia | "viagem com criança", "viagem em família" |
| milhas-e-hoteis | milhas AND viagem, hotel AND review, resort AND dica |

## Casa e decoração
| Subnicho | Termos |
|---|---|
| decoracao | decoração, "decor", "antes e depois" AND casa |
| organizacao | organização AND casa, "personal organizer", "casa organizada" |
| reforma-diy | reforma, "faça você mesmo", diy AND casa |
| limpeza | "dicas de limpeza", faxina, "produto de limpeza" |
| apartamento-pequeno | "apartamento pequeno", "ape pequeno", "casa pequena" |

## Automotivo
| Subnicho | Termos |
|---|---|
| reviews | "avaliação" AND carro, "test drive", review AND carro |
| eletricos | "carro elétrico", híbrido, byd, recarga AND carro |
| manutencao | "manutenção do carro", mecânico AND dica*, óleo AND motor |
| motos | moto AND (review OR viagem), motociclista, motovlog |

## Carreira e educação
| Subnicho | Termos |
|---|---|
| carreira | carreira AND dica*, currículo, entrevista AND emprego, linkedin AND dica* |
| concursos | concurso AND (público OR estudo*), concurseir* |
| vestibular-enem | enem, vestibular, redação AND nota |
| tech-carreira | programação, "carreira em tecnologia", dev AND júnior |
| idiomas | "aprender inglês", inglês AND dica*, idiomas |

## Futebol e esportes
| Subnicho | Termos |
|---|---|
| futebol-conteudo | futebol AND (análise OR tática OR bastidores) |
| futebol-feminino | "futebol feminino" |
| fantasy-e-palpites | cartola, "dicas cartola" ⚠ (apostas: setor regulado) |
| outros-esportes | vôlei, basquete AND nba, ufc, "jiu jitsu" |

## Agro
| Subnicho | Termos |
|---|---|
| agro-negocio | agronegócio, "agro é", safra, colheita |
| pecuaria | pecuária, gado AND (corte OR leite), boiadeiro |
| vida-no-campo | "vida no campo", "vida na roça", sítio AND rotina |
| maquinas | trator, "máquinas agrícolas", colheitadeira |
