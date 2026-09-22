"""
Gera o índice do site estático de distribuição (`docs/`) a partir dos JSONs
em `data/mobilidade/` e dos PDFs em `output/`.

**Arquitetura revisada em 2026-09-22 (reabre a Decisão 4 do CLAUDE.md).**
Até esta data, os PDFs ficavam hospedados numa GitHub Release (nunca
versionados no git): o script só escrevia o índice JSON apontando pra lá.
O usuário pediu que o site público tivesse um botão "Preview" de verdade
(abrir o PDF no navegador, sem baixar), igual ao back-office Django. Isso
provou ser tecnicamente impossível apontando pra uma Release: o asset do
GitHub Releases sempre serve com `Content-Disposition: attachment` e sem
CORS, então nem `<a target="_blank">`, nem `<iframe>`, nem `fetch()`
conseguem mostrar o PDF inline, só baixar. GitHub Pages (arquivo estático
em `docs/`) não tem essa limitação. Decisão do usuário, ciente do
trade-off: os PDFs agora são copiados pra `docs/pdfs/` e VERSIONADOS no
git; o repositório fica maior a cada regeração, mas o Preview funciona de
verdade.

Diferenças deliberadas em relação ao original do folheto-ifem (que ainda
usa Release), ver CLAUDE.md Decisão 4:

  - lê direto `data/mobilidade/*.json` (este projeto ainda não tem um
    `export_folheto/` de pipeline de tratamento separado);
  - nunca inclui `exemplo_fortaleza.json`, dado de validação de pipeline,
    não um município publicável (mesma regra que já rege o PDF, ver
    SCHEMA.md);
  - PDFs copiados pra `docs/pdfs/`, não hospedados em Release.

Saída:
  docs/pdfs/*.pdf      : cópia dos PDFs de output/ (só os municípios reais)
  docs/folhetos.json   : índice de municípios disponíveis (lido pela página)
  docs/index.html      : UI estática (já existe; este script só atualiza o JSON)

Uso típico (depois de gerar os PDFs com python/gerar.py):
    python tools/build_site.py
"""
import argparse
import json
import re
import shutil
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIR_DADOS = ROOT / "data" / "mobilidade"
OUTPUT_DIR = ROOT / "output"
SITE_DIR = ROOT / "docs"
PDFS_DIR = SITE_DIR / "pdfs"

EXCLUIR_PREFIXOS = ("_", "exemplo_")  # "_*" = companheiros; "exemplo_*" = dado de validação, não oficial


def _strip_acentos(s: str) -> str:
    """Nomes de arquivo sem acento: mais seguro pra URL (mesmo cuidado que
    já existia pro nome de asset de Release)."""
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def _slug_publico(nome: str, uf: str) -> str:
    """Nome do arquivo como ele fica publicado em docs/pdfs/: sem acento,
    sem espaço, seguro pra URL."""
    base = _strip_acentos(nome).replace(" ", "_")
    base = re.sub(r"[^A-Za-z0-9._-]", ".", base)
    return f"FolhetoMobilidade_{base}_{uf}.pdf"


def _pdf_filename_local(nome: str, uf: str) -> str:
    """Nome do arquivo tal como o gerador escreve em output/, com acentos
    (ver FolhetoFNP._default_output)."""
    return f"FolhetoMobilidade_{nome.replace(' ', '_')}_{uf}.pdf"


def _carregar_municipios() -> list[dict]:
    """Lê data/mobilidade/*.json, excluindo companheiros (_*.json) e o
    arquivo de exemplo (exemplo_*.json, nunca dado publicável, ver
    SCHEMA.md)."""
    municipios = []
    if not DIR_DADOS.is_dir():
        return municipios
    for jpath in sorted(DIR_DADOS.glob("*.json")):
        if jpath.name.startswith(EXCLUIR_PREFIXOS):
            continue
        try:
            with jpath.open(encoding="utf-8") as f:
                d = json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            print(f"[skip] {jpath.name}: {e}", file=sys.stderr)
            continue
        municipios.append(d)
    return municipios


def build() -> None:
    SITE_DIR.mkdir(exist_ok=True)
    PDFS_DIR.mkdir(exist_ok=True)

    municipios = _carregar_municipios()
    pdfs_disponiveis = {p.name for p in OUTPUT_DIR.glob("FolhetoMobilidade_*.pdf")} if OUTPUT_DIR.is_dir() else set()

    itens = []
    nomes_publicos_validos = set()
    for d in municipios:
        nome, uf = d.get("nome"), d.get("uf")
        if not nome or not uf:
            continue
        fname_local = _pdf_filename_local(nome, uf)
        if fname_local not in pdfs_disponiveis:
            continue  # sem PDF gerado ainda: não entra no índice (nunca linka pra um 404)
        fname_publico = _slug_publico(nome, uf)
        shutil.copyfile(OUTPUT_DIR / fname_local, PDFS_DIR / fname_publico)
        nomes_publicos_validos.add(fname_publico)
        taxa_mortalidade = ((d.get("mortalidade_2024") or {}).get("total") or {}).get("municipio")
        itens.append({
            "municipio": nome,
            "uf": uf,
            "populacao": (d.get("populacao") or {}).get("valor"),
            "taxa_mortalidade_total": taxa_mortalidade,
            "pdf": f"pdfs/{fname_publico}",
            "pdf_filename": fname_publico,
        })

    # Remove PDFs órfãos em docs/pdfs/ (município removido ou renomeado):
    # nunca deixar arquivo publicado que não está mais no índice.
    if PDFS_DIR.is_dir():
        for pdf in PDFS_DIR.glob("*.pdf"):
            if pdf.name not in nomes_publicos_validos:
                pdf.unlink()

    # Cidades maiores primeiro, mesma convenção do folheto-ifem (as mais procuradas).
    itens.sort(key=lambda x: -(x["populacao"] or 0))

    indice = {
        "total": len(itens),
        "atualizado": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "municipios": itens,
    }

    out_json = SITE_DIR / "folhetos.json"
    with out_json.open("w", encoding="utf-8") as f:
        json.dump(indice, f, ensure_ascii=False, indent=2)

    print(f"[ok] {out_json}: {len(itens)} município(s), PDFs copiados pra {PDFS_DIR}")
    if not itens:
        print("[aviso] índice vazio: nenhum município real com PDF gerado ainda "
              "(esperado até Campinas/Montes Claros terem dado e PDF).", file=sys.stderr)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.parse_args()
    build()


if __name__ == "__main__":
    main()
