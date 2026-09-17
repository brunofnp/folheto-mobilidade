# Design System — Folheto Mobilidade

Este projeto herdou o motor de geração (núcleo `python/core/`) e a identidade
visual institucional do **folheto-ifem** (`dadosfnp/folheto-ifem`), o gerador
unificado de folhetos da Frente Nacional de Prefeitas e Prefeitos. Paleta,
tipografia e a maior parte dos componentes visuais abaixo são os mesmos —
**só o formato de página e a estrutura de conteúdo mudaram**, ver §4 e §6.

> Ver `CLAUDE.md` para o histórico de decisão (por que A4 em vez do quadrado
> 20×20cm original, por que os dados ainda não vêm de banco).

---

## 1. Princípio fundador: sistema modular

Toda a identidade nasce de **um vocabulário gráfico mínimo** aplicado em cima
de uma grade de quadrados de mesma dimensão. Existem apenas 4 operações
dentro de cada módulo:

| Operação              | Aparência                              | Uso                              |
|-----------------------|-----------------------------------------|-----------------------------------|
| Quadrado vazio        | linha externa apenas                   | respiro, ritmo                   |
| Quadrado preenchido   | bloco sólido de cor                    | ênfase, peso visual              |
| ¼ de círculo          | quarto de disco em qualquer canto      | direção, dinamismo               |
| ½ círculo             | semicírculo em qualquer aresta         | suavidade, pontuação             |

**Regra de ouro:** se uma decoração nova precisar ser criada, ela deve sair
desse vocabulário. Não introduzir formas estranhas (triângulos, hexágonos,
ondas) sem aprovação.

---

## 2. Paleta de cores

Idêntica ao folheto-ifem — `python/core/tokens.py` é a fonte da verdade.

| Token         | Hex        | Uso primário                                        |
|---------------|------------|-----------------------------------------------------|
| `BLUE_DARK`   | `#122747`  | Títulos, texto de ênfase, faixas escuras            |
| `BLUE`        | `#1B3A6B`  | Cor institucional FNP — fundos, bordas, headers     |
| `BLUE_MID`    | `#3D6FA8`  | Gráficos secundários, hover, variação de azul       |
| `YELLOW`      | `#FFC72C`  | Acento, headlines de seção, aspas, gráficos         |
| `YELLOW_DARK` | `#C99A1F`  | Ranking (números grandes), variação de amarelo      |
| `GREEN`       | `#2A8F5C`  | Pontos fortes, contornos do alfabeto modular        |
| `RED_BURNT`   | `#C04A1A`  | Pontos de atenção (uso pontual)                     |
| `CREAM`       | `#F4EFE6`  | Fundo de cards, fundo neutro quente                 |
| `PAPER`       | `#FBF8F2`  | Fundo de páginas internas                           |
| `RULE`        | `#D9D2C3`  | Linhas divisórias, bordas sutis                     |
| `MUTED`       | `#6B6B6B`  | Texto secundário, fonte/captions                    |
| `INK`         | `#1A1A1A`  | Texto corrido                                       |

**Paleta ordinal (quintis/decis) — atenção à polaridade.** No IFEM, valor
alto = bem financiado (verde). Em segurança viária, valor alto de
**mortalidade/internação é sempre pior**, nunca melhor — a polaridade é
invertida, igual ao que o folheto-ifem já havia enfrentado com o índice de
risco climático do AdaptaBrasil. Por isso `core/paleta_ranking.py` tem duas
funções: `cor_por_percentil` (posição 1 = melhor) e
`cor_por_percentil_invertido` (posição 1 = pior) — **use sempre a segunda
para qualquer ranking de mortes, sinistros ou internações.** Nunca inverta
manualmente o percentual na chamada da função "maior é melhor" — é assim que
um verde acaba sinalizando "aqui morre mais gente".

