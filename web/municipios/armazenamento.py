"""
Leitura de `data/mobilidade/*.json` para o back-office — sem escrita. Os
dados só mudam via `tools/dados_tratados_para_json.py` (a partir de
`data/external/`) ou edição direta do arquivo, nunca por esta ferramenta
(ver CLAUDE.md, Decisão 4).
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from django.conf import settings

DIR_DADOS = Path(settings.BASE_DIR) / "data" / "mobilidade"
ARQUIVO_INDICE_SITE = Path(settings.BASE_DIR) / "docs" / "folhetos.json"


class MunicipioNaoEncontrado(Exception):
    pass


def caminho(slug: str) -> Path:
    """Resolve `slug` para um arquivo dentro de data/mobilidade/, recusando
    qualquer tentativa de escapar do diretório e qualquer slug começado por
    "_" (reservado aos "companheiros" compartilhados, ver python/gerar.py —
    esses não são municípios)."""
    if not slug or slug.startswith("_"):
        raise ValueError(f"slug inválido: {slug!r}")
    p = (DIR_DADOS / f"{slug}.json").resolve()
    if p.parent != DIR_DADOS.resolve():
        raise ValueError(f"slug inválido: {slug!r}")
    return p


def carregar(slug: str) -> dict:
    p = caminho(slug)
    if not p.exists():
        raise MunicipioNaoEncontrado(slug)
    with p.open(encoding="utf-8") as f:
        return json.load(f)


def listar_municipios() -> list[dict]:
    """Para a tela inicial: um dict por arquivo em data/mobilidade/, exceto
    os "companheiros" (`_*.json`). JSON malformado NÃO derruba a lista —
    aparece com `erro` preenchido em vez de nome/uf (degradação barulhenta,
    nunca silenciosa: ver CLAUDE.md)."""
    if not DIR_DADOS.is_dir():
        return []
    linhas = []
    for p in sorted(DIR_DADOS.glob("*.json")):
        if p.name.startswith("_"):
            continue
        slug = p.stem
        item = {"slug": slug, "mtime_json": p.stat().st_mtime}
        try:
            with p.open(encoding="utf-8") as f:
                d = json.load(f)
            item.update(
                nome=d.get("nome") or slug,
                uf=d.get("uf") or "",
                populacao=(d.get("populacao") or {}).get("valor"),
            )
        except (OSError, json.JSONDecodeError) as e:
            item.update(nome=slug, uf="", populacao=None, erro=str(e))
        linhas.append(item)
    return linhas


def rodape_atualizado_texto() -> str:
    """Mesmo texto do rodapé do site público (`docs/index.html`, ver o
    JS em torno de `#rodape-dados`): lê `docs/folhetos.json` (gerado por
    `tools/build_site.py`) e formata a data de "atualizado" como
    DD/MM/AAAA; pedido explícito do usuário, o rodapé do back-office
    local mostrava um texto diferente ("Ferramenta interna · uso local")
    do site público ("Índice atualizado em..."), e os dois devem ser
    exatamente iguais. Fallback idêntico ao do site público se o índice
    ainda não existir ou não tiver o campo."""
    try:
        indice = json.loads(ARQUIVO_INDICE_SITE.read_text(encoding="utf-8"))
        atualizado = indice.get("atualizado")
    except (OSError, json.JSONDecodeError):
        atualizado = None
    if not atualizado:
        return "Folhetos atualizados periodicamente."
    dt = datetime.strptime(atualizado, "%Y-%m-%dT%H:%M:%SZ")
    return f"Índice atualizado em {dt.strftime('%d/%m/%Y')}."
