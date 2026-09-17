# CLAUDE.md — Contexto do Projeto Folheto Mobilidade

> Arquivo de contexto para sessões com Claude Code.
> Criado em 2026-09-17 — primeira sessão do projeto: repositório criado,
> motor herdado e adaptado do `folheto-ifem`, tema `mobilidade` com 11
> páginas implementadas, pipeline validado de ponta a ponta com dado de
> exemplo transcrito do briefing (não oficial). Nenhum dado real de
> Campinas ou Montes Claros ainda — coleta em andamento pela equipe.

---

## Visão Geral

**Folheto Mobilidade** é a **Ficha de Diagnóstico Preliminar de Segurança
Viária** da Frente Nacional de Prefeitas e Prefeitos: um folheto impresso
institucional, com dados comparativos de mortes e internações por sinistro
de trânsito, custo hospitalar e evolução da frota — voltado a **cidades
acima de 80 mil habitantes**. Os dois pilotos definidos são **Campinas/SP**
e **Montes Claros/MG**.

Este projeto **não é uma plataforma web** — é um gerador de PDF em Python
(ReportLab), sem Django, sem banco de dados, sem servidor. Uma plataforma
completa de mobilidade é um objetivo de **fase futura**, explicitamente
adiado pelo usuário ("por agora vamos focar no folheto") — não antecipar
esse trabalho sem pedido explícito.

Público-alvo do documento: gestores municipais (prefeitos, secretários) —
mesma linguagem editorial e visual institucional dos demais folhetos FNP
(ver `DESIGN_SYSTEM.md`).

---

## Origem: herdado do `folheto-ifem`