**Travessão (—) é proibido em qualquer texto impresso.** Vale para copy nova
e para placeholder de valor ausente (usar `n/d`, nunca um traço solto — num
KPI o leitor confunde com sinal de menos). A meia-risca (–) de intervalo,
como em "2010–2024", é permitida. Separador de rótulos curtos: ponto médio
(`·`).

---

## 3. Tipografia

Idêntica ao folheto-ifem (Barlow Condensed + Inter, fallback automático para
Helvetica se as fontes não estiverem em `fonts/` — ver `fonts/README.md`).

| Função              | Fonte                          | Peso        | Tamanho típico |
|---------------------|---------------------------------|-------------|----------------|
| Título de capa      | Barlow Condensed Bold          | 700         | 24–42pt        |
| Headline de seção   | Barlow Condensed Bold          | 700         | 24–32pt (caixa alta) |
| Eyebrow / capítulo  | Barlow Condensed SemiBold      | 600         | 8–10.5pt CAIXA ALTA |
| Texto corrido       | Inter Regular                  | 400         | 8.5–9.5pt      |
| Citação / destaque  | Inter SemiBold ou Barlow Bold  | 600/700     | 11–16pt        |
| Caption / fonte     | Inter Regular                  | 400         | 6.5–9pt        |

---

## 4. Formato e grid — DIFERENTE do folheto-ifem

O folheto-ifem usa página quadrada fixa (20×20cm). Este projeto usa
**A4 retrato (21×29,7cm)** — decisão registrada em `CLAUDE.md`: reaproveitar
o motor como está, só trocando o tamanho do canvas (`PAGE_SIZE` em
`python/core/tokens.py`), sem reescrever o núcleo para um layout de painéis
dobrados de verdade. As dobras físicas (A3/A4, duas dobras — ver briefing do
projeto) são, por ora, **guia de corte/dobra na hora de imprimir**, não algo
que o gerador calcula ou desenha.

- **Página:** 21cm × 29,7cm (A4 retrato).
- **Stripe lateral:** 20pt de azul (`BLUE`) numa das laterais — alterna
  esquerda/direita por página, com numeração branca no rodapé do stripe.
- **Margem útil:** 36pt no lado oposto ao stripe e nas margens sup./inf.
- **Largura de conteúdo:** `CONTENT_W` em `tokens.py` — calculada a partir da
  largura real da página, nunca hardcoded num arquivo de tema.
- **Cabeçalho:** texto pequeno em `MUTED`, caixa alta — nome da publicação.
- **Rodapé:** label da seção à esquerda + logo FNP à direita (se o arquivo
  existir — ver `assets/README.md`).

> **Pendente de ajuste fino:** o núcleo foi validado tecnicamente em A4 (ver
> CLAUDE.md), mas os componentes (KPI box, tabela, gráfico de linha) ainda
> não tiveram o espaçamento vertical recalibrado para aproveitar a altura
> maior da A4 em relação ao quadrado original — hoje sobra respiro no fim de
> algumas páginas. Ajustar conforme o conteúdo real for entrando.

---

## 5. Componentes recorrentes

### 5.1 Capa (`core/components.py::draw_capa_padrao`)
- Foto full-bleed opcional (`_capa_foto` no JSON) — sem foto, fundo
  `BLUE_DARK` sólido (fallback intencional, ver `assets/README.md`).
- Faixa azul inferior cobrindo ~27% da altura, título branco condensado bold.
- Logo FNP + subtítulo (município/tema) na faixa, se o logo existir.

*Diferença do folheto-ifem: lá a capa usa um PNG pré-composto específico do
IFEM (`core/capa.py`, não herdado por este repo — era hardcoded a um asset
que não existe aqui). `draw_capa_padrao` é genérico, reutilizável por
qualquer tema futuro.*

### 5.2 Divisória de seção (`draw_section_divider`)
Fundo `BLUE` cheio, quarto de círculo translúcido no canto, capítulo em
`YELLOW`, título grande branco, subtítulo em azul claro.

