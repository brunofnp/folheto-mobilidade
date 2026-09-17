# Assets

Imagens e logos usados pelo folheto. Organizados por subpasta.

## Estrutura

```
assets/
├── logos/
│   └── fnp-logo.png         # Logo oficial FNP (rodapé + capa) — AINDA NÃO
│                             # existe neste repo, ver nota abaixo.
├── padroes/
│   ├── arte0.png             # padrão modular geométrico (faixa mais fina)
│   ├── arte1.png             # padrão modular geométrico (faixa média)
│   └── arte2.png             # padrão modular geométrico (faixa mais alta)
└── (capa)/
    └── (foto full-bleed opcional para a capa de cada município — ver
        campo `_capa_foto` no SCHEMA.md de data/mobilidade/)
```

## Pendência: falta o logo oficial FNP

`python/core/components.py::draw_footer` e `draw_capa_padrao` procuram
`assets/logos/fnp-logo.png` e simplesmente **não desenham nada** se o
arquivo não existir — degradação intencional (mesmo padrão documentado no
`folheto-ifem`, do qual este motor foi herdado), não um bug. Assim que
alguém tiver o arquivo oficial (PNG, fundo transparente, alta resolução),
basta colocá-lo em `assets/logos/fnp-logo.png` — nenhum código muda.

## Especificações

- **Logos:** PNG com fundo transparente, alta resolução (mínimo 2× do
  tamanho final: ~120×42px para o rodapé, ~120×42px para a capa).
- **Padrões:** PNG (os 3 arquivos já existem, herdados do folheto-ifem —
  são o "alfabeto modular" da identidade visual da FNP, genérico, não
  específico de nenhum tema).
- **Foto de capa:** se usada, cobre a página inteira (full-bleed) — ver
  `DESIGN_SYSTEM.md` §5.1. Sem foto, a capa cai no fundo azul sólido.

## Como o código resolve os caminhos

`python/core/tokens.py` define `ASSETS_DIR = ROOT_DIR / "assets"`. Cada tema
referencia explicitamente, nunca hardcoda o caminho:

```python
from core.tokens import ASSETS_DIR
logo = ASSETS_DIR / "logos" / "fnp-logo.png"
```