O motor de geração (`python/core/`) e a identidade visual vieram de
[`dadosfnp/folheto-ifem`](https://github.com/dadosfnp/folheto-ifem) — o
gerador unificado de folhetos institucionais da FNP (usado hoje para o
folheto IFEM e COSIP). **O que foi trazido, adaptado e descartado:**

| Trazido sem mudança | Adaptado | Descartado |
|---|---|---|
| `components.py` (KPI, tabela, ranking, divisória, QR…) | `tokens.py` — página A4 em vez de 20×20cm quadrado | Todo dado/tema IFEM, COSIP, clima (`data/ifem/`, `data/cosip/`, `data/clima/`, `temas/ifem.py`, `temas/cosip.py`) |
| `fonts.py`, `asset_cache.py`, `base_folheto.py` | `paleta_ranking.py` — nova função `cor_por_percentil_invertido` (ver §Decisões) | `core/capa.py` e `core/ultima.py` — **não eram genéricos apesar de viverem em `core/`**: hardcoded a um PNG pré-composto específico do IFEM. Substituídos por `draw_capa_padrao` (novo, genérico) e reaproveitando `draw_qr_page` já existente para a última página |
| `tools/baixar_fontes.py`, `verificar_arte.py`, `verificar_texto.py` | `gerar.py` — carregamento de "companheiros" (`_*.json`) generalizado (o folheto-ifem hardcodeava os 3 nomes de arquivo do IFEM; agora é qualquer `_*.json` em `data/<tema>/`) | `tools/planilhas_para_json.py`, `adapta_para_json.py`, `sync_dados.py`, `recalcular_problema.py`, `gerar_sem_declaracao.py`, `regerar_capa.py` — pipeline de dados fiscais do Subfinanciados, sem relação com dados de trânsito |
| `assets/padroes/*.png` (alfabeto modular — genérico) | `components.py::draw_page_number` — removida a dependência hardcoded de `ifem_assets` (módulo que não existe aqui) | `docs/` inteiro do folheto-ifem (landing page, `PASSO_A_PASSO.md`, `COMO_ALTERAR_O_FOLHETO.md`) — conteúdo específico do pipeline Subfinanciados/AdaptaBrasil, será reescrito do zero quando este projeto tiver uma landing própria |

**Nova primitiva que o folheto-ifem não tinha:** `draw_line_chart` em
`components.py` — gráfico de linha multi-série sem dependência externa,
com suporte a hachurar uma faixa (usado para marcar o período da gestão do
prefeito atual no gráfico de internações). O folheto-ifem só tinha barra
empilhada (`draw_stacked_bar`); segurança viária é fundamentalmente sobre
séries históricas, então esse componente é central aqui.

---

## Decisões de arquitetura (registradas com o usuário em 2026-09-17)

Estas três perguntas foram feitas antes de escrever qualquer código, porque
mudavam a arquitetura de forma significativa:

### 1. Formato de página: A4, reaproveitando o motor como está

O motor do folheto-ifem usa página quadrada fixa (20×20cm, um PDF de várias
páginas empilhadas — não painéis dobrados). O briefing do projeto pede
formatos A3/A4 **com duas dobras físicas** (um folheto de verdade, dobrado).
São geometrias diferentes. **Decisão do usuário: reaproveitar o motor como
está** — só o `PAGE_SIZE` em `tokens.py` mudou para A4 retrato; as dobras
viram guia de corte/dobra na hora de imprimir, não painéis calculados pelo
gerador.

Validado tecnicamente antes de aplicar ao repo novo: troquei `PAGE_SIZE`
para A4 no clone do folheto-ifem e gerei um PDF real com o tema COSIP
existente (dado de exemplo `data/cosip/rio_de_janeiro.json`) — 8 páginas
saíram sem erro, em 595×842pt (A4 exato via `pypdf`). Confirma que
`CONTENT_W`, `STRIPE_W` e `MARGIN` são genéricos o bastante (só dependiam
de `PAGE_SIZE`, não de um valor hardcoded em outro lugar do núcleo).

**Pendente:** os componentes (KPI, tabela, gráfico) ainda não tiveram o
espaçamento recalibrado para aproveitar a altura maior da A4 — hoje sobra
respiro no fim de algumas páginas de conteúdo. Ajustar conforme o conteúdo
real (Campinas/Montes Claros) for entrando, não antes.

Se algum dia a decisão for revista para um layout de dobras de verdade
(painéis calculados dentro de uma folha física), isso é reabrir esta
decisão — sinalizar explicitamente antes de agir, não decidir sozinho.

### 2. Fonte de dados: arquivos JSON, sem banco (por agora)

Os dados de mortes já foram tratados em R pela equipe e podem, no futuro,
vir de um banco Postgres no Digital Ocean — mas **decisão do usuário: por
agora, sem banco**, alinhado com "focar só no folheto". Os JSONs de entrada
em `data/mobilidade/` são preenchidos/editados à mão (ou por um script de
ingestão ainda não escrito) — nenhuma leitura automática de banco existe
neste repo.

Quando os dados tratados em R chegarem (formato ainda não definido), o
próximo passo natural é um `tools/dados_tratados_para_json.py` (mesmo
padrão do `planilhas_para_json.py` do folheto-ifem) que lê o formato bruto
e escreve `data/mobilidade/<municipio>.json` batendo com `SCHEMA.md`. Não
escrever esse script antes de saber o formato real do dado — evitar
adivinhar um contrato de entrada que a equipe de dados não confirmou.

Se decidirmos migrar para banco depois, é uma decisão de arquitetura nova
— sinalizar antes de agir, mesmo que o padrão (Subfinanciados → JSON →
PDF) já exista como referência no folheto-ifem.

### 3. Repositórios: `brunofnp` (dev) + `dadosfnp` (produção/organização)

Mesmo padrão do Legislativo FNP: `origin` = `brunofnp/folheto-mobilidade`
(pessoal, dev), `production` = `dadosfnp/folheto-mobilidade` (organização).

**Nota para quem for criar o próximo repo institucional pela conta
`brunofnp`:** nesta sessão, o repositório `dadosfnp/folheto-mobilidade`
criado inicialmente pelo usuário era **privado**, e a conta `brunofnp` não
aparecia como colaboradora nele (nem a API do GitHub o enxergava — 404
direto, mesmo com escopo `repo`/`read:org` corretos e visibilidade normal
de todos os outros repositórios públicos do org). O usuário também não
conseguiu adicionar colaborador pela tela do GitHub (provável restrição de
política do org para quem não é admin), e `brunofnp` não tem permissão de
criar repositório novo em `dadosfnp` pela API
(`brunofnp cannot create a repository for dadosfnp`). Resolvido renomeando
o repositório privado antigo (liberando o nome) e criando um novo — dessa
vez a conta que criou o repo aparece com acesso automático. Se isso se
repetir num projeto futuro, o caminho mais rápido é este, não insistir em
convite de colaborador.

---

## Stack

| Camada | Tecnologia |
|---|---|
| Geração de PDF | Python 3.12+, ReportLab ≥4.0 |
| Imagens/QR | Pillow, `qrcode[pil]` |
| Dados (futuro) | pandas, openpyxl — hoje sem uso real, mantidos do `requirements.txt` herdado para quando a ingestão de planilhas/R existir |
| Dados (hoje) | JSON versionado à mão em `data/mobilidade/` |
| Tipografia | Barlow Condensed + Inter (fallback Helvetica se ausentes) |

---

## Estrutura de Arquivos

Ver `README.md` — não duplicar aqui; manter as duas em sincronia se a
estrutura mudar.

---

## Modelo de dados

Contrato completo em `data/mobilidade/SCHEMA.md`. Resumo do que já tem
página implementada: `frota` (evolução % + valores atuais), `mortalidade_2024`
(taxa por 100 mil hab., 4 modos × 6 bases de comparação), `mortes_serie_historica`,
`internacoes_2025`, `internacoes_serie_historica` (com janela de gestão do
prefeito atual), `ranking_causas_morte`, `leitos_uti_hipotetico` (hoje é
texto livre com a pergunta orientadora do projeto, não um número calculado).

**Regra de ouro herdada do folheto-ifem, ainda mais importante aqui:** dado
externo em JSON, nunca hardcoded no código Python. E mais uma, específica
deste projeto: **nunca preencher um campo com um número estimado/lido a
olho de um gráfico como se fosse dado oficial.** O arquivo de exemplo
(`exemplo_fortaleza.json`) documenta isso explicitamente campo a campo —
onde o briefing do projeto não deu o valor por extenso, o campo ficou
`null`, mesmo quando um valor "plausível" seria fácil de inventar.

---

## Git — Remotos e fluxo

| Remoto | URL | Uso |
|---|---|---|
| `origin` | `https://github.com/brunofnp/folheto-mobilidade.git` | Repositório pessoal — desenvolvimento |
| `production` | `https://github.com/dadosfnp/folheto-mobilidade.git` | Repositório da organização |

Sem branches `next`/`main` separadas por enquanto (não há deploy nem
usuário final navegando um site — só geração local de PDF). Revisar essa
decisão se o projeto ganhar uma landing page de distribuição (mesmo padrão
do folheto-ifem, `docs/index.html` + GitHub Pages) — não introduzir isso
sem necessidade real.

---

## Diretrizes de Engenharia

**Núcleo (`python/core/`) nunca conhece um tema específico.** Foi
exatamente o oposto disso que causou o retrabalho ao herdar `capa.py`/
`ultima.py` do folheto-ifem (hardcoded a um PNG do IFEM apesar de viverem
em `core/`) e a dependência de `ifem_assets` dentro de
`draw_page_number`. Qualquer nova primitiva visual entra em
`components.py` de forma genérica (parâmetros, nunca um `if tema == "x"`).

**Tokens só em `core/tokens.py`.** Cores, tamanhos, dimensões — nunca
hardcodar num arquivo de tema.

**Degradação é sempre barulhenta.** Campo ausente no JSON não derruba o
gerador — a seção sai com `"n/d"` ou uma mensagem de "dado ainda não
disponível", e um aviso vai para `stderr` (`_avisar_se_ausente` em
`mobilidade.py`). Nunca transformar um aviso desses em silêncio.