### 5.3 Página de conteúdo
Fundo `PAPER`, eyebrow + título no topo, corpo Inter Regular, cards/tabelas
conforme o conteúdo, sempre com `draw_caption` citando a fonte do dado.

### 5.4 Card de KPI (`draw_kpi_box`)
Borda esquerda `BLUE_MID`, label em caixa alta, número grande Barlow Bold
(encolhe automaticamente se não couber), unidade em fonte menor ao lado.

### 5.5 Tabela comparativa (`draw_table`)
Header `BLUE` + texto branco, linhas alternadas branco/creme, coluna de
destaque (`highlight_col`) em `BLUE_DARK` SemiBold. Usada nas páginas de
mortalidade e internações (município vs. RM vs. mesmo porte vs. estado vs.
Brasil vs. capitais) — **mesmas larguras de coluna nas duas tabelas**, para
que leiam como um sistema, não duas tabelas soltas.

### 5.6 Gráfico de linha (`draw_line_chart` — NOVO, não existe no folheto-ifem)
Série histórica multi-categoria (mortes/internações por modo, por ano), sem
dependência externa (só ReportLab). Suporta uma faixa de destaque
(`faixa_destaque`) para hachurar um intervalo — usado para marcar o período
da gestão do prefeito atual no gráfico de internações (pedido do briefing).

### 5.7 QR code / encerramento (`draw_qr_page`)
Fundo azul-escuro (ou imagem, se houver), QR 140×140pt, URL em `YELLOW`
abaixo.

### 5.8 Bullets / lista
Quadrado `BLUE` 8×8pt. Nunca bullets redondos genéricos.

---

## 6. Estrutura canônica do folheto (tema `mobilidade`)

Diferente da estrutura do folheto-ifem (adaptada ao conteúdo do briefing de
segurança viária — ver `python/temas/mobilidade.py` e `CLAUDE.md`):

| Pág. | Função                              | Stripe | Status |
|------|--------------------------------------|--------|--------|
| 01   | Capa                                | dir    | ✅ implementada |
| 02   | Apresentação / "O problema" + KPIs  | dir    | ✅ implementada |
| 03   | Divisória — Mortes no trânsito      | esq    | ✅ implementada |
| 04   | Tabela: taxa de mortalidade 2024    | dir    | ✅ implementada |
| 05   | Gráfico: série histórica de mortes  | esq    | ✅ implementada |
| 06   | Divisória — Internações e custos    | dir    | ✅ implementada |
| 07   | Tabela: internações por modo        | esq    | ✅ implementada (aceita `null`) |
| 08   | Gráfico: série de internações       | dir    | ✅ implementada (aceita `null`) |
| 09   | Ranking de causas de morte + "leitos de UTI" | esq | ✅ implementada |
| 10   | Metodologia                         | dir    | ✅ implementada |
| 11   | Encerramento + QR                   | esq    | ✅ implementada |
| —    | Custo por hospital, por modo        | —      | ❌ pendente de dado (ver CLAUDE.md) |
| —    | Mapa de internações por bairro (RM) | —      | ❌ pendente de dado + componente novo |

> **Regra de stripe:** alternar lados a cada página (espelho).

---

## 7. Checklist antes de exportar PDF

- [ ] Nenhum travessão (—) no texto do PDF: `python tools/verificar_texto.py output/`.
- [ ] Nenhuma arte de rodapé cobrindo conteúdo: `python tools/verificar_arte.py output/`.
- [ ] Stripes alternam corretamente entre páginas.
- [ ] Numeração de página aparece em todas as páginas.
- [ ] Toda página interna tem cabeçalho e rodapé.
- [ ] Toda fonte de dado aparece como caption em `MUTED` no fim do gráfico/tabela.
- [ ] Nenhum valor ausente aparece como traço solto — sempre `n/d`.
- [ ] Ranking de mortalidade/internação usa `cor_por_percentil_invertido`, nunca a versão normal.
- [ ] QR code da última página aponta para URL real.
