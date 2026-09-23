# Folheto Mobilidade

**Ficha de Diagnóstico Preliminar de Segurança Viária**, folheto institucional
da Frente Nacional de Prefeitas e Prefeitos, para municípios acima de 80 mil
habitantes. Pilotos: **Campinas/SP** e **Montes Claros/MG**.

> **Contexto completo do projeto (decisões, pendências, histórico dia a
> dia):** [`CLAUDE.md`](CLAUDE.md).
> **Identidade visual (paleta, tipografia, grid, componentes):**
> [`DESIGN_SYSTEM.md`](DESIGN_SYSTEM.md).
> **Contrato dos dados de entrada:**
> [`data/mobilidade/SCHEMA.md`](data/mobilidade/SCHEMA.md).

Motor de geração herdado do [`folheto-ifem`](https://github.com/dadosfnp/folheto-ifem)
(gerador unificado de folhetos FNP), mesma identidade visual, formato de
página diferente (A4 retrato em vez do quadrado 20×20cm original).

## O caminho completo, do zero ao ar

As três armadilhas conhecidas estão marcadas com ⚠️, são silenciosas: o PDF
sai, só sai **errado** (ou o índice público sai incompleto).

| # | Etapa | Onde |
|---|---|---|
| 1 | Clonar, venv, dependências, fontes | [Setup](#setup) |
| 2 | ⚠️ `data/external/` e `data/raw/` não vêm no clone, cada máquina mantém a própria cópia local | [Setup](#setup) |
| 3 | Gerar os JSONs a partir do dado tratado pela equipe | [De onde vêm os dados](#de-onde-vêm-os-dados) |
| 4 | ⚠️ `"url": null` quebra o QR; lista de série 100% vazia tem que ser `[]`, nunca uma lista de `null` | [Duas armadilhas do schema](#duas-armadilhas-do-schema) |
| 5 | Gerar o PDF de cada piloto (ou usar o back-office) | [Gerar folhetos](#gerar-folhetos) |
| 6 | Validar antes de publicar | [Validar os PDFs](#validar-os-pdfs-antes-de-publicar) |
| 7 | ⚠️ `exemplo_fortaleza.json`/`exemplo_teresina.json` nunca podem entrar no índice público | [Publicar](#publicar-pdfs-e-site) |
| 8 | Publicar: `docs/pdfs/` + `docs/folhetos.json` + push nos dois remotos, `main` e `next` | [Publicar](#publicar-pdfs-e-site) |

**Se algo sair estranho, comece por aqui:** todo erro conhecido deste
projeto é de degradação silenciosa, campo ausente ou `null` no JSON, fonte
faltando. Nenhum deles derruba o gerador. Rode `python tools/verificar_arte.py
output/` e `python tools/verificar_texto.py output/`, e confira se o PDF tem
7 páginas (menos que isso, geralmente é seção sem dado, não bug).

---

## Setup

```powershell
git clone https://github.com/dadosfnp/folheto-mobilidade.git
cd folheto-mobilidade

# 1. Ambiente virtual
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Dependências
pip install -r requirements.txt

# 3. Fontes oficiais (Barlow Condensed + Inter), NÃO vêm no git
python tools/baixar_fontes.py

# 4. Configuração local (opcional nesta fase, ver .env.example)
Copy-Item .env.example .env
```

### Por que alguns arquivos ficam fora do git

| O quê | Por que fora do git | Sem ele o PDF… |
|---|---|---|
| `fonts/*.ttf` | licença + peso | sai em Helvetica, tipografia diferente da oficial |
| `data/external/` (~350 MB) | planilhas SIM/SIH/SENATRAN já tratadas pela equipe, regeneráveis a partir do dado bruto | `tools/dados_tratados_para_json.py` sai com um erro claro listando o que falta |
| `data/raw/` (~6,6 GB) | extração original SIH/SIM em parquet, cada máquina mantém a própria cópia | idem: sem `data/external/`, nem chega a olhar pra cá |

Pular o passo 3 do Setup (fontes) não dá erro nenhum: o gerador degrada e
continua em Helvetica, avisando em `stderr`. Se aparecer `[aviso]` na saída
de `python python/gerar.py`, o PDF **não** está fiel ao oficial.

---

## De onde vêm os dados

```
planilhas tratadas (data/external/*.xlsx)  ──►  dados_tratados_para_json.py  ──►  data/mobilidade/<slug>.json  ──►  gerar.py  ──►  PDF
```

```powershell
python tools/dados_tratados_para_json.py                      # os dois pilotos
python tools/dados_tratados_para_json.py --municipio campinas # só um
```

Não precisa de banco, de rede, nem de credencial (ver `CLAUDE.md`, Decisão
2, "por agora, sem banco"). Campos que `data/external/` não cobre hoje
(ranking de causas de morte, mandato do prefeito atual, custo hospitalar,
mapa por bairro) continuam `null` no JSON de saída, de propósito, nunca um
valor estimado, ver `CLAUDE.md`, seção Pendências.

### Duas armadilhas do schema

`python/core/base_folheto.py` e `python/temas/mobilidade.py` usam
`dict.get(chave, padrão)`, que só cai no padrão se a **chave não existir**,
não protege contra a chave existir com `null`. Detalhe completo em
[`data/mobilidade/SCHEMA.md`](data/mobilidade/SCHEMA.md#duas-armadilhas-do-motor-achadas-ao-construir-o-formulário-de-edição):

1. **`"url": null` quebra o QR code** (`TypeError` não capturado). Se o
   município ainda não tem URL própria, **omita a chave** (o gerador cai
   em `FolhetoMobilidade.URL_PADRAO`), nunca escreva `null`.
2. **Série 100% vazia tem que ser `[]`, nunca uma lista de `null`s.**
   `draw_line_chart` plota por índice; uma lista de `None` é *truthy* em
   Python e entra na legenda desenhando uma linha vazia.

---

## Gerar folhetos

```powershell
# Listar temas registrados
python python/gerar.py --listar

# Os dois pilotos reais
python python/gerar.py --tema mobilidade --dados data/mobilidade/campinas.json
python python/gerar.py --tema mobilidade --dados data/mobilidade/montes_claros.json

# Exemplo de validação do pipeline (dado transcrito do briefing do projeto,
# NÃO um dado oficial publicável, ver data/mobilidade/SCHEMA.md)
python python/gerar.py --tema mobilidade --dados data/mobilidade/exemplo_fortaleza.json

# Um lote inteiro
python python/gerar.py --tema mobilidade --lote "data/mobilidade/*.json"

# A3 (mesmo design da A4, escalado; não é um redesenho, ver CLAUDE.md Decisão 4)
python python/gerar.py --tema mobilidade --dados data/mobilidade/campinas.json --tamanho A3
```

O PDF sai em `output/FolhetoMobilidade_<Município>_<UF>.pdf`, com 7 páginas
(capa, mortalidade, série de mortes e causas, internações, perfil da
cidade/frota, metodologia, encerramento decorativo).

## Gerar e baixar PDFs pelo navegador

Back-office Django local, só pra equipe da FNP (nunca exposto publicamente,
ver `CLAUDE.md`, Decisão 4). **Só leitura**: lista os municípios, gera e
baixa o PDF (sempre regenerado na hora a partir do JSON atual, nunca serve
um arquivo desatualizado), não edita dado nenhum. Atualizar dado é sempre
via `tools/dados_tratados_para_json.py` ou editando o arquivo diretamente.

```powershell
python manage.py runserver
# abrir http://127.0.0.1:8000/
```

Sem banco de dados (`DATABASES = {}`). Os avisos que normalmente só
apareceriam no console ao gerar (fontes ausentes, campo faltando) aparecem
na tela antes do download.

---

## Validar os PDFs antes de publicar

```powershell
python tools/verificar_arte.py output/
```

Mede, no PDF gerado, se a arte decorativa do rodapé cobre texto ou gráfico,
defeito que não gera erro nenhum (o arquivo abre, o texto continua
extraível) e só aparece pra quem olha a página impressa. Sai com código 1
se achar qualquer colisão.

```powershell
python tools/verificar_texto.py output/
```

Checa a convenção tipográfica da publicação: nenhum travessão (—) em texto
impresso, nem em copy de tela (site público, back-office). A meia-risca
(–) de intervalo, como em "2003–2025", é permitida.

Rodar os dois **sempre** antes de publicar.

---

## Publicar (PDFs e site)

Site estático de distribuição pública (`docs/`, GitHub Pages), réplica
adaptada do padrão do [`folheto-ifem`](https://github.com/dadosfnp/folheto-ifem/tree/main/docs).
Diferente do `folheto-ifem` (que hospeda PDF como asset de GitHub Release):
aqui os PDFs ficam versionados em `docs/pdfs/` porque o botão "Preview" abre
o PDF inline no navegador, e um asset de Release sempre força download
(`Content-Disposition: attachment`, sem CORS), ver `CLAUDE.md`, Decisão 4.

```powershell
# 1. Gerar os PDFs reais (ver "Gerar folhetos" acima)
python python/gerar.py --tema mobilidade --dados data/mobilidade/campinas.json
python python/gerar.py --tema mobilidade --dados data/mobilidade/montes_claros.json

# 2. Reindexar o site: copia os PDFs pra docs/pdfs/ e regrava docs/folhetos.json
python tools/build_site.py

# 3. (Só quando o PDF de exemplo mudar de layout) regenerar as prévias da landing
python tools/gerar_preview_landing.py

# 4. Commitar e publicar nos dois remotos, nas duas branches
git add docs/ python/ web/ CLAUDE.md DESIGN_SYSTEM.md
git commit -m "..."
git push origin main && git push production main
git checkout next && git merge main --ff-only && git push origin next && git push production next
git checkout main
```

`tools/build_site.py` **nunca** inclui `exemplo_fortaleza.json` nem
`exemplo_teresina.json` no índice (dado de validação do pipeline, não
oficial, ver `SCHEMA.md`), nem um município sem PDF em `output/`.

`origin` (`brunofnp/folheto-mobilidade`) é o repositório pessoal de
desenvolvimento; `production` (`dadosfnp/folheto-mobilidade`) é o da
organização, e é de lá que o GitHub Pages serve
`https://dadosfnp.github.io/folheto-mobilidade/` (habilitado manualmente
por um admin do org, `Settings → Pages → branch main, pasta /docs`, passo
único, feito uma vez).

`tools/publicar_release.ps1` ainda existe, mas não é mais obrigatório: é só
um jeito opcional de ter uma cópia versionada dos PDFs fora do site (por
exemplo, pra linkar de um e-mail).

### Conferir que subiu

```powershell
$j = Invoke-RestMethod "https://dadosfnp.github.io/folheto-mobilidade/folhetos.json"
"$($j.total) município(s), atualizado em $($j.atualizado)"
```

O Pages leva um ou dois minutos pra publicar depois do push na `main` da
`production`.

---

## Estrutura

```
.
├── CLAUDE.md                      # Contexto do projeto (decisões, pendências, histórico)
├── DESIGN_SYSTEM.md                # Identidade visual (paleta, tipografia, grid, componentes)
├── manage.py                       # CLI do back-office Django (ver "Gerar e baixar PDFs pelo navegador")
├── web/                            # Back-office Django, só leitura
│   ├── settings.py                  # DATABASES = {}, sem banco
│   └── municipios/
│       ├── armazenamento.py          # Leitura de data/mobilidade/*.json, sem escrita
│       ├── geracao.py                # Chama gerar_um(), o mesmo ponto de entrada do CLI
│       ├── views.py                  # lista/preview/baixar, nunca edita dado
│       └── templates/, static/       # Mesmo padrão visual do site público
├── python/
│   ├── core/                      # Núcleo reusável, herdado do folheto-ifem, nunca conhece um tema
│   │   ├── tokens.py                # Cores, dimensões, tamanhos de fonte, A4
│   │   ├── components.py            # Primitivas visuais (KPI, tabela, donut, gráfico de linha…)
│   │   ├── paleta_ranking.py        # Cor por percentil, normal E invertida (ver CLAUDE.md, polaridade)
│   │   └── base_folheto.py          # Classe-base FolhetoFNP (A4/A3)
│   ├── temas/
│   │   ├── __init__.py               # Registro TEMAS = {"mobilidade": FolhetoMobilidade}
│   │   └── mobilidade.py             # Único tema deste repo, 7 páginas
│   └── gerar.py                    # CLI unificada
├── tools/
│   ├── baixar_fontes.py
│   ├── verificar_arte.py
│   ├── verificar_texto.py
│   ├── dados_tratados_para_json.py  # data/external/ -> data/mobilidade/<slug>.json
│   ├── build_site.py                # Copia PDFs pra docs/pdfs/ e gera docs/folhetos.json
│   ├── gerar_preview_landing.py     # Gera docs/preview/*.jpg a partir de um PDF real
│   └── publicar_release.ps1         # Opcional: cópia dos PDFs numa GitHub Release
├── docs/                           # Site estático de distribuição (GitHub Pages)
│   ├── index.html                   # UI: busca, filtro por UF, ordenação, Preview inline
│   ├── folhetos.json                 # Índice gerado por build_site.py, NÃO editar à mão
│   ├── pdfs/                          # PDFs publicados, versionados (ver "Publicar")
│   └── preview/                       # Prévias de página (JPEG), geradas, versionadas
├── data/
│   ├── mobilidade/
│   │   ├── SCHEMA.md                # Contrato dos JSONs de entrada
│   │   ├── campinas.json            # Piloto real
│   │   ├── montes_claros.json       # Piloto real
│   │   ├── exemplo_fortaleza.json   # Dado de validação do pipeline (não oficial)
│   │   └── exemplo_teresina.json    # Idem
│   ├── external/                   # Planilhas SIM/SIH/SENATRAN já tratadas, não versionado
│   └── raw/                        # Extração original SIH/SIM (parquet), não versionado
├── assets/                        # Logos, capa, alfabeto modular, artes decorativas
├── fonts/                         # Barlow Condensed + Inter (não versionado)
└── output/                        # PDFs gerados (não versionado)
```

---

## Adicionar um folheto novo (outro tema)

O núcleo (`python/core/`) já suporta mais de um tema, mesmo que este repo
hoje só use `mobilidade`. Roteiro em 3 passos:

### 1. Criar `python/temas/<tema>.py`

```python
from core.base_folheto import FolhetoFNP
from core.components import (
    draw_stripe, draw_page_number, draw_header, draw_footer,
    draw_eyebrow, draw_titulo, draw_body, draw_kpi_box, draw_qr_bloco,
)
from core.tokens import MARGIN, CONTENT_W, FS_TITLE_SECAO

class FolhetoMeuTema(FolhetoFNP):
    titulo_publicacao = "MEU TEMA · SUBTÍTULO INSTITUCIONAL"

    def construir_paginas(self):
        return [self._pag_capa, self._pag_dados]

    def _pag_capa(self, c, n):
        # ...usa primitivas de core/components.py
        ...
```

### 2. Registrar em `python/temas/__init__.py`

```python
from .mobilidade import FolhetoMobilidade
from .meu_tema import FolhetoMeuTema

TEMAS = {
    "mobilidade": FolhetoMobilidade,
    "meu_tema": FolhetoMeuTema,   # <- novo
}
```

### 3. Criar `data/<tema>/<municipio>.json` e `data/<tema>/SCHEMA.md`

Estrutura livre, documentada no `SCHEMA.md` do tema. Arquivos começando
com `_` são tratados como companheiros compartilhados e injetados em
todos os municípios do tema (ver `python/gerar.py`).

---

## Princípios de manutenção

- **Tokens só em `core/tokens.py`**. Cores, tamanhos, dimensões, nunca
  hardcodar em `python/temas/mobilidade.py`. Mudou a paleta? Mexa só num
  lugar.
- **Núcleo (`python/core/`) nunca conhece um tema específico.** Nova
  primitiva visual entra em `components.py` de forma genérica (parâmetros,
  nunca um `if tema == "x"`), ver `CLAUDE.md`, Diretrizes de Engenharia.
- **Dados externos em JSON, nunca hardcoded no código Python.** E mais:
  nunca preencher um campo com um número estimado/lido a olho como se
  fosse dado oficial, sempre `null` ou "n/d".
- **Degradação é sempre barulhenta.** Campo ausente no JSON não derruba o
  gerador, a seção sai com "n/d" e um aviso vai pra `stderr`. Nunca
  transformar um aviso desses em silêncio.
- **Nunca usar travessão (—)** em texto do PDF nem em copy de tela (site
  público, back-office), ver `tools/verificar_texto.py`.

> Identidade visual canônica: [`DESIGN_SYSTEM.md`](DESIGN_SYSTEM.md).
> Contrato dos dados: [`data/mobilidade/SCHEMA.md`](data/mobilidade/SCHEMA.md).
> Decisões, pendências e histórico completo: [`CLAUDE.md`](CLAUDE.md).

---

## Estado do projeto

Ver `CLAUDE.md`, seção "Pendências", em resumo: **os dois pilotos têm dado
real** (população, área, frota completa por período e categoria,
mortalidade 2024, série histórica de mortes, internações 2025 e série
histórica de internações). Ainda pendentes, sem fonte disponível hoje:
ranking de causas de morte, mandato do prefeito atual, custo hospitalar e
mapa por bairro, ver `data/mobilidade/SCHEMA.md`.