**Nunca propor comando destrutivo em banco como passo de rotina** (lição
herdada do `folheto-ifem`, `tasks/lessons.md` de lá) — se algum dia este
projeto ganhar um banco (ver Decisão 2 acima), qualquer comando que apague,
dropa, trunque ou sobrescreva dados vai numa mensagem isolada, com o risco
declarado antes, nunca dentro de uma lista de passos "normais".

**Precisão de dado importa mais aqui do que em qualquer folheto anterior.**
Este documento cita taxas de mortalidade e ranking de causas de morte —
número errado aqui não é só um typo, é uma alegação sobre mortes reais.
Nunca completar um campo vazio com um valor "razoável" para o PDF "ficar
completo". Preferir sempre "n/d" ou a seção ausente a um número inventado.

**Polaridade do ranking:** sempre `cor_por_percentil_invertido` (não a
versão normal) para qualquer métrica de mortalidade/sinistro/internação —
ver `DESIGN_SYSTEM.md` §2.

---

## Pendências e próximos passos

**Dados que a equipe ainda está coletando (não é código a escrever, é dado a receber):**
- Dados de internação (SIH/SIA) para os pilotos — página existe e aceita `null`, mas está vazia até o dado chegar.
- Custo hospitalar por hospital e por modo (pedido nº 9 do briefing) — schema documentado em `SCHEMA.md`, nenhuma página implementada ainda.
- Mapa de internações por bairro na RM (pedido nº 9 do briefing) — precisa de dado geográfico E de um componente de mapa novo no núcleo (o motor herdado não desenha mapas, só fotos/ilustrações full-bleed e formas geométricas simples). Não começar a implementar sem primeiro decidir o formato do dado geográfico (GeoJSON? shapefile? já teria que vir de algum lugar).
- População e área dos dois pilotos (Campinas, Montes Claros) — o próprio briefing deixou esses campos como placeholder ("Variável X - planilha X").
- Série histórica de mortes 2010-2024 por extenso (o briefing só trouxe um gráfico de imagem, sem tabela de valores) — necessário para a página 5 realmente mostrar Campinas/Montes Claros (hoje o exemplo de Fortaleza deixa essa página vazia de propósito, para não estimar valor a partir da imagem).

