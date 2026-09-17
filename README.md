# Folheto Mobilidade

Ficha de Diagnóstico Preliminar de Segurança Viária — folheto institucional
da Frente Nacional de Prefeitas e Prefeitos, para municípios acima de 80 mil
habitantes. Pilotos: **Campinas/SP** e **Montes Claros/MG**.

Motor de geração herdado do [`folheto-ifem`](https://github.com/dadosfnp/folheto-ifem)
(gerador unificado de folhetos FNP) — mesma identidade visual, formato de
página diferente (A4 em vez do quadrado 20×20cm original). Ver
`DESIGN_SYSTEM.md` e `CLAUDE.md` para o histórico completo das decisões.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Fontes oficiais (Barlow Condensed + Inter) — não vêm no git
python tools/baixar_fontes.py

# Configuração local (opcional nesta fase — ver .env.example)
Copy-Item .env.example .env
```

## Gerar um folheto

```powershell
# Listar temas registrados
python python/gerar.py --listar

# Exemplo de validação do pipeline (dado transcrito do briefing do projeto,
# NÃO um dado oficial publicável — ver data/mobilidade/SCHEMA.md)
python python/gerar.py --tema mobilidade --dados data/mobilidade/exemplo_fortaleza.json

# Um lote inteiro
python python/gerar.py --tema mobilidade --lote "data/mobilidade/*.json"
```

O PDF sai em `output/FolhetoMobilidade_<Município>_<UF>.pdf`.

## Estrutura

```
.
├── CLAUDE.md                   # Contexto do projeto (decisões, pendências, histórico)
├── DESIGN_SYSTEM.md             # Identidade visual (paleta, tipografia, grid, componentes)
├── python/
│   ├── core/                    # Núcleo reusável — herdado do folheto-ifem
│   │   ├── tokens.py             # Cores, dimensões, tamanhos de fonte, A4
│   │   ├── components.py         # Primitivas visuais (KPI, tabela, gráfico de linha…)
│   │   ├── paleta_ranking.py     # Cor por percentil — normal E invertida (mortalidade)
│   │   └── base_folheto.py       # Classe-base FolhetoFNP
│   ├── temas/
│   │   └── mobilidade.py         # Único tema deste repo
│   └── gerar.py                  # CLI unificada
├── tools/
│   ├── baixar_fontes.py
│   ├── verificar_arte.py
│   └── verificar_texto.py
├── data/
│   └── mobilidade/
│       ├── SCHEMA.md              # Contrato dos JSONs de entrada
│       └── exemplo_fortaleza.json # Dado de validação do pipeline (não oficial)
├── assets/                       # Logos, padrões decorativos
├── fonts/                        # Barlow Condensed + Inter (não versionado)
└── output/                       # PDFs gerados (não versionado)
```

## Estado do projeto

Ver `CLAUDE.md`, seção "Pendências" — em resumo: mortalidade e evolução de
frota têm página implementada e testada; internações, custo hospitalar e o
mapa por bairro dependem de dado que a equipe ainda está coletando.