**Trabalho técnico pendente:**
- **URL do QR code é placeholder, não confirmada** (`FolhetoMobilidade.URL_PADRAO` em `mobilidade.py` = `https://fnp.org.br/mobilidade`) — nunca enviar um PDF para impressão sem sobrescrever com uma URL real e testada via o campo `"url"` no JSON de dados.
- Logo oficial FNP (`assets/logos/fnp-logo.png`) — ainda não existe neste repo (ver `assets/README.md`). Rodapé e capa degradam graciosamente sem ele, mas o visual final depende dele.
- Fontes oficiais (Barlow Condensed + Inter) — baixar com `tools/baixar_fontes.py` antes de qualquer PDF "para valer" (sem elas, sai em Helvetica).
- Recalibrar espaçamento vertical dos componentes para a altura da A4 (ver Decisão 1 acima) — adiado até ter conteúdo real para ajustar contra.
- `tools/dados_tratados_para_json.py` — escrever só quando o formato real do dado tratado em R for conhecido.
- Decidir se/quando este projeto ganha uma landing page de distribuição (mesmo padrão do folheto-ifem) — não é prioridade agora.
- JSONs reais de Campinas e Montes Claros — o único arquivo que existe hoje (`exemplo_fortaleza.json`) é só para validar que o pipeline roda, não é um dos dois pilotos.
